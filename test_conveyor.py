"""
컨베이어 최적화 테스트
"""

import os
import sys

# 프로젝트 루트를 파이썬 모듈 검색 경로에 추가
project_root = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, project_root)

import simpy
from src.Resource.transport import Transport
from src.Resource.worker import Worker
from src.Processes.transport_process import TransportProcess

def test_conveyor_optimization():
    """컨베이어 최적화 테스트"""
    print("=== 컨베이어 최적화 테스트 시작 ===")
    
    env = simpy.Environment()
    
    # 1. 일반 AGV 생성 및 TransportProcess 테스트
    print("\n1. 일반 AGV TransportProcess 테스트:")
    agv = Transport(env, 'AGV_T', 'AGV', capacity=5, transport_speed=2.0, transport_type="agv")
    transport_worker = Worker(env, 'TRANSPORT_W', '운송작업자', skills=['transport'])
    
    agv_transport = TransportProcess(
        env, 'T_AGV', 'AGV운송', 
        [agv], [transport_worker], 
        {}, {}, [], 
        loading_time=2.0,
        transport_time=5.0, 
        unloading_time=1.5, 
        cooldown_time=0.5
    )
    
    print(f"AGV TransportProcess - 적재: {agv_transport.loading_time}, 운송: {agv_transport.transport_time}, 하역: {agv_transport.unloading_time}")
    print(f"AGV TransportProcess - 총 사이클 시간: {agv_transport.processing_time}")
    print(f"AGV TransportProcess - 컨베이어 사용: {agv_transport.is_using_conveyor()}")
    
    # 2. 컨베이어 생성 및 TransportProcess 테스트
    print("\n2. 컨베이어 TransportProcess 테스트:")
    conveyor = Transport(env, 'CONVEYOR_T', '컨베이어', capacity=20, transport_speed=1.0, transport_type="conveyor")
    
    conveyor_transport = TransportProcess(
        env, 'T_CONVEYOR', '컨베이어운송', 
        [conveyor], [transport_worker], 
        {}, {}, [], 
        loading_time=2.0,
        transport_time=10.0, 
        unloading_time=1.5, 
        cooldown_time=0.5
    )
    
    print(f"컨베이어 TransportProcess - 적재: {conveyor_transport.loading_time}, 운송: {conveyor_transport.transport_time}, 하역: {conveyor_transport.unloading_time}")
    print(f"컨베이어 TransportProcess - 총 사이클 시간: {conveyor_transport.processing_time}")
    print(f"컨베이어 TransportProcess - 컨베이어 사용: {conveyor_transport.is_using_conveyor()}")
    
    # 3. Transport 상태 조회
    print(f"\n3. AGV Transport 상태:")
    agv_status = agv_transport.get_transport_status()
    print(f"   - 운송 모드: {agv_status['transport_mode']}")
    print(f"   - 컨베이어 여부: {agv_status.get('is_conveyor', False)}")
    
    print(f"\n컨베이어 Transport 상태:")
    conveyor_status = conveyor_transport.get_transport_status()
    print(f"   - 운송 모드: {conveyor_status['transport_mode']}")
    print(f"   - 컨베이어 여부: {conveyor_status.get('is_conveyor', False)}")
    
    print("\n=== 테스트 완료 ===")

if __name__ == "__main__":
    test_conveyor_optimization()
