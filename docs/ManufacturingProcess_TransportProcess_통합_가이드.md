# ManufacturingProcess와 TransportProcess 통합 가이드

## 개요
ManufacturingProcess에서 자체 구현된 transport 로직 대신 기존의 `TransportProcess` 클래스를 활용하여 출하품을 운송하는 방법을 설명합니다.

## 변경 사항 요약

### 이전 방식 (자체 구현)
```python
# resource_manager를 통한 transport 자원 요청
allocation_id = yield from self.resource_manager.request_resource_with_priority(...)
# 간단한 timeout으로 운송 시뮬레이션
yield self.env.timeout(transport_time)
```

### 새로운 방식 (TransportProcess 활용)
```python
# TransportProcess 인스턴스를 직접 활용
yield from self.transport_process.process_logic(output_products)
# 4단계 운송 프로세스: 적재 → 운송 → 하역 → 대기
```

## 주요 장점

### 1. 모듈화된 구조
- 제조 공정과 운송 공정이 명확히 분리
- 각 공정의 책임이 명확함
- 코드 중복 제거

### 2. TransportProcess의 모든 기능 활용
- **4단계 운송 프로세스**: 적재(loading) → 운송(transport) → 하역(unloading) → 대기(cooldown)
- **배치 처리**: 여러 제품을 한번에 운송
- **우선순위 설정**: 운송 작업의 우선순위 관리
- **경로 설정**: 출발지-도착지 경로 정보
- **상태 모니터링**: 실시간 운송 상태 추적

### 3. 재사용성
- 하나의 TransportProcess를 여러 ManufacturingProcess에서 공유 가능
- 다른 공정 유형에서도 동일한 TransportProcess 활용 가능

### 4. 확장성
- TransportProcess의 설정만 변경하여 다양한 운송 시나리오 지원
- 운송 시간, 배치 크기, 경로 등을 유연하게 조정

## 사용 방법

### 1. TransportProcess 생성
```python
# 운송 공정 생성
transport_process = TransportProcess(
    env=env,
    process_id="transport_001",
    process_name="출하품_운송공정",
    machines=[transport_vehicle],
    workers=[transport_worker],
    input_resources={"완제품": 1.0},
    output_resources={"배송완료": 1.0},
    resource_requirements=transport_requirements,
    loading_time=0.5,    # 적재 시간 (30분)
    transport_time=2.0,  # 운송 시간 (2시간)
    unloading_time=0.5,  # 하역 시간 (30분)
    cooldown_time=0.5,   # 대기 시간 (30분)
    products_per_cycle=1
)

# 운송 경로 설정
transport_process.set_route("제조공장 → 배송센터")
```

### 2. ManufacturingProcess에 연동
```python
# 제조 공정 생성 시 TransportProcess 연동
manufacturing_process = ManufacturingProcess(
    env=env,
    process_id="mfg_001",
    process_name="제조공정1",
    machines=[machine],
    workers=[worker],
    input_resources=manufacturing_input,
    output_resources=manufacturing_output,
    resource_requirements=manufacturing_requirements,
    processing_time=2.0,
    transport_process=transport_process  # TransportProcess 연동
)
```

### 3. 자동 운송 실행
```python
# 제조공정 실행 - 완료 후 자동으로 TransportProcess 실행
yield from manufacturing_process.process_logic(input_data)
```

## 실행 흐름

### 제조 + 운송 통합 프로세스
```
[시간 0.0] 제조공정1 제조 로직 시작
[시간 0.0] 자원 소비 처리
[시간 2.0] 제조 처리 완료
[시간 2.0] 자원 생산 완료
[시간 2.0] 제조공정1 제조 로직 완료

[시간 2.0] 제조공정1 TransportProcess를 통한 출하품 운송 시작
[시간 2.0] 출하품_운송공정 적재 중... (소요시간: 0.5)
[시간 2.5] 출하품_운송공정 운송 중... (소요시간: 2.0)
[시간 4.5] 출하품_운송공정 하역 중... (소요시간: 0.5)
[시간 5.0] 출하품_운송공정 대기 중... (소요시간: 0.5)
[시간 5.5] 출하품_운송공정 운송 로직 완료

[시간 5.5] 제조공정1 TransportProcess를 통한 운송 완료
[시간 5.5] 제조공정1 출력 버퍼에서 제품 제거 (남은 개수: 0)
```

