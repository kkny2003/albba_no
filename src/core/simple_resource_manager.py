import simpy
from typing import List, Dict, Optional, Any, Generator
import uuid
from src.Resource.helper import Resource, ResourceRequirement, ResourceType


class UnifiedResourceManager:
    """SimPy Store/Container 기반 통합 자원 관리 클래스 (이중 시스템 제거)"""

    def __init__(self, env: simpy.Environment):
        """
        통합 자원 관리자 초기화 (SimPy Store/Container 기반으로 통합)
        
        Args:
            env: SimPy 환경 객체
        """
        self.env = env  # SimPy 환경
        
        # 통합 자원 관리: Store/Container 기반
        self.resource_stores: Dict[str, simpy.Store] = {}  # 개별 아이템 관리용
        self.resource_containers: Dict[str, simpy.Container] = {}  # 수량 기반 관리용
        self.resource_metadata: Dict[str, Dict[str, Any]] = {}  # 자원 메타데이터
        
        # 이중 관리 시스템 제거: resource_inventory, allocated_resources 통합
        
    def register_resource(self, resource_id: str, capacity: int, resource_type: ResourceType = None, **metadata):
        """
        자원을 Store/Container 기반으로 통합 등록
        
        Args:
            resource_id: 자원 ID
            capacity: 자원 용량
            resource_type: 자원 타입  
            **metadata: 추가 메타데이터
        """
        # 개별 아이템 관리용 Store
        self.resource_stores[resource_id] = simpy.Store(self.env, capacity=capacity)
        
        # 수량 기반 관리용 Container
        self.resource_containers[resource_id] = simpy.Container(self.env, capacity=capacity, init=capacity)
        
        self.resource_metadata[resource_id] = {
            'capacity': capacity,
            'type': resource_type,
            'description': metadata.get('description', ''),
            **metadata
        }
        print(f"[시간 {self.env.now:.1f}] 통합 자원 등록: {resource_id} (용량: {capacity}, 타입: {resource_type})")
        
    def request_resource(self, resource_id: str, requester_id: str, quantity: float = 1.0) -> Generator[simpy.Event, None, bool]:
        """
        통합된 자원 요청 (Store/Container 기반)
        
        Args:
            resource_id: 자원 ID
            requester_id: 요청자 ID
            quantity: 요청 수량
            
        Yields:
            simpy.Event: SimPy 이벤트들
            
        Returns:
            bool: 할당 성공 여부
        """
        if resource_id not in self.resource_containers:
            print(f"[시간 {self.env.now:.1f}] 자원 요청 실패: {resource_id} (존재하지 않는 자원)")
            return False
            
        print(f"[시간 {self.env.now:.1f}] 통합 자원 요청: {resource_id} by {requester_id} (수량: {quantity})")
        
        # Container를 사용한 수량 기반 자원 할당
        yield self.resource_containers[resource_id].get(quantity)
        
        print(f"[시간 {self.env.now:.1f}] 자원 할당 완료: {resource_id} to {requester_id} (수량: {quantity})")
        return True
        
    def release_resource(self, resource_id: str, requester_id: str, quantity: float = 1.0) -> Generator[simpy.Event, None, None]:
        """
        자원 해제 (Container 기반)
        
        Args:
            resource_id: 자원 ID
            requester_id: 요청자 ID  
            quantity: 해제 수량
            
        Yields:
            simpy.Event: SimPy 이벤트들
        """
        if resource_id in self.resource_containers:
            yield self.resource_containers[resource_id].put(quantity)
            print(f"[시간 {self.env.now:.1f}] 자원 해제: {resource_id} by {requester_id} (수량: {quantity})")
        
    def add_resource_item(self, resource_id: str, item: Any) -> Generator[simpy.Event, None, None]:
        """
        Store를 사용한 개별 아이템 추가
        
        Args:
            resource_id: 자원 ID
            item: 추가할 아이템
            
        Yields:
            simpy.Event: SimPy 이벤트들
        """
        if resource_id in self.resource_stores:
            yield self.resource_stores[resource_id].put(item)
            print(f"[시간 {self.env.now:.1f}] 아이템 추가: {resource_id}")
            
    def get_resource_item(self, resource_id: str) -> Generator[simpy.Event, None, Any]:
        """
        Store에서 개별 아이템 회수
        
        Args:
            resource_id: 자원 ID
            
        Yields:
            simpy.Event: SimPy 이벤트들
            
        Returns:
            Any: 회수된 아이템
        """
        if resource_id in self.resource_stores:
            item = yield self.resource_stores[resource_id].get()
            print(f"[시간 {self.env.now:.1f}] 아이템 회수: {resource_id}")
            return item
        return None
    def get_resource_status(self) -> Dict[str, Any]:
        """현재 자원 상태를 반환하는 메서드 (Store/Container 기반)
        
        Returns:
            자원 상태 정보
        """
        status = {}
        for resource_id in self.resource_containers.keys():
            container = self.resource_containers[resource_id]
            store = self.resource_stores[resource_id]
            metadata = self.resource_metadata[resource_id]
            
            status[resource_id] = {
                'capacity': metadata['capacity'],
                'type': metadata.get('type', 'generic'),
                'current_level': container.level,  # Container의 현재 수준
                'available_space': container.capacity - container.level,
                'store_items': len(store.items),  # Store의 아이템 수
                'utilization': container.level / metadata['capacity'] if metadata['capacity'] > 0 else 0.0
            }
        
        return status
        
    def get_available_quantity(self, resource_id: str) -> float:
        """특정 자원의 사용 가능한 수량을 반환하는 메서드 (Container 기반)
        
        Args:
            resource_id: 확인할 자원의 ID
            
        Returns:
            사용 가능한 수량
        """
        if resource_id in self.resource_containers:
            return self.resource_containers[resource_id].level
        return 0.0
        
    def is_resource_available(self, resource_id: str, required_quantity: float) -> bool:
        """자원이 요청 수량만큼 사용 가능한지 확인
        
        Args:
            resource_id: 자원 ID
            required_quantity: 필요한 수량
            
        Returns:
            자원 사용 가능 여부
        """
        if resource_id in self.resource_containers:
            return self.resource_containers[resource_id].level >= required_quantity
        return False