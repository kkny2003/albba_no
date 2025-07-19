# 배치 처리 기능 가이드

## 개요

제조업 시뮬레이션 프레임워크에 배치 처리 기능이 추가되었습니다. 이 기능을 통해 여러 아이템을 한번에 효율적으로 처리하고 운송할 수 있습니다.

## 주요 기능

### 1. Process 배치 처리

#### BaseProcess 클래스의 배치 기능
- **batch_size**: 한번에 처리할 아이템 수를 설정
- **process_batch()**: 여러 아이템을 한번에 처리하는 메서드
- **batch_process_logic()**: 하위 클래스에서 오버라이드하여 배치 처리 로직 구현
- **add_to_batch()**: 배치에 아이템을 추가하고 처리 준비 여부 확인

#### 사용 예제
```python
import simpy
from src.processes.base_process import BaseProcess

class MyBatchProcess(BaseProcess):
    def __init__(self, env, process_name="배치공정", batch_size=5):
        super().__init__(env, process_name=process_name, batch_size=batch_size)
    
    def process_logic(self, input_data):
        """단일 아이템 처리 로직"""
        yield self.env.timeout(2.0)  # 처리 시간
        return f"processed_{input_data}"
    
    def batch_process_logic(self, batch_items):
        """배치 처리 로직 (더 효율적)"""
        # 배치 처리는 단위 시간이 더 짧음
        yield self.env.timeout(len(batch_items) * 1.5)
        return [f"batch_processed_{item}" for item in batch_items]

# 사용법
env = simpy.Environment()
process = MyBatchProcess(env, batch_size=5)

# 배치 처리
items = ["아이템1", "아이템2", "아이템3", "아이템4", "아이템5"]
results = yield from process.process_batch(items)
```

### 2. Transport 배치 처리

#### Transport 클래스의 배치 기능
- **enable_batch_transport**: 배치 운송 활성화 여부
- **transport_batch()**: 여러 제품을 한번에 운송하는 메서드
- **load_batch()**: 여러 제품을 한번에 적재
- **unload_batch()**: 모든 제품을 한번에 하역

#### 사용 예제
```python
import simpy
from src.Resource.transport import Transport

# 배치 운송 활성화
env = simpy.Environment()
transport = Transport(
    env=env,
    transport_id="배치트럭",
    capacity=10,
    transport_speed=2.0,
    enable_batch_transport=True
)

# 배치 운송
products = ["제품1", "제품2", "제품3", "제품4"]
distance = 15.0
success = yield from transport.transport_batch(products, distance)
```

## 배치 처리의 장점

### 1. 시간 효율성
- **Process**: 배치 처리시 단위 처리 시간이 단축됨
- **Transport**: 여러 제품을 한번에 운송하여 총 운송 시간 절약

### 2. 자원 효율성
- 운송 수단의 용량을 최대한 활용
- 배치 효율성 지표를 통한 성능 모니터링

### 3. 실제 성능 비교
시연 결과에 따르면:
- **Process 배치 처리**: 25% 시간 절약 (10.0시간 → 7.5시간)
- **Transport 배치 운송**: 66.7% 시간 절약 (15.0시간 → 5.0시간)

## 실행 가능한 예제

### 1. 간단한 배치 시연
```bash
python examples/simple_batch_demo.py
```

이 예제는 다음을 시연합니다:
- 단일 처리 vs 배치 처리 비교
- 단일 운송 vs 배치 운송 비교
- 시간 효율성 측정

### 2. 고급 배치 처리 (향후 구현 예정)
```bash
python examples/batch_processing_example.py
```

## API 참조

### BaseProcess 배치 관련 메서드

#### `__init__(env, process_id=None, process_name=None, batch_size=1)`
- **batch_size**: 배치 크기 설정 (기본값: 1)

#### `process_batch(batch_items: List[Any]) -> Generator[simpy.Event, None, List[Any]]`
- 여러 아이템을 한번에 처리
- **인자**: batch_items - 처리할 아이템들의 리스트
- **반환**: 처리된 결과들의 리스트

#### `batch_process_logic(batch_items: List[Any]) -> Generator[simpy.Event, None, List[Any]]`
- 배치 처리 로직 (하위 클래스에서 오버라이드)
- 기본 구현은 각 아이템을 개별적으로 처리

#### `add_to_batch(item: Any) -> bool`
- 배치에 아이템 추가
- **반환**: 배치가 가득 찼는지 여부

#### `get_batch_status() -> Dict[str, Any]`
- 배치 처리 상태 정보 반환

### Transport 배치 관련 메서드

#### `__init__(env, transport_id, capacity=10, transport_speed=1.0, enable_batch_transport=True)`
- **enable_batch_transport**: 배치 운송 활성화 여부

#### `transport_batch(products: List[Any], distance: float) -> Generator[simpy.Event, None, bool]`
- 여러 제품을 한번에 운송
- **인자**: 
  - products - 운송할 제품들의 리스트
  - distance - 운송 거리
- **반환**: 운송 성공 여부

#### `load_batch(products: List[Any]) -> bool`
- 여러 제품을 한번에 적재
- **반환**: 적재 성공 여부

#### `unload_batch() -> List[Any]`
- 모든 제품을 한번에 하역
- **반환**: 하역된 제품들의 리스트

#### `get_batch_status() -> Dict[str, Any]`
- 배치 운송 상태 정보 반환

## 모니터링 및 성능 지표

### Process 배치 지표
- **batch_size**: 설정된 배치 크기
- **current_batch_count**: 현재 배치에 축적된 아이템 수
- **batch_utilization**: 배치 활용률

### Transport 배치 지표
- **batch_transport_count**: 배치 운송 횟수
- **average_batch_efficiency**: 평균 배치 효율성 (적재율)
- **load_utilization**: 현재 적재 활용률

## 주의사항

1. **용량 제한**: Transport의 경우 capacity를 초과하지 않도록 주의
2. **배치 크기**: Process의 batch_size는 실제 작업량에 맞게 조정
3. **호환성**: 기존 단일 처리 방식과 완전히 호환됨 (batch_size=1로 설정시)

## 향후 개선 계획

1. **동적 배치 크기**: 실시간으로 배치 크기를 조정하는 기능
2. **우선순위 배치**: 우선순위에 따른 배치 처리
3. **부분 배치**: 배치가 가득 차지 않아도 시간 제한으로 처리하는 기능
4. **배치 스케줄링**: 최적의 배치 처리 스케줄 생성
