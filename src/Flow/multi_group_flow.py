"""
MultiProcessGroup 모듈 - 병렬 프로세스 그룹 관리

이 모듈은 여러 프로세스를 병렬로 실행하는 그룹 관리 기능을 제공합니다.
& 연산자를 통해 프로세스들을 병렬 그룹으로 결합할 수 있습니다.
"""

from typing import List, Optional, Any, Union, Dict, Generator, Tuple
import uuid
import simpy
from src.Processes.base_process import BaseProcess

# ------------------ Priority Utilities (moved from Processes.base_process) ------------------

class PriorityValidationError(Exception):
    """우선순위 유효성 검사 실패 시 발생하는 예외 (Flow 모듈로 이동)"""
    pass


def parse_process_priority(process_name: str) -> Tuple[str, Optional[int]]:
    """공정명에서 우선순위를 파싱합니다.

    Args:
        process_name: 공정명 (예: "공정2(1)" 또는 "공정2")

    Returns:
        Tuple[str, Optional[int]]: (실제 공정명, 우선순위) 튜플
    """
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
    """공정들의 우선순위 시퀀스가 유효한지 검증합니다.

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




class MultiProcessGroup:
    """다중공정을 그룹으로 관리하여 병렬 실행을 지원하는 클래스 (우선순위 기반 실행 지원)"""
    
    def __init__(self, processes: List['BaseProcess'] = None):
        """
        다중공정 그룹 초기화
        
        Args:
            processes: 그룹에 포함될 공정 리스트
        """
        self.processes = processes or []
        self.group_id = str(uuid.uuid4())
        self.parallel_execution = True
        self.priority_based_execution = False
        self.priority_mapping: Dict[str, int] = {}
        
        # BaseProcess와의 호환성을 위한 속성들
        self.process_id = self.group_id
        self.process_name = self._generate_group_summary()
        self.env = self._extract_environment()
        self.parallel_safe = True
        
        # 공정들에 우선순위가 설정되어 있는지 확인
        self._check_priority_setup()
        
    def _extract_environment(self) -> Optional[simpy.Environment]:
        """
        그룹 내 공정들로부터 SimPy 환경을 추출
        
        Returns:
            simpy.Environment: 첫 번째 공정의 환경 또는 None
        """
        for process in self.processes:
            if hasattr(process, 'env') and process.env is not None:
                return process.env
        return None
        
    def _generate_group_summary(self) -> str:
        """
        그룹의 요약 정보를 생성
        
        Returns:
            str: 그룹 요약 정보
        """
        if not self.processes:
            return "빈 다중공정 그룹"
        
        process_names = [p.process_name for p in self.processes]
        return f"[{' & '.join(process_names)}]"
        
    def _check_priority_setup(self) -> None:
        """공정들의 우선순위 설정 상태를 확인하고 실행 모드를 결정합니다."""
        if not self.processes:
            return
            
        # 연결 시점 우선순위가 있는지 확인
        if self.priority_mapping:
            self.priority_based_execution = True
            print(f"[그룹 {self.group_id}] 우선순위 기반 실행 모드 활성화")
            
    def set_process_priority(self, process: 'BaseProcess', priority: int) -> None:
        """
        공정의 연결 시점 우선순위를 설정합니다.
        
        Args:
            process: 우선순위를 설정할 공정
            priority: 우선순위 (낮은 숫자가 높은 우선순위)
        """
        if not isinstance(process, BaseProcess):
            raise TypeError(f"BaseProcess 타입이어야 합니다. 받은 타입: {type(process)}")
        
        self.priority_mapping[process.process_id] = priority
        self._check_priority_setup()
            
    def sort_by_priority(self) -> List['BaseProcess']:
        """
        우선순위에 따라 공정들을 정렬합니다.
        
        Returns:
            List[BaseProcess]: 우선순위 순으로 정렬된 공정 리스트
        """
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
            
        Raises:
            ValueError: process가 None이거나 BaseProcess가 아닌 경우
        """
        if process is None:
            raise ValueError("추가할 공정이 None입니다.")
        
        if not isinstance(process, BaseProcess):
            raise TypeError(f"BaseProcess 타입이어야 합니다. 받은 타입: {type(process)}")
        
        self.processes.append(process)
        
        # 환경이 없으면 새로 추가된 공정에서 추출
        if self.env is None:
            self.env = self._extract_environment()
        
        # process_name 업데이트
        self.process_name = self._generate_group_summary()
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
                # SimPy 환경에서는 실제 병렬 처리가 아닌 시뮬레이션 병렬 처리
                # 각 공정을 순차적으로 실행하되, 시뮬레이션 시간상 병렬로 처리
                for i, process in enumerate(self.processes, 1):
                    try:
                        print(f"  [{i}/{len(self.processes)}] {process.process_name} 실행 중...")
                        result = process.execute(input_data)
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
        
    # __and__ 연산자는 operators.py에서 동적으로 추가됩니다
    
    # __rshift__ 연산자는 operators.py에서 동적으로 추가됩니다
    
    def __repr__(self) -> str:
        return f"MultiProcessGroup({self.process_name})"


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