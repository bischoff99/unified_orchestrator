"""OpenAI Provider Adapter"""

import httpx
from typing import Any, Optional
from tenacity import retry, stop_after_attempt, wait_exponential, retry_if_exception_type
from . import ProviderError


class OpenAIProvider:
    """
    OpenAI provider adapter with automatic retries and timeout handling.
    
    Supports GPT-4, GPT-3.5-turbo, and other OpenAI models.
    """
    
    def __init__(
        self,
        model: str = "gpt-4",
        api_key: Optional[str] = None,
        timeout_s: int = 120,
        max_retries: int = 3,
        **model_opts
    ):
        self._model = model
        self._api_key = api_key
        self._timeout_s = timeout_s
        self._max_retries = max_retries
        self._model_opts = model_opts
        
        if not api_key:
            import os
            self._api_key = os.getenv("OPENAI_API_KEY")
            if not self._api_key:
                raise ValueError("OpenAI API key required (set OPENAI_API_KEY)")
        
        self._client = httpx.Client(
            base_url="https://api.openai.com/v1",
            headers={"Authorization": f"Bearer {self._api_key}"},
            timeout=timeout_s
        )
    
    @property
    def name(self) -> str:
        return "openai"
    
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
        Generate completion using OpenAI API.
        
        Args:
            messages: OpenAI-format messages
            **opts: Override options
            
        Returns:
            Generated text
            
        Raises:
            ProviderError: On timeout, rate limit, or API error
        """
        options = {**self._model_opts, **opts}
        
        payload = {
            "model": self._model,
            "messages": messages,
            "temperature": options.get("temperature", 0.1),
            "max_tokens": options.get("max_tokens", 8192),
            "top_p": options.get("top_p", 0.9),
        }
        
        if options.get("stop"):
            payload["stop"] = options["stop"]
        
        try:
            response = self._client.post(
                "/chat/completions",
                json=payload
            )
            response.raise_for_status()
            
            result = response.json()
            return result["choices"][0]["message"]["content"]
            
        except httpx.TimeoutException as e:
            raise ProviderError(
                f"OpenAI request timed out after {self._timeout_s}s",
                kind="timeout",
                provider="openai",
                original_error=e
            )
        except httpx.HTTPStatusError as e:
            if e.response.status_code == 429:
                raise ProviderError(
                    "OpenAI rate limit exceeded",
                    kind="rate_limit",
                    provider="openai",
                    original_error=e
                )
            elif e.response.status_code == 401:
                raise ProviderError(
                    "OpenAI authentication failed - check API key",
                    kind="auth",
                    provider="openai",
                    original_error=e
                )
            else:
                raise ProviderError(
                    f"OpenAI API error: {e.response.status_code}",
                    kind="provider",
                    provider="openai",
                    original_error=e
                )
        except Exception as e:
            raise ProviderError(
                f"OpenAI error: {str(e)}",
                kind="provider",
                provider="openai",
                original_error=e
            )
    
    def tool_call(
        self,
        name: str,
        args: dict,
        **opts: Any
    ) -> dict:
        """
        Execute tool call using OpenAI function calling.
        
        Args:
            name: Function name
            args: Function arguments
            **opts: Additional options
            
        Returns:
            Function call result
        """
        options = {**self._model_opts, **opts}
        
        messages = [
            {"role": "user", "content": f"Call function {name} with args: {args}"}
        ]
        
        payload = {
            "model": self._model,
            "messages": messages,
            "tools": [{
                "type": "function",
                "function": {
                    "name": name,
                    "parameters": args
                }
            }],
            "tool_choice": {"type": "function", "function": {"name": name}}
        }
        
        try:
            response = self._client.post("/chat/completions", json=payload)
            response.raise_for_status()
            
            result = response.json()
            tool_calls = result["choices"][0]["message"].get("tool_calls", [])
            
            if tool_calls:
                return {
                    "tool": name,
                    "args": args,
                    "result": tool_calls[0]["function"]["arguments"]
                }
            else:
                return {"tool": name, "args": args, "result": None}
                
        except Exception as e:
            raise ProviderError(
                f"OpenAI tool call failed: {str(e)}",
                kind="tool",
                provider="openai",
                original_error=e
            )
    
    def __del__(self):
        """Cleanup HTTP client"""
        if hasattr(self, '_client'):
            self._client.close()

