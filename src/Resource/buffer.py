import simpy
from typing import Optional, Generator, Any, List, Union
from enum import Enum
from src.Resource.resource_base import ResourceType, Resource


class BufferPolicy(Enum):
    """버퍼 정책을 정의하는 열거형"""
    FIFO = "선입선출"  # First In First Out
    LIFO = "후입선출"  # Last In First Out


class Buffer(Resource):
    """SimPy 기반 버퍼 모델을 정의하는 클래스입니다."""
    
    def __init__(self, env: simpy.Environment, buffer_id: str, name: str, buffer_type: str, 
                 capacity: int = 100, policy: BufferPolicy = BufferPolicy.FIFO):
        """버퍼의 ID, 유형, 용량, 정책을 초기화합니다.
        
        Args:
            env (simpy.Environment): SimPy 시뮬레이션 환경
            buffer_id (str): 버퍼의 고유 ID
            name (str): 버퍼의 이름
            buffer_type (str): 버퍼의 유형
            capacity (int): 버퍼의 최대 저장 용량 (기본값: 100)
            policy (BufferPolicy): 버퍼 정책 (기본값: FIFO)
        """
        # Resource 기본 클래스 초기화
        super().__init__(
            resource_id=buffer_id,
            name=name,
            resource_type=ResourceType.BUFFER,
            quantity=capacity
        )
        
        # 버퍼별 특성을 직접 어트리뷰트로 설정
        self.buffer_type = buffer_type
        self.capacity = capacity
        self.policy = policy
        self.total_put_operations = 0
        self.total_get_operations = 0
        self.total_items_stored = 0
        self.total_items_retrieved = 0
        
        # SimPy 관련 속성
        self.env = env  # 시뮬레이션 환경
        
        # SimPy Store를 사용하여 버퍼 구현 (개선된 방식)
        if policy == BufferPolicy.FIFO:
            self.store = simpy.Store(env, capacity=capacity)
        else:  # LIFO
            self.store = simpy.Store(env, capacity=capacity)
        
    def put(self, item: Any, quantity: int = 1) -> Generator[simpy.Event, None, None]:
        """버퍼에 아이템을 저장하는 프로세스입니다. (Store 기반으로 개선)
        
        Args:
            item: 저장할 아이템 객체
            quantity (int): 저장할 수량 (기본값: 1)
            
        Yields:
            simpy.Event: SimPy 이벤트들
        """
        # LIFO 정책 지원을 위한 특별 처리
        if self.policy == BufferPolicy.LIFO:
            # LIFO를 위해 아이템을 역순으로 저장
            items_to_store = [item] * quantity
            items_to_store.reverse()
            for item_to_store in items_to_store:
                yield self.store.put(item_to_store)
        else:  # FIFO (기본 Store 동작)
            for _ in range(quantity):
                yield self.store.put(item)
        
        # 통계 업데이트
        self.total_put_operations += 1
        self.total_items_stored += quantity
        
        print(f"[시간 {self.env.now:.1f}] {self.buffer_id} 버퍼에 {getattr(item, 'product_id', str(item))} {quantity}개 저장됨 (Store 기반). "
              f"현재 저장량: {len(self.store.items)}/{self.capacity}")
        
    def get(self, quantity: int = 1) -> Generator[simpy.Event, None, Any]:
        """버퍼에서 아이템을 가져오는 프로세스입니다. (Store 기반으로 개선)
        
        Args:
            quantity (int): 가져올 수량 (기본값: 1)
            
        Yields:
            simpy.Event: SimPy 이벤트들
            
        Returns:
            Any: 가져온 아이템(들)
        """
        # Store에서 아이템 직접 회수 (정책과 무관하게 Store가 FIFO 처리)
        retrieved_items = []
        for _ in range(quantity):
            item = yield self.store.get()  # Store에서 직접 아이템 회수
            retrieved_items.append(item)
        
        # 통계 업데이트
        self.total_get_operations += 1
        self.total_items_retrieved += quantity
        
        item_ids = [getattr(item, 'product_id', str(item)) for item in retrieved_items]
        print(f"[시간 {self.env.now:.1f}] {self.buffer_id} 버퍼에서 {item_ids} {quantity}개 회수됨 (Store 기반). "
              f"현재 저장량: {len(self.store.items)}/{self.capacity}")
        
        return retrieved_items[0] if quantity == 1 else retrieved_items
        
    def peek(self, quantity: int = 1) -> List[Any]:
        """버퍼의 내용을 제거하지 않고 확인합니다.
        
        Args:
            quantity (int): 확인할 수량 (기본값: 1)
            
        Returns:
            List[Any]: 확인된 아이템들
        """
        # Store.items 직접 사용하여 확인 (중복 관리 제거)
        store_items = list(self.store.items)
        
        if quantity > len(store_items):
            return store_items
            
        if self.policy == BufferPolicy.FIFO:
            return store_items[:quantity]
        else:  # LIFO
            return store_items[-quantity:]
            
    def is_empty(self) -> bool:
        """버퍼가 비어있는지 확인합니다.
        
        Returns:
            bool: 버퍼가 비어있으면 True, 아니면 False
        """
        return len(self.store.items) == 0
        
    def is_full(self) -> bool:
        """버퍼가 가득 찼는지 확인합니다.
        
        Returns:
            bool: 버퍼가 가득 찼으면 True, 아니면 False
        """
        return len(self.store.items) >= self.capacity
        
    def get_available_space(self) -> int:
        """사용 가능한 공간을 반환합니다.
        
        Returns:
            int: 사용 가능한 공간
        """
        return self.capacity - len(self.store.items)
        
    def get_current_level(self) -> int:
        """현재 저장량을 반환합니다.
        
        Returns:
            int: 현재 저장된 아이템 수
        """
        return len(self.store.items)
        
    def get_utilization(self) -> float:
        """버퍼의 사용률을 계산합니다.
        
        Returns:
            float: 사용률 (0.0 ~ 1.0)
        """
        return len(self.store.items) / self.capacity if self.capacity > 0 else 0.0
        
    def get_status(self) -> dict:
        """버퍼의 현재 상태를 반환합니다.
        
        Returns:
            dict: 버퍼의 현재 상태 정보
        """
        return {
            'buffer_id': self.buffer_id,
            'buffer_type': self.buffer_type,
            'capacity': self.capacity,
            'current_level': self.get_current_level(),
            'available_space': self.get_available_space(),
            'utilization': self.get_utilization(),
            'policy': self.policy.value,
            'is_empty': self.is_empty(),
            'is_full': self.is_full(),
            'total_put_operations': self.total_put_operations,
            'total_get_operations': self.total_get_operations,
            'total_items_stored': self.total_items_stored,
            'total_items_retrieved': self.total_items_retrieved
        }

    def __str__(self):
        """버퍼의 정보를 문자열로 반환합니다."""
        status = self.get_status()
        return (f"버퍼 ID: {self.buffer_id}, 유형: {self.buffer_type}, "
                f"용량: {status['capacity']}, 현재 저장량: {status['current_level']}, "
                f"사용률: {status['utilization']:.2%}, 정책: {status['policy']}")
                
    def clear(self) -> Generator[simpy.Event, None, None]:
        """버퍼를 비우는 프로세스입니다.
        
        Yields:
            simpy.Event: SimPy 이벤트들
        """
        current_level = len(self.store.items)
        if current_level > 0:
            # 모든 아이템 제거 (Store에서 직접 제거)
            for _ in range(current_level):
                yield self.store.get()
            
            print(f"[시간 {self.env.now:.1f}] {self.buffer_id} 버퍼가 비워졌습니다. "
                  f"제거된 아이템 수: {current_level}")


