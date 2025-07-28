"""
운송 공정을 정의하는 클래스입니다.
출발지에서 도착지로 자원을 운송하는 프로세스를 모델링합니다.
"""

from src.Processes.base_process import BaseProcess
from typing import Any, List, Generator
import simpy
from src.Resource.resource_base import Resource, ResourceRequirement, ResourceType
from src.Resource.transport import Transport


class TransportProcess(BaseProcess):
    """운송 공정을 정의하는 클래스입니다 (SimPy 기반)."""

    def __init__(self, env: simpy.Environment, transports: List[Transport], 
                 route: str,
                 input_resources: List[Resource] = None, 
                 output_resources: List[Resource] = None,
                 resource_requirements: List[ResourceRequirement] = None,
                 process_id: str = None, process_name: str = None,
                 distance: float = 5.0, loading_time: float = 0.2, 
                 unloading_time: float = 0.3, transport_time: float = 0.5,
                 cooldown_time: float = 2.0,
                 failure_weight_machine: float = 1.0, 
                 failure_weight_worker: float = 1.0):
        """
        운송 공정의 초기화 메서드입니다 (SimPy 환경 필수).

        :param env: SimPy 환경 객체 (필수)
        :param transports: 사용될 운송 수단 목록 (필수)
        :param route: 운송 경로 (예: "A1->A2", "창고->조립라인")
        :param input_resources: 운송할 입력 자원 목록
        :param output_resources: 운송 완료 후 출력 자원 목록
        :param resource_requirements: 자원 요구사항 목록
        :param process_id: 공정 고유 ID (선택적)
        :param process_name: 공정 이름 (선택적)
        :param distance: 운송 거리
        :param loading_time: 적재 시간
        :param unloading_time: 하역 시간
        :param transport_time: 운송 중간 처리 시간
        :param cooldown_time: 다음 운송까지 대기 시간
        :param failure_weight_machine: 기계 고장률 가중치 (기본값: 1.0)
        :param failure_weight_worker: 작업자 실수율 가중치 (기본값: 1.0)
        """
        # 경로 파싱 (A1->A2 형태)
        self.source, self.destination = self._parse_route(route)
        
        # BaseProcess 초기화 (transports를 machines로 전달)
        super().__init__(env, machines=transports, workers=None, 
                        process_id=process_id, process_name=process_name or f"{self.source}-{self.destination}_운송",
                        failure_weight_machine=failure_weight_machine,
                        failure_weight_worker=failure_weight_worker)
        
        # 운송 관련 설정
        self.transports = transports if isinstance(transports, list) else [transports]
        self.route = route
        self.distance = distance
        self.loading_time = loading_time
        self.unloading_time = unloading_time
        self.transport_time = transport_time
        self.cooldown_time = cooldown_time
        
        # 자원 설정
        self.input_resources = input_resources or []
        self.output_resources = output_resources or []
        self.resource_requirements = resource_requirements or []
        
        print(f"[{self.process_name}] 운송 공정 초기화 완료 - {self.route} (거리: {self.distance})")

    def _parse_route(self, route: str) -> tuple:
        """
        경로 문자열을 파싱하여 출발지와 도착지를 추출합니다.
        
        Args:
            route: 경로 문자열 (예: "A1->A2", "창고->조립라인")
            
        Returns:
            tuple: (출발지, 도착지)
            
        Raises:
            ValueError: 올바르지 않은 경로 형식인 경우
        """
        # -> 또는 > 기호로 분리
        if '->' in route:
            parts = route.split('->')
        elif '>' in route:
            parts = route.split('>')
        else:
            raise ValueError(f"올바르지 않은 경로 형식입니다. '출발지->도착지' 형태로 입력해주세요. 입력값: {route}")
        
        if len(parts) != 2:
            raise ValueError(f"경로는 정확히 출발지와 도착지 두 부분으로 구성되어야 합니다. 입력값: {route}")
        
        source = parts[0].strip()
        destination = parts[1].strip()
        
        if not source or not destination:
            raise ValueError(f"출발지와 도착지는 비어있을 수 없습니다. 입력값: {route}")
        
        return source, destination

    def log(self, msg):
        """로그 메시지 출력"""
        print(msg)
        # 전역 simulation_logs가 있다면 추가
        try:
            # scenario_chain_operator.py에서 정의된 simulation_logs에 접근
            import __main__
            if hasattr(__main__, 'simulation_logs'):
                __main__.simulation_logs.append(msg)
        except:
            pass  # 전역 로그가 없어도 무시

    def execute(self, input_data: Any = None) -> Generator[simpy.Event, None, Any]:
        """
        운송 공정을 실행합니다.
        
        :param input_data: 입력 데이터 (선택적)
        :return: SimPy Generator
        """
        while True:
            # 운송 가능한 Transport 선택 (첫 번째 운송수단 사용)
            transport = self.transports[0] if self.transports else None
            if not transport:
                self.log(f"[시간 {self.env.now:.1f}] {self.process_name}: 사용 가능한 운송 수단이 없습니다.")
                yield self.env.timeout(1.0)
                continue
            
            # 운송할 자원이 있는 경우에만 실행
            resources_to_transport = self.input_resources if self.input_resources else [input_data] if input_data else []
            
            if not resources_to_transport:
                # 자원이 없으면 대기
                yield self.env.timeout(self.cooldown_time)
                continue
                
            for resource in resources_to_transport:
                if resource is None:
                    continue
                    
                self.log(f"[시간 {self.env.now:.1f}] {transport.resource_id} 운송 시작: {self.route} (거리: {self.distance})")
                
                # 적재 단계
                yield self.env.timeout(self.loading_time)
                self.log(f"[시간 {self.env.now:.1f}] {transport.resource_id} 제품 적재: {resource.name} (현재 적재량: {transport.current_load + 1}/{transport.capacity})")
                transport.current_load += 1
                
                # 중간 운송 처리 시간
                yield self.env.timeout(self.transport_time)
                
                # 하역 단계
                yield self.env.timeout(self.unloading_time)
                self.log(f"[시간 {self.env.now:.1f}] {transport.resource_id} 제품 하역: {resource.name} (현재 적재량: {transport.current_load - 1}/{transport.capacity})")
                transport.current_load -= 1
                
                self.log(f"[시간 {self.env.now:.1f}] {transport.resource_id} 운송 완료: {self.route}")
                
                # Transport 클래스의 실제 운송 메서드 호출
                try:
                    yield from transport.transport(resource, distance=self.distance)
                except Exception as e:
                    self.log(f"[시간 {self.env.now:.1f}] 운송 중 오류 발생: {e}")
                
                # 완료된 자원을 출력 리소스에 추가
                if resource not in self.output_resources:
                    self.output_resources.append(resource)
            
            # 다음 운송까지 대기
            yield self.env.timeout(self.cooldown_time)

    def __rshift__(self, other):
        """>> 연산자를 통한 공정 체이닝 지원"""
        from src.Processes.base_process import ProcessChain
        return ProcessChain([self, other])

    def add_input_resource(self, resource: Resource):
        """입력 자원 추가"""
        if resource not in self.input_resources:
            self.input_resources.append(resource)

    def add_output_resource(self, resource: Resource):
        """출력 자원 추가"""
        if resource not in self.output_resources:
            self.output_resources.append(resource)
