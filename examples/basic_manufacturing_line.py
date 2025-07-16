"""
기본 제조 라인 시뮬레이션 예제
가장 간단한 형태의 제조 라인을 구현하여 프레임워크의 기본 사용법을 보여줍니다.
"""

import simpy
import sys
import os

# 프로젝트 루트 디렉토리를 Python 경로에 추가
sys.path.append(os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), 'src'))

from core.simulation_engine import SimulationEngine
from Resource.machine import Machine
from Resource.worker import Worker
from Resource.product import Product
from core.data_collector import DataCollector
from utils.visualization import Visualization


def create_basic_manufacturing_line():
    """기본 제조 라인을 생성하는 함수"""
    print("=== 기본 제조 라인 시뮬레이션 시작 ===")
    
    # 시뮬레이션 엔진 생성 (재현 가능한 결과를 위해 시드 설정)
    engine = SimulationEngine(random_seed=42)
    env = engine.env
    
    # 데이터 수집기 생성
    data_collector = DataCollector()
    
    # 제조 라인 구성 요소 생성
    # 1. 기계들
    cutting_machine = Machine(env, "절단기", "절단기계", processing_time=1.5, capacity=1)
    drilling_machine = Machine(env, "드릴링머신", "드릴링기계", processing_time=2.0, capacity=1)
    assembly_station = Machine(env, "조립스테이션", "조립기계", processing_time=3.0, capacity=1)
    
    # 2. 작업자들
    operator1 = Worker(env, "작업자1", ["절단", "드릴링"], work_speed=1.0)
    operator2 = Worker(env, "작업자2", ["조립", "검사"], work_speed=1.2)
    
    # 3. 시뮬레이션에 자원 등록
    engine.add_resource("cutting_machine", cutting_machine.resource)
    engine.add_resource("drilling_machine", drilling_machine.resource)
    engine.add_resource("assembly_station", assembly_station.resource)
    
    print(f"제조 라인 구성:")
    print(f"- 절단기: 처리시간 {cutting_machine.processing_time}시간")
    print(f"- 드릴링머신: 처리시간 {drilling_machine.processing_time}시간")
    print(f"- 조립스테이션: 처리시간 {assembly_station.processing_time}시간")
    print(f"- 작업자: {len([operator1, operator2])}명")
    
    def product_arrival(env, data_collector):
        """제품 도착 프로세스 - 일정 간격으로 새 제품이 도착"""
        product_count = 0
        
        while True:
            # 새 제품 생성
            product_count += 1
            product = Product(f"P{product_count:03d}", "기본제품")
            
            print(f"시간 {env.now:.1f}: 제품 {product.product_id} 도착")
            
            # 제품 처리 프로세스 시작
            env.process(process_product(env, product, cutting_machine, drilling_machine, 
                                     assembly_station, data_collector))
            
            # 제품 도착 간격 (평균 4시간마다 새 제품 도착)
            yield env.timeout(4.0)
    
    def process_product(env, product, cutting_machine, drilling_machine, assembly_station, data_collector):
        """개별 제품의 전체 제조 프로세스"""
        start_time = env.now
        
        # 1단계: 절단 공정
        print(f"시간 {env.now:.1f}: 제품 {product.product_id} 절단 공정 대기")
        with cutting_machine.resource.request() as request:
            yield request
            print(f"시간 {env.now:.1f}: 제품 {product.product_id} 절단 공정 시작")
            yield env.timeout(cutting_machine.processing_time)
            print(f"시간 {env.now:.1f}: 제품 {product.product_id} 절단 공정 완료")
        
        # 2단계: 드릴링 공정
        print(f"시간 {env.now:.1f}: 제품 {product.product_id} 드릴링 공정 대기")
        with drilling_machine.resource.request() as request:
            yield request
            print(f"시간 {env.now:.1f}: 제품 {product.product_id} 드릴링 공정 시작")
            yield env.timeout(drilling_machine.processing_time)
            print(f"시간 {env.now:.1f}: 제품 {product.product_id} 드릴링 공정 완료")
        
        # 3단계: 조립 공정
        print(f"시간 {env.now:.1f}: 제품 {product.product_id} 조립 공정 대기")
        with assembly_station.resource.request() as request:
            yield request
            print(f"시간 {env.now:.1f}: 제품 {product.product_id} 조립 공정 시작")
            yield env.timeout(assembly_station.processing_time)
            print(f"시간 {env.now:.1f}: 제품 {product.product_id} 조립 공정 완료")
        
        # 전체 처리 시간 계산
        total_time = env.now - start_time
        print(f"시간 {env.now:.1f}: 제품 {product.product_id} 전체 제조 완료 (총 소요시간: {total_time:.1f}시간)")
        
        # 데이터 수집
        data_collector.collect_data("completion_time", total_time, timestamp=env.now)
        data_collector.collect_data("throughput", 1, timestamp=env.now)
        
        # 제품 이력에 완료 정보 추가
        product.add_history("제조완료", env.now)
    
    # 제품 도착 프로세스를 시뮬레이션에 추가
    engine.add_process(product_arrival, data_collector)
    
    # 시뮬레이션 실행 (40시간 동안)
    print("\n시뮬레이션 실행 중...")
    engine.run(until=40)
    
    print("\n=== 시뮬레이션 결과 분석 ===")
    
    # 결과 분석
    completion_times = data_collector.get_data("completion_time")
    throughput_data = data_collector.get_data("throughput")
    
    if completion_times['values']:
        avg_completion_time = sum(completion_times['values']) / len(completion_times['values'])
        min_completion_time = min(completion_times['values'])
        max_completion_time = max(completion_times['values'])
        
        print(f"총 완성된 제품 수: {len(completion_times['values'])}개")
        print(f"평균 제조 시간: {avg_completion_time:.2f}시간")
        print(f"최소 제조 시간: {min_completion_time:.2f}시간")
        print(f"최대 제조 시간: {max_completion_time:.2f}시간")
        
        # 시간당 처리량 계산
        total_products = len(completion_times['values'])
        simulation_time = 40
        hourly_throughput = total_products / simulation_time
        print(f"시간당 평균 처리량: {hourly_throughput:.2f}개/시간")
    
    # 결과 시각화
    create_visualization(data_collector)
    
    return data_collector


