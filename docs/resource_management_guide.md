# 통합 자원 관리 시스템 가이드

## 개요

모든 제조 시뮬레이션 요소(**Product, Worker, Machine, Transport 등**)를 **Resource**라는 하나의 통합된 개념으로 관리하는 시스템을 구축했습니다. 이를 통해 일관성 있고 확장 가능한 자원 관리가 가능해졌습니다.

## 핵심 설계 철학

🎯 **"모든 것은 Resource다"**
- **Product** (원자재, 반제품, 완제품) → Resource
- **Worker** (작업자, 기술자, 검사원) → Resource  
- **Machine** (제조기계, 조립기계, 검사장비) → Resource
- **Transport** (지게차, 컨베이어벨트, 운반카트) → Resource
- **Tool** (도구, 장비) → Resource
- **Energy** (전력, 연료) → Resource
- **Time** (작업시간, 대기시간) → Resource

## 주요 변경사항

### 1. 새로운 Resource 클래스 추가 (`src/models/resource.py`)

```python
class Resource:
    """제조 시뮬레이션에서 사용되는 자원을 정의하는 클래스"""
    
    def __init__(self, resource_id, name, resource_type, quantity, unit):
        # 자원의 고유 식별자, 이름, 타입, 수량, 단위 관리
```

### 지원하는 자원 타입들:
- **RAW_MATERIAL**: 원자재
- **SEMI_FINISHED**: 반제품
- **FINISHED_PRODUCT**: 완제품
- **MACHINE**: 기계
- **WORKER**: 작업자
- **TOOL**: 도구
- **TRANSPORT**: 운송/운반 (지게차, 컨베이어 벨트, 운반차 등)
- **ENERGY**: 에너지
- **TIME**: 시간

### 2. 통합 헬퍼 함수들

각 기존 모델(Product, Worker, Machine, Transport)을 Resource로 쉽게 변환할 수 있는 헬퍼 함수들을 제공합니다:

#### Product → Resource 변환
```python
raw_material = create_product_resource(
    product_id="raw_material_001",
    product_name="원자재",
    product_type=ResourceType.RAW_MATERIAL,
    quantity=10.0,
    sku="RM-001",
    unit="kg"
)
```

#### Worker → Resource 변환
```python
worker = create_worker_resource(
    worker_id="worker_001", 
    worker_name="제조작업자_1",
    skill_level="고급",
    department="제조부"
)
```

#### Machine → Resource 변환
```python
machine = create_machine_resource(
    machine_id="machine_001",
    machine_name="CNC 가공기",
    machine_type="CNC 가공기", 
    capacity=5.0  # 시간당 5개 가공 가능
)
```

#### Transport → Resource 변환
```python
forklift = create_transport_resource(
    transport_id="forklift_001",
    transport_name="지게차_1호",
    capacity=500.0,  # 500kg 운반 가능
    transport_type="지게차"
)
```

모든 공정의 기본 클래스에 다음 기능들을 추가했습니다:

#### 자원 관리 속성
```python
self.input_resources: List[Resource] = []  # 입력 자원 리스트
self.output_resources: List[Resource] = []  # 출력 자원 리스트
self.resource_requirements: List[ResourceRequirement] = []  # 자원 요구사항
```

#### 주요 메서드들
- `add_input_resource(resource)`: 입력 자원 추가
- `add_output_resource(resource)`: 출력 자원 추가
- `add_resource_requirement(requirement)`: 자원 요구사항 정의
- `validate_resources()`: 자원 요구사항 검증
- `consume_resources()`: 입력 자원 소비
- `produce_resources()`: 출력 자원 생산

#### 공정 실행 패턴
```python
def execute(self, input_data):
    # 1. 입력 자원 소비
    if not self.consume_resources(input_data):
        return None
    
    # 2. 구체적인 공정 로직 실행
    result = self.process_logic(input_data)
    
    # 3. 출력 자원 생산
    produced_resources = self.produce_resources(result)
    
    return {'result': result, 'produced_resources': produced_resources}
```

### 3. BaseProcess 클래스 확장 

모든 공정의 기본 클래스에 통합 자원 관리 기능을 추가했습니다:

- **입력 자원**: 원자재, 제조기계, 제조작업자
- **출력 자원**: 반제품
- **자원 요구사항**: 원자재 1.0kg (필수)

#### ManufacturingProcess (제조 공정)
```python
class ManufacturingProcess(BaseProcess):
    def __init__(self, machines, workers):
        super().__init__()
        self.machines = machines
        self.workers = workers
```

#### AssemblyProcess (조립 공정)
- **입력 자원**: 반제품, 조립기계, 조립작업자, 조립도구
- **출력 자원**: 완제품
- **자원 요구사항**: 반제품 2.0개, 조립도구 1.0세트 (필수)

