#!/usr/bin/env bash
# HERMES one-shot deploy — ItsnotAILabs / NOVA PROTOCOL
set -e
ROOT="$(cd "$(dirname "$0")" && pwd)"
cd "$ROOT"
echo "HERMES Fleet deploy"
python "$ROOT/../../scripts/forge_hermes_fleet.py"
if command -v wrangler >/dev/null 2>&1; then
  for d in "$ROOT/workers"/*/; do
    echo "Deploy $(basename "$d")..."
    (cd "$d" && wrangler deploy)
  done
else
  echo "wrangler not found — pack ready at deliverables/hermes/"
fi
