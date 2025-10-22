"""Ollama Provider Adapter"""

import httpx
from typing import Any, Optional
from tenacity import retry, stop_after_attempt, wait_exponential, retry_if_exception_type
from . import ProviderError
from src.core.circuit_breaker import CircuitBreaker, CircuitBreakerOpen


class OllamaProvider:
    """
    Ollama provider adapter with automatic retries and timeout handling.
    
    Supports local Ollama server for models like CodeLlama, Llama3.1, Mistral.
    """
    
    def __init__(
        self,
        model: str = "codellama:13b-instruct",
        base_url: str = "http://localhost:11434",
        timeout_s: int = 120,
        max_retries: int = 3,
        cb_threshold: int = 5,
        cb_cooldown_s: float = 60.0,
        **model_opts
    ):
        self._model = model
        self._base_url = base_url.rstrip('/')
        self._timeout_s = timeout_s
        self._max_retries = max_retries
        self._model_opts = model_opts
        self._timeout = httpx.Timeout(timeout_s, connect=10.0, read=timeout_s, write=timeout_s)
        self._client = httpx.Client(timeout=self._timeout)

        # Circuit breaker for fault tolerance
        self._circuit_breaker = CircuitBreaker(threshold=cb_threshold, cooldown=cb_cooldown_s)
    
    @property
    def name(self) -> str:
        return "ollama"
    
    @property
    def model(self) -> str:
        return self._model
    
    @retry(
        stop=stop_after_attempt(3),
        wait=wait_exponential(multiplier=1, min=2, max=10),
        retry=retry_if_exception_type((httpx.TimeoutException, httpx.ConnectError)),
        reraise=True
    )
    def generate(
        self,
        messages: list[dict],
        **opts: Any
    ) -> str:
        """
        Generate completion using Ollama API.

        Args:
            messages: List of message dicts [{"role": "user", "content": "..."}]
            **opts: Override options (temperature, max_tokens, etc.)

        Returns:
            Generated text response

        Raises:
            ProviderError: On timeout or connection failure after retries
        """
        # Check circuit breaker before making request
        try:
            return self._circuit_breaker.call(self._generate_internal, messages, **opts)
        except CircuitBreakerOpen as e:
            raise ProviderError(
                str(e),
                kind="circuit_breaker",
                provider="ollama"
            )

    def _generate_internal(self, messages: list[dict], **opts: Any) -> str:
        """Internal generation logic wrapped by circuit breaker"""
        # Merge options
        options = {**self._model_opts, **opts}

        # Convert messages to Ollama format
        prompt = self._messages_to_prompt(messages)

        payload = {
            "model": self._model,
            "prompt": prompt,
            "stream": False,
            "options": {
                "temperature": options.get("temperature", 0.1),
                "num_predict": options.get("max_tokens", 8192),
                "num_ctx": options.get("num_ctx", 8192),
                "num_thread": options.get("num_thread", 14),
                "num_batch": options.get("num_batch", 512),
            }
        }

        try:
            response = self._client.post(
                f"{self._base_url}/api/generate",
                json=payload,
            )
            response.raise_for_status()

            result = response.json()
            return result.get("response", "")

        except httpx.TimeoutException as e:
            raise ProviderError(
                f"Ollama request timed out after {self._timeout_s}s",
                kind="timeout",
                provider="ollama",
                original_error=e
            )
        except httpx.ConnectError as e:
            raise ProviderError(
                f"Cannot connect to Ollama at {self._base_url}",
                kind="provider",
                provider="ollama",
                original_error=e
            )
        except Exception as e:
            raise ProviderError(
                f"Ollama error: {str(e)}",
                kind="provider",
                provider="ollama",
                original_error=e
            )
    
    def tool_call(
        self,
        name: str,
        args: dict,
        **opts: Any
    ) -> dict:
        """
        Execute tool call via Ollama.
        
        Note: Ollama doesn't have native function calling yet,
        so we simulate it via structured prompts.
        
        Args:
            name: Tool name
            args: Tool arguments
            **opts: Additional options
            
        Returns:
            Tool execution result
        """
        prompt = f"Execute tool: {name}\nArguments: {args}\nProvide result:"
        response = self.generate([{"role": "user", "content": prompt}], **opts)
        
        return {
            "tool": name,
            "args": args,
            "result": response
        }
    
    def _messages_to_prompt(self, messages: list[dict]) -> str:
        """Convert OpenAI-style messages to Ollama prompt format"""
        parts = []
        for msg in messages:
            role = msg.get("role", "user")
            content = msg.get("content", "")
            
            if role == "system":
                parts.append(f"System: {content}")
            elif role == "user":
                parts.append(f"User: {content}")
            elif role == "assistant":
                parts.append(f"Assistant: {content}")
        
        return "\n\n".join(parts)
    
    def __del__(self):
        """Cleanup HTTP client"""
        if hasattr(self, '_client'):
            self._client.close()
