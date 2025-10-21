"""MLX Backend for Apple Silicon Native Inference"""

try:
    from mlx_lm import load, generate
    MLX_AVAILABLE = True
except ImportError:
    MLX_AVAILABLE = False

class MLXBackend:
    """
    MLX backend for native Apple Silicon inference using Metal.
    
    Provides optimized inference on M1/M2/M3 chips using unified memory architecture.
    """
    
    def __init__(self, model_path="mlx_models/llama3-8b"):
        if not MLX_AVAILABLE:
            raise RuntimeError(
                "MLX not installed. Install with: pip install mlx mlx-lm\n"
                "MLX requires Apple Silicon (M1/M2/M3) and macOS 13.3+"
            )
        self.model_path = model_path
        self.model = None
        self.tokenizer = None
        self._load_model()
    
    def _load_model(self):
        """Lazy load model on first use"""
        if self.model is None:
            print(f"Loading MLX model from {self.model_path}...")
            self.model, self.tokenizer = load(self.model_path)
            print("MLX model loaded successfully")
    
    def generate(self, prompt: str, max_tokens: int = 512, temperature: float = 0.7) -> str:
        """
        Generate text using MLX model.
        
        Args:
            prompt: Input prompt text
            max_tokens: Maximum tokens to generate
            temperature: Sampling temperature (0.0 = deterministic, 1.0 = creative)
        
        Returns:
            Generated text string
        """
        self._load_model()  # Ensure model is loaded
        
        response = generate(
            self.model,
            self.tokenizer,
            prompt=prompt,
            max_tokens=max_tokens,
            temperature=temperature
        )
        
        return response
    
    @staticmethod
    def is_available() -> bool:
        """Check if MLX is available on this system"""
        return MLX_AVAILABLE
    
    def __repr__(self):
        return f"MLXBackend(model_path='{self.model_path}', available={MLX_AVAILABLE})"

