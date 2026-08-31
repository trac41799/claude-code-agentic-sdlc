"""In-memory stream registry, per-client token buckets, and the SSE delivery loop.

Design notes
------------
* Publish is fully synchronous: it never ``await``s, so a publisher can never
  be blocked by a slow consumer. Each subscriber owns a bounded
  ``asyncio.Queue``; once it is full the subscriber is marked closed and an
  error sentinel is queued so the delivery loop emits a 429-style SSE error
  and tears the connection down.
* Token buckets are refilled lazily from ``time.monotonic`` on demand, so no
  background task is needed and idle buckets cost nothing.
* The delivery loop is an async generator: the only resources it owns live in
  the loop body's ``finally``, so closing the connection (client disconnect,
  error, shutdown) always removes the subscriber from the stream.
"""

import asyncio
import time
import uuid

from .sse import (
    ERROR_SENTINEL,
    OVERFLOW_DETAIL,
    OVERFLOW_STATUS,
    SHUTDOWN_SENTINEL,
    error_event,
    heartbeat_event,
    sse_data,
)

DEFAULT_CAPACITY = 10
DEFAULT_REFILL_RATE = 5.0
DEFAULT_BUFFER_SIZE = 100
DEFAULT_HEARTBEAT = 15.0


class TokenBucket:
    """Per-client rate limiter: ``capacity`` tokens, refilled at ``refill_rate``/s.

    Tokens are computed lazily from the clock: ``try_consume`` first credits the
    elapsed time since the last call, then spends one token if available. A
    caller may inject ``now`` (a ``() -> float``) for deterministic tests.
    """

    def __init__(self, capacity=DEFAULT_CAPACITY, refill_rate=DEFAULT_REFILL_RATE, now=None):
        self.capacity = float(capacity)
        self.rate = float(refill_rate)
        self.tokens = self.capacity
        self._now = now if now is not None else time.monotonic
        self._last = self._now()

    def _refill(self) -> float:
        now = self._now()
        elapsed = now - self._last
        if elapsed > 0:
            self.tokens = min(self.capacity, self.tokens + elapsed * self.rate)
            self._last = now
        return now

    def try_consume(self) -> bool:
        """Spend one token if available, otherwise return ``False``."""
        self._refill()
        if self.tokens >= 1.0:
            self.tokens -= 1.0
            return True
        return False

    @property
    def available(self) -> float:
        """Current token balance (after applying any accrued refill)."""
        self._refill()
        return self.tokens


class Subscriber:
    """One connected SSE client on a stream: its queue, bucket and drop count."""

    __slots__ = ("id", "stream", "queue", "bucket", "dropped", "closed")

    def __init__(self, stream):
        self.id = uuid.uuid4().hex
        self.stream = stream
        self.queue = asyncio.Queue(maxsize=stream.buffer_size)
        self.bucket = TokenBucket(stream.capacity, stream.refill_rate)
        self.dropped = 0
        self.closed = False


class Stream:
    """A named broadcast channel holding its subscribers and counters."""

    def __init__(self, stream_id, capacity, refill_rate, buffer_size):
        self.id = stream_id
        self.capacity = capacity
        self.refill_rate = refill_rate
        self.buffer_size = buffer_size
        self.subscribers = {}
        self.published = 0
        self.dropped = 0

    def add_subscriber(self) -> Subscriber:
        sub = Subscriber(self)
        self.subscribers[sub.id] = sub
        return sub

    def remove_subscriber(self, sub) -> None:
        if self.subscribers.pop(sub.id, None) is not None:
            sub.closed = True

    def info(self) -> dict:
        return {
            "id": self.id,
            "subscribers": len(self.subscribers),
            "published": self.published,
            "dropped": self.dropped,
        }


