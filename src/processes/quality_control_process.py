from src.Processes.base_process import BaseProcess
from typing import Any, List, Generator, Dict, Union
import simpy
from src.Resource.resource_base import Resource, ResourceRequirement, ResourceType


class QualityControlProcess(BaseProcess):
    """품질 관리 공정을 정의하는 클래스입니다 (SimPy 기반)."""

    def __init__(self, env: simpy.Environment, process_id: str, process_name: str,
                 machines, workers, 
                 input_resources: Union[List[Resource], Dict[str, float], None], 
                 output_resources: Union[List[Resource], Dict[str, float], None],
                 resource_requirements: List[ResourceRequirement],
                 inspection_time: float = 1.5,
                 products_per_cycle: int = None,
                 failure_weight_machine: float = 1.0, 
                 failure_weight_worker: float = 1.0):
        """
        초기화 메서드입니다 (SimPy 환경 필수).
        
        :param env: SimPy 환경 객체 (필수)
        :param machines: 검사에 사용될 기계 목록 (machine 또는 worker 중 하나는 필수)
        :param workers: 검사 작업을 수행할 작업자 목록 (machine 또는 worker 중 하나는 필수)
        :param input_resources: 입력 자원 (List[Resource] 또는 Dict[str, float]로 자원량 지정, 예: {"검사대상": 1})
        :param output_resources: 출력 자원 (List[Resource] 또는 Dict[str, float]로 자원량 지정, 예: {"합격품": 0.9, "불합격품": 0.1})
        :param resource_requirements: 자원 요구사항 목록 (필수)
        :param process_id: 공정 고유 ID (필수)
        :param process_name: 공정 이름 (필수)
        :param inspection_time: 검사 처리 시간 (시뮬레이션 시간 단위)
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
            processing_time=inspection_time,
            products_per_cycle=products_per_cycle,
            failure_weight_machine=failure_weight_machine,
            failure_weight_worker=failure_weight_worker,
            input_resources=input_resources,
            output_resources=output_resources,
            resource_requirements=resource_requirements
        )
        
        # BaseProcess의 배치 처리 기능 활용 (inspection_line 대신)
        # self.inspection_line은 BaseProcess.current_batch로 대체됨
        self.quality_criteria = {}  # 품질 기준
        self.inspection_time = inspection_time  # 검사 시간 저장
        
        # 품질 관리 공정 특화 자원 설정 (인라인 처리)
        # 기본 자원 설정 (BaseProcess에서 처리됨)
        self._setup_default_resources()
        
        # 검사 대상 요구사항 추가 (검사할 제품)
        inspection_target_req = ResourceRequirement(
            resource_type=ResourceType.FINISHED_PRODUCT,
            name="검사대상",
            required_quantity=1.0,
            unit="개",
            is_mandatory=True
        )
        self.add_resource_requirement(inspection_target_req)
        
        # 검사 도구 요구사항 추가
        inspection_tool_req = ResourceRequirement(
            resource_type=ResourceType.TOOL,
            name="검사도구",
            required_quantity=1.0,
            unit="세트",
            is_mandatory=True
        )
        self.add_resource_requirement(inspection_tool_req)
        
        # BaseProcess의 고급 기능들 활용
        self.apply_failure_weight_to_machines()
        self.apply_failure_weight_to_workers()
        
    def add_to_inspection_line(self, product):
        """
        검사 라인에 제품 추가 (BaseProcess의 배치 기능 활용)
        
        Args:
            product: 추가할 제품
            
        Returns:
            bool: 배치에 추가 성공 여부
        """
        success = self.add_to_batch(product)
        if success:
            print(f"[{self.process_name}] 검사 라인에 제품 추가: {product} (배치: {len(self.current_batch)}/{self.batch_size})")
        else:
            print(f"[{self.process_name}] 배치가 가득 참. 현재 배치를 먼저 처리하세요.")
        return success
    
    def get_inspection_line_status(self):
        """
        검사 라인 상태 조회 (BaseProcess의 배치 상태 활용)
        
        Returns:
            Dict: 검사 라인 상태 정보
        """
        return {
            'products_in_line': self.get_current_batch(),
            'batch_status': self.get_batch_status(),
            'is_batch_ready': self.is_batch_ready(),
            'process_info': self.get_process_info(),
            'quality_criteria': self.quality_criteria
        }
    
    def set_inspection_batch_size(self, batch_size: int):
        """
        검사 배치 크기 설정
        
        Args:
            batch_size: 배치 크기 (1 이상)
        """
        self.batch_size = max(1, batch_size)
        self.enable_batch_processing = batch_size > 1
        print(f"[{self.process_name}] 검사 배치 크기 설정: {self.batch_size}")
    
    def add_inspection_condition(self, condition):
        """
        검사 실행 조건 추가 (BaseProcess 기능 활용)
        
        Args:
            condition: 실행 조건 함수
        """
        return self.add_execution_condition(condition)
    
    def set_parallel_inspection(self, safe: bool):
        """
        병렬 검사 안전성 설정 (BaseProcess 기능 활용)
        
        Args:
            safe: 병렬 실행 안전 여부
        """
        return self.set_parallel_safe(safe)
    
    # ========== 품질검사 특화 출하품 Transport 관리 ==========
    
    def set_inspection_output_buffer(self, capacity: int) -> 'QualityControlProcess':
        """
        검사 출력 버퍼 용량 설정 (BaseProcess 기능 활용)
        
        Args:
            capacity: 출력 버퍼 용량
            
        Returns:
            QualityControlProcess: 자기 자신 (메서드 체이닝용)
        """
        self.set_output_buffer_capacity(capacity)
        return self
    
    def transport_inspected_products(self, count: int = None) -> int:
        """
        검사된 제품들을 운송 (BaseProcess 기능 활용)
        
        Args:
            count: 운송할 제품 수 (None이면 모든 제품)
            
        Returns:
            int: 실제로 운송된 제품 수
        """
        transported = self.transport_output_items(count)
        print(f"[{self.process_name}] 검사품 운송 완료: {transported}개")
        return transported
    
    def get_inspection_buffer_status(self) -> Dict[str, Any]:
        """
        검사 버퍼 상태 조회 (BaseProcess 기능 활용)
        
        Returns:
            Dict: 검사 버퍼 상태 정보
        """
        buffer_status = self.get_output_buffer_status()
        return {
            'inspection_buffer': buffer_status,
            'products_in_buffer': buffer_status['current_count'],
            'buffer_capacity': buffer_status['capacity'],
            'inspection_blocked': buffer_status['waiting_for_transport'],
            'batch_info': self.get_batch_status(),
            'quality_criteria': self.quality_criteria
        }
    
    def is_inspection_blocked(self) -> bool:
        """
        검사가 출하 대기로 막혀있는지 확인 (BaseProcess 기능 활용)
        
        Returns:
            bool: 검사가 막혀있으면 True
        """
        return self.waiting_for_transport or self.is_output_buffer_full()
    
    def enable_inspection_blocking(self, enable: bool = True) -> 'QualityControlProcess':
        """
        검사 blocking 기능 활성화/비활성화 (BaseProcess 기능 활용)
        
        Args:
            enable: blocking 활성화 여부
            
        Returns:
            QualityControlProcess: 자기 자신 (메서드 체이닝용)
        """
        self.enable_output_blocking_feature(enable)
        return self
        
    def start_inspection(self):
        """품질 검사 시작"""
        print(f"[{self.process_name}] 품질 검사 시작")
        
    def inspect_product(self, product):
        """제품 검사"""
        print(f"[{self.process_name}] 제품 검사 중: {product}")
        
    def clear_inspection_line(self):
        """
        검사 라인 정리 (BaseProcess의 배치 기능 활용)
        """
        self.current_batch.clear()
        print(f"[{self.process_name}] 검사 라인 정리 완료")
        
    def get_inspection_queue_count(self):
        """
        검사 대기열 개수 조회 (BaseProcess 기능 활용)
        
        Returns:
            int: 현재 배치의 아이템 수
        """
        return len(self.current_batch)
        
    def set_quality_criteria(self, criteria: dict):
        """품질 기준 설정"""
        self.quality_criteria = criteria
        print(f"[{self.process_name}] 품질 기준 설정: {criteria}")
        
    def evaluate_quality(self, product_data: Any) -> dict:
        """품질 평가"""
        # 품질 평가 로직 구현
        quality_score = 0.95  # 예시 점수
        is_passed = quality_score >= 0.9
        
        return {
            'product': product_data,
            'quality_score': quality_score,
            'is_passed': is_passed,
            'defects': [] if is_passed else ['minor_defect']
        }
        
    def process_logic(self, input_data: Any = None) -> Generator[simpy.Event, None, Any]:
        """
        품질 관리 공정의 핵심 로직 (SimPy generator 방식)
        
        Args:
            input_data: 입력 데이터 (검사할 제품 정보)
            
        Yields:
            simpy.Event: SimPy 이벤트들
            
        Returns:
            Any: 품질 검사 결과
        """
        print(f"[시간 {self.env.now:.1f}] {self.process_name} 검사 로직 시작")
        
        # 1. 검사 대상 확인
        if not self._validate_inspection_target(input_data):
            raise Exception("검사 대상이 유효하지 않습니다")
        
        # 2. 검사 처리 시간 대기
        yield self.env.timeout(self.inspection_time)
        
        # 3. 품질 평가
        quality_result = self.evaluate_quality(input_data)
        
        print(f"[시간 {self.env.now:.1f}] {self.process_name} 검사 로직 완료")
        
        return quality_result
        
    def _validate_inspection_target(self, input_data: Any) -> bool:
        """검사 대상 유효성 검사"""
        # 검사 대상 검증 로직 구현
        return input_data is not None