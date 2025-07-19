import simpy
from typing import Optional, Generator, Any
from src.Resource.helper import ResourceType, Resource


class Machine:
    """SimPy 기반 기계 모델을 정의하는 클래스입니다."""
    
    def __init__(self, env: simpy.Environment, machine_id: str, machine_type: str, 
                 capacity: int = 1, processing_time: float = 1.0):
        """기계의 ID, 유형, 용량을 초기화합니다.
        
        Args:
            env (simpy.Environment): SimPy 시뮬레이션 환경
            machine_id (str): 기계의 고유 ID
            machine_type (str): 기계의 유형
            capacity (int): 기계가 동시에 처리할 수 있는 작업 수 (기본값: 1)
            processing_time (float): 기본 작업 처리 시간 (기본값: 1.0)
        """
        self.env = env  # 시뮬레이션 환경
        self.machine_id = machine_id  # 기계 ID
        self.machine_type = machine_type  # 기계 유형
        self.processing_time = processing_time  # 처리 시간
        self.resource = simpy.Resource(env, capacity=capacity)  # SimPy 리소스
        self.total_processed = 0  # 총 처리된 작업 수
        self.total_busy_time = 0  # 총 작업 시간
        
    def operate(self, product, processing_time: Optional[float] = None) -> Generator[simpy.Event, None, None]:
        """기계가 제품을 처리하는 프로세스입니다.
        
        Args:
            product: 처리할 제품 객체
            processing_time (Optional[float]): 이 작업의 처리 시간 (None이면 기본값 사용)
            
        Yields:
            simpy.Event: SimPy 이벤트들
        """
        process_time = processing_time if processing_time is not None else self.processing_time
        
        # 기계 리소스 요청
        with self.resource.request() as request:
            yield request  # 기계 사용 가능할 때까지 대기
            
            start_time = self.env.now
            print(f"[시간 {self.env.now:.1f}] {self.machine_id} 기계가 제품 {getattr(product, 'product_id', 'Unknown')} 처리를 시작합니다.")
            
            # 처리 시간만큼 대기
            yield self.env.timeout(process_time)
            
            # 통계 업데이트
            self.total_processed += 1
            self.total_busy_time += process_time
            
            print(f"[시간 {self.env.now:.1f}] {self.machine_id} 기계가 제품 {getattr(product, 'product_id', 'Unknown')} 처리를 완료했습니다.")
    
    def get_utilization(self) -> float:
        """기계의 가동률을 계산합니다.
        
        Returns:
            float: 가동률 (0.0 ~ 1.0)
        """
        if self.env.now == 0:
            return 0.0
        return self.total_busy_time / self.env.now
    
    def get_status(self) -> dict:
        """기계의 현재 상태를 반환합니다.
        
        Returns:
            dict: 기계의 현재 상태 정보
        """
        return {
            'machine_id': self.machine_id,
            'machine_type': self.machine_type,
            'capacity': self.resource.capacity,
            'current_users': len(self.resource.users),
            'queue_length': len(self.resource.queue),
            'total_processed': self.total_processed,
            'utilization': self.get_utilization(),
            'is_busy': len(self.resource.users) > 0
        }

    def __str__(self):
        """기계의 정보를 문자열로 반환합니다."""
        status = self.get_status()
        return (f"기계 ID: {self.machine_id}, 유형: {self.machine_type}, "
                f"용량: {status['capacity']}, 현재 사용자: {status['current_users']}, "
                f"대기열: {status['queue_length']}, 가동률: {status['utilization']:.2%}")
                
    def maintenance(self, duration: float) -> Generator[simpy.Event, None, None]:
        """기계 유지보수 프로세스입니다.
        
        Args:
            duration (float): 유지보수 시간
            
        Yields:
            simpy.Event: SimPy 이벤트들
        """
        print(f"[시간 {self.env.now:.1f}] {self.machine_id} 기계 유지보수를 시작합니다. (예상 시간: {duration})")
        
        # 기계 리소스를 독점적으로 사용
        with self.resource.request() as request:
            yield request
            yield self.env.timeout(duration)
            
        print(f"[시간 {self.env.now:.1f}] {self.machine_id} 기계 유지보수가 완료되었습니다.")


def create_machine_resource(machine_id: str,
                          machine_name: str,
                          machine_type: str = "제조기계",
                          capacity: float = 1.0) -> Resource:
    """
    기계 자원을 생성하는 헬퍼 함수
    
    Args:
        machine_id: 기계의 고유 ID
        machine_name: 기계 이름
        machine_type: 기계 유형 (제조기계, 조립기계, 검사장비 등)
        capacity: 기계 처리 용량
        
    Returns:
        Resource: 기계 자원 객체
    """
    machine_resource = Resource(
        resource_id=machine_id,
        name=machine_name,
        resource_type=ResourceType.MACHINE,
        quantity=1.0,  # 기계는 1대
        unit="대"
    )
    
    # 기계 관련 속성들 설정
    machine_resource.set_property("machine_type", machine_type)
    machine_resource.set_property("capacity", capacity)
    machine_resource.set_property("status", "idle")  # 기계 상태 (idle, running, maintenance)
    machine_resource.set_property("efficiency", 1.0)  # 효율성 (0.0 ~ 1.0)
    machine_resource.set_property("maintenance_hours", 0)  # 유지보수 시간
    
    return machine_resource
