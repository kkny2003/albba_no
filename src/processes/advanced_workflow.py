"""
고급 워크플로우 관리 모듈
병렬 공정, 동기화, 조건부 분기 등을 지원하는 확장된 워크플로우 관리 기능을 제공합니다.
"""

import asyncio
import threading
from concurrent.futures import ThreadPoolExecutor, as_completed
from typing import List, Dict, Any, Callable, Optional, Set, Tuple
from enum import Enum
from dataclasses import dataclass
import uuid
import time
from .base_process import BaseProcess, ProcessChain


class ExecutionMode(Enum):
    """실행 모드 열거형"""
    SEQUENTIAL = "sequential"  # 순차 실행
    PARALLEL = "parallel"      # 병렬 실행  
    CONDITIONAL = "conditional"  # 조건부 실행


class SynchronizationType(Enum):
    """동기화 타입 열거형"""
    ALL_COMPLETE = "all_complete"    # 모든 프로세스 완료 대기
    ANY_COMPLETE = "any_complete"    # 하나만 완료되면 진행
    THRESHOLD = "threshold"          # 임계값만큼 완료되면 진행


@dataclass
class ProcessResult:
    """공정 실행 결과"""
    process_id: str
    process_name: str
    success: bool
    result_data: Any
    execution_time: float
    error_message: Optional[str] = None


@dataclass
class SynchronizationPoint:
    """동기화 포인트 정의"""
    sync_id: str
    sync_type: SynchronizationType
    threshold: int = 1  # THRESHOLD 타입일 때 필요한 완료 개수
    timeout: Optional[float] = None  # 타임아웃 (초)


class ConditionalBranch:
    """조건부 분기 클래스"""
    
    def __init__(self, condition_func: Callable[[Any], str], branches: Dict[str, List[BaseProcess]]):
        """
        조건부 분기 초기화
        
        Args:
            condition_func: 입력 데이터를 받아 분기 키를 반환하는 함수
            branches: 분기 키별 프로세스 리스트
        """
        self.condition_func = condition_func
        self.branches = branches
        self.branch_id = str(uuid.uuid4())
    
    def evaluate(self, input_data: Any) -> List[BaseProcess]:
        """
        조건을 평가하여 실행할 프로세스들을 반환
        
        Args:
            input_data: 조건 평가에 사용할 데이터
            
        Returns:
            List[BaseProcess]: 실행할 프로세스 리스트
        """
        branch_key = self.condition_func(input_data)
        return self.branches.get(branch_key, [])


