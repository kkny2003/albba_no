from src.processes.base_process import BaseProcess
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
        # BaseProcess 초기화 (machines와 workers 전달)
        super().__init__(env, machines, workers, process_id, process_name or "제조공정",
                        failure_weight_machine=failure_weight_machine,
                        failure_weight_worker=failure_weight_worker)
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
                properties={"unit": "대"}
            )
            self.add_input_resource(machine_resource)
            
        # 작업자 자원 추가
        for i, worker in enumerate(self.workers):
            worker_resource = Resource(
                resource_id=f"worker_{i}",
                name=f"작업자_{i+1}",
                resource_type=ResourceType.WORKER,
                properties={"unit": "명"}
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
            properties={"unit": "개"}
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

    def execute(self, input_data: Any = None) -> Generator[simpy.Event, None, Any]:
        """
        제조 공정을 실행하는 메서드입니다.

        Args:
            input_data: 제조할 제품 데이터 (선택적)

        Yields:
            simpy.Event: SimPy 이벤트들

        Returns:
            Any: 제조 완료된 제품 데이터와 생산된 자원
        """
        print(f"[{self.process_name}] 제조 공정 실행 시작")

        # 입력 데이터가 있으면 생산 라인에 추가
        if input_data is not None:
            self.add_to_production_line(input_data)

        # 부모 클래스의 execute 메서드 호출 (자원 관리 포함)
        result = yield from super().execute(input_data)
        return result
        
    def process_logic(self, input_data: Any = None) -> Generator[simpy.Event, None, Any]:
        """
        구체적인 제조 공정 로직을 실행하는 SimPy generator 메서드입니다.
        (AllOf를 활용한 병렬 자원 대기로 개선)

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

        # 🚀 개선: AllOf를 사용한 병렬 자원 대기
        resource_requests = []
        
        # 기계 자원 요청 (병렬)
        machine_requests = []
        for i, machine in enumerate(self.machines):
            if hasattr(machine, 'resource'):
                req = machine.resource.request()
                machine_requests.append(req)
                resource_requests.append(req)
                print(f"[시간 {self.env.now:.1f}] [{self.process_name}] 기계 {i+1} 자원 요청")
        
        # 작업자 자원 요청 (병렬)
        worker_requests = []
        for i, worker in enumerate(self.workers):
            if hasattr(worker, 'resource'):
                req = worker.resource.request()
                worker_requests.append(req)
                resource_requests.append(req)
                print(f"[시간 {self.env.now:.1f}] [{self.process_name}] 작업자 {i+1} 자원 요청")
        
        # 🎯 모든 자원이 준비될 때까지 병렬 대기 (기존 순차 대기 개선)
        if resource_requests:
            print(f"[시간 {self.env.now:.1f}] [{self.process_name}] 모든 자원 준비 대기 중... ({len(resource_requests)}개 자원)")
            all_resources_ready = simpy.AllOf(self.env, resource_requests)
            yield all_resources_ready  # 모든 자원이 동시에 준비되면 진행
            print(f"[시간 {self.env.now:.1f}] [{self.process_name}] 모든 자원 준비 완료! 제조 시작")
        
        # SimPy timeout을 사용하여 제조 시간 시뮬레이션
        print(f"[시간 {self.env.now:.1f}] [{self.process_name}] 제조 작업 진행 중... (예상 시간: {self.processing_time})")
        yield self.env.timeout(self.processing_time)
        
        # 실제 제조 로직 (예시)
        manufactured_product = f"제조완료_{input_data}" if input_data else "제조완료_기본제품"
        
        # 자원 해제 (자동 해제되지만 명시적 표시)
        for req in machine_requests:
            print(f"[시간 {self.env.now:.1f}] [{self.process_name}] 기계 자원 해제")
        for req in worker_requests:
            print(f"[시간 {self.env.now:.1f}] [{self.process_name}] 작업자 자원 해제")
        
        print(f"[시간 {self.env.now:.1f}] [{self.process_name}] 제조 로직 실행 완료 (병렬 처리): {manufactured_product}")
        return manufactured_product