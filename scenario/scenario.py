"""
냉장고 제조공정 시뮬레이션 시나리오 (Full-featured)

이 시나리오는 제공된 PPT를 기반으로 냉장고 제조공정의 완전한 시뮬레이션을 구현합니다:
1. Unit 1, 2, 3에 따른 공정 단계 정의
2. 다양한 리소스(기계, 작업자, 운송수단, 버퍼) 정의
3. 병렬 공정 (4개의 프레스 라인, 4개의 최종 조립 라인)
4. ResourceManager를 통한 자동화된 운송 시스템
5. src 폴더의 시뮬레이션 프레임워크 전체 기능 활용
"""

import os
import sys
import io
from datetime import datetime

# 프로젝트 루트를 파이썬 모듈 검색 경로에 추가
project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, project_root)

import simpy
from src.core.simulation_engine import SimulationEngine
from src.core.resource_manager import AdvancedResourceManager
from src.Resource.machine import Machine
from src.Resource.worker import Worker
from src.Resource.transport import Transport
from src.Resource.buffer import Buffer
from src.Resource.product import Product
from src.Resource.resource_base import Resource, ResourceType
from src.Processes.manufacturing_process import ManufacturingProcess
from src.Processes.assembly_process import AssemblyProcess
from src.Processes.quality_control_process import QualityControlProcess
from src.Processes.transport_process import TransportProcess
from src.Flow.multi_group_flow import MultiProcessGroup
from src.Flow.process_chain import ProcessChain