class ParallelProcessChain(ProcessChain):
    """병렬 실행을 지원하는 고급 프로세스 체인"""
    
    def __init__(self, processes: List[BaseProcess] = None):
        """
        병렬 프로세스 체인 초기화
        
        Args:
            processes: 초기 프로세스 리스트
        """
        super().__init__(processes)
        self.execution_mode = ExecutionMode.SEQUENTIAL  # 기본은 순차 실행
        self.max_workers = 4  # 기본 최대 워커 수
        self.sync_points: Dict[str, SynchronizationPoint] = {}  # 동기화 포인트들
        self.conditional_branches: List[ConditionalBranch] = []  # 조건부 분기들
        
    def set_parallel_execution(self, max_workers: int = 4) -> 'ParallelProcessChain':
        """
        병렬 실행 모드로 설정
        
        Args:
            max_workers: 최대 워커 스레드 수
            
        Returns:
            ParallelProcessChain: 체인 객체 (메서드 체이닝용)
        """
        self.execution_mode = ExecutionMode.PARALLEL
        self.max_workers = max_workers
        print(f"병렬 실행 모드 설정 (최대 워커: {max_workers})")
        return self
    
    def add_synchronization_point(self, sync_point: SynchronizationPoint) -> 'ParallelProcessChain':
        """
        동기화 포인트 추가
        
        Args:
            sync_point: 동기화 포인트
            
        Returns:
            ParallelProcessChain: 체인 객체
        """
        self.sync_points[sync_point.sync_id] = sync_point
        print(f"동기화 포인트 추가: {sync_point.sync_id} ({sync_point.sync_type.value})")
        return self
    
    def add_conditional_branch(self, branch: ConditionalBranch) -> 'ParallelProcessChain':
        """
        조건부 분기 추가
        
        Args:
            branch: 조건부 분기
            
        Returns:
            ParallelProcessChain: 체인 객체
        """
        self.conditional_branches.append(branch)
        print(f"조건부 분기 추가: {branch.branch_id}")
        return self
    
    def execute_parallel(self, input_data: Any = None) -> List[ProcessResult]:
        """
        병렬로 프로세스들을 실행
        
        Args:
            input_data: 입력 데이터
            
        Returns:
            List[ProcessResult]: 실행 결과들
        """
        print(f"병렬 실행 시작 - 총 {len(self.processes)}개 프로세스")
        results = []
        
        def execute_single_process(process: BaseProcess, data: Any) -> ProcessResult:
            """단일 프로세스 실행 함수"""
            start_time = time.time()
            try:
                print(f"[병렬] {process.process_name} 실행 시작")
                result = process.execute(data)
                execution_time = time.time() - start_time
                print(f"[병렬] {process.process_name} 완료 ({execution_time:.2f}초)")
                
                return ProcessResult(
                    process_id=process.process_id,
                    process_name=process.process_name,
                    success=True,
                    result_data=result,
                    execution_time=execution_time
                )
            except Exception as e:
                execution_time = time.time() - start_time
                print(f"[병렬] {process.process_name} 실행 실패: {str(e)}")
                
                return ProcessResult(
                    process_id=process.process_id,
                    process_name=process.process_name,
                    success=False,
                    result_data=None,
                    execution_time=execution_time,
                    error_message=str(e)
                )
        
        # ThreadPoolExecutor를 사용한 병렬 실행
        with ThreadPoolExecutor(max_workers=self.max_workers) as executor:
            # 모든 프로세스를 동시에 제출
            future_to_process = {
                executor.submit(execute_single_process, process, input_data): process 
                for process in self.processes
            }
            
            # 완료되는 대로 결과 수집
            for future in as_completed(future_to_process):
                process = future_to_process[future]
                try:
                    result = future.result()
                    results.append(result)
                except Exception as e:
                    print(f"프로세스 {process.process_name} 예외 발생: {e}")
                    results.append(ProcessResult(
                        process_id=process.process_id,
                        process_name=process.process_name,
                        success=False,
                        result_data=None,
                        execution_time=0.0,
                        error_message=str(e)
                    ))
        
        print(f"병렬 실행 완료 - 성공: {sum(1 for r in results if r.success)}개, "
              f"실패: {sum(1 for r in results if not r.success)}개")
        
        return results
    
    def execute_with_synchronization(self, input_data: Any = None, 
                                   sync_point: SynchronizationPoint = None) -> List[ProcessResult]:
        """
        동기화 포인트와 함께 실행
        
        Args:
            input_data: 입력 데이터
            sync_point: 동기화 포인트 (없으면 ALL_COMPLETE 기본 사용)
            
        Returns:
            List[ProcessResult]: 실행 결과들
        """
        if sync_point is None:
            sync_point = SynchronizationPoint(
                sync_id="default_sync",
                sync_type=SynchronizationType.ALL_COMPLETE
            )
        
        print(f"동기화 실행 시작 - {sync_point.sync_type.value} 모드")
        
        results = []
        completed_count = 0
        
        def execute_with_sync(process: BaseProcess, data: Any) -> ProcessResult:
            nonlocal completed_count
            
            start_time = time.time()
            try:
                print(f"[동기화] {process.process_name} 실행 시작")
                result = process.execute(data)
                execution_time = time.time() - start_time
                
                completed_count += 1
                print(f"[동기화] {process.process_name} 완료 ({completed_count}/{len(self.processes)})")
                
                return ProcessResult(
                    process_id=process.process_id,
                    process_name=process.process_name,
                    success=True,
                    result_data=result,
                    execution_time=execution_time
                )
            except Exception as e:
                execution_time = time.time() - start_time
                print(f"[동기화] {process.process_name} 실행 실패: {str(e)}")
                
                return ProcessResult(
                    process_id=process.process_id,
                    process_name=process.process_name,
                    success=False,
                    result_data=None,
                    execution_time=execution_time,
                    error_message=str(e)
                )
        
        with ThreadPoolExecutor(max_workers=self.max_workers) as executor:
            future_to_process = {
                executor.submit(execute_with_sync, process, input_data): process 
                for process in self.processes
            }
            
            # 동기화 타입에 따른 대기 조건
            if sync_point.sync_type == SynchronizationType.ALL_COMPLETE:
                # 모든 프로세스 완료 대기
                for future in as_completed(future_to_process):
                    result = future.result()
                    results.append(result)
                    
            elif sync_point.sync_type == SynchronizationType.ANY_COMPLETE:
                # 첫 번째 완료되는 프로세스만 대기
                for future in as_completed(future_to_process):
                    result = future.result()
                    results.append(result)
                    print(f"첫 번째 프로세스 완료 - 동기화 조건 만족")
                    break
                    
            elif sync_point.sync_type == SynchronizationType.THRESHOLD:
                # 임계값만큼 완료되면 진행
                for future in as_completed(future_to_process):
                    result = future.result()
                    results.append(result)
                    if len(results) >= sync_point.threshold:
                        print(f"임계값 {sync_point.threshold}개 프로세스 완료 - 동기화 조건 만족")
                        break
        
        print(f"동기화 실행 완료 - 처리된 프로세스: {len(results)}개")
        return results
    
    def execute_chain(self, input_data: Any = None) -> Any:
        """
        설정된 실행 모드에 따라 체인 실행
        
        Args:
            input_data: 입력 데이터
            
        Returns:
            Any: 실행 결과
        """
        if self.execution_mode == ExecutionMode.PARALLEL:
            return self.execute_parallel(input_data)
        else:
            # 기본 순차 실행은 부모 클래스 메서드 사용
            return super().execute_chain(input_data)


