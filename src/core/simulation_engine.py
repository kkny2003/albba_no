class SimulationEngine:
    """시뮬레이션 엔진 클래스입니다. 시뮬레이션의 실행 및 관리를 담당합니다."""

    def __init__(self):
        """초기화 메서드입니다. 시뮬레이션 엔진의 기본 설정을 초기화합니다."""
        self.running = False  # 시뮬레이션 실행 상태
        self.time = 0  # 시뮬레이션 시간

    def start(self):
        """시뮬레이션을 시작하는 메서드입니다."""
        self.running = True
        print("시뮬레이션이 시작되었습니다.")

    def stop(self):
        """시뮬레이션을 중지하는 메서드입니다."""
        self.running = False
        print("시뮬레이션이 중지되었습니다.")

    def step(self):
        """시뮬레이션의 한 단계를 진행하는 메서드입니다."""
        if self.running:
            self.time += 1  # 시간 증가
            print(f"시뮬레이션 시간: {self.time}")

    def reset(self):
        """시뮬레이션을 초기 상태로 리셋하는 메서드입니다."""
        self.running = False
        self.time = 0
        print("시뮬레이션이 리셋되었습니다.")