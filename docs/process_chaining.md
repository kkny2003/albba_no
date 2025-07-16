# 프로세스 체이닝 가이드 (Process Chaining Guide)

## 🔗 개요

프로세스 체이닝은 이 프레임워크의 핵심 기능으로, `>>` 연산자를 사용하여 여러 제조 공정을 직관적이고 간단하게 연결할 수 있습니다. 이 기능을 통해 복잡한 제조 워크플로우를 마치 파이프라인처럼 구성할 수 있습니다.

## ✨ 주요 특징

- **직관적인 문법**: `공정A >> 공정B >> 공정C` 형태로 간단하게 연결
- **우선순위 지원**: 프로세스명에 우선순위 포함 가능 (예: "드릴링(1)")
- **유연한 구성**: 동적으로 프로세스 추가/제거 가능
- **오류 처리**: 체인 실행 중 오류 발생 시 적절한 예외 처리
- **타입 검증**: 프로세스 간 입출력 타입 호환성 확인

## 🚀 기본 사용법

### 1. 기본 프로세스 정의

```python
from processes.manufacturing_process import ManufacturingProcess
from processes.assembly_process import AssemblyProcess
from processes.quality_control_process import QualityControlProcess
from Resource.helper import ResourceRequirement, ResourceType

# 자원 요구사항 정의
manufacturing_requirements = [
    ResourceRequirement(ResourceType.RAW_MATERIAL, "철강", 5.0, "kg", True),
    ResourceRequirement(ResourceType.TOOL, "드릴", 1.0, "개", False)
]

assembly_requirements = [
    ResourceRequirement(ResourceType.SEMI_FINISHED, "가공품", 2.0, "개", True),
    ResourceRequirement(ResourceType.TOOL, "조립도구", 1.0, "세트", False)
]

# 프로세스 인스턴스 생성
manufacturing = ManufacturingProcess(
    name="드릴링공정", 
    required_resources=manufacturing_requirements, 
    processing_time=2.5
)

assembly = AssemblyProcess(
    name="조립공정", 
    required_components=assembly_requirements, 
    assembly_time=3.0
)

quality_control = QualityControlProcess(
    name="품질검사", 
    pass_rate=0.95, 
    inspection_time=1.0
)
```

### 2. 프로세스 체이닝

#### 📌 방법 1: 순차적 체이닝
```python
# 두 프로세스 연결
simple_chain = manufacturing >> assembly
print(f"체인 구성: {simple_chain.get_process_count()}개 프로세스")

# 여러 프로세스 연결
complete_chain = manufacturing >> assembly >> quality_control
print(f"완전 체인: {complete_chain.get_process_count()}개 프로세스")
```

#### 📌 방법 2: 동적 체이닝
```python
# 빈 체인으로 시작
from processes.base_process import ProcessChain

chain = ProcessChain()
chain.add_process(manufacturing)
chain.add_process(assembly)
chain.add_process(quality_control)
```

### 3. 우선순위 시스템

```python
# 우선순위가 포함된 프로세스 정의
priority_drilling = ManufacturingProcess("드릴링(1)", manufacturing_requirements, 2.0)
priority_milling = ManufacturingProcess("밀링(2)", manufacturing_requirements, 2.5)
priority_assembly = AssemblyProcess("조립(3)", assembly_requirements, 3.0)

# 우선순위에 따라 자동 정렬되어 실행
priority_chain = priority_drilling >> priority_milling >> priority_assembly

# 우선순위 파싱 확인
from processes.base_process import parse_process_priority
name, priority = parse_process_priority("드릴링(1)")
print(f"프로세스명: {name}, 우선순위: {priority}")  # 프로세스명: 드릴링, 우선순위: 1
```
## 🎯 체이닝 실행

### 1. 기본 실행 방법

```python
from core.simulation_engine import SimulationEngine
from core.resource_manager import ResourceManager
from Resource.product import Product

# 시뮬레이션 환경 설정
engine = SimulationEngine(random_seed=123)
resource_manager = ResourceManager()
product = Product("P001", "테스트제품")

# 프로세스 체인 실행
def run_process_chain(env):
    yield from complete_chain.execute(product, env, resource_manager)

# 시뮬레이션에 추가하고 실행
engine.add_process(run_process_chain)
engine.run(until=50)
```

### 2. 배치 처리

```python
def batch_processing(env, products, chain, resource_manager):
    """여러 제품을 배치로 처리"""
    for product in products:
        print(f"제품 {product.product_id} 처리 시작")
        yield from chain.execute(product, env, resource_manager)
        print(f"제품 {product.product_id} 처리 완료")

# 제품 리스트 생성
products = [Product(f"P{i:03d}", "배치제품") for i in range(1, 6)]

# 배치 처리 실행
engine.add_process(batch_processing, products, complete_chain, resource_manager)
```

