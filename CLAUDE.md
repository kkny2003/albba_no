# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.
한국어를 사용하여 대답하시오.

## Project Overview

This is a **SimPy-based Manufacturing Simulation Framework** that provides a comprehensive system for modeling and simulating complex manufacturing processes. The framework is built around the concept of **BaseProcess integration architecture** with advanced resource management capabilities.

## Key Commands

### Development Commands
```bash
# Run main refrigerator manufacturing scenario
python scenario/scenario.py

# Run complete working scenario (most comprehensive)
python scenario/scenario_complete_working.py

# Run Enhanced Reporting Scenario with ReportManager (RECOMMENDED)
python scenario/enhanced_reporting_scenario.py

# Run ReportManager test scenarios
python scenario/test_report_simple.py
python scenario/test_report_refrigerator.py

# Run specific test scenarios
python scenario/test_simple_process.py
python scenario/test_transport.py

# Install dependencies
pip install -r requirements.txt

# Package installation (development mode)
pip install -e .
```

### Project Structure Setup
When writing new scenarios, always include this path setup at the top:
```python
import os
import sys
project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, project_root)
```

## Architecture Overview

### Core Framework Components

1. **BaseProcess Architecture (src/Processes/base_process.py)**
   - All manufacturing processes inherit from `BaseProcess`
   - Supports batch processing, priority systems, and parallel execution
   - Built-in resource management with input/output tracking
   - Output blocking feature for transport coordination
   - SimPy generator-based execution with `yield from` patterns

2. **Resource Management System**
   - **AdvancedResourceManager** (src/core/resource_manager.py): Centralized resource allocation
   - **ResourceBase** (src/Resource/resource_base.py): Dynamic resource properties with type safety
   - **Resource Types**: Machine, Worker, Transport, Buffer, Product with specific capabilities

3. **ReportManager System (src/core/report_manager.py)** ⭐ **NEW**
   - **ReportManager**: Central reporting and monitoring system
   - **ResourceStateTracker**: Real-time resource status tracking
   - **ProcessPerformanceMonitor**: Process performance analytics
   - **AlertSystem**: Automated anomaly detection and alerts
   - Real-time dashboard generation and comprehensive reporting
   - Data export (JSON, CSV, Excel, HTML) with manufacturing KPIs

4. **Simulation Engine** (src/core/simulation_engine.py)
   - SimPy environment wrapper with centralized statistics
   - Process lifecycle management
   - Integrated data collection with CentralizedStatisticsManager

5. **Process Chain System** (src/Flow/)
   - Process chaining using `>>` operator: `process1 >> process2 >> process3`
   - MultiProcessGroup for parallel execution
   - Advanced workflow composition

### Process Types

- **ManufacturingProcess**: Physical manufacturing operations (cutting, drilling, processing)
- **AssemblyProcess**: Component assembly operations
- **QualityControlProcess**: Quality inspection and testing
- **TransportProcess**: Material and product transportation

### Key Design Patterns

1. **Generator-Based Execution**: All processes use SimPy generators with `yield from`
2. **Resource Blocking**: Output buffers can block processes when full, waiting for transport
3. **Batch Processing**: Configurable batch sizes with automatic batching logic
4. **Failure Modeling**: Probabilistic machine failures and worker errors with weight factors

## Development Guidelines

### Code Style Requirements
- **Import Rules**: Use absolute imports starting with `src.` (e.g., `from src.core.simulation_engine import SimulationEngine`)
- **Documentation**: All classes/methods require detailed Korean docstrings
- **SimPy Integration**: Prefer SimPy built-in methods over custom implementations
- **Backward Compatibility**: All new features must maintain backward compatibility

### Resource Management Patterns
```python
# Proper resource setup
resource_manager = AdvancedResourceManager(env)
resource_manager.register_resource("transport", capacity=10, resource_type=ResourceType.TRANSPORT)

# Process with resource manager integration
process = ManufacturingProcess(
    env=env,
    process_id='DRILL_001',
    process_name='드릴링공정',
    machines=[drilling_machine],
    workers=[operator],
    processing_time=3.0,
    resource_manager=resource_manager
)
```

