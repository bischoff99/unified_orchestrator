"""Tests for caching behavior in DAG orchestrator."""

import shutil
from pathlib import Path

import pytest

from src.core.cache import compute_cache_key
from src.core.models import JobSpec
from src.orchestrator.dag_orchestrator import DAGOrchestrator


def test_cache_key_deterministic():
    """compute_cache_key returns stable values for identical inputs."""
    provider = {"name": "ollama", "model": "llama3", "opts": {"temperature": 0.1}}
    inputs = {"task": "build notes app"}

    key_one = compute_cache_key(provider, "architect", inputs, code_version="abc123")
    key_two = compute_cache_key(provider, "architect", inputs, code_version="abc123")
    key_diff = compute_cache_key(
        provider,
        "architect",
        {"task": "different"},
        code_version="abc123",
    )

    assert key_one == key_two
    assert key_one != key_diff


class DummyProvider:
    """Simple provider mock that records generate() invocations."""

    name = "dummy"

    def __init__(self):
        self.calls = 0

    def generate(self, messages, **kwargs):
        self.calls += 1
        return "cached-response"


class DummyEvents:
    """Collect cache hit/miss counts for assertions."""

    def __init__(self):
        self.cache_hits = 0
        self.cache_misses = 0

    def cache_hit(self, job_id, step_id, cache_key):
        self.cache_hits += 1

    def cache_miss(self, job_id, step_id, cache_key):
        self.cache_misses += 1

    def provider_call(self, job_id, step_id, provider, duration_s):
        # Provider call emission not needed for this test
        pass
    
    def llm_request(self, job_id, step_id, provider, model, prompt_tokens=0):
        pass
    
    def llm_response(
        self,
        job_id,
        step_id,
        provider,
        duration_s,
        tokens_in=0,
        tokens_out=0,
        success=True
    ):
        pass


@pytest.mark.asyncio
async def test_second_run_uses_cache():
    """
    Second invocation with identical inputs should reuse cached response.
    """
    job_id = "job_test_cache"
    run_dir = Path("runs") / job_id
    if run_dir.exists():
        shutil.rmtree(run_dir)

    spec = JobSpec(
        project="cache-test",
        task_description="Verify cache reuse",
        provider="ollama",
    )
    orchestrator = DAGOrchestrator(spec)

    provider = DummyProvider()
    events = DummyEvents()

    context = {
        "provider": provider,
        "events": events,
        "job_id": job_id,
    }

    messages = [{"role": "user", "content": "Generate something"}]
    inputs = {"task": "generate"}

    # First call should miss the cache and invoke provider
    response_1, cache_hit_1 = await orchestrator._call_provider_with_cache(  # noqa: SLF001
        step_id="architect",
        messages=messages,
        context=context,
        inputs=inputs,
    )

    # Second call should hit the cache and skip provider invocation
    response_2, cache_hit_2 = await orchestrator._call_provider_with_cache(  # noqa: SLF001
        step_id="architect",
        messages=messages,
        context=context,
        inputs=inputs,
    )

    try:
        assert response_1 == "cached-response"
        assert response_2 == "cached-response"
        assert cache_hit_1 is False
        assert cache_hit_2 is True
        assert provider.calls == 1, "Provider should be called only once"
        assert events.cache_misses == 1
        assert events.cache_hits == 1
    finally:
        if run_dir.exists():
            shutil.rmtree(run_dir)
