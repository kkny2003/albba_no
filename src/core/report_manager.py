"""
제조 시뮬레이션 프레임워크용 종합 리포트 관리 시스템

모든 Resource와 Process 상태를 실시간으로 추적하고 관리할 수 있는 
종합적인 Report 시스템을 제공합니다.

주요 기능:
- 실시간 리소스 및 프로세스 상태 추적
- 성능 지표 계산 및 모니터링  
- 알림 시스템 및 임계값 모니터링
- 데이터 내보내기 기능
- 대시보드 데이터 제공
"""

import simpy
import time
import json
import csv
import pandas as pd
from typing import Dict, List, Any, Optional, Union, Callable
from dataclasses import dataclass, field
from enum import Enum
import warnings
from collections import defaultdict, deque

from src.core.centralized_statistics import (
    CentralizedStatisticsManager, StatisticsInterface, 
    AlertSeverity, ThresholdAlert, MetricType
)
from src.utils.visualization import VisualizationManager


class ReportType(Enum):
    """리포트 타입 정의"""
    REAL_TIME_DASHBOARD = "real_time_dashboard"
    COMPREHENSIVE_REPORT = "comprehensive_report"
    RESOURCE_STATUS = "resource_status"
    PROCESS_PERFORMANCE = "process_performance"
    ALERT_SUMMARY = "alert_summary"
    TREND_ANALYSIS = "trend_analysis"


class ExportFormat(Enum):
    """데이터 내보내기 형식"""
    JSON = "json"
    CSV = "csv"
    EXCEL = "xlsx"
    HTML = "html"


@dataclass
class PerformanceThreshold:
    """성능 임계값 정의"""
    metric_name: str
    warning_level: float
    critical_level: float
    unit: str = ""
    higher_is_better: bool = True  # True: 높을수록 좋음, False: 낮을수록 좋음


@dataclass
class ResourceStateSnapshot:
    """리소스 상태 스냅샷"""
    resource_id: str
    resource_type: str
    timestamp: float
    status: Dict[str, Any]
    metrics: Dict[str, float]
    alerts: List[Dict[str, Any]]


@dataclass
class ProcessPerformanceSnapshot:
    """프로세스 성능 스냅샷"""
    process_id: str
    process_type: str
    timestamp: float
    performance_metrics: Dict[str, float]
    current_status: str
    throughput: float
    cycle_time: float
    queue_length: int


class ResourceStateTracker:
    """리소스별 실시간 상태 추적"""
    
    def __init__(self, env: simpy.Environment, max_history: int = 1000):
        self.env = env
        self.max_history = max_history
        self.resource_snapshots: Dict[str, deque] = defaultdict(
            lambda: deque(maxlen=max_history)
        )
        self.resource_registry: Dict[str, Any] = {}
        
    def register_resource(self, resource_id: str, resource_obj: Any):
        """리소스 등록"""
        self.resource_registry[resource_id] = resource_obj
        print(f"[ReportManager] 리소스 등록: {resource_id}")
        
    def track_resource_state(self, resource_id: str) -> ResourceStateSnapshot:
        """특정 리소스의 현재 상태 추적"""
        if resource_id not in self.resource_registry:
            return None
            
        resource_obj = self.resource_registry[resource_id]
        
        # 리소스 타입에 따른 상태 수집
        status = self._collect_resource_status(resource_obj)
        metrics = self._collect_resource_metrics(resource_obj)
        alerts = self._collect_resource_alerts(resource_obj)
        
        snapshot = ResourceStateSnapshot(
            resource_id=resource_id,
            resource_type=type(resource_obj).__name__,
            timestamp=self.env.now,
            status=status,
            metrics=metrics,
            alerts=alerts
        )
        
        # 히스토리에 추가
        self.resource_snapshots[resource_id].append(snapshot)
        
        return snapshot
        
    def _collect_resource_status(self, resource_obj: Any) -> Dict[str, Any]:
        """리소스 상태 정보 수집"""
        status = {}
        
        # Machine 리소스
        if hasattr(resource_obj, 'get_status'):
            status = resource_obj.get_status()
        elif hasattr(resource_obj, 'simpy_resource'):
            # SimPy 리소스 기본 정보
            status = {
                'capacity': getattr(resource_obj.simpy_resource, 'capacity', 1),
                'current_users': len(getattr(resource_obj.simpy_resource, 'users', [])),
                'queue_length': len(getattr(resource_obj.simpy_resource, 'queue', [])),
                'is_available': len(getattr(resource_obj.simpy_resource, 'users', [])) < getattr(resource_obj.simpy_resource, 'capacity', 1)
            }
        else:
            # 기본 리소스 정보
            status = {
                'resource_id': getattr(resource_obj, 'resource_id', 'unknown'),
                'name': getattr(resource_obj, 'name', 'unknown'),
                'is_available': getattr(resource_obj, 'is_available', True)
            }
            
        return status
        
    def _collect_resource_metrics(self, resource_obj: Any) -> Dict[str, float]:
        """리소스 메트릭 수집"""
        metrics = {}
        
        # Machine 특화 메트릭
        if hasattr(resource_obj, 'get_utilization'):
            metrics['utilization'] = resource_obj.get_utilization()
        if hasattr(resource_obj, 'get_availability'):
            metrics['availability'] = resource_obj.get_availability()
        if hasattr(resource_obj, 'get_failure_rate'):
            metrics['failure_rate'] = resource_obj.get_failure_rate()
        if hasattr(resource_obj, 'total_processed'):
            metrics['total_processed'] = resource_obj.total_processed
        if hasattr(resource_obj, 'total_failures'):
            metrics['total_failures'] = resource_obj.total_failures
            
        # Worker 특화 메트릭
        if hasattr(resource_obj, 'total_tasks_completed'):
            metrics['tasks_completed'] = resource_obj.total_tasks_completed
        if hasattr(resource_obj, 'get_efficiency'):
            metrics['efficiency'] = resource_obj.get_efficiency()
            
        # Transport 특화 메트릭
        if hasattr(resource_obj, 'total_transports'):
            metrics['total_transports'] = resource_obj.total_transports
        if hasattr(resource_obj, 'get_average_transport_time'):
            metrics['avg_transport_time'] = resource_obj.get_average_transport_time()
            
        return metrics
        
    def _collect_resource_alerts(self, resource_obj: Any) -> List[Dict[str, Any]]:
        """리소스 관련 알림 수집"""
        alerts = []
        
        # 기계 고장 알림
        if hasattr(resource_obj, 'is_broken') and resource_obj.is_broken:
            alerts.append({
                'type': 'failure',
                'severity': 'critical',
                'message': f'기계 {getattr(resource_obj, "resource_id", "unknown")}이 고장 상태입니다',
                'timestamp': self.env.now
            })
            
        # 가동률 임계값 알림
        if hasattr(resource_obj, 'get_utilization'):
            utilization = resource_obj.get_utilization()
            if utilization < 0.3:  # 30% 미만
                alerts.append({
                    'type': 'low_utilization',
                    'severity': 'warning',
                    'message': f'가동률이 낮습니다: {utilization:.1%}',
                    'timestamp': self.env.now
                })
            elif utilization > 0.95:  # 95% 초과
                alerts.append({
                    'type': 'high_utilization',
                    'severity': 'warning',
                    'message': f'가동률이 매우 높습니다: {utilization:.1%}',
                    'timestamp': self.env.now
                })
                
        return alerts
        
    def get_all_resource_states(self) -> Dict[str, ResourceStateSnapshot]:
        """모든 등록된 리소스의 현재 상태 반환"""
        states = {}
        for resource_id in self.resource_registry:
            states[resource_id] = self.track_resource_state(resource_id)
        return states
        
    def get_resource_history(self, resource_id: str, hours: int = 24) -> List[ResourceStateSnapshot]:
        """특정 리소스의 히스토리 반환"""
        if resource_id not in self.resource_snapshots:
            return []
            
        cutoff_time = self.env.now - (hours * 3600)  # hours를 초로 변환
        history = list(self.resource_snapshots[resource_id])
        
        return [snapshot for snapshot in history if snapshot.timestamp >= cutoff_time]


