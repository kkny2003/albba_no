"""
ReportManager 통합 냉장고 제조공정 시뮬레이션 시나리오 (별도 파일)

기존 scenario.py 는 수정하지 않고, 본 파일에서 ReportManager 및 대시보드/리포트
저장 기능을 포함한 확장 시나리오를 제공합니다.

기능 개요:
1. 기존 시나리오 자원 & 공정 구성 재사용 (구조 동일)
2. ReportManager 생성/리소스 & 프로세스 등록
3. 실시간 대시보드 스냅샷 수집 프로세스(reporting_monitor)
4. 시뮬레이션 종료 시: 종합 리포트, 최종 대시보드, 스냅샷 JSON 저장
5. 기존과 동일한 콘솔 로그 캡처 후 MD 저장

사용 방법:
python -m scenario.report_sce  (또는 report_sce.py 직접 실행)

출력물:
- log/refrigerator_simulation_log_*.md
- log/manufacturing_comprehensive_report_*.json
- log/manufacturing_dashboard_final_*.json
- log/manufacturing_dashboard_snapshots_*.json
"""
import os
import sys
import io
import json
from datetime import datetime
import simpy
from typing import Dict, List, Any

# 프로젝트 루트 추가
project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, project_root)

from src.core.simulation_engine import SimulationEngine
from src.core.resource_manager import AdvancedResourceManager
from src.core.report_manager import create_report_manager, setup_default_alert_callbacks
from src.Resource.machine import Machine
from src.Resource.worker import Worker
from src.Resource.transport import Transport
from src.Resource.product import Product
from src.Resource.resource_base import Resource, ResourceType
from src.Processes.manufacturing_process import ManufacturingProcess
from src.Processes.assembly_process import AssemblyProcess
from src.Processes.quality_control_process import QualityControlProcess
from src.Processes.transport_process import TransportProcess
from src.Flow.multi_group_flow import MultiProcessGroup
from src.utils.visualization import VisualizationManager

# ========== 시나리오 구성 함수 ==========

