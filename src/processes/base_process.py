"""
기본 공정 클래스를 관리하는 모듈입니다.
모든 제조 공정의 기본이 되는 클래스와 공통 기능을 제공합니다.
Flow 관련 기능은 별도의 Flow 모듈로 분리되었습니다.
"""

from typing import List, Optional, Any, Union, Dict, Callable, Tuple, Generator
from abc import ABC, abstractmethod
import uuid
import simpy
from src.Resource.resource_base import Resource, ResourceRequirement, ResourceType


class BaseProcess(ABC):
    """모든 제조 공정의 기본이 되는 추상 클래스 (SimPy 기반, 배치 처리 지원)"""
    
    def __init__(self, env: simpy.Environment, process_id: str, process_name: str, 
                 machines=None, workers=None, processing_time: float = 1.0, batch_size: int = 1,
                 products_per_cycle: int = None,
                 failure_weight_machine: float = 1.0, failure_weight_worker: float = 1.0,
                 input_resources: Union[List[Resource], Dict[str, float], None] = None, 
                 output_resources: Union[List[Resource], Dict[str, float], None] = None,
                 resource_requirements: List[ResourceRequirement] = None):
        """
        기본 공정 초기화 (SimPy 환경 필수, machine 또는 worker 중 하나는 필수)
        
        Args:
            env: SimPy 환경 객체 (필수)
            process_id: 공정 고유 ID (필수)
            process_name: 공정 이름 (필수)
            machines: 사용할 기계 리스트 (machine 또는 worker 중 하나는 필수)
            workers: 사용할 작업자 리스트 (machine 또는 worker 중 하나는 필수)
            processing_time: 처리 시간 (시뮬레이션 시간 단위, 기본값: 1.0)
            batch_size: 배치 크기 (한번에 처리할 아이템 수, 기본값: 1)
            products_per_cycle: 한번 공정 실행 시 생산되는 제품 수 (None이면 batch_size와 동일, 기본값: None)
            failure_weight_machine: 기계 고장률 가중치 (기본값: 1.0, 1.5 = 1.5배 고장률)
            failure_weight_worker: 작업자 실수율 가중치 (기본값: 1.0, 1.5 = 1.5배 실수율)
            input_resources: 입력 자원 (List[Resource] 또는 Dict[str, float]로 자원량 지정, 예: {"철강": 1.3, "플라스틱": 2.0})
            output_resources: 출력 자원 (List[Resource] 또는 Dict[str, float]로 자원량 지정, 예: {"완제품": 1.5, "부품": 0.8})
            resource_requirements: 자원 요구사항 목록 (필수)
            
        Raises:
            ValueError: machine과 worker가 모두 None인 경우
            ValueError: process_id 또는 process_name이 None인 경우
        """
        # 필수 파라미터 검증
        if process_id is None:
            raise ValueError("process_id는 필수 파라미터입니다.")
        if process_name is None:
            raise ValueError("process_name은 필수 파라미터입니다.")
        
        # machine 또는 worker 중 하나는 필수로 있어야 함
        if machines is None and workers is None:
            raise ValueError(f"공정 '{process_name}'에는 machine 또는 worker 중 하나 이상이 필요합니다.")
        
        self.env = env  # SimPy 환경 객체 (필수)
        self.process_id = process_id  # 고유 ID (필수)
        self.process_name = process_name  # 공정 이름 (필수)
        self.next_processes = []  # 다음 공정들의 리스트
        self.previous_processes = []  # 이전 공정들의 리스트
        
        # 기계와 작업자 설정 (필수 요소)
        self.machines = machines or []  # 기계 리스트
        self.workers = workers or []   # 작업자 리스트
        
        # 초기화 검증 메시지 출력
        resource_info = []
        if self.machines:
            machine_ids = [getattr(m, 'resource_id', str(m)) for m in self.machines]
            resource_info.append(f"기계: {', '.join(machine_ids)}")
        if self.workers:
            worker_ids = [getattr(w, 'resource_id', str(w)) for w in self.workers]
            resource_info.append(f"작업자: {', '.join(worker_ids)}")
        
        print(f"[{self.process_name}] 공정 초기화 완료 - {' / '.join(resource_info)}")
        
        # 고장률 가중치 설정
        self.failure_weight_machine = failure_weight_machine  # 기계 고장률 가중치
        self.failure_weight_worker = failure_weight_worker    # 작업자 실수율 가중치
        
        # 배치 처리 설정
        self.batch_size = max(1, batch_size)  # 최소 1개 이상
        self.enable_batch_processing = batch_size > 1  # 배치 처리 활성화 여부
        self.current_batch = []  # 현재 배치에 축적된 아이템들
        
        # 출력 생산량 설정 (한번 공정 실행 시 생산되는 제품 수)
        self.products_per_cycle = products_per_cycle if products_per_cycle is not None else self.batch_size
        print(f"[{self.process_name}] 한번 실행당 생산량: {self.products_per_cycle}개")
        
        # 자원 관리 관련 속성들
        self.input_resources: List[Resource] = []  # 입력 자원 리스트
        self.output_resources: List[Resource] = []  # 출력 자원 리스트
        self.resource_requirements: List[ResourceRequirement] = []  # 자원 요구사항
        self.current_input_inventory: Dict[str, Resource] = {}  # 현재 입력 자원 재고
        self.current_output_inventory: Dict[str, Resource] = {}  # 현재 출력 자원 재고
        
        # 출하품 관리 및 blocking 기능 (생산량 기준으로 설정)
        self.output_buffer_capacity: int = self.products_per_cycle  # 출력 버퍼 최대 용량 = 한번 실행당 생산량
        self.current_output_count: int = 0  # 현재 출력 버퍼에 쌓인 개수
        self.enable_output_blocking: bool = True  # 출력 blocking 활성화 여부
        self.transport_ready_event: Optional[simpy.Event] = None  # 운송 준비 완료 이벤트
        self.waiting_for_transport: bool = False  # 운송 대기 상태
        
        # 고급 워크플로우 지원을 위한 새로운 속성들
        self.conditions: List[Callable[[Any], bool]] = []  # 실행 조건들
        self.parallel_safe: bool = True  # 병렬 실행 안전 여부
        self.resource_manager = None  # 고급 자원 관리자 (필요시 설정)
        
        # SimPy 관련 속성들
        self.processing_time: float = processing_time  # 처리 시간 (시뮬레이션 시간 단위)
        
        # 자원 설정 (개선된 통합 로직)
        self._setup_resources(input_resources, output_resources, resource_requirements)
        
    def _setup_resources(self, input_resources: Union[List[Resource], Dict[str, float], None], 
                        output_resources: Union[List[Resource], Dict[str, float], None],
                        resource_requirements: List[ResourceRequirement]):
        """
        자원 정보를 설정하는 통합 메서드 (모든 프로세스에서 공통 사용)
        
        Args:
            input_resources: 입력 자원 (List[Resource], Dict[str, float], 또는 None)
            output_resources: 출력 자원 (List[Resource], Dict[str, float], 또는 None)
            resource_requirements: 자원 요구사항 목록
        """
        # 입력 자원 설정
        if input_resources is not None:
            if isinstance(input_resources, dict):
                # 딕셔너리가 입력된 경우 자원별로 생성
                for resource_name, quantity in input_resources.items():
                    input_resource = Resource(
                        resource_id=f"input_{resource_name}",
                        name=resource_name,
                        properties={"quantity": float(quantity), "unit": "단위"}
                    )
                    self.add_input_resource(input_resource)
                print(f"[{self.process_name}] 입력자원 생성: {input_resources}")
            elif isinstance(input_resources, list):
                # 기존 List[Resource] 처리
                for resource in input_resources:
                    self.add_input_resource(resource)
        
        # 출력 자원 설정  
        if output_resources is not None:
            if isinstance(output_resources, dict):
                # 딕셔너리가 입력된 경우 자원별로 생성
                for resource_name, quantity in output_resources.items():
                    output_resource = Resource(
                        resource_id=f"output_{resource_name}",
                        name=resource_name,
                        properties={"quantity": float(quantity), "unit": "개"}
                    )
                    self.add_output_resource(output_resource)
                print(f"[{self.process_name}] 출력자원 생성: {output_resources}")
            elif isinstance(output_resources, list):
                # 기존 List[Resource] 처리
                for resource in output_resources:
                    self.add_output_resource(resource)
                
        # 자원 요구사항 설정
        if resource_requirements is not None:
            for requirement in resource_requirements:
                self.add_resource_requirement(requirement)
        
    def _setup_default_resources(self):
        """
        기본 자원 요구사항을 설정하는 메서드 (각 프로세스별로 오버라이드 가능)
        """
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
        
    def validate_resources(self) -> bool:
        """
        공정에 필요한 자원(machine/worker)이 올바르게 설정되었는지 검증
        
        Returns:
            bool: 자원 설정이 유효한 경우 True
            
        Raises:
            ValueError: 필수 자원이 누락된 경우
        """
        if not self.machines and not self.workers:
            raise ValueError(f"공정 '{self.process_name}'에는 machine 또는 worker 중 하나 이상이 필요합니다.")
        
        # 기계 검증
        for i, machine in enumerate(self.machines):
            if not hasattr(machine, 'resource_id'):
                print(f"[경고] 기계 {i+1}에 resource_id 속성이 없습니다.")
            if not hasattr(machine, 'operate'):
                print(f"[경고] 기계 {i+1}에 operate 메서드가 없습니다.")
        
        # 작업자 검증        
        for i, worker in enumerate(self.workers):
            if not hasattr(worker, 'resource_id'):
                print(f"[경고] 작업자 {i+1}에 resource_id 속성이 없습니다.")
            if not hasattr(worker, 'work'):
                print(f"[경고] 작업자 {i+1}에 work 메서드가 없습니다.")
        
        return True
    
    def add_machine(self, machine: Any) -> 'BaseProcess':
        """
        공정에 기계를 추가
        
        Args:
            machine: 추가할 기계 객체
            
        Returns:
            BaseProcess: 자기 자신 (메서드 체이닝용)
        """
        if machine not in self.machines:
            self.machines.append(machine)
            machine_id = getattr(machine, 'resource_id', f'Machine-{len(self.machines)}')
            print(f"[{self.process_name}] 기계 추가: {machine_id}")
        return self
    
    def add_worker(self, worker: Any) -> 'BaseProcess':
        """
        공정에 작업자를 추가
        
        Args:
            worker: 추가할 작업자 객체
            
        Returns:
            BaseProcess: 자기 자신 (메서드 체이닝용)
        """
        if worker not in self.workers:
            self.workers.append(worker)
            worker_id = getattr(worker, 'resource_id', f'Worker-{len(self.workers)}')
            print(f"[{self.process_name}] 작업자 추가: {worker_id}")
        return self
    
    def get_available_machines(self) -> List[Any]:
        """
        사용 가능한 기계들을 반환합니다.
        
        Returns:
            List[Any]: 현재 사용 가능한 기계들의 리스트
        """
        available_machines = []
        for machine in self.machines:
            if hasattr(machine, 'is_available') and machine.is_available():
                available_machines.append(machine)
        return available_machines
    
    def get_available_workers(self) -> List[Any]:
        """
        사용 가능한 작업자들을 반환합니다.
        
        Returns:
            List[Any]: 현재 사용 가능한 작업자들의 리스트
        """
        available_workers = []
        for worker in self.workers:
            if hasattr(worker, 'is_available') and worker.is_available():
                available_workers.append(worker)
        return available_workers
    
    def add_execution_condition(self, condition: Callable[[Any], bool]) -> 'BaseProcess':
        """
        실행 조건을 추가
        
        Args:
            condition: 실행 조건 함수 (입력 데이터를 받아 bool을 반환)
            
        Returns:
            BaseProcess: 자기 자신 (메서드 체이닝용)
        """
        self.conditions.append(condition)
        print(f"[{self.process_name}] 실행 조건 추가됨 (총 {len(self.conditions)}개)")
        return self
    
    def set_parallel_safe(self, safe: bool) -> 'BaseProcess':
        """
        병렬 실행 안전 여부를 설정
        
        Args:
            safe: 병렬 실행 안전 여부
            
        Returns:
            BaseProcess: 자기 자신 (메서드 체이닝용)
        """
        self.parallel_safe = safe
        status = "안전" if safe else "위험"
        print(f"[{self.process_name}] 병렬 실행: {status}")
        return self
    
    def can_execute(self, input_data: Any = None) -> bool:
        """
        현재 공정을 실행할 수 있는지 확인
        
        Args:
            input_data: 입력 데이터
            
        Returns:
            bool: 실행 가능 여부
        """
        # 모든 실행 조건을 확인
        for condition in self.conditions:
            if not condition(input_data):
                print(f"[{self.process_name}] 실행 조건 불만족")
                return False
        
        # 자원 검증
        if not self.validate_resources():
            print(f"[{self.process_name}] 자원 검증 실패")
            return False
        
        return True
    
    def execute(self, input_data: Any = None) -> Generator[simpy.Event, None, Any]:
        """
        공정 실행의 메인 진입점 (SimPy generator 방식, 출력 blocking 지원)
        
        Args:
            input_data: 입력 데이터
            
        Yields:
            simpy.Event: SimPy 이벤트들
            
        Returns:
            Any: 처리 결과
        """
        print(f"[시간 {self.env.now:.1f}] {self.process_name} 실행 시작")
        
        # 실행 가능 여부 확인
        if not self.can_execute(input_data):
            raise RuntimeError(f"{self.process_name} 실행 조건을 만족하지 않습니다.")
        
        # 출력 버퍼가 가득 찬 경우 운송 대기
        if self.enable_output_blocking and self.current_output_count >= self.output_buffer_capacity:
            print(f"[시간 {self.env.now:.1f}] {self.process_name} 출력 버퍼 가득참. 운송 대기 중...")
            self.waiting_for_transport = True
            
            # 운송 준비 이벤트 생성 및 대기
            if self.transport_ready_event is None:
                self.transport_ready_event = self.env.event()
            
            yield self.transport_ready_event  # 운송이 완료될 때까지 대기
            print(f"[시간 {self.env.now:.1f}] {self.process_name} 운송 완료, 공정 재개")
            
            # 이벤트 초기화
            self.transport_ready_event = None
            self.waiting_for_transport = False
        
        # 배치 처리 활성화된 경우 배치 처리
        if self.enable_batch_processing:
            # 배치에 추가
            if self.add_to_batch(input_data):
                # 배치가 준비되면 처리
                if self.is_batch_ready():
                    batch_items = self.get_current_batch()
                    result = yield from self.process_batch(batch_items)
                    self.current_batch = []  # 배치 초기화
                    return result
                else:
                    # 배치가 아직 준비되지 않음
                    return None
            else:
                # 배치에 추가할 수 없는 경우 개별 처리
                result = yield from self.process_logic(input_data)
                return result
        else:
            # 개별 처리
            result = yield from self.process_logic(input_data)
            return result
    
    @abstractmethod
    def process_logic(self, input_data: Any = None) -> Generator[simpy.Event, None, Any]:
        """
        구체적인 프로세스 로직을 구현해야 하는 추상 메서드
        
        Args:
            input_data: 입력 데이터
            
        Yields:
            simpy.Event: SimPy 이벤트들
            
        Returns:
            Any: 처리 결과
        """
        pass
    
    def process_batch(self, batch_items: List[Any]) -> Generator[simpy.Event, None, List[Any]]:
        """
        배치 아이템들을 처리
        
        Args:
            batch_items: 배치 아이템 리스트
            
        Yields:
            simpy.Event: SimPy 이벤트들
            
        Returns:
            List[Any]: 처리 결과 리스트
        """
        print(f"[시간 {self.env.now:.1f}] {self.process_name} 배치 처리 시작 ({len(batch_items)}개)")
        
        # 배치 처리 로직 실행
        results = yield from self.batch_process_logic(batch_items)
        
        print(f"[시간 {self.env.now:.1f}] {self.process_name} 배치 처리 완료")
        return results
    
    def batch_process_logic(self, batch_items: List[Any]) -> Generator[simpy.Event, None, List[Any]]:
        """
        배치 처리 로직 (기본 구현: 개별 처리)
        
        Args:
            batch_items: 배치 아이템 리스트
            
        Yields:
            simpy.Event: SimPy 이벤트들
            
        Returns:
            List[Any]: 처리 결과 리스트
        """
        results = []
        for item in batch_items:
            result = yield from self.process_logic(item)
            results.append(result)
        return results
    
    def add_to_batch(self, item: Any) -> bool:
        """
        배치에 아이템 추가
        
        Args:
            item: 추가할 아이템
            
        Returns:
            bool: 추가 성공 여부
        """
        if len(self.current_batch) < self.batch_size:
            self.current_batch.append(item)
            print(f"[{self.process_name}] 배치에 아이템 추가 ({len(self.current_batch)}/{self.batch_size})")
            return True
        return False
    
    def get_current_batch(self) -> List[Any]:
        """
        현재 배치의 아이템들을 반환합니다.
        
        Returns:
            List[Any]: 현재 배치에 축적된 아이템들의 복사본
        """
        return self.current_batch.copy()
    
    def is_batch_ready(self) -> bool:
        """
        배치가 처리 준비가 되었는지 확인합니다.
        
        Returns:
            bool: 배치 크기에 도달했으면 True, 아니면 False
        """
        return len(self.current_batch) >= self.batch_size
    
    def get_batch_status(self) -> Dict[str, Any]:
        """
        배치 상태 정보를 반환합니다.
        
        Returns:
            Dict[str, Any]: 배치 처리 관련 상태 정보를 담은 딕셔너리
        """
        return {
            'batch_size': self.batch_size,
            'current_count': len(self.current_batch),
            'is_ready': self.is_batch_ready(),
            'enable_batch_processing': self.enable_batch_processing
        }
    
    def connect_to(self, next_process: 'BaseProcess') -> 'BaseProcess':
        """
        다음 공정과 연결
        
        Args:
            next_process: 연결할 다음 공정
            
        Returns:
            BaseProcess: 자기 자신 (메서드 체이닝용)
        """
        if next_process not in self.next_processes:
            self.next_processes.append(next_process)
            next_process.previous_processes.append(self)
            print(f"[{self.process_name}] → [{next_process.process_name}] 연결됨")
        return self
    

    
    def add_input_resource(self, resource: Resource) -> None:
        """
        입력 자원을 추가합니다.
        
        Args:
            resource: 추가할 입력 자원
        """
        self.input_resources.append(resource)
        self.current_input_inventory[resource.resource_id] = resource
    
    def add_output_resource(self, resource: Resource) -> None:
        """
        출력 자원을 추가합니다.
        
        Args:
            resource: 추가할 출력 자원
        """
        self.output_resources.append(resource)
        self.current_output_inventory[resource.resource_id] = resource
    
    def add_resource_requirement(self, requirement: ResourceRequirement) -> None:
        """
        자원 요구사항을 추가합니다.
        
        Args:
            requirement: 추가할 자원 요구사항
        """
        self.resource_requirements.append(requirement)
    
    def consume_resources(self, input_data: Any = None) -> bool:
        """
        입력 자원을 소비
        
        Args:
            input_data: 입력 데이터
            
        Returns:
            bool: 소비 성공 여부
        """
        # 자원 요구사항에 따라 입력 자원 소비
        for requirement in self.resource_requirements:
            if requirement.is_mandatory:
                # 필수 자원이 있는지 확인
                available_resources = [r for r in self.input_resources 
                                     if r.resource_type == requirement.resource_type]
                if len(available_resources) < requirement.required_quantity:
                    print(f"[{self.process_name}] 필수 자원 부족: {requirement.name}")
                    return False
        
        print(f"[{self.process_name}] 자원 소비 완료")
        return True
    
    def produce_resources(self, output_data: Any = None) -> List[Resource]:
        """
        출력 자원을 생산 (출력 버퍼 용량 확인 포함)
        
        Args:
            output_data: 출력 데이터
            
        Returns:
            List[Resource]: 생산된 자원 리스트
            
        Raises:
            RuntimeError: 출력 버퍼가 가득 찬 경우
        """
        # 출력 버퍼 용량 확인 (blocking 활성화된 경우)
        if self.enable_output_blocking:
            if self.current_output_count >= self.output_buffer_capacity:
                self.waiting_for_transport = True
                raise RuntimeError(f"[{self.process_name}] 출력 버퍼 가득참 ({self.current_output_count}/{self.output_buffer_capacity}). 운송을 기다리는 중...")
        
        produced_resources = []
        
        # products_per_cycle 만큼 출력 자원 생산
        for i in range(self.products_per_cycle):
            # 기본 출력 자원이 정의되어 있다면 그것을 기반으로 생성
            if self.output_resources:
                # 첫 번째 출력 자원을 템플릿으로 사용
                template_resource = self.output_resources[0]
                produced_resource = Resource(
                    resource_id=f"{template_resource.resource_id}_{i+1}",
                    name=f"{template_resource.name}_{i+1}",
                    resource_type=template_resource.resource_type,
                    properties=template_resource.properties.copy()
                )
            else:
                # 기본 출력 자원이 없다면 기본 제품 생성
                produced_resource = Resource(
                    resource_id=f"product_{i+1}",
                    name=f"제품_{i+1}",
                    resource_type=ResourceType.PRODUCT,
                    properties={"unit": "개"}
                )
            
            produced_resources.append(produced_resource)
            self.current_output_inventory[produced_resource.resource_id] = produced_resource
        
        # 출력 개수 증가 (products_per_cycle 만큼)
        self.current_output_count += self.products_per_cycle
        
        print(f"[{self.process_name}] 자원 생산 완료: {self.products_per_cycle}개 (버퍼: {self.current_output_count}/{self.output_buffer_capacity})")
        return produced_resources
    
    def get_resource_status(self) -> Dict[str, Any]:
        """
        자원 상태 정보를 반환합니다.
        
        Returns:
            Dict[str, Any]: 자원 관리 관련 상태 정보를 담은 딕셔너리
        """
        return {
            'input_resources': len(self.input_resources),
            'output_resources': len(self.output_resources),
            'resource_requirements': len(self.resource_requirements),
            'input_inventory': len(self.current_input_inventory),
            'output_inventory': len(self.current_output_inventory)
        }
    
    def get_input_resources(self) -> List[Resource]:
        """
        입력 자원 리스트를 반환합니다.
        
        Returns:
            List[Resource]: 현재 공정의 입력 자원 리스트 복사본
        """
        return self.input_resources.copy()
    
    def get_output_resources(self) -> List[Resource]:
        """
        출력 자원 리스트를 반환합니다.
        
        Returns:
            List[Resource]: 현재 공정의 출력 자원 리스트 복사본
        """
        return self.output_resources.copy()
    
    def get_resource_requirements(self) -> List[ResourceRequirement]:
        """
        자원 요구사항 리스트를 반환합니다.
        
        Returns:
            List[ResourceRequirement]: 현재 공정의 자원 요구사항 리스트 복사본
        """
        return self.resource_requirements.copy()
    
    def get_process_info(self) -> Dict[str, Any]:
        """
        공정 정보를 반환합니다.
        
        Returns:
            Dict[str, Any]: 공정의 상세 정보를 담은 딕셔너리
        """
        return {
            'process_id': self.process_id,
            'process_name': self.process_name,
            'machines': len(self.machines),
            'workers': len(self.workers),
            'batch_size': self.batch_size,
            'products_per_cycle': self.products_per_cycle,
            'output_buffer_capacity': self.output_buffer_capacity,
            'parallel_safe': self.parallel_safe,
            'resource_status': self.get_resource_status()
        }
    
    def apply_failure_weight_to_machines(self) -> None:
        """
        기계 고장률 가중치를 적용합니다.
        """
        for machine in self.machines:
            if hasattr(machine, 'set_failure_rate'):
                original_rate = getattr(machine, 'original_failure_rate', machine.failure_rate)
                machine.original_failure_rate = original_rate
                machine.failure_rate = original_rate * self.failure_weight_machine
                print(f"[{self.process_name}] 기계 {getattr(machine, 'resource_id', 'Unknown')} 고장률 가중치 적용: {self.failure_weight_machine}")
    
    def apply_failure_weight_to_workers(self) -> None:
        """
        작업자 실수율 가중치를 적용합니다.
        """
        for worker in self.workers:
            if hasattr(worker, 'set_error_rate'):
                original_rate = getattr(worker, 'original_error_rate', worker.error_rate)
                worker.original_error_rate = original_rate
                worker.error_rate = original_rate * self.failure_weight_worker
                print(f"[{self.process_name}] 작업자 {getattr(worker, 'resource_id', 'Unknown')} 실수율 가중치 적용: {self.failure_weight_worker}")
    
    def restore_original_failure_rates(self) -> None:
        """
        원래 고장률/실수율로 복원합니다.
        """
        # 기계 고장률 복원
        for machine in self.machines:
            if hasattr(machine, 'original_failure_rate'):
                machine.failure_rate = machine.original_failure_rate
                print(f"[{self.process_name}] 기계 {getattr(machine, 'resource_id', 'Unknown')} 고장률 복원")
        
        # 작업자 실수율 복원
        for worker in self.workers:
            if hasattr(worker, 'original_error_rate'):
                worker.error_rate = worker.original_error_rate
                print(f"[{self.process_name}] 작업자 {getattr(worker, 'resource_id', 'Unknown')} 실수율 복원")
    
    # ========== 출하품 Transport 관리 메서드들 ==========
    
    def set_output_buffer_capacity(self, capacity: int) -> 'BaseProcess':
        """
        출력 버퍼 용량을 설정합니다.
        
        Args:
            capacity: 버퍼 용량 (1 이상)
            
        Returns:
            BaseProcess: 자기 자신 (메서드 체이닝용)
        """
        self.output_buffer_capacity = max(1, capacity)
        print(f"[{self.process_name}] 출력 버퍼 용량 설정: {self.output_buffer_capacity}")
        return self
    
    def enable_output_blocking_feature(self, enable: bool = True) -> 'BaseProcess':
        """
        출력 blocking 기능을 활성화/비활성화합니다.
        
        Args:
            enable: blocking 활성화 여부 (기본값: True)
            
        Returns:
            BaseProcess: 자기 자신 (메서드 체이닝용)
        """
        self.enable_output_blocking = enable
        status = "활성화" if enable else "비활성화"
        print(f"[{self.process_name}] 출력 blocking 기능 {status}")
        return self
    
    def get_output_buffer_status(self) -> Dict[str, Any]:
        """
        출력 버퍼 상태 정보를 반환합니다.
        
        Returns:
            Dict[str, Any]: 출력 버퍼 상태 정보
        """
        return {
            'current_count': self.current_output_count,
            'capacity': self.output_buffer_capacity,
            'utilization_rate': self.current_output_count / self.output_buffer_capacity if self.output_buffer_capacity > 0 else 0,
            'is_full': self.current_output_count >= self.output_buffer_capacity,
            'waiting_for_transport': self.waiting_for_transport,
            'blocking_enabled': self.enable_output_blocking
        }
    
    def transport_output_items(self, count: int = None) -> int:
        """
        출력 아이템들을 transport로 옮깁니다 (공정 재개 신호 포함).
        
        Args:
            count: 옮길 아이템 수 (None이면 모든 아이템)
            
        Returns:
            int: 실제로 옮겨진 아이템 수
        """
        if count is None:
            count = self.current_output_count
        
        transported_count = min(count, self.current_output_count)
        self.current_output_count -= transported_count
        
        print(f"[시간 {self.env.now:.1f}] {self.process_name} 출하품 운송: {transported_count}개 (잔여: {self.current_output_count})")
        
        # 운송 완료 후 공정 재개 신호
        if self.waiting_for_transport and self.transport_ready_event is not None:
            self.transport_ready_event.succeed()
            print(f"[시간 {self.env.now:.1f}] {self.process_name} 운송 완료, 공정 재개 신호 발송")
        
        return transported_count
    
    def is_output_buffer_full(self) -> bool:
        """
        출력 버퍼가 가득 찬 상태인지 확인합니다.
        
        Returns:
            bool: 버퍼가 가득 찬 경우 True
        """
        return self.current_output_count >= self.output_buffer_capacity
    
    def get_available_output_space(self) -> int:
        """
        출력 버퍼의 사용 가능한 공간을 반환합니다.
        
        Returns:
            int: 사용 가능한 공간 수
        """
        return self.output_buffer_capacity - self.current_output_count
    
    def clear_output_buffer(self) -> int:
        """
        출력 버퍼를 완전히 비웁니다 (강제 초기화).
        
        Returns:
            int: 제거된 아이템 수
        """
        removed_count = self.current_output_count
        self.current_output_count = 0
        print(f"[{self.process_name}] 출력 버퍼 강제 초기화: {removed_count}개 제거")
        
        # 대기 중인 공정 재개
        if self.waiting_for_transport and self.transport_ready_event is not None:
            self.transport_ready_event.succeed()
        
        return removed_count
    
    def set_batch_size(self, batch_size: int) -> 'BaseProcess':
        """
        배치 크기를 설정합니다. (출력 버퍼 크기는 변경하지 않음)
        
        Args:
            batch_size: 새로운 배치 크기 (1 이상)
            
        Returns:
            BaseProcess: 자기 자신 (메서드 체이닝용)
        """
        old_batch_size = self.batch_size
        
        self.batch_size = max(1, batch_size)
        self.enable_batch_processing = self.batch_size > 1
        
        print(f"[{self.process_name}] 배치 크기 변경: {old_batch_size} → {self.batch_size}")
        print(f"[{self.process_name}] 출력 버퍼 크기 유지: {self.output_buffer_capacity}")
        
        return self
    
    def set_products_per_cycle(self, count: int) -> 'BaseProcess':
        """
        한번 공정 실행 시 생산되는 제품 수를 설정하고 출력 버퍼 크기도 동기화합니다.
        
        Args:
            count: 한번 실행당 생산할 제품 수 (1 이상)
            
        Returns:
            BaseProcess: 자기 자신 (메서드 체이닝용)
        """
        old_products_per_cycle = self.products_per_cycle
        old_buffer_capacity = self.output_buffer_capacity
        
        self.products_per_cycle = max(1, count)
        self.output_buffer_capacity = self.products_per_cycle
        
        print(f"[{self.process_name}] 실행당 생산량 변경: {old_products_per_cycle} → {self.products_per_cycle}")
        print(f"[{self.process_name}] 출력 버퍼 크기 동기화: {old_buffer_capacity} → {self.output_buffer_capacity}")
        
        return self
    
    def __repr__(self) -> str:
        return f"{self.__class__.__name__}({self.process_name})"
    
    def __str__(self) -> str:
        return f"{self.process_name} (ID: {self.process_id})"
