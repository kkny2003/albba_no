class Product:
    """제품 모델을 정의하는 클래스입니다."""

    def __init__(self, name, sku, quantity):
        """
        초기화 메서드입니다.
        
        :param name: 제품의 이름
        :param sku: 제품의 SKU (재고 관리 단위)
        :param quantity: 제품의 수량
        """
        self.name = name  # 제품 이름
        self.sku = sku    # SKU
        self.quantity = quantity  # 수량

    def update_quantity(self, amount):
        """
        제품 수량을 업데이트하는 메서드입니다.
        
        :param amount: 수량 변경 값 (양수 또는 음수)
        """
        self.quantity += amount  # 수량 업데이트

    def __str__(self):
        """제품 정보를 문자열로 반환합니다."""
        return f"Product(name={self.name}, sku={self.sku}, quantity={self.quantity})"  # 제품 정보 반환