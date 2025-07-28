# 필수사항
1. 기존 파일은 건드리지 말것.
2. prject폴더를 생성하여 해당 폴더에 코드를 작성할 것.
3. 작성한 코드는 반드시 실행이 가능해야 함.
4. 요구사항이 달성되기 전까지는 나한테 선택사항을 묻지말고 최적의 상황을 판단하여 진행할것.

# 요구사항
1. 기존 프로젝트를 모두 읽어서 이해한 후 정리해보고 진행해줘.
2. 기존 시뮬레이션은 텍스트만 출력하기에 시각화 기능을 추가하는것이 목적이다. 
3. 그 시작화 기능은 기존 시뮬레이션과 연계하여 공정에 대해 동적인 공정 흐름 visualization해야한다.
4. 내가 생각중인 예시로는 resource들이 다양한 도형으로 표기하고 product들이 이동하는 과정을 보여줄수 있도록 하는것이다.(product가 transport를 타고 machine과 worker를 통해 이동하는 흐름)
5. 공정 진행에 대해 시간 배율 설정 가능하여 더 빠르거나 느리게 조절할수 있게해줘.
---


mermaid 사용



# 시각화 기능 설계 및 구현 가이드

## 1. 시뮬레이션 흐름 시각화 방식

### A. 공정 네트워크 (DAG)
- **노드**: 공정(Manufacturing / Assembly 등)
- **엣지**: `>>` 연산자로 연결된 흐름
- **실시간 정보**:  
  - 노드 색상: 현재 가동/대기/완료 상태 표시  
  - 엣지 굵기: 순간 처리량 표시

### B. 타임라인 (Gantt/스위밍레인)
- **X축**: 시뮬레이션 시간
- **Y축**: 각 공정 또는 리소스
- **막대 색상**: 상태(가공, 셋업, 고장, 대기 등)

### C. 레이아웃 애니메이션 (2D 공장 배치)
- 기계·AGV 위치를 좌표로 두고, 토큰(제품) 이동을 시각화

> 대부분 A+B 조합이면 연구·보고서에 충분  
> C는 게임처럼 보여주고 싶을 때 추가

---

## 2. 목적별 오픈소스 라이브러리 후보

### 네트워크 / DAG 애니메이션
- `graphviz + pygraphviz`: 정적 그림에 적합, 실시간은 어려움
- `networkx + matplotlib.animation`: 가볍지만 인터랙티브성 낮음
- **Bokeh graph + ColumnDataSource**: 파이썬만으로 웹-실시간 가능 ★
- **PyVis (vis-js 파이썬 래퍼)**: 마우스 인터랙션 우수, Jupyter 지원 ★
- `streamlit-dagre-flow / react-flow`: 프론트 분리형, websocket 필요

### 타임라인 / Gantt
- **Plotly Express timeline**: Jupyter·웹 지원, 줌/휠 지원 ★
- `matplotlib-timetable / seaborn Gantt`: 간단 보고용
- `bokeh.models.Gantt`: Bokeh 서버와 함께 실시간 업데이트 용이

### 2D/3D 배치 애니메이션
- **salabim**: SimPy와 API 유사, 내장 애니메이션 캔버스 ★
- `pygame / arcade`: 게임엔진, UI 직접 구현 필요
- `Panda3D / three.js(py)`: 3D, 과제 범위 벗어날 수 있음

> “SimPy 이벤트 → 웹소켓 → JS 시각화” 구조로 거의 모든 라이브러리 연동 가능  
> 파이썬 전용만 고집할 필요 없음

---

## 3. SimPy 프레임워크 연동 방법 (DAG + Gantt 예시)

### Step 0. 이벤트 로그 표준화
- `core/data_collector.py`에 한 줄씩 기록  
- 예시:
  ```python
  { "time": env.now, "event": "start" | "end" | "block" | ..., "process": "Assembly-1", "entity": "Product#123", "resource": "Machine#A" # 없으면 None }
  ```

### Step 1. 실시간 Broadcaster 추가
- `src/core/event_bus.py` (간단한 PubSub)
  ```python
  class EventBus:
      def __init__(self):
          self.subscribers = defaultdict(list)
      def publish(self, topic, msg):
          for cb in self.subscribers[topic]:
              cb(msg)
      def subscribe(self, topic, cb):
          self.subscribers[topic].append(cb)

  event_bus = EventBus()  # 싱글턴
  # Process 쪽에서
  event_bus.publish("log", record_dict)
  ```

