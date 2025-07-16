# visualization.py

import matplotlib.pyplot as plt  # 시각화를 위한 matplotlib 라이브러리 임포트
import numpy as np  # 수치 계산을 위한 numpy 라이브러리 임포트
import os

def plot_simulation_results(time, values, title='Simulation Results', xlabel='Time', ylabel='Value'):
    """
    시뮬레이션 결과를 시각화하는 함수입니다.
    
    :param time: 시뮬레이션 시간 데이터
    :param values: 시뮬레이션 값 데이터
    :param title: 그래프 제목
    :param xlabel: x축 레이블
    :param ylabel: y축 레이블
    """
    plt.figure(figsize=(10, 5))  # 그래프 크기 설정
    plt.plot(time, values, marker='o')  # 시간에 따른 값 플롯
    plt.title(title)  # 그래프 제목 설정
    plt.xlabel(xlabel)  # x축 레이블 설정
    plt.ylabel(ylabel)  # y축 레이블 설정
    plt.grid(True)  # 그리드 표시
    plt.show()  # 그래프 출력

def save_simulation_results(time, values, filename='simulation_results.png'):
    """
    시뮬레이션 결과를 이미지 파일로 저장하는 함수입니다.
    
    :param time: 시뮬레이션 시간 데이터
    :param values: 시뮬레이션 값 데이터
    :param filename: 저장할 파일 이름
    """
    plt.figure(figsize=(10, 5))  # 그래프 크기 설정
    plt.plot(time, values, marker='o')  # 시간에 따른 값 플롯
    plt.title('Simulation Results')  # 그래프 제목 설정
    plt.xlabel('Time')  # x축 레이블 설정
    plt.ylabel('Value')  # y축 레이블 설정
    plt.grid(True)  # 그리드 표시
    plt.savefig(filename)  # 이미지 파일로 저장
    plt.close()  # 그래프 닫기

class VisualizationManager:
    """고급 시각화 기능을 제공하는 클래스"""
    
    def __init__(self, output_dir="visualizations"):
        """VisualizationManager 초기화"""
        self.output_dir = output_dir
        # 출력 디렉토리 생성
        if not os.path.exists(output_dir):
            os.makedirs(output_dir)
    
    def plot_line_chart(self, x_data, y_data, title="Line Chart", x_label="X", y_label="Y", save_path=None):
        """라인 차트 생성"""
        plt.figure(figsize=(10, 6))
        plt.plot(x_data, y_data, linewidth=2, marker='o', markersize=4)
        plt.title(title, fontsize=14, fontweight='bold')
        plt.xlabel(x_label)
        plt.ylabel(y_label)
        plt.grid(True, alpha=0.3)
        plt.tight_layout()
        
        if save_path:
            full_path = os.path.join(self.output_dir, save_path)
            plt.savefig(full_path, dpi=300, bbox_inches='tight')
        plt.close()
    
    def plot_histogram(self, data, title="Histogram", x_label="Value", bins=20, save_path=None):
        """히스토그램 생성"""
        plt.figure(figsize=(10, 6))
        plt.hist(data, bins=bins, alpha=0.7, color='skyblue', edgecolor='black')
        plt.title(title, fontsize=14, fontweight='bold')
        plt.xlabel(x_label)
        plt.ylabel("빈도")
        plt.grid(True, alpha=0.3)
        plt.tight_layout()
        
        if save_path:
            full_path = os.path.join(self.output_dir, save_path)
            plt.savefig(full_path, dpi=300, bbox_inches='tight')
        plt.close()
    
    def plot_boxplot(self, data, title="Box Plot", y_label="Value", save_path=None):
        """박스플롯 생성"""
        plt.figure(figsize=(10, 6))
        
        if isinstance(data, dict):
            # 딕셔너리 형태의 데이터 처리
            labels = list(data.keys())
            values = list(data.values())
            plt.boxplot(values, labels=labels)
        else:
            # 리스트나 배열 형태의 데이터 처리
            plt.boxplot(data)
        
        plt.title(title, fontsize=14, fontweight='bold')
        plt.ylabel(y_label)
        plt.grid(True, alpha=0.3)
        plt.tight_layout()
        
        if save_path:
            full_path = os.path.join(self.output_dir, save_path)
            plt.savefig(full_path, dpi=300, bbox_inches='tight')
        plt.close()
    
    def plot_scatter(self, x_data, y_data, title="Scatter Plot", x_label="X", y_label="Y", save_path=None):
        """산점도 생성"""
        plt.figure(figsize=(10, 6))
        plt.scatter(x_data, y_data, alpha=0.6, s=50)
        plt.title(title, fontsize=14, fontweight='bold')
        plt.xlabel(x_label)
        plt.ylabel(y_label)
        plt.grid(True, alpha=0.3)
        plt.tight_layout()
        
        if save_path:
            full_path = os.path.join(self.output_dir, save_path)
            plt.savefig(full_path, dpi=300, bbox_inches='tight')
        plt.close()
    
    def plot_bar_chart(self, categories, values, title="Bar Chart", x_label="Category", y_label="Value", save_path=None):
        """막대 차트 생성"""
        plt.figure(figsize=(10, 6))
        plt.bar(categories, values, color='lightcoral', alpha=0.8)
        plt.title(title, fontsize=14, fontweight='bold')
        plt.xlabel(x_label)
        plt.ylabel(y_label)
        plt.xticks(rotation=45)
        plt.grid(True, alpha=0.3, axis='y')
        plt.tight_layout()
        
        if save_path:
            full_path = os.path.join(self.output_dir, save_path)
            plt.savefig(full_path, dpi=300, bbox_inches='tight')
        plt.close()
    
    def plot_heatmap(self, data, title="Heatmap", save_path=None):
        """히트맵 생성"""
        plt.figure(figsize=(10, 8))
        plt.imshow(data, cmap='Blues', aspect='auto')
        plt.colorbar()
        plt.title(title, fontsize=14, fontweight='bold')
        plt.tight_layout()
        
        if save_path:
            full_path = os.path.join(self.output_dir, save_path)
            plt.savefig(full_path, dpi=300, bbox_inches='tight')
        plt.close()