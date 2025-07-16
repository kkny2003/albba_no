# 필수 자원 및 고급 기능 가이드

## 🎯 개요

이 가이드는 프레임워크의 고급 기능들과 각 프로세스에서 필수로 정의해야 하는 자원 정보에 대해 설명합니다. 올바른 자원 정의를 통해 시뮬레이션의 정확성과 현실성을 높일 수 있습니다.

## 📋 필수 자원 정의

모든 프로세스 클래스는 다음 자원 정보를 명확히 정의해야 합니다:

### 🔄 자원 분류

1. **입력 자원 (Input Resources)**: 프로세스가 소비하거나 사용하는 자원
2. **출력 자원 (Output Resources)**: 프로세스가 생산하거나 변환하는 자원  
3. **자원 요구사항 (Resource Requirements)**: 프로세스 실행에 필요한 구체적 요구사항

### 📝 기본 작성 패턴

```python
from Resource.helper import Resource, ResourceRequirement, ResourceType

# 1. 입력 자원 정의
input_resources = [
    Resource("RAW_STEEL_001", "원강재", ResourceType.RAW_MATERIAL, 100.0, "kg"),
    Resource("CUTTING_OIL_001", "절삭유", ResourceType.RAW_MATERIAL, 5.0, "L")
]

# 2. 출력 자원 정의  
output_resources = [
    Resource("MACHINED_PART_001", "가공부품", ResourceType.SEMI_FINISHED, 1.0, "개"),
    Resource("STEEL_SCRAP_001", "철스크랩", ResourceType.RAW_MATERIAL, 10.0, "kg")
]

# 3. 자원 요구사항 정의
resource_requirements = [
    ResourceRequirement(ResourceType.RAW_MATERIAL, "원강재", 50.0, "kg", True),
    ResourceRequirement(ResourceType.TOOL, "절삭공구", 1.0, "개", False),
    ResourceRequirement(ResourceType.ENERGY, "전력", 25.0, "kWh", True)
]

# 4. 프로세스 생성
from processes.manufacturing_process import ManufacturingProcess

machining_process = ManufacturingProcess(
    name="가공공정",
    required_resources=resource_requirements,
    processing_time=3.0
)
```

## 🏭 프로세스별 자원 정의 가이드

### 1. ManufacturingProcess (제조 공정)

```python
# 드릴링 공정 예제
drilling_requirements = [
    ResourceRequirement(ResourceType.RAW_MATERIAL, "원자재", 10.0, "kg", True),
    ResourceRequirement(ResourceType.TOOL, "드릴비트", 1.0, "개", False),
    ResourceRequirement(ResourceType.ENERGY, "전력", 15.0, "kWh", True)
]

drilling_process = ManufacturingProcess(
    name="드릴링공정",
    required_resources=drilling_requirements,
    processing_time=2.5
)

# 용접 공정 예제
welding_requirements = [
    ResourceRequirement(ResourceType.SEMI_FINISHED, "가공부품", 2.0, "개", True),
    ResourceRequirement(ResourceType.RAW_MATERIAL, "용접봉", 0.5, "kg", True),
    ResourceRequirement(ResourceType.TOOL, "용접기", 1.0, "대", False),
    ResourceRequirement(ResourceType.ENERGY, "전력", 30.0, "kWh", True)
]

welding_process = ManufacturingProcess(
    name="용접공정",
    required_resources=welding_requirements,
    processing_time=4.0
)
```

### 2. AssemblyProcess (조립 공정)

