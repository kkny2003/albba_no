import simpy
import random
from typing import Optional, Generator, Any
from src.Resource.resource_base import ResourceType, Resource


class Machine(Resource):
    """SimPy 기반 기계 모델을 정의하는 클래스입니다."""
    
    def __init__(self, env: simpy.Environment, machine_id: str, name: str, 
                 capacity: int = 1, processing_time: float = 1.0,
                 failure_probability: Optional[float] = None, mean_time_to_failure: Optional[float] = None,
                 mean_time_to_repair: Optional[float] = None):
        """기계의 ID, 유형, 용량 및 고장 관련 매개변수를 초기화합니다.
        
        Args:
            env (simpy.Environment): SimPy 시뮬레이션 환경
            machine_id (str): 기계의 고유 ID
            name (str): 기계의 이름
            capacity (int): 기계가 동시에 처리할 수 있는 작업 수 (기본값: 1)
            processing_time (float): 기본 작업 처리 시간 (기본값: 1.0)
            failure_probability (Optional[float]): 작업당 고장 확률 (0.0~1.0, None=비활성화, 기본값: None)
            mean_time_to_failure (Optional[float]): 평균 고장 간격 시간 (None=비활성화, 기본값: None)
            mean_time_to_repair (Optional[float]): 평균 수리 시간 (None=비활성화, 기본값: None)
        """
        # 기계별 특성을 properties에 저장
        properties = {
            'capacity': capacity,
            'processing_time': processing_time,
            'failure_probability': failure_probability,
            'mean_time_to_failure': mean_time_to_failure,
            'mean_time_to_repair': mean_time_to_repair,
            'total_processed': 0,
            'total_busy_time': 0,
            'is_broken': False,
            'total_failures': 0,
            'total_repair_time': 0,
            'last_failure_time': 0
        }
        
        # Resource 기본 클래스 초기화
        super().__init__(
            resource_id=machine_id,
            name=name,
            resource_type=ResourceType.MACHINE,
            quantity=1,
            properties=properties
        )
        
        # SimPy 관련 속성
        self.env = env  # 시뮬레이션 환경
        self.simpy_resource = simpy.Resource(env, capacity=capacity)  # SimPy 리소스
        
    def operate(self, product, processing_time: Optional[float] = None) -> Generator[simpy.Event, None, None]:
        """기계가 제품을 처리하는 프로세스입니다.
        
        Args:
            product: 처리할 제품 객체
            processing_time (Optional[float]): 이 작업의 처리 시간 (None이면 기본값 사용)
            
        Yields:
            simpy.Event: SimPy 이벤트들
        """
        # 기계가 고장 상태인지 확인
        if self.get_property('is_broken', False):
            print(f"[시간 {self.env.now:.1f}] {self.resource_id} 기계가 고장 상태입니다. 수리가 완료될 때까지 대기합니다.")
            return
            
        process_time = processing_time if processing_time is not None else self.get_property('processing_time', 1.0)
        
        # 기계 리소스 요청
        with self.simpy_resource.request() as request:
            yield request  # 기계 사용 가능할 때까지 대기
            
            start_time = self.env.now
            print(f"[시간 {self.env.now:.1f}] {self.resource_id} 기계가 제품 {getattr(product, 'product_id', 'Unknown')} 처리를 시작합니다.")
            
            # 작업 중 고장 발생 체크 (고장 확률이 설정된 경우에만)
            failure_prob = self.get_property('failure_probability')
            if failure_prob is not None and self._check_failure():
                print(f"[시간 {self.env.now:.1f}] {self.resource_id} 기계에 고장이 발생했습니다!")
                # 고장이 발생하면 수리 프로세스 시작
                yield self.env.process(self._repair_process())
                return  # 고장 발생 시 현재 작업 중단
            
            # 처리 시간만큼 대기
            yield self.env.timeout(process_time)
            
            # 통계 업데이트
            self.set_property('total_processed', self.get_property('total_processed', 0) + 1)
            self.set_property('total_busy_time', self.get_property('total_busy_time', 0) + process_time)
            
            print(f"[시간 {self.env.now:.1f}] {self.resource_id} 기계가 제품 {getattr(product, 'product_id', 'Unknown')} 처리를 완료했습니다.")
    
    def get_utilization(self) -> float:
        """기계의 가동률을 계산합니다.
        
        Returns:
            float: 가동률 (0.0 ~ 1.0)
        """
        if self.env.now == 0:
            return 0.0
        return self.get_property('total_busy_time', 0) / self.env.now
    
    def get_status(self) -> dict:
        """기계의 현재 상태를 반환합니다.
        
        Returns:
            dict: 기계의 현재 상태 정보
        """
        return {
            'machine_id': self.resource_id,
            'machine_name': self.name,
            'capacity': self.get_property('capacity', 1),
            'current_users': len(self.simpy_resource.users),
            'queue_length': len(self.simpy_resource.queue),
            'total_processed': self.get_property('total_processed', 0),
            'utilization': self.get_utilization(),
            'is_busy': len(self.simpy_resource.users) > 0,
            'is_broken': self.get_property('is_broken', False),
            'total_failures': self.get_property('total_failures', 0),
            'failure_rate': self.get_failure_rate(),
            'availability': self.get_availability()
        }

    def __str__(self):
        """기계의 정보를 문자열로 반환합니다."""
        status = self.get_status()
        return (f"기계 ID: {self.resource_id}, 이름: {self.name}, "
                f"용량: {status['capacity']}, 현재 사용자: {status['current_users']}, "
                f"대기열: {status['queue_length']}, 가동률: {status['utilization']:.2%}")
                
    def maintenance(self, duration: float) -> Generator[simpy.Event, None, None]:
        """기계 유지보수 프로세스입니다.
        
        Args:
            duration (float): 유지보수 시간
            
        Yields:
            simpy.Event: SimPy 이벤트들
        """
        print(f"[시간 {self.env.now:.1f}] {self.resource_id} 기계 유지보수를 시작합니다. (예상 시간: {duration})")
        
        # 기계 리소스를 독점적으로 사용
        with self.simpy_resource.request() as request:
            yield request
            yield self.env.timeout(duration)
            
        print(f"[시간 {self.env.now:.1f}] {self.resource_id} 기계 유지보수가 완료되었습니다.")

    def _check_failure(self) -> bool:
        """작업 중 고장 발생 여부를 확인합니다.
        
        Returns:
            bool: 고장 발생 여부
        """
        # 고장 확률이 None이면 고장 발생하지 않음
        failure_prob = self.get_property('failure_probability')
        if failure_prob is None:
            return False
        # 고장 확률에 따른 랜덤 고장 발생 체크
        return random.random() < failure_prob
    
    def _repair_process(self) -> Generator[simpy.Event, None, None]:
        """기계 고장 시 수리 프로세스를 수행합니다.
        
        Yields:
            simpy.Event: SimPy 이벤트들
        """
        self.set_property('is_broken', True)
        self.set_property('total_failures', self.get_property('total_failures', 0) + 1)
        self.set_property('last_failure_time', self.env.now)
        
        # 수리 시간이 None이면 기본값 사용
        mean_repair_time = self.get_property('mean_time_to_repair')
        if mean_repair_time is None:
            repair_time = 5.0  # 기본 수리 시간
        else:
            # 수리 시간은 지수분포를 따름 (평균: mean_time_to_repair)
            repair_time = random.expovariate(1.0 / mean_repair_time)
        
        print(f"[시간 {self.env.now:.1f}] {self.resource_id} 기계 수리를 시작합니다. (예상 시간: {repair_time:.2f})")
        
        # 기계 리소스를 독점적으로 사용하여 수리
        with self.simpy_resource.request() as request:
            yield request
            yield self.env.timeout(repair_time)
            
        self.set_property('total_repair_time', self.get_property('total_repair_time', 0) + repair_time)
        self.set_property('is_broken', False)
        
        print(f"[시간 {self.env.now:.1f}] {self.resource_id} 기계 수리가 완료되었습니다.")
    
    def get_failure_rate(self) -> float:
        """기계의 고장률을 계산합니다 (고장 횟수 / 운영 시간).
        
        Returns:
            float: 고장률
        """
        if self.env.now == 0:
            return 0.0
        return self.get_property('total_failures', 0) / self.env.now
    
    def get_availability(self) -> float:
        """기계의 가용성을 계산합니다 (정상 운영 시간 / 전체 시간).
        
        Returns:
            float: 가용성 (0.0 ~ 1.0)
        """
        if self.env.now == 0:
            return 1.0
        uptime = self.env.now - self.get_property('total_repair_time', 0)
        return uptime / self.env.now
    
    def force_failure(self) -> Generator[simpy.Event, None, None]:
        """강제로 기계 고장을 발생시킵니다 (테스트 용도).
        
        Yields:
            simpy.Event: SimPy 이벤트들
        """
        print(f"[시간 {self.env.now:.1f}] {self.resource_id} 기계에 강제 고장을 발생시킵니다.")
        yield self.env.process(self._repair_process())


