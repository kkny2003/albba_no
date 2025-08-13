"""
실시간 데이터 연동 시스템

시뮬레이션 엔진과 대시보드 간의 실시간 데이터 연동을 담당합니다.
"""

import threading
import time
import queue
import json
from typing import Dict, List, Any, Optional, Callable, Tuple
from datetime import datetime, timedelta
from dataclasses import dataclass, asdict
import pickle
import os

try:
    from src.core.centralized_statistics import CentralizedStatisticsManager
    from src.dashboard.kpi_widgets import KPIManager, KPIData, KPIThreshold, AlertLevel
except ImportError:
    # 테스트 환경에서는 Mock 클래스 사용
    class MockStatisticsManager:
        pass
    CentralizedStatisticsManager = MockStatisticsManager


@dataclass
class DataSnapshot:
    """데이터 스냅샷"""
    timestamp: datetime
    kpi_data: Dict[str, Any]
    resource_data: Dict[str, Any]
    process_data: Dict[str, Any]
    alerts: List[Dict[str, Any]]
    simulation_time: float
    
    def to_dict(self) -> Dict[str, Any]:
        """딕셔너리로 변환"""
        return {
            'timestamp': self.timestamp.isoformat(),
            'kpi_data': self.kpi_data,
            'resource_data': self.resource_data,
            'process_data': self.process_data,
            'alerts': self.alerts,
            'simulation_time': self.simulation_time
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]):
        """딕셔너리에서 생성"""
        return cls(
            timestamp=datetime.fromisoformat(data['timestamp']),
            kpi_data=data['kpi_data'],
            resource_data=data['resource_data'],
            process_data=data['process_data'],
            alerts=data['alerts'],
            simulation_time=data['simulation_time']
        )


