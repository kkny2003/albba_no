# Machine/Worker 필수 요구사항 가이드

## 개요

프레임워크의 모든 제조 공정(`BaseProcess`를 상속하는 클래스)에는 **machine 또는 worker 중 하나 이상이 필수로 있어야 합니다**. 이는 현실적인 제조 환경을 반영한 설계입니다.

## 핵심 요구사항

- ✅ **machine만 있는 공정**: 완전 자동화 공정 (예: 무인 CNC 가공)
- ✅ **worker만 있는 공정**: 수작업 공정 (예: 수동 조립, 품질 검사)
- ✅ **machine과 worker가 모두 있는 공정**: 반자동화 공정 (예: 기계 조작 + 인간 감독)
- ❌ **machine도 worker도 없는 공정**: 불가능 (ValueError 발생)

## 구현된 변경사항

### 1. BaseProcess 클래스 수정

```python
class BaseProcess(ABC):
    def __init__(self, env: simpy.Environment, machines=None, workers=None, 
                 process_id: str = None, process_name: str = None, batch_size: int = 1):
        # machine 또는 worker 중 하나는 필수로 있어야 함
        if machines is None and workers is None:
            raise ValueError(f"공정 '{process_name or self.__class__.__name__}'에는 machine 또는 worker 중 하나 이상이 필요합니다.")
        
        # 기계와 작업자 설정
        self.machines = machines or []
        self.workers = workers or []
        # ... 나머지 초기화 코드
```

### 2. 검증 메서드 추가

```python
def validate_resources(self) -> bool:
    """공정에 필요한 자원(machine/worker)이 올바르게 설정되었는지 검증"""
    if not self.machines and not self.workers:
        raise ValueError(f"공정 '{self.process_name}'에는 machine 또는 worker 중 하나 이상이 필요합니다.")
    return True

def add_machine(self, machine) -> 'BaseProcess':
    """공정에 기계를 추가"""
    
def add_worker(self, worker) -> 'BaseProcess':
    """공정에 작업자를 추가"""

def get_available_machines(self):
    """현재 사용 가능한 기계 목록을 반환"""
    
def get_available_workers(self):
    """현재 사용 가능한 작업자 목록을 반환"""
```

### 3. 실행 시 검증 추가

```python
def execute(self, input_data: Any = None) -> Generator[simpy.Event, None, Any]:
    """공정 실행 시 필수 자원 검증"""
    # 1. 필수 자원(machine/worker) 검증
    try:
        self.validate_resources()
    except ValueError as e:
        print(f"공정 실행 실패: {e}")
        return None
    # ... 나머지 실행 로직
```

## 사용 예시

### 1. 기계만 사용하는 공정

```python
import simpy
from src.Resource.machine import Machine
from src.processes.manufacturing_process import ManufacturingProcess

# SimPy 환경 및 기계 생성
env = simpy.Environment()
cnc_machine = Machine(env, "CNC001", "CNC_MACHINE", capacity=1, processing_time=2.0)

# 기계만 사용하는 제조 공정 생성
process = ManufacturingProcess(
    env=env,
    machines=[cnc_machine],  # 기계만 사용
    workers=None,            # 작업자 없음
    input_resources=input_res,
    output_resources=output_res,
    resource_requirements=requirements,
    process_name="자동화가공공정"
)
```

### 2. 작업자만 사용하는 공정

```python
from src.Resource.worker import Worker
from src.processes.assembly_process import AssemblyProcess

# 작업자 생성
skilled_worker = Worker(env, "W001", ["조립", "검사"], work_speed=1.2)

# 작업자만 사용하는 조립 공정 생성
process = AssemblyProcess(
    env=env,
    machines=None,              # 기계 없음
    workers=[skilled_worker],   # 작업자만 사용
    input_resources=input_res,
    output_resources=output_res,
    resource_requirements=requirements,
    process_name="수작업조립공정"
)
```

### 3. 기계와 작업자를 모두 사용하는 공정

```python
from src.processes.quality_control_process import QualityControlProcess

# 기계와 작업자 생성
inspection_machine = Machine(env, "IM001", "INSPECTION_MACHINE")
quality_inspector = Worker(env, "QI001", ["품질검사", "데이터분석"])

# 기계와 작업자를 모두 사용하는 품질관리 공정 생성
process = QualityControlProcess(
    env=env,
    inspection_criteria={"tolerance": 0.01},
    input_resources=input_res,
    output_resources=output_res,
    resource_requirements=requirements,
    workers=[quality_inspector],    # 작업자 사용
    machines=[inspection_machine],  # 기계도 사용
    process_name="자동화품질검사공정"
)
```

### 4. 잘못된 공정 생성 (오류 발생)

```python
# 기계도 작업자도 없는 공정 생성 시도
try:
    invalid_process = ManufacturingProcess(
        env=env,
        machines=None,  # 기계 없음
        workers=None,   # 작업자도 없음
        input_resources=input_res,
        output_resources=output_res,
        resource_requirements=requirements,
        process_name="불가능한공정"
    )
except ValueError as e:
    print(f"오류: {e}")
    # 출력: "오류: 공정 '불가능한공정'에는 machine 또는 worker 중 하나 이상이 필요합니다."
```

## 동적 자원 관리

공정 생성 후에도 기계나 작업자를 추가할 수 있습니다:

```python
# 공정 생성 (기계만으로 시작)
process = ManufacturingProcess(env, machines=[machine], workers=None, ...)

# 나중에 작업자 추가
new_worker = Worker(env, "W002", ["품질관리"])
process.add_worker(new_worker)

# 기계 추가
new_machine = Machine(env, "M002", "BACKUP_MACHINE")
process.add_machine(new_machine)

# 사용 가능한 자원 확인
available_machines = process.get_available_machines()
available_workers = process.get_available_workers()
```

## 이점

1. **현실성**: 실제 제조 환경을 더 정확히 반영
2. **안전성**: 필수 자원 없는 공정 생성 방지
3. **유연성**: 다양한 제조 방식 지원 (자동화/수작업/반자동화)
4. **확장성**: 기계와 작업자를 동적으로 추가/관리 가능
5. **검증**: 공정 실행 시 자원 유효성 자동 검증

## 테스트 확인

구현된 기능은 다음 테스트로 검증되었습니다:

- ✅ 기계만 있는 공정 생성 및 실행
- ✅ 작업자만 있는 공정 생성 및 실행  
- ✅ 기계+작업자 공정 생성 및 실행
- ✅ 기계/작업자 없는 공정 생성 시 오류 발생
- ✅ 다중 제품 처리 시뮬레이션
- ✅ 동적 자원 추가/관리

이제 모든 제조 공정에서 **machine 또는 worker 중 하나는 필수로 있어야 한다**는 요구사항이 프레임워크 레벨에서 강제됩니다.
