#!/usr/bin/env bash
set -euo pipefail

# PreToolUse session hook: detect stale factory/ and warn.
#
# Compares the git tree hash of packages/factory/ (the source) against the
# hash recorded in the install manifest. On mismatch, prints a warning to
# stderr. Does NOT block — the user may choose to continue working with the
# current version. Runs at most once per session (flag file keyed on
# $SESSION_ID or $PPID).
#
# Monorepo-only: exits 0 immediately when packages/factory/ does not exist
# (consumer projects have no source to compare against).
#
# Contract: always exits 0. Warning goes to stderr only. Never blocks.

# Drain stdin (hook payload — not needed for this check).
cat >/dev/null 2>&1 || true

# Resolve project root.
PROJECT_DIR="${CLAUDE_PROJECT_DIR:-}"
if [ -z "$PROJECT_DIR" ]; then
  PROJECT_DIR=$(git rev-parse --show-toplevel 2>/dev/null) || exit 0
fi

SOURCE_DIR="$PROJECT_DIR/packages/factory"
[ -d "$SOURCE_DIR" ] || exit 0

MANIFEST="$PROJECT_DIR/.agent-factory/factory-install.json"
[ -f "$MANIFEST" ] || exit 0

# Once-per-session guard.
SESSION_KEY="${SESSION_ID:-${PPID:-$$}}"
FLAG_DIR="$PROJECT_DIR/.agent-factory/.freshness-check"
FLAG_FILE="$FLAG_DIR/$SESSION_KEY"
if [ -f "$FLAG_FILE" ]; then
  exit 0
fi
mkdir -p "$FLAG_DIR" 2>/dev/null || true
touch "$FLAG_FILE" 2>/dev/null || true

CURRENT_HASH=$(git -C "$PROJECT_DIR" rev-parse HEAD:packages/factory 2>/dev/null) || exit 0

RECORDED_HASH=$(python3 -c "
import json, sys
try:
    m = json.load(open('$MANIFEST'))
    print(m.get('factory_tree_hash', ''))
except Exception:
    pass
" 2>/dev/null)

if [ -z "$RECORDED_HASH" ] || [ "$CURRENT_HASH" != "$RECORDED_HASH" ]; then
  echo "WARNING: installed factory/ is out of sync with packages/factory/. To update, run: ./init-factory --update ." >&2
fi

exit 0
