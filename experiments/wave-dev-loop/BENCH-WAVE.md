# Wave-arm benchmark — evidence (exp/wave-dev-loop)

Status: COMPLETE (2026-08-31)

Method: `run-wave-bench.py` (wave-only runner) on the fork's bench kit — same
frozen briefs, same model pin (`deepseek/deepseek-chat` via fcc proxy), same
gates and meter as the existing A/B runs. B arms were NOT re-run (the bundle
never touches the bare arm). Session JSONs: `greenfield-wave/out/` and
`greenfield-wave2/out/` in the froam-bench workspace; wave reports inside each
case repo's `.specify/features/{slug}/wave-report.md`.

## Results

| Case | B bare (existing) | A activated (existing) | A+wave (new) | Wave gates |
|---|---|---|---|---|
| BE rate-limited SSE proxy (hard) | 27.4m · $2.84 · 22 tests | 6.5m · $1.08 · 24 tests | **27.7m · 61 turns · FAILED (max_turns)** | 19 passed (work incomplete) |
| E2E crash-safe job pipeline | 11.0m · $1.77 · 13 tests | 7.6m · $1.24 · 17 tests · 58 turns | **18.4m · 26 turns · completed** | 13 passed |
| FE virtualized feed + optimistic rollback | 7.4m · $0.97 · 24 tests | 7.2m · $1.18 · 22 tests · 46 turns | **11.8m · 74 turns · completed** | 16 passed (node --test) |
| DB+ETL 1M rows, idempotent | 4.4m · $0.58 · 8 tests | 5.7m · $1.08 · 6 tests · 55 turns | **9.2m · 57 turns · completed** | 7 passed + perf ✓ (1M rows, rollup 1,000,000) |

Subagents spawned (proxy `subagent_stats.spawned`): be 2 · e2e 2 · fe 4 · db 3 —
the wave loop was genuinely exercised in all four runs, and every run produced
a `wave-report.md` (wave plan, disjoint scopes, post-wave scope + `git status`
checks, suite gates, conflicts found: none in all four).

## What the loop did (evidence, not claims)

- **e2e**: true parallel Wave 1 — Agent A (backend, `app/*.py`) + Agent B
  (frontend, `app/static/index.html`), disjoint scopes, scope checks PASS,
  zero conflicts, one integration fix documented by the coordinator, final
  suite green. **Turns dropped 58 → 26** (−55%).
- **be**: wave plan correctly serialized the dependency chain
  (rate_limit → streams → main) into sequential waves per the v1 dispatch
  table ("tasks share state → sequential agents"); scope checks PASS; but the
  run hit the 60-turn cap before completing — same failure mode as B bare
  (61 turns), though it left 19 passing tests + a full report behind.
- **fe / db**: completed; scope checks PASS; no conflicts.

## Interpretation (VERIFIED grading)

1. **The reintroduction works as designed.** The wave loop executes: plans
   derived from `tasks.md`, disjoint scopes, post-wave verification (R5),
   suite gates per wave (R8), unified reports at the fixed location (R7).
   The R6 failure path was not triggered in any run (all sub-agents returned
   with their contract) — specified, not observed.
2. **In this harness, the wave loop is slower and costlier than the
   single-agent A arm on every case** (wall +42%–326%; cost ×4–8). The cause
   is mechanical: through the headless single-threaded fcc proxy, sub-agent
   dispatch serializes at the API level and re-reads large context
   (`cache_read_input_tokens`: 2.0M–5.8M per run), so "parallel" becomes
   sequential-with-overhead.
3. **Cost is unreliable for these runs**: `costBasis: "unknown"` in the fcc
   client and cache-read tokens charged at full rate inflate the wave arms
   5–8×. Token volumes (tin/tout) are the dependable meter, and even those
   are higher for the wave arms (coordination context). Cost cells are
   reported but MUST NOT be compared to the A/B cells as-is.
4. **Turns are mixed**: e2e −55% (the one genuine win), fe +61%, db +4%, be
   failed at the cap. Fewer turns on e2e did not translate to less wall time —
   sub-agent round trips dominate.
5. **Confound, labeled not hidden**: the wave loop's designed benefit (real
   parallelism on interactive Claude Code, where sub-agents run concurrently)
   cannot materialize in a headless single-threaded proxy. Whether it wins on
   interactive runs is UNMEASURED here — no claim is made either way.

## Verdict

The v1 wave loop is faithfully reintroduced (verbatim design + R4–R8 gap
closures) and functional, with clean removal (`/asdlc-wave-off`, hash-verified
restore to the canonical 17). Its measured value in this bench is **negative**
for wall/cost and mixed for turns — the parallelism advantage it was built for
is not exercisable through the headless proxy. Recommendation: keep as an
experiment; do not promote to the canonical skill set on this evidence.