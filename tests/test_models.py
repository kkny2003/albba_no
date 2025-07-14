import unittest
from src.models.machine import Machine  # 기계 모델 임포트
from src.models.worker import Worker    # 작업자 모델 임포트
from src.models.product import Product    # 제품 모델 임포트
from src.models.transport import Transport  # 운송 모델 임포트

class TestMachine(unittest.TestCase):  # 기계 모델 테스트 클래스
    def setUp(self):
        self.machine = Machine()  # 기계 인스턴스 생성

    def test_machine_operation(self):
        self.machine.start()  # 기계 시작
        self.assertTrue(self.machine.is_running)  # 기계가 작동 중인지 확인
        self.machine.stop()  # 기계 정지
        self.assertFalse(self.machine.is_running)  # 기계가 정지했는지 확인

class TestWorker(unittest.TestCase):  # 작업자 모델 테스트 클래스
    def setUp(self):
        self.worker = Worker()  # 작업자 인스턴스 생성

    def test_worker_productivity(self):
        initial_productivity = self.worker.productivity  # 초기 생산성 저장
        self.worker.work()  # 작업 수행
        self.assertGreater(self.worker.productivity, initial_productivity)  # 생산성이 증가했는지 확인

class TestProduct(unittest.TestCase):  # 제품 모델 테스트 클래스
    def setUp(self):
        self.product = Product(name="Test Product")  # 제품 인스턴스 생성

    def test_product_attributes(self):
        self.assertEqual(self.product.name, "Test Product")  # 제품 이름 확인
        self.assertIsNotNone(self.product.status)  # 제품 상태가 None이 아닌지 확인

class TestTransport(unittest.TestCase):  # 운송 모델 테스트 클래스
    def setUp(self):
        self.transport = Transport()  # 운송 인스턴스 생성

    def test_transport_movement(self):
        self.transport.move()  # 운송 수행
        self.assertTrue(self.transport.is_moving)  # 운송이 진행 중인지 확인

if __name__ == '__main__':
    unittest.main()  # 테스트 실행