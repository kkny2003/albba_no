# 출하품 Transport Blocking 기능 가이드

## 개요
공정에서 생산된 출하품이 transport에 의해 옮겨져야만 다음 공정이 진행될 수 있도록 하는 blocking 기능입니다. 이는 실제 제조업에서 버퍼가 가득 차면 공정이 멈추는 현실적인 시뮬레이션을 제공합니다.

## 핵심 특징

### 1. 배치 크기와 출력 버퍼 크기 동기화
- **출력 버퍼 크기 = 배치 크기**
- 한 번의 배치 처리가 완료되면 출력 버퍼가 가득 참
- Transport가 출하품을 옮겨야만 다음 배치 처리 가능

### 2. Blocking 메커니즘
- 출력 버퍼가 가득 차면 공정이 자동으로 멈춤
- SimPy Event를 이용한 대기 상태 진입
- Transport 완료 시 공정 자동 재개

## 주요 속성들

```python
# 출하품 관리 속성들
self.output_buffer_capacity: int        # 출력 버퍼 최대 용량 (= batch_size)
self.current_output_count: int          # 현재 출력 버퍼에 쌓인 개수  
self.enable_output_blocking: bool       # 출력 blocking 활성화 여부
self.transport_ready_event: simpy.Event # 운송 준비 완료 이벤트
self.waiting_for_transport: bool        # 운송 대기 상태
```

## 핵심 메서드들

### 1. 배치 및 버퍼 크기 관리
```python
# 배치 크기 설정 (출력 버퍼도 자동 동기화)
process.set_batch_size(5)  # 배치=5, 출력버퍼=5

# 출력 버퍼 크기만 개별 설정 (권장하지 않음)
process.set_output_buffer_capacity(10)
```

### 2. Blocking 기능 제어
```python
# Blocking 기능 활성화/비활성화
process.enable_output_blocking_feature(True)   # 활성화 (기본값)
process.enable_output_blocking_feature(False)  # 비활성화
```

### 3. 출하품 Transport 관리
```python
# 출하품 운송 (공정 재개 신호 포함)
transported_count = process.transport_output_items(3)  # 3개 운송
transported_count = process.transport_output_items()   # 모든 아이템 운송

# 버퍼 상태 확인
status = process.get_output_buffer_status()
# {
#     'current_count': 5,
#     'capacity': 5, 
#     'utilization_rate': 1.0,
#     'is_full': True,
#     'waiting_for_transport': True,
#     'blocking_enabled': True
# }

# 버퍼가 가득 찬지 확인
if process.is_output_buffer_full():
    print("출력 버퍼 가득참! Transport 필요")
```

## 동작 시나리오

### 시나리오 1: 정상적인 공정 흐름

```python
# 1. 초기 상태
process = ManufacturingProcess(...)
process.set_batch_size(3)  # 배치=3, 출력버퍼=3

# 2. 첫 번째 배치 처리 (3개 생산)
yield from process.execute(input_data)
# 결과: current_output_count = 3, 버퍼 가득참

# 3. Transport 실행
transported = process.transport_output_items()  # 3개 운송
# 결과: current_output_count = 0, 공정 재개 가능

# 4. 두 번째 배치 처리 가능
yield from process.execute(input_data)
```

### 시나리오 2: Transport 지연으로 인한 Blocking

```python
# 1. 배치 처리 완료로 버퍼 가득참
yield from process.execute(input_data)
# 결과: 출력 버퍼 가득참 (3/3)

# 2. Transport 없이 다음 공정 시도
try:
    yield from process.execute(input_data)  # ← 여기서 blocking!
except:
    print("출력 버퍼 가득참으로 공정 대기 중...")

# 3. Transport 수행 후 공정 재개
process.transport_output_items()  # 운송 완료
# 자동으로 대기 중인 공정이 재개됨
```

## 실제 사용 예시

### ManufacturingProcess에서 활용

