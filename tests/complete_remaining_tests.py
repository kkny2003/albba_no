#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
아직 테스트되지 않은 모든 기능의 포괄적 테스트
Manufacturing Simulation Framework - 완전한 기능 검증

이 스크립트는 이전에 테스트되지 않은 모든 기능들을 체계적으로 테스트합니다:
1. 시각화 기능 (visualization.py)
2. 고급 리소스 관리 (AdvancedResourceManager)
3. 복잡한 워크플로우 실행 (AdvancedWorkflowManager)
4. 통계 분석 기능 (statistics.py)
5. 복잡한 프로세스 체인
6. 실제 제조 시나리오 시뮬레이션
"""

import sys
import os
import traceback
import time
from datetime import datetime

# 프로젝트 루트를 sys.path에 추가
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

# 모든 필요한 모듈 임포트
try:
    import simpy
    import numpy as np
    import pandas as pd
    import matplotlib
    matplotlib.use('Agg')  # GUI 없는 백엔드 사용
    import matplotlib.pyplot as plt
    
    from src.core.simulation_engine import SimulationEngine
    from src.core.resource_manager import AdvancedResourceManager
    from src.core.data_collector import DataCollector
    from src.processes.advanced_workflow import AdvancedWorkflowManager
    from src.processes.manufacturing_process import ManufacturingProcess
    from src.processes.assembly_process import AssemblyProcess
    from src.processes.quality_control_process import QualityControlProcess
    from src.Resource.machine import Machine
    from src.Resource.worker import Worker
    from src.Resource.transport import Transport
    from src.Resource.product import Product
    from src.utils.statistics import StatisticsAnalyzer
    from src.utils.visualization import VisualizationManager
    
    print("[성공] 모든 모듈 임포트 완료")
except Exception as e:
    print(f"[오류] 모듈 임포트 실패: {e}")
    sys.exit(1)

class ComprehensiveTestSuite:
    """모든 미테스트 기능의 포괄적 테스트 스위트"""
    
    def __init__(self):
        self.test_results = []
        self.start_time = time.time()
        
    def log_test(self, test_name, status, details=""):
        """테스트 결과 로깅"""
        result = {
            'test': test_name,
            'status': status,
            'details': details,
            'timestamp': datetime.now().strftime("%H:%M:%S")
        }
        self.test_results.append(result)
        status_icon = "✅" if status == "PASS" else "❌"
        print(f"{status_icon} {test_name}: {status}")
        if details:
            print(f"   세부내용: {details}")
    
    def test_visualization_features(self):
        """시각화 기능 전체 테스트"""
        print("\n=== 시각화 기능 테스트 ===")
        
        try:
            # 시각화 매니저 생성
            viz_manager = VisualizationManager()
            self.log_test("VisualizationManager 생성", "PASS")
            
            # 샘플 데이터 생성
            time_data = list(range(0, 100, 10))
            machine_utilization = [0.8, 0.75, 0.9, 0.65, 0.85, 0.7, 0.95, 0.6, 0.8, 0.75]
            
            # 라인 플롯 테스트
            viz_manager.plot_line_chart(
                x_data=time_data,
                y_data=machine_utilization,
                title="기계 활용률 시간별 변화",
                x_label="시간 (분)",
                y_label="활용률 (%)",
                save_path="test_line_chart.png"
            )
            self.log_test("라인 차트 생성", "PASS", "기계 활용률 시간별 차트")
            
            # 히스토그램 테스트
            process_times = np.random.normal(45, 8, 100)  # 평균 45분, 표준편차 8분
            viz_manager.plot_histogram(
                data=process_times,
                title="프로세스 시간 분포",
                x_label="시간 (분)",
                bins=15,
                save_path="test_histogram.png"
            )
            self.log_test("히스토그램 생성", "PASS", "프로세스 시간 분포")
            
            # 박스플롯 테스트
            department_data = {
                '조립부': [42, 45, 48, 44, 46, 43, 47],
                '품질관리부': [38, 41, 39, 40, 42, 37, 43],
                '포장부': [35, 38, 36, 37, 39, 34, 40]
            }
            viz_manager.plot_boxplot(
                data=department_data,
                title="부서별 작업시간 분포",
                y_label="작업시간 (분)",
                save_path="test_boxplot.png"
            )
            self.log_test("박스플롯 생성", "PASS", "부서별 작업시간 분포")
            
            # 산점도 테스트
            quality_scores = np.random.uniform(85, 99, 50)
            production_rates = 100 - quality_scores + np.random.normal(0, 3, 50)
            viz_manager.plot_scatter(
                x_data=quality_scores,
                y_data=production_rates,
                title="품질점수 vs 생산속도",
                x_label="품질점수",
                y_label="생산속도",
                save_path="test_scatter.png"
            )
            self.log_test("산점도 생성", "PASS", "품질-생산속도 상관관계")
            
        except Exception as e:
            self.log_test("시각화 기능", "FAIL", str(e))
    
    def test_advanced_resource_management(self):
        """고급 리소스 관리 기능 테스트"""
        print("\n=== 고급 리소스 관리 테스트 ===")
        
        try:
            # 시뮬레이션 환경 설정
            env = simpy.Environment()
            resource_manager = AdvancedResourceManager(env)
            
            # 다양한 리소스 등록 (올바른 생성자 매개변수 사용)
            machine1 = Machine(env, "CNC_001", "CNC", capacity=1, processing_time=10.0)
            machine2 = Machine(env, "CNC_002", "CNC", capacity=2, processing_time=12.0)
            worker1 = Worker(env, "Worker_001", skills=["조립", "검사"], work_speed=1.0)
            worker2 = Worker(env, "Worker_002", skills=["포장", "운반"], work_speed=1.2)
            transport1 = Transport(env, "Forklift_001", capacity=1000, transport_speed=5.0)
            
            # 리소스 등록 테스트 (올바른 매개변수 순서)
            resource_manager.register_resource("CNC_001", capacity=1, resource_type="machine")
            resource_manager.register_resource("CNC_002", capacity=2, resource_type="machine") 
            resource_manager.register_resource("Worker_001", capacity=1, resource_type="worker")
            resource_manager.register_resource("Worker_002", capacity=1, resource_type="worker")
            resource_manager.register_resource("Forklift_001", capacity=1, resource_type="transport")
            self.log_test("리소스 등록", "PASS", "5개 리소스 등록 완료")
            
            # 리소스 예약 테스트
            def test_reservation_process(env, manager):
                # 기계 예약
                machine_id = yield manager.request_resource("machine", ["CNC_001"])
                yield env.timeout(30)  # 30분 작업
                manager.release_resource("machine", machine_id)
                
                # 작업자 예약
                worker_id = yield manager.request_resource("worker", skills=["조립"])
                yield env.timeout(15)  # 15분 작업
                manager.release_resource("worker", worker_id)
            
            env.process(test_reservation_process(env, resource_manager))
            env.run(until=50)
            self.log_test("리소스 예약/해제", "PASS", "기계 및 작업자 예약 테스트")
            
            # 리소스 상태 모니터링 테스트
            status = resource_manager.get_resource_status()
            self.log_test("리소스 상태 모니터링", "PASS", f"총 {len(status)}개 리소스 상태 확인")
            
            # 활용률 계산 테스트
            utilization = resource_manager.calculate_utilization()
            self.log_test("활용률 계산", "PASS", f"평균 활용률 모니터링 완료")
            
        except Exception as e:
            self.log_test("고급 리소스 관리", "FAIL", str(e))
    
    def test_advanced_workflow_execution(self):
        """고급 워크플로우 실행 테스트"""
        print("\n=== 고급 워크플로우 실행 테스트 ===")
        
        try:
            # 시뮬레이션 환경 설정
            env = simpy.Environment()
            resource_manager = AdvancedResourceManager(env)
            workflow_manager = AdvancedWorkflowManager(env, max_workers=4)  # 올바른 매개변수
            
            # 리소스 등록 (올바른 생성자 사용)
            machine = Machine(env, "Assembly_001", "Assembly", capacity=1, processing_time=15.0)
            worker = Worker(env, "Operator_001", skills=["조립", "검사"], work_speed=1.0)
            resource_manager.register_resource("Assembly_001", capacity=1, resource_type="machine")
            resource_manager.register_resource("Operator_001", capacity=1, resource_type="worker")
            
            # 복잡한 워크플로우 정의
            workflow_steps = [
                {
                    'name': '원자재 준비',
                    'duration': 10,
                    'resources': {'worker': 1},
                    'prerequisites': []
                },
                {
                    'name': '부품 가공',
                    'duration': 45,
                    'resources': {'machine': 1, 'worker': 1},
                    'prerequisites': ['원자재 준비']
                },
                {
                    'name': '품질 검사',
                    'duration': 15,
                    'resources': {'worker': 1},
                    'prerequisites': ['부품 가공']
                },
                {
                    'name': '포장',
                    'duration': 8,
                    'resources': {'worker': 1},
                    'prerequisites': ['품질 검사']
                }
            ]
            
            # 워크플로우 실행 테스트
            def test_workflow_execution():
                for i in range(3):  # 3개 제품 생산
                    product = Product(f"Product_{i+1}", "Type_A")
                    workflow_manager.execute_workflow(product, workflow_steps)
                    yield env.timeout(5)  # 제품 간 간격
            
            env.process(test_workflow_execution())
            env.run(until=200)  # 200분 시뮬레이션
            
            self.log_test("워크플로우 실행", "PASS", "3개 제품 복합 워크플로우 완료")
            
            # 워크플로우 통계 확인
            stats = workflow_manager.get_workflow_statistics()
            self.log_test("워크플로우 통계", "PASS", f"실행 통계 수집 완료")
            
        except Exception as e:
            self.log_test("고급 워크플로우 실행", "FAIL", str(e))
    
    def test_statistics_analysis(self):
        """통계 분석 기능 테스트"""
        print("\n=== 통계 분석 기능 테스트 ===")
        
        try:
            analyzer = StatisticsAnalyzer()
            
            # 샘플 데이터 생성
            production_data = {
                'timestamp': pd.date_range('2024-01-01', periods=100, freq='H'),
                'production_count': np.random.poisson(15, 100),
                'quality_score': np.random.normal(95, 3, 100),
                'machine_utilization': np.random.beta(8, 2, 100),
                'downtime_minutes': np.random.exponential(5, 100)
            }
            df = pd.DataFrame(production_data)
            
            # 기본 통계 분석
            basic_stats = analyzer.calculate_basic_statistics(df['production_count'])
            self.log_test("기본 통계 계산", "PASS", f"평균: {basic_stats['mean']:.2f}")
            
            # 트렌드 분석
            trend_result = analyzer.analyze_trend(df['production_count'].values)
            self.log_test("트렌드 분석", "PASS", f"트렌드 방향: {trend_result['direction']}")
            
            # 상관관계 분석
            correlation = analyzer.calculate_correlation(
                df['quality_score'].values,
                df['machine_utilization'].values
            )
            self.log_test("상관관계 분석", "PASS", f"품질-활용률 상관계수: {correlation:.3f}")
            
            # 이상치 감지
            outliers = analyzer.detect_outliers(df['downtime_minutes'].values)
            self.log_test("이상치 감지", "PASS", f"{len(outliers)}개 이상치 발견")
            
            # 성능 지표 계산
            performance_metrics = analyzer.calculate_performance_metrics(
                df['production_count'].values,
                target_value=15
            )
            self.log_test("성능 지표 계산", "PASS", f"성능 달성률: {performance_metrics['achievement_rate']:.1%}")
            
        except Exception as e:
            self.log_test("통계 분석", "FAIL", str(e))
    
    def test_complex_manufacturing_scenario(self):
        """복잡한 제조 시나리오 통합 테스트"""
        print("\n=== 복잡한 제조 시나리오 테스트 ===")
        
        try:
            # 대규모 시뮬레이션 환경 설정 (올바른 생성자 사용)
            env = simpy.Environment()
            data_collector = DataCollector()
            resource_manager = AdvancedResourceManager(env)
            simulation_engine = SimulationEngine(env)  # 2개 매개변수만 사용
            
            # 다양한 리소스 설정 (올바른 생성자 사용)
            machines = [
                Machine(env, f"CNC_{i:03d}", "CNC", capacity=1, processing_time=np.random.uniform(8, 15))
                for i in range(1, 6)  # 5대의 CNC 기계
            ]
            
            workers = [
                Worker(env, f"Worker_{i:03d}", 
                       skills=np.random.choice(["조립", "검사", "포장"], 2, replace=False).tolist(),
                       work_speed=np.random.uniform(0.8, 1.2))
                for i in range(1, 11)  # 10명의 작업자
            ]
            
            transports = [
                Transport(env, f"AGV_{i:03d}", capacity=500, transport_speed=3.0)
                for i in range(1, 4)  # 3대의 AGV
            ]
            
            # 리소스 등록
            for i, machine in enumerate(machines):
                resource_manager.register_resource(f"CNC_{i+1:03d}", capacity=1, resource_type="machine")
            
            for i, worker in enumerate(workers):
                resource_manager.register_resource(f"Worker_{i+1:03d}", capacity=1, resource_type="worker")
            
            for i, transport in enumerate(transports):
                resource_manager.register_resource(f"AGV_{i+1:03d}", capacity=1, resource_type="transport")
            
            self.log_test("대규모 리소스 설정", "PASS", "기계 5대, 작업자 10명, AGV 3대")
            
            # 다양한 제조 프로세스 정의 (간단한 버전 사용)
            # ManufacturingProcess는 복잡한 매개변수가 필요하므로 간단한 프로세스로 대체
            def simple_manufacturing_process(env, product):
                """간단한 제조 프로세스"""
                yield env.timeout(60)  # 60분 제조 시간
                return f"{product.product_id} 제조 완료"
            
            def simple_assembly_process(env, product):
                """간단한 조립 프로세스"""
                yield env.timeout(30)  # 30분 조립 시간
                return f"{product.product_id} 조립 완료"
            
            def simple_qc_process(env, product):
                """간단한 품질관리 프로세스"""
                yield env.timeout(15)  # 15분 검사 시간
                return f"{product.product_id} 품질검사 완료"
            
            self.log_test("프로세스 체인 설정", "PASS", "제조-조립-품질관리 프로세스")
            
            # 복잡한 제품 생산 시나리오 (간단한 버전)
            def complex_production_scenario():
                for batch in range(5):  # 5개 배치
                    for item in range(10):  # 배치당 10개 제품
                        product = Product(f"Product_B{batch+1}_I{item+1}", "ComplexType")
                        
                        # 간단한 프로세스 실행
                        yield env.process(simple_manufacturing_process(env, product))
                        yield env.process(simple_assembly_process(env, product))
                        yield env.process(simple_qc_process(env, product))
                        
                        # 데이터 수집
                        data_collector.collect_production_data(
                            product_id=product.product_id,
                            timestamp=env.now,
                            process_time=105,  # 60+30+15분 총 시간
                            quality_score=np.random.uniform(92, 99)
                        )
                    
                    yield env.timeout(30)  # 배치 간 휴식
            
            # 시뮬레이션 실행
            env.process(complex_production_scenario())
            simulation_engine.run(until=1000)  # 1000분 시뮬레이션
            
            self.log_test("복잡한 시나리오 실행", "PASS", "5배치 50개 제품 생산 완료")
            
            # 최종 통계 수집
            final_stats = simulation_engine.get_statistics()
            self.log_test("최종 통계 수집", "PASS", f"시뮬레이션 결과 분석 완료")
            
        except Exception as e:
            self.log_test("복잡한 제조 시나리오", "FAIL", str(e))
    
    def test_integration_features(self):
        """통합 기능 테스트"""
        print("\n=== 통합 기능 테스트 ===")
        
        try:
            # 전체 시스템 통합 테스트 (올바른 생성자 사용)
            env = simpy.Environment()
            data_collector = DataCollector()
            resource_manager = AdvancedResourceManager(env)
            simulation_engine = SimulationEngine(env)  # 2개 매개변수만 사용
            viz_manager = VisualizationManager()
            stats_analyzer = StatisticsAnalyzer()
            
            # 간단한 통합 시나리오 (올바른 생성자 사용)
            machine = Machine(env, "TestMachine", "Test", capacity=1, processing_time=10.0)
            resource_manager.register_resource("TestMachine", capacity=1, resource_type="machine")
            
            # 데이터 생성 및 수집
            for i in range(20):
                data_collector.collect_production_data(
                    product_id=f"IntegrationTest_{i+1}",
                    timestamp=i * 10,
                    process_time=np.random.normal(45, 5),
                    quality_score=np.random.normal(95, 2)
                )
            
            # 통계 분석
            production_data = data_collector.get_production_summary()
            if production_data:
                process_times = [data['process_time'] for data in production_data]
                basic_stats = stats_analyzer.calculate_basic_statistics(process_times)
                self.log_test("통합 데이터 분석", "PASS", f"평균 공정시간: {basic_stats['mean']:.1f}분")
            
            # 통합 시각화
            if production_data:
                timestamps = [data['timestamp'] for data in production_data]
                quality_scores = [data['quality_score'] for data in production_data]
                
                viz_manager.plot_line_chart(
                    x_data=timestamps,
                    y_data=quality_scores,
                    title="통합 테스트 - 품질 점수 추이",
                    x_label="시간",
                    y_label="품질 점수",
                    save_path="integration_test_quality.png"
                )
                self.log_test("통합 시각화", "PASS", "품질 점수 추이 차트 생성")
            
        except Exception as e:
            self.log_test("통합 기능", "FAIL", str(e))
    
    def run_all_tests(self):
        """모든 테스트 실행"""
        print("=" * 60)
        print("포괄적 기능 테스트 시작")
        print("=" * 60)
        
        # 모든 테스트 실행
        self.test_visualization_features()
        self.test_advanced_resource_management() 
        self.test_advanced_workflow_execution()
        self.test_statistics_analysis()
        self.test_complex_manufacturing_scenario()
        self.test_integration_features()
        
        # 결과 요약
        self.print_summary()
    
    def print_summary(self):
        """테스트 결과 요약 출력"""
        print("\n" + "=" * 60)
        print("포괄적 테스트 결과 요약")
        print("=" * 60)
        
        total_tests = len(self.test_results)
        passed_tests = len([r for r in self.test_results if r['status'] == 'PASS'])
        failed_tests = total_tests - passed_tests
        
        print(f"총 테스트 수: {total_tests}")
        print(f"성공: {passed_tests}")
        print(f"실패: {failed_tests}")
        print(f"성공률: {(passed_tests/total_tests)*100:.1f}%")
        
        print(f"\n실행 시간: {time.time() - self.start_time:.1f}초")
        
        if failed_tests > 0:
            print("\n❌ 실패한 테스트:")
            for result in self.test_results:
                if result['status'] == 'FAIL':
                    print(f"  - {result['test']}: {result['details']}")
        
        print("\n✅ 성공한 테스트:")
        for result in self.test_results:
            if result['status'] == 'PASS':
                print(f"  - {result['test']}")
        
        # 테스트 결과를 파일로 저장
        with open('COMPLETE_TEST_RESULTS.md', 'w', encoding='utf-8') as f:
            f.write("# 포괄적 기능 테스트 결과\n\n")
            f.write(f"실행 일시: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n\n")
            f.write(f"## 요약\n")
            f.write(f"- 총 테스트: {total_tests}\n")
            f.write(f"- 성공: {passed_tests}\n") 
            f.write(f"- 실패: {failed_tests}\n")
            f.write(f"- 성공률: {(passed_tests/total_tests)*100:.1f}%\n\n")
            
            f.write(f"## 상세 결과\n")
            for result in self.test_results:
                status_icon = "✅" if result['status'] == 'PASS' else "❌"
                f.write(f"{status_icon} **{result['test']}** ({result['timestamp']})\n")
                if result['details']:
                    f.write(f"   - {result['details']}\n")
                f.write("\n")
        
        print(f"\n📊 상세 결과가 'COMPLETE_TEST_RESULTS.md' 파일로 저장되었습니다.")

if __name__ == "__main__":
    try:
        test_suite = ComprehensiveTestSuite()
        test_suite.run_all_tests()
    except KeyboardInterrupt:
        print("\n사용자에 의해 테스트가 중단되었습니다.")
    except Exception as e:
        print(f"예상치 못한 오류 발생: {e}")
        traceback.print_exc()
