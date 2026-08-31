"""Helpers for driving the app over a real uvicorn socket (true SSE streaming)."""

import threading
import time

import uvicorn


class UvicornServer:
    """Run a uvicorn app in a background thread on an ephemeral port."""

    def __init__(self, app, host="127.0.0.1", port=0, timeout_graceful_shutdown=0.5):
        self.app = app
        self.host = host
        self.port = port
        self.timeout_graceful_shutdown = timeout_graceful_shutdown
        self.server = None
        self.thread = None

    def start(self):
        config = uvicorn.Config(
            self.app,
            host=self.host,
            port=self.port,
            log_level="warning",
            timeout_graceful_shutdown=self.timeout_graceful_shutdown,
        )
        self.server = uvicorn.Server(config)
        self.thread = threading.Thread(target=self.server.run, daemon=True)
        self.thread.start()

        deadline = time.monotonic() + 10
        while not getattr(self.server, "started", False) and time.monotonic() < deadline:
            time.sleep(0.01)
        if not getattr(self.server, "started", False):
            raise RuntimeError("uvicorn failed to start")

        sock = self.server.servers[0].sockets[0]
        self.port = sock.getsockname()[1]
        return self.port

    def stop(self):
        if self.server is not None:
            self.server.should_exit = True
            self.thread.join(timeout=8)
