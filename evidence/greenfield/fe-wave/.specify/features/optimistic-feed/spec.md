# Spec — Infinite Activity Feed (Optimistic Likes)

**Slug:** `optimistic-feed`
**Date:** 2026-08-31
**Status:** APPROVED (brief is frozen — GREENFIELD-2 FE-only)
**Product doc:** `docs/product/product.md`

## Summary

Build a dependency-free JS engine + HTML demo for a 10,000-item activity feed
that (a) renders only the visible window via virtualization and (b) gives
instant optimistic like buttons that roll back cleanly on simulated failure.

## Contracts

### `computeVisibleRange(scrollTop, viewportHeight, items, rowHeight, overscan)`

Pure function. Returns `{ start, end }` where `start` is inclusive, `end` is
exclusive (slice semantics) — the row indices that must be rendered.

- `items` is the full feed array; only `items.length` is read.
- `start` is clamped to `>= 0`.
- `end` is clamped to `<= items.length`.
- `overscan` is the number of extra rows rendered above/below the viewport.
- **Empty `items`** → `{ start: 0, end: 0 }`.
- **`scrollTop` at the very end** (beyond `items.length * rowHeight - viewportHeight`)
  → clamp so the window covers the last rows and never exceeds the list.
- Non-positive `rowHeight` or `viewportHeight`, or negative `scrollTop`/`overscan`
  → defensive: return `{ start: 0, end: 0 }` / clamp as appropriate (never throw).

### `OptimisticLikeSet`

Set-like collection keyed by item id, used so a failed like request can be
rolled back without disturbing other pending likes.

| Method | Behavior |
|---|---|
| `add(id)` | Adds `id` if absent. Returns the new size. |
| `contains(id)` | `true` if `id` is present, else `false`. |
| `rollback(id)` | Removes `id`. **No-op if `id` was never added.** |
| `size()` | Number of ids currently held. |

Key invariant: rollback of one id removes **only** that id — `add(A), add(B),
rollback(A)` leaves `B` present.

## Module format

`engine.js` must be dependency-free and work in both runtimes:

- **Node (tests):** CommonJS `module.exports`.
- **Browser (demo):** exposes a global (`FeedEngine`) via `window` when loaded
  with a plain `<script src="engine.js">`.

## Acceptance criteria

- **AC-1 (window math, mid):** at a mid-list scroll position, `{start, end}` spans
  exactly `floor(scrollTop/rowHeight) - overscan` … `ceil((scrollTop+viewportHeight)/rowHeight) + overscan`, clamped to the list.
- **AC-2 (window math, top):** at `scrollTop = 0`, `start === 0` and the overscan
  below the viewport is included.
- **AC-3 (window math, bottom / clamp):** at the maximum scroll position, `end === items.length` and the window covers the last rows; an over-large `scrollTop` clamps to the same window (never out of bounds).
- **AC-4 (empty list):** `items = []` → `{ start: 0, end: 0 }`.
- **AC-5 (overscan clipping):** for small lists where `overscan` exceeds the
  remaining rows, `start` never drops below 0 and `end` never exceeds `items.length` (both boundaries).
- **AC-6 (optimistic interleaving):** `add(A)`, `add(B)`, `rollback(A)` → `contains(B) === true`, `size() === 1`.
- **AC-7 (rollback no-op):** `rollback(neverAdded)` leaves the set unchanged and throws nothing.
- **AC-8 (engine purity):** `engine.js` has zero imports/requires and exports via both CommonJS and browser global.
- **AC-9 (demo virtualization):** `demo.html` renders 10,000 items but keeps only the visible window (+ overscan) in the DOM.
- **AC-10 (demo optimistic like + rollback):** like buttons update instantly; on simulated failure (random 30%) the like rolls back without affecting other rows' pending likes.
- **AC-11 (suite green):** `node --test tests/` passes.

## Out of scope

Real network layer, persistence, frameworks, bundlers, external deps, commit/push.
