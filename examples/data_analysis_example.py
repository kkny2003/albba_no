"""
데이터 수집 및 시각화 예제
시뮬레이션 중 데이터를 수집하고 다양한 방법으로 시각화하는 방법을 보여줍니다.
"""

import simpy
import sys
import os
import random

# 프로젝트 루트 디렉토리를 Python 경로에 추가
sys.path.append(os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), 'src'))

from core.simulation_engine import SimulationEngine
from Resource.machine import Machine
from Resource.worker import Worker
from Resource.product import Product
from core.data_collector import DataCollector
from utils.visualization import Visualization
from utils.statistics import Statistics


def create_data_analysis_simulation():
    """데이터 수집 및 분석에 특화된 시뮬레이션"""
    print("=== 데이터 수집 및 시각화 시뮬레이션 시작 ===")
    
    # 시뮬레이션 엔진 생성
    engine = SimulationEngine(random_seed=456)
    env = engine.env
    
    # 데이터 수집기 생성
    data_collector = DataCollector()
    
    # 제조 장비 생성
    machines = []
    for i in range(3):
        machine = Machine(env, f"기계{i+1}", "생산기계", 
                         processing_time=2.0 + random.uniform(-0.5, 0.5), capacity=1)
        machines.append(machine)
        engine.add_resource(f"machine_{i+1}", machine.resource)
    
    # 작업자 생성
    workers = []
    for i in range(2):
        worker = Worker(env, f"작업자{i+1}", ["생산", "검사"], 
                       work_speed=1.0 + random.uniform(-0.2, 0.2))
        workers.append(worker)
    
    print(f"시뮬레이션 설정:")
    print(f"- 기계: {len(machines)}대")
    print(f"- 작업자: {len(workers)}명")
    print(f"- 데이터 수집 항목: 처리량, 대기시간, 기계 가동률, 품질 지표")
    
    def production_monitoring(env, machines, data_collector):
        """생산 모니터링 및 데이터 수집 프로세스"""
        while True:
            # 각 기계의 상태 모니터링
            for i, machine in enumerate(machines):
                # 가동률 시뮬레이션 (실제로는 기계 객체에서 가져올 수 있음)
                utilization = random.uniform(0.6, 0.95)
                data_collector.collect_data(f"machine_{i+1}_utilization", utilization, timestamp=env.now)
                
                # 기계 온도 시뮬레이션 (예시 데이터)
                temperature = random.uniform(65, 85)
                data_collector.collect_data(f"machine_{i+1}_temperature", temperature, timestamp=env.now)
                
                # 진동 수준 시뮬레이션
                vibration = random.uniform(0.1, 0.8)
                data_collector.collect_data(f"machine_{i+1}_vibration", vibration, timestamp=env.now)
            
            # 전체 라인 효율성
            line_efficiency = random.uniform(0.70, 0.90)
            data_collector.collect_data("line_efficiency", line_efficiency, timestamp=env.now)
            
            # 1시간마다 모니터링
            yield env.timeout(1.0)
    
    def quality_monitoring(env, data_collector):
        """품질 모니터링 프로세스"""
        defect_rate_trend = 0.05  # 초기 불량률 5%
        
        while True:
            # 불량률 변화 시뮬레이션 (시간에 따라 점진적 변화)
            change = random.uniform(-0.01, 0.01)
            defect_rate_trend = max(0.01, min(0.15, defect_rate_trend + change))
            
            # 불량률 데이터 수집
            data_collector.collect_data("defect_rate", defect_rate_trend, timestamp=env.now)
            
            # 품질 점수 (100 - 불량률*100)
            quality_score = (1 - defect_rate_trend) * 100
            data_collector.collect_data("quality_score", quality_score, timestamp=env.now)
            
            # 30분마다 품질 검사
            yield env.timeout(0.5)
    
    def production_process(env, machines, data_collector):
        """실제 생산 프로세스 시뮬레이션"""
        product_count = 0
        
        while True:
            product_count += 1
            product = Product(f"DA{product_count:03d}", "분석용제품")
            
            # 대기 시간 측정 시작
            arrival_time = env.now
            
            # 사용 가능한 기계 찾기 (간단한 로직)
            machine_index = random.randint(0, len(machines) - 1)
            machine = machines[machine_index]
            
            # 기계 사용 요청
            with machine.resource.request() as request:
                yield request
                
                # 대기 시간 계산 및 수집
                wait_time = env.now - arrival_time
                data_collector.collect_data("wait_time", wait_time, timestamp=env.now)
                
                # 가공 시간 시뮬레이션 (변동성 포함)
                processing_time = machine.processing_time * random.uniform(0.8, 1.2)
                data_collector.collect_data("processing_time", processing_time, timestamp=env.now)
                
                # 가공 수행
                yield env.timeout(processing_time)
                
                # 처리량 데이터 수집
                data_collector.collect_data("throughput", 1, timestamp=env.now)
                
                # 사이클 시간 (대기 + 가공)
                cycle_time = wait_time + processing_time
                data_collector.collect_data("cycle_time", cycle_time, timestamp=env.now)
            
            # 다음 제품 도착 간격 (포아송 분포 근사)
            inter_arrival_time = random.expovariate(1.0/3.0)  # 평균 3시간 간격
            yield env.timeout(inter_arrival_time)
    
    # 모든 프로세스를 시뮬레이션에 추가
    engine.add_process(production_monitoring, machines, data_collector)
    engine.add_process(quality_monitoring, data_collector)
    engine.add_process(production_process, machines, data_collector)
    
    # 시뮬레이션 실행
    print("\n시뮬레이션 실행 중... (72시간)")
    engine.run(until=72)  # 72시간 (3일) 시뮬레이션
    
    # 데이터 분석 및 시각화
    analyze_collected_data(data_collector)
    create_comprehensive_visualizations(data_collector)
    
    return data_collector


