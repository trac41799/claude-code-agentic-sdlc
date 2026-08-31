# Tasks — Infinite activity feed

Slug: `infinite-feed` · Plan: `.specify/features/infinite-feed/impl-plan.md`

All items complete. Symbols/files below are the delivered artifacts.

| # | Task | Delivered in | Status |
|---|------|--------------|--------|
| 1 | Implement `computeVisibleRange(scrollTop, viewportHeight, items, rowHeight, overscan)` with clamping, overscan clipping, empty-list handling, array type guard | `engine.js` | ✅ Done |
| 2 | Implement `OptimisticLikeSet` with `add(id)`, `contains(id)`, `rollback(id)`, `size()` and per-id pending counters | `engine.js` | ✅ Done |
| 3 | UMD wrapper: `module.exports` for Node + `InfiniteFeed`/global exposure for the browser; zero `import`/`require` | `engine.js` | ✅ Done |
| 4 | Write window-math tests: top, mid-list, bottom-clamp, beyond-end, negative scroll, overscan both boundaries, `overscan=0`, empty list, short list, non-integer offset, array guard | `tests/engine.test.js` | ✅ Done |
| 5 | Write OptimisticLikeSet tests: interleaving, never-added rollback no-op, no negative counts, re-add | `tests/optimistic.test.js` | ✅ Done |
| 6 | Add `tests/index.js` entry point for the `node --test tests/` directory quirk | `tests/index.js` | ✅ Done |
| 7 | Build `demo.html`: 10,000-item feed, fixed 40px rows, windowed rendering via `computeVisibleRange` + spacer/translated window | `demo.html` | ✅ Done |
| 8 | Wire optimistic like buttons with simulated 30% failure and rollback via `OptimisticLikeSet` | `demo.html` | ✅ Done |
| 9 | Run `node --test tests/` (acceptance) | — | ✅ 22/22 pass |
| 10 | Verify `engine.js` dependency-free + headless-browser check of `demo.html` | — | ✅ Pass |

## Dependency order

1 → 2 → 3 → (4, 5, 6) → 7 → 8 → (9, 10).

## Done definition

- `node --test tests/` exits 0.
- `demo.html` shows a working virtualized feed in a real browser with
  optimistic likes that roll back on simulated failure.
