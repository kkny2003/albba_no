import unittest
from src.core.simulation_engine import SimulationEngine  # 시뮬레이션 엔진 클래스를 임포트합니다.

class TestSimulationEngine(unittest.TestCase):  # unittest.TestCase를 상속받아 테스트 클래스 정의
    def setUp(self):
        # 각 테스트 전에 실행되는 설정 메서드
        self.engine = SimulationEngine()  # 시뮬레이션 엔진 인스턴스를 생성합니다.

    def test_initialization(self):
        # 시뮬레이션 엔진 초기화 테스트
        self.assertIsNotNone(self.engine)  # 엔진 인스턴스가 None이 아님을 확인합니다.

    def test_run_simulation(self):
        # 시뮬레이션 실행 테스트
        result = self.engine.run_simulation()  # 시뮬레이션을 실행합니다.
        self.assertTrue(result)  # 실행 결과가 True인지 확인합니다.

    def test_collect_data(self):
        # 데이터 수집 테스트
        self.engine.run_simulation()  # 시뮬레이션을 실행합니다.
        data = self.engine.collect_data()  # 데이터를 수집합니다.
        self.assertIsInstance(data, dict)  # 수집된 데이터가 딕셔너리인지 확인합니다.

if __name__ == '__main__':
    unittest.main()  # 테스트를 실행합니다.