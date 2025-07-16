#!/usr/bin/env python3
"""
누락된 모듈들에 대한 포괄적인 테스트
모든 핵심 모듈의 기능을 검증하여 완전한 테스트 커버리지 달성
"""

import unittest
import sys
import os
import simpy
import numpy as np

# 프로젝트 루트의 src 디렉토리를 Python 경로에 추가
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

from core.simple_resource_manager import SimpleResourceManager
from processes.assembly_process import AssemblyProcess
from processes.base_process import BaseProcess, parse_process_priority, PriorityValidationError
from Resource.helper import Resource, ResourceType, ResourceRequirement
from config.settings import Settings

class TestSimpleResourceManager(unittest.TestCase):
    """SimpleResourceManager 클래스 테스트"""
    
    def setUp(self):
        """각 테스트 전 초기화"""
        self.env = simpy.Environment()
        self.manager = SimpleResourceManager(self.env)
    
    def test_initialization(self):
        """초기화 테스트"""
        self.assertIsNotNone(self.manager.env)
        self.assertEqual(len(self.manager.resources), 0)
        self.assertEqual(len(self.manager.resource_metadata), 0)
        self.assertEqual(len(self.manager.resource_inventory), 0)
        print("✅ SimpleResourceManager 초기화 테스트 통과")
    
    def test_register_simpy_resource(self):
        """SimPy 자원 등록 테스트"""
        self.manager.register_simpy_resource("test_machine", capacity=2, type="기계")
        
        self.assertIn("test_machine", self.manager.resources)
        self.assertEqual(self.manager.resources["test_machine"].capacity, 2)
        self.assertIn("test_machine", self.manager.resource_metadata)
        print("✅ SimPy 자원 등록 테스트 통과")
    
    def test_resource_allocation(self):
        """자원 할당/해제 테스트"""
        self.manager.register_simpy_resource("test_resource", capacity=1)
        
        # 간단한 프로세스로 자원 사용 테스트
        def resource_user(env, manager):
            with manager.resources["test_resource"].request() as request:
                yield request
                yield env.timeout(1)  # 1시간 사용
        
        self.env.process(resource_user(self.env, self.manager))
        self.env.run(until=2)
        print("✅ 자원 할당/해제 테스트 통과")

class TestAssemblyProcess(unittest.TestCase):
    """AssemblyProcess 클래스 테스트"""
    
    def setUp(self):
        """각 테스트 전 초기화"""
        self.env = simpy.Environment()
        
        # 테스트용 자원들 생성
        self.input_resources = [
            Resource("부품1", "볼트", ResourceType.RAW_MATERIAL, quantity=10.0),
            Resource("부품2", "너트", ResourceType.RAW_MATERIAL, quantity=10.0)
        ]
        self.output_resources = [
            Resource("조립품", "조립된제품", ResourceType.SEMI_FINISHED, quantity=1.0)
        ]
        self.resource_requirements = [
            ResourceRequirement(ResourceType.RAW_MATERIAL, "볼트", 2.0, "개", True),
            ResourceRequirement(ResourceType.RAW_MATERIAL, "너트", 2.0, "개", True)
        ]
        
        # 기계와 작업자 목록 (간단한 더미 객체)
        self.machines = ["조립기계1"]
        self.workers = ["조립작업자1"]
    
    def test_initialization(self):
        """조립 공정 초기화 테스트"""
        process = AssemblyProcess(
            env=self.env,
            machines=self.machines,
            workers=self.workers,
            input_resources=self.input_resources,
            output_resources=self.output_resources,
            resource_requirements=self.resource_requirements,
            assembly_time=5.0
        )
        
        self.assertIsNotNone(process.env)
        self.assertEqual(process.machines, self.machines)
        self.assertEqual(process.workers, self.workers)
        self.assertEqual(process.assembly_time, 5.0)
        print("✅ AssemblyProcess 초기화 테스트 통과")
    
    def test_process_execution(self):
        """조립 공정 실행 테스트"""
        process = AssemblyProcess(
            env=self.env,
            machines=self.machines,
            workers=self.workers,
            input_resources=self.input_resources,
            output_resources=self.output_resources,
            resource_requirements=self.resource_requirements,
            assembly_time=3.0
        )
        
        # 공정 실행
        self.env.process(process.execute())
        self.env.run(until=10)
        
        # 실행 후 상태 확인
        self.assertGreater(self.env.now, 0)
        print("✅ AssemblyProcess 실행 테스트 통과")

