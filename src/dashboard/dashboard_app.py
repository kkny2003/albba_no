"""
Streamlit 기반 제조 시뮬레이션 대시보드 앱

웹 브라우저에서 실시간으로 시뮬레이션 데이터를 모니터링할 수 있는
인터랙티브 대시보드를 제공합니다.

실행 방법:
    streamlit run dashboard_app.py
"""

import streamlit as st
import pandas as pd
import numpy as np
import plotly.graph_objects as go
import plotly.express as px
from plotly.subplots import make_subplots
import time
import json
from datetime import datetime, timedelta
from typing import Dict, List, Any, Optional
import os
import sys

# 프로젝트 루트를 Python 경로에 추가
current_dir = os.path.dirname(os.path.abspath(__file__))
project_root = os.path.dirname(os.path.dirname(current_dir))
if project_root not in sys.path:
    sys.path.insert(0, project_root)

try:
    from src.dashboard.dashboard_manager import DashboardManager
    from src.dashboard.components import KPICard, GaugeWidget, DashboardGrid
    from src.dashboard.layouts import DashboardLayout, LayoutType
    from src.core.centralized_statistics import CentralizedStatisticsManager
except ImportError as e:
    st.error(f"모듈 가져오기 오류: {e}")
    st.info("Streamlit과 Plotly가 설치되어 있는지 확인하세요.")


