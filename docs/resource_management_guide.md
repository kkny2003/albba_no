# 자원 관리 시스템 가이드 (Resource Management Guide)

## 🎯 개요

이 프레임워크의 자원 관리 시스템은 제조 시뮬레이션에서 필요한 모든 자원을 통합적으로 관리할 수 있도록 설계되었습니다. 원자재부터 완제품, 기계, 작업자, 도구에 이르기까지 모든 요소를 체계적으로 추적하고 할당할 수 있습니다.

## 🔧 핵심 구성 요소

### 1. Resource 클래스

모든 자원의 기본이 되는 클래스입니다:

```python
from Resource.helper import Resource, ResourceType

# 기본 자원 생성
steel_sheet = Resource(
    resource_id="STEEL_001", 
    name="철판", 
    resource_type=ResourceType.RAW_MATERIAL, 
    quantity=100.0, 
    unit="kg"
)
```

### 2. ResourceType 열거형

지원되는 자원 타입들:

- **RAW_MATERIAL**: 원자재 (철강, 플라스틱, 화학물질 등)
- **SEMI_FINISHED**: 반제품 (가공된 부품, 중간 조립품 등)
- **FINISHED_PRODUCT**: 완제품 (최종 제품)
- **TOOL**: 도구 (드릴 비트, 커터, 측정기구 등)
- **ENERGY**: 에너지 (전력, 연료, 압축공기 등)
- **LABOR**: 인력 (작업자, 기술자, 검사원 등)

### 3. ResourceRequirement 클래스

프로세스에서 필요한 자원 요구사항을 정의합니다:

```python
from Resource.helper import ResourceRequirement

# 자원 요구사항 정의
material_req = ResourceRequirement(
    resource_type=ResourceType.RAW_MATERIAL,
    name="철판",
    quantity=5.0,
    unit="kg",
    is_consumed=True  # 소모성 자원 여부
)

tool_req = ResourceRequirement(
    resource_type=ResourceType.TOOL,
    name="드릴비트",
    quantity=1.0,
    unit="개",
    is_consumed=False  # 재사용 가능한 자원
)
```

## 🚀 기본 사용법

### 1. ResourceManager 초기화

```python
from core.resource_manager import ResourceManager

# 자원 관리자 생성
resource_manager = ResourceManager()
```

### 2. 자원 추가

```python
# 다양한 자원들을 풀에 추가
resources = [
    Resource("STEEL_001", "철판", ResourceType.RAW_MATERIAL, 100.0, "kg"),
    Resource("DRILL_001", "드릴비트", ResourceType.TOOL, 5.0, "개"),
    Resource("WORKER_001", "숙련작업자", ResourceType.LABOR, 1.0, "명"),
    Resource("POWER_001", "전력", ResourceType.ENERGY, 1000.0, "kWh")
]

for resource in resources:
    resource_manager.add_resource(resource)
    print(f"추가됨: {resource.name} ({resource.quantity} {resource.unit})")
```

### 3. 자원 할당 및 해제

```python
# 프로세스에 필요한 자원 요구사항 정의
requirements = [
    ResourceRequirement(ResourceType.RAW_MATERIAL, "철판", 10.0, "kg", True),
    ResourceRequirement(ResourceType.TOOL, "드릴비트", 1.0, "개", False),
    ResourceRequirement(ResourceType.LABOR, "숙련작업자", 1.0, "명", False)
]

# 자원 할당 시도
try:
    allocated_resources = resource_manager.allocate_resources(requirements)
    print("자원 할당 성공!")
    
    # 작업 수행...
    
    # 자원 해제
    resource_manager.release_resources(allocated_resources)
    print("자원 해제 완료!")
    
except Exception as e:
    print(f"자원 할당 실패: {e}")
```

## 🔍 고급 자원 관리

### 1. 자원 가용성 확인

```python
# 특정 타입의 사용 가능한 자원 조회
available_materials = resource_manager.get_available_resources(ResourceType.RAW_MATERIAL)
print(f"사용 가능한 원자재: {len(available_materials)}종")

for material in available_materials:
    print(f"  - {material.name}: {material.quantity} {material.unit}")

# 특정 자원의 사용 가능 여부 확인
def check_resource_availability(resource_manager, requirements):
    """자원 요구사항이 충족 가능한지 확인"""
    for req in requirements:
        available = resource_manager.get_available_resources(req.resource_type)
        available_quantity = sum(r.quantity for r in available if r.name == req.name)
        
        if available_quantity < req.quantity:
            print(f"⚠️ 자원 부족: {req.name} (필요: {req.quantity}, 가용: {available_quantity})")
            return False
    
    print("✅ 모든 자원 사용 가능")
    return True

# 사용 예제
check_resource_availability(resource_manager, requirements)
```

### 2. 자원 사용 추적

