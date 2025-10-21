"""Metrics Collection for Performance Tracking"""
import time
import psutil
import json
from pathlib import Path
from contextlib import contextmanager
from typing import Dict, List

class MetricsCollector:
    """
    Collect performance metrics during orchestration execution.
    
    Tracks CPU, memory usage, and duration for each phase of execution.
    """
    
    def __init__(self):
        self.metrics: List[Dict] = []
        self.start_time = None
    
    @contextmanager
    def measure(self, phase: str):
        """
        Context manager to measure performance of a code block.
        
        Usage:
            metrics = MetricsCollector()
            with metrics.measure("architecture_phase"):
                # ... code to measure ...
        
        Args:
            phase: Name of the phase being measured
        """
        start = time.time()
        cpu_before = psutil.cpu_percent(interval=0.1)
        mem_before = psutil.virtual_memory().percent
        
        try:
            yield
        finally:
            duration = time.time() - start
            cpu_after = psutil.cpu_percent(interval=0.1)
            mem_after = psutil.virtual_memory().percent
            
            self.metrics.append({
                "phase": phase,
                "duration_seconds": round(duration, 2),
                "cpu_percent": round((cpu_before + cpu_after) / 2, 2),
                "memory_percent": round((mem_before + mem_after) / 2, 2),
                "timestamp": time.time()
            })
    
    def save(self, filepath: str = "logs/metrics.json"):
        """
        Save metrics to JSON file.
        
        Args:
            filepath: Path to save metrics (default: logs/metrics.json)
        """
        Path(filepath).parent.mkdir(parents=True, exist_ok=True)
        
        output = {
            "total_duration": sum(m['duration_seconds'] for m in self.metrics),
            "phase_count": len(self.metrics),
            "avg_cpu_percent": round(sum(m['cpu_percent'] for m in self.metrics) / len(self.metrics), 2) if self.metrics else 0,
            "avg_memory_percent": round(sum(m['memory_percent'] for m in self.metrics) / len(self.metrics), 2) if self.metrics else 0,
            "phases": self.metrics
        }
        
        with open(filepath, 'w') as f:
            json.dump(output, f, indent=2)
    
    def summary(self) -> Dict:
        """
        Get summary statistics of collected metrics.
        
        Returns:
            Dict with total_duration, phase_count, and per-phase metrics
        """
        if not self.metrics:
            return {"total_duration": 0, "phase_count": 0, "metrics": []}
        
        return {
            "total_duration": round(sum(m['duration_seconds'] for m in self.metrics), 2),
            "phase_count": len(self.metrics),
            "avg_cpu_percent": round(sum(m['cpu_percent'] for m in self.metrics) / len(self.metrics), 2),
            "avg_memory_percent": round(sum(m['memory_percent'] for m in self.metrics) / len(self.metrics), 2),
            "metrics": self.metrics
        }
    
    def __repr__(self):
        return f"MetricsCollector(phases={len(self.metrics)}, total_duration={sum(m['duration_seconds'] for m in self.metrics):.2f}s)"

