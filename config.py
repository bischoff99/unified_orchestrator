"""Unified Configuration for Orchestrator"""
import os
from dotenv import load_dotenv

load_dotenv()

# ========================================
# Provider Configuration (New Architecture)
# ========================================
PROVIDER = os.getenv("PROVIDER", "ollama").lower()  # ollama, openai, anthropic, mlx

# Provider-specific models
PROVIDER_MODELS = {
    "ollama": os.getenv("OLLAMA_MODEL", "codellama:13b-instruct"),
    "openai": os.getenv("OPENAI_MODEL", "gpt-4"),
    "anthropic": os.getenv("ANTHROPIC_MODEL", "claude-3-5-sonnet-20241022"),
    "mlx": os.getenv("MLX_MODEL", "mlx-community/Llama-3.1-8B-Instruct-4bit"),
}

# Common provider options (centralized)
PROVIDER_OPTIONS = {
    "temperature": float(os.getenv("TEMPERATURE", "0.1")),
    "max_tokens": int(os.getenv("MAX_TOKENS", "8192")),
    "timeout_s": int(os.getenv("TIMEOUT_S", "120")),
    "max_retries": int(os.getenv("MAX_RETRIES", "3")),
    "top_p": float(os.getenv("TOP_P", "0.9")),
    "jitter": bool(os.getenv("JITTER", "true").lower() == "true"),
}

# ========================================
# Model Configuration (Backward Compatibility)
# ========================================
MODEL_CONFIG = {
    "model_name": os.getenv("MODEL_NAME", "codellama:13b-instruct"),  # Better tool calling than llama3.1
    "temperature": float(os.getenv("MODEL_TEMPERATURE", "0.1")),  # Lower for tool usage reliability
    "max_tokens": int(os.getenv("MODEL_MAX_TOKENS", "8192")),  # Increased for complete code implementations
}

MODEL_BACKEND = os.getenv("MODEL_BACKEND", "ollama").lower()  # ollama, mlx, openai, anthropic, huggingface

# ========================================
# Agent Configuration
# ========================================
AGENT_CONFIG = {
    "verbose": os.getenv("AGENT_VERBOSE", "true").lower() == "true",
    "memory": os.getenv("AGENT_MEMORY", "true").lower() == "true",
    "cache": os.getenv("AGENT_CACHE", "true").lower() == "true",
}

# ========================================
# Task Configuration
# ========================================
TASK_CONFIG = {
    "async_execution": os.getenv("TASK_ASYNC", "false").lower() == "true",
    "context_window": int(os.getenv("TASK_CONTEXT_WINDOW", "8000")),
}

# ========================================
# Workflow Configuration
# ========================================
WORKFLOW_CONFIG = {
    "process": os.getenv("WORKFLOW_PROCESS", "sequential"),  # sequential or hierarchical
    "max_retries": int(os.getenv("WORKFLOW_MAX_RETRIES", "2")),
    "timeout": int(os.getenv("WORKFLOW_TIMEOUT", "300")),  # seconds
}

# ========================================
# Claude Desktop Integration
# ========================================
CLAUDE_RESPONSE_DELAY = float(os.getenv("CLAUDE_RESPONSE_DELAY", "3.0"))
CLAUDE_PASTE_DELAY = float(os.getenv("CLAUDE_PASTE_DELAY", "0.2"))
CLAUDE_COPY_DELAY = float(os.getenv("CLAUDE_COPY_DELAY", "0.2"))

# ========================================
# Parallel Execution
# ========================================
PARALLEL_MODE = os.getenv("PARALLEL_MODE", "true").lower() == "true"
MAX_CONCURRENT_TASKS = int(os.getenv("MAX_CONCURRENT_TASKS", "8"))  # M3 Max optimized

# ========================================
# MLX Configuration (Apple Silicon)
# ========================================
MLX_MODEL_PATH = os.getenv("MLX_MODEL_PATH", "mlx_models/llama3-8b")
MLX_MAX_TOKENS = int(os.getenv("MLX_MAX_TOKENS", "512"))