def create_refrigerator_scenario():
    """냉장고 제조공정 시나리오의 모든 자원과 프로세스를 생성합니다."""
    
    env = simpy.Environment()
    engine = SimulationEngine(env)
    resource_manager = AdvancedResourceManager(env)
    
    # --- 1. 자원(Resource) 등록 ---
    resource_manager.register_resource("transport", capacity=10, resource_type=ResourceType.TRANSPORT)

    # --- 2. 제품(Product) 및 부품(Resource) 정의 ---
    side_panel_sheet = Resource('R_SIDE_S', 'SidePanelSheet', ResourceType.RAW_MATERIAL)
    back_sheet = Resource('R_BACK_S', 'BackSheet', ResourceType.RAW_MATERIAL)
    top_cover_sheet = Resource('R_TOP_S', 'TopCoverSheet', ResourceType.RAW_MATERIAL)
    top_support_sheet = Resource('R_SUPPORT_S', 'TopPanelSupportSheet', ResourceType.RAW_MATERIAL)
    
    side_panel = Resource('R_SIDE_P', 'SidePanel', ResourceType.SEMI_FINISHED)
    back_panel = Resource('R_BACK_P', 'BackPanel', ResourceType.SEMI_FINISHED)
    top_cover = Resource('R_TOP_P', 'TopCover', ResourceType.SEMI_FINISHED)
    top_support = Resource('R_SUPPORT_P', 'TopPanelSupport', ResourceType.SEMI_FINISHED)

    door_shell = Resource('R_DOOR_SHELL', 'DoorShellAssembly', ResourceType.SEMI_FINISHED)
    
    main_body = Resource('R_MAIN_BODY', 'RefrigeratorMainBody', ResourceType.SEMI_FINISHED)
    hinge = Resource('R_HINGE', 'Hinge', ResourceType.SEMI_FINISHED)
    functional_part = Resource('R_FUNC_PART', 'FunctionalPart', ResourceType.SEMI_FINISHED)

    final_refrigerator = Resource('R_FINAL', 'FinishedRefrigerator', ResourceType.FINISHED_PRODUCT)

    # --- 3. 설비(Machine) 및 작업자(Worker) 정의 ---
    press_machines = [Machine(env, f'PRESS_M{i}', f'프레스기계{i}', capacity=1, processing_time=1) for i in range(1, 5)]
    press_workers = [Worker(env, f'PRESS_W{i}', f'프레스작업자{i}', skills=['blanking', 'drawing', 'piercing']) for i in range(1, 5)]

    assembly_robots = [Machine(env, f'ASSEMBLY_R{i}', f'도어조립로봇{i}', capacity=1, processing_time=25) for i in range(1, 5)]
    filling_machines = [Machine(env, f'FILLING_M{i}', f'발포충진기{i}', capacity=1, processing_time=50) for i in range(1, 5)]
    unit2_workers = [Worker(env, f'UNIT2_W{i}', f'Unit2작업자{i}', skills=['assembly', 'filling']) for i in range(1, 5)]

    final_assembly_robots = [Machine(env, f'FINAL_R{i}', f'최종조립로봇{i}', capacity=1, processing_time=20) for i in range(1, 5)]
    inspection_machines = [Machine(env, f'INSPECT_M{i}', f'품질검사기{i}', capacity=1, processing_time=15) for i in range(1, 5)]
    unit3_workers = [Worker(env, f'UNIT3_W{i}', f'Unit3작업자{i}', skills=['final_assembly', 'inspection']) for i in range(1, 5)]
    
    agv = Transport(env, 'AGV_T', 'AGV', capacity=5, transport_speed=2.0)
    conveyor = Transport(env, 'CONVEYOR_T', '컨베이어', capacity=20, transport_speed=1.0)
    transport_worker = Worker(env, 'TRANSPORT_W', '운송작업자', skills=['transport'])

    # --- 4. 프로세스(Process) 정의 ---
    
    # Unit 1: Pressing Processes (4 parallel lines)
    press_lines = []
    part_info = [
        ("SidePanel", side_panel_sheet, side_panel), ("BackSheet", back_sheet, back_panel),
        ("TopCover", top_cover_sheet, top_cover), ("TopSupport", top_support_sheet, top_support)
    ]
    for i in range(4):
        p_name, p_in, p_out = part_info[i]
        blanking = ManufacturingProcess(env, f'P_BLANK_{i}', f'{p_name}-Blanking', [press_machines[i]], [press_workers[i]], {p_in.name:1}, {p_out.name:1}, [], 10, resource_manager=resource_manager)
        drawing = ManufacturingProcess(env, f'P_DRAW_{i}', f'{p_name}-Drawing', [press_machines[i]], [press_workers[i]], {p_out.name:1}, {p_out.name:1}, [], 15, resource_manager=resource_manager)
        piercing = ManufacturingProcess(env, f'P_PIERCE_{i}', f'{p_name}-Piercing', [press_machines[i]], [press_workers[i]], {p_out.name:1}, {p_out.name:1}, [], 5, resource_manager=resource_manager)
        press_lines.append(blanking >> drawing >> piercing)

    # Unit 2: Door Shell Assembly and Filling
    door_assembly = AssemblyProcess(env, 'P_DOOR_ASSY', '도어쉘조립', assembly_robots, unit2_workers, {side_panel.name:1, back_panel.name:1, top_cover.name:1, top_support.name:1}, {door_shell.name:1}, [], 25, resource_manager=resource_manager)
    foam_filling = ManufacturingProcess(env, 'P_FOAM', '발포충진', filling_machines, unit2_workers, {door_shell.name:1}, {door_shell.name:1}, [], 50, resource_manager=resource_manager)

    # Unit 3: Final Assembly Lines (4 parallel lines)
    final_lines = []
    for i in range(4):
        main_assy = AssemblyProcess(env, f'P_MAIN_ASSY_{i}', f'본체조립{i}', [final_assembly_robots[i]], [unit3_workers[i]], {door_shell.name:1, main_body.name:1}, {final_refrigerator.name:1}, [], 20, resource_manager=None)
        hinge_inst = ManufacturingProcess(env, f'P_HINGE_{i}', f'힌지결합{i}', [final_assembly_robots[i]], [unit3_workers[i]], {final_refrigerator.name:1, hinge.name:1}, {final_refrigerator.name:1}, [], 15, resource_manager=None)
        door_inst = ManufacturingProcess(env, f'P_DOOR_INST_{i}', f'도어결합{i}', [final_assembly_robots[i]], [unit3_workers[i]], {final_refrigerator.name:1}, {final_refrigerator.name:1}, [], 15, resource_manager=None)
        func_inst = ManufacturingProcess(env, f'P_FUNC_{i}', f'기능부품결합{i}', [final_assembly_robots[i]], [unit3_workers[i]], {final_refrigerator.name:1, functional_part.name:1}, {final_refrigerator.name:1}, [], 20, resource_manager=None)
        finishing = ManufacturingProcess(env, f'P_FINISH_{i}', f'최종마감{i}', [final_assembly_robots[i]], [unit3_workers[i]], {final_refrigerator.name:1}, {final_refrigerator.name:1}, [], 10, resource_manager=None)
        inspection = QualityControlProcess(env, f'P_INSPECT_{i}', f'품질검사{i}', [inspection_machines[i]], [unit3_workers[i]], {final_refrigerator.name:1}, {final_refrigerator.name:1}, [], 20)
        
        # 교착 상태(Deadlock) 방지를 위해 연속 공정의 출력 버퍼 블로킹 기능 비활성화
        process_chain_for_blocking_disable = [main_assy, hinge_inst, door_inst, func_inst, finishing, inspection]
        for proc in process_chain_for_blocking_disable:
            proc.enable_output_blocking_feature(False)

        final_lines.append(main_assy >> hinge_inst >> door_inst >> func_inst >> finishing >> inspection)
        
    # Transport Processes
    transport_to_unit2 = TransportProcess(env, 'T_U1_U2', 'Unit1->2운송', [agv], [transport_worker], {}, {}, [], 1, 5, 1, 1)
    transport_to_unit3 = TransportProcess(env, 'T_U2_U3', 'Unit2->3운송', [conveyor], [transport_worker], {}, {}, [], 1, 10, 1, 1)
    
    resource_manager.register_transport_process("transport_u1_u2", transport_to_unit2)
    resource_manager.register_transport_process("transport_u2_u3", transport_to_unit3)
    
    # --- 5. 워크플로우(Workflow) 구성 ---
    unit1_workflow = MultiProcessGroup(press_lines)
    unit2_workflow = door_assembly >> foam_filling
    unit3_workflow = MultiProcessGroup(final_lines)

    complete_workflow = unit1_workflow >> unit2_workflow >> unit3_workflow

    return {
        'env': env,
        'engine': engine,
        'workflow': complete_workflow
    }

