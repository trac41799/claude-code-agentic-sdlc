GREENFIELD-2 (FE-only) TASK BRIEF (frozen, identical for both arms)

Idea: "Infinite activity feed with virtualized rendering and optimistic likes" — a feed where users can like items instantly (optimistic UI) and the list renders only the visible window.

Build it as a dependency-free JS engine + HTML demo:
- `engine.js`: exports a pure function `computeVisibleRange(scrollTop, viewportHeight, items, rowHeight, overscan)` returning {start, end} for windowed rendering, plus an `OptimisticLikeSet` class: `add(id)`, `contains(id)`, `rollback(id)`, `size()` — used so a failed like request can be rolled back without disturbing other pending likes.
- Edge cases the engine must handle: scrollTop at very end (clamp), empty items, overscan clipping at both boundaries, multiple add/rollback interleavings (rollback of one id must not remove a different id added after it).
- `demo.html`: renders a 10,000-item feed with fixed row height, renders only the visible window (+ overscan), like buttons update instantly and roll back on simulated failure (random 30% failure).
- Tests (node built-in test runner, no deps): `node --test tests/` covering: exact window math for mid/start/end scroll positions, clamping, empty list, overscan boundary, optimistic like interleaving (add A, add B, rollback A → B still present; rollback of an id never added is a no-op).

Acceptance: `node --test tests/` passes; `engine.js` has zero dependencies.

Do not commit. Leave changes in the working tree.