class DataBridge:
    """시뮬레이션과 대시보드 간 데이터 브릿지"""
    
    def __init__(self, update_interval: float = 1.0):
        """
        데이터 브릿지 초기화
        
        Args:
            update_interval: 업데이트 간격 (초)
        """
        self.update_interval = update_interval
        self.stats_manager: Optional[CentralizedStatisticsManager] = None
        self.kpi_manager = KPIManager()
        
        # 데이터 저장
        self.data_queue = queue.Queue(maxsize=1000)
        self.latest_snapshot: Optional[DataSnapshot] = None
        self.data_history: List[DataSnapshot] = []
        
        # 실시간 업데이트
        self.running = False
        self.update_thread: Optional[threading.Thread] = None
        self.subscribers: List[Callable] = []
        
        # 설정
        self.max_history_size = 1000
        self.data_cache_file = "dashboard_cache.json"
        
    def connect_simulation(self, stats_manager: CentralizedStatisticsManager):
        """시뮬레이션 연결"""
        self.stats_manager = stats_manager
        self._initialize_kpis()
        
    def _initialize_kpis(self):
        """KPI 초기화"""
        if not self.stats_manager:
            return
        
        # 기본 KPI들 등록
        kpis_config = [
            {
                'name': 'throughput',
                'display_name': '처리량',
                'unit': 'units/h',
                'threshold': KPIThreshold(
                    warning_min=80, warning_max=120,
                    critical_min=60, critical_max=150,
                    target=100
                )
            },
            {
                'name': 'utilization',
                'display_name': '전체 사용률',
                'unit': '%',
                'threshold': KPIThreshold(
                    warning_min=0.6, warning_max=0.9,
                    critical_min=0.4, critical_max=0.95,
                    target=0.8
                )
            },
            {
                'name': 'cycle_time',
                'display_name': '평균 사이클 타임',
                'unit': 'min',
                'threshold': KPIThreshold(
                    warning_max=50, critical_max=60,
                    target=45
                )
            },
            {
                'name': 'quality_score',
                'display_name': '품질 점수',
                'unit': '%',
                'threshold': KPIThreshold(
                    warning_min=90, critical_min=85,
                    target=95
                )
            }
        ]
        
        for config in kpis_config:
            kpi_data = KPIData(
                name=config['display_name'],
                value=0.0,
                unit=config['unit'],
                threshold=config['threshold']
            )
            self.kpi_manager.register_kpi(config['name'], kpi_data)
    
    def start_monitoring(self):
        """모니터링 시작"""
        if self.running:
            return
        
        self.running = True
        self.update_thread = threading.Thread(target=self._update_loop, daemon=True)
        self.update_thread.start()
        print(f"[DataBridge] 실시간 모니터링 시작됨 (간격: {self.update_interval}초)")
    
    def stop_monitoring(self):
        """모니터링 중지"""
        self.running = False
        if self.update_thread and self.update_thread.is_alive():
            self.update_thread.join(timeout=5)
        print("[DataBridge] 실시간 모니터링 중지됨")
    
    def _update_loop(self):
        """업데이트 루프"""
        while self.running:
            try:
                snapshot = self._collect_data()
                if snapshot:
                    self._process_snapshot(snapshot)
                time.sleep(self.update_interval)
            except Exception as e:
                print(f"[DataBridge] 업데이트 오류: {e}")
                time.sleep(self.update_interval)
    
    def _collect_data(self) -> Optional[DataSnapshot]:
        """데이터 수집"""
        if not self.stats_manager:
            return self._generate_mock_snapshot()
        
        try:
            # KPI 데이터 수집
            kpi_data = {
                'throughput': self.stats_manager.get_global_metric('throughput', 0),
                'utilization': self.stats_manager.get_global_metric('utilization', 0),
                'cycle_time': self.stats_manager.get_global_metric('cycle_time', 0),
                'quality_score': self.stats_manager.get_global_metric('quality_score', 95),
                'active_resources': len(self.stats_manager.get_all_resource_ids())
            }
            
            # 리소스 데이터 수집
            resource_data = {}
            for resource_id in self.stats_manager.get_all_resource_ids():
                resource_data[resource_id] = {
                    'utilization': self.stats_manager.get_resource_metric(resource_id, 'utilization', 0),
                    'throughput': self.stats_manager.get_resource_metric(resource_id, 'throughput', 0),
                    'status': self.stats_manager.get_resource_metric(resource_id, 'status', 'unknown')
                }
            
            # 프로세스 데이터 수집
            process_data = {
                'total_processed': self.stats_manager.get_global_metric('total_processed', 0),
                'processing_time_avg': self.stats_manager.get_global_metric('processing_time_avg', 0),
                'queue_lengths': {}  # 큐 길이 정보
            }
            
            # 알림 데이터
            alerts = []
            recent_alerts = self.kpi_manager.alert_system.get_recent_alerts(10)
            for alert in recent_alerts:
                alerts.append({
                    'level': alert['level'].value,
                    'message': alert['message'],
                    'timestamp': alert['timestamp'].isoformat(),
                    'source': alert['source']
                })
            
            snapshot = DataSnapshot(
                timestamp=datetime.now(),
                kpi_data=kpi_data,
                resource_data=resource_data,
                process_data=process_data,
                alerts=alerts,
                simulation_time=getattr(self.stats_manager, 'current_time', 0)
            )
            
            return snapshot
            
        except Exception as e:
            print(f"[DataBridge] 데이터 수집 오류: {e}")
            return None
    
    def _generate_mock_snapshot(self) -> DataSnapshot:
        """Mock 데이터 스냅샷 생성"""
        import random
        
        # 시뮬레이션된 데이터
        base_time = time.time() % 1000
        kpi_data = {
            'throughput': 90 + 20 * random.random(),
            'utilization': 0.7 + 0.2 * random.random(),
            'cycle_time': 40 + 10 * random.random(),
            'quality_score': 92 + 6 * random.random(),
            'active_resources': random.randint(8, 12)
        }
        
        resource_data = {}
        for i in range(1, kpi_data['active_resources'] + 1):
            resource_id = f"Machine_{i:02d}"
            resource_data[resource_id] = {
                'utilization': 0.6 + 0.3 * random.random(),
                'throughput': 8 + 4 * random.random(),
                'status': random.choice(['running', 'idle', 'maintenance'])
            }
        
        process_data = {
            'total_processed': int(base_time * 10),
            'processing_time_avg': 42 + 8 * random.random(),
            'queue_lengths': {
                'input_queue': random.randint(0, 10),
                'output_queue': random.randint(0, 5)
            }
        }
        
        # 가끔 알림 생성
        alerts = []
        if random.random() < 0.1:  # 10% 확률
            alerts.append({
                'level': random.choice(['info', 'warning', 'error']),
                'message': f"Machine_{random.randint(1, 10):02d} 상태 변경",
                'timestamp': datetime.now().isoformat(),
                'source': 'Mock System'
            })
        
        return DataSnapshot(
            timestamp=datetime.now(),
            kpi_data=kpi_data,
            resource_data=resource_data,
            process_data=process_data,
            alerts=alerts,
            simulation_time=base_time
        )
    
    def _process_snapshot(self, snapshot: DataSnapshot):
        """스냅샷 처리"""
        # 최신 데이터 업데이트
        self.latest_snapshot = snapshot
        
        # 히스토리 저장
        self.data_history.append(snapshot)
        if len(self.data_history) > self.max_history_size:
            self.data_history = self.data_history[-self.max_history_size:]
        
        # KPI 업데이트
        self._update_kpis(snapshot)
        
        # 큐에 추가
        try:
            self.data_queue.put_nowait(snapshot)
        except queue.Full:
            # 큐가 가득 찬 경우 오래된 데이터 제거
            try:
                self.data_queue.get_nowait()
                self.data_queue.put_nowait(snapshot)
            except queue.Empty:
                pass
        
        # 구독자들에게 알림
        self._notify_subscribers(snapshot)
    
    def _update_kpis(self, snapshot: DataSnapshot):
        """KPI 업데이트"""
        kpi_data = snapshot.kpi_data
        timestamp = snapshot.timestamp
        
        # 각 KPI 업데이트
        for kpi_name, value in kpi_data.items():
            if kpi_name in self.kpi_manager.kpis:
                self.kpi_manager.update_kpi(kpi_name, value, timestamp)
    
    def _notify_subscribers(self, snapshot: DataSnapshot):
        """구독자들에게 알림"""
        for subscriber in self.subscribers:
            try:
                subscriber(snapshot)
            except Exception as e:
                print(f"[DataBridge] 구독자 알림 오류: {e}")
    
    def subscribe(self, callback: Callable[[DataSnapshot], None]):
        """데이터 업데이트 구독"""
        self.subscribers.append(callback)
    
    def unsubscribe(self, callback: Callable[[DataSnapshot], None]):
        """구독 해제"""
        if callback in self.subscribers:
            self.subscribers.remove(callback)
    
    def get_latest_data(self) -> Optional[DataSnapshot]:
        """최신 데이터 조회"""
        return self.latest_snapshot
    
    def get_historical_data(self, minutes: int = 60) -> List[DataSnapshot]:
        """기간별 이력 데이터 조회"""
        cutoff_time = datetime.now() - timedelta(minutes=minutes)
        return [snapshot for snapshot in self.data_history 
                if snapshot.timestamp >= cutoff_time]
    
    def get_kpi_trend(self, kpi_name: str, minutes: int = 30) -> List[Tuple[datetime, float]]:
        """KPI 트렌드 데이터 조회"""
        historical_data = self.get_historical_data(minutes)
        trend_data = []
        
        for snapshot in historical_data:
            if kpi_name in snapshot.kpi_data:
                trend_data.append((snapshot.timestamp, snapshot.kpi_data[kpi_name]))
        
        return trend_data
    
    def export_data(self, filename: Optional[str] = None, format: str = 'json') -> str:
        """데이터 내보내기"""
        if filename is None:
            timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
            filename = f"dashboard_export_{timestamp}.{format}"
        
        export_data = {
            'export_timestamp': datetime.now().isoformat(),
            'latest_snapshot': self.latest_snapshot.to_dict() if self.latest_snapshot else None,
            'history': [snapshot.to_dict() for snapshot in self.data_history[-100:]]  # 최근 100개
        }
        
        if format == 'json':
            with open(filename, 'w', encoding='utf-8') as f:
                json.dump(export_data, f, ensure_ascii=False, indent=2)
        elif format == 'pickle':
            with open(filename, 'wb') as f:
                pickle.dump(export_data, f)
        
        return filename
    
    def import_data(self, filename: str, format: str = 'json'):
        """데이터 가져오기"""
        try:
            if format == 'json':
                with open(filename, 'r', encoding='utf-8') as f:
                    data = json.load(f)
            elif format == 'pickle':
                with open(filename, 'rb') as f:
                    data = pickle.load(f)
            
            # 히스토리 데이터 복원
            if 'history' in data:
                for snapshot_dict in data['history']:
                    snapshot = DataSnapshot.from_dict(snapshot_dict)
                    self.data_history.append(snapshot)
            
            # 최신 데이터 복원
            if 'latest_snapshot' in data and data['latest_snapshot']:
                self.latest_snapshot = DataSnapshot.from_dict(data['latest_snapshot'])
            
            print(f"[DataBridge] 데이터 가져오기 완료: {filename}")
            
        except Exception as e:
            print(f"[DataBridge] 데이터 가져오기 오류: {e}")
    
    def save_cache(self):
        """캐시 저장"""
        if self.latest_snapshot:
            try:
                cache_data = {
                    'latest_snapshot': self.latest_snapshot.to_dict(),
                    'recent_history': [s.to_dict() for s in self.data_history[-50:]]
                }
                with open(self.data_cache_file, 'w', encoding='utf-8') as f:
                    json.dump(cache_data, f, ensure_ascii=False, indent=2)
            except Exception as e:
                print(f"[DataBridge] 캐시 저장 오류: {e}")
    
    def load_cache(self):
        """캐시 로드"""
        if os.path.exists(self.data_cache_file):
            try:
                with open(self.data_cache_file, 'r', encoding='utf-8') as f:
                    cache_data = json.load(f)
                
                if 'latest_snapshot' in cache_data:
                    self.latest_snapshot = DataSnapshot.from_dict(cache_data['latest_snapshot'])
                
                if 'recent_history' in cache_data:
                    for snapshot_dict in cache_data['recent_history']:
                        self.data_history.append(DataSnapshot.from_dict(snapshot_dict))
                
                print("[DataBridge] 캐시 로드 완료")
            except Exception as e:
                print(f"[DataBridge] 캐시 로드 오류: {e}")


