"""
고급 자원 관리 모듈
자원 경합, 예약, 스케줄링, 우선순위 기반 할당 등을 지원하는 고급 자원 관리 시스템
"""

import threading
import time
from concurrent.futures import ThreadPoolExecutor
from typing import Dict, List, Optional, Set, Tuple, Callable, Any
from dataclasses import dataclass, field
from enum import Enum
from queue import PriorityQueue, Queue
import uuid
from datetime import datetime, timedelta

from ..Resource.helper import Resource, ResourceType, ResourceRequirement


class ResourceStatus(Enum):
    """자원 상태 열거형"""
    AVAILABLE = "available"      # 사용 가능
    RESERVED = "reserved"        # 예약됨
    IN_USE = "in_use"           # 사용 중
    MAINTENANCE = "maintenance"  # 유지보수 중
    UNAVAILABLE = "unavailable" # 사용 불가


class AllocationStrategy(Enum):
    """자원 할당 전략 열거형"""
    FIFO = "fifo"                    # 선입선출
    PRIORITY = "priority"            # 우선순위 기반
    SHORTEST_JOB_FIRST = "sjf"       # 최단 작업 우선
    ROUND_ROBIN = "round_robin"      # 라운드 로빈


@dataclass
class ResourceReservation:
    """자원 예약 정보"""
    reservation_id: str
    resource_id: str
    requester_id: str
    priority: int
    start_time: datetime
    duration: timedelta
    created_at: datetime = field(default_factory=datetime.now)
    
    def __lt__(self, other):
        """우선순위 큐를 위한 비교 연산자 (높은 우선순위가 먼저)"""
        return self.priority > other.priority


@dataclass
class ResourceAllocation:
    """자원 할당 정보"""
    allocation_id: str
    resource_id: str
    process_id: str
    allocated_at: datetime
    expected_release_at: Optional[datetime] = None
    actual_release_at: Optional[datetime] = None


@dataclass
class ResourceMetrics:
    """자원 성능 지표"""
    resource_id: str
    total_requests: int = 0
    successful_allocations: int = 0
    failed_allocations: int = 0
    total_usage_time: float = 0.0
    average_wait_time: float = 0.0
    utilization_rate: float = 0.0
    last_updated: datetime = field(default_factory=datetime.now)


