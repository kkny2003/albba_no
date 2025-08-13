"""
KPI 위젯 시스템

실시간 KPI 모니터링과 알림 기능을 제공하는 고급 위젯들을 구현합니다.
"""

import numpy as np
import matplotlib.pyplot as plt
from typing import Dict, List, Any, Optional, Tuple, Union
from datetime import datetime, timedelta
from dataclasses import dataclass
from enum import Enum
import json


class AlertLevel(Enum):
    """알림 레벨"""
    SUCCESS = "success"
    INFO = "info"
    WARNING = "warning"
    ERROR = "error"
    CRITICAL = "critical"


@dataclass
class KPIThreshold:
    """KPI 임계값 설정"""
    warning_min: Optional[float] = None
    warning_max: Optional[float] = None
    critical_min: Optional[float] = None
    critical_max: Optional[float] = None
    target: Optional[float] = None


@dataclass
class KPIData:
    """KPI 데이터"""
    name: str
    value: float
    unit: str = ""
    timestamp: datetime = None
    threshold: Optional[KPIThreshold] = None
    
    def __post_init__(self):
        if self.timestamp is None:
            self.timestamp = datetime.now()
    
    def get_status(self) -> AlertLevel:
        """현재 값에 따른 상태 반환"""
        if not self.threshold:
            return AlertLevel.INFO
        
        # Critical 체크
        if self.threshold.critical_min is not None and self.value < self.threshold.critical_min:
            return AlertLevel.CRITICAL
        if self.threshold.critical_max is not None and self.value > self.threshold.critical_max:
            return AlertLevel.CRITICAL
        
        # Warning 체크
        if self.threshold.warning_min is not None and self.value < self.threshold.warning_min:
            return AlertLevel.WARNING
        if self.threshold.warning_max is not None and self.value > self.threshold.warning_max:
            return AlertLevel.WARNING
        
        # 목표값 체크
        if self.threshold.target is not None:
            if abs(self.value - self.threshold.target) / self.threshold.target < 0.05:  # 5% 이내
                return AlertLevel.SUCCESS
        
        return AlertLevel.INFO


