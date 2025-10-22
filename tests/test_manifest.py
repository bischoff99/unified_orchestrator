"""Tests for Run Manifest and Structure"""

import pytest
from pathlib import Path
import tempfile
import shutil
import json

from src.core.manifest import RunManager, create_run
from src.core.models import JobSpec, Job, JobStatus, Artifact


class TestRunManager:
    """Test run directory creation and manifest management"""
    
    @pytest.fixture
    def temp_runs(self):
        """Create temporary runs directory"""
        temp_dir = Path(tempfile.mkdtemp())
        yield temp_dir
        shutil.rmtree(temp_dir)
    
    def test_create_structure(self, temp_runs):
        """create_structure creates all required directories"""
        manager = RunManager("test_job_123", runs_base=temp_runs)
        spec = JobSpec(
            project="test_project",
            task_description="Test task",
            provider="ollama"
        )
        
        run_dir = manager.create_structure(spec)
        
        # Check all directories exist
        assert (run_dir / "inputs").exists()
        assert (run_dir / "outputs").exists()
        assert (run_dir / "logs").exists()
        assert (run_dir / "artifacts").exists()
        assert (run_dir / ".cache").exists()
        
        # Check manifest was created
        assert manager.manifest_path.exists()
    
    def test_manifest_initial_content(self, temp_runs):
        """Initial manifest contains correct job information"""
        manager = RunManager("test_job_456", runs_base=temp_runs)
        spec = JobSpec(
            project="my_project",
            task_description="Build API",
            provider="openai"
        )
        
        manager.create_structure(spec)
        manifest = manager.read_manifest()
        
        assert manifest is not None
        assert manifest["job_id"] == "test_job_456"
        assert manifest["project"] == "my_project"
        assert manifest["provider"] == "openai"
        assert manifest["status"] == "running"
        assert "started_at" in manifest
        assert isinstance(manifest["files"], list)
    
    def test_update_manifest_with_artifacts(self, temp_runs):
        """update_manifest correctly adds artifacts"""
        manager = RunManager("test_job_789", runs_base=temp_runs)
        spec = JobSpec(project="test", task_description="test", provider="ollama")
        manager.create_structure(spec)
        
        # Create a job with artifacts
        job = Job(
            job_id="test_job_789",
            spec=spec,
            status=JobStatus.SUCCEEDED
        )
        
        artifact = Artifact(
            path="main.py",
            sha256="abc123",
            size_bytes=1000,
            media_type="text/x-python"
        )
        job.artifacts.append(artifact)
        
        # Update manifest
        manager.update_manifest(job)
        
        # Read and verify
        manifest = manager.read_manifest()
        assert len(manifest["files"]) == 1
        assert manifest["files"][0]["path"] == "main.py"
        assert manifest["files"][0]["sha256"] == "abc123"
        assert manifest["status"] == "succeeded"
    
    def test_add_artifact(self, temp_runs):
        """add_artifact writes file and returns artifact object"""
        manager = RunManager("test_job_abc", runs_base=temp_runs)
        spec = JobSpec(project="test", task_description="test", provider="ollama")
        manager.create_structure(spec)
        
        content = "print('Hello, World!')"
        artifact = manager.add_artifact("hello.py", content, media_type="text/x-python")
        
        # Check artifact properties
        assert artifact.path == "hello.py"
        assert artifact.sha256 == compute_sha256(content)
        assert artifact.size_bytes == len(content)
        assert artifact.media_type == "text/x-python"
        
        # Check file was written
        output_path = manager.run_dir / "outputs" / "hello.py"
        assert output_path.exists()
        assert output_path.read_text() == content
    
    def test_cache_operations(self, temp_runs):
        """Cache get/put operations work correctly"""
        manager = RunManager("test_job_cache", runs_base=temp_runs)
        spec = JobSpec(project="test", task_description="test", provider="ollama")
        manager.create_structure(spec)
        
        # Cache miss
        cache_key = manager.get_cache_key("my prompt")
        result = manager.cache_get(cache_key)
        assert result is None
        
        # Cache put
        manager.cache_put(cache_key, "cached response")
        
        # Cache hit
        result = manager.cache_get(cache_key)
        assert result == "cached response"
    
    def test_cache_key_deterministic(self, temp_runs):
        """Same content produces same cache key"""
        manager = RunManager("test_job_key", runs_base=temp_runs)
        spec = JobSpec(project="test", task_description="test", provider="ollama")
        manager.create_structure(spec)
        
        key1 = manager.get_cache_key("prompt text")
        key2 = manager.get_cache_key("prompt text")
        
        assert key1 == key2


def test_create_run():
    """create_run helper function works end-to-end"""
    with tempfile.TemporaryDirectory() as temp_dir:
        temp_runs = Path(temp_dir)
        
        spec = JobSpec(
            project="integration_test",
            task_description="Full test",
            provider="ollama"
        )
        
        # Mock the runs base for create_run
        import src.core.manifest as manifest_module
        original_init = manifest_module.RunManager.__init__
        
        def patched_init(self, job_id, runs_base=temp_runs):
            original_init(self, job_id, runs_base)
        
        manifest_module.RunManager.__init__ = patched_init
        
        try:
            manager = create_run("test_integration", spec)
            
            assert manager.run_dir.exists()
            assert manager.manifest_path.exists()
            
            manifest_data = manager.read_manifest()
            assert manifest_data["project"] == "integration_test"
            
        finally:
            manifest_module.RunManager.__init__ = original_init


from src.core.filestore import compute_sha256

