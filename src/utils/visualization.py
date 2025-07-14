# visualization.py

import matplotlib.pyplot as plt  # 시각화를 위한 matplotlib 라이브러리 임포트
import numpy as np  # 수치 계산을 위한 numpy 라이브러리 임포트

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