class KPIWidget:
    """고급 KPI 위젯"""
    
    def __init__(self, kpi_data: KPIData, size: Tuple[int, int] = (6, 4)):
        """
        KPI 위젯 초기화
        
        Args:
            kpi_data: KPI 데이터
            size: 위젯 크기
        """
        self.kpi_data = kpi_data
        self.size = size
        self.history = []  # 값 이력
        
    def add_value(self, value: float, timestamp: datetime = None):
        """새로운 값 추가"""
        if timestamp is None:
            timestamp = datetime.now()
        
        self.kpi_data.value = value
        self.kpi_data.timestamp = timestamp
        self.history.append((timestamp, value))
        
        # 최근 100개 값만 유지
        if len(self.history) > 100:
            self.history = self.history[-100:]
    
    def render_card(self, ax: plt.Axes = None):
        """KPI 카드 렌더링"""
        if ax is None:
            fig, ax = plt.subplots(figsize=self.size)
        
        # 상태에 따른 색상 설정
        status = self.kpi_data.get_status()
        color_map = {
            AlertLevel.SUCCESS: '#28a745',
            AlertLevel.INFO: '#17a2b8',
            AlertLevel.WARNING: '#ffc107',
            AlertLevel.ERROR: '#dc3545',
            AlertLevel.CRITICAL: '#6f42c1'
        }
        color = color_map[status]
        
        # 배경 설정
        ax.set_xlim(0, 10)
        ax.set_ylim(0, 10)
        ax.axis('off')
        
        # 카드 배경
        from matplotlib.patches import Rectangle, Circle
        
        # 메인 카드
        card = Rectangle((0.5, 2), 9, 6, linewidth=2, 
                        edgecolor=color, facecolor=color, alpha=0.1)
        ax.add_patch(card)
        
        # 상태 인디케이터 (원형)
        indicator = Circle((8.5, 7), 0.3, color=color, alpha=0.8)
        ax.add_patch(indicator)
        
        # KPI 이름
        ax.text(5, 7.5, self.kpi_data.name, ha='center', va='center',
               fontsize=12, fontweight='bold')
        
        # KPI 값
        value_text = f"{self.kpi_data.value:.1f}{self.kpi_data.unit}"
        ax.text(5, 5.5, value_text, ha='center', va='center',
               fontsize=16, fontweight='bold', color=color)
        
        # 목표값 (있는 경우)
        if self.kpi_data.threshold and self.kpi_data.threshold.target:
            target_text = f"목표: {self.kpi_data.threshold.target:.1f}{self.kpi_data.unit}"
            ax.text(5, 4, target_text, ha='center', va='center',
                   fontsize=10, alpha=0.7)
        
        # 트렌드 표시 (미니 차트)
        if len(self.history) > 1:
            self._draw_mini_trend(ax)
        
        # 상태 텍스트
        status_text = status.value.upper()
        ax.text(8.5, 6.2, status_text, ha='center', va='center',
               fontsize=8, fontweight='bold', color=color)
        
        # 타임스탬프
        time_text = self.kpi_data.timestamp.strftime('%H:%M:%S')
        ax.text(9.5, 2.5, time_text, ha='right', va='bottom',
               fontsize=8, alpha=0.6)
        
        return ax
    
    def _draw_mini_trend(self, ax: plt.Axes):
        """미니 트렌드 차트 그리기"""
        if len(self.history) < 2:
            return
        
        # 최근 10개 값만 사용
        recent_history = self.history[-10:]
        values = [item[1] for item in recent_history]
        
        # 정규화
        min_val, max_val = min(values), max(values)
        if max_val > min_val:
            norm_values = [(v - min_val) / (max_val - min_val) for v in values]
        else:
            norm_values = [0.5] * len(values)
        
        # 미니 차트 위치 (카드 하단)
        x_positions = np.linspace(1, 4, len(norm_values))
        y_positions = [3 + v * 0.8 for v in norm_values]  # 3~3.8 범위
        
        # 선 그리기
        ax.plot(x_positions, y_positions, color='gray', linewidth=1, alpha=0.7)
        
        # 트렌드 방향 표시
        if len(values) >= 2:
            trend = "↗" if values[-1] > values[-2] else "↘" if values[-1] < values[-2] else "→"
            trend_color = "green" if trend == "↗" else "red" if trend == "↘" else "gray"
            ax.text(4.2, 3.4, trend, ha='center', va='center',
                   fontsize=14, color=trend_color, fontweight='bold')
    
    def render_gauge(self, ax: plt.Axes = None):
        """게이지 차트 렌더링"""
        if ax is None:
            fig, ax = plt.subplots(figsize=self.size, subplot_kw={'projection': 'polar'})
        
        # 게이지 범위 설정
        if self.kpi_data.threshold:
            min_val = self.kpi_data.threshold.critical_min or 0
            max_val = self.kpi_data.threshold.critical_max or 100
        else:
            min_val, max_val = 0, 100
        
        # 현재 값의 비율
        if max_val > min_val:
            value_ratio = (self.kpi_data.value - min_val) / (max_val - min_val)
        else:
            value_ratio = 0.5
        value_ratio = max(0, min(1, value_ratio))  # 0-1 범위로 제한
        
        # 게이지 그리기
        theta = np.linspace(0, np.pi, 100)
        
        # 배경
        ax.fill_between(theta, 0, 1, alpha=0.2, color='lightgray')
        
        # 색상 구간
        if self.kpi_data.threshold:
            self._draw_gauge_zones(ax, min_val, max_val)
        
        # 바늘
        needle_angle = value_ratio * np.pi
        ax.plot([needle_angle, needle_angle], [0, 0.9], color='black', linewidth=3)
        ax.plot(needle_angle, 0.9, 'ko', markersize=8)
        
        # 설정
        ax.set_ylim(0, 1)
        ax.set_theta_zero_location('W')
        ax.set_theta_direction(1)
        ax.set_title(f"{self.kpi_data.name}\n{self.kpi_data.value:.1f}{self.kpi_data.unit}",
                    fontsize=12, fontweight='bold', pad=20)
        ax.set_rgrids([])
        
        return ax
    
    def _draw_gauge_zones(self, ax: plt.Axes, min_val: float, max_val: float):
        """게이지 색상 구간 그리기"""
        threshold = self.kpi_data.threshold
        
        zones = []
        if threshold.critical_min is not None:
            zones.append((0, (threshold.critical_min - min_val) / (max_val - min_val), 'red'))
        if threshold.warning_min is not None:
            start = (threshold.critical_min - min_val) / (max_val - min_val) if threshold.critical_min else 0
            end = (threshold.warning_min - min_val) / (max_val - min_val)
            zones.append((start, end, 'orange'))
        
        # 정상 구간
        start = (threshold.warning_min - min_val) / (max_val - min_val) if threshold.warning_min else 0
        end = (threshold.warning_max - min_val) / (max_val - min_val) if threshold.warning_max else 1
        zones.append((start, end, 'green'))
        
        if threshold.warning_max is not None:
            start = (threshold.warning_max - min_val) / (max_val - min_val)
            end = (threshold.critical_max - min_val) / (max_val - min_val) if threshold.critical_max else 1
            zones.append((start, end, 'orange'))
        if threshold.critical_max is not None:
            start = (threshold.critical_max - min_val) / (max_val - min_val)
            zones.append((start, 1, 'red'))
        
        # 구간 그리기
        for start, end, color in zones:
            if start < end:
                zone_theta = np.linspace(start * np.pi, end * np.pi, 50)
                ax.fill_between(zone_theta, 0, 1, alpha=0.6, color=color)


