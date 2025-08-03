# Processes 모듈 상세 설명

## 개요

Processes 모듈은 제조 시뮬레이션 프레임워크의 핵심 구성 요소로, SimPy 기반의 다양한 제조 공정을 정의하고 관리하는 기능을 제공합니다. 이 모듈은 확장 가능한 아키텍처를 통해 제조 공정의 복잡한 워크플로우를 모델링할 수 있도록 설계되었습니다.

## 파일 구조

```
src/Processes/
├── __init__.py              # 모듈 초기화 및 API 노출
├── base_process.py          # 기본 프로세스 클래스 및 체인 관리
├── manufacturing_process.py # 제조 공정 구현
├── assembly_process.py      # 조립 공정 구현
├── quality_control_process.py # 품질 관리 공정 구현
├── transport_process.py     # 운송 공정 구현
└── advanced_workflow.py     # 고급 워크플로우 관리
```

## 핵심 클래스 구조

### 1. BaseProcess (추상 클래스)

**위치**: `base_process.py`

**역할**: 모든 프로세스의 기본 클래스로, 공통 기능과 인터페이스를 정의합니다.

#### 주요 기능

- **자원 관리**: 기계, 작업자, 입력/출력 자원 관리
- **배치 처리**: 여러 항목을 한 번에 처리하는 배치 기능
- **실행 조건**: 프로세스 실행 조건 설정 및 검증
- **우선순위**: 실행 우선순위 관리
- **연결 연산자**: `>>` 연산자를 통한 프로세스 체인 연결
- **그룹 연산자**: `&` 연산자를 통한 병렬 그룹 생성

#### 핵심 메서드

```python
@abstractmethod
def process_logic(self, input_data: Any = None) -> Generator[simpy.Event, None, Any]:
    """구체적인 프로세스 로직을 구현해야 하는 추상 메서드"""

def execute(self, input_data: Any = None) -> Generator[simpy.Event, None, Any]:
    """프로세스 실행의 메인 진입점"""

def __rshift__(self, other) -> ProcessChain:
    """프로세스 체인 연결 (>> 연산자)"""

def __and__(self, other) -> MultiProcessGroup:
    """병렬 그룹 생성 (& 연산자)"""
```

### 2. ProcessChain

**위치**: `base_process.py`

**역할**: 여러 프로세스를 순차적으로 연결하여 실행하는 체인 관리자

#### 주요 기능

- **순차 실행**: 프로세스들을 순서대로 실행
- **데이터 전달**: 이전 프로세스의 출력을 다음 프로세스의 입력으로 전달
- **체인 관리**: 프로세스 추가, 제거, 순서 변경

#### 사용 예시

```python
# 프로세스 체인 생성
chain = ProcessChain([process1, process2, process3])

# 또는 >> 연산자 사용
chain = process1 >> process2 >> process3

# 체인 실행
result = yield from chain.execute(input_data)
```

### 3. MultiProcessGroup

**위치**: `base_process.py`

**역할**: 여러 프로세스를 병렬로 실행하는 그룹 관리자

#### 주요 기능

- **병렬 실행**: 여러 프로세스를 동시에 실행
- **우선순위 관리**: 프로세스별 실행 우선순위 설정
- **결과 수집**: 모든 프로세스의 결과를 수집하여 반환

#### 사용 예시

```python
# 병렬 그룹 생성
group = MultiProcessGroup([process1, process2, process3])

# 또는 & 연산자 사용
group = process1 & process2 & process3

# 그룹 실행
results = yield from group.execute(input_data)
```

## 구체적인 프로세스 구현

### 1. ManufacturingProcess

**위치**: `manufacturing_process.py`

**역할**: 제조 공정을 모델링하는 클래스

#### 주요 특징

- **생산 라인 관리**: 제품이 처리되는 생산 라인 추적
- **처리 시간**: 제조에 필요한 시간 설정
- **자원 요구사항**: 원자재, 기계, 작업자 등 필요한 자원 정의

#### 핵심 메서드

```python
def process_logic(self, input_data: Any = None) -> Generator[simpy.Event, None, Any]:
    """제조 공정의 핵심 로직"""
    # 1. 자원 소비
    if not self.consume_resources(input_data):
        raise Exception("필요한 자원이 부족합니다")
    
    # 2. 제조 처리 시간 대기
    yield self.env.timeout(self.processing_time)
    
    # 3. 자원 생산
    output_resources = self.produce_resources(input_data)
    
    return output_resources
```

