"""
중앙 집중식 통계 관리 시스템 (Enhanced Version)

SimPy 기반의 표준화된 통계 수집 및 분석을 제공합니다.
모든 시뮬레이션 컴포넌트의 통계를 중앙에서 관리하여 코드 중복을 제거하고
일관성을 보장합니다.

향상된 기능:
- 실시간 임계값 모니터링 및 알림
- 제조업 특화 KPI (OEE, MTBF, MTTR 등)
- 성능 최적화를 위한 메트릭 데이터 관리
- 고급 분석 기능 (예측, 패턴 감지)
- 메트릭 수명 관리 (TTL)
"""

import simpy
from typing import Dict, Any, List, Optional, Callable, Union, Tuple
from dataclasses import dataclass, field
from enum import Enum
import time
import threading
from collections import defaultdict, deque
import warnings

# 필수 패키지들을 조건부로 import
try:
    import numpy as np
    NUMPY_AVAILABLE = True
except ImportError:
    NUMPY_AVAILABLE = False
    # numpy 없이도 기본 기능 동작하도록 fallback
    class NumpyFallback:
        @staticmethod
        def mean(data):
            return sum(data) / len(data) if data else 0
        @staticmethod
        def std(data):
            if not data:
                return 0
            mean_val = sum(data) / len(data)
            variance = sum((x - mean_val) ** 2 for x in data) / len(data)
            return variance ** 0.5
    np = NumpyFallback()

# StatisticsAnalyzer import를 try-catch로 감싸기
try:
    from src.utils.statistics import StatisticsAnalyzer
    ADVANCED_STATS_AVAILABLE = True
except ImportError:
    ADVANCED_STATS_AVAILABLE = False
    # 기본 통계 분석기 fallback
    class BasicStatisticsAnalyzer:
        def calculate_basic_statistics(self, data):
            if not data:
                return {}
            return {
                'mean': np.mean(data),
                'std': np.std(data),
                'min': min(data),
                'max': max(data),
                'count': len(data)
            }
        def analyze_trend(self, data):
            return {'direction': '알 수 없음', 'slope': 0}
        def detect_outliers(self, data, method='iqr'):
            return []
    StatisticsAnalyzer = BasicStatisticsAnalyzer


class MetricType(Enum):
    """메트릭 유형 정의"""
    COUNTER = "counter"          # 누적 카운터 (예: 총 요청 수)
    GAUGE = "gauge"             # 현재 값 (예: 현재 대기열 길이)
    HISTOGRAM = "histogram"     # 값의 분포 (예: 처리 시간)
    RATE = "rate"              # 비율 (예: 성공률)
    UTILIZATION = "utilization" # 가동률
    # 제조업 특화 메트릭 타입 추가
    OEE = "oee"                # Overall Equipment Effectiveness
    MTBF = "mtbf"              # Mean Time Between Failures
    MTTR = "mttr"              # Mean Time To Repair
    CYCLE_TIME = "cycle_time"   # 사이클 타임
    THROUGHPUT = "throughput"   # 처리량


class ManufacturingKPI(Enum):
    """제조업 핵심 성과 지표"""
    OVERALL_EQUIPMENT_EFFECTIVENESS = "oee"
    AVAILABILITY = "availability"
    PERFORMANCE = "performance"
    QUALITY = "quality"
    FIRST_PASS_YIELD = "first_pass_yield"
    DEFECT_RATE = "defect_rate"
    DOWNTIME_PERCENTAGE = "downtime_percentage"
    CAPACITY_UTILIZATION = "capacity_utilization"
    ENERGY_EFFICIENCY = "energy_efficiency"


class AlertSeverity(Enum):
    """알림 심각도"""
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"


@dataclass
class ThresholdAlert:
    """임계값 알림"""
    metric_name: str
    component_id: str
    severity: AlertSeverity
    threshold_value: float
    current_value: float
    message: str
    timestamp: float
    resolved: bool = False


@dataclass
class MetricDefinition:
    """메트릭 정의 (Enhanced)"""
    name: str
    metric_type: MetricType
    description: str
    unit: str = ""
    aggregation_func: Optional[Callable] = None
    # 향상된 기능들
    threshold_config: Optional[Dict[str, float]] = None  # 임계값 설정
    ttl_seconds: Optional[int] = None  # 데이터 수명 (초)
    is_kpi: bool = False  # KPI 여부
    calculation_formula: Optional[str] = None  # 계산 공식


@dataclass
class MetricValue:
    """메트릭 값"""
    timestamp: float
    value: Union[float, int]
    metadata: Dict[str, Any] = field(default_factory=dict)


