# 리소스 고장확률 가이드

## 개요

Manufacturing Simulation Framework에서 리소스(기계, 작업자)의 고장확률을 정의하고 활용하는 방법을 설명합니다. 이 기능을 통해 현실적인 제조 환경의 불확실성을 시뮬레이션에 반영할 수 있습니다.

**✨ 새로운 기능: None 값 지원**
- `None`: 해당 기능을 완전히 비활성화 (고장/실수/휴식 없음)
- `0.0`: 확률이 0 (기능은 활성화되어 있지만 발생하지 않음)
- 양수: 정상적인 확률값

## 기계(Machine) 고장확률

### 기본 개념

기계의 고장확률은 다음과 같은 매개변수로 정의됩니다:

- **failure_probability**: 작업당 고장 확률 (0.0 ~ 1.0, 또는 None)
- **mean_time_to_failure**: 평균 고장 간격 시간 (MTTF, 또는 None)
- **mean_time_to_repair**: 평균 수리 시간 (MTTR, 또는 None)

### 사용법

```python
import simpy
from src.Resource.machine import Machine

# SimPy 환경 생성
env = simpy.Environment()

# 🔴 완전히 안정적인 기계 (고장 기능 비활성화)
stable_machine = Machine(
    env=env,
    machine_id="STABLE_M001",
    machine_type="안정기계",
    processing_time=5.0,
    failure_probability=None,      # 고장 기능 완전 비활성화
    mean_time_to_failure=None,     # 비활성화
    mean_time_to_repair=None       # 비활성화
)

# 🟡 고장 확률이 0인 기계 (기능은 활성화, 확률 0)
zero_failure_machine = Machine(
    env=env,
    machine_id="ZERO_M001",
    machine_type="확률0기계",
    processing_time=5.0,
    failure_probability=0.0,       # 고장 확률 0
    mean_time_to_failure=100.0,    # 설정되어 있지만 사용되지 않음
    mean_time_to_repair=8.0
)

# 🟢 실제 고장이 발생하는 기계
normal_machine = Machine(
    env=env,
    machine_id="NORMAL_M001",
    machine_type="일반기계",
    processing_time=5.0,
    failure_probability=0.02,      # 2% 고장 확률
    mean_time_to_failure=100.0,    # 평균 100시간마다 고장
    mean_time_to_repair=8.0        # 평균 8시간 수리
)
```

### 고장 메커니즘

1. **고장 발생**: 각 작업 시작 시 `failure_probability`에 따라 랜덤하게 고장 발생
2. **수리 프로세스**: 고장 발생 시 `_repair_process()` 메서드 실행
3. **수리 시간**: 지수분포를 따르는 수리 시간 (평균: `mean_time_to_repair`)
4. **리소스 차단**: 수리 중에는 기계 사용 불가

### 고장 관련 메서드

#### `_check_failure() -> bool`
- 작업 중 고장 발생 여부를 확인
- `failure_probability`를 기반으로 확률적 판단

#### `_repair_process() -> Generator`
- 기계 고장 시 수리 프로세스 수행
- 수리 시간은 지수분포를 따름

#### `force_failure() -> Generator`
- 강제로 기계 고장을 발생시킴 (테스트 용도)

#### `get_failure_rate() -> float`
- 기계의 고장률 계산 (고장 횟수 / 운영 시간)

#### `get_availability() -> float`
- 기계의 가용성 계산 (정상 운영 시간 / 전체 시간)

### 고장 통계

기계의 `get_status()` 메서드는 다음 고장 관련 정보를 제공합니다:

```python
status = machine.get_status()
print(f"고장 횟수: {status['total_failures']}")
print(f"고장률: {status['failure_rate']:.4f}")
print(f"가용성: {status['availability']:.2%}")
print(f"현재 고장 상태: {status['is_broken']}")
```

## 작업자(Worker) 실수확률

### 기본 개념

작업자의 실수확률은 다음과 같은 매개변수로 정의됩니다:

- **error_probability**: 작업당 실수 확률 (0.0 ~ 1.0, 또는 None)
- **mean_time_to_rest**: 평균 휴식 필요 간격 (또는 None)
- **mean_rest_time**: 평균 휴식 시간 (또는 None)

