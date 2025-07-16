"""
기본 공정 클래스와 공정 체인을 관리하는 모듈입니다.
모든 제조 공정의 기본이 되는 클래스와 >> 연산자를 통한 공정 연결 기능을 제공합니다.
고급 워크플로우 및 자원 관리 기능을 지원합니다.
"""

from typing import List, Optional, Any, Union, Dict, Callable, Tuple, Generator
from abc import ABC, abstractmethod
import uuid
import concurrent.futures
import re
import simpy
from Resource.helper import Resource, ResourceRequirement, ResourceType


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
                error_msg += f"\n범위를 벗어난 우선순위: {sorted(extra)}"
                
            raise PriorityValidationError(error_msg)


class ProcessChain:
    """연결된 공정들의 체인을 관리하는 클래스"""
    
    def __init__(self, processes: List['BaseProcess'] = None):
        """
        공정 체인 초기화
        
        Args:
            processes: 초기 공정 리스트 (선택적)
        """
        self.processes = processes or []  # 공정 리스트 초기화
        self.chain_id = str(uuid.uuid4())  # 체인 고유 ID 생성
    
    def add_process(self, process: 'BaseProcess') -> 'ProcessChain':
        """
        체인에 공정을 추가
        
        Args:
            process: 추가할 공정
            
        Returns:
            ProcessChain: 현재 체인 (메서드 체이닝을 위해)
        """
        self.processes.append(process)
        return self
    
    def execute_chain(self, input_data: Any = None) -> Any:
        """
        전체 공정 체인을 순차적으로 실행
        
        Args:
            input_data: 첫 번째 공정에 전달할 입력 데이터
            
        Returns:
            Any: 마지막 공정의 출력 결과
        """
        current_data = input_data
        
        print(f"공정 체인 실행 시작 (체인 ID: {self.chain_id})")
        print(f"총 {len(self.processes)}개의 공정을 순차 실행합니다.")
        
        for i, process in enumerate(self.processes, 1):
            print(f"\n[{i}/{len(self.processes)}] {process.process_name} 실행 중...")
            current_data = process.execute(current_data)
            print(f"[{i}/{len(self.processes)}] {process.process_name} 완료")
        
        print(f"\n공정 체인 실행 완료 (체인 ID: {self.chain_id})")
        return current_data
    
    def get_process_summary(self) -> str:
        """
        공정 체인의 요약 정보를 반환
        
        Returns:
            str: 체인 요약 정보
        """
        if not self.processes:
            return "빈 공정 체인"
        
        process_names = [p.process_name for p in self.processes]
        return " → ".join(process_names)
    
    def __repr__(self) -> str:
        return f"ProcessChain({self.get_process_summary()})"
    
    def __rshift__(self, other: Union['BaseProcess', 'ProcessChain', 'MultiProcessGroup']) -> 'ProcessChain':
        """
        >> 연산자를 사용하여 체인에 공정이나 다른 체인을 연결
        
        Args:
            other: 연결할 공정 또는 체인
            
        Returns:
            ProcessChain: 새로운 확장된 체인
        """
        new_chain = ProcessChain(self.processes.copy())
        
        if isinstance(other, BaseProcess):
            new_chain.add_process(other)
        elif isinstance(other, ProcessChain):
            new_chain.processes.extend(other.processes)
        elif isinstance(other, MultiProcessGroup):
            # MultiProcessGroup을 래퍼로 감싸서 추가
            group_wrapper = GroupWrapperProcess(other)
            new_chain.add_process(group_wrapper)
        else:
            raise TypeError(f">> 연산자는 BaseProcess, ProcessChain, 또는 MultiProcessGroup과만 사용할 수 있습니다. {type(other)} 타입은 지원되지 않습니다.")
        
        return new_chain


