"""
대시보드 위젯 컴포넌트들

다양한 차트와 위젯들을 생성하고 관리하는 컴포넌트 클래스들을 제공합니다.
"""

import matplotlib.pyplot as plt
import numpy as np
from typing import Dict, List, Any, Optional, Union, Tuple
import pandas as pd
from datetime import datetime


class BaseComponent:
    """기본 컴포넌트 클래스"""
    
    def __init__(self, title: str = "", size: Tuple[int, int] = (10, 6)):
        """
        기본 컴포넌트 초기화
        
        Args:
            title: 컴포넌트 제목
            size: 컴포넌트 크기 (width, height)
        """
        self.title = title
        self.size = size
        self.data = None
        self.config = {}
        
    def set_data(self, data: Any):
        """데이터 설정"""
        self.data = data
        
    def set_config(self, **kwargs):
        """설정 업데이트"""
        self.config.update(kwargs)
        
    def render(self):
        """컴포넌트 렌더링 (하위 클래스에서 구현)"""
        raise NotImplementedError


class KPICard(BaseComponent):
    """KPI 카드 위젯"""
    
    def __init__(self, title: str, value: Union[int, float], 
                 unit: str = "", delta: Optional[float] = None,
                 delta_unit: str = "", color: str = "blue"):
        """
        KPI 카드 초기화
        
        Args:
            title: KPI 제목
            value: KPI 값
            unit: 단위
            delta: 변화량
            delta_unit: 변화량 단위
            color: 카드 색상
        """
        super().__init__(title)
        self.value = value
        self.unit = unit
        self.delta = delta
        self.delta_unit = delta_unit
        self.color = color
        
    def render(self, ax=None):
        """KPI 카드 렌더링"""
        if ax is None:
            fig, ax = plt.subplots(figsize=(4, 2))
        
        # 배경 설정
        ax.set_xlim(0, 10)
        ax.set_ylim(0, 10)
        ax.axis('off')
        
        # 카드 배경
        from matplotlib.patches import Rectangle
        rect = Rectangle((0.5, 2), 9, 6, linewidth=2, 
                        edgecolor=self.color, facecolor='lightgray', alpha=0.3)
        ax.add_patch(rect)
        
        # 제목
        ax.text(5, 7, self.title, ha='center', va='center', 
               fontsize=12, fontweight='bold')
        
        # 값
        value_text = f"{self.value:.1f}{self.unit}" if isinstance(self.value, float) else f"{self.value}{self.unit}"
        ax.text(5, 5, value_text, ha='center', va='center', 
               fontsize=16, fontweight='bold', color=self.color)
        
        # 변화량
        if self.delta is not None:
            delta_color = 'green' if self.delta >= 0 else 'red'
            delta_symbol = '↑' if self.delta >= 0 else '↓'
            delta_text = f"{delta_symbol} {abs(self.delta):.1f}{self.delta_unit}"
            ax.text(5, 3, delta_text, ha='center', va='center', 
                   fontsize=10, color=delta_color)
        
        plt.tight_layout()
        return ax


class GaugeWidget(BaseComponent):
    """게이지 위젯"""
    
    def __init__(self, title: str, value: float, max_value: float = 100,
                 thresholds: List[Tuple[float, str]] = None):
        """
        게이지 위젯 초기화
        
        Args:
            title: 게이지 제목
            value: 현재 값
            max_value: 최대 값
            thresholds: 임계값과 색상 [(임계값, 색상), ...]
        """
        super().__init__(title, (8, 6))
        self.value = value
        self.max_value = max_value
        self.thresholds = thresholds or [(0.3, 'red'), (0.7, 'yellow'), (1.0, 'green')]
        
    def render(self, ax=None):
        """게이지 렌더링"""
        if ax is None:
            fig, ax = plt.subplots(figsize=self.size, subplot_kw={'projection': 'polar'})
        
        # 게이지 설정
        theta = np.linspace(0, np.pi, 100)
        
        # 배경 반원
        ax.fill_between(theta, 0, 1, alpha=0.2, color='lightgray')
        
        # 값에 따른 각도
        value_ratio = min(self.value / self.max_value, 1.0)
        value_angle = value_ratio * np.pi
        
        # 색상 구간
        prev_threshold = 0
        for threshold, color in self.thresholds:
            zone_start = prev_threshold * np.pi
            zone_end = threshold * np.pi
            zone_theta = np.linspace(zone_start, zone_end, 50)
            ax.fill_between(zone_theta, 0, 1, alpha=0.6, color=color)
            prev_threshold = threshold
        
        # 바늘
        ax.plot([value_angle, value_angle], [0, 0.9], color='black', linewidth=3)
        ax.plot(value_angle, 0.9, 'ko', markersize=8)
        
        # 설정
        ax.set_ylim(0, 1)
        ax.set_theta_zero_location('W')
        ax.set_theta_direction(1)
        ax.set_title(self.title, fontsize=14, fontweight='bold', pad=20)
        ax.set_rgrids([])
        
        # 값 표시
        plt.figtext(0.5, 0.25, f'{self.value:.1f}', ha='center', va='center',
                   fontsize=20, fontweight='bold')
        plt.figtext(0.5, 0.15, f'/ {self.max_value}', ha='center', va='center',
                   fontsize=12, alpha=0.7)
        
        return ax


