"""GPU Resource Manager for M3 Max unified memory architecture.

Coordinates GPU access across concurrent agents to prevent:
- GPU memory oversubscription
- MPS device conflicts
- Out-of-memory errors

Optimized for M3 Max: 40 GPU cores, 128GB unified memory.
"""

import logging
import time
from threading import Semaphore, Lock
from typing import Dict, Optional
from contextlib import contextmanager

logger = logging.getLogger(__name__)


class MPSResourceManager:
    """Singleton resource manager for M3 Max MPS device coordination."""
    
    _instance = None
    _creation_lock = Lock()
    
    def __new__(cls):
        """Ensure single instance across all agents."""
        if cls._instance is None:
            with cls._creation_lock:
                if cls._instance is None:
                    cls._instance = super().__new__(cls)
                    cls._instance._initialized = False
        return cls._instance
    
    def __init__(
        self,
        max_concurrent_gpu_users: int = 2,
        total_memory_gb: int = 128,
        gpu_memory_fraction: float = 0.7,  # 70% of 128GB = ~90GB for GPU tasks
    ):
        """Initialize GPU resource manager.
        
        Args:
            max_concurrent_gpu_users: Max agents using GPU simultaneously
            total_memory_gb: Total M3 Max unified memory
            gpu_memory_fraction: Fraction of memory available for GPU tasks
        """
        if self._initialized:
            return
            
        self.max_concurrent = max_concurrent_gpu_users
        self.total_memory_gb = total_memory_gb
        self.gpu_memory_fraction = gpu_memory_fraction
        self.available_memory_gb = total_memory_gb * gpu_memory_fraction
        
        # Semaphore limits concurrent GPU access
        self.gpu_semaphore = Semaphore(max_concurrent_gpu_users)
        
        # Track current allocations
        self.allocations: Dict[str, Dict] = {}
        self.alloc_lock = Lock()
        
        self._initialized = True
        logger.info(
            f"MPS Resource Manager initialized: "
            f"{max_concurrent_gpu_users} concurrent users, "
            f"{self.available_memory_gb:.0f}GB GPU memory available"
        )
    
    @contextmanager
    def acquire_gpu(
        self,
        agent_name: str,
        estimated_memory_gb: float = 20,
        timeout: Optional[float] = None,
    ):
        """Context manager for safe GPU acquisition.
        
        Args:
            agent_name: Name of requesting agent
            estimated_memory_gb: Estimated GPU memory needed
            timeout: Optional timeout for acquisition
            
        Yields:
            GPU access context
            
        Raises:
            ResourceError: If cannot acquire within timeout
            
        Example:
            gpu_mgr = MPSResourceManager()
            with gpu_mgr.acquire_gpu("hf_trainer", estimated_memory_gb=24):
                model.to("mps")
                # Training code here
        """
        acquired = self.gpu_semaphore.acquire(timeout=timeout)
        
        if not acquired:
            raise ResourceError(
                f"GPU acquisition timeout for {agent_name} "
                f"(waited {timeout}s)"
            )
        
        # Register allocation
        with self.alloc_lock:
            self.allocations[agent_name] = {
                "memory_gb": estimated_memory_gb,
                "acquired_at": time.time(),
                "timestamp": time.time(),
            }
        
        # Set memory limits (PyTorch MPS)
        try:
            import torch
            if torch.backends.mps.is_available():
                # Limit per-process memory to prevent OOM
                memory_fraction = min(0.45, estimated_memory_gb / self.total_memory_gb)
                torch.mps.set_per_process_memory_fraction(memory_fraction)
                
        except Exception as e:
            logger.warning(f"Could not set MPS memory limit: {e}")
        
        logger.info(
            f"✅ GPU acquired by '{agent_name}' "
            f"(est: {estimated_memory_gb}GB, fraction: {memory_fraction:.2%})"
        )
        
        try:
            yield  # GPU is available for use
        finally:
            # Clean up and release
            try:
                import torch
                if torch.backends.mps.is_available():
                    torch.mps.empty_cache()  # Free GPU memory
            except:
                pass
            
            # Unregister allocation
            with self.alloc_lock:
                self.allocations.pop(agent_name, None)
            
            # Release semaphore
            self.gpu_semaphore.release()
            
            logger.info(f"✅ GPU released by '{agent_name}'")
    
    def get_current_usage(self) -> Dict:
        """Get current GPU allocation status.
        
        Returns:
            Dict with active users and allocations
        """
        with self.alloc_lock:
            return {
                "active_users": len(self.allocations),
                "max_concurrent": self.max_concurrent,
                "available_slots": self.max_concurrent - len(self.allocations),
                "allocations": self.allocations.copy(),
                "total_allocated_gb": sum(
                    a["memory_gb"] for a in self.allocations.values()
                ),
                "available_memory_gb": self.available_memory_gb,
            }
    
    def is_available(self, required_memory_gb: float = 0) -> bool:
        """Check if GPU is available for new allocation.
        
        Args:
            required_memory_gb: Memory needed (optional check)
            
        Returns:
            True if GPU can be acquired
        """
        with self.alloc_lock:
            # Check if slots available
            if len(self.allocations) >= self.max_concurrent:
                return False
            
            # Check if enough memory
            if required_memory_gb > 0:
                allocated = sum(a["memory_gb"] for a in self.allocations.values())
                return (allocated + required_memory_gb) <= self.available_memory_gb
            
            return True
    
    def wait_for_gpu(
        self,
        agent_name: str,
        estimated_memory_gb: float,
        max_wait_sec: float = 300,
    ):
        """Wait for GPU to become available.
        
        Args:
            agent_name: Requesting agent
            estimated_memory_gb: Memory needed
            max_wait_sec: Maximum wait time
            
        Returns:
            True if acquired, False if timeout
        """
        start = time.time()
        
        while time.time() - start < max_wait_sec:
            if self.is_available(estimated_memory_gb):
                logger.info(
                    f"GPU available for '{agent_name}' "
                    f"after {time.time() - start:.1f}s wait"
                )
                return True
            
            time.sleep(1)  # Check every second
        
        logger.warning(
            f"GPU acquisition timeout for '{agent_name}' "
            f"after {max_wait_sec}s"
        )
        return False
    
    def __repr__(self) -> str:
        usage = self.get_current_usage()
        return (
            f"MPSResourceManager("
            f"active={usage['active_users']}/{usage['max_concurrent']}, "
            f"allocated={usage['total_allocated_gb']:.1f}GB/"
            f"{usage['available_memory_gb']:.1f}GB)"
        )


class ResourceError(Exception):
    """Exception raised when GPU resource cannot be acquired."""
    pass


# Global singleton instance
_gpu_manager = None
_gpu_manager_lock = Lock()


def get_gpu_manager() -> MPSResourceManager:
    """Get global GPU resource manager instance.
    
    Returns:
        Singleton MPSResourceManager instance
    """
    global _gpu_manager
    
    if _gpu_manager is None:
        with _gpu_manager_lock:
            if _gpu_manager is None:
                _gpu_manager = MPSResourceManager()
    
    return _gpu_manager

