"""Init script: apply schema.sql to a SQLite database.

Usage:
    python -m etl.init_db [db_path]
"""

from __future__ import annotations

import argparse
import sys
from pathlib import Path

if __package__ in (None, ""):  # allow `python etl/init_db.py`
    sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from etl.db import init_db  # noqa: E402


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Apply schema.sql to a SQLite database.")
    parser.add_argument(
        "db_path",
        nargs="?",
        default=None,
        help="Path to the SQLite DB (default: data/events.db or $FROAM_DB)",
    )
    args = parser.parse_args(argv)
    path = init_db(args.db_path)
    print(f"initialized database at {path}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
