"""
MultiProcessGroup 모듈 - 병렬 프로세스 그룹 관리

이 모듈은 여러 프로세스를 병렬로 실행하는 그룹 관리 기능을 제공합니다.
& 연산자를 통해 프로세스들을 병렬 그룹으로 결합할 수 있습니다.
"""

from typing import List, Optional, Any, Union, Dict, Generator, TYPE_CHECKING
import uuid
import concurrent.futures
import simpy
from src.Processes.base_process import BaseProcess

if TYPE_CHECKING:
    from .process_chain import ProcessChain


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
        
        # BaseProcess와의 호환성을 위한 추가 속성들
        self.process_id = self.group_id  # BaseProcess와 동일한 인터페이스
        self.process_name = self.get_group_summary()  # 그룹 요약명
        self.env = self._get_environment_from_processes()  # SimPy 환경 추출
        self.parallel_safe = True  # 기본적으로 병렬 안전으로 설정
        
        # 공정들에 우선순위가 설정되어 있는지 확인
        self._check_priority_setup()
        
    def _get_environment_from_processes(self) -> Optional[simpy.Environment]:
        """
        그룹 내 공정들로부터 SimPy 환경을 추출
        
        Returns:
            simpy.Environment: 첫 번째 공정의 환경 또는 None
        """
        for process in self.processes:
            if hasattr(process, 'env') and process.env is not None:
                return process.env
        return None
        
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
        # 환경이 없으면 새로 추가된 공정에서 추출
        if self.env is None:
            self.env = self._get_environment_from_processes()
        # process_name 업데이트
        self.process_name = self.get_group_summary()
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
        
    def execute(self, input_data: Any = None) -> Generator[simpy.Event, None, List[Any]]:
        """
        BaseProcess와 호환되는 SimPy generator 방식의 실행 메서드
        
        Args:
            input_data: 각 공정에 전달할 입력 데이터
            
        Yields:
            simpy.Event: SimPy 이벤트들
            
        Returns:
            List[Any]: 각 공정의 실행 결과 리스트
        """
        if not self.env:
            raise RuntimeError(f"MultiProcessGroup '{self.process_name}'에 SimPy 환경이 설정되지 않았습니다. 그룹에 유효한 공정을 추가하세요.")
        
        if not self.processes:
            print(f"[시간 {self.env.now:.1f}] 다중공정 그룹 {self.group_id}: 실행할 공정이 없습니다")
            return []
            
        print(f"[시간 {self.env.now:.1f}] 다중공정 그룹 실행 시작 (그룹 ID: {self.group_id})")
        
        # 우선순위 기반 실행이면 정렬된 순서로 실행
        if self.priority_based_execution:
            sorted_processes = self.sort_by_priority()
            print(f"우선순위 기반 순차 실행: {', '.join([p.process_name for p in sorted_processes])}")
            
            results = []
            for i, process in enumerate(sorted_processes, 1):
                try:
                    priority = self.priority_mapping.get(process.process_id, "없음")
                    print(f"  [시간 {self.env.now:.1f}] [{i}/{len(sorted_processes)}] {process.process_name} (우선순위: {priority}) 실행 중...")
                    
                    # SimPy generator 방식으로 실행
                    if hasattr(process, 'execute') and callable(process.execute):
                        result = yield from process.execute(input_data)
                        results.append(result)
                        print(f"  [시간 {self.env.now:.1f}] [OK] {process.process_name} 완료")
                    else:
                        print(f"  [경고] {process.process_name}에 execute 메서드가 없습니다. 건너뜀.")
                        results.append(None)
                        
                except Exception as e:
                    print(f"  [시간 {self.env.now:.1f}] [ERROR] {process.process_name} 실행 중 오류: {e}")
                    results.append(None)
                    
            print(f"[시간 {self.env.now:.1f}] 우선순위 기반 실행 완료 (그룹 ID: {self.group_id})")
            return results
        
        else:
            # 순차 실행 (SimPy에서는 진정한 병렬 실행이 어려우므로 순차로 처리)
            print(f"순차 실행할 공정: {', '.join([p.process_name for p in self.processes])}")
            
            results = []
            for i, process in enumerate(self.processes, 1):
                try:
                    print(f"  [시간 {self.env.now:.1f}] [{i}/{len(self.processes)}] {process.process_name} 실행 중...")
                    
                    # SimPy generator 방식으로 실행
                    if hasattr(process, 'execute') and callable(process.execute):
                        result = yield from process.execute(input_data)
                        results.append(result)
                        print(f"  [시간 {self.env.now:.1f}] [OK] {process.process_name} 완료")
                    else:
                        print(f"  [경고] {process.process_name}에 execute 메서드가 없습니다. 건너뜀.")
                        results.append(None)
                        
                except Exception as e:
                    print(f"  [시간 {self.env.now:.1f}] [ERROR] {process.process_name} 실행 중 오류: {e}")
                    results.append(None)
            
            print(f"[시간 {self.env.now:.1f}] 다중공정 그룹 실행 완료 (그룹 ID: {self.group_id})")
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
        
        try:
            from .process_chain import ProcessChain
            
            if isinstance(other, BaseProcess):
                return ProcessChain([group_wrapper, other])
            elif hasattr(other, 'processes') and hasattr(other, 'add_process'):
                # ProcessChain 또는 유사한 체인 객체인 경우
                new_chain = ProcessChain([group_wrapper])
                new_chain.processes.extend(other.processes)
                return new_chain
            elif hasattr(other, 'processes') and hasattr(other, 'execute'):
                # MultiProcessGroup 또는 유사한 그룹 객체인 경우
                other_wrapper = GroupWrapperProcess(other)
                return ProcessChain([group_wrapper, other_wrapper])
            else:
                raise TypeError(f">> 연산자는 BaseProcess, ProcessChain, 또는 MultiProcessGroup과만 사용할 수 있습니다. {type(other)} 타입은 지원되지 않습니다.")
        except ImportError:
            # ProcessChain을 사용할 수 없는 경우 예외 발생
            raise RuntimeError("ProcessChain 모듈을 import할 수 없습니다. 순환 import 문제가 발생했을 수 있습니다.")
    
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


