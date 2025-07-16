# 제조 공정 시뮬레이션 프레임워크 시작하기

이 문서는 제조 공정 시뮬레이션 프레임워크를 시작하는 방법에 대한 완전한 가이드를 제공합니다. 이 프레임워크는 SimPy 기반으로 구축되었으며, 제조업 시뮬레이션의 재사용성과 확장성을 높이기 위해 설계되었습니다.

## 1. 환경 설정

### 1.1. 필수 패키지 설치

먼저, 프로젝트에 필요한 패키지를 설치해야 합니다. `requirements.txt` 파일에 정의된 패키지를 설치하려면 다음 명령어를 실행하세요:

```bash
pip install -r requirements.txt
```

**주요 종속성:**
- `simpy`: 이산 사건 시뮬레이션 엔진
- `matplotlib`: 데이터 시각화
- `numpy`: 수치 계산
- `pandas`: 데이터 처리 및 분석

### 1.2. 프로젝트 구조

프로젝트는 다음과 같은 구조로 되어 있습니다:

```
manufacturing-simulation-framework/
├── src/                        # 소스 코드
│   ├── core/                   # 핵심 엔진 및 관리자
│   │   ├── simulation_engine.py    # SimPy 기반 시뮬레이션 엔진
│   │   ├── resource_manager.py     # 자원 관리자
│   │   └── data_collector.py       # 데이터 수집기
│   ├── processes/              # 제조 프로세스
│   │   ├── base_process.py         # 기본 프로세스 클래스
│   │   ├── manufacturing_process.py # 제조 공정
│   │   ├── assembly_process.py     # 조립 공정
│   │   └── quality_control_process.py # 품질 관리
│   ├── Resource/               # 자원 모델들
│   │   ├── machine.py             # 기계 모델
│   │   ├── worker.py              # 작업자 모델
│   │   ├── product.py             # 제품 모델
│   │   ├── transport.py           # 운송 모델
│   │   └── helper.py              # 자원 헬퍼 클래스
│   ├── utils/                  # 유틸리티
│   │   ├── statistics.py          # 통계 계산
│   │   └── visualization.py       # 시각화
│   └── config/                 # 설정
│       └── settings.py            # 전역 설정
├── examples/                   # 예제 코드
├── tests/                      # 테스트 코드
├── docs/                       # 문서
├── requirements.txt            # 필요한 패키지 목록
├── setup.py                    # 패키지 설정 파일
└── README.md                   # 프로젝트 설명
```

## 2. 기본 사용법

### 2.1. 첫 번째 시뮬레이션 만들기

가장 간단한 시뮬레이션부터 시작해보겠습니다:

```python
import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), '..', 'src'))

from core.simulation_engine import SimulationEngine
from Resource.machine import Machine
from Resource.worker import Worker
from Resource.product import Product

# 1. 시뮬레이션 엔진 생성
engine = SimulationEngine(random_seed=42)

# 2. 자원 생성
machine1 = Machine(engine.env, "드릴링머신", "드릴링머신", processing_time=2.0)
worker1 = Worker(engine.env, "작업자1", ["드릴링", "조립"], work_speed=1.2)

# 3. 제품 생성
product = Product("P001", "제품타입A")

# 4. 시뮬레이션 실행
engine.run(until=100)  # 100시간 동안 시뮬레이션

# 5. 결과 확인
results = engine.get_results()
print("시뮬레이션 완료!")
```

### 2.2. 자원 관리 시스템 사용하기

복잡한 자원 관리가 필요한 경우 ResourceManager를 사용할 수 있습니다:

```python
from core.resource_manager import ResourceManager
from Resource.helper import Resource, ResourceRequirement, ResourceType

# 자원 관리자 생성
resource_manager = ResourceManager()

# 자원 정의
raw_material = Resource("원자재_001", "철강", ResourceType.RAW_MATERIAL, 100.0, "kg")
drill = Resource("드릴_001", "드릴", ResourceType.TOOL, 1.0, "개")

# 자원 풀에 추가
resource_manager.add_resource(raw_material)
resource_manager.add_resource(drill)

# 자원 요구사항 정의
requirements = [
    ResourceRequirement(ResourceType.RAW_MATERIAL, "철강", 5.0, "kg", True),
    ResourceRequirement(ResourceType.TOOL, "드릴", 1.0, "개", False)
]

# 자원 할당
allocated = resource_manager.allocate_resources(requirements)
print(f"할당된 자원: {allocated}")

# 자원 해제
resource_manager.release_resources(allocated)
```

