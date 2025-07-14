class QualityControlProcess:
    """품질 관리 공정을 정의하는 클래스입니다."""

    def __init__(self, inspection_criteria):
        """
        품질 관리 공정의 초기화 메서드입니다.
        
        :param inspection_criteria: 품질 검사 기준
        """
        self.inspection_criteria = inspection_criteria  # 품질 검사 기준 저장
        self.inspected_items = []  # 검사된 항목 목록 초기화

    def inspect(self, item):
        """
        주어진 항목을 검사하는 메서드입니다.
        
        :param item: 검사할 항목
        :return: 검사 결과 (합격/불합격)
        """
        result = self.evaluate_quality(item)  # 품질 평가 수행
        self.inspected_items.append((item, result))  # 검사 결과 저장
        return result  # 검사 결과 반환

    def evaluate_quality(self, item):
        """
        품질을 평가하는 메서드입니다.
        
        :param item: 평가할 항목
        :return: 품질 평가 결과 (합격/불합격)
        """
        # 품질 기준에 따라 평가 수행
        if item.meets_criteria(self.inspection_criteria):
            return "합격"  # 기준을 충족하면 합격
        else:
            return "불합격"  # 기준을 충족하지 않으면 불합격

    def get_inspection_report(self):
        """
        검사 보고서를 생성하는 메서드입니다.
        
        :return: 검사 보고서
        """
        report = {}
        for item, result in self.inspected_items:
            report[item.id] = result  # 항목 ID와 검사 결과 저장
        return report  # 검사 보고서 반환