### ReportManager Integration Pattern ⭐ **NEW**
```python
# ReportManager setup with existing systems
from src.core.report_manager import ReportManager, ExportFormat

# Initialize ReportManager
report_manager = ReportManager(env, engine.stats_manager)

# Register all resources and processes
report_manager.register_resource('MACHINE_1', machine)
report_manager.register_process('PROCESS_1', process)

# Real-time monitoring
status = report_manager.collect_real_time_status()
anomalies = report_manager.detect_anomalies()
dashboard = report_manager.generate_real_time_dashboard()

# Performance analysis
metrics = report_manager.calculate_performance_metrics()
bottlenecks = report_manager.analyze_bottlenecks()

# Data export
report_manager.export_data(ExportFormat.JSON, data, "production_report")
report_manager.export_data(ExportFormat.HTML, data, "dashboard")
```

### Process Chaining Pattern
```python
# Chain processes using >> operator
complete_workflow = manufacturing >> transport >> assembly >> quality_check

# Multi-group parallel processing
parallel_lines = MultiProcessGroup([line1, line2, line3, line4])
```

### Scenario Structure
- Place scenarios in `scenario/` folder
- Include automatic logging to `log/` folder as markdown files
- Capture stdout and save with timestamp
- Use comprehensive error handling

## Important Implementation Details

### BaseProcess Key Features
- **Batch Processing**: `batch_size` parameter controls items processed together
- **Output Buffer**: `output_buffer_capacity` limits output items, enabling transport blocking
- **Resource Validation**: Built-in validation for machine/worker requirements
- **Failure Weights**: `failure_weight_machine` and `failure_weight_worker` for reliability modeling

### Transport Integration
- Processes automatically request transport when output buffer is full
- `transport_ready_event` coordinates between processes and transport systems
- Transport blocking can be disabled per process: `process.enable_output_blocking_feature(False)`

### Statistics Collection
- **CentralizedStatisticsManager**: Standardized metrics collection across all components
- **ReportManager**: Advanced reporting with real-time analytics and export capabilities ⭐ **NEW**
- **DataCollector**: Legacy support with modern integration
- Real-time KPI calculation (OEE, utilization rates, throughput, cycle times)
- Automated anomaly detection and bottleneck analysis

## Common Patterns

### Creating a Complete Manufacturing Line
1. Create SimulationEngine and AdvancedResourceManager
2. Define all resources (machines, workers, transport)
3. Register resources with resource manager
4. Create processes with proper resource assignments
5. Chain processes using `>>` operator
6. Execute with proper product flow

### Error Handling
- Always validate resource availability before process execution
- Handle transport blocking gracefully
- Use try/catch for SimPy environment errors
- Provide clear error messages for debugging

### Future Development Focus (해야할꺼.md)
- ResourceManager improvements for unified resource registration
- Input/output resource definitions for better process validation
- Probabilistic failure distributions (exponential, normal) for machines/workers
- Decorators for automatic logging and time measurement
- Hierarchical hybrid architecture with central orchestration and agent layers

## Testing and Validation

### Scenario Testing
- `enhanced_reporting_scenario.py`: **Complete refrigerator manufacturing with ReportManager** (RECOMMENDED) ⭐
- `scenario.py`: Complete refrigerator manufacturing (basic version)
- `test_report_simple.py`: ReportManager basic functionality testing ⭐ **NEW**
- `test_report_refrigerator.py`: ReportManager integration testing ⭐ **NEW**
- `test_simple_process.py`: Basic process functionality
- `test_transport.py`: Transport system validation

### Performance Monitoring
- Check `log/` folder for execution logs with timestamps
- **ReportManager**: Real-time monitoring with automated report generation ⭐ **NEW**
  - Real-time dashboard: 0.000 seconds response time
  - Comprehensive reports: 0.003 seconds generation time  
  - Automated JSON/HTML export with manufacturing KPIs
  - 35+ resources and 40+ processes simultaneous tracking
- Monitor resource utilization through statistics interfaces
- Validate process chain execution order and timing

## Integration Notes

- Framework uses SimPy 4.0+ for discrete event simulation
- Pandas/NumPy for data processing and analysis
- Matplotlib for visualization capabilities
- **ReportManager**: Comprehensive analytics with multiple export formats ⭐ **NEW**
- All outputs automatically logged to markdown files for analysis

## Claude Code Settings

Based on `.claude/settings.local.json`:
- **Permissions**: 
  - Allowed: `mcp__smithery-ai-server-sequential-thinking__sequentialthinking`, `Bash`, `Bash(python:*)`
  - Default Mode: `plan` (Use planning mode for complex implementations)
- **Recommended Workflow**: 
  1. Use plan mode for complex ReportManager integrations
  2. Execute Python scenarios with Bash permissions
  3. Leverage sequential thinking for multi-step analysis