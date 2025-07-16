"""
올바른 SimPy 사용 예제 - 제조업 시뮬레이션
모든 프로세스가 SimPy를 올바르게 사용하는 예제입니다.
"""

import simpy
import sys
import os

# 프로젝트 루트 디렉토리를 Python 경로에 추가
sys.path.append(os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), 'src'))

from core.simulation_engine import SimulationEngine
from Resource.machine import Machine
from Resource.worker import Worker
from Resource.product import Product
from Resource.helper import Resource, ResourceRequirement, ResourceType
from processes.manufacturing_process import ManufacturingProcess
from processes.assembly_process import AssemblyProcess
from processes.quality_control_process import QualityControlProcess


def simple_manufacturing_simulation():
    """간단한 제조업 시뮬레이션 예제 (SimPy 기반)"""
    print("=== SimPy 기반 제조업 시뮬레이션 시작 ===")
    
    # 시뮬레이션 엔진 생성
    engine = SimulationEngine()
    env = engine.env
    
    # 기계와 작업자 생성 (SimPy 기반)
    machine1 = Machine(env, "기계1", "드릴링머신", processing_time=2.0)
    worker1 = Worker(env, "작업자1", ["드릴링", "조립"], work_speed=1.2)
    
    # 자원 정의
    raw_material = Resource("원자재_001", "원자재", ResourceType.RAW_MATERIAL, 10.0, "kg")
    tool = Resource("도구_001", "드릴", ResourceType.TOOL, 1.0, "개")
    semi_product = Resource("반제품_001", "반제품", ResourceType.SEMI_FINISHED, 1.0, "개")
    finished_product = Resource("완제품_001", "완제품", ResourceType.FINISHED_PRODUCT, 1.0, "개")
    
    # 자원 요구사항 정의
    manufacturing_requirements = [
        ResourceRequirement(ResourceType.RAW_MATERIAL, "원자재", 2.0, "kg", True),
        ResourceRequirement(ResourceType.TOOL, "드릴", 1.0, "개", True)
    ]
    
    assembly_requirements = [
        ResourceRequirement(ResourceType.SEMI_FINISHED, "반제품", 2.0, "개", True)
    ]
    
    quality_requirements = [
        ResourceRequirement(ResourceType.FINISHED_PRODUCT, "완제품", 1.0, "개", True)
    ]
    
    # SimPy 기반 제조 공정 생성
    manufacturing = ManufacturingProcess(
        env=env,
        machines=[machine1], 
        workers=[worker1],
        input_resources=[raw_material, tool],
        output_resources=[semi_product],
        resource_requirements=manufacturing_requirements,
        process_name="제조공정",
        processing_time=3.0
    )
    
    # SimPy 기반 조립 공정 생성
    assembly = AssemblyProcess(
        env=env,
        machines=[machine1],
        workers=[worker1], 
        input_resources=[semi_product],
        output_resources=[finished_product],
        resource_requirements=assembly_requirements,
        process_name="조립공정",
        assembly_time=2.5
    )
    
    # SimPy 기반 품질관리 공정 생성  
    quality_control = QualityControlProcess(
        env=env,
        inspection_criteria={"품질기준": "A급"},
        input_resources=[finished_product],
        output_resources=[],
        resource_requirements=quality_requirements,
        process_name="품질관리공정",
        inspection_time=1.0
    )
    
    def production_process(env, product_data):
        """제품 생산 프로세스 (SimPy generator 함수)"""
        print(f"[시간 {env.now:.1f}] 제품 생산 시작: {product_data}")
        
        # 1. 제조 공정 실행
        print(f"[시간 {env.now:.1f}] 제조 공정 시작")
        result1 = yield env.process(manufacturing.execute(product_data))
        print(f"[시간 {env.now:.1f}] 제조 공정 완료: {result1}")
        
        # 2. 조립 공정 실행
        print(f"[시간 {env.now:.1f}] 조립 공정 시작")
        result2 = yield env.process(assembly.execute(result1))
        print(f"[시간 {env.now:.1f}] 조립 공정 완료: {result2}")
        
        # 3. 품질관리 공정 실행
        print(f"[시간 {env.now:.1f}] 품질관리 공정 시작")
        result3 = yield env.process(quality_control.execute(result2))
        print(f"[시간 {env.now:.1f}] 품질관리 공정 완료: {result3}")
        
        print(f"[시간 {env.now:.1f}] 전체 생산 프로세스 완료!")
    
    # 제품 생산 프로세스를 시뮬레이션에 추가
    engine.add_process(production_process, "제품A")
    
    # 추가 제품 생성 (동시 처리 테스트)
    def delayed_production(env):
        """지연된 제품 생산"""
        yield env.timeout(1.0)  # 1시간 후 시작
        yield env.process(production_process(env, "제품B"))
    
    engine.add_process(delayed_production)
    
    # 시뮬레이션 실행 (15시간 동안)
    engine.run(until=15)
    
    # 결과 출력
    print("\n=== 시뮬레이션 결과 ===")
    stats = engine.get_statistics()
    for key, value in stats.items():
        print(f"{key}: {value}")
    
    print("\n=== 기계 가동률 ===")
    print(f"기계1 가동률: {machine1.get_utilization():.2%}")
    
    print("\n=== 작업자 효율성 ===")
    print(f"작업자1 완료 작업 수: {worker1.total_tasks_completed}")
    print(f"작업자1 총 작업 시간: {worker1.total_work_time:.1f}")


if __name__ == "__main__":
    simple_manufacturing_simulation()
