---
- alwaysApply: true
---
# SimPy 온톨로지 결합 제조공정 시뮬레이션 자동생성 가이드

## 프로젝트 개요
SimPy 기반의 제조공정 시뮬레이션 프레임워크에 온톨로지를 결합해 시뮬레이션 자동생성을 개발하는 프로젝트입니다. 이 프레임워크는 다양한 제조 환경을 모델링하고 시뮬레이션할 수 있는 확장 가능한 구조를 제공합니다.

## 프로젝트 최종 목표의 흐름
**E-bom, M-bom, 추가정보 → 온톨로지 생성 후 인스턴스 추가 → SWRL언어를 사용하여 규칙 정의 후 pellet추론기를 사용하여 추론 → 프레임워크를 사용하여 '공정 시뮬레이션 자동생성'**

## 🎯 현재 단계 핵심 목표 (최우선)

### 온톨로지 기반 시뮬레이션 자동생성 구현
1. **기준 시나리오**: `scenario/scenario.py`는 기존 시뮬레이션 프레임워크를 사용해 만든 목표 시나리오
2. **온톨로지 입력**: `onto/` 폴더의 온톨로지 정보를 활용
   - `M-BOM.xml`: 제조 자재 명세서
   - `E-BOM.xml`: 엔지니어링 자재 명세서  
   - `inference_result.csv`: 추론 결과 데이터
   - `inferred_bom.owl`: 추론된 온톨로지 (필요시)
3. **자동생성 목표**: 온톨로지 정보를 input으로 받아 `scenario.py`와 유사한 시뮬레이션을 자동생성
4. **프레임워크 분석**: `scenario.py`가 프레임워크를 어떻게 활용하는지, 어떤 요소들을 입력받는지 분석 필요
5. **추가정보 요구**: scenario.py 수준의 공정 구현에 추가정보가 필요하면 사용자에게 요청

### 구현 단계
1. **scenario.py 분석**: 프레임워크 사용 패턴, 필수 입력 요소 파악
2. **온톨로지 정보 매핑**: 온톨로지 데이터를 프레임워크 컴포넌트로 변환
3. **자동생성 로직**: 온톨로지 → 시뮬레이션 코드 변환 시스템 구현
4. **검증 및 최적화**: 생성된 시나리오가 기준 시나리오와 동등한 수준인지 검증

## 핵심 아키텍처 이해

### BaseProcess 통합 아키텍처 (필수 이해)
- 모든 프로세스는 `src/Processes/base_process.py`의 `BaseProcess` 상속
- SimPy generator 패턴: `yield from self._execute_process()` 구조
- 배치 처리: `current_batch` 시스템으로 다중 아이템 동시 처리
- 자원 요구사항: `ResourceRequirement` 클래스로 타입 안전성 보장

### 프로세스 체이닝 시스템 (`src/Flow/`)
- `>>` 연산자로 프로세스 연결: `manufacturing >> transport >> assembly`
- `MultiProcessGroup`으로 병렬 실행 지원
- 자동 Transport 요청: 프로세스 간 자동 운송 처리

### AdvancedResourceManager (`src/core/resource_manager.py`)
- 모든 자원(Machine, Worker, Transport, Buffer) 통합 관리
- 실시간 자원 할당/해제 및 모니터링
- `ResourceRequirement` 기반 자원 검증 시스템

## 필수 개발 패턴

### 시나리오 작성 규칙
```python
# 모든 시나리오 파일 시작 부분 (필수)
import os
import sys
project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, project_root)

# 절대 경로 import 사용 (필수)
from src.core.simulation_engine import SimulationEngine
from src.Processes.manufacturing_process import ManufacturingProcess
```

### 프로세스 구현 패턴
```python
class NewProcess(BaseProcess):
    def _execute_process(self) -> Generator:
        """SimPy generator 패턴 (필수)"""
        # 자원 요청
        with self.resource_manager.request_resources(self.resource_requirements) as resources:
            # 처리 시간
            yield self.env.timeout(self.processing_time)
            # 결과 처리
            yield from self._handle_output()
```

