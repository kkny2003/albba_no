"""
운송 공정을 정의하는 클래스입니다.
출발지에서 도착지로 자원을 운송하는 프로세스를 모델링합니다.
"""

from src.Processes.base_process import BaseProcess
from typing import Any, List, Generator, Dict, Union
import simpy
from src.Resource.resource_base import Resource, ResourceRequirement, ResourceType


class TransportProcess(BaseProcess):
    """
    운송 공정을 정의하는 클래스입니다 (SimPy 기반).
    
    운송 공정은 다음 4단계로 구성됩니다:
    1. 적재 (loading_time): 출발지에서 운송 수단에 제품 적재
    2. 운송 (transport_time): 출발지에서 도착지까지 실제 운송
    3. 하역 (unloading_time): 도착지에서 운송 수단에서 제품 하역
    4. 대기 (cooldown_time): 다음 운송 준비를 위한 대기
    
    시간 단위: 시뮬레이션 시간 단위 (1.0 = 1시간)
    """

    def __init__(self, env: simpy.Environment, process_id: str, process_name: str,
                 machines, workers, 
                 input_resources: Union[List[Resource], Dict[str, float], None], 
                 output_resources: Union[List[Resource], Dict[str, float], None],
                 resource_requirements: List[ResourceRequirement],
                 loading_time: float,
                 transport_time: float,
                 unloading_time: float,
                 cooldown_time: float = 0.0,
                 products_per_cycle: int = None,
                 failure_weight_machine: float = 1.0, 
                 failure_weight_worker: float = 1.0):
        """
        초기화 메서드입니다 (SimPy 환경 필수).
        
        :param env: SimPy 환경 객체 (필수)
        :param machines: 운송에 사용될 기계 목록 (machine 또는 worker 중 하나는 필수)
        :param workers: 운송 작업을 수행할 작업자 목록 (machine 또는 worker 중 하나는 필수)
        :param input_resources: 입력 자원 (List[Resource] 또는 Dict[str, float]로 자원량 지정, 예: {"화물": 10})
        :param output_resources: 출력 자원 (List[Resource] 또는 Dict[str, float]로 자원량 지정, 예: {"배송완료": 10})
        :param resource_requirements: 자원 요구사항 목록 (필수)
        :param process_id: 공정 고유 ID (필수)
        :param process_name: 공정 이름 (필수)
        :param loading_time: 적재 시간 (시뮬레이션 시간 단위, 필수)
            - 출발지에서 운송 수단에 제품을 적재하는데 소요되는 시간
            - 실제 시간과의 변환: 1.0 = 1시간
            - 예시: 0.5 = 30분, 1.0 = 1시간
        :param transport_time: 운송 시간 (시뮬레이션 시간 단위, 필수)
            - 출발지에서 도착지까지 실제 운송에 소요되는 시간
            - 거리, 운송 수단 속도, 경로에 따라 조정 가능
            - 예시: 2.0 = 2시간, 0.5 = 30분
        :param unloading_time: 하역 시간 (시뮬레이션 시간 단위, 필수)
            - 도착지에서 운송 수단에서 제품을 하역하는데 소요되는 시간
            - 하역 장비, 작업자 수에 따라 조정 가능
            - 예시: 0.5 = 30분, 1.0 = 1시간
        :param cooldown_time: 대기 시간 (시뮬레이션 시간 단위)
        :param products_per_cycle: 한번 공정 실행 시 생산되는 제품 수 (None이면 batch_size와 동일)
        :param failure_weight_machine: 기계 고장률 가중치 (기본값: 1.0)
        :param failure_weight_worker: 작업자 실수율 가중치 (기본값: 1.0)
        """
        # 필수 시간 매개변수 유효성 검사
        if loading_time <= 0:
            raise ValueError(f"loading_time은 0보다 큰 양수여야 합니다. 입력값: {loading_time}")
        if transport_time <= 0:
            raise ValueError(f"transport_time은 0보다 큰 양수여야 합니다. 입력값: {transport_time}")
        if unloading_time <= 0:
            raise ValueError(f"unloading_time은 0보다 큰 양수여야 합니다. 입력값: {unloading_time}")
        
        # BaseProcess 초기화 (자원 정보 포함)
        super().__init__(
            env=env, 
            process_id=process_id, 
            process_name=process_name,
            machines=machines, 
            workers=workers, 
            processing_time=loading_time + transport_time + unloading_time,
            products_per_cycle=products_per_cycle,
            failure_weight_machine=failure_weight_machine,
            failure_weight_worker=failure_weight_worker,
            input_resources=input_resources,
            output_resources=output_resources,
            resource_requirements=resource_requirements
        )
        
        # BaseProcess의 배치 처리 기능 활용 (transport_queue 대신)
        # self.transport_queue는 BaseProcess.current_batch로 대체됨
        
        # 운송 시간 구성 요소 (시뮬레이션 시간 단위)
        self.loading_time = loading_time      # 적재 시간: 출발지에서 운송 수단에 제품 적재
        self.transport_time = transport_time  # 운송 시간: 출발지에서 도착지까지 실제 운송
        self.unloading_time = unloading_time  # 하역 시간: 도착지에서 운송 수단에서 제품 하역
        self.cooldown_time = cooldown_time    # 대기 시간: 다음 운송 준비를 위한 대기
        
        # 운송 경로 및 상태
        self.route = None  # 운송 경로 (문자열로 설정 가능)
        self.transport_status = "대기"  # 운송 상태: 대기, 적재중, 운송중, 하역중
        
        # 운송 공정 특화 자원 설정
        self._setup_transport_resources()
        
        # BaseProcess의 고급 기능들 활용
        self.apply_failure_weight_to_machines()
        self.apply_failure_weight_to_workers()
        
    def _setup_transport_resources(self):
        """운송 공정용 자원 요구사항을 설정하는 메서드"""
        # 기본 자원 설정 (BaseProcess에서 처리됨)
        self._setup_default_resources()
        
        # 운송 대상 요구사항 추가 (운송할 제품)
        transport_target_req = ResourceRequirement(
            resource_type=ResourceType.FINISHED_PRODUCT,
            name="운송대상",
            required_quantity=1.0,
            unit="개",
            is_mandatory=True
        )
        self.add_resource_requirement(transport_target_req)
        
        # 운송 수단 요구사항 추가
        transport_vehicle_req = ResourceRequirement(
            resource_type=ResourceType.TRANSPORT,
            name="운송수단",
            required_quantity=1.0,
            unit="대",
            is_mandatory=True
        )
        self.add_resource_requirement(transport_vehicle_req)
        
    def add_to_transport_queue(self, item):
        """
        운송 대기열에 아이템 추가 (BaseProcess의 배치 기능 활용)
        
        Args:
            item: 추가할 아이템
            
        Returns:
            bool: 배치에 추가 성공 여부
        """
        success = self.add_to_batch(item)
        if success:
            print(f"[{self.process_name}] 운송 대기열에 아이템 추가: {item} (배치: {len(self.current_batch)}/{self.batch_size})")
        else:
            print(f"[{self.process_name}] 배치가 가득 참. 현재 배치를 먼저 운송하세요.")
        return success
    
    def get_transport_queue_status(self):
        """
        운송 대기열 상태 조회 (BaseProcess의 배치 상태 활용)
        
        Returns:
            Dict: 운송 대기열 상태 정보
        """
        return {
            'items_in_queue': self.get_current_batch(),
            'batch_status': self.get_batch_status(),
            'is_batch_ready': self.is_batch_ready(),
            'transport_status': self.transport_status,
            'route': self.route,
            'process_info': self.get_process_info()
        }
    
    def set_transport_batch_size(self, batch_size: int):
        """
        운송 배치 크기 설정
        
        Args:
            batch_size: 배치 크기 (1 이상)
        """
        self.batch_size = max(1, batch_size)
        self.enable_batch_processing = batch_size > 1
        print(f"[{self.process_name}] 운송 배치 크기 설정: {self.batch_size}")
    
    def set_transport_priority(self, priority: int):
        """
        운송 우선순위 설정 (BaseProcess 기능 활용)
        
        Args:
            priority: 우선순위 (1-10)
        """
        return self.set_execution_priority(priority)
    
    def add_transport_condition(self, condition):
        """
        운송 실행 조건 추가 (BaseProcess 기능 활용)
        
        Args:
            condition: 실행 조건 함수
        """
        return self.add_execution_condition(condition)
    
    def set_parallel_transport(self, safe: bool):
        """
        병렬 운송 안전성 설정 (BaseProcess 기능 활용)
        
        Args:
            safe: 병렬 실행 안전 여부
        """
        return self.set_parallel_safe(safe)
    
    # ========== 운송 특화 출하품 Transport 관리 ==========
    
    def set_transport_batch_capacity(self, capacity: int) -> 'TransportProcess':
        """
        운송 배치 용량 설정 (BaseProcess 기능 활용)
        
        Args:
            capacity: 운송 배치 용량
            
        Returns:
            TransportProcess: 자기 자신 (메서드 체이닝용)
        """
        self.set_batch_size(capacity)
        return self
    
    def execute_transport_delivery(self, count: int = None) -> int:
        """
        운송 배치의 제품들을 목적지로 배송 (BaseProcess 기능 활용)
        
        Args:
            count: 배송할 제품 수 (None이면 모든 제품)
            
        Returns:
            int: 실제로 배송된 제품 수
        """
        delivered = self.transport_output_items(count)
        print(f"[{self.process_name}] 운송 배송 완료: {delivered}개")
        return delivered
    
    def get_transport_buffer_status(self) -> Dict[str, Any]:
        """
        운송 버퍼 상태 조회 (BaseProcess 기능 활용)
        
        Returns:
            Dict: 운송 버퍼 상태 정보
        """
        buffer_status = self.get_output_buffer_status()
        return {
            'transport_buffer': buffer_status,
            'items_in_buffer': buffer_status['current_count'],
            'buffer_capacity': buffer_status['capacity'],
            'transport_blocked': buffer_status['waiting_for_transport'],
            'batch_info': self.get_batch_status(),
            'transport_status': self.transport_status,
            'route': self.route
        }
    
    def is_transport_blocked(self) -> bool:
        """
        운송이 배송 대기로 막혀있는지 확인 (BaseProcess 기능 활용)
        
        Returns:
            bool: 운송이 막혀있으면 True
        """
        return self.waiting_for_transport or self.is_output_buffer_full()
    
    def enable_transport_blocking(self, enable: bool = True) -> 'TransportProcess':
        """
        운송 blocking 기능 활성화/비활성화 (BaseProcess 기능 활용)
        
        Args:
            enable: blocking 활성화 여부
            
        Returns:
            TransportProcess: 자기 자신 (메서드 체이닝용)
        """
        self.enable_output_blocking_feature(enable)
        return self
        
    def set_route(self, route: str):
        """운송 경로 설정"""
        self.route = route
        print(f"[{self.process_name}] 운송 경로 설정: {route}")
        
    def start_transport(self):
        """운송 시작"""
        print(f"[{self.process_name}] 운송 시작")
        
    def clear_transport_queue(self):
        """
        운송 대기열 정리 (BaseProcess의 배치 기능 활용)
        """
        self.current_batch.clear()
        print(f"[{self.process_name}] 운송 대기열 정리 완료")
        
    def get_transport_queue_count(self):
        """
        운송 대기열 개수 조회 (BaseProcess 기능 활용)
        
        Returns:
            int: 현재 배치의 아이템 수
        """
        return len(self.current_batch)
        
    def process_logic(self, input_data: Any = None) -> Generator[simpy.Event, None, Any]:
        """
        운송 공정의 핵심 로직 (SimPy generator 방식)
        
        Args:
            input_data: 입력 데이터 (운송할 제품 정보)
            
        Yields:
            simpy.Event: SimPy 이벤트들
            
        Returns:
            Any: 운송된 제품
        """
        print(f"[시간 {self.env.now:.1f}] {self.process_name} 운송 로직 시작")
        
        # 1. 적재 단계 (loading_time)
        print(f"[시간 {self.env.now:.1f}] {self.process_name} 적재 중... (소요시간: {self.loading_time:.1f})")
        yield self.env.timeout(self.loading_time)
        
        # 2. 운송 단계 (transport_time)
        print(f"[시간 {self.env.now:.1f}] {self.process_name} 운송 중... (소요시간: {self.transport_time:.1f})")
        yield self.env.timeout(self.transport_time)
        
        # 3. 하역 단계 (unloading_time)
        print(f"[시간 {self.env.now:.1f}] {self.process_name} 하역 중... (소요시간: {self.unloading_time:.1f})")
        yield self.env.timeout(self.unloading_time)
        
        # 4. 대기 단계 (cooldown_time) - 다음 운송 준비
        print(f"[시간 {self.env.now:.1f}] {self.process_name} 대기 중... (소요시간: {self.cooldown_time:.1f})")
        yield self.env.timeout(self.cooldown_time)
        
        print(f"[시간 {self.env.now:.1f}] {self.process_name} 운송 로직 완료")
        
        return input_data  # 운송된 자원 반환
