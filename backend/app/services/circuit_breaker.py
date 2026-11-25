"""Small thread-safe circuit breaker plus an async retry-with-backoff helper for outbound calls."""
import asyncio
import random
import threading
import time
from typing import Awaitable, Callable, Optional, TypeVar

T = TypeVar("T")


class CircuitOpenError(RuntimeError):
    pass


class CircuitBreaker:
    """closed -> (N consecutive failures) -> open -> (reset_seconds) -> half_open -> success closes / failure re-opens."""

    def __init__(self, name: str, failure_threshold: int = 3, reset_seconds: float = 30.0, clock: Callable[[], float] = time.monotonic):
        self.name = name
        self.failure_threshold = failure_threshold
        self.reset_seconds = reset_seconds
        self._clock = clock
        self._lock = threading.Lock()
        self._failures = 0
        self._opened_at: Optional[float] = None
        self._half_open_in_flight = False

    @property
    def state(self) -> str:
        with self._lock:
            return self._state_locked()

    def _state_locked(self) -> str:
        if self._opened_at is None:
            return "closed"
        if self._clock() - self._opened_at >= self.reset_seconds:
            return "half_open"
        return "open"

    def allow(self) -> bool:
        with self._lock:
            st = self._state_locked()
            if st == "closed":
                return True
            if st == "half_open" and not self._half_open_in_flight:
                self._half_open_in_flight = True  # exactly one probe request
                return True
            return False

    def record_success(self) -> None:
        with self._lock:
            self._failures = 0
            self._opened_at = None
            self._half_open_in_flight = False

    def record_failure(self) -> None:
        with self._lock:
            self._failures += 1
            self._half_open_in_flight = False
            if self._failures >= self.failure_threshold or self._opened_at is not None:
                self._opened_at = self._clock()

    async def call(self, fn: Callable[[], Awaitable[T]]) -> T:
        if not self.allow():
            raise CircuitOpenError(f"circuit '{self.name}' is open")
        try:
            result = await fn()
        except Exception:
            self.record_failure()
            raise
        self.record_success()
        return result


async def retry_async(fn: Callable[[], Awaitable[T]], attempts: int = 3, base_delay: float = 0.2, max_delay: float = 2.0,
                      retry_on: tuple = (Exception,)) -> T:
    """Retry with exponential backoff and full jitter. Re-raises the last error."""
    last: Optional[BaseException] = None
    for i in range(attempts):
        try:
            return await fn()
        except CircuitOpenError:
            raise
        except retry_on as exc:
            last = exc
            if i == attempts - 1:
                break
            await asyncio.sleep(random.uniform(0, min(max_delay, base_delay * (2 ** i))))
    assert last is not None
    raise last
