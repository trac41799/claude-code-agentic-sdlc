# Epics — Infinite

## Epic 1: Infinite activity feed (virtualized rendering + optimistic likes)

**Goal.** Deliver a frontend-only activity feed that renders 10,000 items while
keeping only the visible window in the DOM, and lets users like items
instantly with safe rollback when a like request fails.

**Narrative.** A social feed grows without bound. Rendering every row would
choke the browser, and a network round-trip before the heart fills would feel
laggy. The epic splits the problem into two small, independently testable
engines: one that computes exactly which rows belong in the viewport (and
clamps safely at the edges), and one that tracks optimistic likes so a failed
request only reverts its own id, never a neighbour's.

**In scope.**
- `computeVisibleRange(scrollTop, viewportHeight, items, rowHeight, overscan)`
  in `engine.js`: exact half-open window `{start, end}`, scrollTop clamped to
  `[0, maxScroll]`, empty list -> `{start: 0, end: 0}`, overscan clipped at
  both boundaries.
- `OptimisticLikeSet` in `engine.js`: `add(id)`, `contains(id)`,
  `rollback(id)`, `size()`; rollback of one id must not remove an id added
  after it; rollback of a never-added id is a no-op.
- `demo.html`: 10,000-item feed, fixed 40px rows, only visible window + overscan
  rendered, like buttons optimistic with a simulated 30% failure rate that
  reverts on failure.
- `tests/` using only `node:test` and `node:assert`.

**Out of scope.** Backend, persistence, real network requests, auth, mobile
native clients.

**Acceptance.**
1. `node --test tests/` passes.
2. `engine.js` is dependency-free (no `import` / `require`).
3. `demo.html` renders windowed rows: DOM row count is a small fraction of
   10,000 at every scroll position.
4. Optimistic-like interleaving holds: add A, add B, rollback A -> B remains;
   rollback never-added -> no-op with size unchanged.

**Epic status:** see `docs/product/epic-status.md`.
