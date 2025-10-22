"""LLM Provider Abstraction Layer

Unified interface for different LLM backends (Ollama, OpenAI, Anthropic, MLX).
All providers implement the LLMProvider protocol for consistent usage.
"""

from typing import Protocol, Any, Optional
from dataclasses import dataclass


@dataclass
class GenerateOptions:
    """Common options for LLM generation"""
    temperature: float = 0.1
    max_tokens: int = 8192
    timeout_s: int = 120
    max_retries: int = 3
    top_p: float = 0.9
    stop: Optional[list[str]] = None


class LLMProvider(Protocol):
    """
    Protocol defining the interface all LLM providers must implement.
    
    This ensures consistent behavior across different backends
    (Ollama, OpenAI, Anthropic, MLX) while allowing provider-specific
    optimizations.
    """
    
    def generate(
        self,
        messages: list[dict],
        **opts: Any
    ) -> str:
        """
        Generate text completion from messages.
        
        Args:
            messages: List of message dicts with 'role' and 'content' keys
                     Example: [{"role": "user", "content": "Write a function..."}]
            **opts: Provider-specific options (temperature, max_tokens, etc.)
            
        Returns:
            Generated text response
            
        Raises:
            ProviderError: On timeout, rate limit, or other provider errors
        """
        ...
    
    def tool_call(
        self,
        name: str,
        args: dict,
        **opts: Any
    ) -> dict:
        """
        Execute a tool call (function calling).
        
        Args:
            name: Tool/function name to call
            args: Arguments to pass to the tool
            **opts: Provider-specific options
            
        Returns:
            Tool execution result as dict
            
        Raises:
            ProviderError: On tool execution failure
        """
        ...
    
    @property
    def name(self) -> str:
        """Provider name (e.g., 'ollama', 'openai', 'anthropic', 'mlx')"""
        ...
    
    @property
    def model(self) -> str:
        """Model identifier being used"""
        ...


class ProviderError(Exception):
    """Base exception for provider-related errors"""
    
    def __init__(
        self,
        message: str,
        kind: str = "provider",
        provider: str = "unknown",
        retry_count: int = 0,
        original_error: Optional[Exception] = None
    ):
        super().__init__(message)
        self.kind = kind  # "timeout", "rate_limit", "auth", "provider"
        self.provider = provider
        self.retry_count = retry_count
        self.original_error = original_error


__all__ = [
    'LLMProvider',
    'GenerateOptions',
    'ProviderError',
]

