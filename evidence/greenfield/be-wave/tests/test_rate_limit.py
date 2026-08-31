"""Token bucket tests — AC-1 (10-token burst then drop) and AC-2 (refill ≈5/s)."""

from __future__ import annotations

import time

import pytest

from app.rate_limit import TokenBucket


class FakeClock:
    """Deterministic monotonic clock for exact refill arithmetic."""

    def __init__(self, start: float = 1_000_000.0) -> None:
        self.now = start

    def __call__(self) -> float:
        return self.now

    def advance(self, seconds: float) -> None:
        self.now += seconds


def test_burst_capacity_enforced_then_drops() -> None:
    """AC-1: capacity 10 allows a 10-token burst, then the next consume drops."""
    bucket = TokenBucket(capacity=10, refill_rate=5.0)
    assert [bucket.try_consume(1) for _ in range(10)] == [True] * 10
    assert bucket.try_consume(1) is False


def test_refill_rate_approx_5_per_second_over_2s() -> None:
    """AC-2: after draining, ~2s restores ~10 tokens (5/sec) — tolerant of CI slack."""
    bucket = TokenBucket(capacity=10, refill_rate=5.0)
    for _ in range(10):
        bucket.try_consume(1)
    time.sleep(2.0)
    consumed = sum(1 for _ in range(10) if bucket.try_consume(1))
    assert consumed >= 8


def test_refill_exact_with_fake_clock() -> None:
    """AC-2 (deterministic): 2s on the clock restores exactly 10 tokens."""
    clock = FakeClock()
    bucket = TokenBucket(capacity=10, refill_rate=5.0, clock=clock)
    for _ in range(10):
        bucket.try_consume(1)
    assert bucket.tokens == pytest.approx(0.0)

    clock.advance(2.0)
    assert bucket.tokens == pytest.approx(10.0)
    assert [bucket.try_consume(1) for _ in range(10)] == [True] * 10
    assert bucket.try_consume(1) is False


def test_refill_capped_at_capacity() -> None:
    """Refill never exceeds the bucket capacity."""
    clock = FakeClock()
    bucket = TokenBucket(capacity=10, refill_rate=5.0, clock=clock)
    clock.advance(100.0)
    assert bucket.tokens == pytest.approx(10.0)
