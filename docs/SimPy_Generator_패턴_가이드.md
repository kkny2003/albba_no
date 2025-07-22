# SimPy Generator 패턴 완벽 가이드

## SimPy의 핵심 개념

### Generator란?

Python의 Generator는 `yield` 키워드를 사용하여 값을 하나씩 생산하는 특별한 함수입니다. SimPy는 이 Generator를 활용하여 시뮬레이션의 시간 흐름을 제어합니다.

```python
def simple_generator():
    yield 1    # 첫 번째 값 반환 후 일시정지
    yield 2    # 두 번째 값 반환 후 일시정지
    yield 3    # 세 번째 값 반환 후 종료
```

### SimPy에서 Generator의 역할

SimPy에서 모든 프로세스는 Generator 함수여야 합니다. 이는 시뮬레이션 시간을 제어하기 위함입니다:

```python
import simpy

def manufacturing_process(env):
    print(f"시간 {env.now}: 공정 시작")
    yield env.timeout(5.0)  # 5시간 대기
    print(f"시간 {env.now}: 공정 완료")

env = simpy.Environment()
env.process(manufacturing_process(env))
env.run()
```

## 문제가 발생했던 패턴 분석

### 잘못된 패턴 1: Generator를 직접 반환

```python
# ❌ 잘못된 코드
class ManufacturingProcess(BaseProcess):
    def execute(self, input_data: Any = None) -> Any:  # 타입 힌트 문제
        return super().execute(input_data)  # Generator 객체를 직접 반환
```

**문제점:**
1. `super().execute()`가 Generator를 반환하지만, 이를 직접 return하면 Generator 객체가 됨
2. SimPy는 Generator 함수를 기대하는데 Generator 객체를 받게 됨
3. Generator 객체에는 `.callbacks` 속성이 없어서 AttributeError 발생

### 올바른 패턴: yield from 사용

```python
# ✅ 올바른 코드
class ManufacturingProcess(BaseProcess):
    def execute(self, input_data: Any = None) -> Generator[simpy.Event, None, Any]:
        # 전처리
        print(f"[{self.process_name}] 제조 공정 실행 시작")
        
        # 부모 클래스의 Generator를 올바르게 위임
        result = yield from super().execute(input_data)
        
        # 후처리
        return result
```

## yield from의 동작 원리

### 기본 개념

`yield from`은 Python 3.3에서 도입된 구문으로, 다른 Generator의 값들을 현재 Generator로 전달합니다.

```python
def inner_generator():
    yield 1
    yield 2
    return "inner result"

def outer_generator():
    result = yield from inner_generator()  # inner의 모든 yield를 전달
    print(f"Inner result: {result}")      # "inner result" 출력
    yield 3

# 사용 예시
gen = outer_generator()
for value in gen:
    print(value)  # 1, 2, 3 출력
```

### SimPy 컨텍스트에서의 yield from

```python
def base_process(env):
    print("Base process start")
    yield env.timeout(2.0)  # 2시간 대기
    print("Base process end")
    return "base result"

def derived_process(env):
    print("Derived process start")
    yield env.timeout(1.0)  # 1시간 대기
    
    # Base process의 모든 이벤트를 위임
    result = yield from base_process(env)
    
    print(f"Received: {result}")
    yield env.timeout(1.0)  # 추가로 1시간 대기
    print("Derived process end")
    return "derived result"
```

## 상속 구조에서의 Generator 패턴

### 계층 구조 예시

```
BaseProcess (추상 클래스)
├── execute() -> Generator[simpy.Event, None, Any]
│
├── ManufacturingProcess
│   └── execute() -> Generator[simpy.Event, None, Any]
│
├── AssemblyProcess  
│   └── execute() -> Generator[simpy.Event, None, Any]
│
└── QualityControlProcess
    └── execute() -> Generator[simpy.Event, None, Any]
```

### BaseProcess의 execute() 구현

