# /manufacturing-simulation-framework/manufacturing-simulation-framework/src/utils/statistics.py

# 통계 관련 유틸리티 함수를 포함하는 파일입니다.
# 
# ⚠️ NOTICE: 기본 통계 함수들은 유지되지만,
# 통합된 통계 시스템을 위해서는 UnifiedStatisticsManager 사용을 권장합니다.

import numpy as np
import warnings
from scipy import stats
import pandas as pd

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

class StatisticsAnalyzer:
    """고급 통계 분석을 위한 클래스"""
    
    def __init__(self):
        """StatisticsAnalyzer 초기화"""
        pass
    
    def calculate_basic_statistics(self, data):
        """기본 통계량 계산"""
        data = np.array(data)
        return {
            'mean': np.mean(data),
            'median': np.median(data),
            'std': np.std(data),
            'min': np.min(data),
            'max': np.max(data),
            'q25': np.percentile(data, 25),
            'q75': np.percentile(data, 75),
            'count': len(data)
        }
    
    def analyze_trend(self, data):
        """데이터의 트렌드 분석"""
        data = np.array(data)
        x = np.arange(len(data))
        slope, intercept, r_value, p_value, std_err = stats.linregress(x, data)
        
        if slope > 0.01:
            direction = "증가"
        elif slope < -0.01:
            direction = "감소"
        else:
            direction = "안정"
            
        return {
            'direction': direction,
            'slope': slope,
            'correlation': r_value,
            'p_value': p_value
        }
    
    def calculate_correlation(self, data1, data2):
        """두 데이터셋 간의 상관관계 계산"""
        correlation, _ = stats.pearsonr(data1, data2)
        return correlation
    
    def detect_outliers(self, data, method='iqr'):
        """이상치 감지 (IQR 방법 사용)"""
        data = np.array(data)
        if method == 'iqr':
            q1 = np.percentile(data, 25)
            q3 = np.percentile(data, 75)
            iqr = q3 - q1
            lower_bound = q1 - 1.5 * iqr
            upper_bound = q3 + 1.5 * iqr
            outliers = data[(data < lower_bound) | (data > upper_bound)]
        else:
            # Z-score 방법
            z_scores = np.abs(stats.zscore(data))
            outliers = data[z_scores > 3]
        
        return outliers
    
    def calculate_performance_metrics(self, actual_values, target_value):
        """성과 지표 계산"""
        actual_values = np.array(actual_values)
        
        # 목표 달성률
        achievement_rate = np.mean(actual_values >= target_value)
        
        # 평균 성과 대비 목표
        performance_ratio = np.mean(actual_values) / target_value
        
        # 변동계수 (CV)
        cv = np.std(actual_values) / np.mean(actual_values)
        
        return {
            'achievement_rate': achievement_rate,
            'performance_ratio': performance_ratio,
            'coefficient_of_variation': cv,
            'target_value': target_value,
            'mean_actual': np.mean(actual_values)
        }