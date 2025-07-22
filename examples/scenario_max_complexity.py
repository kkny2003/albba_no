
"""
슈퍼 복잡성 시나리오: 모든 기능(직렬/병렬/조건부/재작업/운송/버퍼/경합/휴식/고장/동적 이벤트/통계 등) 총동원
"""
import sys, os
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
from src.processes.quality_control_process import QualityControlProcess
from src.processes.base_process import MultiProcessGroup

env = simpy.Environment()
engine = SimulationEngine(env)

# 제품/부품 정의 (다품종)
products = [Product(f'P{i:03d}', f'제품{i}') for i in range(1, 11)]
resources = [Resource(resource_id=f'R{i:03d}', name=f'부품{i}', resource_type=ResourceType.SEMI_FINISHED, quantity=3, unit='개') for i in range(1, 11)]

# 기계/작업자/운송/버퍼 (휴식, 고장, 경합, 다양한 속도)
machines = [Machine(env, f'M{i:03d}', f'기계{i}') for i in range(1, 8)]
workers = [
    Worker(env, f'W{i:03d}', skills=[f'공정{i}', f'공정{i+1}'], work_speed=1.0 + 0.1*i, error_probability=0.1*i, mean_time_to_rest=5+i, mean_rest_time=1+i%2)
    for i in range(1, 6)
]
transports = [Transport(env, f'T{i:03d}', capacity=2+i, transport_speed=1.0+0.3*i) for i in range(1, 4)]

# 버퍼(컨테이너) 예시 (자원 경합)
from src.Resource.buffer import Buffer
buffers = [Buffer(env, f'B{i:03d}', capacity=5+i, buffer_type=ResourceType.SEMI_FINISHED) for i in range(1, 4)]

# 공정 정의 (직렬/병렬/조건부/재작업/운송/버퍼/경합)
proc_a1 = ManufacturingProcess(env, [machines[0]], [workers[0]], [], [resources[0]], [], process_name='A1', processing_time=2.0)
proc_a2 = ManufacturingProcess(env, [machines[1]], [workers[1]], [resources[0]], [resources[1]], [], process_name='A2', processing_time=1.5)
proc_b1 = ManufacturingProcess(env, [machines[2]], [workers[2]], [], [resources[2]], [], process_name='B1', processing_time=2.2)
proc_b2 = ManufacturingProcess(env, [machines[3]], [workers[3]], [resources[2]], [resources[3]], [], process_name='B2', processing_time=1.8)

# 운송 공정 (자원 운반)
def transport_proc(env, transport, src, dst, resource):
    while True:
        yield env.timeout(1.0)
        print(f"[시간 {env.now:.1f}] {transport.transport_id}가 {src}에서 {dst}로 {resource.name} 운반 시도")
        # 실제 운송 로직은 Transport/Buffer 클래스에 맞게 구현 필요

# 버퍼 경합 공정
def buffer_compete_proc(env, buffer, resource):
    for _ in range(3):
        yield env.timeout(0.5)
        print(f"[시간 {env.now:.1f}] {buffer.buffer_id}에 {resource.name} 투입 시도")

# 품질검사(불량시 재작업)
qc = QualityControlProcess(
    env,
    inspection_criteria={'불량허용': 0.2},
    input_resources=[resources[1], resources[3]],
    output_resources=[],
    resource_requirements=[],
    machines=[machines[4]],
    process_name='품질검사',
    inspection_time=1.0,
    failure_weight_worker=2.0
)

# 조립공정 (여러 자원 동시 투입)
assembly = AssemblyProcess(env, [machines[5]], workers, [resources[1], resources[3], resources[4], resources[5]], [], [], process_name='최종조립', assembly_time=3.0)

# 동적 이벤트: 시뮬레이션 중간에 자원 추가/제거
def dynamic_event(env):
    yield env.timeout(10)
    print(f"[시간 {env.now:.1f}] [동적이벤트] 신규 자원 투입!")
    resources.append(Resource(resource_id='R999', name='긴급부품', resource_type=ResourceType.SEMI_FINISHED, quantity=1, unit='개'))


# 공정 체이닝: A1 → A2 → 품질검사 → 조립, B1 → B2 (병렬), 운송/버퍼/동적 이벤트는 병렬로 동작
def main_chain(env):
    # A라인 직렬 체인
    a1_result = yield from proc_a1.execute()
    a2_result = yield from proc_a2.execute(a1_result)
    qc_result = yield from qc.execute(a2_result)
    assembly_result = yield from assembly.execute(qc_result)
    # B라인 직렬 체인
    b1_result = yield from proc_b1.execute()
    b2_result = yield from proc_b2.execute(b1_result)
    # (여기서 병렬/조건부/재작업/통합 등 추가 가능)
    print(f"[main_chain] 전체 공정 완료: {assembly_result}")

engine.add_process(main_chain)
engine.add_process(lambda env: transport_proc(env, transports[0], 'A1', 'A2', resources[0]))
engine.add_process(lambda env: buffer_compete_proc(env, buffers[0], resources[0]))
engine.add_process(lambda env: dynamic_event(env))

engine.run(until=50)
print('슈퍼 복잡성 시나리오 시뮬레이션 완료!')
