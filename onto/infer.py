from owlready2 import *
import pandas as pd
from typing import List, Any


# 1. 기존 온톨로지 로딩
# template에서 onto 객체를 가져온 후, Individuals가 저장된 파일을 로드합니다.
onto = get_ontology("onto/generated_bom.owl").load()

# 2. SWRL 규칙 정의
with onto:
    # Rule 1: 원재료 창고의 Input
    rule1 = Imp()
    rule1.set_as_rule("""
        Storage(?s), Material(?m), isStorageOf(?s, ?m) -> hasInput(?s, ?m)
    """)

    # Rule 2: 원재료 창고의 Output
    rule2 = Imp()
    rule2.set_as_rule("""
        Storage(?s), Material(?m), isStorageOf(?s, ?m) -> hasOutput(?s, ?m)
    """)

    # Rule 3: 부품 창고의 Input
    rule3 = Imp()
    rule3.set_as_rule("""
        Storage(?s), EBoM(?m), isStorageOf(?s, ?m) -> hasInput(?s, ?m)
    """)

    # Rule 4: 부품 창고의 Output
    rule4 = Imp()
    rule4.set_as_rule("""
        Storage(?s), EBoM(?m), isStorageOf(?s, ?m) -> hasOutput(?s, ?m)
    """)

    # Rule 5: 공정 결과(result) 추론
    rule5 = Imp()
    rule5.set_as_rule("""
        ProcessID(?p), hasProductName(?p, ?e) -> result(?p, ?e)
    """)

    # Rule 6: 조립 공정이 아닌 설비의 Input 추론
    rule6 = Imp()
    rule6.set_as_rule("""
        ProcessID(?p), Machine(?m), isMachineOf(?m, ?p), hasProcessType(?p, ?pt), differentFrom(?pt, Assemble), hasMaterial(?p, ?mat) -> hasInput(?m, ?mat)
    """)

    # Rule 7: 조립 공정의 Input 추론
    rule7 = Imp()
    rule7.set_as_rule("""
        ProcessID(?p), Machine(?m), isMachineOf(?m, ?p), hasProcessType(?p, Assemble), hasComponents(?p, ?comp) -> hasInput(?m, ?comp)
    """)

    # Rule 8: 설비의 Output 추론
    rule8 = Imp()
    rule8.set_as_rule("""
        Machine(?m), ProcessID(?p), isMachineOf(?m, ?p), result(?p, ?prod) -> hasOutput(?m, ?prod)
    """)

    # Rule 9: 창고 -> 설비 연결(connectedTo) 추론
    rule9 = Imp()
    rule9.set_as_rule("""
        Storage(?s), Machine(?m), hasOutput(?s, ?mat), hasInput(?m, ?mat) -> connectedTo(?s, ?m)
    """)

    # Rule 10: 설비 -> 창고 연결(connectedTo) 추론 (조립 공정 제외)
    rule10 = Imp()
    rule10.set_as_rule("""
        Machine(?m), Storage(?s), hasOutput(?m, ?mat), hasInput(?s, ?mat), isMachineOf(?m, ?p), hasProcessType(?p, ?pt), differentFrom(?pt, Assemble) -> connectedTo(?m, ?s)
    """)

    # Rule 11: 조립 설비 -> 창고 연결(connectedTo) 추론
    rule11 = Imp()
    rule11.set_as_rule("""
        Machine(?m), Storage(?s), hasOutput(?m, ?mat), hasInput(?s, ?mat), isMachineOf(?m, ?p), hasProcessType(?p, ?pt), sameAs(?pt, Assemble) -> connectedTo(?m, ?s)
    """)

    # Rule 12: 시뮬레이션 파라미터 추론
    rule12 = Imp()
    rule12.set_as_rule("""
        hasQuantity(?prod, ?q), hasProductName(?p, ?prod), ProcessID(?p), hasCarbonFootprint(?prod, ?cf), isMachineOf(?m, ?p), hasProcessingTime(?prod, ?pt), hasCost(?prod, ?c), hasProcessType(?p, ?pty) -> hasCarbonFootprintSim(?m, ?cf), hasCostSim(?m, ?c), hasProcessingTimeSim(?m, ?pt), hasOutputQuantity(?m, ?q), hasInputQuantity(?m, ?q), hasProcessTypeSim(?m, ?pty)
    """)

    # Rule 13: 설비의 Process Type 추론
    rule13 = Imp()
    rule13.set_as_rule("""
        Machine(?m), ProcessID(?p), hasProcessType(?p, ?pt), isMachineOf(?m, ?p) -> hasProcessTypeSim(?m, ?pt)
    """)


# 3. Pellet 추론기 실행
print("Pellet 추론기를 실행합니다...")
with onto:
    sync_reasoner_pellet(infer_property_values=True, infer_data_property_values=True)
print("추론이 완료되었습니다.")

