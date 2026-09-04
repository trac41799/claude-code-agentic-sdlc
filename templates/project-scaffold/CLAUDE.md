# {Project Name} — Project Instructions

This file is the entry point Claude Code reads when this repo is opened. It defines roles, folder conventions, and publishing/engineering workflows.

## Stack
- Website: Next.js + Tailwind + shadcn (`website/`)
- Database: Supabase (`website/supabase/`)
- Deployment: Vercel (auto-deploys when a PR merges to `main` — nobody pushes to `main` directly)

<!-- BEGIN: AGENT-DELEGATION (managed by agentic-sdlc skills — do not delete this block) -->
## Agent delegation (auto-routing)

When you receive a request, **delegate to the right specialist agent** before doing the work yourself:

| Agent | Delegate when the request involves… |
|---|---|
| **product-manager** | roadmap, vision, epics, daily plan, project-status.html, scope changes, approval triage, stakeholder updates |
| **developer** | writing/changing code, fixing bugs, refactoring, scaffolding pages, API endpoints, Supabase migrations, env-vars wiring, **publishing posts to the live site** |
| **qa** | testing, regression checks, browser matrix, accessibility, QA plans, "verify this works" |
| **devops** | CI/CD, deployments, secret management, infra escalations, Vercel/GitHub workflow issues |

**Delegation rules, the full trigger map, and the hard rules live in `.claude/rules/agent-routing.md` — that file is canonical and every agent honors it.** In short: pick exactly one agent per turn (sequence if a request spans agents), ask the operator when unclear, and read `agents/<name>/context/persona.md` on first invocation. Trigger phrases: `@product-manager`, `@developer`, etc. — but auto-route even without the `@` when intent is clear.
<!-- END: AGENT-DELEGATION -->

## Folder conventions
See `FOLDER-STRUCTURE.md` at the project root for the canonical structure every project follows. Agents MUST honor it — do not invent new top-level folders.

## Publishing workflow
Read source content from `content/topics/<slug>/` → optimize images → the developer runs `web-publisher-publish` (writes the App Router page under `website/app/blog/`, updates the blog index, commits on a `publish/{slug}` branch, opens a PR, verifies the Vercel build).

