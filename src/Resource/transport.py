class Transport:
    """운송 모델 클래스입니다. 제품의 이동을 관리합니다."""

    def __init__(self, transport_id, capacity):
        """
        초기화 메서드입니다.
        
        :param transport_id: 운송 수단의 ID
        :param capacity: 운송 수단의 수용 능력
        """
        self.transport_id = transport_id  # 운송 수단의 ID
        self.capacity = capacity            # 운송 수단의 수용 능력
        self.current_load = 0               # 현재 적재량 초기화

    def load_product(self, product):
        """
        제품을 운송 수단에 적재합니다.
        
        :param product: 적재할 제품 객체
        :return: 적재 성공 여부
        """
        if self.current_load < self.capacity:
            self.current_load += 1  # 적재량 증가
            return True  # 적재 성공
        else:
            return False  # 적재 실패

    def unload_product(self):
        """
        운송 수단에서 제품을 하역합니다.
        
        :return: 하역 성공 여부
        """
        if self.current_load > 0:
            self.current_load -= 1  # 적재량 감소
            return True  # 하역 성공
        else:
            return False  # 하역 실패

    def get_current_load(self):
        """
        현재 적재량을 반환합니다.
        
        :return: 현재 적재량
        """
        return self.current_load  # 현재 적재량 반환

    def is_full(self):
        """
        운송 수단이 가득 찼는지 확인합니다.
        
        :return: 가득 찼으면 True, 아니면 False
        """
        return self.current_load >= self.capacity  # 가득 찼는지 여부 반환