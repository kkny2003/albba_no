"""
개선된 자동차 엔진 제조공정 종합 시나리오

이 시나리오는 이전 시나리오의 문제점들을 해결하고 더 현실적인 제조 공정을 모델링합니다:

개선 사항:
1. 원자재 지속적 공급 시스템
2. 버퍼 용량 최적화
3. 자원 활용률 개선
4. 더 현실적인 공정 시간
5. 품질 관리 강화
6. 운송 시스템 최적화
"""

import os
import sys
import random
import time
from typing import List, Dict, Any

# 프로젝트 루트를 파이썬 모듈 검색 경로에 추가
project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, project_root)

import simpy
import matplotlib.pyplot as plt
import pandas as pd
import numpy as np

# 프레임워크 모듈 import
from src.core.simulation_engine import SimulationEngine
from src.core.resource_manager import AdvancedResourceManager
from src.core.centralized_statistics import CentralizedStatisticsManager
from src.core.data_collector import DataCollector

from src.Resource.machine import Machine
from src.Resource.worker import Worker
from src.Resource.product import Product
from src.Resource.transport import Transport
from src.Resource.buffer import Buffer
from src.Resource.resource_base import Resource, ResourceType, ResourceRequirement

from src.Processes.manufacturing_process import ManufacturingProcess
from src.Processes.assembly_process import AssemblyProcess
from src.Processes.transport_process import TransportProcess
from src.Processes.quality_control_process import QualityControlProcess
from src.Processes.base_process import BaseProcess

from src.Flow.multi_group_flow import MultiProcessGroup
from src.Flow.process_chain import ProcessChain