## 🔧 고급 기능

### 1. 조건부 체이닝

```python
def conditional_chain(product, quality_score):
    """품질 점수에 따른 조건부 프로세스 체이닝"""
    base_chain = manufacturing >> assembly
    
    if quality_score >= 0.95:
        # 고품질: 프리미엄 포장
        premium_packaging = ManufacturingProcess("프리미엄포장", packaging_req, 2.0)
        return base_chain >> premium_packaging
    elif quality_score >= 0.80:
        # 표준품질: 일반 포장
        standard_packaging = ManufacturingProcess("일반포장", packaging_req, 1.0)
        return base_chain >> standard_packaging
    else:
        # 저품질: 재작업
        rework = ManufacturingProcess("재작업", rework_req, 4.0)
        return base_chain >> rework >> quality_control

# 사용 예제
quality_score = 0.92
dynamic_chain = conditional_chain(product, quality_score)
yield from dynamic_chain.execute(product, env, resource_manager)
```

### 2. 병렬 프로세스 지원

```python
from processes.advanced_workflow import AdvancedWorkflow

# 병렬로 실행할 프로세스들
parallel_processes = [
    ManufacturingProcess("가공1", req1, 2.0),
    ManufacturingProcess("가공2", req2, 2.5),
    ManufacturingProcess("가공3", req3, 1.8)
]

# 병렬 실행 후 조립
workflow = AdvancedWorkflow()
yield from workflow.execute_parallel(parallel_processes, products, env, resource_manager)

# 병렬 처리 후 조립 공정
final_assembly = AssemblyProcess("최종조립", final_req, 3.0)
yield from final_assembly.execute(products, env, resource_manager)
```

### 3. 체인 검증 및 오류 처리

```python
def validate_and_execute_chain(chain, product, env, resource_manager):
    """체인 유효성 검사 후 실행"""
    try:
        # 체인 유효성 검사
        if not chain.validate_chain():
            raise ValueError("체인 구성이 올바르지 않습니다")
        
        # 입력 제품 유효성 검사
        if not chain.validate_input(product):
            raise ValueError(f"제품 {product.product_id}는 이 체인에 적합하지 않습니다")
        
        # 체인 실행
        yield from chain.execute(product, env, resource_manager)
        
    except Exception as e:
        print(f"체인 실행 중 오류 발생: {e}")
        # 오류 처리 로직 (예: 대체 프로세스, 알림 등)
```

## 📊 성능 최적화

### 1. 체인 분석

```python
def analyze_chain_performance(chain):
    """프로세스 체인의 성능 분석"""
    total_time = 0
    bottleneck_process = None
    max_time = 0
    
    for process in chain.processes:
        if hasattr(process, 'processing_time'):
            time = process.processing_time
            total_time += time
            
            if time > max_time:
                max_time = time
                bottleneck_process = process
    
    print(f"총 처리 시간: {total_time:.2f}시간")
    print(f"병목 공정: {bottleneck_process.name} ({max_time:.2f}시간)")
    print(f"이론적 최대 처리량: {1/max_time:.2f}개/시간")
    
    return {
        'total_time': total_time,
        'bottleneck': bottleneck_process,
        'max_throughput': 1/max_time
    }

# 체인 성능 분석
performance = analyze_chain_performance(complete_chain)
```

### 2. 자원 사용 최적화

```python
def optimize_resource_allocation(chain, resource_manager):
    """체인의 자원 사용을 최적화"""
    resource_usage = {}
    
    for process in chain.processes:
        if hasattr(process, 'required_resources'):
            for req in process.required_resources:
                resource_type = req.resource_type
                quantity = req.quantity
                
                if resource_type not in resource_usage:
                    resource_usage[resource_type] = 0
                resource_usage[resource_type] += quantity
    
    print("체인의 자원 사용량:")
    for resource_type, total_quantity in resource_usage.items():
        print(f"  {resource_type.name}: {total_quantity}")
        
        # 사용 가능한 자원과 비교
        available = resource_manager.get_available_resources(resource_type)
        if available:
            available_quantity = sum(r.quantity for r in available)
            if total_quantity > available_quantity:
                print(f"    ⚠️ 경고: 자원 부족 (필요: {total_quantity}, 사용가능: {available_quantity})")
```

## 🛠️ 실제 활용 예제

### 자동차 부품 제조 라인

```python
# 자동차 부품 제조 프로세스 체인
stamping = ManufacturingProcess("프레스가공(1)", stamping_req, 1.5)
welding = ManufacturingProcess("용접(2)", welding_req, 2.0)
painting = ManufacturingProcess("도장(3)", painting_req, 3.0)
assembly = AssemblyProcess("조립(4)", assembly_req, 2.5)
inspection = QualityControlProcess("검사(5)", pass_rate=0.98, inspection_time=0.5)

# 완전한 제조 라인
auto_parts_line = stamping >> welding >> painting >> assembly >> inspection

print("자동차 부품 제조 라인:")
performance = analyze_chain_performance(auto_parts_line)
```

