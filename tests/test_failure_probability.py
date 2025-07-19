#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
고장확률 기능 단위 테스트

Machine과 Worker 클래스의 고장확률 관련 기능을 테스트합니다.
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


class TestFailureProbability(unittest.TestCase):
    """고장확률 기능 테스트 클래스"""
    
    def setUp(self):
        """각 테스트 전에 실행되는 설정"""
        self.env = simpy.Environment()
    
    def test_machine_initialization_with_failure_params(self):
        """기계 초기화 시 고장 매개변수가 올바르게 설정되는지 테스트"""
        machine = Machine(
            env=self.env,
            machine_id="TEST_M001",
            machine_type="테스트기계",
            failure_probability=0.1,
            mean_time_to_failure=50.0,
            mean_time_to_repair=8.0
        )
        
        # 고장 관련 속성 확인
        self.assertEqual(machine.failure_probability, 0.1)
        self.assertEqual(machine.mean_time_to_failure, 50.0)
        self.assertEqual(machine.mean_time_to_repair, 8.0)
        self.assertFalse(machine.is_broken)
        self.assertEqual(machine.total_failures, 0)
        self.assertEqual(machine.total_repair_time, 0)
    
    def test_worker_initialization_with_error_params(self):
        """작업자 초기화 시 실수 매개변수가 올바르게 설정되는지 테스트"""
        worker = Worker(
            env=self.env,
            worker_id="TEST_W001",
            skills=["테스트"],
            error_probability=0.05,
            mean_time_to_rest=100.0,
            mean_rest_time=10.0
        )
        
        # 실수 관련 속성 확인
        self.assertEqual(worker.error_probability, 0.05)
        self.assertEqual(worker.mean_time_to_rest, 100.0)
        self.assertEqual(worker.mean_rest_time, 10.0)
        self.assertFalse(worker.is_resting)
        self.assertEqual(worker.total_errors, 0)
        self.assertEqual(worker.total_rest_time, 0)
    
    def test_machine_status_includes_failure_info(self):
        """기계 상태 정보에 고장 관련 정보가 포함되는지 테스트"""
        machine = Machine(
            env=self.env,
            machine_id="TEST_M001",
            machine_type="테스트기계",
            failure_probability=0.1
        )
        
        status = machine.get_status()
        
        # 고장 관련 필드가 상태 정보에 포함되는지 확인
        self.assertIn('is_broken', status)
        self.assertIn('total_failures', status)
        self.assertIn('failure_rate', status)
        self.assertIn('availability', status)
        
        # 초기값 확인
        self.assertFalse(status['is_broken'])
        self.assertEqual(status['total_failures'], 0)
        self.assertEqual(status['failure_rate'], 0.0)
        self.assertEqual(status['availability'], 1.0)
    
    def test_worker_status_includes_error_info(self):
        """작업자 상태 정보에 실수 관련 정보가 포함되는지 테스트"""
        worker = Worker(
            env=self.env,
            worker_id="TEST_W001",
            skills=["테스트"],
            error_probability=0.05
        )
        
        status = worker.get_status()
        
        # 실수 관련 필드가 상태 정보에 포함되는지 확인
        self.assertIn('is_resting', status)
        self.assertIn('total_errors', status)
        self.assertIn('error_rate', status)
        self.assertIn('availability', status)
        
        # 초기값 확인
        self.assertFalse(status['is_resting'])
        self.assertEqual(status['total_errors'], 0)
        self.assertEqual(status['error_rate'], 0.0)
        self.assertEqual(status['availability'], 1.0)
    
    def test_machine_force_failure(self):
        """기계 강제 고장 기능 테스트"""
        machine = Machine(
            env=self.env,
            machine_id="TEST_M001",
            machine_type="테스트기계",
            mean_time_to_repair=1.0  # 빠른 수리를 위해 짧게 설정
        )
        
        def failure_test():
            # 강제 고장 발생
            yield self.env.process(machine.force_failure())
            
            # 고장 후 상태 확인
            status = machine.get_status()
            self.assertEqual(status['total_failures'], 1)
            self.assertFalse(status['is_broken'])  # 수리 완료 후
            self.assertGreater(status['failure_rate'], 0)
            self.assertLess(status['availability'], 1.0)
        
        self.env.process(failure_test())
        self.env.run(until=10)
    
    def test_worker_force_rest(self):
        """작업자 강제 휴식 기능 테스트"""
        worker = Worker(
            env=self.env,
            worker_id="TEST_W001",
            skills=["테스트"],
            mean_rest_time=1.0  # 빠른 휴식을 위해 짧게 설정
        )
        
        def rest_test():
            # 강제 휴식 발생
            yield self.env.process(worker.force_rest())
            
            # 휴식 후 상태 확인
            status = worker.get_status()
            self.assertFalse(status['is_resting'])  # 휴식 완료 후
            self.assertLess(status['availability'], 1.0)
        
        self.env.process(rest_test())
        self.env.run(until=10)
    
    def test_machine_operation_with_zero_failure_probability(self):
        """고장확률이 0인 기계의 정상 작업 테스트"""
        machine = Machine(
            env=self.env,
            machine_id="TEST_M001",
            machine_type="테스트기계",
            processing_time=2.0,
            failure_probability=0.0  # 고장 없음
        )
        
        product = Product("TEST_PROD", "테스트제품")
        
        def operation_test():
            # 제품 처리
            yield self.env.process(machine.operate(product, 2.0))
            
            # 작업 완료 후 상태 확인
            status = machine.get_status()
            self.assertEqual(status['total_processed'], 1)
            self.assertEqual(status['total_failures'], 0)
            self.assertFalse(status['is_broken'])
        
        self.env.process(operation_test())
        self.env.run(until=10)
    
    def test_worker_work_with_zero_error_probability(self):
        """실수확률이 0인 작업자의 정상 작업 테스트"""
        worker = Worker(
            env=self.env,
            worker_id="TEST_W001",
            skills=["테스트"],
            error_probability=0.0  # 실수 없음
        )
        
        product = Product("TEST_PROD", "테스트제품")
        
        def work_test():
            # 작업 수행
            yield self.env.process(worker.work(product, "테스트작업", 2.0))
            
            # 작업 완료 후 상태 확인
            status = worker.get_status()
            self.assertEqual(status['total_tasks_completed'], 1)
            self.assertEqual(status['total_errors'], 0)
            self.assertFalse(status['is_resting'])
        
        self.env.process(work_test())
        self.env.run(until=10)