```python
class ResourceTracker:
    """자원 사용량을 추적하는 클래스"""
    
    def __init__(self):
        self.usage_history = []
        self.current_allocations = {}
    
    def track_allocation(self, resource, quantity, process_name):
        """자원 할당 추적"""
        allocation_record = {
            'timestamp': time.time(),
            'resource_id': resource.resource_id,
            'resource_name': resource.name,
            'quantity': quantity,
            'process': process_name,
            'action': 'allocate'
        }
        self.usage_history.append(allocation_record)
        
        # 현재 할당량 업데이트
        if resource.resource_id not in self.current_allocations:
            self.current_allocations[resource.resource_id] = 0
        self.current_allocations[resource.resource_id] += quantity
    
    def track_release(self, resource, quantity, process_name):
        """자원 해제 추적"""
        release_record = {
            'timestamp': time.time(),
            'resource_id': resource.resource_id,
            'resource_name': resource.name,
            'quantity': quantity,
            'process': process_name,
            'action': 'release'
        }
        self.usage_history.append(release_record)
        
        # 현재 할당량 업데이트
        if resource.resource_id in self.current_allocations:
            self.current_allocations[resource.resource_id] -= quantity
    
    def get_usage_summary(self):
        """자원 사용 요약 정보"""
        summary = {}
        for record in self.usage_history:
            resource_name = record['resource_name']
            if resource_name not in summary:
                summary[resource_name] = {'total_allocated': 0, 'total_released': 0}
            
            if record['action'] == 'allocate':
                summary[resource_name]['total_allocated'] += record['quantity']
            else:
                summary[resource_name]['total_released'] += record['quantity']
        
        return summary

# 사용 예제
tracker = ResourceTracker()
# 할당/해제 시 추적 코드 추가...
```

### 3. 자원 우선순위 관리

```python
class PriorityResourceManager(ResourceManager):
    """우선순위 기반 자원 관리자"""
    
    def __init__(self):
        super().__init__()
        self.allocation_queue = []  # (priority, request) 형태
    
    def request_resources_with_priority(self, requirements, priority, requester_id):
        """우선순위를 가진 자원 요청"""
        request = {
            'requirements': requirements,
            'requester_id': requester_id,
            'timestamp': time.time()
        }
        
        # 우선순위 큐에 추가 (낮은 숫자가 높은 우선순위)
        heapq.heappush(self.allocation_queue, (priority, request))
        
        return self.process_priority_queue()
    
    def process_priority_queue(self):
        """우선순위에 따라 자원 할당 처리"""
        while self.allocation_queue:
            priority, request = heapq.heappop(self.allocation_queue)
            
            try:
                # 자원 할당 시도
                allocated = self.allocate_resources(request['requirements'])
                print(f"우선순위 {priority} 요청 처리 완료: {request['requester_id']}")
                return allocated
                
            except Exception as e:
                print(f"우선순위 {priority} 요청 대기: {request['requester_id']} - {e}")
                # 다시 큐에 넣기 (또는 대기 큐로 이동)
                heapq.heappush(self.allocation_queue, (priority, request))
                break
        
        return None
```

## 📊 실제 활용 예제

### 자동차 제조 라인

```python
def setup_automotive_resources():
    """자동차 제조 라인 자원 설정"""
    resource_manager = ResourceManager()
    
    # 원자재
    steel_resources = [
        Resource("STEEL_SHEET_001", "강판", ResourceType.RAW_MATERIAL, 1000.0, "kg"),
        Resource("ALUMINUM_001", "알루미늄", ResourceType.RAW_MATERIAL, 500.0, "kg"),
        Resource("PLASTIC_001", "플라스틱", ResourceType.RAW_MATERIAL, 300.0, "kg")
    ]
    
    # 도구 및 장비
    tools = [
        Resource("PRESS_DIE_001", "프레스 금형", ResourceType.TOOL, 1.0, "세트"),
        Resource("WELDING_TORCH_001", "용접 토치", ResourceType.TOOL, 3.0, "개"),
        Resource("PAINTING_GUN_001", "도장 건", ResourceType.TOOL, 2.0, "개")
    ]
    
    # 에너지
    energy_resources = [
        Resource("ELECTRICITY_001", "전력", ResourceType.ENERGY, 10000.0, "kWh"),
        Resource("COMPRESSED_AIR_001", "압축공기", ResourceType.ENERGY, 5000.0, "L")
    ]
    
    # 모든 자원 추가
    all_resources = steel_resources + tools + energy_resources
    for resource in all_resources:
        resource_manager.add_resource(resource)
    
    return resource_manager

# 자동차 부품 제조 요구사항
door_manufacturing_requirements = [
    ResourceRequirement(ResourceType.RAW_MATERIAL, "강판", 50.0, "kg", True),
    ResourceRequirement(ResourceType.TOOL, "프레스 금형", 1.0, "세트", False),
    ResourceRequirement(ResourceType.ENERGY, "전력", 100.0, "kWh", True)
]

# 자원 할당 및 제조 시뮬레이션
auto_resource_manager = setup_automotive_resources()
allocated = auto_resource_manager.allocate_resources(door_manufacturing_requirements)
print("자동차 도어 제조를 위한 자원 할당 완료")
```

### 전자제품 조립 라인