### 전자제품 조립 라인

```python
# 전자제품 조립 프로세스
pcb_assembly = AssemblyProcess("PCB조립(1)", pcb_req, 1.0)
component_mounting = ManufacturingProcess("부품실장(2)", mounting_req, 1.5)
soldering = ManufacturingProcess("납땜(3)", soldering_req, 2.0)
testing = QualityControlProcess("전기테스트(4)", pass_rate=0.95, inspection_time=1.0)
packaging = ManufacturingProcess("포장(5)", packaging_req, 0.5)

# 전자제품 제조 라인
electronics_line = pcb_assembly >> component_mounting >> soldering >> testing >> packaging

# 불량품 재작업 경로
rework_line = ManufacturingProcess("재작업", rework_req, 3.0) >> testing

print("전자제품 제조 라인:")
performance = analyze_chain_performance(electronics_line)
```

## ⚠️ 주의사항 및 베스트 프랙티스

### 1. 체인 설계 원칙

- **단일 책임**: 각 프로세스는 하나의 명확한 작업을 수행해야 합니다
- **느슨한 결합**: 프로세스 간 의존성을 최소화하세요
- **오류 처리**: 각 단계에서 적절한 오류 처리를 구현하세요
- **유연성**: 동적으로 체인을 수정할 수 있도록 설계하세요

### 2. 성능 고려사항

- **병목 식별**: 가장 긴 처리 시간을 갖는 프로세스가 전체 성능을 결정합니다
- **자원 공유**: 여러 프로세스가 같은 자원을 사용할 때 대기 시간을 고려하세요
- **배치 크기**: 적절한 배치 크기로 처리 효율성을 높이세요

### 3. 디버깅 팁

```python
# 체인 실행 과정 추적
def debug_chain_execution(chain, product, env, resource_manager):
    """체인 실행 과정을 상세히 추적"""
    print(f"체인 실행 시작: {product.product_id}")
    
    for i, process in enumerate(chain.processes):
        print(f"  단계 {i+1}: {process.name} 시작 (시간: {env.now:.2f})")
        start_time = env.now
        
        try:
            yield from process.execute(product, env, resource_manager)
            end_time = env.now
            print(f"  단계 {i+1}: {process.name} 완료 (소요시간: {end_time-start_time:.2f})")
            
        except Exception as e:
            print(f"  단계 {i+1}: {process.name} 실패 - {e}")
            break
    
    print(f"체인 실행 완료: {product.product_id}")
```

## 🔗 관련 문서

- [API Reference - BaseProcess](api_reference.md#31-baseprocess)
- [Resource Management Guide](resource_management_guide.md)
- [Getting Started Guide](getting_started.md)
- [예제: Process Chaining](../examples/process_chaining_example.py)

---

프로세스 체이닝은 복잡한 제조 워크플로우를 간단하고 직관적으로 구성할 수 있게 해주는 강력한 기능입니다. 이 가이드의 예제들을 참조하여 여러분만의 제조 프로세스 체인을 구성해보세요!

## 주요 특징

1. **직관적인 문법**: `공정1 >> 공정2 >> 공정3` 형태로 자연스러운 흐름 표현
2. **체인 관리**: 연결된 공정들을 `ProcessChain` 객체로 관리
3. **순차 실행**: 체인의 모든 공정을 순서대로 실행 가능
4. **연결 추적**: 각 공정의 이전/다음 공정 관계 자동 관리
5. **확장성**: 기존 체인에 새로운 공정이나 체인 추가 가능

## 지원되는 공정 클래스

- `ManufacturingProcess`: 제조 공정
- `AssemblyProcess`: 조립 공정  
- `QualityControlProcess`: 품질 관리 공정
- 모든 `BaseProcess`를 상속받는 사용자 정의 공정

## 실행 예제

전체 예제는 `examples/process_chain_example.py`에서 확인할 수 있습니다:

```bash
python -m examples.process_chain_example
```

## 확장 방법

새로운 공정 타입을 추가하려면 `BaseProcess`를 상속받아 `execute` 메서드를 구현하면 됩니다:

```python
from src.processes.base_process import BaseProcess

class CustomProcess(BaseProcess):
    def __init__(self, custom_params, process_id=None, process_name=None):
        super().__init__(process_id, process_name or "사용자정의공정")
        self.custom_params = custom_params
    
    def execute(self, input_data=None):
        # 공정 실행 로직 구현
        print(f"[{self.process_name}] 사용자 정의 공정 실행")
        return input_data
```

이제 `CustomProcess`도 `>>` 연산자를 사용하여 다른 공정들과 연결할 수 있습니다.