class StreamManager:
    """Owns all streams; the single broadcast entry point for the app."""

    def __init__(
        self,
        capacity=DEFAULT_CAPACITY,
        refill_rate=DEFAULT_REFILL_RATE,
        buffer_size=DEFAULT_BUFFER_SIZE,
        heartbeat=DEFAULT_HEARTBEAT,
    ):
        self.capacity = capacity
        self.refill_rate = refill_rate
        self.buffer_size = buffer_size
        self.heartbeat = heartbeat
        self.streams = {}
        self.shutting_down = False

    def get_stream(self, stream_id, create=True):
        stream = self.streams.get(stream_id)
        if stream is None and create:
            stream = Stream(stream_id, self.capacity, self.refill_rate, self.buffer_size)
            self.streams[stream_id] = stream
        return stream

    def publish(self, stream_id, payload) -> None:
        """Broadcast ``payload`` to every subscriber without ever blocking.

        Bounded queues + ``put_nowait`` keep this O(subscribers) with no
        awaits; a full buffer triggers the overflow close path instead.
        """
        stream = self.get_stream(stream_id)
        stream.published += 1
        for sub in tuple(stream.subscribers.values()):
            if sub.closed:
                continue
            try:
                sub.queue.put_nowait(payload)
            except asyncio.QueueFull:
                self._mark_overflow(sub)

    def shutdown(self) -> None:
        """Mark every subscriber closed and ask its loop to flush + exit."""
        self.shutting_down = True
        for stream in self.streams.values():
            for sub in tuple(stream.subscribers.values()):
                sub.closed = True
                self._enqueue(sub, SHUTDOWN_SENTINEL)

    @staticmethod
    def _mark_overflow(sub) -> None:
        sub.closed = True
        try:
            sub.queue.get_nowait()  # evict the oldest buffered event
        except asyncio.QueueEmpty:
            pass
        try:
            sub.queue.put_nowait(ERROR_SENTINEL)
        except asyncio.QueueFull:
            pass

    @staticmethod
    def _enqueue(sub, sentinel) -> None:
        try:
            sub.queue.put_nowait(sentinel)
        except asyncio.QueueFull:
            try:
                sub.queue.get_nowait()
            except asyncio.QueueEmpty:
                pass
            try:
                sub.queue.put_nowait(sentinel)
            except asyncio.QueueFull:
                pass


async def stream_loop(manager, stream, sub):
    """Yield SSE chunks for one subscriber until it is closed.

    * a heartbeat comment after ``manager.heartbeat`` seconds of silence
    * events are admitted through the token bucket; denied ones are dropped
      (counted on the subscriber and the stream)
    * ``ERROR_SENTINEL``   -> emit a 429-style error event and close
    * ``SHUTDOWN_SENTINEL`` -> flush any buffered events, then close
    """
    try:
        while True:
            try:
                item = await asyncio.wait_for(sub.queue.get(), timeout=manager.heartbeat)
            except asyncio.TimeoutError:
                yield heartbeat_event()
                continue

            if item is ERROR_SENTINEL:
                yield error_event(OVERFLOW_STATUS, OVERFLOW_DETAIL)
                return
            if item is SHUTDOWN_SENTINEL:
                async for chunk in _flush_remaining(sub):
                    yield chunk
                return
            if sub.bucket.try_consume():
                yield sse_data(item)
            else:
                sub.dropped += 1
                stream.dropped += 1
    finally:
        stream.remove_subscriber(sub)


async def _flush_remaining(sub):
    """Drain a subscriber's queue ahead of a shutdown sentinel, then stop."""
    while True:
        try:
            pending = sub.queue.get_nowait()
        except asyncio.QueueEmpty:
            return
        if pending is SHUTDOWN_SENTINEL:
            return
        if pending is ERROR_SENTINEL:
            yield error_event(OVERFLOW_STATUS, OVERFLOW_DETAIL)
            return
        yield sse_data(pending)


async def stream_events(manager, stream_id):
    """Async generator backing the SSE endpoint: subscribe, stream, clean up."""
    stream = manager.get_stream(stream_id)
    sub = stream.add_subscriber()
    async for chunk in stream_loop(manager, stream, sub):
        yield chunk
