from .base_process import BaseProcess
from typing import Any, List
from ..models.resource import Resource, ResourceRequirement, ResourceType


class AssemblyProcess(BaseProcess):
    """조립 공정을 정의하는 클래스입니다."""

    def __init__(self, machines, workers, process_id: str = None, process_name: str = None):
        """
        초기화 메서드입니다.
        
        :param machines: 조립에 사용될 기계 목록
        :param workers: 조립 작업을 수행할 작업자 목록
        :param process_id: 공정 고유 ID (선택적)
        :param process_name: 공정 이름 (선택적)
        """
        super().__init__(process_id, process_name or "조립공정")
        self.machines = machines  # 기계 목록
        self.workers = workers    # 작업자 목록
        self.assembly_line = []   # 조립 라인 초기화
        
        # 조립 공정용 자원 설정
        self._setup_assembly_resources()
        
    def _setup_assembly_resources(self):
        """조립 공정용 자원 요구사항을 설정하는 메서드"""
        # 기계 자원 추가
        for i, machine in enumerate(self.machines):
            machine_resource = Resource(
                resource_id=f"assembly_machine_{i}",
                name=f"조립기계_{i+1}",
                resource_type=ResourceType.MACHINE,
                quantity=1.0,
                unit="대"
            )
            self.add_input_resource(machine_resource)
            
        # 작업자 자원 추가
        for i, worker in enumerate(self.workers):
            worker_resource = Resource(
                resource_id=f"assembly_worker_{i}",
                name=f"조립작업자_{i+1}",
                resource_type=ResourceType.WORKER,
                quantity=1.0,
                unit="명"
            )
            self.add_input_resource(worker_resource)
            
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
        
        # 운송 자원 요구사항 추가 (반제품 운반용)
        transport_req = ResourceRequirement(
            resource_type=ResourceType.TRANSPORT,
            name="운송장비",
            required_quantity=1.0,
            unit="대",
            is_mandatory=False  # 선택적 (수동 운반도 가능)
        )
        self.add_resource_requirement(transport_req)
        
        # 기본 조립도구 자원 추가
        assembly_tool = Resource(
            resource_id="assembly_tool_001",
            name="조립도구",
            resource_type=ResourceType.TOOL,
            quantity=1.0,
            unit="세트"
        )
        self.add_input_resource(assembly_tool)
        
        # 완제품 출력 자원 설정
        finished_product = Resource(
            resource_id="finished_product_001",
            name="완제품",
            resource_type=ResourceType.FINISHED_PRODUCT,
            quantity=1.0,
            unit="개"
        )
        self.add_output_resource(finished_product)

    def add_to_assembly_line(self, product):
        """
        조립 라인에 제품을 추가하는 메서드입니다.
        
        :param product: 조립할 제품
        """
        self.assembly_line.append(product)  # 제품 추가
        print(f"제품 {product}이(가) 조립 라인에 추가되었습니다.")

    def start_assembly(self):
        """조립 작업을 시작하는 메서드입니다."""
        for product in self.assembly_line:
            self.assemble_product(product)  # 각 제품 조립

    def assemble_product(self, product):
        """
        제품을 조립하는 메서드입니다.
        
        :param product: 조립할 제품
        """
        print(f"제품 {product}을(를) 조립 중입니다...")
        # 조립 로직을 여기에 추가합니다.
        # 예: 기계 사용, 작업자 할당 등
        print(f"제품 {product} 조립 완료!")

    def clear_assembly_line(self):
        """조립 라인을 비우는 메서드입니다."""
        self.assembly_line.clear()  # 조립 라인 초기화
        print("조립 라인이 비워졌습니다.")

    def execute(self, input_data: Any = None) -> Any:
        """
        조립 공정을 실행하는 메서드입니다.
        
        Args:
            input_data: 조립할 제품 데이터 (선택적)
            
        Returns:
            Any: 조립 완료된 제품 데이터와 생산된 자원
        """
        print(f"[{self.process_name}] 조립 공정 실행 시작")
        
        # 입력 데이터가 있으면 조립 라인에 추가
        if input_data is not None:
            self.add_to_assembly_line(input_data)
        
        # 부모 클래스의 execute 메서드 호출 (자원 관리 포함)
        return super().execute(input_data)
        
    def process_logic(self, input_data: Any = None) -> Any:
        """
        구체적인 조립 공정 로직을 실행하는 메서드입니다.
        
        Args:
            input_data: 조립할 제품 데이터
            
        Returns:
            Any: 조립 로직 실행 결과
        """
        print(f"[{self.process_name}] 조립 로직 실행 중...")
        
        # 조립 작업 시작
        self.start_assembly()
        
        # 실제 조립 로직 (예시)
        assembled_product = f"조립완료_{input_data}" if input_data else "조립완료_기본제품"
        
        print(f"[{self.process_name}] 조립 로직 실행 완료: {assembled_product}")
        return assembled_product