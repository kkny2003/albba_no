"""
ManufacturingProcess와 TransportProcess 연동 예제

이 예제는 ManufacturingProcess에서 제조 완료 후 TransportProcess를 활용하여
출하품을 운송하는 시나리오를 보여줍니다.
"""

import os
import sys

# 프로젝트 루트를 파이썬 모듈 검색 경로에 추가
project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, project_root)

import simpy
from src.core.resource_manager import AdvancedResourceManager
from src.Processes.manufacturing_process import ManufacturingProcess
from src.Processes.transport_process import TransportProcess
from src.Resource.machine import Machine
from src.Resource.worker import Worker
from src.Resource.resource_base import Resource, ResourceRequirement, ResourceType


def create_integrated_scenario():
    """ManufacturingProcess와 TransportProcess 통합 시나리오 생성"""
    
    # 1. SimPy 환경 생성
    env = simpy.Environment()
    
    # 2. AdvancedResourceManager 생성 (선택적)
    resource_manager = AdvancedResourceManager(env)
    
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
    
    # 4. 운송 장비 및 인력 생성
    transport_machine = Machine(
        env=env,
        machine_id="transport_vehicle_001", 
        name="운송차량1",
        capacity=1,
        processing_time=1.0
    )
    
    transport_worker = Worker(
        env=env,
        worker_id="transport_worker_001",
        name="운송작업자1", 
        skills=["운송", "하역"],
        efficiency=1.2
    )
    
    # 5. 자원 요구사항 정의
    manufacturing_requirements = [
        ResourceRequirement(
            resource_type=ResourceType.RAW_MATERIAL,
            name="원자재",
            required_quantity=1.0,
            unit="kg",
            is_mandatory=True
        )
    ]
    
    transport_requirements = [
        ResourceRequirement(
            resource_type=ResourceType.FINISHED_PRODUCT,
            name="완제품",
            required_quantity=1.0,
            unit="개",
            is_mandatory=True
        )
    ]
    
    # 6. 입력/출력 자원 정의
    manufacturing_input = {"원자재": 1.5, "전력": 0.5}
    manufacturing_output = {"완제품": 1.0}
    
    transport_input = {"완제품": 1.0}
    transport_output = {"배송완료": 1.0}
    
    # 7. TransportProcess 생성
    transport_process = TransportProcess(
        env=env,
        process_id="transport_001",
        process_name="출하품_운송공정",
        machines=[transport_machine],
        workers=[transport_worker],
        input_resources=transport_input,
        output_resources=transport_output,
        resource_requirements=transport_requirements,
        loading_time=0.5,    # 30분 적재
        transport_time=2.0,  # 2시간 운송
        unloading_time=0.5,  # 30분 하역
        cooldown_time=0.5,   # 30분 대기
        products_per_cycle=1
    )
    
    # 운송 경로 설정
    transport_process.set_route("제조공장 → 배송센터")
    
    print(f"[시간 {env.now:.1f}] TransportProcess 생성 완료")
    print(f"  - 적재시간: {transport_process.loading_time}시간")
    print(f"  - 운송시간: {transport_process.transport_time}시간") 
    print(f"  - 하역시간: {transport_process.unloading_time}시간")
    print(f"  - 대기시간: {transport_process.cooldown_time}시간")
    print(f"  - 총 운송시간: {transport_process.processing_time}시간")
    
    # 8. ManufacturingProcess 생성 (TransportProcess 연동)
    manufacturing_process = ManufacturingProcess(
        env=env,
        process_id="mfg_integrated_001",
        process_name="통합_제조공정1",
        machines=[machine],
        workers=[worker],
        input_resources=manufacturing_input,
        output_resources=manufacturing_output,
        resource_requirements=manufacturing_requirements,
        processing_time=2.0,
        products_per_cycle=1,
        resource_manager=resource_manager,      # 선택적
        transport_process=transport_process     # TransportProcess 연동
    )
    
    print(f"[시간 {env.now:.1f}] ManufacturingProcess 생성 완료 - TransportProcess 연동")
    
    return env, resource_manager, manufacturing_process, transport_process


