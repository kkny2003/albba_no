#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
리소스 고장확률 기능 예제

이 예제는 Machine과 Worker 클래스에 구현된 고장확률 기능을 시연합니다.
- 기계의 고장 확률과 수리 과정
- 작업자의 실수 확률과 휴식 과정
- 고장/실수 관련 통계 수집
"""

import simpy
import sys
import os

# 프로젝트 루트 디렉토리를 Python 경로에 추가
sys.path.append(os.path.join(os.path.dirname(__file__), '..'))

from src.Resource.machine import Machine
from src.Resource.worker import Worker
from src.Resource.product import Product


def manufacturing_process_with_failures(env):
    """고장확률이 있는 제조 프로세스를 시뮬레이션합니다."""
    
    # 고장확률이 있는 기계 생성
    # failure_probability: 0.1 (10% 고장 확률)
    # mean_time_to_failure: 50.0 (평균 50시간마다 고장)
    # mean_time_to_repair: 8.0 (평균 8시간 수리)
    machine = Machine(
        env=env,
        machine_id="M001",
        machine_type="밀링머신",
        processing_time=5.0,
        failure_probability=0.1,
        mean_time_to_failure=50.0,
        mean_time_to_repair=8.0
    )
    
    # 실수확률이 있는 작업자 생성
    # error_probability: 0.05 (5% 실수 확률)
    # mean_time_to_rest: 100.0 (평균 100시간마다 휴식 필요)
    # mean_rest_time: 15.0 (평균 15시간 휴식)
    worker = Worker(
        env=env,
        worker_id="W001",
        skills=["밀링", "품질검사"],
        work_speed=1.2,
        error_probability=0.05,
        mean_time_to_rest=100.0,
        mean_rest_time=15.0
    )
    
    # 제품 생산 프로세스
    for i in range(20):  # 20개 제품 생산
        product = Product(f"PROD_{i+1:03d}", "제품A")
        
        print(f"\n=== 제품 {product.product_id} 생산 시작 ===")
        
        # 작업자가 준비 작업 수행
        try:
            yield env.process(worker.work(product, "준비작업", 2.0))
        except Exception as e:
            print(f"작업자 작업 중 오류: {e}")
            continue
        
        # 기계가 가공 작업 수행
        try:
            yield env.process(machine.operate(product, 5.0))
        except Exception as e:
            print(f"기계 작업 중 오류: {e}")
            continue
        
        # 작업자가 품질검사 수행
        try:
            yield env.process(worker.work(product, "품질검사", 1.5))
        except Exception as e:
            print(f"품질검사 중 오류: {e}")
            continue
        
        print(f"제품 {product.product_id} 생산 완료!")
        
        # 제품 간 간격
        yield env.timeout(1.0)


def print_statistics(machine, worker):
    """기계와 작업자의 통계를 출력합니다."""
    print("\n" + "="*60)
    print("🔧 기계 통계")
    print("="*60)
    
    machine_status = machine.get_status()
    print(f"기계 ID: {machine_status['machine_id']}")
    print(f"총 처리 작업: {machine_status['total_processed']}개")
    print(f"가동률: {machine_status['utilization']:.2%}")
    print(f"가용성: {machine_status['availability']:.2%}")
    print(f"총 고장 횟수: {machine_status['total_failures']}회")
    print(f"고장률: {machine_status['failure_rate']:.4f}회/시간")
    print(f"현재 상태: {'고장 중' if machine_status['is_broken'] else '정상'}")
    
    print("\n" + "="*60)
    print("👷 작업자 통계")
    print("="*60)
    
    worker_status = worker.get_status()
    print(f"작업자 ID: {worker_status['worker_id']}")
    print(f"총 완료 작업: {worker_status['total_tasks_completed']}개")
    print(f"가동률: {worker_status['utilization']:.2%}")
    print(f"가용성: {worker_status['availability']:.2%}")
    print(f"총 실수 횟수: {worker_status['total_errors']}회")
    print(f"실수율: {worker_status['error_rate']:.2%}")
    print(f"현재 상태: {'휴식 중' if worker_status['is_resting'] else '작업 가능'}")


def main():
    """메인 시뮬레이션 함수"""
    print("🏭 제조 시뮬레이션 - 리소스 고장확률 예제")
    print("="*60)
    
    # SimPy 환경 생성
    env = simpy.Environment()
    
    # 제조 프로세스 시작
    process = env.process(manufacturing_process_with_failures(env))
    
    # 시뮬레이션 실행 (200시간 시뮬레이션)
    try:
        env.run(until=200)
    except Exception as e:
        print(f"시뮬레이션 중 오류 발생: {e}")
    
    print(f"\n시뮬레이션 완료! (시뮬레이션 시간: {env.now:.1f}시간)")
    
    # 통계 출력은 global 변수나 다른 방법으로 접근해야 함
    # 여기서는 예제를 간단히 하기 위해 생략


def test_failure_functions():
    """고장 관련 함수들을 개별적으로 테스트합니다."""
    print("\n🧪 고장 기능 테스트")
    print("="*40)
    
    env = simpy.Environment()
    
    # 고장확률이 높은 기계 생성 (테스트용)
    test_machine = Machine(
        env=env,
        machine_id="TEST_M001",
        machine_type="테스트기계",
        failure_probability=0.8,  # 80% 고장 확률 (테스트용)
        mean_time_to_repair=2.0
    )
    
    # 실수확률이 높은 작업자 생성 (테스트용)
    test_worker = Worker(
        env=env,
        worker_id="TEST_W001",
        skills=["테스트"],
        error_probability=0.7,  # 70% 실수 확률 (테스트용)
        mean_rest_time=3.0
    )
    
    def test_process():
        # 강제 고장 테스트
        yield env.process(test_machine.force_failure())
        
        # 강제 휴식 테스트
        yield env.process(test_worker.force_rest())
        
        # 통계 출력
        print("\n테스트 기계 상태:")
        print(test_machine.get_status())
        
        print("\n테스트 작업자 상태:")
        print(test_worker.get_status())
    
    env.process(test_process())
    env.run(until=50)
    
    print("테스트 완료!")


if __name__ == "__main__":
    main()
    test_failure_functions()