# ========================================
# Ollama Performance (M3 Max Optimization)
# ========================================
OLLAMA_BASE_URL = os.getenv("OLLAMA_BASE_URL", "http://localhost:11434")
OLLAMA_NUM_THREAD = int(os.getenv("OLLAMA_NUM_THREAD", "14"))  # Leave 2 cores for system
OLLAMA_NUM_BATCH = int(os.getenv("OLLAMA_NUM_BATCH", "512"))  # Smaller batches for faster response
OLLAMA_NUM_GPU = int(os.getenv("OLLAMA_NUM_GPU", "1"))  # Let Ollama auto-detect GPU layers
OLLAMA_NUM_CTX = int(os.getenv("OLLAMA_NUM_CTX", "8192"))  # Keep for code context
OLLAMA_NUM_PREDICT = int(os.getenv("OLLAMA_NUM_PREDICT", "2048"))  # Max tokens per response

# ========================================
# HuggingFace Configuration
# ========================================
HF_TOKEN = os.getenv("HF_TOKEN", "")
HF_EMBEDDING_MODEL = os.getenv("HF_EMBEDDING_MODEL", "sentence-transformers/all-MiniLM-L6-v2")
HF_MODEL = os.getenv("HF_MODEL", "meta-llama/Llama-3.1-8B-Instruct")

# ========================================
# Logging
# ========================================
LOG_LEVEL = os.getenv("LOG_LEVEL", "INFO")

# ========================================
# Backend Getter
# ========================================
def get_llm_backend():
    """Get configured LLM backend with optimized settings"""
    if MODEL_BACKEND == "ollama":
        from crewai import LLM
        return LLM(
            model=f"ollama/{MODEL_CONFIG['model_name']}",
            base_url=OLLAMA_BASE_URL,
            temperature=MODEL_CONFIG['temperature'],
            num_ctx=OLLAMA_NUM_CTX,
            num_predict=OLLAMA_NUM_PREDICT,
            num_thread=OLLAMA_NUM_THREAD,
        )
    elif MODEL_BACKEND == "mlx":
        from src.utils.mlx_backend import MLXBackend
        return MLXBackend(MLX_MODEL_PATH)
    elif MODEL_BACKEND == "openai":
        from crewai import LLM
        return LLM(model=MODEL_CONFIG['model_name'])
    elif MODEL_BACKEND == "anthropic":
        from crewai import LLM
        return LLM(model="anthropic/claude-3-sonnet-20240229")
    elif MODEL_BACKEND == "huggingface":
        from crewai import LLM
        return LLM(model=f"huggingface/{HF_MODEL}", api_key=HF_TOKEN)
    else:
        raise ValueError(f"Unsupported backend: {MODEL_BACKEND}")


# ========================================
# Provider Factory (New Architecture)
# ========================================
def get_provider():
    """
    Get configured LLM provider instance.
    
    Returns provider adapter based on PROVIDER env var with
    centralized timeout/retry settings.
    
    Returns:
        Provider instance (Ollama, OpenAI, Anthropic, or MLX)
        
    Raises:
        ValueError: If provider not supported
    """
    model = PROVIDER_MODELS.get(PROVIDER)
    if not model:
        raise ValueError(f"Unsupported provider: {PROVIDER}")
    
    if PROVIDER == "ollama":
        from src.providers.ollama import OllamaProvider
        return OllamaProvider(
            model=model,
            base_url=OLLAMA_BASE_URL,
            timeout_s=PROVIDER_OPTIONS["timeout_s"],
            max_retries=PROVIDER_OPTIONS["max_retries"],
            num_thread=OLLAMA_NUM_THREAD,
            num_batch=OLLAMA_NUM_BATCH,
            num_ctx=OLLAMA_NUM_CTX,
        )
    elif PROVIDER == "openai":
        from src.providers.openai import OpenAIProvider
        return OpenAIProvider(
            model=model,
            timeout_s=PROVIDER_OPTIONS["timeout_s"],
            max_retries=PROVIDER_OPTIONS["max_retries"],
        )
    elif PROVIDER == "anthropic":
        from src.providers.anthropic import AnthropicProvider
        return AnthropicProvider(
            model=model,
            timeout_s=PROVIDER_OPTIONS["timeout_s"],
            max_retries=PROVIDER_OPTIONS["max_retries"],
        )
    elif PROVIDER == "mlx":
        from src.providers.mlx import MLXProvider
        return MLXProvider(
            model=model,
            model_path=MLX_MODEL_PATH,
            timeout_s=PROVIDER_OPTIONS["timeout_s"],
            max_retries=PROVIDER_OPTIONS["max_retries"],
        )
    else:
        raise ValueError(f"Unsupported provider: {PROVIDER}")

