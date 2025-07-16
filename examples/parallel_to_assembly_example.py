"""
(공정1 & 공정2 & 공정3) >> 조립공정 예제
병렬로 3개의 공정이 실행된 후, 그 결과가 조립공정으로 전달되는 시나리오를 구현합니다.
"""

import sys
import os
import simpy

# 프로젝트 루트 디렉토리를 Python 경로에 추가
sys.path.append(os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), 'src'))

from processes.base_process import BaseProcess
from Resource.helper import create_product_resource, ResourceType
from core.simulation_engine import SimulationEngine


# 간단한 제조 공정 클래스
class ManufacturingProcess(BaseProcess):
    """제조 공정을 시뮬레이트하는 클래스"""
    
    def __init__(self, env, process_name, output_name, processing_time=2.0):
        super().__init__(env, process_name=process_name)
        self.output_name = output_name
        self.processing_time = processing_time
        self.parallel_safe = True  # 병렬 실행 가능
        
    def process_logic(self, input_data=None):
        """실제 제조 공정 로직 (SimPy generator)"""
        print(f"[시간 {self.env.now:.1f}] [{self.process_name}] 작업 시작")
        
        # 처리 시간만큼 대기 (SimPy timeout 이벤트)
        yield self.env.timeout(self.processing_time)
        
        print(f"[시간 {self.env.now:.1f}] [{self.process_name}] 작업 완료 -> {self.output_name} 생산")
        
        # 반제품 생산 및 출력 자원에 추가
        semi_product = create_product_resource(
            product_id=f"product_{self.process_name}",
            product_name=self.output_name,
            product_type=ResourceType.SEMI_FINISHED,
            quantity=1.0,
            unit="개"
        )
        self.add_output_resource(semi_product)
        
        return self.output_name


# 조립 공정 클래스
class AssemblyProcess(BaseProcess):
    """조립 공정을 시뮬레이트하는 클래스"""
    
    def __init__(self, env, process_name="조립공정", assembly_time=3.0):
        super().__init__(env, process_name=process_name)
        self.assembly_time = assembly_time
        self.parallel_safe = False  # 조립은 순차 처리
        
    def process_logic(self, input_data=None):
        """조립 공정 로직 (SimPy generator)"""
        print(f"[시간 {self.env.now:.1f}] [{self.process_name}] 조립 시작")
        print(f"  입력 자원: {input_data if input_data else '병렬 공정 결과물'}")
        
        # 조립 시간만큼 대기
        yield self.env.timeout(self.assembly_time)
        
        print(f"[시간 {self.env.now:.1f}] [{self.process_name}] 조립 완료 -> 완제품 생산")
        
        # 완제품 생산
        final_product = create_product_resource(
            product_id="final_assembly",
            product_name="완제품",
            product_type=ResourceType.FINISHED_PRODUCT,
            quantity=1.0,
            unit="개"
        )
        self.add_output_resource(final_product)
        
        return "완제품"


def run_simulation(env):
    """전체 시뮬레이션을 실행하는 함수"""
    print("\n=== (공정1 & 공정2 & 공정3) >> 조립공정 시뮬레이션 시작 ===")
    
    # 3개의 병렬 제조 공정 생성
    process1 = ManufacturingProcess(env, "공정1", "부품A", processing_time=2.0)
    process2 = ManufacturingProcess(env, "공정2", "부품B", processing_time=2.5)  
    process3 = ManufacturingProcess(env, "공정3", "부품C", processing_time=1.8)
    
    # 조립 공정 생성
    assembly = AssemblyProcess(env, "조립공정", assembly_time=3.0)
    
    # 병렬 공정들을 동시에 시작
    print("\n1단계: 병렬 제조 공정 시작")
    process1_result = env.process(process1.execute())
    process2_result = env.process(process2.execute())  
    process3_result = env.process(process3.execute())
    
    # 모든 병렬 공정이 완료될 때까지 대기
    results = yield process1_result & process2_result & process3_result
    print(f"\n모든 병렬 공정 완료! 결과: {list(results.values())}")
    
    # 병렬 공정 결과를 조립 공정의 입력으로 사용
    print("\n2단계: 조립 공정 시작")
    assembly_input = [result['result'] for result in results.values() if result]
    assembly_result = yield env.process(assembly.execute(assembly_input))
    
    print(f"\n조립 공정 완료! 최종 결과: {assembly_result['result']}")
    print("\n=== 시뮬레이션 종료 ===")


def main():
    """메인 실행 함수"""
    print("=== 제조 시뮬레이션 프레임워크 예제 ===")
    
    # 시뮬레이션 엔진 생성
    engine = SimulationEngine(random_seed=42)
    env = engine.env
    
    # 시뮬레이션 프로세스 등록 및 실행
    engine.add_process(run_simulation)
    
    print(f"시뮬레이션 시작 시간: {env.now}")
    engine.run(until=15)  # 15시간 동안 실행
    print(f"시뮬레이션 종료 시간: {env.now}")


if __name__ == "__main__":
    main()
