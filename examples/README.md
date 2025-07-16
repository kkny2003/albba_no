# Examples README

이 디렉토리에는 제조 공정 시뮬레이션 프레임워크의 다양한 사용 예제가 포함되어 있습니다.

## 📁 예제 파일 목록

### 1. `correct_simpy_example.py`
- **설명**: 기존 SimPy 기반 시뮬레이션 예제
- **난이도**: ⭐⭐
- **주요 기능**: SimPy 기본 사용법, 자원 관리, 기본 프로세스
- **실행 방법**: 
  ```bash
  python correct_simpy_example.py
  ```

### 2. `basic_manufacturing_line.py`
- **설명**: 가장 기본적인 제조 라인 시뮬레이션
- **난이도**: ⭐
- **주요 기능**: 
  - 순차적 제조 공정 (절단 → 드릴링 → 조립)
  - 기본 데이터 수집
  - 간단한 시각화
- **학습 목표**: 프레임워크 기본 사용법 이해
- **실행 방법**:
  ```bash
  python basic_manufacturing_line.py
  ```

### 3. `process_chaining_example.py`
- **설명**: 프로세스 체이닝 기능을 활용한 고급 시뮬레이션
- **난이도**: ⭐⭐⭐
- **주요 기능**:
  - `>>` 연산자를 통한 프로세스 체이닝
  - 우선순위 시스템
  - 복잡한 자원 관리
  - 프로세스 실행 모드 (순차/병렬/우선순위)
- **학습 목표**: 프레임워크의 핵심 기능 활용
- **실행 방법**:
  ```bash
  python process_chaining_example.py
  ```

### 4. `data_analysis_example.py`
- **설명**: 데이터 수집, 분석, 시각화에 특화된 시뮬레이션
- **난이도**: ⭐⭐⭐
- **주요 기능**:
  - 다양한 KPI 데이터 수집 (처리량, 대기시간, 가동률, 품질)
  - 통계 분석 (평균, 분산, 백분위수)
  - 다양한 시각화 (선 그래프, 히스토그램, 박스 플롯, 산점도)
  - 데이터 내보내기 (CSV)
- **학습 목표**: 시뮬레이션 결과 분석 및 활용
- **실행 방법**:
  ```bash
  python data_analysis_example.py
  ```

## 🚀 시작하기

### 전제 조건
1. Python 3.7 이상
2. 필수 패키지 설치:
   ```bash
   pip install -r ../requirements.txt
   ```

### 권장 학습 순서
1. **초보자**: `basic_manufacturing_line.py` → `correct_simpy_example.py`
2. **중급자**: `process_chaining_example.py` → `data_analysis_example.py`
3. **고급자**: 모든 예제 + 사용자 정의 시뮬레이션 개발

## 📊 예제별 주요 학습 내용

| 예제 | SimPy 기본 | 프로세스 체이닝 | 자원 관리 | 데이터 분석 | 시각화 |
|------|------------|-----------------|-----------|-------------|---------|
| basic_manufacturing_line | ✅ | ❌ | ⭐ | ⭐ | ⭐ |
| correct_simpy_example | ✅ | ⭐ | ✅ | ⭐ | ❌ |
| process_chaining_example | ✅ | ✅ | ✅ | ⭐ | ❌ |
| data_analysis_example | ✅ | ❌ | ⭐ | ✅ | ✅ |

범례: ✅ 핵심 기능, ⭐ 기본 기능, ❌ 해당 없음

## 💡 실행 시 참고사항

### 공통 문제 해결
1. **ImportError 발생 시**:
   - 프로젝트 루트 디렉토리에서 실행하세요
   - Python 경로가 올바르게 설정되었는지 확인하세요

2. **시각화 오류 시**:
   - matplotlib가 설치되어 있는지 확인하세요
   - GUI 환경이 없는 서버에서는 backend 설정이 필요할 수 있습니다

3. **성능 이슈**:
   - 시뮬레이션 시간을 줄여보세요
   - 데이터 수집 빈도를 조정하세요

### 사용자 정의하기
각 예제는 쉽게 수정할 수 있도록 설계되었습니다:

- **처리 시간 변경**: `processing_time` 매개변수 수정
- **자원 수량 조정**: 기계/작업자 수 변경
- **시뮬레이션 시간**: `engine.run(until=시간)` 수정
- **데이터 수집 항목 추가**: `data_collector.collect_data()` 호출 추가

## 📈 성능 벤치마크

### 테스트 환경 기준
- **하드웨어**: Intel i5-8250U, 8GB RAM
- **Python**: 3.9.7
- **SimPy**: 4.0.1

| 예제 | 시뮬레이션 시간 | 실행 시간 | 메모리 사용량 |
|------|-----------------|-----------|---------------|
| basic_manufacturing_line | 40시간 | ~2초 | ~50MB |
| process_chaining_example | 50시간 | ~3초 | ~60MB |
| data_analysis_example | 72시간 | ~5초 | ~80MB |

## 🔗 관련 문서

- [Getting Started Guide](../docs/getting_started.md)
- [API Reference](../docs/api_reference.md)
- [Process Chaining Guide](../docs/process_chaining.md)
- [Resource Management Guide](../docs/resource_management_guide.md)

## 🤝 기여하기

새로운 예제를 추가하고 싶으시다면:

1. 기존 예제 스타일을 따라주세요
2. 충분한 주석을 추가하세요
3. README에 예제 설명을 추가하세요
4. Pull Request를 생성하세요

### 예제 작성 가이드라인
- **명확한 목적**: 각 예제는 특정 기능을 명확히 보여줘야 합니다
- **단계별 설명**: 코드에 상세한 주석을 포함하세요
- **오류 처리**: 예외 상황에 대한 적절한 처리를 포함하세요
- **결과 분석**: 시뮬레이션 결과에 대한 분석을 제공하세요

---

**참고**: 모든 예제는 교육 목적으로 작성되었으며, 실제 프로덕션 환경에서 사용하기 전에 추가적인 최적화와 검증이 필요할 수 있습니다.
