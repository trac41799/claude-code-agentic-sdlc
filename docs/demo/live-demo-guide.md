# Live demo — "One request → tested, logging API" (≤ 10 minutes)

The framework, installed live, turns one request into a working, tested FastAPI
service with industry-standard structured JSON logging — and the audience sees
every gate fire in the terminal (spec → plan → RED → GREEN → QA).

**Scenario chosen:** greenfield backend service, a trimmed slice of the
benchmark's star case (GREENFIELD-3 · rate-limited SSE proxy). The full task
measured **6.5 min · $1.08 · 24 tests** (framework) vs **27.4 min · $2.84 ·
22 tests · halted at max_turns** (bare) — same model, same brief. The live
slice keeps the shape (SSE stream, broadcast, structured logging, clean
shutdown) minus the token bucket, so it finishes comfortably on stage.

## Why not the other options (assessed)

| Option | Rejected because |
|---|---|
| Local E2E FE-BE-DB | Four runtimes + DB + auth to stand up; setup alone blows the 10-minute budget; one broken part kills the demo |
| Froam playground + `gh` PR + Vercel preview | Vercel preview builds take 3–5+ min (unpredictable), branch choreography on a live product adds moving parts, and it demonstrates GitHub/Vercel *ops* — not the framework's planning/TDD value |

Greenfield BE: one process, zero accounts, offline-safe, and it **is** the
benchmark star — the numbers on the results slide come from this exact shape.

## Where the devops lane is (and why it's not in this demo)

The devops agent owns **CI/CD, Vercel operations, pre-commit checks, and git
guardrails** (`devops-cicd` · `devops-ops` · `devops-setup-pre-commit` ·
`devops-git-guardrails`). Its lanes fire **only against live targets** — CI runs
when a PR is pushed; `vercel ls`/`logs` need a real deployment. This demo is
offline-safe by design, so devops's work shows up as:

- the branch-protection + `ci.yml` conversation after the PR is opened (ask the
  team: "add CI like devops-cicd" and it writes the workflow, secrets list, and
  branch-protection steps),
- on a real project: preview deploys per PR, the <60-second rollback procedure,
  and the guardrails that block `push --force` / `add .` / `reset --hard`.

The benchmarks measured the same offline lanes — devops was never exercised in
the lab either; its claims are VERIFIED on live client projects, not in the
bench.

## Before the talk (prep, ~20 min once)

- [ ] `claude` CLI installed and authenticated (`claude doctor` passes)
- [ ] `gh auth status` logged in · `python --version` ≥ 3.10 · `pip` available
- [ ] Framework NOT yet installed on this machine (or plan to show `update`)
- [ ] Day before: run the full GREENFIELD-3 task with the framework into
      `~/asdlc-demo-fallback` (commands in [bench/README.md](../../bench/README.md))
      — the safety net if the live run stalls
- [ ] Pre-record the fallback run's session log (`claude -p ... --output-format json`)
      — paste-able proof if the network dies
- [ ] Two extra terminal windows open: one for the server, one for curl
- [ ] Model: **Sonnet** (speed). Do not use the slowest model; the bench pins
      matter, the demo does not.

## The script

### 0:00–1:30 — Install (fresh terminal)

```bash
claude plugin marketplace add trac41799/claude-code-agentic-sdlc
claude plugin install agentic-sdlc@agentic-sdlc
```

Narrate: *"Two commands. Nothing installs globally — no hooks, no telemetry,
no writes outside the project you scaffold. This is the whole setup."*

### 1:30–2:30 — Create the demo project + adopt

```bash
mkdir asdlc-demo && cd asdlc-demo
git init && echo "# demo" > README.md
git add -A && git commit -qm init
claude
```

In Claude Code, run: `/asdlc-adopt` — confirm the repo. It installs the
4-agent team + 18 skills into this project's `.claude/`, injects the
delegation block, touches nothing else, commits nothing. Then run
`/asdlc-doctor` — all checks pass.

### 2:30–8:00 — One request → the team builds it

Paste this verbatim:

```
Build a small FastAPI service:
- GET /health returns {"status": "ok"}
- GET /streams/{id}/events is an SSE stream: a data event with a
  monotonic counter every 2s, and an SSE comment heartbeat every 10s
- POST /streams/{id}/events accepts {"msg": "..."} and broadcasts it
  to the stream's subscribers
- every HTTP request logs one structured JSON line to stdout
  (timestamp, level, method, path, status, duration_ms, request_id)
- on app shutdown all streams close cleanly, no exceptions
Tests (pytest): health returns 200 · broadcast reaches a subscriber ·
heartbeat arrives during silence · clean shutdown.
Acceptance: pytest tests/ -q passes.

Keep the ceremony tight — one feature, short spec, no epics. This is a demo.
```

Narrate the gates as they fire: spec capture → plan (you approve) → RED test
→ minimal implementation → GREEN → QA pass. *"Watch the terminal: the plan
arrives before the code, and the test fails before it passes."*

### 8:00–9:30 — Prove it (two extra windows)

```bash
pytest tests/ -q              # window 1: all green
uvicorn app.main:app --port 8000   # window 2: structured JSON logs stream by
```

```bash
curl localhost:8000/health
curl -N localhost:8000/streams/1/events     # counter events + : heartbeat
curl -X POST localhost:8000/streams/1/events -d '{"msg":"hello"}'
curl localhost:8000/health                  # again: watch request_id + duration_ms
```

Then Ctrl+C in the server window: clean shutdown, no exceptions.
*"Request → test → running service with request IDs and durations per line —
in six minutes, from a terminal that had nothing on it."*

### 9:30–10:00 — Close with the numbers

Show the artifacts the team left behind:

```
docs/product/product.md
.specify/features/live-demo/{spec,impl-plan,tasks}.md
app/main.py · tests/ · docs/qa/
```

Then the measured comparison (same model, same brief, full task):

```
metric         A activated      B bare
wall (min)           6.5         27.4
turns                 56           61
cost                1.08          2.84
gate        24 passed     22 passed · halted (max_turns)
```

*"The only difference was the team. One command reruns this on any repo —
the bench kit ships in the same repository as the framework."*

## Timebox busters

| If… | Do |
|---|---|
| Agent drifts past 7:00 | Interject: "keep it minimal — this is a demo"; if still behind at 7:30, switch to `~/asdlc-demo-fallback` (pre-built) and jump to Prove-it |
| `/asdlc-doctor` fails | Read the one failing line, fix it, rerun — prep checklist should have caught it |
| SSE curl prints nothing | `curl -N` forces streaming; check the server window's logs |
| Model feels slow | Switch to the fastest model in the session |
| Network dies mid-run | Show the pre-recorded session log from the fallback run, then Prove-it on the fallback folder |

Windows notes: PowerShell throughout; use `curl.exe` (not the alias); run
uvicorn in a second terminal window; `python -m venv .venv` first if you want
an isolated env — the team will handle it if you put it in the request.

## After the talk

1. `claude plugin update agentic-sdlc@agentic-sdlc` if a release landed.
2. Offer the bench kit repro on their own repo:
   `python bench/brownfield.py --repo <their-repo> --task bench/tasks/brownfield-add-tests.md --gate "pytest tests/ -q"`
   (one command, A/B, non-merge scratch clone).