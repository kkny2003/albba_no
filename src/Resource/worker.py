import simpy
from typing import Optional, Generator, List
from src.Resource.helper import ResourceType, Resource


class Worker:
    """SimPy 기반 작업자 모델을 정의하는 클래스입니다."""
    
    def __init__(self, env: simpy.Environment, worker_id: str, skills: List[str] = None, 
                 work_speed: float = 1.0):
        """작업자의 정보를 초기화합니다.
        
        Args:
            env (simpy.Environment): SimPy 시뮬레이션 환경
            worker_id (str): 작업자의 고유 ID
            skills (List[str]): 작업자가 가진 기술 목록
            work_speed (float): 작업 속도 배수 (1.0이 기본 속도)
        """
        self.env = env  # 시뮬레이션 환경
        self.worker_id = worker_id  # 작업자 ID
        self.skills = skills if skills is not None else []  # 보유 기술
        self.work_speed = work_speed  # 작업 속도
        self.resource = simpy.Resource(env, capacity=1)  # 작업자는 한 번에 하나의 작업만 수행
        self.total_tasks_completed = 0  # 완료한 총 작업 수
        self.total_work_time = 0  # 총 작업 시간
        self.current_task = None  # 현재 수행 중인 작업
        
    def work(self, product, task_name: str, base_duration: float) -> Generator[simpy.Event, None, None]:
        """작업자가 특정 작업을 수행하는 프로세스입니다.
        
        Args:
            product: 작업할 제품 객체
            task_name (str): 수행할 작업 이름
            base_duration (float): 기본 작업 시간
            
        Yields:
            simpy.Event: SimPy 이벤트들
        """
        # 작업 시간을 작업자의 속도에 맞게 조정
        actual_duration = base_duration / self.work_speed
        
        # 작업자 리소스 요청
        with self.resource.request() as request:
            yield request  # 작업자가 사용 가능할 때까지 대기
            
            self.current_task = task_name
            start_time = self.env.now
            
            print(f"[시간 {self.env.now:.1f}] 작업자 {self.worker_id}가 제품 {getattr(product, 'product_id', 'Unknown')}에 대한 '{task_name}' 작업을 시작합니다.")
            
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
            'utilization': self.get_utilization()
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
        
    def learn_skill(self, new_skill: str):
        """작업자가 새로운 기술을 습득합니다.
        
        Args:
            new_skill (str): 새로 습득할 기술
        """
        if new_skill not in self.skills:
            self.skills.append(new_skill)
            print(f"작업자 {self.worker_id}가 새로운 기술 '{new_skill}'을 습득했습니다.")


def create_worker_resource(worker_id: str,
                         worker_name: str,
                         skill_level: str = "중급",
                         department: str = "제조부") -> Resource:
    """
    작업자 자원을 생성하는 헬퍼 함수
    
    Args:
        worker_id: 작업자의 고유 ID
        worker_name: 작업자 이름
        skill_level: 기술 수준 (초급, 중급, 고급)
        department: 소속 부서
        
    Returns:
        Resource: 작업자 자원 객체
    """
    worker_resource = Resource(
        resource_id=worker_id,
        name=worker_name,
        resource_type=ResourceType.WORKER,
        quantity=1.0,  # 작업자는 1명
        unit="명"
    )
    
    # 작업자 관련 속성들 설정
    worker_resource.set_property("skill_level", skill_level)
    worker_resource.set_property("department", department)
    worker_resource.set_property("current_task", None)
    worker_resource.set_property("is_working", False)
    worker_resource.set_property("work_hours", 8.0)  # 일일 근무시간
    
    return worker_resource
