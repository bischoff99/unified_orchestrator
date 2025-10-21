"""Unified Configuration for Orchestrator"""
import os
from dotenv import load_dotenv

load_dotenv()

# ========================================
# Model Configuration
# ========================================
MODEL_CONFIG = {
    "model_name": os.getenv("MODEL_NAME", "gpt-4o"),  # or "gpt-3.5-turbo", "llama3.1:8b"
    "temperature": float(os.getenv("MODEL_TEMPERATURE", "0.7")),
    "max_tokens": int(os.getenv("MODEL_MAX_TOKENS", "2048")),
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
# Ollama Performance (M3 Max)
# ========================================
OLLAMA_BASE_URL = os.getenv("OLLAMA_BASE_URL", "http://localhost:11434")
OLLAMA_NUM_THREAD = int(os.getenv("OLLAMA_NUM_THREAD", "16"))
OLLAMA_NUM_BATCH = int(os.getenv("OLLAMA_NUM_BATCH", "2048"))
OLLAMA_NUM_GPU = int(os.getenv("OLLAMA_NUM_GPU", "40"))
OLLAMA_NUM_CTX = int(os.getenv("OLLAMA_NUM_CTX", "8192"))

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
    """Get configured LLM backend"""
    if MODEL_BACKEND == "ollama":
        from crewai import LLM
        return LLM(model=f"ollama/{MODEL_CONFIG['model_name']}")
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