def production_starter(env, workflow, num_orders=3):
    """시뮬레이션을 시작하고 정해진 수량만큼 생산 오더를 생성하는 프로세스"""
    for i in range(num_orders):
        print(f"\n--- [시간 {env.now:.2f}] 냉장고 생산 주문 {i+1} 시작 ---")
        initial_product = Product(f'ORDER_{i+1}', '생산주문')
        yield from workflow.execute(initial_product)
        print(f"--- [시간 {env.now:.2f}] 냉장고 생산 주문 {i+1} 완료 ---")
        yield env.timeout(10)

def main():
    """메인 실행 함수"""
    output_capture = io.StringIO()
    original_stdout = sys.stdout
    
    try:
        sys.stdout = output_capture
        
        print("### 냉장고 제조공정 시뮬레이션 초기화 ###")
        scenario_data = create_refrigerator_scenario()
        env = scenario_data['env']
        engine = scenario_data['engine']
        workflow = scenario_data['workflow']

        print("\n### 시뮬레이션 실행 ###")
        engine.add_process(production_starter, workflow, 3)
        engine.run(until=1000)
        
    finally:
        sys.stdout = original_stdout
        captured_output = output_capture.getvalue()
        output_capture.close()
        
        save_output_to_md(captured_output)
        print(captured_output)

def save_output_to_md(output_text):
    """캡처된 출력을 Markdown 파일로 저장하는 함수"""
    log_dir = os.path.join(project_root, 'log')
    if not os.path.exists(log_dir):
        os.makedirs(log_dir)
        
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    filename = os.path.join(log_dir, f"refrigerator_simulation_log_{timestamp}.md")
    
    md_content = f"""# 냉장고 제조공정 시뮬레이션 로그

**시뮬레이션 실행 시간**: {datetime.now().strftime("%Y-%m-%d %H:%M:%S")}

## 시뮬레이션 출력 로그
{output_text}
"""
    try:
        with open(filename, 'w', encoding='utf-8') as f:
            f.write(md_content)
        print(f"\n✅ 시뮬레이션 로그가 '{filename}' 파일로 저장되었습니다.")
    except Exception as e:
        print(f"\n❌ 파일 저장 중 오류 발생: {e}")

if __name__ == "__main__":
    main()
