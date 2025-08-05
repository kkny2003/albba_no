"""
간단한 테스트 시나리오 - 기본 기능 검증

이 시나리오는 다음을 테스트합니다:
1. 기본 제조 프로세스 작동
2. Transport 자동 요청 기능
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
from src.Resource.product import Product
from src.Resource.resource_base import Resource, ResourceRequirement, ResourceType
from src.Processes.manufacturing_process import ManufacturingProcess


def create_simple_test_scenario():
    """간단한 테스트 시나리오 생성"""
    
    # 1. SimPy 환경 생성
    env = simpy.Environment()
    
    # 2. Resource Manager 생성
    resource_manager = AdvancedResourceManager(env)
    resource_manager.register_resource(
        resource_id="transport_slots",
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
    machine = Machine(env, 'M001', '제조기계', capacity=1, processing_time=2.0)
    worker = Worker(env, 'W001', '작업자', skills=['제조'])
    
    # 6. 자원 요구사항 정의
    requirements = [
        ResourceRequirement(
            resource_type=ResourceType.RAW_MATERIAL,
            name="원자재",
            required_quantity=1.0,
            unit="kg",
            is_mandatory=True
        )
    ]
    
    # 7. 제조 프로세스 정의
    manufacturing_process = ManufacturingProcess(
        env=env,
        process_id='PROC001',
        process_name='제조공정',
        machines=[machine],
        workers=[worker],
        input_resources=[raw_material_res],
        output_resources=[final_prod_res],
        resource_requirements=requirements,
        processing_time=2.0,
        resource_manager=resource_manager
    )
    
    return {
        'env': env,
        'resource_manager': resource_manager,
        'process': manufacturing_process,
        'machine': machine,
        'worker': worker
    }


def run_simple_test(scenario_data):
    """간단한 테스트 실행"""
    
    env = scenario_data['env']
    process = scenario_data['process']
    
    def test_cycle():
        """테스트 사이클 실행"""
        print("=== 간단한 제조 테스트 시작 ===")
        
        # 원자재 생성
        raw_material = Product('RM_TEST', '테스트원자재')
        
        try:
            # 프로세스 실행
            print(f"[시간 {env.now:.1f}] 제조 프로세스 시작")
            result = yield from process.process_logic(raw_material)
            print(f"[시간 {env.now:.1f}] 제조 프로세스 완료: {result}")
        except Exception as e:
            print(f"[시간 {env.now:.1f}] 제조 프로세스 실패: {e}")
        
        print("=== 테스트 완료 ===")
    
    # 시뮬레이션에 프로세스 등록
    env.process(test_cycle())
    
    # 시뮬레이션 실행
    env.run(until=10)
    
    # 결과 출력
    print(f"\n=== 최종 결과 ===")
    print(f"시뮬레이션 시간: {env.now:.1f}")
    
    # 기계 상태 확인
    machine_status = scenario_data['machine'].get_status()
    print(f"기계 상태: {machine_status}")
    
    # Resource Manager 상태 확인
    print(f"Resource Manager 자원 수: {len(scenario_data['resource_manager'].resources)}")


def main():
    """메인 실행 함수"""
    
    print("간단한 테스트 시나리오 생성 중...")
    scenario_data = create_simple_test_scenario()
    
    print("테스트 실행 중...")
    run_simple_test(scenario_data)
    
    print("\n=== 간단한 테스트 완료 ===")


if __name__ == "__main__":
    main() 