class TimeSeriesChart(BaseComponent):
    """시계열 차트 위젯"""
    
    def __init__(self, title: str, time_data: List, value_data: Dict[str, List],
                 x_label: str = "Time", y_label: str = "Value"):
        """
        시계열 차트 초기화
        
        Args:
            title: 차트 제목
            time_data: 시간 데이터
            value_data: 값 데이터 {라벨: 값_리스트}
            x_label: X축 레이블
            y_label: Y축 레이블
        """
        super().__init__(title, (12, 8))
        self.time_data = time_data
        self.value_data = value_data
        self.x_label = x_label
        self.y_label = y_label
        
    def render(self, ax=None):
        """시계열 차트 렌더링"""
        if ax is None:
            fig, ax = plt.subplots(figsize=self.size)
        
        colors = ['blue', 'red', 'green', 'orange', 'purple']
        
        for i, (label, values) in enumerate(self.value_data.items()):
            color = colors[i % len(colors)]
            ax.plot(self.time_data, values, label=label, color=color, 
                   linewidth=2, marker='o', markersize=3)
        
        ax.set_title(self.title, fontsize=16, fontweight='bold')
        ax.set_xlabel(self.x_label)
        ax.set_ylabel(self.y_label)
        ax.grid(True, alpha=0.3)
        ax.legend()
        
        plt.tight_layout()
        return ax


class BarChartWidget(BaseComponent):
    """막대 차트 위젯"""
    
    def __init__(self, title: str, categories: List[str], values: List[float],
                 x_label: str = "Categories", y_label: str = "Values",
                 horizontal: bool = False):
        """
        막대 차트 위젯 초기화
        
        Args:
            title: 차트 제목
            categories: 카테고리 리스트
            values: 값 리스트
            x_label: X축 레이블
            y_label: Y축 레이블
            horizontal: 수평 막대 차트 여부
        """
        super().__init__(title, (10, 6))
        self.categories = categories
        self.values = values
        self.x_label = x_label
        self.y_label = y_label
        self.horizontal = horizontal
        
    def render(self, ax=None):
        """막대 차트 렌더링"""
        if ax is None:
            fig, ax = plt.subplots(figsize=self.size)
        
        if self.horizontal:
            bars = ax.barh(self.categories, self.values, color='skyblue', 
                          alpha=0.8, edgecolor='black')
            ax.set_xlabel(self.y_label)
            ax.set_ylabel(self.x_label)
        else:
            bars = ax.bar(self.categories, self.values, color='skyblue', 
                         alpha=0.8, edgecolor='black')
            ax.set_xlabel(self.x_label)
            ax.set_ylabel(self.y_label)
            plt.xticks(rotation=45, ha='right')
        
        # 값 표시
        for bar, value in zip(bars, self.values):
            if self.horizontal:
                ax.text(value + max(self.values) * 0.01, bar.get_y() + bar.get_height()/2,
                       f'{value:.1f}', va='center')
            else:
                ax.text(bar.get_x() + bar.get_width()/2, bar.get_height() + max(self.values) * 0.01,
                       f'{value:.1f}', ha='center')
        
        ax.set_title(self.title, fontsize=14, fontweight='bold')
        ax.grid(True, alpha=0.3, axis='y' if not self.horizontal else 'x')
        plt.tight_layout()
        return ax


