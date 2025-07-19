#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
고장률 가중치 기능 예제

이 예제는 Process에서 Machine과 Worker의 고장률에 가중치를 적용하는 기능을 시연합니다.
- 일반 공정 vs 고장률 가중치가 적용된 공정 비교
- 가중치에 따른 고장률 변화 관찰
- 실제 시뮬레이션에서의 고장 발생 빈도 차이 확인
"""

import simpy
import sys
import os

# 프로젝트 루트 디렉토리를 Python 경로에 추가
sys.path.append(os.path.join(os.path.dirname(__file__), '..'))

from src.Resource.machine import Machine
from src.Resource.worker import Worker
from src.Resource.product import Product
from src.processes.manufacturing_process import ManufacturingProcess
from src.Resource.helper import Resource, ResourceRequirement, ResourceType


def create_test_resources():
    """테스트용 자원들을 생성합니다."""
    # 입력 자원 (원자재)
    input_resources = [
        Resource(
            resource_id="raw_material_001",
            name="철강 원자재",
            resource_type=ResourceType.RAW_MATERIAL,
            quantity=100.0,
            unit="kg"
        )
    ]
    
    # 출력 자원 (완성품)
    output_resources = [
        Resource(
            resource_id="finished_product_001",
            name="완성된 부품",
            resource_type=ResourceType.FINISHED_PRODUCT,
            quantity=1.0,
            unit="개"
        )
    ]
    
    # 자원 요구사항
    resource_requirements = [
        ResourceRequirement(
            resource_type=ResourceType.RAW_MATERIAL,
            name="철강 원자재",
            required_quantity=5.0,
            unit="kg",
            is_mandatory=True
        )
    ]
    
    return input_resources, output_resources, resource_requirements


def run_simulation_with_weights(env, failure_weight_machine=1.0, failure_weight_worker=1.0):
    """가중치를 적용한 시뮬레이션을 실행합니다."""
    
    print(f"\n{'='*60}")
    print(f"시뮬레이션 시작 - 기계 가중치: {failure_weight_machine}, 작업자 가중치: {failure_weight_worker}")
    print(f"{'='*60}")
    
    # 고장확률이 있는 기계 생성
    machine = Machine(
        env=env,
        machine_id="M001",
        machine_type="CNC 가공기",
        processing_time=3.0,
        failure_probability=0.15,  # 15% 기본 고장 확률
        mean_time_to_failure=30.0,
        mean_time_to_repair=5.0
    )
    
    # 실수확률이 있는 작업자 생성
    worker = Worker(
        env=env,
        worker_id="W001",
        skills=["CNC 가공", "품질검사"],
        work_speed=1.0,
        error_probability=0.10,  # 10% 기본 실수 확률
        mean_time_to_rest=80.0,
        mean_rest_time=10.0
    )
    
    # 테스트 자원 생성
    input_resources, output_resources, resource_requirements = create_test_resources()
    
    # 가중치가 적용된 제조 공정 생성
    manufacturing_proc = ManufacturingProcess(
        env=env,
        machines=[machine],
        workers=[worker],
        input_resources=input_resources,
        output_resources=output_resources,
        resource_requirements=resource_requirements,
        process_name=f"가중치 적용 공정 (M:{failure_weight_machine}, W:{failure_weight_worker})",
        processing_time=2.0,
        failure_weight_machine=failure_weight_machine,  # 기계 고장률 가중치
        failure_weight_worker=failure_weight_worker     # 작업자 실수율 가중치
    )
    
    # 제품 생성 및 공정 실행
    def production_process():
        for i in range(5):  # 5개 제품 생산
            product = Product(f"제품_{i+1}")
            print(f"\n[시간 {env.now:.1f}] 제품 {product.product_id} 생산 시작")
            
            try:
                # 공정 실행 (SimPy generator 사용)
                result = yield env.process(manufacturing_proc.execute(product))
                print(f"[시간 {env.now:.1f}] 제품 {product.product_id} 생산 완료")
                
                # 기계 작업 시뮬레이션
                yield env.process(machine.operate(product))
                
                # 작업자 작업 시뮬레이션
                yield env.process(worker.work(product, "품질검사", 1.5))
                
            except Exception as e:
                print(f"[시간 {env.now:.1f}] 제품 {product.product_id} 생산 중 오류: {e}")
            
            # 다음 제품 생산까지 대기
            yield env.timeout(1.0)
    
    # 프로세스 시작
    env.process(production_process())
    
    # 시뮬레이션 실행
    env.run(until=50)  # 50시간 동안 시뮬레이션
    
    # 결과 출력
    print(f"\n{'='*60}")
    print(f"시뮬레이션 결과 요약")
    print(f"{'='*60}")
    print(f"기계 {machine.machine_id}:")
    print(f"  - 총 고장 횟수: {machine.total_failures}")
    print(f"  - 고장률: {machine.get_failure_rate():.4f}")
    print(f"  - 가용성: {machine.get_availability():.2%}")
    print(f"  - 총 처리 작업: {machine.total_processed}")
    
    print(f"\n작업자 {worker.worker_id}:")
    print(f"  - 총 실수 횟수: {worker.total_errors}")
    print(f"  - 실수율: {worker.get_error_rate():.4f}")
    print(f"  - 가용성: {worker.get_availability():.2%}")
    print(f"  - 완료 작업: {worker.total_tasks_completed}")
    
    return {
        'machine_failures': machine.total_failures,
        'machine_failure_rate': machine.get_failure_rate(),
        'worker_errors': worker.total_errors,
        'worker_error_rate': worker.get_error_rate()
    }


def main():
    """메인 실행 함수"""
    print("고장률 가중치 기능 테스트 시작\n")
    
    results = []
    
    # 1. 기본 시나리오 (가중치 없음)
    env1 = simpy.Environment()
    result1 = run_simulation_with_weights(env1, 1.0, 1.0)
    results.append(("기본 (가중치 1.0)", result1))
    
    # 2. 기계 고장률 1.5배 증가
    env2 = simpy.Environment()
    result2 = run_simulation_with_weights(env2, 1.5, 1.0)
    results.append(("기계 가중치 1.5배", result2))
    
    # 3. 작업자 실수율 2.0배 증가
    env3 = simpy.Environment()
    result3 = run_simulation_with_weights(env3, 1.0, 2.0)
    results.append(("작업자 가중치 2.0배", result3))
    
    # 4. 둘 다 증가
    env4 = simpy.Environment()
    result4 = run_simulation_with_weights(env4, 1.3, 1.5)
    results.append(("둘 다 증가 (M:1.3, W:1.5)", result4))
    
    # 전체 결과 비교
    print(f"\n{'='*80}")
    print(f"전체 결과 비교")
    print(f"{'='*80}")
    print(f"{'시나리오':<25} {'기계 고장수':<12} {'기계 고장률':<12} {'작업자 실수수':<15} {'작업자 실수율':<12}")
    print(f"{'-'*80}")
    
    for scenario, result in results:
        print(f"{scenario:<25} "
              f"{result['machine_failures']:<12} "
              f"{result['machine_failure_rate']:<12.4f} "
              f"{result['worker_errors']:<15} "
              f"{result['worker_error_rate']:<12.4f}")
    
    print(f"\n{'='*80}")
    print("테스트 완료!")
    print("가중치가 높을수록 고장/실수 빈도가 증가하는 것을 확인할 수 있습니다.")
    print(f"{'='*80}")


if __name__ == "__main__":
    main()