#### QualityControlProcess (품질 관리 공정)
- **입력 자원**: 완제품, 검사장비, 품질검사원, 검사도구
- **출력 자원**: 검증완제품
- **자원 요구사항**: 완제품 1.0개, 검사도구 1.0세트 (필수)

### 4. ResourceManager 개선

자원의 전체 생명주기를 관리하는 고급 기능들을 추가했습니다:

```python
class ResourceManager:
    def add_resource(self, resource):
        """자원을 시스템에 등록"""
    
    def allocate_resource(self, resource_id, required_quantity):
        """특정 자원을 할당"""
    
    def allocate_by_requirement(self, requirement):
        """요구사항에 따라 자원 할당"""
    
    def release_resource(self, allocated_resource):
        """할당된 자원을 해제하고 재고로 반환"""
    
    def get_inventory_status(self):
        """현재 재고 상태 조회"""
```

## 사용 예제

### 기본 자원 생성
```python
from src.models.resource import Resource, ResourceType

# 원자재 자원 생성
raw_material = Resource(
    resource_id="raw_material_001",
    name="원자재",
    resource_type=ResourceType.RAW_MATERIAL,
    quantity=10.0,
    unit="kg"
)
```

### 공정에 자원 추가
```python
# 제조 공정 생성
manufacturing_process = ManufacturingProcess(
    machines=[machine1],
    workers=[worker1]
)

# 입력 자원 추가
manufacturing_process.add_input_resource(raw_material)

# 공정 실행
result = manufacturing_process.execute("제품_A")
```

### 공정 체인 구성
```python
# 제조 → 조립 → 품질검사 체인
manufacturing_result = manufacturing_process.execute("기본제품")
assembly_result = assembly_process.execute(manufacturing_result['result'])
quality_result = quality_control.execute(assembly_result['result'])
```

## 장점

1. **통합된 자원 관리**: Product, Worker, Machine, Transport가 모두 Resource로 일관되게 관리
2. **현실적인 시뮬레이션**: 실제 제조업의 자원 소비와 생산 패턴을 정확히 반영
3. **명확한 자원 추적**: 모든 자원의 이동과 변화를 완전히 추적 가능
4. **확장성**: 새로운 자원 타입과 공정을 쉽게 추가 가능
5. **검증 기능**: 자원 부족 상황을 사전에 감지
6. **유연한 설계**: 다양한 제조 시나리오에 적용 가능
7. **코드 일관성**: 모든 자원이 동일한 인터페이스로 관리되어 코드 복잡성 감소

## 실행 예제

`examples/resource_management_example.py` 파일을 실행하면 전체 자원 관리 시스템의 동작을 확인할 수 있습니다:

```bash
python examples/resource_management_example.py
```

이 예제는 다음과 같은 통합 자원 관리 시나리오를 보여줍니다:
1. **Product 자원**: 원자재(10kg) → 반제품(1개) → 완제품(1개) → 검증완제품(1개)
2. **Worker 자원**: 제조작업자(고급) + 조립작업자(중급) + 품질검사원(고급)  
3. **Machine 자원**: CNC 가공기(5개/시간) + 자동 조립기(3개/시간) + 검사장비
4. **Transport 자원**: 지게차(500kg) + 컨베이어벨트(100개/분) + 운반카트(50개)
5. 전체 자원 재고 상태 실시간 추적

## 마이그레이션 가이드

기존 코드를 새로운 통합 자원 관리 시스템으로 마이그레이션하려면:

### 1. 기존 모델들을 Resource로 변환
```python
# 기존 방식
product = Product(name="제품A", sku="P001", quantity=10)
worker = Worker(name="작업자1", skill_level="고급") 
machine = Machine(machine_id="M001", machine_type="CNC")

# 새로운 방식 (헬퍼 함수 사용)
product = create_product_resource("P001", "제품A", ResourceType.FINISHED_PRODUCT, 10.0)
worker = create_worker_resource("W001", "작업자1", "고급", "제조부")
machine = create_machine_resource("M001", "CNC_가공기", "CNC", 5.0)
```

### 2. 공정 클래스 업데이트
- **공정 초기화 시 자원 설정 추가**
- **execute 메서드를 process_logic 메서드로 분리**  
- **입력/출력 자원 명시적 정의**
- **자원 요구사항 정의**

### 3. 자원 관리자 활용
```python
# ResourceManager를 통한 중앙집중식 자원 관리
resource_manager = ResourceManager()
resource_manager.add_resource(product)
resource_manager.add_resource(worker)
resource_manager.add_resource(machine)

# 자원 할당 및 해제
allocated_worker = resource_manager.allocate_resource("W001", 1.0)
resource_manager.release_resource(allocated_worker)
```

이러한 변경을 통해 제조 시뮬레이션 프레임워크가 **완전히 통합된 자원 관리 시스템**을 갖추게 되었습니다! 🎯✨