### 2.3. 프로세스 체이닝 사용하기

프레임워크의 핵심 기능인 프로세스 체이닝을 사용해보겠습니다:

```python
from processes.manufacturing_process import ManufacturingProcess
from processes.assembly_process import AssemblyProcess
from processes.quality_control_process import QualityControlProcess

# 각 프로세스 정의
manufacturing = ManufacturingProcess(
    name="드릴링", 
    required_resources=manufacturing_requirements, 
    processing_time=2.0
)

assembly = AssemblyProcess(
    name="조립", 
    required_components=assembly_requirements, 
    assembly_time=3.0
)

quality_check = QualityControlProcess(
    name="품질검사", 
    pass_rate=0.95, 
    inspection_time=1.0
)

# 프로세스 체이닝 (>> 연산자 사용)
complete_process = manufacturing >> assembly >> quality_check

# 제품에 대해 전체 프로세스 실행
product = Product("P001", "제품타입A")
yield from complete_process.execute(product, engine.env, resource_manager)
```

### 2.4. 우선순위 시스템 활용하기

프로세스에 우선순위를 설정하여 실행 순서를 제어할 수 있습니다:

```python
# 우선순위가 포함된 프로세스명 사용
priority_process1 = ManufacturingProcess("드릴링(1)", requirements, 2.0)
priority_process2 = ManufacturingProcess("밀링(2)", requirements, 3.0)
priority_process3 = ManufacturingProcess("연마(3)", requirements, 1.0)

# 우선순위에 따라 자동으로 정렬되어 실행됩니다
process_chain = priority_process1 >> priority_process2 >> priority_process3
```

## 3. 데이터 수집 및 분석

### 3.1. 데이터 수집하기

시뮬레이션 중 주요 지표를 수집하는 방법:

```python
from core.data_collector import DataCollector

# 데이터 수집기 생성
data_collector = DataCollector()

# 시뮬레이션 중 데이터 수집
def production_process(env):
    while True:
        # 생산 작업 수행
        yield env.timeout(1)
        
        # 처리량 데이터 수집
        data_collector.collect_data("throughput", 1, timestamp=env.now)
        
        # 기계 가동률 데이터 수집
        utilization = machine1.get_utilization()
        data_collector.collect_data("machine_utilization", utilization, timestamp=env.now)

# 프로세스를 시뮬레이션에 추가
engine.add_process(production_process)
engine.run(until=100)

# 수집된 데이터 확인
throughput_data = data_collector.get_data("throughput")
print(f"총 처리량: {sum(throughput_data['values'])}")
```

### 3.2. 결과 시각화하기

```python
from utils.visualization import Visualization

# 시각화 도구 생성
viz = Visualization()

# 데이터 가져오기
throughput_data = data_collector.get_data("throughput")
utilization_data = data_collector.get_data("machine_utilization")

# 선 그래프 생성
viz.plot_line_chart(
    throughput_data['timestamps'], 
    throughput_data['values'],
    title="시간에 따른 처리량",
    xlabel="시간 (시간)",
    ylabel="처리량 (개/시간)"
)
viz.save_plot("throughput_over_time.png")

# 히스토그램 생성
viz.plot_histogram(
    utilization_data['values'],
    bins=20,
    title="기계 가동률 분포",
    xlabel="가동률 (%)",
    ylabel="빈도"
)
viz.save_plot("utilization_distribution.png")
```

## 4. 예제 실행

### 4.1. 기본 예제 실행

`examples/` 디렉토리에서 제공되는 예제를 실행해보세요:

```bash
# 기본 SimPy 예제 실행
python examples/correct_simpy_example.py
```

### 4.2. 사용자 정의 시뮬레이션 만들기

나만의 시뮬레이션을 만들어보세요:

