"""
ProcessChain 모듈 - 순차 프로세스 체인 관리

이 모듈은 여러 프로세스를 순차적으로 연결하여 실행하는 체인 관리 기능을 제공합니다.
>> 연산자를 통해 프로세스들을 연결할 수 있습니다.
"""

from typing import List, Optional, Any, Union, Generator
import uuid
import simpy
from src.Processes.base_process import BaseProcess


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
        # process_name 속성 추가 (MultiProcessGroup 등에서 일관성 있게 사용)
        self.process_name = self.get_process_summary()  # 대표 요약명 반환
        
        # BaseProcess와의 호환성을 위한 추가 속성들
        self.process_id = self.chain_id  # BaseProcess와 동일한 인터페이스
        self.env = self._get_environment_from_processes()  # SimPy 환경 추출
        self.parallel_safe = True  # 기본적으로 병렬 안전으로 설정
    
    
    def _get_environment_from_processes(self) -> Optional[simpy.Environment]:
        """
        체인 내 공정들로부터 SimPy 환경을 추출
        
        Returns:
            simpy.Environment: 첫 번째 공정의 환경 또는 None
        """
        for process in self.processes:
            if hasattr(process, 'env') and process.env is not None:
                return process.env
        return None
    
    def add_process(self, process: 'BaseProcess') -> 'ProcessChain':
        """
        체인에 공정을 추가
        
        Args:
            process: 추가할 공정
            
        Returns:
            ProcessChain: 현재 체인 (메서드 체이닝을 위해)
        """
        self.processes.append(process)
        # 환경이 없으면 새로 추가된 공정에서 추출
        if self.env is None:
            self.env = self._get_environment_from_processes()
        # process_name 업데이트
        self.process_name = self.get_process_summary()
        return self
    
    def execute(self, input_data: Any = None) -> Generator[simpy.Event, None, Any]:
        """
        BaseProcess와 호환되는 SimPy generator 방식의 실행 메서드
        
        Args:
            input_data: 첫 번째 공정에 전달할 입력 데이터
            
        Yields:
            simpy.Event: SimPy 이벤트들
            
        Returns:
            Any: 마지막 공정의 출력 결과
        """
        if not self.env:
            raise RuntimeError(f"ProcessChain '{self.process_name}'에 SimPy 환경이 설정되지 않았습니다. 체인에 유효한 공정을 추가하세요.")
        
        current_data = input_data
        
        print(f"[시간 {self.env.now:.1f}] 공정 체인 실행 시작 (체인 ID: {self.chain_id})")
        print(f"총 {len(self.processes)}개의 공정을 순차 실행합니다.")
        
        for i, process in enumerate(self.processes, 1):
            print(f"\n[시간 {self.env.now:.1f}] [{i}/{len(self.processes)}] {process.process_name} 실행 중...")
            
            # 각 공정을 SimPy generator 방식으로 실행
            if hasattr(process, 'execute') and callable(process.execute):
                # BaseProcess 인스턴스인 경우 yield from으로 호출
                try:
                    current_data = yield from process.execute(current_data)
                    print(f"[시간 {self.env.now:.1f}] [{i}/{len(self.processes)}] {process.process_name} 완료")
                except Exception as e:
                    print(f"[시간 {self.env.now:.1f}] [{i}/{len(self.processes)}] {process.process_name} 실행 중 오류: {e}")
                    raise
            else:
                print(f"[경고] {process.process_name}에 execute 메서드가 없습니다. 건너뜀.")
                continue
        
        print(f"\n[시간 {self.env.now:.1f}] 공정 체인 실행 완료 (체인 ID: {self.chain_id})")
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
            from .multi_process_group import GroupWrapperProcess
            group_wrapper = GroupWrapperProcess(other)
            new_chain.add_process(group_wrapper)
        else:
            raise TypeError(f">> 연산자는 BaseProcess, ProcessChain, 또는 MultiProcessGroup과만 사용할 수 있습니다. {type(other)} 타입은 지원되지 않습니다.")
        
        return new_chain 