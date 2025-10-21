"""MCP (Model Checking/Profiling) Tools Module.

Provides data validation, profiling analysis, safety checking,
continuous monitoring, and parallel execution tracking.
"""

from src.mcp.data_validation import DataValidator, validate_training_data
from src.mcp.safety_validator import SafetyValidator, validate_model_safety
from src.mcp.profiling_analyzer import ProfilingAnalyzer, iterative_optimization
from src.mcp.continuous_monitor import ContinuousMonitor, start_monitoring_server
from src.mcp.parallel_monitor import ParallelMonitor, get_parallel_monitor

__all__ = [
    "DataValidator",
    "validate_training_data",
    "SafetyValidator",
    "validate_model_safety",
    "ProfilingAnalyzer",
    "iterative_optimization",
    "ContinuousMonitor",
    "start_monitoring_server",
    "ParallelMonitor",
    "get_parallel_monitor",
]

__version__ = "0.2.0"  # Parallel monitoring added

