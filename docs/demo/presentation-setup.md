# Presentation & demo — fresh-machine setup guide

Everything to present and demo from a brand-new computer, in order. No prior
install needed. Testing this flow on the actual presentation laptop (from a
clean state or a new VM) is itself the best rehearsal.

## Materials check — you have (verified 2026-08-31)

| Material | Where | Status |
|---|---|---|
| Full deck (20 slides) | `docs/slides/Agentic-SDLC-Tech-Audience.pptx` | ✓ validated (20 pages) |
| Condensed deck (9 slides) | `docs/slides/Agentic-SDLC-Tech-Audience-COMPACT.pptx` | ✓ validated (9 pages) — recommended for the talk |
| Cycle diagram | `docs/slides/sdlc-cycle.png` (embedded in decks) | ✓ |
| Flow diagram | `docs/slides/workflow-diagram.png` (embedded in decks) | ✓ |
| Flow walkthrough + Q&A | `docs/demo/flow-walkthrough.md` | ✓ (14 audience questions) |
| Live demo script | `docs/demo/live-demo-guide.md` | ✓ (≤10 min scenario) |
| Raw evidence bundle | `evidence/` (12 projects + sessions + trees) | ✓ — `python evidence/validate.py` → **12/12 claims reproduce** |
| Gap analysis | `docs/slides/GAP-ANALYSIS.md` | ✓ |
| Plugin | `plugin/` v2.9.0, marketplace tag `v2.9.0` | ✓ |
| Bench kit | `bench/` (brownfield + greenfield runners) | ✓ |
| Client setup (non-technical) | `docs/guide/CLIENT-SETUP.md` | ✓ |

Reproduce the evidence on demand (also a great demo moment):
```bash
git -C <repo> diff --quiet; python evidence/validate.py   # → ALL CLAIMS REPRODUCE
```

## Part 1 — Machine prerequisites (run in Terminal)

```bash
# 1. git + Node + Python (versions only — install from git-scm.com, nodejs.org, python.org if absent)
git --version          # ≥ 2.30
node --version         # ≥ 20  (for npm CLI installs + plan-protocol engine)
python --version       # ≥ 3.10 (for validate.py + the demo server)

# 2. GitHub CLI (installer: cli.github.com on Windows, brew install gh on macOS)
gh --version && gh auth login     # browser: GitHub.com, HTTPS, Authorize

# 3. Claude Code (desktop app from claude.ai/download, or npm i -g @anthropic-ai/claude-code)
claude doctor          # confirms auth + tools

# 4. Presentation tooling
npm i -g vercel supabase          # optional; only if the devops/CLI story is shown live
```

## Part 2 — Install the framework (2 commands + check)

```bash
claude plugin marketplace add trac41799/claude-code-agentic-sdlc
claude plugin install agentic-sdlc@agentic-sdlc
```
Then in Claude Code (in any folder): `/asdlc-doctor` — all checks pass.
Optional machine tooling (installs only what's missing, status-first):
`/asdlc-tools` (adds `gh`/Vercel/Supabase CLIs + Supabase MCP config).

## Part 3 — Get the materials onto this machine

```bash
git clone https://github.com/trac41799/claude-code-agentic-sdlc
cd claude-code-agentic-sdlc
python evidence/validate.py        # reproduce the bench (needs pytest: pip install pytest)
```

## Part 4 — Presentation day checklist (10 min before)

- [ ] Both decks open in PowerPoint **on this machine** (or exported PDFs): the
      condensed deck for the talk, the 20-slide deck as backup appendices.
- [ ] `claude plugin update agentic-sdlc@agentic-sdlc` → confirms you're on
      `2.9.0` (show the version in case someone asks).
- [ ] Terminal windows staged: (1) repo folder (evidence path),
      (2) demo server pane (uvicorn, from the demo project), (3) curl pane.
- [ ] Demo folder prepared (see `docs/demo/live-demo-guide.md` — the
      `asdlc-demo` live scenario) **or** the fallback: a warmed `greenfield/be-a`
      project already on disk so the "gate greens" moment is instant.
- [ ] Validate.py output visible (or re-run it live — it's ~60 s and lands hard).
- [ ] Screen share settings: 16:9, nothing else open, version check first.

## Part 5 — Day-of demo script (≤ 10 min)

Follow `docs/demo/live-demo-guide.md` exactly:
1. 0:00–1:30 — install the plugin (2 commands + `/asdlc-doctor`).
2. 1:30–2:30 — `mkdir asdlc-demo && git init` → `/asdlc-adopt` → team installed.
3. 2:30–8:00 — paste the guide's one feature request → gates fire live
   (spec → plan → RED → GREEN → QA).
4. 8:00–9:30 — `pytest` green + uvicorn + curl + clean Ctrl+C shutdown.
5. 9:30–10:00 — show artifacts tree + the bench comparison (27.4 m → 6.5 m)
   + one command repro (`python evidence/validate.py`).

## Gold rules for the machine

- Do NOT demo from the official ex-company repo — tinker/bench on the fork only
  (fork-first is slide 2; it is also your safety: nothing gets committed to
  the official repo).
- Never commit `~$*.pptx` lock files or `__pycache__`.
- If the Wi-Fi dies mid-demo: the pre-warmed `greenfield/be-a` project runs
  fully offline (pytest + uvicorn are local). Have it ready before starting.