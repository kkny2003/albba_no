"""
향상된 통계 수집 시스템 사용 예제

이 예제는 새로운 표준화된 통계 시스템의 주요 기능들을 보여줍니다:
- 중앙 집중식 통계 관리
- 제조업 특화 KPI 계산
- 실시간 알림 시스템
- 성능 분석 및 트렌드 감지
"""

import simpy
import random
from src.core.centralized_statistics import (
    CentralizedStatisticsManager, 
    StatisticsInterface,
    AlertSeverity
)

def alert_handler(alert):
    """알림 처리 함수"""
    print(f"🚨 [{alert.severity.value.upper()}] {alert.component_id}: {alert.message}")

class ManufacturingLine:
    """제조 라인 시뮬레이션 예제"""
    
    def __init__(self, env, stats_manager, line_id):
        self.env = env
        self.line_id = line_id
        
        # 통계 인터페이스 생성
        self.stats = StatisticsInterface(
            component_id=line_id,
            component_type="manufacturing_line",
            stats_manager=stats_manager
        )
        
        # 시뮬레이션 파라미터
        self.cycle_time = 5.0  # 기본 사이클 타임 (분)
        self.failure_rate = 0.02  # 고장률
        self.quality_threshold = 95.0  # 품질 임계값
        
        # 프로세스 시작
        self.env.process(self.production_process())
        self.env.process(self.maintenance_process())
    
    def production_process(self):
        """생산 프로세스"""
        part_count = 0
        total_downtime = 0
        
        while True:
            try:
                # 생산 시작
                start_time = self.env.now
                
                # 처리 시간 (정규분포 with 변동성)
                actual_cycle_time = max(0.5, random.normalvariate(self.cycle_time, 0.5))
                yield self.env.timeout(actual_cycle_time)
                
                part_count += 1
                
                # 품질 검사
                quality_score = random.normalvariate(97.0, 2.0)
                quality_score = max(0, min(100, quality_score))  # 0-100 범위 제한
                
                # 품질에 따른 결과 결정
                if quality_score >= self.quality_threshold:
                    quality_result = "good"
                else:
                    quality_result = "defective"
                
                # 통계 기록
                self.stats.record_manufacturing_event(
                    "production_completed",
                    quality=quality_result
                )
                self.stats.record_histogram("processing_time", actual_cycle_time)
                self.stats.record_histogram("quality_score", quality_score)
                
                # 품질 검사 이벤트
                self.stats.record_manufacturing_event(
                    "quality_check",
                    score=quality_score
                )
                
                # 현재 대기열 길이 (시뮬레이션)
                queue_length = random.randint(0, 15)
                self.stats.record_gauge("queue_length", queue_length)
                
                # 가동률 계산 (간단한 모델)
                uptime_ratio = max(0.5, 1.0 - (total_downtime / max(1, self.env.now)))
                utilization = uptime_ratio * 100
                self.stats.record_gauge("utilization", utilization)
                
                # 시간당 처리량 계산
                if self.env.now > 0:
                    hourly_throughput = (part_count / self.env.now) * 60
                    self.stats.record_gauge("throughput", hourly_throughput)
                
                # 설비 고장 시뮬레이션
                if random.random() < self.failure_rate:
                    failure_duration = random.expovariate(1/30)  # 평균 30분
                    print(f"[{self.env.now:.1f}] {self.line_id}: 설비 고장 발생 ({failure_duration:.1f}분)")
                    
                    self.stats.record_manufacturing_event(
                        "machine_failure",
                        duration=failure_duration
                    )
                    
                    total_downtime += failure_duration
                    yield self.env.timeout(failure_duration)
                    
                # KPI 계산 및 기록
                if part_count % 10 == 0:  # 10개 생산마다 KPI 계산
                    self._calculate_kpis(total_downtime)
                
            except Exception as e:
                print(f"생산 프로세스 오류: {e}")
                yield self.env.timeout(1)
    
    def maintenance_process(self):
        """유지보수 프로세스"""
        while True:
            # 예방 유지보수 (24시간마다)
            yield self.env.timeout(24 * 60)
            
            maintenance_duration = random.normalvariate(60, 15)  # 평균 60분, 표준편차 15분
            maintenance_duration = max(30, maintenance_duration)  # 최소 30분
            
            print(f"[{self.env.now:.1f}] {self.line_id}: 예방 유지보수 시작 ({maintenance_duration:.1f}분)")
            
            self.stats.record_manufacturing_event(
                "maintenance_completed",
                duration=maintenance_duration
            )
            
            yield self.env.timeout(maintenance_duration)
    
    def _calculate_kpis(self, total_downtime):
        """주요 KPI 계산"""
        current_time = self.env.now
        
        if current_time > 0:
            # 가용성 계산 (계획 시간 대비 실제 가동 시간)
            planned_time = current_time
            availability = self.stats.calculate_availability(planned_time, total_downtime)
            
            # 성능 효율성 계산
            total_parts = self.stats.stats_manager.components[self.line_id].get_latest_value("total_parts_produced")
            if total_parts and total_parts.value > 0:
                actual_production_time = current_time - total_downtime
                performance = self.stats.calculate_performance_efficiency(
                    ideal_cycle_time=self.cycle_time,
                    actual_cycle_time=actual_production_time,
                    units_produced=int(total_parts.value)
                )
                
                # 품질률 계산
                good_parts = self.stats.stats_manager.components[self.line_id].get_latest_value("good_parts_first_pass")
                quality_rate = 95.0  # 기본값
                if good_parts and total_parts.value > 0:
                    quality_rate = (good_parts.value / total_parts.value) * 100
                
                # OEE 계산
                oee = self.stats.calculate_oee(availability, performance, quality_rate)
                
                print(f"[{self.env.now:.1f}] {self.line_id} KPI - OEE: {oee:.2f}%, 가용성: {availability:.2f}%, 성능: {performance:.2f}%, 품질: {quality_rate:.2f}%")