### 2. AssemblyProcess

**위치**: `assembly_process.py`

**역할**: 조립 공정을 모델링하는 클래스

#### 주요 특징

- **조립 라인 관리**: 조립 중인 제품 추적
- **반제품 처리**: 여러 반제품을 조립하여 완제품 생성
- **도구 요구사항**: 조립에 필요한 도구 관리

#### 핵심 메서드

```python
def process_logic(self, input_data: Any = None) -> Generator[simpy.Event, None, Any]:
    """조립 공정의 핵심 로직"""
    # 1. 반제품 확인
    if not self._validate_semi_finished_products(input_data):
        raise Exception("조립에 필요한 반제품이 부족합니다")
    
    # 2. 조립 처리 시간 대기
    yield self.env.timeout(self.assembly_time)
    
    # 3. 완제품 생성
    assembled_product = self._create_finished_product(input_data)
    
    return assembled_product
```

### 3. QualityControlProcess

**위치**: `quality_control_process.py`

**역할**: 품질 관리 공정을 모델링하는 클래스

#### 주요 특징

- **검사 기준**: 품질 검사 기준 정의 및 관리
- **검사 결과**: 검사된 항목의 품질 상태 추적
- **불량품 처리**: 불량품 식별 및 처리 로직

#### 핵심 메서드

```python
def process_logic(self, input_data: Any = None) -> Generator[simpy.Event, None, Any]:
    """품질 관리 공정의 핵심 로직"""
    # 1. 검사 대상 확인
    if not self._validate_inspection_target(input_data):
        raise Exception("검사 대상이 유효하지 않습니다")
    
    # 2. 검사 처리 시간 대기
    yield self.env.timeout(self.inspection_time)
    
    # 3. 품질 평가
    quality_result = self.evaluate_quality(input_data)
    
    return quality_result
```

### 4. TransportProcess

**위치**: `transport_process.py`

**역할**: 운송 공정을 모델링하는 클래스

#### 주요 특징

- **경로 관리**: 출발지에서 도착지까지의 운송 경로 정의
- **운송 단계**: 적재 → 운송 → 하역의 단계별 처리
- **운송 수단**: 다양한 운송 수단 지원

#### 핵심 메서드

```python
def process_logic(self, input_data: Any = None) -> Generator[simpy.Event, None, Any]:
    """운송 공정의 핵심 로직"""
    # 1. 적재 시간
    yield self.env.timeout(self.loading_time)
    
    # 2. 운송 시간
    yield self.env.timeout(self.transport_time)
    
    # 3. 하역 시간
    yield self.env.timeout(self.unloading_time)
    
    # 4. 대기 시간 (다음 운송 준비)
    yield self.env.timeout(self.cooldown_time)
    
    return input_data  # 운송된 자원 반환
```

## 고급 워크플로우 관리

### AdvancedWorkflowManager

**위치**: `advanced_workflow.py`

**역할**: 복잡한 워크플로우를 관리하는 고급 기능 제공

#### 주요 기능

- **실행 모드**: 순차, 병렬, 조건부 실행 지원
- **동기화**: 프로세스 간 동기화 포인트 관리
- **리소스 제한**: 동시 실행 프로세스 수 제한
- **결과 추적**: 각 프로세스의 실행 결과 및 통계 수집

#### 핵심 클래스

```python
class ExecutionMode(Enum):
    SEQUENTIAL = "sequential"    # 순차 실행
    PARALLEL = "parallel"       # 병렬 실행
    CONDITIONAL = "conditional" # 조건부 실행

class SynchronizationType(Enum):
    ALL_COMPLETE = "all_complete"  # 모든 프로세스 완료 대기
    ANY_COMPLETE = "any_complete"  # 하나만 완료되면 진행
    THRESHOLD = "threshold"        # 임계값만큼 완료되면 진행
```

## 우선순위 시스템

### 우선순위 파싱

**위치**: `base_process.py`

**기능**: 프로세스명에서 우선순위를 추출하는 기능

#### 사용법

```python
# 프로세스명에 우선순위 포함
process1 = ManufacturingProcess(env, machines, workers, process_name="제조공정(1)")
process2 = ManufacturingProcess(env, machines, workers, process_name="제조공정(2)")

# 우선순위 파싱
name, priority = parse_process_priority("제조공정(1)")  # ("제조공정", 1)
```

