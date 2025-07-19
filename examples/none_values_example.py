#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
None 값을 사용한 고장확률 제어 예제

이 예제는 None 값을 사용하여 고장/실수 기능을 선택적으로 활성화/비활성화하는 방법을 보여줍니다.
"""

import simpy
import sys
import os

# 프로젝트 루트 디렉토리를 Python 경로에 추가
sys.path.append(os.path.join(os.path.dirname(__file__), '..'))

from src.Resource.machine import Machine
from src.Resource.worker import Worker
from src.Resource.product import Product


def demonstrate_none_values(env):
    """None 값을 사용한 다양한 시나리오를 시연합니다."""
    
    print("🔧 다양한 고장확률 설정 시연")
    print("="*50)
    
    # 1. 완전히 안정적인 기계 (고장 기능 비활성화)
    stable_machine = Machine(
        env=env,
        machine_id="STABLE_M001",
        machine_type="안정적기계",
        processing_time=2.0,
        failure_probability=None,      # 고장 기능 비활성화
        mean_time_to_failure=None,     # 비활성화
        mean_time_to_repair=None       # 비활성화
    )
    
    # 2. 고장은 있지만 확률이 0인 기계
    zero_failure_machine = Machine(
        env=env,
        machine_id="ZERO_M001",
        machine_type="확률0기계",
        processing_time=2.0,
        failure_probability=0.0,       # 고장 확률 0
        mean_time_to_failure=50.0,     # 설정되어 있지만 확률이 0이므로 사용되지 않음
        mean_time_to_repair=5.0
    )
    
    # 3. 실제 고장이 발생할 수 있는 기계
    real_failure_machine = Machine(
        env=env,
        machine_id="REAL_M001",
        machine_type="실제고장기계",
        processing_time=2.0,
        failure_probability=0.3,       # 30% 고장 확률 (높게 설정하여 테스트)
        mean_time_to_failure=20.0,
        mean_time_to_repair=3.0
    )
    
    # 4. 완전히 안정적인 작업자 (실수/휴식 기능 비활성화)
    stable_worker = Worker(
        env=env,
        worker_id="STABLE_W001",
        skills=["안정작업"],
        work_speed=1.0,
        error_probability=None,        # 실수 기능 비활성화
        mean_time_to_rest=None,        # 휴식 기능 비활성화
        mean_rest_time=None            # 비활성화
    )
    
    # 5. 실수는 없지만 휴식은 필요한 작업자
    no_error_worker = Worker(
        env=env,
        worker_id="NOERROR_W001",
        skills=["정확작업"],
        work_speed=1.2,
        error_probability=None,        # 실수 없음
        mean_time_to_rest=30.0,        # 휴식 필요
        mean_rest_time=5.0
    )
    
    # 6. 실수와 휴식이 모두 발생할 수 있는 작업자
    real_worker = Worker(
        env=env,
        worker_id="REAL_W001",
        skills=["일반작업"],
        work_speed=1.0,
        error_probability=0.2,         # 20% 실수 확률 (높게 설정하여 테스트)
        mean_time_to_rest=25.0,
        mean_rest_time=4.0
    )
    
    # 각 조합으로 제품 생산 테스트
    machines = [stable_machine, zero_failure_machine, real_failure_machine]
    workers = [stable_worker, no_error_worker, real_worker]
    
    machine_names = ["안정적기계", "확률0기계", "실제고장기계"]
    worker_names = ["안정적작업자", "실수없는작업자", "실제작업자"]
    
    for i, (machine, machine_name) in enumerate(zip(machines, machine_names)):
        for j, (worker, worker_name) in enumerate(zip(workers, worker_names)):
            product_id = f"PROD_{i+1}_{j+1}"
            product = Product(product_id, "테스트제품")
            
            print(f"\n--- {product_id}: {machine_name} + {worker_name} ---")
            
            try:
                # 작업자 작업
                yield env.process(worker.work(product, "준비작업", 1.0))
                
                # 기계 작업
                yield env.process(machine.operate(product, 2.0))
                
                # 작업자 검사
                yield env.process(worker.work(product, "검사작업", 0.5))
                
                print(f"✅ {product_id} 생산 완료!")
                
            except Exception as e:
                print(f"❌ {product_id} 생산 중 오류: {e}")
            
            # 제품 간 간격
            yield env.timeout(0.5)


def print_comparison_statistics(machines, workers):
    """각 리소스의 통계를 비교 출력합니다."""
    
    print("\n" + "="*80)
    print("📊 기계별 통계 비교")
    print("="*80)
    
    for machine in machines:
        status = machine.get_status()
        print(f"\n🔧 {status['machine_id']} ({status['machine_type']}):")
        print(f"   총 처리: {status['total_processed']}개")
        print(f"   가동률: {status['utilization']:.2%}")
        print(f"   가용성: {status['availability']:.2%}")
        print(f"   총 고장: {status['total_failures']}회")
        print(f"   고장률: {status['failure_rate']:.4f}회/시간")
        print(f"   현재 상태: {'🔴 고장' if status['is_broken'] else '🟢 정상'}")
        
        # None 값 여부 표시
        failure_setting = "비활성화" if machine.failure_probability is None else f"{machine.failure_probability:.1%}"
        print(f"   고장 설정: {failure_setting}")
    
    print("\n" + "="*80)
    print("👷 작업자별 통계 비교")
    print("="*80)
    
    for worker in workers:
        status = worker.get_status()
        print(f"\n👤 {status['worker_id']} (기술: {', '.join(status['skills'])}):")
        print(f"   총 작업: {status['total_tasks_completed']}개")
        print(f"   가동률: {status['utilization']:.2%}")
        print(f"   가용성: {status['availability']:.2%}")
        print(f"   총 실수: {status['total_errors']}회")
        print(f"   실수율: {status['error_rate']:.2%}")
        print(f"   현재 상태: {'😴 휴식' if status['is_resting'] else '💪 작업가능'}")
        
        # None 값 여부 표시
        error_setting = "비활성화" if worker.error_probability is None else f"{worker.error_probability:.1%}"
        rest_setting = "비활성화" if worker.mean_time_to_rest is None else f"{worker.mean_time_to_rest:.1f}h"
        print(f"   실수 설정: {error_setting}")
        print(f"   휴식 설정: {rest_setting}")


def main():
    """메인 시뮬레이션 함수"""
    print("🎯 None 값을 사용한 고장확률 제어 예제")
    print("="*60)
    print("이 예제는 None 값을 사용하여 고장/실수 기능을 선택적으로 제어하는 방법을 보여줍니다.")
    print()
    
    # SimPy 환경 생성
    env = simpy.Environment()
    
    # 시뮬레이션 프로세스 시작
    demo_process = env.process(demonstrate_none_values(env))
    
    # 시뮬레이션 실행
    try:
        env.run(until=100)
    except Exception as e:
        print(f"시뮬레이션 중 오류 발생: {e}")
    
    print(f"\n🏁 시뮬레이션 완료! (총 시간: {env.now:.1f}시간)")


def test_none_usage():
    """None 값 사용법 테스트"""
    print("\n🧪 None 값 사용법 테스트")
    print("="*40)
    
    env = simpy.Environment()
    
    # 각각 다른 None 설정으로 리소스 생성
    test_cases = [
        {
            "name": "모든 기능 비활성화",
            "machine_params": {
                "failure_probability": None,
                "mean_time_to_failure": None,
                "mean_time_to_repair": None
            },
            "worker_params": {
                "error_probability": None,
                "mean_time_to_rest": None,
                "mean_rest_time": None
            }
        },
        {
            "name": "일부 기능만 활성화",
            "machine_params": {
                "failure_probability": 0.1,  # 고장 활성화
                "mean_time_to_failure": None,  # 비활성화
                "mean_time_to_repair": 5.0    # 활성화
            },
            "worker_params": {
                "error_probability": None,     # 실수 비활성화
                "mean_time_to_rest": 50.0,     # 휴식 활성화
                "mean_rest_time": None         # 기본값 사용
            }
        }
    ]
    
    for i, test_case in enumerate(test_cases):
        print(f"\n테스트 케이스 {i+1}: {test_case['name']}")
        
        # 기계 생성
        machine = Machine(
            env=env,
            machine_id=f"TEST_M{i+1}",
            machine_type="테스트기계",
            **test_case['machine_params']
        )
        
        # 작업자 생성
        worker = Worker(
            env=env,
            worker_id=f"TEST_W{i+1}",
            skills=["테스트"],
            **test_case['worker_params']
        )
        
        print(f"✅ 기계 생성 성공: {machine.machine_id}")
        print(f"   고장확률: {machine.failure_probability}")
        print(f"   수리시간: {machine.mean_time_to_repair}")
        
        print(f"✅ 작업자 생성 성공: {worker.worker_id}")
        print(f"   실수확률: {worker.error_probability}")
        print(f"   휴식간격: {worker.mean_time_to_rest}")


if __name__ == "__main__":
    main()
    test_none_usage()
