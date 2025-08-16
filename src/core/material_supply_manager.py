"""
MaterialSupplyManager: 자재 보충 시스템을 위한 프레임워크 컴포넌트

이 모듈은 제조 시뮬레이션에서 자재 보충을 자동화하고 관리하는 기능을 제공합니다.
ReportManager와 통합하여 임계값 기반 자동 보충 시스템을 구현합니다.
"""

import simpy
from typing import Dict, List, Optional, Callable, Any
from dataclasses import dataclass
from enum import Enum

from src.Resource.product import Product
from src.core.report_manager import ReportManager
from src.Processes.transport_process import TransportProcess


class SupplyStrategy(Enum):
    """자재 보충 전략"""
    IMMEDIATE = "immediate"      # 즉시 보충
    SCHEDULED = "scheduled"      # 스케줄 기반 보충
    THRESHOLD_BASED = "threshold"  # 임계값 기반 보충


@dataclass
class MaterialConfig:
    """자재 설정 클래스"""
    material_name: str
    material_type: str
    default_quantity: int = 30
    min_threshold: int = 10
    warning_threshold: int = 20
    max_capacity: Optional[int] = None
    supply_time: float = 2.0  # 자재 생성 시간
    

@dataclass
class SupplyRoute:
    """자재 공급 경로 설정"""
    source_id: str
    target_buffer: Any
    transport_process: TransportProcess
    material_config: MaterialConfig
    

