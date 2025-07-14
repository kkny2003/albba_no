"""
공정 연결 기능 사용 예제
>> 연산자를 사용하여 공정들을 체인으로 연결하는 방법을 보여줍니다.
"""

from src.processes import ManufacturingProcess, AssemblyProcess, QualityControlProcess


def main():
    """공정 연결 예제 실행"""
    
    print("=" * 60)
    print("제조 시뮬레이션 프레임워크 - 공정 연결 예제")
    print("=" * 60)
    
    # 샘플 기계와 작업자 리스트 생성
    machines = ["CNC기계1", "용접기1", "프레스1"]
    workers = ["작업자A", "작업자B", "작업자C"]
    inspection_criteria = {"강도": "> 100N", "정밀도": "± 0.1mm"}
    
    # 각 공정 인스턴스 생성
    print("\n1. 공정 인스턴스 생성")
    manufacturing = ManufacturingProcess(
        machines=machines[:2], 
        workers=workers[:2], 
        process_id="P001",
        process_name="원료가공공정"
    )
    print(f"   ✓ {manufacturing}")
    
    assembly = AssemblyProcess(
        machines=machines[1:], 
        workers=workers[1:], 
        process_id="P002",
        process_name="부품조립공정"
    )
    print(f"   ✓ {assembly}")
    
    quality_control = QualityControlProcess(
        inspection_criteria=inspection_criteria, 
        process_id="P003",
        process_name="최종품질검사"
    )
    print(f"   ✓ {quality_control}")
    
    # >> 연산자를 사용한 공정 연결 예제
    print("\n2. >> 연산자를 사용한 공정 연결")
    
    # 방법 1: 두 공정 연결
    print("\n   [방법 1] 두 공정 직접 연결")
    chain1 = manufacturing >> assembly
    print(f"   연결 결과: {chain1}")
    
    # 방법 2: 세 공정 연쇄 연결
    print("\n   [방법 2] 세 공정 연쇄 연결")
    chain2 = manufacturing >> assembly >> quality_control
    print(f"   연결 결과: {chain2}")
    
    # 방법 3: 체인에 추가 공정 연결
    print("\n   [방법 3] 기존 체인에 공정 추가")
    additional_qc = QualityControlProcess(
        inspection_criteria={"외관": "양호"}, 
        process_id="P004",
        process_name="외관검사"
    )
    extended_chain = chain1 >> additional_qc
    print(f"   연결 결과: {extended_chain}")
    
    # 공정 체인 실행 예제
    print("\n3. 공정 체인 실행")
    print("\n   전체 공정 체인 실행:")
    sample_product = "샘플제품A"
    result = chain2.execute_chain(sample_product)
    
    # 공정 연결 정보 확인
    print("\n4. 공정 연결 정보 확인")
    print(f"\n   {manufacturing.process_name} 연결 정보:")
    info = manufacturing.get_process_info()
    print(f"   - 다음 공정: {info['next_processes']}")
    print(f"   - 이전 공정: {info['previous_processes']}")
    
    print(f"\n   {assembly.process_name} 연결 정보:")
    info = assembly.get_process_info()
    print(f"   - 다음 공정: {info['next_processes']}")
    print(f"   - 이전 공정: {info['previous_processes']}")
    
    # 복잡한 체인 예제
    print("\n5. 복잡한 공정 체인 예제")
    
    # 병렬 공정을 위한 추가 공정들
    packaging = AssemblyProcess(
        machines=["포장기1"], 
        workers=["포장작업자"], 
        process_id="P005",
        process_name="포장공정"
    )
    
    final_inspection = QualityControlProcess(
        inspection_criteria={"포장상태": "완전"}, 
        process_id="P006",
        process_name="출하전검사"
    )
    
    # 복잡한 체인 생성
    complex_chain = manufacturing >> assembly >> quality_control >> packaging >> final_inspection
    print(f"\n   복잡한 공정 체인: {complex_chain}")
    print(f"   총 공정 수: {len(complex_chain.processes)}")
    
    print("\n" + "=" * 60)
    print("예제 실행 완료!")
    print("=" * 60)


if __name__ == "__main__":
    main()
