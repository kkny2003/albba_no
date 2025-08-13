"""
대시보드 관리자 클래스

시뮬레이션 데이터를 실시간으로 수집하고 웹 대시보드에
표시하는 기능을 관리합니다.
"""

import streamlit as st
import pandas as pd
import plotly.graph_objects as go
import plotly.express as px
from plotly.subplots import make_subplots
from typing import Dict, List, Any, Optional, Union
import time
import threading
from datetime import datetime
import json

from src.utils.visualization import VisualizationManager


class DashboardManager:
    """실시간 대시보드 관리 클래스"""
    
    def __init__(self, stats_manager: Optional[Any] = None):
        """
        DashboardManager 초기화
        
        Args:
            stats_manager: 통계 관리자 인스턴스
        """
        self.stats_manager = stats_manager
        self.viz_manager = VisualizationManager()
        self.data_cache = {}
        self.last_update = None
        self.auto_refresh = True
        self.refresh_interval = 5  # 5초마다 갱신
        
    def set_stats_manager(self, stats_manager: Any):
        """통계 관리자 설정"""
        self.stats_manager = stats_manager
        
    def get_kpi_data(self) -> Dict[str, Any]:
        """KPI 데이터 수집"""
        if not self.stats_manager:
            return self._get_sample_kpi_data()
            
        kpi_data = {}
        try:
            # 기본 KPI 수집
            kpi_data['total_throughput'] = self.stats_manager.get_global_metric('throughput')
            kpi_data['overall_utilization'] = self.stats_manager.get_global_metric('utilization')
            kpi_data['active_resources'] = len(self.stats_manager.get_all_resource_ids())
            kpi_data['current_time'] = self.stats_manager.current_time
            
            # 리소스별 사용률
            resource_utilization = {}
            for resource_id in self.stats_manager.get_all_resource_ids():
                utilization = self.stats_manager.get_resource_metric(resource_id, 'utilization')
                if utilization is not None:
                    resource_utilization[resource_id] = utilization
            kpi_data['resource_utilization'] = resource_utilization
            
        except Exception as e:
            st.error(f"KPI 데이터 수집 오류: {e}")
            kpi_data = self._get_sample_kpi_data()
            
        return kpi_data
    
    def _get_sample_kpi_data(self) -> Dict[str, Any]:
        """샘플 KPI 데이터 생성 (통계 관리자가 없을 때)"""
        import random
        
        return {
            'total_throughput': random.randint(80, 120),
            'overall_utilization': random.uniform(0.7, 0.95),
            'active_resources': random.randint(5, 15),
            'current_time': time.time(),
            'resource_utilization': {
                f'Machine_{i}': random.uniform(0.6, 0.9) 
                for i in range(1, 6)
            }
        }
    
    def create_kpi_cards(self, kpi_data: Dict[str, Any]):
        """KPI 카드 위젯 생성"""
        col1, col2, col3, col4 = st.columns(4)
        
        with col1:
            st.metric(
                label="총 처리량",
                value=f"{kpi_data.get('total_throughput', 0):.0f}",
                delta=f"{kpi_data.get('total_throughput', 0) - 100:.0f}"
            )
        
        with col2:
            utilization = kpi_data.get('overall_utilization', 0)
            st.metric(
                label="전체 사용률",
                value=f"{utilization:.1%}",
                delta=f"{(utilization - 0.8):.1%}"
            )
        
        with col3:
            st.metric(
                label="활성 리소스",
                value=f"{kpi_data.get('active_resources', 0):.0f}",
                delta="0"
            )
        
        with col4:
            st.metric(
                label="시뮬레이션 시간",
                value=f"{kpi_data.get('current_time', 0):.1f}",
                delta=None
            )
    
    def create_utilization_chart(self, kpi_data: Dict[str, Any]):
        """리소스 사용률 차트 생성"""
        resource_utilization = kpi_data.get('resource_utilization', {})
        
        if not resource_utilization:
            st.warning("리소스 사용률 데이터가 없습니다.")
            return
        
        # Plotly 막대 차트
        fig = go.Figure(data=[
            go.Bar(
                x=list(resource_utilization.keys()),
                y=[v * 100 for v in resource_utilization.values()],
                marker_color='skyblue',
                text=[f'{v:.1%}' for v in resource_utilization.values()],
                textposition='auto',
            )
        ])
        
        fig.update_layout(
            title="리소스 사용률",
            xaxis_title="리소스",
            yaxis_title="사용률 (%)",
            yaxis=dict(range=[0, 100]),
            height=400
        )
        
        st.plotly_chart(fig, use_container_width=True)
    
    def create_gauge_chart(self, value: float, title: str, max_value: float = 100):
        """게이지 차트 생성"""
        fig = go.Figure(go.Indicator(
            mode = "gauge+number+delta",
            value = value * 100 if value <= 1 else value,
            domain = {'x': [0, 1], 'y': [0, 1]},
            title = {'text': title},
            delta = {'reference': 80},
            gauge = {
                'axis': {'range': [None, max_value]},
                'bar': {'color': "darkblue"},
                'steps': [
                    {'range': [0, 50], 'color': "lightgray"},
                    {'range': [50, 80], 'color': "yellow"},
                    {'range': [80, max_value], 'color': "lightgreen"}
                ],
                'threshold': {
                    'line': {'color': "red", 'width': 4},
                    'thickness': 0.75,
                    'value': 90
                }
            }
        ))
        
        fig.update_layout(height=300)
        return fig
    
    def create_timeline_chart(self, timeline_data: Dict[str, List]):
        """타임라인 차트 생성"""
        if not timeline_data:
            st.warning("타임라인 데이터가 없습니다.")
            return
        
        fig = make_subplots(specs=[[{"secondary_y": True}]])
        
        for resource_id, data_points in timeline_data.items():
            if data_points:
                times = [point[0] for point in data_points]
                values = [point[1] for point in data_points]
                
                fig.add_trace(
                    go.Scatter(
                        x=times,
                        y=values,
                        mode='lines+markers',
                        name=resource_id,
                        line=dict(width=2)
                    )
                )
        
        fig.update_layout(
            title="리소스 사용률 시계열",
            xaxis_title="시뮬레이션 시간",
            yaxis_title="사용률",
            height=400,
            hovermode='x unified'
        )
        
        st.plotly_chart(fig, use_container_width=True)
    
    def create_pie_chart(self, data: Dict[str, float], title: str):
        """원형 차트 생성"""
        fig = go.Figure(data=[go.Pie(
            labels=list(data.keys()),
            values=list(data.values()),
            hole=.3
        )])
        
        fig.update_layout(
            title=title,
            height=400
        )
        
        return fig
    
    def run_dashboard(self):
        """Streamlit 대시보드 실행"""
        st.set_page_config(
            page_title="제조 시뮬레이션 대시보드",
            page_icon="🏭",
            layout="wide",
            initial_sidebar_state="expanded"
        )
        
        st.title("🏭 제조 시뮬레이션 실시간 대시보드")
        
        # 사이드바 설정
        st.sidebar.header("설정")
        self.auto_refresh = st.sidebar.checkbox("자동 갱신", value=True)
        self.refresh_interval = st.sidebar.slider("갱신 간격 (초)", 1, 30, 5)
        
        if st.sidebar.button("수동 갱신"):
            st.rerun()
        
        # 메인 콘텐츠
        kpi_data = self.get_kpi_data()
        
        # KPI 카드
        st.header("주요 성과 지표")
        self.create_kpi_cards(kpi_data)
        
        # 차트 섹션
        col1, col2 = st.columns(2)
        
        with col1:
            st.header("리소스 사용률")
            self.create_utilization_chart(kpi_data)
        
        with col2:
            st.header("전체 사용률 게이지")
            gauge_fig = self.create_gauge_chart(
                kpi_data.get('overall_utilization', 0),
                "전체 사용률"
            )
            st.plotly_chart(gauge_fig, use_container_width=True)
        
        # 상세 정보 탭
        tab1, tab2, tab3 = st.tabs(["시계열 분석", "리소스 분석", "원시 데이터"])
        
        with tab1:
            st.header("시계열 분석")
            # 여기에 시계열 데이터가 있다면 표시
            timeline_data = {}  # 실제 구현에서는 데이터 수집
            self.create_timeline_chart(timeline_data)
        
        with tab2:
            st.header("리소스 분석")
            resource_data = kpi_data.get('resource_utilization', {})
            if resource_data:
                pie_fig = self.create_pie_chart(resource_data, "리소스별 사용률 분포")
                st.plotly_chart(pie_fig, use_container_width=True)
        
        with tab3:
            st.header("원시 데이터")
            st.json(kpi_data)
        
        # 자동 갱신
        if self.auto_refresh:
            time.sleep(self.refresh_interval)
            st.rerun()


if __name__ == "__main__":
    # 대시보드 실행 예제
    dashboard = DashboardManager()
    dashboard.run_dashboard()
