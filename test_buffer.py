"""
Buffer 리소스 테스트 파일
버퍼의 기본 기능들을 테스트합니다.
"""

import simpy
import sys
import os

# 프로젝트 루트 디렉토리를 Python 경로에 추가
project_root = os.path.join(os.path.dirname(__file__))
sys.path.append(project_root)

from src.Resource.buffer import Buffer, BufferPolicy, create_buffer_resource
from src.Resource.product import Product


def test_buffer_basic_operations():
    """버퍼의 기본 입출고 기능을 테스트합니다."""
    print("=== 버퍼 기본 기능 테스트 시작 ===")
    
    # 시뮬레이션 환경 생성
    env = simpy.Environment()
    
    # 버퍼 생성 (용량: 10, FIFO 정책)
    buffer = Buffer(env, "BUFFER_001", "중간저장소", capacity=10, policy=BufferPolicy.FIFO)
    
    # 테스트용 제품들 생성
    products = [
        Product(f"PROD_{i:03d}", f"테스트제품_{i}", specifications={"batch": i})
        for i in range(1, 6)
    ]
    
    def producer_process():
        """제품을 생산하여 버퍼에 저장하는 프로세스"""
        for i, product in enumerate(products):
            print(f"\n[생산자] 제품 {product.product_id} 생산 완료")
            yield env.process(buffer.put(product))
            
            # 버퍼 상태 출력
            status = buffer.get_status()
            print(f"[버퍼 상태] 저장량: {status['current_level']}/{status['capacity']}, "
                  f"사용률: {status['utilization']:.1%}")
            
            yield env.timeout(1)  # 1시간 대기
    
    def consumer_process():
        """버퍼에서 제품을 가져와 소비하는 프로세스"""
        yield env.timeout(3)  # 3시간 후 소비 시작
        
        for i in range(3):
            print(f"\n[소비자] 제품 요청 {i+1}")
            retrieved_product = yield env.process(buffer.get())
            print(f"[소비자] 제품 {retrieved_product.product_id} 수령")
            
            # 버퍼 상태 출력
            status = buffer.get_status()
            print(f"[버퍼 상태] 저장량: {status['current_level']}/{status['capacity']}, "
                  f"사용률: {status['utilization']:.1%}")
            
            yield env.timeout(2)  # 2시간 대기
    
    # 프로세스 시작
    env.process(producer_process())
    env.process(consumer_process())
    
    # 시뮬레이션 실행
    env.run(until=15)
    
    # 최종 상태 출력
    print(f"\n=== 최종 버퍼 상태 ===")
    print(buffer)
    final_status = buffer.get_status()
    print(f"총 입고 횟수: {final_status['total_put_operations']}")
    print(f"총 출고 횟수: {final_status['total_get_operations']}")
    print(f"총 저장된 아이템: {final_status['total_items_stored']}")
    print(f"총 회수된 아이템: {final_status['total_items_retrieved']}")


def test_buffer_policies():
    """FIFO와 LIFO 정책을 테스트합니다."""
    print("\n\n=== 버퍼 정책 테스트 시작 ===")
    
    # FIFO 테스트
    print("\n--- FIFO 정책 테스트 ---")
    env = simpy.Environment()
    fifo_buffer = Buffer(env, "FIFO_BUFFER", "FIFO테스트", capacity=5, policy=BufferPolicy.FIFO)
    
    def test_fifo():
        # 제품들을 순서대로 저장
        for i in range(1, 4):
            product = Product(f"FIFO_{i}", f"테스트제품_{i}")
            yield env.process(fifo_buffer.put(product))
        
        print(f"저장된 순서: FIFO_1, FIFO_2, FIFO_3")
        
        # 제품들을 순서대로 회수
        for i in range(3):
            product = yield env.process(fifo_buffer.get())
            print(f"회수된 제품: {product.product_id}")
    
    env.process(test_fifo())
    env.run()
    
    # LIFO 테스트
    print("\n--- LIFO 정책 테스트 ---")
    env = simpy.Environment()
    lifo_buffer = Buffer(env, "LIFO_BUFFER", "LIFO테스트", capacity=5, policy=BufferPolicy.LIFO)
    
    def test_lifo():
        # 제품들을 순서대로 저장
        for i in range(1, 4):
            product = Product(f"LIFO_{i}", f"테스트제품_{i}")
            yield env.process(lifo_buffer.put(product))
        
        print(f"저장된 순서: LIFO_1, LIFO_2, LIFO_3")
        
        # 제품들을 순서대로 회수
        for i in range(3):
            product = yield env.process(lifo_buffer.get())
            print(f"회수된 제품: {product.product_id}")
    
    env.process(test_lifo())
    env.run()


def test_buffer_resource_creation():
    """create_buffer_resource 함수를 테스트합니다."""
    print("\n\n=== 버퍼 리소스 생성 테스트 ===")
    
    # 버퍼 리소스 생성
    buffer_resource = create_buffer_resource(
        buffer_id="BUFFER_RES_001",
        buffer_type="원자재_저장소",
        capacity=50,
        policy=BufferPolicy.FIFO
    )
    
    print(f"생성된 버퍼 리소스:")
    print(f"- ID: {buffer_resource.resource_id}")
    print(f"- 이름: {buffer_resource.name}")
    print(f"- 타입: {buffer_resource.resource_type.value}")
    print(f"- 속성: {buffer_resource.properties}")


if __name__ == "__main__":
    test_buffer_basic_operations()
    test_buffer_policies()
    test_buffer_resource_creation()
    print("\n=== 모든 테스트 완료 ===")
