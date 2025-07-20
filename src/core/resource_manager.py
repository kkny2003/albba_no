"""
SimPy 기반 고급 자원 관리 모듈
자원 경합, 예약, 스케줄링, 우선순위 기반 할당 등을 지원하는 고급 자원 관리 시스템
"""

import simpy
from typing import Dict, List, Optional, Set, Tuple, Callable, Any, Generator
from dataclasses import dataclass, field
from enum import Enum
import uuid

from src.Resource.helper import Resource, ResourceType, ResourceRequirement


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
    start_time: float
    duration: float
    created_at: float = field(default=0.0)
    
    def __lt__(self, other):
        """우선순위 큐를 위한 비교 연산자 (높은 우선순위가 먼저)"""
        return self.priority > other.priority


@dataclass
class ResourceAllocation:
    """자원 할당 정보"""
    allocation_id: str
    resource_id: str
    requester_id: str
    allocated_amount: float
    allocation_time: float
    expected_release_time: Optional[float] = None


@dataclass
class ResourceMetrics:
    """자원 사용 메트릭 (단순화됨)"""
    resource_id: str
    total_requests: int = 0
    successful_allocations: int = 0
    average_wait_time: float = 0.0  # 핵심 메트릭만 유지


class AdvancedResourceManager:
    """SimPy 기반 고급 자원 관리자 클래스"""
    
    def __init__(self, env: simpy.Environment, strategy: AllocationStrategy = AllocationStrategy.FIFO):
        """
        고급 자원 관리자 초기화
        
        Args:
            env: SimPy 환경 객체
            strategy: 자원 할당 전략
        """
        self.env = env
        self.strategy = strategy
        
        # 자원 관리
        self.resources: Dict[str, simpy.Resource] = {}
        self.resource_metadata: Dict[str, Dict[str, Any]] = {}
        self.resource_status: Dict[str, ResourceStatus] = {}
        self.resource_metrics: Dict[str, ResourceMetrics] = {}
        
        # 예약 및 할당 관리
        self.reservations: Dict[str, ResourceReservation] = {}
        self.allocations: Dict[str, ResourceAllocation] = {}
        # wait_queues 제거: SimPy PriorityResource가 내장 큐로 자동 관리
        
        # 통계
        self.allocation_history: List[ResourceAllocation] = []
        self.total_requests = 0
        self.successful_allocations = 0
        
        # 스케줄링 관련
        self._monitoring_process = None
        
    def register_resource(self, resource_id: str, capacity: int, resource_type: ResourceType = None, **metadata):
        """
        자원을 등록합니다.
        
        Args:
            resource_id: 자원 ID
            capacity: 자원 용량
            resource_type: 자원 타입
            **metadata: 추가 메타데이터
        """
        # PriorityResource 사용으로 개선 (우선순위 기반 자원 할당 지원)
        self.resources[resource_id] = simpy.PriorityResource(self.env, capacity=capacity)
        self.resource_status[resource_id] = ResourceStatus.AVAILABLE
        self.resource_metadata[resource_id] = {
            'capacity': capacity,
            'type': resource_type,
            'description': metadata.get('description', ''),
            'properties': metadata.get('properties', {}),
            **metadata
        }
        self.resource_metrics[resource_id] = ResourceMetrics(resource_id=resource_id)
        # wait_queues 제거: SimPy PriorityResource 내장 큐 사용
        
        print(f"[시간 {self.env.now:.1f}] 고급 자원 등록 (우선순위 지원): {resource_id} (용량: {capacity}, 타입: {resource_type})")
        
    def request_resource_with_priority(self, resource_id: str, requester_id: str, 
                                     priority: int = 5, duration: float = None) -> Generator[simpy.Event, None, Optional[str]]:
        """
        우선순위를 가진 자원 요청 (SimPy PriorityResource 활용으로 개선)
        
        Args:
            resource_id: 자원 ID
            requester_id: 요청자 ID
            priority: 우선순위 (1-10, 높을수록 우선) - SimPy는 낮은 값이 높은 우선순위이므로 변환
            duration: 예상 사용 시간
            
        Yields:
            simpy.Event: SimPy 이벤트들
            
        Returns:
            Optional[str]: 할당 ID 또는 None
        """
        self.total_requests += 1
        request_time = self.env.now
        
        if resource_id not in self.resources:
            print(f"[시간 {self.env.now:.1f}] 자원 요청 실패: {resource_id} (존재하지 않는 자원)")
            return None
            
        # 메트릭 업데이트
        self.resource_metrics[resource_id].total_requests += 1
            
        print(f"[시간 {self.env.now:.1f}] 우선순위 자원 요청: {resource_id} by {requester_id} (우선순위: {priority})")
        
        # SimPy PriorityResource 우선순위 변환 (높은 값 → 낮은 값)
        simpy_priority = 10 - priority  # 사용자 우선순위 10 → SimPy 우선순위 0 (최고 우선순위)
        
        # wait_queues 제거: SimPy PriorityResource가 자동으로 우선순위 기반 큐 관리
        
        # SimPy PriorityResource를 사용한 우선순위 기반 자원 요청
        with self.resources[resource_id].request(priority=simpy_priority) as request:
            yield request
            
            # 대기 시간 계산
            wait_time = self.env.now - request_time
            
            # 할당 성공
            allocation_id = str(uuid.uuid4())
            allocation = ResourceAllocation(
                allocation_id=allocation_id,
                resource_id=resource_id,
                requester_id=requester_id,
                allocated_amount=1.0,
                allocation_time=self.env.now,
                expected_release_time=self.env.now + duration if duration else None
            )
            
            self.allocations[allocation_id] = allocation
            self.allocation_history.append(allocation)
            self.successful_allocations += 1
            
            # 메트릭 업데이트 (단순화)
            metrics = self.resource_metrics[resource_id]
            metrics.successful_allocations += 1
            metrics.average_wait_time = ((metrics.average_wait_time * (metrics.successful_allocations - 1)) + wait_time) / metrics.successful_allocations
            
            # wait_queues 제거: SimPy PriorityResource가 자동으로 큐 관리
            
            print(f"[시간 {self.env.now:.1f}] 자원 할당 완료 (우선순위 처리): {resource_id} to {requester_id} (할당 ID: {allocation_id}, 대기시간: {wait_time:.1f})")
            return allocation_id
            
    def make_reservation(self, resource_id: str, requester_id: str, start_time: float, 
                        duration: float, priority: int = 5) -> Optional[str]:
        """
        자원 예약
        
        Args:
            resource_id: 자원 ID
            requester_id: 요청자 ID
            start_time: 시작 시간
            duration: 사용 시간
            priority: 우선순위
            
        Returns:
            Optional[str]: 예약 ID 또는 None
        """
        if resource_id not in self.resources:
            return None
            
        reservation_id = str(uuid.uuid4())
        reservation = ResourceReservation(
            reservation_id=reservation_id,
            resource_id=resource_id,
            requester_id=requester_id,
            priority=priority,
            start_time=start_time,
            duration=duration,
            created_at=self.env.now
        )
        
        self.reservations[reservation_id] = reservation
        print(f"[시간 {self.env.now:.1f}] 자원 예약: {resource_id} by {requester_id} (예약 ID: {reservation_id})")
        return reservation_id
        
    def cancel_reservation(self, reservation_id: str) -> bool:
        """
        예약 취소
        
        Args:
            reservation_id: 예약 ID
            
        Returns:
            bool: 취소 성공 여부
        """
        if reservation_id in self.reservations:
            reservation = self.reservations[reservation_id]
            del self.reservations[reservation_id]
            print(f"[시간 {self.env.now:.1f}] 예약 취소: {reservation.resource_id} (예약 ID: {reservation_id})")
            return True
        return False
        
    def get_resource_utilization(self, resource_id: str) -> float:
        """
        자원 가동률 계산 (필요시에만 계산하는 방식으로 개선)
        
        Args:
            resource_id: 자원 ID
            
        Returns:
            float: 가동률 (0.0 ~ 1.0)
        """
        if resource_id not in self.resources or self.env.now == 0:
            return 0.0
            
        resource = self.resources[resource_id]
        capacity = self.resource_metadata[resource_id]['capacity']
        
        if capacity == 0:
            return 0.0
            
        # 실시간 계산 (메트릭 저장 제거로 단순화)
        return len(resource.users) / capacity
        
    def get_statistics(self) -> Dict[str, Any]:
        """
        자원 관리 통계 반환
        
        Returns:
            Dict[str, Any]: 통계 정보
        """
        success_rate = (self.successful_allocations / self.total_requests * 100) if self.total_requests > 0 else 0
        
        # 전체 가동률 계산
        total_utilization = 0.0
        if self.resources:
            total_utilization = sum(self.get_resource_utilization(rid) for rid in self.resources) / len(self.resources)
        
        return {
            'simulation_time': self.env.now,
            'total_requests': self.total_requests,
            'successful_allocations': self.successful_allocations,
            'success_rate': success_rate,
            'active_allocations': len(self.allocations),
            'total_reservations': len(self.reservations),
            'resource_count': len(self.resources),
            'average_utilization': total_utilization,
            'strategy': self.strategy.value
        }
        
    def get_all_resource_status(self) -> Dict[str, Dict[str, Any]]:
        """
        모든 자원의 상태 반환
        
        Returns:
            Dict[str, Dict[str, Any]]: 자원별 상태 정보
        """
        status = {}
        for resource_id in self.resources:
            resource = self.resources[resource_id]
            metadata = self.resource_metadata[resource_id]
            metrics = self.resource_metrics[resource_id]
            
            status[resource_id] = {
                'resource_id': resource_id,
                'status': self.resource_status[resource_id].value,
                'capacity': metadata['capacity'],
                'current_users': len(resource.users),
                'queue_length': len(resource.queue),
                'utilization': self.get_resource_utilization(resource_id),
                # wait_queue_length 제거: SimPy queue 사용
                'total_requests': metrics.total_requests,
                'successful_allocations': metrics.successful_allocations,
                'average_wait_time': metrics.average_wait_time,
                'metadata': metadata
            }
            
        return status
        
    def start_monitoring(self, update_interval: float = 10.0):
        """
        자원 모니터링 프로세스 시작
        
        Args:
            update_interval: 업데이트 간격
        """
        if self._monitoring_process is None:
            self._monitoring_process = self.env.process(self._monitoring_loop(update_interval))
            print(f"[시간 {self.env.now:.1f}] 자원 모니터링 시작 (간격: {update_interval}초)")
            
    def _monitoring_loop(self, update_interval: float) -> Generator[simpy.Event, None, None]:
        """
        모니터링 루프 (내부 사용)
        
        Args:
            update_interval: 업데이트 간격
            
        Yields:
            simpy.Event: SimPy 이벤트들
        """
        while True:
            yield self.env.timeout(update_interval)
            
            # 자원 상태 업데이트
            for resource_id in self.resources:
                self.get_resource_utilization(resource_id)  # 가동률 업데이트
                
            # 예약된 자원 확인 및 처리
            current_time = self.env.now
            for reservation_id, reservation in list(self.reservations.items()):
                if current_time >= reservation.start_time:
                    # 예약 시간이 되었으므로 자원 우선 할당 처리
                    print(f"[시간 {self.env.now:.1f}] 예약 시간 도달: {reservation.resource_id} (예약 ID: {reservation_id})")
                    
    def set_resource_status(self, resource_id: str, status: ResourceStatus):
        """
        자원 상태 설정
        
        Args:
            resource_id: 자원 ID
            status: 새로운 상태
        """
        if resource_id in self.resource_status:
            old_status = self.resource_status[resource_id]
            self.resource_status[resource_id] = status
            print(f"[시간 {self.env.now:.1f}] 자원 상태 변경: {resource_id} ({old_status.value} -> {status.value})")
            
    def get_resource_queue_info(self, resource_id: str) -> Dict[str, Any]:
        """
        특정 자원의 대기열 정보 반환
        
        Args:
            resource_id: 자원 ID
            
        Returns:
            Dict[str, Any]: 대기열 정보
        """
        if resource_id not in self.resources:
            return {}
            
        resource = self.resources[resource_id]
        # wait_queue 제거: SimPy 내장 큐 정보만 제공
        
        return {
            'resource_id': resource_id,
            'simpy_queue_length': len(resource.queue),
            # priority_queue 관련 정보는 SimPy 내장 큐에서 관리되므로 제거
        }
    
    def get_resource_status(self, resource_id: str = None):
        """
        자원 상태 조회
        
        Args:
            resource_id: 특정 자원 ID (None이면 모든 자원)
            
        Returns:
            Dict: 자원 상태 정보
        """
        if resource_id:
            if resource_id not in self.resources:
                return {'error': f'Resource {resource_id} not found'}
            
            resource = self.resources[resource_id]
            return {
                'resource_id': resource_id,
                'status': self.resource_status[resource_id],
                'capacity': resource.capacity,
                'in_use': resource.count,
                'available': resource.capacity - resource.count,
                'queue_length': len(resource.queue),
                'metadata': self.resource_metadata.get(resource_id, {})
            }
        else:
            # 모든 자원 상태 반환
            all_status = {}
            for rid in self.resources:
                resource = self.resources[rid]
                all_status[rid] = {
                    'status': self.resource_status[rid],
                    'capacity': resource.capacity,
                    'in_use': resource.count,
                    'available': resource.capacity - resource.count,
                    'queue_length': len(resource.queue)
                }
            return all_status
    
    def calculate_utilization(self):
        """
        자원 활용률 계산
        
        Returns:
            Dict: 활용률 정보
        """
        if not self.resources:
            return {'error': 'No resources registered'}
        
        utilization_data = {}
        total_utilization = 0
        
        for resource_id, resource in self.resources.items():
            if resource.capacity > 0:
                utilization = resource.count / resource.capacity
                utilization_data[resource_id] = {
                    'utilization_rate': utilization,
                    'in_use': resource.count,
                    'capacity': resource.capacity,
                    'percentage': utilization * 100
                }
                total_utilization += utilization
        
        if len(self.resources) > 0:
            average_utilization = total_utilization / len(self.resources)
        else:
            average_utilization = 0
        
        return {
            'individual_utilization': utilization_data,
            'average_utilization': average_utilization,
            'average_percentage': average_utilization * 100,
            'total_resources': len(self.resources)
        }