```python
# 엔진 조립 예제
engine_assembly_requirements = [
    ResourceRequirement(ResourceType.SEMI_FINISHED, "실린더블록", 1.0, "개", True),
    ResourceRequirement(ResourceType.SEMI_FINISHED, "피스톤", 4.0, "개", True),
    ResourceRequirement(ResourceType.SEMI_FINISHED, "크랭크샤프트", 1.0, "개", True),
    ResourceRequirement(ResourceType.RAW_MATERIAL, "엔진오일", 4.0, "L", True),
    ResourceRequirement(ResourceType.TOOL, "조립도구세트", 1.0, "세트", False)
]

engine_assembly = AssemblyProcess(
    name="엔진조립",
    required_components=engine_assembly_requirements,
    assembly_time=8.0
)

# 전자부품 조립 예제
pcb_assembly_requirements = [
    ResourceRequirement(ResourceType.SEMI_FINISHED, "PCB기판", 1.0, "개", True),
    ResourceRequirement(ResourceType.SEMI_FINISHED, "CPU", 1.0, "개", True),
    ResourceRequirement(ResourceType.SEMI_FINISHED, "메모리칩", 2.0, "개", True),
    ResourceRequirement(ResourceType.RAW_MATERIAL, "납땜", 0.1, "kg", True),
    ResourceRequirement(ResourceType.TOOL, "납땜인두", 1.0, "개", False)
]

pcb_assembly = AssemblyProcess(
    name="PCB조립",
    required_components=pcb_assembly_requirements,
    assembly_time=3.0
)
```

### 3. QualityControlProcess (품질 관리 공정)

```python
# 기계적 품질 검사
mechanical_inspection_requirements = [
    ResourceRequirement(ResourceType.TOOL, "측정기구", 1.0, "세트", False),
    ResourceRequirement(ResourceType.TOOL, "게이지", 1.0, "개", False),
    ResourceRequirement(ResourceType.ENERGY, "압축공기", 10.0, "L", True)
]

mechanical_qc = QualityControlProcess(
    name="기계적검사",
    pass_rate=0.95,
    inspection_time=1.5
)

# 전기적 품질 검사  
electrical_inspection_requirements = [
    ResourceRequirement(ResourceType.TOOL, "멀티미터", 1.0, "개", False),
    ResourceRequirement(ResourceType.TOOL, "오실로스코프", 1.0, "대", False),
    ResourceRequirement(ResourceType.ENERGY, "전력", 5.0, "kWh", True)
]

electrical_qc = QualityControlProcess(
    name="전기적검사",
    pass_rate=0.98,
    inspection_time=2.0
)
```

## 🔧 고급 자원 관리 패턴

### 1. 동적 자원 요구사항

```python
class DynamicManufacturingProcess(ManufacturingProcess):
    """동적으로 자원 요구사항이 변하는 제조 공정"""
    
    def __init__(self, name, base_requirements, processing_time):
        super().__init__(name, base_requirements, processing_time)
        self.base_requirements = base_requirements
    
    def get_dynamic_requirements(self, product, env_conditions):
        """환경 조건에 따라 동적으로 자원 요구사항 계산"""
        dynamic_requirements = self.base_requirements.copy()
        
        # 제품 크기에 따른 재료 사용량 조정
        if hasattr(product, 'size_factor'):
            for req in dynamic_requirements:
                if req.resource_type == ResourceType.RAW_MATERIAL:
                    req.quantity *= product.size_factor
        
        # 환경 온도에 따른 에너지 사용량 조정
        if 'temperature' in env_conditions:
            temp = env_conditions['temperature']
            energy_factor = 1.0 + (temp - 20) * 0.02  # 20도 기준으로 ±2%/도
            
            for req in dynamic_requirements:
                if req.resource_type == ResourceType.ENERGY:
                    req.quantity *= energy_factor
        
        return dynamic_requirements

# 사용 예제
base_reqs = [
    ResourceRequirement(ResourceType.RAW_MATERIAL, "강재", 10.0, "kg", True),
    ResourceRequirement(ResourceType.ENERGY, "전력", 20.0, "kWh", True)
]

dynamic_process = DynamicManufacturingProcess("동적가공", base_reqs, 3.0)

# 환경 조건과 제품 특성에 따른 자원 요구사항 계산
product = Product("LARGE_001", "대형부품")
product.size_factor = 1.5

env_conditions = {'temperature': 25, 'humidity': 60}
actual_requirements = dynamic_process.get_dynamic_requirements(product, env_conditions)
```

### 2. 자원 대체 가능성