### 사용법

```python
import simpy
from src.Resource.worker import Worker

# SimPy 환경 생성
env = simpy.Environment()

# 🔴 완전히 안정적인 작업자 (실수/휴식 기능 비활성화)
stable_worker = Worker(
    env=env,
    worker_id="STABLE_W001",
    skills=["안정작업"],
    work_speed=1.0,
    error_probability=None,        # 실수 기능 완전 비활성화
    mean_time_to_rest=None,        # 휴식 기능 비활성화
    mean_rest_time=None            # 비활성화
)

# 🟡 실수는 없지만 휴식은 필요한 작업자
no_error_worker = Worker(
    env=env,
    worker_id="NOERROR_W001",
    skills=["정확작업"],
    work_speed=1.2,
    error_probability=None,        # 실수 없음
    mean_time_to_rest=100.0,       # 휴식 필요
    mean_rest_time=15.0
)

# 🟢 실수와 휴식이 모두 발생할 수 있는 작업자
normal_worker = Worker(
    env=env,
    worker_id="NORMAL_W001",
    skills=["일반작업"],
    work_speed=1.0,
    error_probability=0.05,        # 5% 실수 확률
    mean_time_to_rest=100.0,       # 평균 100시간마다 휴식 필요
    mean_rest_time=15.0            # 평균 15시간 휴식
)
```

### 실수/휴식 메커니즘

1. **실수 발생**: 각 작업 시작 시 `error_probability`에 따라 랜덤하게 실수 발생
2. **실수 처리**: 실수 발생 시 작업 시간이 1.5배 증가
3. **휴식 필요**: `mean_time_to_rest` 간격으로 확률적 휴식 필요
4. **휴식 프로세스**: 휴식 중에는 작업자 사용 불가

### 실수/휴식 관련 메서드

#### `_check_error() -> bool`
- 작업 중 실수 발생 여부를 확인
- `error_probability`를 기반으로 확률적 판단

#### `_check_rest_needed() -> bool`
- 휴식이 필요한지 확인
- `mean_time_to_rest` 간격과 확률을 고려

#### `_rest_process() -> Generator`
- 작업자 휴식 프로세스 수행
- 휴식 시간은 지수분포를 따름

#### `force_rest() -> Generator`
- 강제로 작업자 휴식을 발생시킴 (테스트 용도)

#### `get_error_rate() -> float`
- 작업자의 실수율 계산 (실수 횟수 / 완료 작업 수)

#### `get_availability() -> float`
- 작업자의 가용성 계산 (정상 작업 시간 / 전체 시간)

### 실수/휴식 통계

작업자의 `get_status()` 메서드는 다음 실수 관련 정보를 제공합니다:

```python
status = worker.get_status()
print(f"실수 횟수: {status['total_errors']}")
print(f"실수율: {status['error_rate']:.2%}")
print(f"가용성: {status['availability']:.2%}")
print(f"현재 휴식 상태: {status['is_resting']}")
```

## None 값 활용 가이드

### None vs 0.0의 차이점

| 설정값 | 의미 | 동작 | 사용 케이스 |
|--------|------|------|-------------|
| `None` | 기능 완전 비활성화 | 해당 로직이 전혀 실행되지 않음 | 완전히 안정적인 환경 시뮬레이션 |
| `0.0` | 확률이 0 | 기능은 활성화되어 있지만 발생하지 않음 | 기능 테스트나 비교 분석 |
| 양수 | 정상적인 확률 | 확률에 따라 이벤트 발생 | 현실적인 시뮬레이션 |

### 혼합 사용 예제

```python
# 부분적 기능 활성화 예제
machine = Machine(
    env=env,
    machine_id="MIXED_M001",
    machine_type="혼합설정기계",
    failure_probability=0.1,       # 고장은 발생 (10%)
    mean_time_to_failure=None,     # MTTF 기능은 비활성화
    mean_time_to_repair=5.0        # 수리 시간 설정
)

worker = Worker(
    env=env,
    worker_id="MIXED_W001",
    skills=["혼합작업"],
    error_probability=None,        # 실수 없음
    mean_time_to_rest=50.0,        # 휴식은 필요
    mean_rest_time=None            # 기본 휴식 시간 사용
)
```

