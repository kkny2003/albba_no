# manufacturing-simulation-framework/docs/getting_started.md

# 제조 공정 시뮬레이션 프레임워크 시작하기

이 문서는 제조 공정 시뮬레이션 프레임워크를 시작하는 방법에 대한 가이드를 제공합니다. 이 프레임워크는 재사용성을 높이기 위해 설계되었습니다.

## 1. 환경 설정

### 1.1. 필수 패키지 설치

먼저, 프로젝트에 필요한 패키지를 설치해야 합니다. `requirements.txt` 파일에 정의된 패키지를 설치하려면 다음 명령어를 실행하세요:

```
pip install -r requirements.txt
```

### 1.2. 프로젝트 구조

프로젝트는 다음과 같은 구조로 되어 있습니다:

```
manufacturing-simulation-framework/
├── src/                # 소스 코드
├── examples/           # 예제 코드
├── tests/              # 테스트 코드
├── docs/               # 문서
├── requirements.txt    # 필요한 패키지 목록
├── setup.py            # 패키지 설정 파일
└── README.md           # 프로젝트 설명
```

## 2. 기본 사용법

### 2.1. 시뮬레이션 실행

시뮬레이션을 실행하려면 `src/core/simulation_engine.py` 파일에 정의된 `SimulationEngine` 클래스를 사용합니다. 예를 들어:

```python
from src.core.simulation_engine import SimulationEngine

# 시뮬레이션 엔진 인스턴스 생성
engine = SimulationEngine()

# 시뮬레이션 실행
engine.run()
```

### 2.2. 공정 흐름을 그래프 기반으로 입력하기

공정 흐름을 그래프 구조로 입력하려면 `ProcessGraph` 클래스를 사용할 수 있습니다. 예시:

```python
from src.processes import ProcessGraph

# 공정 그래프 인스턴스 생성
process_graph = ProcessGraph()

# 공정 노드 추가
process_graph.add_process('제조')
process_graph.add_process('조립')
process_graph.add_process('품질관리')

# 공정 간 흐름(순서) 추가
process_graph.add_flow('제조', '조립')
process_graph.add_flow('조립', '품질관리')

# 전체 공정 순서 확인
order = process_graph.get_order()
print('공정 순서:', order)

# 그래프 시각화
process_graph.visualize()
```

### 2.2. 모델 정의

모델을 정의하려면 `src/models/` 디렉토리 내의 클래스를 사용합니다. 예를 들어, 기계 모델을 정의하려면 `machine.py` 파일을 참조하세요.

```python
from src.models.machine import Machine

# 기계 인스턴스 생성
machine = Machine(name="기계1")
```

## 3. 예제 실행

`examples/` 디렉토리에는 간단한 공장 및 복잡한 조립 라인 시뮬레이션 예제가 포함되어 있습니다. 예제를 실행하여 프레임워크의 기능을 확인할 수 있습니다.

```bash
python examples/simple_factory.py
```

## 4. 기여하기

이 프로젝트에 기여하고 싶다면, 먼저 이 문서를 읽고, 코드 스타일 가이드라인을 준수해 주세요. Pull Request를 통해 기여할 수 있습니다.

## 5. 문의

문제가 발생하거나 질문이 있는 경우, [이슈 트래커](링크)를 통해 문의해 주세요.