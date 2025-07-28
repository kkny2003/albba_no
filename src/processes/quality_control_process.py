from src.processes.base_process import BaseProcess
from typing import Any, List, Generator
import simpy
from src.Resource.resource_base import Resource, ResourceRequirement, ResourceType


class QualityControlProcess(BaseProcess):
    """품질 관리 공정을 정의하는 클래스입니다 (SimPy 기반)."""

    def __init__(self, env: simpy.Environment, inspection_criteria,
                 input_resources: List[Resource], 
                 output_resources: List[Resource],
                 resource_requirements: List[ResourceRequirement],
                 workers=None, machines=None,
                 process_id: str = None, process_name: str = None,
                 inspection_time: float = 1.5,
                 failure_weight_machine: float = 1.0, 
                 failure_weight_worker: float = 1.0):
        """
        품질 관리 공정의 초기화 메서드입니다 (SimPy 환경 필수).
        
        :param env: SimPy 환경 객체 (필수)
        :param inspection_criteria: 품질 검사 기준
        :param workers: 품질 검사를 수행할 작업자 목록 (machine 또는 worker 중 하나는 필수)
        :param machines: 검사 장비 목록 (선택적, machine 또는 worker 중 하나는 필수)
        :param input_resources: 입력 자원 목록 (필수)
        :param output_resources: 출력 자원 목록 (필수)
        :param resource_requirements: 자원 요구사항 목록 (필수)
        :param process_id: 공정 고유 ID (선택적)
        :param process_name: 공정 이름 (선택적)
        :param inspection_time: 검사 처리 시간 (시뮬레이션 시간 단위)
        :param failure_weight_machine: 기계 고장률 가중치 (기본값: 1.0)
        :param failure_weight_worker: 작업자 실수율 가중치 (기본값: 1.0)
        """
        # BaseProcess 초기화 (machines와 workers 전달)
        super().__init__(env, machines, workers, process_id, process_name or "품질관리공정",
                        failure_weight_machine=failure_weight_machine,
                        failure_weight_worker=failure_weight_worker)
        self.inspection_criteria = inspection_criteria  # 품질 검사 기준 저장
        self.inspected_items = []  # 검사된 항목 목록 초기화
        self.inspection_time = inspection_time  # 검사 처리 시간
        
        # 필수 자원 정보 설정
        self._setup_resources(input_resources, output_resources, resource_requirements)
        
    def _setup_resources(self, input_resources: List[Resource], 
                        output_resources: List[Resource],
                        resource_requirements: List[ResourceRequirement]):
        """필수 자원 정보를 설정하는 메서드"""
        # 입력 자원 설정
        for resource in input_resources:
            self.add_input_resource(resource)
        
        # 출력 자원 설정  
        for resource in output_resources:
            self.add_output_resource(resource)
                
        # 자원 요구사항 설정
        for requirement in resource_requirements:
            self.add_resource_requirement(requirement)
        
    def _setup_quality_control_resources(self):
        """품질 관리 공정용 자원 요구사항을 설정하는 메서드"""
        # 검사 장비 자원 추가
        inspection_equipment = Resource(
            resource_id="inspection_equipment_001",
            name="검사장비",
            resource_type=ResourceType.MACHINE,
            quantity=1.0,
            unit="대"
        )
        self.add_input_resource(inspection_equipment)
        
        # 품질 검사원 자원 추가
        quality_inspector = Resource(
            resource_id="quality_inspector_001",
            name="품질검사원",
            resource_type=ResourceType.WORKER,
            quantity=1.0,
            unit="명"
        )
        self.add_input_resource(quality_inspector)
        
        # 완제품 요구사항 추가 (검사 대상)
        finished_product_req = ResourceRequirement(
            resource_type=ResourceType.FINISHED_PRODUCT,
            name="완제품",
            required_quantity=1.0,
            unit="개",
            is_mandatory=True
        )
        self.add_resource_requirement(finished_product_req)
        
        # 검사 도구 요구사항 추가
        tool_req = ResourceRequirement(
            resource_type=ResourceType.TOOL,
            name="검사도구",
            required_quantity=1.0,
            unit="세트",
            is_mandatory=True
        )
        self.add_resource_requirement(tool_req)
        
        # 운송 자원 요구사항 추가 (완제품 운반용)
        transport_req = ResourceRequirement(
            resource_type=ResourceType.TRANSPORT,
            name="운송장비",
            required_quantity=1.0,
            unit="대",
            is_mandatory=False  # 선택적 (수동 운반도 가능)
        )
        self.add_resource_requirement(transport_req)
        
        # 검사도구 자원 추가
        inspection_tool = Resource(
            resource_id="inspection_tool_001",
            name="검사도구",
            resource_type=ResourceType.TOOL,
            quantity=1.0,
            unit="세트"
        )
        self.add_input_resource(inspection_tool)
        
        # 검증된 완제품 출력 자원 설정
        verified_product = Resource(
            resource_id="verified_product_001",
            name="검증완제품",
            resource_type=ResourceType.FINISHED_PRODUCT,
            quantity=1.0,
            unit="개"
        )
        self.add_output_resource(verified_product)

    def inspect(self, item):
        """
        주어진 항목을 검사하는 메서드입니다.
        
        :param item: 검사할 항목
        :return: 검사 결과 (합격/불합격)
        """
        result = self.evaluate_quality(item)  # 품질 평가 수행
        self.inspected_items.append((item, result))  # 검사 결과 저장
        return result  # 검사 결과 반환

    def evaluate_quality(self, item):
        """
        품질을 평가하는 메서드입니다.
        
        :param item: 평가할 항목
        :return: 품질 평가 결과 (합격/불합격)
        """
        # 품질 기준에 따라 평가 수행
        # item이 객체가 아닌 단순 값인 경우를 처리
        if hasattr(item, 'meets_criteria'):
            # item이 meets_criteria 메서드를 가진 객체인 경우
            if item.meets_criteria(self.inspection_criteria):
                return "합격"  # 기준을 충족하면 합격
            else:
                return "불합격"  # 기준을 충족하지 않으면 불합격
        else:
            # item이 단순 값인 경우 기본적으로 합격 처리 (데모용)
            print(f"    제품 '{item}' 품질 검사 완료 - 기본 합격 처리")
            return "합격"

    def get_inspection_report(self):
        """
        검사 보고서를 생성하는 메서드입니다.
        
        :return: 검사 보고서
        """
        report = {}
        for item, result in self.inspected_items:
            # item이 객체인 경우 id 속성을 사용하고, 그렇지 않으면 item 자체를 키로 사용
            item_key = getattr(item, 'id', str(item))
            report[item_key] = result  # 항목 ID와 검사 결과 저장
        return report  # 검사 보고서 반환

    def execute(self, input_data: Any = None) -> Generator[simpy.Event, None, Any]:
        """
        품질 관리 공정을 실행하는 메서드입니다.
        
        Args:
            input_data: 검사할 제품 데이터 (선택적)
            
        Yields:
            simpy.Event: SimPy 이벤트들
            
        Returns:
            Any: 품질 검사 완료된 제품 데이터와 생산된 자원
        """
        print(f"[{self.process_name}] 품질 관리 공정 실행 시작")
        
        # 부모 클래스의 execute 메서드 호출 (자원 관리 포함)
        result = yield from super().execute(input_data)
        return result
        
    def process_logic(self, input_data: Any = None) -> Generator[simpy.Event, None, Any]:
        """
        구체적인 품질 관리 공정 로직을 실행하는 SimPy generator 메서드입니다.
        
        Args:
            input_data: 검사할 제품 데이터
            
        Yields:
            simpy.Event: SimPy 이벤트들
            
        Returns:
            Any: 품질 검사 로직 실행 결과
        """
        print(f"[시간 {self.env.now:.1f}] [{self.process_name}] 품질 검사 로직 실행 중...")
        
        # SimPy timeout을 사용하여 검사 시간 시뮬레이션
        print(f"[시간 {self.env.now:.1f}] [{self.process_name}] 품질 검사 진행 중... (예상 시간: {self.inspection_time})")
        yield self.env.timeout(self.inspection_time)
        
        quality_result = "합격"  # 기본값
        
        if input_data is not None:
            # 품질 검사 수행
            quality_result = self.inspect(input_data)
            print(f"[시간 {self.env.now:.1f}] 품질 검사 결과: {quality_result}")
        else:
            print(f"[시간 {self.env.now:.1f}] 검사할 데이터가 없어 기본 합격 처리")
        
        # 검사 결과에 따른 출력 설정
        inspection_result = {
            'input_data': input_data,
            'quality_result': quality_result,
            'inspection_report': self.get_inspection_report()
        }
        
        print(f"[시간 {self.env.now:.1f}] [{self.process_name}] 품질 검사 로직 실행 완료")
        return inspection_result