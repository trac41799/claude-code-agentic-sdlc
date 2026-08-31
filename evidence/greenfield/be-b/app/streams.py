"""In-memory stream registry, token buckets, and the SSE delivery loop."""

import asyncio
import time
import uuid

from .sse import ERROR_SENTINEL, SHUTDOWN_SENTINEL, error_event, sse_data

DEFAULT_CAPACITY = 10
DEFAULT_REFILL_RATE = 5.0
DEFAULT_BUFFER_SIZE = 100
DEFAULT_HEARTBEAT = 15.0


class TokenBucket:
    """Per-client rate limiter: capacity tokens, refilled at rate tokens/sec.

    Tokens are computed lazily from the clock, so there is no background task
    and the bucket degrades gracefully under load.
    """

    def __init__(self, capacity=DEFAULT_CAPACITY, refill_rate=DEFAULT_REFILL_RATE, now=None):
        self.capacity = float(capacity)
        self.rate = float(refill_rate)
        self.tokens = self.capacity
        self._now = now if now is not None else time.monotonic
        self._last = self._now()

    def _refill(self):
        now = self._now()
        elapsed = now - self._last
        if elapsed > 0:
            self.tokens = min(self.capacity, self.tokens + elapsed * self.rate)
            self._last = now
        return now

    def try_consume(self):
        self._refill()
        if self.tokens >= 1.0:
            self.tokens -= 1.0
            return True
        return False

    @property
    def available(self):
        self._refill()
        return self.tokens


class Subscriber:
    __slots__ = ("id", "stream", "queue", "bucket", "dropped", "closed")

    def __init__(self, stream, bucket):
        self.id = uuid.uuid4().hex
        self.stream = stream
        self.queue = asyncio.Queue(maxsize=stream.buffer_size)
        self.bucket = bucket
        self.dropped = 0
        self.closed = False


class Stream:
    def __init__(self, stream_id, capacity, refill_rate, buffer_size):
        self.id = stream_id
        self.capacity = capacity
        self.refill_rate = refill_rate
        self.buffer_size = buffer_size
        self.subscribers = {}
        self.published = 0
        self.dropped = 0

    def add_subscriber(self):
        sub = Subscriber(self, TokenBucket(self.capacity, self.refill_rate))
        self.subscribers[sub.id] = sub
        return sub

    def remove_subscriber(self, sub):
        if self.subscribers.pop(sub.id, None) is not None:
            sub.closed = True

    def info(self):
        return {
            "id": self.id,
            "subscribers": len(self.subscribers),
            "published": self.published,
            "dropped": self.dropped,
        }


class StreamManager:
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

    def publish(self, stream_id, payload):
        """Broadcast an event to every subscriber without ever blocking.

        Bounded queues + put_nowait keep the publisher at O(subscribers) with
        no awaits; a full buffer triggers the overflow close path instead.
        """
        stream = self.get_stream(stream_id)
        stream.published += 1
        for sub in list(stream.subscribers.values()):
            if sub.closed:
                continue
            try:
                sub.queue.put_nowait(payload)
            except asyncio.QueueFull:
                # Slow consumer: evict the oldest buffered event to make room
                # for the error sentinel, then let the SSE loop close it.
                sub.closed = True
                try:
                    sub.queue.get_nowait()
                except asyncio.QueueEmpty:
                    pass
                sub.queue.put_nowait(ERROR_SENTINEL)

    def shutdown(self):
        self.shutting_down = True
        for stream in self.streams.values():
            for sub in list(stream.subscribers.values()):
                sub.closed = True
                try:
                    sub.queue.put_nowait(SHUTDOWN_SENTINEL)
                except asyncio.QueueFull:
                    try:
                        sub.queue.get_nowait()
                    except asyncio.QueueEmpty:
                        pass
                    try:
                        sub.queue.put_nowait(SHUTDOWN_SENTINEL)
                    except asyncio.QueueFull:
                        pass


async def stream_loop(manager, stream, sub):
    """Deliver one subscriber's queue as SSE chunks.

    - heartbeat comment after `manager.heartbeat` seconds of silence
    - token bucket drops events that arrive while it is empty (counted)
    - ERROR_SENTINEL emits a 429-style SSE error and closes
    - SHUTDOWN_SENTINEL flushes buffered events and closes
    """
    try:
        while True:
            try:
                item = await asyncio.wait_for(sub.queue.get(), timeout=manager.heartbeat)
            except asyncio.TimeoutError:
                yield ": heartbeat\n\n"
                continue
            if item is ERROR_SENTINEL:
                yield error_event(429, "buffer overflow")
                return
            if item is SHUTDOWN_SENTINEL:
                # Flush anything still buffered, then close cleanly.
                while True:
                    try:
                        pending = sub.queue.get_nowait()
                    except asyncio.QueueEmpty:
                        break
                    if pending is SHUTDOWN_SENTINEL:
                        break
                    if pending is ERROR_SENTINEL:
                        yield error_event(429, "buffer overflow")
                        return
                    yield sse_data(pending)
                return
            if sub.bucket.try_consume():
                yield sse_data(item)
            else:
                sub.dropped += 1
                stream.dropped += 1
    finally:
        stream.remove_subscriber(sub)


async def stream_events(manager, stream_id):
    """Async generator used by the SSE endpoint: subscribe, stream, clean up."""
    stream = manager.get_stream(stream_id)
    sub = stream.add_subscriber()
    async for chunk in stream_loop(manager, stream, sub):
        yield chunk