class AdvancedResourceManager:
    """고급 자원 관리자 클래스"""
    
    def __init__(self, allocation_strategy: AllocationStrategy = AllocationStrategy.PRIORITY):
        """
        고급 자원 관리자 초기화
        
        Args:
            allocation_strategy: 자원 할당 전략
        """
        self.allocation_strategy = allocation_strategy
        
        # 자원 관련 데이터 구조
        self.resources: Dict[str, Resource] = {}                    # 자원 정보
        self.resource_status: Dict[str, ResourceStatus] = {}        # 자원 상태
        self.resource_capacities: Dict[str, float] = {}             # 자원 용량
        self.resource_current_usage: Dict[str, float] = {}          # 현재 사용량
        
        # 예약 및 할당 관련
        self.reservations: Dict[str, ResourceReservation] = {}      # 예약 정보
        self.active_allocations: Dict[str, ResourceAllocation] = {} # 활성 할당
        self.allocation_history: List[ResourceAllocation] = []      # 할당 이력
        
        # 대기열 관리
        self.wait_queues: Dict[str, PriorityQueue] = {}            # 자원별 대기열
        self.process_wait_times: Dict[str, float] = {}             # 프로세스별 대기 시간
        
        # 성능 지표
        self.resource_metrics: Dict[str, ResourceMetrics] = {}     # 자원별 성능 지표
        
        # 스레딩 관련
        self._lock = threading.RLock()                             # 스레드 안전성을 위한 락
        self._resource_locks: Dict[str, threading.Lock] = {}       # 자원별 락
        
        # 스케줄러
        self._scheduler_running = False
        self._scheduler_thread: Optional[threading.Thread] = None
        
        print(f"고급 자원 관리자 초기화 완료 (할당 전략: {allocation_strategy.value})")
    
    def register_resource(self, resource: Resource, capacity: float = 1.0) -> None:
        """
        자원을 시스템에 등록
        
        Args:
            resource: 등록할 자원
            capacity: 자원 용량 (동시 사용 가능한 양)
        """
        with self._lock:
            self.resources[resource.resource_id] = resource
            self.resource_status[resource.resource_id] = ResourceStatus.AVAILABLE
            self.resource_capacities[resource.resource_id] = capacity
            self.resource_current_usage[resource.resource_id] = 0.0
            
            # 대기열 및 락 초기화
            self.wait_queues[resource.resource_id] = PriorityQueue()
            self._resource_locks[resource.resource_id] = threading.Lock()
            
            # 성능 지표 초기화
            self.resource_metrics[resource.resource_id] = ResourceMetrics(
                resource_id=resource.resource_id
            )
            
            print(f"자원 등록: {resource.name} (용량: {capacity}, ID: {resource.resource_id})")
    
    def request_resource(self, resource_id: str, process_id: str, 
                        required_amount: float = 1.0, priority: int = 5,
                        max_wait_time: Optional[float] = None) -> Optional[str]:
        """
        자원 요청 (차단 방식)
        
        Args:
            resource_id: 요청할 자원 ID
            process_id: 요청하는 프로세스 ID
            required_amount: 필요한 자원 양
            priority: 우선순위 (1-10, 높을수록 우선)
            max_wait_time: 최대 대기 시간 (초)
            
        Returns:
            Optional[str]: 할당 ID (실패시 None)
        """
        start_time = time.time()
        
        with self._lock:
            # 자원 존재 확인
            if resource_id not in self.resources:
                print(f"자원 요청 실패: 존재하지 않는 자원 ID {resource_id}")
                return None
            
            # 메트릭 업데이트
            metrics = self.resource_metrics[resource_id]
            metrics.total_requests += 1
            
            print(f"자원 요청: {self.resources[resource_id].name} "
                  f"(프로세스: {process_id}, 필요량: {required_amount}, 우선순위: {priority})")
        
        # 자원 할당 시도
        allocation_id = self._try_allocate_resource(
            resource_id, process_id, required_amount, priority, max_wait_time
        )
        
        # 대기 시간 기록
        wait_time = time.time() - start_time
        self.process_wait_times[process_id] = wait_time
        
        with self._lock:
            metrics = self.resource_metrics[resource_id]
            if allocation_id:
                metrics.successful_allocations += 1
                print(f"자원 할당 성공: {allocation_id} (대기 시간: {wait_time:.2f}초)")
            else:
                metrics.failed_allocations += 1
                print(f"자원 할당 실패: {resource_id} (대기 시간: {wait_time:.2f}초)")
            
            # 평균 대기 시간 업데이트
            total_allocations = metrics.successful_allocations + metrics.failed_allocations
            if total_allocations > 0:
                metrics.average_wait_time = (
                    (metrics.average_wait_time * (total_allocations - 1) + wait_time) / total_allocations
                )
        
        return allocation_id
    
    def _try_allocate_resource(self, resource_id: str, process_id: str, 
                              required_amount: float, priority: int,
                              max_wait_time: Optional[float]) -> Optional[str]:
        """
        자원 할당 시도 (내부 메서드)
        
        Args:
            resource_id: 자원 ID
            process_id: 프로세스 ID
            required_amount: 필요한 양
            priority: 우선순위
            max_wait_time: 최대 대기 시간
            
        Returns:
            Optional[str]: 할당 ID
        """
        resource_lock = self._resource_locks[resource_id]
        start_wait_time = time.time()
        
        while True:
            with resource_lock:
                # 자원 가용성 확인
                if self._is_resource_available(resource_id, required_amount):
                    # 즉시 할당 가능
                    allocation_id = self._allocate_resource_immediately(
                        resource_id, process_id, required_amount
                    )
                    return allocation_id
            
            # 대기 시간 초과 확인
            if max_wait_time and (time.time() - start_wait_time) > max_wait_time:
                print(f"자원 할당 타임아웃: {resource_id} (최대 대기 시간 {max_wait_time}초 초과)")
                return None
            
            # 대기열에 추가하고 잠시 대기
            self._add_to_wait_queue(resource_id, process_id, required_amount, priority)
            time.sleep(0.1)  # 짧은 대기 후 재시도
    
    def _is_resource_available(self, resource_id: str, required_amount: float) -> bool:
        """
        자원 가용성 확인
        
        Args:
            resource_id: 자원 ID
            required_amount: 필요한 양
            
        Returns:
            bool: 사용 가능 여부
        """
        if self.resource_status[resource_id] != ResourceStatus.AVAILABLE:
            return False
        
        capacity = self.resource_capacities[resource_id]
        current_usage = self.resource_current_usage[resource_id]
        
        return (current_usage + required_amount) <= capacity
    
    def _allocate_resource_immediately(self, resource_id: str, process_id: str, 
                                     required_amount: float) -> str:
        """
        자원 즉시 할당
        
        Args:
            resource_id: 자원 ID
            process_id: 프로세스 ID
            required_amount: 필요한 양
            
        Returns:
            str: 할당 ID
        """
        allocation_id = str(uuid.uuid4())
        
        # 할당 정보 생성
        allocation = ResourceAllocation(
            allocation_id=allocation_id,
            resource_id=resource_id,
            process_id=process_id,
            allocated_at=datetime.now()
        )
        
        # 상태 업데이트
        self.active_allocations[allocation_id] = allocation
        self.resource_current_usage[resource_id] += required_amount
        
        # 용량이 모두 사용되면 상태를 IN_USE로 변경
        if self.resource_current_usage[resource_id] >= self.resource_capacities[resource_id]:
            self.resource_status[resource_id] = ResourceStatus.IN_USE
        
        return allocation_id
    
    def _add_to_wait_queue(self, resource_id: str, process_id: str, 
                          required_amount: float, priority: int) -> None:
        """
        대기열에 프로세스 추가
        
        Args:
            resource_id: 자원 ID
            process_id: 프로세스 ID
            required_amount: 필요한 양
            priority: 우선순위
        """
        wait_item = (priority, process_id, required_amount, time.time())
        self.wait_queues[resource_id].put(wait_item)
    
    def release_resource(self, allocation_id: str) -> bool:
        """
        자원 해제
        
        Args:
            allocation_id: 할당 ID
            
        Returns:
            bool: 해제 성공 여부
        """
        with self._lock:
            if allocation_id not in self.active_allocations:
                print(f"자원 해제 실패: 존재하지 않는 할당 ID {allocation_id}")
                return False
            
            allocation = self.active_allocations[allocation_id]
            resource_id = allocation.resource_id
            
            # 할당 정보 업데이트
            allocation.actual_release_at = datetime.now()
            
            # 사용량 감소
            # 여기서는 단순화를 위해 1.0으로 가정 (실제로는 할당시 양을 저장해야 함)
            self.resource_current_usage[resource_id] -= 1.0
            if self.resource_current_usage[resource_id] < 0:
                self.resource_current_usage[resource_id] = 0.0
            
            # 상태 업데이트
            if self.resource_current_usage[resource_id] < self.resource_capacities[resource_id]:
                self.resource_status[resource_id] = ResourceStatus.AVAILABLE
            
            # 할당 이력으로 이동
            self.allocation_history.append(allocation)
            del self.active_allocations[allocation_id]
            
            # 성능 지표 업데이트
            usage_duration = (allocation.actual_release_at - allocation.allocated_at).total_seconds()
            metrics = self.resource_metrics[resource_id]
            metrics.total_usage_time += usage_duration
            
            resource_name = self.resources[resource_id].name
            print(f"자원 해제: {resource_name} (할당 ID: {allocation_id}, 사용 시간: {usage_duration:.2f}초)")
            
            # 대기 중인 프로세스들 처리
            self._process_wait_queue(resource_id)
            
            return True
    
    def _process_wait_queue(self, resource_id: str) -> None:
        """
        대기열 처리 (자원 해제 후 호출)
        
        Args:
            resource_id: 자원 ID
        """
        wait_queue = self.wait_queues[resource_id]
        
        while not wait_queue.empty():
            try:
                priority, process_id, required_amount, wait_start_time = wait_queue.get_nowait()
                
                if self._is_resource_available(resource_id, required_amount):
                    # 대기 중인 프로세스에 자원 할당
                    allocation_id = self._allocate_resource_immediately(
                        resource_id, process_id, required_amount
                    )
                    
                    wait_time = time.time() - wait_start_time
                    print(f"대기열에서 자원 할당: {process_id} (대기 시간: {wait_time:.2f}초)")
                    break
                else:
                    # 아직 할당할 수 없으면 다시 대기열에 추가
                    wait_queue.put((priority, process_id, required_amount, wait_start_time))
                    break
                    
            except:
                break
    
    def get_resource_status(self, resource_id: str) -> Dict[str, Any]:
        """
        자원 상태 정보 반환
        
        Args:
            resource_id: 자원 ID
            
        Returns:
            Dict[str, Any]: 자원 상태 정보
        """
        with self._lock:
            if resource_id not in self.resources:
                return {}
            
            resource = self.resources[resource_id]
            metrics = self.resource_metrics[resource_id]
            
            return {
                'resource_id': resource_id,
                'name': resource.name,
                'type': resource.resource_type.value,
                'status': self.resource_status[resource_id].value,
                'capacity': self.resource_capacities[resource_id],
                'current_usage': self.resource_current_usage[resource_id],
                'utilization_rate': (self.resource_current_usage[resource_id] / 
                                   self.resource_capacities[resource_id]) * 100,
                'wait_queue_size': self.wait_queues[resource_id].qsize(),
                'total_requests': metrics.total_requests,
                'successful_allocations': metrics.successful_allocations,
                'failed_allocations': metrics.failed_allocations,
                'average_wait_time': metrics.average_wait_time,
                'total_usage_time': metrics.total_usage_time
            }
    
    def get_system_status(self) -> Dict[str, Any]:
        """
        전체 시스템 상태 반환
        
        Returns:
            Dict[str, Any]: 시스템 상태 정보
        """
        with self._lock:
            total_resources = len(self.resources)
            available_resources = sum(1 for status in self.resource_status.values() 
                                    if status == ResourceStatus.AVAILABLE)
            active_allocations = len(self.active_allocations)
            total_wait_queue_size = sum(queue.qsize() for queue in self.wait_queues.values())
            
            return {
                'total_resources': total_resources,
                'available_resources': available_resources,
                'busy_resources': total_resources - available_resources,
                'active_allocations': active_allocations,
                'total_wait_queue_size': total_wait_queue_size,
                'allocation_strategy': self.allocation_strategy.value,
                'total_allocation_history': len(self.allocation_history)
            }
    
    def start_resource_monitor(self, monitor_interval: float = 1.0) -> None:
        """
        자원 모니터링 스레드 시작
        
        Args:
            monitor_interval: 모니터링 간격 (초)
        """
        if self._scheduler_running:
            print("자원 모니터가 이미 실행 중입니다.")
            return
        
        self._scheduler_running = True
        
        def monitor_loop():
            """모니터링 루프"""
            while self._scheduler_running:
                try:
                    # 각 자원의 활용률 계산
                    with self._lock:
                        for resource_id in self.resources:
                            metrics = self.resource_metrics[resource_id]
                            capacity = self.resource_capacities[resource_id]
                            current_usage = self.resource_current_usage[resource_id]
                            
                            if capacity > 0:
                                metrics.utilization_rate = (current_usage / capacity) * 100
                            
                            metrics.last_updated = datetime.now()
                    
                    time.sleep(monitor_interval)
                    
                except Exception as e:
                    print(f"자원 모니터링 오류: {e}")
                    time.sleep(monitor_interval)
        
        self._scheduler_thread = threading.Thread(target=monitor_loop, daemon=True)
        self._scheduler_thread.start()
        print(f"자원 모니터링 시작 (간격: {monitor_interval}초)")
    
    def stop_resource_monitor(self) -> None:
        """자원 모니터링 스레드 중지"""
        if self._scheduler_running:
            self._scheduler_running = False
            if self._scheduler_thread:
                self._scheduler_thread.join()
            print("자원 모니터링 중지")
    
    def print_status_report(self) -> None:
        """상태 리포트 출력"""
        print("\n" + "=" * 60)
        print("고급 자원 관리자 상태 리포트")
        print("=" * 60)
        
        # 시스템 전체 상태
        system_status = self.get_system_status()
        print(f"전체 자원 수: {system_status['total_resources']}")
        print(f"사용 가능한 자원: {system_status['available_resources']}")
        print(f"사용 중인 자원: {system_status['busy_resources']}")
        print(f"활성 할당 수: {system_status['active_allocations']}")
        print(f"대기열 총 크기: {system_status['total_wait_queue_size']}")
        
        print(f"\n개별 자원 상태:")
        print("-" * 60)
        
        # 개별 자원 상태
        for resource_id in self.resources:
            status = self.get_resource_status(resource_id)
            print(f"• {status['name']} ({status['type']})")
            print(f"  상태: {status['status']}")
            print(f"  활용률: {status['utilization_rate']:.1f}%")
            print(f"  요청 수: {status['total_requests']} (성공: {status['successful_allocations']}, 실패: {status['failed_allocations']})")
            print(f"  평균 대기 시간: {status['average_wait_time']:.2f}초")
            print(f"  대기열 크기: {status['wait_queue_size']}")
            print()
        
        print("=" * 60)
