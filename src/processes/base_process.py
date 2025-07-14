"""
기본 공정 클래스와 공정 체인을 관리하는 모듈입니다.
모든 제조 공정의 기본이 되는 클래스와 >> 연산자를 통한 공정 연결 기능을 제공합니다.
"""

from typing import List, Optional, Any, Union, Dict
from abc import ABC, abstractmethod
import uuid
from ..models.resource import Resource, ResourceRequirement, ResourceType


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
    
    def __rshift__(self, other: Union['BaseProcess', 'ProcessChain']) -> 'ProcessChain':
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
        else:
            raise TypeError(f">> 연산자는 BaseProcess 또는 ProcessChain과만 사용할 수 있습니다. {type(other)} 타입은 지원되지 않습니다.")
        
        return new_chain


class BaseProcess(ABC):
    """모든 제조 공정의 기본이 되는 추상 클래스"""
    
    def __init__(self, process_id: str = None, process_name: str = None):
        """
        기본 공정 초기화
        
        Args:
            process_id: 공정 고유 ID (선택적, 자동 생성됨)
            process_name: 공정 이름 (선택적)
        """
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
        
    def execute(self, input_data: Any = None) -> Any:
        """
        공정을 실행하는 메서드 (기본 구현)
        
        기본적으로 다음 순서로 실행됩니다:
        1. 입력 자원 소비 (consume_resources)
        2. 구체적인 공정 로직 실행 (process_logic - 하위 클래스에서 구현)
        3. 출력 자원 생산 (produce_resources)
        
        Args:
            input_data: 공정에 전달되는 입력 데이터
            
        Returns:
            Any: 공정 실행 결과 (생산된 자원 포함)
        """
        print(f"[{self.process_name}] 공정 실행 시작")
        
        # 1. 자원 소비
        if not self.consume_resources(input_data):
            print(f"[{self.process_name}] 공정 실행 실패: 자원 부족")
            return None
            
        # 2. 구체적인 공정 로직 실행 (하위 클래스에서 구현)
        result = self.process_logic(input_data)
        
        # 3. 자원 생산
        produced_resources = self.produce_resources(result)
        
        print(f"[{self.process_name}] 공정 실행 완료")
        
        # 결과와 생산된 자원을 함께 반환
        return {
            'result': result,
            'produced_resources': produced_resources,
            'process_info': self.get_resource_status()
        }
        
    @abstractmethod
    def process_logic(self, input_data: Any = None) -> Any:
        """
        구체적인 공정 로직을 실행하는 추상 메서드
        각 구체적인 공정 클래스에서 구현해야 함
        
        Args:
            input_data: 공정에 전달되는 입력 데이터
            
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
    
    def __rshift__(self, other: Union['BaseProcess', 'ProcessChain']) -> ProcessChain:
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
        
        else:
            raise TypeError(f">> 연산자는 BaseProcess 또는 ProcessChain과만 사용할 수 있습니다. {type(other)} 타입은 지원되지 않습니다.")
    
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
                    print(f"  ✓ 요구사항 만족: {requirement}")
                    break
                    
            if not satisfied and requirement.is_mandatory:
                print(f"  ✗ 필수 요구사항 미충족: {requirement}")
                return False
            elif not satisfied:
                print(f"  ! 선택적 요구사항 미충족: {requirement}")
                
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
