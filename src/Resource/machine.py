import simpy
import random
from typing import Optional, Generator, Any
from src.Resource.helper import ResourceType, Resource


class Machine:
    """SimPy 기반 기계 모델을 정의하는 클래스입니다."""
    
    def __init__(self, env: simpy.Environment, machine_id: str, machine_type: str, 
                 capacity: int = 1, processing_time: float = 1.0,
                 failure_probability: Optional[float] = None, mean_time_to_failure: Optional[float] = None,
                 mean_time_to_repair: Optional[float] = None):
        """기계의 ID, 유형, 용량 및 고장 관련 매개변수를 초기화합니다.
        
        Args:
            env (simpy.Environment): SimPy 시뮬레이션 환경
            machine_id (str): 기계의 고유 ID
            machine_type (str): 기계의 유형
            capacity (int): 기계가 동시에 처리할 수 있는 작업 수 (기본값: 1)
            processing_time (float): 기본 작업 처리 시간 (기본값: 1.0)
            failure_probability (Optional[float]): 작업당 고장 확률 (0.0~1.0, None=비활성화, 기본값: None)
            mean_time_to_failure (Optional[float]): 평균 고장 간격 시간 (None=비활성화, 기본값: None)
            mean_time_to_repair (Optional[float]): 평균 수리 시간 (None=비활성화, 기본값: None)
        """
        self.env = env  # 시뮬레이션 환경
        self.machine_id = machine_id  # 기계 ID
        self.machine_type = machine_type  # 기계 유형
        self.processing_time = processing_time  # 처리 시간
        self.resource = simpy.Resource(env, capacity=capacity)  # SimPy 리소스
        self.total_processed = 0  # 총 처리된 작업 수
        self.total_busy_time = 0  # 총 작업 시간
        
        # 고장 관련 매개변수
        self.failure_probability = failure_probability  # 작업당 고장 확률 (None이면 비활성화)
        self.mean_time_to_failure = mean_time_to_failure  # 평균 고장 간격 (None이면 비활성화)
        self.mean_time_to_repair = mean_time_to_repair  # 평균 수리 시간 (None이면 비활성화)
        self.is_broken = False  # 현재 고장 상태
        self.total_failures = 0  # 총 고장 횟수
        self.total_repair_time = 0  # 총 수리 시간
        self.last_failure_time = 0  # 마지막 고장 시간
        
    def operate(self, product, processing_time: Optional[float] = None) -> Generator[simpy.Event, None, None]:
        """기계가 제품을 처리하는 프로세스입니다.
        
        Args:
            product: 처리할 제품 객체
            processing_time (Optional[float]): 이 작업의 처리 시간 (None이면 기본값 사용)
            
        Yields:
            simpy.Event: SimPy 이벤트들
        """
        # 기계가 고장 상태인지 확인
        if self.is_broken:
            print(f"[시간 {self.env.now:.1f}] {self.machine_id} 기계가 고장 상태입니다. 수리가 완료될 때까지 대기합니다.")
            return
            
        process_time = processing_time if processing_time is not None else self.processing_time
        
        # 기계 리소스 요청
        with self.resource.request() as request:
            yield request  # 기계 사용 가능할 때까지 대기
            
            start_time = self.env.now
            print(f"[시간 {self.env.now:.1f}] {self.machine_id} 기계가 제품 {getattr(product, 'product_id', 'Unknown')} 처리를 시작합니다.")
            
            # 작업 중 고장 발생 체크 (고장 확률이 설정된 경우에만)
            if self.failure_probability is not None and self._check_failure():
                print(f"[시간 {self.env.now:.1f}] {self.machine_id} 기계에 고장이 발생했습니다!")
                # 고장이 발생하면 수리 프로세스 시작
                yield self.env.process(self._repair_process())
                return  # 고장 발생 시 현재 작업 중단
            
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
            'is_busy': len(self.resource.users) > 0,
            'is_broken': self.is_broken,
            'total_failures': self.total_failures,
            'failure_rate': self.get_failure_rate(),
            'availability': self.get_availability()
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

    def _check_failure(self) -> bool:
        """작업 중 고장 발생 여부를 확인합니다.
        
        Returns:
            bool: 고장 발생 여부
        """
        # 고장 확률이 None이면 고장 발생하지 않음
        if self.failure_probability is None:
            return False
        # 고장 확률에 따른 랜덤 고장 발생 체크
        return random.random() < self.failure_probability
    
    def _repair_process(self) -> Generator[simpy.Event, None, None]:
        """기계 고장 시 수리 프로세스를 수행합니다.
        
        Yields:
            simpy.Event: SimPy 이벤트들
        """
        self.is_broken = True
        self.total_failures += 1
        self.last_failure_time = self.env.now
        
        # 수리 시간이 None이면 기본값 사용
        if self.mean_time_to_repair is None:
            repair_time = 5.0  # 기본 수리 시간
        else:
            # 수리 시간은 지수분포를 따름 (평균: mean_time_to_repair)
            repair_time = random.expovariate(1.0 / self.mean_time_to_repair)
        
        print(f"[시간 {self.env.now:.1f}] {self.machine_id} 기계 수리를 시작합니다. (예상 시간: {repair_time:.2f})")
        
        # 기계 리소스를 독점적으로 사용하여 수리
        with self.resource.request() as request:
            yield request
            yield self.env.timeout(repair_time)
            
        self.total_repair_time += repair_time
        self.is_broken = False
        
        print(f"[시간 {self.env.now:.1f}] {self.machine_id} 기계 수리가 완료되었습니다.")
    
    def get_failure_rate(self) -> float:
        """기계의 고장률을 계산합니다 (고장 횟수 / 운영 시간).
        
        Returns:
            float: 고장률
        """
        if self.env.now == 0:
            return 0.0
        return self.total_failures / self.env.now
    
    def get_availability(self) -> float:
        """기계의 가용성을 계산합니다 (정상 운영 시간 / 전체 시간).
        
        Returns:
            float: 가용성 (0.0 ~ 1.0)
        """
        if self.env.now == 0:
            return 1.0
        uptime = self.env.now - self.total_repair_time
        return uptime / self.env.now
    
    def force_failure(self) -> Generator[simpy.Event, None, None]:
        """강제로 기계 고장을 발생시킵니다 (테스트 용도).
        
        Yields:
            simpy.Event: SimPy 이벤트들
        """
        print(f"[시간 {self.env.now:.1f}] {self.machine_id} 기계에 강제 고장을 발생시킵니다.")
        yield self.env.process(self._repair_process())


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
