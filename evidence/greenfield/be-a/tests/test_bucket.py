"""Unit tests for TokenBucket: burst behavior, refill rate, and capping."""

import pytest

from app.streams import TokenBucket


class FakeClock:
    """Deterministic monotonic clock: advance time by hand."""

    def __init__(self, start=0.0):
        self.t = start

    def __call__(self):
        return self.t

    def advance(self, dt):
        self.t += dt


def test_bucket_starts_full_at_capacity():
    bucket = TokenBucket(capacity=10, refill_rate=5.0)
    assert bucket.tokens == 10.0


def test_burst_of_10_passes_then_11th_is_dropped():
    clock = FakeClock(0.0)
    bucket = TokenBucket(capacity=10, refill_rate=5.0, now=clock)
    assert all(bucket.try_consume() for _ in range(10))
    assert not bucket.try_consume()


def test_refill_rate_is_approximately_5_per_second():
    clock = FakeClock(0.0)
    bucket = TokenBucket(capacity=10, refill_rate=5.0, now=clock)
    for _ in range(10):
        bucket.try_consume()  # drain the burst
    assert bucket.available == 0.0

    clock.advance(1.0)
    assert bucket.available == pytest.approx(5.0, abs=1e-6)
    clock.advance(1.0)
    assert bucket.available == pytest.approx(10.0, abs=1e-6)


def test_refill_over_two_seconds_restores_ten_tokens():
    clock = FakeClock(0.0)
    bucket = TokenBucket(capacity=10, refill_rate=5.0, now=clock)
    for _ in range(10):
        bucket.try_consume()

    clock.advance(2.0)
    assert bucket.available == pytest.approx(10.0, abs=1e-6)
    assert all(bucket.try_consume() for _ in range(10))
    assert not bucket.try_consume()


def test_tokens_never_exceed_capacity():
    clock = FakeClock(0.0)
    bucket = TokenBucket(capacity=10, refill_rate=5.0, now=clock)
    bucket.try_consume()
    clock.advance(100.0)  # 500 tokens would accrue, but the cap is 10
    assert bucket.available == 10.0