class ProcessPerformanceMonitor:
    """프로세스별 성능 지표 모니터링"""
    
    def __init__(self, env: simpy.Environment, max_history: int = 1000):
        self.env = env
        self.max_history = max_history
        self.process_snapshots: Dict[str, deque] = defaultdict(
            lambda: deque(maxlen=max_history)
        )
        self.process_registry: Dict[str, Any] = {}
        self.performance_thresholds: Dict[str, PerformanceThreshold] = {}
        
    def register_process(self, process_id: str, process_obj: Any):
        """프로세스 등록"""
        self.process_registry[process_id] = process_obj
        print(f"[ReportManager] 프로세스 등록: {process_id}")
        
    def set_performance_threshold(self, threshold: PerformanceThreshold):
        """성능 임계값 설정"""
        self.performance_thresholds[threshold.metric_name] = threshold
        
    def track_process_performance(self, process_id: str) -> ProcessPerformanceSnapshot:
        """특정 프로세스의 성능 추적"""
        if process_id not in self.process_registry:
            return None
            
        process_obj = self.process_registry[process_id]
        
        # 프로세스 성능 메트릭 수집
        performance_metrics = self._collect_process_metrics(process_obj)
        current_status = self._get_process_status(process_obj)
        throughput = self._calculate_throughput(process_obj)
        cycle_time = self._calculate_cycle_time(process_obj)
        queue_length = self._get_queue_length(process_obj)
        
        snapshot = ProcessPerformanceSnapshot(
            process_id=process_id,
            process_type=type(process_obj).__name__,
            timestamp=self.env.now,
            performance_metrics=performance_metrics,
            current_status=current_status,
            throughput=throughput,
            cycle_time=cycle_time,
            queue_length=queue_length
        )
        
        # 히스토리에 추가
        self.process_snapshots[process_id].append(snapshot)
        
        return snapshot
        
    def _collect_process_metrics(self, process_obj: Any) -> Dict[str, float]:
        """프로세스 메트릭 수집"""
        metrics = {}
        
        # BaseProcess 공통 메트릭
        if hasattr(process_obj, 'processing_time'):
            metrics['processing_time'] = process_obj.processing_time
        if hasattr(process_obj, 'current_output_count'):
            metrics['current_output_count'] = process_obj.current_output_count
        if hasattr(process_obj, 'output_buffer_capacity'):
            metrics['output_buffer_capacity'] = process_obj.output_buffer_capacity
            
        # 배치 처리 메트릭
        if hasattr(process_obj, 'batch_size'):
            metrics['batch_size'] = process_obj.batch_size
        if hasattr(process_obj, 'current_batch') and hasattr(process_obj.current_batch, '__len__'):
            metrics['current_batch_size'] = len(process_obj.current_batch)
            
        # 효율성 메트릭
        if hasattr(process_obj, 'get_process_info'):
            info = process_obj.get_process_info()
            metrics.update({k: v for k, v in info.items() if isinstance(v, (int, float))})
            
        return metrics
        
    def _get_process_status(self, process_obj: Any) -> str:
        """프로세스 현재 상태"""
        if hasattr(process_obj, 'waiting_for_transport') and process_obj.waiting_for_transport:
            return "운송_대기"
        elif hasattr(process_obj, 'current_batch') and len(process_obj.current_batch) > 0:
            return "배치_처리중"
        elif hasattr(process_obj, 'is_output_buffer_full') and process_obj.is_output_buffer_full():
            return "출력_버퍼_가득참"
        else:
            return "대기"
            
    def _calculate_throughput(self, process_obj: Any) -> float:
        """처리량 계산 (단위시간당 처리 건수)"""
        if hasattr(process_obj, 'total_processed') and self.env.now > 0:
            return process_obj.total_processed / self.env.now
        return 0.0
        
    def _calculate_cycle_time(self, process_obj: Any) -> float:
        """사이클 타임 계산"""
        if hasattr(process_obj, 'processing_time'):
            return process_obj.processing_time
        return 0.0
        
    def _get_queue_length(self, process_obj: Any) -> int:
        """대기열 길이"""
        if hasattr(process_obj, 'current_batch') and hasattr(process_obj.current_batch, '__len__'):
            return len(process_obj.current_batch)
        return 0
        
    def get_all_process_performance(self) -> Dict[str, ProcessPerformanceSnapshot]:
        """모든 등록된 프로세스의 성능 반환"""
        performance = {}
        for process_id in self.process_registry:
            performance[process_id] = self.track_process_performance(process_id)
        return performance
        
    def detect_performance_anomalies(self) -> List[Dict[str, Any]]:
        """성능 이상 상황 감지"""
        anomalies = []
        
        for process_id, process_obj in self.process_registry.items():
            # 처리량 이상 감지
            throughput = self._calculate_throughput(process_obj)
            if throughput < 0.1:  # 매우 낮은 처리량
                anomalies.append({
                    'process_id': process_id,
                    'type': 'low_throughput',
                    'severity': 'warning',
                    'message': f'처리량이 매우 낮습니다: {throughput:.3f}',
                    'timestamp': self.env.now
                })
                
            # 출력 버퍼 가득참 감지
            if hasattr(process_obj, 'is_output_buffer_full') and process_obj.is_output_buffer_full():
                anomalies.append({
                    'process_id': process_id,
                    'type': 'buffer_full',
                    'severity': 'critical',
                    'message': '출력 버퍼가 가득 찼습니다',
                    'timestamp': self.env.now
                })
                
            # 장시간 대기 감지
            if hasattr(process_obj, 'waiting_for_transport') and process_obj.waiting_for_transport:
                anomalies.append({
                    'process_id': process_id,
                    'type': 'long_wait',
                    'severity': 'warning',
                    'message': '운송을 위해 장시간 대기 중입니다',
                    'timestamp': self.env.now
                })
                
        return anomalies