```python
class FlexibleResourceRequirement(ResourceRequirement):
    """대체 가능한 자원을 포함한 요구사항"""
    
    def __init__(self, primary_resource, alternative_resources=None, **kwargs):
        super().__init__(**kwargs)
        self.primary_resource = primary_resource
        self.alternative_resources = alternative_resources or []
    
    def get_available_options(self, resource_manager):
        """사용 가능한 자원 옵션 반환"""
        options = []
        
        # 주요 자원 확인
        if resource_manager.is_available(self.primary_resource):
            options.append(self.primary_resource)
        
        # 대체 자원 확인
        for alt_resource in self.alternative_resources:
            if resource_manager.is_available(alt_resource):
                options.append(alt_resource)
        
        return options

# 사용 예제
primary_steel = Resource("HIGH_CARBON_STEEL", "고탄소강", ResourceType.RAW_MATERIAL, 50.0, "kg")
alt_steel_1 = Resource("MEDIUM_CARBON_STEEL", "중탄소강", ResourceType.RAW_MATERIAL, 55.0, "kg")
alt_steel_2 = Resource("ALLOY_STEEL", "합금강", ResourceType.RAW_MATERIAL, 45.0, "kg")

flexible_req = FlexibleResourceRequirement(
    primary_resource=primary_steel,
    alternative_resources=[alt_steel_1, alt_steel_2],
    resource_type=ResourceType.RAW_MATERIAL,
    name="강재",
    quantity=50.0,
    unit="kg",
    is_consumed=True
)
```

### 3. 자원 품질 등급

```python
class GradedResource(Resource):
    """품질 등급이 있는 자원"""
    
    def __init__(self, resource_id, name, resource_type, quantity, unit, grade='A'):
        super().__init__(resource_id, name, resource_type, quantity, unit)
        self.grade = grade  # A, B, C 등급
        self.quality_factor = self._get_quality_factor(grade)
    
    def _get_quality_factor(self, grade):
        """품질 등급에 따른 품질 계수"""
        grade_factors = {
            'A': 1.0,    # 최고 품질
            'B': 0.9,    # 양호 품질  
            'C': 0.8,    # 보통 품질
            'D': 0.7     # 최저 품질
        }
        return grade_factors.get(grade, 0.8)

# 사용 예제
premium_steel = GradedResource("STEEL_A_001", "프리미엄강재", ResourceType.RAW_MATERIAL, 100.0, "kg", 'A')
standard_steel = GradedResource("STEEL_B_001", "표준강재", ResourceType.RAW_MATERIAL, 100.0, "kg", 'B')
economy_steel = GradedResource("STEEL_C_001", "이코노미강재", ResourceType.RAW_MATERIAL, 100.0, "kg", 'C')

# 품질에 따른 처리 시간 조정 로직
def adjust_processing_time_by_quality(base_time, resource_quality_factor):
    """자원 품질에 따른 처리 시간 조정"""
    # 고품질 자원일수록 처리 시간 단축
    return base_time / resource_quality_factor
```

## 📊 자원 최적화 전략

### 1. 자원 사용 효율성 분석

```python
def analyze_resource_efficiency(process_chain, resource_manager):
    """프로세스 체인의 자원 사용 효율성 분석"""
    
    efficiency_metrics = {}
    
    for process in process_chain.processes:
        process_name = process.name
        requirements = process.required_resources if hasattr(process, 'required_resources') else []
        
        # 자원별 효율성 계산
        for req in requirements:
            resource_name = req.name
            required_quantity = req.quantity
            
            # 실제 사용량 대비 요구량 비율 (예시)
            actual_usage = get_actual_usage(process_name, resource_name)  # 구현 필요
            efficiency = actual_usage / required_quantity if required_quantity > 0 else 0
            
            if resource_name not in efficiency_metrics:
                efficiency_metrics[resource_name] = []
            
            efficiency_metrics[resource_name].append({
                'process': process_name,
                'efficiency': efficiency,
                'waste': max(0, required_quantity - actual_usage)
            })
    
    # 개선 제안 생성
    recommendations = []
    for resource_name, metrics in efficiency_metrics.items():
        avg_efficiency = sum(m['efficiency'] for m in metrics) / len(metrics)
        total_waste = sum(m['waste'] for m in metrics)
        
        if avg_efficiency < 0.8:
            recommendations.append(f"{resource_name}: 효율성 개선 필요 (현재 {avg_efficiency:.1%})")
        
        if total_waste > 10:
            recommendations.append(f"{resource_name}: 폐기물 감소 필요 (현재 {total_waste:.1f})")
    
    return efficiency_metrics, recommendations

# 사용 예제
# efficiency, recommendations = analyze_resource_efficiency(complete_chain, resource_manager)
# print("자원 효율성 분석 결과:")
# for rec in recommendations:
#     print(f"  - {rec}")
```

