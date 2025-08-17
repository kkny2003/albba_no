"""
간단하고 강력한 로깅 프레임워크

이 모듈은 시뮬레이션 로그를 마크다운 파일로 저장하는 간단하고 효율적인 프레임워크를 제공합니다.
기존의 복잡한 로깅 코드를 간단한 데코레이터나 컨텍스트 매니저로 대체할 수 있습니다.

주요 기능:
- LogManager: 로그 파일 관리
- LogContext: 컨텍스트 매니저 (with 문 사용)
- LogFormatter: 다양한 포맷 지원
- log_execution: 데코레이터
- quick_log: 빠른 로그 저장
- capture_output: 출력 캡처
- save_output_to_md: MD 파일 저장
"""

import os
import sys
import io
import time
import traceback
from datetime import datetime
from contextlib import contextmanager
from typing import Dict, Any, Optional, List
import functools


class LogFormatter:
    """로그 포맷터 - 다양한 형식으로 로그를 포맷팅"""
    
    def __init__(self, format_type: str = "basic_md"):
        self.format_type = format_type
    
    def format_basic_md(self, name: str, content: str, metadata: Dict[str, Any] = None) -> str:
        """기본 마크다운 포맷"""
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        
        md_content = f"# {name}\n\n"
        md_content += f"**실행 시간**: {timestamp}\n\n"
        
        if metadata:
            md_content += "## 메타데이터\n\n"
            for key, value in metadata.items():
                md_content += f"- **{key}**: {value}\n"
            md_content += "\n"
        
        md_content += "## 로그 내용\n\n"
        md_content += "```\n"
        md_content += content
        md_content += "\n```\n"
        
        return md_content
    
    def format_detailed_md(self, name: str, content: str, metadata: Dict[str, Any] = None) -> str:
        """상세 마크다운 포맷"""
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        
        md_content = f"# {name} - 상세 로그\n\n"
        md_content += f"**실행 시간**: {timestamp}\n\n"
        
        if metadata:
            md_content += "## 메타데이터\n\n"
            md_content += "| 항목 | 값 |\n"
            md_content += "|------|----|\n"
            for key, value in metadata.items():
                md_content += f"| {key} | {value} |\n"
            md_content += "\n"
        
        md_content += "## 실행 로그\n\n"
        md_content += "```\n"
        md_content += content
        md_content += "\n```\n"
        
        md_content += "## 요약\n\n"
        md_content += f"- 실행 완료 시간: {timestamp}\n"
        md_content += f"- 로그 길이: {len(content)} 문자\n"
        
        return md_content
    
    def format_simple_text(self, name: str, content: str, metadata: Dict[str, Any] = None) -> str:
        """간단한 텍스트 포맷"""
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        
        text_content = f"=== {name} ===\n"
        text_content += f"실행 시간: {timestamp}\n\n"
        
        if metadata:
            text_content += "메타데이터:\n"
            for key, value in metadata.items():
                text_content += f"  {key}: {value}\n"
            text_content += "\n"
        
        text_content += "로그 내용:\n"
        text_content += content
        text_content += "\n"
        
        return text_content
    
    def format(self, name: str, content: str, metadata: Dict[str, Any] = None) -> str:
        """포맷 타입에 따라 로그 포맷팅"""
        if self.format_type == "basic_md":
            return self.format_basic_md(name, content, metadata)
        elif self.format_type == "detailed_md":
            return self.format_detailed_md(name, content, metadata)
        elif self.format_type == "simple_text":
            return self.format_simple_text(name, content, metadata)
        else:
            return self.format_basic_md(name, content, metadata)


class LogManager:
    """로그 매니저 - 로그 파일 관리 및 저장"""
    
    def __init__(self, log_dir: str = "log", filename_pattern: str = "{name}_{timestamp}.md", 
                 format_type: str = "basic_md"):
        self.log_dir = log_dir
        self.filename_pattern = filename_pattern
        self.formatter = LogFormatter(format_type)
        
        # 로그 디렉토리 생성
        os.makedirs(log_dir, exist_ok=True)
    
    def save_log(self, name: str, content: str, metadata: Dict[str, Any] = None) -> str:
        """로그를 파일로 저장"""
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = self.filename_pattern.format(name=name, timestamp=timestamp)
        filepath = os.path.join(self.log_dir, filename)
        
        formatted_content = self.formatter.format(name, content, metadata)
        
        with open(filepath, 'w', encoding='utf-8') as f:
            f.write(formatted_content)
        
        return filepath