# 4. 추론 결과를 DataFrame으로 생성 (Simulation 인스턴스 중심)
report = []

# --------- 헬퍼 함수들 ---------
def _get_prop_values(inst, prop_name: str) -> List[Any]:
    """onto의 prop_name 속성값을 리스트로 반환. 값이 엔티티면 .name으로 치환하지 않고 원본을 유지.
    빈 경우 [] 반환, 속성 미존재 시 [] 반환."""
    prop = getattr(onto, prop_name, None)
    if not prop:
        return []
    try:
        return list(prop[inst])
    except Exception:
        return []


def _names(values: List[Any]) -> List[str]:
    return [v.name if hasattr(v, "name") else str(v) for v in values]


def _is_instance_of(inst, class_name: str) -> bool:
    cls = getattr(onto, class_name, None)
    if not cls:
        return False
    try:
        return isinstance(inst, cls)
    except Exception:
        # fallback: 클래스 이름 비교
        return any(getattr(c, "name", "") == class_name for c in getattr(inst, "is_a", []))


def _is_assemble_proc(p) -> bool:
    pt_vals = _get_prop_values(p, "hasProcessType")
    pts = {n.lower() for n in _names(pt_vals)}
    return ("assemble" in pts) or ("assembly" in pts)


def _exists_name(values: List[Any], target: str) -> bool:
    return any((getattr(v, "name", str(v)) == target) for v in values)


def _reason_for_missing(inst, prop_name: str) -> str:
    """빈칸 사유를 SWRL 규칙 전제 충족 여부로 설명을 생성한다."""
    is_machine = _is_instance_of(inst, "Machine")
    is_storage = _is_instance_of(inst, "Storage")

    # 공통
    if prop_name in ("isMachineOf", "isStorageOf"):
        return "기본 매핑 누락(원본 온톨로지에서 생성되지 않음)"

    # 시뮬레이션 파라미터들 (Rule12/Rule13)
    if prop_name in ("hasProcessingTimeSim", "hasCostSim", "hasCarbonFootprintSim", "hasOutputQuantity", "hasInputQuantity", "hasProcessTypeSim"):
        if not is_machine:
            return "대상 아님: 설비(Machine)가 아님(Rule12 비적용)"
        p_vals = _get_prop_values(inst, "isMachineOf")
        if not p_vals:
            return "Rule12 미충족: isMachineOf 누락 → 공정 정보 부재"
        p = p_vals[0]
        # Rule13 대체 경로(공정 타입만)
        if prop_name == "hasProcessTypeSim":
            if not _get_prop_values(p, "hasProcessType"):
                return "Rule12/13 미충족: hasProcessType 누락"
            # 나머지 전제가 부족하면 Rule12는 실패하지만 Rule13만으로는 채워질 수 있음
            return "Rule12 일부 전제 부족 가능. Rule13 충족 시 추론되어야 함"
        # 나머지 파라미터는 제품(product) 속성 의존
        prod_vals = _get_prop_values(p, "hasProductName")
        if not prod_vals:
            return "Rule12 미충족: hasProductName 누락 → result/제품 속성 접근 불가"
        prod = prod_vals[0]
        if prop_name == "hasProcessingTimeSim" and not _get_prop_values(prod, "hasProcessingTime"):
            return f"Rule12 미충족: hasProcessingTime({getattr(prod, 'name', str(prod))}) 없음"
        if prop_name == "hasCostSim" and not _get_prop_values(prod, "hasCost"):
            return f"Rule12 미충족: hasCost({getattr(prod, 'name', str(prod))}) 없음"
        if prop_name == "hasCarbonFootprintSim" and not _get_prop_values(prod, "hasCarbonFootprint"):
            return f"Rule12 미충족: hasCarbonFootprint({getattr(prod, 'name', str(prod))}) 없음"
        if prop_name in ("hasOutputQuantity", "hasInputQuantity") and not _get_prop_values(prod, "hasQuantity"):
            return f"Rule12 미충족: hasQuantity({getattr(prod, 'name', str(prod))}) 없음"
        # 모든 전제가 있는 것 같은데 값이 비어있다면 일반 메시지
        return "Rule12 전제는 보이지만 추론 결과 없음(규칙/데이터 정합 확인 필요)"

    # hasInput
    if prop_name == "hasInput":
        if is_machine:
            p_vals = _get_prop_values(inst, "isMachineOf")
            if not p_vals:
                return "Rule6/7 미충족: isMachineOf 누락"
            p = p_vals[0]
            if _is_assemble_proc(p):
                if not _get_prop_values(p, "hasComponents"):
                    return "Rule7 미충족: hasComponents 없음(조립 공정)"
                return "Rule7 적용 대상이나 입력 구성요소-자원 매칭 부재"
            else:
                if not _get_prop_values(p, "hasMaterial"):
                    return "Rule6 미충족: hasMaterial 없음(비-조립 공정)"
                prec = _get_prop_values(p, "hasPrecedingProcess")
                if not prec:
                    return "Rule6 미충족: hasPrecedingProcess 없음(비-조립 공정)"
                if not _exists_name(prec, "N/A"):
                    return "Rule6 미충족: hasPrecedingProcess ≠ 'N/A'"
                return "Rule6 전제는 보이지만 입력-자원 매칭 부재"
        if is_storage:
            if not _get_prop_values(inst, "isStorageOf"):
                return "Rule1/3 미충족: isStorageOf 누락"
            return "Rule1/3 전제는 보이지만 타입/매칭 불일치"
        return "대상 클래스 판별 불가"

    # hasOutput
    if prop_name == "hasOutput":
        if is_machine:
            p_vals = _get_prop_values(inst, "isMachineOf")
            if not p_vals:
                return "Rule8 미충족: isMachineOf 누락"
            p = p_vals[0]
            if not _get_prop_values(p, "hasProductName"):
                return "Rule5 미충족: hasProductName 누락 → result 부재"
            res = _get_prop_values(p, "result")
            if not res:
                return "Rule5 미적용: result 생성 실패"
            return "Rule8 전제는 보이지만 출력-제품 매핑 부재"
        if is_storage:
            if not _get_prop_values(inst, "isStorageOf"):
                return "Rule2/4 미충족: isStorageOf 누락(창고)"
            return "Rule2/4 전제는 보이지만 타입/매칭 불일치"
        return "대상 클래스 판별 불가"

    # connectedTo
    if prop_name == "connectedTo":
        if is_machine:
            outs = _get_prop_values(inst, "hasOutput")
            if not outs:
                return "Rule10/11 미충족: hasOutput 없음(설비)"
            p_vals = _get_prop_values(inst, "isMachineOf")
            if not p_vals:
                return "Rule10/11 미충족: isMachineOf 누락"
            p = p_vals[0]
            if _is_assemble_proc(p):
                return "Rule11 미적용: 대응 창고의 hasInput(동일 자원) 없음"
            else:
                return "Rule10 미적용: 대응 창고의 hasInput(동일 자원) 없음"
        if is_storage:
            outs = _get_prop_values(inst, "hasOutput")
            if not outs:
                return "Rule9 미충족: Storage hasOutput 없음"
            return "Rule9 미적용: 대응 설비의 hasInput(동일 자원) 없음"
        return "대상 클래스 판별 불가"

    # 기본
    return "값 없음: 규칙 전제 미충족 또는 적용 대상 아님"


