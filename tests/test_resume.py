"""Tests for DAG resume functionality."""

from pathlib import Path

import pytest

from src.core.dag import DAG, DAGNode, run_dag
from src.core.events import EventEmitter


@pytest.mark.asyncio
async def test_resume_skips_completed_steps(tmp_path, monkeypatch):
    """Resume mode should skip steps that already succeeded."""
    monkeypatch.chdir(tmp_path)

    job_id = "job_resume"
    events_path = Path("runs") / job_id / "events.jsonl"
    events_path.parent.mkdir(parents=True, exist_ok=True)

    # First run executes both steps
    emitter = EventEmitter(events_path)
    executed_first: list[str] = []

    async def step_a(context, deps):
        executed_first.append("a")
        return {"result": "a"}

    async def step_b(context, deps):
        executed_first.append("b")
        return {"result": "b"}

    dag = DAG()
    dag.add_node(DAGNode(id="a", fn=step_a, needs=[]))
    dag.add_node(DAGNode(id="b", fn=step_b, needs=["a"]))

    await run_dag(dag, job_id, {}, emitter, concurrency=2, resume=False)
    emitter.close()

    assert executed_first == ["a", "b"]

    # Second run should skip both steps using cached events
    emitter_resume = EventEmitter(events_path)
    executed_resume: list[str] = []

    async def step_a_resume(context, deps):
        executed_resume.append("a")
        return {"result": "a"}

    async def step_b_resume(context, deps):
        executed_resume.append("b")
        return {"result": "b"}

    dag_resume = DAG()
    dag_resume.add_node(DAGNode(id="a", fn=step_a_resume, needs=[]))
    dag_resume.add_node(DAGNode(id="b", fn=step_b_resume, needs=["a"]))

    results = await run_dag(
        dag_resume,
        job_id,
        {},
        emitter_resume,
        concurrency=2,
        resume=True,
    )
    emitter_resume.close()

    # No new executions should occur
    assert executed_resume == []
    assert set(results.keys()) == {"a", "b"}
    assert all(result.output.get("resumed") is True for result in results.values())


@pytest.mark.asyncio
async def test_resume_after_failure(tmp_path, monkeypatch):
    """Resume should rerun only the failed steps."""
    monkeypatch.chdir(tmp_path)

    job_id = "job_resume_failure"
    events_path = Path("runs") / job_id / "events.jsonl"
    events_path.parent.mkdir(parents=True, exist_ok=True)

    emitter = EventEmitter(events_path)
    executed_initial: list[str] = []

    async def step_ok(context, deps):
        executed_initial.append("ok")
        return {"result": "ok"}

    async def step_fail(context, deps):
        executed_initial.append("fail")
        raise RuntimeError("boom")

    dag = DAG()
    dag.add_node(DAGNode(id="ok", fn=step_ok, needs=[]))
    dag.add_node(DAGNode(id="fail", fn=step_fail, needs=["ok"]))

    with pytest.raises(RuntimeError):
        await run_dag(dag, job_id, {}, emitter, concurrency=2, resume=False)
    emitter.close()

    assert executed_initial == ["ok", "fail"]

    # Resume should skip 'ok' and rerun 'fail'
    emitter_resume = EventEmitter(events_path)
    executed_resume: list[str] = []

    async def step_ok_resume(context, deps):
        executed_resume.append("ok")
        return {"result": "ok"}

    async def step_fail_resume(context, deps):
        executed_resume.append("fail")
        return {"result": "recovered"}

    dag_resume = DAG()
    dag_resume.add_node(DAGNode(id="ok", fn=step_ok_resume, needs=[]))
    dag_resume.add_node(DAGNode(id="fail", fn=step_fail_resume, needs=["ok"]))

    results = await run_dag(
        dag_resume,
        job_id,
        {},
        emitter_resume,
        concurrency=2,
        resume=True,
    )
    emitter_resume.close()

    # Only the failing step should rerun
    assert executed_resume == ["fail"]
    assert results["ok"].output.get("resumed") is True
    assert results["fail"].output.get("resumed") is not True
    assert results["fail"].status == "succeeded"
