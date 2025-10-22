"""Tests for DAG Execution"""

import pytest
import asyncio
from datetime import datetime

from src.core.dag import DAG, DAGNode, run_dag, topological_sort
from src.core.events import EventEmitter
from src.core.models import StepResult


class TestDAG:
    """Test DAG structure and validation"""
    
    def test_add_node(self):
        """Can add nodes to DAG"""
        dag = DAG()
        node = DAGNode(id="step1", fn=lambda ctx, deps: None, needs=[])
        
        dag.add_node(node)
        assert "step1" in dag.nodes
    
    def test_duplicate_node_fails(self):
        """Adding duplicate node raises error"""
        dag = DAG()
        node = DAGNode(id="step1", fn=lambda ctx, deps: None, needs=[])
        
        dag.add_node(node)
        with pytest.raises(ValueError, match="already exists"):
            dag.add_node(node)
    
    def test_validate_missing_dependency(self):
        """Validation fails if dependency doesn't exist"""
        dag = DAG()
        dag.add_node(DAGNode(id="step1", fn=lambda: None, needs=["nonexistent"]))
        
        with pytest.raises(ValueError, match="doesn't exist"):
            dag.validate()
    
    def test_validate_cycle_detection(self):
        """Validation detects cycles in DAG"""
        dag = DAG()
        dag.add_node(DAGNode(id="a", fn=lambda ctx, deps: None, needs=["b"]))
        dag.add_node(DAGNode(id="b", fn=lambda ctx, deps: None, needs=["c"]))
        dag.add_node(DAGNode(id="c", fn=lambda ctx, deps: None, needs=["a"]))  # Cycle!
        
        with pytest.raises(ValueError, match="cycle"):
            dag.validate()
    
    def test_validate_valid_dag(self):
        """Valid DAG passes validation"""
        dag = DAG()
        dag.add_node(DAGNode(id="a", fn=lambda ctx, deps: None, needs=[]))
        dag.add_node(DAGNode(id="b", fn=lambda ctx, deps: None, needs=["a"]))
        dag.add_node(DAGNode(id="c", fn=lambda ctx, deps: None, needs=["a"]))
        dag.add_node(DAGNode(id="d", fn=lambda ctx, deps: None, needs=["b", "c"]))
        
        # Should not raise
        dag.validate()
    
    def test_get_ready_nodes_empty_dag(self):
        """get_ready_nodes with no completed steps returns root nodes"""
        dag = DAG()
        dag.add_node(DAGNode(id="a", fn=lambda ctx, deps: None, needs=[]))
        dag.add_node(DAGNode(id="b", fn=lambda ctx, deps: None, needs=["a"]))
        
        ready = dag.get_ready_nodes(completed=set())
        assert len(ready) == 1
        assert ready[0].id == "a"
    
    def test_get_ready_nodes_after_completion(self):
        """get_ready_nodes returns nodes whose deps are complete"""
        dag = DAG()
        dag.add_node(DAGNode(id="a", fn=lambda ctx, deps: None, needs=[]))
        dag.add_node(DAGNode(id="b", fn=lambda ctx, deps: None, needs=["a"]))
        dag.add_node(DAGNode(id="c", fn=lambda ctx, deps: None, needs=["a"]))
        
        ready = dag.get_ready_nodes(completed={"a"})
        assert len(ready) == 2
        assert {n.id for n in ready} == {"b", "c"}


class TestTopologicalSort:
    """Test topological sorting of DAG"""
    
    def test_simple_linear_dag(self):
        """Linear DAG produces sequential order"""
        dag = DAG()
        dag.add_node(DAGNode(id="a", fn=lambda ctx, deps: None, needs=[]))
        dag.add_node(DAGNode(id="b", fn=lambda ctx, deps: None, needs=["a"]))
        dag.add_node(DAGNode(id="c", fn=lambda ctx, deps: None, needs=["b"]))
        
        order = topological_sort(dag)
        assert order == ["a", "b", "c"]
    
    def test_parallel_branches(self):
        """DAG with parallel branches has valid ordering"""
        dag = DAG()
        dag.add_node(DAGNode(id="a", fn=lambda ctx, deps: None, needs=[]))
        dag.add_node(DAGNode(id="b", fn=lambda ctx, deps: None, needs=["a"]))
        dag.add_node(DAGNode(id="c", fn=lambda ctx, deps: None, needs=["a"]))
        dag.add_node(DAGNode(id="d", fn=lambda ctx, deps: None, needs=["b", "c"]))
        
        order = topological_sort(dag)
        assert order[0] == "a"  # Must be first
        assert order[3] == "d"  # Must be last
        assert {"b", "c"} == {order[1], order[2]}  # b,c in middle (any order)


