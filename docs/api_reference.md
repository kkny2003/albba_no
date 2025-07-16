# API Reference Documentation

이 문서는 제조 공정 시뮬레이션 프레임워크의 API에 대한 참조 문서입니다. 각 모듈과 클래스의 기능 및 사용법을 상세히 설명합니다.

## 1. Core Module (핵심 모듈)

### 1.1 SimulationEngine

- **클래스**: `SimulationEngine`
- **설명**: SimPy 기반 시뮬레이션 엔진. 시뮬레이션의 실행 및 관리를 담당합니다.
- **초기화**:
  ```python
  def __init__(self, env=None, random_seed: Optional[int] = None)
  ```
- **주요 메서드**:
  - `add_process(process_func, *args, **kwargs)`: 시뮬레이션에 프로세스를 추가합니다.
  - `add_resource(name: str, resource: simpy.Resource)`: 시뮬레이션에 리소스를 등록합니다.
  - `get_resource(name: str)`: 등록된 리소스를 가져옵니다.
  - `run(until: Union[int, float] = None)`: 시뮬레이션을 실행합니다.
  - `get_results()`: 시뮬레이션 결과를 반환합니다.

### 1.2 ResourceManager

- **클래스**: `ResourceManager`
- **설명**: 복잡한 자원 할당 및 해제를 관리하는 고급 자원 관리자입니다.
- **주요 메서드**:
  - `allocate_resources(requirements: List[ResourceRequirement])`: 필요한 자원들을 할당합니다.
  - `release_resources(allocated_resources: List[Resource])`: 할당된 자원들을 해제합니다.
  - `add_resource(resource: Resource)`: 자원을 풀에 추가합니다.
  - `remove_resource(resource_id: str)`: 자원을 풀에서 제거합니다.
  - `get_available_resources(resource_type: ResourceType)`: 사용 가능한 자원 목록을 반환합니다.

### 1.3 DataCollector

- **클래스**: `DataCollector`
- **설명**: 시뮬레이션 데이터를 수집하고 저장하는 데이터 수집기입니다.
- **주요 메서드**:
  - `collect_data(name: str, value: Any, timestamp: float = None)`: 데이터를 수집합니다.
  - `get_data(name: str = None)`: 수집된 데이터를 반환합니다.
  - `save_to_csv(filename: str)`: 데이터를 CSV 파일로 저장합니다.
  - `clear_data()`: 수집된 데이터를 초기화합니다.

## 2. Resource Module (자원 모듈)

### 2.1 Machine

- **클래스**: `Machine`
- **설명**: 제조 기계의 동작과 상태를 관리하는 SimPy 기반 기계 클래스입니다.
- **초기화**:
  ```python
  def __init__(self, env, name: str, machine_type: str, processing_time: float = 1.0, capacity: int = 1)
  ```
- **주요 메서드**:
  - `process(product)`: 제품을 가공하는 SimPy 프로세스입니다.
  - `get_status()`: 기계의 현재 상태를 반환합니다.
  - `start_maintenance()`: 유지보수 모드를 시작합니다.
  - `stop_maintenance()`: 유지보수 모드를 종료합니다.

### 2.2 Worker

- **클래스**: `Worker`
- **설명**: 작업자의 동작과 스킬을 관리하는 SimPy 기반 작업자 클래스입니다.
- **초기화**:
  ```python
  def __init__(self, env, name: str, skills: List[str], work_speed: float = 1.0)
  ```
- **주요 메서드**:
  - `work_on(product, process_type: str)`: 특정 작업을 수행하는 SimPy 프로세스입니다.
  - `has_skill(skill: str)`: 특정 스킬을 보유하고 있는지 확인합니다.
  - `get_status()`: 작업자의 현재 상태를 반환합니다.

### 2.3 Product

- **클래스**: `Product`
- **설명**: 제품의 속성과 상태를 관리하는 제품 클래스입니다.
- **초기화**:
  ```python
  def __init__(self, product_id: str, product_type: str, properties: Dict[str, Any] = None)
  ```
- **주요 메서드**:
  - `get_property(key: str)`: 제품의 특정 속성을 반환합니다.
  - `set_property(key: str, value: Any)`: 제품의 속성을 설정합니다.
  - `add_history(event: str, timestamp: float)`: 제품 이력을 추가합니다.
  - `get_history()`: 제품 이력을 반환합니다.

### 2.4 Transport

- **클래스**: `Transport`
- **설명**: 제품의 이동과 운송을 관리하는 운송 클래스입니다.
- **초기화**:
  ```python
  def __init__(self, env, name: str, speed: float = 1.0, capacity: int = 1)
  ```
- **주요 메서드**:
  - `move(product, destination, distance: float)`: 제품을 목적지로 이동시키는 SimPy 프로세스입니다.
  - `get_travel_time(distance: float)`: 이동 시간을 계산합니다.

### 2.5 Resource Helper Classes