class MaterialSupplyManager:
    """
    자재 보충을 관리하는 프레임워크 컴포넌트
    
    ReportManager와 통합하여 버퍼 상태를 모니터링하고
    임계값에 따라 자동으로 자재를 보충하는 시스템을 제공합니다.
    """
    
    def __init__(self, env: simpy.Environment, report_manager: Optional[ReportManager] = None):
        """
        MaterialSupplyManager 초기화
        
        Args:
            env: SimPy 환경
            report_manager: ReportManager 인스턴스 (None인 경우 새로 생성)
        """
        self.env = env
        self.report_manager = report_manager or ReportManager(env)
        
        # 자재 설정과 공급 경로 관리
        self.material_configs: Dict[str, MaterialConfig] = {}
        self.supply_routes: Dict[str, SupplyRoute] = {}
        
        # 공급 통계
        self.supply_count = 0
        self.total_supplies = {}
        
        # 활성 상태 관리
        self.is_monitoring = False
        self.monitoring_process = None
        
    def register_material(self, material_name: str, material_config: MaterialConfig):
        """
        자재 설정을 등록합니다
        
        Args:
            material_name: 자재명
            material_config: 자재 설정
        """
        self.material_configs[material_name] = material_config
        self.total_supplies[material_name] = 0
        
    def register_supply_route(self, route_id: str, supply_route: SupplyRoute):
        """
        자재 공급 경로를 등록합니다
        
        Args:
            route_id: 공급 경로 ID
            supply_route: 공급 경로 설정
        """
        self.supply_routes[route_id] = supply_route
        
        # ReportManager에 버퍼 등록 및 임계값 설정
        buffer = supply_route.target_buffer
        material_config = supply_route.material_config
        
        self.report_manager.register_resource(buffer.resource_id, buffer)
        self.report_manager.alert_system.set_threshold_rule(
            f"{buffer.resource_id}_current_level",
            warning=material_config.warning_threshold,
            critical=material_config.min_threshold
        )
        
    def create_materials(self, material_name: str, quantity: Optional[int] = None) -> List[Product]:
        """
        자재를 생성합니다 (SimPy 제너레이터)
        
        Args:
            material_name: 자재명
            quantity: 생성할 수량 (None인 경우 기본값 사용)
            
        Yields:
            List[Product]: 생성된 자재 리스트
        """
        if material_name not in self.material_configs:
            raise ValueError(f"등록되지 않은 자재: {material_name}")
            
        config = self.material_configs[material_name]
        actual_quantity = quantity or config.default_quantity
        
        # 자재 생성 시간 대기
        yield self.env.timeout(config.supply_time)
        
        # 공급 통계 업데이트
        self.supply_count += 1
        self.total_supplies[material_name] += actual_quantity
        
        # 자재 생성
        materials = [
            Product(f'{material_name}_{self.supply_count}_{i}', config.material_type)
            for i in range(actual_quantity)
        ]
        
        print(f"[MaterialSupplyManager] {material_name} {actual_quantity}개 생성 완료 (총 공급: {self.total_supplies[material_name]}개)")
        return materials
        
    def auto_replenish(self, route_id: str, quantity: Optional[int] = None):
        """
        자동 보충 프로세스 (SimPy 제너레이터)
        
        Args:
            route_id: 공급 경로 ID
            quantity: 보충할 수량 (None인 경우 기본값 사용)
        """
        if route_id not in self.supply_routes:
            print(f"[MaterialSupplyManager] 경고: 등록되지 않은 공급 경로 {route_id}")
            return
            
        route = self.supply_routes[route_id]
        material_name = route.material_config.material_name
        
        try:
            # 자재 생성
            materials = yield from self.create_materials(material_name, quantity)
            
            # 운송 및 버퍼에 투입
            for material in materials:
                yield from route.transport_process.execute(material)
                yield from route.target_buffer.put(material)
                
            print(f"[MaterialSupplyManager] {route.target_buffer.name} 자동 보충 완료")
            
        except Exception as e:
            print(f"[MaterialSupplyManager] 자동 보충 실패 ({route_id}): {e}")
            
    def handle_buffer_alert(self, alert: Dict[str, Any]):
        """
        버퍼 알림 처리 핸들러
        
        Args:
            alert: ReportManager에서 발생한 알림 정보
        """
        if 'current_level' not in alert['metric_name']:
            return
            
        buffer_id = alert['component_id']
        
        # 해당 버퍼와 연결된 공급 경로 찾기
        matching_route = None
        route_id = None
        
        for rid, route in self.supply_routes.items():
            if route.target_buffer.resource_id == buffer_id:
                matching_route = route
                route_id = rid
                break
                
        if matching_route:
            print(f"[MaterialSupplyManager] {matching_route.target_buffer.name} 재고부족 알림 - 자동보충 시작")
            self.env.process(self.auto_replenish(route_id))
        else:
            print(f"[MaterialSupplyManager] 경고: 버퍼 {buffer_id}에 대한 공급 경로를 찾을 수 없음")
            
    def start_monitoring(self, strategy: SupplyStrategy = SupplyStrategy.THRESHOLD_BASED):
        """
        자재 보충 모니터링을 시작합니다
        
        Args:
            strategy: 보충 전략
        """
        if self.is_monitoring:
            print("[MaterialSupplyManager] 이미 모니터링이 실행 중입니다")
            return
            
        # ReportManager의 알림 콜백 등록
        self.report_manager.alert_system.register_alert_callback(self.handle_buffer_alert)
        
        # 모니터링 프로세스 시작
        self.monitoring_process = self.env.process(self._monitoring_loop(strategy))
        self.is_monitoring = True
        
        print(f"[MaterialSupplyManager] 자재 보충 모니터링 시작 (전략: {strategy.value})")
        
    def _monitoring_loop(self, strategy: SupplyStrategy):
        """
        모니터링 루프 (내부 메서드)
        
        Args:
            strategy: 보충 전략
        """
        while True:
            try:
                # ReportManager를 통한 실시간 상태 수집
                status_data = self.report_manager.collect_real_time_status()
                
                # 전략에 따른 처리
                if strategy == SupplyStrategy.THRESHOLD_BASED:
                    # 임계값 기반 모니터링은 알림 시스템에 의해 처리됨
                    pass
                elif strategy == SupplyStrategy.SCHEDULED:
                    # 스케줄 기반 보충 로직
                    yield from self._scheduled_replenishment()
                    
                yield self.env.timeout(5.0)  # 5초마다 모니터링
                
            except Exception as e:
                print(f"[MaterialSupplyManager] 모니터링 오류: {e}")
                yield self.env.timeout(10.0)
                
    def _scheduled_replenishment(self):
        """스케줄 기반 보충 로직"""
        current_time = self.env.now
        
        # 정해진 시간 간격으로 모든 버퍼 체크 및 보충
        for route_id, route in self.supply_routes.items():
            buffer = route.target_buffer
            config = route.material_config
            
            current_level = buffer.get_current_level()
            
            # 경고 임계값 이하인 경우 보충
            if current_level <= config.warning_threshold:
                yield from self.auto_replenish(route_id)
                
    def stop_monitoring(self):
        """모니터링을 중지합니다"""
        if self.monitoring_process:
            self.monitoring_process.interrupt()
            
        self.is_monitoring = False
        print("[MaterialSupplyManager] 자재 보충 모니터링 중지")
        
    def get_supply_statistics(self) -> Dict[str, Any]:
        """
        공급 통계를 반환합니다
        
        Returns:
            Dict[str, Any]: 공급 통계 정보
        """
        return {
            'total_supply_operations': self.supply_count,
            'material_supplies': self.total_supplies.copy(),
            'registered_materials': len(self.material_configs),
            'registered_routes': len(self.supply_routes),
            'is_monitoring': self.is_monitoring,
            'current_time': self.env.now
        }
        
    def force_replenish_all(self):
        """
        모든 등록된 경로에 대해 강제 보충을 실행합니다
        """
        print("[MaterialSupplyManager] 모든 버퍼에 대한 강제 보충 시작")
        
        for route_id in self.supply_routes.keys():
            self.env.process(self.auto_replenish(route_id))
            
    def configure_material_from_dict(self, config_dict: Dict[str, Any]) -> MaterialConfig:
        """
        딕셔너리에서 MaterialConfig 생성
        
        Args:
            config_dict: 자재 설정 딕셔너리
            
        Returns:
            MaterialConfig: 생성된 자재 설정
        """
        return MaterialConfig(
            material_name=config_dict['material_name'],
            material_type=config_dict.get('material_type', config_dict['material_name']),
            default_quantity=config_dict.get('default_quantity', 30),
            min_threshold=config_dict.get('min_threshold', 10),
            warning_threshold=config_dict.get('warning_threshold', 20),
            max_capacity=config_dict.get('max_capacity'),
            supply_time=config_dict.get('supply_time', 2.0)
        )