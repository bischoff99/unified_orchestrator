"""Anthropic Provider Adapter"""

import httpx
from typing import Any, Optional
from tenacity import retry, stop_after_attempt, wait_exponential, retry_if_exception_type
from . import ProviderError
from src.core.circuit_breaker import CircuitBreaker, CircuitBreakerOpen


class AnthropicProvider:
    """
    Anthropic (Claude) provider adapter with retries and timeout handling.
    
    Supports Claude 3.5 Sonnet, Claude 3 Opus, and other Claude models.
    """
    
    def __init__(
        self,
        model: str = "claude-3-5-sonnet-20241022",
        api_key: Optional[str] = None,
        timeout_s: int = 120,
        max_retries: int = 3,
        cb_threshold: int = 5,
        cb_cooldown_s: float = 60.0,
        **model_opts
    ):
        self._model = model
        self._api_key = api_key
        self._timeout_s = timeout_s
        self._max_retries = max_retries
        self._model_opts = model_opts
        
        if not api_key:
            import os
            self._api_key = os.getenv("ANTHROPIC_API_KEY")
            if not self._api_key:
                raise ValueError("Anthropic API key required (set ANTHROPIC_API_KEY)")
        
        self._client = httpx.Client(
            base_url="https://api.anthropic.com/v1",
            headers={
                "x-api-key": self._api_key,
                "anthropic-version": "2023-06-01"
            },
            timeout=httpx.Timeout(timeout_s, connect=10.0)
        )

        # Circuit breaker for fault tolerance
        self._circuit_breaker = CircuitBreaker(threshold=cb_threshold, cooldown=cb_cooldown_s)
    
    @property
    def name(self) -> str:
        return "anthropic"
    
    @property
    def model(self) -> str:
        return self._model
    
    @retry(
        stop=stop_after_attempt(3),
        wait=wait_exponential(multiplier=1, min=2, max=10),
        retry=retry_if_exception_type((httpx.TimeoutException, httpx.HTTPStatusError)),
        reraise=True
    )
    def generate(
        self,
        messages: list[dict],
        **opts: Any
    ) -> str:
        """
        Generate completion using Anthropic API.

        Args:
            messages: Message history
            **opts: Override options

        Returns:
            Generated text

        Raises:
            ProviderError: On timeout, rate limit, or API error
        """
        # Check circuit breaker before making request
        try:
            return self._circuit_breaker.call(self._generate_internal, messages, **opts)
        except CircuitBreakerOpen as e:
            raise ProviderError(
                str(e),
                kind="circuit_breaker",
                provider="anthropic"
            )

    def _generate_internal(self, messages: list[dict], **opts: Any) -> str:
        """Internal generation logic wrapped by circuit breaker"""
        options = {**self._model_opts, **opts}

        # Separate system message from conversation
        system_msg = None
        conversation = []

        for msg in messages:
            if msg.get("role") == "system":
                system_msg = msg.get("content", "")
            else:
                conversation.append(msg)

        payload = {
            "model": self._model,
            "messages": conversation,
            "max_tokens": options.get("max_tokens", 8192),
            "temperature": options.get("temperature", 0.1),
        }

        if system_msg:
            payload["system"] = system_msg

        if options.get("stop"):
            payload["stop_sequences"] = options["stop"]

        try:
            response = self._client.post(
                "/messages",
                json=payload
            )
            response.raise_for_status()

            result = response.json()
            return result["content"][0]["text"]

        except httpx.TimeoutException as e:
            raise ProviderError(
                f"Anthropic request timed out after {self._timeout_s}s",
                kind="timeout",
                provider="anthropic",
                original_error=e
            )
        except httpx.HTTPStatusError as e:
            if e.response.status_code == 429:
                raise ProviderError(
                    "Anthropic rate limit exceeded",
                    kind="rate_limit",
                    provider="anthropic",
                    original_error=e
                )
            elif e.response.status_code == 401:
                raise ProviderError(
                    "Anthropic authentication failed - check API key",
                    kind="auth",
                    provider="anthropic",
                    original_error=e
                )
            else:
                raise ProviderError(
                    f"Anthropic API error: {e.response.status_code}",
                    kind="provider",
                    provider="anthropic",
                    original_error=e
                )
        except Exception as e:
            raise ProviderError(
                f"Anthropic error: {str(e)}",
                kind="provider",
                provider="anthropic",
                original_error=e
            )
    
    def tool_call(
        self,
        name: str,
        args: dict,
        **opts: Any
    ) -> dict:
        """
        Execute tool call using Claude's tool use API.
        
        Args:
            name: Tool name
            args: Tool arguments
            **opts: Additional options
            
        Returns:
            Tool execution result
        """
        options = {**self._model_opts, **opts}
        
        messages = [
            {"role": "user", "content": f"Use the {name} tool with these arguments: {args}"}
        ]
        
        payload = {
            "model": self._model,
            "messages": messages,
            "max_tokens": options.get("max_tokens", 4096),
            "tools": [{
                "name": name,
                "description": f"Execute {name}",
                "input_schema": {
                    "type": "object",
                    "properties": args
                }
            }]
        }
        
        try:
            response = self._client.post("/messages", json=payload)
            response.raise_for_status()
            
            result = response.json()
            tool_use = None
            
            for content in result.get("content", []):
                if content.get("type") == "tool_use":
                    tool_use = content
                    break
            
            if tool_use:
                return {
                    "tool": name,
                    "args": args,
                    "result": tool_use.get("input", {})
                }
            else:
                return {"tool": name, "args": args, "result": None}
                
        except Exception as e:
            raise ProviderError(
                f"Anthropic tool call failed: {str(e)}",
                kind="tool",
                provider="anthropic",
                original_error=e
            )
    
    def __del__(self):
        """Cleanup HTTP client"""
        if hasattr(self, '_client'):
            self._client.close()
