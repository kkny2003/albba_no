"""
(공정1 & 공정2 & 공정3) >> 조립공정 예제 (프레임워크 연산자 활용)
프레임워크의 & 및 >> 연산자를 사용하여 직관적인 공정 흐름을 구현합니다.
"""

import sys
import os
import simpy

# 프로젝트 루트 디렉토리를 Python 경로에 추가
sys.path.append(os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), 'src'))

from processes.base_process import BaseProcess
from Resource.helper import create_product_resource, ResourceType
from core.simulation_engine import SimulationEngine


class ManufacturingProcess(BaseProcess):
    """제조 공정 클래스 - 프레임워크 연산자 지원"""
    
    def __init__(self, env, process_name, output_name, processing_time=2.0):
        super().__init__(env, process_name=process_name)
        self.output_name = output_name
        self.processing_time = processing_time
        self.parallel_safe = True  # 병렬 실행 안전
        
    def process_logic(self, input_data=None):
        """제조 공정의 핵심 로직 (SimPy generator)"""
        print(f"[Time {self.env.now:.1f}] [{self.process_name}] Manufacturing started")
        
        # 제조 처리 시간만큼 대기
        yield self.env.timeout(self.processing_time)
        
        print(f"[Time {self.env.now:.1f}] [{self.process_name}] Manufacturing completed -> {self.output_name} produced")
        
        # 반제품 자원 생성 및 출력에 추가
        semi_product = create_product_resource(
            product_id=f"product_{self.process_name}",
            product_name=self.output_name,
            product_type=ResourceType.SEMI_FINISHED,
            quantity=1.0,
            unit="개"
        )
        self.add_output_resource(semi_product)
        
        return self.output_name


class AssemblyProcess(BaseProcess):
    """조립 공정 클래스 - 프레임워크 연산자 지원"""
    
    def __init__(self, env, process_name="조립공정", assembly_time=3.0):
        super().__init__(env, process_name=process_name)
        self.assembly_time = assembly_time
        self.parallel_safe = False  # 조립은 순차 처리 필요
        
    def process_logic(self, input_data=None):
        """조립 공정의 핵심 로직 (SimPy generator)"""
        print(f"[Time {self.env.now:.1f}] [{self.process_name}] Assembly started")
        print(f"  -> Input data: {input_data}")
        
        # 조립 처리 시간만큼 대기
        yield self.env.timeout(self.assembly_time)
        
        print(f"[Time {self.env.now:.1f}] [{self.process_name}] Assembly completed -> Final product produced")
        
        # 완제품 자원 생성 및 출력에 추가
        final_product = create_product_resource(
            product_id="final_assembly",
            product_name="Final Product",
            product_type=ResourceType.FINISHED_PRODUCT,
            quantity=1.0,
            unit="개"
        )
        self.add_output_resource(final_product)
        
        return "Final Product"


def run_simple_chain_demo(env):
    """간단한 체인 데모 실행"""
    print("=== Chain Demo: (Process1 & Process2 & Process3) >> Assembly ===")
    
    # 병렬 제조 공정 3개 생성
    process1 = ManufacturingProcess(env, "Process1", "PartA", processing_time=2.0)
    process2 = ManufacturingProcess(env, "Process2", "PartB", processing_time=2.5)
    process3 = ManufacturingProcess(env, "Process3", "PartC", processing_time=1.8)
    
    # 조립 공정 생성  
    assembly = AssemblyProcess(env, "Assembly", assembly_time=3.0)
    
    # 공정 체인 생성: (Process1 & Process2 & Process3) >> Assembly
    print("Building chain: (Process1 & Process2 & Process3) >> Assembly")
    process_chain = (process1 & process2 & process3) >> assembly
    
    print(f"Chain created: {process_chain.get_process_summary()}")
    
    # 체인 실행 (비SimPy 방식)
    print("Executing chain...")
    final_result = process_chain.execute_chain(input_data="RawMaterial")
    
    print(f"Final result: {final_result}")
    print("=== Chain Demo Complete ===")


def main():
    """메인 실행 함수"""
    print("Manufacturing Simulation Framework - Chain Operator Demo")
    print("=" * 60)
    
    # 시뮬레이션 엔진 생성
    engine = SimulationEngine(random_seed=42)
    env = engine.env
    
    print(f"Start time: {env.now}")
    
    # 간단한 체인 데모 실행 (비SimPy 방식)
    run_simple_chain_demo(env)
    
    print(f"End time: {env.now}")
    print("Demo Complete!")


if __name__ == "__main__":
    main()
