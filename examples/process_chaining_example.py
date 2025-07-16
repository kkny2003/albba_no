"""
프로세스 체이닝 시뮬레이션 예제
프레임워크의 핵심 기능인 프로세스 체이닝 (>> 연산자)을 활용한 시뮬레이션을 보여줍니다.
"""

import simpy
import sys
import os

# 프로젝트 루트 디렉토리를 Python 경로에 추가
sys.path.append(os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), 'src'))

from core.simulation_engine import SimulationEngine
from Resource.machine import Machine
from Resource.worker import Worker
from Resource.product import Product
from Resource.helper import Resource, ResourceRequirement, ResourceType
from processes.manufacturing_process import ManufacturingProcess
from processes.assembly_process import AssemblyProcess
from processes.quality_control_process import QualityControlProcess
from core.resource_manager import ResourceManager
from core.data_collector import DataCollector


def create_process_chain_simulation():
    """프로세스 체이닝을 활용한 제조 시뮬레이션"""
    print("=== 프로세스 체이닝 시뮬레이션 시작 ===")
    
    # 시뮬레이션 엔진 및 자원 관리자 생성
    engine = SimulationEngine(random_seed=123)
    resource_manager = ResourceManager()
    data_collector = DataCollector()
    
    # 자원 정의 및 추가
    setup_resources(resource_manager)
    
    # 프로세스 체인 구성
    process_chain = create_manufacturing_chain()
    
    print("프로세스 체인 구성:")
    print("드릴링 공정 >> 밀링 공정 >> 조립 공정 >> 품질 검사")
    
    def product_flow(env):
        """제품 흐름을 시뮬레이션하는 프로세스"""
        product_count = 0
        
        while True:
            # 새 제품 생성
            product_count += 1
            product = Product(f"PC{product_count:03d}", "체인제품")
            
            print(f"\n시간 {env.now:.1f}: 제품 {product.product_id} 프로세스 체인 시작")
            
            try:
                # 프로세스 체인 실행 (핵심 기능!)
                yield from process_chain.execute(product, env, resource_manager)
                
                # 성공적으로 완료된 제품 수집
                data_collector.collect_data("completed_products", 1, timestamp=env.now)
                print(f"시간 {env.now:.1f}: 제품 {product.product_id} 전체 프로세스 완료")
                
            except Exception as e:
                print(f"시간 {env.now:.1f}: 제품 {product.product_id} 처리 중 오류: {e}")
                data_collector.collect_data("failed_products", 1, timestamp=env.now)
            
            # 다음 제품 도착까지 대기
            yield env.timeout(5.0)  # 5시간 간격
    
    # 프로세스를 시뮬레이션에 추가
    engine.add_process(product_flow)
    
    # 시뮬레이션 실행
    print("\n시뮬레이션 실행 중...")
    engine.run(until=50)
    
    # 결과 분석
    analyze_chain_results(data_collector)
    
    return data_collector


def setup_resources(resource_manager):
    """시뮬레이션에 필요한 자원들을 설정"""
    print("\n자원 설정 중...")
    
    # 원자재
    steel_sheet = Resource("STEEL_001", "철판", ResourceType.RAW_MATERIAL, 100.0, "kg")
    aluminum_rod = Resource("ALU_001", "알루미늄 막대", ResourceType.RAW_MATERIAL, 50.0, "kg")
    
    # 도구들
    drill_bit = Resource("DRILL_001", "드릴 비트", ResourceType.TOOL, 5.0, "개")
    milling_cutter = Resource("MILL_001", "밀링 커터", ResourceType.TOOL, 3.0, "개")
    assembly_tools = Resource("TOOLS_001", "조립 도구", ResourceType.TOOL, 2.0, "세트")
    
    # 반제품
    drilled_part = Resource("SEMI_001", "드릴링 완료 부품", ResourceType.SEMI_FINISHED, 10.0, "개")
    milled_part = Resource("SEMI_002", "밀링 완료 부품", ResourceType.SEMI_FINISHED, 10.0, "개")
    
    # 자원들을 자원 관리자에 추가
    resources = [steel_sheet, aluminum_rod, drill_bit, milling_cutter, 
                assembly_tools, drilled_part, milled_part]
    
    for resource in resources:
        resource_manager.add_resource(resource)
        print(f"  추가된 자원: {resource.name} ({resource.quantity} {resource.unit})")


