"""
Transport 할당이 작동하는 시나리오

이 시나리오는 다음을 테스트합니다:
1. TransportProcess를 ResourceManager에 등록
2. Transport 자동 요청 및 할당
3. 자원 흐름
"""

import os
import sys

# 프로젝트 루트를 파이썬 모듈 검색 경로에 추가
project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, project_root)

import simpy
from src.core.resource_manager import AdvancedResourceManager
from src.Resource.machine import Machine
from src.Resource.worker import Worker
from src.Resource.transport import Transport
from src.Resource.product import Product
from src.Resource.resource_base import Resource, ResourceRequirement, ResourceType
from src.Processes.manufacturing_process import ManufacturingProcess
from src.Processes.transport_process import TransportProcess


def create_transport_working_scenario():
    """Transport 할당이 작동하는 시나리오 생성"""
    
    # 1. SimPy 환경 생성
    env = simpy.Environment()
    
    # 2. Resource Manager 생성
    resource_manager = AdvancedResourceManager(env)
    resource_manager.register_resource(
        resource_id="transport",
        capacity=5,
        resource_type=ResourceType.TRANSPORT,
        description="운송 요청 관리용 자원"
    )
    
    # 3. 제품 정의
    raw_material = Product('RM001', '원자재')
    final_product = Product('FINAL', '최종제품')
    
    # 4. Resource 객체 생성
    raw_material_res = Resource(
        resource_id='R001', 
        name='원자재', 
        resource_type=ResourceType.RAW_MATERIAL, 
        properties={'quantity': 1, 'unit': 'kg'}
    )
    
    final_prod_res = Resource(
        resource_id='R002', 
        name='최종제품', 
        resource_type=ResourceType.FINISHED_PRODUCT, 
        properties={'quantity': 1, 'unit': '개'}
    )
    
    # 5. 기계 및 작업자 정의
    manufacturing_machine = Machine(env, 'M001', '제조기계', capacity=1, processing_time=2.0)
    manufacturing_worker = Worker(env, 'W001', '제조작업자', skills=['제조'])
    
    transport_machine = Machine(env, 'T001', '운송차량', capacity=1, processing_time=1.0)
    transport_worker = Worker(env, 'W002', '운송작업자', skills=['운송'])
    
    # 6. 자원 요구사항 정의
    manufacturing_requirements = [
        ResourceRequirement(
            resource_type=ResourceType.RAW_MATERIAL,
            name="원자재",
            required_quantity=1.0,
            unit="kg",
            is_mandatory=True
        )
    ]
    
    transport_requirements = [
        ResourceRequirement(
            resource_type=ResourceType.SEMI_FINISHED,
            name="운송물품",
            required_quantity=1.0,
            unit="개",
            is_mandatory=True
        )
    ]
    
    # 7. 제조 프로세스 정의
    manufacturing_process = ManufacturingProcess(
        env=env,
        process_id='PROC001',
        process_name='제조공정',
        machines=[manufacturing_machine],
        workers=[manufacturing_worker],
        input_resources=[raw_material_res],
        output_resources=[final_prod_res],
        resource_requirements=manufacturing_requirements,
        processing_time=2.0,
        resource_manager=resource_manager
    )
    
    # 8. Transport 프로세스 정의
    transport_process = TransportProcess(
        env=env,
        process_id='TRANS001',
        process_name='운송공정',
        machines=[transport_machine],
        workers=[transport_worker],
        input_resources=[final_prod_res],
        output_resources=[final_prod_res],
        resource_requirements=transport_requirements,
        loading_time=0.5,
        transport_time=1.0,
        unloading_time=0.5,
        cooldown_time=0.2
    )
    
    # 9. TransportProcess를 ResourceManager에 등록 (중요!)
    resource_manager.register_transport_process("transport_001", transport_process)
    
    return {
        'env': env,
        'resource_manager': resource_manager,
        'manufacturing_process': manufacturing_process,
        'transport_process': transport_process,
        'manufacturing_machine': manufacturing_machine,
        'transport_machine': transport_machine
    }


def run_transport_working_test(scenario_data):
    """Transport 할당 테스트 실행"""
    
    env = scenario_data['env']
    manufacturing_process = scenario_data['manufacturing_process']
    
    def test_cycle():
        """테스트 사이클 실행"""
        print("=== Transport 할당 테스트 시작 ===")
        
        # 원자재 생성
        raw_material = Product('RM_TEST', '테스트원자재')
        
        try:
            # 제조 프로세스 실행
            print(f"[시간 {env.now:.1f}] 제조 프로세스 시작")
            result = yield from manufacturing_process.process_logic(raw_material)
            print(f"[시간 {env.now:.1f}] 제조 프로세스 완료: {result}")
        except Exception as e:
            print(f"[시간 {env.now:.1f}] 제조 프로세스 실패: {e}")
        
        print("=== 테스트 완료 ===")
    
    # 시뮬레이션에 프로세스 등록
    env.process(test_cycle())
    
    # 시뮬레이션 실행
    env.run(until=15)
    
    # 결과 출력
    print(f"\n=== 최종 결과 ===")
    print(f"시뮬레이션 시간: {env.now:.1f}")
    
    # 기계 상태 확인
    manufacturing_status = scenario_data['manufacturing_machine'].get_status()
    transport_status = scenario_data['transport_machine'].get_status()
    print(f"제조기계 상태: {manufacturing_status}")
    print(f"운송기계 상태: {transport_status}")
    
    # Resource Manager 상태 확인
    print(f"Resource Manager 자원 수: {len(scenario_data['resource_manager'].resources)}")
    
    # Transport 상태 확인
    transport_status_info = scenario_data['resource_manager'].get_transport_status()
    print(f"Transport 상태: {transport_status_info}")


def main():
    """메인 실행 함수"""
    
    print("Transport 할당 시나리오 생성 중...")
    scenario_data = create_transport_working_scenario()
    
    print("Transport 할당 테스트 실행 중...")
    run_transport_working_test(scenario_data)
    
    print("\n=== Transport 할당 테스트 완료 ===")


if __name__ == "__main__":
    main() 