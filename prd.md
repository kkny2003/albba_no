 🎯 제조 시뮬레이션 Framework Report 기능 구현을 위한 최적화된 프롬프트

  📋 작업 개요

  manufacturing-simulation-framework의 모든 Resource와 Process 상태를 실시간으로 추적하고 관리할 수 있는 종합적인 Report 시스템을 구현해야 합니다.

  🎯 구체적이고 실행 가능한 작업 지침

  1단계: 현재 시스템 분석 및 통합

  현재 프레임워크의 CentralizedStatisticsManager (src/core/centralized_statistics.py)와 DataCollector (src/core/data_collector.py)를 기반으로:

  1. 모든 Resource 클래스들의 상태 추적 메서드 분석
     - Machine, Worker, Transport, Buffer의 상태 정보 수집 방식 파악
  2. 모든 Process 클래스들의 성능 메트릭 분석
     - BaseProcess, ManufacturingProcess, AssemblyProcess의 실행 통계 수집 방식 파악
  3. 기존 통계 수집 인터페이스 (StatisticsInterface) 활용 방안 설계

  2단계: Report Manager 핵심 모듈 구현

  src/core/report_manager.py 생성:

  주요 기능:
  - ReportManager 클래스: 모든 리포트 기능의 중앙 관리자
  - ResourceStateTracker: Resource별 실시간 상태 추적
  - ProcessPerformanceMonitor: Process별 성능 지표 모니터링
  - AlertSystem: 임계값 기반 실시간 알림 시스템

  필수 메서드:
  - generate_real_time_dashboard() → Dict: 실시간 대시보드 데이터
  - generate_comprehensive_report() → Dict: 종합 성능 리포트
  - track_resource_status(resource_id) → Dict: 특정 자원 상태 추적
  - track_process_performance(process_id) → Dict: 특정 공정 성능 추적
  - export_data(format: str) → 데이터 내보내기

  3단계: 단계별 분석 절차 구현

  3-1: 실시간 상태 수집

  def collect_real_time_status(self):
      # 1. 모든 등록된 Resource의 현재 상태 수집
      # 2. 모든 활성 Process의 실행 현황 수집
      # 3. Flow 및 워크플로우 진행 상황 수집
      # 4. 병목 지점 및 대기열 상태 분석

  3-2: 성능 지표 계산

  def calculate_performance_metrics(self):
      # 1. 자원 가동률 (Utilization Rate) 계산
      # 2. 처리량 (Throughput) 측정
      # 3. 평균 대기시간 (Average Waiting Time) 계산
      # 4. 완료율 (Completion Rate) 산출
      # 5. OEE (Overall Equipment Effectiveness) 계산

  3-3: 이상 상황 감지

  def detect_anomalies(self):
      # 1. 설정된 임계값과 현재 값 비교
      # 2. 예상 범위를 벗어난 성능 지표 식별
      # 3. 장시간 대기 상태인 자원/공정 감지
      # 4. 처리량 급감 패턴 탐지

  4단계: 성능 측정 방법 명시

  핵심 KPI 정의

  Resource 성능 지표:
    - 가동률: (실제 작업시간 / 전체 시간) × 100
    - 처리량: 시간당 처리 건수
    - 고장률: (고장 시간 / 전체 시간) × 100
    - 효율성: (예상 성능 / 실제 성능) × 100

  Process 성능 지표:
    - 사이클 타임: 작업 완료까지 소요 시간
    - 대기시간: 자원 할당 대기 시간
    - 성공률: (성공 건수 / 전체 시도 건수) × 100
    - 품질률: (양품 수 / 전체 생산량) × 100

  System 성능 지표:
    - 전체 처리량: 시스템 전체 출력량
    - 병목도: 가장 느린 공정 대비 처리율
    - 자원 활용도: 평균 자원 가동률
    - 응답시간: 주문 입력부터 완료까지 시간

  측정 주기 및 방법

  # 실시간 측정: 1초 간격
  # 성능 리포트: 시뮬레이션 종료 시점
  # 알림 체크: 이벤트 발생 시마다
  # 데이터 저장: 설정 가능한 간격 (기본 10초)

  5단계: 검증 기준 제시

  기능적 검증

  ✅ 모든 Resource 상태가 실시간으로 정확히 수집되는가?
  ✅ 모든 Process 성능이 올바르게 계산되는가?
  ✅ 알림 시스템이 설정된 임계값에서 정확히 작동하는가?
  ✅ 리포트 생성이 5초 이내에 완료되는가?
  ✅ 내보내기 기능이 모든 형식(CSV, JSON, Excel)에서 작동하는가?

  성능적 검증

  📊 메모리 사용량: 전체 시스템 메모리의 10% 이하
  📊 CPU 오버헤드: 시뮬레이션 성능에 5% 이하 영향
  📊 데이터 정확도: 실제 값과 99% 이상 일치
  📊 응답 속도: 대시보드 조회 1초 이내
  📊 확장성: 1000개 이상의 Resource/Process 동시 추적 가능

  통합 테스트 시나리오

  # 1. 냉장고 제조 시나리오 (scenario/scenario.py) 실행
  # 2. Report 시스템으로 전체 공정 모니터링
  # 3. 의도적 병목 생성 후 감지 여부 확인
  # 4. 알림 발생 및 리포트 생성 검증
  # 5. 다양한 형식으로 데이터 내보내기 테스트

  🔧 구현 우선순위

  1. 높음: ReportManager 핵심 클래스 구현
  2. 높음: 실시간 상태 수집 기능
  3. 중간: 성능 지표 계산 로직
  4. 중간: 알림 시스템 구현
  5. 낮음: 데이터 내보내기 및 시각화

  💡 추가 고려사항

  - 기존 CentralizedStatisticsManager와의 원활한 통합
  - 시뮬레이션 성능에 미치는 영향 최소화
  - 확장 가능한 플러그인 구조 설계
  - 사용자 친화적인 리포트 형식 제공