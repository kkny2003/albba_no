# /manufacturing-simulation-framework/manufacturing-simulation-framework/src/utils/statistics.py

# 통계 관련 유틸리티 함수를 포함하는 파일입니다.

import numpy as np

def calculate_mean(data):
    """주어진 데이터의 평균을 계산합니다."""
    return np.mean(data)

def calculate_median(data):
    """주어진 데이터의 중앙값을 계산합니다."""
    return np.median(data)

def calculate_variance(data):
    """주어진 데이터의 분산을 계산합니다."""
    return np.var(data)

def calculate_standard_deviation(data):
    """주어진 데이터의 표준편차를 계산합니다."""
    return np.std(data)

def calculate_percentile(data, percentile):
    """주어진 데이터의 특정 백분위를 계산합니다."""
    return np.percentile(data, percentile)

def summarize_statistics(data):
    """주어진 데이터의 통계 요약을 반환합니다."""
    return {
        'mean': calculate_mean(data),
        'median': calculate_median(data),
        'variance': calculate_variance(data),
        'standard_deviation': calculate_standard_deviation(data),
        '25th_percentile': calculate_percentile(data, 25),
        '75th_percentile': calculate_percentile(data, 75),
    }