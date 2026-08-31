# Implementation Plan — Infinite Activity Feed (Optimistic Likes)

**Slug:** `optimistic-feed`
**Date:** 2026-08-31
**Spec:** `.specify/features/optimistic-feed/spec.md` · `docs/product/product.md`
**Branch:** `main` (deliberately not on a feature branch — brief forbids commits; work stays in the working tree)

## Phase 0 — Outline & research

**In scope (this build):**
- `engine.js` — `computeVisibleRange` + `OptimisticLikeSet`, dependency-free, CommonJS + browser-global.
- `tests/` — Node built-in test runner (`node --test tests/`), two files with disjoint scope.
- `demo.html` — 10,000-item virtualized feed with optimistic like buttons (30% simulated failure).

**Deferred:** real network layer, persistence, any framework/bundler. Not needed for acceptance.

**Prototype needed?** No — window math and set semantics are small and fully specified by AC-1…AC-7. No hard unknowns.

**Risks & assumptions:**
| Risk | Mitigation |
|---|---|
| RED evidence could fail for the wrong reason (module load error instead of assertion) if `engine.js` doesn't exist | Coordinator writes a **stub** `engine.js` before Wave 1 so tests load and fail on assertions |
| Window math off-by-one at boundaries (end clamp, overscan) | Pin the math in the spec (AC-1…AC-5) and encode exact expected values in tests before any implementation |
| Rollback semantics regress to "stack" behavior | AC-6/AC-7 encode interleaving + no-op invariants |
| Demo leaves too many rows in DOM, defeating virtualization | demo.html renders only `[start, end)` into the container; container height is the spacer (`items.length * rowHeight`) |

## Phase 1 — Design & contracts

### Architecture

Three artifacts, one vertical slice each:

```
tests/visible-range.test.js  ──┐
tests/optimistic-like.test.js ──┼─▶ engine.js (pure, dependency-free)
demo.html ─────────────────────┘
```

### Contracts (see spec.md for full table)

- `computeVisibleRange(scrollTop, viewportHeight, items, rowHeight, overscan) → {start, end}`
  - `start = max(0, floor(scrollTop / rowHeight) - overscan)`
  - `end = min(items.length, ceil((scrollTop + viewportHeight) / rowHeight) + overscan)`
  - `scrollTop` clamped to `[0, max(0, items.length * rowHeight - viewportHeight)]` first (bottom clamp).
  - `items.length === 0` or non-positive `rowHeight`/`viewportHeight` → `{start: 0, end: 0}`.
- `OptimisticLikeSet` — Set keyed by id; `add` returns new size, `contains` boolean, `rollback` removes exactly `id` (no-op if absent), `size()` count.

### Module format

UMD-lite: `module.exports` when CommonJS; otherwise attach to `window.FeedEngine`.

### UI/UX flow (demo.html)

1. Fixed-height scroll container; inner spacer div of height `items.length * rowHeight`.
2. On scroll/resize → `computeVisibleRange(...)` → render only rows `[start, end)` absolutely positioned at `index * rowHeight`.
3. Like button per row → `likes.add(id)` → re-style instantly. Then `setTimeout` simulates the request: 70% success (keep), 30% failure → `likes.rollback(id)` + revert style. A failed rollback never touches other rows because each row's state is derived from `likes.contains(id)`.

### Testing strategy

- **Unit (all of it):** exact window math mid/top/bottom, clamp, empty list, overscan clipping, optimistic interleaving, rollback no-op.
- **Integration:** demo is a static HTML file; verified by inspection + the engine unit suite. No browser automation in scope (zero-dependency constraint).

## Phase 2 — Milestones (mapped to spec AC)

| Milestone | Delivers | AC |
|---|---|---|
| M1 — Test suite (RED) | tests/visible-range.test.js, tests/optimistic-like.test.js | AC-1…AC-7, AC-11 |
| M2 — engine.js (GREEN) | `computeVisibleRange`, `OptimisticLikeSet`, UMD-lite export | AC-1…AC-8 |
| M3 — demo.html | Virtualized 10,000-item feed + optimistic like/rollback | AC-9, AC-10 |
| M4 — QA + wave report | qa-triage report, wave-report.md, final green suite | AC-11 |

Effort: M1 S · M2 S · M3 M · M4 S.
Dependencies: M1 → M2 → M3; M4 after M3.

**NEXT:** start dev-tdd on Task 1.1 — each test cites the AC it validates.
