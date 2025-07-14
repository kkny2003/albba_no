"""
공정 흐름을 그래프 기반으로 관리하는 모듈입니다.
NetworkX를 사용하여 제조 공정의 흐름을 그래프로 모델링하고 관리합니다.
"""

import networkx as nx
from typing import Dict, List, Tuple, Optional, Union, Any
from dataclasses import dataclass
import json

# matplotlib은 선택적으로 import (시각화 기능용)
try:
    import matplotlib.pyplot as plt
    MATPLOTLIB_AVAILABLE = True
except ImportError:
    MATPLOTLIB_AVAILABLE = False
    plt = None


@dataclass
class ProcessNode:
    """공정 노드의 속성을 정의하는 데이터 클래스"""
    process_id: str  # 공정 ID
    process_name: str  # 공정 이름
    process_type: str  # 공정 유형 (manufacturing, assembly, quality_control, transport 등)
    duration: float  # 공정 소요 시간
    resources: List[str]  # 필요한 자원 목록 (기계, 작업자 등)
    capacity: int = 1  # 공정 용량 (동시 처리 가능한 제품 수)
    cost: float = 0.0  # 공정 비용
    description: str = ""  # 공정 설명
    
    def to_dict(self) -> Dict[str, Any]:
        """노드 정보를 딕셔너리로 변환"""
        return {
            'process_id': self.process_id,
            'process_name': self.process_name,
            'process_type': self.process_type,
            'duration': self.duration,
            'resources': self.resources,
            'capacity': self.capacity,
            'cost': self.cost,
            'description': self.description
        }


@dataclass
class ProcessEdge:
    """공정 간의 연결을 정의하는 데이터 클래스"""
    from_process: str  # 시작 공정 ID
    to_process: str  # 목표 공정 ID
    transport_time: float = 0.0  # 운송 시간
    transport_cost: float = 0.0  # 운송 비용
    batch_size: int = 1  # 한 번에 전송되는 배치 크기
    condition: Optional[str] = None  # 전송 조건 (선택적)
    
    def to_dict(self) -> Dict[str, Any]:
        """엣지 정보를 딕셔너리로 변환"""
        return {
            'transport_time': self.transport_time,
            'transport_cost': self.transport_cost,
            'batch_size': self.batch_size,
            'condition': self.condition
        }


