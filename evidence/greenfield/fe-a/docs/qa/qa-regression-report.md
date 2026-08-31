# QA Regression Report — Infinite activity feed

Date: 2026-08-29 · Feature: `infinite-feed` · Plan: `docs/qa/qa-plan.md`

## Result: PASS

## 1. Acceptance command

```
$ node --test tests/
```

**22/22 passed, exit 0.**

| Suite | Tests | Result |
|-------|-------|--------|
| `tests/engine.test.js` | 12 | ✅ pass |
| `tests/optimistic.test.js` | 10 | ✅ pass |

## 2. Static checks

- `engine.js` dependency-free: no `import` / `require` (verified by scan).
- `demo.html` builds rows at runtime; no 10,000-row markup (DOM row count at
  load was 11 in a real browser).

## 3. Headless-browser checks (Edge, CDP)

Loaded `demo.html` in headless Edge and drove scroll + click:

| Check | Expected | Observed | Result |
|-------|----------|----------|--------|
| Initial DOM rows | << 10,000 | 11 | ✅ |
| Window at top | "0 – N of 10000" | "0 – 11 of 10000" | ✅ |
| Mid scroll (`scrollTop = 200000`) | small row count, valid window | 14 rows, "4997 – 5011 of 10000" | ✅ |
| End scroll (`1e9`) | clamp to maxScroll | `scrollTop = maxScroll`, "9989 – 10000 of 10000" | ✅ |
| Beyond-end (`Number.MAX_SAFE_INTEGER`) | same clamp | same window | ✅ |
| Like (forced success) | optimistic then stays | "♡ Like" -> "♥ Liked" -> "♥ Liked" | ✅ |
| Like (forced failure) | optimistic then reverts | "♥ Liked" -> "♡ Like" | ✅ |

## 4. Findings

No open defects. One issue found during testing — newly rendered rows showed an
empty like-button label until clicked — was fixed in `demo.html` by syncing
button state for fresh and recycled rows alike, then re-verified.

## Sign-off

QA: PASS. Ready for delivery as FE-only.
