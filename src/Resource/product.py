from typing import Optional, Dict, Any
from datetime import datetime
from src.Resource.resource_base import Resource, ResourceType


class Product(Resource):
    """SimPy 시뮬레이션을 위한 제품 모델을 정의하는 클래스입니다."""

    def __init__(self, resource_id: str, name: str, product_type: str = "기본제품", 
                 specifications: Optional[Dict[str, Any]] = None,
                 resource_type: ResourceType = ResourceType.SEMI_FINISHED):
        """제품을 초기화합니다.
        
        Args:
            resource_id (str): 제품의 고유 ID
            name (str): 제품의 이름
            product_type (str): 제품 유형 (기본값: "기본제품")
            specifications (Optional[Dict[str, Any]]): 제품 사양 정보
            resource_type (ResourceType): 제품의 자원 타입 (원자재/반제품/완제품)
        """
        # Resource 기본 클래스 초기화
        super().__init__(
            resource_id=resource_id,
            name=name,
            resource_type=resource_type
        )
        
        # 제품별 특성을 직접 어트리뷰트로 설정
        self.product_type = product_type
        self.specifications = specifications or {}
        self.creation_time = None
        self.completion_time = None
        self.lead_time = None
        self.current_process_step = "대기중"
        self.quality_status = "미검사"
        self.defect_count = 0
        self.process_history = []
        self.total_processing_time = 0.0
        self.total_waiting_time = 0.0
        
    def start_process_step(self, step_name: str, start_time: float):
        """새로운 공정 단계를 시작합니다.
        
        Args:
            step_name (str): 공정 단계 이름
            start_time (float): 시작 시간
        """
        self.current_process_step = step_name
        
        # 이전 단계가 있다면 완료 처리
        if self.process_history:
            last_step = self.process_history[-1]
            if 'end_time' not in last_step:
                last_step['end_time'] = start_time
                last_step['duration'] = start_time - last_step['start_time']
                self.total_processing_time += last_step['duration']
        
        # 새 단계 기록
        self.process_history.append({
            'step_name': step_name,
            'start_time': start_time,
            'end_time': None,
            'duration': None
        })
        
    def complete_process_step(self, end_time: float):
        """현재 공정 단계를 완료합니다.
        
        Args:
            end_time (float): 완료 시간
        """
        if self.process_history:
            current_step = self.process_history[-1]
            current_step['end_time'] = end_time
            current_step['duration'] = end_time - current_step['start_time']
            self.total_processing_time += current_step['duration']
        
    def set_quality_status(self, status: str, defects: int = 0):
        """품질 검사 결과를 설정합니다.
        
        Args:
            status (str): 품질 상태 ("양호", "불량", "재작업필요" 등)
            defects (int): 발견된 결함 수
        """
        self.quality_status = status
        self.defect_count = defects
        
    def add_specification(self, key: str, value: Any):
        """제품 사양을 추가합니다.
        
        Args:
            key (str): 사양 키
            value (Any): 사양 값
        """
        self.specifications[key] = value
        
    def get_specification(self, key: str, default: Any = None) -> Any:
        """제품 사양을 가져옵니다.
        
        Args:
            key (str): 사양 키
            default (Any): 기본값
            
        Returns:
            Any: 사양 값
        """
        return self.specifications.get(key, default)
        
    def calculate_lead_time(self) -> Optional[float]:
        """리드타임을 계산합니다.
        
        Returns:
            Optional[float]: 리드타임 (완료되지 않은 경우 None)
        """
        if self.creation_time is not None and self.completion_time is not None:
            self.lead_time = self.completion_time - self.creation_time
            return self.lead_time
        return None
        
    def get_processing_efficiency(self) -> float:
        """처리 효율성을 계산합니다 (처리시간 / 총 시간).
        
        Returns:
            float: 처리 효율성 (0.0 ~ 1.0)
        """
        if self.lead_time and self.lead_time > 0:
            return self.total_processing_time / self.lead_time
        return 0.0
        
    def get_status_summary(self) -> Dict[str, Any]:
        """제품의 현재 상태 요약을 반환합니다.
        
        Returns:
            Dict[str, Any]: 상태 요약 정보
        """
        return {
            'resource_id': self.resource_id,
            'product_type': self.product_type,
            'current_step': self.current_process_step,
            'quality_status': self.quality_status,
            'defect_count': self.defect_count,
            'total_steps_completed': len(self.process_history),
            'total_processing_time': self.total_processing_time,
            'lead_time': self.lead_time,
            'processing_efficiency': self.get_processing_efficiency(),
            'is_completed': self.completion_time is not None
        }

    def __str__(self):
        """제품 정보를 문자열로 반환합니다."""
        status = self.get_status_summary()
        return (f"제품[{self.resource_id}] 유형:{self.product_type} "
                f"단계:{self.current_process_step} 품질:{self.quality_status} "
                f"완료:{status['is_completed']}")
                
    def __repr__(self):
        """제품의 상세 정보를 반환합니다."""
        return (f"Product(id='{self.resource_id}', type='{self.product_type}', "
                f"step='{self.current_process_step}', quality='{self.quality_status}')")


