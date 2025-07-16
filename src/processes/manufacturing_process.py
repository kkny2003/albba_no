from .base_process import BaseProcess
from typing import Any, List, Generator
import simpy
from Resource.helper import Resource, ResourceRequirement, ResourceType


class ManufacturingProcess(BaseProcess):
    """제조 공정을 정의하는 클래스입니다 (SimPy 기반)."""

    def __init__(self, env: simpy.Environment, machines, workers, 
                 input_resources: List[Resource], 
                 output_resources: List[Resource],
                 resource_requirements: List[ResourceRequirement],
                 process_id: str = None, process_name: str = None,
                 processing_time: float = 2.0):
        """
        제조 공정의 초기화 메서드입니다 (SimPy 환경 필수).

        :param env: SimPy 환경 객체 (필수)
        :param machines: 사용될 기계 목록
        :param workers: 작업자 목록
        :param input_resources: 입력 자원 목록 (필수)
        :param output_resources: 출력 자원 목록 (필수)
        :param resource_requirements: 자원 요구사항 목록 (필수)
        :param process_id: 공정 고유 ID (선택적)
        :param process_name: 공정 이름 (선택적)
        :param processing_time: 제조 처리 시간 (시뮬레이션 시간 단위)
        """
        super().__init__(env, process_id, process_name or "제조공정")
        self.machines = machines  # 기계 목록
        self.workers = workers    # 작업자 목록
        self.production_line = []  # 생산 라인 초기화
        self.processing_time = processing_time  # 제조 처리 시간
        
        # 필수 자원 정보 설정
        self._setup_resources(input_resources, output_resources, resource_requirements)
        
    def _setup_resources(self, input_resources: List[Resource], 
                        output_resources: List[Resource],
                        resource_requirements: List[ResourceRequirement]):
        """필수 자원 정보를 설정하는 메서드"""
        # 입력 자원 설정
        for resource in input_resources:
            self.add_input_resource(resource)
        
        # 출력 자원 설정  
        for resource in output_resources:
            self.add_output_resource(resource)
                
        # 자원 요구사항 설정
        for requirement in resource_requirements:
            self.add_resource_requirement(requirement)
        
    def _setup_default_resources(self):
        """기본 자원 요구사항을 설정하는 메서드"""
        # 기계 자원 추가
        for i, machine in enumerate(self.machines):
            machine_resource = Resource(
                resource_id=f"machine_{i}",
                name=f"기계_{i+1}",
                resource_type=ResourceType.MACHINE,
                quantity=1.0,
                unit="대"
            )
            self.add_input_resource(machine_resource)
            
        # 작업자 자원 추가
        for i, worker in enumerate(self.workers):
            worker_resource = Resource(
                resource_id=f"worker_{i}",
                name=f"작업자_{i+1}",
                resource_type=ResourceType.WORKER,
                quantity=1.0,
                unit="명"
            )
            self.add_input_resource(worker_resource)
            
        # 원자재 요구사항 추가 (예시)
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
        
        # 기본 출력 자원 설정 (반제품)
        semi_finished_product = Resource(
            resource_id="semi_finished_001",
            name="반제품",
            resource_type=ResourceType.SEMI_FINISHED,
            quantity=1.0,
            unit="개"
        )
        self.add_output_resource(semi_finished_product)

    def start_process(self):
        """제조 공정을 시작하는 메서드입니다."""
        # 공정 시작 로직 구현
        print("제조 공정이 시작되었습니다.")

    def stop_process(self):
        """제조 공정을 중지하는 메서드입니다."""
        # 공정 중지 로직 구현
        print("제조 공정이 중지되었습니다.")

    def add_to_production_line(self, product):
        """
        생산 라인에 제품을 추가하는 메서드입니다.

        :param product: 추가할 제품
        """
        self.production_line.append(product)  # 제품 추가
        print(f"{product}가 생산 라인에 추가되었습니다.")

    def remove_from_production_line(self, product):
        """
        생산 라인에서 제품을 제거하는 메서드입니다.

        :param product: 제거할 제품
        """
        if product in self.production_line:
            self.production_line.remove(product)  # 제품 제거
            print(f"{product}가 생산 라인에서 제거되었습니다.")
        else:
            print(f"{product}는 생산 라인에 없습니다.")

    def execute(self, input_data: Any = None) -> Any:
        """
        제조 공정을 실행하는 메서드입니다.

        Args:
            input_data: 제조할 제품 데이터 (선택적)

        Returns:
            Any: 제조 완료된 제품 데이터와 생산된 자원
        """
        print(f"[{self.process_name}] 제조 공정 실행 시작")

        # 입력 데이터가 있으면 생산 라인에 추가
        if input_data is not None:
            self.add_to_production_line(input_data)

        # 부모 클래스의 execute 메서드 호출 (자원 관리 포함)
        return super().execute(input_data)
        
    def process_logic(self, input_data: Any = None) -> Generator[simpy.Event, None, Any]:
        """
        구체적인 제조 공정 로직을 실행하는 SimPy generator 메서드입니다.

        Args:
            input_data: 제조할 제품 데이터

        Yields:
            simpy.Event: SimPy 이벤트들

        Returns:
            Any: 제조 로직 실행 결과
        """
        print(f"[시간 {self.env.now:.1f}] [{self.process_name}] 제조 로직 실행 중...")
        
        # 제조 공정 시작
        self.start_process()
        
        # SimPy timeout을 사용하여 제조 시간 시뮬레이션
        print(f"[시간 {self.env.now:.1f}] [{self.process_name}] 제조 작업 진행 중... (예상 시간: {self.processing_time})")
        yield self.env.timeout(self.processing_time)
        
        # 실제 제조 로직 (예시)
        manufactured_product = f"제조완료_{input_data}" if input_data else "제조완료_기본제품"
        
        print(f"[시간 {self.env.now:.1f}] [{self.process_name}] 제조 로직 실행 완료: {manufactured_product}")
        return manufactured_product