def create_refrigerator_scenario_with_reporting():
    """ReportManager 통합 냉장고 제조공정 시나리오 생성"""
    env = simpy.Environment()
    engine = SimulationEngine(env)
    resource_manager = AdvancedResourceManager(env)
    report_manager = create_report_manager(env, engine.get_centralized_statistics_manager())
    setup_default_alert_callbacks(report_manager)

    # 1. 운송 리소스 관리자 초기 등록
    resource_manager.register_resource("transport", capacity=10, resource_type=ResourceType.TRANSPORT)

    # 2. 자원 (원자재 / 중간 / 완제품)
    side_panel_sheet = Resource('R_SIDE_S', 'SidePanelSheet', ResourceType.RAW_MATERIAL)
    back_sheet = Resource('R_BACK_S', 'BackSheet', ResourceType.RAW_MATERIAL)
    top_cover_sheet = Resource('R_TOP_S', 'TopCoverSheet', ResourceType.RAW_MATERIAL)
    top_support_sheet = Resource('R_SUPPORT_S', 'TopPanelSupportSheet', ResourceType.RAW_MATERIAL)

    side_panel = Resource('R_SIDE_P', 'SidePanel', ResourceType.SEMI_FINISHED)
    back_panel = Resource('R_BACK_P', 'BackPanel', ResourceType.SEMI_FINISHED)
    top_cover = Resource('R_TOP_P', 'TopCover', ResourceType.SEMI_FINISHED)
    top_support = Resource('R_SUPPORT_P', 'TopPanelSupport', ResourceType.SEMI_FINISHED)
    door_shell = Resource('R_DOOR_SHELL', 'DoorShellAssembly', ResourceType.SEMI_FINISHED)
    main_body = Resource('R_MAIN_BODY', 'RefrigeratorMainBody', ResourceType.SEMI_FINISHED)
    hinge = Resource('R_HINGE', 'Hinge', ResourceType.SEMI_FINISHED)
    functional_part = Resource('R_FUNC_PART', 'FunctionalPart', ResourceType.SEMI_FINISHED)
    final_refrigerator = Resource('R_FINAL', 'FinishedRefrigerator', ResourceType.FINISHED_PRODUCT)

    # 3. 설비 / 작업자 / 운송 수단
    press_machines = [Machine(env, f'PRESS_M{i}', f'프레스기계{i}', capacity=1, processing_time=1) for i in range(1, 5)]
    press_workers = [Worker(env, f'PRESS_W{i}', f'프레스작업자{i}', skills=['blanking', 'drawing', 'piercing']) for i in range(1, 5)]
    assembly_robots = [Machine(env, f'ASSEMBLY_R{i}', f'도어조립로봇{i}', capacity=1, processing_time=25) for i in range(1, 5)]
    filling_machines = [Machine(env, f'FILLING_M{i}', f'발포충진기{i}', capacity=1, processing_time=50) for i in range(1, 5)]
    unit2_workers = [Worker(env, f'UNIT2_W{i}', f'Unit2작업자{i}', skills=['assembly', 'filling']) for i in range(1, 5)]
    final_assembly_robots = [Machine(env, f'FINAL_R{i}', f'최종조립로봇{i}', capacity=1, processing_time=20) for i in range(1, 5)]
    inspection_machines = [Machine(env, f'INSPECT_M{i}', f'품질검사기{i}', capacity=1, processing_time=15) for i in range(1, 5)]
    unit3_workers = [Worker(env, f'UNIT3_W{i}', f'Unit3작업자{i}', skills=['final_assembly', 'inspection']) for i in range(1, 5)]
    agv = Transport(env, 'AGV_T', 'AGV', capacity=5, transport_speed=2.0)
    conveyor = Transport(env, 'CONVEYOR_T', '컨베이어', capacity=20, transport_speed=1.0)
    transport_worker = Worker(env, 'TRANSPORT_W', '운송작업자', skills=['transport'])

    # 4. 공정 정의
    press_lines = []
    part_info = [
        ("SidePanel", side_panel_sheet, side_panel), ("BackSheet", back_sheet, back_panel),
        ("TopCover", top_cover_sheet, top_cover), ("TopSupport", top_support_sheet, top_support)
    ]
    for i in range(4):
        p_name, p_in, p_out = part_info[i]
        blanking = ManufacturingProcess(env, f'P_BLANK_{i}', f'{p_name}-Blanking', [press_machines[i]], [press_workers[i]], {p_in.name:1}, {p_out.name:1}, [], 10, resource_manager=resource_manager)
        drawing = ManufacturingProcess(env, f'P_DRAW_{i}', f'{p_name}-Drawing', [press_machines[i]], [press_workers[i]], {p_out.name:1}, {p_out.name:1}, [], 15, resource_manager=resource_manager)
        piercing = ManufacturingProcess(env, f'P_PIERCE_{i}', f'{p_name}-Piercing', [press_machines[i]], [press_workers[i]], {p_out.name:1}, {p_out.name:1}, [], 5, resource_manager=resource_manager)
        press_lines.append(blanking >> drawing >> piercing)
        for proc in [blanking, drawing, piercing]:
            report_manager.register_process(proc.process_id, proc)

    door_assembly = AssemblyProcess(env, 'P_DOOR_ASSY', '도어쉘조립', assembly_robots, unit2_workers,{side_panel.name:1, back_panel.name:1, top_cover.name:1, top_support.name:1},{door_shell.name:1}, [], 25, resource_manager=resource_manager)
    foam_filling = ManufacturingProcess(env, 'P_FOAM', '발포충진', filling_machines, unit2_workers,{door_shell.name:1},{door_shell.name:1}, [], 50, resource_manager=resource_manager)
    for proc in [door_assembly, foam_filling]:
        report_manager.register_process(proc.process_id, proc)

    final_lines = []
    for i in range(4):
        main_assy = AssemblyProcess(env, f'P_MAIN_ASSY_{i}', f'본체조립{i}', [final_assembly_robots[i]],[unit3_workers[i]], {door_shell.name:1, main_body.name:1}, {final_refrigerator.name:1}, [], 20, resource_manager=None)
        hinge_inst = ManufacturingProcess(env, f'P_HINGE_{i}', f'힌지결합{i}', [final_assembly_robots[i]],[unit3_workers[i]], {final_refrigerator.name:1, hinge.name:1}, {final_refrigerator.name:1}, [], 15, resource_manager=None)
        door_inst = ManufacturingProcess(env, f'P_DOOR_INST_{i}', f'도어결합{i}', [final_assembly_robots[i]],[unit3_workers[i]], {final_refrigerator.name:1}, {final_refrigerator.name:1}, [], 15, resource_manager=None)
        func_inst = ManufacturingProcess(env, f'P_FUNC_{i}', f'기능부품결합{i}', [final_assembly_robots[i]],[unit3_workers[i]], {final_refrigerator.name:1, functional_part.name:1}, {final_refrigerator.name:1}, [], 20, resource_manager=None)
        finishing = ManufacturingProcess(env, f'P_FINISH_{i}', f'최종마감{i}', [final_assembly_robots[i]],[unit3_workers[i]], {final_refrigerator.name:1}, {final_refrigerator.name:1}, [], 10, resource_manager=None)
        inspection = QualityControlProcess(env, f'P_INSPECT_{i}', f'품질검사{i}', [inspection_machines[i]],[unit3_workers[i]], {final_refrigerator.name:1}, {final_refrigerator.name:1}, [], 20)
        for proc in [main_assy, hinge_inst, door_inst, func_inst, finishing, inspection]:
            proc.enable_output_blocking_feature(False)
        final_lines.append(main_assy >> hinge_inst >> door_inst >> func_inst >> finishing >> inspection)
        for proc in [main_assy, hinge_inst, door_inst, func_inst, finishing, inspection]:
            report_manager.register_process(proc.process_id, proc)

    transport_to_unit2 = TransportProcess(env, 'T_U1_U2', 'Unit1->2운송', [agv], [transport_worker], {}, {}, [], 1, 5, 1, 1)
    transport_to_unit3 = TransportProcess(env, 'T_U2_U3', 'Unit2->3운송', [conveyor], [transport_worker], {}, {}, [], 1, 10, 1, 1)
    for proc in [transport_to_unit2, transport_to_unit3]:
        report_manager.register_process(proc.process_id, proc)
    resource_manager.register_transport_process("transport_u1_u2", transport_to_unit2)
    resource_manager.register_transport_process("transport_u2_u3", transport_to_unit3)

    unit1_workflow = MultiProcessGroup(press_lines)
    unit2_workflow = door_assembly >> foam_filling
    unit3_workflow = MultiProcessGroup(final_lines)
    complete_workflow = unit1_workflow >> unit2_workflow >> unit3_workflow

    # 리소스 등록
    for m in press_machines + assembly_robots + filling_machines + final_assembly_robots + inspection_machines:
        report_manager.register_resource(m.resource_id, m)
    for w in press_workers + unit2_workers + unit3_workers + [transport_worker]:
        report_manager.register_resource(w.resource_id, w)
    for t in [agv, conveyor]:
        report_manager.register_resource(t.resource_id, t)

    return {
        'env': env,
        'engine': engine,
        'workflow': complete_workflow,
    'report_manager': report_manager,
    'resources': press_machines + assembly_robots + filling_machines + final_assembly_robots + inspection_machines + press_workers + unit2_workers + unit3_workers + [transport_worker] + [agv, conveyor]
    }

