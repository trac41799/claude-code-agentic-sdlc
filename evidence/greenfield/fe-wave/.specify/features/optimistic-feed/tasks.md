# Tasks — Infinite Activity Feed (Optimistic Likes)

**Slug:** `optimistic-feed`
**Date:** 2026-08-31
**Spec:** `.specify/features/optimistic-feed/spec.md`

> Wave scopes are derived from these tasks. Disjoint file scopes per wave:
> - **Wave 1 (RED):** Task 1.1 → `tests/visible-range.test.js` · Task 1.2 → `tests/optimistic-like.test.js`
> - **Wave 2 (GREEN):** Task 2.1 → `engine.js`
> - **Wave 3 (demo):** Task 3.1 → `demo.html`

## Phase 1: Test suite (RED)

### Task 1.1: Write failing tests for `computeVisibleRange`
**Description:** Create `tests/visible-range.test.js` covering exact window math at mid/top/bottom scroll, bottom clamping, empty list, and overscan clipping at both boundaries, against the spec contract.
**Acceptance Criteria:**
- [ ] Each case validates AC-1…AC-5 (cite AC in test name/comment)
- [ ] Tests fail with assertion failures (stub `engine.js` exists), not module-load errors
- [ ] Uses Node built-in `node:test` + `assert` only, no deps
**Effort:** S
**Dependencies:** None
**[P] parallel-capable**

### Task 1.2: Write failing tests for `OptimisticLikeSet`
**Description:** Create `tests/optimistic-like.test.js` covering `add`/`contains`/`rollback`/`size`, the interleaving invariant (add A, add B, rollback A → B still present), and no-op rollback of an unadded id.
**Acceptance Criteria:**
- [ ] Each case validates AC-6, AC-7 (cite AC)
- [ ] Tests fail with assertion failures, not module-load errors
- [ ] Uses Node built-in `node:test` + `assert` only, no deps
**Effort:** S
**Dependencies:** None
**[P] parallel-capable**

## Phase 2: Engine (GREEN)

### Task 2.1: Implement `engine.js`
**Description:** Implement `computeVisibleRange` (clamp scrollTop to `[0, max(0, total - viewport)]`; `start = max(0, floor(scrollTop/rowHeight) - overscan)`; `end = min(len, ceil((scrollTop+viewport)/rowHeight) + overscan)`; empty/non-positive → `{0,0}`) and `OptimisticLikeSet` (Set keyed by id; `add`→new size, `contains`→bool, `rollback`→remove exactly id, no-op if absent, `size`→count). Export via CommonJS and browser global `FeedEngine`.
**Acceptance Criteria:**
- [ ] `node --test tests/` fully GREEN (AC-11)
- [ ] Zero imports/requires — AC-8
- [ ] Both runtime exports work (AC-8)
- [ ] Defensive inputs never throw (AC-3/AC-5)
**Effort:** S
**Dependencies:** Task 1.1, Task 1.2

## Phase 3: Demo

### Task 3.1: Build `demo.html`
**Description:** 10,000-item feed; fixed-height scroll container with spacer (`items.length * rowHeight`); only `[start, end)` from `computeVisibleRange` in the DOM, absolutely positioned; like buttons derive state from `OptimisticLikeSet`, flip instantly, and roll back on a simulated 30% failure via `setTimeout`.
**Acceptance Criteria:**
- [ ] Renders all 10,000 items by scroll but keeps DOM window constant (AC-9)
- [ ] Like updates instantly; failed like (30%) rolls back without affecting other rows (AC-10)
- [ ] Loads `engine.js` via plain `<script>` and uses `window.FeedEngine` (AC-8)
**Effort:** M
**Dependencies:** Task 2.1

## Phase 4: QA & wrap-up

### Task 4.1: Run QA triage and write report
**Description:** Verify the greenfield feature against AC-1…AC-11; write `docs/qa/{date}-optimistic-feed-triage.md`.
**Acceptance Criteria:**
- [ ] Triage report documents classification, priority, and route decision
- [ ] No P0/P1 issues outstanding
**Effort:** S
**Dependencies:** Task 2.1, Task 3.1

### Task 4.2: Write wave report
**Description:** Write `.specify/features/optimistic-feed/wave-report.md` with conflicts found / follow-up waves needed.
**Acceptance Criteria:**
- [ ] Wave report present and accurate
**Effort:** S
**Dependencies:** Task 4.1
