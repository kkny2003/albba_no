import simpy
from src.Resource.resource_base import Resource, ResourceType

def inject_dynamic_resource_event(env: simpy.Environment, resources: list):
    """
    시뮬레이션 중 동적으로 신규 자원을 투입하는 이벤트 프로세스
    Args:
        env (simpy.Environment): SimPy 환경
        resources (list): 자원 리스트 (in-place append)
    Yields:
        simpy.Event: SimPy 이벤트
    """
    yield env.timeout(10)
    print(f"[시간 {env.now:.1f}] [동적이벤트] 신규 자원 투입!")
    resources.append(Resource(resource_id='R999', name='긴급부품', resource_type=ResourceType.SEMI_FINISHED))