# ========== 프로세스 함수 ==========

def production_starter(env, workflow, num_orders=3):
    for i in range(num_orders):
        print(f"\n--- [시간 {env.now:.2f}] 냉장고 생산 주문 {i+1} 시작 ---")
        initial_product = Product(f'ORDER_{i+1}', '생산주문')
        yield from workflow.execute(initial_product)
        print(f"--- [시간 {env.now:.2f}] 냉장고 생산 주문 {i+1} 완료 ---")
        yield env.timeout(10)

def reporting_monitor(env, report_manager, snapshot_interval=100, snapshots=None):
    if snapshots is None:
        snapshots = []
    while True:
        dashboard = report_manager.generate_real_time_dashboard()
        snapshots.append(dashboard)
        print(f"[Report] 실시간 대시보드 스냅샷 저장 (sim time={env.now:.1f})")
        yield env.timeout(snapshot_interval)

def utilization_monitor(env, resources, interval, history_store):
    """주기적으로 각 리소스 get_utilization()/get_availability() 호출하여 기록
    history_store 구조: {resource_id: [(time, utilization), ...]}
    interval: 샘플링 주기 (sim time)
    """
    while True:
        now = env.now
        for r in resources:
            rid = getattr(r, 'resource_id', getattr(r, 'name', 'unknown'))
            util = None
            if hasattr(r, 'get_utilization'):
                try:
                    util = r.get_utilization()
                except Exception:
                    util = None
            if util is None and hasattr(r, 'get_availability'):
                try:
                    util = r.get_availability()
                except Exception:
                    util = None
            if util is not None:
                history_store.setdefault(rid, []).append((now, float(util)))
        yield env.timeout(interval)

# ========== 출력 저장 유틸 ==========

def save_output_to_md(output_text: str):
    log_dir = os.path.join(project_root, 'log')
    os.makedirs(log_dir, exist_ok=True)
    timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
    filename = os.path.join(log_dir, f"refrigerator_simulation_log_{timestamp}.md")
    md_content = f"""# 냉장고 제조공정 시뮬레이션 로그\n\n**시뮬레이션 실행 시간**: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n\n## 시뮬레이션 출력 로그\n{output_text}\n"""
    with open(filename, 'w', encoding='utf-8') as f:
        f.write(md_content)
    print(f"\n✅ 시뮬레이션 로그 저장: {filename}")

