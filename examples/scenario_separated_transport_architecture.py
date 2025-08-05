"""
분리된 구조의 ManufacturingProcess + ResourceManager + TransportProcess 예제

이 예제는 다음과 같은 구조를 보여줍니다:
1. ManufacturingProcess: 운송 요청만 보냄
2. ResourceManager: 운송 요청 관리 및 TransportProcess 할당
3. TransportProcess: 실제 운송 처리
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


def create_separated_architecture_scenario():
    """분리된 구조의 시나리오 생성"""
    
    # 1. SimPy 환경 생성
    env = simpy.Environment()
    
    # 2. AdvancedResourceManager 생성
    resource_manager = AdvancedResourceManager(env)
    
    # Transport 자원 등록 (용량 2개의 운송 슬롯)
    resource_manager.register_resource(
        resource_id="transport",
        capacity=2,
        resource_type=ResourceType.TRANSPORT,
        description="운송 요청 관리용 자원"
    )
    
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
        process_name="자동_운송공정",
        machines=[transport_machine],
        workers=[transport_worker],
        input_resources=transport_input,
        output_resources=transport_output,
        resource_requirements=transport_requirements,
        loading_time=0.3,    # 18분 적재
        transport_time=1.5,  # 1.5시간 운송
        unloading_time=0.2,  # 12분 하역
        cooldown_time=0.2,   # 12분 대기
        products_per_cycle=1
    )
    
    # 운송 경로 설정
    transport_process.set_route("제조공장 → 중간창고 → 최종목적지")
    
    # 8. ResourceManager에 TransportProcess 등록
    resource_manager.register_transport_process("transport_main", transport_process)
    
    print(f"[시간 {env.now:.1f}] TransportProcess ResourceManager에 등록 완료")
    
    # 9. ManufacturingProcess 생성 (운송 요청만 담당)
    manufacturing_process = ManufacturingProcess(
        env=env,
        process_id="mfg_separated_001",
        process_name="분리구조_제조공정1",
        machines=[machine],
        workers=[worker],
        input_resources=manufacturing_input,
        output_resources=manufacturing_output,
        resource_requirements=manufacturing_requirements,
        processing_time=2.0,
        products_per_cycle=1,
        resource_manager=resource_manager,  # 운송 요청용
        transport_process=transport_process # 참조용 (직접 호출하지 않음)
    )
    
    print(f"[시간 {env.now:.1f}] ManufacturingProcess 생성 완료 - 운송 요청만 담당")
    
    return env, resource_manager, manufacturing_process, transport_process


def run_separated_manufacturing_cycles(env, manufacturing_process, cycles: int = 3):
    """분리된 구조에서 제조 사이클 실행"""
    
    def manufacturing_cycle():
        """제조 사이클 (운송 요청만 보냄)"""
        print(f"\n[시간 {env.now:.1f}] === 분리구조 제조 사이클 시작 ===")
        
        try:
            # 제조공정 실행 (완료 후 ResourceManager에 운송 요청)
            yield from manufacturing_process.process_logic(
                input_data={"제품유형": "표준제품", "배치번호": f"BATCH_{env.now}"}
            )
            
            print(f"[시간 {env.now:.1f}] === 분리구조 제조 사이클 완료 ===")
            print(f"[시간 {env.now:.1f}] (운송은 ResourceManager와 TransportProcess가 별도로 처리)\n")
            
        except Exception as e:
            print(f"[시간 {env.now:.1f}] 제조 사이클 중 오류: {e}")
    
    # 여러 제조 사이클을 실행
    for cycle in range(cycles):
        print(f"\n{'='*70}")
        print(f"분리구조 제조 사이클 {cycle + 1}/{cycles} 시작")
        print(f"{'='*70}")
        
        yield from manufacturing_cycle()
        
        # 사이클 간 간격
        if cycle < cycles - 1:
            yield env.timeout(2.0)  # 2시간 간격


def monitor_separated_system(env, resource_manager, manufacturing_process, interval: float = 8.0):
    """분리된 시스템 상태 모니터링"""
    
    while True:
        yield env.timeout(interval)
        
        print(f"\n[시간 {env.now:.1f}] === 분리구조 시스템 상태 모니터링 ===")
        
        # ManufacturingProcess 상태
        mfg_status = manufacturing_process.get_transport_status()
        print(f"제조공정 운송모드: {mfg_status['transport_mode']}")
        print(f"제조공정 자동운송: {mfg_status['auto_transport_enabled']}")
        
        # ResourceManager Transport 관리 상태
        transport_mgmt_status = resource_manager.get_transport_status()
        print(f"등록된 TransportProcess: {transport_mgmt_status['registered_transports']}개")
        print(f"Transport 자원 상태: {transport_mgmt_status['transport_resource_status']['in_use']}/{transport_mgmt_status['transport_resource_status']['capacity']} 사용중")
        
        # 각 TransportProcess 상태
        for transport_id, tp_info in transport_mgmt_status['transport_processes'].items():
            print(f"  - {transport_id}: {tp_info['process_name']} (상태: {tp_info['status']})")
        
        print(f"{'='*60}\n")


def main():
    """메인 실행 함수"""
    print("=" * 80)
    print("분리된 구조의 ManufacturingProcess + ResourceManager + TransportProcess")
    print("=" * 80)
    print("구조:")
    print("1. ManufacturingProcess: 운송 요청만 보냄")
    print("2. ResourceManager: 운송 요청 관리 및 TransportProcess 할당")
    print("3. TransportProcess: 실제 운송 처리")
    print("=" * 80)
    
    # 1. 분리된 구조 시나리오 설정
    env, resource_manager, manufacturing_process, transport_process = create_separated_architecture_scenario()
    
    # 2. 시스템 상태 모니터링 프로세스 시작
    env.process(monitor_separated_system(env, resource_manager, manufacturing_process, interval=12.0))
    
    # 3. 분리된 구조 제조 사이클 실행 프로세스 시작
    env.process(run_separated_manufacturing_cycles(env, manufacturing_process, cycles=4))
    
    # 4. 시뮬레이션 실행
    print(f"\n[시간 {env.now:.1f}] 분리구조 시뮬레이션 시작\n")
    env.run(until=60)
    
    # 5. 최종 결과 출력
    print("\n" + "=" * 80)
    print("분리구조 시뮬레이션 완료 - 최종 결과")
    print("=" * 80)
    
    # ManufacturingProcess 최종 상태
    mfg_final_status = manufacturing_process.get_transport_status()
    print(f"제조공정 운송 모드: {mfg_final_status['transport_mode']}")
    print(f"제조공정에서 ResourceManager 연동: {mfg_final_status['has_resource_manager']}")
    
    # ResourceManager Transport 관리 최종 상태
    rm_transport_status = resource_manager.get_transport_status()
    print(f"ResourceManager 등록된 TransportProcess: {rm_transport_status['registered_transports']}개")
    
    # 자원 관리자 통계
    rm_stats = resource_manager.get_statistics()
    print(f"총 자원 요청: {rm_stats['total_requests']}")
    print(f"성공한 할당: {rm_stats['successful_allocations']}")
    print(f"성공률: {rm_stats['success_rate']:.1f}%")
    
    print("\n분리된 구조의 장점:")
    print("1. 책임 분리: 각 컴포넌트가 명확한 역할을 담당")
    print("2. 확장성: ResourceManager에서 여러 TransportProcess 관리 가능")
    print("3. 재사용성: 하나의 TransportProcess를 여러 제조공정에서 공유")
    print("4. 유지보수성: 운송 로직 변경 시 TransportProcess만 수정")
    print("5. 테스트 용이성: 각 컴포넌트를 독립적으로 테스트 가능")


if __name__ == "__main__":
    main()