### Step 2. Bokeh 서버(웹소켓 자동 포함) 설정

- `run_visualizer.py` 예시
  ```python
  from bokeh.plotting import curdoc
  from bokeh.models import ColumnDataSource, GraphRenderer, StaticLayoutProvider
  from bokeh.layouts import column
  from sim.event_bus import event_bus
  import networkx as nx

  # 2-1 DAG 그림
  G = nx.DiGraph()
  for p in process_list:
      G.add_node(p.name)
      for nxt in p.next_processes:
          G.add_edge(p.name, nxt.name)

  graph_source = GraphRenderer()
  graph_source.node_renderer.data_source.data = {"index": list(G.nodes()), "color": ["lightgray"]*len(G)}
  pos = nx.nx_agraph.graphviz_layout(G, prog="dot")
  graph_source.layout_provider = StaticLayoutProvider(graph_layout=pos)

  # 2-2 Gantt용 ColumnDataSource
  gantt_src = ColumnDataSource(dict(start=[], end=[], y=[], color=[], desc=[]))

  def update_on_event(msg):
      if msg["event"] == "start":
          idx = list(G.nodes()).index(msg["process"])
          colors = graph_source.node_renderer.data_source.data["color"]
          colors[idx] = "orange"
          graph_source.node_renderer.data_source.data["color"] = colors
          gantt_src.stream(dict(start=[msg["time"]], end=[msg["time"]], y=[msg["process"]], color=["orange"], desc=[msg["entity"]]))
      elif msg["event"] == "end":
          idx = list(G.nodes()).index(msg["process"])
          colors = graph_source.node_renderer.data_source.data["color"]
          colors[idx] = "lightgreen"
          graph_source.node_renderer.data_source.data["color"] = colors
          last_row = len(gantt_src.data["end"]) - 1
          gantt_src.patch({"end": [(last_row, msg["time"])]})

  event_bus.subscribe("log", update_on_event)

  curdoc().add_root(column(graph_source, figure_gantt))
  ```
- 시뮬레이션 파트는 그대로 두고  
  `python -m bokeh serve run_visualizer.py` 실행 → 웹 브라우저에서 실시간 공정 흐름 확인

### Step 3. 시뮬레이션 ↔ 시각화 동기화
- 시뮬레이션을 thread/async로 돌리며 이벤트만 Bus에 푸시
- Bokeh 서버는 메인 프로세스에서 브라우저로 바로 스트림

### Step 4. Gantt를 Plotly로만 쓰고 싶다면?
- Streamlit: `st.plotly_chart(update_stream=True)`
- Dash callback으로 ColumnDataSource 대체 가능

---

## 4. salabim을 사용할 때의 초간단 대안

- SimPy와 문법이 매우 비슷
  ```python
  import salabim as sim

  class Manufacturing(sim.Component):
      def process(self):
          while True:
              yield self.hold(5)
              self.enter(assembly_queue)  # 시각화 자동

  env = sim.Environment(trace=True)
  m = Manufacturing()
  env.run(till=100)
  env.animate()  # Tkinter 창에 2D 애니메이션
  ```
- SimPy → salabim.Component 래퍼로 최소 작업으로 실시간 2D 애니메이션 가능

---

## 5. 정리 – 추천 조합

### 연구·데모 둘 다 노릴 때
- Backend: SimPy + 자체 Framework
- Event Bus: 위의 PubSub (or ZeroMQ)
- Front: Bokeh 서버
- 시각화: DAG + Gantt (필요 시 Plotly로 export)

### Jupyter 노트북에서 가볍게
- PyVis(network) + Plotly timeline, 이벤트는 IPython.display.clear_output 루프

### “진짜 게임처럼”
- salabim or pygame (단, 개발 공수↑)

> 위 순서대로 난이도와 개발시간이 올라가니,  
> 먼저 “PubSub + Bokeh” 프로토타입을 1-2일 안에 만들고,  
> 만족스러우면 커스터마이징하는 전략 추천