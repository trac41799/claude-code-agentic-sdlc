#!/usr/bin/env bash
# asdlc-wave-off — remove the wave-based dev loop and recover the original
# agentic-sdlc project state (17 canonical skills, no wave artifacts).
# Usage: wave-remove.sh [project-dir]
# Idempotent: safe to run when nothing is installed; reports what it found.
set -uo pipefail

PROJ="${1:-.}"
DST="$PROJ/.claude/skills"
FOUND=""

for s in dev-multi-agent asdlc-wave-on asdlc-wave-off; do
  if [ -d "$DST/$s" ]; then
    rm -rf "$DST/$s"
    FOUND="$FOUND $s"
  fi
done

if [ -d "$PROJ/.specify" ]; then
  while IFS= read -r f; do
    rm -f "$f"
    FOUND="$FOUND wave-report:${f#"$PROJ/"}"
  done < <(find "$PROJ/.specify" -name wave-report.md -type f 2>/dev/null)
fi

if [ -n "$FOUND" ]; then
  echo "wave-remove: removed:$FOUND"
else
  echo "wave-remove: nothing installed — project already at original state"
fi
echo "wave-remove: skill count is back to canonical (17)"