## 코드 작성 원칙

### 1. SimPy 활용 극대화
- SimPy의 내장 메서드와 어트리뷰트를 최대한 활용하여 구현
- 커스텀 구현보다 SimPy의 기본 기능 우선 사용
- 예: `env.process()`, `env.timeout()`, `Resource`, `Container` 등

### 2. 기존 프레임워크 최대 활용
- 새로운 기능 추가 시 기존 프레임워크의 구조와 컴포넌트를 최대한 재사용
- 기존 클래스와 모듈의 기능을 확장하는 방향으로 개발
- 중복 구현을 피하고 기존 코드의 패턴과 아키텍처를 따를 것
- 예시:
  - 새로운 프로세스 타입 추가 시 `BaseProcess` 상속 활용
  - 리소스 관리는 기존 `ResourceManager` 확장
  - 통계 및 시각화는 기존 `statistics.py`, `visualization.py` 활용

### 3. 호환성 및 확장성
- 모든 새로운 기능은 기존 코드와 완벽한 하위 호환성 유지
- 기존 API를 변경하지 않고 새로운 기능 추가
- 인터페이스 변경 시 deprecation warning 제공

### 4. 코드 구조 및 스타일
- **Import 규칙**: 
  - 절대 경로 사용 (예시: `from src.core.machine import Machine`)
  - 상대 경로 import 금지
- **문서화**:
  - 모든 클래스, 메서드, 함수에 상세한 한국어 docstring 작성
  - 파라미터 타입 힌트 필수
- **예외 처리**:
  - 명확한 에러 메시지와 함께 적절한 예외 발생
  - 사용자가 문제를 쉽게 파악하고 해결할 수 있도록 가이드 제공

## 온톨로지 통합 워크플로우

### BOM to OWL 변환 (`onto/`)
- `bom_to_owl.py`: E-BOM, M-BOM을 OWL 온톨로지로 변환
- `infer.py`: SWRL 규칙과 Pellet 추론기를 통한 추론
- `template.py`: 온톨로지 템플릿 및 규칙 정의

### 자동 시뮬레이션 생성 (`owl_to_sim/`)
- 추론된 온톨로지에서 시뮬레이션 코드 자동 생성
- 프레임워크 컴포넌트를 활용한 시나리오 구성

## 핵심 컴포넌트 상호작용

### 실행 흐름
1. **시뮬레이션 엔진** (`SimulationEngine`) 초기화
2. **자원 관리자** (`AdvancedResourceManager`) 설정
3. **프로세스 체인** 구성 (`>>` 연산자 활용)
4. **통계 수집** (`CentralizedStatistics`) 자동 실행
5. **결과 시각화** (`visualization.py`) 및 로그 저장

### 자원 관리 패턴
- 모든 자원은 `ResourceBase` 상속
- `ResourceRequirement`로 자원 요구사항 명시
- `AdvancedResourceManager`를 통한 중앙 집중식 관리

## 출력 형식 가이드

### 코드 작성 시
- 시나리오 코드는 `scenario/` 폴더에 작성
- 실행 로그는 `log/` 폴더에 markdown으로 자동 저장
- 프로젝트 루트를 파이썬 모듈 검색 경로에 추가 필수

### 사용 가이드 작성 시
- 코드 예제 대신 텍스트 기반의 상세한 사용 가이드 제공
- 단계별 설명과 함께 개념적인 흐름 설명
- 주요 클래스와 메서드의 역할 및 상호작용 설명

## 디버깅 및 성능 최적화

### 일반적인 문제점
- Import 경로 오류: 절대 경로 사용 확인
- 자원 할당 실패: `ResourceRequirement` 검증
- 프로세스 블로킹: 출력 버퍼 용량 및 Transport 요청 확인

### 성능 고려사항
- 배치 처리 활용으로 처리량 최대화
- `AdvancedResourceManager`의 자원 풀링 기능 활용
- 통계 수집 오버헤드 최소화
