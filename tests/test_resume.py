"""Tests for Resume-from-Failure Functionality"""

import pytest
import asyncio
import json
from pathlib import Path
import tempfile
import shutil

from src.core.dag import DAG, DAGNode, run_dag, read_completed_steps
from src.core.events import EventEmitter
from src.core.models import StepResult


class TestReadCompletedSteps:
    """Test reading completed steps from events.jsonl"""
    
    @pytest.fixture
    def temp_dir(self):
        """Create temporary directory for test files"""
        temp_path = Path(tempfile.mkdtemp())
        yield temp_path
        shutil.rmtree(temp_path)
    
    def test_read_completed_steps_empty_file(self, temp_dir):
        """Empty events file returns empty set"""
        events_path = temp_dir / "events.jsonl"
        events_path.touch()
        
        completed = read_completed_steps(events_path)
        assert completed == set()
    
    def test_read_completed_steps_no_file(self, temp_dir):
        """Non-existent file returns empty set"""
        events_path = temp_dir / "nonexistent.jsonl"
        
        completed = read_completed_steps(events_path)
        assert completed == set()
    
    def test_read_completed_steps_with_succeeded(self, temp_dir):
        """Reads step.succeeded events correctly"""
        events_path = temp_dir / "events.jsonl"
        
        events = [
            {"type": "job.started", "job_id": "test", "ts": "2025-01-01T00:00:00Z"},
            {"type": "step.started", "job_id": "test", "step": "architect", "ts": "2025-01-01T00:00:01Z"},
            {"type": "step.succeeded", "job_id": "test", "step": "architect", "ts": "2025-01-01T00:00:05Z"},
            {"type": "step.started", "job_id": "test", "step": "builder", "ts": "2025-01-01T00:00:06Z"},
            {"type": "step.succeeded", "job_id": "test", "step": "builder", "ts": "2025-01-01T00:00:10Z"},
        ]
        
        with open(events_path, 'w') as f:
            for event in events:
                f.write(json.dumps(event) + '\n')
        
        completed = read_completed_steps(events_path)
        assert completed == {"architect", "builder"}
    
    def test_read_completed_steps_ignores_failed(self, temp_dir):
        """Ignores step.failed events"""
        events_path = temp_dir / "events.jsonl"
        
        events = [
            {"type": "step.succeeded", "job_id": "test", "step": "architect", "ts": "2025-01-01T00:00:05Z"},
            {"type": "step.failed", "job_id": "test", "step": "builder", "ts": "2025-01-01T00:00:10Z"},
            {"type": "step.succeeded", "job_id": "test", "step": "docs", "ts": "2025-01-01T00:00:15Z"},
        ]
        
        with open(events_path, 'w') as f:
            for event in events:
                f.write(json.dumps(event) + '\n')
        
        completed = read_completed_steps(events_path)
        # Should only include succeeded steps
        assert completed == {"architect", "docs"}
        assert "builder" not in completed


