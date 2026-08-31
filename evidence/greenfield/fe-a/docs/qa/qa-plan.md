# QA Plan — Infinite activity feed

Feature: `infinite-feed` · Spec: `.specify/features/infinite-feed/spec.md`

## Scope

Verify the FE-only deliverable: `engine.js`, `demo.html`, `tests/`.

## Test pyramid

### Unit (Node built-in runner, no deps) — `node --test tests/`

**Window math** (`tests/engine.test.js`):
- Exact windows: `scrollTop = 0` -> `{start: 0, end: 17}`; mid-list
  `4000` -> `{start: 98, end: 117}` and `200000` -> `{start: 4998, end: 5017}`
  with `rowHeight = 40`, `viewportHeight = 600`, `overscan = 2`,
  `items.length = 10000`.
- Bottom clamp: at `maxScroll` and far beyond it (incl.
  `Number.MAX_SAFE_INTEGER`) -> `{start: 9983, end: 10000}`.
- Negative scroll clamps to 0.
- Overscan clipping at both boundaries (`80` -> `{0, 19}`; `120` -> `{1, 20}`;
  `maxScroll - 80` -> `{9981, 10000}`; `maxScroll - 40` -> `{9982, 10000}`).
- `overscan = 0`, empty list -> `{0, 0}`, list shorter than viewport, non-integer
  offsets, `items` must be an array.

**OptimisticLikeSet** (`tests/optimistic.test.js`):
- add/contains/size, distinct ids.
- Interleaving: add A, add B, rollback A -> B remains, A gone, size 1.
- Rollback of never-added id is a no-op, size unchanged, returns `false`.
- Repeated rollbacks never go below zero.
- Rollback of one id never removes an id added after it.
- Re-add after full rollback works.

### Integration (headless browser — CDP)

- `demo.html` loads, renders the initial window only (DOM rows ~11, not 10,000).
- Scrolling to mid/end keeps DOM rows in the single digits/teens and clamps
  `scrollTop` to `maxScroll` at the bottom.
- Like button flips to "♥ Liked" instantly; forced-success keeps it, forced
  failure reverts it to "♡ Like".

### Static checks

- `engine.js` contains no `import` / `require`.
- `demo.html` does not embed 10,000 rows in markup (rows are built at runtime).

## Entry/exit criteria

- **Entry:** `engine.js`, `demo.html`, and `tests/` present per plan
  `.specify/features/infinite-feed/impl-plan.md`.
- **Exit:** acceptance command passes, static checks pass, headless-browser
  checks pass. See `docs/qa/qa-regression-report.md`.
