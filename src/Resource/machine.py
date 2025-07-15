class Machine:
    """기계 모델을 정의하는 클래스입니다."""
    
    def __init__(self, machine_id, machine_type):
        """기계의 ID와 유형을 초기화합니다.
        
        Args:
            machine_id (str): 기계의 고유 ID
            machine_type (str): 기계의 유형
        """
        self.machine_id = machine_id  # 기계 ID
        self.machine_type = machine_type  # 기계 유형
        self.status = 'idle'  # 기계 상태 (대기 중)
    
    def start(self):
        """기계를 시작합니다."""
        if self.status == 'idle':
            self.status = 'running'  # 기계 상태를 실행 중으로 변경
            print(f"{self.machine_id} 기계가 시작되었습니다.")
        else:
            print(f"{self.machine_id} 기계는 이미 실행 중입니다.")
    
    def stop(self):
        """기계를 중지합니다."""
        if self.status == 'running':
            self.status = 'idle'  # 기계 상태를 대기 중으로 변경
            print(f"{self.machine_id} 기계가 중지되었습니다.")
        else:
            print(f"{self.machine_id} 기계는 이미 대기 중입니다.")
    
    def get_status(self):
        """기계의 현재 상태를 반환합니다.
        
        Returns:
            str: 기계의 현재 상태
        """
        return self.status  # 기계의 현재 상태 반환

    def __str__(self):
        """기계의 정보를 문자열로 반환합니다."""
        return f"기계 ID: {self.machine_id}, 유형: {self.machine_type}, 상태: {self.status}"