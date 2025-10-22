"""File Store with Safe Writes and Content Hashing

Provides idempotent file operations with SHA256 hashing for integrity.
All file writes go through this layer to ensure consistency and tracking.
"""

import hashlib
from pathlib import Path
from typing import Literal, Union
import fcntl
from contextlib import contextmanager


def compute_sha256(content: Union[bytes, str]) -> str:
    """
    Compute SHA256 hash of content.
    
    Args:
        content: Bytes or string to hash
        
    Returns:
        Hexadecimal SHA256 hash string
    """
    if isinstance(content, str):
        content = content.encode('utf-8')
    
    return hashlib.sha256(content).hexdigest()


@contextmanager
def _file_lock(file_path: Path):
    """
    Context manager for exclusive file locking.
    
    Prevents race conditions when multiple processes write to same file.
    
    Args:
        file_path: Path to lock
        
    Yields:
        Lock context (file is exclusively locked)
    """
    lock_path = file_path.with_suffix(file_path.suffix + '.lock')
    lock_file = open(lock_path, 'w')
    
    try:
        fcntl.flock(lock_file.fileno(), fcntl.LOCK_EX)  # Exclusive lock
        yield
    finally:
        fcntl.flock(lock_file.fileno(), fcntl.LOCK_UN)  # Unlock
        lock_file.close()
        lock_path.unlink(missing_ok=True)  # Clean up lock file


class FileStore:
    """
    Safe file storage with content hashing and duplicate detection.
    
    Features:
    - Content-addressed storage (SHA256)
    - Idempotent writes (won't rewrite same content)
    - Parent directory creation
    - Exclusive locking for parallel safety
    - Multiple write modes (create_new, overwrite, append)
    """
    
    def __init__(self, base_dir: Path = Path(".")):
        """
        Initialize file store.
        
        Args:
            base_dir: Base directory for all file operations
        """
        self.base_dir = base_dir
    
    def safe_write(
        self,
        path: Union[str, Path],
        content: Union[str, bytes],
        mode: Literal["create_new", "overwrite", "append"] = "overwrite"
    ) -> tuple[Path, str, int]:
        """
        Write content to file with safety guarantees.
        
        Args:
            path: Relative path from base_dir
            content: Content to write (string or bytes)
            mode: Write mode:
                  - create_new: Fail if file exists
                  - overwrite: Replace existing file
                  - append: Append to existing file
                  
        Returns:
            Tuple of (full_path, sha256_hash, size_bytes)
            
        Raises:
            FileExistsError: If mode='create_new' and file exists
            ValueError: If mode is invalid
        """
        # Resolve path
        if isinstance(path, str):
            path = Path(path)
        
        full_path = self.base_dir / path
        
        # Convert content to bytes
        if isinstance(content, str):
            content_bytes = content.encode('utf-8')
        else:
            content_bytes = content
        
        # Compute hash before writing
        content_hash = compute_sha256(content_bytes)
        
        # Create parent directories
        full_path.parent.mkdir(parents=True, exist_ok=True)
        
        # Lock file for exclusive access
        with _file_lock(full_path):
            # Check mode constraints
            if mode == "create_new" and full_path.exists():
                # Check if content is same (idempotent)
                existing_hash = compute_sha256(full_path.read_bytes())
                if existing_hash == content_hash:
                    # Same content - idempotent, return success
                    return full_path, content_hash, len(content_bytes)
                else:
                    raise FileExistsError(
                        f"File exists with different content: {full_path}"
                    )
            
            # Duplicate detection (skip write if content unchanged)
            if mode == "overwrite" and full_path.exists():
                existing_hash = compute_sha256(full_path.read_bytes())
                if existing_hash == content_hash:
                    # Content unchanged - skip write
                    return full_path, content_hash, len(content_bytes)
            
            # Perform write
            if mode == "append":
                with open(full_path, 'ab') as f:
                    f.write(content_bytes)
            else:  # create_new or overwrite
                with open(full_path, 'wb') as f:
                    f.write(content_bytes)
        
        # Return path, hash, and size
        final_size = full_path.stat().st_size
        return full_path, content_hash, final_size
    
    def read(self, path: Union[str, Path]) -> bytes:
        """
        Read file content as bytes.
        
        Args:
            path: Relative path from base_dir
            
        Returns:
            File content as bytes
            
        Raises:
            FileNotFoundError: If file doesn't exist
        """
        if isinstance(path, str):
            path = Path(path)
        
        full_path = self.base_dir / path
        return full_path.read_bytes()
    
    def exists(self, path: Union[str, Path]) -> bool:
        """Check if file exists"""
        if isinstance(path, str):
            path = Path(path)
        
        return (self.base_dir / path).exists()
    
    def list_files(self, pattern: str = "**/*") -> list[Path]:
        """
        List files matching pattern.
        
        Args:
            pattern: Glob pattern (default: all files)
            
        Returns:
            List of matching file paths (relative to base_dir)
        """
        return [
            p.relative_to(self.base_dir)
            for p in self.base_dir.glob(pattern)
            if p.is_file()
        ]


# Global instance for convenient access
_default_store = None


def get_filestore(base_dir: Path = Path(".")) -> FileStore:
    """Get or create the default file store instance"""
    global _default_store
    if _default_store is None or _default_store.base_dir != base_dir:
        _default_store = FileStore(base_dir)
    return _default_store

