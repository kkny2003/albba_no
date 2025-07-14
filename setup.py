from setuptools import setup, find_packages

setup(
    name='manufacturing-simulation-framework',  # 패키지 이름
    version='0.1.0',  # 패키지 버전
    author='Your Name',  # 저자 이름
    author_email='your.email@example.com',  # 저자 이메일
    description='A framework for simulating manufacturing processes.',  # 패키지 설명
    long_description=open('README.md').read(),  # README 파일 내용
    long_description_content_type='text/markdown',  # 내용 형식
    url='https://github.com/yourusername/manufacturing-simulation-framework',  # 프로젝트 URL
    packages=find_packages(where='src'),  # src 디렉토리 내의 패키지 찾기
    package_dir={'': 'src'},  # 패키지 디렉토리 설정
    install_requires=[  # 필요한 패키지 목록
        'simpy',  # 시뮬레이션을 위한 simpy 패키지
        # 추가적인 패키지를 여기에 나열
    ],
    classifiers=[  # 패키지 분류
        'Programming Language :: Python :: 3',  # Python 3 지원
        'License :: OSI Approved :: MIT License',  # 라이센스 정보
        'Operating System :: OS Independent',  # 운영 체제 독립성
    ],
    python_requires='>=3.6',  # 필요한 Python 버전
)