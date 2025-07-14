# /manufacturing-simulation-framework/manufacturing-simulation-framework/examples/simple_factory.py

# 간단한 공장 시뮬레이션 예제
import simpy  # 시뮬레이션을 위한 라이브러리
from src.core.simulation_engine import SimulationEngine  # 시뮬레이션 엔진 임포트
from src.models.machine import Machine  # 기계 모델 임포트
from src.models.worker import Worker  # 작업자 모델 임포트
from src.models.product import Product  # 제품 모델 임포트

# 공장 클래스 정의
class SimpleFactory:
    def __init__(self, env):
        self.env = env  # 시뮬레이션 환경
        self.machine = Machine(env)  # 기계 인스턴스 생성
        self.worker = Worker(env)  # 작업자 인스턴스 생성

    def produce(self):
        while True:
            product = Product()  # 새로운 제품 생성
            yield self.env.process(self.machine.operate(product))  # 기계 작동
            yield self.env.process(self.worker.work(product))  # 작업자 작업

# 메인 함수
def main():
    env = simpy.Environment()  # 시뮬레이션 환경 생성
    factory = SimpleFactory(env)  # 공장 인스턴스 생성
    env.process(factory.produce())  # 생산 프로세스 시작
    env.run(until=10)  # 시뮬레이션 실행 (10 시간 단위)

# 스크립트가 직접 실행될 때 메인 함수 호출
if __name__ == "__main__":
    main()  # 메인 함수 실행