#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""AGV 구성 테스트 스크립트"""

import os
import sys

# 프로젝트 루트를 파이썬 모듈 검색 경로에 추가
project_root = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, project_root)

try:
    from scenario.scenario import create_refrigerator_scenario
    print("모듈 임포트 성공")
    
    data = create_refrigerator_scenario()
    print("시나리오 생성 완료")
    
    print("반환된 데이터:")
    print(f"- env: {data['env']}")
    print(f"- engine: {data['engine']}")
    print(f"- workflow: {data['workflow']}")
    
except Exception as e:
    print(f"오류 발생: {e}")
    import traceback
    traceback.print_exc()