def save_reports_to_files(comprehensive_report, final_dashboard, snapshots):
    log_dir = os.path.join(project_root, 'log')
    os.makedirs(log_dir, exist_ok=True)
    timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
    comp_path = os.path.join(log_dir, f"manufacturing_comprehensive_report_{timestamp}.json")
    dash_path = os.path.join(log_dir, f"manufacturing_dashboard_final_{timestamp}.json")
    snap_path = os.path.join(log_dir, f"manufacturing_dashboard_snapshots_{timestamp}.json")
    with open(comp_path, 'w', encoding='utf-8') as f:
        json.dump(comprehensive_report, f, ensure_ascii=False, indent=2)
    with open(dash_path, 'w', encoding='utf-8') as f:
        json.dump(final_dashboard, f, ensure_ascii=False, indent=2)
    with open(snap_path, 'w', encoding='utf-8') as f:
        json.dump(snapshots, f, ensure_ascii=False, indent=2)
    print(f"\n✅ ReportManager 리포트 저장: {comp_path}\n{dash_path}\n{snap_path}")

# ========== 시각화 생성 유틸 ==========

def generate_visualizations(report_manager, comprehensive_report: Dict[str, Any]):
    """시뮬레이션 종료 후 핵심 메트릭 시각화 파일 생성
    - 리소스 가동률 타임라인 (가능한 경우)
    - 프로세스 처리량 / 사이클타임 바차트
    - 알림(Alerts) 심각도 분포 파이차트
    """
    try:
        viz = VisualizationManager(output_dir=os.path.join(project_root, 'visualizations'))

        # 1. 프로세스 분석 섹션 활용
        process_analysis = comprehensive_report.get('process_analysis', {})
        performance_section = process_analysis.get('performance_metrics') if isinstance(process_analysis, dict) else None
        # fallback: process_analysis 자체에 dict로 있을 수 있음
        proc_metrics_container = performance_section or process_analysis
        if isinstance(proc_metrics_container, dict):
            proc_ids = []
            throughputs = []
            cycle_times = []
            for pid, pdata in proc_metrics_container.items():
                if not isinstance(pdata, dict):
                    continue
                # 추정되는 키 이름들 탐색
                th = pdata.get('throughput') or pdata.get('avg_throughput') or pdata.get('throughput_per_time')
                ct = pdata.get('cycle_time') or pdata.get('avg_cycle_time') or pdata.get('mean_cycle_time')
                if th is not None or ct is not None:
                    proc_ids.append(pid)
                    throughputs.append(th if th is not None else 0)
                    cycle_times.append(ct if ct is not None else 0)
            if proc_ids:
                viz.plot_bar_chart(proc_ids, throughputs, title='프로세스 처리량(Throughput)', x_label='Process', y_label='Throughput', save_path='process_throughput.png')
                viz.plot_bar_chart(proc_ids, cycle_times, title='프로세스 사이클타임', x_label='Process', y_label='Cycle Time', save_path='process_cycle_time.png')

    # 2. 리소스 분석 섹션 활용 (최종 시점 스냅샷)
        resource_analysis = comprehensive_report.get('resource_analysis', {})
        utilization_series = {}
        if isinstance(resource_analysis, dict):
            resources_section = resource_analysis.get('resources') or resource_analysis
            if isinstance(resources_section, dict):
                for rid, rdata in resources_section.items():
                    if not isinstance(rdata, dict):
                        continue
                    metrics = rdata.get('metrics') or rdata
                    if isinstance(metrics, dict):
                        u = metrics.get('utilization') or metrics.get('avg_utilization') or metrics.get('availability')
                        if isinstance(u, (int, float)):
                            utilization_series[rid] = [u]
        if utilization_series:
            viz.plot_multi_line_chart([0], utilization_series, title='리소스 가동률 (최종시점)', x_label='Time', y_label='Utilization', save_path='resource_utilization_final.png', show_legend=True)

        # 3. 성능 메트릭(전체) 기반 KPI 바차트 (선택)
        perf_metrics_global = comprehensive_report.get('performance_metrics', {})
        if isinstance(perf_metrics_global, dict):
            kpi_candidates = {k: v for k, v in perf_metrics_global.items() if isinstance(v, (int, float))}
            if kpi_candidates:
                labels = list(kpi_candidates.keys())[:12]  # 너무 많으면 자름
                values = [kpi_candidates[l] for l in labels]
                viz.plot_bar_chart(labels, values, title='글로벌 성능 KPI', x_label='Metric', y_label='Value', save_path='global_kpis.png')

        # 4. 경고/알림 데이터: anomaly_analysis 섹션이나 performance_metrics 내 경고 수 추출 시도
        anomalies = comprehensive_report.get('anomaly_analysis', {})
        severity_counts = {}
        if isinstance(anomalies, dict):
            sev_map = anomalies.get('severity_counts') or anomalies.get('severity') or {}
            if isinstance(sev_map, dict):
                severity_counts = {k: v for k, v in sev_map.items() if isinstance(v, (int, float))}
        # 시각화
        if severity_counts:
            import matplotlib.pyplot as plt
            labels = list(severity_counts.keys())
            values = list(severity_counts.values())
            plt.figure(figsize=(6,6))
            plt.pie(values, labels=labels, autopct='%1.1f%%', startangle=140)
            plt.title('알림/이상 심각도 분포')
            pie_path = os.path.join(project_root, 'visualizations', 'alert_severity_distribution.png')
            os.makedirs(os.path.dirname(pie_path), exist_ok=True)
            plt.savefig(pie_path, dpi=300, bbox_inches='tight')
            plt.close()
            print(f"[Visualization] 파이차트 저장: {pie_path}")
    except Exception as e:
        print(f"[Visualization] 시각화 생성 중 오류: {e}")

