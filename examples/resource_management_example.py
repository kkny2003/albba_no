"""
새로운 자원 관리 시스템을 테스트하는 예제입니다.
모든 프로세스가 입력자원과 출력자원을 명시적으로 관리하는 것을 보여줍니다.
"""

import sys
import os

# 프로젝트 루트 디렉토리를 Python 경로에 추가
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from src.Resource.helper import (Resource, ResourceRequirement, ResourceType, 
                                create_transport_resource, create_product_resource,
                                create_worker_resource, create_machine_resource)
from src.core.resource_manager import ResourceManager
from src.processes.manufacturing_process import ManufacturingProcess
from src.processes.assembly_process import AssemblyProcess
from src.processes.quality_control_process import QualityControlProcess


def main():
    """메인 실행 함수"""
    print("=== 자원 관리 시스템 테스트 시작 ===\n")
    
    # 1. 자원 관리자 생성
    resource_manager = ResourceManager()
    
    # 2. 기본 자원들 생성 및 등록
    print("🔧 기본 자원 등록 중...")
    
    # 원자재 자원 (헬퍼 함수 사용)
    raw_material = create_product_resource(
        product_id="raw_material_001",
        product_name="원자재",
        product_type=ResourceType.RAW_MATERIAL,
        quantity=10.0,
        sku="RM-001",
        unit="kg"
    )
    resource_manager.add_resource(raw_material)
    
    # 기계 자원들 (헬퍼 함수 사용)
    machine1 = create_machine_resource(
        machine_id="machine_001",
        machine_name="제조기계_1",
        machine_type="CNC 가공기",
        capacity=5.0  # 시간당 5개 가공 가능
    )
    machine2 = create_machine_resource(
        machine_id="machine_002", 
        machine_name="조립기계_1",
        machine_type="자동 조립기",
        capacity=3.0  # 시간당 3개 조립 가능
    )
    resource_manager.add_resource(machine1)
    resource_manager.add_resource(machine2)
    
    # 작업자 자원들 (헬퍼 함수 사용)
    worker1 = create_worker_resource(
        worker_id="worker_001",
        worker_name="제조작업자_1",
        skill_level="고급",
        department="제조부"
    )
    worker2 = create_worker_resource(
        worker_id="worker_002",
        worker_name="조립작업자_1", 
        skill_level="중급",
        department="조립부"
    )
    worker3 = create_worker_resource(
        worker_id="worker_003",
        worker_name="품질검사원_1",
        skill_level="고급", 
        department="품질관리부"
    )
    resource_manager.add_resource(worker1)
    resource_manager.add_resource(worker2)
    resource_manager.add_resource(worker3)
    
    # 운송 자원들 추가
    forklift1 = create_transport_resource(
        transport_id="forklift_001",
        transport_name="지게차_1호",
        capacity=500.0,  # 500kg 운반 가능
        transport_type="지게차"
    )
    conveyor_belt = create_transport_resource(
        transport_id="conveyor_001", 
        transport_name="컨베이어벨트_1번",
        capacity=100.0,  # 100개/분 처리 가능
        transport_type="컨베이어벨트"
    )
    transport_cart = create_transport_resource(
        transport_id="cart_001",
        transport_name="운반카트_1번", 
        capacity=50.0,   # 50개 운반 가능
        transport_type="운반카트"
    )
    
    resource_manager.add_resource(forklift1)
    resource_manager.add_resource(conveyor_belt)
    resource_manager.add_resource(transport_cart)
    
    print(f"\n현재 자원 재고 상태:")
    print(f"  원자재: {resource_manager.get_available_quantity('raw_material_001')}kg")
    print(f"  기계 수: {len(resource_manager.get_resources_by_type(ResourceType.MACHINE))}대")
    print(f"  작업자 수: {len(resource_manager.get_resources_by_type(ResourceType.WORKER))}명")
    print(f"  운송장비 수: {len(resource_manager.get_resources_by_type(ResourceType.TRANSPORT))}대")
    
    # 3. 제조 공정 생성 및 실행
    print("\n🏭 제조 공정 생성 및 실행...")
    
    # 제조 공정에 필요한 자원들을 사전에 할당
    manufacturing_process = ManufacturingProcess(
        machines=[machine1],
        workers=[worker1],
        process_name="원자재_제조공정"
    )
    
    # 원자재를 제조 공정의 입력 자원에 추가
    manufacturing_process.add_input_resource(raw_material.clone(2.0))  # 2kg의 원자재 필요
    
    # 운송 자원을 제조 공정에 추가 (원자재 운반용)
    manufacturing_process.add_input_resource(forklift1.clone())  # 지게차 사용
    
    print(f"\n제조 공정 자원 상태:")
    status = manufacturing_process.get_resource_status()
    for key, value in status.items():
        print(f"  {key}: {value}")
    
    # 제조 공정 실행
    manufacturing_result = manufacturing_process.execute("기본제품_A")
    print(f"\n제조 공정 실행 결과: {manufacturing_result}")
    
    # 4. 조립 공정 생성 및 실행
    print("\n🔧 조립 공정 생성 및 실행...")
    
    assembly_process = AssemblyProcess(
        machines=[machine2],
        workers=[worker2],
        process_name="제품_조립공정"
    )
    
    # 제조 공정의 출력을 조립 공정의 입력으로 사용
    if manufacturing_result and 'produced_resources' in manufacturing_result:
        for produced_resource in manufacturing_result['produced_resources']:
            if produced_resource.resource_type == ResourceType.SEMI_FINISHED:
                # 조립을 위해 2개의 반제품 필요
                assembly_process.add_input_resource(produced_resource.clone(2.0))
    
    # 운송 자원을 조립 공정에 추가 (반제품 운반용)
    assembly_process.add_input_resource(conveyor_belt.clone())  # 컨베이어벨트 사용
    
    print(f"\n조립 공정 자원 상태:")
    assembly_status = assembly_process.get_resource_status()
    for key, value in assembly_status.items():
        print(f"  {key}: {value}")
    
    # 조립 공정 실행
    assembly_result = assembly_process.execute(manufacturing_result['result'] if manufacturing_result else "기본_조립품")
    print(f"\n조립 공정 실행 결과: {assembly_result}")
    
    # 5. 품질 관리 공정 생성 및 실행
    print("\n🔍 품질 관리 공정 생성 및 실행...")
    
    quality_control = QualityControlProcess(
        inspection_criteria={"품질기준": "우수"},
        process_name="최종_품질검사"
    )
    
    # 조립 공정의 출력을 품질 관리 공정의 입력으로 사용
    if assembly_result and 'produced_resources' in assembly_result:
        for produced_resource in assembly_result['produced_resources']:
            if produced_resource.resource_type == ResourceType.FINISHED_PRODUCT:
                quality_control.add_input_resource(produced_resource)
    
    # 운송 자원을 품질 관리 공정에 추가 (완제품 운반용)
    quality_control.add_input_resource(transport_cart.clone())  # 운반카트 사용
    
    print(f"\n품질 관리 공정 자원 상태:")
    qc_status = quality_control.get_resource_status()
    for key, value in qc_status.items():
        print(f"  {key}: {value}")
    
    # 품질 관리 공정 실행
    quality_result = quality_control.execute(assembly_result['result'] if assembly_result else "기본_완제품")
    print(f"\n품질 관리 공정 실행 결과: {quality_result}")
    
    # 6. 전체 공정 체인 실행 결과 요약
    print("\n📊 전체 공정 체인 실행 요약:")
    print(f"  1. 제조 공정: {manufacturing_result['result'] if manufacturing_result else 'None'}")
    print(f"  2. 조립 공정: {assembly_result['result'] if assembly_result else 'None'}")
    print(f"  3. 품질 관리: {quality_result['result'] if quality_result else 'None'}")
    
    # 7. 최종 자원 재고 상태
    print(f"\n📦 최종 자원 재고 상태:")
    final_inventory = resource_manager.get_inventory_status()
    for key, value in final_inventory.items():
        print(f"  {key}: {value}")
    
    print("\n=== 자원 관리 시스템 테스트 완료 ===")


if __name__ == "__main__":
    main()
