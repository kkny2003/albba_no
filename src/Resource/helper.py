from typing import Any, Dict, Optional
from enum import Enum


class ResourceType(Enum):
    """자원 타입을 정의하는 열거형"""
    RAW_MATERIAL = "원자재"       # 원자재
    SEMI_FINISHED = "반제품"      # 반제품
    FINISHED_PRODUCT = "완제품"   # 완제품
    MACHINE = "기계"              # 기계
    WORKER = "작업자"             # 작업자
    TOOL = "도구"                 # 도구
    TRANSPORT = "운송"            # 운송/운반 (지게차, 컨베이어 벨트, 운반차 등)
    ENERGY = "에너지"             # 에너지
    TIME = "시간"                 # 시간


class Resource:
    """제조 시뮬레이션에서 사용되는 자원을 정의하는 클래스"""
    
    def __init__(self, 
                 resource_id: str,
                 name: str,
                 resource_type: ResourceType,
                 quantity: float = 1.0,
                 unit: str = "개",
                 properties: Optional[Dict[str, Any]] = None):
        """
        자원 초기화
        
        Args:
            resource_id: 자원의 고유 ID
            name: 자원 이름
            resource_type: 자원 타입 (ResourceType 열거형)
            quantity: 자원 수량 (기본값: 1.0)
            unit: 자원 단위 (기본값: "개")
            properties: 추가 속성들 (선택적)
        """
        self.resource_id = resource_id
        self.name = name
        self.resource_type = resource_type
        self.quantity = quantity
        self.unit = unit
        self.properties = properties or {}
        self.is_available = True  # 자원 사용 가능 여부
        
    def clone(self, new_quantity: Optional[float] = None) -> 'Resource':
        """
        자원을 복제하는 메서드 (수량 변경 가능)
        
        Args:
            new_quantity: 새로운 수량 (선택적)
            
        Returns:
            Resource: 복제된 자원 객체
        """
        quantity = new_quantity if new_quantity is not None else self.quantity
        return Resource(
            resource_id=self.resource_id,
            name=self.name,
            resource_type=self.resource_type,
            quantity=quantity,
            unit=self.unit,
            properties=self.properties.copy()
        )
        
    def consume(self, amount: float) -> bool:
        """
        자원을 소비하는 메서드
        
        Args:
            amount: 소비할 양
            
        Returns:
            bool: 소비 성공 여부
        """
        if self.quantity >= amount and self.is_available:
            self.quantity -= amount
            return True
        return False
        
    def produce(self, amount: float):
        """
        자원을 생산(추가)하는 메서드
        
        Args:
            amount: 생산할 양
        """
        self.quantity += amount
        
    def is_sufficient(self, required_amount: float) -> bool:
        """
        필요한 양만큼 자원이 충분한지 확인
        
        Args:
            required_amount: 필요한 양
            
        Returns:
            bool: 충분한지 여부
        """
        return self.quantity >= required_amount and self.is_available
        
    def get_property(self, key: str, default: Any = None) -> Any:
        """
        자원의 속성값을 가져오는 메서드
        
        Args:
            key: 속성 키
            default: 기본값
            
        Returns:
            Any: 속성값
        """
        return self.properties.get(key, default)
        
    def set_property(self, key: str, value: Any):
        """
        자원의 속성값을 설정하는 메서드
        
        Args:
            key: 속성 키
            value: 속성값
        """
        self.properties[key] = value
        
    def __str__(self) -> str:
        return f"{self.name}({self.quantity}{self.unit})"
        
    def __repr__(self) -> str:
        return f"Resource(id='{self.resource_id}', name='{self.name}', type={self.resource_type.value}, quantity={self.quantity})"


class ResourceRequirement:
    """자원 요구사항을 정의하는 클래스"""
    
    def __init__(self,
                 resource_type: ResourceType,
                 name: str,
                 required_quantity: float,
                 unit: str = "개",
                 is_mandatory: bool = True):
        """
        자원 요구사항 초기화
        
        Args:
            resource_type: 필요한 자원 타입
            name: 자원 이름
            required_quantity: 필요한 수량
            unit: 단위
            is_mandatory: 필수 여부 (기본값: True)
        """
        self.resource_type = resource_type
        self.name = name
        self.required_quantity = required_quantity
        self.unit = unit
        self.is_mandatory = is_mandatory
        
    def is_satisfied_by(self, resource: Resource) -> bool:
        """
        주어진 자원이 요구사항을 만족하는지 확인
        
        Args:
            resource: 확인할 자원
            
        Returns:
            bool: 요구사항 만족 여부
        """
        return (resource.resource_type == self.resource_type and
                resource.name == self.name and
                resource.is_sufficient(self.required_quantity))
                
    def __str__(self) -> str:
        mandatory_str = "필수" if self.is_mandatory else "선택"
        return f"[{mandatory_str}] {self.name}: {self.required_quantity}{self.unit}"
        
    def __repr__(self) -> str:
        return f"ResourceRequirement(type={self.resource_type.value}, name='{self.name}', qty={self.required_quantity}, mandatory={self.is_mandatory})"