class LogContext:
    """로그 컨텍스트 매니저 - with 문으로 로그 캡처"""
    
    def __init__(self, name: str, log_manager: Optional[LogManager] = None, 
                 metadata: Dict[str, Any] = None):
        self.name = name
        self.log_manager = log_manager or LogManager()
        self.metadata = metadata or {}
        self.output_capture = None
        self.original_stdout = None
    
    def __enter__(self):
        """컨텍스트 진입 - 출력 캡처 시작"""
        self.output_capture = io.StringIO()
        self.original_stdout = sys.stdout
        sys.stdout = self.output_capture
        return self
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        """컨텍스트 종료 - 출력 캡처 및 로그 저장"""
        # 원래 stdout 복원
        sys.stdout = self.original_stdout
        
        # 캡처된 출력 가져오기
        captured_output = self.output_capture.getvalue()
        self.output_capture.close()
        
        # 예외 정보 추가
        if exc_type:
            error_info = f"\n\n## 오류 발생\n\n"
            error_info += f"**오류 타입**: {exc_type.__name__}\n\n"
            error_info += f"**오류 메시지**: {exc_val}\n\n"
            error_info += f"**스택 트레이스**:\n```\n{traceback.format_exc()}\n```\n"
            captured_output += error_info
        
        # 로그 저장
        filepath = self.log_manager.save_log(self.name, captured_output, self.metadata)
        
        # 캡처된 출력을 다시 출력
        print(captured_output)
        
        print(f"\n[로그 저장됨] {filepath}")
        
        return False  # 예외를 다시 발생시킴


def log_execution(name: str, log_manager: Optional[LogManager] = None, 
                 metadata: Dict[str, Any] = None):
    """함수 실행 로깅 데코레이터"""
    def decorator(func):
        @functools.wraps(func)
        def wrapper(*args, **kwargs):
            with LogContext(name, log_manager, metadata):
                return func(*args, **kwargs)
        return wrapper
    return decorator


def quick_log(name: str, content: str, log_dir: str = "log") -> str:
    """빠른 로그 저장 - 간단한 사용법"""
    log_manager = LogManager(log_dir)
    return log_manager.save_log(name, content)


@contextmanager
def capture_output():
    """출력 캡처 컨텍스트 매니저"""
    output_capture = io.StringIO()
    original_stdout = sys.stdout
    try:
        sys.stdout = output_capture
        yield output_capture
    finally:
        sys.stdout = original_stdout
        output_capture.close()


def save_output_to_md(name: str, content: str, log_dir: str = "log") -> str:
    """출력을 MD 파일로 저장"""
    log_manager = LogManager(log_dir)
    return log_manager.save_log(name, content)


# 편의 함수들
def log_simulation(name: str, metadata: Dict[str, Any] = None):
    """시뮬레이션 전용 로깅 데코레이터"""
    return log_execution(name, metadata=metadata)


def log_function(name: str, metadata: Dict[str, Any] = None):
    """함수 전용 로깅 데코레이터"""
    return log_execution(name, metadata=metadata)


# 사용 예제
if __name__ == "__main__":
    # 예제 1: 기본 사용법
    with LogContext("테스트_로깅"):
        print("이것은 테스트 로그입니다.")
        print("여러 줄의 출력을 캡처합니다.")
    
    # 예제 2: 데코레이터 사용법
    @log_execution("함수_테스트")
    def test_function():
        print("함수 내부에서 출력")
        return "성공"
    
    result = test_function()
    
    # 예제 3: 빠른 로그
    quick_log("빠른_테스트", "이것은 빠른 로그 테스트입니다.")
