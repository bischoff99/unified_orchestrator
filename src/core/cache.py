"""Deterministic Cache Key Generation

Computes stable cache keys for LLM responses based on:
- Provider configuration (name, model, options)
- Step identifier
- Input data (pydantic-serialized for consistency)
- Code version (git commit or file hash)
"""

import json
import hashlib
import subprocess
from pathlib import Path
from typing import Any, Optional


def get_code_version() -> str:
    """
    Get code version for cache invalidation.
    
    Returns git HEAD commit if in a git repo, otherwise returns
    a hash of key source files.
    
    Returns:
        Version string (git commit or file hash)
    """
    try:
        # Try to get git commit
        result = subprocess.run(
            ["git", "rev-parse", "HEAD"],
            capture_output=True,
            text=True,
            timeout=2,
            check=False
        )
        if result.returncode == 0:
            return result.stdout.strip()[:12]  # Short commit hash
    except (subprocess.TimeoutExpired, FileNotFoundError):
        pass
    
    # Fallback: hash of key source files
    src_dir = Path(__file__).parent.parent
    key_files = [
        "core/dag.py",
        "core/events.py",
        "orchestrator/dag_orchestrator.py",
    ]
    
    hasher = hashlib.sha256()
    for file_rel in key_files:
        file_path = src_dir / file_rel
        if file_path.exists():
            hasher.update(file_path.read_bytes())
    
    return hasher.hexdigest()[:12]


def compute_cache_key(
    provider: dict[str, Any],
    step_id: str,
    inputs: dict[str, Any],
    code_version: Optional[str] = None
) -> str:
    """
    Compute deterministic cache key.
    
    The cache key is a SHA256 hash of JSON-serialized:
    - provider: {name, model, opts}
    - step: step identifier
    - inputs: step inputs (must be JSON-serializable)
    - version: code version (git commit or file hash)
    
    Args:
        provider: Provider config dict with 'name', 'model', 'opts'
        step_id: Step identifier (e.g., 'architect', 'builder')
        inputs: Input data for this step
        code_version: Optional code version (auto-detected if not provided)
        
    Returns:
        64-character SHA256 hex string
        
    Example:
        >>> compute_cache_key(
        ...     provider={'name': 'ollama', 'model': 'llama3', 'opts': {}},
        ...     step_id='architect',
        ...     inputs={'task': 'Build a todo app'},
        ...     code_version='abc123'
        ... )
        'e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855'
    """
    if code_version is None:
        code_version = get_code_version()
    
    # Create deterministic cache structure
    cache_input = {
        "provider": {
            "name": provider.get("name", "unknown"),
            "model": provider.get("model", "unknown"),
            "opts": provider.get("opts", {}),
        },
        "step": step_id,
        "inputs": inputs,
        "code_version": code_version,
    }
    
    # Serialize to JSON with sorted keys for determinism
    cache_json = json.dumps(
        cache_input,
        sort_keys=True,
        separators=(',', ':'),  # No spaces
        default=str,  # Handle non-JSON types
    )
    
    # Hash to get fixed-length key
    hasher = hashlib.sha256()
    hasher.update(cache_json.encode('utf-8'))
    
    return hasher.hexdigest()


def cache_path(job_id: str, cache_key: str) -> Path:
    """
    Get filesystem path for a cache entry.
    
    Args:
        job_id: Job identifier
        cache_key: Cache key from compute_cache_key()
        
    Returns:
        Path to cache file: runs/<job_id>/.cache/<key>.json
    """
    return Path(f"runs/{job_id}/.cache/{cache_key}.json")


def read_cache(cache_file: Path) -> Optional[dict]:
    """
    Read cache entry from disk.
    
    Args:
        cache_file: Path to cache file
        
    Returns:
        Cached data dict or None if not found/invalid
    """
    if not cache_file.exists():
        return None
    
    try:
        with open(cache_file, 'r') as f:
            return json.load(f)
    except (json.JSONDecodeError, IOError):
        return None


def write_cache(cache_file: Path, data: dict):
    """
    Write cache entry to disk.
    
    Args:
        cache_file: Path to cache file
        data: Data to cache (must be JSON-serializable)
    """
    cache_file.parent.mkdir(parents=True, exist_ok=True)
    
    with open(cache_file, 'w') as f:
        json.dump(data, f, indent=2, default=str)

