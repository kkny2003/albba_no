"""
대시보드 데모 시나리오

대시보드 기능을 테스트하고 시연하기 위한 간단한 시나리오입니다.
"""

import os
import sys
import time
import threading
from datetime import datetime

# 프로젝트 루트를 Python 경로에 추가
project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if project_root not in sys.path:
    sys.path.insert(0, project_root)

try:
    import matplotlib
    matplotlib.use('Agg')  # 백그라운드 모드로 설정
    
    from src.utils.visualization import VisualizationManager
    
    print("✅ 모든 모듈 로드 성공")
    
except ImportError as e:
    print(f"❌ 모듈 로드 실패: {e}")
    print("필요한 패키지를 설치하세요: pip install matplotlib numpy pandas")
    sys.exit(1)


def test_visualization_components():
    """시각화 컴포넌트 테스트"""
    print("\n🎨 시각화 컴포넌트 테스트...")
    
    viz_manager = VisualizationManager()
    
    # 1. 막대 차트 테스트
    categories = ['Machine_01', 'Machine_02', 'Machine_03', 'Machine_04', 'Machine_05']
    values = [85, 92, 78, 95, 87]
    viz_manager.plot_bar_chart(
        categories, values, 
        save_path="test_bar_chart.png"
    )
    print("  ✅ 막대 차트 생성 완료")
    
    # 2. 원형 차트 테스트
    labels = ['가공기계', '조립라인', '검사장비', '운송장비']
    sizes = [8, 4, 3, 5]
    viz_manager.plot_pie_chart(
        labels, sizes,
        title="리소스 타입별 분포 (원형 차트)",
        save_path="test_pie_chart.png"
    )
    print("  ✅ 원형 차트 생성 완료")
    
    # 3. 영역 차트 테스트
    import numpy as np
    x_data = list(range(0, 50, 2))
    y_data = [80 + 20 * np.sin(t/5) + np.random.normal(0, 3) for t in x_data]
    viz_manager.plot_area_chart(
    )
    print("  ✅ 영역 차트 생성 완료")
    
    # 4. 게이지 차트 테스트
    viz_manager.plot_gauge_chart(
        value=82.5, max_value=100,
        title="전체 사용률 (게이지 차트)",
        save_path="test_gauge_chart.png"
    )
    print("  ✅ 게이지 차트 생성 완료")


    """KPI 시스템 테스트"""
    print("\n📊 KPI 시스템 테스트...")
    
    # 샘플 KPI 시스템 생성
    kpi_manager = create_sample_kpi_system()
    
    # KPI 값 업데이트 시뮬레이션
    import random
    for i in range(5):
        # 처리량 업데이트
        throughput = random.uniform(85, 115)
        kpi_manager.update_kpi("throughput", throughput)
        # 사용률 업데이트
        utilization = random.uniform(0.75, 0.9)
        kpi_manager.update_kpi("utilization", utilization)
        
        # 품질 점수 업데이트
        quality = random.uniform(92, 97)
        kpi_manager.update_kpi("quality", quality)
        
    
    # KPI 대시보드 생성
    dashboard_fig = kpi_manager.create_dashboard("mixed")
    if dashboard_fig:
        dashboard_fig.savefig("kpi_dashboard_demo.png", dpi=300, bbox_inches='tight')
        print("  ✅ KPI 대시보드 생성 완료: kpi_dashboard_demo.png")
    
    # 알림 확인
    recent_alerts = kpi_manager.alert_system.get_recent_alerts(5)
    print(f"  📢 생성된 알림 수: {len(recent_alerts)}")
    for alert in recent_alerts[-3:]:  # 최근 3개 알림만 표시
        print(f"    - {alert['level'].value}: {alert['message']}")


def test_dashboard_layout():
    """대시보드 레이아웃 테스트"""
    print("\n🎛️ 대시보드 레이아웃 테스트...")
    # 샘플 대시보드 생성
    layout, fig = create_sample_dashboard()
    if fig:
        fig.savefig("manufacturing_dashboard_demo.png", dpi=300, bbox_inches='tight')
    
    # 모니터링 레이아웃 테스트
    sample_data = {
        'status': {'status_1': 'OK', 'status_2': 'WARNING', 'status_3': 'OK', 'status_4': 'ERROR'},
        'realtime': {},
        'alerts': ['시스템 정상', '일부 리소스 주의 필요'],
        'system': {}
    }
    
    monitoring_fig = layout.create_monitoring_layout(sample_data)
    if monitoring_fig:
        monitoring_fig.savefig("monitoring_dashboard_demo.png", dpi=300, bbox_inches='tight')
        print("  ✅ 모니터링 대시보드 생성 완료: monitoring_dashboard_demo.png")


