#!/usr/bin/env bash
# asdlc-wave-on — install the v1 wave-based dev loop into a project.
# Usage: wave-install.sh <bundle-dir> [project-dir]
# Idempotent: re-running overwrites the three wave skills, nothing else.
set -euo pipefail

BUNDLE="${1:?usage: wave-install.sh <bundle-dir> [project-dir]}"
PROJ="${2:-.}"
SRC="$BUNDLE/skills"
DST="$PROJ/.claude/skills"

mkdir -p "$DST"
for s in dev-multi-agent asdlc-wave-on asdlc-wave-off; do
  if [ ! -f "$SRC/$s/SKILL.md" ]; then
    echo "wave-install: missing $SRC/$s/SKILL.md" >&2
    exit 1
  fi
  mkdir -p "$DST/$s"
  cp "$SRC/$s/SKILL.md" "$DST/$s/SKILL.md"
done
echo "wave-install: installed dev-multi-agent + asdlc-wave-on + asdlc-wave-off into $DST"