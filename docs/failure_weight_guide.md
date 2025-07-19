# 공정별 고장률 가중치 기능 가이드

## 개요

이 기능을 통해 각 공정(Process)에서 기계(Machine)와 작업자(Worker)의 고장률에 가중치를 적용할 수 있습니다. 예를 들어, 특정 공정이 기계에 더 많은 부담을 주거나 작업자에게 더 어려운 작업을 요구하는 경우, 고장률을 높게 설정할 수 있습니다.

## 주요 특징

- **공정별 독립적 가중치**: 각 공정마다 다른 가중치 설정 가능
- **자동 적용/복원**: 공정 실행 시 자동으로 가중치 적용, 완료 후 원래값 복원
- **안전한 범위**: 고장률은 최대 1.0(100%)을 넘지 않음
- **기계와 작업자 분리**: 기계 고장률과 작업자 실수율을 독립적으로 제어

## 사용법

### 1. 기본 공정 생성 시 가중치 지정

```python
import simpy
from src.processes.manufacturing_process import ManufacturingProcess
from src.Resource.machine import Machine
from src.Resource.worker import Worker

# SimPy 환경 생성
env = simpy.Environment()

# 기계와 작업자 생성
machine = Machine(env, "M001", "CNC 가공기", failure_probability=0.1)
worker = Worker(env, "W001", ["가공"], error_probability=0.05)

# 가중치를 적용한 제조 공정 생성
manufacturing_proc = ManufacturingProcess(
    env=env,
    machines=[machine],
    workers=[worker],
    input_resources=input_resources,
    output_resources=output_resources,
    resource_requirements=resource_requirements,
    process_name="고위험 가공 공정",
    failure_weight_machine=1.5,  # 기계 고장률 1.5배 증가
    failure_weight_worker=2.0     # 작업자 실수율 2.0배 증가
)
```

### 2. 조립 공정에서의 가중치 적용

```python
from src.processes.assembly_process import AssemblyProcess

# 조립 공정에서 가중치 적용
assembly_proc = AssemblyProcess(
    env=env,
    machines=[assembly_machine],
    workers=[assembly_worker],
    input_resources=parts_list,
    output_resources=assembled_product,
    resource_requirements=assembly_requirements,
    process_name="정밀 조립 공정",
    failure_weight_machine=1.2,  # 기계 고장률 1.2배 증가
    failure_weight_worker=1.8     # 작업자 실수율 1.8배 증가
)
```

## 가중치 계산 방식

### 기계 고장률 계산
```
새로운_고장률 = min(1.0, 원래_고장률 × 가중치)
```

**예시:**
- 원래 고장률: 0.15 (15%)
- 가중치: 1.5
- 적용된 고장률: 0.225 (22.5%)

### 작업자 실수율 계산
```
새로운_실수율 = min(1.0, 원래_실수율 × 가중치)
```

**예시:**
- 원래 실수율: 0.10 (10%)
- 가중치: 2.0
- 적용된 실수율: 0.20 (20%)

## 가중치 적용 타이밍

1. **공정 실행 시작**: `execute()` 메소드 호출 시 가중치가 자동 적용
2. **공정 실행 중**: 가중치가 적용된 고장률/실수율로 시뮬레이션 진행
3. **공정 실행 완료**: 원래 고장률/실수율로 자동 복원

```python
# 공정 실행 예시
def production_process():
    for i in range(5):
        product = Product(f"제품_{i+1}")
        
        # 가중치가 자동으로 적용되고 복원됨
        result = yield env.process(manufacturing_proc.execute(product))
        
        yield env.timeout(1.0)  # 다음 작업까지 대기
```

## 실제 사용 시나리오

### 시나리오 1: 고온 가공 공정
```python
# 고온에서 작업하는 공정 - 기계에 부담이 큼
hot_process = ManufacturingProcess(
    env=env,
    machines=[furnace_machine],
    workers=[heat_resistant_worker],
    # ... 기타 파라미터 ...
    failure_weight_machine=2.0,  # 고온으로 인한 기계 고장률 증가
    failure_weight_worker=1.0     # 작업자는 보호장비로 정상
)
```

### 시나리오 2: 정밀 조립 공정  
```python
# 매우 정밀한 조립 작업 - 작업자 실수 가능성 높음
precision_assembly = AssemblyProcess(
    env=env,
    machines=[precision_machine],
    workers=[skilled_worker],
    # ... 기타 파라미터 ...
    failure_weight_machine=1.1,  # 기계는 약간의 부담
    failure_weight_worker=1.8     # 작업자 실수율 크게 증가
)
```

### 시나리오 3: 야간 작업 공정
```python
# 야간 근무로 인한 피로도 증가
night_shift_process = ManufacturingProcess(
    env=env,
    machines=[night_machine],
    workers=[night_worker],
    # ... 기타 파라미터 ...
    failure_weight_machine=1.2,  # 야간 유지보수 부족
    failure_weight_worker=1.5     # 피로로 인한 실수 증가
)
```

## 주의사항

1. **가중치 범위**: 일반적으로 0.5 ~ 3.0 사이의 값을 권장
2. **현실성**: 과도하게 높은 가중치는 비현실적인 결과를 초래할 수 있음
3. **성능**: 가중치 적용/복원은 자동으로 처리되므로 별도 관리 불필요
4. **복원 보장**: `try-finally` 구조로 예외 발생 시에도 원래값 복원 보장

## 모니터링 및 디버깅

가중치 적용 과정은 로그로 확인할 수 있습니다:

```
[공정명] 기계 M001 고장률 적용: 0.150 → 0.225 (가중치: 1.5)
[공정명] 작업자 W001 실수율 적용: 0.100 → 0.150 (가중치: 1.5)
...
[공정명] 기계 M001 고장률 복원
[공정명] 작업자 W001 실수율 복원
```

## 예제 파일

전체 예제는 `examples/failure_weight_example.py`에서 확인할 수 있습니다:
```bash
python examples/failure_weight_example.py
```

이 예제는 다양한 가중치 조합의 효과를 비교하여 보여줍니다.
