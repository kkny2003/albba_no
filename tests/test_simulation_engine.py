import unittest
import sys
import os

# 프로젝트 루트의 src 디렉토리를 Python 경로에 추가
sys.path.insert(0, os.path.join(os.path.dirname(os.path.dirname(__file__)), 'src'))

from core.simulation_engine import SimulationEngine  # 시뮬레이션 엔진 클래스를 임포트합니다.

class TestSimulationEngine(unittest.TestCase):  # unittest.TestCase를 상속받아 테스트 클래스 정의
    def setUp(self):
        # 각 테스트 전에 실행되는 설정 메서드
        self.engine = SimulationEngine()  # 시뮬레이션 엔진 인스턴스를 생성합니다.

    def test_initialization(self):
        # 시뮬레이션 엔진 초기화 테스트
        self.assertIsNotNone(self.engine)  # 엔진 인스턴스가 None이 아님을 확인합니다.
        self.assertIsNotNone(self.engine.env)  # SimPy 환경이 생성되었는지 확인합니다.

    def test_run_simulation(self):
        # 시뮬레이션 실행 테스트
        # 간단한 프로세스를 추가해서 테스트
        def simple_process(env):
            yield env.timeout(1)
            
        self.engine.add_process(simple_process)
        self.engine.run(until=10)  # 10초까지 실행
        self.assertGreaterEqual(self.engine.get_current_time(), 1)  # 최소 1초는 진행되었는지 확인

    def test_get_statistics(self):
        # 통계 수집 테스트
        stats = self.engine.get_statistics()  # 통계를 수집합니다.
        self.assertIsInstance(stats, dict)  # 수집된 통계가 딕셔너리인지 확인합니다.
        self.assertIn('simulation_time', stats)  # 시뮬레이션 시간이 포함되어 있는지 확인
        self.assertIn('total_processes', stats)  # 프로세스 수가 포함되어 있는지 확인

if __name__ == '__main__':
    unittest.main()  # 테스트를 실행합니다.