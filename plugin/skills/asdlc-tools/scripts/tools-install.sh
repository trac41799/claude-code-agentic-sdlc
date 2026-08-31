#!/usr/bin/env bash
# asdlc-tools install — installs ONE missing CLI (gh | vercel | supabase).
# Platform-aware: brew on macOS, winget on Windows, npm fallback everywhere.
# Usage: tools-install.sh <gh|vercel|supabase>
set -uo pipefail
T="${1:?usage: tools-install.sh <gh|vercel|supabase>}"
if command -v "$T" >/dev/null 2>&1; then
  echo "$T already installed \u2014 nothing to do"; exit 0
fi
if command -v brew >/dev/null 2>&1; then
  case "$T" in
    gh) brew install gh; exit $? ;;
    vercel) npm i -g vercel; exit $? ;;
    supabase) npm i -g supabase; exit $? ;;
  esac
elif command -v winget >/dev/null 2>&1; then
  case "$T" in
    gh) winget install --accept-source-agreements GitHub.cli; exit $? ;;
  esac
fi
# npm fallback (vercel/supabase are npm packages; gh falls through if no winget/brew)
case "$T" in
  gh) echo "install gh via https://cli.github.com (no brew/winget here)"; exit 1 ;;
  vercel) npm i -g vercel; exit $? ;;
  supabase) npm i -g supabase; exit $? ;;
esac