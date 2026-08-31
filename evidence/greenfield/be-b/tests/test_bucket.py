import pytest

from app.streams import TokenBucket


class FakeClock:
    def __init__(self, start=0.0):
        self.t = start

    def __call__(self):
        return self.t

    def advance(self, dt):
        self.t += dt


def test_burst_of_10_passes_then_11th_dropped():
    clock = FakeClock(0.0)
    bucket = TokenBucket(capacity=10, refill_rate=5.0, now=clock)
    assert bucket.tokens == 10.0
    assert all(bucket.try_consume() for _ in range(10))
    assert not bucket.try_consume()


def test_refill_is_5_per_second():
    clock = FakeClock(0.0)
    bucket = TokenBucket(capacity=10, refill_rate=5.0, now=clock)
    bucket.try_consume()  # consume everything first
    for _ in range(9):
        bucket.try_consume()

    clock.advance(1.0)
    assert bucket.available == pytest.approx(5.0, abs=1e-6)
    clock.advance(1.0)
    assert bucket.available == pytest.approx(10.0, abs=1e-6)


def test_tokens_cap_at_capacity():
    clock = FakeClock(0.0)
    bucket = TokenBucket(capacity=10, refill_rate=5.0, now=clock)
    bucket.try_consume()
    clock.advance(100.0)
    assert bucket.available == 10.0


def test_refill_over_two_seconds_yields_ten_tokens():
    clock = FakeClock(0.0)
    bucket = TokenBucket(capacity=10, refill_rate=5.0, now=clock)
    for _ in range(10):
        bucket.try_consume()
    clock.advance(2.0)
    # 5/sec * 2s = 10 tokens, capped at capacity
    assert bucket.available == pytest.approx(10.0, abs=1e-6)
    assert all(bucket.try_consume() for _ in range(10))
    assert not bucket.try_consume()
