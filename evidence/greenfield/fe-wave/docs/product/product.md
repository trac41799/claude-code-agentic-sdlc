# Product — Infinite Activity Feed (Optimistic Likes)

**Slug:** `optimistic-feed`
**Date:** 2026-08-31
**Status:** Approved (brief is frozen — GREENFIELD-2 FE-only)
**Source of truth for planning decisions:** this file and `.specify/features/optimistic-feed/spec.md`.

## One-line idea

> "Infinite activity feed with virtualized rendering and optimistic likes" — a feed where users can like items instantly (optimistic UI) and the list renders only the visible window.

## Problem / opportunity

Long activity feeds (10,000+ items) cannot be rendered as one DOM tree without
jank and memory pressure. At the same time, like buttons that block on a network
round-trip feel unresponsive and lose taps. The product opportunity is a
dependency-free engine that makes both problems disappear:

1. **Virtualized rendering** — only the rows inside the current viewport
   (+ overscan) are ever in the DOM, so rendering cost stays constant no matter
   how large the feed grows.
2. **Optimistic likes** — the like state flips instantly on tap; a failed
   request is rolled back without disturbing any other pending like.

## Target user

FE engineering teams / benchmark reviewer — this is a self-contained, reusable
JS engine + working HTML demo, not a hosted service.

## Scope (MVP)

| Deliverable | What it does |
|---|---|
| `engine.js` | Pure, dependency-free JS: `computeVisibleRange(scrollTop, viewportHeight, items, rowHeight, overscan) → {start, end}` and `OptimisticLikeSet` (`add` / `contains` / `rollback` / `size`). |
| `demo.html` | 10,000-item feed, fixed row height, renders only the visible window + overscan, optimistic like buttons that roll back on a simulated 30% failure. |
| `tests/` | Node built-in test runner (`node --test tests/`), zero deps. |

## Edge cases the engine must handle (from the brief)

- `scrollTop` at the very end → clamp (never an out-of-bounds window).
- Empty `items` list → empty window.
- Overscan clipped at **both** boundaries (start never < 0, end never > `items.length`).
- Multiple add/rollback interleavings: `add A, add B, rollback A` → B still present; `rollback` of an id never added is a no-op.

## Non-goals

- No backend / real network layer (failure is simulated at 30% in the demo).
- No framework, bundler, or package dependencies.
- No persistence of likes across reloads.
- No commit — deliverables stay in the working tree.

## Success criteria

1. `node --test tests/` passes (window math, clamping, empty list, overscan, optimistic-like interleaving).
2. `engine.js` has zero dependencies and runs in both Node (CommonJS) and the browser (global).
3. `demo.html` renders a 10,000-item feed with a constant-size DOM window and instant like/rollback UX.
