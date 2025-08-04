"""
Flow Operators 모듈 - BaseProcess와의 연산자 기능

이 모듈은 BaseProcess 클래스와 Flow 객체들 간의 연산자 기능을 제공합니다.
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
    """
    if isinstance(right, BaseProcess):
        return ProcessChain([left, right])
    elif isinstance(right, ProcessChain):
        new_chain = ProcessChain([left])
        new_chain.processes.extend(right.processes)
        return new_chain
    elif isinstance(right, MultiProcessGroup):
        # MultiProcessGroup을 래퍼로 감싸서 추가
        group_wrapper = GroupWrapperProcess(right)
        return ProcessChain([left, group_wrapper])
    else:
        raise TypeError(f">> 연산자는 BaseProcess, ProcessChain, 또는 MultiProcessGroup과만 사용할 수 있습니다. {type(right)} 타입은 지원되지 않습니다.")


def create_multi_process_group(left: BaseProcess, right: BaseProcess) -> MultiProcessGroup:
    """
    & 연산자를 사용하여 병렬 그룹 생성
    
    Args:
        left: 왼쪽 공정
        right: 병렬 실행할 공정
        
    Returns:
        MultiProcessGroup: 생성된 병렬 그룹
    """
    if isinstance(right, BaseProcess):
        return MultiProcessGroup([left, right])
    else:
        raise TypeError(f"& 연산자는 BaseProcess와만 사용할 수 있습니다. {type(right)} 타입은 지원되지 않습니다.")


# BaseProcess 클래스에 연산자 메서드 추가
def add_operators_to_base_process():
    """
    BaseProcess 클래스에 연산자 메서드를 동적으로 추가합니다.
    """
    def __rshift__(self, other: Union[BaseProcess, ProcessChain, MultiProcessGroup]) -> ProcessChain:
        """>> 연산자를 사용하여 공정 체인 생성"""
        return create_process_chain(self, other)
    
    def __and__(self, other: BaseProcess) -> MultiProcessGroup:
        """& 연산자를 사용하여 병렬 그룹 생성"""
        return create_multi_process_group(self, other)
    
    # BaseProcess 클래스에 메서드 추가
    BaseProcess.__rshift__ = __rshift__
    BaseProcess.__and__ = __and__


# 모듈 로드 시 자동으로 연산자 추가
add_operators_to_base_process() 