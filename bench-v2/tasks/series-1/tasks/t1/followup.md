# SERIES-1 · follow-up 1 (on task 1's delivered code) — discount + edge guard

Frozen brief (both arms, run after task 1 with the working tree preserved from
task 1; treat it as a hotfix from a backlog report):

1. A customer applied `SAVE10` twice in one day; the current `apply_coupon`
   multiplies total by 0.9 repeatedly. Change it: `SAVE10` may only apply
   once per order (record `coupon_used` on the order); a second attempt is a
   no-op (not an error), and total stays intact.
2. Add one regression test asserting double-coupon does not reduce further.

Acceptance gate: `python -m pytest tests/ -q` passes (the task-1 tests still
pass too). Keep the diff surgical; `OrderStore`'s public shape stays
(no renaming).