class ComponentMetrics:
    """개별 컴포넌트의 메트릭 관리 (Enhanced)"""
    
    def __init__(self, component_id: str, component_type: str, max_history_size: int = 10000):
        self.component_id = component_id
        self.component_type = component_type
        self.max_history_size = max_history_size
        self.metrics: Dict[str, deque] = defaultdict(lambda: deque(maxlen=max_history_size))
        self.latest_values: Dict[str, MetricValue] = {}
        self.threshold_alerts: List[ThresholdAlert] = []
        
    def add_metric(self, metric_name: str, value: Union[float, int], 
                   timestamp: float, metadata: Optional[Dict[str, Any]] = None,
                   metric_def: Optional[MetricDefinition] = None):
        """메트릭 값 추가 (향상된 버전)"""
        metric_value = MetricValue(
            timestamp=timestamp,
            value=value,
            metadata=metadata or {}
        )
        
        # 메트릭 히스토리 추가 (deque 사용으로 메모리 효율성 향상)
        self.metrics[metric_name].append(metric_value)
        self.latest_values[metric_name] = metric_value
        
        # TTL 기반 데이터 정리
        if metric_def and metric_def.ttl_seconds:
            self._cleanup_expired_data(metric_name, timestamp - metric_def.ttl_seconds)
        
        # 임계값 체크
        if metric_def and metric_def.threshold_config:
            self._check_thresholds(metric_name, value, metric_def.threshold_config)
    
    def _cleanup_expired_data(self, metric_name: str, cutoff_time: float):
        """만료된 데이터 정리"""
        metric_deque = self.metrics[metric_name]
        while metric_deque and metric_deque[0].timestamp < cutoff_time:
            metric_deque.popleft()
    
    def _check_thresholds(self, metric_name: str, value: float, threshold_config: Dict[str, float]):
        """임계값 체크 및 알림 생성"""
        for severity_str, threshold_value in threshold_config.items():
            try:
                severity = AlertSeverity(severity_str.lower())
                if value > threshold_value:
                    alert = ThresholdAlert(
                        metric_name=metric_name,
                        component_id=self.component_id,
                        severity=severity,
                        threshold_value=threshold_value,
                        current_value=value,
                        message=f"{metric_name} 값 {value}이(가) {severity_str} 임계값 {threshold_value}을(를) 초과했습니다.",
                        timestamp=time.time()
                    )
                    self.threshold_alerts.append(alert)
            except ValueError:
                continue  # 유효하지 않은 심각도 무시
        
    def get_latest_value(self, metric_name: str) -> Optional[MetricValue]:
        """최신 메트릭 값 반환"""
        return self.latest_values.get(metric_name)
        
    def get_metric_history(self, metric_name: str, 
                          start_time: Optional[float] = None,
                          end_time: Optional[float] = None) -> List[MetricValue]:
        """메트릭 히스토리 반환"""
        history = list(self.metrics.get(metric_name, []))
        
        if start_time is not None or end_time is not None:
            filtered_history = []
            for metric_value in history:
                if start_time is not None and metric_value.timestamp < start_time:
                    continue
                if end_time is not None and metric_value.timestamp > end_time:
                    continue
                filtered_history.append(metric_value)
            return filtered_history
            
        return history
    
    def get_unresolved_alerts(self) -> List[ThresholdAlert]:
        """해결되지 않은 알림 반환"""
        return [alert for alert in self.threshold_alerts if not alert.resolved]
    
    def resolve_alert(self, alert_index: int):
        """알림 해결 처리"""
        if 0 <= alert_index < len(self.threshold_alerts):
            self.threshold_alerts[alert_index].resolved = True


