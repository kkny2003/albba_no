"""
공정 체이닝(>>) 오퍼레이터 기반 슈퍼 복잡성 시나리오 예제
- 직렬/병렬/조건부/재작업/운송/버퍼/경합/동적 이벤트 등 포함
- ProcessChain, MultiProcessGroup, >> 연산자 활용
"""
# -*- coding: utf-8 -*-
import sys, os
import io


sys.path.append(os.path.join(os.path.dirname(__file__), '..'))

import simpy
# SimulationEngine 대신 직접 SimPy 사용
# from src.core.simulation_engine import SimulationEngine
from src.Resource.machine import Machine
from src.Resource.worker import Worker
from src.Resource.product import Product
from src.Resource.transport import Transport
from src.Resource.resource_base import Resource, ResourceType
from src.Processes.manufacturing_process import ManufacturingProcess
from src.Processes.assembly_process import AssemblyProcess
from src.Processes.quality_control_process import QualityControlProcess
from src.Processes.transport_process import TransportProcess
from src.Flow.multi_process_group import MultiProcessGroup

env = simpy.Environment()
# engine = SimulationEngine(env)  # 이 부분을 주석 처리

# 로그 저장 리스트 및 기록 함수 추가
simulation_logs = []
def log(msg):
    print(msg)
    simulation_logs.append(msg)

# 제품/부품 정의 (다품종)
products = [Product(resource_id=f'Product{i:03d}', name=f'제품{i}') for i in range(1, 11)]
resources = [Resource(resource_id=f'Part{i:03d}', name=f'부품{i}', resource_type=ResourceType.SEMI_FINISHED) for i in range(1, 11)]

# 기계/작업자/운송/버퍼 (휴식, 고장, 경합, 다양한 속도)
machines = [Machine(env, resource_id=f'M{i:03d}', name=f'기계{i}') for i in range(1, 8)]
workers = [
    Worker(env, resource_id=f'W{i:03d}', name=f'작업자{i}', skills=[f'공정{i}', f'공정{i+1}'], work_speed=1.0 + 0.1*i, error_probability=0.1*i, mean_time_to_rest=5+i, mean_rest_time=1+i%2)
    for i in range(1, 6)
]
transports = [Transport(env, resource_id=f'T{i:03d}', name=f'운송{i}', capacity=2+i, transport_speed=1.0+0.3*i) for i in range(1, 4)]

from src.Resource.buffer import Buffer
buffers = [Buffer(env, resource_id=f'B{i:03d}', name=f'버퍼{i}', capacity=5+i, buffer_type=ResourceType.SEMI_FINISHED) for i in range(1, 4)]

# 공정 정의
proc_a1 = ManufacturingProcess(env, 'PROC001', 'A1', [machines[0]], [workers[0]], [], [resources[0]], [], processing_time=2.0)
proc_a2 = ManufacturingProcess(env, 'PROC002', 'A2', [machines[1]], [workers[1]], [resources[0]], [resources[1]], [], processing_time=1.5)
proc_b1 = ManufacturingProcess(env, 'PROC003', 'B1', [machines[2]], [workers[2]], [], [resources[2]], [], processing_time=2.2)
proc_b2 = ManufacturingProcess(env, 'PROC004', 'B2', [machines[3]], [workers[3]], [resources[2]], [resources[3]], [], processing_time=1.8)
qc = QualityControlProcess(
    env,
    'PROC005',
    '품질검사',
    machines=[machines[4]],
    workers=[],  # 빈 workers 리스트 추가
    input_resources=[resources[1], resources[3]],
    output_resources=[resources[1], resources[3]],  # output_resources 추가
    resource_requirements=[],  # resource_requirements 추가
    inspection_time=1.0,
    failure_weight_worker=2.0
)
assembly = AssemblyProcess(env, 'PROC006', '최종조립', [machines[5]], workers, [resources[1], resources[3], resources[4], resources[5]], [], [], assembly_time=3.0)

# 운송 공정 생성 (모듈화된 클래스 사용)
transport_a1_to_a2 = TransportProcess(
    env, 
    'T001',
    'A1_to_A2_운송',
    machines=[transports[0]],  # transports를 machines로 변경
    workers=[],  # 빈 workers 리스트 추가
    input_resources=[resources[0]], 
    output_resources=[resources[0]],  # output_resources 추가
    resource_requirements=[],  # resource_requirements 추가
    loading_time=0.2,
    unloading_time=0.3,
    transport_time=0.5,
    cooldown_time=2.0
)

def buffer_compete_proc(env, buffer, resource):
    # Buffer 클래스의 put 메서드 활용 예시
    for _ in range(3):
        yield env.timeout(0.5)
        log(f"[시간 {env.now:.1f}] 버퍼에 {resource.name} 투입 시도")
        yield from buffer.put(resource)

# 동적 이벤트(신규 자원 투입)는 utils로 분리하여 재사용 가능하게 처리

# 동적 이벤트 유틸리티 함수 import
from src.utils.dynamic_event import inject_dynamic_resource_event

def dynamic_event(env):
    yield from inject_dynamic_resource_event(env, resources)

# 공정 체이닝(>>) 및 병렬(MultiProcessGroup) 활용
# A라인: A1 >> A2 >> 품질검사 >> 조립
aline_chain = proc_a1 >> proc_a2 >> qc >> assembly
# B라인: B1 >> B2
bline_chain = proc_b1 >> proc_b2
# 병렬 그룹: A라인과 B라인 동시 실행
main_group = MultiProcessGroup([aline_chain, bline_chain])

# SimPy 프로세스 함수로 래핑
def main_chain(env):
    try:
        log(f"[Time {env.now:.1f}] Starting main process chain")
        # MultiProcessGroup을 단일 공정처럼 execute (SimPy generator)
        result = yield from main_group.execute()
        log(f"[Time {env.now:.1f}] Main chain completed: {result}")
    except Exception as e:
        log(f"[Time {env.now:.1f}] Error in main_chain: {e}")
        import traceback
        traceback.print_exc()

# 직접 SimPy에 프로세스 등록
env.process(main_chain(env))
env.process(transport_a1_to_a2.execute())
env.process(buffer_compete_proc(env, buffers[0], resources[0]))
env.process(dynamic_event(env))


log("Running simulation...")
env.run(until=50)
log('Process chaining simulation completed!')

# 시뮬레이션 결과 md 파일로 export
md_path = os.path.join(os.path.dirname(__file__), "simulation_result.md")
with io.open(md_path, "w", encoding="utf-8") as f:
    f.write("# 시뮬레이션 결과 로그\n\n")
    for line in simulation_logs:
        f.write(f"- {line}\n")
log(f"[Export] 시뮬레이션 결과가 {md_path}에 저장되었습니다.")
