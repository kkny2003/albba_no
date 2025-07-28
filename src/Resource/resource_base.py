from typing import Any, Dict, Optional, Set
from enum import Enum
import warnings


class ResourceType(Enum):
    """자원 타입을 정의하는 열거형"""
    RAW_MATERIAL = "원자재"       # 원자재
    SEMI_FINISHED = "반제품"      # 반제품
    FINISHED_PRODUCT = "완제품"   # 완제품
    MACHINE = "기계"              # 기계
    WORKER = "작업자"             # 작업자
    TOOL = "도구"                 # 도구
    TRANSPORT = "운송"            # 운송/운반 (지게차, 컨베이어 벨트, 운반차 등)
    BUFFER = "버퍼"               # 버퍼/중간저장소
    ENERGY = "에너지"             # 에너지
    TIME = "시간"                 # 시간


class Resource:
    """제조 시뮬레이션에서 사용되는 자원을 정의하는 클래스 (개선된 안전 버전)"""
    
    # 보호된 attribute 목록 (properties에서 사용하면 안 되는 이름들)
    _PROTECTED_ATTRIBUTES: Set[str] = {
        'resource_id', 'name', 'resource_type', 'is_available',
        'properties', '_dynamic_attributes', '_sync_enabled'
    }
    
    def __init__(self, 
                 resource_id: str,
                 name: str,
                 resource_type: ResourceType,
                 properties: Optional[Dict[str, Any]] = None,
                 strict_mode: bool = False):
        """
        자원 초기화 (개선된 안전 버전)
        
        Args:
            resource_id: 자원의 고유 ID
            name: 자원 이름
            resource_type: 자원 타입 (ResourceType 열거형)
            properties: 추가 속성들 (선택적)
            strict_mode: 엄격 모드 
                        - True: 충돌 시 예외 발생 (안전한 개발)
                        - False: 충돌 시 자동 접두사 추가 (관대한 모드, 기본값)
            properties에 None, False 자료형(int, str, ...) type을 정의 가능
        """
        # 기본 속성들 먼저 설정
        self.resource_id = resource_id
        self.name = name
        self.resource_type = resource_type
        self.is_available = True
        
        # 내부 관리용 속성들
        self._dynamic_attributes: Set[str] = set()  # 동적으로 추가된 attribute 목록
        self._sync_enabled = True  # 동기화 활성화 여부
        
        # strict_mode에 따라 자동으로 auto_prefix 결정
        auto_prefix = not strict_mode  # strict_mode가 True면 auto_prefix는 False
        
        # properties 검증 및 안전한 설정
        safe_properties = self._validate_and_fix_properties(
            properties or {}, 
            strict_mode=strict_mode, 
            auto_prefix=auto_prefix
        )
        self.properties = safe_properties
        
        # 안전하게 동적 attribute 설정
        self._set_dynamic_attributes(self.properties)
        
    def _validate_and_fix_properties(self, properties: Dict[str, Any], 
                                    strict_mode: bool = False, 
                                    auto_prefix: bool = True) -> Dict[str, Any]:
        """
        properties를 검증하고 안전하게 수정하는 메서드
        
        Args:
            properties: 검증할 properties 딕셔너리
            strict_mode: 엄격 모드 (충돌 시 예외 발생)
            auto_prefix: 자동 접두사 추가
            
        Returns:
            Dict[str, Any]: 검증되고 수정된 properties
        """
        safe_properties = {}
        
        for key, value in properties.items():
            if key in self._PROTECTED_ATTRIBUTES:
                if strict_mode:
                    # strict_mode=True: 예외 발생 (auto_prefix는 자동으로 False)
                    raise ValueError(f"[STRICT MODE] 속성 이름 '{key}'는 기존 클래스 attribute와 충돌합니다. "
                                   f"다른 이름을 사용해주세요. (예: custom_{key}, config_{key} 등)")
                else:
                    # strict_mode=False: 자동 접두사 추가 (auto_prefix는 자동으로 True)
                    new_key = f"prop_{key}"
                    safe_properties[new_key] = value
                    warnings.warn(f"속성 이름 '{key}'가 '{new_key}'로 자동 변경되었습니다. "
                                f"충돌을 피하기 위해 다른 이름 사용을 권장합니다.", 
                                UserWarning)
            else:
                safe_properties[key] = value
                
        return safe_properties
    
    def _set_dynamic_attributes(self, properties: Dict[str, Any]):
        """
        properties를 동적 attribute로 안전하게 설정
        
        Args:
            properties: 설정할 properties 딕셔너리
        """
        for key, value in properties.items():
            setattr(self, key, value)
            self._dynamic_attributes.add(key)
    
    def __setattr__(self, name: str, value: Any):
        """
        attribute 설정 시 자동 동기화 처리
        """
        # 내부 속성이나 초기화 중에는 일반적인 설정
        if (name.startswith('_') or 
            name in self._PROTECTED_ATTRIBUTES or 
            not hasattr(self, '_sync_enabled') or 
            not self._sync_enabled):
            super().__setattr__(name, value)
            return
        
        # 동적 attribute인 경우 properties와 동기화
        if hasattr(self, '_dynamic_attributes') and name in self._dynamic_attributes:
            super().__setattr__(name, value)
            if hasattr(self, 'properties'):
                self.properties[name] = value
        else:
            # 새로운 attribute인 경우
            super().__setattr__(name, value)
            
    def clone(self) -> 'Resource':
        """
        자원을 복제하는 메서드
        
        Returns:
            Resource: 복제된 자원 객체
        """
        cloned_resource = Resource(
            resource_id=self.resource_id,
            name=self.name,
            resource_type=self.resource_type,
            properties=self.properties.copy(),
            strict_mode=False  # 복제 시에는 관대한 모드 사용
        )
        return cloned_resource
        
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
        자원의 속성값을 설정하는 메서드 (개선된 안전 버전)
        
        Args:
            key: 속성 키
            value: 속성값
        """
        # 보호된 attribute명 검사
        if key in self._PROTECTED_ATTRIBUTES:
            warnings.warn(f"'{key}'는 보호된 attribute명입니다. "
                         f"'prop_{key}' 사용을 권장합니다.", UserWarning)
            key = f"prop_{key}"
        
        # properties 딕셔너리와 동적 attribute 모두 업데이트
        self.properties[key] = value
        setattr(self, key, value)
        self._dynamic_attributes.add(key)
    
    def get_all_properties(self) -> Dict[str, Any]:
        """
        모든 동적 속성들을 반환 (읽기 전용)
        
        Returns:
            Dict[str, Any]: 모든 properties의 복사본
        """
        return self.properties.copy()
    
    def get_dynamic_attributes(self) -> Set[str]:
        """
        동적으로 추가된 attribute 목록 반환
        
        Returns:
            Set[str]: 동적 attribute 이름들
        """
        return self._dynamic_attributes.copy()
    
    def remove_property(self, key: str) -> bool:
        """
        속성을 안전하게 제거
        
        Args:
            key: 제거할 속성 키
            
        Returns:
            bool: 제거 성공 여부
        """
        if key in self.properties:
            del self.properties[key]
            if hasattr(self, key):
                delattr(self, key)
            self._dynamic_attributes.discard(key)
            return True
        return False
        
    def __str__(self) -> str:
        return f"{self.name}"
        
    def __repr__(self) -> str:
        return f"Resource(id='{self.resource_id}', name='{self.name}', type={self.resource_type.value})"


class ResourceRequirement:
    """자원 요구사항을 정의하는 클래스"""
    
    def __init__(self,
                 resource_type: ResourceType,
                 name: str,
                 required_quantity: int,
                 unit: str = "개",
                 is_mandatory: bool = True):
        """
        자원 요구사항 초기화
        
        Args:
            resource_type: 필요한 자원 타입
            name: 자원 이름
            required_quantity: 필요한 수량
            unit: 단위 (기본값: "개")
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
                resource.is_available)
                
    def __str__(self) -> str:
        return f"{self.name}: {self.required_quantity}{self.unit}"
        
    def __repr__(self) -> str:
        return f"ResourceRequirement(type={self.resource_type.value}, name='{self.name}', qty={self.required_quantity}, unit='{self.unit}', mandatory={self.is_mandatory})"
