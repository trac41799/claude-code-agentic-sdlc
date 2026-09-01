# SERIES-1 · task 3 — N+1 inventory fix (perf)

Frozen brief (both arms). `app/inventory.py::deduct_all` is called per SKU in
a loop (N+1 style) with a single global dict and no guard. Fix:

1. Add `deduct_many(skus: dict) -> dict` that adjusts multiple SKUs
   atomically (all-or-nothing: raise before mutating if ANY SKU lacks stock).
2. Keep `deduct_all(sku, qty)` working (backward compat shim over
   `deduct_many`).
3. `items()` returns snapshot ordering stable.
4. Add tests: atomic multi-deduct, partial failure leaves stock unchanged,
   backward-compat shim.

Acceptance gate: `python -m pytest tests/ -q` passes.

## Hidden rubric
`rubric-hidden-tests/` — atomicity under a partial-failure order and shim
parity (single-SKU results identical pre/post change).