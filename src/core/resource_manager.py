"""
SimPy 기반 고급 자원 관리 모듈
자원 경합, 예약, 스케줄링, 우선순위 기반 할당 등을 지원하는 고급 자원 관리 시스템
"""

import simpy
from typing import Dict, List, Optional, Set, Tuple, Callable, Any, Generator
from dataclasses import dataclass, field
from enum import Enum
import uuid

from src.Resource.resource_base import Resource, ResourceType, ResourceRequirement
from src.core.centralized_statistics import CentralizedStatisticsManager, StatisticsInterface


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
    
    def __init__(self, env: simpy.Environment, strategy: AllocationStrategy = AllocationStrategy.FIFO,
                 stats_manager: Optional[CentralizedStatisticsManager] = None):
        """
        고급 자원 관리자 초기화
        
        Args:
            env: SimPy 환경 객체
            strategy: 자원 할당 전략
            stats_manager: 중앙 통계 관리자 (선택적)
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
        
        # 통계 (하위 호환성)
        self.allocation_history: List[ResourceAllocation] = []
        self.total_requests = 0
        self.successful_allocations = 0
        
        # 중앙 집중식 통계 관리
        self.stats_manager = stats_manager
        self.stats_interface = None
        
        if stats_manager:
            self.stats_interface = StatisticsInterface(
                component_id="advanced_resource_manager",
                component_type="resource_manager", 
                stats_manager=stats_manager
            )
        
        # Transport 완료 이벤트 관리 시스템
        self.transport_completion_events: Dict[str, simpy.Event] = {}  # allocation_id -> Event 매핑
        self.transport_requester_map: Dict[str, str] = {}  # allocation_id -> requester_id 매핑
        
        # 스케줄링 관련
        self._monitoring_process = None
        
        # TransportProcess 관리
        self.transport_processes: Dict[str, Any] = {}  # transport_id -> TransportProcess 매핑
        self.transport_queue: List[Dict[str, Any]] = []  # 운송 요청 대기열
        
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
        
    def register_transport_process(self, transport_id: str, transport_process):
        """
        TransportProcess를 ResourceManager에 등록
        
        Args:
            transport_id: Transport 식별자
            transport_process: TransportProcess 인스턴스
        """
        self.transport_processes[transport_id] = transport_process
        print(f"[시간 {self.env.now:.1f}] TransportProcess 등록: {transport_id} (프로세스 ID: {transport_process.process_id})")
        
    def unregister_transport_process(self, transport_id: str):
        """
        TransportProcess 등록 해제
        
        Args:
            transport_id: Transport 식별자
        """
        if transport_id in self.transport_processes:
            del self.transport_processes[transport_id]
            print(f"[시간 {self.env.now:.1f}] TransportProcess 등록 해제: {transport_id}")
            return True
        return False
        
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
            # 중앙 통계 관리자에 기록
            if self.stats_interface:
                self.stats_interface.record_counter("failed_requests")
            return None
            
        # 메트릭 업데이트
        self.resource_metrics[resource_id].total_requests += 1
        
        # 중앙 통계 관리자에 기록
        if self.stats_interface:
            self.stats_interface.record_counter("total_requests")
            
        print(f"[시간 {self.env.now:.1f}] 우선순위 자원 요청: {resource_id} by {requester_id} (우선순위: {priority})")
        
        # Transport 자원 요청의 경우 특별 처리
        if resource_id == "transport":
            allocation_id = yield from self._handle_transport_request(requester_id, priority, request_time)
            return allocation_id
        
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
            
            # 중앙 통계 관리자에 기록
            if self.stats_interface:
                self.stats_interface.record_counter("successful_allocations")
                self.stats_interface.record_histogram("waiting_time", wait_time)
                self.stats_interface.record_gauge("utilization", self.get_resource_utilization(resource_id) * 100)
            
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
        # 중앙 통계 관리자 사용 시 표준화된 통계 반환
        if self.stats_interface:
            centralized_stats = self.stats_interface.get_statistics()
            # 하위 호환성을 위한 기존 형식 포함
            legacy_stats = self._get_legacy_statistics()
            
            return {
                **legacy_stats,  # 기존 형식 유지
                'centralized_statistics': centralized_stats  # 새로운 표준화된 통계
            }
        
        # 하위 호환성: 기존 방식으로 통계 계산
        return self._get_legacy_statistics()
    
    def _get_legacy_statistics(self) -> Dict[str, Any]:
        """기존 방식의 통계 계산 (하위 호환성)"""
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
    
    def _handle_transport_request(self, requester_id: str, priority: int, request_time: float, 
                                 original_allocation_id: str = None) -> Generator[simpy.Event, None, Optional[str]]:
        """
        Transport 요청 특별 처리 (TransportProcess 할당 및 실행)
        
        Args:
            requester_id: 요청자 ID
            priority: 우선순위
            request_time: 요청 시간
            
        Yields:
            simpy.Event: SimPy 이벤트들
            
        Returns:
            Optional[str]: 할당 ID 또는 None
        """
        # 사용 가능한 TransportProcess 찾기
        available_transport = self._find_available_transport_process()
        
        if not available_transport:
            print(f"[시간 {self.env.now:.1f}] Transport 요청 실패: 사용 가능한 TransportProcess가 없습니다")
            return None
        
        transport_id, transport_process = available_transport
        
        # SimPy PriorityResource를 사용한 우선순위 기반 자원 요청
        simpy_priority = 10 - priority  # 사용자 우선순위 변환
        
        with self.resources["transport"].request(priority=simpy_priority) as request:
            yield request
            
            # 대기 시간 계산
            wait_time = self.env.now - request_time
            
            # 할당 성공
            allocation_id = str(uuid.uuid4())
            allocation = ResourceAllocation(
                allocation_id=allocation_id,
                resource_id="transport",
                requester_id=requester_id,
                allocated_amount=1.0,
                allocation_time=self.env.now,
                expected_release_time=None  # TransportProcess에서 관리
            )
            
            self.allocations[allocation_id] = allocation
            self.allocation_history.append(allocation)
            self.successful_allocations += 1
            
            # 메트릭 업데이트
            metrics = self.resource_metrics["transport"]
            metrics.successful_allocations += 1
            metrics.average_wait_time = ((metrics.average_wait_time * (metrics.successful_allocations - 1)) + wait_time) / metrics.successful_allocations
            
            # 중앙 통계 관리자에 기록
            if self.stats_interface:
                self.stats_interface.record_counter("successful_allocations")
                self.stats_interface.record_histogram("waiting_time", wait_time)
                self.stats_interface.record_gauge("utilization", self.get_resource_utilization("transport") * 100)
            
            print(f"[시간 {self.env.now:.1f}] Transport 할당 완료: {transport_id} to {requester_id} (할당 ID: {allocation_id}, 대기시간: {wait_time:.1f})")
            
            # TransportProcess 실행 (백그라운드에서 실행)
            # 원래 요청의 allocation_id도 함께 전달하여 완료 알림과 연결
            self.env.process(self._execute_transport_process(
                transport_process, requester_id, allocation_id, original_allocation_id
            ))
            
            return allocation_id
    
    def _find_available_transport_process(self):
        """
        사용 가능한 TransportProcess 찾기
        
        Returns:
            Tuple[str, TransportProcess] 또는 None: (transport_id, transport_process)
        """
        for transport_id, transport_process in self.transport_processes.items():
            # TransportProcess가 사용 가능한지 확인 (간단한 체크)
            if hasattr(transport_process, 'transport_status') and transport_process.transport_status == "대기":
                return (transport_id, transport_process)
        
        # 첫 번째로 등록된 TransportProcess 반환 (기본값)
        if self.transport_processes:
            first_item = next(iter(self.transport_processes.items()))
            return first_item
        
        return None
    
    def _execute_transport_process(self, transport_process, requester_id: str, allocation_id: str, 
                                  original_allocation_id: str = None) -> Generator[simpy.Event, None, None]:
        """
        TransportProcess 실행 (백그라운드 프로세스)
        
        Args:
            transport_process: 실행할 TransportProcess
            requester_id: 요청자 ID
            allocation_id: 할당 ID
            original_allocation_id: 원래 요청의 allocation_id (완료 알림용)
            
        Yields:
            simpy.Event: SimPy 이벤트들
        """
        try:
            print(f"[시간 {self.env.now:.1f}] ResourceManager가 TransportProcess 실행 시작: {transport_process.process_id} (요청자: {requester_id})")
            
            # TransportProcess의 process_logic 실행 (적재 완료 알림을 위한 정보 전달)
            yield from transport_process.process_logic(
                input_data={
                    "requester_id": requester_id, 
                    "allocation_id": allocation_id,
                    "resource_manager": self,  # ResourceManager 참조 전달
                    "original_allocation_id": original_allocation_id  # 적재 완료 알림용
                }
            )
            
            print(f"[시간 {self.env.now:.1f}] ResourceManager가 TransportProcess 실행 완료: {transport_process.process_id}")
            
            # 할당 정보 정리
            if allocation_id in self.allocations:
                del self.allocations[allocation_id]
            
            # � 전체 운송 프로세스 완료 시에는 추가 처리 없음 (적재 완료 시 이미 알림 전송됨)
            print(f"[시간 {self.env.now:.1f}] ResourceManager: 전체 운송 프로세스 완료 (적재 완료 시 이미 알림 전송됨)")
            
        except Exception as e:
            print(f"[시간 {self.env.now:.1f}] TransportProcess 실행 중 오류: {e}")
            # 오류 발생 시에도 완료 알림 (실패로 표시)
            if original_allocation_id:
                self._notify_transport_completion(original_allocation_id, requester_id, success=False)
    
    def get_transport_status(self) -> Dict[str, Any]:
        """
        Transport 관리 상태 조회
        
        Returns:
            Dict: Transport 관리 상태 정보
        """
        transport_info = {}
        for transport_id, transport_process in self.transport_processes.items():
            transport_info[transport_id] = {
                'process_id': transport_process.process_id,
                'process_name': transport_process.process_name,
                'status': getattr(transport_process, 'transport_status', 'unknown'),
                'route': getattr(transport_process, 'route', None)
            }
        
        return {
            'registered_transports': len(self.transport_processes),
            'transport_queue_length': len(self.transport_queue),
            'transport_processes': transport_info,
            'transport_resource_status': self.get_resource_status("transport") if "transport" in self.resources else None
        }
    
    def request_transport(self, requester_id: str, output_products: Any, priority: int = 7) -> Optional[simpy.Event]:
        """
        단순한 운송 요청 (완료 이벤트 반환)
        
        Args:
            requester_id: 요청자 ID
            output_products: 운송할 출하품
            priority: 우선순위 (기본값: 7)
            
        Returns:
            Optional[simpy.Event]: 운송 완료 이벤트 (실패 시 None)
        """
        try:
            print(f"[시간 {self.env.now:.1f}] ResourceManager: {requester_id}로부터 운송 요청 접수")
            
            # 고유한 allocation_id 생성
            allocation_id = f"transport_{requester_id}_{self.env.now}_{uuid.uuid4().hex[:8]}"
            
            # 완료 이벤트 생성
            completion_event = self.env.event()
            self.transport_completion_events[allocation_id] = completion_event
            self.transport_requester_map[allocation_id] = requester_id
            
            print(f"[시간 {self.env.now:.1f}] ResourceManager: 운송 완료 이벤트 생성 (할당 ID: {allocation_id})")
            
            # 운송 요청을 비동기적으로 처리하기 위해 프로세스 시작
            self.env.process(self._process_transport_request(requester_id, output_products, priority, allocation_id))
            
            return completion_event
            
        except Exception as e:
            print(f"[시간 {self.env.now:.1f}] ResourceManager: 운송 요청 접수 실패 - {e}")
            return None
    
    def _process_transport_request(self, requester_id: str, output_products: Any, priority: int, allocation_id: str) -> Generator[simpy.Event, None, None]:
        """
        운송 요청을 백그라운드에서 처리하는 내부 메서드
        
        Args:
            requester_id: 요청자 ID
            output_products: 운송할 출하품
            priority: 우선순위
            allocation_id: 할당 ID
            
        Yields:
            simpy.Event: SimPy 이벤트들
        """
        try:
            print(f"[시간 {self.env.now:.1f}] ResourceManager: {requester_id} 운송 요청 처리 시작 (할당 ID: {allocation_id})")
            
            # 기존 transport 할당 로직 활용 (원래 allocation_id 전달)
            transport_allocation_id = yield from self._handle_transport_request(
                requester_id, priority, self.env.now, allocation_id
            )
            
            if transport_allocation_id:
                print(f"[시간 {self.env.now:.1f}] ResourceManager: {requester_id} 운송 할당 성공 (할당 ID: {transport_allocation_id})")
                print(f"[시간 {self.env.now:.1f}] ResourceManager: 실제 운송 처리는 TransportProcess에서 수행")
                
                # 📦 실제 TransportProcess 실행이 완료될 때까지 대기한 후 완료 알림
                # 완료 알림은 _handle_transport_request 내부의 _execute_transport_process에서 처리해야 함
                
            else:
                print(f"[시간 {self.env.now:.1f}] ResourceManager: {requester_id} 운송 할당 실패")
                self._notify_transport_completion(allocation_id, requester_id, success=False)
                
        except Exception as e:
            print(f"[시간 {self.env.now:.1f}] ResourceManager: {requester_id} 운송 요청 처리 중 오류 - {e}")
            self._notify_transport_completion(allocation_id, requester_id, success=False)
    
    def _notify_transport_completion(self, allocation_id: str, requester_id: str, success: bool = True):
        """
        운송 완료 알림
        
        Args:
            allocation_id: 할당 ID
            requester_id: 요청자 ID
            success: 성공 여부
        """
        if allocation_id in self.transport_completion_events:
            completion_event = self.transport_completion_events[allocation_id]
            
            # SimPy Event는 succeed(value)로 값을 전달해야 함
            completion_event.succeed({
                'allocation_id': allocation_id,
                'requester_id': requester_id, 
                'success': success,
                'completion_time': self.env.now
            })
            
            print(f"[시간 {self.env.now:.1f}] ResourceManager: {requester_id} 운송 완료 알림 전송 (성공: {success})")
            
            # 정리
            del self.transport_completion_events[allocation_id]
            if allocation_id in self.transport_requester_map:
                del self.transport_requester_map[allocation_id]
        else:
            print(f"[시간 {self.env.now:.1f}] ResourceManager: 완료 이벤트를 찾을 수 없음 (할당 ID: {allocation_id})")