```python
def custom_simulation():
    """사용자 정의 제조 시뮬레이션"""
    print("=== 사용자 정의 제조 시뮬레이션 ===")
    
    # 시뮬레이션 설정
    engine = SimulationEngine(random_seed=123)
    
    # 여러 기계와 작업자 생성
    machines = []
    for i in range(3):
        machine = Machine(engine.env, f"기계{i+1}", "범용기계", processing_time=1.5+i*0.5)
        machines.append(machine)
    
    workers = []
    for i in range(2):
        worker = Worker(engine.env, f"작업자{i+1}", ["가공", "조립", "검사"], work_speed=1.0+i*0.2)
        workers.append(worker)
    
    # 복잡한 프로세스 체인 구성
    # 여러 단계를 거치는 제조 공정
    
    # 시뮬레이션 실행
    engine.run(until=200)
    
    # 결과 분석
    results = engine.get_results()
    return results

# 실행
results = custom_simulation()
print("시뮬레이션 결과:", results)
```

## 5. 고급 기능

### 5.1. 병렬 프로세스 실행

```python
from processes.advanced_workflow import AdvancedWorkflow

# 병렬로 실행할 프로세스들 정의
parallel_processes = [
    ManufacturingProcess("가공1", requirements1, 2.0),
    ManufacturingProcess("가공2", requirements2, 2.5),
    ManufacturingProcess("가공3", requirements3, 1.8)
]

# 고급 워크플로우로 병렬 실행
workflow = AdvancedWorkflow()
workflow.execute_parallel(parallel_processes, products, engine.env, resource_manager)
```

### 5.2. 조건부 프로세스 실행

```python
def quality_based_routing(product, quality_score):
    """품질 점수에 따른 조건부 라우팅"""
    if quality_score >= 0.95:
        return premium_packaging_process
    elif quality_score >= 0.80:
        return standard_packaging_process
    else:
        return rework_process

# 조건부 실행 적용
quality_score = quality_check.get_quality_score(product)
next_process = quality_based_routing(product, quality_score)
yield from next_process.execute(product, engine.env, resource_manager)
```

## 6. 성능 최적화 및 팁

### 6.1. 시뮬레이션 성능 최적화

1. **적절한 시뮬레이션 시간 설정**: 너무 긴 시뮬레이션은 성능에 영향을 줄 수 있습니다.
2. **자원 풀 크기 조정**: 자원이 부족하면 대기 시간이 길어집니다.
3. **데이터 수집 빈도 조절**: 너무 자주 데이터를 수집하면 성능이 저하될 수 있습니다.

### 6.2. 디버깅 팁

1. **로깅 활용**: 각 프로세스에서 중요한 이벤트를 로깅하세요.
2. **단계별 실행**: 복잡한 프로세스는 단계별로 나누어 테스트하세요.
3. **자원 상태 모니터링**: 자원 부족이나 데드락을 방지하기 위해 자원 상태를 모니터링하세요.

```python
# 디버깅을 위한 로깅 예제
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def logged_process(env, product):
    logger.info(f"프로세스 시작: {product.product_id}")
    yield env.timeout(2.0)
    logger.info(f"프로세스 완료: {product.product_id}")
```

## 7. 다음 단계

이제 기본적인 사용법을 익혔으니 다음 문서들을 참조하여 더 고급 기능을 학습해보세요:

- [API Reference](api_reference.md): 전체 API 문서
- [Resource Management Guide](resource_management_guide.md): 자원 관리 심화 가이드
- [Process Chaining](process_chaining.md): 프로세스 체이닝 상세 가이드
- [Mandatory Resources Guide](mandatory_resources_guide.md): 필수 자원 관리 가이드

## 8. 문제 해결

### 자주 발생하는 문제들:

1. **ImportError**: 경로 설정을 확인하고 `sys.path.append()`를 사용하세요.
2. **SimPy 관련 오류**: 모든 프로세스 함수에서 `yield` 키워드를 사용하는지 확인하세요.
3. **자원 부족**: 자원 풀 크기를 늘리거나 자원 요구사항을 조정하세요.
4. **성능 문제**: 시뮬레이션 시간을 줄이거나 데이터 수집 빈도를 조정하세요.

### 문의 및 지원

문제가 발생하거나 질문이 있는 경우:
1. 프로젝트 문서를 먼저 확인해보세요.
2. 예제 코드를 참조하여 올바른 사용법을 확인하세요.
3. GitHub Issues를 통해 버그 리포트나 기능 요청을 제출하세요.