class TestResumeDAGExecution:
    """Test DAG execution with resume functionality"""
    
    @pytest.fixture
    def temp_dir(self):
        """Create temporary directory for test"""
        temp_path = Path(tempfile.mkdtemp())
        (temp_path / "runs" / "test_job").mkdir(parents=True)
        yield temp_path
        shutil.rmtree(temp_path)
    
    @pytest.mark.asyncio
    async def test_resume_skips_completed_steps(self, temp_dir):
        """Resume skips steps that already succeeded"""
        # Setup: Create events.jsonl with architect completed
        events_path = temp_dir / "runs" / "test_job" / "events.jsonl"
        events_path.parent.mkdir(parents=True, exist_ok=True)
        
        # Write event showing architect already completed
        with open(events_path, 'w') as f:
            f.write(json.dumps({
                "type": "step.succeeded",
                "job_id": "test_job",
                "step": "architect",
                "ts": "2025-01-01T00:00:05Z"
            }) + '\n')
        
        # Create DAG: architect → builder → qa
        dag = DAG()
        
        # Track which steps actually executed
        executed_steps = []
        
        async def mock_architect(context, deps):
            executed_steps.append("architect")
            return {"output": "architect_result"}
        
        async def mock_builder(context, deps):
            executed_steps.append("builder")
            return {"output": "builder_result"}
        
        async def mock_qa(context, deps):
            executed_steps.append("qa")
            return {"output": "qa_result"}
        
        dag.add_node(DAGNode(id="architect", fn=mock_architect, needs=[], description="Architect"))
        dag.add_node(DAGNode(id="builder", fn=mock_builder, needs=["architect"], description="Builder"))
        dag.add_node(DAGNode(id="qa", fn=mock_qa, needs=["builder"], description="QA"))
        
        # Create event emitter
        emitter = EventEmitter(events_path)
        
        # Execute with resume=True
        context = {"test": "context"}
        results = await run_dag(
            dag=dag,
            job_id="test_job",
            context=context,
            events=emitter,
            resume=True
        )
        
        emitter.close()
        
        # Assertions
        # 1. Architect should NOT have executed (was already complete)
        assert "architect" not in executed_steps
        
        # 2. Builder and QA should have executed
        assert "builder" in executed_steps
        assert "qa" in executed_steps
        
        # 3. All steps should be in results
        assert "architect" in results
        assert "builder" in results
        assert "qa" in results
        
        # 4. Architect result should be placeholder (resumed)
        assert results["architect"].output.get("resumed") is True
        
        # 5. Events file should have step.skipped for architect
        with open(events_path, 'r') as f:
            events = [json.loads(line) for line in f if line.strip()]
        
        skipped_events = [e for e in events if e.get('type') == 'step.skipped']
        assert len(skipped_events) == 1
        assert skipped_events[0]['step'] == 'architect'
    
    @pytest.mark.asyncio
    async def test_resume_after_failure(self, temp_dir):
        """Resume after mid-DAG failure completes remaining steps"""
        events_path = temp_dir / "runs" / "test_job" / "events.jsonl"
        events_path.parent.mkdir(parents=True, exist_ok=True)
        
        # Simulate previous run where architect succeeded but builder failed
        with open(events_path, 'w') as f:
            f.write(json.dumps({
                "type": "step.succeeded",
                "job_id": "test_job",
                "step": "architect",
                "ts": "2025-01-01T00:00:05Z"
            }) + '\n')
            f.write(json.dumps({
                "type": "step.failed",
                "job_id": "test_job",
                "step": "builder",
                "ts": "2025-01-01T00:00:10Z"
            }) + '\n')
        
        # Create DAG
        dag = DAG()
        executed_steps = []
        
        async def mock_architect(context, deps):
            executed_steps.append("architect")
            return {"data": "arch"}
        
        async def mock_builder(context, deps):
            executed_steps.append("builder")
            # This time it succeeds
            return {"data": "build"}
        
        dag.add_node(DAGNode(id="architect", fn=mock_architect, needs=[]))
        dag.add_node(DAGNode(id="builder", fn=mock_builder, needs=["architect"]))
        
        # Execute with resume
        emitter = EventEmitter(events_path)
        results = await run_dag(
            dag=dag,
            job_id="test_job",
            context={},
            events=emitter,
            resume=True
        )
        emitter.close()
        
        # Assertions
        # 1. Architect should NOT re-execute
        assert "architect" not in executed_steps
        
        # 2. Builder SHOULD execute (it failed before)
        assert "builder" in executed_steps
        
        # 3. Both should be in results
        assert len(results) == 2
    
    @pytest.mark.asyncio
    async def test_resume_false_executes_all(self, temp_dir):
        """When resume=False, all steps execute regardless of events"""
        events_path = temp_dir / "runs" / "test_job" / "events.jsonl"
        events_path.parent.mkdir(parents=True, exist_ok=True)
        
        # Write completed step
        with open(events_path, 'w') as f:
            f.write(json.dumps({
                "type": "step.succeeded",
                "job_id": "test_job",
                "step": "step1",
                "ts": "2025-01-01T00:00:05Z"
            }) + '\n')
        
        # Create simple DAG
        dag = DAG()
        executed = []
        
        async def step_fn(context, deps):
            executed.append("step1")
            return {}
        
        dag.add_node(DAGNode(id="step1", fn=step_fn, needs=[]))
        
        emitter = EventEmitter(events_path)
        
        # Execute with resume=False (default)
        results = await run_dag(
            dag=dag,
            job_id="test_job",
            context={},
            events=emitter,
            resume=False  # Explicit
        )
        emitter.close()
        
        # Step should have executed
        assert "step1" in executed
        assert results["step1"].output.get("resumed") is not True
    
    @pytest.mark.asyncio
    async def test_resume_with_no_completed_steps(self, temp_dir):
        """Resume with no prior completion executes normally"""
        events_path = temp_dir / "runs" / "test_job" / "events.jsonl"
        events_path.parent.mkdir(parents=True, exist_ok=True)
        
        # Empty events file
        events_path.touch()
        
        dag = DAG()
        executed = []
        
        async def step_fn(context, deps):
            executed.append("step1")
            return {}
        
        dag.add_node(DAGNode(id="step1", fn=step_fn, needs=[]))
        
        emitter = EventEmitter(events_path)
        results = await run_dag(
            dag=dag,
            job_id="test_job",
            context={},
            events=emitter,
            resume=True
        )
        emitter.close()
        
        # All steps should execute normally
        assert "step1" in executed
        assert len(results) == 1


class TestResumeIntegration:
    """Integration tests for resume with real-world scenarios"""
    
    @pytest.mark.asyncio
    async def test_resume_parallel_steps(self):
        """Resume works correctly with parallel DAG execution"""
        temp_dir = Path(tempfile.mkdtemp())
        events_path = temp_dir / "runs" / "test_job" / "events.jsonl"
        events_path.parent.mkdir(parents=True, exist_ok=True)
        
        try:
            # Simulate: architect done, builder and docs both pending
            with open(events_path, 'w') as f:
                f.write(json.dumps({
                    "type": "step.succeeded",
                    "job_id": "test_job",
                    "step": "architect",
                    "ts": "2025-01-01T00:00:05Z"
                }) + '\n')
            
            # DAG: architect → {builder, docs} → qa
            dag = DAG()
            executed = []
            
            async def track(name):
                async def fn(ctx, deps):
                    executed.append(name)
                    await asyncio.sleep(0.01)  # Simulate work
                    return {"name": name}
                return fn
            
            dag.add_node(DAGNode(id="architect", fn=await track("architect"), needs=[]))
            dag.add_node(DAGNode(id="builder", fn=await track("builder"), needs=["architect"]))
            dag.add_node(DAGNode(id="docs", fn=await track("docs"), needs=["architect"]))
            dag.add_node(DAGNode(id="qa", fn=await track("qa"), needs=["builder", "docs"]))
            
            emitter = EventEmitter(events_path)
            results = await run_dag(
                dag=dag,
                job_id="test_job",
                context={},
                events=emitter,
                concurrency=2,
                resume=True
            )
            emitter.close()
            
            # Assertions
            assert "architect" not in executed  # Skipped
            assert "builder" in executed  # Executed
            assert "docs" in executed  # Executed
            assert "qa" in executed  # Executed
            
            # All 4 should be in results
            assert len(results) == 4
            
        finally:
            shutil.rmtree(temp_dir)
