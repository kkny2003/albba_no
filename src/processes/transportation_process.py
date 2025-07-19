"""
운송 공정을 처리하는 모듈입니다.
제품이나 자재의 이동을 시뮬레이션하며 배치 운송을 지원합니다.
"""

from .base_process import BaseProcess
from ..Resource.transport import Transport
from ..Resource.helper import Resource, ResourceRequirement, ResourceType
from typing import Any, List, Generator, Optional, Dict, Union
import simpy


class TransportationProcess(BaseProcess):
    """운송 공정을 정의하는 클래스입니다 (SimPy 기반)."""

    def __init__(self, env: simpy.Environment, 
                 transports: List[Transport],
                 source_location: str,
                 destination_location: str,
                 distance: float,
                 input_resources: List[Resource],
                 output_resources: List[Resource],
                 resource_requirements: List[ResourceRequirement],
                 process_id: str, 
                 process_name: str,
                 max_batch_size: int = None):
        """
        운송 공정의 초기화 메서드입니다 (SimPy 환경 필수).

        :param env: SimPy 환경 객체 (필수)
        :param transports: 사용할 운송 수단 목록 (필수)
        :param source_location: 출발지 위치 (필수)
        :param destination_location: 목적지 위치 (필수)
        :param distance: 운송 거리 (필수)
        :param input_resources: 입력 자원 목록 (필수)
        :param output_resources: 출력 자원 목록 (필수)
        :param resource_requirements: 자원 요구사항 목록 (필수)
        :param process_id: 공정 고유 ID (필수)
        :param process_name: 공정 이름 (필수)
        :param max_batch_size: 최대 배치 크기 (None이면 운송 수단 용량 사용)
        """
        # BaseProcess 초기화 (기계나 작업자 대신 운송 수단 사용)
        super().__init__(env, [], [], process_id, process_name)
        
        # 운송 관련 속성 설정
        self.transports = transports if isinstance(transports, list) else [transports]
        self.source_location = source_location
        self.destination_location = destination_location
        self.distance = distance
        
        # 배치 크기 설정 (운송 수단의 최소 용량 사용)
        if max_batch_size is None and self.transports:
            # 모든 운송 수단 중 최소 용량을 배치 크기로 설정
            self.max_batch_size = min(transport.capacity for transport in self.transports)
        else:
            self.max_batch_size = max_batch_size or 1
            
        # 각 운송 수단의 용량도 고려하여 실제 배치 크기 제한
        if self.transports:
            max_transport_capacity = max(transport.capacity for transport in self.transports)
            self.max_batch_size = min(self.max_batch_size, max_transport_capacity)
            
        # 운송 관련 통계
        self.total_products_transported = 0
        self.total_transportation_time = 0.0
        self.batch_transport_count = 0
        self.waiting_products = []  # 배치 운송을 위해 대기 중인 제품들
        
        # 자원 정보 설정
        self._setup_resources(input_resources, output_resources, resource_requirements)
    
    def _setup_resources(self, input_resources: List[Resource], 
                        output_resources: List[Resource],
                        resource_requirements: List[ResourceRequirement]):
        """자원 정보를 설정하는 메서드"""
        # 입력 자원 설정
        for resource in input_resources:
            self.add_input_resource(resource)
        
        # 출력 자원 설정  
        for resource in output_resources:
            self.add_output_resource(resource)
                
        # 자원 요구사항 설정
        for requirement in resource_requirements:
            self.add_resource_requirement(requirement)

    def _setup_default_resources(self):
        """기본 자원 요구사항을 설정하는 메서드"""
        # 운송 수단 자원 추가
        for i, transport in enumerate(self.transports):
            transport_resource = Resource(
                resource_id=f"transport_{i}",
                name=f"운송수단_{transport.transport_id}",
                resource_type=ResourceType.MACHINE,  # 운송 수단을 기계 타입으로 분류
                quantity=1.0,
                unit="대"
            )
            self.add_input_resource(transport_resource)
            
        # 연료/에너지 요구사항 추가
        fuel_requirement = ResourceRequirement(
            resource_type=ResourceType.RAW_MATERIAL,
            name="연료",
            required_quantity=self.distance * 0.1,  # 거리에 비례한 연료 소모
            unit="L"
        )
        self.add_resource_requirement(fuel_requirement)

    def execute(self, product: Any) -> Generator[simpy.Event, None, Any]:
        """
        단일 제품을 운송하는 SimPy generator 프로세스입니다.
        
        :param product: 운송할 제품 객체
        
        Yields:
            simpy.Event: SimPy 이벤트들
            
        Returns:
            Any: 처리된 제품 객체
        """
        start_time = self.env.now
        
        print(f"[시간 {self.env.now:.1f}] 운송 공정 시작: {getattr(product, 'product_id', 'Unknown')} "
              f"({self.source_location} → {self.destination_location})")
        
        # 배치 운송으로 처리
        yield from self._handle_batch_transport(product)
        
        # 통계 업데이트
        processing_time = self.env.now - start_time
        self.total_products_transported += 1
        self.total_transportation_time += processing_time
        
        print(f"[시간 {self.env.now:.1f}] 운송 공정 완료: {getattr(product, 'product_id', 'Unknown')}")
        
        return product

    def _transport_single_product(self, product: Any) -> Generator[simpy.Event, None, None]:
        """단일 제품을 운송하는 내부 메서드"""
        # 사용 가능한 운송 수단 선택 (라운드 로빈 방식)
        transport = self._select_available_transport()
        
        # 운송 실행
        success = yield from transport.transport(product, self.distance)
        
        if not success:
            print(f"[시간 {self.env.now:.1f}] 운송 실패: {getattr(product, 'product_id', 'Unknown')}")

    def _handle_batch_transport(self, product: Any) -> Generator[simpy.Event, None, None]:
        """배치 운송을 처리하는 내부 메서드"""
        # 대기 목록에 제품 추가
        self.waiting_products.append(product)
        
        # 배치 크기에 도달했거나 마지막 제품인 경우 배치 운송 실행
        if len(self.waiting_products) >= self.max_batch_size:
            yield from self._execute_batch_transport()

    def _execute_batch_transport(self) -> Generator[simpy.Event, None, None]:
        """실제 배치 운송을 실행하는 내부 메서드"""
        if not self.waiting_products:
            return
            
        # 사용 가능한 운송 수단 선택
        transport = self._select_available_transport()
        
        # 운송 수단의 용량에 맞춰 배치 크기 조정
        actual_batch_size = min(len(self.waiting_products), transport.capacity)
        batch_products = self.waiting_products[:actual_batch_size]
        self.waiting_products = self.waiting_products[actual_batch_size:]
        
        # 운송 수단 리소스 요청
        with transport.resource.request() as request:
            yield request  # 운송 수단이 사용 가능할 때까지 대기
            
            product_ids = [getattr(p, 'product_id', 'Unknown') for p in batch_products]
            print(f"[시간 {self.env.now:.1f}] {transport.transport_id} 배치 운송 시작: {len(batch_products)}개 제품 (거리: {self.distance})")
            print(f"    운송 제품들: {product_ids}")
            
            # 배치 적재 - 각 제품을 순차적으로 적재
            successful_loads = 0
            for product in batch_products:
                if transport.load_product(product):
                    successful_loads += 1
                else:
                    print(f"[시간 {self.env.now:.1f}] {transport.transport_id} 적재 실패: 용량 초과")
                    break
            
            if successful_loads == 0:
                print(f"[시간 {self.env.now:.1f}] {transport.transport_id} 배치 운송 실패: 제품 적재 불가")
                return
            
            # 운송 시간 계산 (거리 / 속도)
            transport_time = self.distance / transport.transport_speed
            
            # 운송 시간만큼 대기
            yield self.env.timeout(transport_time)
            
            # 배치 하역 - 모든 제품을 순차적으로 하역
            unloaded_products = []
            while transport.current_load > 0:
                unloaded_product = transport.unload_product()
                if unloaded_product:
                    unloaded_products.append(unloaded_product)
            
            # 통계 업데이트
            transport.total_distance_traveled += self.distance
            transport.total_transport_time += transport_time
            
            # 배치 효율성 계산 (적재율)
            batch_efficiency = successful_loads / transport.capacity
            
            print(f"[시간 {self.env.now:.1f}] {transport.transport_id} 배치 운송 완료: {len(unloaded_products)}개 제품")
            print(f"    배치 효율성: {batch_efficiency:.2%} (적재율: {successful_loads}/{transport.capacity})")
            
            self.batch_transport_count += 1

    def _select_available_transport(self) -> Transport:
        """사용 가능한 운송 수단을 선택하는 메서드"""
        # 간단한 라운드 로빈 선택 (실제로는 더 복잡한 스케줄링 로직 가능)
        if hasattr(self, '_transport_index'):
            self._transport_index = (self._transport_index + 1) % len(self.transports)
        else:
            self._transport_index = 0
            
        return self.transports[self._transport_index]

    def force_batch_transport(self) -> Generator[simpy.Event, None, None]:
        """
        대기 중인 모든 제품을 강제로 배치 운송하는 메서드
        시뮬레이션 종료 시 사용
        """
        while self.waiting_products:
            yield from self._execute_batch_transport()

    def get_transportation_statistics(self) -> Dict[str, Any]:
        """운송 통계를 반환하는 메서드"""
        avg_transport_time = (self.total_transportation_time / self.total_products_transported 
                            if self.total_products_transported > 0 else 0)
        
        return {
            "총_운송_제품수": self.total_products_transported,
            "총_운송_시간": self.total_transportation_time,
            "평균_운송_시간": avg_transport_time,
            "배치_운송_횟수": self.batch_transport_count,
            "대기_중인_제품수": len(self.waiting_products),
            "출발지": self.source_location,
            "목적지": self.destination_location,
            "운송_거리": self.distance,
            "사용된_운송_수단수": len(self.transports)
        }

    def __str__(self) -> str:
        """문자열 표현을 반환하는 메서드"""
        return (f"TransportationProcess(name={self.name}, "
                f"source={self.source_location}, "
                f"destination={self.destination_location}, "
                f"distance={self.distance}, "
                f"transports={len(self.transports)})")

    def __repr__(self) -> str:
        """객체 표현을 반환하는 메서드"""
        return self.__str__()
