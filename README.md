# 제조 공정 시뮬레이션 프레임워크 (Manufacturing Simulation Framework)

[![Python](https://img.shields.io/badge/Python-3.8+-blue.svg)](https://www.python.org/downloads/)
[![SimPy](https://img.shields.io/badge/SimPy-4.0+-green.svg)](https://simpy.readthedocs.io/)
[![NumPy](https://img.shields.io/badge/NumPy-1.21.0+-orange.svg)](https://numpy.org/)
[![Matplotlib](https://img.shields.io/badge/Matplotlib-3.4.0+-red.svg)](https://matplotlib.org/)
[![License](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)
[![Version](https://img.shields.io/badge/Version-1.0.0-brightgreen.svg)]()

이 프로젝트는 **SimPy 기반의 이산 사건 시뮬레이션** 엔진을 활용한 고도화된 제조 공정 시뮬레이션 프레임워크입니다. 복잡한 제조 및 조립 프로세스를 직관적으로 모델링하고 시뮬레이션할 수 있는 강력하고 유연한 기능을 제공합니다. **BaseProcess 통합 아키텍처**와 **AdvancedResourceManager**를 통해 최고 수준의 재사용성과 확장성을 제공하며, 프로세스 체이닝(`>>` 연산자)을 통한 직관적인 워크플로우 구성이 핵심 특징입니다.

## ✨ 주요 기능

### 🏗️ BaseProcess 통합 아키텍처 (핵심)
- **통합된 기반 클래스**: 모든 프로세스가 BaseProcess를 상속받아 일관성 보장
- **배치 처리**: 효율적인 다중 아이템 동시 처리 (`current_batch` 시스템)
- **우선순위 시스템**: 프로세스별 세밀한 우선순위 제어
- **실행 조건**: 동적 실행 조건 설정 및 검증
- **병렬 처리**: 안전한 병렬 실행 지원
- **통계 수집**: 자동화된 성능 지표 수집

### 🔗 프로세스 체이닝 & 워크플로우
- **직관적인 연결**: `>>` 연산자를 사용한 프로세스 체이닝
  ```python
  # 프로세스 체이닝 예제
  complete_process = manufacturing >> transport >> assembly >> quality_check
  ```
- **자동 Transport 통합**: 프로세스 간 자동 운송 요청 및 처리
- **MultiProcessGroup**: 병렬 프로세스 그룹 지원
- **동적 구성**: 런타임 중 프로세스 추가/제거 가능

### 🎯 고급 자원 관리 (AdvancedResourceManager)
- **통합 자원 관리**: Machine, Worker, Transport, Buffer 등 모든 자원 통합 관리
- **자동 할당/해제**: 효율적인 자원 생명주기 관리
- **실시간 모니터링**: 자원 사용량, 가용성, 성능 지표 실시간 추적
- **자원 검증**: ResourceRequirement 기반 자원 요구사항 검증
- **동적 자원 조정**: 런타임 중 자원 추가/제거 및 재구성

### � 완전한 제조 프로세스 지원
- **ManufacturingProcess**: 제조 공정 (절단, 드릴링, 가공 등)
- **AssemblyProcess**: 조립 공정 (부품 조립, 결합 등)
- **QualityControlProcess**: 품질 검사 (검사, 테스트, 승인 등)
- **TransportProcess**: 운송 공정 (이송, 운송, 물류 등)

### 📊 통합 데이터 수집 & 시각화
- **CentralizedStatistics**: 중앙화된 통계 수집 시스템
- **실시간 데이터**: 처리량, 대기시간, 가동률, 품질 지표
- **고급 시각화**: 선 그래프, 히스토그램, 박스 플롯, 산점도
- **데이터 내보내기**: CSV 포맷 자동 저장 및 분석 지원

### 📝 프레임워크화된 로깅 시스템
- **LogManager**: 로그 설정과 관리
- **LogContext**: 컨텍스트 매니저로 출력 캡처
- **@log_execution**: 데코레이터로 함수 실행 로깅
- **다양한 포맷**: 기본 MD, 상세 MD, 텍스트 포맷 지원
- **간단한 사용법**: 기존 복잡한 로깅 코드를 한 줄로 단순화

## 🚀 빠른 시작

### 설치

```bash
# 1. 저장소 클론
git clone https://github.com/aakn232/sim.git
cd manufacturing-simulation-framework

# 2. 의존성 설치
pip install -r requirements.txt

# 3. 설치 확인
python -c "import simpy; print('SimPy 설치 완료!')"
```

**주요 의존성:**
- `simpy>=4.0` - 이산 사건 시뮬레이션 엔진
- `numpy>=1.21.0` - 수치 계산
- `pandas>=1.3.0` - 데이터 처리 및 분석
- `matplotlib>=3.4.0` - 데이터 시각화

### 첫 번째 시뮬레이션 (완전한 작동 예제)

```python
import os
import sys

# 프로젝트 루트를 파이썬 모듈 검색 경로에 추가
project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, project_root)

from src.core.simulation_engine import SimulationEngine
from src.core.resource_manager import AdvancedResourceManager
from src.Resource.machine import Machine
from src.Resource.worker import Worker
from src.Resource.product import Product
from src.Processes.manufacturing_process import ManufacturingProcess

# 시뮬레이션 엔진 및 자원 관리자 생성
engine = SimulationEngine(random_seed=42)
resource_manager = AdvancedResourceManager()

# 자원 생성 및 등록
machine = Machine(
    env=engine.env,
    name="드릴링머신",
    machine_type="DRILLING",
    processing_time=2.0,
    failure_rate=0.01
)
worker = Worker(
    env=engine.env,
    name="작업자1",
    skills=["드릴링", "조립"],
    work_speed=1.2,
    error_rate=0.02
)

resource_manager.register_machine(machine)
resource_manager.register_worker(worker)

# 제조 프로세스 생성
manufacturing = ManufacturingProcess(
    name="드릴링공정",
    resource_requirements=[],  # AdvancedResourceManager가 자동 관리
    base_processing_time=3.0
)

# 제품 생성 및 처리 프로세스
def production_process(env):
    """완전한 제품 생산 프로세스"""
    for i in range(5):
        product = Product(f"P{i+1:03d}", "테스트제품")
        print(f"시간 {env.now}: 제품 {product.product_id} 생성")
        
        # 제조 프로세스 실행
        yield from manufacturing.execute(product, env, resource_manager)
        print(f"시간 {env.now}: 제품 {product.product_id} 완료")
        
        # 다음 제품까지 대기
        yield env.timeout(1)

# 시뮬레이션 실행
engine.add_process(production_process)
engine.run(until=50)
print("시뮬레이션 완료!")
```

### 고급 시나리오 실행

```bash
# 완전한 제조공정 시뮬레이션 실행
python scenario/scenario_complete_working.py

# 냉장고 도어 제조 시뮬레이션 실행
python scenario/scenario_refrigerator_manufacturing.py

# 개선된 엔진 제조 시뮬레이션 실행
python scenario/scenario_improved_engine_manufacturing.py
```

## 📁 프로젝트 구조

```
manufacturing-simulation-framework/
├── src/                              # 소스 코드
│   ├── core/                         # 핵심 엔진
│   │   ├── simulation_engine.py      # SimPy 기반 시뮬레이션 엔진
│   │   ├── resource_manager.py       # 고급 자원 관리자 (AdvancedResourceManager)
│   │   ├── data_collector.py         # 데이터 수집기
│   │   └── centralized_statistics.py # 중앙화된 통계 시스템
│   ├── Processes/                    # 제조 프로세스
│   │   ├── base_process.py           # BaseProcess 통합 기반 클래스
│   │   ├── manufacturing_process.py  # 제조 공정
│   │   ├── assembly_process.py       # 조립 공정
│   │   ├── quality_control_process.py# 품질 검사 공정
│   │   └── transport_process.py      # 운송 공정
│   ├── Resource/                     # 자원 모델들
│   │   ├── machine.py                # 기계 모델 (고장률 포함)
│   │   ├── worker.py                 # 작업자 모델 (실수율 포함)
│   │   ├── transport.py              # 운송 자원
│   │   ├── buffer.py                 # 버퍼 시스템
│   │   ├── product.py                # 제품 모델
│   │   └── resource_base.py          # 자원 기반 클래스
│   ├── Flow/                         # 워크플로우 관리
│   │   ├── advanced_workflow.py      # 고급 워크플로우
│   │   ├── multi_group_flow.py       # 다중 그룹 플로우
│   │   ├── operators.py              # 연산자 통합
│   │   └── process_chain.py          # 프로세스 체이닝
│   ├── utils/                        # 유틸리티
│   │   ├── statistics.py             # 통계 계산
│   │   ├── visualization.py          # 시각화 도구
│   │   └── dynamic_event.py          # 동적 이벤트
│   └── config/                       # 설정
│       └── settings.py               # 시스템 설정
├── scenario/                         # 시나리오 예제
│   ├── scenario_complete_working.py  # 완전한 작동 시나리오
│   ├── scenario_refrigerator_manufacturing.py # 냉장고 도어 제조
│   ├── scenario_improved_engine_manufacturing.py # 개선된 엔진 제조
│   └── test_*.py                     # 테스트 시나리오들
├── docs/                             # 상세 문서
│   ├── BaseProcess_통합_완료_보고서.md
│   ├── ManufacturingProcess_TransportProcess_통합_가이드.md
│   ├── Priority_기능_분리_가이드.md
│   ├── Processes_모듈_상세_설명.md
│   ├── SimPy_Generator_패턴_가이드.md
│   ├── 냉장고도어_제조공정_시나리오.md
│   ├── 분리된_Transport_아키텍처_가이드.md
│   ├── 연산자_통합_가이드.md
│   ├── 제조공정_Transport_자동요청_가이드.md
│   ├── 출하품_Transport_Blocking_가이드.md
│   └── 통계_수집_표준화_가이드.md
├── log/                              # 시뮬레이션 로그
├── visualizations/                   # 시각화 결과
└── README.md                         # 이 파일
```

## 📖 문서 및 가이드

### 📚 핵심 문서
- **[BaseProcess 통합 완료 보고서](docs/BaseProcess_통합_완료_보고서.md)**: BaseProcess 아키텍처의 완전한 통합 내역
- **[Processes 모듈 상세 설명](docs/Processes_모듈_상세_설명.md)**: 모든 프로세스 클래스의 상세 기능 설명
- **[ManufacturingProcess TransportProcess 통합 가이드](docs/ManufacturingProcess_TransportProcess_통합_가이드.md)**: 제조공정과 운송공정의 통합 방법
- **[SimPy Generator 패턴 가이드](docs/SimPy_Generator_패턴_가이드.md)**: SimPy 제너레이터 패턴 활용 방법

### 🏭 실제 시나리오 가이드
- **[냉장고도어 제조공정 시나리오](docs/냉장고도어_제조공정_시나리오.md)**: 실제 냉장고 도어 제조 프로세스 시뮬레이션
- **[분리된 Transport 아키텍처 가이드](docs/분리된_Transport_아키텍처_가이드.md)**: 운송 시스템 아키텍처 설계
- **[제조공정 Transport 자동요청 가이드](docs/제조공정_Transport_자동요청_가이드.md)**: 자동 운송 요청 시스템

### 🔧 고급 기능 가이드
- **[Priority 기능 분리 가이드](docs/Priority_기능_분리_가이드.md)**: 우선순위 시스템 활용
- **[연산자 통합 가이드](docs/연산자_통합_가이드.md)**: 프로세스 체이닝 연산자 활용
- **[출하품 Transport Blocking 가이드](docs/출하품_Transport_Blocking_가이드.md)**: 운송 차단 및 대기 시스템
- **[통계 수집 표준화 가이드](docs/통계_수집_표준화_가이드.md)**: 표준화된 통계 수집 방법

### 🎯 실행 가능한 시나리오들
| 시나리오 파일 | 난이도 | 주요 기능 | 설명 |
|-----------|--------|-----------|------|
| [`scenario_complete_working.py`](scenario/scenario_complete_working.py) | ⭐⭐⭐⭐ | **완전한 통합 시스템** | 모든 기능이 통합된 완전한 제조 시스템 |
| [`scenario_refrigerator_manufacturing.py`](scenario/scenario_refrigerator_manufacturing.py) | ⭐⭐⭐ | 냉장고 도어 제조 | 실제 냉장고 도어 제조 공정 시뮬레이션 |
| [`scenario_improved_engine_manufacturing.py`](scenario/scenario_improved_engine_manufacturing.py) | ⭐⭐⭐ | 엔진 제조 공정 | 개선된 엔진 제조 라인 시뮬레이션 |
| [`test_simple_process.py`](scenario/test_simple_process.py) | ⭐ | 기본 프로세스 | 간단한 프로세스 테스트 |
| [`test_transport.py`](scenario/test_transport.py) | ⭐⭐ | 운송 시스템 | 운송 시스템 단독 테스트 |

### 🚀 성능 최적화 특징
- **BaseProcess 통합**: 중복 코드 제거로 메모리 효율성 향상
- **AdvancedResourceManager**: 자원 관리 최적화로 실행 속도 향상
- **배치 처리**: 다중 아이템 동시 처리로 처리량 증대
- **중앙화된 통계**: 효율적인 데이터 수집 및 분석

### 📝 로깅 프레임워크 사용 예제

#### 기본 사용법
```python
from src.utils.log_util import LogContext

# 간단한 로깅
with LogContext("시뮬레이션_실행"):
    run_simulation()
```

#### 데코레이터 사용법
```python
from src.utils.log_util import log_execution

@log_execution("함수_실행_로깅")
def my_function():
    # 함수 코드
    pass
```

#### 커스텀 설정
```python
from src.utils.log_util import LogManager, LogContext

# 상세한 로그 포맷 사용
custom_manager = LogManager(
    log_dir="custom_logs",
    format_type="detailed_md"
)

with LogContext("커스텀_로깅", custom_manager, {"테스트": "상세포맷"}):
    run_test()
```

**기존 복잡한 코드:**
```python
# 기존 방식 (복잡함)
output_capture = io.StringIO()
original_stdout = sys.stdout
try:
    sys.stdout = output_capture
    run_simulation()
finally:
    sys.stdout = original_stdout
    captured_output = output_capture.getvalue()
    output_capture.close()
    save_output_to_md(captured_output)
```

**새로운 간단한 코드:**
```python
# 새로운 방식 (간단함)
@log_execution("시뮬레이션")
def run_simulation():
    # 시뮬레이션 코드
    pass
```



### 🛠️ 개발 환경 설정

```bash
# 1. 포크 및 클론
git clone https://github.com/your-username/manufacturing-simulation-framework.git
cd manufacturing-simulation-framework

# 2. 개발용 환경 설정
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate

# 3. 의존성 설치
pip install -r requirements.txt

# 4. 테스트 실행
python scenario/test_simple_process.py

# 5. 완전한 시나리오 실행으로 동작 확인
python scenario/scenario_complete_working.py
```

### 📋 개발 가이드라인
- **코드 스타일**: PEP 8 준수
- **한국어 주석**: 모든 클래스/함수에 한국어 주석 추가
- **BaseProcess 상속**: 새로운 프로세스는 BaseProcess를 상속받아 구현
- **통합 시스템**: AdvancedResourceManager 활용 권장
- **문서화**: 새 기능에 대한 상세 가이드 작성

## � 업데이트 내역

### v1.0.0 (현재)
- ✅ **BaseProcess 통합 아키텍처**: 모든 프로세스의 완전한 통합
- ✅ **AdvancedResourceManager**: 고급 자원 관리 시스템
- ✅ **완전한 작동 시나리오**: 실제 제조 공정 시뮬레이션 완료
- ✅ **통합 운송 시스템**: Transport 프로세스의 완전한 통합
- ✅ **중앙화된 통계**: CentralizedStatistics 시스템
- ✅ **상세한 문서화**: 11개의 전문 가이드 문서

### 🔮 향후 계획 (해야할꺼.md 기반)
- 🔄 **확률 분포 개선**: 기계 고장률, 작업자 실수율의 확률 분포 정의
- 🔄 **ResourceManager 고도화**: 리소스 한번에 등록 및 관리 시스템
- 🔄 **Input/Output Resource**: 프로세스별 입출력 자원 정의 시스템
- 🔄 **워밍업 타임**: 프로세스 워밍업 시간 설정 기능
- 🔄 **데코레이터 패턴**: 자원 예약, 로그 기록, 시간 측정 자동화
- 🔄 **계층적 하이브리드 아키텍처**: 중앙 관리 + 에이전트 계층 시스템

---

### 📞 빠른 시작 링크
- [🚀 설치 및 첫 시뮬레이션](#-빠른-시작)
- [📁 프로젝트 구조 확인](#-프로젝트-구조)
- [📖 상세 문서 및 가이드](#-문서-및-가이드)
- [🎯 실제 시나리오 실행](#고급-시나리오-실행)