TARGET_COLS = [
    "hasOutputQuantity",
    "hasProcessingTimeSim",
    "hasProcessTypeSim",
    "hasInput",
    "hasCostSim",
    "hasOutput",
    "hasCarbonFootprintSim",
    "connectedTo",
    "hasInputQuantity",
    "isMachineOf",
    "isStorageOf",
]

if hasattr(onto, "Simulation"):
    for inst in onto.Simulation.instances():
        entry = {"name": inst.name, "type": "Simulation"}

        # 1) 우선 현재 인스턴스에 존재하는 속성값을 수집
        present_props = {}
        for prop in inst.get_properties():
            try:
                values = [v.name if hasattr(v, "name") else v for v in prop[inst]]
            except Exception:
                values = []
            present_props[prop.python_name] = values

        # 2) 타깃 컬럼을 모두 보장하고, 빈칸이라면 사유를 채움
        for col in TARGET_COLS:
            if col in present_props and present_props[col]:
                entry[col] = present_props[col]
            else:
                # 원본 값이 비어있거나 아예 없는 경우 → 사유 기입
                reason = _reason_for_missing(inst, col)
                entry[col] = reason

        # 3) 그 외 존재하는 속성도 담되, 이미 TARGET_COLS에 있는 것은 건너뜀
        for k, v in present_props.items():
            if k not in TARGET_COLS:
                entry[k] = v

        report.append(entry)
else:
    print("❌ 'Simulation' 클래스가 온톨로지에 존재하지 않습니다.")

df = pd.DataFrame(report)
if not df.empty:
    # 리스트 값을 보기 좋게 문자열로 변환
    for col in df.columns:
        df[col] = df[col].apply(lambda x: repr(x) if isinstance(x, list) else x)
    csv_path = "onto/inference_result.csv"
    df.to_csv(csv_path, index=False, encoding="utf-8-sig")
    print(f"추론 리포트를 '{csv_path}'로 저장했습니다. (행 수: {len(df)})")
    print("상위 10행 미리보기:")
    print(df.head(10))
else:
    print("수집된 추론 결과가 없습니다.")

# 5. 추론된 온톨로지 저장
output_file = "onto/inferred_bom.owl"
onto.save(file=output_file, format="rdfxml")
print(f"추론된 온톨로지가 '{output_file}' 파일로 저장되었습니다.")