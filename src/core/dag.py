"""DAG (Directed Acyclic Graph) Runner

Executes workflow steps in parallel based on dependencies.
Replaces linear sequential execution with concurrent task execution.
"""

import asyncio
from typing import Callable, Any, Optional
from dataclasses import dataclass
from datetime import datetime
from pathlib import Path

from .models import StepResult, Failure
from .events import EventEmitter


@dataclass
class DAGNode:
    """
    Represents a single step in the DAG.
    
    Attributes:
        id: Unique step identifier (e.g., 'architect', 'builder')
        fn: Async function to execute for this step
        needs: List of step IDs that must complete before this one
        description: Human-readable description
    """
    id: str
    fn: Callable[..., Any]
    needs: list[str]
    description: str = ""


class DAG:
    """
    Directed Acyclic Graph for workflow execution.
    
    Manages dependencies between steps and ensures correct execution order.
    """
    
    def __init__(self):
        self.nodes: dict[str, DAGNode] = {}
    
    def add_node(self, node: DAGNode):
        """Add a node to the DAG"""
        if node.id in self.nodes:
            raise ValueError(f"Node {node.id} already exists")
        self.nodes[node.id] = node
    
    def validate(self):
        """
        Validate DAG has no cycles and all dependencies exist.
        
        Raises:
            ValueError: If DAG is invalid (cycles or missing deps)
        """
        # Check all dependencies exist
        for node in self.nodes.values():
            for dep in node.needs:
                if dep not in self.nodes:
                    raise ValueError(
                        f"Node {node.id} depends on {dep} which doesn't exist"
                    )
        
        # Check for cycles using DFS
        visited = set()
        rec_stack = set()
        
        def has_cycle(node_id: str) -> bool:
            visited.add(node_id)
            rec_stack.add(node_id)
            
            node = self.nodes[node_id]
            for dep in node.needs:
                if dep not in visited:
                    if has_cycle(dep):
                        return True
                elif dep in rec_stack:
                    return True
            
            rec_stack.remove(node_id)
            return False
        
        for node_id in self.nodes:
            if node_id not in visited:
                if has_cycle(node_id):
                    raise ValueError("DAG contains a cycle")
    
    def get_ready_nodes(self, completed: set[str]) -> list[DAGNode]:
        """
        Get nodes that are ready to execute.
        
        A node is ready if all its dependencies have completed.
        
        Args:
            completed: Set of completed step IDs
            
        Returns:
            List of nodes ready to execute
        """
        ready = []
        for node in self.nodes.values():
            if node.id not in completed:
                if all(dep in completed for dep in node.needs):
                    ready.append(node)
        return ready


async def run_dag(
    dag: DAG,
    job_id: str,
    context: dict[str, Any],
    events: EventEmitter,
    concurrency: int = 4,
    timeout_s: Optional[int] = None
) -> dict[str, StepResult]:
    """
    Execute DAG with controlled concurrency.
    
    Steps execute in parallel when dependencies allow, respecting
    the concurrency limit.
    
    Args:
        dag: DAG to execute
        job_id: Job identifier for event logging
        context: Shared context passed to all step functions
        events: Event emitter for logging
        concurrency: Maximum concurrent tasks
        timeout_s: Overall timeout for entire DAG
        
    Returns:
        Dict mapping step_id to StepResult
        
    Raises:
        asyncio.TimeoutError: If overall timeout exceeded
        Exception: If any step fails
    """
    dag.validate()
    
    completed: set[str] = set()
    results: dict[str, StepResult] = {}
    semaphore = asyncio.Semaphore(concurrency)
    
    async def execute_node(node: DAGNode) -> StepResult:
        """Execute a single node with semaphore control"""
        async with semaphore:
            step_start = datetime.utcnow()
            
            # Emit step.started event
            events.step_started(job_id, node.id, node.needs)
            
            try:
                # Execute step function
                # Pass results from dependencies
                dep_results = {dep_id: results[dep_id] for dep_id in node.needs}
                
                # Call step function (may be sync or async)
                if asyncio.iscoroutinefunction(node.fn):
                    output = await node.fn(context, dep_results)
                else:
                    output = await asyncio.to_thread(node.fn, context, dep_results)
                
                step_end = datetime.utcnow()
                duration = (step_end - step_start).total_seconds()
                
                # Create success result
                result = StepResult(
                    step_id=node.id,
                    status="succeeded",
                    output=output if isinstance(output, dict) else {"result": output},
                    duration_s=duration,
                    started_at=step_start,
                    finished_at=step_end,
                )
                
                # Emit step.succeeded event
                events.step_succeeded(job_id, node.id, duration)
                
                return result
                
            except Exception as e:
                step_end = datetime.utcnow()
                duration = (step_end - step_start).total_seconds()
                
                # Determine failure kind
                error_kind = "provider"
                if "timeout" in str(e).lower():
                    error_kind = "timeout"
                elif "validation" in str(e).lower():
                    error_kind = "validation"
                elif "tool" in str(e).lower():
                    error_kind = "tool"
                
                # Create failure
                failure = Failure(
                    kind=error_kind,
                    step=node.id,
                    message=str(e),
                    data={"exception_type": type(e).__name__}
                )
                
                # Create failed result
                result = StepResult(
                    step_id=node.id,
                    status="failed",
                    failure=failure,
                    duration_s=duration,
                    started_at=step_start,
                    finished_at=step_end,
                )
                
                # Emit step.failed event
                events.step_failed(job_id, node.id, error_kind, str(e))
                
                # Re-raise to stop DAG execution
                raise
    
    async def run_wave():
        """Execute one wave of ready nodes"""
        ready = dag.get_ready_nodes(completed)
        if not ready:
            return False  # No more work
        
        # Execute all ready nodes in parallel
        tasks = [execute_node(node) for node in ready]
        wave_results = await asyncio.gather(*tasks, return_exceptions=True)
        
        # Process results
        for node, result in zip(ready, wave_results):
            if isinstance(result, Exception):
                # Failure - propagate up
                raise result
            else:
                # Success - record and mark complete
                results[node.id] = result
                completed.add(node.id)
        
        return True  # More work may be available
    
    # Execute waves until complete
    async def execute_all():
        while len(completed) < len(dag.nodes):
            has_work = await run_wave()
            if not has_work and len(completed) < len(dag.nodes):
                # Deadlock - some nodes can't execute
                pending = set(dag.nodes.keys()) - completed
                raise RuntimeError(
                    f"DAG deadlock: nodes {pending} cannot execute. "
                    f"Check dependencies."
                )
    
    # Run with optional timeout
    if timeout_s:
        await asyncio.wait_for(execute_all(), timeout=timeout_s)
    else:
        await execute_all()
    
    return results


def topological_sort(dag: DAG) -> list[str]:
    """
    Return topological ordering of DAG nodes.
    
    Useful for understanding execution order.
    
    Args:
        dag: DAG to sort
        
    Returns:
        List of node IDs in topological order
    """
    dag.validate()
    
    in_degree = {node_id: 0 for node_id in dag.nodes}
    
    # Count incoming edges
    for node in dag.nodes.values():
        for dep in node.needs:
            in_degree[node.id] += 1
    
    # Start with nodes that have no dependencies
    queue = [node_id for node_id, degree in in_degree.items() if degree == 0]
    result = []
    
    while queue:
        node_id = queue.pop(0)
        result.append(node_id)
        
        # Reduce in-degree of dependent nodes
        for other_id, node in dag.nodes.items():
            if node_id in node.needs:
                in_degree[other_id] -= 1
                if in_degree[other_id] == 0:
                    queue.append(other_id)
    
    return result