def analyze_collected_data(data_collector):
    """수집된 데이터를 통계적으로 분석"""
    print("\n=== 수집된 데이터 통계 분석 ===")
    
    stats = Statistics()
    
    # 처리량 분석
    throughput_data = data_collector.get_data("throughput")
    if throughput_data['values']:
        total_products = len(throughput_data['values'])
        simulation_hours = 72
        hourly_rate = total_products / simulation_hours
        
        print(f"생산성 분석:")
        print(f"  총 생산량: {total_products}개")
        print(f"  시간당 평균 생산량: {hourly_rate:.2f}개/시간")
    
    # 대기 시간 분석
    wait_time_data = data_collector.get_data("wait_time")
    if wait_time_data['values']:
        wait_times = wait_time_data['values']
        print(f"\n대기 시간 분석:")
        print(f"  평균 대기 시간: {stats.calculate_mean(wait_times):.2f}시간")
        print(f"  대기 시간 표준편차: {stats.calculate_std_deviation(wait_times):.2f}시간")
        print(f"  최대 대기 시간: {max(wait_times):.2f}시간")
        print(f"  95% 백분위수: {stats.calculate_percentile(wait_times, 95):.2f}시간")
    
    # 사이클 시간 분석
    cycle_time_data = data_collector.get_data("cycle_time")
    if cycle_time_data['values']:
        cycle_times = cycle_time_data['values']
        print(f"\n사이클 시간 분석:")
        print(f"  평균 사이클 시간: {stats.calculate_mean(cycle_times):.2f}시간")
        print(f"  사이클 시간 분산: {stats.calculate_variance(cycle_times):.2f}")
    
    # 품질 분석
    quality_data = data_collector.get_data("quality_score")
    defect_data = data_collector.get_data("defect_rate")
    if quality_data['values'] and defect_data['values']:
        print(f"\n품질 분석:")
        print(f"  평균 품질 점수: {stats.calculate_mean(quality_data['values']):.1f}점")
        print(f"  평균 불량률: {stats.calculate_mean(defect_data['values'])*100:.2f}%")
        print(f"  불량률 표준편차: {stats.calculate_std_deviation(defect_data['values'])*100:.2f}%")
    
    # 기계 가동률 분석
    for i in range(3):
        utilization_data = data_collector.get_data(f"machine_{i+1}_utilization")
        if utilization_data['values']:
            avg_util = stats.calculate_mean(utilization_data['values']) * 100
            print(f"  기계{i+1} 평균 가동률: {avg_util:.1f}%")


