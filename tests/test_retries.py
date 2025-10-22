"""Tests for provider retry logic and circuit breaker behavior."""

import types

import httpx
import pytest

from src.providers import ProviderError
from src.providers.ollama import OllamaProvider


def _make_timeout():
    """Helper to create a timeout exception."""
    return httpx.TimeoutException("timeout")


def test_provider_retries_on_timeout():
    """Ollama provider should retry on httpx timeouts."""
    provider = OllamaProvider(
        timeout_s=1,
        max_retries=3,
        cb_threshold=5,
        cb_cooldown_s=60.0,
    )

    call_count = {"count": 0}

    def flaky_internal(self, messages, **kwargs):
        call_count["count"] += 1
        if call_count["count"] < 3:
            raise _make_timeout()
        return "recovered"

    provider._generate_internal = types.MethodType(flaky_internal, provider)  # type: ignore[attr-defined]

    result = provider.generate([{"role": "user", "content": "hello"}])

    try:
        assert result == "recovered"
        assert call_count["count"] == 3  # two failures + final success
    finally:
        provider._client.close()


def test_circuit_breaker_opens_after_threshold():
    """Circuit breaker should open after consecutive failures."""
    provider = OllamaProvider(
        timeout_s=1,
        max_retries=3,
        cb_threshold=2,
        cb_cooldown_s=60.0,
    )

    call_count = {"count": 0}

    def always_timeout(self, messages, **kwargs):
        call_count["count"] += 1
        raise _make_timeout()

    provider._generate_internal = types.MethodType(always_timeout, provider)  # type: ignore[attr-defined]

    with pytest.raises(ProviderError) as excinfo:
        provider.generate([{"role": "user", "content": "hello"}])

    try:
        assert excinfo.value.kind == "circuit_breaker"
        # Underlying call should be attempted twice before breaker opens
        assert call_count["count"] == 2
    finally:
        provider._client.close()