#### Resource
- **클래스**: `Resource`
- **설명**: 시뮬레이션에서 사용되는 자원을 표현하는 기본 클래스입니다.
- **초기화**:
  ```python
  def __init__(self, resource_id: str, name: str, resource_type: ResourceType, quantity: float, unit: str)
  ```

#### ResourceRequirement
- **클래스**: `ResourceRequirement`  
- **설명**: 프로세스에서 필요한 자원 요구사항을 정의하는 클래스입니다.
- **초기화**:
  ```python
  def __init__(self, resource_type: ResourceType, name: str, quantity: float, unit: str, is_consumed: bool = False)
  ```

#### ResourceType
- **열거형**: `ResourceType`
- **설명**: 자원의 종류를 정의하는 열거형입니다.
- **값들**:
  - `RAW_MATERIAL`: 원자재
  - `TOOL`: 도구
  - `SEMI_FINISHED`: 반제품
  - `FINISHED_PRODUCT`: 완제품
  - `ENERGY`: 에너지
  - `LABOR`: 인력

## 3. Processes Module (프로세스 모듈)

### 3.1 BaseProcess

- **클래스**: `BaseProcess`
- **설명**: 모든 제조 공정의 기본이 되는 추상 클래스입니다. 프로세스 체이닝 기능을 지원합니다.
- **주요 메서드**:
  - `execute(product, *args, **kwargs)`: 프로세스를 실행하는 추상 메서드입니다.
  - `__rshift__(other)`: `>>` 연산자를 통한 프로세스 체이닝을 지원합니다.
  - `add_next_process(process)`: 다음 프로세스를 추가합니다.
  - `validate_input(product)`: 입력 제품의 유효성을 검사합니다.

### 3.2 ProcessChain

- **클래스**: `ProcessChain`
- **설명**: 여러 프로세스를 연결하여 복합 공정을 만드는 클래스입니다.
- **주요 메서드**:
  - `execute(product, *args, **kwargs)`: 체인의 모든 프로세스를 순차적으로 실행합니다.
  - `add_process(process)`: 체인에 프로세스를 추가합니다.
  - `get_process_count()`: 체인에 포함된 프로세스 수를 반환합니다.

### 3.3 ManufacturingProcess

- **클래스**: `ManufacturingProcess`
- **설명**: 기본적인 제조 공정을 관리하는 클래스입니다.
- **초기화**:
  ```python
  def __init__(self, name: str, required_resources: List[ResourceRequirement], processing_time: float = 1.0)
  ```
- **주요 메서드**:
  - `execute(product, env, resource_manager)`: 제조 공정을 실행하는 SimPy 프로세스입니다.
  - `get_required_resources()`: 필요한 자원 목록을 반환합니다.
  - `set_processing_time(time: float)`: 가공 시간을 설정합니다.

### 3.4 AssemblyProcess

- **클래스**: `AssemblyProcess`
- **설명**: 여러 부품을 조립하는 조립 공정을 관리하는 클래스입니다.
- **초기화**:
  ```python
  def __init__(self, name: str, required_components: List[ResourceRequirement], assembly_time: float = 2.0)
  ```
- **주요 메서드**:
  - `execute(components: List[Product], env, resource_manager)`: 조립 공정을 실행합니다.
  - `validate_components(components)`: 조립에 필요한 부품들이 모두 있는지 확인합니다.

### 3.5 QualityControlProcess

- **클래스**: `QualityControlProcess`
- **설명**: 품질 검사를 수행하는 품질 관리 공정입니다.
- **초기화**:
  ```python
  def __init__(self, name: str, pass_rate: float = 0.95, inspection_time: float = 0.5)
  ```
- **주요 메서드**:
  - `execute(product, env, resource_manager)`: 품질 검사를 실행합니다.
  - `set_pass_rate(rate: float)`: 품질 통과율을 설정합니다.
  - `get_inspection_result(product)`: 검사 결과를 반환합니다.

### 3.6 고급 기능

#### 우선순위 시스템
- **함수**: `parse_process_priority(process_name: str)`
- **설명**: 공정명에서 우선순위를 파싱합니다. (예: "공정2(1)" → ("공정2", 1))

- **함수**: `validate_priority_sequence(processes_with_priorities)`
- **설명**: 우선순위 순서의 유효성을 검사합니다.

#### 프로세스 실행 모드
- **Sequential Execution**: 순차적 프로세스 실행
- **Parallel Execution**: 병렬 프로세스 실행  
- **Priority-based Execution**: 우선순위 기반 프로세스 실행

## 4. Utils Module (유틸리티 모듈)

### 4.1 Statistics