class ProcessGraph:
    """제조 공정 흐름을 그래프로 관리하는 클래스"""
    
    def __init__(self, graph_name: str = "Manufacturing Process"):
        """
        ProcessGraph 초기화
        
        Args:
            graph_name (str): 그래프 이름
        """
        self.graph_name = graph_name
        self.graph = nx.DiGraph()  # 방향성 그래프 생성 (공정 흐름이므로 방향이 있음)
        self.start_nodes = set()  # 시작 노드들 (입력이 없는 노드)
        self.end_nodes = set()  # 종료 노드들 (출력이 없는 노드)
    
    def add_process(self, process_node: ProcessNode) -> bool:
        """
        공정 노드를 그래프에 추가
        
        Args:
            process_node (ProcessNode): 추가할 공정 노드
            
        Returns:
            bool: 추가 성공 여부
        """
        try:
            if process_node.process_id in self.graph.nodes:
                print(f"경고: 공정 ID '{process_node.process_id}'가 이미 존재합니다.")
                return False
            
            # 노드를 그래프에 추가 (속성 포함)
            self.graph.add_node(process_node.process_id, **process_node.to_dict())
            self._update_start_end_nodes()
            
            print(f"공정 '{process_node.process_name}' (ID: {process_node.process_id})이 추가되었습니다.")
            return True
            
        except Exception as e:
            print(f"공정 추가 중 오류 발생: {e}")
            return False
    
    def add_flow(self, process_edge: ProcessEdge) -> bool:
        """
        공정 간의 흐름(연결)을 추가
        
        Args:
            process_edge (ProcessEdge): 추가할 공정 간 연결
            
        Returns:
            bool: 추가 성공 여부
        """
        try:
            from_id = process_edge.from_process
            to_id = process_edge.to_process
            
            # 노드 존재 확인
            if from_id not in self.graph.nodes:
                print(f"오류: 시작 공정 '{from_id}'가 존재하지 않습니다.")
                return False
                
            if to_id not in self.graph.nodes:
                print(f"오류: 목표 공정 '{to_id}'가 존재하지 않습니다.")
                return False
            
            # 엣지 추가 (속성 포함)
            self.graph.add_edge(from_id, to_id, **process_edge.to_dict())
            self._update_start_end_nodes()
            
            from_name = self.graph.nodes[from_id]['process_name']
            to_name = self.graph.nodes[to_id]['process_name']
            print(f"공정 흐름이 추가되었습니다: {from_name} → {to_name}")
            return True
            
        except Exception as e:
            print(f"공정 흐름 추가 중 오류 발생: {e}")
            return False
    
    def remove_process(self, process_id: str) -> bool:
        """
        공정 노드를 제거
        
        Args:
            process_id (str): 제거할 공정 ID
            
        Returns:
            bool: 제거 성공 여부
        """
        try:
            if process_id not in self.graph.nodes:
                print(f"오류: 공정 ID '{process_id}'가 존재하지 않습니다.")
                return False
            
            process_name = self.graph.nodes[process_id]['process_name']
            self.graph.remove_node(process_id)
            self._update_start_end_nodes()
            
            print(f"공정 '{process_name}' (ID: {process_id})이 제거되었습니다.")
            return True
            
        except Exception as e:
            print(f"공정 제거 중 오류 발생: {e}")
            return False
    
    def remove_flow(self, from_process: str, to_process: str) -> bool:
        """
        공정 간의 흐름을 제거
        
        Args:
            from_process (str): 시작 공정 ID
            to_process (str): 목표 공정 ID
            
        Returns:
            bool: 제거 성공 여부
        """
        try:
            if not self.graph.has_edge(from_process, to_process):
                print(f"오류: '{from_process}' → '{to_process}' 흐름이 존재하지 않습니다.")
                return False
            
            self.graph.remove_edge(from_process, to_process)
            self._update_start_end_nodes()
            
            from_name = self.graph.nodes[from_process]['process_name']
            to_name = self.graph.nodes[to_process]['process_name']
            print(f"공정 흐름이 제거되었습니다: {from_name} → {to_name}")
            return True
            
        except Exception as e:
            print(f"공정 흐름 제거 중 오류 발생: {e}")
            return False
    
    def _update_start_end_nodes(self):
        """시작 노드와 종료 노드를 업데이트"""
        self.start_nodes = {node for node in self.graph.nodes if self.graph.in_degree(node) == 0}
        self.end_nodes = {node for node in self.graph.nodes if self.graph.out_degree(node) == 0}
    
    def get_process_info(self, process_id: str) -> Optional[Dict[str, Any]]:
        """
        특정 공정의 정보를 조회
        
        Args:
            process_id (str): 조회할 공정 ID
            
        Returns:
            Optional[Dict[str, Any]]: 공정 정보 딕셔너리 또는 None
        """
        if process_id not in self.graph.nodes:
            print(f"오류: 공정 ID '{process_id}'가 존재하지 않습니다.")
            return None
        
        return dict(self.graph.nodes[process_id])
    
    def get_flow_info(self, from_process: str, to_process: str) -> Optional[Dict[str, Any]]:
        """
        특정 공정 흐름의 정보를 조회
        
        Args:
            from_process (str): 시작 공정 ID
            to_process (str): 목표 공정 ID
            
        Returns:
            Optional[Dict[str, Any]]: 흐름 정보 딕셔너리 또는 None
        """
        if not self.graph.has_edge(from_process, to_process):
            print(f"오류: '{from_process}' → '{to_process}' 흐름이 존재하지 않습니다.")
            return None
        
        return dict(self.graph.edges[from_process, to_process])
    
    def get_all_processes(self) -> List[Dict[str, Any]]:
        """
        모든 공정 정보를 조회
        
        Returns:
            List[Dict[str, Any]]: 모든 공정 정보 리스트
        """
        processes = []
        for node_id in self.graph.nodes:
            process_info = dict(self.graph.nodes[node_id])
            process_info['node_id'] = node_id
            processes.append(process_info)
        return processes
    
    def get_all_flows(self) -> List[Dict[str, Any]]:
        """
        모든 공정 흐름 정보를 조회
        
        Returns:
            List[Dict[str, Any]]: 모든 흐름 정보 리스트
        """
        flows = []
        for from_id, to_id in self.graph.edges:
            flow_info = dict(self.graph.edges[from_id, to_id])
            flow_info['from_process'] = from_id
            flow_info['to_process'] = to_id
            flows.append(flow_info)
        return flows
    
    def validate_graph(self) -> Dict[str, Any]:
        """
        그래프의 유효성을 검사
        
        Returns:
            Dict[str, Any]: 검사 결과 딕셔너리
        """
        validation_result = {
            'is_valid': True,
            'warnings': [],
            'errors': [],
            'info': {}
        }
        
        # 순환 검사 (DAG인지 확인)
        if not nx.is_directed_acyclic_graph(self.graph):
            cycles = list(nx.simple_cycles(self.graph))
            validation_result['is_valid'] = False
            validation_result['errors'].append(f"그래프에 순환이 있습니다: {cycles}")
        
        # 연결성 검사
        if not nx.is_weakly_connected(self.graph):
            validation_result['warnings'].append("그래프가 완전히 연결되어 있지 않습니다.")
        
        # 시작 노드와 종료 노드 확인
        if not self.start_nodes:
            validation_result['warnings'].append("시작 노드가 없습니다.")
        
        if not self.end_nodes:
            validation_result['warnings'].append("종료 노드가 없습니다.")
        
        # 고립된 노드 확인
        isolated_nodes = list(nx.isolates(self.graph))
        if isolated_nodes:
            validation_result['warnings'].append(f"고립된 노드가 있습니다: {isolated_nodes}")
        
        # 기본 정보 추가
        validation_result['info'] = {
            'total_processes': self.graph.number_of_nodes(),
            'total_flows': self.graph.number_of_edges(),
            'start_nodes': list(self.start_nodes),
            'end_nodes': list(self.end_nodes),
            'isolated_nodes': isolated_nodes
        }
        
        return validation_result
    
    def get_critical_path(self) -> Optional[List[str]]:
        """
        최장 경로(임계 경로)를 계산
        
        Returns:
            Optional[List[str]]: 임계 경로의 노드 리스트 또는 None
        """
        try:
            if not nx.is_directed_acyclic_graph(self.graph):
                print("오류: 순환이 있는 그래프에서는 임계 경로를 계산할 수 없습니다.")
                return None
            
            # 각 노드의 가중치(duration)를 기반으로 최장 경로 계산
            longest_path = nx.dag_longest_path(self.graph, weight='duration')
            return longest_path
            
        except Exception as e:
            print(f"임계 경로 계산 중 오류 발생: {e}")
            return None
    
    def get_total_duration(self, path: Optional[List[str]] = None) -> float:
        """
        특정 경로 또는 임계 경로의 총 소요 시간을 계산
        
        Args:
            path (Optional[List[str]]): 계산할 경로. None이면 임계 경로 사용
            
        Returns:
            float: 총 소요 시간
        """
        if path is None:
            path = self.get_critical_path()
        
        if not path:
            return 0.0
        
        total_duration = 0.0
        
        # 각 노드의 공정 시간 합계
        for node in path:
            total_duration += self.graph.nodes[node]['duration']
        
        # 각 엣지의 운송 시간 합계
        for i in range(len(path) - 1):
            if self.graph.has_edge(path[i], path[i + 1]):
                edge_data = self.graph.edges[path[i], path[i + 1]]
                total_duration += edge_data.get('transport_time', 0.0)
        
        return total_duration
    
    def visualize(self, layout: str = 'hierarchical', 
                  save_path: Optional[str] = None,
                  figsize: Tuple[int, int] = (12, 8),
                  show_labels: bool = True,
                  show_edge_labels: bool = False) -> None:
        """
        그래프를 시각화
        
        Args:
            layout (str): 레이아웃 종류 ('hierarchical', 'spring', 'circular', 'kamada_kawai')
            save_path (Optional[str]): 저장할 파일 경로 (None이면 화면에 표시)
            figsize (Tuple[int, int]): 그림 크기
            show_labels (bool): 노드 라벨 표시 여부
            show_edge_labels (bool): 엣지 라벨 표시 여부
        """
        if not MATPLOTLIB_AVAILABLE:
            print("matplotlib이 설치되지 않아 시각화를 수행할 수 없습니다.")
            print("pip install matplotlib을 실행하여 설치하세요.")
            return
            
        try:
            plt.figure(figsize=figsize)
            
            # 레이아웃 설정
            if layout == 'hierarchical':
                # 계층적 레이아웃 (위상 정렬 기반)
                try:
                    pos = self._get_hierarchical_layout()
                except:
                    pos = nx.spring_layout(self.graph)
            elif layout == 'spring':
                pos = nx.spring_layout(self.graph)
            elif layout == 'circular':
                pos = nx.circular_layout(self.graph)
            elif layout == 'kamada_kawai':
                pos = nx.kamada_kawai_layout(self.graph)
            else:
                pos = nx.spring_layout(self.graph)
            
            # 노드 색상 설정 (공정 유형별)
            node_colors = []
            color_map = {
                'manufacturing': '#FFB6C1',  # 연분홍
                'assembly': '#87CEEB',       # 하늘색
                'quality_control': '#98FB98', # 연녹색
                'transport': '#F0E68C',      # 카키색
                'default': '#D3D3D3'         # 연회색
            }
            
            for node in self.graph.nodes:
                process_type = self.graph.nodes[node].get('process_type', 'default')
                node_colors.append(color_map.get(process_type, color_map['default']))
            
            # 노드 그리기
            nx.draw_networkx_nodes(self.graph, pos, 
                                 node_color=node_colors,
                                 node_size=1500,
                                 alpha=0.8)
            
            # 엣지 그리기
            nx.draw_networkx_edges(self.graph, pos,
                                 edge_color='gray',
                                 arrows=True,
                                 arrowsize=20,
                                 alpha=0.6)
            
            # 노드 라벨 그리기
            if show_labels:
                labels = {}
                for node in self.graph.nodes:
                    process_name = self.graph.nodes[node]['process_name']
                    labels[node] = f"{node}\n{process_name}"
                
                nx.draw_networkx_labels(self.graph, pos, labels,
                                      font_size=8, font_weight='bold')
            
            # 엣지 라벨 그리기
            if show_edge_labels:
                edge_labels = {}
                for from_id, to_id in self.graph.edges:
                    edge_data = self.graph.edges[from_id, to_id]
                    transport_time = edge_data.get('transport_time', 0)
                    edge_labels[(from_id, to_id)] = f"t={transport_time}"
                
                nx.draw_networkx_edge_labels(self.graph, pos, edge_labels,
                                           font_size=6)
            
            plt.title(f"{self.graph_name} - 공정 흐름도", fontsize=16, fontweight='bold')
            plt.axis('off')
            
            # 범례 추가
            legend_elements = []
            for process_type, color in color_map.items():
                if process_type != 'default':
                    legend_elements.append(plt.Rectangle((0, 0), 1, 1, 
                                                       facecolor=color, 
                                                       alpha=0.8,
                                                       label=process_type))
            
            if legend_elements:
                plt.legend(handles=legend_elements, loc='upper right')
            
            plt.tight_layout()
            
            if save_path:
                plt.savefig(save_path, dpi=300, bbox_inches='tight')
                print(f"그래프가 '{save_path}'에 저장되었습니다.")
            else:
                plt.show()
                
        except Exception as e:
            print(f"그래프 시각화 중 오류 발생: {e}")
    
    def _get_hierarchical_layout(self) -> Dict[str, Tuple[float, float]]:
        """계층적 레이아웃 계산"""
        if not nx.is_directed_acyclic_graph(self.graph):
            raise ValueError("계층적 레이아웃은 DAG에서만 사용 가능합니다.")
        
        # 위상 정렬
        topo_sort = list(nx.topological_sort(self.graph))
        
        # 각 레벨별 노드 분류
        levels = {}
        for node in topo_sort:
            if node in self.start_nodes:
                levels[node] = 0
            else:
                max_level = max(levels[pred] for pred in self.graph.predecessors(node))
                levels[node] = max_level + 1
        
        # 레벨별 노드 그룹화
        level_groups = {}
        for node, level in levels.items():
            if level not in level_groups:
                level_groups[level] = []
            level_groups[level].append(node)
        
        # 위치 계산
        pos = {}
        for level, nodes in level_groups.items():
            for i, node in enumerate(nodes):
                x = level
                y = i - len(nodes) / 2
                pos[node] = (x, y)
        
        return pos
    
    def export_to_json(self, file_path: str) -> bool:
        """
        그래프를 JSON 파일로 내보내기
        
        Args:
            file_path (str): 저장할 파일 경로
            
        Returns:
            bool: 저장 성공 여부
        """
        try:
            # NetworkX 그래프를 JSON 형태로 변환
            graph_data = nx.node_link_data(self.graph)
            graph_data['graph_name'] = self.graph_name
            
            with open(file_path, 'w', encoding='utf-8') as f:
                json.dump(graph_data, f, ensure_ascii=False, indent=2)
            
            print(f"그래프가 '{file_path}'에 저장되었습니다.")
            return True
            
        except Exception as e:
            print(f"JSON 내보내기 중 오류 발생: {e}")
            return False
    
    def import_from_json(self, file_path: str) -> bool:
        """
        JSON 파일에서 그래프 가져오기
        
        Args:
            file_path (str): 가져올 파일 경로
            
        Returns:
            bool: 가져오기 성공 여부
        """
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                graph_data = json.load(f)
            
            # NetworkX 그래프로 변환
            self.graph = nx.node_link_graph(graph_data)
            self.graph_name = graph_data.get('graph_name', 'Manufacturing Process')
            self._update_start_end_nodes()
            
            print(f"그래프가 '{file_path}'에서 로드되었습니다.")
            return True
            
        except Exception as e:
            print(f"JSON 가져오기 중 오류 발생: {e}")
            return False
    
    def print_summary(self) -> None:
        """그래프 요약 정보를 출력"""
        print(f"\n=== {self.graph_name} 요약 ===")
        print(f"총 공정 수: {self.graph.number_of_nodes()}")
        print(f"총 흐름 수: {self.graph.number_of_edges()}")
        print(f"시작 노드: {list(self.start_nodes)}")
        print(f"종료 노드: {list(self.end_nodes)}")
        
        # 임계 경로 정보
        critical_path = self.get_critical_path()
        if critical_path:
            total_duration = self.get_total_duration(critical_path)
            print(f"임계 경로: {' → '.join(critical_path)}")
            print(f"총 소요 시간: {total_duration}")
        
        # 유효성 검사 결과
        validation = self.validate_graph()
        if validation['is_valid']:
            print("그래프 상태: 유효")
        else:
            print("그래프 상태: 오류 있음")
            for error in validation['errors']:
                print(f"  - 오류: {error}")
        
        if validation['warnings']:
            print("경고사항:")
            for warning in validation['warnings']:
                print(f"  - {warning}")
        
        print("=" * 50)