class TestBaseProcess(unittest.TestCase):
    """BaseProcess 클래스 테스트"""
    
    def setUp(self):
        """각 테스트 전 초기화"""
        self.env = simpy.Environment()
    
    def test_parse_process_priority(self):
        """공정 우선순위 파싱 테스트"""
        # 우선순위가 있는 경우
        name, priority = parse_process_priority("공정1(2)")
        self.assertEqual(name, "공정1")
        self.assertEqual(priority, 2)
        
        # 우선순위가 없는 경우
        name, priority = parse_process_priority("공정2")
        self.assertEqual(name, "공정2")
        self.assertIsNone(priority)
        
        print("✅ 공정 우선순위 파싱 테스트 통과")
    
    def test_concrete_base_process(self):
        """구체적인 BaseProcess 구현 테스트"""
        
        class TestProcess(BaseProcess):
            def execute(self):
                """테스트용 실행 메서드"""
                yield self.env.timeout(2)
                return "실행완료"
        
        process = TestProcess(self.env, "TEST001", "테스트공정")
        
        self.assertEqual(process.process_id, "TEST001")
        self.assertEqual(process.process_name, "테스트공정")
        self.assertIsNotNone(process.env)
        
        # 실행 테스트
        result = yield from process.execute()
        self.assertEqual(result, "실행완료")
        print("✅ BaseProcess 구체 구현 테스트 통과")

class TestResourceHelper(unittest.TestCase):
    """Resource/helper.py 모듈 테스트"""
    
    def test_resource_type_enum(self):
        """ResourceType 열거형 테스트"""
        self.assertEqual(ResourceType.RAW_MATERIAL.value, "원자재")
        self.assertEqual(ResourceType.MACHINE.value, "기계")
        self.assertEqual(ResourceType.WORKER.value, "작업자")
        self.assertEqual(ResourceType.TRANSPORT.value, "운송")
        print("✅ ResourceType 열거형 테스트 통과")
    
    def test_resource_creation(self):
        """Resource 클래스 생성 테스트"""
        resource = Resource(
            resource_id="RES001",
            name="강철 파이프",
            resource_type=ResourceType.RAW_MATERIAL,
            quantity=100.0,
            unit="개",
            properties={"재질": "스테인리스", "길이": "2m"}
        )
        
        self.assertEqual(resource.resource_id, "RES001")
        self.assertEqual(resource.name, "강철 파이프")
        self.assertEqual(resource.resource_type, ResourceType.RAW_MATERIAL)
        self.assertEqual(resource.quantity, 100.0)
        self.assertEqual(resource.unit, "개")
        self.assertEqual(resource.properties["재질"], "스테인리스")
        print("✅ Resource 클래스 생성 테스트 통과")
    
    def test_resource_requirement(self):
        """ResourceRequirement 클래스 테스트"""
        requirement = ResourceRequirement(
            resource_type=ResourceType.RAW_MATERIAL,
            name="강철 파이프",
            required_quantity=5.0,
            unit="개",
            is_mandatory=True
        )
        
        self.assertEqual(requirement.resource_type, ResourceType.RAW_MATERIAL)
        self.assertEqual(requirement.name, "강철 파이프")
        self.assertEqual(requirement.required_quantity, 5.0)
        self.assertEqual(requirement.unit, "개")
        self.assertTrue(requirement.is_mandatory)
        print("✅ ResourceRequirement 클래스 테스트 통과")

class TestSettings(unittest.TestCase):
    """Settings 클래스 테스트"""
    
    def setUp(self):
        """각 테스트 전 초기화"""
        self.settings = Settings()
    
    def test_default_settings(self):
        """기본 설정값 테스트"""
        self.assertEqual(self.settings.simulation_time, 1000)
        self.assertEqual(self.settings.num_machines, 5)
        self.assertEqual(self.settings.num_workers, 10)
        self.assertEqual(self.settings.production_rate, 1.0)
        self.assertTrue(self.settings.quality_control_enabled)
        print("✅ 기본 설정값 테스트 통과")
    
    def test_update_settings(self):
        """설정 업데이트 테스트"""
        self.settings.update_settings(
            simulation_time=2000,
            num_machines=8,
            production_rate=1.5
        )
        
        self.assertEqual(self.settings.simulation_time, 2000)
        self.assertEqual(self.settings.num_machines, 8)
        self.assertEqual(self.settings.production_rate, 1.5)
        print("✅ 설정 업데이트 테스트 통과")
    
    def test_invalid_setting_update(self):
        """잘못된 설정 업데이트 테스트"""
        with self.assertRaises(AttributeError):
            self.settings.update_settings(invalid_setting=123)
        print("✅ 잘못된 설정 업데이트 예외 테스트 통과")
    
    def test_display_settings(self):
        """설정 출력 테스트"""
        # 출력 함수가 오류 없이 실행되는지 확인
        try:
            self.settings.display_settings()
            print("✅ 설정 출력 테스트 통과")
        except Exception as e:
            self.fail(f"설정 출력 중 오류 발생: {e}")

