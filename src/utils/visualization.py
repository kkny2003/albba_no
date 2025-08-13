# visualization.py

import matplotlib.pyplot as plt  # 시각화를 위한 matplotlib 라이브러리 임포트
import numpy as np  # 수치 계산을 위한 numpy 라이브러리 임포트
import os
import matplotlib
import platform

# 한글 폰트 설정 (Windows/Mac/Linux 자동 감지)
if platform.system() == 'Windows':
    matplotlib.rc('font', family='Malgun Gothic')
elif platform.system() == 'Darwin':
    matplotlib.rc('font', family='AppleGothic')
else:
    matplotlib.rc('font', family='NanumGothic')
# 마이너스 깨짐 방지
matplotlib.rcParams['axes.unicode_minus'] = False

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
    
    def plot_multi_line_chart(self, time_data, data_series, title="Multi-Line Chart", 
                             x_label="Time", y_label="Value", save_path=None, 
                             colors=None, line_styles=None, show_legend=True):
        """
        여러 데이터 시리즈를 하나의 차트에 표시하는 다중 선형 차트 생성
        
        Args:
            time_data: 공통 시간 축 데이터 (리스트 또는 배열)
            data_series: 데이터 시리즈 딕셔너리 {라벨: 값_리스트}
            title: 차트 제목
            x_label: X축 레이블
            y_label: Y축 레이블
            save_path: 저장 경로 (선택적)
            colors: 선 색상 리스트 (선택적)
            line_styles: 선 스타일 리스트 (선택적)
            show_legend: 범례 표시 여부
        """
        plt.figure(figsize=(12, 8))
        
        # 기본 색상과 선 스타일 설정
        if colors is None:
            colors = ['blue', 'red', 'green', 'orange', 'purple', 'brown', 'pink', 'gray', 'olive', 'cyan']
        if line_styles is None:
            line_styles = ['-', '--', '-.', ':', '-', '--', '-.', ':', '-', '--']
        
        # 각 데이터 시리즈를 플롯
        for i, (label, values) in enumerate(data_series.items()):
            color = colors[i % len(colors)]
            line_style = line_styles[i % len(line_styles)]
            
            plt.plot(time_data, values, 
                    label=label,
                    color=color,
                    linestyle=line_style,
                    linewidth=2,
                    marker='o',
                    markersize=3,
                    alpha=0.8)
        
        plt.title(title, fontsize=16, fontweight='bold')
        plt.xlabel(x_label, fontsize=12)
        plt.ylabel(y_label, fontsize=12)
        plt.grid(True, alpha=0.3)
        
        if show_legend and data_series:
            plt.legend(bbox_to_anchor=(1.05, 1), loc='upper left')
        
        plt.tight_layout()
        
        if save_path:
            full_path = os.path.join(self.output_dir, save_path)
            plt.savefig(full_path, dpi=300, bbox_inches='tight')
            print(f"[Visualization] 차트가 저장되었습니다: {full_path}")
            
        plt.show()
        plt.close()
    
    def plot_utilization_timeline(self, resource_utilization_data, title="Resource Utilization Timeline",
                                 save_path=None, show_percentage=True):
        """
        리소스 사용률 타임라인 차트 생성 (특화된 다중 선형 차트)
        
        Args:
            resource_utilization_data: {resource_id: [(time, utilization), ...]} 형태의 데이터
            title: 차트 제목
            save_path: 저장 경로
            show_percentage: 백분율로 표시할지 여부
        """
        plt.figure(figsize=(14, 8))
        
        colors = ['#1f77b4', '#ff7f0e', '#2ca02c', '#d62728', '#9467bd', 
                 '#8c564b', '#e377c2', '#7f7f7f', '#bcbd22', '#17becf']
        
        for i, (resource_id, data_points) in enumerate(resource_utilization_data.items()):
            if not data_points:
                continue
                
            times = [point[0] for point in data_points]
            utilizations = [point[1] * 100 if show_percentage else point[1] 
                          for point in data_points]
            
            color = colors[i % len(colors)]
            
            plt.plot(times, utilizations,
                    label=f"Resource {resource_id}",
                    color=color,
                    linewidth=2.5,
                    marker='o',
                    markersize=4,
                    alpha=0.8)
        
        plt.title(title, fontsize=16, fontweight='bold', pad=20)
        plt.xlabel('시뮬레이션 시간', fontsize=12)
        
        if show_percentage:
            plt.ylabel('사용률 (%)', fontsize=12)
            plt.ylim(0, 105)  # 0-100% + 여유공간
        else:
            plt.ylabel('사용률', fontsize=12)
            plt.ylim(0, 1.1)
        
        plt.grid(True, alpha=0.3)
        plt.legend(bbox_to_anchor=(1.05, 1), loc='upper left')
        
        # 통계 정보 추가
        if resource_utilization_data:
            plt.figtext(0.02, 0.02, 
                       f"총 리소스 수: {len(resource_utilization_data)}", 
                       fontsize=10, alpha=0.7)
        
        plt.tight_layout()
        
        if save_path:
            full_path = os.path.join(self.output_dir, save_path)
            plt.savefig(full_path, dpi=300, bbox_inches='tight')
            print(f"[Visualization] 사용률 차트가 저장되었습니다: {full_path}")
            
        plt.show()
        plt.close()