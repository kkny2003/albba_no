class ResourceManager:
    """자원 관리 클래스입니다. 자원의 할당 및 해제를 관리합니다."""

    def __init__(self):
        """초기화 메서드입니다. 자원 목록을 초기화합니다."""
        self.resources = []  # 자원 목록 초기화

    def add_resource(self, resource):
        """자원을 추가하는 메서드입니다.
        
        Args:
            resource: 추가할 자원 객체입니다.
        """
        self.resources.append(resource)  # 자원 목록에 추가
        print(f"자원 추가: {resource}")

    def allocate_resource(self):
        """자원을 할당하는 메서드입니다.
        
        Returns:
            할당된 자원 객체입니다. 자원이 없으면 None을 반환합니다.
        """
        if self.resources:
            allocated_resource = self.resources.pop(0)  # 첫 번째 자원 할당
            print(f"자원 할당: {allocated_resource}")
            return allocated_resource
        print("할당할 자원이 없습니다.")
        return None  # 자원이 없을 경우 None 반환

    def release_resource(self, resource):
        """자원을 해제하는 메서드입니다.
        
        Args:
            resource: 해제할 자원 객체입니다.
        """
        self.resources.append(resource)  # 자원 목록에 추가하여 해제
        print(f"자원 해제: {resource}")

    def get_resources(self):
        """현재 자원 목록을 반환하는 메서드입니다.
        
        Returns:
            현재 자원 목록입니다.
        """
        return self.resources  # 현재 자원 목록 반환