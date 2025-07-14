class ManufacturingProcess:
    """제조 공정을 정의하는 클래스입니다."""

    def __init__(self, machines, workers):
        """
        제조 공정의 초기화 메서드입니다.

        :param machines: 사용될 기계 목록
        :param workers: 작업자 목록
        """
        self.machines = machines  # 기계 목록
        self.workers = workers    # 작업자 목록
        self.production_line = []  # 생산 라인 초기화

    def start_process(self):
        """제조 공정을 시작하는 메서드입니다."""
        # 공정 시작 로직 구현
        print("제조 공정이 시작되었습니다.")

    def stop_process(self):
        """제조 공정을 중지하는 메서드입니다."""
        # 공정 중지 로직 구현
        print("제조 공정이 중지되었습니다.")

    def add_to_production_line(self, product):
        """
        생산 라인에 제품을 추가하는 메서드입니다.

        :param product: 추가할 제품
        """
        self.production_line.append(product)  # 제품 추가
        print(f"{product}가 생산 라인에 추가되었습니다.")

    def remove_from_production_line(self, product):
        """
        생산 라인에서 제품을 제거하는 메서드입니다.

        :param product: 제거할 제품
        """
        if product in self.production_line:
            self.production_line.remove(product)  # 제품 제거
            print(f"{product}가 생산 라인에서 제거되었습니다.")
        else:
            print(f"{product}는 생산 라인에 없습니다.")