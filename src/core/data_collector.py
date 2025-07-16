class DataCollector:
    """시뮬레이션 데이터를 수집하고 저장하는 클래스입니다."""

    def __init__(self):
        """초기화 메서드로, 데이터 저장소를 초기화합니다."""
        self.data = []  # 수집된 데이터를 저장할 리스트
        self.production_data = []  # 생산 데이터 전용 저장소

    def collect_data(self, simulation_step, data_point):
        """주어진 시뮬레이션 단계에서 데이터를 수집합니다.

        Args:
            simulation_step (int): 현재 시뮬레이션 단계
            data_point (dict): 수집할 데이터 포인트
        """
        # 데이터 포인트에 시뮬레이션 단계를 추가
        data_entry = {
            'step': simulation_step,
            'data': data_point
        }
        self.data.append(data_entry)  # 수집된 데이터를 리스트에 추가

    def collect_production_data(self, product_id, timestamp, process_time, quality_score):
        """생산 데이터를 수집합니다.
        
        Args:
            product_id (str): 제품 ID
            timestamp (float): 타임스탬프
            process_time (float): 공정 시간
            quality_score (float): 품질 점수
        """
        production_entry = {
            'product_id': product_id,
            'timestamp': timestamp,
            'process_time': process_time,
            'quality_score': quality_score
        }
        self.production_data.append(production_entry)

    def get_data(self):
        """수집된 데이터를 반환합니다.

        Returns:
            list: 수집된 데이터 리스트
        """
        return self.data  # 수집된 데이터 반환

    def get_production_summary(self):
        """생산 데이터 요약을 반환합니다.
        
        Returns:
            list: 수집된 생산 데이터 리스트
        """
        return self.production_data

    def clear_data(self):
        """수집된 데이터를 초기화합니다."""
        self.data = []  # 데이터 리스트를 비움
        self.production_data = []  # 생산 데이터도 초기화

    def get_statistics(self):
        """수집된 데이터의 통계를 반환합니다.
        
        Returns:
            dict: 통계 정보
        """
        if not self.production_data:
            return {'total_products': 0}
            
        process_times = [item['process_time'] for item in self.production_data]
        quality_scores = [item['quality_score'] for item in self.production_data]
        
        return {
            'total_products': len(self.production_data),
            'avg_process_time': sum(process_times) / len(process_times),
            'avg_quality_score': sum(quality_scores) / len(quality_scores),
            'min_process_time': min(process_times),
            'max_process_time': max(process_times)
        }