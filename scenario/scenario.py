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
from datetime import datetime

# 프로젝트 루트를 파이썬 모듈 검색 경로에 추가
project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, project_root)

# 간단한 로깅 프레임워크 가져오기
from src.utils.log_util import LogContext, log_execution, quick_log

import simpy
from src.core.simulation_engine import SimulationEngine
from src.core.resource_manager import AdvancedResourceManager
from src.core.report_manager import ReportManager
from src.core.material_supply_manager import MaterialSupplyManager, SupplyRoute, SupplyStrategy
from src.Resource.machine import Machine
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

    # --- 자재창고 및 팰릿 스택 버퍼 정의 ---
    # Unit1 앞단에 설치할 4개의 팰릿 스택 버퍼 (50개 용량)
    side_panel_pallet_buffer = Buffer(env, 'PALLET_SIDE', 'Side Panel Pallet Stack', 'raw_material', capacity=50)
    back_sheet_pallet_buffer = Buffer(env, 'PALLET_BACK', 'Back Sheet Pallet Stack', 'raw_material', capacity=50)
    top_cover_pallet_buffer = Buffer(env, 'PALLET_TOP', 'Top Cover Pallet Stack', 'raw_material', capacity=50)
    lower_cover_pallet_buffer = Buffer(env, 'PALLET_LOWER', 'Lower Cover Pallet Stack', 'raw_material', capacity=50)
    
    pallet_buffers = [side_panel_pallet_buffer, back_sheet_pallet_buffer, top_cover_pallet_buffer, lower_cover_pallet_buffer]

    # --- 3. 설비(Machine) 정의 (완전 자동화 공정) ---
    press_machines = [Machine(env, f'PRESS_M{i}', f'프레스기계{i}', capacity=1, processing_time=1) for i in range(1, 5)]

    assembly_robots = [Machine(env, f'ASSEMBLY_R{i}', f'도어조립로봇{i}', capacity=1, processing_time=25) for i in range(1, 5)]
    filling_machines = [Machine(env, f'FILLING_M{i}', f'발포충진기{i}', capacity=1, processing_time=50) for i in range(1, 5)]

    final_assembly_robots = [Machine(env, f'FINAL_R{i}', f'최종조립로봇{i}', capacity=1, processing_time=20) for i in range(1, 5)]
    inspection_machines = [Machine(env, f'INSPECT_M{i}', f'품질검사기{i}', capacity=1, processing_time=15) for i in range(1, 5)]
    
    # 자재창고 설비 (자동화)
    warehouse_equipment = [Machine(env, 'WAREHOUSE_M1', '자재창고장비', capacity=1, processing_time=2.0)]
    
    # 자재창고 -> 팰릿버퍼 보충용 AGV (각 버퍼당 1대씩, 총 4대)
    agv_warehouse_side = Transport(env, 'AGV_WH_SIDE', '창고→사이드팰릿-AGV', capacity=5, transport_speed=2.0, transport_type="agv")
    agv_warehouse_back = Transport(env, 'AGV_WH_BACK', '창고→백시트팰릿-AGV', capacity=5, transport_speed=2.0, transport_type="agv")
    agv_warehouse_top = Transport(env, 'AGV_WH_TOP', '창고→탑커버팰릿-AGV', capacity=5, transport_speed=2.0, transport_type="agv")
    agv_warehouse_lower = Transport(env, 'AGV_WH_LOWER', '창고→로워커버팰릿-AGV', capacity=5, transport_speed=2.0, transport_type="agv")
    warehouse_agvs = [agv_warehouse_side, agv_warehouse_back, agv_warehouse_top, agv_warehouse_lower]
    
    # 팰릿버퍼 -> Unit1공정 연결용 컨베이어 (각 버퍼당 1대씩, 총 4대)
    conv_pallet_to_unit1_side = Transport(env, 'CONV_PALLET_SIDE', '사이드팰릿→Unit1-컨베이어', capacity=10, transport_speed=1.5, transport_type="conveyor")
    conv_pallet_to_unit1_back = Transport(env, 'CONV_PALLET_BACK', '백시트팰릿→Unit1-컨베이어', capacity=10, transport_speed=1.5, transport_type="conveyor")
    conv_pallet_to_unit1_top = Transport(env, 'CONV_PALLET_TOP', '탑커버팰릿→Unit1-컨베이어', capacity=10, transport_speed=1.5, transport_type="conveyor")
    conv_pallet_to_unit1_lower = Transport(env, 'CONV_PALLET_LOWER', '로워커버팰릿→Unit1-컨베이어', capacity=10, transport_speed=1.5, transport_type="conveyor")
    pallet_to_unit1_conveyors = [conv_pallet_to_unit1_side, conv_pallet_to_unit1_back, conv_pallet_to_unit1_top, conv_pallet_to_unit1_lower]
    
    # Unit1 -> Buffer1 AGV (각 라인당 1대씩, 총 4대)
    agv_u1_b1_l1 = Transport(env, 'AGV_U1_B1_L1', 'Unit1→Buffer1-라인1-AGV', capacity=3, transport_speed=2.0, transport_type="agv")
    agv_u1_b1_l2 = Transport(env, 'AGV_U1_B1_L2', 'Unit1→Buffer1-라인2-AGV', capacity=3, transport_speed=2.0, transport_type="agv")
    agv_u1_b1_l3 = Transport(env, 'AGV_U1_B1_L3', 'Unit1→Buffer1-라인3-AGV', capacity=3, transport_speed=2.0, transport_type="agv")
    agv_u1_b1_l4 = Transport(env, 'AGV_U1_B1_L4', 'Unit1→Buffer1-라인4-AGV', capacity=3, transport_speed=2.0, transport_type="agv")
    agvs_u1_b1 = [agv_u1_b1_l1, agv_u1_b1_l2, agv_u1_b1_l3, agv_u1_b1_l4]
    
    # Buffer1 -> Assembly AGV (각 라인당 1대씩, 총 4대)
    agv_b1_assy_l1 = Transport(env, 'AGV_B1_ASSY_L1', 'Buffer1→조립-라인1-AGV', capacity=3, transport_speed=2.0, transport_type="agv")
    agv_b1_assy_l2 = Transport(env, 'AGV_B1_ASSY_L2', 'Buffer1→조립-라인2-AGV', capacity=3, transport_speed=2.0, transport_type="agv")
    agv_b1_assy_l3 = Transport(env, 'AGV_B1_ASSY_L3', 'Buffer1→조립-라인3-AGV', capacity=3, transport_speed=2.0, transport_type="agv")
    agv_b1_assy_l4 = Transport(env, 'AGV_B1_ASSY_L4', 'Buffer1→조립-라인4-AGV', capacity=3, transport_speed=2.0, transport_type="agv")
    agvs_b1_assy = [agv_b1_assy_l1, agv_b1_assy_l2, agv_b1_assy_l3, agv_b1_assy_l4]
    
    # Assembly -> Buffer2 AGV (각 라인당 1대씩, 총 4대)
    agv_assy_b2_l1 = Transport(env, 'AGV_ASSY_B2_L1', '조립→Buffer2-라인1-AGV', capacity=3, transport_speed=2.0, transport_type="agv")
    agv_assy_b2_l2 = Transport(env, 'AGV_ASSY_B2_L2', '조립→Buffer2-라인2-AGV', capacity=3, transport_speed=2.0, transport_type="agv")
    agv_assy_b2_l3 = Transport(env, 'AGV_ASSY_B2_L3', '조립→Buffer2-라인3-AGV', capacity=3, transport_speed=2.0, transport_type="agv")
    agv_assy_b2_l4 = Transport(env, 'AGV_ASSY_B2_L4', '조립→Buffer2-라인4-AGV', capacity=3, transport_speed=2.0, transport_type="agv")
    agvs_assy_b2 = [agv_assy_b2_l1, agv_assy_b2_l2, agv_assy_b2_l3, agv_assy_b2_l4]
    
    # Buffer2 -> Filling AGV (각 라인당 1대씩, 총 4대)
    agv_b2_fill_l1 = Transport(env, 'AGV_B2_FILL_L1', 'Buffer2→충진-라인1-AGV', capacity=3, transport_speed=2.0, transport_type="agv")
    agv_b2_fill_l2 = Transport(env, 'AGV_B2_FILL_L2', 'Buffer2→충진-라인2-AGV', capacity=3, transport_speed=2.0, transport_type="agv")
    agv_b2_fill_l3 = Transport(env, 'AGV_B2_FILL_L3', 'Buffer2→충진-라인3-AGV', capacity=3, transport_speed=2.0, transport_type="agv")
    agv_b2_fill_l4 = Transport(env, 'AGV_B2_FILL_L4', 'Buffer2→충진-라인4-AGV', capacity=3, transport_speed=2.0, transport_type="agv")
    agvs_b2_fill = [agv_b2_fill_l1, agv_b2_fill_l2, agv_b2_fill_l3, agv_b2_fill_l4]
    
    # Filling -> Buffer3 AGV (각 라인당 1대씩, 총 4대)
    agv_fill_b3_l1 = Transport(env, 'AGV_FILL_B3_L1', '충진→Buffer3-라인1-AGV', capacity=3, transport_speed=2.0, transport_type="agv")
    agv_fill_b3_l2 = Transport(env, 'AGV_FILL_B3_L2', '충진→Buffer3-라인2-AGV', capacity=3, transport_speed=2.0, transport_type="agv")
    agv_fill_b3_l3 = Transport(env, 'AGV_FILL_B3_L3', '충진→Buffer3-라인3-AGV', capacity=3, transport_speed=2.0, transport_type="agv")
    agv_fill_b3_l4 = Transport(env, 'AGV_FILL_B3_L4', '충진→Buffer3-라인4-AGV', capacity=3, transport_speed=2.0, transport_type="agv")
    agvs_fill_b3 = [agv_fill_b3_l1, agv_fill_b3_l2, agv_fill_b3_l3, agv_fill_b3_l4]
    
    # Buffer3 -> Unit3 AGV (각 라인당 1대씩, 총 4대)
    agv_b3_u3_l1 = Transport(env, 'AGV_B3_U3_L1', 'Buffer3→Unit3-라인1-AGV', capacity=3, transport_speed=2.0, transport_type="agv")
    agv_b3_u3_l2 = Transport(env, 'AGV_B3_U3_L2', 'Buffer3→Unit3-라인2-AGV', capacity=3, transport_speed=2.0, transport_type="agv")
    agv_b3_u3_l3 = Transport(env, 'AGV_B3_U3_L3', 'Buffer3→Unit3-라인3-AGV', capacity=3, transport_speed=2.0, transport_type="agv")
    agv_b3_u3_l4 = Transport(env, 'AGV_B3_U3_L4', 'Buffer3→Unit3-라인4-AGV', capacity=3, transport_speed=2.0, transport_type="agv")
    agvs_b3_u3 = [agv_b3_u3_l1, agv_b3_u3_l2, agv_b3_u3_l3, agv_b3_u3_l4]
    
    # AGV는 무인운반차이므로 별도의 운송작업자가 필요하지 않음
    
    # 공정간 운송수단들 (자동화된 컨베이어 및 AGV, 운송작업자 불필요)
    unit1_conveyors = []
    for i in range(4):
        conv1 = Transport(env, f'CONV_U1_L{i}_1', f'Unit1-라인{i}-컨베이어1', capacity=10, transport_speed=1.5, transport_type="conveyor")
        conv2 = Transport(env, f'CONV_U1_L{i}_2', f'Unit1-라인{i}-컨베이어2', capacity=10, transport_speed=1.5, transport_type="conveyor")
        unit1_conveyors.extend([conv1, conv2])
    
    # Unit3 공정간 컨베이어 (각 라인당 5개씩, 총 20개) - 자동화
    unit3_conveyors = []
    for i in range(4):
        for j in range(5):
            conv = Transport(env, f'CONV_U3_L{i}_{j+1}', f'Unit3-라인{i}-컨베이어{j+1}', capacity=8, transport_speed=1.2, transport_type="conveyor")
            unit3_conveyors.append(conv)
    
    # Buffer 정의 - Unit1->Unit2 버퍼 (각 라인당 하나씩, 총 4개)
    buffer1_line1 = Buffer(env, 'BUFFER1_L1', 'Unit1->Unit2 Buffer Line1', 'intermediate', capacity=25)
    buffer1_line2 = Buffer(env, 'BUFFER1_L2', 'Unit1->Unit2 Buffer Line2', 'intermediate', capacity=25)
    buffer1_line3 = Buffer(env, 'BUFFER1_L3', 'Unit1->Unit2 Buffer Line3', 'intermediate', capacity=25)
    buffer1_line4 = Buffer(env, 'BUFFER1_L4', 'Unit1->Unit2 Buffer Line4', 'intermediate', capacity=25)
    buffers1 = [buffer1_line1, buffer1_line2, buffer1_line3, buffer1_line4]
    
    # Buffer 정의 - Unit2에서의 중간 버퍼 (총 4개)
    buffer2_line1 = Buffer(env, 'BUFFER2_L1', 'Unit2 Buffer Line1', 'intermediate', capacity=25)
    buffer2_line2 = Buffer(env, 'BUFFER2_L2', 'Unit2 Buffer Line2', 'intermediate', capacity=25)
    buffer2_line3 = Buffer(env, 'BUFFER2_L3', 'Unit2 Buffer Line3', 'intermediate', capacity=25)
    buffer2_line4 = Buffer(env, 'BUFFER2_L4', 'Unit2 Buffer Line4', 'intermediate', capacity=25)
    buffers2 = [buffer2_line1, buffer2_line2, buffer2_line3, buffer2_line4]
    
    # Buffer 정의 - Unit2->Unit3 버퍼 (각 라인당 하나씩, 총 4개)
    buffer3_line1 = Buffer(env, 'BUFFER3_L1', 'Unit2->Unit3 Buffer Line1', 'intermediate', capacity=25)
    buffer3_line2 = Buffer(env, 'BUFFER3_L2', 'Unit2->Unit3 Buffer Line2', 'intermediate', capacity=25)
    buffer3_line3 = Buffer(env, 'BUFFER3_L3', 'Unit2->Unit3 Buffer Line3', 'intermediate', capacity=25)
    buffer3_line4 = Buffer(env, 'BUFFER3_L4', 'Unit2->Unit3 Buffer Line4', 'intermediate', capacity=25)
    buffers3 = [buffer3_line1, buffer3_line2, buffer3_line3, buffer3_line4]

    # --- 4. 프로세스(Process) 정의 ---
    
    # === MaterialSupplyManager 기반 자재 보충 시스템 ===
    material_supply_manager = MaterialSupplyManager(env)
    
    # Resource 객체에 자재 보충 설정 추가
    material_supply_manager.configure_material_resource(side_panel_sheet, {
        'default_quantity': 30,
        'min_threshold': 10,
        'warning_threshold': 20,
        'supply_time': 2.0
    })
    material_supply_manager.configure_material_resource(back_sheet, {
        'default_quantity': 30,
        'min_threshold': 10,
        'warning_threshold': 20,
        'supply_time': 2.0
    })
    material_supply_manager.configure_material_resource(top_cover_sheet, {
        'default_quantity': 30,
        'min_threshold': 10,
        'warning_threshold': 20,
        'supply_time': 2.0
    })
    material_supply_manager.configure_material_resource(top_support_sheet, {
        'default_quantity': 30,
        'min_threshold': 10,
        'warning_threshold': 20,
        'supply_time': 2.0
    })
    
    # 자재 등록
    for resource in [side_panel_sheet, back_sheet, top_cover_sheet, top_support_sheet]:
        material_supply_manager.register_material(resource)
    
    # 버퍼 보충 운송 프로세스들 정의
    replenish_transport_side = TransportProcess(env, 'T_REPLENISH_SIDE', '창고→사이드팰릿보충운송', 
                                              [agv_warehouse_side], [], 
                                              {}, {}, [], 1.0, 3.0, 1.0, 0.5)
    replenish_transport_back = TransportProcess(env, 'T_REPLENISH_BACK', '창고→백시트팰릿보충운송', 
                                              [agv_warehouse_back], [], 
                                              {}, {}, [], 1.0, 3.0, 1.0, 0.5)
    replenish_transport_top = TransportProcess(env, 'T_REPLENISH_TOP', '창고→탑커버팰릿보충운송', 
                                             [agv_warehouse_top], [], 
                                             {}, {}, [], 1.0, 3.0, 1.0, 0.5)
    replenish_transport_lower = TransportProcess(env, 'T_REPLENISH_LOWER', '창고→로워커버팰릿보충운송', 
                                               [agv_warehouse_lower], [], 
                                               {}, {}, [], 1.0, 3.0, 1.0, 0.5)
    
    # Unit 1: Pressing Processes (4 parallel lines with conveyor connections)
    press_lines = []
    part_info = [
        ("SidePanel", side_panel_sheet, side_panel), ("BackSheet", back_sheet, back_panel),
        ("TopCover", top_cover_sheet, top_cover), ("TopSupport", top_support_sheet, top_support)
    ]
    buffer_info = [side_panel_pallet_buffer, back_sheet_pallet_buffer, top_cover_pallet_buffer, lower_cover_pallet_buffer]
    
    for i in range(4):
        p_name, p_in, p_out = part_info[i]
        
        # 팰릿버퍼에서 Unit1 공정으로의 운송 프로세스 생성 (자동화된 컨베이어)
        transport_pallet_to_blank = TransportProcess(env, f'T_PALLET_BLANK_{i}', f'{p_name}-팰릿→Blanking운송', 
                                                   [pallet_to_unit1_conveyors[i]], [], 
                                                   {}, {}, [], 0, 1.5, 0, 0)
        
        # 공정들 생성 - blanking은 팰릿버퍼에서 운송으로 자재를 받음 (완전 자동화)
        blanking = ManufacturingProcess(env, f'P_BLANK_{i}', f'{p_name}-Blanking', [press_machines[i]], [], 
                                      {p_in.name:1}, {p_out.name:1}, [], 10, resource_manager=resource_manager)
        drawing = ManufacturingProcess(env, f'P_DRAW_{i}', f'{p_name}-Drawing', [press_machines[i]], [], 
                                     {p_out.name:1}, {p_out.name:1}, [], 15, resource_manager=resource_manager)
        piercing = ManufacturingProcess(env, f'P_PIERCE_{i}', f'{p_name}-Piercing', [press_machines[i]], [], 
                                      {p_out.name:1}, {p_out.name:1}, [], 5, resource_manager=resource_manager)
        
        # Unit1 공정간 운송 프로세스들 생성 (자동화된 컨베이어)
        transport_blank_draw = TransportProcess(env, f'T_U1_L{i}_BD', f'Unit1-라인{i}-Blanking→Drawing운송', 
                                              [unit1_conveyors[i*2]], [], 
                                              {}, {}, [], 0, 2.0, 0, 0)
        transport_draw_pierce = TransportProcess(env, f'T_U1_L{i}_DP', f'Unit1-라인{i}-Drawing→Piercing운송', 
                                               [unit1_conveyors[i*2+1]], [], 
                                               {}, {}, [], 0, 2.0, 0, 0)
        
        # 팰릿버퍼에서 시작하여 컨베이어로 연결된 공정 체인 생성
        press_lines.append(transport_pallet_to_blank >> blanking >> transport_blank_draw >> drawing >> transport_draw_pierce >> piercing)

    # Unit 2: Door Shell Assembly and Filling (4 parallel lines with AGV connections)
    unit2_lines = []
    for i in range(4):
        # Unit1 -> Buffer1 운송 프로세스
        transport_u1_b1 = TransportProcess(env, f'T_U1_B1_L{i}', f'Unit1→Buffer1-라인{i}-운송', 
                                          [agvs_u1_b1[i]], [], 
                                          {}, {}, [], 1.0, 3.0, 1.0, 0.5)
        
        # Buffer1 -> Assembly 운송 프로세스  
        transport_b1_assy = TransportProcess(env, f'T_B1_ASSY_L{i}', f'Buffer1→조립-라인{i}-운송', 
                                           [agvs_b1_assy[i]], [], 
                                           {}, {}, [], 1.0, 3.0, 1.0, 0.5)
        
        # 공정들 생성 (완전 자동화)
        door_assembly = AssemblyProcess(env, f'P_DOOR_ASSY_{i}', f'도어쉘조립{i}', [assembly_robots[i]], [], 
                                      {side_panel.name:1, back_panel.name:1, top_cover.name:1, top_support.name:1}, 
                                      {door_shell.name:1}, [], 25, resource_manager=resource_manager)
        
        # Assembly -> Buffer2 운송 프로세스
        transport_assy_b2 = TransportProcess(env, f'T_ASSY_B2_L{i}', f'조립→Buffer2-라인{i}-운송', 
                                           [agvs_assy_b2[i]], [], 
                                           {}, {}, [], 1.0, 3.0, 1.0, 0.5)
        
        # Buffer2 -> Filling 운송 프로세스
        transport_b2_fill = TransportProcess(env, f'T_B2_FILL_L{i}', f'Buffer2→충진-라인{i}-운송', 
                                           [agvs_b2_fill[i]], [], 
                                           {}, {}, [], 1.0, 3.0, 1.0, 0.5)
        
        foam_filling = ManufacturingProcess(env, f'P_FOAM_{i}', f'발포충진{i}', [filling_machines[i]], [], 
                                          {door_shell.name:1}, {door_shell.name:1}, [], 50, resource_manager=resource_manager)
        
        # Filling -> Buffer3 운송 프로세스
        transport_fill_b3 = TransportProcess(env, f'T_FILL_B3_L{i}', f'충진→Buffer3-라인{i}-운송', 
                                           [agvs_fill_b3[i]], [], 
                                           {}, {}, [], 1.0, 3.0, 1.0, 0.5)
        
        # AGV로 연결된 전체 Unit2 공정 체인 생성
        unit2_lines.append(transport_u1_b1 >> transport_b1_assy >> door_assembly >> transport_assy_b2 >> 
                          transport_b2_fill >> foam_filling >> transport_fill_b3)

    # Unit 3: Final Assembly Lines (4 parallel lines with conveyor connections and AGV input)
    final_lines = []
    for i in range(4):
        # Buffer3 -> Unit3 운송 프로세스
        transport_b3_u3 = TransportProcess(env, f'T_B3_U3_L{i}', f'Buffer3→Unit3-라인{i}-운송', 
                                         [agvs_b3_u3[i]], [], 
                                         {}, {}, [], 1.0, 3.0, 1.0, 0.5)
        
        # 공정들 생성 (완전 자동화)
        main_assy = AssemblyProcess(env, f'P_MAIN_ASSY_{i}', f'본체조립{i}', [final_assembly_robots[i]], [], 
                                  {door_shell.name:1, main_body.name:1}, {final_refrigerator.name:1}, [], 20, resource_manager=None)
        hinge_inst = ManufacturingProcess(env, f'P_HINGE_{i}', f'힌지결합{i}', [final_assembly_robots[i]], [], 
                                        {final_refrigerator.name:1, hinge.name:1}, {final_refrigerator.name:1}, [], 15, resource_manager=None)
        door_inst = ManufacturingProcess(env, f'P_DOOR_INST_{i}', f'도어결합{i}', [final_assembly_robots[i]], [], 
                                       {final_refrigerator.name:1}, {final_refrigerator.name:1}, [], 15, resource_manager=None)
        func_inst = ManufacturingProcess(env, f'P_FUNC_{i}', f'기능부품결합{i}', [final_assembly_robots[i]], [], 
                                       {final_refrigerator.name:1, functional_part.name:1}, {final_refrigerator.name:1}, [], 20, resource_manager=None)
        finishing = ManufacturingProcess(env, f'P_FINISH_{i}', f'최종마감{i}', [final_assembly_robots[i]], [], 
                                       {final_refrigerator.name:1}, {final_refrigerator.name:1}, [], 10, resource_manager=None)
        inspection = QualityControlProcess(env, f'P_INSPECT_{i}', f'품질검사{i}', [inspection_machines[i]], [], 
                                         {final_refrigerator.name:1}, {final_refrigerator.name:1}, [], 20)
        
        # Unit3 공정간 운송 프로세스들 생성 (자동화된 컨베이어)
        transport_main_hinge = TransportProcess(env, f'T_U3_L{i}_MH', f'Unit3-라인{i}-본체조립→힌지결합운송', 
                                              [unit3_conveyors[i*5]], [], 
                                              {}, {}, [], 0, 1.5, 0, 0)
        transport_hinge_door = TransportProcess(env, f'T_U3_L{i}_HD', f'Unit3-라인{i}-힌지결합→도어결합운송', 
                                              [unit3_conveyors[i*5+1]], [], 
                                              {}, {}, [], 0, 1.5, 0, 0)
        transport_door_func = TransportProcess(env, f'T_U3_L{i}_DF', f'Unit3-라인{i}-도어결합→기능부품결합운송', 
                                             [unit3_conveyors[i*5+2]], [], 
                                             {}, {}, [], 0, 1.5, 0, 0)
        transport_func_finish = TransportProcess(env, f'T_U3_L{i}_FF', f'Unit3-라인{i}-기능부품결합→최종마감운송', 
                                               [unit3_conveyors[i*5+3]], [], 
                                               {}, {}, [], 0, 1.5, 0, 0)
        transport_finish_inspect = TransportProcess(env, f'T_U3_L{i}_FI', f'Unit3-라인{i}-최종마감→품질검사운송', 
                                                  [unit3_conveyors[i*5+4]], [], 
                                                  {}, {}, [], 0, 1.5, 0, 0)
        
        # 교착 상태(Deadlock) 방지를 위해 연속 공정의 출력 버퍼 블로킹 기능 비활성화
        process_chain_for_blocking_disable = [main_assy, hinge_inst, door_inst, func_inst, finishing, inspection]
        for proc in process_chain_for_blocking_disable:
            proc.enable_output_blocking_feature(False)

        # AGV + 컨베이어로 연결된 공정 체인 생성
        final_lines.append(transport_b3_u3 >> main_assy >> transport_main_hinge >> hinge_inst >> transport_hinge_door >> 
                          door_inst >> transport_door_func >> func_inst >> transport_func_finish >> 
                          finishing >> transport_finish_inspect >> inspection)
        
    # AGV 운송 프로세스들을 ResourceManager에 등록
    agv_transport_processes = []
    for i in range(4):
        # Unit1->Buffer1 AGV 운송 프로세스들
        transport_u1_b1 = TransportProcess(env, f'T_U1_B1_L{i}_RM', f'Unit1→Buffer1-라인{i}-RM운송', 
                                          [agvs_u1_b1[i]], [], {}, {}, [], 1.0, 3.0, 1.0, 0.5)
        agv_transport_processes.append(transport_u1_b1)
        resource_manager.register_transport_process(f"transport_u1_b1_l{i}", transport_u1_b1)
        
        # Buffer1->Assembly AGV 운송 프로세스들
        transport_b1_assy = TransportProcess(env, f'T_B1_ASSY_L{i}_RM', f'Buffer1→조립-라인{i}-RM운송', 
                                           [agvs_b1_assy[i]], [], {}, {}, [], 1.0, 3.0, 1.0, 0.5)
        agv_transport_processes.append(transport_b1_assy)
        resource_manager.register_transport_process(f"transport_b1_assy_l{i}", transport_b1_assy)
        
        # Assembly->Buffer2 AGV 운송 프로세스들
        transport_assy_b2 = TransportProcess(env, f'T_ASSY_B2_L{i}_RM', f'조립→Buffer2-라인{i}-RM운송', 
                                           [agvs_assy_b2[i]], [], {}, {}, [], 1.0, 3.0, 1.0, 0.5)
        agv_transport_processes.append(transport_assy_b2)
        resource_manager.register_transport_process(f"transport_assy_b2_l{i}", transport_assy_b2)
        
        # Buffer2->Filling AGV 운송 프로세스들
        transport_b2_fill = TransportProcess(env, f'T_B2_FILL_L{i}_RM', f'Buffer2→충진-라인{i}-RM운송', 
                                           [agvs_b2_fill[i]], [], {}, {}, [], 1.0, 3.0, 1.0, 0.5)
        agv_transport_processes.append(transport_b2_fill)
        resource_manager.register_transport_process(f"transport_b2_fill_l{i}", transport_b2_fill)
        
        # Filling->Buffer3 AGV 운송 프로세스들
        transport_fill_b3 = TransportProcess(env, f'T_FILL_B3_L{i}_RM', f'충진→Buffer3-라인{i}-RM운송', 
                                           [agvs_fill_b3[i]], [], {}, {}, [], 1.0, 3.0, 1.0, 0.5)
        agv_transport_processes.append(transport_fill_b3)
        resource_manager.register_transport_process(f"transport_fill_b3_l{i}", transport_fill_b3)
        
        # Buffer3->Unit3 AGV 운송 프로세스들
        transport_b3_u3 = TransportProcess(env, f'T_B3_U3_L{i}_RM', f'Buffer3→Unit3-라인{i}-RM운송', 
                                         [agvs_b3_u3[i]], [], {}, {}, [], 1.0, 3.0, 1.0, 0.5)
        agv_transport_processes.append(transport_b3_u3)
        resource_manager.register_transport_process(f"transport_b3_u3_l{i}", transport_b3_u3)
    
    
    # Unit내 공정간 운송 프로세스들도 등록 (필요시)
    print(f"운송 시스템 구성 완료:")
    print(f"   - Unit1 컨베이어: {len(unit1_conveyors)}대 (자동화)")
    print(f"   - Unit1→Buffer1 AGV: {len(agvs_u1_b1)}대") 
    print(f"   - Buffer1→조립 AGV: {len(agvs_b1_assy)}대")
    print(f"   - 조립→Buffer2 AGV: {len(agvs_assy_b2)}대")
    print(f"   - Buffer2→충진 AGV: {len(agvs_b2_fill)}대")
    print(f"   - 충진→Buffer3 AGV: {len(agvs_fill_b3)}대")
    print(f"   - Buffer3→Unit3 AGV: {len(agvs_b3_u3)}대")
    print(f"   - Unit3 컨베이어: {len(unit3_conveyors)}대 (자동화)")
    print(f"   - 총 AGV 수: {len(agv_transport_processes)}대")
    print(f"   - 자재창고→팰릿버퍼 보충 AGV: {len(warehouse_agvs)}대")
    print(f"   - 팰릿버퍼→Unit1 컨베이어: {len(pallet_to_unit1_conveyors)}대 (자동화)")
    print(f"   - 완전 자동화 공정: 모든 제조 및 운송 작업이 기계에 의해 수행됨")
    
    # === MaterialSupplyManager 기반 자재 보충 시스템 설정 ===
    
    # 공급 경로 등록 (Resource 객체 직접 사용)
    supply_routes = [
        SupplyRoute('route_side', side_panel_pallet_buffer, replenish_transport_side, side_panel_sheet),
        SupplyRoute('route_back', back_sheet_pallet_buffer, replenish_transport_back, back_sheet),
        SupplyRoute('route_top', top_cover_pallet_buffer, replenish_transport_top, top_cover_sheet),
        SupplyRoute('route_lower', lower_cover_pallet_buffer, replenish_transport_lower, top_support_sheet)
    ]
    
    for route in supply_routes:
        material_supply_manager.register_supply_route(route.source_id, route)
    
    # 자동 모니터링 시작 (임계값 기반)
    material_supply_manager.start_supply_monitoring(SupplyStrategy.THRESHOLD_BASED)
    
    # 초기 재고 설정 (프레임워크 활용)
    material_supply_manager.setup_initial_inventory()
    
    # --- 5. 워크플로우(Workflow) 구성 ---
    unit1_workflow = MultiProcessGroup(press_lines)
    unit2_workflow = MultiProcessGroup(unit2_lines)
    unit3_workflow = MultiProcessGroup(final_lines)

    # Unit1, Unit2, Unit3을 동시에 작동하도록 병렬 워크플로우 구성
    complete_workflow = MultiProcessGroup([unit1_workflow, unit2_workflow, unit3_workflow])
    
    # --- 6. 자동 생산 시작 설정 ---
    # 단순히 워크플로우를 프로세스에 등록 (제품 1개로 시작)
    initial_product = Product('AUTO_ORDER_1', '자동생산주문')
    env.process(complete_workflow.execute(initial_product))

    return {
        'env': env,
        'engine': engine,
        'workflow': complete_workflow,
        'pallet_buffers': pallet_buffers,
        'material_supply_manager': material_supply_manager,
        'report_manager': material_supply_manager.report_manager,
        'supply_statistics': material_supply_manager.get_supply_statistics()
    }

@log_execution("냉장고_제조공정_시뮬레이션")
def main():
    """메인 실행 함수 - 간단한 로깅 적용"""
    print("### 냉장고 제조공정 시뮬레이션 초기화 ###")
    scenario_data = create_refrigerator_scenario()
    env = scenario_data['env']
    engine = scenario_data['engine']
    workflow = scenario_data['workflow']
    pallet_buffers = scenario_data['pallet_buffers']

    print("\n### 시뮬레이션 자동 실행 ###")
    print("시뮬레이션이 자동으로 시작됩니다...")
    
    # 자동 생산이 설정되어 있으므로 바로 시뮬레이션 실행
    engine.run(until=1000)
    
    print("\n### 시뮬레이션 완료 ###")
    print("모든 로그가 자동으로 MD 파일로 저장되었습니다.")

if __name__ == "__main__":
    main()
