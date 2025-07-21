"""
냉장고 도어 제조공정 시뮬레이션 메인 엔트리
- 각 라인별 직렬공정, 운송, 조립공정 연결
- SimPy 및 프레임워크의 표준 클래스 적극 활용
"""
import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), '..'))


import simpy
from src.core.simulation_engine import SimulationEngine
from src.Resource.machine import Machine
from src.Resource.worker import Worker
from src.Resource.product import Product
from src.Resource.transport import Transport
from src.Resource.helper import Resource, ResourceType
from src.processes.manufacturing_process import ManufacturingProcess
from src.processes.assembly_process import AssemblyProcess

# 1. SimPy 환경 및 엔진 생성
env = simpy.Environment()
engine = SimulationEngine(env)


# 2. 제품 정의 (4종) 및 자원 객체 생성
outer_panel = Product('P001', '도어외판')
inner_panel = Product('P002', '도어내판')
insulation = Product('P003', '단열재')
handle = Product('P004', '핸들')

# 각 부품별 Resource 객체 (공정 input/output에 사용)
outer_panel_res = Resource(resource_id='R001', name='도어외판', resource_type=ResourceType.SEMI_FINISHED, quantity=1, unit='개')
inner_panel_res = Resource(resource_id='R002', name='도어내판', resource_type=ResourceType.SEMI_FINISHED, quantity=1, unit='개')
insulation_res = Resource(resource_id='R003', name='단열재', resource_type=ResourceType.SEMI_FINISHED, quantity=1, unit='개')
handle_res = Resource(resource_id='R004', name='핸들', resource_type=ResourceType.SEMI_FINISHED, quantity=1, unit='개')

# 3. 운송수단 정의 (2종)
panel_robot = Transport(env, 'T001', capacity=5, transport_speed=2.0)  # 패널 운송 로봇
parts_conveyor = Transport(env, 'T002', capacity=10, transport_speed=1.5)  # 부품 이송 컨베이어


# 4. 각 라인별 직렬공정 정의 (각 3단계)
# A라인: 외판
press_outer = ManufacturingProcess(env, [Machine(env, 'M001', '프레스')], [], [], [outer_panel_res], [], process_name='외판프레스', processing_time=2.0)
clean_outer = ManufacturingProcess(env, [Machine(env, 'M002', '세척기')], [], [outer_panel_res], [outer_panel_res], [], process_name='외판세척', processing_time=1.5)
paint_outer = ManufacturingProcess(env, [Machine(env, 'M003', '도장기')], [], [outer_panel_res], [outer_panel_res], [], process_name='외판도장', processing_time=2.5)

# B라인: 내판
press_inner = ManufacturingProcess(env, [Machine(env, 'M004', '프레스')], [], [], [inner_panel_res], [], process_name='내판프레스', processing_time=2.0)
clean_inner = ManufacturingProcess(env, [Machine(env, 'M005', '세척기')], [], [inner_panel_res], [inner_panel_res], [], process_name='내판세척', processing_time=1.5)
paint_inner = ManufacturingProcess(env, [Machine(env, 'M006', '도장기')], [], [inner_panel_res], [inner_panel_res], [], process_name='내판도장', processing_time=2.5)

# C라인: 단열재/핸들
form_insulation = ManufacturingProcess(env, [Machine(env, 'M007', '성형기')], [], [], [insulation_res], [], process_name='단열재성형', processing_time=2.2)
inject_handle = ManufacturingProcess(env, [Machine(env, 'M008', '사출기')], [], [], [handle_res], [], process_name='핸드사출', processing_time=1.8)
finish_handle = ManufacturingProcess(env, [Machine(env, 'M009', '마감기')], [], [handle_res], [handle_res], [], process_name='핸들마감', processing_time=1.2)

# 5. 조립공정 정의 (4개 부품 모두 Resource 객체로)
assembly = AssemblyProcess(env, [Machine(env, 'M010', '조립기')], [], [outer_panel_res, inner_panel_res, insulation_res, handle_res], [], [], process_name='도어조립', assembly_time=3.5)

# 6. 공정 체이닝 및 운송 연결 (개념적 예시)

# 실제 연결 예시: 각 라인별 직렬공정 체이닝 및 조립공정 연결
from src.processes.base_process import MultiProcessGroup
a_line_chain = press_outer >> clean_outer >> paint_outer
b_line_chain = press_inner >> clean_inner >> paint_inner
c_line_chain = form_insulation >> inject_handle >> finish_handle

# MultiProcessGroup으로 병렬 라인 결과를 조립공정에 연결
pre_assembly_group = MultiProcessGroup([paint_outer, paint_inner, finish_handle])
complete_process = pre_assembly_group >> assembly

# 7. 시뮬레이션 실행

# 체이닝된 complete_process를 시뮬레이션에 등록
engine.add_process(complete_process.execute_chain)

engine.run(until=50)
print('냉장고 도어 제조공정 시뮬레이션 완료!')
