import simpy
import random
from typing import Optional, Generator, List
from src.Resource.resource_base import ResourceType, Resource


class Worker(Resource):
    """SimPy 기반 작업자 모델을 정의하는 클래스입니다."""
    
    def __init__(self, env: simpy.Environment, worker_id: str, name: str, skills: List[str] = None, 
                 work_speed: float = 1.0, error_probability: Optional[float] = None,
                 mean_time_to_rest: Optional[float] = None, mean_rest_time: Optional[float] = None):
        """작업자의 정보를 초기화합니다.
        
        Args:
            env (simpy.Environment): SimPy 시뮬레이션 환경
            worker_id (str): 작업자의 고유 ID
            name (str): 작업자의 이름
            skills (List[str]): 작업자가 가진 기술 목록
            work_speed (float): 작업 속도 배수 (1.0이 기본 속도)
            error_probability (Optional[float]): 작업당 실수 확률 (0.0~1.0, None=비활성화, 기본값: None)
            mean_time_to_rest (Optional[float]): 평균 휴식 필요 간격 (None=비활성화, 기본값: None)
            mean_rest_time (Optional[float]): 평균 휴식 시간 (None=비활성화, 기본값: None)
        """
        # 작업자별 특성을 properties에 저장
        properties = {
            'skills': skills if skills is not None else [],
            'work_speed': work_speed,
            'error_probability': error_probability,
            'mean_time_to_rest': mean_time_to_rest,
            'mean_rest_time': mean_rest_time,
            'total_tasks_completed': 0,
            'total_work_time': 0,
            'current_task': None,
            'is_resting': False,
            'total_errors': 0,
            'total_rest_time': 0,
            'last_rest_time': 0
        }
        
        # Resource 기본 클래스 초기화
        super().__init__(
            resource_id=worker_id,
            name=name,
            resource_type=ResourceType.WORKER,
            quantity=1,
            properties=properties
        )
        
        # SimPy 관련 속성
        self.env = env  # 시뮬레이션 환경
        self.simpy_resource = simpy.Resource(env, capacity=1)  # 작업자는 한 번에 하나의 작업만 수행
        
    def work(self, product, task_name: str, base_duration: float) -> Generator[simpy.Event, None, None]:
        """작업자가 특정 작업을 수행하는 프로세스입니다.
        
        Args:
            product: 작업할 제품 객체
            task_name (str): 수행할 작업 이름
            base_duration (float): 기본 작업 시간
            
        Yields:
            simpy.Event: SimPy 이벤트들
        """
        # 작업자가 휴식 중인지 확인
        if self.get_property('is_resting', False):
            print(f"[시간 {self.env.now:.1f}] 작업자 {self.resource_id}가 휴식 중입니다. 휴식이 완료될 때까지 대기합니다.")
            return
            
        # 작업 시간을 작업자의 속도에 맞게 조정
        work_speed = self.get_property('work_speed', 1.0)
        actual_duration = base_duration / work_speed
        
        # 작업자 리소스 요청
        with self.simpy_resource.request() as request:
            yield request  # 작업자가 사용 가능할 때까지 대기
            
            self.set_property('current_task', task_name)
            start_time = self.env.now
            
            print(f"[시간 {self.env.now:.1f}] 작업자 {self.resource_id}가 제품 {getattr(product, 'product_id', 'Unknown')}에 대한 '{task_name}' 작업을 시작합니다.")
            
            # 작업 중 실수 발생 체크 (실수 확률이 설정된 경우에만)
            error_prob = self.get_property('error_probability')
            if error_prob is not None and self._check_error():
                print(f"[시간 {self.env.now:.1f}] 작업자 {self.resource_id}가 실수를 했습니다! 작업을 다시 시작합니다.")
                # 실수 발생 시 작업 시간이 1.5배 증가
                actual_duration *= 1.5
                self.set_property('total_errors', self.get_property('total_errors', 0) + 1)
            
            # 휴식 필요 여부 체크 (휴식 기능이 활성화된 경우에만)
            mean_rest = self.get_property('mean_time_to_rest')
            if mean_rest is not None and self._check_rest_needed():
                print(f"[시간 {self.env.now:.1f}] 작업자 {self.resource_id}가 휴식이 필요합니다!")
                # 휴식 프로세스 시작
                yield self.env.process(self._rest_process())
                return  # 휴식 후 작업 재시작 필요
            
            # 작업 시간만큼 대기
            yield self.env.timeout(actual_duration)
            
            # 통계 업데이트
            self.total_tasks_completed += 1
            self.total_work_time += actual_duration
            self.current_task = None
            
            print(f"[시간 {self.env.now:.1f}] 작업자 {self.worker_id}가 '{task_name}' 작업을 완료했습니다.")
    
    def can_perform_task(self, required_skill: str) -> bool:
        """작업자가 특정 기술이 필요한 작업을 수행할 수 있는지 확인합니다.
        
        Args:
            required_skill (str): 필요한 기술
            
        Returns:
            bool: 작업 수행 가능 여부
        """
        return required_skill in self.skills
    
    def get_efficiency(self) -> float:
        """작업자의 작업 효율성을 계산합니다.
        
        Returns:
            float: 효율성 (작업 완료 수 / 시간)
        """
        if self.env.now == 0:
            return 0.0
        return self.total_tasks_completed / self.env.now
    
    def get_utilization(self) -> float:
        """작업자의 가동률을 계산합니다.
        
        Returns:
            float: 가동률 (0.0 ~ 1.0)
        """
        if self.env.now == 0:
            return 0.0
        return self.total_work_time / self.env.now
    
    def get_status(self) -> dict:
        """작업자의 현재 상태를 반환합니다.
        
        Returns:
            dict: 작업자의 현재 상태 정보
        """
        return {
            'worker_id': self.worker_id,
            'skills': self.skills,
            'work_speed': self.work_speed,
            'is_busy': len(self.resource.users) > 0,
            'current_task': self.current_task,
            'total_tasks_completed': self.total_tasks_completed,
            'efficiency': self.get_efficiency(),
            'utilization': self.get_utilization(),
            'is_resting': self.is_resting,
            'total_errors': self.total_errors,
            'error_rate': self.get_error_rate(),
            'availability': self.get_availability()
        }

    def __str__(self):
        """작업자의 정보를 문자열로 반환합니다."""
        status = self.get_status()
        return (f"작업자 ID: {self.worker_id}, 기술: {', '.join(self.skills)}, "
                f"작업 속도: {self.work_speed}x, 현재 작업: {self.current_task or '없음'}, "
                f"완료 작업: {self.total_tasks_completed}, 가동률: {status['utilization']:.2%}")
                
    def take_break(self, duration: float) -> Generator[simpy.Event, None, None]:
        """작업자가 휴식을 취하는 프로세스입니다.
        
        Args:
            duration (float): 휴식 시간
            
        Yields:
            simpy.Event: SimPy 이벤트들
        """
        print(f"[시간 {self.env.now:.1f}] 작업자 {self.worker_id}가 휴식을 시작합니다. (시간: {duration})")
        
        # 작업자 리소스를 독점적으로 사용 (다른 작업 불가)
        with self.resource.request() as request:
            yield request
            yield self.env.timeout(duration)
            
        print(f"[시간 {self.env.now:.1f}] 작업자 {self.worker_id}가 휴식을 마쳤습니다.")
    
    def _check_error(self) -> bool:
        """작업 중 실수 발생 여부를 확인합니다.
        
        Returns:
            bool: 실수 발생 여부
        """
        # 실수 확률이 None이면 실수 발생하지 않음
        if self.error_probability is None:
            return False
        # 실수 확률에 따른 랜덤 실수 발생 체크
        return random.random() < self.error_probability
    
    def _check_rest_needed(self) -> bool:
        """휴식이 필요한지 확인합니다.
        
        Returns:
            bool: 휴식 필요 여부
        """
        # 휴식 관련 매개변수가 None이면 휴식 불필요
        if self.mean_time_to_rest is None:
            return False
        # 평균 휴식 간격에 따른 확률적 휴식 필요 체크
        if self.env.now - self.last_rest_time > self.mean_time_to_rest:
            return random.random() < 0.3  # 30% 확률로 휴식 필요
        return False
    
    def _rest_process(self) -> Generator[simpy.Event, None, None]:
        """작업자 휴식 프로세스를 수행합니다.
        
        Yields:
            simpy.Event: SimPy 이벤트들
        """
        # 휴식 시간이 None이면 기본값 사용
        if self.mean_rest_time is None:
            rest_duration = 10.0  # 기본 휴식 시간
        else:
            # 휴식 시간은 지수분포를 따름 (평균: mean_rest_time)
            rest_duration = random.expovariate(1.0 / self.mean_rest_time)
        
        self.is_resting = True
        self.last_rest_time = self.env.now
        
        print(f"[시간 {self.env.now:.1f}] 작업자 {self.worker_id}가 휴식을 시작합니다. (예상 시간: {rest_duration:.2f})")
        
        # 작업자 리소스를 독점적으로 사용하여 휴식
        with self.resource.request() as request:
            yield request
            yield self.env.timeout(rest_duration)
            
        self.total_rest_time += rest_duration
        self.is_resting = False
        
        print(f"[시간 {self.env.now:.1f}] 작업자 {self.worker_id}의 휴식이 완료되었습니다.")
    
    def get_error_rate(self) -> float:
        """작업자의 실수율을 계산합니다 (실수 횟수 / 완료 작업 수).
        
        Returns:
            float: 실수율
        """
        if self.total_tasks_completed == 0:
            return 0.0
        return self.total_errors / self.total_tasks_completed
    
    def get_availability(self) -> float:
        """작업자의 가용성을 계산합니다 (정상 작업 시간 / 전체 시간).
        
        Returns:
            float: 가용성 (0.0 ~ 1.0)
        """
        if self.env.now == 0:
            return 1.0
        available_time = self.env.now - self.total_rest_time
        return available_time / self.env.now
    
    def force_rest(self) -> Generator[simpy.Event, None, None]:
        """강제로 작업자 휴식을 발생시킵니다 (테스트 용도).
        
        Yields:
            simpy.Event: SimPy 이벤트들
        """
        print(f"[시간 {self.env.now:.1f}] 작업자 {self.worker_id}에게 강제 휴식을 발생시킵니다.")
        yield self.env.process(self._rest_process())
        
    def learn_skill(self, new_skill: str):
        """작업자가 새로운 기술을 습득합니다.
        
        Args:
            new_skill (str): 새로 습득할 기술
        """
        if new_skill not in self.skills:
            self.skills.append(new_skill)
            print(f"작업자 {self.worker_id}가 새로운 기술 '{new_skill}'을 습득했습니다.")


