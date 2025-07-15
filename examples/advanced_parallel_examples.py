"""
고급 병렬 공정 예제
개선된 워크플로우 시스템을 활용한 복잡한 제조 시나리오들
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import time
from src.processes import ManufacturingProcess, AssemblyProcess, QualityControlProcess
from src.processes.advanced_workflow import (
    ParallelProcessChain, WorkflowGraph, SynchronizationPoint, 
    SynchronizationType, ConditionalBranch, ExecutionMode
)
from src.core.resource_manager import (
    AdvancedResourceManager, AllocationStrategy, ResourceStatus
)
from src.Resource.helper import Resource, ResourceType
from src.Resource.product import Product


class EngineBlockProcess(ManufacturingProcess):
    """엔진 블록 가공 공정"""
    
    def __init__(self):
        super().__init__(
            machines=["CNC기계1"], 
            workers=["가공작업자1"],
            process_id="engine_block_001",
            process_name="엔진블록가공"
        )
        self.set_execution_priority(8)
    
    def process_logic(self, input_data=None):
        print(f"[{self.process_name}] 엔진 블록 가공 중...")
        time.sleep(2.0)  # 가공 시간 시뮬레이션
        return {"component": "엔진블록", "quality": "A급", "status": "완료"}


class PistonProcess(ManufacturingProcess):
    """피스톤 제조 공정"""
    
    def __init__(self):
        super().__init__(
            machines=["프레스기1"], 
            workers=["단조작업자1"],
            process_id="piston_001",
            process_name="피스톤제조"
        )
        self.set_execution_priority(8)
    
    def process_logic(self, input_data=None):
        print(f"[{self.process_name}] 피스톤 제조 중...")
        time.sleep(1.5)  # 제조 시간 시뮬레이션
        return {"component": "피스톤", "quality": "A급", "status": "완료"}


class CrankshaftProcess(ManufacturingProcess):
    """크랭크샤프트 가공 공정"""
    
    def __init__(self):
        super().__init__(
            machines=["터닝머신1"], 
            workers=["정밀가공자1"],
            process_id="crankshaft_001", 
            process_name="크랭크샤프트가공"
        )
        self.set_execution_priority(9)
    
    def process_logic(self, input_data=None):
        print(f"[{self.process_name}] 크랭크샤프트 가공 중...")
        time.sleep(2.5)  # 가공 시간 시뮬레이션
        return {"component": "크랭크샤프트", "quality": "A급", "status": "완료"}


class EngineAssemblyProcess(AssemblyProcess):
    """엔진 조립 공정 (모든 부품이 준비되어야 시작 가능)"""
    
    def __init__(self):
        super().__init__(
            machines=["조립라인1"], 
            workers=["조립작업자1", "조립작업자2"],
            process_id="engine_assembly_001",
            process_name="엔진조립"
        )
        self.set_execution_priority(10)
        
        # 조립 조건: 모든 부품이 A급이어야 함
        def assembly_condition(input_data):
            if not input_data or not isinstance(input_data, list):
                return False
            
            required_components = {"엔진블록", "피스톤", "크랭크샤프트"}
            available_components = set()
            
            for data in input_data:
                if isinstance(data, dict) and data.get("status") == "완료" and data.get("quality") == "A급":
                    available_components.add(data.get("component"))
            
            return required_components.issubset(available_components)
        
        self.add_execution_condition(assembly_condition)
    
    def process_logic(self, input_data=None):
        print(f"[{self.process_name}] 엔진 조립 시작 - 모든 부품 준비 완료")
        time.sleep(3.0)  # 조립 시간 시뮬레이션
        return {"product": "완성된엔진", "quality": "A급", "status": "조립완료"}


class QualityInspectionProcess(QualityControlProcess):
    """품질 검사 공정 (조건부 분기를 위한)"""
    
    def __init__(self):
        super().__init__(
            inspection_criteria={"성능": ">= 95%", "외관": "양호"},
            process_id="quality_inspection_001",
            process_name="품질검사"
        )
        self.set_execution_priority(7)
    
    def process_logic(self, input_data=None):
        print(f"[{self.process_name}] 품질 검사 실시...")
        time.sleep(1.0)  # 검사 시간 시뮬레이션
        
        # 90% 확률로 합격 (시뮬레이션)
        import random
        is_pass = random.random() > 0.1
        
        if is_pass:
            print(f"[{self.process_name}] 품질 검사 합격!")
            return {"inspection_result": "합격", "quality": "A급", "next_step": "packaging"}
        else:
            print(f"[{self.process_name}] 품질 검사 불합격 - 재작업 필요")
            return {"inspection_result": "불합격", "quality": "재작업", "next_step": "rework"}


class PackagingProcess(ManufacturingProcess):
    """포장 공정"""
    
    def __init__(self):
        super().__init__(
            machines=["포장기1"], 
            workers=["포장작업자1"],
            process_id="packaging_001",
            process_name="포장공정"
        )
        self.set_execution_priority(5)
    
    def process_logic(self, input_data=None):
        print(f"[{self.process_name}] 제품 포장 중...")
        time.sleep(0.5)
        return {"product": "포장완료제품", "status": "출하준비"}


class ReworkProcess(ManufacturingProcess):
    """재작업 공정"""
    
    def __init__(self):
        super().__init__(
            machines=["재작업라인1"], 
            workers=["재작업자1"],
            process_id="rework_001",
            process_name="재작업공정"
        )
        self.set_execution_priority(6)
    
    def process_logic(self, input_data=None):
        print(f"[{self.process_name}] 재작업 실시...")
        time.sleep(2.0)
        return {"product": "재작업완료제품", "quality": "A급", "status": "재검사필요"}


def car_engine_manufacturing_example():
    """
    자동차 엔진 제조 예제
    - 엔진블록, 피스톤, 크랭크샤프트를 병렬 제조
    - 모든 부품 완료 후 동기화하여 조립
    """
    print("=" * 80)
    print("🚗 자동차 엔진 제조 - 병렬 공정 + 동기화 예제")
    print("=" * 80)
    
    # 고급 자원 관리자 설정
    resource_manager = AdvancedResourceManager(AllocationStrategy.PRIORITY)
    
    # 자원 등록
    cnc_machine = Resource("cnc_001", "CNC기계1", ResourceType.MACHINE, 1.0, "대")
    press_machine = Resource("press_001", "프레스기1", ResourceType.MACHINE, 1.0, "대") 
    turning_machine = Resource("turning_001", "터닝머신1", ResourceType.MACHINE, 1.0, "대")
    assembly_line = Resource("assembly_001", "조립라인1", ResourceType.MACHINE, 1.0, "대")
    
    resource_manager.register_resource(cnc_machine, capacity=1.0)
    resource_manager.register_resource(press_machine, capacity=1.0)
    resource_manager.register_resource(turning_machine, capacity=1.0)
    resource_manager.register_resource(assembly_line, capacity=1.0)
    
    resource_manager.start_resource_monitor(0.5)
    
    # 프로세스 생성
    engine_block = EngineBlockProcess()
    piston = PistonProcess()
    crankshaft = CrankshaftProcess()
    engine_assembly = EngineAssemblyProcess()
    
    # 워크플로우 그래프 생성
    workflow = WorkflowGraph()
    
    # 프로세스들을 그래프에 추가
    workflow.add_process(engine_block)
    workflow.add_process(piston)
    workflow.add_process(crankshaft)
    workflow.add_process(engine_assembly)
    
    # 의존성 설정 (병렬 부품 제조 → 조립)
    workflow.add_dependency(engine_block.process_id, engine_assembly.process_id)
    workflow.add_dependency(piston.process_id, engine_assembly.process_id)
    workflow.add_dependency(crankshaft.process_id, engine_assembly.process_id)
    
    # 동기화 포인트 설정 (모든 부품 완료 대기)
    sync_point = SynchronizationPoint(
        sync_id="parts_completion_sync",
        sync_type=SynchronizationType.ALL_COMPLETE,
        timeout=10.0
    )
    workflow.add_parallel_group([
        engine_block.process_id, 
        piston.process_id, 
        crankshaft.process_id
    ], sync_point)
    
    # 워크플로우 시각화
    print("\n워크플로우 구조:")
    print(workflow.visualize_graph())
    
    # 워크플로우 실행
    print("\n워크플로우 실행 시작...")
    start_time = time.time()
    
    results = workflow.execute_workflow({"raw_materials": "철강자재"})
    
    execution_time = time.time() - start_time
    
    # 결과 출력
    print(f"\n워크플로우 실행 완료! (총 소요 시간: {execution_time:.2f}초)")
    print("\n실행 결과:")
    print("-" * 40)
    
    for process_id, result in results.items():
        process_name = result.process_name
        success_status = "✅ 성공" if result.success else "❌ 실패"
        print(f"• {process_name}: {success_status} ({result.execution_time:.2f}초)")
        if result.result_data:
            print(f"  결과: {result.result_data}")
    
    # 자원 관리자 상태 리포트
    resource_manager.print_status_report()
    resource_manager.stop_resource_monitor()


def smartphone_manufacturing_example():
    """
    스마트폰 제조 예제
    - 메인보드, 케이스, 배터리 병렬 제조
    - 분기/합류 구조 + 조건부 분기
    """
    print("\n" + "=" * 80)
    print("📱 스마트폰 제조 - 복합 워크플로우 예제")
    print("=" * 80)
    
    # 병렬 프로세스 체인 생성
    parallel_chain = ParallelProcessChain()
    
    # 부품 제조 프로세스들
    mainboard_process = ManufacturingProcess(
        machines=["SMT라인1"], workers=["전자작업자1"],
        process_id="mainboard_001", process_name="메인보드제조"
    ).set_execution_priority(9)
    
    case_process = ManufacturingProcess(
        machines=["사출기1"], workers=["플라스틱작업자1"],
        process_id="case_001", process_name="케이스제조"
    ).set_execution_priority(7)
    
    battery_process = ManufacturingProcess(
        machines=["배터리라인1"], workers=["배터리작업자1"],
        process_id="battery_001", process_name="배터리제조"
    ).set_execution_priority(8)
    
    # 병렬 체인에 프로세스 추가
    parallel_chain.processes = [mainboard_process, case_process, battery_process]
    
    # 병렬 실행 모드 설정
    parallel_chain.set_parallel_execution(max_workers=3)
    
    # 동기화 포인트 설정 (모든 부품 완료 대기)
    sync_point = SynchronizationPoint(
        sync_id="components_ready_sync",
        sync_type=SynchronizationType.ALL_COMPLETE,
        timeout=15.0
    )
    parallel_chain.add_synchronization_point(sync_point)
    
    print("병렬 부품 제조 시작...")
    component_results = parallel_chain.execute_with_synchronization(
        input_data={"order": "갤럭시S25", "quantity": 1},
        sync_point=sync_point
    )
    
    print("\n부품 제조 결과:")
    for result in component_results:
        status = "✅" if result.success else "❌"
        print(f"{status} {result.process_name}: {result.execution_time:.2f}초")
    
    # 조립 공정
    assembly_process = AssemblyProcess(
        machines=["최종조립라인1"], workers=["조립작업자1", "조립작업자2"],
        process_id="final_assembly_001", process_name="최종조립"
    )
    
    print("\n최종 조립 시작...")
    assembly_result = assembly_process.execute(component_results)
    print(f"조립 완료: {assembly_result}")


def conditional_workflow_example():
    """
    조건부 워크플로우 예제
    - 품질 검사 결과에 따른 다른 경로 처리
    """
    print("\n" + "=" * 80)
    print("🔍 조건부 워크플로우 - 품질 검사 분기 예제")
    print("=" * 80)
    
    # 품질 검사 조건 함수
    def quality_check_condition(input_data):
        if isinstance(input_data, dict):
            return input_data.get("inspection_result") == "합격"
        return False
    
    def rework_condition(input_data):
        if isinstance(input_data, dict):
            return input_data.get("inspection_result") == "불합격"
        return False
    
    # 프로세스들 생성
    quality_inspection = QualityInspectionProcess()
    packaging = PackagingProcess()
    rework = ReworkProcess()
    
    # 조건부 분기 설정
    packaging.add_execution_condition(quality_check_condition)
    rework.add_execution_condition(rework_condition)
    
    # 조건부 분기 정의
    def branch_condition(input_data):
        if isinstance(input_data, dict):
            return input_data.get("next_step", "unknown")
        return "unknown"
    
    conditional_branch = ConditionalBranch(
        condition_func=branch_condition,
        branches={
            "packaging": [packaging],
            "rework": [rework],
            "unknown": []
        }
    )
    
    # 워크플로우 그래프로 복잡한 분기 구현
    workflow = WorkflowGraph()
    workflow.add_process(quality_inspection)
    workflow.add_process(packaging)
    workflow.add_process(rework)
    
    print("품질 검사 및 조건부 분기 실행...")
    
    # 여러 번 실행해서 다른 결과 확인
    for i in range(3):
        print(f"\n--- 시뮬레이션 {i+1} ---")
        
        # 품질 검사 실행
        inspection_result = quality_inspection.execute({"product": f"제품{i+1}"})
        print(f"검사 결과: {inspection_result}")
        
        if inspection_result and isinstance(inspection_result, dict):
            result_data = inspection_result.get('result', {})
            
            # 조건부 분기 평가
            next_processes = conditional_branch.evaluate(result_data)
            
            if next_processes:
                for process in next_processes:
                    if process.can_execute(result_data):
                        final_result = process.execute(result_data)
                        print(f"최종 처리: {process.process_name} - {final_result}")
                    else:
                        print(f"실행 조건 불만족: {process.process_name}")
            else:
                print("해당하는 처리 경로가 없습니다.")


def main():
    """메인 함수 - 모든 예제 실행"""
    print("🏭 고급 병렬 공정 시스템 데모")
    print("=" * 80)
    
    try:
        # 1. 자동차 엔진 제조 (병렬 + 동기화)
        car_engine_manufacturing_example()
        
        # 2. 스마트폰 제조 (복합 워크플로우)
        smartphone_manufacturing_example()
        
        # 3. 조건부 워크플로우
        conditional_workflow_example()
        
    except Exception as e:
        print(f"예제 실행 중 오류 발생: {e}")
        import traceback
        traceback.print_exc()
    
    print("\n" + "=" * 80)
    print("🎉 모든 고급 워크플로우 예제 완료!")
    print("=" * 80)
    print("""
    개선된 기능들:
    ✅ 병렬 프로세스 실행 (ThreadPoolExecutor 기반)
    ✅ 동기화 포인트 (ALL_COMPLETE, ANY_COMPLETE, THRESHOLD)
    ✅ 워크플로우 그래프 (복잡한 의존성 관리)
    ✅ 조건부 분기 (품질 검사 결과에 따른 라우팅)
    ✅ 고급 자원 관리 (경합, 예약, 우선순위)
    ✅ 실행 조건 및 우선순위 설정
    ✅ 성능 지표 및 모니터링
    """)


if __name__ == "__main__":
    # 원하는 예제 함수만 직접 호출할 수 있도록 수정
    # 예시: 자동차 엔진 제조 예제만 실행
    smartphone_manufacturing_example()
