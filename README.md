# 제조 공정 시뮬레이션 프레임워크

[![Python](https://img.shields.io/badge/Python-3.7+-blue.svg)](https://www.python.org/downloads/)
[![SimPy](https://img.shields.io/badge/SimPy-4.0+-green.svg)](https://simpy.readthedocs.io/)
[![License](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)

이 프로젝트는 SimPy 기반의 제조 공정 시뮬레이션 프레임워크입니다. 복잡한 제조 및 조립 프로세스를 모델링하고 시뮬레이션할 수 있는 강력하고 유연한 기능을 제공합니다. 재사용성과 확장성을 높이기 위해 모듈화된 구조로 설계되었습니다.

## ✨ 주요 기능

### 🔗 프로세스 체이닝
- **직관적인 연결**: `>>` 연산자를 사용한 프로세스 체이닝
- **우선순위 시스템**: 프로세스명에 우선순위 포함 가능
- **동적 구성**: 런타임 중 프로세스 추가/제거 가능

### 📦 배치 처리 (NEW!)
- **효율적인 처리**: 여러 아이템을 한번에 처리하여 시간 절약
- **배치 운송**: 여러 제품을 한번에 운송하여 운송 효율성 향상
- **성능 모니터링**: 배치 효율성 및 활용률 추적
- **호환성**: 기존 단일 처리 방식과 완전 호환

### 🎯 통합 자원 관리
- **포괄적 자원 지원**: 원자재, 반제품, 완제품, 도구, 에너지, 인력
- **자동 할당/해제**: 효율적인 자원 생명주기 관리
- **사용량 추적**: 실시간 자원 사용 모니터링

### 📊 데이터 수집 & 시각화
- **실시간 데이터 수집**: 처리량, 대기시간, 가동률, 품질 지표
- **다양한 차트**: 선 그래프, 히스토그램, 박스 플롯, 산점도
- **통계 분석**: 평균, 분산, 백분위수 등 기본 통계

### 🏭 현실적인 시뮬레이션
- **SimPy 기반**: 이산 사건 시뮬레이션 엔진
- **확률적 요소**: 처리 시간 변동성, 품질 불확실성
- **병목 분석**: 자동 병목 구간 식별 및 최적화 제안

## 🚀 빠른 시작

### 설치

```bash
# 저장소 클론
git clone https://github.com/your-username/manufacturing-simulation-framework.git
cd manufacturing-simulation-framework

# 의존성 설치
pip install -r requirements.txt
```

### 첫 번째 시뮬레이션

```python
from core.simulation_engine import SimulationEngine
from Resource.machine import Machine
from Resource.worker import Worker
from Resource.product import Product

# 시뮬레이션 엔진 생성
engine = SimulationEngine(random_seed=42)

# 자원 생성
machine = Machine(engine.env, "드릴링머신", "드릴링머신", processing_time=2.0)
worker = Worker(engine.env, "작업자1", ["드릴링", "조립"], work_speed=1.2)

# 시뮬레이션 실행
engine.run(until=100)
print("시뮬레이션 완료!")
```

### 프로세스 체이닝 예제

```python
from processes.manufacturing_process import ManufacturingProcess
from processes.assembly_process import AssemblyProcess
from processes.quality_control_process import QualityControlProcess

# 프로세스 정의
manufacturing = ManufacturingProcess("드릴링", requirements, 2.0)
assembly = AssemblyProcess("조립", components, 3.0)
quality_check = QualityControlProcess("품질검사", pass_rate=0.95, inspection_time=1.0)

# 프로세스 체이닝 (핵심 기능!)
complete_process = manufacturing >> assembly >> quality_check

# 실행
yield from complete_process.execute(product, engine.env, resource_manager)
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

## 📖 문서

- **[시작하기](docs/getting_started.md)**: 기본 사용법과 첫 시뮬레이션 만들기
- **[API 레퍼런스](docs/api_reference.md)**: 전체 API 문서
- **[프로세스 체이닝](docs/process_chaining.md)**: 핵심 기능인 프로세스 체이닝 가이드
- **[자원 관리](docs/resource_management_guide.md)**: 자원 관리 시스템 가이드
- **[예제 모음](examples/README.md)**: 다양한 사용 예제

## 🎯 사용 사례

### 제조업
- 자동차 부품 제조 라인 최적화
- 전자제품 조립 공정 분석
- 품질 관리 시스템 개선

### 연구 및 교육
- 제조 시스템 연구
- 산업공학 교육 도구
- 최적화 알고리즘 테스트베드

### 컨설팅
- 공정 개선 제안
- 생산성 분석
- 병목 구간 식별

## 📊 성능 특징

| 항목 | 기본 예제 | 복잡한 시스템 |
|------|-----------|---------------|
| 시뮬레이션 시간 | 40-72시간 | 수백 시간 |
| 실행 시간 | 2-5초 | 수십 초 |
| 메모리 사용량 | 50-80MB | 수백 MB |
| 동시 프로세스 | 10-50개 | 수백 개 |

## 🤝 기여하기

기여를 환영합니다! 다음 방법으로 참여할 수 있습니다:

1. **이슈 리포팅**: 버그나 개선 사항을 이슈로 등록
2. **기능 제안**: 새로운 기능에 대한 아이디어 제안
3. **Pull Request**: 코드 개선이나 새 기능 구현
4. **문서 개선**: 문서 오타 수정이나 예제 추가

### 개발 환경 설정

```bash
# 개발용 의존성 설치
pip install -r requirements.txt

# 테스트 실행
python -m pytest tests/

# 코드 스타일 확인
flake8 src/
```

## 📄 라이센스

이 프로젝트는 MIT 라이센스 하에 배포됩니다. 자세한 내용은 [LICENSE](LICENSE) 파일을 참조하세요.

## 🙋‍♂️ 지원 및 문의

- **문서**: [Getting Started Guide](docs/getting_started.md)
- **예제**: [Examples Directory](examples/)
- **이슈**: GitHub Issues에서 버그 리포트나 기능 요청
- **토론**: GitHub Discussions에서 질문이나 아이디어 공유

## 🔄 업데이트 내역

### v2.1.0 (최신)
- ✅ **배치 처리 기능 추가**: 여러 아이템을 한번에 효율적으로 처리
- ✅ **배치 운송 시스템**: 여러 제품을 한번에 운송하여 운송 효율성 66.7% 향상
- ✅ **성능 모니터링**: 배치 효율성 및 활용률 실시간 추적
- ✅ **완전 호환성**: 기존 단일 처리 방식과 100% 호환
- ✅ **시연 예제**: [배치 처리 가이드](docs/batch_processing_guide.md) 및 실행 가능한 예제 제공

### v2.0.0
- ✅ 프로세스 체이닝 기능 추가 (`>>` 연산자)
- ✅ 통합 자원 관리 시스템
- ✅ 고급 데이터 수집 및 시각화
- ✅ 우선순위 시스템
- ✅ 포괄적인 문서 및 예제

### v1.0.0
- 기본 SimPy 기반 시뮬레이션 엔진
- 기본 자원 관리
- 간단한 프로세스 모델링

---

**제조 시뮬레이션을 위한 강력하고 유연한 프레임워크로 여러분의 제조 시스템을 최적화하세요!** 🏭✨