class SimulationDashboardApp:
    """Streamlit 기반 시뮬레이션 대시보드 애플리케이션"""
    
    def __init__(self):
        """대시보드 앱 초기화"""
        self.setup_page_config()
        self.initialize_session_state()
        
    def setup_page_config(self):
        """페이지 설정"""
        st.set_page_config(
            page_title="제조 시뮬레이션 대시보드",
            page_icon="🏭",
            layout="wide",
            initial_sidebar_state="expanded"
        )
        
        # 커스텀 CSS
        st.markdown("""
        <style>
        .main {
            padding-top: 1rem;
        }
        .metric-card {
            background-color: #f0f2f6;
            padding: 1rem;
            border-radius: 0.5rem;
            border-left: 4px solid #1f77b4;
        }
        .status-good {
            color: #28a745;
        }
        .status-warning {
            color: #ffc107;
        }
        .status-error {
            color: #dc3545;
        }
        </style>
        """, unsafe_allow_html=True)
    
    def initialize_session_state(self):
        """세션 상태 초기화"""
        if 'dashboard_data' not in st.session_state:
            st.session_state.dashboard_data = self.generate_sample_data()
        
        if 'last_update' not in st.session_state:
            st.session_state.last_update = datetime.now()
        
        if 'auto_refresh' not in st.session_state:
            st.session_state.auto_refresh = True
        
        if 'simulation_running' not in st.session_state:
            st.session_state.simulation_running = False
    
    def generate_sample_data(self) -> Dict[str, Any]:
        """샘플 데이터 생성"""
        import random
        
        # 시간 시리즈 데이터
        time_points = list(range(0, 100, 5))
        current_time = datetime.now()
        
        return {
            'timestamp': current_time,
            'kpi': {
                'total_throughput': random.randint(85, 125),
                'overall_utilization': random.uniform(0.75, 0.95),
                'active_resources': random.randint(8, 15),
                'cycle_time': random.uniform(40, 50),
                'quality_score': random.uniform(92, 98),
                'current_time': random.uniform(1000, 1500)
            },
            'resource_utilization': {
                f'Machine_{i:02d}': random.uniform(0.6, 0.9) 
                for i in range(1, 11)
            },
            'timeline_data': {
                'time': time_points,
                'throughput': [80 + 20 * np.sin(t/10) + random.uniform(-5, 5) for t in time_points],
                'target': [100] * len(time_points),
                'utilization': [0.7 + 0.2 * np.sin(t/8) + random.uniform(-0.05, 0.05) for t in time_points]
            },
            'resource_types': {
                '가공기계': random.randint(6, 10),
                '조립라인': random.randint(3, 6),
                '검사장비': random.randint(2, 5),
                '운송장비': random.randint(4, 8)
            },
            'alerts': [
                {'level': 'info', 'message': '시스템 정상 운영 중'},
                {'level': 'warning', 'message': f'Machine_05 사용률 {random.randint(85, 95)}% - 주의 필요'},
                {'level': 'success', 'message': f'품질 점수 목표 달성: {random.uniform(95, 98):.1f}%'}
            ],
            'production_summary': {
                '오늘 생산량': random.randint(2800, 3200),
                '주간 평균': random.randint(2900, 3100),
                '월간 목표': 95000,
                '달성률': random.uniform(0.85, 0.95)
            }
        }
    
    def create_sidebar(self):
        """사이드바 생성"""
        st.sidebar.header("🎛️ 대시보드 설정")
        
        # 자동 갱신 설정
        auto_refresh = st.sidebar.checkbox(
            "자동 갱신",
            value=st.session_state.auto_refresh,
            help="체크하면 5초마다 자동으로 데이터를 갱신합니다."
        )
        st.session_state.auto_refresh = auto_refresh
        
        # 갱신 간격 설정
        refresh_interval = st.sidebar.slider(
            "갱신 간격 (초)",
            min_value=1,
            max_value=30,
            value=5,
            help="자동 갱신 간격을 설정합니다."
        )
        
        # 수동 갱신 버튼
        if st.sidebar.button("🔄 수동 갱신", use_container_width=True):
            st.session_state.dashboard_data = self.generate_sample_data()
            st.session_state.last_update = datetime.now()
            st.rerun()
        
        # 시뮬레이션 제어
        st.sidebar.subheader("🎮 시뮬레이션 제어")
        
        col1, col2 = st.sidebar.columns(2)
        with col1:
            if st.button("▶️ 시작", use_container_width=True):
                st.session_state.simulation_running = True
        
        with col2:
            if st.button("⏸️ 정지", use_container_width=True):
                st.session_state.simulation_running = False
        
        # 데이터 내보내기
        st.sidebar.subheader("📊 데이터 내보내기")
        if st.sidebar.button("JSON 다운로드", use_container_width=True):
            json_data = json.dumps(st.session_state.dashboard_data, 
                                 indent=2, default=str)
            st.sidebar.download_button(
                label="💾 JSON 파일 저장",
                data=json_data,
                file_name=f"dashboard_data_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json",
                mime="application/json"
            )
        
        # 상태 정보
        st.sidebar.subheader("ℹ️ 시스템 정보")
        st.sidebar.info(f"""
        **마지막 업데이트:** {st.session_state.last_update.strftime('%H:%M:%S')}
        
        **시뮬레이션 상태:** {'🟢 실행 중' if st.session_state.simulation_running else '🔴 정지'}
        
        **활성 리소스:** {st.session_state.dashboard_data['kpi']['active_resources']}개
        """)
        
        return refresh_interval
    
    def create_kpi_section(self):
        """KPI 섹션 생성"""
        st.header("📊 주요 성과 지표 (KPI)")
        
        kpi_data = st.session_state.dashboard_data['kpi']
        
        # 4개 열로 KPI 카드 배치
        col1, col2, col3, col4 = st.columns(4)
        
        with col1:
            throughput = kpi_data['total_throughput']
            delta_throughput = throughput - 100
            st.metric(
                label="총 처리량 (units/hour)",
                value=f"{throughput:.0f}",
                delta=f"{delta_throughput:+.0f}"
            )
        
        with col2:
            utilization = kpi_data['overall_utilization']
            st.metric(
                label="전체 사용률",
                value=f"{utilization:.1%}",
                delta=f"{(utilization - 0.85):+.1%}"
            )
        
        with col3:
            active_resources = kpi_data['active_resources']
            st.metric(
                label="활성 리소스",
                value=f"{active_resources}개",
                delta="0"
            )
        
        with col4:
            cycle_time = kpi_data['cycle_time']
            st.metric(
                label="평균 사이클 타임",
                value=f"{cycle_time:.1f}분",
                delta=f"{(cycle_time - 45):+.1f}분"
            )
        
        # 추가 KPI 행
        col5, col6, col7, col8 = st.columns(4)
        
        with col5:
            quality = kpi_data['quality_score']
            st.metric(
                label="품질 점수",
                value=f"{quality:.1f}%",
                delta=f"{(quality - 95):+.1f}%"
            )
        
        with col6:
            sim_time = kpi_data['current_time']
            st.metric(
                label="시뮬레이션 시간",
                value=f"{sim_time:.1f}분",
                delta=None
            )
        
        with col7:
            production_summary = st.session_state.dashboard_data['production_summary']
            today_production = production_summary['오늘 생산량']
            st.metric(
                label="오늘 생산량",
                value=f"{today_production:,}개",
                delta=f"{today_production - production_summary['주간 평균']:+,}개"
            )
        
        with col8:
            achievement = production_summary['달성률']
            st.metric(
                label="월간 목표 달성률",
                value=f"{achievement:.1%}",
                delta=f"{(achievement - 0.9):+.1%}"
            )
    
    def create_main_charts(self):
        """주요 차트 섹션 생성"""
        st.header("📈 실시간 모니터링")
        
        # 2개 열로 차트 배치
        col1, col2 = st.columns(2)
        
        with col1:
            self.create_resource_utilization_chart()
        
        with col2:
            self.create_utilization_gauge()
        
        # 시계열 차트 (전체 너비)
        self.create_timeline_chart()
    
    def create_resource_utilization_chart(self):
        """리소스 사용률 막대 차트"""
        st.subheader("🏭 리소스 사용률")
        
        resource_data = st.session_state.dashboard_data['resource_utilization']
        
        # Plotly 막대 차트
        fig = go.Figure(data=[
            go.Bar(
                x=list(resource_data.keys()),
                y=[v * 100 for v in resource_data.values()],
                marker_color=['#1f77b4' if v < 0.8 else '#ff7f0e' if v < 0.9 else '#d62728' 
                             for v in resource_data.values()],
                text=[f'{v:.1%}' for v in resource_data.values()],
                textposition='auto',
                hovertemplate='<b>%{x}</b><br>사용률: %{text}<extra></extra>'
            )
        ])
        
        fig.update_layout(
            title="리소스별 사용률",
            xaxis_title="리소스",
            yaxis_title="사용률 (%)",
            yaxis=dict(range=[0, 100]),
            height=400,
            showlegend=False
        )
        
        # 임계값 선 추가
        fig.add_hline(y=80, line_dash="dash", line_color="orange", 
                     annotation_text="주의 임계값 (80%)")
        fig.add_hline(y=90, line_dash="dash", line_color="red", 
                     annotation_text="위험 임계값 (90%)")
        
        st.plotly_chart(fig, use_container_width=True)
    
    def create_utilization_gauge(self):
        """전체 사용률 게이지"""
        st.subheader("⚡ 전체 시스템 사용률")
        
        utilization = st.session_state.dashboard_data['kpi']['overall_utilization']
        
        fig = go.Figure(go.Indicator(
            mode="gauge+number+delta",
            value=utilization * 100,
            domain={'x': [0, 1], 'y': [0, 1]},
            title={'text': "전체 사용률 (%)"},
            delta={'reference': 85, 'valueformat': '.1f'},
            gauge={
                'axis': {'range': [None, 100]},
                'bar': {'color': "darkblue"},
                'steps': [
                    {'range': [0, 50], 'color': "lightgray"},
                    {'range': [50, 80], 'color': "yellow"},
                    {'range': [80, 90], 'color': "orange"},
                    {'range': [90, 100], 'color': "red"}
                ],
                'threshold': {
                    'line': {'color': "red", 'width': 4},
                    'thickness': 0.75,
                    'value': 95
                }
            }
        ))
        
        fig.update_layout(height=400)
        st.plotly_chart(fig, use_container_width=True)
    
    def create_timeline_chart(self):
        """시계열 차트"""
        st.subheader("📊 시계열 분석")
        
        timeline_data = st.session_state.dashboard_data['timeline_data']
        
        # 서브플롯 생성
        fig = make_subplots(
            rows=2, cols=1,
            subplot_titles=('처리량 추이', '사용률 추이'),
            vertical_spacing=0.1
        )
        
        # 처리량 차트
        fig.add_trace(
            go.Scatter(
                x=timeline_data['time'],
                y=timeline_data['throughput'],
                mode='lines+markers',
                name='실제 처리량',
                line=dict(color='blue', width=2),
                marker=dict(size=4)
            ),
            row=1, col=1
        )
        
        fig.add_trace(
            go.Scatter(
                x=timeline_data['time'],
                y=timeline_data['target'],
                mode='lines',
                name='목표 처리량',
                line=dict(color='red', dash='dash', width=2)
            ),
            row=1, col=1
        )
        
        # 사용률 차트
        fig.add_trace(
            go.Scatter(
                x=timeline_data['time'],
                y=[v * 100 for v in timeline_data['utilization']],
                mode='lines+markers',
                name='사용률',
                line=dict(color='green', width=2),
                marker=dict(size=4),
                fill='tonexty'
            ),
            row=2, col=1
        )
        
        fig.update_layout(
            height=600,
            title_text="시계열 성능 분석",
            showlegend=True
        )
        
        fig.update_xaxes(title_text="시뮬레이션 시간", row=2, col=1)
        fig.update_yaxes(title_text="처리량 (units/hour)", row=1, col=1)
        fig.update_yaxes(title_text="사용률 (%)", row=2, col=1)
        
        st.plotly_chart(fig, use_container_width=True)
    
    def create_analysis_section(self):
        """분석 섹션"""
        st.header("🔍 상세 분석")
        
        # 탭으로 분석 내용 구분
        tab1, tab2, tab3 = st.tabs(["리소스 분석", "품질 분석", "알림 및 이벤트"])
        
        with tab1:
            self.create_resource_analysis()
        
        with tab2:
            self.create_quality_analysis()
        
        with tab3:
            self.create_alerts_section()
    
    def create_resource_analysis(self):
        """리소스 분석"""
        col1, col2 = st.columns(2)
        
        with col1:
            # 리소스 타입별 분포 원형 차트
            resource_types = st.session_state.dashboard_data['resource_types']
            
            fig = go.Figure(data=[go.Pie(
                labels=list(resource_types.keys()),
                values=list(resource_types.values()),
                hole=.3,
                textinfo='label+percent'
            )])
            
            fig.update_layout(
                title="리소스 타입별 분포",
                height=400
            )
            
            st.plotly_chart(fig, use_container_width=True)
        
        with col2:
            # 리소스 효율성 분석
            resource_util = st.session_state.dashboard_data['resource_utilization']
            
            # 효율성 카테고리 분류
            high_util = sum(1 for v in resource_util.values() if v > 0.8)
            medium_util = sum(1 for v in resource_util.values() if 0.6 <= v <= 0.8)
            low_util = sum(1 for v in resource_util.values() if v < 0.6)
            
            efficiency_data = {
                '고효율 (>80%)': high_util,
                '중효율 (60-80%)': medium_util,
                '저효율 (<60%)': low_util
            }
            
            fig = go.Figure(data=[go.Bar(
                x=list(efficiency_data.keys()),
                y=list(efficiency_data.values()),
                marker_color=['green', 'orange', 'red']
            )])
            
            fig.update_layout(
                title="리소스 효율성 분포",
                yaxis_title="리소스 수",
                height=400
            )
            
            st.plotly_chart(fig, use_container_width=True)
    
    def create_quality_analysis(self):
        """품질 분석"""
        # 품질 점수 트렌드 (샘플 데이터)
        time_points = list(range(0, 50, 2))
        quality_scores = [95 + 3 * np.sin(t/5) + np.random.normal(0, 1) for t in time_points]
        
        fig = go.Figure()
        
        fig.add_trace(go.Scatter(
            x=time_points,
            y=quality_scores,
            mode='lines+markers',
            name='품질 점수',
            line=dict(color='green', width=2)
        ))
        
        # 목표선
        fig.add_hline(y=95, line_dash="dash", line_color="red", 
                     annotation_text="목표 품질 (95%)")
        
        fig.update_layout(
            title="품질 점수 트렌드",
            xaxis_title="시뮬레이션 시간",
            yaxis_title="품질 점수 (%)",
            yaxis=dict(range=[85, 100]),
            height=400
        )
        
        st.plotly_chart(fig, use_container_width=True)
        
        # 품질 통계
        col1, col2, col3, col4 = st.columns(4)
        
        with col1:
            avg_quality = np.mean(quality_scores)
            st.metric("평균 품질", f"{avg_quality:.1f}%")
        
        with col2:
            min_quality = min(quality_scores)
            st.metric("최저 품질", f"{min_quality:.1f}%")
        
        with col3:
            max_quality = max(quality_scores)
            st.metric("최고 품질", f"{max_quality:.1f}%")
        
        with col4:
            std_quality = np.std(quality_scores)
            st.metric("품질 편차", f"{std_quality:.1f}%")
    
    def create_alerts_section(self):
        """알림 및 이벤트 섹션"""
        alerts = st.session_state.dashboard_data['alerts']
        
        st.subheader("🚨 실시간 알림")
        
        for alert in alerts:
            level = alert['level']
            message = alert['message']
            
            if level == 'error':
                st.error(f"🔴 {message}")
            elif level == 'warning':
                st.warning(f"🟡 {message}")
            elif level == 'info':
                st.info(f"🔵 {message}")
            else:
                st.success(f"🟢 {message}")
        
        # 이벤트 로그 (샘플)
        st.subheader("📋 이벤트 로그")
        
        event_data = {
            '시간': [
                (datetime.now() - timedelta(minutes=i*5)).strftime('%H:%M:%S') 
                for i in range(10, 0, -1)
            ],
            '이벤트': [
                'Machine_03 정기 점검 완료',
                'Machine_07 사용률 85% 도달',
                '품질 검사 통과 - Batch #1234',
                'Machine_02 정비 시작',
                '생산 목표 달성',
                'Machine_09 가동 시작',
                'Alert: Machine_05 과부하 경고',
                '품질 검사 통과 - Batch #1233',
                'Machine_01 사이클 완료',
                '시프트 교대 완료'
            ],
            '상태': [
                '정상', '주의', '정상', '정비', '성공', 
                '정상', '경고', '정상', '정상', '정상'
            ]
        }
        
        df = pd.DataFrame(event_data)
        st.dataframe(df, use_container_width=True)
    
    def run(self):
        """대시보드 앱 실행"""
        # 헤더
        st.title("🏭 제조 시뮬레이션 실시간 대시보드")
        st.markdown("---")
        
        # 사이드바
        refresh_interval = self.create_sidebar()
        
        # 메인 콘텐츠
        self.create_kpi_section()
        st.markdown("---")
        
        self.create_main_charts()
        st.markdown("---")
        
        self.create_analysis_section()
        
        # 자동 갱신
        if st.session_state.auto_refresh:
            time.sleep(refresh_interval)
            st.rerun()


def main():
    """메인 함수"""
    try:
        app = SimulationDashboardApp()
        app.run()
    except Exception as e:
        st.error(f"애플리케이션 실행 오류: {e}")
        st.info("필요한 패키지가 설치되어 있는지 확인하세요: streamlit, plotly, pandas, numpy")


if __name__ == "__main__":
    main()
