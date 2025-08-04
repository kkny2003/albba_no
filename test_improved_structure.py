#!/usr/bin/env python3
"""
개선된 Processes와 Flow 모듈 구조 테스트

이 스크립트는 개선된 모듈 구조가 제대로 작동하는지 확인합니다.
"""

import simpy
from src.Processes import (
    BaseProcess, ManufacturingProcess, AssemblyProcess, 
    QualityControlProcess, TransportProcess
)
from src.Flow import ProcessChain, MultiProcessGroup, AdvancedWorkflowManager
from src.Resource.resource_base import Resource, ResourceRequirement, ResourceType


class TestProcess(BaseProcess):
    """테스트용 프로세스"""
    
    def __init__(self, env, name, processing_time=1.0):
        # 테스트용 더미 machine과 worker 생성
        class DummyMachine:
            def __init__(self, name):
                self.machine_id = name
                self.operate = lambda: None
                
        class DummyWorker:
            def __init__(self, name):
                self.worker_id = name
                self.work = lambda: None
                
        super().__init__(
            env=env,
            process_id=f"test_{name}",
            process_name=name,
            machines=[DummyMachine(f"machine_{name}")],
            workers=[DummyWorker(f"worker_{name}")],
            processing_time=processing_time
        )
        
    def process_logic(self, input_data=None):
        print(f"[시간 {self.env.now:.1f}] {self.process_name} 실행 중...")
        yield self.env.timeout(self.processing_time)
        print(f"[시간 {self.env.now:.1f}] {self.process_name} 완료")
        return f"{self.process_name}_결과"


def test_basic_process():
    """기본 프로세스 테스트"""
    print("=== 기본 프로세스 테스트 ===")
    env = simpy.Environment()
    
    # 테스트 프로세스 생성
    test_proc = TestProcess(env, "테스트공정", 2.0)
    
    # 프로세스 실행
    env.process(test_proc.execute("테스트데이터"))
    env.run(until=5.0)
    print()


def test_process_chain():
    """프로세스 체인 테스트"""
    print("=== 프로세스 체인 테스트 ===")
    env = simpy.Environment()
    
    # 여러 프로세스 생성
    proc1 = TestProcess(env, "공정1", 1.0)
    proc2 = TestProcess(env, "공정2", 1.5)
    proc3 = TestProcess(env, "공정3", 1.0)
    
    # 체인 생성 (>> 연산자 사용)
    chain = proc1 >> proc2 >> proc3
    
    # 체인 실행
    env.process(chain.execute("체인테스트데이터"))
    env.run(until=10.0)
    print()


def test_multi_group_flow():
    """다중 프로세스 그룹 테스트"""
    print("=== 다중 프로세스 그룹 테스트 ===")
    env = simpy.Environment()
    
    # 여러 프로세스 생성
    proc1 = TestProcess(env, "병렬공정1", 2.0)
    proc2 = TestProcess(env, "병렬공정2", 1.5)
    proc3 = TestProcess(env, "병렬공정3", 2.5)
    
    # 그룹 생성 (& 연산자 사용)
    group = proc1 & proc2 & proc3
    
    # 그룹 실행
    env.process(group.execute("그룹테스트데이터"))
    env.run(until=10.0)
    print()


def test_advanced_workflow():
    """고급 워크플로우 테스트"""
    print("=== 고급 워크플로우 테스트 ===")
    env = simpy.Environment()
    
    # 워크플로우 매니저 생성
    workflow_manager = AdvancedWorkflowManager(env)
    
    # 프로세스들 생성
    proc1 = TestProcess(env, "워크플로우공정1", 1.0)
    proc2 = TestProcess(env, "워크플로우공정2", 1.5)
    
    # 워크플로우 단계 정의
    workflow_steps = [proc1, proc2]
    
    # 워크플로우 실행
    env.process(workflow_manager.execute_workflow("워크플로우테스트데이터", workflow_steps))
    env.run(until=10.0)
    
    # 통계 출력
    stats = workflow_manager.get_workflow_statistics()
    print(f"워크플로우 통계: {stats}")
    print()


def test_manufacturing_process():
    """제조 공정 테스트"""
    print("=== 제조 공정 테스트 ===")
    env = simpy.Environment()
    
    # 자원 생성
    input_resources = [
        Resource("raw_material_1", "원자재1", ResourceType.RAW_MATERIAL)
    ]
    output_resources = [
        Resource("semi_finished_1", "반제품1", ResourceType.SEMI_FINISHED)
    ]
    resource_requirements = [
        ResourceRequirement(ResourceType.RAW_MATERIAL, "원자재", 1.0, "kg", True)
    ]
    
    # 테스트용 더미 machine과 worker 생성
    class DummyMachine:
        def __init__(self, name):
            self.machine_id = name
            self.operate = lambda: None
            
    class DummyWorker:
        def __init__(self, name):
            self.worker_id = name
            self.work = lambda: None
    
    # 제조 공정 생성
    manufacturing = ManufacturingProcess(
        env=env,
        machines=[DummyMachine("manufacturing_machine")],
        workers=[DummyWorker("manufacturing_worker")],
        input_resources=input_resources,
        output_resources=output_resources,
        resource_requirements=resource_requirements,
        process_name="테스트제조공정",
        processing_time=2.0
    )
    
    # 제조 공정 실행
    env.process(manufacturing.execute("제조테스트데이터"))
    env.run(until=5.0)
    print()


def main():
    """메인 테스트 함수"""
    print("개선된 Processes와 Flow 모듈 구조 테스트 시작\n")
    
    try:
        test_basic_process()
        test_process_chain()
        test_multi_group_flow()
        test_advanced_workflow()
        test_manufacturing_process()
        
        print("모든 테스트가 성공적으로 완료되었습니다!")
        
    except Exception as e:
        print(f"테스트 중 오류 발생: {e}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    main() 