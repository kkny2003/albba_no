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
# Flow 모듈은 런타임에 import하여 순환 import 방지
# from src.Flow import ProcessChain, MultiProcessGroup


class PriorityValidationError(Exception):
    """우선순위 유효성 검사 실패 시 발생하는 예외"""
    pass


def parse_process_priority(process_name: str) -> Tuple[str, Optional[int]]:
    """
    공정명에서 우선순위를 파싱합니다.
    
    Args:
        process_name: 공정명 (예: "공정2(1)" 또는 "공정2")
        
    Returns:
        Tuple[str, Optional[int]]: (실제 공정명, 우선순위) 튜플
        
    Examples:
        >>> parse_process_priority("공정2(1)")
        ("공정2", 1)
        >>> parse_process_priority("공정2")
        ("공정2", None)
    """
    # 정규식으로 공정명(우선순위) 패턴 매칭
    import re
    pattern = r'^(.+?)\((\d+)\)$'
    match = re.match(pattern, process_name.strip())
    
    if match:
        actual_name = match.group(1).strip()
        priority = int(match.group(2))
        return actual_name, priority
    else:
        return process_name.strip(), None


def validate_priority_sequence(processes_with_priorities: List[Tuple['BaseProcess', Optional[int]]]) -> None:
    """
    공정들의 우선순위 시퀀스가 유효한지 검증합니다.
    
    Args:
        processes_with_priorities: (공정, 우선순위) 튜플 리스트
        
    Raises:
        PriorityValidationError: 우선순위가 유효하지 않을 때
        
    Rules:
        1. n개의 공정이 있을 때, 우선순위는 1부터 n까지여야 함
        2. 모든 공정에 우선순위가 있거나, 모든 공정에 우선순위가 없어야 함
        3. 중복된 우선순위는 허용되지 않음
    """
    total_processes = len(processes_with_priorities)
    priorities = [p[1] for p in processes_with_priorities if p[1] is not None]
    
    # 일부만 우선순위가 있는 경우 오류
    if len(priorities) > 0 and len(priorities) != total_processes:
        raise PriorityValidationError(
            f"모든 공정에 우선순위를 지정하거나 모든 공정에서 우선순위를 생략해야 합니다. "
            f"현재 {len(priorities)}개 공정에만 우선순위가 지정되어 있습니다."
        )
    
    # 우선순위가 지정된 경우 유효성 검사
    if priorities:
        # 중복 확인
        if len(set(priorities)) != len(priorities):
            duplicates = [p for p in set(priorities) if priorities.count(p) > 1]
            raise PriorityValidationError(f"중복된 우선순위가 있습니다: {duplicates}")
        
        # 범위 확인 (1부터 n까지)
        expected_priorities = set(range(1, total_processes + 1))
        actual_priorities = set(priorities)
        
        if actual_priorities != expected_priorities:
            missing = expected_priorities - actual_priorities
            extra = actual_priorities - expected_priorities
            
            # 더 자세한 오류 메시지 생성
            process_info = []
            for process, priority in processes_with_priorities:
                if priority is not None:
                    process_info.append(f"{process.process_name}({priority})")
                else:
                    process_info.append(f"{process.process_name}(없음)")
            
            error_msg = f"{total_processes}개 공정에 대해 1부터 {total_processes}까지의 우선순위가 필요합니다."
            error_msg += f"\n현재 공정들: {', '.join(process_info)}"
            
            if missing:
                error_msg += f"\n누락된 우선순위: {sorted(missing)}"
            if extra:
                error_msg += f"\n잘못된 우선순위: {sorted(extra)}"
            
            raise PriorityValidationError(error_msg)


