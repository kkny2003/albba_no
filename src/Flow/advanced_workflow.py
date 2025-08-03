"""
SimPy 기반 고급 워크플로우 관리 모듈
병렬 공정, 동기화, 조건부 분기 등을 지원하는 확장된 워크플로우 관리 기능을 제공합니다.
"""

import simpy
from typing import List, Dict, Any, Callable, Optional, Set, Tuple, Generator
from enum import Enum
from dataclasses import dataclass
import uuid
from src.Processes.base_process import BaseProcess
from .process_chain import ProcessChain
from .multi_process_group import MultiProcessGroup


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
    start_time: float
    end_time: float
    error_message: Optional[str] = None


@dataclass
class SynchronizationPoint:
    """동기화 포인트 정의 (SimPy Event 기반으로 단순화)"""
    sync_id: str
    sync_type: SynchronizationType
    threshold: int = 1  # THRESHOLD 타입일 때 필요한 완료 개수
    timeout: Optional[float] = None  # 타임아웃 (초)
    events: List[simpy.Event] = None  # SimPy Event 리스트로 직접 관리


class AdvancedWorkflowManager:
    """SimPy 기반 고급 워크플로우 관리자"""
    
    def __init__(self, env: simpy.Environment, max_workers: int = 4):
        """
        고급 워크플로우 관리자 초기화
        
        Args:
            env: SimPy 환경 객체
            max_workers: 최대 동시 실행 프로세스 수
        """
        self.env = env
        self.max_workers = max_workers
        
        # 프로세스 관리 (BaseProcess 타입 체크를 위해 typing.TYPE_CHECKING 사용하지 않음)
        self.processes: Dict[str, Any] = {}  # BaseProcess 객체들
        self.process_chains: Dict[str, Any] = {}  # ProcessChain 객체들
        self.execution_results: Dict[str, ProcessResult] = {}
        
        # 동기화 관리 (SimPy Event 기반으로 단순화)
        self.sync_points: Dict[str, SynchronizationPoint] = {}
        # sync_events, sync_results 제거: SimPy Event 직접 사용
        
        # 워크플로우 상태
        self.active_workflows: Set[str] = set()
        self.completed_workflows: Set[str] = set()
        
        # 리소스 제한
        self.worker_pool = simpy.Resource(env, capacity=max_workers)
        
    def register_process(self, process):
        """
        프로세스를 등록합니다.
        
        Args:
            process: 등록할 프로세스 (BaseProcess 객체)
        """
        self.processes[process.process_id] = process
        print(f"[시간 {self.env.now:.1f}] 프로세스 등록: {process.process_id} ({process.process_name})")
        
    def register_process_chain(self, chain):
        """
        프로세스 체인을 등록합니다.
        
        Args:
            chain: 등록할 프로세스 체인 (ProcessChain 객체)
        """
        self.process_chains[chain.chain_id] = chain
        print(f"[시간 {self.env.now:.1f}] 프로세스 체인 등록: {chain.chain_id}")
        
    def simple_sync(self, events: List[simpy.Event], sync_type: SynchronizationType = SynchronizationType.ALL_COMPLETE) -> Generator[simpy.Event, None, None]:
        """
        간단한 동기화 기능 (SimPy Event 기반)
        
        Args:
            events: 동기화할 이벤트 리스트
            sync_type: 동기화 타입
            
        Yields:
            simpy.Event: 동기화 완료 이벤트
        """
        if not events:
            return
            
        if sync_type == SynchronizationType.ALL_COMPLETE:
            # 모든 이벤트 완료 대기
            yield simpy.AllOf(self.env, events)
        elif sync_type == SynchronizationType.ANY_COMPLETE:
            # 하나의 이벤트 완료 대기
            yield simpy.AnyOf(self.env, events)
        elif sync_type == SynchronizationType.THRESHOLD:
            # 임계값만큼 완료 대기 (복잡하므로 간단히 구현)
            completed_count = 0
            threshold = min(len(events), 1)  # 기본값 1
            
            def check_completion():
                nonlocal completed_count
                completed_count += 1
                return completed_count >= threshold
                
            def monitor_event(event):
                try:
                    yield event
                    if check_completion():
                        return
                except:
                    pass
                    
            # 모든 이벤트 모니터링
            yield simpy.AllOf(self.env, [monitor_event(event) for event in events])
        
    def get_workflow_statistics(self) -> Dict[str, Any]:
        """
        워크플로우 통계 정보를 반환합니다.
        
        Returns:
            Dict[str, Any]: 통계 정보
        """
        total_processes = len(self.processes)
        total_chains = len(self.process_chains)
        active_workflows = len(self.active_workflows)
        completed_workflows = len(self.completed_workflows)
        
        # 실행 결과 통계
        successful_executions = sum(1 for result in self.execution_results.values() if result.success)
        failed_executions = len(self.execution_results) - successful_executions
        
        return {
            'total_processes': total_processes,
            'total_chains': total_chains,
            'active_workflows': active_workflows,
            'completed_workflows': completed_workflows,
            'successful_executions': successful_executions,
            'failed_executions': failed_executions,
            'execution_results': len(self.execution_results)
        }
        
    def execute_workflow(self, product, workflow_steps):
        """
        워크플로우를 실행합니다.
        
        Args:
            product: 처리할 제품
            workflow_steps: 워크플로우 단계들
            
        Returns:
            Generator: 워크플로우 실행 제너레이터
        """
        def workflow_process():
            print(f"[시간 {self.env.now:.1f}] 워크플로우 실행 시작")
            
            # 워크플로우 단계별 실행
            for step in workflow_steps:
                if hasattr(step, 'execute'):
                    result = yield from step.execute(product)
                    print(f"[시간 {self.env.now:.1f}] 워크플로우 단계 완료: {step.process_name}")
                else:
                    print(f"[시간 {self.env.now:.1f}] 워크플로우 단계 건너뜀: {step}")
                    
            print(f"[시간 {self.env.now:.1f}] 워크플로우 실행 완료")
            
        return workflow_process()
