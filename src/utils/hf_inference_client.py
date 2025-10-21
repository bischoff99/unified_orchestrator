"""HuggingFace Pro inference client with cost tracking and safety validation.

Provides a production-ready client for HF Pro Inference API with:
- Automatic cost tracking
- Safety validation integration
- Latency monitoring
- Rate limiting
- Automatic fallback to Ollama
"""

import logging
import os
import time
from typing import Dict, Any, Optional, List
import httpx

from src.utils.hf_cost_monitor import HFCostMonitor
from src.mcp import SafetyValidator

logger = logging.getLogger(__name__)


class HFProClient:
    """Production HuggingFace Pro inference client with MCP integration."""

    def __init__(
        self,
        model_id: str,
        hf_token: Optional[str] = None,
        base_url: str = "https://api-inference.huggingface.co/models/",
        enable_cost_tracking: bool = True,
        enable_safety_checks: bool = True,
        timeout: int = 30,
        max_retries: int = 3,
    ):
        """Initialize HF Pro client.
        
        Args:
            model_id: HuggingFace model ID (e.g., "meta-llama/Llama-3.1-8B-Instruct")
            hf_token: HuggingFace API token (defaults to HF_TOKEN env var)
            base_url: Base URL for HF Inference API
            enable_cost_tracking: Enable cost monitoring
            enable_safety_checks: Enable safety validation
            timeout: Request timeout in seconds
            max_retries: Maximum retry attempts
        """
        self.model_id = model_id
        self.hf_token = hf_token or os.getenv("HF_TOKEN")
        self.base_url = base_url
        self.url = f"{base_url}{model_id}"
        self.timeout = timeout
        self.max_retries = max_retries
        
        if not self.hf_token:
            raise ValueError("HF_TOKEN must be provided or set in environment")
        
        self.headers = {
            "Authorization": f"Bearer {self.hf_token}",
            "Content-Type": "application/json",
        }
        
        # Initialize MCP components
        self.cost_monitor = HFCostMonitor() if enable_cost_tracking else None
        self.safety_validator = SafetyValidator() if enable_safety_checks else None
        
        logger.info(f"Initialized HF Pro client for model: {model_id}")

    def generate(
        self,
        prompt: str,
        max_tokens: int = 100,
        temperature: float = 0.7,
        top_p: float = 0.9,
        check_budget: bool = True,
        validate_safety: bool = True,
    ) -> Dict[str, Any]:
        """Generate text using HF Pro inference endpoint.
        
        Args:
            prompt: Input prompt
            max_tokens: Maximum tokens to generate
            temperature: Sampling temperature
            top_p: Nucleus sampling parameter
            check_budget: Check budget before making request
            validate_safety: Validate output safety
            
        Returns:
            Dict with generated text, metrics, and validation results
        """
        start_time = time.time()
        
        # Budget check (if enabled)
        if check_budget and self.cost_monitor:
            if not self.cost_monitor.should_use_hf_pro():
                return {
                    "error": "Budget exceeded, HF Pro disabled",
                    "status": "budget_exceeded",
                    "fallback_recommended": True,
                }
        
        # Prepare request
        payload = {
            "inputs": prompt,
            "parameters": {
                "max_new_tokens": max_tokens,
                "temperature": temperature,
                "top_p": top_p,
                "return_full_text": False,
            }
        }
        
        # Make request with retries
        for attempt in range(self.max_retries):
            try:
                response = httpx.post(
                    self.url,
                    json=payload,
                    headers=self.headers,
                    timeout=self.timeout,
                )
                
                latency_ms = (time.time() - start_time) * 1000
                
                if response.status_code == 200:
                    result = response.json()
                    generated_text = self._extract_text(result)
                    tokens_used = self._estimate_tokens(generated_text)
                    
                    # Cost tracking
                    if self.cost_monitor:
                        self.cost_monitor.record_inference(
                            model_id=self.model_id,
                            tokens_used=tokens_used,
                            latency_ms=latency_ms,
                            success=True,
                        )
                    
                    # Safety validation
                    safety_result = None
                    if validate_safety and self.safety_validator:
                        safety_result = self.safety_validator.check_output_safety(generated_text)
                        
                        if not safety_result["passed"]:
                            logger.warning(
                                f"Safety check failed: {safety_result['issues']}"
                            )
                    
                    return {
                        "status": "success",
                        "text": generated_text,
                        "latency_ms": latency_ms,
                        "tokens_used": tokens_used,
                        "model_id": self.model_id,
                        "safety_check": safety_result,
                        "attempt": attempt + 1,
                    }
                
                elif response.status_code == 503:
                    # Model loading, retry
                    logger.info(f"Model loading, retrying... (attempt {attempt + 1})")
                    time.sleep(2 ** attempt)  # Exponential backoff
                    continue
                
                elif response.status_code == 429:
                    # Rate limited
                    logger.warning(f"Rate limited, retrying... (attempt {attempt + 1})")
                    time.sleep(5 * (attempt + 1))
                    continue
                
                else:
                    error_msg = f"HTTP {response.status_code}: {response.text}"
                    logger.error(error_msg)
                    
                    latency_ms = (time.time() - start_time) * 1000
                    if self.cost_monitor:
                        self.cost_monitor.record_inference(
                            model_id=self.model_id,
                            tokens_used=0,
                            latency_ms=latency_ms,
                            success=False,
                        )
                    
                    return {
                        "status": "error",
                        "error": error_msg,
                        "latency_ms": latency_ms,
                        "attempt": attempt + 1,
                    }
                    
            except httpx.TimeoutException:
                logger.error(f"Request timeout (attempt {attempt + 1})")
                if attempt == self.max_retries - 1:
                    return {
                        "status": "error",
                        "error": "Request timeout after retries",
                        "latency_ms": (time.time() - start_time) * 1000,
                    }
                time.sleep(2 ** attempt)
                
            except Exception as e:
                logger.error(f"Request failed: {e}")
                return {
                    "status": "error",
                    "error": str(e),
                    "latency_ms": (time.time() - start_time) * 1000,
                }
        
        return {
            "status": "error",
            "error": "Max retries exceeded",
            "latency_ms": (time.time() - start_time) * 1000,
        }

    def _extract_text(self, response: Any) -> str:
        """Extract generated text from API response.
        
        Args:
            response: API response (list or dict)
            
        Returns:
            Generated text string
        """
        if isinstance(response, list):
            if len(response) > 0 and "generated_text" in response[0]:
                return response[0]["generated_text"]
        elif isinstance(response, dict):
            if "generated_text" in response:
                return response["generated_text"]
            elif "text" in response:
                return response["text"]
        
        # Fallback
        return str(response)

    def _estimate_tokens(self, text: str) -> int:
        """Estimate token count from text.
        
        Simple estimation: ~4 chars per token for English text.
        For accurate counting, use tiktoken library.
        
        Args:
            text: Generated text
            
        Returns:
            Estimated token count
        """
        return max(1, len(text) // 4)

    def chat(
        self,
        messages: List[Dict[str, str]],
        max_tokens: int = 100,
        temperature: float = 0.7,
        **kwargs,
    ) -> Dict[str, Any]:
        """Chat completion (for models that support it).
        
        Args:
            messages: List of message dicts with 'role' and 'content'
            max_tokens: Maximum tokens to generate
            temperature: Sampling temperature
            **kwargs: Additional generation parameters
            
        Returns:
            Generation result dict
        """
        # Convert messages to prompt
        prompt = self._format_chat_prompt(messages)
        return self.generate(
            prompt=prompt,
            max_tokens=max_tokens,
            temperature=temperature,
            **kwargs,
        )

    def _format_chat_prompt(self, messages: List[Dict[str, str]]) -> str:
        """Format chat messages as prompt.
        
        Args:
            messages: List of message dicts
            
        Returns:
            Formatted prompt string
        """
        formatted = []
        for msg in messages:
            role = msg.get("role", "user")
            content = msg.get("content", "")
            
            if role == "system":
                formatted.append(f"System: {content}")
            elif role == "user":
                formatted.append(f"User: {content}")
            elif role == "assistant":
                formatted.append(f"Assistant: {content}")
        
        formatted.append("Assistant:")
        return "\n".join(formatted)

    def get_model_info(self) -> Dict[str, Any]:
        """Get model information from HF API.
        
        Returns:
            Model info dict
        """
        try:
            response = httpx.get(
                f"https://huggingface.co/api/models/{self.model_id}",
                timeout=10,
            )
            if response.status_code == 200:
                return response.json()
        except Exception as e:
            logger.error(f"Failed to get model info: {e}")
        
        return {}

    def estimate_cost(self, tokens: int) -> Dict[str, float]:
        """Estimate cost for planned generation.
        
        Args:
            tokens: Number of tokens to generate
            
        Returns:
            Cost estimate dict
        """
        if self.cost_monitor:
            return self.cost_monitor.estimate_cost(tokens)
        return {"error": "Cost monitoring not enabled"}

    def check_budget(self) -> Dict[str, Any]:
        """Check current budget status.
        
        Returns:
            Budget status dict
        """
        if self.cost_monitor:
            return self.cost_monitor.check_budget()
        return {"error": "Cost monitoring not enabled"}

    def __repr__(self) -> str:
        return f"HFProClient(model={self.model_id}, cost_tracking={self.cost_monitor is not None})"