class AlertSystem:
    """임계값 기반 실시간 알림 시스템"""
    
    def __init__(self, env: simpy.Environment):
        self.env = env
        self.alert_callbacks: List[Callable] = []
        self.alert_history: deque = deque(maxlen=1000)
        self.threshold_rules: Dict[str, Dict[str, float]] = {}
        
    def register_alert_callback(self, callback: Callable):
        """알림 콜백 등록"""
        self.alert_callbacks.append(callback)
        
    def set_threshold_rule(self, metric_name: str, warning: float, critical: float):
        """임계값 규칙 설정"""
        self.threshold_rules[metric_name] = {
            'warning': warning,
            'critical': critical
        }
        
    def check_thresholds(self, metrics: Dict[str, float], component_id: str = None):
        """임계값 체크 및 알림 발생"""
        for metric_name, value in metrics.items():
            if metric_name in self.threshold_rules:
                rules = self.threshold_rules[metric_name]
                
                severity = None
                if value <= rules['critical']:
                    severity = 'critical'
                elif value <= rules['warning']:
                    severity = 'warning'
                    
                if severity:
                    alert = {
                        'component_id': component_id,
                        'metric_name': metric_name,
                        'current_value': value,
                        'severity': severity,
                        'threshold': rules[severity],
                        'message': f'{metric_name} 값 {value}이(가) {severity} 임계값 {rules[severity]}을(를) 벗어났습니다',
                        'timestamp': self.env.now
                    }
                    
                    self.alert_history.append(alert)
                    self._trigger_alert_callbacks(alert)
                    
    def _trigger_alert_callbacks(self, alert: Dict[str, Any]):
        """알림 콜백 실행"""
        for callback in self.alert_callbacks:
            try:
                callback(alert)
            except Exception as e:
                print(f"알림 콜백 실행 중 오류: {e}")
                
    def get_active_alerts(self, hours: int = 24) -> List[Dict[str, Any]]:
        """활성 알림 목록 반환"""
        cutoff_time = self.env.now - (hours * 3600)
        return [alert for alert in self.alert_history if alert['timestamp'] >= cutoff_time]