# 사용 예제 및 테스트 함수들
def create_sample_process_graph() -> ProcessGraph:
    """샘플 공정 그래프를 생성하는 함수"""
    
    # ProcessGraph 인스턴스 생성
    pg = ProcessGraph("샘플 제조 공정")
    
    # 공정 노드들 생성
    processes = [
        ProcessNode("P001", "원자재 입고", "transport", 1.0, ["forklift", "worker1"], 5),
        ProcessNode("P002", "1차 가공", "manufacturing", 3.0, ["machine1", "worker2"], 2),
        ProcessNode("P003", "2차 가공", "manufacturing", 2.5, ["machine2", "worker3"], 2),
        ProcessNode("P004", "조립", "assembly", 4.0, ["worker4", "worker5"], 1),
        ProcessNode("P005", "품질검사", "quality_control", 1.5, ["inspector", "test_equipment"], 3),
        ProcessNode("P006", "포장", "assembly", 1.0, ["packing_machine", "worker6"], 2),
        ProcessNode("P007", "출고", "transport", 0.5, ["forklift", "worker7"], 5)
    ]
    
    # 공정 노드들을 그래프에 추가
    for process in processes:
        pg.add_process(process)
    
    # 공정 흐름들 생성
    flows = [
        ProcessEdge("P001", "P002", 0.5, 1.0, 1),
        ProcessEdge("P002", "P003", 0.3, 0.5, 1),
        ProcessEdge("P003", "P004", 0.2, 0.3, 1),
        ProcessEdge("P004", "P005", 0.1, 0.1, 1),
        ProcessEdge("P005", "P006", 0.2, 0.2, 1),
        ProcessEdge("P006", "P007", 0.3, 0.5, 1)
    ]
    
    # 공정 흐름들을 그래프에 추가
    for flow in flows:
        pg.add_flow(flow)
    
    return pg


if __name__ == "__main__":
    # 샘플 그래프 생성 및 테스트
    print("=== ProcessGraph 테스트 시작 ===")
    
    # 샘플 그래프 생성
    sample_graph = create_sample_process_graph()
    
    # 그래프 요약 출력
    sample_graph.print_summary()
    
    # 그래프 시각화 (선택적)
    # sample_graph.visualize()
    
    print("\n=== ProcessGraph 테스트 완료 ===")
