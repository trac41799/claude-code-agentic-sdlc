"""Application settings for the Research Request Pipeline."""

from dataclasses import dataclass


@dataclass
class Settings:
    """Runtime configuration for a single app instance.

    Each ``create_app(...)`` call builds its own Settings so apps are fully
    isolated (own DB, own worker, own broadcaster).
    """

    db_path: str = "./data/app.db"
    work_delay: float = 0.2
    worker_poll_interval: float = 0.05
    worker_enabled: bool = True
