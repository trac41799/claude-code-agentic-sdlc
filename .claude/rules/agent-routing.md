# Agent Routing Rules — canonical routing contract

**This file is the single source of truth for agent routing.** It is installed
per-project by `/asdlc-project` (new projects) and `/asdlc-adopt` (existing
repos), and the `AGENT-DELEGATION` block in every project's `CLAUDE.md`
references it. If this file disagrees with any other routing surface, this file
wins.

The rules below govern when and how agents are automatically triggered from
conversation context. Claude Code reads this file alongside `CLAUDE.md` and
routes work to the right agent without requiring an explicit `@agent` call.

---

## The 4 agents and their delegation triggers

| Agent | Delegate when the request involves… |
|---|---|
| **product-manager** | roadmap, vision, epics, daily plan, project-status.html, scope changes, approval triage, stakeholder updates |
| **developer** | writing/changing code, fixing bugs, refactoring, scaffolding pages, API endpoints, Supabase migrations, env-vars wiring, **publishing posts to the live site** |
| **qa** | testing, regression checks, browser matrix, accessibility, QA plans, "verify this works" |
| **devops** | CI/CD, deployments, secret management, infra escalations, Vercel/GitHub workflow issues |

## Delegation rules

1. Pick exactly **one** agent per turn — don't run two in parallel unless the operator explicitly says so.
2. If a request spans agents (e.g., "build it *and* verify it"), call them **in sequence**: developer → qa.
3. If unclear which agent fits, **ask the operator** before assuming.
4. Cross-cutting engineering rules live in `.claude/rules/global-engineering.md` — every agent honors them.
5. Project-level persona overrides for each agent live in `agents/<name>/context/persona.md` — read these on first invocation.
6. Trigger phrases: `@product-manager`, `@developer`, etc. — but auto-route even without the `@` when intent is clear.

---

## Dev Team — Auto-Routing Triggers

The following context patterns automatically invoke the relevant dev team agent.

| Trigger Context | Agent | Skill (if applicable) |
|---|---|---|
| "plan", "spec", "write an epic", "what should we build", "acceptance criteria" | product-manager | — |
| "client interview", "understand the business", "capture what we're building" | product-manager | `pm-client-interview` |
| "constitution", "project principles", "sync the constitution" | product-manager | `pm-constitution-sync` |
| "create issues", "break into tickets", "to issues" | product-manager | `pm-to-issues` |
| "validate plan", "check against epics", "grill with docs" | product-manager | `pm-grill-with-docs` |
| "project status", "update the dashboard", "where are we" | product-manager | `pm-project-status` |
| "build", "implement", "code this", "write the function" | developer | — |
| "debug", "why is this broken", "diagnose", "I can't figure out" | developer | — (agent handles natively) |
| "zoom out", "give me context on this module", "I'm new to this area" | developer | — (agent handles natively) |
| "grill me", "stress-test this plan", "what could go wrong" | developer | — (agent handles natively) |
| "tdd", "test-driven", "red-green-refactor" | developer | `dev-tdd` |
| "plan this feature", "how do we build this", "impl-plan" | developer | `dev-feature-plan` |
| "spike", "prototype", "is this feasible", "hard unknown" | developer | — (agent handles natively) |
| "improve architecture", "refactor this module", "tech debt" | developer | — (agent handles natively) |
| "handoff", "wrapping up", "passing to QA", "done for now" | developer | — (agent handles natively) |
| "plan registry", "pre-push guard", "plan.mjs", "plan enforcement" | developer | `plan-protocol` |
| "triage", "classify this bug", "prioritise this bug" | qa | `qa-triage` |
| "test strategy", "what to test", "test plan", "verify this works" | qa | — (agent handles natively) |
| "ci/cd", "pipeline", "github actions", "deployment setup" | devops | — |
| "is the site up", "deployment failed", "check the logs", "roll back" | devops | `devops-ops` |
| "pre-commit", "husky", "lint-staged" | devops | `devops-setup-pre-commit` |
| "git hooks", "protect main", "guardrails" | devops | `devops-git-guardrails` |

## Publishing — Auto-Routing Triggers

| Trigger Context | Agent | Skill (if applicable) |
|---|---|---|
| "publish", "build the page", "push to site", "update blog index" | developer | `web-publisher-publish` |

---

## Hard Rules

These cannot be overridden by operator instructions:

1. **Developer never starts without an approved PM plan.** If there is no approved plan, route to PM first.
2. **QA never skips triage.** Every bug is classified and scored before being assigned.
3. **DevOps never deploys directly.** All deployments flow through `git push` → CI/CD pipeline.
4. **Publishing never lands on `main` directly.** The Developer owns publishing (`web-publisher-publish`): commit on a `publish/{slug}` branch, open a PR, merge only under the auto-merge criteria in `developer.md`.
5. **No agent merges its own PR — unless the change is trivial and self-contained.** See auto-merge criteria in `developer.md`. For all other changes: Developer opens → QA verifies → operator merges.

---

## Cross-Team Handoff Points

| From | To | Trigger |
|---|---|---|
| PM (approved plan) | Developer | Plan signed off — issues created |
| Developer (feature complete) | QA | Dev handoff doc written |
| QA (bugs found) | Developer | Triage report → P0/P1 bugs |
| QA (all pass) | Developer (publish) | QA sign-off on content changes |

---

## Something not working?

See `docs/guide/troubleshooting.md` for plain-English fixes to the most common
problems (agents not responding, CI failures, production down, guardrails
blocking a command).

---

## Team Routing Skills

The routing table above **is** the full index. Each agent's own definition in
`.claude/agents/` lists the skills it owns; each skill's `SKILL.md` carries its
own trigger phrases. There are no separate team-routing skills.
