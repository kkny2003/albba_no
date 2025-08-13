"""
transport_type 속성을 사용한 컨베이어 확인 테스트
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

def test_transport_type_detection():
    """transport_type 속성을 사용한 컨베이어 감지 테스트"""
    print("=== transport_type 속성 기반 컨베이어 감지 테스트 ===")
    
    env = simpy.Environment()
    transport_worker = Worker(env, 'TRANSPORT_W', '운송작업자', skills=['transport'])
    
    # 1. 다양한 타입의 운송 수단 생성 및 테스트
    transport_types = [
        ("general", "일반 운송수단"),
        ("agv", "AGV"),
        ("truck", "트럭"),
        ("conveyor", "컨베이어")
    ]
    
    for transport_type, description in transport_types:
        print(f"\n--- {description} ({transport_type}) 테스트 ---")
        
        # Transport 객체 생성
        transport = Transport(
            env, f'{transport_type.upper()}_T', description, 
            capacity=20, transport_speed=1.0, transport_type=transport_type
        )
        
        # TransportProcess 생성
        transport_process = TransportProcess(
            env, f'T_{transport_type.upper()}', f'{description}운송', 
            [transport], [transport_worker], 
            {}, {}, [], 
            loading_time=2.0,
            transport_time=10.0, 
            unloading_time=1.5, 
            cooldown_time=0.5
        )
        
        # 결과 확인
        print(f"   - Transport의 transport_type: {transport.transport_type}")
        print(f"   - 컨베이어인지 확인: {transport_process.is_using_conveyor()}")
        print(f"   - 적재시간: {transport_process.loading_time}")
        print(f"   - 운송시간: {transport_process.transport_time}")
        print(f"   - 하역시간: {transport_process.unloading_time}")
        print(f"   - 총 사이클 시간: {transport_process.processing_time}")
        
        # Transport 상태 확인
        status = transport_process.get_transport_status()
        print(f"   - 운송 모드: {status['transport_mode']}")
    
    print("\n=== 테스트 완료 ===")

if __name__ == "__main__":
    test_transport_type_detection()