class MultiProcessGroup:
    """다중공정을 그룹으로 관리하여 병렬 실행을 지원하는 클래스 (우선순위 기반 실행 지원)"""
    
    def __init__(self, processes: List['BaseProcess'] = None):
        """
        다중공정 그룹 초기화
        
        Args:
            processes: 그룹에 포함될 공정 리스트
        """
        self.processes = processes or []  # 그룹 내 공정들
        self.group_id = str(uuid.uuid4())  # 그룹 고유 ID
        self.parallel_execution = True  # 병렬 실행 여부
        self.priority_based_execution = False  # 우선순위 기반 실행 여부
        self.priority_mapping: Dict[str, int] = {}  # 공정 ID -> 연결 시점 우선순위 매핑
        
        # 공정들에 우선순위가 설정되어 있는지 확인
        self._check_priority_setup()
        
    def _check_priority_setup(self) -> None:
        """공정들의 우선순위 설정 상태를 확인하고 실행 모드를 결정합니다."""
        if not self.processes:
            return
            
        # 연결 시점 우선순위가 있는지 확인
        if self.priority_mapping:
            self.priority_based_execution = True
            print(f"[그룹 {self.group_id}] 우선순위 기반 실행 모드 활성화")
            
    def set_process_priority(self, process: 'BaseProcess', priority: int) -> None:
        """공정의 연결 시점 우선순위를 설정합니다."""
        self.priority_mapping[process.process_id] = priority
        self._check_priority_setup()
            
    def sort_by_priority(self) -> List['BaseProcess']:
        """우선순위에 따라 공정들을 정렬합니다."""
        if not self.priority_based_execution or not self.priority_mapping:
            return self.processes.copy()
            
        # priority_mapping 기준으로 정렬 (낮은 숫자 = 높은 우선순위)
        def get_priority(process):
            return self.priority_mapping.get(process.process_id, 999)  # 우선순위 없으면 맨 뒤
            
        sorted_processes = sorted(self.processes, key=get_priority)
        
        priority_info = []
        for p in sorted_processes:
            priority = self.priority_mapping.get(p.process_id, "없음")
            priority_info.append(f"{p.process_name}({priority})")
            
        print(f"[그룹 {self.group_id}] 우선순위 순서: {' → '.join(priority_info)}")
        
        return sorted_processes
        
    def add_process(self, process: 'BaseProcess') -> 'MultiProcessGroup':
        """
        그룹에 공정을 추가
        
        Args:
            process: 추가할 공정
            
        Returns:
            MultiProcessGroup: 현재 그룹 (메서드 체이닝용)
        """
        self.processes.append(process)
        # 우선순위 설정 재확인
        self._check_priority_setup()
        return self
        
    def execute_group(self, input_data: Any = None) -> List[Any]:
        """
        그룹 내 모든 공정을 실행 (우선순위 기반 또는 병렬)
        
        Args:
            input_data: 각 공정에 전달할 입력 데이터
            
        Returns:
            List[Any]: 각 공정의 실행 결과 리스트 (우선순위 순서로 정렬됨)
        """
        if not self.processes:
            print(f"다중공정 그룹 {self.group_id}: 실행할 공정이 없습니다")
            return []
            
        print(f"다중공정 그룹 실행 시작 (그룹 ID: {self.group_id})")
        
        # 우선순위 기반 실행이면 정렬된 순서로 실행
        if self.priority_based_execution:
            sorted_processes = self.sort_by_priority()
            print(f"우선순위 기반 순차 실행: {', '.join([p.process_name for p in sorted_processes])}")
            
            results = []
            for i, process in enumerate(sorted_processes, 1):
                try:
                    priority = self.priority_mapping.get(process.process_id, "없음")
                    print(f"  [{i}/{len(sorted_processes)}] {process.process_name} (우선순위: {priority}) 실행 중...")
                    result = process.execute(input_data)
                    results.append(result)
                    print(f"  [OK] {process.process_name} 완료")
                except Exception as e:
                    print(f"  [ERROR] {process.process_name} 실행 중 오류: {e}")
                    results.append(None)
                    
            print(f"우선순위 기반 실행 완료 (그룹 ID: {self.group_id})")
            return results
        
        else:
            # 기존 병렬/순차 실행 로직
            print(f"병렬 실행할 공정: {', '.join([p.process_name for p in self.processes])}")
            
            results = []
            
            if self.parallel_execution and all(p.parallel_safe for p in self.processes):
                # 병렬 실행 (모든 공정이 병렬 안전한 경우)
                print("병렬 실행 모드 사용")
                with concurrent.futures.ThreadPoolExecutor(max_workers=len(self.processes)) as executor:
                    # 각 공정을 병렬로 실행
                    future_to_process = {
                        executor.submit(process.execute, input_data): process 
                        for process in self.processes
                    }
                    
                    for future in concurrent.futures.as_completed(future_to_process):
                        process = future_to_process[future]
                        try:
                            result = future.result()
                            results.append(result)
                            print(f"  [OK] {process.process_name} 완료")
                        except Exception as e:
                            print(f"  [ERROR] {process.process_name} 실행 중 오류: {e}")
                            results.append(None)
            else:
                # 순차 실행 (병렬 안전하지 않은 공정이 있는 경우)
                print("순차 실행 모드 사용")
                for process in self.processes:
                    try:
                        result = process.execute(input_data)
                        results.append(result)
                        print(f"  [OK] {process.process_name} 완료")
                    except Exception as e:
                        print(f"  [ERROR] {process.process_name} 실행 중 오류: {e}")
                        results.append(None)
            
            print(f"다중공정 그룹 실행 완료 (그룹 ID: {self.group_id})")
            return results
        
    def __and__(self, other: 'BaseProcess') -> 'MultiProcessGroup':
        """
        & 연산자를 사용하여 공정을 그룹에 추가
        연결 시점에 우선순위 문법을 지원합니다: 공정명(우선순위)
        
        Args:
            other: 그룹에 추가할 공정 (우선순위 포함 가능)
            
        Returns:
            MultiProcessGroup: 새로운 확장된 그룹
            
        Raises:
            PriorityValidationError: 우선순위가 유효하지 않을 때
        """
        if isinstance(other, BaseProcess):
            # 새로운 공정의 우선순위 파싱
            other_name, other_priority = parse_process_priority(other.process_name)
            
            # 새 그룹 생성
            new_group = MultiProcessGroup(self.processes.copy())
            new_group.priority_mapping = self.priority_mapping.copy()  # 기존 우선순위 매핑 복사
            new_group.add_process(other)
            
            # 우선순위가 파싱된 경우 설정 (공정명은 변경하지 않음)
            if other_priority is not None:
                new_group.set_process_priority(other, other_priority)
            
            # 우선순위 유효성 검사 (우선순위가 하나라도 있는 경우)
            all_priorities = list(new_group.priority_mapping.values())
            if all_priorities:  # 우선순위가 하나라도 설정된 경우
                processes_with_priorities = []
                
                for process in new_group.processes:
                    priority = new_group.priority_mapping.get(process.process_id)
                    processes_with_priorities.append((process, priority))
                
                validate_priority_sequence(processes_with_priorities)
            
            return new_group
        else:
            raise TypeError(f"& 연산자는 BaseProcess와만 사용할 수 있습니다. {type(other)} 타입은 지원되지 않습니다.")
    
    def __rshift__(self, other: Union['BaseProcess', 'ProcessChain', 'MultiProcessGroup']) -> 'ProcessChain':
        """
        >> 연산자를 사용하여 그룹을 다음 공정이나 체인과 연결
        
        Args:
            other: 연결할 공정 또는 체인
            
        Returns:
            ProcessChain: 그룹과 다음 공정이 연결된 체인
        """
        # 그룹을 단일 실행 단위로 래핑하는 특수 공정 생성
        group_wrapper = GroupWrapperProcess(self)
        
        if isinstance(other, BaseProcess):
            return ProcessChain([group_wrapper, other])
        elif isinstance(other, ProcessChain):
            new_chain = ProcessChain([group_wrapper])
            new_chain.processes.extend(other.processes)
            return new_chain
        elif isinstance(other, MultiProcessGroup):
            # 다른 그룹과 연결할 때는 두 그룹을 모두 래퍼로 감싸서 체인 생성
            other_wrapper = GroupWrapperProcess(other)
            return ProcessChain([group_wrapper, other_wrapper])
        else:
            raise TypeError(f">> 연산자는 BaseProcess, ProcessChain, 또는 MultiProcessGroup과만 사용할 수 있습니다. {type(other)} 타입은 지원되지 않습니다.")
    
    def get_group_summary(self) -> str:
        """
        그룹 요약 정보 반환
        
        Returns:
            str: 그룹 요약
        """
        if not self.processes:
            return "빈 다중공정 그룹"
        
        process_names = [p.process_name for p in self.processes]
        return f"[{' & '.join(process_names)}]"
    
    def __repr__(self) -> str:
        return f"MultiProcessGroup({self.get_group_summary()})"


