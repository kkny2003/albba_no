"""
냉장고 제조공정 시뮬레이션 시나리오

이 시나리오는 냉장고 제조공정의 완전한 시뮬레이션을 포함합니다:
1. 다양한 리소스 정의 (기계, 작업자, 운송수단, 제품, 버퍼)
2. 다양한 프로세스 정의 (제조, 조립, 품질검사, 운송)
3. Transport를 통한 프로세스 간 이송 과정
4. 병렬 공정 (도어, 본체, 컴프레서 동시 제조)
5. 다중 공정 (도어 패널, 프레임, 어셈블리 등)
6. 기존 src 폴더의 시뮬레이션 프레임워크 활용
7. 모든 문제가 해결된 완전한 작동 시스템
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


def create_refrigerator_manufacturing_scenario():
    """냉장고 제조공정 시나리오 생성"""
    
    # 1. SimPy 환경 및 엔진 생성
    env = simpy.Environment()
    engine = SimulationEngine(env)
    
    # 2. Resource Manager 생성 및 Transport 등록
    resource_manager = AdvancedResourceManager(env)
    resource_manager.register_resource(
        resource_id="transport",
        capacity=15,
        resource_type=ResourceType.TRANSPORT,
        description="냉장고 제조 운송 요청 관리용 자원"
    )
    
    # 3. 냉장고 제조용 제품 정의
    # 원자재
    steel_sheet = Product('STEEL_SHEET', '강판')
    plastic_panel = Product('PLASTIC_PANEL', '플라스틱 패널')
    insulation_foam = Product('INSULATION_FOAM', '단열폼')
    compressor_unit = Product('COMPRESSOR_UNIT', '컴프레서 유닛')
    door_gasket = Product('DOOR_GASKET', '도어 가스켓')
    door_handle = Product('DOOR_HANDLE', '도어 핸들')
    
    # 도어 관련 부품
    door_panel = Product('DOOR_PANEL', '도어 패널')
    door_frame = Product('DOOR_FRAME', '도어 프레임')
    door_assembly = Product('DOOR_ASSEMBLY', '도어 어셈블리')
    
    # 본체 관련 부품
    body_panel = Product('BODY_PANEL', '본체 패널')
    body_frame = Product('BODY_FRAME', '본체 프레임')
    body_assembly = Product('BODY_ASSEMBLY', '본체 어셈블리')
    
    # 최종 제품
    refrigerator_unit = Product('REFRIGERATOR_UNIT', '냉장고 유닛')
    final_refrigerator = Product('FINAL_REFRIGERATOR', '완성된 냉장고')
    
    # 4. Resource 객체 생성
    steel_sheet_res = Resource(
        resource_id='R001', 
        name='강판', 
        resource_type=ResourceType.RAW_MATERIAL, 
        properties={'quantity': 1, 'unit': '장'}
    )
    
    plastic_panel_res = Resource(
        resource_id='R002', 
        name='플라스틱 패널', 
        resource_type=ResourceType.RAW_MATERIAL, 
        properties={'quantity': 1, 'unit': '장'}
    )
    
    insulation_foam_res = Resource(
        resource_id='R003', 
        name='단열폼', 
        resource_type=ResourceType.RAW_MATERIAL, 
        properties={'quantity': 1, 'unit': '개'}
    )
    
    compressor_unit_res = Resource(
        resource_id='R004', 
        name='컴프레서 유닛', 
        resource_type=ResourceType.SEMI_FINISHED, 
        properties={'quantity': 1, 'unit': '개'}
    )
    
    door_gasket_res = Resource(
        resource_id='R005', 
        name='도어 가스켓', 
        resource_type=ResourceType.SEMI_FINISHED, 
        properties={'quantity': 1, 'unit': '개'}
    )
    
    door_handle_res = Resource(
        resource_id='R006', 
        name='도어 핸들', 
        resource_type=ResourceType.SEMI_FINISHED, 
        properties={'quantity': 1, 'unit': '개'}
    )
    
    door_panel_res = Resource(
        resource_id='R007', 
        name='도어 패널', 
        resource_type=ResourceType.SEMI_FINISHED, 
        properties={'quantity': 1, 'unit': '개'}
    )
    
    door_frame_res = Resource(
        resource_id='R008', 
        name='도어 프레임', 
        resource_type=ResourceType.SEMI_FINISHED, 
        properties={'quantity': 1, 'unit': '개'}
    )
    
    door_assembly_res = Resource(
        resource_id='R009', 
        name='도어 어셈블리', 
        resource_type=ResourceType.SEMI_FINISHED, 
        properties={'quantity': 1, 'unit': '개'}
    )
    
    body_panel_res = Resource(
        resource_id='R010', 
        name='본체 패널', 
        resource_type=ResourceType.SEMI_FINISHED, 
        properties={'quantity': 1, 'unit': '개'}
    )
    
    body_frame_res = Resource(
        resource_id='R011', 
        name='본체 프레임', 
        resource_type=ResourceType.SEMI_FINISHED, 
        properties={'quantity': 1, 'unit': '개'}
    )
    
    body_assembly_res = Resource(
        resource_id='R012', 
        name='본체 어셈블리', 
        resource_type=ResourceType.SEMI_FINISHED, 
        properties={'quantity': 1, 'unit': '개'}
    )
    
    refrigerator_unit_res = Resource(
        resource_id='R013', 
        name='냉장고 유닛', 
        resource_type=ResourceType.SEMI_FINISHED, 
        properties={'quantity': 1, 'unit': '개'}
    )
    
    final_refrigerator_res = Resource(
        resource_id='R014', 
        name='완성된 냉장고', 
        resource_type=ResourceType.FINISHED_PRODUCT, 
        properties={'quantity': 1, 'unit': '개'}
    )
    
    # 5. 냉장고 제조용 기계 정의
    # 도어 제조 라인
    door_panel_cutter = Machine(env, 'M001', '도어패널 절단기', capacity=1, processing_time=2.0)
    door_frame_welder = Machine(env, 'M002', '도어프레임 용접기', capacity=1, processing_time=2.5)
    door_assembler = Machine(env, 'M003', '도어 조립기', capacity=1, processing_time=3.0)
    
    # 본체 제조 라인
    body_panel_cutter = Machine(env, 'M004', '본체패널 절단기', capacity=1, processing_time=2.5)
    body_frame_welder = Machine(env, 'M005', '본체프레임 용접기', capacity=1, processing_time=3.0)
    body_assembler = Machine(env, 'M006', '본체 조립기', capacity=1, processing_time=3.5)
    
    # 컴프레서 및 부품 제조
    compressor_tester = Machine(env, 'M007', '컴프레서 테스터', capacity=1, processing_time=1.5)
    gasket_molder = Machine(env, 'M008', '가스켓 성형기', capacity=1, processing_time=1.0)
    handle_assembler = Machine(env, 'M009', '핸들 조립기', capacity=1, processing_time=1.5)
    
    # 최종 조립 및 검사
    refrigerator_assembler = Machine(env, 'M010', '냉장고 조립기', capacity=1, processing_time=4.0)
    quality_inspector = Machine(env, 'M011', '품질검사기', capacity=1, processing_time=2.0)
    packaging_machine = Machine(env, 'M012', '포장기', capacity=1, processing_time=1.5)
    
    # 6. 작업자 정의
    door_worker_1 = Worker(env, 'W001', '도어작업자1', skills=['절단', '용접'])
    door_worker_2 = Worker(env, 'W002', '도어작업자2', skills=['조립', '검사'])
    body_worker_1 = Worker(env, 'W003', '본체작업자1', skills=['절단', '용접'])
    body_worker_2 = Worker(env, 'W004', '본체작업자2', skills=['조립', '검사'])
    component_worker = Worker(env, 'W005', '부품작업자', skills=['테스트', '성형', '조립'])
    final_assembler = Worker(env, 'W006', '최종조립자', skills=['조립', '검사'])
    transport_worker = Worker(env, 'W007', '운송작업자', skills=['운송', '하역'])
    
    # 7. 운송수단 정의
    forklift = Transport(env, 'T001', '지게차', capacity=5, transport_speed=2.0)
    conveyor = Transport(env, 'T002', '컨베이어', capacity=15, transport_speed=1.5)
    robot_arm = Transport(env, 'T003', '로봇팔', capacity=2, transport_speed=3.0)
    crane = Transport(env, 'T004', '크레인', capacity=3, transport_speed=1.0)
    
    # 8. 버퍼 정의
    door_buffer = Buffer(env, 'B001', '도어버퍼', 'door', capacity=10, policy=BufferPolicy.FIFO)
    body_buffer = Buffer(env, 'B002', '본체버퍼', 'body', capacity=10, policy=BufferPolicy.FIFO)
    component_buffer = Buffer(env, 'B003', '부품버퍼', 'component', capacity=15, policy=BufferPolicy.FIFO)
    assembly_buffer = Buffer(env, 'B004', '조립버퍼', 'assembly', capacity=8, policy=BufferPolicy.FIFO)
    final_buffer = Buffer(env, 'B005', '최종버퍼', 'final', capacity=5, policy=BufferPolicy.FIFO)
    
    # 9. 자원 요구사항 정의
    door_panel_requirements = [
        ResourceRequirement(
            resource_type=ResourceType.RAW_MATERIAL,
            name="강판",
            required_quantity=1.0,
            unit="장",
            is_mandatory=True
        )
    ]
    
    door_frame_requirements = [
        ResourceRequirement(
            resource_type=ResourceType.RAW_MATERIAL,
            name="강판",
            required_quantity=1.0,
            unit="장",
            is_mandatory=True
        )
    ]
    
    door_assembly_requirements = [
        ResourceRequirement(
            resource_type=ResourceType.SEMI_FINISHED,
            name="도어 패널",
            required_quantity=1.0,
            unit="개",
            is_mandatory=True
        ),
        ResourceRequirement(
            resource_type=ResourceType.SEMI_FINISHED,
            name="도어 프레임",
            required_quantity=1.0,
            unit="개",
            is_mandatory=True
        ),
        ResourceRequirement(
            resource_type=ResourceType.SEMI_FINISHED,
            name="도어 가스켓",
            required_quantity=1.0,
            unit="개",
            is_mandatory=True
        ),
        ResourceRequirement(
            resource_type=ResourceType.SEMI_FINISHED,
            name="도어 핸들",
            required_quantity=1.0,
            unit="개",
            is_mandatory=True
        )
    ]
    
    body_panel_requirements = [
        ResourceRequirement(
            resource_type=ResourceType.RAW_MATERIAL,
            name="강판",
            required_quantity=2.0,
            unit="장",
            is_mandatory=True
        )
    ]
    
    body_frame_requirements = [
        ResourceRequirement(
            resource_type=ResourceType.RAW_MATERIAL,
            name="강판",
            required_quantity=1.5,
            unit="장",
            is_mandatory=True
        )
    ]
    
    body_assembly_requirements = [
        ResourceRequirement(
            resource_type=ResourceType.SEMI_FINISHED,
            name="본체 패널",
            required_quantity=1.0,
            unit="개",
            is_mandatory=True
        ),
        ResourceRequirement(
            resource_type=ResourceType.SEMI_FINISHED,
            name="본체 프레임",
            required_quantity=1.0,
            unit="개",
            is_mandatory=True
        ),
        ResourceRequirement(
            resource_type=ResourceType.RAW_MATERIAL,
            name="단열폼",
            required_quantity=2.0,
            unit="개",
            is_mandatory=True
        )
    ]
    
    refrigerator_assembly_requirements = [
        ResourceRequirement(
            resource_type=ResourceType.SEMI_FINISHED,
            name="도어 어셈블리",
            required_quantity=1.0,
            unit="개",
            is_mandatory=True
        ),
        ResourceRequirement(
            resource_type=ResourceType.SEMI_FINISHED,
            name="본체 어셈블리",
            required_quantity=1.0,
            unit="개",
            is_mandatory=True
        ),
        ResourceRequirement(
            resource_type=ResourceType.SEMI_FINISHED,
            name="컴프레서 유닛",
            required_quantity=1.0,
            unit="개",
            is_mandatory=True
        )
    ]
    
    # 10. 도어 제조 라인 프로세스 정의
    door_panel_process = ManufacturingProcess(
        env=env,
        process_id='DOOR_PANEL_PROC',
        process_name='도어패널 제조',
        machines=[door_panel_cutter],
        workers=[door_worker_1],
        input_resources=[steel_sheet_res],
        output_resources=[door_panel_res],
        resource_requirements=door_panel_requirements,
        processing_time=2.0,
        resource_manager=resource_manager
    )
    
    door_frame_process = ManufacturingProcess(
        env=env,
        process_id='DOOR_FRAME_PROC',
        process_name='도어프레임 제조',
        machines=[door_frame_welder],
        workers=[door_worker_1],
        input_resources=[steel_sheet_res],
        output_resources=[door_frame_res],
        resource_requirements=door_frame_requirements,
        processing_time=2.5,
        resource_manager=resource_manager
    )
    
    door_assembly_process = AssemblyProcess(
        env=env,
        process_id='DOOR_ASSEMBLY_PROC',
        process_name='도어 어셈블리',
        machines=[door_assembler],
        workers=[door_worker_2],
        input_resources=[door_panel_res, door_frame_res, door_gasket_res, door_handle_res],
        output_resources=[door_assembly_res],
        resource_requirements=door_assembly_requirements,
        assembly_time=3.0,
        resource_manager=resource_manager
    )
    
    # 11. 본체 제조 라인 프로세스 정의
    body_panel_process = ManufacturingProcess(
        env=env,
        process_id='BODY_PANEL_PROC',
        process_name='본체패널 제조',
        machines=[body_panel_cutter],
        workers=[body_worker_1],
        input_resources=[steel_sheet_res],
        output_resources=[body_panel_res],
        resource_requirements=body_panel_requirements,
        processing_time=2.5,
        resource_manager=resource_manager
    )
    
    body_frame_process = ManufacturingProcess(
        env=env,
        process_id='BODY_FRAME_PROC',
        process_name='본체프레임 제조',
        machines=[body_frame_welder],
        workers=[body_worker_1],
        input_resources=[steel_sheet_res],
        output_resources=[body_frame_res],
        resource_requirements=body_frame_requirements,
        processing_time=3.0,
        resource_manager=resource_manager
    )
    
    body_assembly_process = AssemblyProcess(
        env=env,
        process_id='BODY_ASSEMBLY_PROC',
        process_name='본체 어셈블리',
        machines=[body_assembler],
        workers=[body_worker_2],
        input_resources=[body_panel_res, body_frame_res, insulation_foam_res],
        output_resources=[body_assembly_res],
        resource_requirements=body_assembly_requirements,
        assembly_time=3.5,
        resource_manager=resource_manager
    )
    
    # 12. 부품 제조 프로세스 정의
    compressor_test_process = ManufacturingProcess(
        env=env,
        process_id='COMPRESSOR_TEST_PROC',
        process_name='컴프레서 테스트',
        machines=[compressor_tester],
        workers=[component_worker],
        input_resources=[compressor_unit_res],
        output_resources=[compressor_unit_res],
        resource_requirements=[ResourceRequirement(
            resource_type=ResourceType.SEMI_FINISHED,
            name="컴프레서 유닛",
            required_quantity=1.0,
            unit="개",
            is_mandatory=True
        )],
        processing_time=1.5,
        resource_manager=resource_manager
    )
    
    gasket_molding_process = ManufacturingProcess(
        env=env,
        process_id='GASKET_MOLDING_PROC',
        process_name='가스켓 성형',
        machines=[gasket_molder],
        workers=[component_worker],
        input_resources=[plastic_panel_res],
        output_resources=[door_gasket_res],
        resource_requirements=[ResourceRequirement(
            resource_type=ResourceType.RAW_MATERIAL,
            name="플라스틱 패널",
            required_quantity=1.0,
            unit="장",
            is_mandatory=True
        )],
        processing_time=1.0,
        resource_manager=resource_manager
    )
    
    handle_assembly_process = ManufacturingProcess(
        env=env,
        process_id='HANDLE_ASSEMBLY_PROC',
        process_name='핸들 조립',
        machines=[handle_assembler],
        workers=[component_worker],
        input_resources=[plastic_panel_res, steel_sheet_res],
        output_resources=[door_handle_res],
        resource_requirements=[ResourceRequirement(
            resource_type=ResourceType.RAW_MATERIAL,
            name="플라스틱 패널",
            required_quantity=0.5,
            unit="장",
            is_mandatory=True
        ), ResourceRequirement(
            resource_type=ResourceType.RAW_MATERIAL,
            name="강판",
            required_quantity=0.2,
            unit="장",
            is_mandatory=True
        )],
        processing_time=1.5,
        resource_manager=resource_manager
    )
    
    # 13. 최종 조립 및 검사 프로세스 정의
    refrigerator_assembly_process = AssemblyProcess(
        env=env,
        process_id='REFRIGERATOR_ASSEMBLY_PROC',
        process_name='냉장고 조립',
        machines=[refrigerator_assembler],
        workers=[final_assembler],
        input_resources=[door_assembly_res, body_assembly_res, compressor_unit_res],
        output_resources=[refrigerator_unit_res],
        resource_requirements=refrigerator_assembly_requirements,
        assembly_time=4.0,
        resource_manager=resource_manager
    )
    
    quality_inspection_process = QualityControlProcess(
        env=env,
        process_id='QUALITY_INSPECTION_PROC',
        process_name='품질검사',
        machines=[quality_inspector],
        workers=[final_assembler],
        input_resources=[refrigerator_unit_res],
        output_resources=[final_refrigerator_res],
        resource_requirements=[ResourceRequirement(
            resource_type=ResourceType.SEMI_FINISHED,
            name="냉장고 유닛",
            required_quantity=1.0,
            unit="개",
            is_mandatory=True
        )],
        inspection_time=2.0
    )
    
    packaging_process = ManufacturingProcess(
        env=env,
        process_id='PACKAGING_PROC',
        process_name='포장',
        machines=[packaging_machine],
        workers=[final_assembler],
        input_resources=[final_refrigerator_res],
        output_resources=[final_refrigerator_res],
        resource_requirements=[ResourceRequirement(
            resource_type=ResourceType.FINISHED_PRODUCT,
            name="완성된 냉장고",
            required_quantity=1.0,
            unit="개",
            is_mandatory=True
        )],
        processing_time=1.5,
        resource_manager=resource_manager
    )
    
    # 14. Transport 프로세스들 정의
    transport_processes = []
    
    # 도어 관련 운송
    door_transport_1 = TransportProcess(
        env=env,
        process_id='DOOR_TRANS_1',
        process_name='도어패널 운송',
        machines=[forklift],
        workers=[transport_worker],
        input_resources=[door_panel_res],
        output_resources=[door_panel_res],
        resource_requirements=[ResourceRequirement(
            resource_type=ResourceType.SEMI_FINISHED,
            name="도어 패널",
            required_quantity=1.0,
            unit="개",
            is_mandatory=True
        )],
        loading_time=0.5,
        transport_time=1.5,
        unloading_time=0.5,
        cooldown_time=0.3
    )
    
    door_transport_2 = TransportProcess(
        env=env,
        process_id='DOOR_TRANS_2',
        process_name='도어프레임 운송',
        machines=[conveyor],
        workers=[transport_worker],
        input_resources=[door_frame_res],
        output_resources=[door_frame_res],
        resource_requirements=[ResourceRequirement(
            resource_type=ResourceType.SEMI_FINISHED,
            name="도어 프레임",
            required_quantity=1.0,
            unit="개",
            is_mandatory=True
        )],
        loading_time=0.3,
        transport_time=1.0,
        unloading_time=0.3,
        cooldown_time=0.2
    )
    
    # 본체 관련 운송
    body_transport_1 = TransportProcess(
        env=env,
        process_id='BODY_TRANS_1',
        process_name='본체패널 운송',
        machines=[robot_arm],
        workers=[transport_worker],
        input_resources=[body_panel_res],
        output_resources=[body_panel_res],
        resource_requirements=[ResourceRequirement(
            resource_type=ResourceType.SEMI_FINISHED,
            name="본체 패널",
            required_quantity=1.0,
            unit="개",
            is_mandatory=True
        )],
        loading_time=0.4,
        transport_time=1.2,
        unloading_time=0.4,
        cooldown_time=0.3
    )
    
    body_transport_2 = TransportProcess(
        env=env,
        process_id='BODY_TRANS_2',
        process_name='본체프레임 운송',
        machines=[crane],
        workers=[transport_worker],
        input_resources=[body_frame_res],
        output_resources=[body_frame_res],
        resource_requirements=[ResourceRequirement(
            resource_type=ResourceType.SEMI_FINISHED,
            name="본체 프레임",
            required_quantity=1.0,
            unit="개",
            is_mandatory=True
        )],
        loading_time=0.6,
        transport_time=2.0,
        unloading_time=0.6,
        cooldown_time=0.4
    )
    
    # 최종 조립 운송
    final_transport = TransportProcess(
        env=env,
        process_id='FINAL_TRANS',
        process_name='최종조립 운송',
        machines=[forklift],
        workers=[transport_worker],
        input_resources=[door_assembly_res, body_assembly_res],
        output_resources=[door_assembly_res, body_assembly_res],
        resource_requirements=[ResourceRequirement(
            resource_type=ResourceType.SEMI_FINISHED,
            name="도어 어셈블리",
            required_quantity=1.0,
            unit="개",
            is_mandatory=True
        ), ResourceRequirement(
            resource_type=ResourceType.SEMI_FINISHED,
            name="본체 어셈블리",
            required_quantity=1.0,
            unit="개",
            is_mandatory=True
        )],
        loading_time=1.0,
        transport_time=2.5,
        unloading_time=1.0,
        cooldown_time=0.5
    )
    
    transport_processes = [door_transport_1, door_transport_2, body_transport_1, body_transport_2, final_transport]
    
    # TransportProcess들을 ResourceManager에 등록
    for i, transport_process in enumerate(transport_processes):
        resource_manager.register_transport_process(f"transport_{i+1:03d}", transport_process)
    
    return {
        'env': env,
        'engine': engine,
        'resource_manager': resource_manager,
        'processes': {
            # 도어 제조 라인
            'door_panel': door_panel_process,
            'door_frame': door_frame_process,
            'door_assembly': door_assembly_process,
            
            # 본체 제조 라인
            'body_panel': body_panel_process,
            'body_frame': body_frame_process,
            'body_assembly': body_assembly_process,
            
            # 부품 제조
            'compressor_test': compressor_test_process,
            'gasket_molding': gasket_molding_process,
            'handle_assembly': handle_assembly_process,
            
            # 최종 조립 및 검사
            'refrigerator_assembly': refrigerator_assembly_process,
            'quality_inspection': quality_inspection_process,
            'packaging': packaging_process,
            
            # 운송 프로세스
            'door_transport_1': door_transport_1,
            'door_transport_2': door_transport_2,
            'body_transport_1': body_transport_1,
            'body_transport_2': body_transport_2,
            'final_transport': final_transport
        },
        'resources': {
            'machines': [door_panel_cutter, door_frame_welder, door_assembler,
                        body_panel_cutter, body_frame_welder, body_assembler,
                        compressor_tester, gasket_molder, handle_assembler,
                        refrigerator_assembler, quality_inspector, packaging_machine],
            'workers': [door_worker_1, door_worker_2, body_worker_1, body_worker_2,
                       component_worker, final_assembler, transport_worker],
            'transports': [forklift, conveyor, robot_arm, crane],
            'buffers': [door_buffer, body_buffer, component_buffer, assembly_buffer, final_buffer]
        }
    }


def create_refrigerator_workflow(scenario_data):
    """냉장고 제조 워크플로우 생성 (병렬 공정 포함)"""
    
    processes = scenario_data['processes']
    
    # 1. 병렬 공정 그룹들 생성
    
    # 도어 제조 라인 (병렬)
    door_panel_and_frame = MultiProcessGroup([
        processes['door_panel'],
        processes['door_frame']
    ])
    
    # 본체 제조 라인 (병렬)
    body_panel_and_frame = MultiProcessGroup([
        processes['body_panel'],
        processes['body_frame']
    ])
    
    # 부품 제조 라인 (병렬)
    component_manufacturing = MultiProcessGroup([
        processes['compressor_test'],
        processes['gasket_molding'],
        processes['handle_assembly']
    ])
    
    # 2. 순차 공정들
    door_assembly_chain = (
        door_panel_and_frame >> 
        processes['door_transport_1'] >> 
        processes['door_transport_2'] >> 
        processes['door_assembly']
    )
    
    body_assembly_chain = (
        body_panel_and_frame >> 
        processes['body_transport_1'] >> 
        processes['body_transport_2'] >> 
        processes['body_assembly']
    )
    
    # 3. 최종 조립 체인
    final_assembly_chain = (
        processes['refrigerator_assembly'] >> 
        processes['quality_inspection'] >> 
        processes['packaging']
    )
    
    # 4. 전체 워크플로우 (병렬 + 순차)
    # 병렬 그룹들을 하나의 큰 병렬 그룹으로 결합
    parallel_groups = MultiProcessGroup([
        component_manufacturing,
        door_assembly_chain,
        body_assembly_chain
    ])
    
    # 전체 워크플로우 구성
    complete_workflow = (
        parallel_groups >> 
        processes['final_transport'] >> 
        final_assembly_chain
    )
    
    return complete_workflow


def run_refrigerator_simulation(scenario_data, workflow, num_refrigerators=2):
    """냉장고 제조 시뮬레이션 실행"""
    
    env = scenario_data['env']
    
    def refrigerator_manufacturing_cycle():
        """냉장고 제조 사이클 실행"""
        for i in range(num_refrigerators):
            print(f"\n=== 냉장고 {i+1} 제조 시작 ===")
            
            # 원자재 생성
            raw_materials = {
                'steel_sheet': Product(f'STEEL_{i+1}', f'강판_{i+1}'),
                'plastic_panel': Product(f'PLASTIC_{i+1}', f'플라스틱패널_{i+1}'),
                'insulation_foam': Product(f'INSULATION_{i+1}', f'단열폼_{i+1}'),
                'compressor_unit': Product(f'COMPRESSOR_{i+1}', f'컴프레서_{i+1}'),
                'door_gasket': Product(f'GASKET_{i+1}', f'가스켓_{i+1}'),
                'door_handle': Product(f'HANDLE_{i+1}', f'핸들_{i+1}')
            }
            
            try:
                # 워크플로우 실행
                result = yield from workflow.execute(raw_materials)
                print(f"냉장고 {i+1} 제조 완료: {result}")
            except Exception as e:
                print(f"냉장고 {i+1} 제조 실패: {e}")
            
            # 다음 냉장고 제조 전 대기
            yield env.timeout(3.0)
    
    # 시뮬레이션에 프로세스 등록
    env.process(refrigerator_manufacturing_cycle())
    
    # 시뮬레이션 실행
    print("=== 냉장고 제조공정 시뮬레이션 시작 ===")
    env.run(until=150)
    print("=== 시뮬레이션 완료 ===")


def monitor_refrigerator_system(scenario_data, interval=15.0):
    """냉장고 제조 시스템 상태 모니터링"""
    
    env = scenario_data['env']
    resource_manager = scenario_data['resource_manager']
    processes = scenario_data['processes']
    resources = scenario_data['resources']
    
    def monitor():
        while True:
            print(f"\n=== 시간 {env.now:.1f} - 냉장고 제조 시스템 상태 ===")
            
            # 기계 상태
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
    
    # 1. 냉장고 제조 시나리오 생성
    print("냉장고 제조 시나리오 생성 중...")
    scenario_data = create_refrigerator_manufacturing_scenario()
    
    # 2. 냉장고 제조 워크플로우 생성
    print("냉장고 제조 워크플로우 생성 중...")
    workflow = create_refrigerator_workflow(scenario_data)
    
    # 3. 모니터링 시작
    print("모니터링 시작...")
    monitor_process = monitor_refrigerator_system(scenario_data)
    
    # 4. 시뮬레이션 실행
    print("냉장고 제조 시뮬레이션 실행 중...")
    run_refrigerator_simulation(scenario_data, workflow, num_refrigerators=2)
    
    print("\n=== 냉장고 제조공정 시뮬레이션 완료 ===")


if __name__ == "__main__":
    main() 