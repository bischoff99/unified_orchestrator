"""Run Manifest Management

Creates and manages the run folder structure:
runs/<job_id>/
  ├── manifest.json      (job metadata and file listing)
  ├── events.jsonl       (execution events)
  ├── inputs/            (input files/data)
  ├── outputs/           (generated files)
  ├── logs/              (step logs)
  ├── artifacts/         (binary artifacts)
  └── .cache/            (LLM response cache)
"""

import json
from pathlib import Path
from datetime import datetime
from typing import Optional, Union
from .models import Job, JobSpec, JobStatus, Artifact
from .filestore import compute_sha256


class RunManager:
    """
    Manages the run folder structure and manifest for a job.
    
    Responsibilities:
    - Create run directory structure
    - Write and update manifest.json
    - Track artifacts and files
    - Manage job metadata
    """
    
    def __init__(self, job_id: str, runs_base: Path = Path("runs")):
        """
        Initialize run manager.
        
        Args:
            job_id: Unique job identifier
            runs_base: Base directory for all runs (default: 'runs/')
        """
        self.job_id = job_id
        self.run_dir = runs_base / job_id
        self.manifest_path = self.run_dir / "manifest.json"
    
    def create_structure(self, spec: JobSpec) -> Path:
        """
        Create the run directory structure.
        
        Args:
            spec: Job specification
            
        Returns:
            Path to run directory
        """
        # Create all subdirectories
        (self.run_dir / "inputs").mkdir(parents=True, exist_ok=True)
        (self.run_dir / "outputs").mkdir(parents=True, exist_ok=True)
        (self.run_dir / "logs").mkdir(parents=True, exist_ok=True)
        (self.run_dir / "artifacts").mkdir(parents=True, exist_ok=True)
        (self.run_dir / ".cache").mkdir(parents=True, exist_ok=True)
        
        # Write initial manifest
        manifest = {
            "job_id": self.job_id,
            "started_at": datetime.utcnow().isoformat(),
            "project": spec.project,
            "task_description": spec.task_description,
            "provider": spec.provider,
            "status": "running",
            "files": [],
            "artifacts": [],
            "steps": {},
        }
        
        self._write_manifest(manifest)
        
        return self.run_dir
    
    def update_manifest(
        self,
        job: Job,
        artifacts: Optional[list[Artifact]] = None
    ):
        """
        Update manifest.json with current job state.
        
        Args:
            job: Current job instance
            artifacts: Optional list of artifacts to add
        """
        manifest = {
            "job_id": job.job_id,
            "started_at": job.started_at.isoformat(),
            "finished_at": job.finished_at.isoformat() if job.finished_at else None,
            "project": job.spec.project,
            "task_description": job.spec.task_description,
            "provider": job.spec.provider,
            "status": job.status.value,
            "duration_s": job.duration_s,
            "files": [
                {
                    "path": str(art.path),
                    "sha256": art.sha256,
                    "size_bytes": art.size_bytes,
                    "media_type": art.media_type,
                    "created_at": art.created_at.isoformat(),
                }
                for art in (artifacts or job.artifacts)
            ],
            "steps": {
                step_id: {
                    "status": result.status,
                    "duration_s": result.duration_s,
                    "provider_calls": result.provider_calls,
                    "artifacts": len(result.artifacts),
                }
                for step_id, result in job.steps.items()
            },
            "failures": [
                {
                    "kind": f.kind,
                    "step": f.step,
                    "message": f.message,
                    "timestamp": f.timestamp.isoformat(),
                }
                for f in job.failures
            ] if job.failures else [],
        }
        
        self._write_manifest(manifest)
    
    def _write_manifest(self, manifest: dict):
        """Write manifest to disk"""
        with open(self.manifest_path, 'w') as f:
            json.dump(manifest, f, indent=2)
    
    def read_manifest(self) -> Optional[dict]:
        """
        Read manifest.json if it exists.
        
        Returns:
            Manifest dict or None if not found
        """
        if not self.manifest_path.exists():
            return None
        
        with open(self.manifest_path, 'r') as f:
            return json.load(f)
    
    def add_artifact(
        self,
        relative_path: str,
        content: Union[str, bytes],
        media_type: str = "text/plain"
    ) -> Artifact:
        """
        Add an artifact to the run and update manifest.
        
        Args:
            relative_path: Path relative to outputs/ (e.g., 'main.py')
            content: Artifact content
            media_type: MIME type
            
        Returns:
            Artifact object with path and hash
        """
        # Write to outputs/
        output_path = self.run_dir / "outputs" / relative_path
        output_path.parent.mkdir(parents=True, exist_ok=True)
        
        if isinstance(content, str):
            content_bytes = content.encode('utf-8')
        else:
            content_bytes = content
        
        output_path.write_bytes(content_bytes)
        
        # Create artifact record
        artifact = Artifact(
            path=str(relative_path),
            sha256=compute_sha256(content_bytes),
            size_bytes=len(content_bytes),
            media_type=media_type,
        )
        
        return artifact
    
    def get_cache_key(self, content: str) -> str:
        """
        Get cache key for LLM response caching.
        
        Args:
            content: Input content to cache (e.g., prompt)
            
        Returns:
            Cache file path in .cache/
        """
        content_hash = compute_sha256(content)
        return str(self.run_dir / ".cache" / f"{content_hash}.json")
    
    def cache_get(self, key: str) -> Optional[str]:
        """
        Retrieve cached LLM response.
        
        Args:
            key: Cache key from get_cache_key()
            
        Returns:
            Cached response or None if not found
        """
        cache_path = Path(key)
        if not cache_path.exists():
            return None
        
        try:
            with open(cache_path, 'r') as f:
                data = json.load(f)
                return data.get('response')
        except:
            return None
    
    def cache_put(self, key: str, response: str):
        """
        Store LLM response in cache.
        
        Args:
            key: Cache key from get_cache_key()
            response: LLM response to cache
        """
        cache_path = Path(key)
        cache_path.parent.mkdir(parents=True, exist_ok=True)
        
        with open(cache_path, 'w') as f:
            json.dump({
                'response': response,
                'cached_at': datetime.utcnow().isoformat(),
            }, f)


def create_run(job_id: str, spec: JobSpec) -> RunManager:
    """
    Create a new run with directory structure.
    
    Args:
        job_id: Unique identifier for this run
        spec: Job specification
        
    Returns:
        RunManager instance for this run
    """
    manager = RunManager(job_id)
    manager.create_structure(spec)
    return manager