class AlertSystem:
    """알림 시스템"""
    
    def __init__(self, max_alerts: int = 100):
        """알림 시스템 초기화"""
        self.alerts = []
        self.max_alerts = max_alerts
        self.subscribers = []  # 알림 구독자들
    
    def add_alert(self, level: AlertLevel, message: str, 
                 source: str = "System", timestamp: datetime = None):
        """알림 추가"""
        if timestamp is None:
            timestamp = datetime.now()
        
        alert = {
            'level': level,
            'message': message,
            'source': source,
            'timestamp': timestamp,
            'id': len(self.alerts)
        }
        
        self.alerts.append(alert)
        
        # 최대 개수 제한
        if len(self.alerts) > self.max_alerts:
            self.alerts = self.alerts[-self.max_alerts:]
        
        # 구독자들에게 알림
        for subscriber in self.subscribers:
            subscriber(alert)
    
    def get_recent_alerts(self, minutes: int = 60) -> List[Dict]:
        """최근 알림 조회"""
        cutoff_time = datetime.now() - timedelta(minutes=minutes)
        return [alert for alert in self.alerts 
                if alert['timestamp'] >= cutoff_time]
    
    def get_alerts_by_level(self, level: AlertLevel) -> List[Dict]:
        """레벨별 알림 조회"""
        return [alert for alert in self.alerts if alert['level'] == level]
    
    def subscribe(self, callback):
        """알림 구독"""
        self.subscribers.append(callback)
    
    def unsubscribe(self, callback):
        """알림 구독 해제"""
        if callback in self.subscribers:
            self.subscribers.remove(callback)
    
    def render_alert_panel(self, ax: plt.Axes = None, max_display: int = 10):
        """알림 패널 렌더링"""
        if ax is None:
            fig, ax = plt.subplots(figsize=(12, 8))
        
        ax.set_xlim(0, 10)
        ax.set_ylim(0, 10)
        ax.axis('off')
        
        # 제목
        ax.text(5, 9.5, "🚨 시스템 알림", ha='center', va='top',
               fontsize=16, fontweight='bold')
        
        # 최근 알림들
        recent_alerts = self.get_recent_alerts()[-max_display:]
        
        if not recent_alerts:
            ax.text(5, 5, "알림이 없습니다.", ha='center', va='center',
                   fontsize=12, alpha=0.6)
            return ax
        
        # 알림 표시
        y_start = 8.5
        y_step = 0.7
        
        color_map = {
            AlertLevel.SUCCESS: '#28a745',
            AlertLevel.INFO: '#17a2b8',
            AlertLevel.WARNING: '#ffc107',
            AlertLevel.ERROR: '#dc3545',
            AlertLevel.CRITICAL: '#6f42c1'
        }
        
        for i, alert in enumerate(reversed(recent_alerts)):
            y_pos = y_start - i * y_step
            if y_pos < 0.5:
                break
            
            color = color_map[alert['level']]
            
            # 알림 배경
            from matplotlib.patches import Rectangle
            alert_bg = Rectangle((0.5, y_pos - 0.25), 9, 0.5,
                               facecolor=color, alpha=0.1,
                               edgecolor=color, linewidth=1)
            ax.add_patch(alert_bg)
            
            # 시간
            time_str = alert['timestamp'].strftime('%H:%M')
            ax.text(1, y_pos, time_str, ha='left', va='center',
                   fontsize=9, fontweight='bold')
            
            # 레벨
            level_str = alert['level'].value.upper()
            ax.text(2.5, y_pos, level_str, ha='left', va='center',
                   fontsize=9, color=color, fontweight='bold')
            
            # 메시지
            message = alert['message']
            if len(message) > 50:
                message = message[:47] + "..."
            ax.text(4, y_pos, message, ha='left', va='center',
                   fontsize=9)
        
        return ax


