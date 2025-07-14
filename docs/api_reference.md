# API Reference Documentation

이 문서는 제조 공정 시뮬레이션 프레임워크의 API에 대한 참조 문서입니다. 각 모듈과 클래스의 기능 및 사용법을 설명합니다.

## 1. Core Module

### 1.1 Simulation Engine

- **클래스**: `SimulationEngine`
- **설명**: 시뮬레이션의 실행 및 관리를 담당합니다.
- **메서드**:
  - `run()`: 시뮬레이션을 시작합니다.
  - `stop()`: 시뮬레이션을 중지합니다.
  - `reset()`: 시뮬레이션 상태를 초기화합니다.

### 1.2 Resource Manager

- **클래스**: `ResourceManager`
- **설명**: 자원의 할당 및 해제를 관리합니다.
- **메서드**:
  - `allocate_resource(resource)`: 자원을 할당합니다.
  - `release_resource(resource)`: 자원을 해제합니다.

### 1.3 Data Collector

- **클래스**: `DataCollector`
- **설명**: 시뮬레이션 데이터를 수집하고 저장합니다.
- **메서드**:
  - `collect_data()`: 데이터를 수집합니다.
  - `save_data(file_path)`: 데이터를 파일에 저장합니다.

## 2. Models Module

### 2.1 Machine

- **클래스**: `Machine`
- **설명**: 기계의 동작 및 상태를 관리합니다.
- **메서드**:
  - `start()`: 기계를 시작합니다.
  - `stop()`: 기계를 중지합니다.
  - `status()`: 기계의 현재 상태를 반환합니다.

### 2.2 Worker

- **클래스**: `Worker`
- **설명**: 작업자의 동작 및 상태를 관리합니다.
- **메서드**:
  - `work()`: 작업을 수행합니다.
  - `rest()`: 휴식을 취합니다.

### 2.3 Product

- **클래스**: `Product`
- **설명**: 제품의 속성과 상태를 관리합니다.
- **메서드**:
  - `get_details()`: 제품의 세부 정보를 반환합니다.

### 2.4 Transport

- **클래스**: `Transport`
- **설명**: 제품의 이동을 관리합니다.
- **메서드**:
  - `move(product, destination)`: 제품을 지정된 위치로 이동합니다.

## 3. Processes Module

### 3.1 Manufacturing Process

- **클래스**: `ManufacturingProcess`
- **설명**: 전체 제조 흐름을 관리합니다.
- **메서드**:
  - `start_process()`: 제조 공정을 시작합니다.
  - `end_process()`: 제조 공정을 종료합니다.

### 3.4 Process Graph

- **클래스**: `ProcessGraph`
- **설명**: 공정 흐름을 그래프 구조로 입력하고 관리합니다. 각 노드는 공정(예: 제조, 조립, 품질관리 등)을 나타내며, 엣지는 공정 간의 순서를 나타냅니다.
- **메서드**:
  - `add_process(process_name, process_obj=None)`: 공정 노드를 그래프에 추가합니다.
  - `add_flow(from_process, to_process)`: 두 공정 간의 흐름(엣지)을 추가합니다.
  - `get_order()`: 위상 정렬을 통해 전체 공정 순서를 반환합니다.
  - `visualize()`: 공정 그래프를 시각화합니다.

### 3.2 Assembly Process

- **클래스**: `AssemblyProcess`
- **설명**: 조립 작업을 관리합니다.
- **메서드**:
  - `assemble()`: 조립 작업을 수행합니다.

### 3.3 Quality Control Process

- **클래스**: `QualityControlProcess`
- **설명**: 품질 검사를 관리합니다.
- **메서드**:
  - `inspect()`: 품질 검사를 수행합니다.

## 4. Utils Module

### 4.1 Statistics

- **클래스**: `Statistics`
- **설명**: 통계 관련 유틸리티 함수를 포함합니다.
- **메서드**:
  - `calculate_mean(data)`: 평균을 계산합니다.
  - `calculate_variance(data)`: 분산을 계산합니다.

### 4.2 Visualization

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