# SERIES-1 · follow-up 2 (on task 2's delivered code) — rollback safety

Frozen brief (run after task 2 with the tree preserved; treat as an ops
incident):

1. The config migration shipped but a config file written by an operator used
   `TAX_RATE=custom` (works) — then an old partial deploy set `SHIP_FLAT` to
   an empty string. `get_pricing()` must treat empty/blank env values as
   missing and fall back to the shipped default.
2. Add a regression test: `SHIP_FLAT=""` yields the default, not 0.

Acceptance gate: `python -m pytest tests/ -q` passes.