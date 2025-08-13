"""
제조 시뮬레이션 프레임워크용 대시보드 모듈

이 모듈은 웹 기반 대시보드를 통해 시뮬레이션 데이터를 실시간으로
시각화하고 모니터링할 수 있는 기능을 제공합니다.
"""

# 선택적 import (패키지가 없어도 에러 발생하지 않도록)
try:
    from .dashboard_manager import DashboardManager
    __all__ = ['DashboardManager']
except ImportError:
    __all__ = []

try:
    from .components import DashboardGrid
    __all__.append('DashboardGrid')
except ImportError:
    pass

try:
    from .layouts import DashboardLayout
    __all__.append('DashboardLayout')
except ImportError:
    pass

try:
    from .kpi_widgets import KPIManager, KPIData, KPIThreshold
    __all__.extend(['KPIManager', 'KPIData', 'KPIThreshold'])
except ImportError:
    pass

try:
    from .real_time_connector import DataBridge, initialize_real_time_system
    __all__.extend(['DataBridge', 'initialize_real_time_system'])
except ImportError:
    pass