class KPIManager:
    """KPI 관리자"""
    
    def __init__(self):
        """KPI 관리자 초기화"""
        self.kpis = {}
        self.alert_system = AlertSystem()
        self.monitoring_active = False
    
    def register_kpi(self, name: str, kpi_data: KPIData):
        """KPI 등록"""
        widget = KPIWidget(kpi_data)
        self.kpis[name] = widget
    
    def update_kpi(self, name: str, value: float, timestamp: datetime = None):
        """KPI 값 업데이트"""
        if name not in self.kpis:
            return
        
        old_value = self.kpis[name].kpi_data.value
        self.kpis[name].add_value(value, timestamp)
        
        # 임계값 체크 및 알림
        self._check_thresholds(name, old_value, value)
    
    def _check_thresholds(self, name: str, old_value: float, new_value: float):
        """임계값 체크 및 알림 생성"""
        kpi = self.kpis[name]
        old_status = KPIData(name, old_value, 
                           threshold=kpi.kpi_data.threshold).get_status()
        new_status = kpi.kpi_data.get_status()
        
        # 상태 변화 체크
        if old_status != new_status:
            if new_status == AlertLevel.CRITICAL:
                self.alert_system.add_alert(
                    AlertLevel.CRITICAL,
                    f"{name}: 임계값 위반 - {new_value:.1f}{kpi.kpi_data.unit}",
                    "KPI Monitor"
                )
            elif new_status == AlertLevel.WARNING:
                self.alert_system.add_alert(
                    AlertLevel.WARNING,
                    f"{name}: 주의 필요 - {new_value:.1f}{kpi.kpi_data.unit}",
                    "KPI Monitor"
                )
            elif new_status == AlertLevel.SUCCESS and old_status in [AlertLevel.WARNING, AlertLevel.CRITICAL]:
                self.alert_system.add_alert(
                    AlertLevel.SUCCESS,
                    f"{name}: 정상 복구 - {new_value:.1f}{kpi.kpi_data.unit}",
                    "KPI Monitor"
                )
    
    def create_dashboard(self, layout: str = "grid") -> plt.Figure:
        """KPI 대시보드 생성"""
        if layout == "grid":
            return self._create_grid_dashboard()
        elif layout == "gauge":
            return self._create_gauge_dashboard()
        else:
            return self._create_mixed_dashboard()
    
    def _create_grid_dashboard(self) -> plt.Figure:
        """그리드 레이아웃 대시보드"""
        n_kpis = len(self.kpis)
        if n_kpis == 0:
            return None
        
        # 그리드 크기 결정
        cols = min(4, n_kpis)
        rows = (n_kpis + cols - 1) // cols
        
        fig, axes = plt.subplots(rows, cols, figsize=(16, 4 * rows))
        if rows == 1 and cols == 1:
            axes = [axes]
        elif rows == 1 or cols == 1:
            axes = axes.flatten()
        else:
            axes = axes.flatten()
        
        # KPI 카드들 렌더링
        for i, (name, kpi_widget) in enumerate(self.kpis.items()):
            if i < len(axes):
                kpi_widget.render_card(axes[i])
        
        # 빈 subplot 숨기기
        for i in range(len(self.kpis), len(axes)):
            axes[i].axis('off')
        
        plt.tight_layout()
        return fig
    
    def _create_gauge_dashboard(self) -> plt.Figure:
        """게이지 레이아웃 대시보드"""
        n_kpis = len(self.kpis)
        if n_kpis == 0:
            return None
        
        cols = min(3, n_kpis)
        rows = (n_kpis + cols - 1) // cols
        
        fig = plt.figure(figsize=(18, 6 * rows))
        
        for i, (name, kpi_widget) in enumerate(self.kpis.items()):
            ax = fig.add_subplot(rows, cols, i + 1, projection='polar')
            kpi_widget.render_gauge(ax)
        
        plt.tight_layout()
        return fig
    
    def _create_mixed_dashboard(self) -> plt.Figure:
        """혼합 레이아웃 대시보드"""
        fig = plt.figure(figsize=(20, 12))
        
        # 상단: KPI 카드들
        n_kpis = len(self.kpis)
        for i, (name, kpi_widget) in enumerate(self.kpis.items()):
            if i < 6:  # 최대 6개 KPI 카드
                ax = plt.subplot2grid((3, 6), (0, i), fig=fig)
                kpi_widget.render_card(ax)
        
        # 하단: 알림 패널
        alert_ax = plt.subplot2grid((3, 6), (1, 0), colspan=6, rowspan=2, fig=fig)
        self.alert_system.render_alert_panel(alert_ax)
        
        plt.tight_layout()
        return fig


# 사용 예제
def create_sample_kpi_system():
    """샘플 KPI 시스템 생성"""
    manager = KPIManager()
    
    # 처리량 KPI
    throughput_threshold = KPIThreshold(
        warning_min=80, warning_max=120,
        critical_min=60, critical_max=150,
        target=100
    )
    throughput_kpi = KPIData("처리량", 95, "units/h", threshold=throughput_threshold)
    manager.register_kpi("throughput", throughput_kpi)
    
    # 사용률 KPI
    utilization_threshold = KPIThreshold(
        warning_min=0.6, warning_max=0.9,
        critical_min=0.4, critical_max=0.95,
        target=0.8
    )
    utilization_kpi = KPIData("사용률", 0.82, "%", threshold=utilization_threshold)
    manager.register_kpi("utilization", utilization_kpi)
    
    # 품질 KPI
    quality_threshold = KPIThreshold(
        warning_min=90, critical_min=85, target=95
    )
    quality_kpi = KPIData("품질 점수", 94.5, "%", threshold=quality_threshold)
    manager.register_kpi("quality", quality_kpi)
    
    return manager
