"""
SimPy 기반 고급 워크플로우 관리 모듈
병렬 공정, 동기화, 조건부 분기 등을 지원하는 확장된 워크플로우 관리 기능을 제공합니다.
"""

import simpy
from typing import List, Dict, Any, Callable, Optional, Set, Tuple, Generator
from enum import Enum
from dataclasses import dataclass
import uuid


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
        SimPy 내장 기능을 활용한 간단한 동기화 (복잡한 동기화 시스템 대체)
        
        Args:
            events: 동기화할 이벤트 리스트
            sync_type: 동기화 타입
            
        Yields:
            simpy.Event: SimPy 이벤트들
        """
        if sync_type == SynchronizationType.ALL_COMPLETE:
            # SimPy AllOf 사용: 모든 이벤트 완료 대기
            yield simpy.AllOf(self.env, events)
        elif sync_type == SynchronizationType.ANY_COMPLETE:
            # SimPy AnyOf 사용: 하나의 이벤트만 완료되면 진행
            yield simpy.AnyOf(self.env, events)
        else:  # THRESHOLD
            # 임계값 만큼의 이벤트 완료 대기 (SimPy Condition 활용)
            completed_count = 0
            threshold = len(events) // 2  # 예시: 절반 완료
            
            def check_completion():
                return completed_count >= threshold
                
            condition = simpy.Condition(self.env)
            
            # 각 이벤트 완료 시 카운터 증가
            def monitor_event(event):
                nonlocal completed_count
                yield event
                completed_count += 1
                if check_completion():
                    condition.succeed()
                    
            for event in events:
                self.env.process(monitor_event(event))
                
            yield condition
            
        print(f"[시간 {self.env.now:.1f}] 동기화 완료: {sync_type.value}")
        
    def get_workflow_statistics(self) -> Dict[str, Any]:
        """
        워크플로우 통계 반환
        
        Returns:
            Dict[str, Any]: 통계 정보
        """
        total_results = len(self.execution_results)
        successful_results = sum(1 for result in self.execution_results.values() if result.success)
        
        return {
            'simulation_time': self.env.now,
            'total_workflows': len(self.completed_workflows) + len(self.active_workflows),
            'active_workflows': len(self.active_workflows),
            'completed_workflows': len(self.completed_workflows),
            'total_process_executions': total_results,
            'successful_executions': successful_results,
            'success_rate': (successful_results / total_results * 100) if total_results > 0 else 0,
            'worker_pool_capacity': self.worker_pool.capacity,
            'worker_pool_usage': len(self.worker_pool.users),
            'sync_points': len(self.sync_points)
        }
    
    def execute_workflow(self, product, workflow_steps):
        """
        워크플로우 실행
        
        Args:
            product: 처리할 제품 객체
            workflow_steps: 워크플로우 단계 리스트
        """
        workflow_id = f"workflow_{uuid.uuid4().hex[:8]}"
        self.active_workflows.add(workflow_id)
        
        def workflow_process():
            try:
                for step in workflow_steps:
                    step_name = step['name']
                    duration = step['duration']
                    
                    print(f"[시간 {self.env.now:.1f}] {product.product_id} - {step_name} 시작")
                    
                    # 워커 풀에서 리소스 요청
                    with self.worker_pool.request() as request:
                        yield request
                        
                        # 작업 시간만큼 대기
                        yield self.env.timeout(duration)
                        
                        print(f"[시간 {self.env.now:.1f}] {product.product_id} - {step_name} 완료")
                
                # 워크플로우 완료
                self.active_workflows.remove(workflow_id)
                self.completed_workflows.add(workflow_id)
                
            except Exception as e:
                print(f"[오류] 워크플로우 실행 중 오류 발생: {e}")
                if workflow_id in self.active_workflows:
                    self.active_workflows.remove(workflow_id)
        
        return self.env.process(workflow_process())
