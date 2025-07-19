# 제조 공정 시뮬레이션 프레임워크 (Manufacturing Simulation Framework)

[![Python](https://img.shields.io/badge/Python-3.6+-blue.svg)](https://www.python.org/downloads/)
[![SimPy](https://img.shields.io/badge/SimPy-4.0+-green.svg)](https://simpy.readthedocs.io/)
[![NumPy](https://img.shields.io/badge/NumPy-1.21.0+-orange.svg)](https://numpy.org/)
[![Matplotlib](https://img.shields.io/badge/Matplotlib-3.4.0+-red.svg)](https://matplotlib.org/)
[![License](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)
[![Version](https://img.shields.io/badge/Version-0.1.0-brightgreen.svg)]()

이 프로젝트는 **SimPy 기반의 이산 사건 시뮬레이션** 엔진을 활용한 제조 공정 시뮬레이션 프레임워크입니다. 복잡한 제조 및 조립 프로세스를 직관적으로 모델링하고 시뮬레이션할 수 있는 강력하고 유연한 기능을 제공합니다. **재사용성과 확장성**을 높이기 위해 모듈화된 구조로 설계되었으며, 프로세스 체이닝(`>>` 연산자)을 통한 직관적인 워크플로우 구성이 핵심 특징입니다.

## ✨ 주요 기능

### 🔗 프로세스 체이닝 (핵심 기능)
- **직관적인 연결**: `>>` 연산자를 사용한 프로세스 체이닝
  ```python
  # 프로세스 체이닝 예제 (핵심 기능!)
  complete_process = manufacturing >> assembly >> quality_check
  ```
- **우선순위 시스템**: 프로세스명에 우선순위 포함 가능 (`"공정1(1)"`, `"공정2(2)"`)
- **동적 구성**: 런타임 중 프로세스 추가/제거 가능
- **MultiProcessGroup**: 병렬 프로세스 그룹 지원
- **실행 모드**: 순차, 병렬, 우선순위 기반 실행

### 📦 배치 처리 (NEW!)
- **효율적인 처리**: 여러 아이템을 한번에 처리하여 시간 절약
- **배치 운송**: 여러 제품을 한번에 운송하여 운송 효율성 향상
- **성능 모니터링**: 배치 효율성 및 활용률 추적
- **호환성**: 기존 단일 처리 방식과 완전 호환

### 🎯 통합 자원 관리
- **포괄적 자원 지원**: 원자재, 반제품, 완제품, 도구, 에너지, 인력
- **자동 할당/해제**: 효율적인 자원 생명주기 관리
- **사용량 추적**: 실시간 자원 사용 모니터링
- **ResourceManager**: 통합 자원 관리자

### 📊 데이터 수집 & 시각화
- **실시간 데이터 수집**: 처리량, 대기시간, 가동률, 품질 지표
- **다양한 차트**: 선 그래프, 히스토그램, 박스 플롯, 산점도
- **통계 분석**: 평균, 분산, 백분위수 등 기본 통계
- **데이터 내보내기**: CSV 포맷 지원
- **VisualizationManager**: 고급 시각화 도구

### 🏭 현실적인 시뮬레이션
- **SimPy 기반**: 이산 사건 시뮬레이션 엔진
- **확률적 요소**: 처리 시간 변동성, 품질 불확실성
- **병목 분석**: 자동 병목 구간 식별 및 최적화 제안
- **Machine/Worker 모델**: 현실적인 제조 자원 시뮬레이션
- **⚠️ 고장확률 지원**: 기계 고장, 작업자 실수 등 현실적인 장애 상황 모델링
- **🔧 고장률 가중치 (NEW!)**: 공정별로 기계/작업자 고장률에 가중치 적용 가능

## 🚀 빠른 시작

### 시스템 요구사항
- **Python**: 3.6 이상
- **운영체제**: Windows, macOS, Linux
- **메모리**: 최소 512MB (복잡한 시뮬레이션의 경우 2GB+ 권장)

### 설치

```bash
# 1. 저장소 클론
git clone https://github.com/aakn232/sim.git
cd sim

# 2. 의존성 설치
pip install -r requirements.txt

# 3. 설치 확인 (선택사항)
python -c "import simpy; print('SimPy 설치 완료!')"
```

**주요 의존성:**
- `simpy>=4.0` - 이산 사건 시뮬레이션 엔진
- `numpy>=1.21.0` - 수치 계산
- `pandas>=1.3.0` - 데이터 처리 및 분석
- `matplotlib>=3.4.0` - 데이터 시각화

### 첫 번째 시뮬레이션

```python
import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), 'src'))

from core.simulation_engine import SimulationEngine
from Resource.machine import Machine
from Resource.worker import Worker
from Resource.product import Product

# 시뮬레이션 엔진 생성
engine = SimulationEngine(random_seed=42)

# 자원 생성
machine = Machine(engine.env, "드릴링머신", "드릴링머신", processing_time=2.0)
worker = Worker(engine.env, "작업자1", ["드릴링", "조립"], work_speed=1.2)

# 제품 생성 및 처리
def simple_process(env):
    """간단한 제품 처리 프로세스"""
    product = Product("P001", "테스트제품")
    print(f"시간 {env.now}: 제품 {product.product_id} 생성")
    
    # 기계 작업 실행
    yield from machine.operate(product, processing_time=3.0)
    print(f"시간 {env.now}: 제품 {product.product_id} 완료")

# 시뮬레이션 실행
engine.add_process(simple_process)
engine.run(until=10)
print("시뮬레이션 완료!")
```

### 프로세스 체이닝 예제 (핵심 기능)

```python
import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), 'src'))

from core.simulation_engine import SimulationEngine
from core.resource_manager import ResourceManager
from processes.manufacturing_process import ManufacturingProcess
from processes.assembly_process import AssemblyProcess
from processes.quality_control_process import QualityControlProcess
from Resource.helper import ResourceRequirement, ResourceType

# 시뮬레이션 엔진 및 자원 관리자 생성
engine = SimulationEngine(random_seed=123)
resource_manager = ResourceManager()

# 자원 요구사항 정의
drilling_requirements = [
    ResourceRequirement("STEEL_001", 2.0, ResourceType.RAW_MATERIAL, "kg"),
    ResourceRequirement("DRILL_001", 1.0, ResourceType.TOOL, "개")
]

assembly_requirements = [
    ResourceRequirement("TOOLS_001", 1.0, ResourceType.TOOL, "세트")
]

# 프로세스 정의
manufacturing = ManufacturingProcess("드릴링", drilling_requirements, 2.0)
assembly = AssemblyProcess("조립", assembly_requirements, 3.0)
quality_check = QualityControlProcess("품질검사", pass_rate=0.95, inspection_time=1.0)

# 프로세스 체이닝 (핵심 기능!)
complete_process = manufacturing >> assembly >> quality_check

# 프로세스 실행
def run_process_chain(env):
    product = Product("PC001", "체인제품")
    yield from complete_process.execute(product, env, resource_manager)

engine.add_process(run_process_chain)
engine.run(until=20)
```

### 배치 처리 시연

```bash
# 배치 처리 기능 체험
python examples/simple_batch_demo.py
```

이 예제를 통해 확인할 수 있는 성능 향상:
- **Process 배치 처리**: 25% 시간 절약
- **Transport 배치 운송**: 66.7% 시간 절약

## 📁 프로젝트 구조

```
manufacturing-simulation-framework/
├── src/                          # 소스 코드
│   ├── core/                     # 핵심 엔진
│   │   ├── simulation_engine.py  # SimPy 기반 시뮬레이션 엔진
│   │   ├── resource_manager.py   # 고급 자원 관리자
│   │   └── data_collector.py     # 데이터 수집기
│   ├── processes/                # 제조 프로세스
│   │   ├── base_process.py       # 프로세스 체이닝 기반 클래스
│   │   ├── manufacturing_process.py
│   │   ├── assembly_process.py
│   │   └── quality_control_process.py
│   ├── Resource/                 # 자원 모델들
│   │   ├── machine.py           # SimPy 기반 기계 모델
│   │   ├── worker.py            # 작업자 모델
│   │   ├── product.py           # 제품 모델
│   │   └── helper.py            # 자원 헬퍼 클래스
│   ├── utils/                   # 유틸리티
│   │   ├── statistics.py       # 통계 계산
│   │   └── visualization.py    # 시각화 도구
│   └── config/                  # 설정
├── examples/                    # 사용 예제
│   ├── basic_manufacturing_line.py    # 기본 제조 라인
│   ├── process_chaining_example.py    # 프로세스 체이닝
│   ├── data_analysis_example.py       # 데이터 분석
│   └── README.md                      # 예제 가이드
├── docs/                             # 문서
│   ├── getting_started.md            # 시작 가이드
│   ├── api_reference.md              # API 레퍼런스
│   ├── process_chaining.md           # 프로세스 체이닝 가이드
│   ├── batch_processing_guide.md     # 배치 처리 가이드 (NEW!)
│   ├── resource_management_guide.md  # 자원 관리 가이드
│   └── mandatory_resources_guide.md  # 필수 자원 가이드
│   ├── resource_management_guide.md  # 자원 관리 가이드
│   └── mandatory_resources_guide.md  # 고급 자원 관리
└── tests/                           # 테스트
```

## 📖 문서 및 예제

### 📚 문서
- **[시작하기](docs/getting_started.md)**: 기본 사용법과 첫 시뮬레이션 만들기
- **[API 레퍼런스](docs/api_reference.md)**: 전체 API 문서
- **[프로세스 체이닝](docs/process_chaining.md)**: 핵심 기능인 프로세스 체이닝 가이드
- **[자원 관리](docs/resource_management_guide.md)**: 자원 관리 시스템 가이드
- **[고급 자원 관리](docs/mandatory_resources_guide.md)**: 필수 자원 및 고급 관리 기능
- **[고장확률 가이드](docs/failure_probability_guide.md)**: 리소스 고장확률 정의 및 활용 방법 (NEW!)

### 🎯 예제 모음
| 예제 파일 | 난이도 | 주요 기능 | 설명 |
|-----------|--------|-----------|------|
| [`basic_manufacturing_line.py`](examples/basic_manufacturing_line.py) | ⭐ | 기본 제조 라인 | 순차적 제조 공정 (절단→드릴링→조립) |
| [`process_chaining_example.py`](examples/process_chaining_example.py) | ⭐⭐⭐ | **프로세스 체이닝** | `>>` 연산자, 우선순위 시스템 |
| [`data_analysis_example.py`](examples/data_analysis_example.py) | ⭐⭐⭐ | 데이터 분석 | KPI 수집, 통계 분석, 시각화 |
| [`complex_assembly_line.py`](examples/complex_assembly_line.py) | ⭐⭐⭐⭐ | 복잡한 조립 | 다중 프로세스, 고급 자원 관리 |
| [`resource_management_example.py`](examples/resource_management_example.py) | ⭐⭐ | 자원 관리 | ResourceManager, 자원 추적 |
| [`parallel_to_assembly_example.py`](examples/parallel_to_assembly_example.py) | ⭐⭐⭐ | 병렬 처리 | MultiProcessGroup, 병렬 실행 |
| [`failure_probability_example.py`](examples/failure_probability_example.py) | ⭐⭐ | **고장확률** | 기계 고장, 작업자 실수 시뮬레이션 (NEW!) |
| [`failure_weight_example.py`](examples/failure_weight_example.py) | ⭐⭐⭐ | **고장률 가중치** | 공정별 고장률 가중치 적용 (NEW!) |
| [`none_values_example.py`](examples/none_values_example.py) | ⭐ | **None 값 제어** | 고장/실수 기능 선택적 활성화 (NEW!) |
| [`simple_factory.py`](examples/simple_factory.py) | ⭐ | 간단한 공장 | 기본 공장 시뮬레이션 |
| [`correct_simpy_example.py`](examples/correct_simpy_example.py) | ⭐⭐ | SimPy 기본 | 순수 SimPy 사용 예제 |

자세한 예제 정보는 **[예제 가이드](examples/README.md)**를 참조하세요.

## 🎯 사용 사례 및 적용 분야

### 🏭 제조업
- **자동차 부품 제조**: 엔진 부품, 차체 부품 제조 라인 최적화
- **전자제품 조립**: PCB 조립, 스마트폰/태블릿 생산 공정 분석
- **의료기기 제조**: 정밀 부품 가공, 품질 관리 시스템 개선
- **식품가공업**: 식품 생산 라인, 포장 공정 최적화

### 🔬 연구 및 교육
- **산업공학 연구**: 제조 시스템 모델링 및 분석
- **대학 교육**: 생산 관리, 시뮬레이션 실습 도구
- **최적화 연구**: 생산 스케줄링, 자원 할당 알고리즘 테스트
- **논문 연구**: 제조 시스템 성능 분석 및 개선

### 💼 컨설팅 및 실무
- **공정 개선**: 기존 제조 라인의 병목 구간 식별 및 개선
- **생산성 분석**: 설비 가동률, 작업자 효율성 분석
- **투자 의사결정**: 신규 설비 도입 효과 사전 분석
- **품질 관리**: 품질 검사 프로세스 최적화

## 📊 성능 특징 및 벤치마크

| 항목 | 기본 시뮬레이션 | 중간 복잡도 | 복잡한 시스템 |
|------|----------------|-------------|---------------|
| **시뮬레이션 시간** | 10-50시간 | 100-500시간 | 1000+ 시간 |
| **실행 시간** | 1-3초 | 5-15초 | 30초-2분 |
| **메모리 사용량** | 20-50MB | 50-150MB | 200-500MB |
| **동시 프로세스** | 5-20개 | 20-100개 | 100+ 개 |
| **자원 수** | 10-30개 | 30-100개 | 100+ 개 |
| **제품 처리량** | 100-500개 | 500-2000개 | 2000+ 개 |

### 🚀 성능 최적화 팁
- **메모리 최적화**: 대용량 시뮬레이션 시 데이터 수집 주기 조정
- **실행 속도**: 복잡한 로직은 별도 함수로 분리
- **시각화**: 실시간 시각화보다는 시뮬레이션 완료 후 시각화 권장
- **병렬 처리**: MultiProcessGroup 활용으로 병렬 처리 성능 향상

### 🔧 테스트 환경
- **Python**: 3.8-3.11 테스트 완료
- **OS**: Windows 10/11, macOS, Ubuntu 20.04+
- **하드웨어**: Intel i5/AMD Ryzen 5 이상 권장

## 🤝 기여하기

기여를 환영합니다! 다음 방법으로 참여할 수 있습니다:

### 💡 기여 방법
1. **이슈 리포팅**: 버그나 개선 사항을 Issues에 등록
2. **기능 제안**: 새로운 기능에 대한 아이디어 제안
3. **Pull Request**: 코드 개선이나 새 기능 구현
4. **문서 개선**: 문서 오타 수정이나 예제 추가
5. **예제 추가**: 새로운 사용 사례 예제 작성

### 🛠️ 개발 환경 설정

```bash
# 1. 포크 및 클론
git clone https://github.com/your-username/sim.git
cd sim

# 2. 개발용 환경 설정
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate

# 3. 의존성 설치
pip install -r requirements.txt

# 4. 테스트 실행
python -m pytest tests/ -v

# 5. 예제 실행으로 동작 확인
python examples/basic_manufacturing_line.py
```

### 📋 개발 가이드라인
- **코드 스타일**: PEP 8 준수
- **한국어 주석**: 모든 클래스/함수에 한국어 주석 추가
- **테스트**: 새 기능 추가 시 테스트 코드 작성
- **문서화**: 새 기능에 대한 문서 업데이트

## 📄 라이센스

이 프로젝트는 MIT 라이센스 하에 배포됩니다. 자세한 내용은 [LICENSE](LICENSE) 파일을 참조하세요.

## 🙋‍♂️ 지원 및 문의

### 📞 문의 채널
- **문서**: [Getting Started Guide](docs/getting_started.md)에서 기본 사용법 확인
- **예제**: [Examples Directory](examples/)에서 다양한 사용 사례 참조
- **이슈**: [GitHub Issues](https://github.com/aakn232/sim/issues)에서 버그 리포트나 기능 요청
- **토론**: [GitHub Discussions](https://github.com/aakn232/sim/discussions)에서 질문이나 아이디어 공유

### 🐛 문제 해결
**자주 발생하는 문제:**
1. **ImportError**: `sys.path.append()`로 src 경로 추가 확인
2. **SimPy 관련 오류**: `pip install simpy>=4.0` 재설치
3. **시각화 문제**: matplotlib 백엔드 설정 확인
4. **메모리 부족**: 시뮬레이션 시간이나 데이터 수집 주기 조정

### 📧 직접 문의
- **GitHub**: [@aakn232](https://github.com/aakn232)
- **이메일**: 프로젝트 관련 문의는 GitHub Issues 활용 권장

## 🔄 업데이트 내역

### v2.1.0 (최신)
- ✅ **배치 처리 기능 추가**: 여러 아이템을 한번에 효율적으로 처리
- ✅ **배치 운송 시스템**: 여러 제품을 한번에 운송하여 운송 효율성 66.7% 향상
- ✅ **성능 모니터링**: 배치 효율성 및 활용률 실시간 추적
- ✅ **완전 호환성**: 기존 단일 처리 방식과 100% 호환
- ✅ **🔧 고장률 가중치 기능**: 공정별로 기계/작업자 고장률에 가중치 적용 가능 (NEW!)
- ✅ **시연 예제**: [배치 처리 가이드](docs/batch_processing_guide.md) 및 [고장률 가중치 가이드](docs/failure_weight_guide.md) 제공

### v2.0.0
- ✅ 프로세스 체이닝 기능 추가 (`>>` 연산자)
- ✅ 통합 자원 관리 시스템
- ✅ 고급 데이터 수집 및 시각화
- ✅ 우선순위 시스템
- ✅ 포괄적인 문서 및 예제

### 🔮 향후 계획
- 🔄 **웹 기반 GUI**: 웹 인터페이스를 통한 시뮬레이션 설정 및 실행
- 🔄 **고급 최적화**: 유전 알고리즘, 시뮬레이티드 어닐링 등 최적화 알고리즘 통합
- 🔄 **데이터베이스 연동**: 시뮬레이션 결과 데이터베이스 저장 기능
- 🔄 **클라우드 지원**: 분산 시뮬레이션 실행 환경
- 🔄 **3D 시각화**: 3D 공장 레이아웃 및 실시간 시뮬레이션 시각화

---

**🏭 제조 시뮬레이션을 위한 강력하고 유연한 프레임워크로 여러분의 제조 시스템을 최적화하세요!** ✨

**핵심 특징**: 프로세스 체이닝(`>>`) + 통합 자원 관리 + 실시간 데이터 분석 + 한국어 지원

---

### 📞 빠른 시작 링크
- [🚀 설치 가이드](#-빠른-시작)
- [🔗 프로세스 체이닝 예제](#프로세스-체이닝-예제-핵심-기능)
- [📁 프로젝트 구조](#-프로젝트-구조)
- [📖 문서 및 예제](#-문서-및-예제)