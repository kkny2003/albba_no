#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
None 값 지원 기능 단위 테스트

Machine과 Worker 클래스의 None 값 지원 기능을 테스트합니다.
"""

import sys
import os
import unittest
import simpy

# 프로젝트 루트 디렉토리를 Python 경로에 추가
sys.path.append(os.path.join(os.path.dirname(__file__), '..'))

from src.Resource.machine import Machine
from src.Resource.worker import Worker
from src.Resource.product import Product


class TestNoneValueSupport(unittest.TestCase):
    """None 값 지원 기능 테스트 클래스"""
    
    def setUp(self):
        """각 테스트 전에 실행되는 설정"""
        self.env = simpy.Environment()
    
    def test_machine_none_failure_probability(self):
        """기계의 failure_probability가 None일 때 고장이 발생하지 않는지 테스트"""
        machine = Machine(
            env=self.env,
            machine_id="TEST_M001",
            machine_type="테스트기계",
            failure_probability=None  # None으로 설정
        )
        
        # _check_failure 메서드가 항상 False를 반환하는지 확인
        for _ in range(100):  # 여러 번 테스트
            self.assertFalse(machine._check_failure())
    
    def test_machine_zero_failure_probability(self):
        """기계의 failure_probability가 0.0일 때와 None일 때의 차이 테스트"""
        machine_none = Machine(
            env=self.env,
            machine_id="NONE_M001",
            machine_type="None기계",
            failure_probability=None
        )
        
        machine_zero = Machine(
            env=self.env,
            machine_id="ZERO_M001",
            machine_type="Zero기계",
            failure_probability=0.0
        )
        
        # 둘 다 고장이 발생하지 않아야 함
        for _ in range(100):
            self.assertFalse(machine_none._check_failure())
            self.assertFalse(machine_zero._check_failure())
        
        # 하지만 설정값은 다름
        self.assertIsNone(machine_none.failure_probability)
        self.assertEqual(machine_zero.failure_probability, 0.0)
    
    def test_worker_none_error_probability(self):
        """작업자의 error_probability가 None일 때 실수가 발생하지 않는지 테스트"""
        worker = Worker(
            env=self.env,
            worker_id="TEST_W001",
            skills=["테스트"],
            error_probability=None  # None으로 설정
        )
        
        # _check_error 메서드가 항상 False를 반환하는지 확인
        for _ in range(100):  # 여러 번 테스트
            self.assertFalse(worker._check_error())
    
    def test_worker_none_rest_parameters(self):
        """작업자의 휴식 관련 매개변수가 None일 때 휴식이 필요하지 않은지 테스트"""
        worker = Worker(
            env=self.env,
            worker_id="TEST_W001",
            skills=["테스트"],
            mean_time_to_rest=None  # None으로 설정
        )
        
        # _check_rest_needed 메서드가 항상 False를 반환하는지 확인
        for _ in range(100):  # 여러 번 테스트
            self.assertFalse(worker._check_rest_needed())
    
    def test_mixed_none_and_values(self):
        """일부는 None, 일부는 값으로 설정했을 때의 동작 테스트"""
        machine = Machine(
            env=self.env,
            machine_id="MIXED_M001",
            machine_type="혼합기계",
            failure_probability=0.5,      # 높은 확률로 설정
            mean_time_to_failure=None,     # None으로 설정
            mean_time_to_repair=5.0        # 값으로 설정
        )
        
        worker = Worker(
            env=self.env,
            worker_id="MIXED_W001",
            skills=["혼합"],
            error_probability=None,        # None으로 설정
            mean_time_to_rest=10.0,        # 값으로 설정  
            mean_rest_time=None            # None으로 설정
        )
        
        # 설정값 확인
        self.assertEqual(machine.failure_probability, 0.5)
        self.assertIsNone(machine.mean_time_to_failure)
        self.assertEqual(machine.mean_time_to_repair, 5.0)
        
        self.assertIsNone(worker.error_probability)
        self.assertEqual(worker.mean_time_to_rest, 10.0)
        self.assertIsNone(worker.mean_rest_time)
        
        # 동작 확인
        self.assertFalse(worker._check_error())  # error_probability가 None이므로 실수 없음
    
    def test_operation_with_none_values(self):
        """None 값으로 설정된 리소스들이 정상적으로 작업을 수행하는지 테스트"""
        machine = Machine(
            env=self.env,
            machine_id="STABLE_M001",
            machine_type="안정기계",
            processing_time=2.0,
            failure_probability=None,
            mean_time_to_failure=None,
            mean_time_to_repair=None
        )
        
        worker = Worker(
            env=self.env,
            worker_id="STABLE_W001",
            skills=["안정작업"],
            error_probability=None,
            mean_time_to_rest=None,
            mean_rest_time=None
        )
        
        product = Product("TEST_PROD", "테스트제품")
        
        def test_process():
            # 작업자 작업
            yield self.env.process(worker.work(product, "테스트작업", 1.0))
            
            # 기계 작업
            yield self.env.process(machine.operate(product, 2.0))
            
            # 통계 확인
            machine_status = machine.get_status()
            worker_status = worker.get_status()
            
            # 정상적으로 작업이 완료되었는지 확인
            self.assertEqual(machine_status['total_processed'], 1)
            self.assertEqual(worker_status['total_tasks_completed'], 1)
            
            # 고장/실수가 발생하지 않았는지 확인
            self.assertEqual(machine_status['total_failures'], 0)
            self.assertEqual(worker_status['total_errors'], 0)
            
            # 가용성이 100%인지 확인
            self.assertEqual(machine_status['availability'], 1.0)
            self.assertEqual(worker_status['availability'], 1.0)
        
        self.env.process(test_process())
        self.env.run(until=10)
    
    def test_default_values_with_none_repair_time(self):
        """수리/휴식 시간이 None일 때 기본값이 사용되는지 테스트"""
        machine = Machine(
            env=self.env,
            machine_id="DEFAULT_M001",
            machine_type="기본값기계",
            mean_time_to_repair=None  # None으로 설정
        )
        
        worker = Worker(
            env=self.env,
            worker_id="DEFAULT_W001",
            skills=["기본값"],
            mean_rest_time=None  # None으로 설정
        )
        
        def test_default_process():
            # 강제로 수리/휴식 프로세스 실행
            start_time = self.env.now
            
            # 기계 강제 고장 (수리 시간 기본값 사용)
            yield self.env.process(machine.force_failure())
            machine_repair_time = self.env.now - start_time
            
            start_time = self.env.now
            
            # 작업자 강제 휴식 (휴식 시간 기본값 사용)
            yield self.env.process(worker.force_rest())
            worker_rest_time = self.env.now - start_time
            
            # 기본값이 사용되었는지 확인 (정확한 값이 아닌 범위 확인)
            self.assertGreater(machine_repair_time, 0)
            self.assertGreater(worker_rest_time, 0)
        
        self.env.process(test_default_process())
        self.env.run(until=50)


class TestBackwardCompatibility(unittest.TestCase):
    """기존 코드와의 호환성 테스트 클래스"""
    
    def setUp(self):
        """각 테스트 전에 실행되는 설정"""
        self.env = simpy.Environment()
    
    def test_old_style_initialization(self):
        """기존 스타일의 초기화가 여전히 작동하는지 테스트"""
        # 기존 스타일 (위치 매개변수 사용)
        machine = Machine(self.env, "OLD_M001", "기존기계")
        worker = Worker(self.env, "OLD_W001", ["기존기술"])
        
        # 기본값이 None으로 설정되었는지 확인
        self.assertIsNone(machine.failure_probability)
        self.assertIsNone(worker.error_probability)
        
        # 정상적으로 작동하는지 확인
        self.assertEqual(machine.machine_id, "OLD_M001")
        self.assertEqual(worker.worker_id, "OLD_W001")
    
    def test_mixed_old_new_style(self):
        """기존 스타일과 새로운 스타일을 혼합해서 사용할 때 테스트"""
        # 일부는 기존 스타일, 일부는 새로운 스타일
        machine = Machine(
            self.env, "MIXED_M001", "혼합기계",
            capacity=2,  # 기존 매개변수
            failure_probability=0.1  # 새로운 매개변수
        )
        
        worker = Worker(
            self.env, "MIXED_W001", ["혼합기술"],
            work_speed=1.5,  # 기존 매개변수
            error_probability=None  # 새로운 매개변수 (None)
        )
        
        # 설정이 올바르게 적용되었는지 확인
        self.assertEqual(machine.resource.capacity, 2)
        self.assertEqual(machine.failure_probability, 0.1)
        self.assertEqual(worker.work_speed, 1.5)
        self.assertIsNone(worker.error_probability)


if __name__ == '__main__':
    print("🧪 None 값 지원 기능 테스트 시작")
    print("="*50)
    
    # 테스트 실행
    unittest.main(verbosity=2)