def create_comprehensive_visualizations(data_collector):
    """포괄적인 데이터 시각화"""
    print("\n데이터 시각화 생성 중...")
    
    try:
        viz = Visualization()
        
        # 1. 시간에 따른 처리량 누적 차트
        throughput_data = data_collector.get_data("throughput")
        if throughput_data['timestamps']:
            cumulative_throughput = []
            total = 0
            for value in throughput_data['values']:
                total += value
                cumulative_throughput.append(total)
            
            viz.plot_line_chart(
                throughput_data['timestamps'],
                cumulative_throughput,
                title="시간에 따른 누적 생산량",
                xlabel="시간 (시간)",
                ylabel="누적 생산량 (개)"
            )
            viz.save_plot("data_analysis_cumulative_throughput.png")
        
        # 2. 대기 시간 분포 히스토그램
        wait_time_data = data_collector.get_data("wait_time")
        if wait_time_data['values']:
            viz.plot_histogram(
                wait_time_data['values'],
                bins=20,
                title="대기 시간 분포",
                xlabel="대기 시간 (시간)",
                ylabel="빈도"
            )
            viz.save_plot("data_analysis_wait_time_distribution.png")
        
        # 3. 기계 가동률 비교 박스 플롯
        machine_utilizations = []
        machine_labels = []
        for i in range(3):
            util_data = data_collector.get_data(f"machine_{i+1}_utilization")
            if util_data['values']:
                machine_utilizations.append([u*100 for u in util_data['values']])
                machine_labels.append(f"기계{i+1}")
        
        if machine_utilizations:
            viz.plot_box_plot(
                machine_utilizations,
                machine_labels,
                title="기계별 가동률 분포",
                ylabel="가동률 (%)"
            )
            viz.save_plot("data_analysis_machine_utilization.png")
        
        # 4. 품질 점수 시계열
        quality_data = data_collector.get_data("quality_score")
        if quality_data['timestamps']:
            viz.plot_line_chart(
                quality_data['timestamps'],
                quality_data['values'],
                title="시간에 따른 품질 점수 변화",
                xlabel="시간 (시간)",
                ylabel="품질 점수"
            )
            viz.save_plot("data_analysis_quality_trend.png")
        
        # 5. 사이클 시간 vs 대기 시간 산점도
        cycle_data = data_collector.get_data("cycle_time")
        wait_data = data_collector.get_data("wait_time")
        if cycle_data['values'] and wait_data['values']:
            # 데이터 길이 맞추기
            min_length = min(len(cycle_data['values']), len(wait_data['values']))
            viz.plot_scatter(
                wait_data['values'][:min_length],
                cycle_data['values'][:min_length],
                title="대기 시간 vs 사이클 시간",
                xlabel="대기 시간 (시간)",
                ylabel="사이클 시간 (시간)"
            )
            viz.save_plot("data_analysis_wait_vs_cycle.png")
        
        print("모든 시각화 차트가 생성되었습니다:")
        print("  - data_analysis_cumulative_throughput.png")
        print("  - data_analysis_wait_time_distribution.png") 
        print("  - data_analysis_machine_utilization.png")
        print("  - data_analysis_quality_trend.png")
        print("  - data_analysis_wait_vs_cycle.png")
        
    except Exception as e:
        print(f"시각화 중 오류 발생: {e}")


def demonstrate_data_export():
    """데이터 내보내기 기능 시연"""
    print("\n=== 데이터 내보내기 시연 ===")
    
    # 간단한 데이터 수집기 생성
    data_collector = DataCollector()
    
    # 샘플 데이터 추가
    for i in range(10):
        data_collector.collect_data("sample_metric", i * 2.5, timestamp=i)
    
    # CSV로 내보내기
    try:
        data_collector.save_to_csv("sample_data_export.csv")
        print("샘플 데이터가 'sample_data_export.csv'로 내보내졌습니다.")
    except Exception as e:
        print(f"데이터 내보내기 중 오류: {e}")
    
    # 데이터 조회 방법 시연
    sample_data = data_collector.get_data("sample_metric")
    print(f"수집된 샘플 데이터 포인트 수: {len(sample_data['values'])}")
    print(f"첫 번째 데이터: 값={sample_data['values'][0]}, 시간={sample_data['timestamps'][0]}")


def demonstrate_real_time_monitoring():
    """실시간 모니터링 개념 시연"""
    print("\n=== 실시간 모니터링 개념 ===")
    print("실제 구현에서는 다음과 같은 기능을 추가할 수 있습니다:")
    print("1. 임계값 알림 시스템")
    print("   - 대기 시간이 5시간 이상일 때 알림")
    print("   - 불량률이 10% 이상일 때 경고")
    print("   - 기계 가동률이 60% 이하일 때 알림")
    print()
    print("2. 대시보드 실시간 업데이트")
    print("   - 웹 기반 대시보드 연동")
    print("   - 실시간 차트 업데이트")
    print("   - KPI 모니터링")
    print()
    print("3. 자동 보고서 생성")
    print("   - 일일/주간/월간 자동 보고서")
    print("   - 이메일 자동 발송")
    print("   - 예외 상황 자동 리포팅")


if __name__ == "__main__":
    # 메인 데이터 분석 시뮬레이션 실행
    data_collector = create_data_analysis_simulation()
    
    # 데이터 내보내기 시연
    demonstrate_data_export()
    
    # 실시간 모니터링 개념 설명
    demonstrate_real_time_monitoring()
    
    print("\n=== 데이터 수집 및 시각화 시뮬레이션 완료 ===")
    print("이 예제는 시뮬레이션 중 다양한 데이터를 수집하고")
    print("통계 분석 및 시각화하는 방법을 보여줍니다.")
    print("실제 제조 시스템에서는 이런 데이터를 활용하여")
    print("생산성 향상과 품질 개선을 도모할 수 있습니다.")