def generate_utilization_timeline_charts(util_history: Dict[str, List[tuple]]):
    """샘플링된 리소스 사용률 히스토리로 타임라인 및 시간당 평균 차트 생성"""
    if not util_history:
        print('[Visualization] 사용률 히스토리 비어있어 타임라인 생략')
        return
    viz = VisualizationManager(output_dir=os.path.join(project_root, 'visualizations'))
    # 타임라인 (raw)
    viz.plot_utilization_timeline(util_history, title='리소스 사용률 타임라인', save_path='resource_utilization_timeline.png')
    # 시간당 평균 계산
    hourly: Dict[str, List[float]] = {}
    for rid, series in util_history.items():
        buckets: Dict[int, List[float]] = {}
        for t, v in series:
            hour = int(t // 60)  # 60단위로 1시간 가정
            buckets.setdefault(hour, []).append(v)
        hourly[rid] = [sum(vals)/len(vals) for h, vals in sorted(buckets.items())]
    # 공통 시간축 (시간 인덱스)
    if hourly:
        max_len = max(len(v) for v in hourly.values())
        time_axis = list(range(max_len))
        # 다중 라인 차트용 변환
        transformed = {rid: vals + [None]*(max_len-len(vals)) for rid, vals in hourly.items()}
        viz.plot_multi_line_chart(time_axis, transformed, title='리소스 시간당 평균 사용률', x_label='Hour(Index)', y_label='Avg Utilization', save_path='resource_utilization_hourly.png')

# ========== 메인 실행 ==========

def main():
    """메인 실행 진입점: 시뮬레이션 수행, 리포트/시각화 생성, 로그 저장"""
    output_capture = io.StringIO()
    original_stdout = sys.stdout
    report_snapshots: List[Dict[str, Any]] = []
    utilization_history: Dict[str, List[tuple]] = {}
    try:
        sys.stdout = output_capture
        print("### ReportManager 통합 냉장고 시뮬레이션 초기화 ###")
        data = create_refrigerator_scenario_with_reporting()
        env = data['env']
        engine = data['engine']
        workflow = data['workflow']
        report_manager = data['report_manager']
        resources = data['resources']

        print("\n### 시뮬레이션 실행 ###")
        engine.add_process(production_starter, workflow, 3)
        engine.add_process(reporting_monitor, report_manager, 100, report_snapshots)
        # 사용률 모니터 (예: 20시간 시뮬 가정 1000 until -> 50 샘플) 간격 20
        engine.add_process(utilization_monitor, resources, 20, utilization_history)
        engine.run(until=1000)

        comprehensive_report = report_manager.generate_comprehensive_report()
        dashboard_final = report_manager.generate_real_time_dashboard()
        save_reports_to_files(comprehensive_report, dashboard_final, report_snapshots)

        # 시각화 생성 (보고서 파일 저장 직후)
        generate_visualizations(report_manager, comprehensive_report)
        generate_utilization_timeline_charts(utilization_history)
    except Exception as e:
        # 오류 메시지를 캡처 로그에 남김
        print(f"[MAIN] 실행 중 예외 발생: {e}")
    finally:
        sys.stdout = original_stdout
        captured = output_capture.getvalue()
        output_capture.close()
        save_output_to_md(captured)
        print(captured)

if __name__ == "__main__":
    main()
