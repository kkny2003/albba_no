"""
제조공정 Transport 자동 요청 기능 예제

이 예제는 제조공정이 완료되면 자동으로 resource_manager에 transport 요청을 보내고,
transport가 할당되면 출하품을 운송하는 시나리오를 보여줍니다.
"""

import os
import sys

# 프로젝트 루트를 파이썬 모듈 검색 경로에 추가
project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, project_root)

import simpy
from src.core.resource_manager import AdvancedResourceManager
from src.Processes.manufacturing_process import ManufacturingProcess
from src.Resource.machine import Machine
from src.Resource.worker import Worker
from src.Resource.resource_base import Resource, ResourceRequirement, ResourceType


def create_manufacturing_scenario():
    """제조공정 Transport 자동 요청 시나리오 생성"""
    
    # 1. SimPy 환경 생성
    env = simpy.Environment()
    
    # 2. AdvancedResourceManager 생성 및 Transport 등록
    resource_manager = AdvancedResourceManager(env)
    
    # Transport 자원 등록 (용량 3개의 운송수단)
    resource_manager.register_resource(
        resource_id="transport",
        capacity=3,
        resource_type=ResourceType.TRANSPORT,
        description="제조공정 출하품 운송용",
        properties={"speed": 1.0, "type": "forklift"}
    )
    
    print(f"[시간 {env.now:.1f}] Transport 자원 등록 완료 (용량: 3)")
    
    # 3. 제조 장비 및 인력 생성
    machine = Machine(
        env=env,
        machine_id="machine_001", 
        name="제조기계1",
        capacity=1,
        processing_time=2.0
    )
    
    worker = Worker(
        env=env,
        worker_id="worker_001",
        name="작업자1", 
        skills=["제조", "조립"],
        efficiency=1.0
    )
    
    # 4. 자원 요구사항 정의
    requirements = [
        ResourceRequirement(
            resource_type=ResourceType.RAW_MATERIAL,
            name="원자재",
            required_quantity=1.0,
            unit="kg",
            is_mandatory=True
        )
    ]
    
    # 5. 입력/출력 자원 정의
    input_resources = {"원자재": 1.5, "전력": 0.5}
    output_resources = {"완제품": 1.0}
    
    # 6. ManufacturingProcess 생성 (자동 transport 활성화)
    manufacturing_process = ManufacturingProcess(
        env=env,
        process_id="mfg_transport_001",
        process_name="자동운송_제조공정1",
        machines=[machine],
        workers=[worker],
        input_resources=input_resources,
        output_resources=output_resources,
        resource_requirements=requirements,
        processing_time=2.0,
        products_per_cycle=1,
        resource_manager=resource_manager,  # 자동 transport 요청용
        transport_distance=15.0             # 운송 거리 15.0 단위
    )
    
    print(f"[시간 {env.now:.1f}] 제조공정 생성 완료 - 자동 Transport 활성화")
    
    return env, resource_manager, manufacturing_process


def run_manufacturing_cycles(env, manufacturing_process, cycles: int = 3):
    """제조공정을 여러 사이클 실행하는 함수"""
    
    def manufacturing_cycle():
        """단일 제조 사이클 실행"""
        print(f"\n[시간 {env.now:.1f}] === 제조 사이클 시작 ===")
        
        try:
            # 제조공정 실행 (완료 후 자동으로 transport 요청)
            yield from manufacturing_process.process_logic(
                input_data={"제품유형": "표준제품", "배치번호": f"BATCH_{env.now}"}
            )
            
            print(f"[시간 {env.now:.1f}] === 제조 사이클 완료 ===\n")
            
        except Exception as e:
            print(f"[시간 {env.now:.1f}] 제조 사이클 중 오류: {e}")
    
    # 여러 제조 사이클을 순차적으로 실행
    for cycle in range(cycles):
        print(f"\n{'='*50}")
        print(f"제조 사이클 {cycle + 1}/{cycles} 시작")
        print(f"{'='*50}")
        
        yield from manufacturing_cycle()
        
        # 사이클 간 간격 (다음 원자재 도착 대기)
        if cycle < cycles - 1:
            yield env.timeout(5.0)


def monitor_resource_status(env, resource_manager, interval: float = 10.0):
    """자원 상태를 주기적으로 모니터링하는 함수"""
    
    while True:
        yield env.timeout(interval)
        
        print(f"\n[시간 {env.now:.1f}] === 자원 상태 모니터링 ===")
        
        # Transport 자원 상태 확인
        transport_status = resource_manager.get_resource_status("transport")
        if transport_status and 'error' not in transport_status:
            print(f"Transport 상태: 사용중 {transport_status['in_use']}/{transport_status['capacity']}, "
                  f"대기열 {transport_status['queue_length']}개")
        
        # 전체 자원 활용률 확인
        utilization = resource_manager.calculate_utilization()
        if 'error' not in utilization:
            print(f"평균 자원 활용률: {utilization['average_percentage']:.1f}%")
        
        print(f"{'='*40}\n")


def main():
    """메인 실행 함수"""
    print("=" * 60)
    print("제조공정 Transport 자동 요청 시뮬레이션 시작")
    print("=" * 60)
    
    # 1. 시나리오 설정
    env, resource_manager, manufacturing_process = create_manufacturing_scenario()
    
    # 2. 자원 모니터링 프로세스 시작
    env.process(monitor_resource_status(env, resource_manager, interval=20.0))
    
    # 3. 제조공정 실행 프로세스 시작
    env.process(run_manufacturing_cycles(env, manufacturing_process, cycles=3))
    
    # 4. 시뮬레이션 실행
    print(f"\n[시간 {env.now:.1f}] 시뮬레이션 시작\n")
    env.run(until=100)
    
    # 5. 최종 결과 출력
    print("\n" + "=" * 60)
    print("시뮬레이션 완료 - 최종 결과")
    print("=" * 60)
    
    # Transport 상태 조회
    transport_status = manufacturing_process.get_transport_status()
    print(f"자동 Transport 활성화: {transport_status['auto_transport_enabled']}")
    print(f"Transport 거리: {transport_status['transport_distance']}")
    
    # 자원 관리자 통계
    stats = resource_manager.get_statistics()
    print(f"총 자원 요청: {stats['total_requests']}")
    print(f"성공한 할당: {stats['successful_allocations']}")
    print(f"성공률: {stats['success_rate']:.1f}%")
    
    # Transport 자원 상세 상태
    all_status = resource_manager.get_all_resource_status()
    if "transport" in all_status:
        transport_info = all_status["transport"]
        print(f"Transport 총 요청: {transport_info['total_requests']}")
        print(f"Transport 평균 대기시간: {transport_info['average_wait_time']:.1f}")
        print(f"Transport 최종 활용률: {transport_info['utilization'] * 100:.1f}%")


if __name__ == "__main__":
    main()
