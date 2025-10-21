"""Parallel execution monitoring for multi-agent orchestration.

Tracks agent-level execution metrics, concurrent worker counts,
and dependency wait times for parallel orchestration observability.
"""

import logging
import time
from typing import Dict, Set, Optional
from contextlib import contextmanager
from threading import Lock

logger = logging.getLogger(__name__)

# Prometheus metrics (lazy initialization)
_METRICS_INITIALIZED = False
AGENT_EXECUTION_TIME = None
CONCURRENT_AGENTS = None
TASK_WAIT_TIME = None
TASK_QUEUE_LENGTH = None


def _init_parallel_metrics():
    """Initialize Prometheus metrics for parallel monitoring."""
    global _METRICS_INITIALIZED, AGENT_EXECUTION_TIME, CONCURRENT_AGENTS, TASK_WAIT_TIME, TASK_QUEUE_LENGTH
    
    if _METRICS_INITIALIZED:
        return
    
    try:
        from prometheus_client import Histogram, Gauge
        
        AGENT_EXECUTION_TIME = Histogram(
            'agent_execution_seconds',
            'Agent task execution duration',
            ['agent_name', 'task_name', 'phase']
        )
        
        CONCURRENT_AGENTS = Gauge(
            'concurrent_agents_active',
            'Number of agents executing concurrently'
        )
        
        TASK_WAIT_TIME = Histogram(
            'task_dependency_wait_seconds',
            'Time spent waiting for task dependencies',
            ['task_name']
        )
        
        TASK_QUEUE_LENGTH = Gauge(
            'task_queue_length',
            'Number of tasks waiting to execute'
        )
        
        _METRICS_INITIALIZED = True
        logger.info("Parallel monitoring metrics initialized")
        
    except ImportError:
        logger.warning("prometheus_client not available, parallel metrics disabled")
        _METRICS_INITIALIZED = False


class ParallelMonitor:
    """Monitor parallel agent execution for observability."""
    
    def __init__(self):
        """Initialize parallel monitor."""
        self.active_agents: Set[str] = set()
        self.task_start_times: Dict[str, float] = {}
        self.task_wait_times: Dict[str, float] = {}
        self.execution_history: list = []
        self._lock = Lock()
        
        _init_parallel_metrics()
    
    @contextmanager
    def track_agent(
        self,
        agent_name: str,
        task_name: str = "default",
        phase: str = "execution"
    ):
        """Track agent execution with metrics.
        
        Args:
            agent_name: Name of agent being tracked
            task_name: Name of task being executed
            phase: Execution phase (architecture, implementation, validation, etc.)
            
        Yields:
            Tracking context
            
        Example:
            monitor = ParallelMonitor()
            with monitor.track_agent("fullstack", "implement_api", "implementation"):
                # Agent execution code here
                pass
        """
        # Mark agent as active
        with self._lock:
            self.active_agents.add(agent_name)
            if _METRICS_INITIALIZED:
                CONCURRENT_AGENTS.set(len(self.active_agents))
        
        start_time = time.time()
        
        try:
            yield
        finally:
            # Record execution time
            duration = time.time() - start_time
            
            if _METRICS_INITIALIZED:
                AGENT_EXECUTION_TIME.labels(
                    agent_name=agent_name,
                    task_name=task_name,
                    phase=phase
                ).observe(duration)
            
            # Record history
            with self._lock:
                self.execution_history.append({
                    "agent_name": agent_name,
                    "task_name": task_name,
                    "phase": phase,
                    "duration_sec": duration,
                    "timestamp": time.time(),
                })
                
                # Remove from active set
                self.active_agents.discard(agent_name)
                if _METRICS_INITIALIZED:
                    CONCURRENT_AGENTS.set(len(self.active_agents))
            
            logger.info(
                f"Agent '{agent_name}' completed '{task_name}' in {duration:.2f}s"
            )
    
    @contextmanager
    def track_dependency_wait(self, task_name: str):
        """Track time spent waiting for task dependencies.
        
        Args:
            task_name: Name of task waiting for dependencies
            
        Yields:
            Wait tracking context
        """
        start_time = time.time()
        
        try:
            yield
        finally:
            wait_time = time.time() - start_time
            
            if _METRICS_INITIALIZED:
                TASK_WAIT_TIME.labels(task_name=task_name).observe(wait_time)
            
            with self._lock:
                self.task_wait_times[task_name] = wait_time
            
            if wait_time > 10:  # Alert if waiting > 10 seconds
                logger.warning(
                    f"Task '{task_name}' waited {wait_time:.1f}s for dependencies"
                )
    
    def get_active_agents(self) -> Set[str]:
        """Get set of currently active agents.
        
        Returns:
            Set of active agent names
        """
        with self._lock:
            return self.active_agents.copy()
    
    def get_execution_summary(self) -> Dict:
        """Get execution summary statistics.
        
        Returns:
            Summary with concurrent counts, total executions, avg duration
        """
        with self._lock:
            if not self.execution_history:
                return {
                    "total_executions": 0,
                    "active_now": 0,
                    "avg_duration_sec": 0,
                }
            
            total_duration = sum(e["duration_sec"] for e in self.execution_history)
            
            return {
                "total_executions": len(self.execution_history),
                "active_now": len(self.active_agents),
                "avg_duration_sec": total_duration / len(self.execution_history),
                "max_concurrent": max(
                    self._count_concurrent_at_time(e["timestamp"])
                    for e in self.execution_history
                ),
                "by_agent": self._group_by_agent(),
                "by_phase": self._group_by_phase(),
            }
    
    def _count_concurrent_at_time(self, timestamp: float) -> int:
        """Count how many agents were active at given timestamp."""
        count = 0
        for e in self.execution_history:
            start = e["timestamp"] - e["duration_sec"]
            end = e["timestamp"]
            if start <= timestamp <= end:
                count += 1
        return count
    
    def _group_by_agent(self) -> Dict:
        """Group execution history by agent."""
        grouped = {}
        for e in self.execution_history:
            agent = e["agent_name"]
            if agent not in grouped:
                grouped[agent] = {"count": 0, "total_duration": 0}
            grouped[agent]["count"] += 1
            grouped[agent]["total_duration"] += e["duration_sec"]
        return grouped
    
    def _group_by_phase(self) -> Dict:
        """Group execution history by phase."""
        grouped = {}
        for e in self.execution_history:
            phase = e["phase"]
            if phase not in grouped:
                grouped[phase] = {"count": 0, "total_duration": 0}
            grouped[phase]["count"] += 1
            grouped[phase]["total_duration"] += e["duration_sec"]
        return grouped
    
    def clear_history(self):
        """Clear execution history (for testing or reset)."""
        with self._lock:
            self.execution_history.clear()
            self.task_wait_times.clear()
            logger.info("Execution history cleared")


# Global singleton instance
_parallel_monitor = None
_monitor_lock = Lock()


def get_parallel_monitor() -> ParallelMonitor:
    """Get global parallel monitor instance.
    
    Returns:
        Singleton ParallelMonitor instance
    """
    global _parallel_monitor
    
    if _parallel_monitor is None:
        with _monitor_lock:
            if _parallel_monitor is None:
                _parallel_monitor = ParallelMonitor()
    
    return _parallel_monitor