class BaseProcess(ABC):
    """모든 제조 공정의 기본이 되는 추상 클래스 (SimPy 기반, 배치 처리 지원)"""
    
    def __init__(self, env: simpy.Environment, machines=None, workers=None, 
                 process_id: str = None, process_name: str = None, batch_size: int = 1,
                 failure_weight_machine: float = 1.0, failure_weight_worker: float = 1.0,
                 input_resources: List[Resource], 
                 output_resources: List[Resource],
                 resource_requirements: List[ResourceRequirement]):
        """
        기본 공정 초기화 (SimPy 환경 필수, machine 또는 worker 중 하나는 필수)
        
        Args:
            env: SimPy 환경 객체 (필수)
            machines: 사용할 기계 리스트 (machine 또는 worker 중 하나는 필수)
            workers: 사용할 작업자 리스트 (machine 또는 worker 중 하나는 필수)
            process_id: 공정 고유 ID (선택적, 자동 생성됨)
            process_name: 공정 이름 (선택적)
            batch_size: 배치 크기 (한번에 처리할 아이템 수, 기본값: 1)
            failure_weight_machine: 기계 고장률 가중치 (기본값: 1.0, 1.5 = 1.5배 고장률)
            failure_weight_worker: 작업자 실수율 가중치 (기본값: 1.0, 1.5 = 1.5배 실수율)
            input_resources: 입력 자원 목록 (필수)
            output_resources: 출력 자원 목록 (필수)
            resource_requirements: 자원 요구사항 목록 (필수)
            
        Raises:
            ValueError: machine과 worker가 모두 None인 경우
        """
        # machine 또는 worker 중 하나는 필수로 있어야 함
        if machines is None and workers is None:
            raise ValueError(f"공정 '{process_name or self.__class__.__name__}'에는 machine 또는 worker 중 하나 이상이 필요합니다.")
        
        self.env = env  # SimPy 환경 객체 (필수)
        self.process_id = process_id or str(uuid.uuid4())  # 고유 ID 생성
        self.process_name = process_name or self.__class__.__name__  # 기본 이름 설정
        self.next_processes = []  # 다음 공정들의 리스트
        self.previous_processes = []  # 이전 공정들의 리스트
        
        # 기계와 작업자 설정 (필수 요소)
        self.machines = machines or []  # 기계 리스트
        self.workers = workers or []   # 작업자 리스트
        
        # 초기화 검증 메시지 출력
        resource_info = []
        if self.machines:
            machine_ids = [getattr(m, 'machine_id', str(m)) for m in self.machines]
            resource_info.append(f"기계: {', '.join(machine_ids)}")
        if self.workers:
            worker_ids = [getattr(w, 'worker_id', str(w)) for w in self.workers]
            resource_info.append(f"작업자: {', '.join(worker_ids)}")
        
        print(f"[{self.process_name}] 공정 초기화 완료 - {' / '.join(resource_info)}")
        
        # 고장률 가중치 설정
        self.failure_weight_machine = failure_weight_machine  # 기계 고장률 가중치
        self.failure_weight_worker = failure_weight_worker    # 작업자 실수율 가중치
        
        # 배치 처리 설정
        self.batch_size = max(1, batch_size)  # 최소 1개 이상
        self.enable_batch_processing = batch_size > 1  # 배치 처리 활성화 여부
        self.current_batch = []  # 현재 배치에 축적된 아이템들
        
        # 자원 관리 관련 속성들
        self.input_resources: List[Resource] = []  # 입력 자원 리스트
        self.output_resources: List[Resource] = []  # 출력 자원 리스트
        self.resource_requirements: List[ResourceRequirement] = []  # 자원 요구사항
        self.current_input_inventory: Dict[str, Resource] = {}  # 현재 입력 자원 재고
        self.current_output_inventory: Dict[str, Resource] = {}  # 현재 출력 자원 재고
        
        # 고급 워크플로우 지원을 위한 새로운 속성들
        self.execution_priority: int = 5  # 실행 우선순위 (1-10, 높을수록 우선)
        self.conditions: List[Callable[[Any], bool]] = []  # 실행 조건들
        self.parallel_safe: bool = True  # 병렬 실행 안전 여부
        self.resource_manager = None  # 고급 자원 관리자 (필요시 설정)
        
        # SimPy 관련 속성들
        self.processing_time: float = 1.0  # 기본 처리 시간 (시뮬레이션 시간 단위)
        
        # 자원 설정 (개선된 통합 로직)
        self._setup_resources(input_resources, output_resources, resource_requirements)
        
    def _setup_resources(self, input_resources: List[Resource], 
                        output_resources: List[Resource],
                        resource_requirements: List[ResourceRequirement]):
        """
        자원 정보를 설정하는 통합 메서드 (모든 프로세스에서 공통 사용)
        
        Args:
            input_resources: 입력 자원 목록
            output_resources: 출력 자원 목록
            resource_requirements: 자원 요구사항 목록
        """
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
            if not hasattr(machine, 'machine_id'):
                print(f"[경고] 기계 {i+1}에 machine_id 속성이 없습니다.")
            if not hasattr(machine, 'operate'):
                print(f"[경고] 기계 {i+1}에 operate 메서드가 없습니다.")
        
        # 작업자 검증        
        for i, worker in enumerate(self.workers):
            if not hasattr(worker, 'worker_id'):
                print(f"[경고] 작업자 {i+1}에 worker_id 속성이 없습니다.")
            if not hasattr(worker, 'work'):
                print(f"[경고] 작업자 {i+1}에 work 메서드가 없습니다.")
        
        return True
    
    def add_machine(self, machine) -> 'BaseProcess':
        """
        공정에 기계를 추가
        
        Args:
            machine: 추가할 기계 객체
            
        Returns:
            BaseProcess: 자기 자신 (메서드 체이닝용)
        """
        if machine not in self.machines:
            self.machines.append(machine)
            machine_id = getattr(machine, 'machine_id', f'Machine-{len(self.machines)}')
            print(f"[{self.process_name}] 기계 추가: {machine_id}")
        return self
    
    def add_worker(self, worker) -> 'BaseProcess':
        """
        공정에 작업자를 추가
        
        Args:
            worker: 추가할 작업자 객체
            
        Returns:
            BaseProcess: 자기 자신 (메서드 체이닝용)
        """
        if worker not in self.workers:
            self.workers.append(worker)
            worker_id = getattr(worker, 'worker_id', f'Worker-{len(self.workers)}')
            print(f"[{self.process_name}] 작업자 추가: {worker_id}")
        return self
    
    def get_available_machines(self):
        """
        사용 가능한 기계들을 반환
        
        Returns:
            List: 사용 가능한 기계 리스트
        """
        available_machines = []
        for machine in self.machines:
            if hasattr(machine, 'is_available') and machine.is_available():
                available_machines.append(machine)
        return available_machines
    
    def get_available_workers(self):
        """
        사용 가능한 작업자들을 반환
        
        Returns:
            List: 사용 가능한 작업자 리스트
        """
        available_workers = []
        for worker in self.workers:
            if hasattr(worker, 'is_available') and worker.is_available():
                available_workers.append(worker)
        return available_workers
    
    def set_execution_priority(self, priority: int) -> 'BaseProcess':
        """
        실행 우선순위를 설정
        
        Args:
            priority: 우선순위 (1-10, 높을수록 우선)
            
        Returns:
            BaseProcess: 자기 자신 (메서드 체이닝용)
        """
        self.execution_priority = max(1, min(10, priority))
        print(f"[{self.process_name}] 실행 우선순위 설정: {self.execution_priority}")
        return self
    
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
        공정 실행의 메인 진입점 (SimPy generator 방식)
        
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
        """현재 배치의 아이템들을 반환"""
        return self.current_batch.copy()
    
    def is_batch_ready(self) -> bool:
        """배치가 처리 준비가 되었는지 확인"""
        return len(self.current_batch) >= self.batch_size
    
    def get_batch_status(self) -> Dict[str, Any]:
        """배치 상태 정보를 반환"""
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
    
    def __rshift__(self, other: Union['BaseProcess', 'ProcessChain', 'MultiProcessGroup']) -> 'ProcessChain':
        """
        >> 연산자를 사용하여 공정 체인 생성
        
        Args:
            other: 연결할 공정, 체인, 또는 그룹
            
        Returns:
            ProcessChain: 생성된 공정 체인
        """
        # 런타임에 Flow 모듈 import
        from src.Flow import ProcessChain, MultiProcessGroup
        from src.Flow.multi_process_group import GroupWrapperProcess
        
        if isinstance(other, BaseProcess):
            return ProcessChain([self, other])
        elif isinstance(other, ProcessChain):
            new_chain = ProcessChain([self])
            new_chain.processes.extend(other.processes)
            return new_chain
        elif isinstance(other, MultiProcessGroup):
            # MultiProcessGroup을 래퍼로 감싸서 추가
            group_wrapper = GroupWrapperProcess(other)
            return ProcessChain([self, group_wrapper])
        else:
            raise TypeError(f">> 연산자는 BaseProcess, ProcessChain, 또는 MultiProcessGroup과만 사용할 수 있습니다. {type(other)} 타입은 지원되지 않습니다.")
    
    def __and__(self, other: 'BaseProcess') -> 'MultiProcessGroup':
        """
        & 연산자를 사용하여 병렬 그룹 생성
        
        Args:
            other: 병렬 실행할 공정
            
        Returns:
            MultiProcessGroup: 생성된 병렬 그룹
        """
        # 런타임에 Flow 모듈 import
        from src.Flow import MultiProcessGroup
        
        if isinstance(other, BaseProcess):
            return MultiProcessGroup([self, other])
        else:
            raise TypeError(f"& 연산자는 BaseProcess와만 사용할 수 있습니다. {type(other)} 타입은 지원되지 않습니다.")
    
    def add_input_resource(self, resource: Resource):
        """입력 자원 추가"""
        self.input_resources.append(resource)
        self.current_input_inventory[resource.resource_id] = resource
    
    def add_output_resource(self, resource: Resource):
        """출력 자원 추가"""
        self.output_resources.append(resource)
        self.current_output_inventory[resource.resource_id] = resource
    
    def add_resource_requirement(self, requirement: ResourceRequirement):
        """자원 요구사항 추가"""
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
        출력 자원을 생산
        
        Args:
            output_data: 출력 데이터
            
        Returns:
            List[Resource]: 생산된 자원 리스트
        """
        produced_resources = []
        
        # 출력 자원 생산
        for output_resource in self.output_resources:
            # 자원 복사본 생성
            produced_resource = Resource(
                resource_id=output_resource.resource_id,
                name=output_resource.name,
                resource_type=output_resource.resource_type,
                properties=output_resource.properties.copy()
            )
            produced_resources.append(produced_resource)
            self.current_output_inventory[produced_resource.resource_id] = produced_resource
        
        print(f"[{self.process_name}] 자원 생산 완료: {len(produced_resources)}개")
        return produced_resources
    
    def get_resource_status(self) -> Dict[str, Any]:
        """자원 상태 정보를 반환"""
        return {
            'input_resources': len(self.input_resources),
            'output_resources': len(self.output_resources),
            'resource_requirements': len(self.resource_requirements),
            'input_inventory': len(self.current_input_inventory),
            'output_inventory': len(self.current_output_inventory)
        }
    
    def get_input_resources(self) -> List[Resource]:
        """입력 자원 리스트를 반환"""
        return self.input_resources.copy()
    
    def get_output_resources(self) -> List[Resource]:
        """출력 자원 리스트를 반환"""
        return self.output_resources.copy()
    
    def get_resource_requirements(self) -> List[ResourceRequirement]:
        """자원 요구사항 리스트를 반환"""
        return self.resource_requirements.copy()
    
    def get_process_info(self) -> dict:
        """공정 정보를 반환"""
        return {
            'process_id': self.process_id,
            'process_name': self.process_name,
            'machines': len(self.machines),
            'workers': len(self.workers),
            'batch_size': self.batch_size,
            'execution_priority': self.execution_priority,
            'parallel_safe': self.parallel_safe,
            'resource_status': self.get_resource_status()
        }
    
    def apply_failure_weight_to_machines(self):
        """기계 고장률 가중치 적용"""
        for machine in self.machines:
            if hasattr(machine, 'set_failure_rate'):
                original_rate = getattr(machine, 'original_failure_rate', machine.failure_rate)
                machine.original_failure_rate = original_rate
                machine.failure_rate = original_rate * self.failure_weight_machine
                print(f"[{self.process_name}] 기계 {getattr(machine, 'machine_id', 'Unknown')} 고장률 가중치 적용: {self.failure_weight_machine}")
    
    def apply_failure_weight_to_workers(self):
        """작업자 실수율 가중치 적용"""
        for worker in self.workers:
            if hasattr(worker, 'set_error_rate'):
                original_rate = getattr(worker, 'original_error_rate', worker.error_rate)
                worker.original_error_rate = original_rate
                worker.error_rate = original_rate * self.failure_weight_worker
                print(f"[{self.process_name}] 작업자 {getattr(worker, 'worker_id', 'Unknown')} 실수율 가중치 적용: {self.failure_weight_worker}")
    
    def restore_original_failure_rates(self):
        """원래 고장률/실수율로 복원"""
        # 기계 고장률 복원
        for machine in self.machines:
            if hasattr(machine, 'original_failure_rate'):
                machine.failure_rate = machine.original_failure_rate
                print(f"[{self.process_name}] 기계 {getattr(machine, 'machine_id', 'Unknown')} 고장률 복원")
        
        # 작업자 실수율 복원
        for worker in self.workers:
            if hasattr(worker, 'original_error_rate'):
                worker.error_rate = worker.original_error_rate
                print(f"[{self.process_name}] 작업자 {getattr(worker, 'worker_id', 'Unknown')} 실수율 복원")
    
    def __repr__(self) -> str:
        return f"{self.__class__.__name__}({self.process_name})"
    
    def __str__(self) -> str:
        return f"{self.process_name} (ID: {self.process_id})"
