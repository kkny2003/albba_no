import simpy
from typing import Optional, Generator, List, Dict, Any
from src.Resource.helper import Resource, ResourceType


class Transport:
    """SimPy 기반 운송 모델 클래스입니다. 제품의 이동을 시뮬레이션합니다."""

    def __init__(self, env: simpy.Environment, transport_id: str, capacity: int = 10, 
                 transport_speed: float = 1.0):
        """
        초기화 메서드입니다 (SimPy 환경 필수).
        
        :param env: SimPy 환경 객체 (필수)
        :param transport_id: 운송 수단의 ID
        :param capacity: 운송 수단의 수용 능력
        :param transport_speed: 운송 속도 (단위: 거리/시간)
        """
        self.env = env  # SimPy 환경
        self.transport_id = transport_id  # 운송 수단의 ID
        self.capacity = capacity            # 운송 수단의 수용 능력
        self.transport_speed = transport_speed  # 운송 속도
        self.current_load = 0               # 현재 적재량 초기화
        self.resource = simpy.Resource(env, capacity=1)  # 운송 수단은 한 번에 하나의 작업만 수행
        self.cargo = []                     # 적재된 화물 목록
        self.total_distance_traveled = 0.0  # 총 이동 거리
        self.total_transport_time = 0.0     # 총 운송 시간

    def transport(self, product, distance: float) -> Generator[simpy.Event, None, bool]:
        """
        제품을 운송하는 SimPy generator 프로세스입니다.
        
        :param product: 운송할 제품 객체
        :param distance: 운송 거리
        
        Yields:
            simpy.Event: SimPy 이벤트들
            
        Returns:
            bool: 운송 성공 여부
        """
        # 운송 수단 리소스 요청
        with self.resource.request() as request:
            yield request  # 운송 수단이 사용 가능할 때까지 대기
            
            print(f"[시간 {self.env.now:.1f}] {self.transport_id} 운송 시작: {getattr(product, 'product_id', 'Unknown')} (거리: {distance})")
            
            # 적재
            if not self.load_product(product):
                print(f"[시간 {self.env.now:.1f}] {self.transport_id} 적재 실패: 용량 초과")
                return False
            
            # 운송 시간 계산 (거리 / 속도)
            transport_time = distance / self.transport_speed
            
            # 운송 시간만큼 대기
            yield self.env.timeout(transport_time)
            
            # 하역
            self.unload_product()
            
            # 통계 업데이트
            self.total_distance_traveled += distance
            self.total_transport_time += transport_time
            
            print(f"[시간 {self.env.now:.1f}] {self.transport_id} 운송 완료: {getattr(product, 'product_id', 'Unknown')}")
            return True

    def load_product(self, product) -> bool:
        """
        제품을 운송 수단에 적재합니다.
        
        :param product: 적재할 제품 객체
        :return: 적재 성공 여부
        """
        if self.current_load < self.capacity:
            self.current_load += 1  # 적재량 증가
            self.cargo.append(product)  # 화물 목록에 추가
            print(f"[시간 {self.env.now:.1f}] {self.transport_id} 제품 적재: {getattr(product, 'product_id', 'Unknown')} (현재 적재량: {self.current_load}/{self.capacity})")
            return True  # 적재 성공
        else:
            return False  # 적재 실패

    def unload_product(self):
        """
        운송 수단에서 제품을 하역합니다.
        
        :return: 하역된 제품 또는 None
        """
        if self.current_load > 0:
            product = self.cargo.pop()  # 마지막 제품 제거
            self.current_load -= 1  # 적재량 감소
            print(f"[시간 {self.env.now:.1f}] {self.transport_id} 제품 하역: {getattr(product, 'product_id', 'Unknown')} (현재 적재량: {self.current_load}/{self.capacity})")
            return product  # 하역된 제품 반환
        else:
            print(f"[시간 {self.env.now:.1f}] {self.transport_id} 하역할 제품이 없습니다")
            return None  # 하역할 제품이 없음

    def get_current_load(self) -> int:
        """
        현재 적재량을 반환합니다.
        
        :return: 현재 적재량
        """
        return self.current_load

    def is_full(self) -> bool:
        """
        운송 수단이 가득 찼는지 확인합니다.
        
        :return: 가득 찼으면 True, 아니면 False
        """
        return self.current_load >= self.capacity

    def get_utilization(self) -> float:
        """
        운송 수단의 가동률을 계산합니다.
        
        :return: 가동률 (0.0 ~ 1.0)
        """
        if self.env.now > 0:
            return self.total_transport_time / self.env.now
        return 0.0

    def get_status(self) -> dict:
        """
        운송 수단의 현재 상태를 반환합니다.
        
        :return: 상태 정보 딕셔너리
        """
        return {
            'transport_id': self.transport_id,
            'current_load': self.current_load,
            'capacity': self.capacity,
            'is_full': self.is_full(),
            'total_distance_traveled': self.total_distance_traveled,
            'total_transport_time': self.total_transport_time,
            'utilization': self.get_utilization(),
            'cargo_list': [getattr(item, 'product_id', 'Unknown') for item in self.cargo]
        }

    def __str__(self):
        """운송 수단의 정보를 문자열로 반환합니다."""
        return f"{self.transport_id} (적재량: {self.current_load}/{self.capacity}, 속도: {self.transport_speed})"


def create_transport_resource(transport_id: str, 
                            transport_name: str,
                            capacity: float,
                            transport_type: str = "지게차") -> Resource:
    """
    운송 자원을 생성하는 헬퍼 함수
    
    Args:
        transport_id: 운송 수단의 고유 ID
        transport_name: 운송 수단 이름
        capacity: 운송 용량
        transport_type: 운송 수단 타입 (지게차, 컨베이어벨트, 운반차 등)
        
    Returns:
        Resource: 운송 자원 객체
    """
    transport_resource = Resource(
        resource_id=transport_id,
        name=transport_name,
        resource_type=ResourceType.TRANSPORT,
        quantity=1.0,  # 운송 수단 자체는 1개
        unit="대"
    )
    
    # 운송 관련 속성들 설정
    transport_resource.set_property("capacity", capacity)
    transport_resource.set_property("current_load", 0.0)
    transport_resource.set_property("transport_type", transport_type)
    transport_resource.set_property("is_moving", False)
    transport_resource.set_property("speed", 1.0)  # 이동 속도 (단위: m/s 또는 적절한 단위)
    
    return transport_resource
