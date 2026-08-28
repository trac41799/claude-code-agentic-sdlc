# Agentic SDLC (v2)

The Agentic SDLC system in one repo: a bare-minimum Claude Code plugin, the
4 agent definitions, their workflow skills, and the canonical project scaffold.

**v2 principle: nothing installs globally.** The plugin ships 4 skills — no
hooks, no telemetry, no background behavior; agents and workflow skills are
installed **into each client project** by `/asdlc-project`. (Edge8-internal
telemetry and the v1 cleanup live in the separate private `agentic-sdlc-telemetry`
plugin.)

## Install

Add this repo as a plugin marketplace in Claude Code and install
`agentic-sdlc`:

```bash
claude plugin marketplace add trac41799/claude-code-agentic-sdlc
claude plugin install agentic-sdlc@agentic-sdlc
```

Then run `/asdlc-doctor` once. It checks the prerequisites (`git`, an authenticated
`gh`, `perl`, `node`/`npm`/`npx`, `rsync`), and tells you if your installed plugin
is behind the latest release — worth doing before a workshop, since `/asdlc-project`'s
own steps ship inside the plugin.

To update later:

```bash
claude plugin update agentic-sdlc@agentic-sdlc
```

## What the plugin contains

| Piece | What it does |
|---|---|
| `/asdlc-project` | Scaffolds a new client project from `templates/project-scaffold/`, installs the 4 agents + skills **into the project's `.claude/`**, seeds `docs/product/` and `docs/brand/`, initializes git |
| `/asdlc-adopt` | Installs the same 4 agents + skills + rules into an **already-established repo** — injects the delegation block into its `CLAUDE.md`, seeds only missing doc anchors, touches nothing the operator wrote, commits nothing |
| `/asdlc-doctor` | Setup check: prerequisites, repo context, scaffolded-project layout |
| `/asdlc-memory-cleanup` | Human-in-the-loop cleanup of a multi-account memory mess: reads every memory file, narrates duplicates/conflicts/stale facts, then deletes/merges/re-indexes only what the operator approves — after a backup |

## Repo structure

```
.claude-plugin/            ← marketplace manifest (this repo IS the marketplace)
plugin/                    ← the shipped plugin payload
├── .claude-plugin/        ← plugin manifest
└── skills/                ← asdlc-project, asdlc-adopt, asdlc-doctor, asdlc-memory-cleanup
.claude/
├── agents/                ← 4 agent definitions (per-project install source)
├── skills/                ← agent workflow skills (per-project install source)
└── rules/                 ← engineering guardrails
templates/project-scaffold/ ← canonical new-project layout
docs/                      ← guides, plans, slides
```

## Where the skills live now

The plugin itself exposes only `/asdlc-project`, `/asdlc-adopt`, `/asdlc-doctor`, and
`/asdlc-memory-cleanup`. Everything else
is **project-scoped**: `/asdlc-project` (new project) and `/asdlc-adopt` (existing
repo) install the 4 agents and all workflow skills below into the project's own
`.claude/`, so they are active only inside Agentic SDLC projects — never
globally on a machine.

The v1 setup skills are retired and replaced:

| v1 (retired) | v2 |
|---|---|
| `/infiniteleverage-init` | Install the plugin + run `/asdlc-project` — there is no machine setup anymore |
| `/infiniteleverage-onboard` | Same — any laptop just installs the plugin |
| `/infiniteleverage-patch` | Marketplace plugin updates; projects refresh via `/asdlc-adopt` |
| `/infiniteleverage-validate` | `/asdlc-doctor` (product checks) + `/infiniteleverage-telemetry` (Edge8-internal tracking) |
| `/infiniteleverage-project` | `/asdlc-project` |

Machines still carrying the v1 copies keep working until they migrate; the
private `agentic-sdlc-telemetry` plugin cleans them up on its first run.

## The 4 agents

**Build team**: product-manager, developer, qa, devops.
(The developer owns publishing — the old web-publisher role was folded in as a
skill. The writer and designer agents were removed in v2.6.0.)

Each agent is a thin definition in [`.claude/agents/`](.claude/agents) listing
the workflow skills it uses; the skills themselves live in
[`.claude/skills/`](.claude/skills). Those two directories are the single
source of truth — this README deliberately doesn't enumerate skills, because a
hand-maintained list is how the v1 docs drifted.

## Updating

1. Edit `.claude/agents/*.md`, `.claude/skills/*/SKILL.md`, or `plugin/` — all canonical here
2. Bump the version in `plugin/.claude-plugin/plugin.json` + `.claude-plugin/marketplace.json`, update `CHANGELOG.md`
3. Merge to `main` — installed plugins update through the marketplace

Existing projects refresh their agents/skills by running `/asdlc-adopt` in the
repo — or wait for the next scaffolded project to pick up the latest
automatically. There are no zips and no `/infiniteleverage-patch` anymore.

## Migrating from v1

Edge8-internal: handled by the private `agentic-sdlc-telemetry` plugin (its first
session run cleans v1's global installs, hash-verified). Outside users never
had v1 and need nothing.

## Tests

CI validates the plugin manifests, version lockstep, and the no-global-install
invariants on every PR. (The telemetry test suite moved to `agentic-sdlc-telemetry`.)
