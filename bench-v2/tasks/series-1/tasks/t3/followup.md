# SERIES-1 · follow-up 3 (on task 3's delivered code) — retry semantics

Frozen brief (run after task 3; ops-replay style). The multi-deduct shipped
but a retry loop in the caller replays a previously-applied order (double
deduct). Fix:

1. `deduct_many` accepts `idempotency_key` (string) recorded on the applied
   keys; replaying the same key is a no-op returning the original result.
2. Regression test: apply twice with the same key → stock changed exactly
   once.

Acceptance gate: `python -m pytest tests/ -q` passes.