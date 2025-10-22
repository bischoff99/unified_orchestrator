"""Core Data Models for Orchestration System"""

from pydantic import BaseModel, Field, ConfigDict
from typing import Literal, Optional, Any
from datetime import datetime
from enum import Enum


class JobStatus(str, Enum):
    """Job execution status"""
    RUNNING = "running"
    SUCCEEDED = "succeeded"
    FAILED = "failed"
    CANCELLED = "cancelled"


class Failure(BaseModel):
    """
    Represents a step or job failure with detailed context.
    
    Attributes:
        kind: Type of failure (timeout, validation, tool, provider)
        step: Step identifier where failure occurred
        message: Human-readable error message
        data: Additional context data (stack trace, args, etc.)
    """
    kind: Literal["timeout", "validation", "tool", "provider"]
    step: str
    message: str
    data: Optional[dict[str, Any]] = None
    timestamp: datetime = Field(default_factory=datetime.utcnow)
    
    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "kind": "timeout",
                "step": "builder",
                "message": "Provider request timed out after 120s",
                "data": {"provider": "ollama", "retry_count": 3}
            }
        }
    )


class Artifact(BaseModel):
    """
    Represents a generated file or output artifact.
    
    Attributes:
        path: Relative path to artifact (e.g., 'src/main.py')
        sha256: Content hash for integrity verification
        size_bytes: File size in bytes
        media_type: MIME type (e.g., 'text/x-python', 'application/json')
        created_at: Timestamp when artifact was created
    """
    path: str
    sha256: str
    size_bytes: int
    media_type: str = "text/plain"
    created_at: datetime = Field(default_factory=datetime.utcnow)
    
    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "path": "src/generated/notes_api/main.py",
                "sha256": "a3b2c1...",
                "size_bytes": 1784,
                "media_type": "text/x-python"
            }
        }
    )


class StepResult(BaseModel):
    """
    Result of a single DAG step execution.
    
    Attributes:
        step_id: Unique identifier for this step
        status: Execution status (succeeded/failed)
        output: Step output data (arbitrary structure)
        artifacts: List of files/outputs produced
        duration_s: Execution time in seconds
        provider_calls: Number of LLM API calls made
        failure: Failure details if status=failed
    """
    step_id: str
    status: Literal["succeeded", "failed"]
    output: Optional[dict[str, Any]] = None
    artifacts: list[Artifact] = Field(default_factory=list)
    duration_s: float = 0.0
    provider_calls: int = 0
    failure: Optional[Failure] = None
    started_at: datetime = Field(default_factory=datetime.utcnow)
    finished_at: Optional[datetime] = None
    
    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "step_id": "builder",
                "status": "succeeded",
                "output": {"files_created": 2},
                "artifacts": [],
                "duration_s": 45.2,
                "provider_calls": 3
            }
        }
    )


class JobSpec(BaseModel):
    """
    Specification for a job to be executed.
    
    Defines the task to be performed and execution parameters.
    
    Attributes:
        project: Project name/description
        task_description: What the job should accomplish
        provider: LLM provider to use (ollama, openai, anthropic, mlx)
        concurrency: Max parallel steps
        timeout_s: Overall job timeout
        output_dir: Where to write generated files
    """
    project: str
    task_description: str
    provider: str = "ollama"
    concurrency: int = 4
    timeout_s: int = 900  # 15 minutes
    output_dir: str = "src/generated"
    
    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "project": "notes_api",
                "task_description": "Create FastAPI notes app with CRUD endpoints",
                "provider": "ollama",
                "concurrency": 4
            }
        }
    )


class Job(BaseModel):
    """
    Represents a running or completed job.
    
    Tracks execution state, results, and metadata.
    
    Attributes:
        job_id: Unique identifier (UUID)
        spec: Job specification
        status: Current execution status
        steps: Results from each executed step
        artifacts: All files/outputs produced
        failures: List of any failures encountered
        started_at: Job start timestamp
        finished_at: Job completion timestamp (if finished)
        run_dir: Path to run directory (runs/<job_id>/)
    """
    job_id: str
    spec: JobSpec
    status: JobStatus = JobStatus.RUNNING
    steps: dict[str, StepResult] = Field(default_factory=dict)
    artifacts: list[Artifact] = Field(default_factory=list)
    failures: list[Failure] = Field(default_factory=list)
    started_at: datetime = Field(default_factory=datetime.utcnow)
    finished_at: Optional[datetime] = None
    run_dir: str = ""
    
    def add_step_result(self, result: StepResult):
        """Add a step result to the job"""
        self.steps[result.step_id] = result
        self.artifacts.extend(result.artifacts)
        if result.failure:
            self.failures.append(result.failure)
    
    def mark_completed(self, status: JobStatus):
        """Mark job as completed with final status"""
        self.status = status
        self.finished_at = datetime.utcnow()
    
    @property
    def duration_s(self) -> float:
        """Calculate total job duration"""
        if self.finished_at:
            return (self.finished_at - self.started_at).total_seconds()
        else:
            return (datetime.utcnow() - self.started_at).total_seconds()
    
    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "job_id": "job_123abc",
                "spec": {"project": "notes_api", "task_description": "..."},
                "status": "running",
                "steps": {},
                "artifacts": []
            }
        }
    )