class CentralizedStatisticsManager:
    """중앙 집중식 통계 관리자 (Enhanced)
    
    SimPy Environment와 연동하여 모든 시뮬레이션 컴포넌트의 
    통계를 중앙에서 수집하고 관리합니다.
    
    향상된 기능:
    - 실시간 알림 시스템
    - 제조업 특화 KPI 계산
    - 메트릭 수명 관리
    - 성능 최적화
    """
    
    def __init__(self, env: simpy.Environment, max_components: int = 1000, 
                 enable_alerts: bool = True):
        """
        초기화
        
        Args:
            env: SimPy Environment
            max_components: 최대 컴포넌트 수
            enable_alerts: 알림 시스템 활성화
        """
        self.env = env
        self.max_components = max_components
        self.enable_alerts = enable_alerts
        self.components: Dict[str, ComponentMetrics] = {}
        self.metric_definitions: Dict[str, MetricDefinition] = {}
        self.statistics_analyzer = StatisticsAnalyzer()
        self.alert_callbacks: List[Callable[[ThresholdAlert], None]] = []
        
        # 스레드 안전성을 위한 락
        self._lock = threading.RLock()
        
        # 표준 메트릭 정의 등록
        self._register_standard_metrics()
        self._register_manufacturing_kpis()
        
    def _register_standard_metrics(self):
        """표준 메트릭 정의 등록 (향상된 버전)"""
        standard_metrics = [
            MetricDefinition("total_requests", MetricType.COUNTER, "총 요청 수"),
            MetricDefinition("successful_operations", MetricType.COUNTER, "성공한 작업 수"),
            MetricDefinition("failed_operations", MetricType.COUNTER, "실패한 작업 수"),
            MetricDefinition("success_rate", MetricType.RATE, "성공률", "%", is_kpi=True,
                           threshold_config={"high": 95.0, "medium": 90.0, "low": 85.0}),
            MetricDefinition("queue_length", MetricType.GAUGE, "대기열 길이",
                           threshold_config={"critical": 100, "high": 50, "medium": 20}),
            MetricDefinition("utilization", MetricType.UTILIZATION, "자원 가동률", "%", is_kpi=True,
                           threshold_config={"low": 30.0, "medium": 50.0, "high": 85.0}),
            MetricDefinition("processing_time", MetricType.HISTOGRAM, "처리 시간", "time_unit",
                           ttl_seconds=3600),  # 1시간 TTL
            MetricDefinition("waiting_time", MetricType.HISTOGRAM, "대기 시간", "time_unit",
                           threshold_config={"high": 300, "critical": 600}),
            MetricDefinition("throughput", MetricType.THROUGHPUT, "처리량", "items/time_unit", is_kpi=True),
            MetricDefinition("quality_score", MetricType.HISTOGRAM, "품질 점수", "score",
                           threshold_config={"low": 70.0, "medium": 80.0, "high": 90.0}),
        ]
        
        for metric_def in standard_metrics:
            self.metric_definitions[metric_def.name] = metric_def
    
    def _register_manufacturing_kpis(self):
        """제조업 특화 KPI 등록"""
        manufacturing_kpis = [
            MetricDefinition("oee", MetricType.OEE, "Overall Equipment Effectiveness", "%", 
                           is_kpi=True, calculation_formula="availability * performance * quality",
                           threshold_config={"low": 50.0, "medium": 70.0, "high": 85.0}),
            MetricDefinition("availability", MetricType.RATE, "설비 가용성", "%", is_kpi=True,
                           threshold_config={"low": 80.0, "medium": 90.0, "high": 95.0}),
            MetricDefinition("performance_efficiency", MetricType.RATE, "성능 효율성", "%", is_kpi=True),
            MetricDefinition("quality_rate", MetricType.RATE, "품질률", "%", is_kpi=True),
            MetricDefinition("mtbf", MetricType.MTBF, "평균 고장 간격", "hours", is_kpi=True),
            MetricDefinition("mttr", MetricType.MTTR, "평균 수리 시간", "hours", is_kpi=True,
                           threshold_config={"critical": 8, "high": 4, "medium": 2}),
            MetricDefinition("cycle_time", MetricType.CYCLE_TIME, "사이클 타임", "time_unit", is_kpi=True),
            MetricDefinition("first_pass_yield", MetricType.RATE, "일발 양품률", "%", is_kpi=True,
                           threshold_config={"low": 95.0, "medium": 98.0, "high": 99.5}),
            MetricDefinition("defect_rate", MetricType.RATE, "불량률", "%",
                           threshold_config={"medium": 2.0, "high": 5.0, "critical": 10.0}),
            MetricDefinition("energy_efficiency", MetricType.RATE, "에너지 효율성", "%", is_kpi=True),
        ]
        
        for kpi_def in manufacturing_kpis:
            self.metric_definitions[kpi_def.name] = kpi_def
    
    def register_component(self, component_id: str, component_type: str, 
                          max_history_size: int = 10000) -> ComponentMetrics:
        """
        컴포넌트 등록 (향상된 버전)
        
        Args:
            component_id: 컴포넌트 고유 ID
            component_type: 컴포넌트 유형
            max_history_size: 최대 히스토리 크기
            
        Returns:
            ComponentMetrics: 컴포넌트 메트릭 객체
        """
        with self._lock:
            if component_id in self.components:
                return self.components[component_id]
            
            if len(self.components) >= self.max_components:
                warnings.warn(f"최대 컴포넌트 수 {self.max_components}에 도달했습니다.")
                return None
                
            component_metrics = ComponentMetrics(component_id, component_type, max_history_size)
            self.components[component_id] = component_metrics
            return component_metrics
    
    def collect_metric(self, component_id: str, metric_name: str, 
                      value: Union[float, int], metadata: Optional[Dict[str, Any]] = None):
        """
        메트릭 수집 (향상된 버전)
        
        Args:
            component_id: 컴포넌트 ID
            metric_name: 메트릭 이름
            value: 메트릭 값
            metadata: 추가 메타데이터
        """
        with self._lock:
            if component_id not in self.components:
                # 자동으로 컴포넌트 등록
                self.register_component(component_id, "unknown")
                
            component = self.components[component_id]
            metric_def = self.metric_definitions.get(metric_name)
            
            component.add_metric(metric_name, value, self.env.now, metadata, metric_def)
            
            # 알림 시스템이 활성화되어 있고 새로운 알림이 있다면 콜백 실행
            if self.enable_alerts and component.get_unresolved_alerts():
                for alert in component.get_unresolved_alerts():
                    if not alert.resolved:
                        self._trigger_alert_callbacks(alert)
    
    def _trigger_alert_callbacks(self, alert: ThresholdAlert):
        """알림 콜백 실행"""
        for callback in self.alert_callbacks:
            try:
                callback(alert)
            except Exception as e:
                print(f"알림 콜백 실행 중 오류: {e}")
    
    def register_alert_callback(self, callback: Callable[[ThresholdAlert], None]):
        """알림 콜백 등록"""
        self.alert_callbacks.append(callback)
    
    def calculate_manufacturing_kpi(self, component_id: str, kpi_name: str) -> Optional[float]:
        """제조업 KPI 계산"""
        if component_id not in self.components:
            return None
            
        component = self.components[component_id]
        
        if kpi_name == "oee":
            # OEE = 가용성 × 성능 × 품질
            availability = component.get_latest_value("availability")
            performance = component.get_latest_value("performance_efficiency")
            quality = component.get_latest_value("quality_rate")
            
            if availability and performance and quality:
                oee = (availability.value / 100) * (performance.value / 100) * (quality.value / 100) * 100
                # OEE 값을 메트릭으로 저장
                self.collect_metric(component_id, "oee", oee)
                return oee
                
        elif kpi_name == "first_pass_yield":
            # 일발 양품률 = (일발 양품 수 / 총 생산 수) × 100
            good_parts = component.get_latest_value("good_parts_first_pass")
            total_parts = component.get_latest_value("total_parts_produced")
            
            if good_parts and total_parts and total_parts.value > 0:
                fpy = (good_parts.value / total_parts.value) * 100
                self.collect_metric(component_id, "first_pass_yield", fpy)
                return fpy
                
        elif kpi_name == "defect_rate":
            # 불량률 = (불량품 수 / 총 생산 수) × 100
            defects = component.get_latest_value("defective_parts")
            total_parts = component.get_latest_value("total_parts_produced")
            
            if defects and total_parts and total_parts.value > 0:
                defect_rate = (defects.value / total_parts.value) * 100
                self.collect_metric(component_id, "defect_rate", defect_rate)
                return defect_rate
        
        return None
    
    def get_component_statistics(self, component_id: str, include_kpis: bool = True) -> Dict[str, Any]:
        """
        컴포넌트별 통계 반환 (향상된 버전)
        
        Args:
            component_id: 컴포넌트 ID
            include_kpis: KPI 포함 여부
            
        Returns:
            Dict[str, Any]: 통계 정보
        """
        if component_id not in self.components:
            return {}
            
        component = self.components[component_id]
        stats = {
            'component_id': component_id,
            'component_type': component.component_type,
            'simulation_time': self.env.now,
            'metrics': {},
            'alerts': {
                'active_alerts': len(component.get_unresolved_alerts()),
                'alert_details': [
                    {
                        'metric': alert.metric_name,
                        'severity': alert.severity.value,
                        'message': alert.message,
                        'timestamp': alert.timestamp
                    } for alert in component.get_unresolved_alerts()
                ]
            }
        }
        
        # 각 메트릭별 통계 계산
        for metric_name, values in component.metrics.items():
            if not values:
                continue
                
            metric_values = [v.value for v in values]
            latest_value = component.get_latest_value(metric_name)
            
            metric_stats = {
                'latest_value': latest_value.value if latest_value else None,
                'count': len(metric_values),
            }
            
            # 메트릭 유형에 따른 추가 통계
            metric_def = self.metric_definitions.get(metric_name)
            if metric_def:
                if metric_def.metric_type in [MetricType.HISTOGRAM, MetricType.GAUGE]:
                    basic_stats = self.statistics_analyzer.calculate_basic_statistics(metric_values)
                    metric_stats.update(basic_stats)
                elif metric_def.metric_type == MetricType.RATE:
                    if metric_name == "success_rate":
                        # 성공률 계산
                        success_count = component.get_latest_value("successful_operations")
                        total_count = component.get_latest_value("total_requests")
                        if success_count and total_count and total_count.value > 0:
                            metric_stats['calculated_rate'] = (success_count.value / total_count.value) * 100
                
                # KPI 여부 표시
                metric_stats['is_kpi'] = metric_def.is_kpi
            
            stats['metrics'][metric_name] = metric_stats
        
        # 제조업 KPI 계산 및 추가
        if include_kpis:
            kpi_stats = {}
            for kpi_name in ['oee', 'first_pass_yield', 'defect_rate']:
                kpi_value = self.calculate_manufacturing_kpi(component_id, kpi_name)
                if kpi_value is not None:
                    kpi_stats[kpi_name] = kpi_value
            
            if kpi_stats:
                stats['calculated_kpis'] = kpi_stats
            
        return stats
    
    def get_global_statistics(self, include_manufacturing_summary: bool = True) -> Dict[str, Any]:
        """
        전체 시뮬레이션 통계 반환 (향상된 버전)
        
        Args:
            include_manufacturing_summary: 제조업 요약 포함 여부
            
        Returns:
            Dict[str, Any]: 전체 통계 정보
        """
        global_stats = {
            'simulation_time': self.env.now,
            'total_components': len(self.components),
            'component_types': {},
            'aggregated_metrics': {},
            'system_health': {
                'total_alerts': 0,
                'critical_alerts': 0,
                'components_with_alerts': 0
            }
        }
        
        # 컴포넌트 유형별 집계 및 알림 통계
        component_type_counts = defaultdict(int)
        aggregated_metrics = defaultdict(list)
        alert_summary = {'total': 0, 'critical': 0, 'components_with_alerts': set()}
        
        for component in self.components.values():
            component_type_counts[component.component_type] += 1
            
            # 알림 통계
            unresolved_alerts = component.get_unresolved_alerts()
            if unresolved_alerts:
                alert_summary['components_with_alerts'].add(component.component_id)
                alert_summary['total'] += len(unresolved_alerts)
                alert_summary['critical'] += sum(1 for alert in unresolved_alerts 
                                                if alert.severity == AlertSeverity.CRITICAL)
            
            # 메트릭 집계
            for metric_name, values in component.metrics.items():
                if values:
                    latest_value = values[-1].value
                    aggregated_metrics[metric_name].append(latest_value)
        
        global_stats['component_types'] = dict(component_type_counts)
        global_stats['system_health'] = {
            'total_alerts': alert_summary['total'],
            'critical_alerts': alert_summary['critical'],
            'components_with_alerts': len(alert_summary['components_with_alerts'])
        }
        
        # 집계된 메트릭 통계
        for metric_name, values in aggregated_metrics.items():
            if values:
                metric_def = self.metric_definitions.get(metric_name)
                if metric_def and metric_def.metric_type in [MetricType.HISTOGRAM, MetricType.GAUGE]:
                    global_stats['aggregated_metrics'][metric_name] = (
                        self.statistics_analyzer.calculate_basic_statistics(values)
                    )
                else:
                    avg_value = np.mean(values) if NUMPY_AVAILABLE else sum(values) / len(values)
                    global_stats['aggregated_metrics'][metric_name] = {
                        'total': sum(values),
                        'average': avg_value,
                        'count': len(values)
                    }
        
        # 제조업 요약 추가
        if include_manufacturing_summary:
            manufacturing_summary = self._calculate_manufacturing_summary()
            global_stats['manufacturing_summary'] = manufacturing_summary
        
        return global_stats
    
    def _calculate_manufacturing_summary(self) -> Dict[str, Any]:
        """제조업 전체 요약 계산"""
        summary = {
            'overall_oee': 0.0,
            'average_availability': 0.0,
            'average_quality_rate': 0.0,
            'total_production': 0,
            'total_defects': 0,
            'global_defect_rate': 0.0
        }
        
        oee_values = []
        availability_values = []
        quality_values = []
        total_production = 0
        total_defects = 0
        
        for component in self.components.values():
            # OEE 수집
            oee = component.get_latest_value("oee")
            if oee:
                oee_values.append(oee.value)
            
            # 가용성 수집
            availability = component.get_latest_value("availability")
            if availability:
                availability_values.append(availability.value)
            
            # 품질률 수집
            quality_rate = component.get_latest_value("quality_rate")
            if quality_rate:
                quality_values.append(quality_rate.value)
            
            # 생산량 및 불량 수집
            production = component.get_latest_value("total_parts_produced")
            defects = component.get_latest_value("defective_parts")
            
            if production:
                total_production += production.value
            if defects:
                total_defects += defects.value
        
        # 평균값 계산
        if oee_values:
            summary['overall_oee'] = np.mean(oee_values) if NUMPY_AVAILABLE else sum(oee_values) / len(oee_values)
        if availability_values:
            summary['average_availability'] = np.mean(availability_values) if NUMPY_AVAILABLE else sum(availability_values) / len(availability_values)
        if quality_values:
            summary['average_quality_rate'] = np.mean(quality_values) if NUMPY_AVAILABLE else sum(quality_values) / len(quality_values)
        
        summary['total_production'] = total_production
        summary['total_defects'] = total_defects
        if total_production > 0:
            summary['global_defect_rate'] = (total_defects / total_production) * 100
        
        return summary
    
    def get_real_time_dashboard_data(self) -> Dict[str, Any]:
        """실시간 대시보드용 데이터 반환"""
        dashboard_data = {
            'timestamp': time.time(),
            'simulation_time': self.env.now,
            'system_status': 'healthy',
            'key_metrics': {},
            'alerts': [],
            'performance_indicators': {}
        }
        
        # 시스템 상태 판단
        total_critical_alerts = 0
        all_alerts = []
        
        for component in self.components.values():
            unresolved_alerts = component.get_unresolved_alerts()
            all_alerts.extend(unresolved_alerts)
            total_critical_alerts += sum(1 for alert in unresolved_alerts 
                                       if alert.severity == AlertSeverity.CRITICAL)
        
        if total_critical_alerts > 0:
            dashboard_data['system_status'] = 'critical'
        elif len(all_alerts) > 5:
            dashboard_data['system_status'] = 'warning'
        
        # 주요 메트릭 수집
        key_metric_names = ['oee', 'availability', 'quality_rate', 'defect_rate', 'throughput']
        for metric_name in key_metric_names:
            values = []
            for component in self.components.values():
                latest = component.get_latest_value(metric_name)
                if latest:
                    values.append(latest.value)
            
            if values:
                dashboard_data['key_metrics'][metric_name] = {
                    'current_average': np.mean(values) if NUMPY_AVAILABLE else sum(values) / len(values),
                    'component_count': len(values)
                }
        
        # 최근 알림 (최대 10개)
        sorted_alerts = sorted(all_alerts, key=lambda x: x.timestamp, reverse=True)[:10]
        dashboard_data['alerts'] = [
            {
                'component': alert.component_id,
                'metric': alert.metric_name,
                'severity': alert.severity.value,
                'message': alert.message,
                'timestamp': alert.timestamp
            } for alert in sorted_alerts
        ]
        
        return dashboard_data
    
    def get_performance_trends(self, component_id: str, 
                             metric_name: str, hours: int = 24) -> Dict[str, Any]:
        """성능 트렌드 분석 (지정된 시간 범위)"""
        if component_id not in self.components:
            return {}
        
        component = self.components[component_id]
        cutoff_time = self.env.now - (hours * 3600)  # 시간을 초로 변환
        
        history = component.get_metric_history(metric_name, start_time=cutoff_time)
        if len(history) < 2:
            return {'error': '충분한 데이터가 없습니다'}
        
        values = [h.value for h in history]
        timestamps = [h.timestamp for h in history]
        
        trend_analysis = self.statistics_analyzer.analyze_trend(values)
        basic_stats = self.statistics_analyzer.calculate_basic_statistics(values)
        
        return {
            'metric_name': metric_name,
            'component_id': component_id,
            'time_range_hours': hours,
            'data_points': len(history),
            'trend': trend_analysis,
            'statistics': basic_stats,
            'latest_value': values[-1] if values else None,
            'time_series': [
                {'timestamp': ts, 'value': val} 
                for ts, val in zip(timestamps, values)
            ][-50:]  # 최근 50개 포인트만
        }
    
    def cleanup_old_data(self, max_age_hours: int = 48):
        """오래된 데이터 정리"""
        cutoff_time = self.env.now - (max_age_hours * 3600)
        
        with self._lock:
            for component in self.components.values():
                for metric_name in list(component.metrics.keys()):
                    component._cleanup_expired_data(metric_name, cutoff_time)
                    
                # 오래된 알림도 정리
                component.threshold_alerts = [
                    alert for alert in component.threshold_alerts
                    if alert.timestamp > cutoff_time
                ]
    
    def get_component_performance_analysis(self, component_id: str) -> Dict[str, Any]:
        """
        컴포넌트 성능 분석
        
        Args:
            component_id: 컴포넌트 ID
            
        Returns:
            Dict[str, Any]: 성능 분석 결과
        """
        if component_id not in self.components:
            return {}
            
        component = self.components[component_id]
        analysis = {
            'component_id': component_id,
            'performance_summary': {},
            'trend_analysis': {},
            'outlier_detection': {}
        }
        
        # 주요 성능 메트릭 분석
        performance_metrics = ['processing_time', 'waiting_time', 'utilization', 'throughput']
        
        for metric_name in performance_metrics:
            if metric_name not in component.metrics:
                continue
                
            values = [v.value for v in component.metrics[metric_name]]
            if len(values) < 2:
                continue
                
            # 기본 통계
            basic_stats = self.statistics_analyzer.calculate_basic_statistics(values)
            analysis['performance_summary'][metric_name] = basic_stats
            
            # 트렌드 분석
            trend = self.statistics_analyzer.analyze_trend(values)
            analysis['trend_analysis'][metric_name] = trend
            
            # 이상치 감지
            outliers = self.statistics_analyzer.detect_outliers(values)
            analysis['outlier_detection'][metric_name] = {
                'outlier_count': len(outliers),
                'outlier_percentage': (len(outliers) / len(values)) * 100,
                'outlier_values': outliers.tolist() if len(outliers) > 0 else []
            }
        
        return analysis
        """
        컴포넌트 성능 분석
        
        Args:
            component_id: 컴포넌트 ID
            
        Returns:
            Dict[str, Any]: 성능 분석 결과
        """
        if component_id not in self.components:
            return {}
            
        component = self.components[component_id]
        analysis = {
            'component_id': component_id,
            'performance_summary': {},
            'trend_analysis': {},
            'outlier_detection': {}
        }
        
        # 주요 성능 메트릭 분석
        performance_metrics = ['processing_time', 'waiting_time', 'utilization', 'throughput']
        
        for metric_name in performance_metrics:
            if metric_name not in component.metrics:
                continue
                
            values = [v.value for v in component.metrics[metric_name]]
            if len(values) < 2:
                continue
                
            # 기본 통계
            basic_stats = self.statistics_analyzer.calculate_basic_statistics(values)
            analysis['performance_summary'][metric_name] = basic_stats
            
            # 트렌드 분석
            trend = self.statistics_analyzer.analyze_trend(values)
            analysis['trend_analysis'][metric_name] = trend
            
            # 이상치 감지
            outliers = self.statistics_analyzer.detect_outliers(values)
            analysis['outlier_detection'][metric_name] = {
                'outlier_count': len(outliers),
                'outlier_percentage': (len(outliers) / len(values)) * 100,
                'outlier_values': outliers.tolist() if len(outliers) > 0 else []
            }
        
        return analysis
    
    def export_statistics(self, component_ids: Optional[List[str]] = None) -> Dict[str, Any]:
        """
        통계 데이터 내보내기
        
        Args:
            component_ids: 내보낼 컴포넌트 ID 목록 (None이면 전체)
            
        Returns:
            Dict[str, Any]: 내보내기 데이터
        """
        if component_ids is None:
            component_ids = list(self.components.keys())
            
        export_data = {
            'metadata': {
                'export_time': time.time(),
                'simulation_time': self.env.now,
                'component_count': len(component_ids)
            },
            'global_statistics': self.get_global_statistics(),
            'component_statistics': {},
            'performance_analysis': {}
        }
        
        for component_id in component_ids:
            if component_id in self.components:
                export_data['component_statistics'][component_id] = (
                    self.get_component_statistics(component_id)
                )
                export_data['performance_analysis'][component_id] = (
                    self.get_component_performance_analysis(component_id)
                )
        
        return export_data
    
    def clear_statistics(self, component_id: Optional[str] = None):
        """
        통계 데이터 초기화
        
        Args:
            component_id: 초기화할 컴포넌트 ID (None이면 전체)
        """
        if component_id is None:
            self.components.clear()
        elif component_id in self.components:
            del self.components[component_id]