def create_visualization(data_collector):
    """수집된 데이터를 시각화하는 함수"""
    print("\n결과 시각화 중...")
    
    try:
        viz = Visualization()
        
        # 제조 시간 분포 히스토그램
        completion_times = data_collector.get_data("completion_time")
        if completion_times['values']:
            viz.plot_histogram(
                completion_times['values'],
                bins=10,
                title="제품 제조 시간 분포",
                xlabel="제조 시간 (시간)",
                ylabel="제품 수"
            )
            viz.save_plot("basic_manufacturing_completion_times.png")
            print("제조 시간 분포 차트가 'basic_manufacturing_completion_times.png'로 저장되었습니다.")
        
        # 시간에 따른 누적 처리량
        throughput_data = data_collector.get_data("throughput")
        if throughput_data['timestamps']:
            # 누적 처리량 계산
            cumulative_throughput = []
            total = 0
            for value in throughput_data['values']:
                total += value
                cumulative_throughput.append(total)
            
            viz.plot_line_chart(
                throughput_data['timestamps'],
                cumulative_throughput,
                title="시간에 따른 누적 처리량",
                xlabel="시간 (시간)",
                ylabel="누적 제품 수"
            )
            viz.save_plot("basic_manufacturing_throughput.png")
            print("누적 처리량 차트가 'basic_manufacturing_throughput.png'로 저장되었습니다.")
            
    except Exception as e:
        print(f"시각화 중 오류 발생: {e}")
        print("시각화 없이 시뮬레이션을 계속합니다.")


def analyze_bottleneck():
    """병목 구간 분석을 위한 함수"""
    print("\n=== 병목 구간 분석 ===")
    print("이론적 분석:")
    print("- 절단기: 1.5시간")
    print("- 드릴링머신: 2.0시간")  
    print("- 조립스테이션: 3.0시간")
    print("병목 구간: 조립스테이션 (가장 긴 처리 시간)")
    print("이론적 최대 처리량: 1/3.0 = 0.33개/시간")


if __name__ == "__main__":
    # 기본 제조 라인 시뮬레이션 실행
    data_collector = create_basic_manufacturing_line()
    
    # 병목 구간 분석
    analyze_bottleneck()
    
    print("\n=== 시뮬레이션 완료 ===")
    print("이 예제는 가장 기본적인 제조 라인 시뮬레이션을 보여줍니다.")
    print("더 복잡한 예제는 다른 예제 파일들을 참조하세요.")
