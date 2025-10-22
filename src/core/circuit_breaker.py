"""Circuit Breaker Pattern Implementation

Prevents cascading failures by tracking provider errors and temporarily
blocking requests when failure threshold is exceeded.
"""

import time
from enum import Enum
from typing import Optional, Callable, Any
from dataclasses import dataclass, field
from datetime import datetime, timedelta


class CircuitState(Enum):
    """Circuit breaker states"""
    CLOSED = "closed"      # Normal operation
    OPEN = "open"          # Blocking requests
    HALF_OPEN = "half_open"  # Testing recovery


@dataclass
class CircuitBreaker:
    """
    Circuit breaker for provider fault tolerance.

    Tracks failures and opens circuit (blocks requests) when threshold
    is exceeded. After cooldown period, enters half-open state to test
    if provider has recovered.

    Attributes:
        threshold: Number of consecutive failures before opening circuit
        cooldown: Seconds to wait before attempting recovery
        state: Current circuit state (CLOSED, OPEN, HALF_OPEN)
    """
    threshold: int = 5
    cooldown: float = 60.0  # seconds
    state: CircuitState = field(default=CircuitState.CLOSED, init=False)
    _failure_count: int = field(default=0, init=False)
    _last_failure_time: Optional[float] = field(default=None, init=False)
    _opened_at: Optional[float] = field(default=None, init=False)

    def call(self, func: Callable, *args, **kwargs) -> Any:
        """
        Execute function through circuit breaker.

        Args:
            func: Function to execute
            *args: Positional arguments for func
            **kwargs: Keyword arguments for func

        Returns:
            Result of func execution

        Raises:
            CircuitBreakerOpen: When circuit is open and cooldown not expired
            Exception: Original exception from func if circuit allows execution
        """
        if self.state == CircuitState.OPEN:
            # Check if cooldown period has passed
            if self._opened_at and time.time() - self._opened_at >= self.cooldown:
                self._transition_to_half_open()
            else:
                raise CircuitBreakerOpen(
                    f"Circuit breaker OPEN (cooldown: {self.cooldown}s, "
                    f"opened {time.time() - (self._opened_at or 0):.1f}s ago)"
                )

        try:
            result = func(*args, **kwargs)
            self._on_success()
            return result
        except Exception as e:
            self._on_failure()
            raise

    def _on_success(self):
        """Handle successful execution"""
        if self.state == CircuitState.HALF_OPEN:
            # Recovery successful, close circuit
            self._transition_to_closed()
        elif self.state == CircuitState.CLOSED:
            # Reset failure count on success
            self._failure_count = 0

    def _on_failure(self):
        """Handle failed execution"""
        self._failure_count += 1
        self._last_failure_time = time.time()

        if self.state == CircuitState.HALF_OPEN:
            # Failed during recovery, reopen circuit
            self._transition_to_open()
        elif self.state == CircuitState.CLOSED:
            # Check if threshold exceeded
            if self._failure_count >= self.threshold:
                self._transition_to_open()

    def _transition_to_open(self):
        """Transition to OPEN state"""
        self.state = CircuitState.OPEN
        self._opened_at = time.time()
        self._failure_count = 0

    def _transition_to_half_open(self):
        """Transition to HALF_OPEN state"""
        self.state = CircuitState.HALF_OPEN

    def _transition_to_closed(self):
        """Transition to CLOSED state"""
        self.state = CircuitState.CLOSED
        self._failure_count = 0
        self._opened_at = None

    def reset(self):
        """Manually reset circuit breaker to closed state"""
        self._transition_to_closed()

    @property
    def is_open(self) -> bool:
        """Check if circuit is currently open"""
        return self.state == CircuitState.OPEN

    @property
    def failure_count(self) -> int:
        """Current failure count"""
        return self._failure_count

    def __repr__(self) -> str:
        return (
            f"CircuitBreaker(state={self.state.value}, "
            f"failures={self._failure_count}/{self.threshold}, "
            f"cooldown={self.cooldown}s)"
        )


class CircuitBreakerOpen(Exception):
    """Raised when circuit breaker is open and blocking requests"""
    pass
