"""Tunable service settings.

All values are the GREENFIELD-3 defaults; tests may construct a Settings with
shorter heartbeat intervals or a more permissive bucket to keep runs fast and
deterministic.
"""

from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True)
class Settings:
    """Runtime knobs for a stream's per-client behaviour."""

    bucket_capacity: int = 10
    bucket_refill_rate: float = 5.0
    buffer_size: int = 100
    heartbeat_seconds: float = 15.0
