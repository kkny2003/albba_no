class AssemblyProcess:
    """조립 공정을 정의하는 클래스입니다."""

    def __init__(self, machines, workers):
        """
        초기화 메서드입니다.
        
        :param machines: 조립에 사용될 기계 목록
        :param workers: 조립 작업을 수행할 작업자 목록
        """
        self.machines = machines  # 기계 목록
        self.workers = workers    # 작업자 목록
        self.assembly_line = []   # 조립 라인 초기화

    def add_to_assembly_line(self, product):
        """
        조립 라인에 제품을 추가하는 메서드입니다.
        
        :param product: 조립할 제품
        """
        self.assembly_line.append(product)  # 제품 추가
        print(f"제품 {product}이(가) 조립 라인에 추가되었습니다.")

    def start_assembly(self):
        """조립 작업을 시작하는 메서드입니다."""
        for product in self.assembly_line:
            self.assemble_product(product)  # 각 제품 조립

    def assemble_product(self, product):
        """
        제품을 조립하는 메서드입니다.
        
        :param product: 조립할 제품
        """
        print(f"제품 {product}을(를) 조립 중입니다...")
        # 조립 로직을 여기에 추가합니다.
        # 예: 기계 사용, 작업자 할당 등
        print(f"제품 {product} 조립 완료!")

    def clear_assembly_line(self):
        """조립 라인을 비우는 메서드입니다."""
        self.assembly_line.clear()  # 조립 라인 초기화
        print("조립 라인이 비워졌습니다.")