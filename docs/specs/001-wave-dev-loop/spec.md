# Spec — wave-dev-loop (reintroduce the v1 multi-agent wave loop)

Slug: `wave-dev-loop` · Branch: `exp/wave-dev-loop` · Status: DRAFT

## Goal

Surgically reintroduce the v1 `dev-multi-agent` skill (wave-based parallel
implementation loop) into the V2 framework **on the fork, behind an exp
branch**, closing only the immature assumptions of the original — no novel
improvements. Provide a one-command removal (`/asdlc-wave-off`) that restores
the current 17-skill canonical state. Rerun the 4 frozen greenfield benchmarks
with the wave arm (A+wave) against the existing A/B numbers.

## Non-goals

- No plugin / marketplace changes (`plugin/`, `.claude-plugin/`, `VERSION` stay
  untouched; the 4 commands stay 4).
- No changes to canonical `.claude/skills/` (17 skills) or `.claude/agents/`
  (4 agents). The wave loop is **not** wired into `developer.md`.
- No novel design: no scheduler, no token budgets, no auto-parallel heuristics
  beyond v1's dispatch table, no telemetry, no hooks.
- No commit to `main`. Everything lands on `exp/wave-dev-loop`.

## Actors

- **Operator** — runs `/asdlc-wave-on` (install), `/asdlc-wave-off` (remove),
  approves wave plans; reviews benchmark evidence.
- **Developer agent** — executes the wave loop as coordinator.
- **Bench harness** (`bench/`) — installs the bundle with `--wave` and meters
  the A+wave arms.

## Requirements (EARS)

- R1 · WHEN the operator runs `/asdlc-wave-on` in a project THEN the project's
  `.claude/skills/` SHALL gain exactly `dev-multi-agent`, `asdlc-wave-on`,
  `asdlc-wave-off`, and no canonical skill file SHALL be modified.
  *AC: install script test — 17 → 20 skills, canonical hashes unchanged.*
- R2 · WHEN the operator runs `/asdlc-wave-off` THEN the three wave skills and
  every `wave-report.md` artifact SHALL be removed and the skill count SHALL
  return to its pre-install baseline. *AC: remove script test — 20 → 17, no
  wave files remain, idempotent on second run.*
- R3 · The reintroduced `dev-multi-agent` SHALL preserve the v1 wave execution
  model, dispatch table, sub-agent prompt template, coordinator
  responsibilities, and integration check verbatim. *AC: content test — required
  v1 sections present and unmodified.*
- R4 · WHEN the coordinator proposes a wave plan THEN it SHALL derive task
  groups from `tasks.md`, assign disjoint file scopes, and present the plan to
  the operator before Wave 1. *AC: skill content test — R4 section present.*
- R5 · AFTER each wave completes THEN the coordinator SHALL verify every
  agent's reported files against its declared scope and check `git status`
  for out-of-scope changes; violations SHALL be reverted or re-queued before
  the next wave. *AC: skill content test — R5 procedure present.*
- R6 · IF a sub-agent fails or returns without its contract THEN the
  coordinator SHALL re-run that item sequentially in a later wave or abort
  with a written reason; it SHALL NOT proceed silently. *AC: skill content
  test — R6 failure path present.*
- R7 · WHEN all waves complete THEN a unified summary SHALL be written to
  `.specify/features/{slug}/wave-report.md` (conflicts found / follow-up
  waves). *AC: skill content test — R7 path present; remove script deletes it.*
- R8 · AFTER each wave THEN the project test suite SHALL be run; IF red THEN
  fixes SHALL happen before the next wave starts. *AC: skill content test —
  R8 gate present.*
- R9 · WHEN the bench harness runs with `--wave` THEN `install_framework`
  SHALL also install the wave bundle and the activation prompt SHALL instruct
  wave dispatch for independent tasks. *AC: benchkit unit tests.*
- R10 · The A+wave benchmark SHALL use the same frozen briefs, model pin
  (deepseek-chat via fcc proxy), gates, and meter as the existing A/B runs;
  only the new arms execute. *AC: greenfield.py --wave runs all 4 cases with
  session JSONs + gate output recorded.*

## Edge cases

- E1 · `/asdlc-wave-off` on a project that never installed the wave bundle →
  no-op success (count already 17). Covered by R2 (idempotent).
- E2 · Wave bundle partially installed (e.g., manual deletion) → `wave-off`
  removes whatever remains and reports what was found.
- E3 · Bench arm fails (proxy error, model failure) → session JSON records
  `is_error`; the run is reported as failed, never silently dropped.
- E4 · A wave with zero independent tasks → coordinator runs one sequential
  wave (single agent), documented in the report.

## Out of scope (dated 2026-08-31)

- Porting the loop into the canonical skill set or plugin; operator
  auto-approval of wave plans; cross-repo wave execution; parallel QA lanes.

## Assumptions (decisions recorded from clarify)

- Bench scope: all 4 frozen greenfield cases (be, fe, db, e2e), arm A+wave,
  compared against the existing A/B numbers (same pin, same briefs — no
  re-runs of old arms).
- Experiment lives on `exp/wave-dev-loop` and IS pushed to origin (fork only;
  `main` untouched).
- The wave bundle ships under `experiments/wave-dev-loop/` — outside
  `.claude/skills/` — so canonical structure is structurally guaranteed.
- Gap list G1–G5 (R4–R8) is the complete set of closed immature assumptions;
  nothing else changes.