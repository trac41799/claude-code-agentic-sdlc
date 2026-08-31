#!/usr/bin/env bash
# asdlc-tools mcp — merges the Supabase MCP server entry into the operator's
# Claude Code user config (mcpServers in ~/.claude.json). Reads the access
# token from SUPABASE_ACCESS_TOKEN (never writes it into this repo). Fails
# cleanly with instructions if the token is unset or the config is unreadable.
set -uo pipefail
if [ -z "${SUPABASE_ACCESS_TOKEN:-}" ]; then
  echo "SUPABASE_ACCESS_TOKEN is not set." >&2
  echo "Create one: supabase.com/dashboard/account/tokens (sbp_...)" >&2
  echo "Then: export SUPABASE_ACCESS_TOKEN=sbp_... and rerun this script." >&2
  exit 1
fi
python3 - <<'PY'
import json, os, sys
import pathlib as _pl
home = os.path.expanduser("~")
cfg_path = os.path.expanduser("~/.claude.json")
# defensive guard: never write outside the user's home
if not os.path.abspath(cfg_path).startswith(os.path.abspath(home)):
    print("refusing to write outside the user home:", cfg_path, file=sys.stderr)
    sys.exit(1)
try:
    with open(cfg_path, "r", encoding="utf-8-sig") as f:
        cfg = json.load(f)
except FileNotFoundError:
    cfg = {}
except Exception as e:
    print("could not read the Claude Code user config:", e, file=sys.stderr)
    sys.exit(1)
servers = cfg.setdefault("mcpServers", {})
token = os.environ["SUPABASE_ACCESS_TOKEN"]
servers["supabase"] = {
    "type": "http",
    "url": "https://mcp.supabase.com/mcp",
    "headers": {"Authorization": "Bearer " + token},
}
tmp = cfg_path + ".tmp"
try:
    with open(tmp, "w", encoding="utf-8") as f:
        json.dump(cfg, f, indent=2)
    os.replace(tmp, cfg_path)
except Exception as e:
    print("could not write the MCP config:", e, file=sys.stderr)
    sys.exit(1)
print("supabase MCP entry added to the Claude Code user config (restart Claude Code to load it).")
PY