class TestFailureStatistics(unittest.TestCase):
    """고장 통계 관련 테스트 클래스"""
    
    def setUp(self):
        """각 테스트 전에 실행되는 설정"""
        self.env = simpy.Environment()
    
    def test_machine_failure_rate_calculation(self):
        """기계 고장률 계산 테스트"""
        machine = Machine(
            env=self.env,
            machine_id="TEST_M001",
            machine_type="테스트기계"
        )
        
        # 시간이 0일 때는 고장률이 0
        self.assertEqual(machine.get_failure_rate(), 0.0)
        
        # 시간을 진행시키고 고장 횟수 증가
        machine.total_failures = 2
        self.env.run(until=10)
        
        expected_rate = 2 / 10  # 2번 고장 / 10시간
        self.assertEqual(machine.get_failure_rate(), expected_rate)
    
    def test_machine_availability_calculation(self):
        """기계 가용성 계산 테스트"""
        machine = Machine(
            env=self.env,
            machine_id="TEST_M001",
            machine_type="테스트기계"
        )
        
        # 시간이 0일 때는 가용성이 1.0
        self.assertEqual(machine.get_availability(), 1.0)
        
        # 수리 시간을 설정하고 시간 진행
        machine.total_repair_time = 3
        self.env.run(until=10)
        
        expected_availability = (10 - 3) / 10  # (전체시간 - 수리시간) / 전체시간
        self.assertEqual(machine.get_availability(), expected_availability)
    
    def test_worker_error_rate_calculation(self):
        """작업자 실수율 계산 테스트"""
        worker = Worker(
            env=self.env,
            worker_id="TEST_W001",
            skills=["테스트"]
        )
        
        # 작업을 완료하지 않았을 때는 실수율이 0
        self.assertEqual(worker.get_error_rate(), 0.0)
        
        # 작업 완료 수와 실수 수 설정
        worker.total_tasks_completed = 10
        worker.total_errors = 2
        
        expected_rate = 2 / 10  # 2번 실수 / 10번 작업
        self.assertEqual(worker.get_error_rate(), expected_rate)
    
    def test_worker_availability_calculation(self):
        """작업자 가용성 계산 테스트"""
        worker = Worker(
            env=self.env,
            worker_id="TEST_W001",
            skills=["테스트"]
        )
        
        # 시간이 0일 때는 가용성이 1.0
        self.assertEqual(worker.get_availability(), 1.0)
        
        # 휴식 시간을 설정하고 시간 진행
        worker.total_rest_time = 2
        self.env.run(until=10)
        
        expected_availability = (10 - 2) / 10  # (전체시간 - 휴식시간) / 전체시간
        self.assertEqual(worker.get_availability(), expected_availability)


if __name__ == '__main__':
    print("🧪 고장확률 기능 테스트 시작")
    print("="*50)
    
    # 테스트 실행
    unittest.main(verbosity=2)
