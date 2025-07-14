# 공정 연결 기능 (Process Chaining)

## 개요

이 기능을 사용하면 `>>` 연산자를 통해 직관적으로 제조 공정들을 연결할 수 있습니다.

## 기본 사용법

### 1. 공정 인스턴스 생성

```python
from src.processes import ManufacturingProcess, AssemblyProcess, QualityControlProcess

# 기계와 작업자 목록
machines = ["CNC기계1", "용접기1", "프레스1"]
workers = ["작업자A", "작업자B", "작업자C"]

# 공정 인스턴스 생성
manufacturing = ManufacturingProcess(
    machines=machines[:2], 
    workers=workers[:2], 
    process_id="P001",
    process_name="원료가공공정"
)

assembly = AssemblyProcess(
    machines=machines[1:], 
    workers=workers[1:], 
    process_id="P002",
    process_name="부품조립공정"
)

quality_control = QualityControlProcess(
    inspection_criteria={"강도": "> 100N"}, 
    process_id="P003",
    process_name="품질검사공정"
)
```

### 2. 공정 연결

#### 방법 1: 두 공정 직접 연결
```python
chain = manufacturing >> assembly
print(chain)  # ProcessChain(원료가공공정 → 부품조립공정)
```

#### 방법 2: 여러 공정 연쇄 연결
```python
chain = manufacturing >> assembly >> quality_control
print(chain)  # ProcessChain(원료가공공정 → 부품조립공정 → 품질검사공정)
```

#### 방법 3: 기존 체인에 공정 추가
```python
additional_process = AssemblyProcess(machines, workers, "P004", "포장공정")
extended_chain = chain >> additional_process
```

### 3. 공정 체인 실행

```python
# 전체 체인 실행
sample_product = "샘플제품A"
result = chain.execute_chain(sample_product)
```

### 4. 공정 연결 정보 확인

```python
# 공정 연결 상태 확인
info = manufacturing.get_process_info()
print(f"다음 공정: {info['next_processes']}")
print(f"이전 공정: {info['previous_processes']}")
```

## 주요 특징

1. **직관적인 문법**: `공정1 >> 공정2 >> 공정3` 형태로 자연스러운 흐름 표현
2. **체인 관리**: 연결된 공정들을 `ProcessChain` 객체로 관리
3. **순차 실행**: 체인의 모든 공정을 순서대로 실행 가능
4. **연결 추적**: 각 공정의 이전/다음 공정 관계 자동 관리
5. **확장성**: 기존 체인에 새로운 공정이나 체인 추가 가능

## 지원되는 공정 클래스

- `ManufacturingProcess`: 제조 공정
- `AssemblyProcess`: 조립 공정  
- `QualityControlProcess`: 품질 관리 공정
- 모든 `BaseProcess`를 상속받는 사용자 정의 공정

## 실행 예제

전체 예제는 `examples/process_chain_example.py`에서 확인할 수 있습니다:

```bash
python -m examples.process_chain_example
```

## 확장 방법

새로운 공정 타입을 추가하려면 `BaseProcess`를 상속받아 `execute` 메서드를 구현하면 됩니다:

```python
from src.processes.base_process import BaseProcess

class CustomProcess(BaseProcess):
    def __init__(self, custom_params, process_id=None, process_name=None):
        super().__init__(process_id, process_name or "사용자정의공정")
        self.custom_params = custom_params
    
    def execute(self, input_data=None):
        # 공정 실행 로직 구현
        print(f"[{self.process_name}] 사용자 정의 공정 실행")
        return input_data
```

이제 `CustomProcess`도 `>>` 연산자를 사용하여 다른 공정들과 연결할 수 있습니다.