class WorkflowGraph:
    """복잡한 워크플로우를 그래프로 표현하고 실행하는 클래스"""
    
    def __init__(self):
        """워크플로우 그래프 초기화"""
        self.nodes: Dict[str, BaseProcess] = {}  # 노드들 (프로세스들)
        self.edges: Dict[str, List[str]] = {}  # 간선들 (의존성)
        self.conditional_edges: Dict[str, ConditionalBranch] = {}  # 조건부 간선들
        self.sync_points: Dict[str, SynchronizationPoint] = {}  # 동기화 포인트들
        self.execution_results: Dict[str, ProcessResult] = {}  # 실행 결과들
        
    def add_process(self, process: BaseProcess) -> 'WorkflowGraph':
        """
        프로세스를 그래프에 추가
        
        Args:
            process: 추가할 프로세스
            
        Returns:
            WorkflowGraph: 그래프 객체
        """
        self.nodes[process.process_id] = process
        if process.process_id not in self.edges:
            self.edges[process.process_id] = []
        print(f"프로세스 추가: {process.process_name} ({process.process_id})")
        return self
    
    def add_dependency(self, from_process_id: str, to_process_id: str) -> 'WorkflowGraph':
        """
        프로세스 간 의존성 추가 (from_process 완료 후 to_process 실행)
        
        Args:
            from_process_id: 선행 프로세스 ID
            to_process_id: 후행 프로세스 ID
            
        Returns:
            WorkflowGraph: 그래프 객체
        """
        if from_process_id not in self.edges:
            self.edges[from_process_id] = []
        self.edges[from_process_id].append(to_process_id)
        
        from_name = self.nodes[from_process_id].process_name
        to_name = self.nodes[to_process_id].process_name
        print(f"의존성 추가: {from_name} → {to_name}")
        return self
    
    def add_parallel_group(self, process_ids: List[str], 
                          sync_point: SynchronizationPoint = None) -> 'WorkflowGraph':
        """
        병렬 실행 그룹 추가
        
        Args:
            process_ids: 병렬로 실행할 프로세스 ID들
            sync_point: 동기화 포인트
            
        Returns:
            WorkflowGraph: 그래프 객체
        """
        if sync_point is None:
            sync_point = SynchronizationPoint(
                sync_id=f"parallel_group_{len(self.sync_points)}",
                sync_type=SynchronizationType.ALL_COMPLETE
            )
        
        self.sync_points[sync_point.sync_id] = sync_point
        
        process_names = [self.nodes[pid].process_name for pid in process_ids]
        print(f"병렬 그룹 추가: {', '.join(process_names)} (동기화: {sync_point.sync_type.value})")
        return self
    
    def execute_workflow(self, input_data: Any = None) -> Dict[str, ProcessResult]:
        """
        전체 워크플로우 실행 (토폴로지 정렬 기반)
        
        Args:
            input_data: 입력 데이터
            
        Returns:
            Dict[str, ProcessResult]: 프로세스 ID별 실행 결과
        """
        print("워크플로우 실행 시작")
        
        # 진입 차수 계산 (토폴로지 정렬을 위해)
        in_degree = {node_id: 0 for node_id in self.nodes}
        for from_node, to_nodes in self.edges.items():
            for to_node in to_nodes:
                in_degree[to_node] += 1
        
        # 진입 차수가 0인 노드들부터 시작 (의존성이 없는 프로세스들)
        ready_queue = [node_id for node_id, degree in in_degree.items() if degree == 0]
        completed = set()
        
        print(f"시작 프로세스들: {[self.nodes[nid].process_name for nid in ready_queue]}")
        
        while ready_queue or len(completed) < len(self.nodes):
            if not ready_queue:
                # 순환 의존성 또는 오류 상황
                remaining = [nid for nid in self.nodes if nid not in completed]
                print(f"경고: 실행할 수 없는 프로세스들이 남았습니다: {remaining}")
                break
            
            # 현재 실행 가능한 프로세스들을 병렬로 실행
            current_batch = ready_queue[:]
            ready_queue.clear()
            
            batch_names = [self.nodes[nid].process_name for nid in current_batch]
            print(f"배치 실행: {', '.join(batch_names)}")
            
            # 배치를 병렬로 실행
            batch_results = self._execute_batch(current_batch, input_data)
            
            # 결과 저장 및 완료 처리
            for process_id, result in batch_results.items():
                self.execution_results[process_id] = result
                completed.add(process_id)
                
                # 이 프로세스에 의존하는 프로세스들의 진입 차수 감소
                for dependent_id in self.edges.get(process_id, []):
                    in_degree[dependent_id] -= 1
                    if in_degree[dependent_id] == 0:
                        ready_queue.append(dependent_id)
        
        print("워크플로우 실행 완료")
        return self.execution_results
    
    def _execute_batch(self, process_ids: List[str], input_data: Any) -> Dict[str, ProcessResult]:
        """
        프로세스 배치를 병렬로 실행
        
        Args:
            process_ids: 실행할 프로세스 ID들
            input_data: 입력 데이터
            
        Returns:
            Dict[str, ProcessResult]: 프로세스 ID별 실행 결과
        """
        batch_results = {}
        
        def execute_process(process_id: str) -> Tuple[str, ProcessResult]:
            """단일 프로세스 실행"""
            process = self.nodes[process_id]
            start_time = time.time()
            
            try:
                print(f"[배치] {process.process_name} 실행 시작")
                result = process.execute(input_data)
                execution_time = time.time() - start_time
                print(f"[배치] {process.process_name} 완료 ({execution_time:.2f}초)")
                
                return process_id, ProcessResult(
                    process_id=process_id,
                    process_name=process.process_name,
                    success=True,
                    result_data=result,
                    execution_time=execution_time
                )
            except Exception as e:
                execution_time = time.time() - start_time
                print(f"[배치] {process.process_name} 실행 실패: {str(e)}")
                
                return process_id, ProcessResult(
                    process_id=process_id,
                    process_name=process.process_name,
                    success=False,
                    result_data=None,
                    execution_time=execution_time,
                    error_message=str(e)
                )
        
        # 배치 내 프로세스들을 병렬로 실행
        with ThreadPoolExecutor(max_workers=len(process_ids)) as executor:
            future_to_id = {
                executor.submit(execute_process, pid): pid 
                for pid in process_ids
            }
            
            for future in as_completed(future_to_id):
                process_id, result = future.result()
                batch_results[process_id] = result
        
        return batch_results
    
    def visualize_graph(self) -> str:
        """
        그래프 구조를 텍스트로 시각화
        
        Returns:
            str: 그래프 구조 텍스트
        """
        lines = ["워크플로우 그래프 구조:", "=" * 40]
        
        for process_id, process in self.nodes.items():
            dependencies = self.edges.get(process_id, [])
            if dependencies:
                dep_names = [self.nodes[dep_id].process_name for dep_id in dependencies]
                lines.append(f"{process.process_name} → {', '.join(dep_names)}")
            else:
                lines.append(f"{process.process_name} (종료 노드)")
        
        return "\n".join(lines)