class GroupWrapperProcess(BaseProcess):
    """MultiProcessGroup을 BaseProcess로 래핑하는 클래스"""
    
    def __init__(self, group: MultiProcessGroup):
        """
        그룹 래퍼 초기화
        
        Args:
            group: 래핑할 MultiProcessGroup
        """
        # BaseProcess 초기화 (그룹의 환경 사용, 빈 machines/workers로 초기화)
        super().__init__(
            env=group.env,
            process_id=f"wrapper_{group.group_id}",
            process_name=f"그룹래퍼({group.process_name})",
            machines=[],  # 그룹 래퍼는 직접적인 기계를 가지지 않음
            workers=[],   # 그룹 래퍼는 직접적인 작업자를 가지지 않음
            input_resources=[],  # 필수 파라미터
            output_resources=[],  # 필수 파라미터
            resource_requirements=[]  # 필수 파라미터
        )
        self.group = group
    
    def validate_resources(self) -> bool:
        """
        그룹 래퍼는 직접적인 자원 검증을 건너뜀 (그룹 내 공정들이 자체적으로 검증)
        
        Returns:
            bool: 항상 True
        """
        return True
        
    def process_logic(self, input_data: Any = None) -> Generator[simpy.Event, None, Any]:
        """
        그룹의 실행 로직을 BaseProcess 인터페이스로 래핑
        
        Args:
            input_data: 그룹에 전달할 입력 데이터
            
        Yields:
            simpy.Event: SimPy 이벤트들
            
        Returns:
            List[Any]: 그룹의 실행 결과 리스트
        """
        # 그룹의 execute 메서드를 호출하여 SimPy generator 방식으로 실행
        results = yield from self.group.execute(input_data)
        return results 