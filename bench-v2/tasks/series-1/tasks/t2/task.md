# SERIES-1 · task 2 — config migration (removes magic constants)

Frozen brief (both arms). The service hardcodes pricing (`PRICE_MAPPING`),
`TAX_RATE`, `SHIP_FLAT` in `app/orders.py` and an unfinished parser in
`app/pricing.py`. Migrate to a real config boundary WITHOUT changing
observable behavior:

1. New `app/config.py` ships the constants (`PRICE_MAPPING`, `TAX_RATE`,
   `SHIP_FLAT`) with the same values, loaded from environment overrides
   (`PRICE_1024`, `TAX_RATE`, `SHIP_FLAT`) when present.
2. `OrderStore.create` reads pricing through `app.config` (no direct module
   constants).
3. Add `app/config.py` tests: defaults match old values; env override wins.
4. `OrderStore.labels()` behavior unchanged.

Acceptance gate: `python -m pytest tests/ -q` passes.

## Hidden rubric
`rubric-hidden-tests/` — the delivered code must keep every existing test
green and the env-override path correct (including a missing-env fallback to
the shipped defaults).