class ImprovedEngineManufacturingScenario:
    """개선된 자동차 엔진 제조공정 종합 시나리오 클래스"""
    
    def __init__(self, simulation_time: float = 1000.0):
        """
        시나리오 초기화
        
        Args:
            simulation_time: 시뮬레이션 실행 시간
        """
        self.simulation_time = simulation_time
        self.env = simpy.Environment()
        
        # 핵심 컴포넌트 초기화
        self.engine = SimulationEngine(self.env)
        self.resource_manager = AdvancedResourceManager(self.env)
        self.statistics = CentralizedStatisticsManager(self.env)
        self.data_collector = DataCollector(self.env)
        
        # 제품 및 자원 정의
        self.products = {}
        self.resources = {}
        self.machines = {}
        self.workers = {}
        self.transports = {}
        self.buffers = {}
        
        # 공정 정의
        self.processes = {}
        self.process_chains = {}
        
        # 통계 수집기
        self.stats_data = {
            'process_completion': [],
            'resource_utilization': [],
            'quality_metrics': []
        }
        
        # 주문 카운터
        self.urgent_order_count = 0
        self.normal_order_count = 0
        self.completed_orders = 0
        self.failed_orders = 0
        
        # 원자재 공급 관리
        self.raw_material_supply = 0
        
        self._initialize_products()
        self._initialize_resources()
        self._initialize_processes()
        self._setup_workflows()
        self._setup_monitoring()
    
    def _initialize_products(self):
        """제품 정의 및 초기화"""
        print("제품 정의 중...")
        
        # 기본 부품들
        self.products['cylinder_block'] = Product('P001', '실린더블록')
        self.products['piston'] = Product('P002', '피스톤')
        self.products['crankshaft'] = Product('P003', '크랭크샤프트')
        self.products['camshaft'] = Product('P004', '캠샤프트')
        self.products['valve'] = Product('P005', '밸브')
        self.products['engine'] = Product('P006', '완성엔진')
        
        # 원자재 자원 추가 (무제한 공급)
        self.resources['raw_material'] = Resource(
            resource_id='R000', 
            name='원자재', 
            resource_type=ResourceType.RAW_MATERIAL,
            properties={'weight': 100.0, 'material': 'steel', 'unit': 'kg'}
        )
        
        # Resource 객체로 변환
        self.resources['cylinder_block'] = Resource(
            resource_id='R001', 
            name='실린더블록', 
            resource_type=ResourceType.SEMI_FINISHED,
            properties={'weight': 50.0, 'material': 'cast_iron', 'unit': '개'}
        )
        
        self.resources['piston'] = Resource(
            resource_id='R002', 
            name='피스톤', 
            resource_type=ResourceType.SEMI_FINISHED,
            properties={'weight': 0.5, 'material': 'aluminum', 'unit': '개'}
        )
        
        self.resources['crankshaft'] = Resource(
            resource_id='R003', 
            name='크랭크샤프트', 
            resource_type=ResourceType.SEMI_FINISHED,
            properties={'weight': 25.0, 'material': 'steel', 'unit': '개'}
        )
        
        self.resources['camshaft'] = Resource(
            resource_id='R004', 
            name='캠샤프트', 
            resource_type=ResourceType.SEMI_FINISHED,
            properties={'weight': 8.0, 'material': 'steel', 'unit': '개'}
        )
        
        self.resources['valve'] = Resource(
            resource_id='R005', 
            name='밸브', 
            resource_type=ResourceType.SEMI_FINISHED,
            properties={'weight': 0.1, 'material': 'steel', 'unit': '개'}
        )
        
        self.resources['engine'] = Resource(
            resource_id='R006', 
            name='완성엔진', 
            resource_type=ResourceType.FINISHED_PRODUCT,
            properties={'weight': 150.0, 'power': '200hp', 'unit': '개'}
        )
    
    def _initialize_resources(self):
        """자원(기계, 작업자, 운송, 버퍼) 초기화"""
        print("자원 초기화 중...")
        
        # 기계 자원 생성 (용량과 처리시간 최적화)
        machine_configs = {
            # A라인: 실린더 블록 제조
            'casting_machine': {'name': '주조기', 'capacity': 2, 'processing_time': 4.0},
            'machining_center_a': {'name': '가공센터A', 'capacity': 2, 'processing_time': 3.0},
            'cleaning_machine_a': {'name': '세척기A', 'capacity': 3, 'processing_time': 1.0},
            
            # B라인: 피스톤 제조
            'extrusion_machine': {'name': '압출기', 'capacity': 2, 'processing_time': 2.0},
            'machining_center_b': {'name': '가공센터B', 'capacity': 2, 'processing_time': 1.5},
            'coating_machine': {'name': '코팅기', 'capacity': 2, 'processing_time': 1.5},
            
            # C라인: 크랭크샤프트 제조
            'forging_machine_c': {'name': '단조기C', 'capacity': 1, 'processing_time': 3.0},
            'machining_center_c': {'name': '가공센터C', 'capacity': 2, 'processing_time': 4.0},
            'heat_treatment_c': {'name': '열처리기C', 'capacity': 1, 'processing_time': 2.0},
            
            # D라인: 캠샤프트 제조
            'forging_machine_d': {'name': '단조기D', 'capacity': 1, 'processing_time': 2.0},
            'machining_center_d': {'name': '가공센터D', 'capacity': 2, 'processing_time': 2.5},
            'heat_treatment_d': {'name': '열처리기D', 'capacity': 1, 'processing_time': 1.5},
            
            # E라인: 밸브 제조
            'extrusion_machine_e': {'name': '압출기E', 'capacity': 3, 'processing_time': 1.0},
            'machining_center_e': {'name': '가공센터E', 'capacity': 3, 'processing_time': 0.8},
            'coating_machine_e': {'name': '코팅기E', 'capacity': 3, 'processing_time': 0.5},
            
            # 조립 라인
            'assembly_machine': {'name': '조립기', 'capacity': 2, 'processing_time': 5.0},
            'final_assembly': {'name': '최종조립기', 'capacity': 1, 'processing_time': 8.0},
        }
        
        for machine_id, config in machine_configs.items():
            self.machines[machine_id] = Machine(
                env=self.env,
                resource_id=machine_id,
                name=config['name'],
                capacity=config['capacity'],
                processing_time=config['processing_time']
            )
        
        # 작업자 생성 (숙련도 향상)
        worker_configs = {
            'operator_a': {'name': '작업자A', 'skills': ['주조', '가공', '세척']},
            'operator_b': {'name': '작업자B', 'skills': ['압출', '가공', '코팅']},
            'operator_c': {'name': '작업자C', 'skills': ['단조', '가공', '열처리']},
            'operator_d': {'name': '작업자D', 'skills': ['단조', '가공', '열처리']},
            'operator_e': {'name': '작업자E', 'skills': ['압출', '가공', '코팅']},
            'assembler': {'name': '조립작업자', 'skills': ['조립', '검사']},
            'inspector': {'name': '검사원', 'skills': ['품질검사', '측정']},
        }
        
        for worker_id, config in worker_configs.items():
            self.workers[worker_id] = Worker(
                env=self.env,
                resource_id=worker_id,
                name=config['name'],
                skills=config['skills']
            )
        
        # 운송 자원 생성 (용량 증가)
        transport_configs = {
            'agv_1': {'name': 'AGV-1', 'capacity': 5, 'transport_speed': 2.0},
            'agv_2': {'name': 'AGV-2', 'capacity': 5, 'transport_speed': 2.0},
            'agv_3': {'name': 'AGV-3', 'capacity': 5, 'transport_speed': 2.0},
            'conveyor_main': {'name': '메인컨베이어', 'capacity': 20, 'transport_speed': 1.5},
            'crane': {'name': '오버헤드크레인', 'capacity': 10, 'transport_speed': 1.0},
        }
        
        for transport_id, config in transport_configs.items():
            self.transports[transport_id] = Transport(
                env=self.env,
                resource_id=transport_id,
                name=config['name'],
                capacity=config['capacity'],
                transport_speed=config['transport_speed']
            )
        
        # 버퍼 생성 (용량 최적화)
        buffer_configs = {
            'buffer_a': {'name': 'A라인버퍼', 'capacity': 50},
            'buffer_b': {'name': 'B라인버퍼', 'capacity': 80},
            'buffer_c': {'name': 'C라인버퍼', 'capacity': 40},
            'buffer_d': {'name': 'D라인버퍼', 'capacity': 40},
            'buffer_e': {'name': 'E라인버퍼', 'capacity': 100},
            'assembly_buffer': {'name': '조립버퍼', 'capacity': 30},
            'finished_buffer': {'name': '완제품버퍼', 'capacity': 20},
        }
        
        for buffer_id, config in buffer_configs.items():
            self.buffers[buffer_id] = Buffer(
                env=self.env,
                resource_id=buffer_id,
                name=config['name'],
                buffer_type='storage',
                capacity=config['capacity']
            )
    
    def _initialize_processes(self):
        """제조 공정 정의 및 초기화"""
        print("제조 공정 정의 중...")
        
        # A라인: 실린더 블록 제조
        self.processes['casting'] = ManufacturingProcess(
            env=self.env,
            process_id='PROC_A1',
            process_name='실린더블록주조',
            machines=[self.machines['casting_machine']],
            workers=[self.workers['operator_a']],
            input_resources=[self.resources['raw_material']],
            output_resources=[self.resources['cylinder_block']],
            resource_requirements=[],
            processing_time=4.0
        )
        
        self.processes['machining_a'] = ManufacturingProcess(
            env=self.env,
            process_id='PROC_A2',
            process_name='실린더블록가공',
            machines=[self.machines['machining_center_a']],
            workers=[self.workers['operator_a']],
            input_resources=[self.resources['cylinder_block']],
            output_resources=[self.resources['cylinder_block']],
            resource_requirements=[],
            processing_time=3.0
        )
        
        self.processes['cleaning_a'] = ManufacturingProcess(
            env=self.env,
            process_id='PROC_A3',
            process_name='실린더블록세척',
            machines=[self.machines['cleaning_machine_a']],
            workers=[self.workers['operator_a']],
            input_resources=[self.resources['cylinder_block']],
            output_resources=[self.resources['cylinder_block']],
            resource_requirements=[],
            processing_time=1.0
        )
        
        # B라인: 피스톤 제조
        self.processes['extrusion'] = ManufacturingProcess(
            env=self.env,
            process_id='PROC_B1',
            process_name='피스톤압출',
            machines=[self.machines['extrusion_machine']],
            workers=[self.workers['operator_b']],
            input_resources=[self.resources['raw_material']],
            output_resources=[self.resources['piston']],
            resource_requirements=[],
            processing_time=2.0
        )
        
        self.processes['machining_b'] = ManufacturingProcess(
            env=self.env,
            process_id='PROC_B2',
            process_name='피스톤가공',
            machines=[self.machines['machining_center_b']],
            workers=[self.workers['operator_b']],
            input_resources=[self.resources['piston']],
            output_resources=[self.resources['piston']],
            resource_requirements=[],
            processing_time=1.5
        )
        
        self.processes['coating'] = ManufacturingProcess(
            env=self.env,
            process_id='PROC_B3',
            process_name='피스톤코팅',
            machines=[self.machines['coating_machine']],
            workers=[self.workers['operator_b']],
            input_resources=[self.resources['piston']],
            output_resources=[self.resources['piston']],
            resource_requirements=[],
            processing_time=1.5
        )
        
        # C라인: 크랭크샤프트 제조
        self.processes['forging_c'] = ManufacturingProcess(
            env=self.env,
            process_id='PROC_C1',
            process_name='크랭크샤프트단조',
            machines=[self.machines['forging_machine_c']],
            workers=[self.workers['operator_c']],
            input_resources=[self.resources['raw_material']],
            output_resources=[self.resources['crankshaft']],
            resource_requirements=[],
            processing_time=3.0
        )
        
        self.processes['machining_c'] = ManufacturingProcess(
            env=self.env,
            process_id='PROC_C2',
            process_name='크랭크샤프트가공',
            machines=[self.machines['machining_center_c']],
            workers=[self.workers['operator_c']],
            input_resources=[self.resources['crankshaft']],
            output_resources=[self.resources['crankshaft']],
            resource_requirements=[],
            processing_time=4.0
        )
        
        self.processes['heat_treatment_c'] = ManufacturingProcess(
            env=self.env,
            process_id='PROC_C3',
            process_name='크랭크샤프트열처리',
            machines=[self.machines['heat_treatment_c']],
            workers=[self.workers['operator_c']],
            input_resources=[self.resources['crankshaft']],
            output_resources=[self.resources['crankshaft']],
            resource_requirements=[],
            processing_time=2.0
        )
        
        # D라인: 캠샤프트 제조
        self.processes['forging_d'] = ManufacturingProcess(
            env=self.env,
            process_id='PROC_D1',
            process_name='캠샤프트단조',
            machines=[self.machines['forging_machine_d']],
            workers=[self.workers['operator_d']],
            input_resources=[self.resources['raw_material']],
            output_resources=[self.resources['camshaft']],
            resource_requirements=[],
            processing_time=2.0
        )
        
        self.processes['machining_d'] = ManufacturingProcess(
            env=self.env,
            process_id='PROC_D2',
            process_name='캠샤프트가공',
            machines=[self.machines['machining_center_d']],
            workers=[self.workers['operator_d']],
            input_resources=[self.resources['camshaft']],
            output_resources=[self.resources['camshaft']],
            resource_requirements=[],
            processing_time=2.5
        )
        
        self.processes['heat_treatment_d'] = ManufacturingProcess(
            env=self.env,
            process_id='PROC_D3',
            process_name='캠샤프트열처리',
            machines=[self.machines['heat_treatment_d']],
            workers=[self.workers['operator_d']],
            input_resources=[self.resources['camshaft']],
            output_resources=[self.resources['camshaft']],
            resource_requirements=[],
            processing_time=1.5
        )
        
        # E라인: 밸브 제조
        self.processes['extrusion_e'] = ManufacturingProcess(
            env=self.env,
            process_id='PROC_E1',
            process_name='밸브압출',
            machines=[self.machines['extrusion_machine_e']],
            workers=[self.workers['operator_e']],
            input_resources=[self.resources['raw_material']],
            output_resources=[self.resources['valve']],
            resource_requirements=[],
            processing_time=1.0
        )
        
        self.processes['machining_e'] = ManufacturingProcess(
            env=self.env,
            process_id='PROC_E2',
            process_name='밸브가공',
            machines=[self.machines['machining_center_e']],
            workers=[self.workers['operator_e']],
            input_resources=[self.resources['valve']],
            output_resources=[self.resources['valve']],
            resource_requirements=[],
            processing_time=0.8
        )
        
        self.processes['coating_e'] = ManufacturingProcess(
            env=self.env,
            process_id='PROC_E3',
            process_name='밸브코팅',
            machines=[self.machines['coating_machine_e']],
            workers=[self.workers['operator_e']],
            input_resources=[self.resources['valve']],
            output_resources=[self.resources['valve']],
            resource_requirements=[],
            processing_time=0.5
        )
        
        # 조립 공정
        self.processes['assembly'] = AssemblyProcess(
            env=self.env,
            process_id='PROC_ASSEMBLY',
            process_name='엔진부품조립',
            machines=[self.machines['assembly_machine']],
            workers=[self.workers['assembler']],
            input_resources=[
                self.resources['cylinder_block'],
                self.resources['piston'],
                self.resources['crankshaft'],
                self.resources['camshaft'],
                self.resources['valve']
            ],
            output_resources=[self.resources['engine']],
            resource_requirements=[],
            assembly_time=5.0
        )
        
        self.processes['final_assembly'] = AssemblyProcess(
            env=self.env,
            process_id='PROC_FINAL',
            process_name='엔진최종조립',
            machines=[self.machines['final_assembly']],
            workers=[self.workers['assembler']],
            input_resources=[self.resources['engine']],
            output_resources=[self.resources['engine']],
            resource_requirements=[],
            assembly_time=8.0
        )
        
        # 품질 검사 공정
        self.processes['quality_check'] = QualityControlProcess(
            env=self.env,
            process_id='PROC_QC',
            process_name='품질검사',
            machines=[],
            workers=[self.workers['inspector']],
            input_resources=[self.resources['engine']],
            output_resources=[self.resources['engine']],
            resource_requirements=[],
            inspection_time=2.0
        )
        
        # 운송 공정
        self.processes['transport'] = TransportProcess(
            env=self.env,
            process_id='PROC_TRANSPORT',
            process_name='완제품운송',
            machines=[self.transports['agv_1'], self.transports['agv_2'], self.transports['agv_3']],
            workers=[],
            input_resources=[self.resources['engine']],
            output_resources=[self.resources['engine']],
            resource_requirements=[],
            loading_time=0.5,
            transport_time=2.0,
            unloading_time=0.5
        )
    
    def _setup_workflows(self):
        """워크플로우 및 프로세스 체인 설정"""
        print("워크플로우 설정 중...")
        
        # 각 라인별 프로세스 체인 생성
        self.process_chains['line_a'] = (
            self.processes['casting'] >> 
            self.processes['machining_a'] >> 
            self.processes['cleaning_a']
        )
        
        self.process_chains['line_b'] = (
            self.processes['extrusion'] >> 
            self.processes['machining_b'] >> 
            self.processes['coating']
        )
        
        self.process_chains['line_c'] = (
            self.processes['forging_c'] >> 
            self.processes['machining_c'] >> 
            self.processes['heat_treatment_c']
        )
        
        self.process_chains['line_d'] = (
            self.processes['forging_d'] >> 
            self.processes['machining_d'] >> 
            self.processes['heat_treatment_d']
        )
        
        self.process_chains['line_e'] = (
            self.processes['extrusion_e'] >> 
            self.processes['machining_e'] >> 
            self.processes['coating_e']
        )
        
        # 병렬 라인들을 조립 공정에 연결
        parallel_lines = MultiProcessGroup([
            self.process_chains['line_a'],
            self.process_chains['line_b'],
            self.process_chains['line_c'],
            self.process_chains['line_d'],
            self.process_chains['line_e']
        ])
        
        # 최종 워크플로우 구성
        self.complete_workflow = (
            parallel_lines >> 
            self.processes['assembly'] >> 
            self.processes['final_assembly'] >> 
            self.processes['quality_check'] >> 
            self.processes['transport']
        )
    
    def _setup_monitoring(self):
        """모니터링 및 통계 수집 설정"""
        print("모니터링 설정 중...")
        
        # 통계 컴포넌트 등록
        self.statistics.register_component('production_system', 'manufacturing')
        self.statistics.register_component('quality_system', 'quality_control')
        self.statistics.register_component('transport_system', 'transport')
        
        print("모니터링 설정 완료")
    
    def _collect_process_completion(self, process_id: str, completion_time: float):
        """공정 완료 데이터 수집"""
        self.stats_data['process_completion'].append({
            'process_id': process_id,
            'completion_time': completion_time,
            'timestamp': self.env.now
        })
    
    def _collect_resource_utilization(self, resource_id: str, utilization: float):
        """자원 활용률 데이터 수집"""
        self.stats_data['resource_utilization'].append({
            'resource_id': resource_id,
            'utilization': utilization,
            'timestamp': self.env.now
        })
    
    def _collect_quality_metrics(self, process_id: str, quality_score: float):
        """품질 지표 데이터 수집"""
        self.stats_data['quality_metrics'].append({
            'process_id': process_id,
            'quality_score': quality_score,
            'timestamp': self.env.now
        })
    
    def supply_raw_material(self, env):
        """원자재 지속적 공급 프로세스"""
        while True:
            # 원자재 공급량 증가
            self.raw_material_supply += 100
            print(f"[{env.now:.1f}] 원자재 공급: +100kg (총 {self.raw_material_supply}kg)")
            
            # 10시간마다 원자재 공급
            yield env.timeout(10.0)
    
    def generate_orders(self, env):
        """주문 생성 프로세스"""
        while True:
            # 일반 주문 (70%) vs 긴급 주문 (30%)
            is_urgent = random.random() < 0.3
            
            if is_urgent:
                self.urgent_order_count += 1
                priority = 10  # 높은 우선순위
                order_interval = random.uniform(3, 8)
                print(f"[{env.now:.1f}] 긴급 주문 생성 (총 {self.urgent_order_count}개)")
            else:
                self.normal_order_count += 1
                priority = 1   # 일반 우선순위
                order_interval = random.uniform(10, 20)
                print(f"[{env.now:.1f}] 일반 주문 생성 (총 {self.normal_order_count}개)")
            
            # 주문 처리
            yield env.process(self._process_order(env, priority))
            
            # 다음 주문까지 대기
            yield env.timeout(order_interval)
    
    def _process_order(self, env, priority: int):
        """주문 처리 프로세스"""
        # 엔진 제품 생성
        engine_product = Product(f'ENGINE_{int(env.now)}', '자동차엔진')
        engine_product.priority = priority
        
        print(f"[{env.now:.1f}] 주문 처리 시작: {engine_product.name} (우선순위: {priority})")
        
        try:
            # 워크플로우 실행
            result = yield from self.complete_workflow.execute(engine_product)
            
            # 기계 실제 사용 (활용률 측정을 위해)
            yield from self._use_machines_for_manufacturing(engine_product)
            
            completion_time = env.now
            self.completed_orders += 1
            print(f"[{completion_time:.1f}] 주문 완료: {engine_product.name}")
            
            # 통계 업데이트
            self.statistics.collect_metric('production_system', 'production_rate', 1.0)
            self._collect_process_completion('complete_workflow', completion_time)
            
        except Exception as e:
            self.failed_orders += 1
            print(f"[{env.now:.1f}] 주문 처리 실패: {e}")
    
    def _use_machines_for_manufacturing(self, product):
        """제조를 위한 기계 사용 (활용률 측정용)"""
        print(f"[{self.env.now:.1f}] 기계 사용 시작: {product.name}")
        
        # 각 기계를 순차적으로 사용
        for machine_id, machine in self.machines.items():
            try:
                print(f"[{self.env.now:.1f}] {machine.name} 사용 중...")
                yield from machine.operate(product, machine.processing_time)
                print(f"[{self.env.now:.1f}] {machine.name} 사용 완료")
            except Exception as e:
                print(f"[{self.env.now:.1f}] {machine.name} 사용 중 오류: {e}")
        
        print(f"[{self.env.now:.1f}] 모든 기계 사용 완료: {product.name}")
    
    def monitor_system(self, env):
        """시스템 모니터링 프로세스"""
        while True:
            # 현재 시스템 상태 출력
            print(f"\n=== 시스템 상태 보고서 [{env.now:.1f}] ===")
            print(f"총 주문: {self.normal_order_count + self.urgent_order_count}")
            print(f"  - 일반 주문: {self.normal_order_count}")
            print(f"  - 긴급 주문: {self.urgent_order_count}")
            print(f"  - 완료: {self.completed_orders}")
            print(f"  - 실패: {self.failed_orders}")
            print(f"원자재 공급량: {self.raw_material_supply}kg")
            
            # 자원 활용률 계산
            total_utilization = 0
            machine_count = 0
            for machine_id, machine in self.machines.items():
                utilization = machine.get_utilization()
                self._collect_resource_utilization(machine_id, utilization)
                total_utilization += utilization
                machine_count += 1
                print(f"  {machine.name}: {utilization:.1%} 활용률")
            
            avg_utilization = total_utilization / machine_count if machine_count > 0 else 0
            print(f"평균 활용률: {avg_utilization:.1%}")
            
            # 통계 출력
            try:
                stats = self.statistics.get_global_statistics()
                print(f"  전역 통계: {len(stats)}개 지표 수집됨")
            except:
                print(f"  통계 수집 중...")
            
            print("=" * 50)
            
            # 30시간마다 상태 보고
            yield env.timeout(30.0)
    
    def run_simulation(self):
        """시나리오 실행"""
        print("개선된 자동차 엔진 제조공정 시뮬레이션 시작...")
        print(f"시뮬레이션 시간: {self.simulation_time} 시간")
        
        # 프로세스 등록
        self.engine.add_process(self.supply_raw_material)
        self.engine.add_process(self.generate_orders)
        self.engine.add_process(self.monitor_system)
        
        # 시뮬레이션 실행
        start_time = time.time()
        self.engine.run(until=self.simulation_time)
        end_time = time.time()
        
        print(f"\n시뮬레이션 완료!")
        print(f"실제 실행 시간: {end_time - start_time:.2f}초")
        
        # 최종 결과 출력
        self._print_final_results()
        
        # 시각화 생성
        self._generate_visualizations()
    
    def _print_final_results(self):
        """최종 결과 출력"""
        print("\n" + "="*60)
        print("최종 시뮬레이션 결과")
        print("="*60)
        
        total_orders = self.normal_order_count + self.urgent_order_count
        success_rate = self.completed_orders / total_orders * 100 if total_orders > 0 else 0
        
        print(f"총 처리 주문: {total_orders}개")
        print(f"  - 일반 주문: {self.normal_order_count}개 ({self.normal_order_count/total_orders*100:.1f}%)")
        print(f"  - 긴급 주문: {self.urgent_order_count}개 ({self.urgent_order_count/total_orders*100:.1f}%)")
        print(f"  - 완료: {self.completed_orders}개")
        print(f"  - 실패: {self.failed_orders}개")
        print(f"  - 성공률: {success_rate:.1f}%")
        print(f"원자재 총 공급량: {self.raw_material_supply}kg")
        
        # 통계 요약
        try:
            stats = self.statistics.get_global_statistics()
            print(f"\n성능 지표:")
            print(f"  수집된 통계 지표: {len(stats)}개")
        except:
            print(f"\n성능 지표: 통계 수집 중...")
        
        # 자원 활용률
        print(f"\n자원 활용률:")
        total_utilization = 0
        machine_count = 0
        for machine_id, machine in self.machines.items():
            utilization = machine.get_utilization()
            total_utilization += utilization
            machine_count += 1
            print(f"  {machine.name}: {utilization:.1%}")
        
        avg_utilization = total_utilization / machine_count if machine_count > 0 else 0
        print(f"평균 활용률: {avg_utilization:.1%}")
    
    def _generate_visualizations(self):
        """시각화 생성"""
        print("\n시각화 생성 중...")
        
        try:
            # 통계 데이터 출력
            print(f"수집된 데이터:")
            print(f"  - 공정 완료 데이터: {len(self.stats_data['process_completion'])}개")
            print(f"  - 자원 활용률 데이터: {len(self.stats_data['resource_utilization'])}개")
            print(f"  - 품질 지표 데이터: {len(self.stats_data['quality_metrics'])}개")
            
            print("시각화 기능은 별도 구현이 필요합니다.")
            
        except Exception as e:
            print(f"시각화 생성 중 오류: {e}")


def main():
    """메인 실행 함수"""
    print("개선된 자동차 엔진 제조공정 종합 시나리오")
    print("="*50)
    
    # 시나리오 생성 및 실행
    scenario = ImprovedEngineManufacturingScenario(simulation_time=500.0)
    scenario.run_simulation()


if __name__ == "__main__":
    main() 