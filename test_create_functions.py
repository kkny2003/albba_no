#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Create 함수들이 정상적으로 작동하는지 테스트하는 스크립트
"""

from src.Resource import (
    create_machine_resource, 
    create_worker_resource, 
    create_product_resource, 
    create_transport_resource, 
    ResourceType
)

def test_create_functions():
    """각 create 함수가 정상적으로 작동하는지 테스트"""
    
    print("=== Create 함수 테스트 시작 ===\n")
    
    # 기계 자원 생성 테스트
    print("1. 기계 자원 생성 테스트")
    machine = create_machine_resource('M001', '조립기계', '조립기계', 2.0)
    print(f"   생성된 기계: {machine}")
    print(f"   기계 타입: {machine.resource_type}")
    print(f"   기계 용량: {machine.get_property('capacity')}")
    print(f"   기계 상태: {machine.get_property('status')}\n")
    
    # 작업자 자원 생성 테스트
    print("2. 작업자 자원 생성 테스트")
    worker = create_worker_resource('W001', '김작업자', '고급', '조립부')
    print(f"   생성된 작업자: {worker}")
    print(f"   작업자 타입: {worker.resource_type}")
    print(f"   기술 수준: {worker.get_property('skill_level')}")
    print(f"   소속 부서: {worker.get_property('department')}\n")
    
    # 제품 자원 생성 테스트
    print("3. 제품 자원 생성 테스트")
    product = create_product_resource('P001', '부품A', ResourceType.RAW_MATERIAL, 100.0, 'SKU001')
    print(f"   생성된 제품: {product}")
    print(f"   제품 타입: {product.resource_type}")
    print(f"   제품 수량: {product.quantity}")
    print(f"   제품 SKU: {product.get_property('sku')}\n")
    
    # 운송 자원 생성 테스트
    print("4. 운송 자원 생성 테스트")
    transport = create_transport_resource('T001', '지게차1', 500.0, '지게차')
    print(f"   생성된 운송수단: {transport}")
    print(f"   운송 타입: {transport.resource_type}")
    print(f"   운송 용량: {transport.get_property('capacity')}")
    print(f"   운송 수단 타입: {transport.get_property('transport_type')}\n")
    
    print("=== 모든 테스트 성공! ===")
    print("각 리소스 타입별 create 함수가 정상적으로 해당 파일로 이동되었습니다.")

if __name__ == "__main__":
    test_create_functions()