## 고급 기능

### 1. 동적 TransportProcess 설정
```python
# 런타임에 TransportProcess 변경
new_transport = TransportProcess(...)
manufacturing_process.set_transport_process(new_transport)

# 자동 운송 기능 비활성화
manufacturing_process.enable_auto_transport(False)
```

### 2. 배치 운송
```python
# 여러 제품을 배치로 운송
batch_products = [product1, product2, product3]
yield from manufacturing_process.request_batch_transport(batch_products)
```

### 3. 상태 모니터링
```python
# 통합 상태 조회
status = manufacturing_process.get_transport_status()
print(f"TransportProcess 연동: {status['has_transport_process']}")
print(f"운송 경로: {status['transport_process_info']['route']}")
print(f"총 운송시간: {status['transport_process_info']['loading_time'] + 
                     status['transport_process_info']['transport_time'] + 
                     status['transport_process_info']['unloading_time'] + 
                     status['transport_process_info']['cooldown_time']}")

# TransportProcess 상태 직접 조회
queue_status = transport_process.get_transport_queue_status()
print(f"운송 대기열: {len(queue_status['items_in_queue'])}개")
print(f"운송 상태: {queue_status['transport_status']}")
```

### 4. 운송 우선순위 및 조건 설정
```python
# TransportProcess에 운송 우선순위 설정
transport_process.set_transport_priority(8)  # 높은 우선순위

# 운송 실행 조건 추가
def urgent_delivery_condition():
    return env.now > 10.0  # 10시간 후에만 운송

transport_process.add_transport_condition(urgent_delivery_condition)
```

## 구조적 차이점

### 자체 구현 방식
```
ManufacturingProcess
├── process_logic()
├── request_transport_for_output()    # 자체 구현
├── handle_transport_output()         # 자체 구현
└── resource_manager 연동             # 단순 자원 요청
```

### TransportProcess 활용 방식
```
ManufacturingProcess
├── process_logic()
├── execute_transport_with_transport_process()  # TransportProcess 활용
└── transport_process
    ├── process_logic()               # 4단계 운송 프로세스
    ├── add_to_transport_queue()      # 배치 관리
    ├── set_transport_priority()      # 우선순위 관리
    └── get_transport_queue_status()  # 상태 모니터링
```

## 설정 옵션

### TransportProcess 설정
```python
transport_process = TransportProcess(
    # 기본 설정
    env=env,
    process_id="transport_001",
    process_name="운송공정",
    
    # 자원 설정
    machines=[transport_vehicle],
    workers=[transport_worker],
    
    # 운송 시간 설정
    loading_time=0.5,     # 적재 시간
    transport_time=2.0,   # 실제 운송 시간
    unloading_time=0.5,   # 하역 시간
    cooldown_time=0.3,    # 다음 운송 준비 시간
    
    # 배치 설정
    products_per_cycle=1  # 한 번에 운송할 제품 수
)

# 운송 배치 크기 설정
transport_process.set_transport_batch_size(5)  # 5개씩 배치 처리

# 운송 경로 설정
transport_process.set_route("공장A → 창고B → 배송센터C")
```

## 예제 파일
- **기본 예제**: `examples/scenario_manufacturing_with_transport_process.py`
- **기존 자체 구현**: `examples/scenario_manufacturing_transport.py` (참고용)

## 마이그레이션 가이드

### 기존 코드에서 새로운 방식으로 변경
1. **생성자 변경**: `transport_distance` → `transport_process`
2. **메서드 호출 변경**: `request_transport_for_output()` → `execute_transport_with_transport_process()`
3. **TransportProcess 인스턴스 생성 및 설정**
4. **테스트 및 검증**

이 방식을 사용하면 더 구조화되고 확장 가능한 제조+운송 시스템을 구축할 수 있습니다.
