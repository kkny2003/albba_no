"""
대시보드 레이아웃 관리

다양한 레이아웃 템플릿과 구성을 제공합니다.
"""

from typing import Dict, List, Any, Optional, Tuple
from enum import Enum
import matplotlib.pyplot as plt
from matplotlib.gridspec import GridSpec

from .components import (
    BaseComponent, KPICard, GaugeWidget, TimeSeriesChart,
    BarChartWidget, PieChartWidget, DashboardGrid
)


class LayoutType(Enum):
    """레이아웃 타입"""
    GRID = "grid"
    DASHBOARD = "dashboard"
    REPORT = "report"
    MONITORING = "monitoring"


class DashboardLayout:
    """대시보드 레이아웃 관리자"""
    
    def __init__(self, layout_type: LayoutType = LayoutType.DASHBOARD):
        """
        레이아웃 관리자 초기화
        
        Args:
            layout_type: 레이아웃 타입
        """
        self.layout_type = layout_type
        self.components = []
        self.figure = None
        self.grid_spec = None
        
    def create_manufacturing_dashboard(self, data: Dict[str, Any]) -> plt.Figure:
        """
        제조 모니터링 대시보드 생성
        
        Args:
            data: 대시보드 데이터
            
        Returns:
            matplotlib Figure 객체
        """
        # 그리드 스펙 설정 (3x4 레이아웃)
        fig = plt.figure(figsize=(20, 15))
        gs = GridSpec(4, 6, figure=fig, hspace=0.3, wspace=0.3)
        
        # KPI 카드 영역 (상단)
        self._create_kpi_section(fig, gs, data)
        
        # 주요 차트 영역 (중간)
        self._create_main_charts(fig, gs, data)
        
        # 상세 분석 영역 (하단)
        self._create_detail_charts(fig, gs, data)
        
        # 제목 추가
        fig.suptitle('🏭 제조 시뮬레이션 실시간 대시보드', 
                    fontsize=20, fontweight='bold', y=0.98)
        
        self.figure = fig
        return fig
    
    def _create_kpi_section(self, fig: plt.Figure, gs: GridSpec, data: Dict[str, Any]):
        """KPI 섹션 생성"""
        kpi_data = data.get('kpi', {})
        
        # KPI 카드들 (첫 번째 행)
        kpi_positions = [(0, 0), (0, 1), (0, 2), (0, 3), (0, 4), (0, 5)]
        kpi_items = [
            ("총 처리량", kpi_data.get('throughput', 0), "units", "blue"),
            ("전체 사용률", kpi_data.get('utilization', 0.75), "%", "green"),
            ("활성 리소스", kpi_data.get('active_resources', 8), "", "orange"),
            ("처리 시간", kpi_data.get('cycle_time', 45.2), "min", "purple"),
            ("품질 점수", kpi_data.get('quality_score', 95.5), "%", "red"),
            ("시뮬레이션 시간", kpi_data.get('sim_time', 1440), "min", "gray")
        ]
        
        for i, ((row, col), (title, value, unit, color)) in enumerate(zip(kpi_positions, kpi_items)):
            if i < len(kpi_items):
                ax = fig.add_subplot(gs[row, col])
                self._create_kpi_card(ax, title, value, unit, color)
    
    def _create_main_charts(self, fig: plt.Figure, gs: GridSpec, data: Dict[str, Any]):
        """주요 차트 섹션 생성"""
        # 리소스 사용률 막대 차트 (왼쪽 상단)
        ax1 = fig.add_subplot(gs[1, :3])
        self._create_resource_utilization_chart(ax1, data.get('resource_utilization', {}))
        
        # 전체 사용률 게이지 (오른쪽 상단)
        ax2 = fig.add_subplot(gs[1, 3:], projection='polar')
        self._create_utilization_gauge(ax2, data.get('kpi', {}).get('utilization', 0.75))
        
        # 생산량 시계열 (두 번째 행 전체)
        ax3 = fig.add_subplot(gs[2, :])
        self._create_production_timeline(ax3, data.get('timeline', {}))
    
    def _create_detail_charts(self, fig: plt.Figure, gs: GridSpec, data: Dict[str, Any]):
        """상세 분석 섹션 생성"""
        # 리소스 타입별 분포 (원형 차트)
        ax1 = fig.add_subplot(gs[3, :2])
        self._create_resource_distribution_pie(ax1, data.get('resource_types', {}))
        
        # 처리 시간 히스토그램
        ax2 = fig.add_subplot(gs[3, 2:4])
        self._create_processing_time_histogram(ax2, data.get('processing_times', []))
        
        # 품질 트렌드
        ax3 = fig.add_subplot(gs[3, 4:])
        self._create_quality_trend(ax3, data.get('quality_trend', {}))
    
    def _create_kpi_card(self, ax: plt.Axes, title: str, value: float, 
                        unit: str, color: str):
        """KPI 카드 생성"""
        ax.set_xlim(0, 10)
        ax.set_ylim(0, 10)
        ax.axis('off')
        
        # 카드 배경
        from matplotlib.patches import Rectangle
        rect = Rectangle((0.5, 1), 9, 8, linewidth=2, 
                        edgecolor=color, facecolor=color, alpha=0.1)
        ax.add_patch(rect)
        
        # 제목
        ax.text(5, 7.5, title, ha='center', va='center', 
               fontsize=10, fontweight='bold')
        
        # 값
        if unit == "%":
            value_text = f"{value:.1f}%"
        elif isinstance(value, float):
            value_text = f"{value:.1f}{unit}"
        else:
            value_text = f"{value}{unit}"
            
        ax.text(5, 5, value_text, ha='center', va='center', 
               fontsize=14, fontweight='bold', color=color)
        
        # 아이콘 영역 (간단한 사각형으로 대체)
        icon_rect = Rectangle((1, 2), 2, 2, linewidth=1, 
                            edgecolor=color, facecolor=color, alpha=0.3)
        ax.add_patch(icon_rect)
    
    def _create_resource_utilization_chart(self, ax: plt.Axes, 
                                         resource_data: Dict[str, float]):
        """리소스 사용률 막대 차트"""
        if not resource_data:
            # 샘플 데이터 생성
            resource_data = {
                f'Machine_{i}': 0.6 + (i * 0.05) 
                for i in range(1, 8)
            }
        
        resources = list(resource_data.keys())
        utilizations = [v * 100 for v in resource_data.values()]
        
        bars = ax.bar(resources, utilizations, color='skyblue', 
                     alpha=0.8, edgecolor='navy')
        
        # 값 표시
        for bar, util in zip(bars, utilizations):
            ax.text(bar.get_x() + bar.get_width()/2, bar.get_height() + 1,
                   f'{util:.1f}%', ha='center', va='bottom', fontweight='bold')
        
        ax.set_title('리소스 사용률', fontsize=14, fontweight='bold')
        ax.set_ylabel('사용률 (%)')
        ax.set_ylim(0, 100)
        ax.grid(True, alpha=0.3, axis='y')
        plt.setp(ax.get_xticklabels(), rotation=45, ha='right')
    
    def _create_utilization_gauge(self, ax: plt.Axes, utilization: float):
        """사용률 게이지 차트"""
        import numpy as np
        
        # 반원 게이지
        theta = np.linspace(0, np.pi, 100)
        
        # 배경
        ax.fill_between(theta, 0, 1, alpha=0.2, color='lightgray')
        
        # 색상 구간
        zones = [(0.3, 'red'), (0.7, 'yellow'), (1.0, 'green')]
        prev = 0
        for threshold, color in zones:
            zone_start = prev * np.pi
            zone_end = threshold * np.pi
            zone_theta = np.linspace(zone_start, zone_end, 50)
            ax.fill_between(zone_theta, 0, 1, alpha=0.6, color=color)
            prev = threshold
        
        # 바늘
        value_angle = utilization * np.pi
        ax.plot([value_angle, value_angle], [0, 0.9], color='black', linewidth=4)
        ax.plot(value_angle, 0.9, 'ko', markersize=10)
        
        ax.set_ylim(0, 1)
        ax.set_theta_zero_location('W')
        ax.set_theta_direction(1)
        ax.set_title('전체 사용률', fontsize=14, fontweight='bold', pad=20)
        ax.set_rgrids([])
        
        # 값 표시
        plt.figtext(0.75, 0.35, f'{utilization:.1%}', ha='center', va='center',
                   fontsize=18, fontweight='bold')
    
    def _create_production_timeline(self, ax: plt.Axes, timeline_data: Dict[str, List]):
        """생산량 시계열 차트"""
        if not timeline_data:
            # 샘플 데이터 생성
            import numpy as np
            time_points = list(range(0, 100, 5))
            timeline_data = {
                '생산량': [80 + 20 * np.sin(t/10) + np.random.normal(0, 5) for t in time_points],
                '목표': [100] * len(time_points)
            }
            timeline_data['time'] = time_points
        
        colors = ['blue', 'red', 'green', 'orange']
        for i, (label, values) in enumerate(timeline_data.items()):
            if label != 'time':
                ax.plot(timeline_data.get('time', range(len(values))), values,
                       label=label, color=colors[i % len(colors)], 
                       linewidth=2, marker='o', markersize=3)
        
        ax.set_title('생산량 시계열 분석', fontsize=14, fontweight='bold')
        ax.set_xlabel('시뮬레이션 시간')
        ax.set_ylabel('생산량 (units/hour)')
        ax.grid(True, alpha=0.3)
        ax.legend()
    
    def _create_resource_distribution_pie(self, ax: plt.Axes, 
                                        resource_types: Dict[str, int]):
        """리소스 타입별 분포 원형 차트"""
        if not resource_types:
            resource_types = {
                '가공기계': 8,
                '조립라인': 4,
                '검사장비': 3,
                '운송장비': 5
            }
        
        labels = list(resource_types.keys())
        sizes = list(resource_types.values())
        colors = ['#ff9999', '#66b3ff', '#99ff99', '#ffcc99']
        
        wedges, texts, autotexts = ax.pie(sizes, labels=labels, colors=colors,
                                         autopct='%1.1f%%', startangle=90)
        
        for autotext in autotexts:
            autotext.set_color('white')
            autotext.set_fontweight('bold')
        
        ax.set_title('리소스 타입별 분포', fontsize=14, fontweight='bold')
    
    def _create_processing_time_histogram(self, ax: plt.Axes, 
                                        processing_times: List[float]):
        """처리 시간 히스토그램"""
        if not processing_times:
            import numpy as np
            processing_times = np.random.normal(45, 10, 100)
        
        ax.hist(processing_times, bins=20, alpha=0.7, color='lightcoral', 
               edgecolor='black')
        ax.set_title('처리 시간 분포', fontsize=14, fontweight='bold')
        ax.set_xlabel('처리 시간 (분)')
        ax.set_ylabel('빈도')
        ax.grid(True, alpha=0.3, axis='y')
        
        # 평균선 표시
        mean_time = sum(processing_times) / len(processing_times)
        ax.axvline(mean_time, color='red', linestyle='--', linewidth=2,
                  label=f'평균: {mean_time:.1f}분')
        ax.legend()
    
    def _create_quality_trend(self, ax: plt.Axes, quality_data: Dict[str, List]):
        """품질 트렌드 차트"""
        if not quality_data:
            import numpy as np
            time_points = list(range(0, 50, 2))
            quality_data = {
                'time': time_points,
                'quality_score': [95 + 3 * np.sin(t/5) + np.random.normal(0, 1) 
                                for t in time_points]
            }
        
        ax.plot(quality_data.get('time', []), quality_data.get('quality_score', []),
               color='green', linewidth=2, marker='o', markersize=4)
        
        # 목표선
        ax.axhline(95, color='red', linestyle='--', alpha=0.7, label='목표 (95%)')
        
        ax.set_title('품질 점수 트렌드', fontsize=14, fontweight='bold')
        ax.set_xlabel('시뮬레이션 시간')
        ax.set_ylabel('품질 점수 (%)')
        ax.set_ylim(85, 100)
        ax.grid(True, alpha=0.3)
        ax.legend()
    
    def create_monitoring_layout(self, data: Dict[str, Any]) -> plt.Figure:
        """실시간 모니터링 레이아웃 생성"""
        fig = plt.figure(figsize=(16, 12))
        gs = GridSpec(3, 4, figure=fig, hspace=0.3, wspace=0.3)
        
        # 상태 표시기들 (상단)
        for i in range(4):
            ax = fig.add_subplot(gs[0, i])
            status_data = data.get('status', {})
            self._create_status_indicator(ax, f"Status {i+1}", 
                                        status_data.get(f'status_{i+1}', 'OK'))
        
        # 실시간 차트들 (중간 및 하단)
        ax1 = fig.add_subplot(gs[1, :2])
        self._create_realtime_chart(ax1, data.get('realtime', {}))
        
        ax2 = fig.add_subplot(gs[1, 2:])
        self._create_alert_panel(ax2, data.get('alerts', []))
        
        ax3 = fig.add_subplot(gs[2, :])
        self._create_system_overview(ax3, data.get('system', {}))
        
        fig.suptitle('🔍 실시간 시스템 모니터링', fontsize=18, fontweight='bold')
        return fig
    
    def _create_status_indicator(self, ax: plt.Axes, title: str, status: str):
        """상태 표시기 생성"""
        ax.set_xlim(0, 10)
        ax.set_ylim(0, 10)
        ax.axis('off')
        
        # 상태에 따른 색상
        color_map = {'OK': 'green', 'WARNING': 'yellow', 'ERROR': 'red', 'OFFLINE': 'gray'}
        color = color_map.get(status, 'gray')
        
        # 상태 원
        circle = plt.Circle((5, 6), 2, color=color, alpha=0.7)
        ax.add_patch(circle)
        
        ax.text(5, 3, title, ha='center', va='center', fontsize=10, fontweight='bold')
        ax.text(5, 1, status, ha='center', va='center', fontsize=8, color=color)
    
    def _create_realtime_chart(self, ax: plt.Axes, realtime_data: Dict):
        """실시간 차트 생성"""
        # 샘플 실시간 데이터
        import numpy as np
        if not realtime_data:
            time_points = list(range(-50, 0))
            realtime_data = {
                'time': time_points,
                'throughput': [100 + 10 * np.sin(t/5) + np.random.normal(0, 2) for t in time_points]
            }
        
        ax.plot(realtime_data.get('time', []), realtime_data.get('throughput', []),
               color='blue', linewidth=2)
        ax.set_title('실시간 처리량', fontsize=12, fontweight='bold')
        ax.set_ylabel('처리량 (units/min)')
        ax.grid(True, alpha=0.3)
    
    def _create_alert_panel(self, ax: plt.Axes, alerts: List[str]):
        """알림 패널 생성"""
        ax.set_xlim(0, 10)
        ax.set_ylim(0, 10)
        ax.axis('off')
        
        if not alerts:
            alerts = ["시스템 정상 운영 중", "모든 리소스 활성화", "품질 기준 충족"]
        
        ax.text(5, 9, '알림', ha='center', va='top', fontsize=12, fontweight='bold')
        
        for i, alert in enumerate(alerts[:5]):  # 최대 5개 알림
            y_pos = 8 - i * 1.5
            ax.text(0.5, y_pos, f"• {alert}", ha='left', va='top', fontsize=9)
    
    def _create_system_overview(self, ax: plt.Axes, system_data: Dict):
        """시스템 개요 생성"""
        # 시스템 아키텍처나 플로우차트 같은 개요
        ax.set_xlim(0, 10)
        ax.set_ylim(0, 5)
        ax.axis('off')
        
        # 단순한 플로우 다이어그램
        boxes = [
            (1, 2.5, "입력"),
            (3, 2.5, "처리"),
            (5, 2.5, "검사"),
            (7, 2.5, "출력"),
            (9, 2.5, "완료")
        ]
        
        for x, y, label in boxes:
            from matplotlib.patches import Rectangle
            rect = Rectangle((x-0.4, y-0.3), 0.8, 0.6, 
                           facecolor='lightblue', edgecolor='blue')
            ax.add_patch(rect)
            ax.text(x, y, label, ha='center', va='center', fontsize=9)
        
        # 화살표
        for i in range(len(boxes)-1):
            x1, y1 = boxes[i][0] + 0.4, boxes[i][1]
            x2, y2 = boxes[i+1][0] - 0.4, boxes[i+1][1]
            ax.annotate('', xy=(x2, y2), xytext=(x1, y1),
                       arrowprops=dict(arrowstyle='->', color='blue'))
        
        ax.set_title('시스템 프로세스 플로우', fontsize=12, fontweight='bold')
    
    def save_layout(self, filename: str):
        """레이아웃을 파일로 저장"""
        if self.figure:
            self.figure.savefig(filename, dpi=300, bbox_inches='tight')
            print(f"레이아웃이 저장되었습니다: {filename}")
        else:
            print("저장할 레이아웃이 없습니다.")


# 사용 예제
def create_sample_dashboard():
    """샘플 대시보드 생성"""
    import numpy as np
    
    # 샘플 데이터 생성
    sample_data = {
        'kpi': {
            'throughput': 95.5,
            'utilization': 0.82,
            'active_resources': 12,
            'cycle_time': 42.3,
            'quality_score': 96.8,
            'sim_time': 1440
        },
        'resource_utilization': {
            f'Machine_{i}': 0.65 + i * 0.05 for i in range(1, 8)
        },
        'timeline': {
            'time': list(range(0, 100, 5)),
            'production': [80 + 20 * np.sin(t/10) + np.random.normal(0, 3) 
                          for t in range(0, 100, 5)]
        },
        'resource_types': {
            '가공기계': 8, '조립라인': 4, '검사장비': 3, '운송장비': 5
        }
    }
    
    layout = DashboardLayout()
    fig = layout.create_manufacturing_dashboard(sample_data)
    return layout, fig