def create_manufacturing_chain():
    """제조 프로세스 체인을 생성"""
    print("\n프로세스 체인 생성 중...")
    
    # 1. 드릴링 공정 - 우선순위 1
    drilling_requirements = [
        ResourceRequirement(ResourceType.RAW_MATERIAL, "철판", 2.0, "kg", True),
        ResourceRequirement(ResourceType.TOOL, "드릴 비트", 1.0, "개", False)
    ]
    drilling_process = ManufacturingProcess(
        name="드릴링(1)", 
        required_resources=drilling_requirements, 
        processing_time=2.5
    )
    
    # 2. 밀링 공정 - 우선순위 2  
    milling_requirements = [
        ResourceRequirement(ResourceType.SEMI_FINISHED, "드릴링 완료 부품", 1.0, "개", True),
        ResourceRequirement(ResourceType.TOOL, "밀링 커터", 1.0, "개", False)
    ]
    milling_process = ManufacturingProcess(
        name="밀링(2)", 
        required_resources=milling_requirements, 
        processing_time=3.0
    )
    
    # 3. 조립 공정 - 우선순위 3
    assembly_requirements = [
        ResourceRequirement(ResourceType.SEMI_FINISHED, "밀링 완료 부품", 2.0, "개", True),
        ResourceRequirement(ResourceType.TOOL, "조립 도구", 1.0, "세트", False)
    ]
    assembly_process = AssemblyProcess(
        name="조립(3)", 
        required_components=assembly_requirements, 
        assembly_time=4.0
    )
    
    # 4. 품질 검사 공정 - 우선순위 4
    quality_process = QualityControlProcess(
        name="품질검사(4)", 
        pass_rate=0.90, 
        inspection_time=1.5
    )
    
    # 프로세스 체이닝 (>> 연산자 사용)
    print("프로세스 체이닝 적용...")
    complete_chain = drilling_process >> milling_process >> assembly_process >> quality_process
    
    print(f"  체인 구성: {complete_chain.get_process_count()}개 프로세스")
    
    return complete_chain


def analyze_chain_results(data_collector):
    """프로세스 체인 결과 분석"""
    print("\n=== 프로세스 체인 결과 분석 ===")
    
    completed_data = data_collector.get_data("completed_products")
    failed_data = data_collector.get_data("failed_products")
    
    completed_count = len(completed_data['values']) if completed_data['values'] else 0
    failed_count = len(failed_data['values']) if failed_data['values'] else 0
    total_count = completed_count + failed_count
    
    print(f"총 처리 시도한 제품 수: {total_count}개")
    print(f"성공적으로 완료된 제품 수: {completed_count}개")
    print(f"실패한 제품 수: {failed_count}개")
    
    if total_count > 0:
        success_rate = (completed_count / total_count) * 100
        print(f"전체 성공률: {success_rate:.1f}%")
        
        if completed_count > 0:
            # 평균 완료 시간 계산 (각 제품이 완료된 시점 기준)
            avg_completion_time = sum(completed_data['timestamps']) / len(completed_data['timestamps'])
            print(f"평균 완료 시간: {avg_completion_time:.2f}시간")
    
    # 프로세스 체인의 이론적 분석
    print(f"\n이론적 분석:")
    print(f"- 드릴링: 2.5시간")
    print(f"- 밀링: 3.0시간") 
    print(f"- 조립: 4.0시간")
    print(f"- 품질검사: 1.5시간")
    print(f"이론적 총 처리 시간: 11.0시간")
    print(f"품질 통과율 고려: 90%")


def demonstrate_priority_system():
    """우선순위 시스템 시연"""
    print("\n=== 우선순위 시스템 시연 ===")
    
    from processes.base_process import parse_process_priority
    
    # 우선순위가 포함된 프로세스명 파싱 예제
    test_names = ["드릴링(1)", "밀링(2)", "조립(3)", "품질검사(4)", "일반공정"]
    
    for name in test_names:
        actual_name, priority = parse_process_priority(name)
        print(f"입력: '{name}' → 실제명: '{actual_name}', 우선순위: {priority}")


def demonstrate_alternative_chains():
    """다양한 프로세스 체인 구성 방법 시연"""
    print("\n=== 다양한 체인 구성 방법 ===")
    
    # 간단한 체인
    simple_requirements = [
        ResourceRequirement(ResourceType.RAW_MATERIAL, "원자재", 1.0, "kg", True)
    ]
    
    process_a = ManufacturingProcess("공정A", simple_requirements, 1.0)
    process_b = ManufacturingProcess("공정B", simple_requirements, 2.0)
    process_c = ManufacturingProcess("공정C", simple_requirements, 1.5)
    
    # 다양한 체인 구성
    chain1 = process_a >> process_b
    chain2 = process_a >> process_b >> process_c
    
    print(f"체인1 (A >> B): {chain1.get_process_count()}개 프로세스")
    print(f"체인2 (A >> B >> C): {chain2.get_process_count()}개 프로세스")
    
    # 조건부 체인 (예시)
    print("\n조건부 프로세스 체인 가능:")
    print("if 품질검사_통과:")
    print("    포장공정 >> 출하공정")
    print("else:")
    print("    재작업공정 >> 다시_품질검사")


if __name__ == "__main__":
    # 메인 프로세스 체이닝 시뮬레이션 실행
    data_collector = create_process_chain_simulation()
    
    # 우선순위 시스템 시연
    demonstrate_priority_system()
    
    # 다양한 체인 구성 방법 시연
    demonstrate_alternative_chains()
    
    print("\n=== 프로세스 체이닝 시뮬레이션 완료 ===")
    print("이 예제는 프레임워크의 핵심 기능인 프로세스 체이닝을 보여줍니다.")
    print(">> 연산자를 사용하여 복잡한 제조 공정을 간단하게 연결할 수 있습니다.")