```python
def setup_electronics_resources():
    """전자제품 조립 라인 자원 설정"""
    resource_manager = ResourceManager()
    
    # 전자 부품 (반제품)
    components = [
        Resource("PCB_001", "인쇄회로기판", ResourceType.SEMI_FINISHED, 100.0, "개"),
        Resource("CPU_001", "프로세서", ResourceType.SEMI_FINISHED, 50.0, "개"),
        Resource("MEMORY_001", "메모리", ResourceType.SEMI_FINISHED, 200.0, "개"),
        Resource("RESISTOR_001", "저항", ResourceType.SEMI_FINISHED, 1000.0, "개")
    ]
    
    # 조립 도구
    assembly_tools = [
        Resource("SOLDERING_IRON_001", "납땜인두", ResourceType.TOOL, 5.0, "개"),
        Resource("MULTIMETER_001", "멀티미터", ResourceType.TOOL, 3.0, "개"),
        Resource("PICK_PLACE_001", "픽앤플레이스", ResourceType.TOOL, 1.0, "대")
    ]
    
    # 모든 자원 추가
    all_resources = components + assembly_tools
    for resource in all_resources:
        resource_manager.add_resource(resource)
    
    return resource_manager

# 스마트폰 조립 요구사항
smartphone_assembly_requirements = [
    ResourceRequirement(ResourceType.SEMI_FINISHED, "인쇄회로기판", 1.0, "개", True),
    ResourceRequirement(ResourceType.SEMI_FINISHED, "프로세서", 1.0, "개", True),
    ResourceRequirement(ResourceType.SEMI_FINISHED, "메모리", 2.0, "개", True),
    ResourceRequirement(ResourceType.TOOL, "픽앤플레이스", 1.0, "대", False)
]
```

## ⚠️ 주의사항 및 베스트 프랙티스

### 1. 자원 관리 원칙

- **명확한 분류**: 각 자원을 적절한 ResourceType으로 분류하세요
- **정확한 수량**: 실제 사용량과 일치하는 수량을 설정하세요
- **적절한 단위**: 표준화된 단위를 사용하세요 (kg, 개, 시간 등)
- **소모성 구분**: 재사용 가능한 자원과 소모성 자원을 명확히 구분하세요

### 2. 성능 최적화

```python
# 자원 풀 최적화
def optimize_resource_pool(resource_manager):
    """자원 풀 사용량 분석 및 최적화"""
    resource_usage = {}
    
    # 각 자원 타입별 사용률 계산
    for resource_type in ResourceType:
        available = resource_manager.get_available_resources(resource_type)
        if available:
            total_capacity = sum(r.quantity for r in available)
            # 실제 사용량 데이터를 기반으로 사용률 계산
            usage_rate = calculate_usage_rate(resource_type)  # 구현 필요
            
            resource_usage[resource_type] = {
                'total_capacity': total_capacity,
                'usage_rate': usage_rate,
                'recommendation': 'increase' if usage_rate > 0.8 else 'optimal'
            }
    
    return resource_usage

# 자원 부족 예측
def predict_resource_shortage(resource_manager, production_plan):
    """생산 계획을 기반으로 자원 부족 예측"""
    shortage_predictions = []
    
    for plan_item in production_plan:
        required_resources = plan_item['requirements']
        production_quantity = plan_item['quantity']
        
        for req in required_resources:
            total_needed = req.quantity * production_quantity
            available = resource_manager.get_available_quantity(req.resource_type, req.name)
            
            if available < total_needed:
                shortage_predictions.append({
                    'resource': req.name,
                    'shortage': total_needed - available,
                    'plan_item': plan_item['name']
                })
    
    return shortage_predictions
```

### 3. 오류 처리

```python
class ResourceAllocationError(Exception):
    """자원 할당 관련 예외"""
    pass

class ResourceManager:
    def allocate_resources(self, requirements):
        """안전한 자원 할당"""
        allocated_resources = []
        
        try:
            # 모든 자원이 사용 가능한지 먼저 확인
            for req in requirements:
                if not self._check_availability(req):
                    raise ResourceAllocationError(f"자원 부족: {req.name}")
            
            # 실제 할당 수행
            for req in requirements:
                resource = self._allocate_single_resource(req)
                allocated_resources.append(resource)
            
            return allocated_resources
            
        except Exception as e:
            # 할당 실패 시 이미 할당된 자원들 모두 해제
            self._rollback_allocations(allocated_resources)
            raise ResourceAllocationError(f"자원 할당 실패: {e}")
    
    def _rollback_allocations(self, allocated_resources):
        """할당 롤백"""
        for resource in allocated_resources:
            try:
                self.release_resource(resource)
            except Exception as e:
                # 로깅 등의 처리
                print(f"롤백 중 오류: {e}")
```

## 🔗 관련 문서

- [API Reference - ResourceManager](api_reference.md#12-resourcemanager)
- [Process Chaining Guide](process_chaining.md)
- [Getting Started Guide](getting_started.md)
- [예제: Resource Management](../examples/resource_management_example.py)

---

효율적인 자원 관리는 성공적인 제조 시뮬레이션의 핵심입니다. 이 가이드의 원칙과 예제를 참조하여 여러분의 시뮬레이션에 최적화된 자원 관리 시스템을 구축하세요!
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
