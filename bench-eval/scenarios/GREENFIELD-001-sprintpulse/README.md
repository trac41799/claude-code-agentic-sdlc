# Scenario GREENFIELD-001 — "SprintPulse" (designed evaluation scenario)

> **Rule (mandatory for every benchmark from 2026-09-06):** design the test/eval
> scenario — product requirements, acceptance criteria, task breakdown, and the
> **expected deliverables** — **before** making any eval runs, greenfield or
> brownfield. Scenarios must be humanly comprehensive yet complex enough to
> prove worth and edge out differences between frameworks. After a run, the
> deliverable product (codebase, documentation, task tracking, test suites,
> test results) must be captured, accessible, and packaged alongside the eval
> results as proof. See `docs/guide/EVAL-GUIDE.md` §"Scenario design rule".

## Why this scenario

SprintPulse is a deliberately mid-size product slice: one small web service with
a real schema, data-integrity subtlety (timezones), a UI, migrations, tests, and
documentation — sized so a competent human completes it in roughly 2–4 hours and
an agent in a bounded session (≤ 600–1800s per the harness cap).

It differentiates frameworks on the axes that matter:

| Axis | What separates frameworks here |
|---|---|
| **Correctness under subtlety** | The sprint-aggregation spec has a timezone trap; frameworks that rush structure over semantics fail the integration tests |
| **Evidence discipline** | Deliverables (docs/product, task tracking, tests, CI, results) are part of the *oracle*, not optional — bare agents that "just code" fail the gate |
| **Ceremony cost** | Multi-file vertical slices show whether plan/spec/QA steps pay for themselves or purely tax wall time |
| **Traceability** | Task tracking must link to the actual change set — verifiable from the captured artifact |

## Deliverables (the evidence contract — all required)

| # | Deliverable | Path (in the product repo) | Gate |
|---|---|---|---|
| D1 | Product codebase (buildable, tested) | `app/`, `migrations/` | `python -m build`-equivalent compiles; app imports |
| D2 | Product documentation | `README.md` (run instructions), `docs/product/product.md` (purpose & scope) | files exist, non-empty |
| D3 | Task tracking | `docs/plans/tasks.md` (or equivalent) listing the tasks actually done | exists; references implemented features |
| D4 | Test suites | `tests/` unit + integration | `pytest tests/ -q` green (all tests) |
| D5 | Test results artifact | `docs/qa/test-results.txt` (or `test-results.md`) with a dated pass summary | exists; contains pass counts |
| D6 | CI configuration | `.github/workflows/ci.yml` (or equivalent) | exists; references the test command |

The oracle (`oracle.sh`) enforces D1–D6 mechanically, then reports which
deliverables each framework produced — so the eval result *is* the comparison of
evidence, not just of test pass/fail.

## Files

- `brief.md` — the product brief handed to the agent (the only input)
- `oracle.sh` — the automated acceptance gate (build + tests + deliverable checks)
- `item.json` — the aisdlc-eval corpus item wrapping brief + oracle
