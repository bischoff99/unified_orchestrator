"""MLX Provider Adapter (Apple Silicon)"""

from typing import Any, Optional
from . import ProviderError


class MLXProvider:
    """
    MLX provider adapter for Apple Silicon local inference.
    
    Uses MLX framework for efficient on-device inference on M1/M2/M3 Max chips.
    """
    
    def __init__(
        self,
        model: str = "mlx-community/Llama-3.1-8B-Instruct-4bit",
        model_path: Optional[str] = None,
        timeout_s: int = 120,
        max_retries: int = 3,
        **model_opts
    ):
        self._model = model
        self._model_path = model_path or f"mlx_models/{model}"
        self._timeout_s = timeout_s
        self._max_retries = max_retries
        self._model_opts = model_opts
        
        # Lazy load MLX (only when needed)
        self._mlx_model = None
        self._mlx_tokenizer = None
    
    @property
    def name(self) -> str:
        return "mlx"
    
    @property
    def model(self) -> str:
        return self._model
    
    def _load_model(self):
        """Lazy load MLX model and tokenizer"""
        if self._mlx_model is not None:
            return
        
        try:
            from mlx_lm import load, generate
            
            self._mlx_model, self._mlx_tokenizer = load(self._model_path)
            self._mlx_generate = generate
            
        except ImportError:
            raise ProviderError(
                "MLX not installed. Install with: pip install mlx-lm",
                kind="provider",
                provider="mlx"
            )
        except Exception as e:
            raise ProviderError(
                f"Failed to load MLX model from {self._model_path}: {str(e)}",
                kind="provider",
                provider="mlx",
                original_error=e
            )
    
    def generate(
        self,
        messages: list[dict],
        **opts: Any
    ) -> str:
        """
        Generate completion using MLX local inference.
        
        Args:
            messages: Message history
            **opts: Override options
            
        Returns:
            Generated text
            
        Raises:
            ProviderError: On model loading or generation failure
        """
        self._load_model()
        
        options = {**self._model_opts, **opts}
        
        # Convert messages to prompt
        prompt = self._messages_to_prompt(messages)
        
        try:
            # MLX generation parameters
            max_tokens = options.get("max_tokens", 8192)
            temperature = options.get("temperature", 0.1)
            top_p = options.get("top_p", 0.9)
            
            # Generate using MLX
            response = self._mlx_generate(
                model=self._mlx_model,
                tokenizer=self._mlx_tokenizer,
                prompt=prompt,
                max_tokens=max_tokens,
                temp=temperature,
                top_p=top_p,
                verbose=False
            )
            
            return response
            
        except Exception as e:
            raise ProviderError(
                f"MLX generation failed: {str(e)}",
                kind="provider",
                provider="mlx",
                original_error=e
            )
    
    def tool_call(
        self,
        name: str,
        args: dict,
        **opts: Any
    ) -> dict:
        """
        Simulate tool calling via structured prompt.
        
        MLX doesn't have native function calling, so we use
        structured prompts similar to Ollama.
        
        Args:
            name: Tool name
            args: Tool arguments
            **opts: Additional options
            
        Returns:
            Tool execution result
        """
        prompt = f"""Execute the following tool:
Tool: {name}
Arguments: {args}

Provide the result in JSON format:"""
        
        response = self.generate(
            [{"role": "user", "content": prompt}],
            **opts
        )
        
        return {
            "tool": name,
            "args": args,
            "result": response
        }
    
    def _messages_to_prompt(self, messages: list[dict]) -> str:
        """Convert OpenAI-style messages to MLX prompt format"""
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
        
        return "\n\n".join(parts) + "\n\nAssistant:"

