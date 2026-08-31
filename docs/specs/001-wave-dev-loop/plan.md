# Plan — wave-dev-loop

## Chosen approach

Ship the wave loop as an **opt-in project-scoped bundle** under
`experiments/wave-dev-loop/` with two toggle skills (`/asdlc-wave-on`,
`/asdlc-wave-off`) that run deterministic shell scripts. The skill content is
the v1 `dev-multi-agent` verbatim, plus five marked gap-closing sections
(R4–R8). Bench support: `benchkit.install_framework(..., wave=True)` +
`bench/greenfield.py --wave`, which install the bundle and extend the
activation prompt with a wave-dispatch instruction.

**Rejected alternatives:** (a) plugin skill (`plugin/skills/`) — touches the
canonical 4-command plugin and bumps versions, violating non-goals; (b) adding
the skill to `.claude/skills/` — would make every `/asdlc-adopt` reinstall it
and silently change the canonical 17, breaking the "clean removal" guarantee;
(c) rewriting/wiring into `developer.md` — removal would require patching an
agent file back, and v1 never wired it that way.

## Architecture delta

- New dir `experiments/wave-dev-loop/` (README, `SKILL.dev-multi-agent.md`,
  `skills/asdlc-wave-on|off/SKILL.md`, `scripts/wave-install.sh|wave-remove.sh`,
  `tests/test_wave.py`, `BENCH-WAVE.md` template).
- `bench/benchkit.py`: `install_framework(repo, fw, wave=False)` copies the
  bundle's 3 skills when `wave=True`; `run_arm` gains a wave hint in the
  activation text (new `wave_activation` flag).
- `bench/greenfield.py`: new `--wave` flag → passes to `fresh_repo` +
  activation.
- No changes to `plugin/`, `.claude-plugin/`, `.claude/skills/`,
  `.claude/agents/`, `VERSION`, or `main`.

## Public deltas

- Slash commands added per project: `/asdlc-wave-on`, `/asdlc-wave-off`
  (project-scoped; not shipped by the plugin).
- Env/flag: `BENCH_WAVE=1` or `--wave` on the greenfield runner.

## Risks & mitigations

- **Proxy/credits during 4 bench runs (~35–45 min)** → verify fcc server +
  model pin with a 1-turn probe before starting; run arms sequentially; a
  failed arm is recorded, not faked (E3).
- **Wave instability on a hard case (be-sse)** → the skill's failure path
  (R6) governs; if the arm degrades vs A, that is the honest result — the
  evidence doc reports it either way.
- **Drift risk: reintroduced skill diverges from v1** → R3 content test
  asserts verbatim sections (diff against the `66dc6a2` source).
- **Removal leaves residue** → R2 script test runs on a staged project;
  artifact sweep is deterministic (fixed paths).

## Milestones

1. **M1 — Bundle + toggle (R1–R8)**: scripts, skills, content tests, frontmatter
   and no-global-install gates. Leaves suite green.
2. **M2 — Harness (R9)**: benchkit/greenfield wave integration + unit tests.
3. **M3 — Bench (R10)**: 4 A+wave runs, gates, evidence doc.
4. **M4 — Ship**: commit `exp/wave-dev-loop`, push; main untouched.

## ADRs

- ADR-0001: wave bundle location (experiments dir vs plugin vs canonical
  skills) — `docs/adr/0001-wave-bundle-location.md`.