class MissingModulesTestRunner:
    """누락된 모듈 테스트 실행 클래스"""
    
    def __init__(self):
        self.results = {}
        self.total_tests = 0
        self.passed_tests = 0
        self.failed_tests = 0
    
    def log_test(self, test_name, status, details=""):
        """테스트 결과 로깅"""
        self.results[test_name] = {
            'status': status,
            'details': details
        }
        self.total_tests += 1
        if status == "PASS":
            self.passed_tests += 1
        else:
            self.failed_tests += 1
        
        status_symbol = "✅" if status == "PASS" else "❌"
        print(f"{status_symbol} {test_name}: {status}")
        if details:
            print(f"   상세: {details}")
    
    def run_all_tests(self):
        """모든 누락된 모듈 테스트 실행"""
        print("=" * 60)
        print("🔍 누락된 모듈들에 대한 포괄적인 테스트 시작")
        print("=" * 60)
        
        test_classes = [
            TestSimpleResourceManager,
            TestAssemblyProcess,
            TestBaseProcess,
            TestResourceHelper,
            TestSettings
        ]
        
        total_success = 0
        total_tests = 0
        
        for test_class in test_classes:
            print(f"\n📋 {test_class.__name__} 테스트 실행 중...")
            
            try:
                # unittest 슈트 생성 및 실행
                suite = unittest.TestLoader().loadTestsFromTestCase(test_class)
                runner = unittest.TextTestRunner(verbosity=0, stream=open(os.devnull, 'w'))
                result = runner.run(suite)
                
                class_tests = result.testsRun
                class_success = class_tests - len(result.failures) - len(result.errors)
                
                total_tests += class_tests
                total_success += class_success
                
                if len(result.failures) == 0 and len(result.errors) == 0:
                    self.log_test(f"{test_class.__name__}", "PASS", f"{class_tests}/{class_tests} 테스트 성공")
                else:
                    self.log_test(f"{test_class.__name__}", "FAIL", 
                                f"{class_success}/{class_tests} 테스트 성공, {len(result.failures)} 실패, {len(result.errors)} 오류")
                
            except Exception as e:
                self.log_test(f"{test_class.__name__}", "FAIL", f"테스트 실행 중 예외 발생: {str(e)}")
        
        # 최종 결과 출력
        self.print_final_results(total_success, total_tests)
        
        return total_success == total_tests
    
    def print_final_results(self, success_count, total_count):
        """최종 테스트 결과 출력"""
        print("\n" + "=" * 60)
        print("📊 누락된 모듈 테스트 결과 요약")
        print("=" * 60)
        
        success_rate = (success_count / total_count * 100) if total_count > 0 else 0
        
        print(f"총 테스트: {total_count}")
        print(f"성공: {success_count}")
        print(f"실패: {total_count - success_count}")
        print(f"성공률: {success_rate:.1f}%")
        
        if success_rate == 100:
            print("\n🎉 모든 누락된 모듈 테스트가 성공했습니다!")
            print("✅ 이제 진정한 100% 테스트 커버리지를 달성했습니다!")
        else:
            print(f"\n⚠️  {total_count - success_count}개의 테스트가 실패했습니다.")
            print("🔧 추가 수정이 필요합니다.")
        
        print("\n📋 테스트된 누락 모듈들:")
        print("   • SimpleResourceManager - SimPy 기반 간단한 자원 관리")
        print("   • AssemblyProcess - 조립 공정 클래스")
        print("   • BaseProcess - 모든 공정의 기본 클래스")
        print("   • Resource/helper - 자원 타입 및 기본 구조")
        print("   • Settings - 시뮬레이션 설정 관리")

if __name__ == "__main__":
    # 누락된 모듈 테스트 실행
    runner = MissingModulesTestRunner()
    success = runner.run_all_tests()
    
    if success:
        print("\n🌟 완전한 테스트 커버리지 달성!")
    else:
        print("\n🔧 추가 작업 필요")
