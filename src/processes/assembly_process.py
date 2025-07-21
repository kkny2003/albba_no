from src.processes.base_process import BaseProcess
from typing import Any, List, Generator
import simpy
from src.Resource.helper import Resource, ResourceRequirement, ResourceType


class AssemblyProcess(BaseProcess):
    """조립 공정을 정의하는 클래스입니다 (SimPy 기반)."""

    def __init__(self, env: simpy.Environment, machines, workers, 
                 input_resources: List[Resource], 
                 output_resources: List[Resource],
                 resource_requirements: List[ResourceRequirement],
                 process_id: str = None, process_name: str = None,
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
        # BaseProcess 초기화 (machines와 workers 전달)
        super().__init__(env, machines, workers, process_id, process_name or "조립공정",
                        failure_weight_machine=failure_weight_machine,
                        failure_weight_worker=failure_weight_worker)
        self.assembly_line = []   # 조립 라인 초기화
        self.assembly_time = assembly_time  # 조립 처리 시간
        
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
        
    def process_logic(self, input_data: Any = None) -> Generator[simpy.Event, None, Any]:
        """
        구체적인 조립 공정 로직을 실행하는 SimPy generator 메서드입니다.
        
        Args:
            input_data: 조립할 제품 데이터
            
        Yields:
            simpy.Event: SimPy 이벤트들
            
        Returns:
            Any: 조립 로직 실행 결과
        """
        print(f"[시간 {self.env.now:.1f}] [{self.process_name}] 조립 로직 실행 중...")
        
        # 조립 작업 시작
        self.start_assembly()
        
        # SimPy timeout을 사용하여 조립 시간 시뮬레이션
        print(f"[시간 {self.env.now:.1f}] [{self.process_name}] 조립 작업 진행 중... (예상 시간: {self.assembly_time})")
        yield self.env.timeout(self.assembly_time)
        
        # 실제 조립 로직 (예시)
        assembled_product = f"조립완료_{input_data}" if input_data else "조립완료_기본제품"
        
        print(f"[시간 {self.env.now:.1f}] [{self.process_name}] 조립 로직 실행 완료: {assembled_product}")
        return assembled_product