class ReportManager:
    """모든 리포트 기능의 중앙 관리자"""
    
    def __init__(self, env: simpy.Environment, 
                 stats_manager: Optional[CentralizedStatisticsManager] = None):
        """
        ReportManager 초기화
        
        Args:
            env: SimPy 환경
            stats_manager: 중앙 통계 관리자 (선택적)
        """
        self.env = env
        self.stats_manager = stats_manager or CentralizedStatisticsManager(env)
        
        # 서브 컴포넌트 초기화
        self.resource_tracker = ResourceStateTracker(env)
        self.process_monitor = ProcessPerformanceMonitor(env)
        self.alert_system = AlertSystem(env)
        
        # 시각화 관리자 초기화
        self.visualization_manager = VisualizationManager()
        
        # 통계 인터페이스
        self.stats_interface = StatisticsInterface(
            component_id="report_manager",
            component_type="report_manager",
            stats_manager=self.stats_manager
        )
        
        # 기본 임계값 설정
        self._setup_default_thresholds()
        
        print(f"[시간 {self.env.now:.1f}] ReportManager 초기화 완료")
        
    def _setup_default_thresholds(self):
        """기본 임계값 설정"""
        # 가동률 임계값
        self.alert_system.set_threshold_rule('utilization', warning=30.0, critical=10.0)
        # 가용성 임계값  
        self.alert_system.set_threshold_rule('availability', warning=85.0, critical=70.0)
        # 처리량 임계값
        self.alert_system.set_threshold_rule('throughput', warning=0.5, critical=0.1)
        
    def register_resource(self, resource_id: str, resource_obj: Any):
        """리소스 등록"""
        self.resource_tracker.register_resource(resource_id, resource_obj)
        
    def register_process(self, process_id: str, process_obj: Any):
        """프로세스 등록"""
        self.process_monitor.register_process(process_id, process_obj)
        
    def collect_real_time_status(self) -> Dict[str, Any]:
        """실시간 상태 수집"""
        # 1. 모든 등록된 Resource의 현재 상태 수집
        resource_states = self.resource_tracker.get_all_resource_states()
        
        # 2. 모든 활성 Process의 실행 현황 수집  
        process_performance = self.process_monitor.get_all_process_performance()
        
        # 3. 병목 지점 및 대기열 상태 분석
        bottlenecks = self._analyze_bottlenecks(resource_states, process_performance)
        
        # 4. 이상 상황 감지
        anomalies = self.process_monitor.detect_performance_anomalies()
        
        return {
            'timestamp': self.env.now,
            'resource_states': resource_states,
            'process_performance': process_performance,
            'bottlenecks': bottlenecks,
            'anomalies': anomalies
        }
        
    def calculate_performance_metrics(self) -> Dict[str, Any]:
        """성능 지표 계산"""
        metrics = {}
        
        # 1. 자원 가동률 (Utilization Rate) 계산
        resource_utilization = self._calculate_resource_utilization()
        metrics['resource_utilization'] = resource_utilization
        
        # 2. 처리량 (Throughput) 측정
        throughput = self._calculate_system_throughput()
        metrics['throughput'] = throughput
        
        # 3. 평균 대기시간 (Average Waiting Time) 계산
        avg_waiting_time = self._calculate_average_waiting_time()
        metrics['average_waiting_time'] = avg_waiting_time
        
        # 4. 완료율 (Completion Rate) 산출
        completion_rate = self._calculate_completion_rate()
        metrics['completion_rate'] = completion_rate
        
        # 5. OEE (Overall Equipment Effectiveness) 계산
        oee = self._calculate_overall_oee()
        metrics['oee'] = oee
        
        # 임계값 체크
        flat_metrics = self._flatten_metrics(metrics)
        self.alert_system.check_thresholds(flat_metrics, "system")
        
        return metrics
    
    def extract_resource_utilization_timeline(self, resource_ids: List[str] = None, 
                                            hours: int = 24) -> Dict[str, List[tuple]]:
        """
        리소스들의 사용률 시계열 데이터를 추출
        
        Args:
            resource_ids: 특정 리소스 ID 리스트 (None이면 모든 리소스)
            hours: 몇 시간 전까지의 데이터를 가져올지
            
        Returns:
            {resource_id: [(time, utilization), ...]} 형태의 데이터
        """
        timeline_data = {}
        
        # 대상 리소스 결정
        target_resources = resource_ids if resource_ids else list(self.resource_tracker.resource_registry.keys())
        
        for resource_id in target_resources:
            # 해당 리소스의 히스토리 가져오기
            history = self.resource_tracker.get_resource_history(resource_id, hours)
            
            # 시간-사용률 쌍으로 변환
            timeline_points = []
            for snapshot in history:
                if snapshot and snapshot.metrics:
                    utilization = snapshot.metrics.get('utilization', 0.0)
                    timeline_points.append((snapshot.timestamp, utilization))
            
            # 시간순으로 정렬
            timeline_points.sort(key=lambda x: x[0])
            timeline_data[resource_id] = timeline_points
            
        return timeline_data
    
    def generate_utilization_timeline_chart(self, resource_ids: List[str] = None,
                                          hours: int = 24, 
                                          save_path: str = None,
                                          title: str = None,
                                          show_chart: bool = True) -> str:
        """
        리소스 사용률 타임라인 차트 생성
        
        Args:
            resource_ids: 표시할 리소스 ID 리스트 (None이면 모든 리소스)
            hours: 몇 시간 전까지의 데이터를 표시할지
            save_path: 저장 파일명 (선택적)
            title: 차트 제목 (선택적)
            show_chart: 차트 화면 표시 여부
            
        Returns:
            저장된 파일 경로 (저장된 경우)
        """
        # 시계열 데이터 추출
        timeline_data = self.extract_resource_utilization_timeline(resource_ids, hours)
        
        if not timeline_data:
            print("[ReportManager] 표시할 사용률 데이터가 없습니다.")
            return None
        
        # 차트 제목 설정
        if title is None:
            resource_count = len(timeline_data)
            title = f"리소스 사용률 타임라인 (총 {resource_count}개 리소스, 최근 {hours}시간)"
        
        # 저장 파일명 설정
        if save_path is None:
            timestamp = int(time.time())
            save_path = f"resource_utilization_timeline_{timestamp}.png"
        
        # 차트 생성
        try:
            if show_chart:
                self.visualization_manager.plot_utilization_timeline(
                    resource_utilization_data=timeline_data,
                    title=title,
                    save_path=save_path
                )
            else:
                # 차트를 화면에 표시하지 않고 저장만
                import matplotlib.pyplot as plt
                plt.ioff()  # 인터랙티브 모드 끄기
                self.visualization_manager.plot_utilization_timeline(
                    resource_utilization_data=timeline_data,
                    title=title,
                    save_path=save_path
                )
                plt.ion()  # 인터랙티브 모드 다시 켜기
            
            print(f"[ReportManager] 사용률 타임라인 차트 생성 완료")
            
            # 데이터 요약 출력
            self._print_utilization_summary(timeline_data)
            
            return save_path
            
        except Exception as e:
            print(f"[ReportManager] 차트 생성 중 오류 발생: {e}")
            return None
    
    def generate_real_time_utilization_chart(self, save_path: str = None) -> str:
        """
        현재 시점의 리소스 사용률을 막대 차트로 생성
        
        Args:
            save_path: 저장 파일명 (선택적)
            
        Returns:
            저장된 파일 경로 (저장된 경우)
        """
        # 현재 사용률 데이터 수집
        current_utilization = self._calculate_resource_utilization()
        
        if not current_utilization:
            print("[ReportManager] 표시할 사용률 데이터가 없습니다.")
            return None
        
        # 저장 파일명 설정
        if save_path is None:
            timestamp = int(time.time())
            save_path = f"resource_utilization_current_{timestamp}.png"
        
        # 데이터 준비
        resource_ids = list(current_utilization.keys())
        utilization_values = [util * 100 for util in current_utilization.values()]  # 백분율로 변환
        
        try:
            # 막대 차트 생성
            self.visualization_manager.plot_bar_chart(
                categories=resource_ids,
                values=utilization_values,
                title=f"현재 리소스 사용률 (시뮬레이션 시간: {self.env.now:.1f})",
                x_label="리소스 ID",
                y_label="사용률 (%)",
                save_path=save_path
            )
            
            print(f"[ReportManager] 실시간 사용률 차트 생성 완료")
            return save_path
            
        except Exception as e:
            print(f"[ReportManager] 차트 생성 중 오류 발생: {e}")
            return None
    
    def compare_resource_utilization_trends(self, resource_ids: List[str], 
                                          hours: int = 24,
                                          save_path: str = None) -> str:
        """
        특정 리소스들의 사용률 트렌드 비교 차트 생성
        
        Args:
            resource_ids: 비교할 리소스 ID 리스트
            hours: 분석 시간 범위
            save_path: 저장 파일명
            
        Returns:
            저장된 파일 경로
        """
        timeline_data = self.extract_resource_utilization_timeline(resource_ids, hours)
        
        if not timeline_data:
            print("[ReportManager] 비교할 데이터가 없습니다.")
            return None
        
        # 저장 파일명 설정
        if save_path is None:
            timestamp = int(time.time())
            save_path = f"resource_utilization_comparison_{timestamp}.png"
        
        # 차트 생성
        try:
            title = f"리소스 사용률 트렌드 비교 ({', '.join(resource_ids)})"
            
            self.visualization_manager.plot_utilization_timeline(
                resource_utilization_data=timeline_data,
                title=title,
                save_path=save_path
            )
            
            print(f"[ReportManager] 사용률 트렌드 비교 차트 생성 완료")
            return save_path
            
        except Exception as e:
            print(f"[ReportManager] 차트 생성 중 오류 발생: {e}")
            return None
    
    def _print_utilization_summary(self, timeline_data: Dict[str, List[tuple]]):
        """사용률 데이터 요약 정보 출력"""
        print("\n=== 리소스 사용률 요약 ===")
        
        for resource_id, data_points in timeline_data.items():
            if not data_points:
                continue
                
            utilizations = [point[1] for point in data_points]
            
            avg_util = sum(utilizations) / len(utilizations) if utilizations else 0
            max_util = max(utilizations) if utilizations else 0
            min_util = min(utilizations) if utilizations else 0
            current_util = utilizations[-1] if utilizations else 0
            
            print(f"리소스 {resource_id}:")
            print(f"  - 평균 사용률: {avg_util:.1%}")
            print(f"  - 최대 사용률: {max_util:.1%}")
            print(f"  - 최소 사용률: {min_util:.1%}")
            print(f"  - 현재 사용률: {current_util:.1%}")
            print(f"  - 데이터 포인트 수: {len(data_points)}")
        
        print("=" * 30)
        
    def detect_anomalies(self) -> List[Dict[str, Any]]:
        """이상 상황 감지"""
        anomalies = []
        
        # 1. 설정된 임계값과 현재 값 비교
        current_metrics = self.calculate_performance_metrics()
        threshold_anomalies = self._detect_threshold_anomalies(current_metrics)
        anomalies.extend(threshold_anomalies)
        
        # 2. 예상 범위를 벗어난 성능 지표 식별
        performance_anomalies = self.process_monitor.detect_performance_anomalies()
        anomalies.extend(performance_anomalies)
        
        # 3. 장시간 대기 상태인 자원/공정 감지
        waiting_anomalies = self._detect_waiting_anomalies()
        anomalies.extend(waiting_anomalies)
        
        # 4. 처리량 급감 패턴 탐지
        throughput_anomalies = self._detect_throughput_drops()
        anomalies.extend(throughput_anomalies)
        
        return anomalies
        
    def generate_real_time_dashboard(self) -> Dict[str, Any]:
        """실시간 대시보드 데이터 생성"""
        dashboard_data = {
            'timestamp': time.time(),
            'simulation_time': self.env.now,
            'system_status': self._determine_system_status(),
            'key_metrics': self._get_key_metrics(),
            'resource_overview': self._get_resource_overview(),
            'process_overview': self._get_process_overview(),
            'active_alerts': self.alert_system.get_active_alerts(hours=1),
            'performance_indicators': self.calculate_performance_metrics()
        }
        
        return dashboard_data
        
    def generate_comprehensive_report(self) -> Dict[str, Any]:
        """종합 성능 리포트 생성"""
        report = {
            'report_metadata': {
                'generated_at': time.time(),
                'simulation_time': self.env.now,
                'report_type': ReportType.COMPREHENSIVE_REPORT.value,
                'version': '1.0'
            },
            'executive_summary': self._generate_executive_summary(),
            'resource_analysis': self._generate_resource_analysis(),
            'process_analysis': self._generate_process_analysis(), 
            'performance_metrics': self.calculate_performance_metrics(),
            'anomaly_analysis': self.detect_anomalies(),
            'recommendations': self._generate_recommendations(),
            'detailed_statistics': self.stats_manager.get_global_statistics() if self.stats_manager else {}
        }
        
        return report
        
    def track_resource_status(self, resource_id: str) -> Dict[str, Any]:
        """특정 자원 상태 추적"""
        snapshot = self.resource_tracker.track_resource_state(resource_id)
        if not snapshot:
            return {'error': f'Resource {resource_id} not found'}
            
        history = self.resource_tracker.get_resource_history(resource_id, hours=24)
        
        return {
            'resource_id': resource_id,
            'current_state': snapshot.__dict__,
            'historical_data': [snap.__dict__ for snap in history],
            'trend_analysis': self._analyze_resource_trend(history),
            'performance_score': self._calculate_resource_performance_score(snapshot)
        }
        
    def track_process_performance(self, process_id: str) -> Dict[str, Any]:
        """특정 공정 성능 추적"""
        snapshot = self.process_monitor.track_process_performance(process_id)
        if not snapshot:
            return {'error': f'Process {process_id} not found'}
            
        return {
            'process_id': process_id,
            'current_performance': snapshot.__dict__,
            'efficiency_score': self._calculate_process_efficiency(snapshot),
            'bottleneck_analysis': self._analyze_process_bottlenecks(process_id),
            'improvement_suggestions': self._suggest_process_improvements(snapshot)
        }
        
    def export_data(self, format: ExportFormat, data: Dict[str, Any] = None, 
                   filename: str = None) -> str:
        """데이터 내보내기"""
        if data is None:
            data = self.generate_comprehensive_report()
            
        if filename is None:
            timestamp = int(time.time())
            filename = f"manufacturing_report_{timestamp}"
            
        try:
            if format == ExportFormat.JSON:
                filepath = f"{filename}.json"
                with open(filepath, 'w', encoding='utf-8') as f:
                    json.dump(data, f, ensure_ascii=False, indent=2, default=str)
                    
            elif format == ExportFormat.CSV:
                filepath = f"{filename}.csv"
                # 중요 메트릭만 CSV로 변환
                csv_data = self._convert_to_csv_format(data)
                df = pd.DataFrame(csv_data)
                df.to_csv(filepath, index=False, encoding='utf-8-sig')
                
            elif format == ExportFormat.EXCEL:
                filepath = f"{filename}.xlsx"
                with pd.ExcelWriter(filepath, engine='openpyxl') as writer:
                    # 여러 시트로 데이터 분할
                    self._write_excel_sheets(data, writer)
                    
            elif format == ExportFormat.HTML:
                filepath = f"{filename}.html"
                html_content = self._generate_html_report(data)
                with open(filepath, 'w', encoding='utf-8') as f:
                    f.write(html_content)
                    
            print(f"[ReportManager] 데이터 내보내기 완료: {filepath}")
            return filepath
            
        except Exception as e:
            print(f"[ReportManager] 데이터 내보내기 실패: {e}")
            return None
            
    # === 내부 헬퍼 메서드들 ===
    
    def _analyze_bottlenecks(self, resource_states: Dict, process_performance: Dict) -> List[Dict[str, Any]]:
        """병목 지점 분석"""
        bottlenecks = []
        
        # 높은 가동률 리소스 찾기
        for resource_id, state in resource_states.items():
            if state and 'metrics' in state.__dict__:
                utilization = state.metrics.get('utilization', 0)
                if utilization > 0.9:  # 90% 초과
                    bottlenecks.append({
                        'type': 'resource_bottleneck',
                        'component_id': resource_id,
                        'severity': 'high',
                        'utilization': utilization,
                        'message': f'리소스 {resource_id}의 가동률이 {utilization:.1%}로 매우 높습니다'
                    })
                    
        # 출력 버퍼 가득찬 프로세스 찾기
        for process_id, perf in process_performance.items():
            if perf and perf.current_status == "출력_버퍼_가득함":
                bottlenecks.append({
                    'type': 'process_bottleneck',
                    'component_id': process_id,
                    'severity': 'critical',
                    'message': f'프로세스 {process_id}의 출력 버퍼가 가득 찼습니다'
                })
                
        return bottlenecks
        
    def _calculate_resource_utilization(self) -> Dict[str, float]:
        """자원 가동률 계산"""
        utilization = {}
        resource_states = self.resource_tracker.get_all_resource_states()
        
        for resource_id, state in resource_states.items():
            if state and 'metrics' in state.__dict__:
                utilization[resource_id] = state.metrics.get('utilization', 0.0)
                
        return utilization
        
    def _calculate_system_throughput(self) -> float:
        """시스템 전체 처리량 계산"""
        total_throughput = 0.0
        process_performance = self.process_monitor.get_all_process_performance()
        
        for process_id, perf in process_performance.items():
            if perf:
                total_throughput += perf.throughput
                
        return total_throughput
        
    def _calculate_average_waiting_time(self) -> float:
        """평균 대기시간 계산"""
        # 중앙 통계 관리자에서 대기시간 데이터 수집
        if self.stats_manager:
            global_stats = self.stats_manager.get_global_statistics()
            waiting_times = global_stats.get('aggregated_metrics', {}).get('waiting_time', {})
            return waiting_times.get('average', 0.0)
        return 0.0
        
    def _calculate_completion_rate(self) -> float:
        """완료율 계산"""
        if self.stats_manager:
            global_stats = self.stats_manager.get_global_statistics()
            success_metrics = global_stats.get('aggregated_metrics', {}).get('successful_operations', {})
            total_metrics = global_stats.get('aggregated_metrics', {}).get('total_requests', {})
            
            total_success = success_metrics.get('total', 0)
            total_requests = total_metrics.get('total', 1)
            
            return (total_success / total_requests) * 100 if total_requests > 0 else 0.0
        return 0.0
        
    def _calculate_overall_oee(self) -> float:
        """전체 OEE 계산"""
        if self.stats_manager:
            global_stats = self.stats_manager.get_global_statistics()
            manufacturing_summary = global_stats.get('manufacturing_summary', {})
            return manufacturing_summary.get('overall_oee', 0.0)
        return 0.0
        
    def _flatten_metrics(self, metrics: Dict[str, Any]) -> Dict[str, float]:
        """중첩된 메트릭을 평면화"""
        flat_metrics = {}
        
        def flatten_dict(d, prefix=''):
            for key, value in d.items():
                new_key = f"{prefix}_{key}" if prefix else key
                if isinstance(value, dict):
                    flatten_dict(value, new_key)
                elif isinstance(value, (int, float)):
                    flat_metrics[new_key] = value
                    
        flatten_dict(metrics)
        return flat_metrics
        
    def _detect_threshold_anomalies(self, metrics: Dict[str, Any]) -> List[Dict[str, Any]]:
        """임계값 기반 이상 감지"""
        # AlertSystem에서 이미 처리됨
        return []
        
    def _detect_waiting_anomalies(self) -> List[Dict[str, Any]]:
        """대기 상태 이상 감지"""
        anomalies = []
        process_performance = self.process_monitor.get_all_process_performance()
        
        for process_id, perf in process_performance.items():
            if perf and perf.current_status in ["운송_대기", "출력_버퍼_가득참"]:
                anomalies.append({
                    'type': 'long_waiting',
                    'component_id': process_id,
                    'severity': 'warning',
                    'message': f'프로세스 {process_id}가 {perf.current_status} 상태입니다',
                    'timestamp': self.env.now
                })
                
        return anomalies
        
    def _detect_throughput_drops(self) -> List[Dict[str, Any]]:
        """처리량 급감 패턴 탐지"""
        anomalies = []
        # 여기서는 간단한 구현. 실제로는 히스토리 비교 필요
        current_throughput = self._calculate_system_throughput()
        
        if current_throughput < 0.1:  # 매우 낮은 처리량
            anomalies.append({
                'type': 'throughput_drop',
                'component_id': 'system',
                'severity': 'critical',
                'message': f'시스템 처리량이 매우 낮습니다: {current_throughput:.3f}',
                'timestamp': self.env.now
            })
            
        return anomalies
        
    def _determine_system_status(self) -> str:
        """시스템 전체 상태 판단"""
        active_alerts = self.alert_system.get_active_alerts(hours=1)
        
        critical_alerts = [a for a in active_alerts if a['severity'] == 'critical']
        warning_alerts = [a for a in active_alerts if a['severity'] == 'warning']
        
        if critical_alerts:
            return 'critical'
        elif len(warning_alerts) > 5:
            return 'warning'
        elif warning_alerts:
            return 'caution'
        else:
            return 'healthy'
            
    def _get_key_metrics(self) -> Dict[str, Any]:
        """주요 메트릭 요약"""
        metrics = self.calculate_performance_metrics()
        
        return {
            'system_throughput': self._calculate_system_throughput(),
            'average_utilization': sum(metrics.get('resource_utilization', {}).values()) / 
                                 len(metrics.get('resource_utilization', {})) if metrics.get('resource_utilization') else 0,
            'completion_rate': metrics.get('completion_rate', 0),
            'oee': metrics.get('oee', 0),
            'active_alerts': len(self.alert_system.get_active_alerts(hours=1))
        }
        
    def _get_resource_overview(self) -> Dict[str, Any]:
        """리소스 개요"""
        resource_states = self.resource_tracker.get_all_resource_states()
        
        total_resources = len(resource_states)
        active_resources = sum(1 for state in resource_states.values() 
                             if state and state.status.get('is_available', False))
        
        return {
            'total_resources': total_resources,
            'active_resources': active_resources,
            'availability_rate': (active_resources / total_resources * 100) if total_resources > 0 else 0
        }
        
    def _get_process_overview(self) -> Dict[str, Any]:
        """프로세스 개요"""
        process_performance = self.process_monitor.get_all_process_performance()
        
        total_processes = len(process_performance)
        active_processes = sum(1 for perf in process_performance.values() 
                             if perf and perf.current_status != "대기")
        
        return {
            'total_processes': total_processes,
            'active_processes': active_processes,
            'activity_rate': (active_processes / total_processes * 100) if total_processes > 0 else 0
        }
        
    def _generate_executive_summary(self) -> Dict[str, Any]:
        """경영진 요약 생성"""
        key_metrics = self._get_key_metrics()
        
        return {
            'simulation_duration': self.env.now,
            'system_status': self._determine_system_status(),
            'overall_performance': {
                'throughput': key_metrics['system_throughput'],
                'efficiency': key_metrics['average_utilization'],
                'quality': key_metrics['completion_rate']
            },
            'critical_issues': len([a for a in self.alert_system.get_active_alerts() 
                                  if a['severity'] == 'critical']),
            'recommendations_count': 3  # 실제로는 추천사항 개수 계산
        }
        
    def _generate_resource_analysis(self) -> Dict[str, Any]:
        """리소스 분석 생성"""
        resource_states = self.resource_tracker.get_all_resource_states()
        utilization = self._calculate_resource_utilization()
        
        return {
            'resource_count': len(resource_states),
            'utilization_analysis': utilization,
            'performance_ranking': sorted(utilization.items(), key=lambda x: x[1], reverse=True),
            'underutilized_resources': {k: v for k, v in utilization.items() if v < 0.3},
            'overutilized_resources': {k: v for k, v in utilization.items() if v > 0.9}
        }
        
    def _generate_process_analysis(self) -> Dict[str, Any]:
        """프로세스 분석 생성"""
        process_performance = self.process_monitor.get_all_process_performance()
        
        throughputs = {pid: perf.throughput for pid, perf in process_performance.items() if perf}
        cycle_times = {pid: perf.cycle_time for pid, perf in process_performance.items() if perf}
        
        return {
            'process_count': len(process_performance),
            'throughput_analysis': throughputs,
            'cycle_time_analysis': cycle_times,
            'bottleneck_processes': [pid for pid, perf in process_performance.items() 
                                   if perf and perf.current_status == "출력_버퍼_가득참"],
            'idle_processes': [pid for pid, perf in process_performance.items() 
                             if perf and perf.current_status == "대기"]
        }
        
    def _generate_recommendations(self) -> List[Dict[str, Any]]:
        """개선 추천사항 생성"""
        recommendations = []
        
        # 낮은 가동률 리소스에 대한 추천
        utilization = self._calculate_resource_utilization()
        for resource_id, util in utilization.items():
            if util < 0.3:
                recommendations.append({
                    'type': 'resource_optimization',
                    'priority': 'medium',
                    'target': resource_id,
                    'issue': f'낮은 가동률 ({util:.1%})',
                    'recommendation': '작업 스케줄링 최적화 또는 다른 프로세스로 재할당 검토'
                })
                
        # 병목 프로세스에 대한 추천
        bottlenecks = self._analyze_bottlenecks(
            self.resource_tracker.get_all_resource_states(),
            self.process_monitor.get_all_process_performance()
        )
        
        for bottleneck in bottlenecks:
            recommendations.append({
                'type': 'bottleneck_resolution',
                'priority': 'high',
                'target': bottleneck['component_id'],
                'issue': bottleneck['message'],
                'recommendation': '용량 증설 또는 프로세스 병렬화 검토'
            })
            
        return recommendations
        
    def _analyze_resource_trend(self, history: List[ResourceStateSnapshot]) -> Dict[str, Any]:
        """리소스 트렌드 분석"""
        if len(history) < 2:
            return {'trend': 'insufficient_data'}
            
        # 가동률 트렌드 분석
        utilizations = [snap.metrics.get('utilization', 0) for snap in history]
        
        if len(utilizations) >= 2:
            trend = 'increasing' if utilizations[-1] > utilizations[0] else 'decreasing'
            change_rate = (utilizations[-1] - utilizations[0]) / len(utilizations)
        else:
            trend = 'stable'
            change_rate = 0
            
        return {
            'trend': trend,
            'change_rate': change_rate,
            'current_utilization': utilizations[-1] if utilizations else 0,
            'average_utilization': sum(utilizations) / len(utilizations) if utilizations else 0
        }
        
    def _calculate_resource_performance_score(self, snapshot: ResourceStateSnapshot) -> float:
        """리소스 성능 점수 계산"""
        if not snapshot or not snapshot.metrics:
            return 0.0
            
        # 여러 메트릭을 종합한 점수 (0-100)
        utilization = snapshot.metrics.get('utilization', 0) * 100
        availability = snapshot.metrics.get('availability', 1) * 100
        
        # 가중평균 (가용성에 더 높은 가중치)
        score = (utilization * 0.4 + availability * 0.6)
        
        # 알림이 있으면 점수 차감
        if snapshot.alerts:
            critical_alerts = len([a for a in snapshot.alerts if a.get('severity') == 'critical'])
            warning_alerts = len([a for a in snapshot.alerts if a.get('severity') == 'warning'])
            score -= (critical_alerts * 20 + warning_alerts * 10)
            
        return max(0, min(100, score))
        
    def _calculate_process_efficiency(self, snapshot: ProcessPerformanceSnapshot) -> float:
        """프로세스 효율성 계산"""
        if not snapshot:
            return 0.0
            
        # 처리량과 사이클 타임을 기반으로 효율성 계산
        efficiency = snapshot.throughput * 100  # 간단한 효율성 지표
        
        # 대기 상태이면 효율성 감소
        if snapshot.current_status == "대기":
            efficiency *= 0.5
        elif snapshot.current_status in ["운송_대기", "출력_버퍼_가득참"]:
            efficiency *= 0.7
            
        return max(0, min(100, efficiency))
        
    def _analyze_process_bottlenecks(self, process_id: str) -> Dict[str, Any]:
        """프로세스 병목 분석"""
        if process_id not in self.process_monitor.process_registry:
            return {}
            
        snapshot = self.process_monitor.track_process_performance(process_id)
        if not snapshot:
            return {}
            
        bottlenecks = []
        
        # 출력 버퍼 가득참
        if snapshot.current_status == "출력_버퍼_가득참":
            bottlenecks.append({
                'type': 'output_buffer',
                'severity': 'high',
                'message': '출력 버퍼가 가득 차서 처리가 지연됩니다'
            })
            
        # 낮은 처리량
        if snapshot.throughput < 0.1:
            bottlenecks.append({
                'type': 'low_throughput',
                'severity': 'medium', 
                'message': '처리량이 기대값보다 낮습니다'
            })
            
        return {
            'process_id': process_id,
            'bottlenecks': bottlenecks,
            'bottleneck_score': len(bottlenecks) * 25  # 0-100 점수
        }
        
    def _suggest_process_improvements(self, snapshot: ProcessPerformanceSnapshot) -> List[str]:
        """프로세스 개선 제안"""
        suggestions = []
        
        if snapshot.current_status == "출력_버퍼_가득참":
            suggestions.append("운송 프로세스의 용량을 늘리거나 빈도를 높이세요")
            
        if snapshot.throughput < 0.5:
            suggestions.append("프로세스 병렬화나 배치 크기 증대를 고려하세요")
            
        if snapshot.queue_length > 10:
            suggestions.append("입력 대기열이 길어지고 있습니다. 처리 속도를 개선하세요")
            
        if not suggestions:
            suggestions.append("현재 프로세스가 정상적으로 운영되고 있습니다")
            
        return suggestions
        
    def _convert_to_csv_format(self, data: Dict[str, Any]) -> List[Dict[str, Any]]:
        """CSV 형식으로 데이터 변환"""
        csv_rows = []
        
        # 주요 메트릭을 CSV 행으로 변환
        metrics = data.get('performance_metrics', {})
        timestamp = data.get('report_metadata', {}).get('simulation_time', 0)
        
        def add_metrics_to_csv(metric_dict, prefix=''):
            for key, value in metric_dict.items():
                if isinstance(value, dict):
                    add_metrics_to_csv(value, f"{prefix}_{key}" if prefix else key)
                elif isinstance(value, (int, float)):
                    csv_rows.append({
                        'timestamp': timestamp,
                        'metric_name': f"{prefix}_{key}" if prefix else key,
                        'value': value,
                        'unit': ''  # 단위는 메트릭별로 설정 가능
                    })
                    
        add_metrics_to_csv(metrics)
        return csv_rows
        
    def _write_excel_sheets(self, data: Dict[str, Any], writer):
        """Excel 시트별 데이터 작성"""
        # 요약 시트
        summary_data = {
            'Metric': [],
            'Value': [],
            'Unit': []
        }
        
        key_metrics = data.get('performance_metrics', {})
        for key, value in key_metrics.items():
            if isinstance(value, (int, float)):
                summary_data['Metric'].append(key)
                summary_data['Value'].append(value)
                summary_data['Unit'].append('')
                
        pd.DataFrame(summary_data).to_sheet('Summary', writer, index=False)
        
        # 리소스 분석 시트
        resource_analysis = data.get('resource_analysis', {})
        if resource_analysis:
            pd.DataFrame([resource_analysis]).to_sheet('Resource_Analysis', writer, index=False)
            
        # 프로세스 분석 시트  
        process_analysis = data.get('process_analysis', {})
        if process_analysis:
            pd.DataFrame([process_analysis]).to_sheet('Process_Analysis', writer, index=False)
            
    def _generate_html_report(self, data: Dict[str, Any]) -> str:
        """HTML 리포트 생성"""
        html_template = f"""
        <!DOCTYPE html>
        <html>
        <head>
            <title>Manufacturing Simulation Report</title>
            <style>
                body {{ font-family: Arial, sans-serif; margin: 20px; }}
                h1, h2 {{ color: #333; }}
                table {{ border-collapse: collapse; width: 100%; margin: 10px 0; }}
                th, td {{ border: 1px solid #ddd; padding: 8px; text-align: left; }}
                th {{ background-color: #f2f2f2; }}
                .summary {{ background-color: #f9f9f9; padding: 15px; border-radius: 5px; }}
            </style>
        </head>
        <body>
            <h1>Manufacturing Simulation Report</h1>
            
            <div class="summary">
                <h2>Executive Summary</h2>
                <p><strong>Report Generated:</strong> {time.strftime('%Y-%m-%d %H:%M:%S')}</p>
                <p><strong>Simulation Time:</strong> {data.get('report_metadata', {}).get('simulation_time', 0):.2f}</p>
                <p><strong>System Status:</strong> {data.get('executive_summary', {}).get('system_status', 'Unknown')}</p>
            </div>
            
            <h2>Key Performance Metrics</h2>
            <table>
                <tr><th>Metric</th><th>Value</th></tr>
        """
        
        # 성능 메트릭 테이블 추가
        metrics = data.get('performance_metrics', {})
        for key, value in metrics.items():
            if isinstance(value, (int, float)):
                html_template += f"<tr><td>{key}</td><td>{value:.4f}</td></tr>"
                
        html_template += """
            </table>
            
            <h2>Recommendations</h2>
            <ul>
        """
        
        # 추천사항 추가
        recommendations = data.get('recommendations', [])
        for rec in recommendations[:5]:  # 상위 5개만
            html_template += f"<li><strong>{rec.get('type', 'General')}:</strong> {rec.get('recommendation', 'No details')}</li>"
            
        html_template += """
            </ul>
        </body>
        </html>
        """
        
        return html_template


# === 편의를 위한 팩토리 함수 ===

def create_report_manager(env: simpy.Environment, 
                         stats_manager: Optional[CentralizedStatisticsManager] = None) -> ReportManager:
    """
    ReportManager 생성 팩토리 함수
    
    Args:
        env: SimPy 환경
        stats_manager: 중앙 통계 관리자 (선택적)
        
    Returns:
        ReportManager: 설정된 리포트 관리자
    """
    return ReportManager(env, stats_manager)
    

def setup_default_alert_callbacks(report_manager: ReportManager):
    """
    기본 알림 콜백 설정
    
    Args:
        report_manager: 리포트 관리자
    """
    def print_alert(alert):
        severity_emoji = {
            'critical': '🚨',
            'warning': '⚠️', 
            'info': 'ℹ️'
        }
        emoji = severity_emoji.get(alert['severity'], '📋')
        print(f"{emoji} [Alert] {alert['message']} (Component: {alert.get('component_id', 'Unknown')})")
        
    report_manager.alert_system.register_alert_callback(print_alert)