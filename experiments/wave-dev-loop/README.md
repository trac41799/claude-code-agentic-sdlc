# Wave dev loop — experiment bundle (exp/wave-dev-loop)

Surgical reintroduction of the v1 `dev-multi-agent` skill (wave-based parallel
implementation loop) into the V2 framework — **on the fork, exp branch only,
never main**. Verbatim v1 design plus five marked gap-closings
(`[V2-REINTRO R4–R8]`) — no novel features.

## What it adds

| Skill | Role |
|---|---|
| `dev-multi-agent` | The v1 wave loop: sequential waves of concurrent, independent sub-agents; disjoint file scopes; post-wave conflict checks; unified wave report |
| `asdlc-wave-on` | Installs the three skills into a project's `.claude/skills/` (17 → 20) |
| `asdlc-wave-off` | Removes them + all `wave-report.md` artifacts; restores the canonical 17 — idempotent |

## Gaps closed (only immature assumptions)

- **R4** wave plan derived from `tasks.md`, disjoint scopes, operator approval
  before Wave 1 (v1 never said where tasks came from).
- **R5** post-wave verification defined: reported files ⊆ scope, `git status`
  cross-check, out-of-scope changes reverted/re-queued (v1 said "check for
  conflicts" — no procedure).
- **R6** failure path: failed/missing sub-agent returns are re-run sequentially
  or aborted with a written reason (v1 was silent).
- **R7** unified summary location: `.specify/features/{slug}/wave-report.md`.
- **R8** test suite runs after every wave; red blocks the next wave.

## Toggle

```bash
# in the target project, via Claude Code
/asdlc-wave-on     # install (needs the fork repo on disk, or clones it)
/asdlc-wave-off    # remove — recovers the original 17-skill state
```

## Bench

`bench/greenfield.py --wave` installs the bundle on the A arm and appends the
wave-dispatch instruction to the activation prompt. Evidence:
`BENCH-WAVE.md` in this directory; session JSONs under the run's `--out`.

## Invariants

- Canonical `.claude/skills/` (17) and `plugin/` (4 commands) are untouched.
- No writes into `~/.claude/` anywhere in this bundle (CI grep enforced).
- Removing the bundle restores byte-identical canonical skills (hash-verified
  in `tests/test_wave.py`).