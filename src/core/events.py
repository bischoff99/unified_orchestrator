"""Event Logging System

Emits typed events to ND-JSON (newline-delimited JSON) log files.
Each job gets its own events.jsonl file in runs/<job_id>/events.jsonl
"""

import json
from pathlib import Path
from datetime import datetime
from typing import Any, Literal, Optional
from contextlib import contextmanager


class EventEmitter:
    """
    Emits structured events to ND-JSON log files.
    
    Events are written one-per-line as JSON objects to enable
    streaming analysis and easy parsing.
    """
    
    def __init__(self, log_path: Path):
        """
        Initialize event emitter.
        
        Args:
            log_path: Path to events.jsonl file
        """
        self.log_path = log_path
        self.log_path.parent.mkdir(parents=True, exist_ok=True)
        
        # Create/open log file
        self._log_file = open(self.log_path, 'a', buffering=1)  # Line buffered
    
    def emit(self, event: dict[str, Any]):
        """
        Emit a typed event to the log.
        
        Args:
            event: Event dict with 'type' and other fields
        """
        # Add timestamp if not present
        if 'timestamp' not in event:
            event['timestamp'] = datetime.utcnow().isoformat()
        
        # Write as ND-JSON
        json_line = json.dumps(event, default=str)
        self._log_file.write(json_line + '\n')
        self._log_file.flush()
    
    def job_started(self, job_id: str, spec: dict[str, Any]):
        """Emit job.started event"""
        self.emit({
            'type': 'job.started',
            'job_id': job_id,
            'project': spec.get('project'),
            'provider': spec.get('provider'),
            'task': spec.get('task_description'),
        })
    
    def job_succeeded(self, job_id: str, duration_s: float, artifact_count: int):
        """Emit job.succeeded event"""
        self.emit({
            'type': 'job.succeeded',
            'job_id': job_id,
            'duration_s': duration_s,
            'artifacts': artifact_count,
        })
    
    def job_failed(self, job_id: str, error: str, duration_s: float):
        """Emit job.failed event"""
        self.emit({
            'type': 'job.failed',
            'job_id': job_id,
            'error': error,
            'duration_s': duration_s,
        })
    
    def step_started(self, job_id: str, step_id: str, dependencies: list[str]):
        """Emit step.started event"""
        self.emit({
            'type': 'step.started',
            'job_id': job_id,
            'step': step_id,
            'needs': dependencies,
        })
    
    def step_succeeded(
        self,
        job_id: str,
        step_id: str,
        duration_s: float,
        provider_calls: int = 0
    ):
        """Emit step.succeeded event"""
        self.emit({
            'type': 'step.succeeded',
            'job_id': job_id,
            'step': step_id,
            'duration_s': duration_s,
            'provider_calls': provider_calls,
        })
    
    def step_failed(
        self,
        job_id: str,
        step_id: str,
        kind: Literal["timeout", "validation", "tool", "provider"],
        message: str,
        data: Optional[dict] = None
    ):
        """Emit step.failed event"""
        self.emit({
            'type': 'step.failed',
            'job_id': job_id,
            'step': step_id,
            'kind': kind,
            'message': message,
            'data': data or {},
        })
    
    def provider_call(
        self,
        job_id: str,
        step_id: str,
        provider: str,
        duration_s: float,
        tokens_in: int = 0,
        tokens_out: int = 0
    ):
        """Emit provider.call event"""
        self.emit({
            'type': 'provider.call',
            'job_id': job_id,
            'step': step_id,
            'provider': provider,
            'duration_s': duration_s,
            'tokens_in': tokens_in,
            'tokens_out': tokens_out,
        })
    
    def artifact_created(
        self,
        job_id: str,
        step_id: str,
        path: str,
        sha256: str,
        size_bytes: int
    ):
        """Emit artifact.created event"""
        self.emit({
            'type': 'artifact.created',
            'job_id': job_id,
            'step': step_id,
            'path': path,
            'sha256': sha256,
            'size_bytes': size_bytes,
        })
    
    def close(self):
        """Close the log file"""
        if hasattr(self, '_log_file') and self._log_file:
            self._log_file.close()
    
    def __del__(self):
        """Ensure log file is closed"""
        self.close()


@contextmanager
def event_logger(log_path: Path):
    """
    Context manager for event logging.
    
    Usage:
        with event_logger(Path('runs/job_123/events.jsonl')) as emit:
            emit.job_started('job_123', spec_dict)
            emit.step_started('job_123', 'architect', [])
            ...
    """
    emitter = EventEmitter(log_path)
    try:
        yield emitter
    finally:
        emitter.close()


def read_events(log_path: Path) -> list[dict]:
    """
    Read all events from an events.jsonl file.
    
    Args:
        log_path: Path to events.jsonl
        
    Returns:
        List of event dicts in chronological order
    """
    if not log_path.exists():
        return []
    
    events = []
    with open(log_path, 'r') as f:
        for line in f:
            line = line.strip()
            if line:
                events.append(json.loads(line))
    
    return events


def filter_events(
    events: list[dict],
    event_type: Optional[str] = None,
    step_id: Optional[str] = None
) -> list[dict]:
    """
    Filter events by type and/or step.
    
    Args:
        events: List of event dicts
        event_type: Filter by event type (e.g., 'step.started')
        step_id: Filter by step identifier
        
    Returns:
        Filtered list of events
    """
    filtered = events
    
    if event_type:
        filtered = [e for e in filtered if e.get('type') == event_type]
    
    if step_id:
        filtered = [e for e in filtered if e.get('step') == step_id]
    
    return filtered

