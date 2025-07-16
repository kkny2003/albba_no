import simpy
from typing import List, Dict, Optional, Any, Generator
import uuid
from Resource.helper import Resource, ResourceRequirement, ResourceType


class SimpleResourceManager:
    """SimPy 기반 간단한 자원 관리 클래스입니다. 자원의 할당, 해제, 재고 관리를 담당합니다."""

    def __init__(self, env: simpy.Environment):
        """
        초기화 메서드입니다 (SimPy 환경 필수).
        
        Args:
            env: SimPy 환경 객체
        """
        self.env = env  # SimPy 환경
        self.resources: Dict[str, simpy.Resource] = {}  # SimPy 자원들
        self.resource_metadata: Dict[str, Dict[str, Any]] = {}  # 자원 메타데이터
        self.resource_inventory: Dict[str, Resource] = {}  # 자원 재고 (resource_id를 키로 사용)
        self.allocated_resources: Dict[str, Resource] = {}  # 할당된 자원 목록
        
    def register_simpy_resource(self, resource_id: str, capacity: int, **metadata):
        """
        SimPy 자원을 등록합니다.
        
        Args:
            resource_id: 자원 ID
            capacity: 자원 용량
            **metadata: 추가 메타데이터
        """
        self.resources[resource_id] = simpy.Resource(self.env, capacity=capacity)
        self.resource_metadata[resource_id] = {
            'capacity': capacity,
            'type': metadata.get('type', 'generic'),
            'description': metadata.get('description', ''),
            **metadata
        }
        print(f"[시간 {self.env.now:.1f}] SimPy 자원 등록: {resource_id} (용량: {capacity})")
        
    def request_simpy_resource(self, resource_id: str, requester_id: str) -> Generator[simpy.Event, None, bool]:
        """
        SimPy 자원을 요청하는 generator 메서드
        
        Args:
            resource_id: 자원 ID
            requester_id: 요청자 ID
            
        Yields:
            simpy.Event: SimPy 이벤트들
            
        Returns:
            bool: 할당 성공 여부
        """
        if resource_id not in self.resources:
            print(f"[시간 {self.env.now:.1f}] 자원 요청 실패: {resource_id} (존재하지 않는 자원)")
            return False
            
        print(f"[시간 {self.env.now:.1f}] 자원 요청: {resource_id} by {requester_id}")
        
        # 자원 요청
        with self.resources[resource_id].request() as request:
            yield request
            print(f"[시간 {self.env.now:.1f}] 자원 할당 완료: {resource_id} to {requester_id}")
            return True
        
    def add_resource(self, resource: Resource):
        """자원을 추가하는 메서드입니다.
        
        Args:
            resource: 추가할 자원 객체입니다.
        """
        self.resources.append(resource)
        
        # 재고에 추가 (이미 있으면 수량 증가)
        if resource.resource_id in self.resource_inventory:
            self.resource_inventory[resource.resource_id].produce(resource.quantity)
        else:
            self.resource_inventory[resource.resource_id] = resource.clone()
            
        print(f"자원 추가: {resource}")

    def allocate_resource(self, resource_id: str, required_quantity: float = 1.0) -> Optional[Resource]:
        """특정 자원을 할당하는 메서드입니다.
        
        Args:
            resource_id: 할당할 자원의 ID
            required_quantity: 필요한 수량
            
        Returns:
            할당된 자원 객체입니다. 자원이 부족하면 None을 반환합니다.
        """
        if resource_id in self.resource_inventory:
            available_resource = self.resource_inventory[resource_id]
            
            if available_resource.is_sufficient(required_quantity):
                # 자원 소비
                if available_resource.consume(required_quantity):
                    # 할당된 자원 생성
                    allocated_resource = available_resource.clone(required_quantity)
                    self.allocated_resources[f"{resource_id}_{len(self.allocated_resources)}"] = allocated_resource
                    
                    print(f"자원 할당: {allocated_resource}")
                    return allocated_resource
                    
        print(f"자원 할당 실패: {resource_id} (필요량: {required_quantity})")
        return None

    def allocate_by_requirement(self, requirement: ResourceRequirement) -> Optional[Resource]:
        """자원 요구사항에 따라 자원을 할당하는 메서드입니다.
        
        Args:
            requirement: 자원 요구사항
            
        Returns:
            할당된 자원 객체입니다. 요구사항을 만족하는 자원이 없으면 None을 반환합니다.
        """
        # 요구사항을 만족하는 자원 찾기
        for resource_id, resource in self.resource_inventory.items():
            if requirement.is_satisfied_by(resource):
                return self.allocate_resource(resource_id, requirement.required_quantity)
                
        print(f"요구사항을 만족하는 자원 없음: {requirement}")
        return None

    def release_resource(self, allocated_resource: Resource):
        """할당된 자원을 해제하고 재고로 되돌리는 메서드입니다.
        
        Args:
            allocated_resource: 해제할 자원 객체입니다.
        """
        # 재고로 되돌리기
        if allocated_resource.resource_id in self.resource_inventory:
            self.resource_inventory[allocated_resource.resource_id].produce(allocated_resource.quantity)
        else:
            self.resource_inventory[allocated_resource.resource_id] = allocated_resource.clone()
            
        # 할당 목록에서 제거
        keys_to_remove = []
        for key, resource in self.allocated_resources.items():
            if (resource.resource_id == allocated_resource.resource_id and 
                resource.quantity == allocated_resource.quantity):
                keys_to_remove.append(key)
                
        for key in keys_to_remove:
            del self.allocated_resources[key]
            
        print(f"자원 해제: {allocated_resource}")

    def get_resources(self) -> List[Resource]:
        """현재 자원 목록을 반환하는 메서드입니다.
        
        Returns:
            현재 자원 목록입니다.
        """
        return self.resources

    def get_inventory_status(self) -> Dict[str, Any]:
        """현재 자원 재고 상태를 반환하는 메서드입니다.
        
        Returns:
            자원 재고 상태 정보입니다.
        """
        return {
            'total_resources': len(self.resources),
            'inventory': {k: str(v) for k, v in self.resource_inventory.items()},
            'allocated': {k: str(v) for k, v in self.allocated_resources.items()}
        }
        
    def get_available_quantity(self, resource_id: str) -> float:
        """특정 자원의 사용 가능한 수량을 반환하는 메서드입니다.
        
        Args:
            resource_id: 확인할 자원의 ID
            
        Returns:
            사용 가능한 수량
        """
        if resource_id in self.resource_inventory:
            return self.resource_inventory[resource_id].quantity
        return 0.0
        
    def is_requirement_satisfied(self, requirement: ResourceRequirement) -> bool:
        """자원 요구사항이 현재 재고로 만족 가능한지 확인하는 메서드입니다.
        
        Args:
            requirement: 확인할 자원 요구사항
            
        Returns:
            요구사항 만족 가능 여부
        """
        for resource in self.resource_inventory.values():
            if requirement.is_satisfied_by(resource):
                return True
        return False
        
    def get_resources_by_type(self, resource_type: ResourceType) -> List[Resource]:
        """특정 타입의 자원들을 반환하는 메서드입니다.
        
        Args:
            resource_type: 찾을 자원 타입
            
        Returns:
            해당 타입의 자원 리스트
        """
        return [resource for resource in self.resource_inventory.values() 
                if resource.resource_type == resource_type]