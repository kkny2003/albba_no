# Priority 기능 분리 완료 가이드

## 수정 개요

SimPy 제조공정 시뮬레이션 프레임워크에서 Priority(우선순위) 관련 기능을 기본 공정에서 분리하여, 복잡한 다중공정이나 조립공정에서만 사용하도록 구조를 개선하였습니다.

## 주요 변경사항

### 1. BaseProcess 클래스 수정

**제거된 기능들:**
- `execution_priority` 속성 제거
- `set_execution_priority()` 메서드 제거  
- `get_process_info()`에서 execution_priority 반환 부분 제거

**이유:**
- 단순한 제조공정에서는 우선순위 기능이 불필요
- 코드 복잡성 감소 및 성능 향상
- 책임 분리 원칙 적용

### 2. TransportProcess 클래스 수정

**제거된 기능들:**
- `set_transport_priority()` 메서드 제거

**변경 이유:**
- BaseProcess에서 set_execution_priority가 제거되어 호출할 수 없음
- Transport 공정에서는 우선순위보다 효율성이 더 중요

### 3. QualityControlProcess 클래스 수정

**제거된 기능들:**
- `set_inspection_priority()` 메서드 제거

**변경 이유:**
- BaseProcess에서 set_execution_priority가 제거되어 호출할 수 없음
- 품질 검사는 순서대로 진행되는 것이 일반적

### 4. AssemblyProcess 클래스 강화

**추가된 기능들:**
- `execution_priority` 속성 (조립공정용)
- `assembly_step_priorities` 속성 (조립 단계별 우선순위)
- `set_execution_priority()` 메서드
- `set_assembly_step_priority()` 메서드  
- `get_execution_priority()` 메서드

**추가 이유:**
- 조립공정은 복잡한 다단계 프로세스로 우선순위 관리가 필요
- 부품간 조립 순서가 제품 품질에 영향을 미침

## 우선순위 기능이 필요한 경우

### 1. 다중공정 (MultiProcessGroup)

```python
from src.Flow.multi_group_flow import MultiProcessGroup

# 다중공정 그룹에서 우선순위 사용
group = MultiProcessGroup([process1, process2, process3])
group.set_process_priority(process1, 1)  # 가장 높은 우선순위
group.set_process_priority(process2, 2)
group.set_process_priority(process3, 3)
```

### 2. 조립공정 (AssemblyProcess)

```python
from src.Processes.assembly_process import AssemblyProcess

# 조립공정에서 우선순위 사용
assembly = AssemblyProcess(...)
assembly.set_execution_priority(8)  # 높은 우선순위 설정
assembly.set_assembly_step_priority("전처리", 1)
assembly.set_assembly_step_priority("본조립", 2)
assembly.set_assembly_step_priority("후처리", 3)
```

## 마이그레이션 가이드

### 기존 코드에서 사용하던 경우

**Before (더 이상 사용 불가):**
```python
# BaseProcess, TransportProcess, QualityControlProcess에서
process.set_execution_priority(5)  # ❌ 오류 발생
transport.set_transport_priority(3)  # ❌ 오류 발생  
quality.set_inspection_priority(7)  # ❌ 오류 발생
```

**After (권장 방법):**
```python
# 1. 다중공정이 필요한 경우
from src.Flow.multi_group_flow import MultiProcessGroup
group = MultiProcessGroup([process1, process2])
group.set_process_priority(process1, 1)

# 2. 조립공정인 경우
from src.Processes.assembly_process import AssemblyProcess
assembly_process.set_execution_priority(5)  # ✅ 사용 가능

# 3. 단순 공정인 경우
# 우선순위 기능 없이 순차적으로 실행 (권장)
```

## 기술적 이점

### 1. 성능 향상
- 단순한 공정에서 불필요한 우선순위 계산 제거
- 메모리 사용량 감소
- 실행 속도 향상

### 2. 코드 명확성
- 각 공정의 책임이 명확해짐
- 복잡한 기능은 필요한 곳에만 존재
- 디버깅 및 유지보수 용이성 증대

### 3. 확장성
- 새로운 공정 타입 추가 시 필요한 기능만 구현
- 기본 공정은 단순하게 유지
- 고급 기능은 특화된 공정에서 제공

## Flow 모듈에서의 Priority 지원

Flow 모듈의 `multi_group_flow.py`에서는 여전히 완전한 Priority 기능을 제공합니다:

- `parse_process_priority()`: 공정명에서 우선순위 파싱
- `validate_priority_sequence()`: 우선순위 유효성 검사
- `PriorityValidationError`: 우선순위 오류 예외
- `MultiProcessGroup`: 우선순위 기반 다중공정 실행

## 결론

이번 변경으로 SimPy 제조공정 시뮬레이션 프레임워크는 다음과 같은 구조를 가지게 되었습니다:

- **BaseProcess**: 기본적인 공정 기능만 제공 (단순성 추구)
- **AssemblyProcess**: 복잡한 조립공정에 특화된 우선순위 기능 제공
- **MultiProcessGroup**: 다중공정 관리 및 우선순위 기반 실행 지원

각 공정 타입의 목적에 맞는 기능만 제공하여 코드의 명확성과 성능을 동시에 확보할 수 있습니다.
