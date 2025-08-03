from src.Processes.base_process import BaseProcess
from typing import Any, List, Generator
import simpy
from src.Resource.resource_base import Resource, ResourceRequirement, ResourceType


class ManufacturingProcess(BaseProcess):
    """제조 공정을 정의하는 클래스입니다 (SimPy 기반)."""

    def __init__(self, env: simpy.Environment, machines, workers, 
                 input_resources: List[Resource], 
                 output_resources: List[Resource],
                 resource_requirements: List[ResourceRequirement],
                 process_id: str = None, process_name: str = None,
                 processing_time: float = 2.0,
                 failure_weight_machine: float = 1.0, 
                 failure_weight_worker: float = 1.0):
        """
        제조 공정의 초기화 메서드입니다 (SimPy 환경 필수).

        :param env: SimPy 환경 객체 (필수)
        :param machines: 사용될 기계 목록 (machine 또는 worker 중 하나는 필수)
        :param workers: 작업자 목록 (machine 또는 worker 중 하나는 필수)
        :param input_resources: 입력 자원 목록 (필수)
        :param output_resources: 출력 자원 목록 (필수)
        :param resource_requirements: 자원 요구사항 목록 (필수)
        :param process_id: 공정 고유 ID (선택적)
        :param process_name: 공정 이름 (선택적)
        :param processing_time: 제조 처리 시간 (시뮬레이션 시간 단위)
        :param failure_weight_machine: 기계 고장률 가중치 (기본값: 1.0)
        :param failure_weight_worker: 작업자 실수율 가중치 (기본값: 1.0)
        """
        # BaseProcess 초기화 (자원 정보 포함)
        super().__init__(
            env=env, 
            machines=machines, 
            workers=workers, 
            process_id=process_id, 
            process_name=process_name or "제조공정",
            failure_weight_machine=failure_weight_machine,
            failure_weight_worker=failure_weight_worker,
            input_resources=input_resources,
            output_resources=output_resources,
            resource_requirements=resource_requirements
        )
        
        self.production_line = []  # 생산 라인 초기화
        self.processing_time = processing_time  # 제조 처리 시간
        
        # 제조 공정 특화 자원 설정
        self._setup_manufacturing_resources()
        
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
        """생산 라인에 제품 추가"""
        if product not in self.production_line:
            self.production_line.append(product)
            print(f"[{self.process_name}] 생산 라인에 제품 추가: {product}")
        
    def remove_from_production_line(self, product):
        """생산 라인에서 제품 제거"""
        if product in self.production_line:
            self.production_line.remove(product)
            print(f"[{self.process_name}] 생산 라인에서 제품 제거: {product}")
        
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