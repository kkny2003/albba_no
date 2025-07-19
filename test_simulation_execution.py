"""
machine과 worker 검증이 포함된 실제 시뮬레이션 실행 테스트입니다.
"""

import simpy
from src.Resource.machine import Machine
from src.Resource.worker import Worker
from src.Resource.helper import Resource, ResourceRequirement, ResourceType
from src.Resource.product import Product

# 간단한 제조 공정 클래스를 만들어서 테스트
class SimpleManufacturingProcess:
    """간단한 제조 공정 구현 (테스트용)"""
    
    def __init__(self, env, machines, workers, process_name="간단제조공정"):
        # machine 또는 worker 중 하나는 필수로 있어야 함
        if machines is None and workers is None:
            raise ValueError(f"공정 '{process_name}'에는 machine 또는 worker 중 하나 이상이 필요합니다.")
        
        self.env = env
        self.process_name = process_name
        self.machines = machines or []
        self.workers = workers or []
        
        # 초기화 메시지 출력
        resource_info = []
        if self.machines:
            machine_ids = [getattr(m, 'machine_id', str(m)) for m in self.machines]
            resource_info.append(f"기계: {', '.join(machine_ids)}")
        if self.workers:
            worker_ids = [getattr(w, 'worker_id', str(w)) for w in self.workers]
            resource_info.append(f"작업자: {', '.join(worker_ids)}")
        
        print(f"[{self.process_name}] 공정 초기화 완료 - {' / '.join(resource_info)}")
    
    def run_process(self, product):
        """공정 실행 (generator 함수)"""
        return self.env.process(self._process_logic(product))
    
    def _process_logic(self, product):
        """실제 공정 로직"""
        print(f"[시간 {self.env.now:.1f}] [{self.process_name}] 제품 {product.product_id} 처리 시작")
        
        # 기계가 있으면 기계 사용
        if self.machines:
            machine = self.machines[0]  # 첫 번째 기계 사용
            yield from machine.operate(product)
        
        # 작업자가 있으면 작업자 작업
        if self.workers:
            worker = self.workers[0]  # 첫 번째 작업자 사용
            yield from worker.work(product, "제조작업", 1.0)
        
        print(f"[시간 {self.env.now:.1f}] [{self.process_name}] 제품 {product.product_id} 처리 완료")

def test_simulation_with_machine_only():
    """기계만 사용하는 시뮬레이션 테스트"""
    print("=== 기계만 사용하는 시뮬레이션 테스트 ===")
    
    # SimPy 환경 생성
    env = simpy.Environment()
    
    # 기계 생성
    machine = Machine(env, "M001", "CNC_MACHINE", capacity=1, processing_time=2.0)
    
    # 공정 생성
    process = SimpleManufacturingProcess(
        env=env,
        machines=[machine],
        workers=None,
        process_name="기계전용공정"
    )
    
    # 제품 생성
    product = Product("P001", "테스트제품1")
    
    # 공정 실행
    env.process(process._process_logic(product))
    
    # 시뮬레이션 실행
    env.run(until=10)
    
    print("✅ 기계만 사용하는 시뮬레이션 완료\n")

def test_simulation_with_worker_only():
    """작업자만 사용하는 시뮬레이션 테스트"""
    print("=== 작업자만 사용하는 시뮬레이션 테스트 ===")
    
    # SimPy 환경 생성
    env = simpy.Environment()
    
    # 작업자 생성
    worker = Worker(env, "W001", ["조립", "검사"], work_speed=1.5)
    
    # 공정 생성
    process = SimpleManufacturingProcess(
        env=env,
        machines=None,
        workers=[worker],
        process_name="수작업공정"
    )
    
    # 제품 생성
    product = Product("P002", "테스트제품2")
    
    # 공정 실행
    env.process(process._process_logic(product))
    
    # 시뮬레이션 실행
    env.run(until=10)
    
    print("✅ 작업자만 사용하는 시뮬레이션 완료\n")