def create_transport_resource(transport_id: str, 
                            transport_name: str,
                            capacity: float,
                            transport_type: str = "지게차") -> Resource:
    """
    운송 자원을 생성하는 헬퍼 함수
    
    Args:
        transport_id: 운송 수단의 고유 ID
        transport_name: 운송 수단 이름
        capacity: 운송 용량
        transport_type: 운송 수단 타입 (지게차, 컨베이어벨트, 운반차 등)
        
    Returns:
        Resource: 운송 자원 객체
    """
    transport_resource = Resource(
        resource_id=transport_id,
        name=transport_name,
        resource_type=ResourceType.TRANSPORT,
        quantity=1.0,  # 운송 수단 자체는 1개
        unit="대"
    )
    
    # 운송 관련 속성들 설정
    transport_resource.set_property("capacity", capacity)
    transport_resource.set_property("current_load", 0.0)
    transport_resource.set_property("transport_type", transport_type)
    transport_resource.set_property("is_moving", False)
    transport_resource.set_property("speed", 1.0)  # 이동 속도 (단위: m/s 또는 적절한 단위)
    
    return transport_resource


def create_product_resource(product_id: str,
                          product_name: str,
                          product_type: ResourceType,
                          quantity: float,
                          sku: str = None,
                          unit: str = "개") -> Resource:
    """
    제품 자원을 생성하는 헬퍼 함수
    
    Args:
        product_id: 제품의 고유 ID
        product_name: 제품 이름
        product_type: 제품 타입 (RAW_MATERIAL, SEMI_FINISHED, FINISHED_PRODUCT)
        quantity: 제품 수량
        sku: 제품 SKU (재고 관리 단위)
        unit: 제품 단위
        
    Returns:
        Resource: 제품 자원 객체
    """
    product_resource = Resource(
        resource_id=product_id,
        name=product_name,
        resource_type=product_type,
        quantity=quantity,
        unit=unit
    )
    
    # 제품 관련 속성들 설정
    if sku:
        product_resource.set_property("sku", sku)
    product_resource.set_property("product_type", product_type.value)
    product_resource.set_property("creation_date", "2025-07-15")  # 생성일
    
    return product_resource


def create_worker_resource(worker_id: str,
                         worker_name: str,
                         skill_level: str = "중급",
                         department: str = "제조부") -> Resource:
    """
    작업자 자원을 생성하는 헬퍼 함수
    
    Args:
        worker_id: 작업자의 고유 ID
        worker_name: 작업자 이름
        skill_level: 기술 수준 (초급, 중급, 고급)
        department: 소속 부서
        
    Returns:
        Resource: 작업자 자원 객체
    """
    worker_resource = Resource(
        resource_id=worker_id,
        name=worker_name,
        resource_type=ResourceType.WORKER,
        quantity=1.0,  # 작업자는 1명
        unit="명"
    )
    
    # 작업자 관련 속성들 설정
    worker_resource.set_property("skill_level", skill_level)
    worker_resource.set_property("department", department)
    worker_resource.set_property("current_task", None)
    worker_resource.set_property("is_working", False)
    worker_resource.set_property("work_hours", 8.0)  # 일일 근무시간
    
    return worker_resource


def create_machine_resource(machine_id: str,
                          machine_name: str,
                          machine_type: str = "제조기계",
                          capacity: float = 1.0) -> Resource:
    """
    기계 자원을 생성하는 헬퍼 함수
    
    Args:
        machine_id: 기계의 고유 ID
        machine_name: 기계 이름
        machine_type: 기계 유형 (제조기계, 조립기계, 검사장비 등)
        capacity: 기계 처리 용량
        
    Returns:
        Resource: 기계 자원 객체
    """
    machine_resource = Resource(
        resource_id=machine_id,
        name=machine_name,
        resource_type=ResourceType.MACHINE,
        quantity=1.0,  # 기계는 1대
        unit="대"
    )
    
    # 기계 관련 속성들 설정
    machine_resource.set_property("machine_type", machine_type)
    machine_resource.set_property("capacity", capacity)
    machine_resource.set_property("status", "idle")  # 기계 상태 (idle, running, maintenance)
    machine_resource.set_property("efficiency", 1.0)  # 효율성 (0.0 ~ 1.0)
    machine_resource.set_property("maintenance_hours", 0)  # 유지보수 시간
    
    return machine_resource