class StatisticsInterface:
    """통계 수집을 위한 표준 인터페이스 (Enhanced)
    
    기존 클래스들이 중앙 통계 관리자를 쉽게 사용할 수 있도록 하는 인터페이스입니다.
    향상된 기능으로 제조업 특화 메트릭과 실시간 모니터링을 지원합니다.
    """
    
    def __init__(self, component_id: str, component_type: str, 
                 stats_manager: CentralizedStatisticsManager):
        """
        초기화
        
        Args:
            component_id: 컴포넌트 ID
            component_type: 컴포넌트 유형
            stats_manager: 중앙 통계 관리자
        """
        self.component_id = component_id
        self.component_type = component_type
        self.stats_manager = stats_manager
        
        # 컴포넌트 등록
        self.stats_manager.register_component(component_id, component_type)
    
    def record_counter(self, metric_name: str, increment: int = 1):
        """카운터 메트릭 기록 (Enhanced)"""
        current = self.stats_manager.components[self.component_id].get_latest_value(metric_name)
        new_value = (current.value if current else 0) + increment
        self.stats_manager.collect_metric(self.component_id, metric_name, new_value)
    
    def record_gauge(self, metric_name: str, value: Union[float, int]):
        """게이지 메트릭 기록"""
        self.stats_manager.collect_metric(self.component_id, metric_name, value)
    
    def record_histogram(self, metric_name: str, value: Union[float, int]):
        """히스토그램 메트릭 기록"""
        self.stats_manager.collect_metric(self.component_id, metric_name, value)
    
    def record_manufacturing_event(self, event_type: str, **kwargs):
        """제조업 특화 이벤트 기록"""
        if event_type == "production_completed":
            self.record_counter("total_parts_produced")
            if kwargs.get('quality', 'good') == 'good':
                self.record_counter("good_parts_first_pass")
            else:
                self.record_counter("defective_parts")
                
        elif event_type == "machine_failure":
            self.record_counter("failure_events")
            failure_time = kwargs.get('duration', 0)
            self.record_histogram("failure_duration", failure_time)
            
        elif event_type == "maintenance_completed":
            self.record_counter("maintenance_events")
            maintenance_time = kwargs.get('duration', 0)
            self.record_histogram("maintenance_duration", maintenance_time)
            
        elif event_type == "quality_check":
            quality_score = kwargs.get('score', 0)
            self.record_histogram("quality_score", quality_score)
    
    def calculate_oee(self, availability: float, performance: float, quality: float):
        """OEE 계산 및 기록"""
        oee = (availability / 100) * (performance / 100) * (quality / 100) * 100
        self.record_gauge("oee", oee)
        return oee
    
    def calculate_availability(self, planned_time: float, downtime: float):
        """가용성 계산 및 기록"""
        if planned_time > 0:
            availability = ((planned_time - downtime) / planned_time) * 100
            self.record_gauge("availability", availability)
            return availability
        return 0.0
    
    def calculate_performance_efficiency(self, ideal_cycle_time: float, 
                                       actual_cycle_time: float, units_produced: int):
        """성능 효율성 계산 및 기록"""
        if actual_cycle_time > 0:
            ideal_production_time = ideal_cycle_time * units_produced
            performance = (ideal_production_time / actual_cycle_time) * 100
            self.record_gauge("performance_efficiency", performance)
            return performance
        return 0.0
    
    def calculate_rate(self, numerator_metric: str, denominator_metric: str) -> float:
        """비율 계산"""
        component = self.stats_manager.components[self.component_id]
        numerator = component.get_latest_value(numerator_metric)
        denominator = component.get_latest_value(denominator_metric)
        
        if numerator and denominator and denominator.value > 0:
            return (numerator.value / denominator.value) * 100
        return 0.0
    
    def get_statistics(self) -> Dict[str, Any]:
        """컴포넌트 통계 반환 (하위 호환성)"""
        return self.stats_manager.get_component_statistics(self.component_id)
    
    def get_kpi_dashboard(self) -> Dict[str, Any]:
        """KPI 대시보드 데이터 반환"""
        stats = self.get_statistics()
        component = self.stats_manager.components[self.component_id]
        
        kpi_dashboard = {
            'component_id': self.component_id,
            'timestamp': time.time(),
            'key_metrics': {},
            'alerts': component.get_unresolved_alerts(),
            'performance_status': 'normal'
        }
        
        # 주요 KPI 추출
        kpi_metrics = ['oee', 'availability', 'quality_rate', 'utilization', 'throughput']
        for metric_name in kpi_metrics:
            if metric_name in stats.get('metrics', {}):
                kpi_dashboard['key_metrics'][metric_name] = stats['metrics'][metric_name]
        
        # 성능 상태 결정
        unresolved_alerts = component.get_unresolved_alerts()
        if any(alert.severity == AlertSeverity.CRITICAL for alert in unresolved_alerts):
            kpi_dashboard['performance_status'] = 'critical'
        elif any(alert.severity == AlertSeverity.HIGH for alert in unresolved_alerts):
            kpi_dashboard['performance_status'] = 'warning'
        elif len(unresolved_alerts) > 3:
            kpi_dashboard['performance_status'] = 'caution'
        
        return kpi_dashboard
