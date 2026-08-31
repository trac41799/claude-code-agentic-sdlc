#!/usr/bin/env bash
# asdlc-tools status — machine status before anything is installed.
# Prints one row per tool: gh / vercel / supabase / supabase MCP.
set -uo pipefail
echo "== TOOL STATUS =="
for cmd in gh vercel supabase; do
  if command -v "$cmd" >/dev/null 2>&1; then
    printf "%-14s INSTALLED\n" "$cmd"
  else
    printf "%-14s missing\n" "$cmd"
  fi
done
if [ -f "$HOME/.claude.json" ]; then
  if python3 - <<'PY'
import json, os, sys
try:
    cfg = json.load(open(os.path.expanduser("~/.claude.json"), encoding="utf-8"))
except Exception:
    sys.exit(1)
servers = cfg.get("mcpServers") or {}
sys.exit(0 if "supabase" in servers else 1)
PY
  then
    printf "%-14s configured\n" "supabase MCP"
  else
    printf "%-14s not configured\n" "supabase MCP"
  fi
else
  printf "%-14s not configured (no user config)\n" "supabase MCP"
fi