```python
class BaseProcess(ABC):
    def execute(self, input_data: Any = None) -> Generator[simpy.Event, None, Any]:
        print(f"[시간 {self.env.now:.1f}] [{self.process_name}] 공정 실행 시작")
        
        # 1. 자원 검증
        self.validate_resources()
        
        # 2. 입력 자원 소비
        yield from self.consume_resources()
        
        # 3. 실제 공정 로직 실행 (하위 클래스에서 구현)
        result = yield from self.process_logic(input_data)
        
        # 4. 출력 자원 생산
        yield from self.produce_resources()
        
        return result
    
    @abstractmethod
    def process_logic(self, input_data: Any = None) -> Generator[simpy.Event, None, Any]:
        """하위 클래스에서 구현해야 하는 실제 공정 로직"""
        pass
```

### 하위 클래스의 올바른 구현

```python
class ManufacturingProcess(BaseProcess):
    def execute(self, input_data: Any = None) -> Generator[simpy.Event, None, Any]:
        # 제조공정 전용 전처리
        print(f"[{self.process_name}] 제조 공정 실행 시작")
        if input_data is not None:
            self.add_to_production_line(input_data)
        
        # 부모 클래스의 공통 로직 실행
        result = yield from super().execute(input_data)
        
        # 제조공정 전용 후처리
        print(f"[{self.process_name}] 제조 완료: {result}")
        return result
    
    def process_logic(self, input_data: Any = None) -> Generator[simpy.Event, None, Any]:
        """실제 제조 로직"""
        print(f"[시간 {self.env.now:.1f}] [{self.process_name}] 제조 로직 실행 중...")
        
        # 기계와 작업자 자원 요청
        with self.machine.request() as machine_req, \
             self.worker.request() as worker_req:
            
            # 모든 자원이 준비될 때까지 대기
            yield machine_req & worker_req
            
            # 실제 제조 작업 수행
            yield self.env.timeout(self.processing_time)
            
            print(f"[시간 {self.env.now:.1f}] [{self.process_name}] 제조 작업 완료")
            
        return f"제조완료_{self.process_name}"
```

## MultiProcessGroup에서의 Generator 활용

### 병렬 공정 처리

```python
class MultiProcessGroup:
    def execute(self, input_data: Any = None) -> Generator[simpy.Event, None, List[Any]]:
        if not self.processes:
            return []
            
        print(f"[시간 {self.env.now:.1f}] 다중공정 그룹 실행 시작")
        
        results = []
        for i, process in enumerate(self.processes, 1):
            print(f"  [시간 {self.env.now:.1f}] [{i}/{len(self.processes)}] {process.process_name} 실행 중...")
            
            # 각 공정을 순차적으로 실행 (SimPy Generator)
            result = yield from process.execute(input_data)
            results.append(result)
            
            print(f"  [시간 {self.env.now:.1f}] [OK] {process.process_name} 완료")
        
        print(f"[시간 {self.env.now:.1f}] 다중공정 그룹 실행 완료")
        return results
```

### 공정 체이닝 (>> 연산자)

```python
class ProcessChain:
    def execute(self, input_data: Any = None) -> Generator[simpy.Event, None, Any]:
        print(f"[시간 {self.env.now:.1f}] 공정 체인 실행 시작")
        
        current_data = input_data
        results = []
        
        for i, process in enumerate(self.chain_processes, 1):
            print(f"[시간 {self.env.now:.1f}] [{i}/{len(self.chain_processes)}] {process.process_name} 실행 중...")
            
            # 이전 공정의 결과를 다음 공정의 입력으로 사용
            result = yield from process.execute(current_data)
            results.append(result)
            current_data = result  # 체이닝
            
            print(f"[시간 {self.env.now:.1f}] [{i}/{len(self.chain_processes)}] {process.process_name} 완료")
        
        print(f"[시간 {self.env.now:.1f}] 공정 체인 실행 완료")
        return results[-1] if results else None
```

## 실제 사용 패턴

### 시뮬레이션 메인 프로세스