#### 우선순위 규칙

1. n개의 공정이 있을 때, 우선순위는 1부터 n까지
2. 모든 공정에 우선순위가 있거나, 모든 공정에 우선순위가 없어야 함
3. 중복된 우선순위는 허용되지 않음

## 자원 관리 시스템

### 자원 요구사항

각 프로세스는 다음과 같은 자원 요구사항을 정의할 수 있습니다:

- **입력 자원**: 프로세스 실행에 필요한 자원
- **출력 자원**: 프로세스 실행 후 생성되는 자원
- **자원 요구사항**: 특정 타입과 수량의 자원 필요성

### 자원 타입

```python
class ResourceType(Enum):
    MACHINE = "machine"           # 기계
    WORKER = "worker"             # 작업자
    RAW_MATERIAL = "raw_material" # 원자재
    SEMI_FINISHED = "semi_finished" # 반제품
    FINISHED_PRODUCT = "finished_product" # 완제품
    TOOL = "tool"                 # 도구
    TRANSPORT = "transport"       # 운송 수단
```

## 사용 예시

### 기본 프로세스 체인 생성

```python
# 1. 개별 프로세스 생성
manufacturing = ManufacturingProcess(env, machines, workers, 
                                   input_resources, output_resources, requirements)
assembly = AssemblyProcess(env, machines, workers,
                          input_resources, output_resources, requirements)
quality_check = QualityControlProcess(env, inspection_criteria,
                                     input_resources, output_resources, requirements)

# 2. 프로세스 체인 생성
production_chain = manufacturing >> assembly >> quality_check

# 3. 체인 실행
result = yield from production_chain.execute(input_data)
```

### 병렬 프로세스 그룹 생성

```python
# 1. 병렬 실행할 프로세스들
process1 = ManufacturingProcess(env, machines, workers, process_name="제조공정(1)")
process2 = ManufacturingProcess(env, machines, workers, process_name="제조공정(2)")
process3 = ManufacturingProcess(env, machines, workers, process_name="제조공정(3)")

# 2. 병렬 그룹 생성
parallel_group = process1 & process2 & process3

# 3. 그룹 실행
results = yield from parallel_group.execute(input_data)
```

### 복합 워크플로우

```python
# 1. 복잡한 워크플로우 구성
workflow = (manufacturing >> assembly) & (transport >> quality_check)

# 2. 고급 워크플로우 매니저 사용
workflow_manager = AdvancedWorkflowManager(env)
workflow_manager.register_process_chain(workflow)

# 3. 워크플로우 실행
result = yield from workflow_manager.execute_workflow(product, workflow_steps)
```

## 코드 이해를 위한 읽기 순서

1. **`__init__.py`**: 모듈의 전체 구조와 API 파악
2. **`base_process.py`**: 
   - `BaseProcess` 클래스 (라인 568-1283): 모든 프로세스의 기본 클래스
   - `ProcessChain` 클래스 (라인 108-240): 순차 실행 관리
   - `MultiProcessGroup` 클래스 (라인 241-567): 병렬 실행 관리
   - `GroupWrapperProcess` 클래스 (라인 1284-1337): 그룹 래핑
3. **`manufacturing_process.py`**: 제조 공정 구현 예시
4. **`assembly_process.py`**: 조립 공정 구현 예시
5. **`quality_control_process.py`**: 품질 관리 공정 구현 예시
6. **`transport_process.py`**: 운송 공정 구현 예시
7. **`advanced_workflow.py`**: 고급 워크플로우 관리 기능

## 확장성

이 모듈은 다음과 같은 방식으로 확장할 수 있습니다:

1. **새로운 프로세스 타입**: `BaseProcess`를 상속받아 새로운 프로세스 클래스 생성
2. **커스텀 로직**: `process_logic` 메서드를 오버라이드하여 특정 비즈니스 로직 구현
3. **새로운 연산자**: `__rshift__`, `__and__` 외에 추가 연산자 정의 가능
4. **고급 기능**: `AdvancedWorkflowManager`를 확장하여 더 복잡한 워크플로우 지원

이 모듈은 제조 시뮬레이션의 복잡한 요구사항을 유연하고 확장 가능한 방식으로 처리할 수 있도록 설계되었습니다. 