- **클래스**: `Statistics`
- **설명**: 시뮬레이션 결과 분석을 위한 통계 계산 유틸리티입니다.
- **주요 메서드**:
  - `calculate_mean(data: List[float])`: 데이터의 평균을 계산합니다.
  - `calculate_variance(data: List[float])`: 데이터의 분산을 계산합니다.
  - `calculate_std_deviation(data: List[float])`: 표준편차를 계산합니다.
  - `calculate_percentile(data: List[float], percentile: float)`: 백분위수를 계산합니다.
  - `generate_summary_statistics(data: List[float])`: 요약 통계를 생성합니다.

### 4.2 Visualization

- **클래스**: `Visualization`
- **설명**: 시뮬레이션 결과를 시각화하는 유틸리티입니다.
- **주요 메서드**:
  - `plot_line_chart(x_data, y_data, title, xlabel, ylabel)`: 선 그래프를 생성합니다.
  - `plot_histogram(data, bins, title, xlabel, ylabel)`: 히스토그램을 생성합니다.
  - `plot_scatter(x_data, y_data, title, xlabel, ylabel)`: 산점도를 생성합니다.
  - `plot_box_plot(data, labels, title, ylabel)`: 박스 플롯을 생성합니다.
  - `save_plot(filename: str)`: 현재 플롯을 파일로 저장합니다.

## 5. Config Module (설정 모듈)

### 5.1 Settings

- **모듈**: `settings.py`
- **설명**: 시뮬레이션의 전역 설정을 관리합니다.
- **주요 설정**:
  - `DEFAULT_SIMULATION_TIME`: 기본 시뮬레이션 시간
  - `DEFAULT_RANDOM_SEED`: 기본 랜덤 시드
  - `LOGGING_LEVEL`: 로깅 레벨 설정
  - `OUTPUT_DIRECTORY`: 출력 파일 디렉토리
  - `VISUALIZATION_SETTINGS`: 시각화 관련 설정

## 6. 사용 예제

### 6.1 기본 시뮬레이션 설정

```python
from core.simulation_engine import SimulationEngine
from Resource.machine import Machine
from Resource.worker import Worker
from Resource.product import Product

# 시뮬레이션 엔진 생성
engine = SimulationEngine(random_seed=42)

# 자원 생성
machine = Machine(engine.env, "기계1", "드릴링머신", processing_time=2.0)
worker = Worker(engine.env, "작업자1", ["드릴링", "조립"], work_speed=1.2)

# 시뮬레이션 실행
engine.run(until=100)
```

### 6.2 프로세스 체이닝

```python
from processes.manufacturing_process import ManufacturingProcess
from processes.assembly_process import AssemblyProcess
from processes.quality_control_process import QualityControlProcess

# 프로세스 생성
manufacturing = ManufacturingProcess("제조", required_resources, processing_time=2.0)
assembly = AssemblyProcess("조립", required_components, assembly_time=3.0)
quality_check = QualityControlProcess("품질검사", pass_rate=0.95, inspection_time=1.0)

# 프로세스 체이닝 (>> 연산자 사용)
complete_process = manufacturing >> assembly >> quality_check

# 제품에 대해 전체 프로세스 실행
product = Product("P001", "제품타입A")
complete_process.execute(product, engine.env, resource_manager)
```

### 6.3 데이터 수집 및 시각화

```python
from core.data_collector import DataCollector
from utils.visualization import Visualization

# 데이터 수집
data_collector = DataCollector()
data_collector.collect_data("throughput", 100, timestamp=engine.env.now)

# 시각화
viz = Visualization()
data = data_collector.get_data("throughput")
viz.plot_line_chart(data['timestamps'], data['values'], 
                   "Throughput Over Time", "Time", "Throughput")
viz.save_plot("throughput_analysis.png")
```

## 7. 주의사항 및 팁

1. **SimPy 환경**: 모든 프로세스는 SimPy 환경에서 실행되므로 `yield` 키워드를 적절히 사용해야 합니다.

2. **자원 관리**: 자원을 할당한 후에는 반드시 해제해야 합니다.

3. **프로세스 체이닝**: `>>` 연산자를 사용할 때 프로세스의 입출력 타입이 호환되는지 확인하세요.

4. **우선순위 시스템**: 프로세스명에 우선순위를 지정할 때는 "프로세스명(우선순위)" 형식을 사용하세요.

5. **데이터 수집**: 시뮬레이션 중 주요 지표들을 지속적으로 수집하여 분석에 활용하세요.

- **클래스**: `Visualization`
- **설명**: 시뮬레이션 결과를 시각화합니다.
- **메서드**:
  - `plot_results(data)`: 결과를 그래프로 시각화합니다.

## 5. Configuration Module

### 5.1 Settings

- **클래스**: `Settings`
- **설명**: 시뮬레이션 설정을 정의합니다.
- **메서드**:
  - `load_settings(file_path)`: 설정 파일을 로드합니다.
  - `save_settings(file_path)`: 설정을 파일에 저장합니다.

이 문서는 API의 기본적인 사용법을 설명하며, 각 클래스와 메서드에 대한 자세한 내용은 소스 코드를 참조하시기 바랍니다.