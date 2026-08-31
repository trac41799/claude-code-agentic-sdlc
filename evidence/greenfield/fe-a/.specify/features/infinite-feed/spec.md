# Feature Spec — Infinite activity feed

- **Slug:** `infinite-feed`
- **Epic:** Infinite activity feed (see `docs/product/epics.md`)
- **Status:** Implemented and QA-verified

## Problem

A feed that never ends cannot render all rows at once. A like that waits for
the server feels broken. Both problems are solved with two small, pure,
testable pieces of frontend logic.

## 1. Windowing engine — `computeVisibleRange`

Signature (exported from `engine.js`):

```
computeVisibleRange(scrollTop, viewportHeight, items, rowHeight, overscan) -> { start, end }
```

- `items` is the full list; only `items.length` is used.
- `end` is **exclusive** (half-open `[start, end)`), matching
  `items.slice(start, end)`.
- `scrollTop` is clamped to `[0, max(0, items.length * rowHeight - viewportHeight)]`
  before any math, so both over-scroll at the bottom and negative scroll at the
  top produce valid windows.
- `overscan` is floored and applied above and below, then clipped at the list
  boundaries (start never below 0, end never above `items.length`).
- Empty list returns `{ start: 0, end: 0 }`.

**Reference constants used across tests and demo:** `rowHeight = 40`,
`viewportHeight = 600`, `overscan = 2`, `items.length = 10000`.

Expected windows for those constants:

| scrollTop | start | end |
|-----------|-------|-----|
| 0 (top) | 0 | 17 |
| 4000 (mid) | 98 | 117 |
| 200000 (mid) | 4998 | 5017 |
| 399400 (maxScroll, bottom clamp) | 9983 | 10000 |
| 399400 + 99999 (beyond end) | 9983 | 10000 |
| 80 (overscan clipped at top) | 0 | 19 |
| 120 (overscan no longer clipped) | 1 | 20 |

## 2. Optimistic-like engine — `OptimisticLikeSet`

Class exported from `engine.js`. API:

| Method | Behaviour |
|--------|-----------|
| `add(id)` | Register a pending like for `id`; increments its counter. |
| `contains(id)` | `true` while `id` has at least one pending like. |
| `rollback(id)` | Revert one pending like for `id`; removes it when the counter hits 0. Returns `false` if `id` was never added (no-op). |
| `size()` | Number of ids with at least one pending like. |

**Correctness invariants:**
- Interleaving: `add(A); add(B); rollback(A)` leaves `B` present, `A` gone.
- Re-entrancy: `add(A); add(A); rollback(A)` leaves `A` present (one op still
  pending).
- No negative counts: `add(A); rollback(A); rollback(A)` — the second rollback
  is a no-op.
- Rollback of a never-added id never changes `size()`.

## 3. Demo — `demo.html`

- Generates 10,000 items with fixed `rowHeight = 40`.
- Uses `computeVisibleRange` on every scroll/resize (rAF-throttled) to render
  only the visible window + `overscan = 3`.
- A spacer div sizes the scrollbar; the rendered window is absolutely
  positioned with `translateY(start * rowHeight)`.
- Like buttons update instantly via `OptimisticLikeSet` and roll back on a
  simulated **30% failure** after a short random delay.

## Out of scope

Backend, persistence, auth, real network requests.

## Acceptance

1. `node --test tests/` passes.
2. `engine.js` is dependency-free.
3. `demo.html` DOM row count stays far below 10,000 at every scroll position.
4. Optimistic-like interleaving invariants hold (see §2).

## Test mapping

- Window math / clamping / overscan / empty / short lists:
  `tests/engine.test.js`.
- OptimisticLikeSet invariants: `tests/optimistic.test.js`.
- Entry point for the Windows directory quirk: `tests/index.js`.
