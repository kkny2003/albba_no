from src.Processes.base_process import BaseProcess
from typing import Any, List, Generator, Dict, Union
import simpy
from src.Resource.resource_base import Resource, ResourceRequirement, ResourceType


class ManufacturingProcess(BaseProcess):
    """제조 공정을 정의하는 클래스입니다 (SimPy 기반)."""

    def __init__(self, env: simpy.Environment, process_id: str, process_name: str,
                 machines, workers, 
                 input_resources: Union[List[Resource], Dict[str, float], None], 
                 output_resources: Union[List[Resource], Dict[str, float], None],
                 resource_requirements: List[ResourceRequirement],
                 processing_time: float = 2.0,
                 products_per_cycle: int = None,
                 failure_weight_machine: float = 1.0, 
                 failure_weight_worker: float = 1.0):
        """
        제조 공정의 초기화 메서드입니다 (SimPy 환경 필수).

        :param env: SimPy 환경 객체 (필수)
        :param machines: 사용될 기계 목록 (machine 또는 worker 중 하나는 필수)
        :param workers: 작업자 목록 (machine 또는 worker 중 하나는 필수)
        :param input_resources: 입력 자원 (List[Resource] 또는 Dict[str, float]로 자원량 지정, 예: {"철강": 1.3, "플라스틱": 2.0})
        :param output_resources: 출력 자원 (List[Resource] 또는 Dict[str, float]로 자원량 지정, 예: {"완제품": 1.5, "부품": 0.8})
        :param resource_requirements: 자원 요구사항 목록 (필수)
        :param process_id: 공정 고유 ID (필수)
        :param process_name: 공정 이름 (필수)
        :param processing_time: 제조 처리 시간 (시뮬레이션 시간 단위)
        :param products_per_cycle: 한번 공정 실행 시 생산되는 제품 수 (None이면 batch_size와 동일)
        :param failure_weight_machine: 기계 고장률 가중치 (기본값: 1.0)
        :param failure_weight_worker: 작업자 실수율 가중치 (기본값: 1.0)
        """
        # BaseProcess 초기화 (자원 정보 포함)
        super().__init__(
            env=env, 
            process_id=process_id, 
            process_name=process_name,
            machines=machines, 
            workers=workers, 
            processing_time=processing_time,
            products_per_cycle=products_per_cycle,
            failure_weight_machine=failure_weight_machine,
            failure_weight_worker=failure_weight_worker,
            input_resources=input_resources,
            output_resources=output_resources,
            resource_requirements=resource_requirements
        )
        
        # BaseProcess의 배치 처리 기능 활용 (production_line 대신)
        # self.production_line은 BaseProcess.current_batch로 대체됨
        
        # 제조 공정 특화 자원 설정
        self._setup_manufacturing_resources()
        
        # BaseProcess의 고급 기능들 활용
        self.apply_failure_weight_to_machines()
        self.apply_failure_weight_to_workers()
        
    def _setup_manufacturing_resources(self):
        """제조 공정용 자원 요구사항을 설정하는 메서드"""
        # 기본 자원 설정 (BaseProcess에서 처리됨)
        self._setup_default_resources()
        
        # 원자재 요구사항 추가 (제조용 입력)
        raw_material_req = ResourceRequirement(
            resource_type=ResourceType.RAW_MATERIAL,
            name="원자재",
            required_quantity=1.0,
            unit="kg",
            is_mandatory=True
        )
        self.add_resource_requirement(raw_material_req)
        
        # 운송 자원 요구사항 추가 (원자재 운반용)
        transport_req = ResourceRequirement(
            resource_type=ResourceType.TRANSPORT,
            name="운송장비",
            required_quantity=1.0,
            unit="대", 
            is_mandatory=False  # 선택적 (수동 운반도 가능)
        )
        self.add_resource_requirement(transport_req)
        
    def start_process(self):
        """제조 공정 시작"""
        print(f"[{self.process_name}] 제조 공정 시작")
        
    def stop_process(self):
        """제조 공정 중지"""
        print(f"[{self.process_name}] 제조 공정 중지")
        
    def add_to_production_line(self, product):
        """
        생산 라인에 제품 추가 (BaseProcess의 배치 기능 활용)
        
        Args:
            product: 추가할 제품
            
        Returns:
            bool: 배치에 추가 성공 여부
        """
        success = self.add_to_batch(product)
        if success:
            print(f"[{self.process_name}] 생산 라인에 제품 추가: {product} (배치: {len(self.current_batch)}/{self.batch_size})")
        else:
            print(f"[{self.process_name}] 배치가 가득 참. 현재 배치를 먼저 처리하세요.")
        return success
        
    def remove_from_production_line(self, product):
        """
        생산 라인에서 제품 제거 (BaseProcess의 배치 기능 활용)
        
        Args:
            product: 제거할 제품
            
        Returns:
            bool: 제거 성공 여부
        """
        if product in self.current_batch:
            self.current_batch.remove(product)
            print(f"[{self.process_name}] 생산 라인에서 제품 제거: {product}")
            return True
        else:
            print(f"[{self.process_name}] 제품을 찾을 수 없음: {product}")
            return False
    
    def get_production_line_status(self):
        """
        생산 라인 상태 조회 (BaseProcess의 배치 상태 활용)
        
        Returns:
            Dict: 생산 라인 상태 정보
        """
        return {
            'products_in_line': self.get_current_batch(),
            'batch_status': self.get_batch_status(),
            'is_batch_ready': self.is_batch_ready(),
            'process_info': self.get_process_info()
        }
    
    def set_production_batch_size(self, batch_size: int):
        """
        생산 배치 크기 설정
        
        Args:
            batch_size: 배치 크기 (1 이상)
        """
        self.batch_size = max(1, batch_size)
        self.enable_batch_processing = batch_size > 1
        print(f"[{self.process_name}] 생산 배치 크기 설정: {self.batch_size}")
    
    def set_manufacturing_priority(self, priority: int):
        """
        제조 우선순위 설정 (BaseProcess 기능 활용)
        
        Args:
            priority: 우선순위 (1-10)
        """
        return self.set_execution_priority(priority)
    
    def add_manufacturing_condition(self, condition):
        """
        제조 실행 조건 추가 (BaseProcess 기능 활용)
        
        Args:
            condition: 실행 조건 함수
        """
        return self.add_execution_condition(condition)
    
    def set_parallel_manufacturing(self, safe: bool):
        """
        병렬 제조 안전성 설정 (BaseProcess 기능 활용)
        
        Args:
            safe: 병렬 실행 안전 여부
        """
        return self.set_parallel_safe(safe)
    
    # ========== 제조 특화 출하품 Transport 관리 ==========
    
    def set_production_output_buffer(self, capacity: int) -> 'ManufacturingProcess':
        """
        생산 출력 버퍼 용량 설정 (BaseProcess 기능 활용)
        
        Args:
            capacity: 출력 버퍼 용량
            
        Returns:
            ManufacturingProcess: 자기 자신 (메서드 체이닝용)
        """
        self.set_output_buffer_capacity(capacity)
        return self
    
    def transport_manufactured_products(self, count: int = None) -> int:
        """
        제조된 제품들을 운송 (BaseProcess 기능 활용)
        
        Args:
            count: 운송할 제품 수 (None이면 모든 제품)
            
        Returns:
            int: 실제로 운송된 제품 수
        """
        transported = self.transport_output_items(count)
        print(f"[{self.process_name}] 제조품 운송 완료: {transported}개")
        return transported
    
    def get_production_buffer_status(self) -> Dict[str, Any]:
        """
        생산 버퍼 상태 조회 (BaseProcess 기능 활용)
        
        Returns:
            Dict: 생산 버퍼 상태 정보
        """
        buffer_status = self.get_output_buffer_status()
        return {
            'production_buffer': buffer_status,
            'products_in_buffer': buffer_status['current_count'],
            'buffer_capacity': buffer_status['capacity'],
            'production_blocked': buffer_status['waiting_for_transport'],
            'batch_info': self.get_batch_status()
        }
    
    def is_production_blocked(self) -> bool:
        """
        생산이 출하 대기로 막혀있는지 확인 (BaseProcess 기능 활용)
        
        Returns:
            bool: 생산이 막혀있으면 True
        """
        return self.waiting_for_transport or self.is_output_buffer_full()
    
    def enable_production_blocking(self, enable: bool = True) -> 'ManufacturingProcess':
        """
        생산 blocking 기능 활성화/비활성화 (BaseProcess 기능 활용)
        
        Args:
            enable: blocking 활성화 여부
            
        Returns:
            ManufacturingProcess: 자기 자신 (메서드 체이닝용)
        """
        self.enable_output_blocking_feature(enable)
        return self
    
    # ========== 제조 공정 출하품 Transport 관리 메서드들 ==========
    
    def set_production_buffer_capacity(self, capacity: int):
        """
        생산 출력 버퍼 용량 설정 (BaseProcess 기능 활용)
        
        Args:
            capacity: 버퍼 용량 (1 이상)
        """
        return self.set_output_buffer_capacity(capacity)
    
    def enable_production_blocking(self, enable: bool = True):
        """
        생산 출력 blocking 기능 활성화/비활성화 (BaseProcess 기능 활용)
        
        Args:
            enable: blocking 활성화 여부 (기본값: True)
        """
        return self.enable_output_blocking_feature(enable)
    
    def get_production_buffer_status(self):
        """
        생산 출력 버퍼 상태 조회 (BaseProcess 기능 활용)
        
        Returns:
            Dict: 생산 출력 버퍼 상태 정보
        """
        buffer_status = self.get_output_buffer_status()
        return {
            'production_buffer_count': buffer_status['current_count'],
            'production_buffer_capacity': buffer_status['capacity'],
            'production_utilization_rate': buffer_status['utilization_rate'],
            'production_buffer_full': buffer_status['is_full'],
            'waiting_for_production_transport': buffer_status['waiting_for_transport'],
            'production_blocking_enabled': buffer_status['blocking_enabled'],
            'batch_status': self.get_batch_status(),
            'production_line_items': self.get_current_batch()
        }
    
    def transport_produced_items(self, count: int = None):
        """
        생산된 제품들을 transport로 운송 (BaseProcess 기능 활용)
        
        Args:
            count: 운송할 제품 수 (None이면 모든 제품)
            
        Returns:
            int: 실제로 운송된 제품 수
        """
        transported = self.transport_output_items(count)
        print(f"[{self.process_name}] 생산품 운송 완료: {transported}개")
        return transported
    
    def is_production_buffer_full(self):
        """
        생산 출력 버퍼가 가득 찬 상태인지 확인 (BaseProcess 기능 활용)
        
        Returns:
            bool: 버퍼가 가득 찬 경우 True
        """
        return self.is_output_buffer_full()
    
    def get_production_space_available(self):
        """
        생산 버퍼의 사용 가능한 공간 조회 (BaseProcess 기능 활용)
        
        Returns:
            int: 사용 가능한 공간 수
        """
        return self.get_available_output_space()
    
    def clear_production_buffer(self):
        """
        생산 버퍼 강제 초기화 (BaseProcess 기능 활용)
        
        Returns:
            int: 제거된 제품 수
        """
        removed = self.clear_output_buffer()
        print(f"[{self.process_name}] 생산 버퍼 강제 초기화: {removed}개 제품 제거")
        return removed
        
    def process_logic(self, input_data: Any = None) -> Generator[simpy.Event, None, Any]:
        """
        제조 공정의 핵심 로직 (SimPy generator 방식)
        
        Args:
            input_data: 입력 데이터 (제조할 제품 정보)
            
        Yields:
            simpy.Event: SimPy 이벤트들
            
        Returns:
            Any: 제조된 제품
        """
        print(f"[시간 {self.env.now:.1f}] {self.process_name} 제조 로직 시작")
        
        # 1. 자원 소비
        if not self.consume_resources(input_data):
            raise Exception("필요한 자원이 부족합니다")
        
        # 2. 제조 처리 시간 대기
        yield self.env.timeout(self.processing_time)
        
        # 3. 자원 생산
        output_resources = self.produce_resources(input_data)
        
        print(f"[시간 {self.env.now:.1f}] {self.process_name} 제조 로직 완료")
        
        return output_resources