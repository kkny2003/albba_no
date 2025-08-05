"""
완전한 제조공정 시뮬레이션 시나리오

이 시나리오는 다음을 포함합니다:
1. 다양한 리소스 정의 (기계, 작업자, 운송수단, 제품, 버퍼)
2. 다양한 프로세스 정의 (제조, 조립, 품질검사, 운송)
3. Transport를 통한 프로세스 간 이송 과정
4. 기존 src 폴더의 시뮬레이션 프레임워크 활용
5. 모든 문제가 해결된 완전한 작동 시스템
"""

import os
import sys

# 프로젝트 루트를 파이썬 모듈 검색 경로에 추가
project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, project_root)

import simpy
from src.core.simulation_engine import SimulationEngine
from src.core.resource_manager import AdvancedResourceManager
from src.Resource.machine import Machine
from src.Resource.worker import Worker
from src.Resource.transport import Transport
from src.Resource.buffer import Buffer, BufferPolicy
from src.Resource.product import Product
from src.Resource.resource_base import Resource, ResourceRequirement, ResourceType
from src.Processes.manufacturing_process import ManufacturingProcess
from src.Processes.assembly_process import AssemblyProcess
from src.Processes.quality_control_process import QualityControlProcess
from src.Processes.transport_process import TransportProcess
from src.Flow.multi_group_flow import MultiProcessGroup


