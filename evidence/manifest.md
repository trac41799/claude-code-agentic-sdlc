# Evidence manifest — benchmark claims & folder-structure evidence

Every claim on the deck's results slide (and in `docs/benchmarks/BENCHMARK-SUMMARY.md`)
can be checked against the raw artifacts in this directory. Structure:

```
evidence/
├── README.md                 ← what this is, how to use
├── manifest.md               ← this file: claim → evidence → validation
├── validate.py               ← reruns every acceptance gate, emits validation-report.md
├── validation-report.md      ← generated: 12/12 claims reproduce
├── tree/
│   ├── install-payload.txt   ← the framework files /asdlc-adopt installs (per-project)
│   ├── scaffold-canonical.txt← the /asdlc-project canonical scaffold layout
│   ├── greenfield-be-a.txt   ← full project tree (A arm: .claude/.specify/process artifacts)
│   └── greenfield-be-b.txt   ← full project tree (B arm: bare — no .claude, no .specify)
├── sessions/                 ← raw provider session JSONs (12) — metered, unmodified
└── greenfield/               ← 12 intact project folders (source, tests, process artifacts)
    ├── be-a/ be-b/ be-wave/  ← rate-limited SSE proxy (hard case)
    ├── e2e-a/ e2e-b/ e2e-wave/ ← crash-safe job pipeline
    ├── fe-a/ fe-b/ fe-wave/  ← virtualized feed + optimistic rollback
    └── db-a/ db-b/ db-wave/  ← 1M-row ETL
```

## Folder structure evidence

| Claim | Evidence | How to validate |
|---|---|---|
| `/asdlc-adopt` installs a per-project team, nothing global | `tree/install-payload.txt` (`.claude/agents` 4 · `.claude/skills` 17 · `.claude/rules` · `CLAUDE.md` delegation block) | Diff against the repo's own `.claude/`: same files (benchkit.install_framework replicates the adopt payload 1:1). Anything in `~/.claude/` is untouched by design. |
| A-arm runs carry process artifacts; bare arms do not | `tree/greenfield-be-a.txt` (`.specify/features/…` spec/plan/tasks + `docs/`) vs `tree/greenfield-be-b.txt` (app+tests only) | Read both trees side by side. |
| `/asdlc-project` scaffold layout | `tree/scaffold-canonical.txt` (`templates/project-scaffold/` — the copied content) | Compare to `templates/FOLDER-STRUCTURE.md`. |
| Wave-loop runs write `wave-report.md` | `greenfield/{be,e2e,fe,db}-wave/wave-report.md` | Read the report; artifacts remain in the project. |

## Benchmark evidence (claims → where)

| Claim (summary) | Project folder | Session JSON | Gate log | Validation |
|---|---|---|---|---|
| BE: A 24 tests / B 22 / W 19 (A 6.5m·$1.08 — B 27.4m·$2.84) | `greenfield/be-{a,b,wave}` | `sessions/be-{a,b,wave-a}.json` | `greenfield/be-*/gate.txt` | `validate.py` (row `be`) |
| E2E: A 17 / B 13 / W 13 | `greenfield/e2e-{a,b,wave}` | `sessions/e2e-*` | `greenfield/e2e-*/gate.txt` | `validate.py` (row `e2e`) |
| FE: A 22 / B 24 / W 16 | `greenfield/fe-{a,b,wave}` | `sessions/fe-*` | `greenfield/fe-*/gate.txt` | `validate.py` (row `fe`) |
| DB: A 6 / B 8 / W 7 (+ perf ✓) | `greenfield/db-{a,b,wave}` | `sessions/db-*` | `greenfield/db-*/gate.txt` | `validate.py` (row `db`) |

## How to validate yourself (3 steps)

```bash
# 1. (optional) review the trees
git clone https://github.com/trac41799/claude-code-agentic-sdlc
open evidence/tree/*.txt

# 2. rerun the acceptance gates — reproduces every test count from the claims
python evidence/validate.py      # needs: python+pytest, node

# 3. read the generated report
cat evidence/validation-report.md
```

## Notes on honesty

- Session JSONs are raw provider client output (fcc) — unmodified byte-for-byte;
  token counts and estimated cost fields included. Costs carry the client's
  `costBasis: "unknown"` caveat documented in `docs/slides/GAP-ANALYSIS.md` (G1):
  treat dollar cells as approximate, test counts as exact.
- Project folders: `.pytest_cache` stripped; `.claude/skills` from the run installs
  remain (they are the adopt payload evidence). Nothing else altered.
- Bench arms ran with one model pin (deepseek-chat via fcc proxy); the A+wave
  evidence (negative wall/cost, honest) sits in `experiments/wave-dev-loop/BENCH-WAVE.md`
  on the `exp/wave-dev-loop` branch.