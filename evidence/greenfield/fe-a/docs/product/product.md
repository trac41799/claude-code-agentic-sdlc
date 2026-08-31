# Infinite — Activity Feed

## Overview

**Infinite** is a dependency-free activity-feed engine and demo for a feed that
feels unlimited: a 10,000-item list that scrolls at 60fps because only the
visible window is ever in the DOM, and likes that respond the instant you click
them because they are optimistic.

Two small, well-tested pieces make this possible, both delivered in
`engine.js`:

- `computeVisibleRange(scrollTop, viewportHeight, items, rowHeight, overscan)`
  — a pure function that returns the half-open index range `{start, end}` of
  rows that must be rendered for a given scroll position. Handles clamping at
  the top and bottom, empty lists, and overscan clipping at both boundaries.
- `OptimisticLikeSet` — a class (`add(id)`, `contains(id)`, `rollback(id)`,
  `size()`) that tracks pending optimistic likes with a per-id counter, so a
  failed like request can be rolled back without disturbing any other pending
  like.

`demo.html` ties them together into a working 10,000-item feed: fixed 40px
rows, only the visible window (+ overscan) in the DOM, and like buttons that
flip instantly and revert on a simulated 30% failure rate.

## Scope (FE-only)

- `engine.js` — the pure windowing math and the optimistic-like set. Zero
  dependencies; loads as a CommonJS module and as browser globals.
- `demo.html` — the interactive virtualized feed demo.
- `tests/` — Node's built-in test runner (`node:test` / `node:assert`, no
  dependencies) covering exact window math and optimistic-like interleavings.

Out of scope: persistence, server-side likes, auth, and any backend. This is a
frontend-only deliverable.

## Success criteria

- `node --test tests/` passes.
- `engine.js` contains no `import` / `require` (dependency-free).
- `demo.html` keeps the DOM row count orders of magnitude below the 10,000-item
  data set while scrolling.
- Liking is optimistic and rollback-safe: rolling back one id never removes a
  different id added after it, and rolling back a never-added id is a no-op.

## Key files

| File | Purpose |
|------|---------|
| `engine.js` | `computeVisibleRange` + `OptimisticLikeSet` |
| `demo.html` | Virtualized feed demo with optimistic likes |
| `tests/engine.test.js` | Window-math, clamping, overscan, empty-list tests |
| `tests/optimistic.test.js` | OptimisticLikeSet interleaving tests |
| `tests/index.js` | Entry point so `node --test tests/` resolves on Windows |