def run_simulation():
    """시뮬레이션 실행"""
    print("🏭 향상된 통계 수집 시스템 예제 시작")
    print("=" * 60)
    
    # SimPy 환경 생성
    env = simpy.Environment()
    
    # 중앙 통계 관리자 생성
    stats_manager = CentralizedStatisticsManager(
        env=env,
        max_components=100,
        enable_alerts=True
    )
    
    # 알림 콜백 등록
    stats_manager.register_alert_callback(alert_handler)
    
    # 제조 라인 생성
    lines = []
    for i in range(3):
        line = ManufacturingLine(env, stats_manager, f"line_{i+1:02d}")
        lines.append(line)
    
    # 시뮬레이션 실행 (48시간)
    simulation_time = 48 * 60  # 48시간 (분 단위)
    
    # 중간 보고서 생성 프로세스
    def periodic_report():
        while True:
            yield env.timeout(8 * 60)  # 8시간마다
            
            print(f"\n📊 [{env.now:.1f}분] 중간 보고서")
            print("-" * 40)
            
            # 전체 시스템 성능 요약
            performance_summary = stats_manager.get_system_performance_summary()
            print(f"시스템 상태: {performance_summary['health_status']}")
            print(f"활성 알림: {performance_summary['alerts_summary']['total_alerts']}개")
            
            # 각 라인별 주요 KPI
            for line in lines:
                kpi_dashboard = line.stats.get_kpi_dashboard()
                print(f"{line.line_id}: {kpi_dashboard['performance_status']}")
                
                if 'oee' in kpi_dashboard['key_metrics']:
                    oee_value = kpi_dashboard['key_metrics']['oee']['latest_value']
                    if oee_value:
                        print(f"  - OEE: {oee_value:.2f}%")
    
    # 보고서 프로세스 시작
    env.process(periodic_report())
    
    # 시뮬레이션 실행
    print(f"🚀 시뮬레이션 시작 (시간: {simulation_time}분)")
    env.run(until=simulation_time)
    
    print(f"\n✅ 시뮬레이션 완료 (최종 시간: {env.now:.1f}분)")
    print("=" * 60)
    
    # 최종 통계 보고서
    print("\n📈 최종 통계 보고서")
    print("-" * 40)
    
    # 전체 시스템 통계
    global_stats = stats_manager.get_global_statistics(include_manufacturing_summary=True)
    manufacturing_summary = global_stats.get('manufacturing_summary', {})
    
    print(f"전체 OEE: {manufacturing_summary.get('overall_oee', 0):.2f}%")
    print(f"평균 가용성: {manufacturing_summary.get('average_availability', 0):.2f}%")
    print(f"총 생산량: {manufacturing_summary.get('total_production', 0):.0f}개")
    print(f"총 불량품: {manufacturing_summary.get('total_defects', 0):.0f}개")
    print(f"전체 불량률: {manufacturing_summary.get('global_defect_rate', 0):.2f}%")
    
    # 라인별 상세 통계
    print(f"\n📋 라인별 상세 통계")
    print("-" * 40)
    
    for line in lines:
        print(f"\n{line.line_id}:")
        stats = stats_manager.get_component_statistics(line.line_id, include_kpis=True)
        
        # 주요 메트릭 출력
        metrics = stats.get('metrics', {})
        if 'total_parts_produced' in metrics:
            total_parts = metrics['total_parts_produced']['latest_value']
            print(f"  총 생산량: {total_parts:.0f}개")
        
        if 'processing_time' in metrics:
            avg_time = metrics['processing_time'].get('mean', 0)
            print(f"  평균 처리 시간: {avg_time:.2f}분")
        
        if 'quality_score' in metrics:
            avg_quality = metrics['quality_score'].get('mean', 0)
            print(f"  평균 품질 점수: {avg_quality:.2f}")
        
        # 알림 정보
        alerts_info = stats.get('alerts', {})
        active_alerts = alerts_info.get('active_alerts', 0)
        if active_alerts > 0:
            print(f"  ⚠️  활성 알림: {active_alerts}개")
    
    # 실시간 대시보드 데이터
    dashboard_data = stats_manager.get_real_time_dashboard_data()
    print(f"\n🎛️  시스템 대시보드")
    print("-" * 40)
    print(f"시스템 상태: {dashboard_data['system_status']}")
    
    key_metrics = dashboard_data.get('key_metrics', {})
    for metric_name, metric_data in key_metrics.items():
        avg_value = metric_data.get('current_average', 0)
        component_count = metric_data.get('component_count', 0)
        print(f"{metric_name}: {avg_value:.2f} (컴포넌트 {component_count}개)")
    
    # 데이터 내보내기 예제
    print(f"\n💾 데이터 내보내기")
    print("-" * 40)
    
    export_data = stats_manager.export_statistics(include_time_series=False)
    
    # JSON 파일로 저장
    import json
    export_filename = "simulation_statistics.json"
    try:
        with open(export_filename, "w", encoding='utf-8') as f:
            json.dump(export_data, f, indent=2, ensure_ascii=False)
        print(f"✅ 통계 데이터가 {export_filename}에 저장되었습니다.")
    except Exception as e:
        print(f"❌ 파일 저장 중 오류: {e}")
    
    print(f"\n🎉 예제 완료!")

if __name__ == "__main__":
    run_simulation()
