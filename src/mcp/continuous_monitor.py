"""Continuous monitoring module with Prometheus metrics.

Provides real-time monitoring of inference latency, GPU memory,
costs, and safety filter performance.
"""

import logging
import time
from typing import Dict, List, Optional

logger = logging.getLogger(__name__)

# Prometheus metrics (initialized lazily)
_METRICS_INITIALIZED = False
LATENCY = None
TOKENS_GENERATED = None
GPU_MEMORY = None
SAFETY_FAILURES = None
COST_DAILY = None


def _init_prometheus_metrics():
    """Initialize Prometheus metrics on first use."""
    global _METRICS_INITIALIZED, LATENCY, TOKENS_GENERATED, GPU_MEMORY, SAFETY_FAILURES, COST_DAILY
    
    if _METRICS_INITIALIZED:
        return
    
    try:
        from prometheus_client import Gauge, Counter, Histogram
        
        LATENCY = Histogram('hf_inference_latency_ms', 'HF Pro inference latency in milliseconds')
        TOKENS_GENERATED = Counter('tokens_generated_total', 'Total tokens generated')
        GPU_MEMORY = Gauge('gpu_memory_percent', 'GPU memory usage percentage')
        SAFETY_FAILURES = Counter('safety_failures_total', 'Safety filter failures')
        COST_DAILY = Gauge('cost_daily_pounds', 'Daily cost in GBP')
        
        _METRICS_INITIALIZED = True
        logger.info("Prometheus metrics initialized")
        
    except ImportError:
        logger.warning("prometheus_client not available, metrics disabled")
        _METRICS_INITIALIZED = False


class ContinuousMonitor:
    """Continuous monitoring with alerting for production inference."""

    def __init__(
        self,
        alert_latency_ms: float = 100,
        alert_memory_pct: float = 80,
        alert_budget_pct: float = 80,
    ):
        """Initialize continuous monitor.
        
        Args:
            alert_latency_ms: Alert threshold for latency
            alert_memory_pct: Alert threshold for GPU memory
            alert_budget_pct: Alert threshold for budget (% of daily limit)
        """
        self.alert_latency_ms = alert_latency_ms
        self.alert_memory_pct = alert_memory_pct
        self.alert_budget_pct = alert_budget_pct
        self.alerts = []
        
        _init_prometheus_metrics()

    def record_inference(
        self,
        latency_ms: float,
        tokens: int,
        passed_safety: bool
    ) -> None:
        """Record inference metrics.
        
        Args:
            latency_ms: Inference latency in milliseconds
            tokens: Number of tokens generated
            passed_safety: Whether safety checks passed
        """
        if _METRICS_INITIALIZED:
            LATENCY.observe(latency_ms)
            TOKENS_GENERATED.inc(tokens)
            
            if not passed_safety:
                SAFETY_FAILURES.inc()
        
        # Check for alerts
        if not passed_safety:
            self._add_alert(
                "SAFETY",
                "Safety filter failure detected"
            )
        
        if latency_ms > self.alert_latency_ms:
            self._add_alert(
                "LATENCY",
                f"Latency {latency_ms:.1f}ms exceeds {self.alert_latency_ms}ms threshold"
            )

    def record_gpu_memory(self, percent: float) -> None:
        """Record GPU memory usage.
        
        Args:
            percent: GPU memory usage percentage
        """
        if _METRICS_INITIALIZED:
            GPU_MEMORY.set(percent)
        
        if percent > self.alert_memory_pct:
            self._add_alert(
                "MEMORY",
                f"GPU memory {percent:.1f}% exceeds {self.alert_memory_pct}% threshold"
            )

    def record_cost(self, daily_cost: float, budget: float = 3.33) -> None:
        """Record daily cost.
        
        Args:
            daily_cost: Current daily cost in GBP
            budget: Daily budget limit in GBP
        """
        if _METRICS_INITIALIZED:
            COST_DAILY.set(daily_cost)
        
        threshold_cost = budget * (self.alert_budget_pct / 100)
        if daily_cost > threshold_cost:
            self._add_alert(
                "BUDGET",
                f"Daily cost £{daily_cost:.2f} approaching budget £{budget:.2f}"
            )

    def _add_alert(self, alert_type: str, message: str) -> None:
        """Add alert to queue.
        
        Args:
            alert_type: Type of alert (SAFETY, LATENCY, MEMORY, BUDGET)
            message: Alert message
        """
        self.alerts.append({
            "type": alert_type,
            "message": message,
            "timestamp": time.time(),
        })
        logger.warning(f"ALERT [{alert_type}]: {message}")

    def get_alerts(self, hours: int = 1) -> List[Dict]:
        """Get recent alerts.
        
        Args:
            hours: Number of hours to look back
            
        Returns:
            List of alerts from specified timeframe
        """
        cutoff = time.time() - (hours * 3600)
        return [a for a in self.alerts if a["timestamp"] > cutoff]

    def clear_alerts(self, hours: Optional[int] = None) -> int:
        """Clear old alerts.
        
        Args:
            hours: Clear alerts older than N hours (None = clear all)
            
        Returns:
            Number of alerts cleared
        """
        if hours is None:
            count = len(self.alerts)
            self.alerts.clear()
            return count
        
        cutoff = time.time() - (hours * 3600)
        before = len(self.alerts)
        self.alerts = [a for a in self.alerts if a["timestamp"] > cutoff]
        return before - len(self.alerts)

    def get_summary(self) -> Dict:
        """Get monitoring summary.
        
        Returns:
            Summary of recent alerts and status
        """
        recent_alerts = self.get_alerts(hours=1)
        
        alert_counts = {}
        for alert in recent_alerts:
            alert_type = alert["type"]
            alert_counts[alert_type] = alert_counts.get(alert_type, 0) + 1
        
        return {
            "total_alerts_1h": len(recent_alerts),
            "alerts_by_type": alert_counts,
            "active_alerts": [a for a in recent_alerts if time.time() - a["timestamp"] < 300],  # Last 5 min
        }


def start_monitoring_server(port: int = 9090) -> None:
    """Start Prometheus metrics HTTP server.
    
    Args:
        port: Port to expose metrics on
    """
    try:
        from prometheus_client import start_http_server
        
        _init_prometheus_metrics()
        start_http_server(port)
        logger.info(f"Metrics server running on http://localhost:{port}/metrics")
        
    except ImportError:
        logger.error("prometheus_client not installed, cannot start metrics server")
    except Exception as e:
        logger.error(f"Failed to start metrics server: {e}")

