# Implementation Plan — Infinite activity feed

Slug: `infinite-feed` · Spec: `.specify/features/infinite-feed/spec.md`

## Phases

### Phase 1 — Engine (`engine.js`)
1. Write `computeVisibleRange(scrollTop, viewportHeight, items, rowHeight, overscan)`:
   - Validate `items` is an array (`TypeError` otherwise).
   - `maxScroll = max(0, items.length * rowHeight - viewportHeight)`.
   - Clamp `scrollTop` into `[0, maxScroll]`.
   - `start = max(0, floor(scrollTop / rowHeight) - overscan)`.
   - `end = min(items.length, floor(scrollTop / rowHeight) + ceil(viewportHeight / rowHeight) + overscan)`.
   - Return `{ start, end }` (end exclusive).
2. Write `OptimisticLikeSet` with a `Map<id, count>`:
   - `add(id)` increments; `contains(id)` is `count > 0`; `rollback(id)`
     decrements/removes and returns whether it removed; `size()` returns the
     number of ids with `count > 0`.
3. Wrap in a UMD-style loader: `module.exports` for Node, `InfiniteFeed` +
   convenience globals for the browser. No `import` / `require`.

### Phase 2 — Tests (`tests/`)
1. `tests/engine.test.js` — exact window math (top / mid / bottom-clamp /
   beyond-end / negative), overscan clipping at both boundaries, `overscan=0`,
   empty list, list shorter than the viewport, non-integer offsets, array type
   guard. Constants: `rowHeight = 40`, `viewportHeight = 600`, `overscan = 2`,
   `items.length = 10000`.
2. `tests/optimistic.test.js` — empty start, add/contains/size, distinct ids,
   the brief's interleaving (`add A`, `add B`, `rollback A` -> `B` remains),
   never-added rollback no-op, no negative counts, re-add after rollback.
3. `tests/index.js` — entry point requiring both test files so `node --test
   tests/` resolves where the runner treats the bare directory as a module
   (Node 24 / Windows). Not named `*.test.js`, so pattern discovery elsewhere
   does not double-run.

### Phase 3 — Demo (`demo.html`)
1. Generate 10,000 items (`id`, name, text, timestamp, avatar colour).
2. Scroll container with a height-scaled spacer; windowed rows absolutely
   positioned, translated by `start * rowHeight`.
3. Reconcile a `Map<index, element>` on each rAF-throttled render: remove rows
   outside `[start, end)`, create/reposition rows inside.
4. Like buttons: optimistic toggle via `OptimisticLikeSet`; simulated
   round-trip with `FAIL_RATE = 0.3`; revert the specific op on failure; flash
   success/failure; live stats (DOM rows, window, liked count, scroll).

### Phase 4 — Verification & QA
1. `node --test tests/` green.
2. Static scan: `engine.js` free of `import` / `require`.
3. Headless-browser check of `demo.html`: windowed DOM row count, scroll
   clamping at the end, optimistic like rollback on simulated failure.

## Deliverables

- `engine.js` — `computeVisibleRange`, `OptimisticLikeSet`
- `demo.html` — virtualized feed demo
- `tests/engine.test.js`, `tests/optimistic.test.js`, `tests/index.js`

## Notes / risks

- The half-open `end` is the single most important convention; tests assert it
  with exact values (`{ start: 0, end: 17 }`, etc.).
- `size()` counts distinct liked ids, not total pending operations — matches
  the "liked" badge semantics in `demo.html`.