```python
import simpy
from src.processes.manufacturing_process import ManufacturingProcess

# 1. 환경 및 공정 생성
env = simpy.Environment()
manufacturing = ManufacturingProcess(
    env=env,
    process_id='PROC001', 
    process_name='제조공정',
    machines=[machine],
    workers=[worker],
    input_resources=input_res,
    output_resources=output_res,
    resource_requirements=requirements,
    batch_size=5  # 배치=5, 출력버퍼=5
)

# 2. Transport 프로세스 정의
def transport_process(env, manufacturing_proc):
    while True:
        # 출력 버퍼가 가득 찰 때까지 대기
        yield env.timeout(3.0)  # 3시간마다 운송
        
        if manufacturing_proc.is_output_buffer_full():
            count = manufacturing_proc.transport_output_items()
            print(f"운송 완료: {count}개")

# 3. 시뮬레이션 실행
def main_process(env, manufacturing_proc):
    for i in range(10):
        yield from manufacturing_proc.execute(f"제품_{i}")
        print(f"제품_{i} 처리 완료")

# 프로세스 시작
env.process(main_process(env, manufacturing))
env.process(transport_process(env, manufacturing))
env.run(until=50)
```

### Transport와 연동된 공정 체이닝

```python
# 1. 두 공정 간 Transport 연동
manufacturing = ManufacturingProcess(...)  # 배치=3
assembly = AssemblyProcess(...)             # 배치=3

# 2. Transport 연동 함수
def connect_with_transport(source_process, target_process, transport_interval=2.0):
    def transport_runner(env):
        while True:
            yield env.timeout(transport_interval)
            
            # 출발지에서 출하품 수집
            if source_process.current_output_count > 0:
                items_count = source_process.transport_output_items()
                print(f"운송: {source_process.process_name} → {target_process.process_name} ({items_count}개)")
                
                # 목적지로 전달 (여기서는 단순화)
                # 실제로는 target_process의 input_buffer에 추가하는 로직 필요
    
    return transport_runner

# 3. Transport 프로세스 시작
env.process(connect_with_transport(manufacturing, assembly)(env))
```

## 성능 및 최적화 팁

### 1. 배치 크기 최적화
- **작은 배치**: 빠른 반응성, 높은 운송 빈도
- **큰 배치**: 효율적인 처리, 낮은 운송 빈도

```python
# 반응성 우선 (실시간 처리)
process.set_batch_size(1)  # 즉시 처리, 즉시 운송 필요

# 효율성 우선 (배치 처리)  
process.set_batch_size(10)  # 10개씩 모아서 처리, 운송 효율성 증대
```

### 2. Transport 주기 조정
- 출력 버퍼 크기와 transport 주기의 균형이 중요
- 너무 긴 주기: 공정 대기 시간 증가
- 너무 짧은 주기: 운송 비효율성 증가

### 3. 상태 모니터링
```python
# 정기적인 상태 확인
def monitor_process_status(process, interval=5.0):
    while True:
        yield env.timeout(interval)
        
        buffer_status = process.get_output_buffer_status()
        print(f"[{process.process_name}] 버퍼 상태: {buffer_status['current_count']}/{buffer_status['capacity']} "
              f"(사용률: {buffer_status['utilization_rate']:.1%})")
        
        if buffer_status['waiting_for_transport']:
            print(f"⚠️ {process.process_name} 운송 대기 중!")
```

## 주의사항

1. **Blocking 비활성화**: `enable_output_blocking_feature(False)` 사용 시 무제한 생산 가능
2. **Event 처리**: SimPy Event는 한 번만 사용 가능하므로 자동으로 재생성됨
3. **동기화**: 배치 크기 변경 시 출력 버퍼 크기도 자동 동기화됨
4. **강제 초기화**: `clear_output_buffer()` 사용 시 대기 중인 공정도 강제 재개됨

## 결론

이 기능을 통해 실제 제조업의 버퍼 제약과 운송 의존성을 정확히 시뮬레이션할 수 있습니다. 출하품이 적절히 운송되지 않으면 공정이 자연스럽게 멈추고, 운송이 완료되면 자동으로 재개되는 현실적인 시뮬레이션을 제공합니다.