def run_integrated_manufacturing_cycles(env, manufacturing_process, transport_process, cycles: int = 3):
    """통합된 제조+운송 사이클을 여러 번 실행하는 함수"""
    
    def integrated_cycle():
        """제조 + 운송 통합 사이클 실행"""
        print(f"\n[시간 {env.now:.1f}] === 통합 제조+운송 사이클 시작 ===")
        
        try:
            # 제조공정 실행 (완료 후 자동으로 TransportProcess 실행)
            yield from manufacturing_process.process_logic(
                input_data={"제품유형": "표준제품", "배치번호": f"BATCH_{env.now}"}
            )
            
            print(f"[시간 {env.now:.1f}] === 통합 제조+운송 사이클 완료 ===\n")
            
        except Exception as e:
            print(f"[시간 {env.now:.1f}] 통합 사이클 중 오류: {e}")
    
    # 여러 통합 사이클을 순차적으로 실행
    for cycle in range(cycles):
        print(f"\n{'='*60}")
        print(f"통합 제조+운송 사이클 {cycle + 1}/{cycles} 시작")
        print(f"{'='*60}")
        
        yield from integrated_cycle()
        
        # 사이클 간 간격
        if cycle < cycles - 1:
            yield env.timeout(1.0)


def monitor_integrated_status(env, manufacturing_process, transport_process, interval: float = 5.0):
    """통합 시스템 상태를 주기적으로 모니터링하는 함수"""
    
    while True:
        yield env.timeout(interval)
        
        print(f"\n[시간 {env.now:.1f}] === 통합 시스템 상태 모니터링 ===")
        
        # ManufacturingProcess 상태
        mfg_transport_status = manufacturing_process.get_transport_status()
        print(f"제조공정 자동 운송: {mfg_transport_status['auto_transport_enabled']}")
        
        # TransportProcess 상태
        transport_queue_status = transport_process.get_transport_queue_status()
        print(f"운송 대기열: {len(transport_queue_status['items_in_queue'])}개")
        print(f"운송 상태: {transport_queue_status['transport_status']}")
        print(f"운송 경로: {transport_queue_status['route']}")
        
        # 배치 상태
        if transport_queue_status['batch_status']:
            batch_info = transport_queue_status['batch_status']
            print(f"운송 배치: {batch_info['current_size']}/{batch_info['batch_size']}")
        
        print(f"{'='*50}\n")


def main():
    """메인 실행 함수"""
    print("=" * 70)
    print("ManufacturingProcess + TransportProcess 통합 시뮬레이션 시작")
    print("=" * 70)
    
    # 1. 통합 시나리오 설정
    env, resource_manager, manufacturing_process, transport_process = create_integrated_scenario()
    
    # 2. 시스템 상태 모니터링 프로세스 시작
    env.process(monitor_integrated_status(env, manufacturing_process, transport_process, interval=15.0))
    
    # 3. 통합 제조+운송 사이클 실행 프로세스 시작
    env.process(run_integrated_manufacturing_cycles(env, manufacturing_process, transport_process, cycles=3))
    
    # 4. 시뮬레이션 실행
    print(f"\n[시간 {env.now:.1f}] 통합 시뮬레이션 시작\n")
    env.run(until=50)
    
    # 5. 최종 결과 출력
    print("\n" + "=" * 70)
    print("통합 시뮬레이션 완료 - 최종 결과")
    print("=" * 70)
    
    # ManufacturingProcess 상태
    mfg_status = manufacturing_process.get_transport_status()
    print(f"제조공정 자동 운송 활성화: {mfg_status['auto_transport_enabled']}")
    print(f"TransportProcess 연동: {mfg_status['has_transport_process']}")
    
    if mfg_status['transport_process_info']:
        tp_info = mfg_status['transport_process_info']
        print(f"연동된 TransportProcess: {tp_info['transport_process_name']} (ID: {tp_info['transport_process_id']})")
        print(f"총 운송 소요시간: {tp_info['loading_time'] + tp_info['transport_time'] + tp_info['unloading_time'] + tp_info['cooldown_time']}시간")
    
    # TransportProcess 최종 상태
    final_queue_status = transport_process.get_transport_queue_status()
    print(f"운송 대기열 최종 상태: {len(final_queue_status['items_in_queue'])}개")
    print(f"최종 운송 상태: {final_queue_status['transport_status']}")
    
    print("\n통합 시뮬레이션의 장점:")
    print("1. 모듈화된 구조: 제조와 운송이 독립적으로 관리됨")
    print("2. 재사용성: TransportProcess를 다른 공정에서도 활용 가능") 
    print("3. 확장성: TransportProcess의 모든 고급 기능 활용 가능")
    print("4. 유지보수성: 각 공정의 로직이 명확히 분리됨")


if __name__ == "__main__":
    main()