class BaseProcess(ABC):
    """모든 제조 공정의 기본이 되는 추상 클래스 (SimPy 기반)"""
    
    def __init__(self, env: simpy.Environment, process_id: str = None, process_name: str = None):
        """
        기본 공정 초기화 (SimPy 환경 필수)
        
        Args:
            env: SimPy 환경 객체 (필수)
            process_id: 공정 고유 ID (선택적, 자동 생성됨)
            process_name: 공정 이름 (선택적)
        """
        self.env = env  # SimPy 환경 객체 (필수)
        self.process_id = process_id or str(uuid.uuid4())  # 고유 ID 생성
        self.process_name = process_name or self.__class__.__name__  # 기본 이름 설정
        self.next_processes = []  # 다음 공정들의 리스트
        self.previous_processes = []  # 이전 공정들의 리스트
        
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
        
    def set_execution_priority(self, priority: int) -> 'BaseProcess':
        """
        실행 우선순위 설정
        
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
        실행 조건 추가
        
        Args:
            condition: 입력 데이터를 받아 bool을 반환하는 함수
            
        Returns:
            BaseProcess: 자기 자신
        """
        self.conditions.append(condition)
        print(f"[{self.process_name}] 실행 조건 추가")
        return self
    
    def set_parallel_safe(self, safe: bool) -> 'BaseProcess':
        """
        병렬 실행 안전 여부 설정
        
        Args:
            safe: 병렬 실행 안전 여부
            
        Returns:
            BaseProcess: 자기 자신
        """
        self.parallel_safe = safe
        status = "안전" if safe else "불안전"
        print(f"[{self.process_name}] 병렬 실행 {status}으로 설정")
        return self
    
    def can_execute(self, input_data: Any = None) -> bool:
        """
        실행 가능 여부 확인 (모든 조건 검사)
        
        Args:
            input_data: 입력 데이터
            
        Returns:
            bool: 실행 가능 여부
        """
        # 모든 조건이 만족되어야 실행 가능
        for condition in self.conditions:
            try:
                if not condition(input_data):
                    return False
            except Exception as e:
                print(f"[{self.process_name}] 조건 검사 중 오류: {e}")
                return False
        
        return True
        
    def execute(self, input_data: Any = None) -> Generator[simpy.Event, None, Any]:
        """
        공정을 실행하는 SimPy generator 메서드 (기본 구현)
        
        기본적으로 다음 순서로 실행됩니다:
        1. 입력 자원 소비 (consume_resources)
        2. 구체적인 공정 로직 실행 (process_logic - 하위 클래스에서 구현)
        3. 출력 자원 생산 (produce_resources)
        
        Args:
            input_data: 공정에 전달되는 입력 데이터
            
        Yields:
            simpy.Event: SimPy 이벤트들
            
        Returns:
            Any: 공정 실행 결과 (생산된 자원 포함)
        """
        print(f"[시간 {self.env.now:.1f}] [{self.process_name}] 공정 실행 시작")
        
        # 1. 자원 소비 검증
        if not self.consume_resources(input_data):
            print(f"[시간 {self.env.now:.1f}] [{self.process_name}] 공정 실행 실패: 자원 부족")
            return None
            
        # 2. 구체적인 공정 로직 실행 (하위 클래스에서 구현하는 generator)
        result = yield from self.process_logic(input_data)
        
        # 3. 자원 생산
        produced_resources = self.produce_resources(result)
        
        print(f"[시간 {self.env.now:.1f}] [{self.process_name}] 공정 실행 완료")
        
        # 결과와 생산된 자원을 함께 반환
        return {
            'result': result,
            'produced_resources': produced_resources,
            'process_info': self.get_resource_status()
        }
        
    @abstractmethod
    def process_logic(self, input_data: Any = None) -> Generator[simpy.Event, None, Any]:
        """
        구체적인 공정 로직을 실행하는 추상 SimPy generator 메서드
        각 구체적인 공정 클래스에서 구현해야 함
        
        Args:
            input_data: 공정에 전달되는 입력 데이터
            
        Yields:
            simpy.Event: SimPy 이벤트들
            
        Returns:
            Any: 공정 로직 실행 결과
        """
        pass
    
    def connect_to(self, next_process: 'BaseProcess') -> 'BaseProcess':
        """
        다른 공정과 연결 (명시적 연결 메서드)
        
        Args:
            next_process: 연결할 다음 공정
            
        Returns:
            BaseProcess: 연결된 다음 공정 (메서드 체이닝을 위해)
        """
        if next_process not in self.next_processes:
            self.next_processes.append(next_process)
        
        if self not in next_process.previous_processes:
            next_process.previous_processes.append(self)
        
        print(f"공정 연결: {self.process_name} → {next_process.process_name}")
        return next_process
    
    def __rshift__(self, other: Union['BaseProcess', 'ProcessChain', 'MultiProcessGroup']) -> ProcessChain:
        """
        >> 연산자를 사용하여 공정을 연결
        
        Args:
            other: 연결할 공정 또는 체인
            
        Returns:
            ProcessChain: 연결된 공정들의 체인
        """
        if isinstance(other, BaseProcess):
            # 공정 간 연결 설정
            self.connect_to(other)
            # 새로운 체인 생성하여 반환
            return ProcessChain([self, other])
        
        elif isinstance(other, ProcessChain):
            # 체인의 첫 번째 공정과 연결
            if other.processes:
                self.connect_to(other.processes[0])
            # 새로운 체인 생성
            new_chain = ProcessChain([self])
            new_chain.processes.extend(other.processes)
            return new_chain
        
        elif isinstance(other, MultiProcessGroup):
            # MultiProcessGroup을 래퍼로 감싸서 연결
            group_wrapper = GroupWrapperProcess(other)
            return ProcessChain([self, group_wrapper])
        
        else:
            raise TypeError(f">> 연산자는 BaseProcess, ProcessChain, 또는 MultiProcessGroup과만 사용할 수 있습니다. {type(other)} 타입은 지원되지 않습니다.")
    
    def __and__(self, other: 'BaseProcess') -> 'MultiProcessGroup':
        """
        & 연산자를 사용하여 다중공정 그룹을 생성
        연결 시점에 우선순위 문법을 지원합니다: 공정명(우선순위)
        
        Args:
            other: 그룹에 포함할 다른 공정 (우선순위 포함 가능)
            
        Returns:
            MultiProcessGroup: 두 공정이 포함된 다중공정 그룹
            
        Examples:
            >>> process1 = SomeProcess(process_name="공정1")
            >>> process2 = SomeProcess(process_name="공정2")
            >>> # 연결 시점에 우선순위 지정
            >>> group = process1(1) & process2(2)  # 실제로는 process1._with_priority(1) & process2._with_priority(2)
            
        Note:
            실제 사용법: process1 >> (process2(1) & process3(2) & process4(3))
            이 경우 다른 파싱 메커니즘이 필요할 수 있습니다.
        """
        if isinstance(other, BaseProcess):
            # 현재 공정(self)의 우선순위 파싱 - 하지만 실제로는 다른 방식으로 처리될 예정
            self_name, self_priority = parse_process_priority(self.process_name)
            other_name, other_priority = parse_process_priority(other.process_name)
            
            # 그룹 생성
            group = MultiProcessGroup([self, other])
            
            # 우선순위가 파싱된 경우 설정 (공정명은 변경하지 않음)
            if self_priority is not None:
                group.set_process_priority(self, self_priority)
                
            if other_priority is not None:
                group.set_process_priority(other, other_priority)
            
            # 우선순위가 하나라도 있으면 유효성 검사
            if self_priority is not None or other_priority is not None:
                processes_with_priorities = [
                    (self, self_priority),
                    (other, other_priority)
                ]
                validate_priority_sequence(processes_with_priorities)
            
            return group
        else:
            raise TypeError(f"& 연산자는 BaseProcess와만 사용할 수 있습니다. {type(other)} 타입은 지원되지 않습니다.")
    
    def add_input_resource(self, resource: Resource):
        """
        입력 자원을 추가하는 메서드
        
        Args:
            resource: 추가할 입력 자원
        """
        self.input_resources.append(resource)
        self.current_input_inventory[resource.resource_id] = resource
        print(f"[{self.process_name}] 입력 자원 추가: {resource}")
        
    def add_output_resource(self, resource: Resource):
        """
        출력 자원을 추가하는 메서드
        
        Args:
            resource: 추가할 출력 자원
        """
        self.output_resources.append(resource)
        self.current_output_inventory[resource.resource_id] = resource
        print(f"[{self.process_name}] 출력 자원 추가: {resource}")
        
    def add_resource_requirement(self, requirement: ResourceRequirement):
        """
        자원 요구사항을 추가하는 메서드
        
        Args:
            requirement: 자원 요구사항
        """
        self.resource_requirements.append(requirement)
        print(f"[{self.process_name}] 자원 요구사항 추가: {requirement}")
        
    def validate_resources(self) -> bool:
        """
        현재 사용 가능한 자원이 요구사항을 만족하는지 검증
        
        Returns:
            bool: 자원 요구사항 만족 여부
        """
        print(f"[{self.process_name}] 자원 요구사항 검증 시작")
        
        for requirement in self.resource_requirements:
            satisfied = False
            
            # 입력 자원에서 요구사항을 만족하는 자원 찾기
            for resource in self.input_resources:
                if requirement.is_satisfied_by(resource):
                    satisfied = True
                    print(f"  [OK] 요구사항 만족: {requirement}")
                    break
                    
            if not satisfied and requirement.is_mandatory:
                print(f"  [ERROR] 필수 요구사항 미충족: {requirement}")
                return False
            elif not satisfied:
                print(f"  [WARNING] 선택적 요구사항 미충족: {requirement}")
                
        print(f"[{self.process_name}] 자원 검증 완료")
        return True
        
    def consume_resources(self, input_data: Any = None) -> bool:
        """
        필요한 입력 자원을 소비하는 메서드
        
        Args:
            input_data: 외부에서 제공되는 입력 데이터
            
        Returns:
            bool: 자원 소비 성공 여부
        """
        print(f"[{self.process_name}] 입력 자원 소비 시작")
        
        # 자원 검증 먼저 수행
        if not self.validate_resources():
            print(f"[{self.process_name}] 자원 소비 실패: 요구사항 미충족")
            return False
            
        # 요구사항에 따라 자원 소비
        for requirement in self.resource_requirements:
            if requirement.is_mandatory:
                for resource in self.input_resources:
                    if requirement.is_satisfied_by(resource):
                        if resource.consume(requirement.required_quantity):
                            print(f"  소비: {requirement.name} {requirement.required_quantity}{requirement.unit}")
                        else:
                            print(f"  소비 실패: {requirement.name}")
                            return False
                        break
                        
        print(f"[{self.process_name}] 입력 자원 소비 완료")
        return True
        
    def produce_resources(self, output_data: Any = None) -> List[Resource]:
        """
        출력 자원을 생산하는 메서드
        
        Args:
            output_data: 생산할 출력 데이터
            
        Returns:
            List[Resource]: 생산된 자원 리스트
        """
        print(f"[{self.process_name}] 출력 자원 생산 시작")
        produced_resources = []
        
        # 기본 출력 자원들 생산
        for resource in self.output_resources:
            # 자원 복제하여 생산
            produced_resource = resource.clone()
            produced_resources.append(produced_resource)
            
            # 출력 재고에 추가
            if produced_resource.resource_id in self.current_output_inventory:
                self.current_output_inventory[produced_resource.resource_id].produce(produced_resource.quantity)
            else:
                self.current_output_inventory[produced_resource.resource_id] = produced_resource
                
            print(f"  생산: {produced_resource}")
            
        print(f"[{self.process_name}] 출력 자원 생산 완료 (총 {len(produced_resources)}개)")
        return produced_resources
        
    def get_resource_status(self) -> Dict[str, Any]:
        """
        현재 자원 상태를 반환하는 메서드
        
        Returns:
            Dict[str, Any]: 자원 상태 정보
        """
        return {
            'process_id': self.process_id,
            'process_name': self.process_name,
            'input_resources': [str(r) for r in self.input_resources],
            'output_resources': [str(r) for r in self.output_resources],
            'requirements': [str(req) for req in self.resource_requirements],
            'input_inventory': {k: str(v) for k, v in self.current_input_inventory.items()},
            'output_inventory': {k: str(v) for k, v in self.current_output_inventory.items()}
        }
    
    def get_input_resources(self) -> List[Resource]:
        """
        입력 자원 목록을 반환하는 메서드
        
        Returns:
            List[Resource]: 입력 자원 목록
        """
        return self.input_resources.copy()
    
    def get_output_resources(self) -> List[Resource]:
        """
        출력 자원 목록을 반환하는 메서드
        
        Returns:
            List[Resource]: 출력 자원 목록
        """
        return self.output_resources.copy()
    
    def get_resource_requirements(self) -> List[ResourceRequirement]:
        """
        자원 요구사항 목록을 반환하는 메서드
        
        Returns:
            List[ResourceRequirement]: 자원 요구사항 목록
        """
        return self.resource_requirements.copy()

    def get_process_info(self) -> dict:
        """
        공정 정보를 딕셔너리로 반환
        
        Returns:
            dict: 공정 정보
        """
        return {
            'process_id': self.process_id,
            'process_name': self.process_name,
            'process_type': self.__class__.__name__,
            'next_processes': [p.process_name for p in self.next_processes],
            'previous_processes': [p.process_name for p in self.previous_processes]
        }
    
    def __repr__(self) -> str:
        return f"{self.__class__.__name__}(id='{self.process_id}', name='{self.process_name}')"
    
    def __str__(self) -> str:
        return self.process_name


class GroupWrapperProcess(BaseProcess):
    """다중공정 그룹을 단일 공정처럼 취급하기 위한 래퍼 클래스"""
    
    def __init__(self, group: MultiProcessGroup):
        """
        그룹 래퍼 초기화
        
        Args:
            group: 래핑할 다중공정 그룹
        """
        super().__init__(
            process_id=f"wrapper_{group.group_id}",
            process_name=f"그룹({group.get_group_summary()})"
        )
        self.group = group
        # 그룹 내 모든 공정이 병렬 안전해야 래퍼도 병렬 안전
        self.parallel_safe = all(p.parallel_safe for p in group.processes)
    
    def process_logic(self, input_data: Any = None) -> Any:
        """
        그룹 내 모든 공정을 실행하는 로직
        
        Args:
            input_data: 입력 데이터
            
        Returns:
            Any: 그룹 실행 결과
        """
        return self.group.execute_group(input_data)
