from src.Processes.base_process import BaseProcess
from typing import Any, List, Generator
import simpy
from src.Resource.resource_base import Resource, ResourceRequirement, ResourceType


class AssemblyProcess(BaseProcess):
    """조립 공정을 정의하는 클래스입니다 (SimPy 기반)."""

    def __init__(self, env: simpy.Environment, process_id: str, process_name: str,
                 machines, workers, 
                 input_resources: List[Resource], 
                 output_resources: List[Resource],
                 resource_requirements: List[ResourceRequirement],
                 assembly_time: float = 3.0,
                 failure_weight_machine: float = 1.0, 
                 failure_weight_worker: float = 1.0):
        """
        초기화 메서드입니다 (SimPy 환경 필수).
        
        :param env: SimPy 환경 객체 (필수)
        :param machines: 조립에 사용될 기계 목록 (machine 또는 worker 중 하나는 필수)
        :param workers: 조립 작업을 수행할 작업자 목록 (machine 또는 worker 중 하나는 필수)
        :param input_resources: 입력 자원 목록 (필수)
        :param output_resources: 출력 자원 목록 (필수)
        :param resource_requirements: 자원 요구사항 목록 (필수)
        :param process_id: 공정 고유 ID (선택적)
        :param process_name: 공정 이름 (선택적)
        :param assembly_time: 조립 처리 시간 (시뮬레이션 시간 단위)
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
            processing_time=assembly_time,
            failure_weight_machine=failure_weight_machine,
            failure_weight_worker=failure_weight_worker,
            input_resources=input_resources,
            output_resources=output_resources,
            resource_requirements=resource_requirements
        )
        
        self.assembly_line = []   # 조립 라인 초기화
        self.assembly_time = assembly_time  # 조립 처리 시간
        
        # 조립 공정 특화 자원 설정
        self._setup_assembly_resources()
        
    def _setup_assembly_resources(self):
        """조립 공정용 자원 요구사항을 설정하는 메서드"""
        # 기본 자원 설정 (BaseProcess에서 처리됨)
        self._setup_default_resources()
        
        # 반제품 요구사항 추가 (조립용 입력)
        semi_finished_req = ResourceRequirement(
            resource_type=ResourceType.SEMI_FINISHED,
            name="반제품",
            required_quantity=2.0,  # 조립을 위해 2개의 반제품 필요
            unit="개",
            is_mandatory=True
        )
        self.add_resource_requirement(semi_finished_req)
        
        # 도구 요구사항 추가
        tool_req = ResourceRequirement(
            resource_type=ResourceType.TOOL,
            name="조립도구",
            required_quantity=1.0,
            unit="세트",
            is_mandatory=True
        )
        self.add_resource_requirement(tool_req)
        
    def add_to_assembly_line(self, product):
        """조립 라인에 제품 추가"""
        if product not in self.assembly_line:
            self.assembly_line.append(product)
            print(f"[{self.process_name}] 조립 라인에 제품 추가: {product}")
        
    def start_assembly(self):
        """조립 공정 시작"""
        print(f"[{self.process_name}] 조립 공정 시작")
        
    def assemble_product(self, product):
        """제품 조립"""
        print(f"[{self.process_name}] 제품 조립 중: {product}")
        
    def clear_assembly_line(self):
        """조립 라인 정리"""
        self.assembly_line.clear()
        print(f"[{self.process_name}] 조립 라인 정리 완료")
        
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
        yield self.env.timeout(self.assembly_time)
        
        # 3. 완제품 생성
        assembled_product = self._create_finished_product(input_data)
        
        print(f"[시간 {self.env.now:.1f}] {self.process_name} 조립 로직 완료")
        
        return assembled_product
        
    def _validate_semi_finished_products(self, input_data: Any) -> bool:
        """반제품 유효성 검사"""
        # 반제품 검증 로직 구현
        return True
        
    def _create_finished_product(self, input_data: Any) -> Any:
        """완제품 생성"""
        # 완제품 생성 로직 구현
        return f"조립완료_{input_data}" if input_data else "조립완료_기본제품"