class RealTimeDataProvider:
    """실시간 데이터 제공자"""
    
    def __init__(self, data_bridge: DataBridge):
        """실시간 데이터 제공자 초기화"""
        self.data_bridge = data_bridge
        self.websocket_clients = []  # WebSocket 클라이언트들 (향후 확장용)
    
    def get_dashboard_data(self) -> Dict[str, Any]:
        """대시보드용 데이터 제공"""
        latest = self.data_bridge.get_latest_data()
        if not latest:
            return self._get_empty_dashboard_data()
        
        # 트렌드 데이터 추가
        trends = {}
        for kpi_name in ['throughput', 'utilization', 'cycle_time']:
            trend_data = self.data_bridge.get_kpi_trend(kpi_name, 30)
            if trend_data:
                trends[kpi_name] = {
                    'timestamps': [t.isoformat() for t, v in trend_data],
                    'values': [v for t, v in trend_data]
                }
        
        return {
            'timestamp': latest.timestamp.isoformat(),
            'kpi': latest.kpi_data,
            'resources': latest.resource_data,
            'processes': latest.process_data,
            'alerts': latest.alerts,
            'simulation_time': latest.simulation_time,
            'trends': trends,
            'summary': self._generate_summary(latest)
        }
    
    def _get_empty_dashboard_data(self) -> Dict[str, Any]:
        """빈 대시보드 데이터"""
        return {
            'timestamp': datetime.now().isoformat(),
            'kpi': {},
            'resources': {},
            'processes': {},
            'alerts': [],
            'simulation_time': 0,
            'trends': {},
            'summary': {
                'status': 'No Data',
                'total_resources': 0,
                'active_alerts': 0
            }
        }
    
    def _generate_summary(self, snapshot: DataSnapshot) -> Dict[str, Any]:
        """요약 정보 생성"""
        kpi_data = snapshot.kpi_data
        resource_data = snapshot.resource_data
        alerts = snapshot.alerts
        
        # 리소스 상태 요약
        running_resources = sum(1 for r in resource_data.values() 
                               if r.get('status') == 'running')
        
        # 알림 레벨 요약
        alert_counts = {}
        for alert in alerts:
            level = alert.get('level', 'info')
            alert_counts[level] = alert_counts.get(level, 0) + 1
        
        # 전체 상태 결정
        if alert_counts.get('critical', 0) > 0:
            overall_status = 'Critical'
        elif alert_counts.get('error', 0) > 0:
            overall_status = 'Error'
        elif alert_counts.get('warning', 0) > 0:
            overall_status = 'Warning'
        else:
            overall_status = 'Normal'
        
        return {
            'status': overall_status,
            'total_resources': len(resource_data),
            'running_resources': running_resources,
            'utilization_avg': kpi_data.get('utilization', 0),
            'throughput_current': kpi_data.get('throughput', 0),
            'active_alerts': len(alerts),
            'alert_breakdown': alert_counts
        }


# 전역 데이터 브릿지 인스턴스 (싱글톤 패턴)
_global_data_bridge: Optional[DataBridge] = None

def get_data_bridge() -> DataBridge:
    """전역 데이터 브릿지 인스턴스 반환"""
    global _global_data_bridge
    if _global_data_bridge is None:
        _global_data_bridge = DataBridge()
    return _global_data_bridge

def initialize_real_time_system(stats_manager: Optional[CentralizedStatisticsManager] = None,
                               update_interval: float = 1.0) -> DataBridge:
    """실시간 시스템 초기화"""
    bridge = get_data_bridge()
    bridge.update_interval = update_interval
    
    if stats_manager:
        bridge.connect_simulation(stats_manager)
    
    bridge.load_cache()  # 이전 세션 데이터 로드
    bridge.start_monitoring()
    
    return bridge