@pytest.mark.asyncio
class TestRunDAG:
    """Test DAG execution"""
    
    async def test_simple_dag_execution(self, tmp_path):
        """Simple DAG executes all nodes"""
        execution_order = []
        
        async def step_a(ctx, deps):
            execution_order.append("a")
            return {"result": "a_output"}
        
        async def step_b(ctx, deps):
            execution_order.append("b")
            assert "a" in deps
            assert deps["a"].output["result"] == "a_output"
            return {"result": "b_output"}
        
        dag = DAG()
        dag.add_node(DAGNode(id="a", fn=step_a, needs=[]))
        dag.add_node(DAGNode(id="b", fn=step_b, needs=["a"]))
        
        # Create mock event emitter
        events_path = tmp_path / "events.jsonl"
        events = EventEmitter(events_path)
        
        results = await run_dag(
            dag=dag,
            job_id="test_job",
            context={},
            events=events,
            concurrency=2
        )
        
        assert execution_order == ["a", "b"]
        assert "a" in results
        assert "b" in results
        assert results["a"].status == "succeeded"
        assert results["b"].status == "succeeded"
        
        events.close()
    
    async def test_parallel_execution(self, tmp_path):
        """Parallel branches execute concurrently"""
        execution_times = {}
        
        async def step_a(ctx, deps):
            execution_times["a"] = datetime.utcnow()
            await asyncio.sleep(0.01)
            return {"result": "a"}
        
        async def step_b(ctx, deps):
            execution_times["b"] = datetime.utcnow()
            await asyncio.sleep(0.01)
            return {"result": "b"}
        
        async def step_c(ctx, deps):
            execution_times["c"] = datetime.utcnow()
            await asyncio.sleep(0.01)
            return {"result": "c"}
        
        # Build DAG: a -> {b, c} (b and c should run in parallel)
        dag = DAG()
        dag.add_node(DAGNode(id="a", fn=step_a, needs=[]))
        dag.add_node(DAGNode(id="b", fn=step_b, needs=["a"]))
        dag.add_node(DAGNode(id="c", fn=step_c, needs=["a"]))
        
        events = EventEmitter(tmp_path / "events.jsonl")
        results = await run_dag(dag, "test", {}, events, concurrency=4)
        events.close()
        
        # b and c should start within 100ms of each other (parallel)
        time_diff = abs((execution_times["b"] - execution_times["c"]).total_seconds())
        assert time_diff < 0.1, f"b and c should run in parallel, but diff was {time_diff}s"
    
    async def test_dependency_results_passed(self, tmp_path):
        """Dependency results are passed to downstream nodes"""
        async def step_a(ctx, deps):
            return {"value": 42}
        
        async def step_b(ctx, deps):
            # Should receive result from step a
            assert "a" in deps
            assert deps["a"].output["value"] == 42
            return {"value": deps["a"].output["value"] * 2}
        
        dag = DAG()
        dag.add_node(DAGNode(id="a", fn=step_a, needs=[]))
        dag.add_node(DAGNode(id="b", fn=step_b, needs=["a"]))
        
        events = EventEmitter(tmp_path / "events.jsonl")
        results = await run_dag(dag, "test", {}, events)
        events.close()
        
        assert results["b"].output["value"] == 84
    
    async def test_step_failure_stops_dag(self, tmp_path):
        """Failed step stops DAG execution"""
        async def step_a(ctx, deps):
            raise ValueError("Intentional failure")
        
        async def step_b(ctx, deps):
            pytest.fail("Step b should not execute after a fails")
        
        dag = DAG()
        dag.add_node(DAGNode(id="a", fn=step_a, needs=[]))
        dag.add_node(DAGNode(id="b", fn=step_b, needs=["a"]))
        
        events = EventEmitter(tmp_path / "events.jsonl")
        
        with pytest.raises(ValueError, match="Intentional failure"):
            await run_dag(dag, "test", {}, events)
        
        events.close()
    
    async def test_concurrency_limit(self, tmp_path):
        """Concurrency limit is respected"""
        active_count = 0
        max_concurrent = 0
        lock = asyncio.Lock()
        
        async def step_fn(ctx, deps):
            nonlocal active_count, max_concurrent
            
            async with lock:
                active_count += 1
                max_concurrent = max(max_concurrent, active_count)
            
            await asyncio.sleep(0.05)
            
            async with lock:
                active_count -= 1
            
            return {}
        
        # Create 5 parallel tasks
        dag = DAG()
        dag.add_node(DAGNode(id="root", fn=step_fn, needs=[]))
        for i in range(4):
            dag.add_node(DAGNode(id=f"step{i}", fn=step_fn, needs=["root"]))
        
        events = EventEmitter(tmp_path / "events.jsonl")
        await run_dag(dag, "test", {}, events, concurrency=2)  # Limit to 2
        events.close()
        
        # Max concurrent should not exceed 2
        assert max_concurrent <= 2
    
    async def test_timeout_enforced(self, tmp_path):
        """DAG timeout stops long-running execution"""
        async def slow_step(ctx, deps):
            await asyncio.sleep(10)  # Too slow
            return {}
        
        dag = DAG()
        dag.add_node(DAGNode(id="slow", fn=slow_step, needs=[]))
        
        events = EventEmitter(tmp_path / "events.jsonl")
        
        with pytest.raises(asyncio.TimeoutError):
            await run_dag(dag, "test", {}, events, timeout_s=1)  # 1 second timeout
        
        events.close()

