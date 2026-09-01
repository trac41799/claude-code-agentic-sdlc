# SERIES-1 · task 1 — order status tracking + notifications (feature)

Frozen brief (identical for both arms). You are working in a legacy
catalog/order service. Add order status tracking end-to-end:

- `OrderStore` statuses become an explicit state machine:
  CREATED → PAID → SHIPPED → DELIVERED (and CANCELLED from CREATED/PAID).
- Only valid transitions are allowed; invalid ones raise `ValueError`.
- When an order reaches PAID, a notification stub records it in
  `app/notifications.py` (a function `notify(order_id, kind)` that appends to
  an in-memory list `SENT`); it must be called exactly once per transition.
- Add tests (pytest) covering: valid transitions, invalid transition raises,
  notify-once on repeat shipping attempts, and a method `history(order_id)`
  returning the ordered transition list.

Acceptance gate: `python -m pytest tests/ -q` passes.

## Hidden rubric (held-out — will be run against your code)
See `rubric-hidden-tests/` in the task package; your implementation must satisfy
those too (they are NOT part of the acceptance gate above).

## Rules
Do not commit; leave the working tree as-is. Keep the change limited to the
service package (no new top-level infra).