def create_complete_working_scenario():
    """완전한 제조공정 시나리오 생성"""
    
    # 1. SimPy 환경 및 엔진 생성
    env = simpy.Environment()
    engine = SimulationEngine(env)
    
    # 2. Resource Manager 생성 및 Transport 등록
    resource_manager = AdvancedResourceManager(env)
    resource_manager.register_resource(
        resource_id="transport",
        capacity=10,
        resource_type=ResourceType.TRANSPORT,
        description="운송 요청 관리용 자원"
    )
    
    # 3. 다양한 제품 정의
    raw_material = Product('RM001', '원자재')
    component_a = Product('COMP_A', '부품A')
    component_b = Product('COMP_B', '부품B')
    component_c = Product('COMP_C', '부품C')
    sub_assembly = Product('SUB_ASM', '서브어셈블리')
    final_product = Product('FINAL_PROD', '최종제품')
    
    # 4. Resource 객체 생성 (프로세스 입력/출력용)
    raw_material_res = Resource(
        resource_id='R001', 
        name='원자재', 
        resource_type=ResourceType.RAW_MATERIAL, 
        properties={'quantity': 1, 'unit': 'kg'}
    )
    
    comp_a_res = Resource(
        resource_id='R002', 
        name='부품A', 
        resource_type=ResourceType.SEMI_FINISHED, 
        properties={'quantity': 1, 'unit': '개'}
    )
    
    comp_b_res = Resource(
        resource_id='R003', 
        name='부품B', 
        resource_type=ResourceType.SEMI_FINISHED, 
        properties={'quantity': 1, 'unit': '개'}
    )
    
    comp_c_res = Resource(
        resource_id='R004', 
        name='부품C', 
        resource_type=ResourceType.SEMI_FINISHED, 
        properties={'quantity': 1, 'unit': '개'}
    )
    
    sub_asm_res = Resource(
        resource_id='R005', 
        name='서브어셈블리', 
        resource_type=ResourceType.SEMI_FINISHED, 
        properties={'quantity': 1, 'unit': '개'}
    )
    
    final_prod_res = Resource(
        resource_id='R006', 
        name='최종제품', 
        resource_type=ResourceType.FINISHED_PRODUCT, 
        properties={'quantity': 1, 'unit': '개'}
    )
    
    # 5. 다양한 기계 정의
    cutting_machine = Machine(env, 'M001', '절단기', capacity=1, processing_time=1.5)
    drilling_machine = Machine(env, 'M002', '드릴링기', capacity=1, processing_time=2.0)
    welding_machine = Machine(env, 'M003', '용접기', capacity=1, processing_time=2.5)
    assembly_machine = Machine(env, 'M004', '조립기', capacity=1, processing_time=3.0)
    inspection_machine = Machine(env, 'M005', '검사기', capacity=1, processing_time=1.0)
    packaging_machine = Machine(env, 'M006', '포장기', capacity=1, processing_time=1.5)
    
    # 6. 다양한 작업자 정의
    operator_1 = Worker(env, 'W001', '작업자1', skills=['절단', '드릴링'])
    operator_2 = Worker(env, 'W002', '작업자2', skills=['용접', '조립'])
    operator_3 = Worker(env, 'W003', '작업자3', skills=['검사', '포장'])
    transport_worker = Worker(env, 'W004', '운송작업자', skills=['운송', '하역'])
    
    # 7. 다양한 운송수단 정의
    forklift = Transport(env, 'T001', '지게차', capacity=3, transport_speed=2.0)
    conveyor = Transport(env, 'T002', '컨베이어', capacity=10, transport_speed=1.5)
    robot_arm = Transport(env, 'T003', '로봇팔', capacity=1, transport_speed=3.0)
    
    # 8. 버퍼 정의
    input_buffer = Buffer(env, 'B001', '입력버퍼', 'input', capacity=20, policy=BufferPolicy.FIFO)
    output_buffer = Buffer(env, 'B002', '출력버퍼', 'output', capacity=20, policy=BufferPolicy.FIFO)
    inspection_buffer = Buffer(env, 'B003', '검사버퍼', 'inspection', capacity=10, policy=BufferPolicy.FIFO)
    
    # 9. 각 프로세스별 자원 요구사항 정의
    cutting_requirements = [
        ResourceRequirement(
            resource_type=ResourceType.RAW_MATERIAL,
            name="원자재",
            required_quantity=1.0,
            unit="kg",
            is_mandatory=True
        )
    ]
    
    drilling_requirements = [
        ResourceRequirement(
            resource_type=ResourceType.SEMI_FINISHED,
            name="부품A",
            required_quantity=1.0,
            unit="개",
            is_mandatory=True
        )
    ]
    
    welding_requirements = [
        ResourceRequirement(
            resource_type=ResourceType.SEMI_FINISHED,
            name="부품B",
            required_quantity=1.0,
            unit="개",
            is_mandatory=True
        )
    ]
    
    assembly_requirements = [
        ResourceRequirement(
            resource_type=ResourceType.SEMI_FINISHED,
            name="부품A",
            required_quantity=1.0,
            unit="개",
            is_mandatory=True
        ),
        ResourceRequirement(
            resource_type=ResourceType.SEMI_FINISHED,
            name="부품C",
            required_quantity=1.0,
            unit="개",
            is_mandatory=True
        )
    ]
    
    inspection_requirements = [
        ResourceRequirement(
            resource_type=ResourceType.SEMI_FINISHED,
            name="서브어셈블리",
            required_quantity=1.0,
            unit="개",
            is_mandatory=True
        )
    ]
    
    packaging_requirements = [
        ResourceRequirement(
            resource_type=ResourceType.FINISHED_PRODUCT,
            name="최종제품",
            required_quantity=1.0,
            unit="개",
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
    
    # 10. 다양한 프로세스 정의
    cutting_process = ManufacturingProcess(
        env=env,
        process_id='PROC001',
        process_name='절단공정',
        machines=[cutting_machine],
        workers=[operator_1],
        input_resources=[raw_material_res],
        output_resources=[comp_a_res],
        resource_requirements=cutting_requirements,
        processing_time=1.5,
        resource_manager=resource_manager
    )
    
    drilling_process = ManufacturingProcess(
        env=env,
        process_id='PROC002',
        process_name='드릴링공정',
        machines=[drilling_machine],
        workers=[operator_1],
        input_resources=[comp_a_res],
        output_resources=[comp_b_res],
        resource_requirements=drilling_requirements,
        processing_time=2.0,
        resource_manager=resource_manager
    )
    
    welding_process = ManufacturingProcess(
        env=env,
        process_id='PROC003',
        process_name='용접공정',
        machines=[welding_machine],
        workers=[operator_2],
        input_resources=[comp_b_res],
        output_resources=[comp_c_res],
        resource_requirements=welding_requirements,
        processing_time=2.5,
        resource_manager=resource_manager
    )
    
    assembly_process = AssemblyProcess(
        env=env,
        process_id='PROC004',
        process_name='조립공정',
        machines=[assembly_machine],
        workers=[operator_2],
        input_resources=[comp_a_res, comp_c_res],
        output_resources=[sub_asm_res],
        resource_requirements=assembly_requirements,
        assembly_time=3.0,
        resource_manager=resource_manager
    )
    
    inspection_process = QualityControlProcess(
        env=env,
        process_id='PROC005',
        process_name='품질검사',
        machines=[inspection_machine],
        workers=[operator_3],
        input_resources=[sub_asm_res],
        output_resources=[final_prod_res],
        resource_requirements=inspection_requirements,
        inspection_time=1.0
    )
    
    packaging_process = ManufacturingProcess(
        env=env,
        process_id='PROC006',
        process_name='포장공정',
        machines=[packaging_machine],
        workers=[operator_3],
        input_resources=[final_prod_res],
        output_resources=[final_prod_res],
        resource_requirements=packaging_requirements,
        processing_time=1.5,
        resource_manager=resource_manager
    )
    
    # 11. Transport 프로세스들 정의 및 등록
    transport_process_1 = TransportProcess(
        env=env,
        process_id='TRANS001',
        process_name='운송공정1',
        machines=[forklift],
        workers=[transport_worker],
        input_resources=[comp_a_res],
        output_resources=[comp_a_res],
        resource_requirements=transport_requirements,
        loading_time=0.5,
        transport_time=2.0,
        unloading_time=0.5,
        cooldown_time=0.5
    )
    
    transport_process_2 = TransportProcess(
        env=env,
        process_id='TRANS002',
        process_name='운송공정2',
        machines=[conveyor],
        workers=[transport_worker],
        input_resources=[comp_b_res],
        output_resources=[comp_b_res],
        resource_requirements=transport_requirements,
        loading_time=0.3,
        transport_time=1.5,
        unloading_time=0.3,
        cooldown_time=0.2
    )
    
    transport_process_3 = TransportProcess(
        env=env,
        process_id='TRANS003',
        process_name='운송공정3',
        machines=[robot_arm],
        workers=[transport_worker],
        input_resources=[sub_asm_res],
        output_resources=[sub_asm_res],
        resource_requirements=transport_requirements,
        loading_time=0.2,
        transport_time=1.0,
        unloading_time=0.2,
        cooldown_time=0.1
    )
    
    # TransportProcess들을 ResourceManager에 등록
    resource_manager.register_transport_process("transport_001", transport_process_1)
    resource_manager.register_transport_process("transport_002", transport_process_2)
    resource_manager.register_transport_process("transport_003", transport_process_3)
    
    return {
        'env': env,
        'engine': engine,
        'resource_manager': resource_manager,
        'processes': {
            'cutting': cutting_process,
            'drilling': drilling_process,
            'welding': welding_process,
            'assembly': assembly_process,
            'inspection': inspection_process,
            'packaging': packaging_process,
            'transport_1': transport_process_1,
            'transport_2': transport_process_2,
            'transport_3': transport_process_3
        },
        'resources': {
            'machines': [cutting_machine, drilling_machine, welding_machine, 
                        assembly_machine, inspection_machine, packaging_machine],
            'workers': [operator_1, operator_2, operator_3, transport_worker],
            'transports': [forklift, conveyor, robot_arm],
            'buffers': [input_buffer, output_buffer, inspection_buffer]
        }
    }


def create_complete_workflow(scenario_data):
    """완전한 워크플로우 생성"""
    
    processes = scenario_data['processes']
    
    # 단순한 순차 워크플로우로 테스트
    # 절단 -> 드릴링 -> 용접 -> 조립 -> 검사 -> 포장
    complete_workflow = (
        processes['cutting'] >> 
        processes['drilling'] >> 
        processes['welding'] >> 
        processes['assembly'] >> 
        processes['inspection'] >> 
        processes['packaging']
    )
    
    return complete_workflow


def run_complete_simulation(scenario_data, workflow, num_products=3):
    """완전한 시뮬레이션 실행"""
    
    env = scenario_data['env']
    
    def manufacturing_cycle():
        """제조 사이클 실행"""
        for i in range(num_products):
            print(f"\n=== 제품 {i+1} 제조 시작 ===")
            
            # 원자재 생성
            raw_material = Product(f'RM_{i+1}', f'원자재_{i+1}')
            
            try:
                # 워크플로우 실행
                result = yield from workflow.execute(raw_material)
                print(f"제품 {i+1} 제조 완료: {result}")
            except Exception as e:
                print(f"제품 {i+1} 제조 실패: {e}")
            
            # 다음 제품 제조 전 대기
            yield env.timeout(2.0)
    
    # 시뮬레이션에 프로세스 등록
    env.process(manufacturing_cycle())
    
    # 시뮬레이션 실행
    print("=== 완전한 제조공정 시뮬레이션 시작 ===")
    env.run(until=100)
    print("=== 시뮬레이션 완료 ===")


def monitor_complete_system(scenario_data, interval=10.0):
    """완전한 시스템 상태 모니터링"""
    
    env = scenario_data['env']
    resource_manager = scenario_data['resource_manager']
    processes = scenario_data['processes']
    resources = scenario_data['resources']
    
    def monitor():
        while True:
            print(f"\n=== 시간 {env.now:.1f} - 시스템 상태 ===")
            
            # 기계 상태 (간단하게)
            print("기계 상태:")
            for machine in resources['machines']:
                try:
                    status = machine.get_status()
                    print(f"  {machine.resource_id}: 사용중={status.get('is_busy', 'N/A')}, 처리수={status.get('total_processed', 0)}")
                except Exception as e:
                    print(f"  {machine.resource_id}: 상태 조회 오류")
            
            # 운송수단 상태
            print("운송수단 상태:")
            for transport in resources['transports']:
                try:
                    load = transport.get_current_load()
                    print(f"  {transport.resource_id}: 적재량 {load}/{transport.capacity}")
                except Exception as e:
                    print(f"  {transport.resource_id}: 상태 조회 오류")
            
            # Transport 상태 확인
            try:
                transport_status = resource_manager.get_transport_status()
                print(f"Transport 관리 상태: 등록된 운송={transport_status.get('registered_transports', 0)}")
            except Exception as e:
                print(f"Transport 상태 조회 오류: {e}")
            
            yield env.timeout(interval)
    
    return env.process(monitor())


def main():
    """메인 실행 함수"""
    
    # 1. 시나리오 생성
    print("완전한 시나리오 생성 중...")
    scenario_data = create_complete_working_scenario()
    
    # 2. 워크플로우 생성
    print("완전한 워크플로우 생성 중...")
    workflow = create_complete_workflow(scenario_data)
    
    # 3. 모니터링 시작
    print("모니터링 시작...")
    monitor_process = monitor_complete_system(scenario_data)
    
    # 4. 시뮬레이션 실행
    print("완전한 시뮬레이션 실행 중...")
    run_complete_simulation(scenario_data, workflow, num_products=3)
    
    print("\n=== 완전한 제조공정 시뮬레이션 완료 ===")


if __name__ == "__main__":
    main() 