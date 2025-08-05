# 분리된 Transport 아키텍처 가이드

## 개요
ManufacturingProcess, ResourceManager, TransportProcess 간의 책임을 명확히 분리한 새로운 아키텍처입니다.

## 아키텍처 구조

### 역할 분담
```
┌─────────────────────┐    요청    ┌─────────────────────┐    할당    ┌─────────────────────┐
│  ManufacturingProcess │ ────────► │   ResourceManager   │ ────────► │  TransportProcess   │
│                     │            │                     │            │                     │
│ • 제조 공정 실행     │            │ • 운송 요청 관리     │            │ • 실제 운송 처리     │
│ • 운송 요청만 보냄   │            │ • TransportProcess   │            │ • 4단계 운송 프로세스│
│                     │            │   할당 및 실행       │            │ • 운송 상태 관리     │
└─────────────────────┘            └─────────────────────┘            └─────────────────────┘
```

## 각 컴포넌트의 책임

### 1. ManufacturingProcess
**책임**: 제조 공정 실행 + 운송 요청만 보냄

```python
# 제조 완료 후 운송 요청
if self.auto_transport_enabled and self.resource_manager:
    yield from self.request_transport_for_output(output_resources)
```

**주요 변경사항**:
- TransportProcess를 직접 호출하지 않음
- ResourceManager에게 운송 요청만 보냄
- 운송 처리 결과를 기다리지 않음 (비동기)

### 2. ResourceManager
**책임**: 운송 요청 관리 + TransportProcess 할당 및 실행

```python
# TransportProcess 등록
resource_manager.register_transport_process("transport_main", transport_process)

# Transport 요청 특별 처리
if resource_id == "transport":
    allocation_id = yield from self._handle_transport_request(...)
```

**새로운 기능**:
- `register_transport_process()`: TransportProcess 등록
- `_handle_transport_request()`: Transport 요청 특별 처리
- `_execute_transport_process()`: TransportProcess 백그라운드 실행

### 3. TransportProcess
**책임**: 실제 운송 처리만 담당

```python
# 4단계 운송 프로세스
yield self.env.timeout(self.loading_time)    # 적재
yield self.env.timeout(self.transport_time)  # 운송
yield self.env.timeout(self.unloading_time)  # 하역
yield self.env.timeout(self.cooldown_time)   # 대기
```

**변경사항 없음**: 기존 TransportProcess 그대로 사용

## 실행 흐름

### 1. 시스템 초기화
```python
# 1. ResourceManager 생성
resource_manager = AdvancedResourceManager(env)

# 2. Transport 자원 등록
resource_manager.register_resource("transport", capacity=2, ...)

# 3. TransportProcess 생성
transport_process = TransportProcess(...)

# 4. ResourceManager에 TransportProcess 등록
resource_manager.register_transport_process("transport_main", transport_process)

# 5. ManufacturingProcess 생성 (ResourceManager 연동)
manufacturing = ManufacturingProcess(..., resource_manager=resource_manager)
```

### 2. 제조 + 운송 실행 흐름
```
[제조공정 실행]
└─ ManufacturingProcess.process_logic()
   ├─ 제조 로직 실행 (2.0시간)
   └─ request_transport_for_output() 호출
      └─ ResourceManager.request_resource_with_priority("transport", ...)
         └─ _handle_transport_request() 실행
            ├─ 사용 가능한 TransportProcess 찾기
            ├─ SimPy PriorityResource로 자원 할당
            └─ _execute_transport_process() 백그라운드 실행
               └─ TransportProcess.process_logic() 실행
                  ├─ 적재 (0.3시간)
                  ├─ 운송 (1.5시간)  
                  ├─ 하역 (0.2시간)
                  └─ 대기 (0.2시간)
```

### 3. 타이밍 다이어그램
```
시간 →  0.0    2.0    2.3    3.8    4.0    4.2
제조    |------|                              
운송           |-----|-----|-----|-----|
               적재  운송   하역  대기
```

## 코드 예제

### 기본 사용법
```python
import simpy
from src.core.resource_manager import AdvancedResourceManager
from src.Processes.manufacturing_process import ManufacturingProcess
from src.Processes.transport_process import TransportProcess

# 환경 및 ResourceManager 생성
env = simpy.Environment()
resource_manager = AdvancedResourceManager(env)

# Transport 자원 등록
resource_manager.register_resource("transport", capacity=2, 
                                  resource_type=ResourceType.TRANSPORT)

# TransportProcess 생성
transport_process = TransportProcess(
    env=env, process_id="transport_001", process_name="운송공정",
    machines=[transport_vehicle], workers=[transport_worker],
    input_resources={"완제품": 1.0}, output_resources={"배송완료": 1.0},
    resource_requirements=requirements,
    loading_time=0.3, transport_time=1.5, 
    unloading_time=0.2, cooldown_time=0.2
)

# ResourceManager에 TransportProcess 등록
resource_manager.register_transport_process("main_transport", transport_process)

# ManufacturingProcess 생성 (분리된 구조)
manufacturing = ManufacturingProcess(
    env=env, process_id="mfg_001", process_name="제조공정",
    machines=[machine], workers=[worker],
    input_resources=input_res, output_resources=output_res,
    resource_requirements=mfg_requirements,
    resource_manager=resource_manager  # 운송 요청용
)

# 제조 실행 (운송은 자동으로 처리됨)
yield from manufacturing.process_logic(input_data)
```

