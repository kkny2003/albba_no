"""
Flow Operators 모듈 - 공정 객체들 간의 연산자 기능

이 모듈은 BaseProcess, ProcessChain, MultiProcessGroup 클래스들 간의 연산자 기능을 제공합니다.
>> 연산자와 & 연산자를 통해 공정들을 연결할 수 있습니다.
"""

from typing import Union
from src.Processes.base_process import BaseProcess
from .process_chain import ProcessChain
from .multi_process_group import MultiProcessGroup, GroupWrapperProcess


def create_process_chain(left: BaseProcess, right: Union[BaseProcess, ProcessChain, MultiProcessGroup]) -> ProcessChain:
    """
    >> 연산자를 사용하여 공정 체인 생성
    
    Args:
        left: 왼쪽 공정
        right: 연결할 공정, 체인, 또는 그룹
        
    Returns:
        ProcessChain: 생성된 공정 체인
        
    Raises:
        TypeError: 지원되지 않는 타입의 객체와 연결하려는 경우
    """
    if isinstance(right, BaseProcess):
        return ProcessChain([left, right])
    elif isinstance(right, ProcessChain):
        new_chain = ProcessChain([left])
        new_chain.processes.extend(right.processes)
        # 환경 정보 업데이트
        if new_chain.env is None:
            new_chain.env = new_chain._extract_environment()
        new_chain.process_name = new_chain._generate_process_summary()
        return new_chain
    elif isinstance(right, MultiProcessGroup):
        # MultiProcessGroup을 래퍼로 감싸서 추가
        group_wrapper = GroupWrapperProcess(right)
        return ProcessChain([left, group_wrapper])
    else:
        raise TypeError(
            f">> 연산자는 BaseProcess, ProcessChain, 또는 MultiProcessGroup과만 사용할 수 있습니다. "
            f"{type(right)} 타입은 지원되지 않습니다."
        )


def create_multi_process_group(left: BaseProcess, right: BaseProcess) -> MultiProcessGroup:
    """
    & 연산자를 사용하여 병렬 그룹 생성
    
    Args:
        left: 왼쪽 공정
        right: 병렬 실행할 공정
        
    Returns:
        MultiProcessGroup: 생성된 병렬 그룹
        
    Raises:
        TypeError: BaseProcess가 아닌 객체와 그룹을 생성하려는 경우
    """
    if isinstance(right, BaseProcess):
        return MultiProcessGroup([left, right])
    else:
        raise TypeError(f"& 연산자는 BaseProcess와만 사용할 수 있습니다. {type(right)} 타입은 지원되지 않습니다.")


def chain_rshift(self, other: Union[BaseProcess, ProcessChain, MultiProcessGroup]) -> ProcessChain:
    """
    ProcessChain의 >> 연산자 구현
    
    Args:
        other: 연결할 공정 또는 체인
        
    Returns:
        ProcessChain: 새로운 확장된 체인
        
    Raises:
        TypeError: 지원되지 않는 타입의 객체와 연결하려는 경우
    """
    new_chain = ProcessChain(self.processes.copy())
    
    if isinstance(other, BaseProcess):
        new_chain.add_process(other)
    elif isinstance(other, ProcessChain):
        new_chain.processes.extend(other.processes)
        # 환경 정보 업데이트
        if new_chain.env is None:
            new_chain.env = new_chain._extract_environment()
        new_chain.process_name = new_chain._generate_process_summary()
    elif isinstance(other, MultiProcessGroup):
        # MultiProcessGroup을 래퍼로 감싸서 추가
        group_wrapper = GroupWrapperProcess(other)
        new_chain.add_process(group_wrapper)
    else:
        raise TypeError(
            f">> 연산자는 BaseProcess, ProcessChain, 또는 MultiProcessGroup과만 사용할 수 있습니다. "
            f"{type(other)} 타입은 지원되지 않습니다."
        )
    
    return new_chain


def group_rshift(self, other: Union[BaseProcess, ProcessChain, MultiProcessGroup]) -> ProcessChain:
    """
    MultiProcessGroup의 >> 연산자 구현
    
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
        other_wrapper = GroupWrapperProcess(other)
        return ProcessChain([group_wrapper, other_wrapper])
    else:
        raise TypeError(
            f">> 연산자는 BaseProcess, ProcessChain, 또는 MultiProcessGroup과만 사용할 수 있습니다. "
            f"{type(other)} 타입은 지원되지 않습니다."
        )


def group_and(self, other: BaseProcess) -> MultiProcessGroup:
    """
    MultiProcessGroup의 & 연산자 구현
    연결 시점에 우선순위 문법을 지원합니다: 공정명(우선순위)
    
    Args:
        other: 병렬 실행할 공정 (우선순위 포함 가능)
        
    Returns:
        MultiProcessGroup: 새로운 확장된 그룹
        
    Raises:
        TypeError: BaseProcess가 아닌 객체와 그룹을 생성하려는 경우
        PriorityValidationError: 우선순위가 유효하지 않을 때
    """
    if isinstance(other, BaseProcess):
        # 새로운 공정의 우선순위 파싱
        from src.Processes.base_process import parse_process_priority, validate_priority_sequence
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


def add_operators_to_all_classes():
    """
    모든 공정 클래스에 연산자 메서드를 동적으로 추가합니다.
    """
    # BaseProcess 연산자
    def base_rshift(self, other: Union[BaseProcess, ProcessChain, MultiProcessGroup]) -> ProcessChain:
        """>> 연산자를 사용하여 공정 체인 생성"""
        return create_process_chain(self, other)
    
    def base_and(self, other: BaseProcess) -> MultiProcessGroup:
        """& 연산자를 사용하여 병렬 그룹 생성"""
        return create_multi_process_group(self, other)
    
    # ProcessChain 연산자
    def chain_and(self, other: BaseProcess) -> MultiProcessGroup:
        """& 연산자를 사용하여 병렬 그룹 생성 (ProcessChain용)"""
        if isinstance(other, BaseProcess):
            return MultiProcessGroup(self.processes + [other])
        else:
            raise TypeError(f"& 연산자는 BaseProcess와만 사용할 수 있습니다. {type(other)} 타입은 지원되지 않습니다.")
    
    # 클래스에 메서드 추가
    BaseProcess.__rshift__ = base_rshift
    BaseProcess.__and__ = base_and
    
    ProcessChain.__rshift__ = chain_rshift
    ProcessChain.__and__ = chain_and
    
    MultiProcessGroup.__rshift__ = group_rshift
    MultiProcessGroup.__and__ = group_and


# 모듈 로드 시 자동으로 연산자 추가
add_operators_to_all_classes() 