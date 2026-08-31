"""Per-client token bucket rate limiter."""

from __future__ import annotations

import time
from typing import Callable

Clock = Callable[[], float]


class TokenBucket:
    """A lazily-refilling token bucket.

    ``capacity`` tokens max; refills at ``refill_rate`` tokens per second
    computed from the injected clock (defaults to ``time.monotonic``).
    """

    def __init__(
        self,
        capacity: int = 10,
        refill_rate: float = 5.0,
        *,
        clock: Clock | None = None,
    ) -> None:
        self.capacity = capacity
        self.refill_rate = refill_rate
        self._clock: Clock = clock if clock is not None else time.monotonic
        self._tokens = float(capacity)
        self._last = self._clock()

    def _refill(self) -> None:
        now = self._clock()
        elapsed = now - self._last
        self._last = now
        self._tokens = min(self.capacity, self._tokens + elapsed * self.refill_rate)

    def try_consume(self, tokens: int = 1) -> bool:
        """Consume ``tokens`` if available; return True on success."""
        self._refill()
        if self._tokens >= tokens:
            self._tokens -= tokens
            return True
        return False

    @property
    def tokens(self) -> float:
        """Current (refilled) token count."""
        self._refill()
        return self._tokens
