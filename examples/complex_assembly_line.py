# 복잡한 조립 라인 시뮬레이션 예제 코드

# 필요한 라이브러리 임포트
import simpy
from src.Resource.machine import Machine  # 기계 모델 임포트
from src.Resource.worker import Worker    # 작업자 모델 임포트
from src.Resource.product import Product    # 제품 모델 임포트
from src.processes.assembly_process import AssemblyProcess  # 조립 공정 임포트

# 시뮬레이션 환경 설정
def complex_assembly_line_simulation():
    # 시뮬레이션 환경 생성
    env = simpy.Environment()

    # 기계와 작업자 생성
    machine1 = Machine(env, 'Machine 1')
    machine2 = Machine(env, 'Machine 2')
    worker1 = Worker(env, 'Worker 1')
    worker2 = Worker(env, 'Worker 2')

    # 제품 생성
    product1 = Product('Product 1')
    product2 = Product('Product 2')

    # 조립 공정 생성
    assembly_process = AssemblyProcess(env, [machine1, machine2], [worker1, worker2])

    # 조립 공정 시작
    env.process(assembly_process.assemble(product1))
    env.process(assembly_process.assemble(product2))

    # 시뮬레이션 실행
    env.run()

# 메인 함수
if __name__ == '__main__':
    complex_assembly_line_simulation()  # 시뮬레이션 실행