# -*- coding: utf-8 -*-
"""
BOM to OWL Converter
온톨로지 맵핑 및 OWL 저장 전용 스크립트
"""

import xml.etree.ElementTree as ET
import sys

try:
    from owlready2 import *
    
    # template.py에서 온톨로지 정의 import
    from template import (
        onto, ProcessID, ProcessType, ProcessDetail, Material,
        hasProcessType, hasMaterial, hasPrecedingProcess,
        Module, EBoM, Level, hasLevel,
        ProcessingTime, Cost, CarbonFootprint, Quantity,
        hasProcessingTime, hasCost, hasCarbonFootprint, hasQuantity,
        hasProductName, hasComponents,
        Machine, isMachineOf, hasChildren, Storage, isStorageOf
    )
    
except ImportError as e:
    print(f"패키지 import 오류: {e}")
    print("필요한 패키지들을 설치해주세요: pip install owlready2")
    sys.exit(1)

def makeOntology(mbom_filename, ebom_filename):
    """
    E-BOM과 M-BOM 파일을 파싱하여 온톨로지 인스턴스를 생성하고 OWL 형식으로 저장
    
    Args:
        mbom_filename (str): M-BOM XML 파일 경로
        ebom_filename (str): E-BOM XML 파일 경로
    
    Returns:
        bool: 성공 여부
    """

    # 1. 인스턴스 캐시 초기화
    instances = {
        "ProcessID": {},
        "ProcessType": {},
        "ProcessDetail": {},
        "Material": {},
        "Module": {},
        "EBoM": {},
        "Level": {},
        "Machine": {}
    }

    # 2. E-BOM 파싱
    print(f"E-BOM 파일 파싱 중: {ebom_filename}")
    ebom_tree = ET.parse(ebom_filename)
    ebom_root = ebom_tree.getroot()

    def process_ebom_element(elem, parent_inst=None):
        """E-BOM 요소를 재귀적으로 처리"""
        name = elem.findtext("Name", "").strip()
        level = elem.findtext("Level", "").strip()
        
        if not name or not level:
            return

        # Level 인스턴스 생성 또는 가져오기
        if level not in instances["Level"]:
            level_ind = Level(level)
            instances["Level"][level] = level_ind
        else:
            level_ind = instances["Level"][level]

        # Level 0는 Module, 나머지는 EBoM으로 분류
        if level == "0":
            obj = Module(name.replace(" ", "_"))
            instances["Module"][name] = obj
        else:
            obj = EBoM(name.replace(" ", "_"))
            instances["EBoM"][name] = obj
        
        obj.hasLevel = [level_ind]

        # 부모-자식 관계 설정
        if parent_inst and isinstance(obj, EBoM) and isinstance(parent_inst, EBoM):
            parent_inst.hasChildren.append(obj)

        # 하위 Part 요소들 재귀 처리
        for part_elem in elem.findall("Part"):
            process_ebom_element(part_elem, parent_inst=obj)

    # Assembly 요소 처리
    assembly_elem = ebom_root.find("Assembly")
    if assembly_elem is not None:
        process_ebom_element(assembly_elem)

    # 3. M-BOM 파싱
    print(f"M-BOM 파일 파싱 중: {mbom_filename}")
    mbom_tree = ET.parse(mbom_filename)
    mbom_root = mbom_tree.getroot()

    # Processes 섹션 처리
    processes_elem = mbom_root.find("Processes")
    if processes_elem is not None:
        for process_elem in processes_elem.findall("Process"):
            pid = process_elem.get("id", "").strip()
            ptype = process_elem.findtext("ProcessType", "").strip()
            pdetail = process_elem.findtext("ProcessDetail", "").strip()
            material = process_elem.findtext("Material", "").strip()
            part_name = process_elem.findtext("PartName", "").strip()
            pre_refs = process_elem.findall("PrecedingProcesses/ProcessRef")

            # ProcessID 인스턴스 생성
            if pid not in instances["ProcessID"]:
                proc_ind = ProcessID(pid)
                instances["ProcessID"][pid] = proc_ind
            else:
                proc_ind = instances["ProcessID"][pid]

            # ProcessType 연결
            if ptype:
                if ptype not in instances["ProcessType"]:
                    ptype_ind = ProcessType(ptype.replace(" ", "_"))
                    instances["ProcessType"][ptype] = ptype_ind
                else:
                    ptype_ind = instances["ProcessType"][ptype]
                proc_ind.hasProcessType = [ptype_ind]

            # ProcessDetail 연결
            if pdetail and pdetail not in instances["ProcessDetail"]:
                detail_ind = ProcessDetail(pdetail.replace(" ", "_"))
                instances["ProcessDetail"][pdetail] = detail_ind

            # Material 연결 (특정 프로세스 타입에만)
            if ptype in ["Press", "Foaming", "assemble"] and material:
                if material not in instances["Material"]:
                    mat_ind = Material(material.replace(" ", "_"))
                    instances["Material"][material] = mat_ind
                else:
                    mat_ind = instances["Material"][material]
                proc_ind.hasMaterial = [mat_ind]

            # Assembly 타입 프로세스의 컴포넌트 연결
            if ptype.lower() == "assemble":
                comp_elems = process_elem.findall("Components/ComponentName")
                for comp_elem in comp_elems:
                    comp_name = comp_elem.text.strip()
                    if comp_name in instances["EBoM"]:
                        comp_inst = instances["EBoM"][comp_name]
                        proc_ind.hasComponents.append(comp_inst)

            # 선행 프로세스 연결
            preceding_inds = []
            for pre_ref_elem in pre_refs:
                pre_ref = pre_ref_elem.text.strip()
                # N/A도 포함하여 처리
                if pre_ref not in instances["ProcessID"]:
                    pre_ind = ProcessID(pre_ref)
                    instances["ProcessID"][pre_ref] = pre_ind
                else:
                    pre_ind = instances["ProcessID"][pre_ref]
                preceding_inds.append(pre_ind)
            
            if preceding_inds:
                proc_ind.hasPrecedingProcess = preceding_inds

            # ProcessID → EBoM 또는 Module 연결 (hasProductName)
            if part_name:
                part_inst = instances["EBoM"].get(part_name) or instances["Module"].get(part_name)
                if part_inst:
                    proc_ind.hasProductName = [part_inst]

    # 4. Parts 섹션의 속성 연결
    parts_elem = mbom_root.find("Parts")
    if parts_elem is not None:
        for part in parts_elem.findall("Part"):
            name = part.findtext("Name", "").strip()
            qty = part.findtext("Quantity", "").strip()
            time = part.findtext("ProcessTime", "").strip()
            cost = part.findtext("ProcessCost", "").strip()
            carbon = part.findtext("CarbonFootprint", "").strip()

            if name in instances["EBoM"]:
                ebom_inst = instances["EBoM"][name]

                if qty:
                    qty_inst = Quantity(qty.replace("s", "").replace("$", "").replace("gCO2", ""))
                    ebom_inst.hasQuantity = [qty_inst]

                if time:
                    time_inst = ProcessingTime(time.replace("s", ""))
                    ebom_inst.hasProcessingTime = [time_inst]

                if cost:
                    cost_inst = Cost(cost.replace("$", ""))
                    ebom_inst.hasCost = [cost_inst]

                if carbon:
                    carbon_inst = CarbonFootprint(carbon.replace("gCO2", ""))
                    ebom_inst.hasCarbonFootprint = [carbon_inst]
    
 
    # 5. ProcessType 간 서로 다른 개체 지정
    process_types = ["Press", "Foaming", "Assemble"]
    for pt in process_types:
        if pt not in instances["ProcessType"]:
            instances["ProcessType"][pt] = ProcessType(pt)

    

    # 서로 다른 개체로 명시
    different_individuals = list(instances["ProcessType"].values())
    if len(different_individuals) > 1:
        AllDifferent(different_individuals)

    # 6. ProcessDetail → Machine 연결 (최소 수정)
    if processes_elem is not None:
        for process_elem in processes_elem.findall("Process"):
            pid = process_elem.get("id", "").strip()
            detail = process_elem.findtext("ProcessDetail", "").strip()
        
            if pid in instances["ProcessID"] and detail in instances["ProcessDetail"]:
                proc_inst = instances["ProcessID"][pid]
                detail_inst = instances["ProcessDetail"][detail]
                
                # 기존 연결이 있는지 확인 후 추가 (덮어쓰기 방지)
                if hasattr(detail_inst, 'isMachineOf') and detail_inst.isMachineOf:
                    # 이미 연결된 프로세스가 있다면 추가
                    if proc_inst not in detail_inst.isMachineOf:
                        detail_inst.isMachineOf.append(proc_inst)
                else:
                    # 첫 번째 연결
                    detail_inst.isMachineOf = [proc_inst]

    # 7. hasChildren 관계 정의 - Assemble 타입 Process에 대해
    if processes_elem is not None:
        for process_elem in processes_elem.findall("Process"):
            process_type = process_elem.findtext("ProcessType", "").strip().lower()
            if process_type == "assemble":
                parent_name = process_elem.findtext("PartName", "").strip()
                component_elems = process_elem.findall("Components/ComponentName")
                
                if parent_name in instances["EBoM"] or parent_name in instances["Module"]:
                    parent_inst = instances["EBoM"].get(parent_name) or instances["Module"].get(parent_name)
                    for comp_elem in component_elems:
                        comp_name = comp_elem.text.strip()
                        if comp_name in instances["EBoM"] or comp_name in instances["Module"]:
                            child_inst = instances["EBoM"].get(comp_name) or instances["Module"].get(comp_name)
                            if child_inst not in parent_inst.hasChildren:
                                parent_inst.hasChildren.append(child_inst)

    # 8. Storage 생성 및 isStorageOf 연결
    raw_material_storage_targets = []
    intermediate_storage_targets = []
    finished_goods_storage_targets = []

    # EBoM 인스턴스 분류
    for name, inst in instances["EBoM"].items():
        if inst.hasLevel:
            level_name = str(inst.hasLevel[0].name)
            if level_name.isdigit() and int(level_name) > 0:
                intermediate_storage_targets.append(inst)

    # Material 인스턴스는 raw material storage에
    raw_material_storage_targets.extend(instances["Material"].values())

    # Module 인스턴스는 finished goods storage에
    finished_goods_storage_targets.extend(instances["Module"].values())

    # Storage 인스턴스 생성 및 연결
    for i, target in enumerate(intermediate_storage_targets):
        storage_inst = Storage(f"I_Storage_{i}")
        storage_inst.isStorageOf = [target]

    for i, target in enumerate(raw_material_storage_targets):
        storage_inst = Storage(f"R_Storage_{i}")
        storage_inst.isStorageOf = [target]

    for i, target in enumerate(finished_goods_storage_targets):
        storage_inst = Storage(f"F_Storage_{i}")
        storage_inst.isStorageOf = [target]

    # 9. 온톨로지 OWL 형식으로 저장
    print("온톨로지를 OWL 형식으로 저장 중...")
    output_file = "onto/generated_bom.owl"
    onto.save(file=output_file, format="rdfxml")
    
    print(f"✅ 온톨로지가 OWL 형식으로 저장되었습니다: {output_file}")
    
    return True


def main():
    """메인 함수"""
    print("BOM to OWL 변환기 시작")
    print("=" * 50)
    
    # 파일 경로 설정
    ebom_file = "onto/E-BOM.xml"
    mbom_file = "onto/M-BOM.xml"

    try:
        # 온톨로지 생성 및 OWL 저장
        success = makeOntology(mbom_file, ebom_file)
        
        if success:
            print("=" * 50)
            print("온톨로지 생성 및 OWL 저장 완료!")
        else:
            print("❌ 온톨로지 생성에 실패했습니다.")
            
    except Exception as e:
        print(f"오류 발생: {e}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    main()
