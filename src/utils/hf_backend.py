"""HuggingFace Pro Backend for CrewAI"""
import os
from huggingface_hub import InferenceClient
from typing import Optional


class HFBackend:
    """
    HuggingFace Pro inference backend.
    Uses your HF Pro subscription for hosted model inference.
    """
    
    def __init__(self, model_name: str = "meta-llama/Llama-3.1-8B-Instruct"):
        """
        Initialize HF Pro backend.
        
        Args:
            model_name: HuggingFace model identifier
        """
        self.model_name = model_name
        self.token = os.getenv("HF_TOKEN")
        
        if not self.token:
            raise ValueError("HF_TOKEN not set. Get from huggingface.co/settings/tokens")
        
        self.client = InferenceClient(token=self.token)
        print(f"✅ HF Pro backend initialized: {model_name}")
    
    def generate(self, prompt: str, max_tokens: int = 512, temperature: float = 0.7) -> str:
        """
        Generate text using HF Pro inference.
        
        Args:
            prompt: Input prompt
            max_tokens: Max tokens to generate
            temperature: Sampling temperature
            
        Returns:
            Generated text
        """
        try:
            response = self.client.text_generation(
                self.model_name,
                prompt=prompt,
                max_new_tokens=max_tokens,
                temperature=temperature,
                return_full_text=False
            )
            return response
        except Exception as e:
            return f"❌ HF Pro error: {str(e)}"
    
    def __call__(self, prompt: str) -> str:
        """Make instance callable"""
        return self.generate(prompt)

