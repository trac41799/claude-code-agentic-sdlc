---
name: asdlc-tools
description: Installs the machine's missing CLI tools for the developer stack — GitHub CLI (gh), Vercel CLI, Supabase CLI — and configures the Supabase MCP server in the Claude Code user config if it is not already present. Checks machine status FIRST, then installs only what is missing. Use when the operator says "install the tools", "setup the CLIs", "get gh/vercel/supabase", "configure supabase mcp", or before a first /asdlc-project run on a fresh machine.
---
# asdlc-tools — install the stack's CLIs + Supabase MCP

This skill checks what is already on the machine, then installs ONLY the
missing pieces. Nothing is installed twice, nothing global is touched except
the operator's own `~/.claude.json` MCP config (explicitly at their
direction), and no credentials are invented — if a token is missing the skill
says exactly where to get it and stops.

## Step 1 — status first (never install before checking)

Run the status script from this plugin:

```bash
bash "$(dirname "$0")/scripts/tools-status.sh"
```

It prints a row per tool: `gh`, `vercel`, `supabase`, and `supabase MCP
(config)`. Read every line to the operator and wait for approval — the
operator decides which items to install. Never run installs before showing
status.

## Step 2 — install the missing CLIs (one at a time)

For each missing CLI the operator confirms, run:

```bash
bash "$(dirname "$0")/scripts/tools-install.sh gh"      # or: vercel, supabase
```

The installer picks the platform's package manager:
- macOS: Homebrew (`brew`) if present, else `npm i -g`.
- Windows: `winget` if present, else `npm i -g`.
- Linux: `npm i -g` (requires Node, which /asdlc-doctor already verifies).

`npm` is the common fallback for vercel and supabase (both are npm
packages); `gh` uses winget/brew/curl. After each install, re-run the status
script and confirm the row flipped to `installed` before moving on.

## Step 3 — Supabase MCP config

The Supabase MCP server lets the agent query a Supabase project live (see
`supabase.com/docs/guides/ai-tools/mcp`). The status check reports whether
`supabase` is already in the Claude Code user config (`~/.claude.json`,
`mcpServers`).

If not configured and the operator approves:

1. Ask if they already have a personal access token (PAT). If not, tell them
   to create one: supabase.com/dashboard/account/tokens → "Generate new
   token" → name it e.g. `asdlc-mcp`, copy the `sbp_...` value. Say explicitly:
   keep the token out of any file that ends up in git; the MCP config lives
   in `~/.claude.json` (the operator's own home), never in the project.
2. Set it for the config step:
   `export SUPABASE_ACCESS_TOKEN=sbp_...` (or have it in the environment).
3. Run:
   ```bash
   bash "$(dirname "$0")/scripts/tools-mcp.sh"
   ```
   The script merges the `supabase` server entry into the user config's
   `mcpServers` (HTTP type, `https://mcp.supabase.com/mcp`, `Authorization:
   Bearer $SUPABASE_ACCESS_TOKEN`) — and it FAILS cleanly with instructions
   if SUPABASE_ACCESS_TOKEN is unset or if the config file is unreadable.
4. Verify: re-run the status script — the MCP row shows `configured`.
   Tell the operator to restart Claude Code so the MCP server loads.

Never write the token value into any file in this repository. The script
only reads it from the environment.

## Rules

- Machine status is checked and shown BEFORE any install (never assume).
- Idempotent: re-running skips everything already present.
- No `permissions` grants; no writes into `~/.claude/` (only the operator's
  own `~/.claude.json` MCP entry, at their explicit direction).
- If a tool returns an error mid-install, stop and report the exact output —
  never paper over a failed install.