class PieChartWidget(BaseComponent):
    """원형 차트 위젯"""
    
    def __init__(self, title: str, labels: List[str], sizes: List[float],
                 colors: List[str] = None, explode: List[float] = None):
        """
        원형 차트 위젯 초기화
        
        Args:
            title: 차트 제목
            labels: 라벨 리스트
            sizes: 크기 리스트
            colors: 색상 리스트
            explode: 분리할 섹션 리스트
        """
        super().__init__(title, (8, 8))
        self.labels = labels
        self.sizes = sizes
        self.colors = colors or ['#ff9999', '#66b3ff', '#99ff99', '#ffcc99', '#ff99cc']
        self.explode = explode
        
    def render(self, ax=None):
        """원형 차트 렌더링"""
        if ax is None:
            fig, ax = plt.subplots(figsize=self.size)
        
        wedges, texts, autotexts = ax.pie(self.sizes, explode=self.explode, 
                                         labels=self.labels, colors=self.colors,
                                         autopct='%1.1f%%', shadow=True, startangle=90)
        
        # 텍스트 스타일
        for autotext in autotexts:
            autotext.set_color('white')
            autotext.set_fontweight('bold')
        
        ax.set_title(self.title, fontsize=14, fontweight='bold')
        plt.tight_layout()
        return ax


class DashboardGrid:
    """대시보드 그리드 레이아웃 관리자"""
    
    def __init__(self, rows: int = 2, cols: int = 2):
        """
        그리드 레이아웃 초기화
        
        Args:
            rows: 행 수
            cols: 열 수
        """
        self.rows = rows
        self.cols = cols
        self.components = {}
        self.fig = None
        
    def add_component(self, component: BaseComponent, row: int, col: int, 
                     rowspan: int = 1, colspan: int = 1):
        """
        컴포넌트를 그리드에 추가
        
        Args:
            component: 추가할 컴포넌트
            row: 행 위치
            col: 열 위치
            rowspan: 행 스팬
            colspan: 열 스팬
        """
        self.components[(row, col)] = {
            'component': component,
            'rowspan': rowspan,
            'colspan': colspan
        }
        
    def render(self, figsize: Tuple[int, int] = (16, 12)):
        """전체 그리드 렌더링"""
        self.fig, axes = plt.subplots(self.rows, self.cols, figsize=figsize)
        
        # 단일 서브플롯인 경우 배열로 변환
        if self.rows == 1 and self.cols == 1:
            axes = [[axes]]
        elif self.rows == 1 or self.cols == 1:
            axes = axes.reshape(self.rows, self.cols)
        
        for (row, col), component_info in self.components.items():
            component = component_info['component']
            ax = axes[row][col]
            component.render(ax)
        
        plt.tight_layout()
        return self.fig
        
    def save(self, filename: str):
        """그리드를 이미지로 저장"""
        if self.fig:
            self.fig.savefig(filename, dpi=300, bbox_inches='tight')
        else:
            print("렌더링된 그리드가 없습니다. 먼저 render()를 호출하세요.")


# 사용 예제를 위한 팩토리 함수들
def create_kpi_dashboard(kpi_data: Dict[str, Any]) -> DashboardGrid:
    """KPI 대시보드 생성"""
    grid = DashboardGrid(2, 3)
    
    # KPI 카드들
    grid.add_component(
        KPICard("총 처리량", kpi_data.get('throughput', 0), "units"),
        0, 0
    )
    grid.add_component(
        KPICard("사용률", kpi_data.get('utilization', 0), "%"),
        0, 1
    )
    grid.add_component(
        KPICard("활성 리소스", kpi_data.get('active_resources', 0)),
        0, 2
    )
    
    # 차트들
    if 'resource_utilization' in kpi_data:
        resource_data = kpi_data['resource_utilization']
        grid.add_component(
            BarChartWidget("리소스 사용률", 
                          list(resource_data.keys()),
                          list(resource_data.values())),
            1, 0, colspan=2
        )
    
    return grid