### 마이그레이션 가이드

기존 코드를 None 값 지원 버전으로 업그레이드하는 방법:

```python
# 기존 코드 (여전히 작동함)
old_machine = Machine(env, "M001", "기계", failure_probability=0.0)

# 새로운 코드 (더 명확함)
new_machine = Machine(env, "M001", "기계", failure_probability=None)
```

### 기본 사용법

```python
import simpy
from src.Resource.machine import Machine
from src.Resource.worker import Worker
from src.Resource.product import Product

def production_with_failures(env):
    # 고장확률이 있는 리소스 생성
    machine = Machine(
        env=env,
        machine_id="M001",
        machine_type="CNC",
        failure_probability=0.02,
        mean_time_to_repair=5.0
    )
    
    worker = Worker(
        env=env,
        worker_id="W001",
        skills=["조작"],
        error_probability=0.03,
        mean_rest_time=10.0
    )
    
    # 제품 생산
    for i in range(10):
        product = Product(f"P{i+1}", "제품A")
        
        # 작업자 작업
        yield env.process(worker.work(product, "준비", 2.0))
        
        # 기계 작업
        yield env.process(machine.operate(product, 5.0))
        
        yield env.timeout(1.0)  # 제품 간 간격

# 시뮬레이션 실행
env = simpy.Environment()
env.process(production_with_failures(env))
env.run(until=100)
```

### 통계 수집 예제

```python
def analyze_reliability(machine, worker):
    """신뢰성 분석"""
    
    # 기계 신뢰성
    machine_status = machine.get_status()
    print(f"기계 가용성: {machine_status['availability']:.2%}")
    print(f"기계 고장률: {machine_status['failure_rate']:.4f}/시간")
    
    # 작업자 신뢰성
    worker_status = worker.get_status()
    print(f"작업자 가용성: {worker_status['availability']:.2%}")
    print(f"작업자 실수율: {worker_status['error_rate']:.2%}")
    
    # MTBF (Mean Time Between Failures) 계산
    if machine_status['total_failures'] > 0:
        mtbf = env.now / machine_status['total_failures']
        print(f"평균 고장 간격(MTBF): {mtbf:.2f}시간")
```

## 고장확률 설정 가이드

### 기계 고장확률 설정

| 기계 유형 | failure_probability | mean_time_to_repair | 설명 |
|----------|-------------------|-------------------|------|
| 신형 CNC | 0.001 - 0.01 | 2-4 시간 | 매우 안정적 |
| 일반 밀링머신 | 0.01 - 0.05 | 4-8 시간 | 보통 수준 |
| 노후 장비 | 0.05 - 0.15 | 8-24 시간 | 자주 고장 |

### 작업자 실수확률 설정

| 기술 수준 | error_probability | mean_rest_time | 설명 |
|---------|-----------------|---------------|------|
| 숙련공 | 0.001 - 0.01 | 8-12 시간 | 매우 숙련 |
| 일반 작업자 | 0.01 - 0.05 | 10-15 시간 | 보통 수준 |
| 신입 | 0.05 - 0.2 | 15-20 시간 | 실수 빈번 |

## 주의사항

1. **확률값 범위**: 모든 확률값은 0.0 ~ 1.0 범위 내에서 설정
2. **현실성**: 실제 데이터를 기반으로 현실적인 값 설정
3. **시뮬레이션 시간**: 고장/실수가 관찰될 수 있는 충분한 시간으로 시뮬레이션 실행
4. **통계적 유의성**: 충분한 샘플 수를 확보하여 통계의 신뢰성 확보

## 확장 가능성

이 기본 구현을 바탕으로 다음과 같은 확장이 가능합니다:

- 시간대별 고장률 변화
- 사용량에 따른 고장률 증가
- 예방 정비 스케줄링
- 다양한 고장 유형별 처리
- 학습 효과에 따른 실수율 감소
