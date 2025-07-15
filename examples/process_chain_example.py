"""
공정 연결 기능 사용 예제
>> 연산자를 사용하여 공정들을 체인으로 연결하고,
& 연산자를 사용하여 다중공정을 그룹으로 묶는 방법을 보여줍니다.
"""

from src.processes import ManufacturingProcess, AssemblyProcess, QualityControlProcess


def main():
    """공정 연결 예제 실행"""
    
    print("=" * 60)
    print("제조 시뮬레이션 프레임워크 - 공정 연결 예제")
    print("=" * 60)
    
    # 샘플 기계와 작업자 리스트 생성
    machines = ["CNC기계1", "용접기1", "프레스1"]
    workers = ["작업자A", "작업자B", "작업자C"]
    inspection_criteria = {"강도": "> 100N", "정밀도": "± 0.1mm"}
    
    # 각 공정 인스턴스 생성
    print("\n1. 공정 인스턴스 생성")
    manufacturing = ManufacturingProcess(
        machines=machines[:2], 
        workers=workers[:2], 
        process_id="P001",
        process_name="원료가공공정"
    )
    print(f"   ✓ {manufacturing}")
    
    assembly = AssemblyProcess(
        machines=machines[1:], 
        workers=workers[1:], 
        process_id="P002",
        process_name="부품조립공정"
    )
    print(f"   ✓ {assembly}")
    
    quality_control = QualityControlProcess(
        inspection_criteria=inspection_criteria, 
        process_id="P003",
        process_name="최종품질검사"
    )
    print(f"   ✓ {quality_control}")
    
    # >> 연산자를 사용한 공정 연결 예제
    print("\n2. >> 연산자를 사용한 공정 연결")
    
    # 방법 1: 두 공정 연결
    print("\n   [방법 1] 두 공정 직접 연결")
    chain1 = manufacturing >> assembly
    print(f"   연결 결과: {chain1}")
    
    # 방법 2: 세 공정 연쇄 연결
    print("\n   [방법 2] 세 공정 연쇄 연결")
    chain2 = manufacturing >> assembly >> quality_control
    print(f"   연결 결과: {chain2}")
    
    # 방법 3: 체인에 추가 공정 연결
    print("\n   [방법 3] 기존 체인에 공정 추가")
    additional_qc = QualityControlProcess(
        inspection_criteria={"외관": "양호"}, 
        process_id="P004",
        process_name="외관검사"
    )
    extended_chain = chain1 >> additional_qc
    print(f"   연결 결과: {extended_chain}")
    
    # 공정 체인 실행 예제
    print("\n3. 공정 체인 실행")
    print("\n   전체 공정 체인 실행:")
    sample_product = "샘플제품A"
    result = chain2.execute_chain(sample_product)
    
    # 공정 연결 정보 확인
    print("\n4. 공정 연결 정보 확인")
    print(f"\n   {manufacturing.process_name} 연결 정보:")
    info = manufacturing.get_process_info()
    print(f"   - 다음 공정: {info['next_processes']}")
    print(f"   - 이전 공정: {info['previous_processes']}")
    
    print(f"\n   {assembly.process_name} 연결 정보:")
    info = assembly.get_process_info()
    print(f"   - 다음 공정: {info['next_processes']}")
    print(f"   - 이전 공정: {info['previous_processes']}")
    
    # 복잡한 체인 예제
    print("\n5. 복잡한 공정 체인 예제")
    
    # 병렬 공정을 위한 추가 공정들
    packaging = AssemblyProcess(
        machines=["포장기1"], 
        workers=["포장작업자"], 
        process_id="P005",
        process_name="포장공정"
    )
    
    final_inspection = QualityControlProcess(
        inspection_criteria={"포장상태": "완전"}, 
        process_id="P006",
        process_name="출하전검사"
    )
    
    # 복잡한 체인 생성
    complex_chain = manufacturing >> assembly >> quality_control >> packaging >> final_inspection
    print(f"\n   복잡한 공정 체인: {complex_chain}")
    print(f"   총 공정 수: {len(complex_chain.processes)}")
    
    # 새로운 기능: 다중공정 그룹화 (& 연산자 사용)
    print("\n6. 다중공정 그룹화 및 연결 예제 (& 연산자)")
    
    # 병렬로 실행할 수 있는 추가 공정들 생성
    heat_treatment = ManufacturingProcess(
        machines=["열처리로1"], 
        workers=["열처리작업자"], 
        process_id="P007",
        process_name="열처리공정"
    )
    
    surface_coating = ManufacturingProcess(
        machines=["코팅기1"], 
        workers=["코팅작업자"], 
        process_id="P008",
        process_name="표면코팅공정"
    )
    
    dimensional_check = QualityControlProcess(
        inspection_criteria={"치수": "± 0.05mm"}, 
        process_id="P009",
        process_name="치수검사"
    )
    
    print(f"   추가 공정 생성 완료:")
    print(f"   - {heat_treatment}")
    print(f"   - {surface_coating}")
    print(f"   - {dimensional_check}")
    
    # 방법 1: 두 공정을 & 연산자로 그룹화
    print("\n   [방법 1] 두 공정 그룹화 (열처리 & 표면코팅)")
    parallel_group1 = heat_treatment & surface_coating
    print(f"   그룹 생성: {parallel_group1}")
    
    # 방법 2: 세 공정을 & 연산자로 그룹화
    print("\n   [방법 2] 세 공정 그룹화 (조립 & 열처리 & 표면코팅)")
    parallel_group2 = assembly & heat_treatment & surface_coating
    print(f"   그룹 생성: {parallel_group2}")
    
    # 방법 3: 그룹을 다음 공정과 연결 (group >> next_process)
    print("\n   [방법 3] 그룹을 다음 공정과 연결")
    chain_with_group = parallel_group1 >> dimensional_check
    print(f"   연결 결과: {chain_with_group}")
    
    # 방법 4: 복합 체인 (일반공정 >> 그룹 >> 일반공정)
    print("\n   [방법 4] 복합 체인 생성")
    complex_group_chain = manufacturing >> (heat_treatment & surface_coating) >> final_inspection
    print(f"   복합 체인: {complex_group_chain}")
    
    # 방법 5: 다중 그룹을 포함한 전체 공정 라인
    print("\n   [방법 5] 전체 제조 라인 (다중 그룹 포함)")
    # 원료가공 >> (병렬처리: 열처리&표면코팅) >> 조립 >> (병렬검사: 치수검사&품질검사) >> 포장
    quality_group = dimensional_check & quality_control
    processing_group = heat_treatment & surface_coating
    
    full_manufacturing_line = manufacturing >> processing_group >> assembly >> quality_group >> packaging
    print(f"   전체 제조 라인: {full_manufacturing_line}")
    print(f"   총 공정 단계: {len(full_manufacturing_line.processes)}")
    
    # 그룹 체인 실행 테스트
    print("\n7. 다중공정 그룹 체인 실행 테스트")
    print("\n   간단한 그룹 체인 실행:")
    sample_product = "테스트제품B"
    group_result = chain_with_group.execute_chain(sample_product)
    
    print("\n" + "=" * 60)
    print("다중공정 연결 예제 실행 완료!")
    print("사용된 새로운 기능:")
    print("- & 연산자: 공정들을 병렬 그룹으로 묶기")
    print("- 그룹 >> 공정: 그룹 완료 후 다음 공정 실행")
    print("- 복합 체인: 단일공정과 그룹을 혼합한 체인")
    print("=" * 60)


if __name__ == "__main__":
    main()