def test_real_time_system():
    """실시간 시스템 테스트"""
    print("\n⚡ 실시간 시스템 테스트...")
    
    # 실시간 시스템 초기화 (Mock 모드)
    data_bridge = initialize_real_time_system(None, update_interval=2.0)
    
    print(f"  🔄 데이터 브릿지 생성됨 (업데이트 간격: {data_bridge.update_interval}초)")
    
    # 데이터 수집 테스트
    time.sleep(3)  # 몇 초 대기하여 데이터 수집
    
    latest_data = data_bridge.get_latest_data()
    if latest_data:
        print(f"  📊 최신 데이터 수집됨: {latest_data.timestamp}")
        print(f"     - 처리량: {latest_data.kpi_data.get('throughput', 0):.1f}")
        print(f"     - 사용률: {latest_data.kpi_data.get('utilization', 0):.1%}")
        print(f"     - 활성 리소스: {latest_data.kpi_data.get('active_resources', 0)}")
    
    # 히스토리 데이터 확인
    history = data_bridge.get_historical_data(5)  # 최근 5분
    print(f"  📈 수집된 히스토리 데이터: {len(history)}개")
    
    # 트렌드 데이터 테스트
    trend_data = data_bridge.get_kpi_trend('throughput', 5)
    print(f"  📊 처리량 트렌드 데이터: {len(trend_data)}개 포인트")
    
    # 데이터 내보내기 테스트
    export_file = data_bridge.export_data("dashboard_demo_export.json")
    print(f"  💾 데이터 내보내기 완료: {export_file}")
    
    # 모니터링 중지
    data_bridge.stop_monitoring()
    print("  ⏹️ 모니터링 중지됨")


def run_interactive_demo():
    """인터랙티브 데모 실행"""
    print("\n🎮 인터랙티브 데모 (10초간 실행)...")
    
    # 실시간 시스템 시작
    data_bridge = get_data_bridge()
    data_bridge.update_interval = 1.0
    
    if not data_bridge.running:
        data_bridge.start_monitoring()
    
    # 10초간 실시간 데이터 모니터링
    start_time = time.time()
    while time.time() - start_time < 10:
        latest = data_bridge.get_latest_data()
        if latest:
            throughput = latest.kpi_data.get('throughput', 0)
            utilization = latest.kpi_data.get('utilization', 0)
            timestamp = latest.timestamp.strftime('%H:%M:%S')
            
            print(f"  [{timestamp}] 처리량: {throughput:.1f}, 사용률: {utilization:.1%}")
        
        time.sleep(2)
    
    data_bridge.stop_monitoring()
    print("  ✅ 인터랙티브 데모 완료")


def main():
    """메인 함수"""
    print("🏭 제조 시뮬레이션 대시보드 데모 시작")
    print("=" * 60)
    
    try:
        # 1. 시각화 컴포넌트 테스트
        test_visualization_components()
        
        # 2. KPI 시스템 테스트
        
        # 3. 대시보드 레이아웃 테스트
        
        # 4. 실시간 시스템 테스트
        test_real_time_system()
        
        # 5. 인터랙티브 데모
        
        print("\n" + "=" * 60)
        print("🎉 모든 테스트 완료!")
        print("\n생성된 파일들:")
        print("  - test_bar_chart.png: 막대 차트 예제")
        print("  - test_pie_chart.png: 원형 차트 예제")
        print("  - test_area_chart.png: 영역 차트 예제")
        print("  - test_gauge_chart.png: 게이지 차트 예제")
        print("  - kpi_dashboard_demo.png: KPI 대시보드")
        print("  - manufacturing_dashboard_demo.png: 제조 대시보드")
        print("  - monitoring_dashboard_demo.png: 모니터링 대시보드")
        print("  - dashboard_demo_export.json: 데이터 내보내기 예제")
        
        print("\n다음 단계:")
        print("  1. Streamlit 대시보드 실행:")
        print("     streamlit run src/dashboard/dashboard_app.py")
        print("  2. 웹 브라우저에서 http://localhost:8501 접속")
        print("  3. 실시간 대시보드 확인")
        
    except Exception as e:
        print(f"\n❌ 데모 실행 중 오류 발생: {e}")
        import traceback
        traceback.print_exc()
        return 1
    
    return 0


if __name__ == "__main__":
    exit_code = main()
    sys.exit(exit_code)
