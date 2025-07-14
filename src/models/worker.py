class Worker:
    """작업자 모델을 정의하는 클래스입니다."""
    
    def __init__(self, name, skill_level):
        """
        작업자의 이름과 기술 수준을 초기화합니다.
        
        :param name: 작업자의 이름
        :param skill_level: 작업자의 기술 수준 (예: 초급, 중급, 고급)
        """
        self.name = name  # 작업자의 이름
        self.skill_level = skill_level  # 작업자의 기술 수준
        self.current_task = None  # 현재 작업 상태

    def assign_task(self, task):
        """
        작업자를 특정 작업에 할당합니다.
        
        :param task: 할당할 작업
        """
        self.current_task = task  # 현재 작업을 할당
        print(f"{self.name} 작업자에게 '{task}' 작업이 할당되었습니다.")

    def complete_task(self):
        """
        현재 작업을 완료합니다.
        """
        if self.current_task:
            print(f"{self.name} 작업자가 '{self.current_task}' 작업을 완료했습니다.")
            self.current_task = None  # 작업 완료 후 초기화
        else:
            print(f"{self.name} 작업자는 현재 수행 중인 작업이 없습니다.")

    def __str__(self):
        """
        작업자의 정보를 문자열로 반환합니다.
        """
        return f"작업자 이름: {self.name}, 기술 수준: {self.skill_level}"