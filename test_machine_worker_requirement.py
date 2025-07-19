"""
machine 또는 worker가 필수로 들어가는지 테스트하는 파일입니다.
"""

import simpy
from src.Resource.machine import Machine
from src.Resource.worker import Worker
from src.Resource.helper import Resource, ResourceRequirement, ResourceType
from src.processes.manufacturing_process import ManufacturingProcess
from src.processes.assembly_process import AssemblyProcess
from src.processes.quality_control_process import QualityControlProcess

def test_process_with_machine_only():
    """기계만 있는 공정 테스트"""
    print("=== 기계만 있는 공정 테스트 ===")
    
    # SimPy 환경 생성
    env = simpy.Environment()
    
    # 기계 생성
    machine1 = Machine(env, "M001", "CNC_MACHINE", capacity=1, processing_time=2.0)
    
    # 자원 정의
    input_res = [Resource("input_1", "원자재1", ResourceType.RAW_MATERIAL, 10.0, "kg")]
    output_res = [Resource("output_1", "반제품1", ResourceType.SEMI_FINISHED, 5.0, "개")]
    requirements = [ResourceRequirement(ResourceType.RAW_MATERIAL, "원자재", 1.0, "kg", True)]
    
    try:
        # 제조 공정 생성 (기계만 사용)
        process = ManufacturingProcess(
            env=env,
            machines=[machine1],
            workers=None,  # 작업자 없음
            input_resources=input_res,
            output_resources=output_res,
            resource_requirements=requirements,
            process_name="기계전용공정"
        )
        print(f"✅ 성공: {process.process_name} 생성됨")
        return True
        
    except Exception as e:
        print(f"❌ 실패: {e}")
        return False

def test_process_with_worker_only():
    """작업자만 있는 공정 테스트"""
    print("\n=== 작업자만 있는 공정 테스트 ===")
    
    # SimPy 환경 생성
    env = simpy.Environment()
    
    # 작업자 생성
    worker1 = Worker(env, "W001", ["조립", "검사"], work_speed=1.2)
    
    # 자원 정의
    input_res = [Resource("input_2", "부품1", ResourceType.SEMI_FINISHED, 5.0, "개")]
    output_res = [Resource("output_2", "완성품1", ResourceType.FINISHED_PRODUCT, 1.0, "개")]
    requirements = [ResourceRequirement(ResourceType.SEMI_FINISHED, "부품", 2.0, "개", True)]
    
    try:
        # 조립 공정 생성 (작업자만 사용)
        process = AssemblyProcess(
            env=env,
            machines=None,  # 기계 없음
            workers=[worker1],
            input_resources=input_res,
            output_resources=output_res,
            resource_requirements=requirements,
            process_name="수작업조립공정"
        )
        print(f"✅ 성공: {process.process_name} 생성됨")
        return True
        
    except Exception as e:
        print(f"❌ 실패: {e}")
        return False

def test_process_with_both():
    """기계와 작업자가 모두 있는 공정 테스트"""
    print("\n=== 기계와 작업자가 모두 있는 공정 테스트 ===")
    
    # SimPy 환경 생성
    env = simpy.Environment()
    
    # 기계와 작업자 생성
    machine1 = Machine(env, "M002", "TEST_MACHINE", capacity=1, processing_time=1.5)
    worker1 = Worker(env, "W002", ["품질검사"], work_speed=1.0)
    
    # 자원 정의
    input_res = [Resource("input_3", "검사대상", ResourceType.SEMI_FINISHED, 1.0, "개")]
    output_res = [Resource("output_3", "검사완료품", ResourceType.FINISHED_PRODUCT, 1.0, "개")]
    requirements = [ResourceRequirement(ResourceType.SEMI_FINISHED, "검사대상품", 1.0, "개", True)]
    
    try:
        # 품질관리 공정 생성 (기계와 작업자 모두 사용)
        process = QualityControlProcess(
            env=env,
            inspection_criteria={"tolerance": 0.01},
            input_resources=input_res,
            output_resources=output_res,
            resource_requirements=requirements,
            workers=[worker1],
            machines=[machine1],
            process_name="자동화품질검사공정"
        )
        print(f"✅ 성공: {process.process_name} 생성됨")
        return True
        
    except Exception as e:
        print(f"❌ 실패: {e}")
        return False

def test_process_with_neither():
    """기계도 작업자도 없는 공정 테스트 (실패해야 함)"""
    print("\n=== 기계도 작업자도 없는 공정 테스트 (실패해야 함) ===")
    
    # SimPy 환경 생성
    env = simpy.Environment()
    
    # 자원 정의
    input_res = [Resource("input_4", "무엇인가", ResourceType.RAW_MATERIAL, 1.0, "개")]
    output_res = [Resource("output_4", "결과물", ResourceType.FINISHED_PRODUCT, 1.0, "개")]
    requirements = [ResourceRequirement(ResourceType.RAW_MATERIAL, "재료", 1.0, "개", True)]
    
    try:
        # 제조 공정 생성 (기계도 작업자도 없음)
        process = ManufacturingProcess(
            env=env,
            machines=None,  # 기계 없음
            workers=None,   # 작업자 없음
            input_resources=input_res,
            output_resources=output_res,
            resource_requirements=requirements,
            process_name="불가능한공정"
        )
        print(f"❌ 예상과 다름: {process.process_name} 생성됨 (실패해야 했음)")
        return False
        
    except ValueError as e:
        print(f"✅ 예상대로 실패: {e}")
        return True
    except Exception as e:
        print(f"❌ 예상과 다른 오류: {e}")
        return False

def main():
    """테스트 실행"""
    print("machine/worker 필수 요구사항 테스트 시작\n")
    
    results = []
    
    # 각 테스트 실행
    results.append(("기계만 있는 공정", test_process_with_machine_only()))
    results.append(("작업자만 있는 공정", test_process_with_worker_only()))
    results.append(("기계+작업자 공정", test_process_with_both()))
    results.append(("기계도 작업자도 없는 공정", test_process_with_neither()))
    
    # 결과 요약
    print(f"\n{'='*50}")
    print("테스트 결과 요약")
    print(f"{'='*50}")
    
    passed = 0
    for test_name, result in results:
        status = "PASS" if result else "FAIL"
        print(f"{test_name}: {status}")
        if result:
            passed += 1
    
    print(f"\n총 {len(results)}개 테스트 중 {passed}개 통과")
    
    if passed == len(results):
        print("🎉 모든 테스트가 통과했습니다!")
    else:
        print("⚠️  일부 테스트가 실패했습니다.")

if __name__ == "__main__":
    main()
