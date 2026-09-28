#!/usr/bin/env bash
# Regenerate board.svg from the GitHub API so the README serves it from the
# repo instead of a third-party card service at view time. The script only
# writes once the API call has succeeded, so a failed refresh keeps the
# previous board and the profile never shows an error card.
set -uo pipefail
cd "$(dirname "$0")/.."

if python3 scripts/generate-board.py; then
  echo "ok: board.svg"
else
  echo "warn: board refresh failed; keeping previous copy" >&2
  exit 1
fi