def test_simulation_with_both():
    """기계와 작업자를 모두 사용하는 시뮬레이션 테스트"""
    print("=== 기계와 작업자를 모두 사용하는 시뮬레이션 테스트 ===")
    
    # SimPy 환경 생성
    env = simpy.Environment()
    
    # 기계와 작업자 생성
    machine = Machine(env, "M002", "ASSEMBLY_MACHINE", capacity=1, processing_time=1.5)
    worker = Worker(env, "W002", ["기계조작", "품질검사"], work_speed=1.0)
    
    # 공정 생성
    process = SimpleManufacturingProcess(
        env=env,
        machines=[machine],
        workers=[worker],
        process_name="자동화공정"
    )
    
    # 제품 생성
    product = Product("P003", "테스트제품3")
    
    # 공정 실행
    env.process(process._process_logic(product))
    
    # 시뮬레이션 실행
    env.run(until=10)
    
    print("✅ 기계와 작업자를 모두 사용하는 시뮬레이션 완료\n")

def test_multiple_products():
    """여러 제품을 처리하는 시뮬레이션 테스트"""
    print("=== 여러 제품을 처리하는 시뮬레이션 테스트 ===")
    
    # SimPy 환경 생성
    env = simpy.Environment()
    
    # 기계와 작업자 생성
    machine = Machine(env, "M003", "MULTI_MACHINE", capacity=2, processing_time=1.0)
    worker = Worker(env, "W003", ["다중작업"], work_speed=1.2)
    
    # 공정 생성
    process = SimpleManufacturingProcess(
        env=env,
        machines=[machine],
        workers=[worker],
        process_name="다중제품처리공정"
    )
    
    def product_generator():
        """제품을 주기적으로 생성하는 generator"""
        for i in range(3):
            product = Product(f"P00{i+4}", f"배치제품{i+1}")
            print(f"[시간 {env.now:.1f}] 새 제품 도착: {product.product_id}")
            
            # 공정 실행
            env.process(process._process_logic(product))
            
            # 다음 제품까지 대기
            yield env.timeout(0.5)
    
    # 제품 생성 프로세스 시작
    env.process(product_generator())
    
    # 시뮬레이션 실행
    env.run(until=15)
    
    print("✅ 여러 제품 처리 시뮬레이션 완료\n")

def test_invalid_process():
    """잘못된 공정 생성 테스트"""
    print("=== 잘못된 공정 생성 테스트 (실패해야 함) ===")
    
    # SimPy 환경 생성
    env = simpy.Environment()
    
    try:
        # 기계도 작업자도 없는 공정 생성 시도
        process = SimpleManufacturingProcess(
            env=env,
            machines=None,
            workers=None,
            process_name="불가능한공정"
        )
        print("❌ 예상과 다름: 공정이 생성됨 (실패해야 했음)")
        return False
        
    except ValueError as e:
        print(f"✅ 예상대로 실패: {e}")
        return True
    except Exception as e:
        print(f"❌ 예상과 다른 오류: {e}")
        return False

def main():
    """모든 시뮬레이션 테스트 실행"""
    print("machine/worker 필수 요구사항 시뮬레이션 테스트 시작\n")
    
    # 각 테스트 실행
    test_simulation_with_machine_only()
    test_simulation_with_worker_only()
    test_simulation_with_both()
    test_multiple_products()
    
    # 검증 테스트
    success = test_invalid_process()
    
    print(f"{'='*50}")
    print("시뮬레이션 테스트 완료")
    print(f"{'='*50}")
    
    if success:
        print("🎉 모든 시뮬레이션 테스트가 성공적으로 완료되었습니다!")
        print("✅ machine 또는 worker 중 하나는 필수로 있어야 한다는 요구사항이 올바르게 구현되었습니다.")
    else:
        print("⚠️  일부 테스트에서 문제가 발생했습니다.")

if __name__ == "__main__":
    main()
