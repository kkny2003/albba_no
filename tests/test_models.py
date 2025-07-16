import unittest
import sys
import os
import simpy

# 프로젝트 루트의 src 디렉토리를 Python 경로에 추가
sys.path.insert(0, os.path.join(os.path.dirname(os.path.dirname(__file__)), 'src'))

from Resource.machine import Machine  # 기계 모델 임포트
from Resource.worker import Worker    # 작업자 모델 임포트
from Resource.product import Product    # 제품 모델 임포트
from Resource.transport import Transport  # 운송 모델 임포트

class TestMachine(unittest.TestCase):  # 기계 모델 테스트 클래스
    def setUp(self):
        self.env = simpy.Environment()  # SimPy 환경 생성
        self.machine = Machine(self.env, "M1", "CNC", capacity=1)  # 기계 인스턴스 생성

    def test_machine_operation(self):
        # 기계 리소스가 정상적으로 생성되었는지 테스트
        self.assertIsNotNone(self.machine.resource)  # 기계 리소스가 존재하는지 확인
        self.assertEqual(self.machine.machine_id, "M1")  # 기계 ID 확인
        self.assertEqual(self.machine.machine_type, "CNC")  # 기계 타입 확인

class TestWorker(unittest.TestCase):  # 작업자 모델 테스트 클래스
    def setUp(self):
        self.env = simpy.Environment()  # SimPy 환경 생성
        self.worker = Worker(self.env, "W1", skills=["assembly", "welding"])  # 작업자 인스턴스 생성

    def test_worker_attributes(self):
        self.assertEqual(self.worker.worker_id, "W1")  # 작업자 ID 확인
        self.assertIn("assembly", self.worker.skills)  # 기술 확인
        self.assertIn("welding", self.worker.skills)  # 기술 확인

class TestProduct(unittest.TestCase):  # 제품 모델 테스트 클래스
    def setUp(self):
        self.product = Product("P1", "Widget")  # 제품 인스턴스 생성

    def test_product_attributes(self):
        self.assertEqual(self.product.product_id, "P1")  # 제품 ID 확인
        self.assertEqual(self.product.product_type, "Widget")  # 제품 타입 확인

class TestTransport(unittest.TestCase):  # 운송 모델 테스트 클래스
    def setUp(self):
        self.env = simpy.Environment()  # SimPy 환경 생성
        self.transport = Transport(self.env, "T1", "conveyor")  # 운송 인스턴스 생성

    def test_transport_attributes(self):
        self.assertEqual(self.transport.transport_id, "T1")  # 운송 ID 확인
        self.assertIsNotNone(self.transport.resource)  # 운송 리소스가 존재하는지 확인

if __name__ == '__main__':
    unittest.main()  # 테스트 실행