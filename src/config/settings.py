class Settings:
    """시뮬레이션 설정을 정의하는 클래스입니다."""
    
    def __init__(self):
        # 기본 설정 값 초기화
        self.simulation_time = 1000  # 시뮬레이션 시간 (단위: 초)
        self.num_machines = 5         # 기계 수
        self.num_workers = 10         # 작업자 수
        self.production_rate = 1.0    # 생산 속도 (단위: 제품/초)
        self.quality_control_enabled = True  # 품질 관리 활성화 여부

    def update_settings(self, **kwargs):
        """설정 값을 업데이트하는 메서드입니다."""
        for key, value in kwargs.items():
            if hasattr(self, key):
                setattr(self, key, value)
            else:
                raise AttributeError(f"{key}는 유효한 설정 항목이 아닙니다.")

    def display_settings(self):
        """현재 설정 값을 출력하는 메서드입니다."""
        settings = vars(self)
        for key, value in settings.items():
            print(f"{key}: {value}")  # 설정 항목과 값을 출력합니다.