### 2. 자원 예측 및 계획

```python
class ResourcePlanner:
    """자원 계획 및 예측 도구"""
    
    def __init__(self, resource_manager):
        self.resource_manager = resource_manager
        self.usage_history = []
    
    def predict_resource_needs(self, production_schedule, horizon_days=30):
        """생산 계획을 바탕으로 자원 필요량 예측"""
        
        predictions = {}
        
        for schedule_item in production_schedule:
            product_type = schedule_item['product_type']
            quantity = schedule_item['quantity']
            due_date = schedule_item['due_date']
            
            # 제품 타입별 표준 자원 요구사항 조회
            standard_requirements = self.get_standard_requirements(product_type)
            
            for req in standard_requirements:
                resource_name = req.name
                total_needed = req.quantity * quantity
                
                if resource_name not in predictions:
                    predictions[resource_name] = {
                        'total_needed': 0,
                        'peak_daily_need': 0,
                        'schedule_items': []
                    }
                
                predictions[resource_name]['total_needed'] += total_needed
                predictions[resource_name]['schedule_items'].append({
                    'due_date': due_date,
                    'quantity_needed': total_needed,
                    'product_type': product_type
                })
                
                # 일일 최대 필요량 계산
                daily_need = total_needed / max(1, (due_date - datetime.now()).days)
                predictions[resource_name]['peak_daily_need'] = max(
                    predictions[resource_name]['peak_daily_need'], 
                    daily_need
                )
        
        return predictions
    
    def generate_procurement_plan(self, predictions):
        """자원 예측을 바탕으로 조달 계획 생성"""
        procurement_plan = []
        
        for resource_name, prediction in predictions.items():
            current_stock = self.resource_manager.get_current_stock(resource_name)
            total_needed = prediction['total_needed']
            
            if current_stock < total_needed:
                shortage = total_needed - current_stock
                procurement_plan.append({
                    'resource': resource_name,
                    'current_stock': current_stock,
                    'total_needed': total_needed,
                    'to_procure': shortage,
                    'urgency': 'high' if shortage > current_stock * 2 else 'medium'
                })
        
        return procurement_plan

# 사용 예제
planner = ResourcePlanner(resource_manager)
schedule = [
    {'product_type': 'ProductA', 'quantity': 100, 'due_date': datetime(2024, 1, 15)},
    {'product_type': 'ProductB', 'quantity': 50, 'due_date': datetime(2024, 1, 20)}
]

predictions = planner.predict_resource_needs(schedule)
procurement_plan = planner.generate_procurement_plan(predictions)
```

## ⚠️ 주의사항 및 베스트 프랙티스

### 1. 자원 정의 원칙

- **정확한 수량**: 실제 생산 데이터를 기반으로 정확한 자원 사용량을 정의하세요
- **적절한 단위**: 표준화된 측정 단위를 일관성 있게 사용하세요
- **현실적인 요구사항**: 과도하게 많거나 적은 자원 요구사항을 피하세요
- **소모성 구분**: 재사용 가능한 자원과 소모성 자원을 명확히 구분하세요

### 2. 성능 최적화

- **자원 풀 크기**: 적절한 자원 풀 크기를 유지하여 대기 시간을 최소화하세요
- **배치 처리**: 유사한 자원 요구사항을 가진 작업들을 배치로 처리하세요
- **예측 기반 계획**: 과거 데이터를 활용하여 자원 필요량을 예측하세요

### 3. 오류 방지

