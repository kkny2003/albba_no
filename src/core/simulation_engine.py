import simpy
from typing import Optional, Callable, Dict, Any


class SimulationEngine:
    """SimPy 기반 시뮬레이션 엔진 클래스입니다. 시뮬레이션의 실행 및 관리를 담당합니다."""

    def __init__(self, env=None, random_seed: Optional[int] = None):
        """초기화 메서드입니다. SimPy 환경과 시뮬레이션 엔진의 기본 설정을 초기화합니다.
        
        Args:
            env: SimPy 환경 객체 (제공되지 않으면 새로 생성)
            random_seed (Optional[int]): 시뮬레이션의 랜덤 시드. 재현 가능한 결과를 위해 사용
        """
        self.env = env if env is not None else simpy.Environment()  # SimPy 시뮬레이션 환경
        
        self.processes = []  # 실행 중인 프로세스 목록
        self.resources = {}  # 등록된 리소스들
        self.random_seed = random_seed  # 랜덤 시드
        
        if random_seed is not None and isinstance(random_seed, (int, float, str, bytes, bytearray)):
            import random
            random.seed(random_seed)
            
    def add_process(self, process_func: Callable, *args, **kwargs):
        """시뮬레이션에 프로세스를 추가합니다.
        
        Args:
            process_func: SimPy 프로세스 함수 (generator 함수)
            *args, **kwargs: 프로세스 함수에 전달할 인자들
        """
        process = self.env.process(process_func(self.env, *args, **kwargs))
        self.processes.append(process)
            
        return process
        
    def add_resource(self, name: str, resource: simpy.Resource):
        """시뮬레이션에 리소스를 등록합니다.
        
        Args:
            name (str): 리소스 이름
            resource (simpy.Resource): SimPy 리소스 객체
        """
        self.resources[name] = resource
        
    def get_resource(self, name: str) -> Optional[simpy.Resource]:
        """등록된 리소스를 가져옵니다.
        
        Args:
            name (str): 리소스 이름
            
        Returns:
            Optional[simpy.Resource]: 해당 이름의 리소스 또는 None
        """
        return self.resources.get(name)
        
    def run(self, until: Optional[float] = None):
        """시뮬레이션을 실행합니다.
        
        Args:
            until (Optional[float]): 시뮬레이션 종료 시간. None이면 모든 프로세스가 끝날 때까지 실행
        """
        print(f"시뮬레이션이 시작되었습니다. (종료 시간: {until})")
        try:
            self.env.run(until=until)
            print(f"시뮬레이션이 완료되었습니다. (최종 시간: {self.env.now})")
        except KeyboardInterrupt:
            print(f"시뮬레이션이 중단되었습니다. (현재 시간: {self.env.now})")
            
    def get_current_time(self) -> float:
        """현재 시뮬레이션 시간을 반환합니다.
        
        Returns:
            float: 현재 시뮬레이션 시간
        """
        return self.env.now
        
    def reset(self):
        """시뮬레이션을 초기 상태로 리셋합니다."""
        self.env = simpy.Environment()
        self.processes.clear()
        self.resources.clear()
        
    def get_statistics(self) -> Dict[str, Any]:
        """시뮬레이션 통계를 반환합니다.
        
        Returns:
            Dict[str, Any]: 통계 정보 딕셔너리
        """
        return {
            'simulation_time': self.env.now,
            'total_processes': len(self.processes),
            'total_resources': len(self.resources),
            'random_seed': self.random_seed
        }
