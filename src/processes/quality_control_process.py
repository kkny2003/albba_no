from src.Processes.base_process import BaseProcess
from typing import Any, List, Generator
import simpy
from src.Resource.resource_base import Resource, ResourceRequirement, ResourceType


class QualityControlProcess(BaseProcess):
    """품질 관리 공정을 정의하는 클래스입니다 (SimPy 기반)."""

    def __init__(self, env: simpy.Environment, machines, workers, 
                 input_resources: List[Resource], 
                 output_resources: List[Resource],
                 resource_requirements: List[ResourceRequirement],
                 process_id: str = None, process_name: str = None,
                 inspection_time: float = 1.5,
                 failure_weight_machine: float = 1.0, 
                 failure_weight_worker: float = 1.0):
        """
        초기화 메서드입니다 (SimPy 환경 필수).
        
        :param env: SimPy 환경 객체 (필수)
        :param machines: 검사에 사용될 기계 목록 (machine 또는 worker 중 하나는 필수)
        :param workers: 검사 작업을 수행할 작업자 목록 (machine 또는 worker 중 하나는 필수)
        :param input_resources: 입력 자원 목록 (필수)
        :param output_resources: 출력 자원 목록 (필수)
        :param resource_requirements: 자원 요구사항 목록 (필수)
        :param process_id: 공정 고유 ID (선택적)
        :param process_name: 공정 이름 (선택적)
        :param inspection_time: 검사 처리 시간 (시뮬레이션 시간 단위)
        :param failure_weight_machine: 기계 고장률 가중치 (기본값: 1.0)
        :param failure_weight_worker: 작업자 실수율 가중치 (기본값: 1.0)
        """
        # BaseProcess 초기화 (자원 정보 포함)
        super().__init__(
            env=env, 
            machines=machines, 
            workers=workers, 
            process_id=process_id, 
            process_name=process_name or "품질관리공정",
            failure_weight_machine=failure_weight_machine,
            failure_weight_worker=failure_weight_worker,
            input_resources=input_resources,
            output_resources=output_resources,
            resource_requirements=resource_requirements
        )
        
        self.inspection_line = []  # 검사 라인 초기화
        self.inspection_time = inspection_time  # 검사 처리 시간
        self.quality_criteria = {}  # 품질 기준
        
        # 품질 관리 공정 특화 자원 설정
        self._setup_quality_control_resources()
        
    def _setup_quality_control_resources(self):
        """품질 관리 공정용 자원 요구사항을 설정하는 메서드"""
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
        
    def add_to_inspection_line(self, product):
        """검사 라인에 제품 추가"""
        if product not in self.inspection_line:
            self.inspection_line.append(product)
            print(f"[{self.process_name}] 검사 라인에 제품 추가: {product}")
        
    def start_inspection(self):
        """품질 검사 시작"""
        print(f"[{self.process_name}] 품질 검사 시작")
        
    def inspect_product(self, product):
        """제품 검사"""
        print(f"[{self.process_name}] 제품 검사 중: {product}")
        
    def clear_inspection_line(self):
        """검사 라인 정리"""
        self.inspection_line.clear()
        print(f"[{self.process_name}] 검사 라인 정리 완료")
        
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