```python
def main_simulation(env):
    try:
        print(f"[Time {env.now:.1f}] 시뮬레이션 시작")
        
        # 공정 체인 생성: A1 >> A2 >> 품질검사 >> 조립
        chain = proc_a1 >> proc_a2 >> qc >> assembly
        
        # 병렬 그룹: 여러 체인 동시 실행
        group = MultiProcessGroup([chain, other_chain])
        
        # 전체 그룹 실행
        result = yield from group.execute()
        
        print(f"[Time {env.now:.1f}] 시뮬레이션 완료: {result}")
        
    except Exception as e:
        print(f"[Time {env.now:.1f}] 오류 발생: {e}")
        import traceback
        traceback.print_exc()

# 시뮬레이션 실행
env = simpy.Environment()
env.process(main_simulation(env))
env.run(until=100)
```

## 디버깅 팁

### 1. Generator 체인 확인

```python
def debug_generator_chain(gen):
    """Generator 체인이 올바른지 확인"""
    if not hasattr(gen, '__next__'):
        print(f"Warning: {gen}은 Generator가 아닙니다!")
        return False
    
    try:
        # 첫 번째 yield 확인
        first_yield = next(gen)
        print(f"First yield: {first_yield}")
        return True
    except StopIteration as e:
        print(f"Generator immediately finished with: {e.value}")
        return True
    except Exception as e:
        print(f"Generator error: {e}")
        return False
```

### 2. SimPy 이벤트 타입 확인

```python
def validate_simpy_event(event):
    """SimPy 이벤트가 올바른지 확인"""
    if hasattr(event, 'callbacks'):
        print(f"✓ Valid SimPy event: {type(event)}")
    else:
        print(f"✗ Invalid SimPy event: {type(event)} (no callbacks attribute)")
```

### 3. 공통 오류 패턴

```python
# ❌ 잘못된 패턴들
def wrong_pattern1(env):
    # Generator 함수가 아닌 일반 함수
    time.sleep(1)  # 절대 사용하지 말 것!
    return "result"

def wrong_pattern2(env):
    # yield 없이 return만 사용
    return env.timeout(1.0)  # Generator 객체를 반환

def wrong_pattern3(env):
    # yield from 없이 직접 호출
    result = other_process(env)  # Generator 함수를 직접 호출
    return result

# ✅ 올바른 패턴들
def correct_pattern1(env):
    # 올바른 SimPy 프로세스
    yield env.timeout(1.0)  # SimPy 이벤트를 yield
    return "result"

def correct_pattern2(env):
    # 다른 Generator 위임
    result = yield from other_generator_process(env)
    return result

def correct_pattern3(env):
    # 복합 패턴
    yield env.timeout(0.5)  # 전처리 대기
    result = yield from sub_process(env)  # 하위 프로세스 실행
    yield env.timeout(0.5)  # 후처리 대기
    return result
```

## 성능 고려사항

### 1. Generator 오버헤드

```python
# Generator 체인이 깊어질수록 약간의 오버헤드 발생
# 하지만 SimPy의 설계상 불가피하며, 실제 성능에는 큰 영향 없음

def deep_chain_example(env, depth=0):
    if depth > 100:  # 너무 깊은 재귀는 피하기
        yield env.timeout(0.1)
        return f"depth_{depth}"
    
    yield env.timeout(0.1)
    result = yield from deep_chain_example(env, depth + 1)
    return result
```

### 2. 메모리 사용량

```python
# Generator는 지연 평가되므로 메모리 효율적
# 하지만 결과를 모두 리스트에 저장하면 메모리 사용량 증가

def memory_efficient_processing(env, items):
    """메모리 효율적인 대량 아이템 처리"""
    for item in items:  # 한 번에 하나씩 처리
        yield env.timeout(0.1)
        result = yield from process_item(env, item)
        yield result  # 결과를 즉시 yield (메모리 절약)
```

## 결론

SimPy에서 Generator 패턴을 올바르게 사용하기 위한 핵심 포인트:

1. **모든 프로세스는 Generator 함수여야 함**
2. **상속에서는 `yield from super().execute()` 패턴 사용**
3. **타입 힌트는 `Generator[simpy.Event, None, ReturnType]` 형식**
4. **SimPy 이벤트만 yield하고, 일반 값은 return**
5. **예외 처리와 디버깅을 위한 적절한 로깅 추가**

이러한 패턴을 준수하면 복잡한 제조공정 시뮬레이션도 안정적으로 구현할 수 있습니다.
