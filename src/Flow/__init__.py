"""
Flow 모듈 - 프로세스 흐름 관리

이 모듈은 제조 시뮬레이션에서 프로세스들의 흐름을 관리하는 기능을 제공합니다.
순차 실행, 병렬 실행, 조건부 분기 등의 복잡한 워크플로우를 지원합니다.
"""

from .process_chain import ProcessChain
from .multi_process_group import MultiProcessGroup, GroupWrapperProcess
from .advanced_workflow import AdvancedWorkflowManager, ExecutionMode, SynchronizationType
from . import operators  # 연산자 기능 자동 로드

__all__ = [
    'ProcessChain',
    'MultiProcessGroup', 
    'GroupWrapperProcess',
    'AdvancedWorkflowManager',
    'ExecutionMode',
    'SynchronizationType'
] 