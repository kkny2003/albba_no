from src.Processes.base_process import BaseProcess
from typing import Any, List, Generator, Dict, Union, Optional, TYPE_CHECKING
import simpy
from src.Resource.resource_base import Resource, ResourceRequirement, ResourceType

if TYPE_CHECKING:
    from src.Processes.transport_process import TransportProcess


class AssemblyProcess(BaseProcess):
    """조립 공정을 정의하는 클래스입니다 (SimPy 기반)."""

    def __init__(self, env: simpy.Environment, process_id: str, process_name: str,
                 machines, workers, 
                 input_resources: Union[List[Resource], Dict[str, float], None], 
                 output_resources: Union[List[Resource], Dict[str, float], None],
                 resource_requirements: List[ResourceRequirement],
                 assembly_time: float = 3.0,
                 products_per_cycle: int = None,
                 failure_weight_machine: float = 1.0, 
                 failure_weight_worker: float = 1.0,
                 resource_manager=None,
                 transport_process: Optional['TransportProcess'] = None):
        """
        초기화 메서드입니다 (SimPy 환경 필수).
        
        :param env: SimPy 환경 객체 (필수)
        :param machines: 조립에 사용될 기계 목록 (machine 또는 worker 중 하나는 필수)
        :param workers: 조립 작업을 수행할 작업자 목록 (machine 또는 worker 중 하나는 필수)
        :param input_resources: 입력 자원 (List[Resource] 또는 Dict[str, float]로 자원량 지정, 예: {"부품A": 2, "부품B": 1})
        :param output_resources: 출력 자원 (List[Resource] 또는 Dict[str, float]로 자원량 지정, 예: {"완제품": 1})
        :param resource_requirements: 자원 요구사항 목록 (필수)
        :param process_id: 공정 고유 ID (필수)
        :param process_name: 공정 이름 (필수)
        :param assembly_time: 조립 처리 시간 (시뮬레이션 시간 단위)
        :param products_per_cycle: 한번 공정 실행 시 생산되는 제품 수 (None이면 batch_size와 동일)
        :param failure_weight_machine: 기계 고장률 가중치 (기본값: 1.0)
        :param failure_weight_worker: 작업자 실수율 가중치 (기본값: 1.0)
        :param resource_manager: 자원 관리자 객체 (transport 할당용, 선택적)
        :param transport_process: 운송 공정 객체 (TransportProcess 인스턴스, 선택적)
        """
        # BaseProcess 초기화 (자원 정보 포함)
        super().__init__(
            env=env, 
            process_id=process_id, 
            process_name=process_name,
            machines=machines, 
            workers=workers, 
            processing_time=assembly_time,
            products_per_cycle=products_per_cycle,
            failure_weight_machine=failure_weight_machine,
            failure_weight_worker=failure_weight_worker,
            input_resources=input_resources,
            output_resources=output_resources,
            resource_requirements=resource_requirements
        )
        
        # Transport 관련 설정
        self.resource_manager = resource_manager
        self.transport_process = transport_process  # 참조용 (직접 호출하지 않음)
        self.auto_transport_enabled = resource_manager is not None  # resource_manager가 있으면 자동 transport 활성화
        
        # 조립 공정용 우선순위 관리 (복잡한 공정에서 필요)
        self.execution_priority: int = 5  # 실행 우선순위 (1-10, 높을수록 우선)
        self.assembly_step_priorities: Dict[str, int] = {}  # 조립 단계별 우선순위
        
        print(f"[{self.process_name}] Transport 설정 - 자동 운송: {'활성화' if self.auto_transport_enabled else '비활성화'}")
        
        # BaseProcess의 배치 처리 기능 활용 (assembly_line 대신)
        # self.assembly_line은 BaseProcess.current_batch로 대체됨
        

        
        # BaseProcess의 고급 기능들 활용
        self.apply_failure_weight_to_machines()
        self.apply_failure_weight_to_workers()
        

        

        
    def add_to_assembly_line(self, product):
        """
        조립 라인에 제품 추가 (BaseProcess의 배치 기능 활용)
        
        Args:
            product: 추가할 제품
            
        Returns:
            bool: 배치에 추가 성공 여부
        """
        success = self.add_to_batch(product)
        if success:
            print(f"[{self.process_name}] 조립 라인에 제품 추가: {product} (배치: {len(self.current_batch)}/{self.batch_size})")
        else:
            print(f"[{self.process_name}] 배치가 가득 참. 현재 배치를 먼저 처리하세요.")
        return success
    
    def get_assembly_line_status(self):
        """
        조립 라인 상태 조회 (BaseProcess의 배치 상태 활용)
        
        Returns:
            Dict: 조립 라인 상태 정보
        """
        return {
            'products_in_line': self.get_current_batch(),
            'batch_status': self.get_batch_status(),
            'is_batch_ready': self.is_batch_ready(),
            'process_info': self.get_process_info()
        }
    
    def set_execution_priority(self, priority: int) -> 'AssemblyProcess':
        """
        조립 공정의 실행 우선순위를 설정 (복잡한 조립 공정에서 필요)
        
        Args:
            priority: 우선순위 (1-10, 높을수록 우선)
            
        Returns:
            AssemblyProcess: 자기 자신 (메서드 체이닝용)
        """
        self.execution_priority = max(1, min(10, priority))
        print(f"[{self.process_name}] 조립 공정 우선순위 설정: {self.execution_priority}")
        return self
    
    def set_assembly_step_priority(self, step_name: str, priority: int) -> 'AssemblyProcess':
        """
        조립 단계별 우선순위를 설정
        
        Args:
            step_name: 조립 단계 이름
            priority: 우선순위 (1-10, 높을수록 우선)
            
        Returns:
            AssemblyProcess: 자기 자신 (메서드 체이닝용)
        """
        self.assembly_step_priorities[step_name] = max(1, min(10, priority))
        print(f"[{self.process_name}] 조립 단계 '{step_name}' 우선순위 설정: {priority}")
        return self
    
    def get_execution_priority(self) -> int:
        """
        현재 설정된 실행 우선순위를 반환
        
        Returns:
            int: 실행 우선순위
        """
        return self.execution_priority
    
    def set_assembly_batch_size(self, batch_size: int):
        """
        조립 배치 크기 설정
        
        Args:
            batch_size: 배치 크기 (1 이상)
        """
        self.batch_size = max(1, batch_size)
        self.enable_batch_processing = batch_size > 1
        print(f"[{self.process_name}] 조립 배치 크기 설정: {self.batch_size}")
    
    def add_assembly_condition(self, condition):
        """
        조립 실행 조건 추가 (BaseProcess 기능 활용)
        
        Args:
            condition: 실행 조건 함수
        """
        return self.add_execution_condition(condition)
    
    def set_parallel_assembly(self, safe: bool):
        """
        병렬 조립 안전성 설정 (BaseProcess 기능 활용)
        
        Args:
            safe: 병렬 실행 안전 여부
        """
        return self.set_parallel_safe(safe)
    
    # ========== 조립 특화 출하품 Transport 관리 ==========
    
    def set_assembly_output_buffer(self, capacity: int) -> 'AssemblyProcess':
        """
        조립 출력 버퍼 용량 설정 (BaseProcess 기능 활용)
        
        Args:
            capacity: 출력 버퍼 용량
            
        Returns:
            AssemblyProcess: 자기 자신 (메서드 체이닝용)
        """
        self.set_output_buffer_capacity(capacity)
        return self
    
    def transport_assembled_products(self, count: int = None) -> int:
        """
        조립된 제품들을 운송 (BaseProcess 기능 활용)
        
        Args:
            count: 운송할 제품 수 (None이면 모든 제품)
            
        Returns:
            int: 실제로 운송된 제품 수
        """
        transported = self.transport_output_items(count)
        print(f"[{self.process_name}] 조립품 운송 완료: {transported}개")
        return transported
    
    def get_assembly_buffer_status(self) -> Dict[str, Any]:
        """
        조립 버퍼 상태 조회 (BaseProcess 기능 활용)
        
        Returns:
            Dict: 조립 버퍼 상태 정보
        """
        buffer_status = self.get_output_buffer_status()
        return {
            'assembly_buffer': buffer_status,
            'products_in_buffer': buffer_status['current_count'],
            'buffer_capacity': buffer_status['capacity'],
            'assembly_blocked': buffer_status['waiting_for_transport'],
            'batch_info': self.get_batch_status()
        }
    
    def is_assembly_blocked(self) -> bool:
        """
        조립이 출하 대기로 막혀있는지 확인 (BaseProcess 기능 활용)
        
        Returns:
            bool: 조립이 막혀있으면 True
        """
        return self.waiting_for_transport or self.is_output_buffer_full()
    
    def enable_assembly_blocking(self, enable: bool = True) -> 'AssemblyProcess':
        """
        조립 blocking 기능 활성화/비활성화 (BaseProcess 기능 활용)
        
        Args:
            enable: blocking 활성화 여부
            
        Returns:
            AssemblyProcess: 자기 자신 (메서드 체이닝용)
        """
        self.enable_output_blocking_feature(enable)
        return self
        
    def start_assembly(self):
        """조립 공정 시작"""
        print(f"[{self.process_name}] 조립 공정 시작")
        
    def assemble_product(self, product):
        """제품 조립"""
        print(f"[{self.process_name}] 제품 조립 중: {product}")
        
    def clear_assembly_line(self):
        """
        조립 라인 정리 (BaseProcess의 배치 기능 활용)
        """
        self.current_batch.clear()
        print(f"[{self.process_name}] 조립 라인 정리 완료")
        
    def get_assembly_queue_count(self):
        """
        조립 대기열 개수 조회 (BaseProcess 기능 활용)
        
        Returns:
            int: 현재 배치의 아이템 수
        """
        return len(self.current_batch)
        
    def process_logic(self, input_data: Any = None) -> Generator[simpy.Event, None, Any]:
        """
        조립 공정의 핵심 로직 (SimPy generator 방식)
        
        Args:
            input_data: 입력 데이터 (조립할 반제품 정보)
            
        Yields:
            simpy.Event: SimPy 이벤트들
            
        Returns:
            Any: 조립된 완제품
        """
        print(f"[시간 {self.env.now:.1f}] {self.process_name} 조립 로직 시작")
        
        # 1. 반제품 확인
        if not self._validate_semi_finished_products(input_data):
            raise Exception("조립에 필요한 반제품이 부족합니다")
        
        # 2. 조립 처리 시간 대기
        yield self.env.timeout(self.processing_time)
        
        # 3. 완제품 생성
        assembled_product = self._create_finished_product(input_data)
        
        print(f"[시간 {self.env.now:.1f}] {self.process_name} 조립 로직 완료")
        
        # 4. 조립 완료 후 운송 요청 (자동 운송이 활성화된 경우)
        if self.auto_transport_enabled and self.resource_manager:
            print(f"[시간 {self.env.now:.1f}] {self.process_name} 조립품 운송 요청 시작")
            yield from self.request_transport_for_output(assembled_product)
        
        return assembled_product
        
    def _validate_semi_finished_products(self, input_data: Any) -> bool:
        """반제품 유효성 검사"""
        # 반제품 검증 로직 구현
        return True
        
    def _create_finished_product(self, input_data: Any) -> Any:
        """완제품 생성"""
        # 완제품 생성 로직 구현
        return f"조립완료_{input_data}" if input_data else "조립완료_기본제품"
    
    # ========== 조립 공정 운송 요청 메서드들 ==========
    
    def request_transport_for_output(self, output_products: Any) -> Generator[simpy.Event, None, None]:
        """
        조립품을 위한 Transport 요청 (완료까지 대기)
        
        Args:
            output_products: 운송할 조립품
            
        Yields:
            simpy.Event: SimPy 이벤트들
        """
        if not self.resource_manager:
            print(f"[시간 {self.env.now:.1f}] {self.process_name} Transport 요청 실패: resource_manager가 없습니다")
            return
        
        print(f"[시간 {self.env.now:.1f}] {self.process_name} Transport 요청을 ResourceManager에게 전달")
        
        # ResourceManager에게 운송 요청하고 완료 이벤트 받기
        completion_event = self.resource_manager.request_transport(
            requester_id=self.process_id,
            output_products=output_products,
            priority=7  # 조립 완료 후 운송은 높은 우선순위
        )
        
        if completion_event:
            print(f"[시간 {self.env.now:.1f}] {self.process_name} Transport 요청 접수됨 - 완료까지 대기")
            
            # 출력 버퍼에서 제품 제거 (요청 접수 성공으로 간주)
            if hasattr(self, 'current_output_count') and self.current_output_count > 0:
                self.current_output_count -= 1
                print(f"[시간 {self.env.now:.1f}] {self.process_name} 출력 버퍼에서 제품 제거 (운송 요청 접수 완료, 남은 개수: {self.current_output_count})")
            
            # 운송 완료까지 대기
            try:
                completion_info = yield completion_event
                print(f"[시간 {self.env.now:.1f}] {self.process_name} Transport 완료 알림 수신: {completion_info}")
                
                if completion_info and completion_info.get('success', False):
                    print(f"[시간 {self.env.now:.1f}] {self.process_name} Transport 성공적으로 완료")
                else:
                    print(f"[시간 {self.env.now:.1f}] {self.process_name} Transport 실패")
                    
            except Exception as e:
                print(f"[시간 {self.env.now:.1f}] {self.process_name} Transport 완료 대기 중 오류: {e}")
        else:
            print(f"[시간 {self.env.now:.1f}] {self.process_name} Transport 요청 접수 실패")
    
    def request_batch_transport(self, batch_products: List[Any]) -> bool:
        """
        배치 단위로 Transport 요청 (단순 요청만 담당)
        
        Args:
            batch_products: 운송 요청할 조립품들의 배치
            
        Returns:
            bool: 요청 성공 여부
        """
        if not self.resource_manager:
            print(f"[시간 {self.env.now:.1f}] {self.process_name} 배치 운송 요청 실패: resource_manager가 없습니다")
            return False
        
        print(f"[시간 {self.env.now:.1f}] {self.process_name} 배치 운송 요청 ({len(batch_products)}개 조립품)")
        
        # 배치 전체를 하나의 운송 요청으로 처리
        success = self.resource_manager.request_transport(
            requester_id=self.process_id,
            output_products=batch_products,
            priority=6  # 배치 운송은 일반 우선순위
        )
        
        if success:
            print(f"[시간 {self.env.now:.1f}] {self.process_name} 배치 운송 요청 접수됨 - ResourceManager에서 처리")
        else:
            print(f"[시간 {self.env.now:.1f}] {self.process_name} 배치 운송 요청 접수 실패")
            
        return success