```python
def validate_resource_requirements(requirements):
    """자원 요구사항 유효성 검사"""
    errors = []
    
    for req in requirements:
        # 수량 검사
        if req.quantity <= 0:
            errors.append(f"잘못된 수량: {req.name} ({req.quantity})")
        
        # 단위 검사
        if not req.unit or req.unit.strip() == "":
            errors.append(f"단위 누락: {req.name}")
        
        # 자원 타입 검사
        if not isinstance(req.resource_type, ResourceType):
            errors.append(f"잘못된 자원 타입: {req.name}")
    
    if errors:
        raise ValueError(f"자원 요구사항 오류: {', '.join(errors)}")
    
    return True

# 모든 프로세스 생성 시 검증 수행
validate_resource_requirements(manufacturing_requirements)
```

## 🔗 관련 문서

- [Resource Management Guide](resource_management_guide.md)
- [API Reference](api_reference.md)
- [Process Chaining Guide](process_chaining.md)
- [예제: Advanced Resource Management](../examples/advanced_resource_example.py)

---

체계적인 자원 정의와 관리는 정확하고 현실적인 시뮬레이션의 기반입니다. 이 가이드의 패턴과 예제를 활용하여 여러분의 제조 시뮬레이션을 더욱 정교하게 만들어보세요!
AssemblyProcess(
    machines,                    # 기계 목록
    workers,                     # 작업자 목록
    input_resources,             # 입력 자원 목록 (필수)
    output_resources,            # 출력 자원 목록 (필수)
    resource_requirements,       # 자원 요구사항 목록 (필수)
    process_id=None,             # 공정 ID (선택적)
    process_name=None            # 공정명 (선택적)
)
```

### QualityControlProcess
```python
QualityControlProcess(
    inspection_criteria,         # 검사 기준
    input_resources,             # 입력 자원 목록 (필수)
    output_resources,            # 출력 자원 목록 (필수)
    resource_requirements,       # 자원 요구사항 목록 (필수)
    process_id=None,             # 공정 ID (선택적)
    process_name=None            # 공정명 (선택적)
)
```

## 완전한 예제

```python
from src.processes import ManufacturingProcess
from src.Resource.helper import Resource, ResourceRequirement, ResourceType

# 입력 자원 정의
input_resources = [
    Resource(
        resource_id="steel_material",
        name="강철 원자재",
        resource_type=ResourceType.RAW_MATERIAL,
        quantity=10.0,
        unit="kg"
    )
]

# 출력 자원 정의
output_resources = [
    Resource(
        resource_id="steel_parts",
        name="강철 부품", 
        resource_type=ResourceType.SEMI_FINISHED,
        quantity=5.0,
        unit="개"
    )
]

# 자원 요구사항 정의
resource_requirements = [
    ResourceRequirement(
        resource_type=ResourceType.WORKER,
        name="숙련공",
        required_quantity=2.0,
        unit="명",
        is_mandatory=True
    )
]

# 공정 생성 - 모든 자원 정보 필수!
manufacturing = ManufacturingProcess(
    machines=["머신1", "머신2"],
    workers=["작업자A"],
    input_resources=input_resources,        # 필수
    output_resources=output_resources,      # 필수
    resource_requirements=resource_requirements  # 필수
)
```

## 빈 자원 리스트

자원이 없는 경우에도 빈 리스트를 명시적으로 제공해야 합니다:

```python
# 자원이 없는 경우 - 빈 리스트로 명시
simple_process = ManufacturingProcess(
    machines=["머신1"],
    workers=["작업자1"],
    input_resources=[],         # 빈 리스트 명시
    output_resources=[],        # 빈 리스트 명시  
    resource_requirements=[]    # 빈 리스트 명시
)
```

## 오류 처리

자원 정보를 제공하지 않으면 `TypeError`가 발생합니다:

```python
# 이렇게 하면 오류 발생!
try:
    manufacturing = ManufacturingProcess(
        machines=["머신1"],
        workers=["작업자1"]
        # 자원 정보 누락 - TypeError 발생
    )
except TypeError as e:
    print(f"오류: {e}")
    # 출력: missing 3 required positional arguments: 
    #       'input_resources', 'output_resources', and 'resource_requirements'
```

## 이점

1. **명확성**: 모든 공정의 입출력이 명확히 정의됨
2. **일관성**: 모든 공정이 동일한 방식으로 자원을 정의
3. **안정성**: 자원 정의 누락으로 인한 런타임 오류 방지
4. **문서화**: 코드 자체가 공정의 자원 요구사항을 문서화