### 상태 모니터링
```python
# ManufacturingProcess 상태
mfg_status = manufacturing.get_transport_status()
print(f"운송 모드: {mfg_status['transport_mode']}")  # 'request_only'

# ResourceManager Transport 관리 상태
rm_status = resource_manager.get_transport_status()
print(f"등록된 TransportProcess: {rm_status['registered_transports']}개")
print(f"Transport 자원 사용률: {rm_status['transport_resource_status']}")
```

## 장점

### 1. 명확한 책임 분리
- **ManufacturingProcess**: 제조만 담당, 운송은 요청만
- **ResourceManager**: 운송 요청 관리 및 스케줄링
- **TransportProcess**: 순수 운송 로직만 담당

### 2. 확장성
```python
# 여러 TransportProcess 등록 가능
resource_manager.register_transport_process("forklift", forklift_process)
resource_manager.register_transport_process("truck", truck_process)
resource_manager.register_transport_process("conveyor", conveyor_process)

# 하나의 TransportProcess를 여러 제조공정에서 공유
manufacturing1 = ManufacturingProcess(..., resource_manager=resource_manager)
manufacturing2 = ManufacturingProcess(..., resource_manager=resource_manager)
manufacturing3 = ManufacturingProcess(..., resource_manager=resource_manager)
```

### 3. 비동기 처리
- 제조공정은 운송 요청 후 즉시 다음 작업 진행 가능
- 운송은 백그라운드에서 독립적으로 실행
- 운송 완료를 기다리지 않아도 됨

### 4. 유지보수성
```python
# 운송 로직 변경 시 TransportProcess만 수정
transport_process.loading_time = 0.5  # 적재 시간 변경
transport_process.set_route("새로운 경로")  # 경로 변경

# 제조공정 코드는 변경 불필요
```

### 5. 테스트 용이성
```python
# 각 컴포넌트를 독립적으로 테스트
def test_manufacturing_only():
    # 운송 없이 제조만 테스트
    manufacturing = ManufacturingProcess(..., resource_manager=None)
    
def test_transport_only():
    # 제조 없이 운송만 테스트
    yield from transport_process.process_logic(test_data)
    
def test_resource_management():
    # ResourceManager의 할당 로직만 테스트
    allocation_id = yield from resource_manager.request_resource_with_priority(...)
```

## 설정 옵션

### ManufacturingProcess 설정
```python
manufacturing = ManufacturingProcess(
    # 기본 제조 설정
    env=env, process_id="mfg_001", process_name="제조공정",
    machines=[machine], workers=[worker],
    
    # 분리된 구조 설정
    resource_manager=resource_manager,     # 운송 요청용 (필수)
    transport_process=transport_process    # 참조용 (선택적)
)

# 런타임 설정 변경
manufacturing.set_transport_settings(new_resource_manager)
manufacturing.enable_auto_transport(True)
```

### ResourceManager 설정
```python
resource_manager = AdvancedResourceManager(env)

# Transport 자원 등록
resource_manager.register_resource("transport", capacity=3)

# 여러 TransportProcess 등록
resource_manager.register_transport_process("fast", fast_transport)
resource_manager.register_transport_process("heavy", heavy_transport)

# TransportProcess 등록 해제
resource_manager.unregister_transport_process("fast")
```

## 예제 파일
- **분리된 구조 예제**: `examples/scenario_separated_transport_architecture.py`
- **통합 구조 예제**: `examples/scenario_manufacturing_with_transport_process.py` (참고용)

## 마이그레이션 가이드

### 기존 코드에서 분리된 구조로 변경
1. **ResourceManager에 TransportProcess 등록**:
   ```python
   resource_manager.register_transport_process("main", transport_process)
   ```

2. **ManufacturingProcess 생성 시 ResourceManager만 전달**:
   ```python
   # 이전: transport_process 직접 전달
   ManufacturingProcess(..., transport_process=transport_process)
   
   # 현재: resource_manager 전달
   ManufacturingProcess(..., resource_manager=resource_manager)
   ```

3. **운송 처리 방식 변경**:
   - 이전: ManufacturingProcess가 TransportProcess 직접 호출
   - 현재: ManufacturingProcess가 ResourceManager에 요청, ResourceManager가 TransportProcess 실행

이 분리된 구조를 사용하면 더 모듈화되고 확장 가능한 시뮬레이션 시스템을 구축할 수 있습니다.
