# 제조공정 Transport 자동 요청 기능 가이드

## 개요
제조공정이 완료되면 자동으로 resource_manager에 transport 요청을 보내고, transport가 할당되면 출하품을 운송하는 기능입니다.

## 주요 기능

### 1. 자동 Transport 요청
- 제조공정 완료 후 자동으로 transport 자원 요청
- resource_manager를 통한 우선순위 기반 transport 할당
- 운송 거리 및 시간 계산 기반 스케줄링

### 2. 통합된 출하품 관리
- BaseProcess의 출력 버퍼 기능과 연동
- 운송 완료 후 자동으로 출력 버퍼에서 제품 제거
- Transport blocking 기능 지원

### 3. 유연한 설정 옵션
- 자동 transport 활성화/비활성화
- 운송 거리 및 우선순위 설정
- resource_manager 동적 변경 가능

## 코드 구조

### ManufacturingProcess 클래스 확장
```python
class ManufacturingProcess(BaseProcess):
    def __init__(self, ..., resource_manager=None, transport_distance=10.0):
        # resource_manager: transport 할당을 위한 자원 관리자
        # transport_distance: 운송 거리 (운송 시간 계산용)
        
    def process_logic(self, input_data=None):
        # 1. 제조 로직 실행
        # 2. 제조 완료 후 자동 transport 요청
        # 3. transport 할당되면 출하품 운송
```

### 핵심 메서드

#### request_transport_for_output()
- 출하품을 위한 transport 자원 요청
- resource_manager의 우선순위 기반 할당 활용
- SimPy generator 방식으로 비동기 처리

#### handle_transport_output()
- 할당된 transport를 사용한 출하품 운송
- 운송 시간 계산 및 시뮬레이션
- 출력 버퍼 관리 연동

#### set_transport_settings()
- transport 설정 동적 변경
- resource_manager, 거리, 자동 활성화 설정

## 사용 방법

### 1. 기본 설정
```python
# resource_manager 생성 및 transport 등록
resource_manager = AdvancedResourceManager(env)
resource_manager.register_resource("transport", capacity=3, resource_type=ResourceType.TRANSPORT)

# ManufacturingProcess 생성 (자동 transport 활성화)
manufacturing = ManufacturingProcess(
    env=env,
    process_id="mfg_001", 
    process_name="제조공정1",
    machines=[machine1],
    workers=[worker1],
    input_resources=input_res,
    output_resources=output_res,
    resource_requirements=requirements,
    resource_manager=resource_manager,  # 자동 transport 요청용
    transport_distance=15.0             # 운송 거리
)
```

### 2. 공정 실행
```python
# 제조공정 실행 - 완료 후 자동으로 transport 요청
def run_manufacturing():
    yield from manufacturing.process_logic(input_data)
    
env.process(run_manufacturing())
env.run(until=100)
```

### 3. 동적 설정 변경
```python
# transport 설정 변경
manufacturing.set_transport_settings(
    resource_manager=new_resource_manager,
    distance=20.0,
    auto_enable=True
)

# 자동 transport 기능만 비활성화
manufacturing.enable_auto_transport(False)

# 상태 조회
status = manufacturing.get_transport_status()
print(f"자동 운송: {status['auto_transport_enabled']}")
```

## 실행 흐름

### 1. 제조공정 실행
```
[시간 0.0] 제조공정1 제조 로직 시작
[시간 0.0] 자원 소비 처리
[시간 2.0] 제조 처리 완료
[시간 2.0] 자원 생산 완료
[시간 2.0] 제조공정1 제조 로직 완료
```

### 2. Transport 요청 및 할당
```
[시간 2.0] 제조공정1 출하품 Transport 요청 시작
[시간 2.0] 제조공정1 Transport 자원 요청 중...
[시간 2.0] 우선순위 자원 요청: transport by mfg_001 (우선순위: 7)
[시간 2.0] 자원 할당 완료: transport to mfg_001 (할당 ID: abc-123)
[시간 2.0] 제조공정1 Transport 할당 성공 (할당 ID: abc-123)
```

### 3. 출하품 운송
```
[시간 2.0] 제조공정1 출하품 운송 시작 (거리: 15.0)
[시간 17.0] 제조공정1 출하품 운송 완료 (소요시간: 15.0)
[시간 17.0] 제조공정1 출력 버퍼에서 제품 제거 (남은 개수: 0)
```

## 주요 특징

### 1. SimPy 호환성
- SimPy generator 패턴을 따르는 비동기 처리
- SimPy 이벤트 기반 스케줄링
- resource_manager의 우선순위 기반 자원 할당 활용

### 2. BaseProcess 통합
- BaseProcess의 출력 버퍼 기능 활용
- 기존 배치 처리 및 blocking 기능과 호환
- 표준화된 자원 관리 인터페이스 사용

### 3. 유연한 확장성
- 다양한 transport 타입 지원 가능
- 운송 거리별 차등 우선순위 설정 가능
- 동적 설정 변경 및 모니터링 지원

### 4. 에러 처리
- resource_manager 없음 시 graceful degradation
- transport 할당 실패 시 안전한 처리
- 예외 상황에 대한 상세한 로깅

## 확장 가능성

### 1. 다중 Transport 타입
```python
# 운송 타입별 차등 요청
def request_specific_transport(self, transport_type="forklift"):
    resource_id = f"transport_{transport_type}"
    yield from self.resource_manager.request_resource_with_priority(...)
```

### 2. 거리별 우선순위
```python
# 거리가 짧을수록 높은 우선순위
def calculate_priority_by_distance(self):
    base_priority = 7
    distance_factor = min(5, self.transport_distance / 10.0)
    return max(1, base_priority - distance_factor)
```

### 3. 배치 운송
```python
# 여러 제품을 한번에 운송
def batch_transport_request(self, batch_products):
    for product in batch_products:
        yield from self.request_transport_for_output(product)
```

이 기능을 통해 제조공정에서 출하품이 생성되면 자동으로 transport가 할당되어 효율적인 물류 관리가 가능합니다.
