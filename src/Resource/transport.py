import simpy
from typing import Optional, Generator, List, Dict, Any
from src.Resource.resource_base import Resource, ResourceType


class Transport(Resource):
    """SimPy 기반 운송 모델 클래스입니다. 제품의 이동을 시뮬레이션합니다."""

    def __init__(self, env: simpy.Environment, resource_id: str, name: str, capacity: int = 10, 
                 transport_speed: float = 1.0, transport_type: str = "general"):
        """
        초기화 메서드입니다 (SimPy 환경 필수).
        
        Args:
            env (simpy.Environment): SimPy 환경 객체 (필수)
            resource_id (str): 운송 수단의 ID (필수)
            name (str): 운송 수단의 이름 (필수)
            capacity (int): 운송 수단의 수용 능력 (선택적, 기본값: 10)
                - conveyor: 동시에 위에 존재할 수 있는 product 개수
                - 기타: 운송 수단의 적재 용량
            transport_speed (float): 운송 속도 (단위: 거리/시간, 선택적, 기본값: 1.0)
            transport_type (str): 운송 수단 타입 (선택적, 기본값: "general")
                - "conveyor": 컨베이어 벨트 (transport_time만 사용)
                - "agv": 자동 운반 차량
                - "truck": 트럭
                - "general": 일반 운송 수단
        """
        # Resource 기본 클래스 초기화
        super().__init__(
            resource_id=resource_id,
            name=name,
            resource_type=ResourceType.TRANSPORT
        )
        
        # 운송수단별 특성을 직접 어트리뷰트로 설정
        self.capacity = capacity
        self.transport_speed = transport_speed
        self.transport_type = transport_type  # 운송 수단 타입 추가
        self.current_load = 0
        self.cargo = []
        self.total_distance_traveled = 0.0
        self.total_transport_time = 0.0
        
        # SimPy 관련 속성
        self.env = env  # SimPy 환경
        # conveyor의 경우 capacity만큼 동시에 제품을 운송할 수 있음
        if transport_type == "conveyor":
            self.simpy_resource = simpy.Resource(env, capacity=capacity)
        else:
            self.simpy_resource = simpy.Resource(env, capacity=1)  # 기타 운송 수단은 한 번에 하나의 작업만 수행

    def is_conveyor(self) -> bool:
        """컨베이어 타입인지 확인합니다."""
        return self.transport_type == "conveyor"

    def transport(self, product, distance: float) -> Generator[simpy.Event, None, bool]:
        """
        제품을 운송하는 SimPy generator 프로세스입니다.
        
        Args:
            product: 운송할 제품 객체 (필수)
            distance (float): 운송 거리 (필수)
        
        Yields:
            simpy.Event: SimPy 이벤트들
            
        Returns:
            bool: 운송 성공 여부
        """
        # 운송 수단 리소스 요청
        with self.simpy_resource.request() as request:
            yield request  # 운송 수단이 사용 가능할 때까지 대기
            
            print(f"[시간 {self.env.now:.1f}] {self.resource_id} 운송 시작: {getattr(product, 'resource_id', 'Unknown')} (거리: {distance})")
            
            # conveyor의 경우 간소화된 운송 프로세스
            if self.is_conveyor():
                # conveyor는 적재/하역 없이 transport_time만 사용
                transport_time = distance / self.transport_speed
                print(f"[시간 {self.env.now:.1f}] {self.resource_id} (컨베이어) 운송 중... (소요시간: {transport_time:.1f})")
                yield self.env.timeout(transport_time)
                
                # 통계 업데이트
                self.total_distance_traveled += distance
                self.total_transport_time += transport_time
                
                print(f"[시간 {self.env.now:.1f}] {self.resource_id} (컨베이어) 운송 완료: {getattr(product, 'resource_id', 'Unknown')}")
                return True
            else:
                # 일반 운송 수단의 경우 기존 로직 유지
                # 적재
                if not self.load_product(product):
                    print(f"[시간 {self.env.now:.1f}] {self.resource_id} 적재 실패: 용량 초과")
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
                
                print(f"[시간 {self.env.now:.1f}] {self.resource_id} 운송 완료: {getattr(product, 'resource_id', 'Unknown')}")
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
            print(f"[시간 {self.env.now:.1f}] {self.resource_id} 제품 적재: {getattr(product, 'resource_id', 'Unknown')} (현재 적재량: {self.current_load}/{self.capacity})")
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
            print(f"[시간 {self.env.now:.1f}] {self.resource_id} 제품 하역: {getattr(product, 'resource_id', 'Unknown')} (현재 적재량: {self.current_load}/{self.capacity})")
            return product  # 하역된 제품 반환
        else:
            print(f"[시간 {self.env.now:.1f}] {self.resource_id} 하역할 제품이 없습니다")
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
            'resource_id': self.resource_id,
            'transport_type': self.transport_type,
            'current_load': self.current_load,
            'capacity': self.capacity,
            'is_full': self.is_full(),
            'is_conveyor': self.is_conveyor(),
            'total_distance_traveled': self.total_distance_traveled,
            'total_transport_time': self.total_transport_time,
            'utilization': self.get_utilization(),
            'cargo_list': [getattr(item, 'resource_id', 'Unknown') for item in self.cargo]
        }

    def __str__(self):
        """운송 수단의 정보를 문자열로 반환합니다."""
        return f"{self.resource_id} (적재량: {self.current_load}/{self.capacity}, 속도: {self.transport_speed})"


