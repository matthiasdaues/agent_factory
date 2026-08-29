#!/bin/bash
# Shared step-guard adapter for Claude Code, Copilot CLI, and Codex.

set -eu

INPUT=$(cat)
GUARD_TYPE=${GUARD_TYPE:-${STEP_GUARD_TYPE:-}}

case "$GUARD_TYPE" in
  read|write|bash) ;;
  *)
    echo "step-guard adapter: missing or invalid GUARD_TYPE" >&2
    exit 2
    ;;
esac

if [ "$GUARD_TYPE" = "bash" ]; then
  COMMAND=$(printf '%s' "$INPUT" | jq -r \
    '.tool_input.command // .toolArgs.command // .tool_input.cmd // .toolArgs.cmd // empty')
  EVENT=$(jq -n --arg command "$COMMAND" '{command: $command}')
else
  PATH_VALUE=$(printf '%s' "$INPUT" | jq -r \
    '.tool_input.file_path // .tool_input.path // .toolArgs.path // .toolArgs.file_path // .path // empty')

  # Codex apply_patch: path is embedded in patch text, not a separate field.
  # Extract all target paths from *** Add/Update/Delete File: headers.
  if [ -z "$PATH_VALUE" ]; then
    PATCH_TEXT=$(printf '%s' "$INPUT" | jq -r \
      '.tool_input.patch // .toolArgs.patch // empty')
    if [ -n "$PATCH_TEXT" ]; then
      PATCH_PATHS=$(printf '%s' "$PATCH_TEXT" | \
        grep -oP '^\*{3} (?:Add|Update|Delete) File: \K.+' || true)
    fi
  fi
fi

PROJECT_DIR=$(git rev-parse --show-toplevel 2>/dev/null)
if [ -z "$PROJECT_DIR" ]; then
  exit 0
fi

GUARD="$PROJECT_DIR/factory/scripts/step-guard"

if [ "$GUARD_TYPE" != "bash" ] && [ -n "${PATCH_PATHS:-}" ]; then
  # Check each path from the patch against the guard.
  while IFS= read -r P; do
    [ -z "$P" ] && continue
    EVENT=$(jq -n --arg path "$P" '{path: $path}')
    printf '%s' "$EVENT" | "$GUARD" --guard-type "$GUARD_TYPE"
    RC=$?
    if [ "$RC" -ne 0 ]; then
      exit "$RC"
    fi
  done <<< "$PATCH_PATHS"
  exit 0
fi

if [ "$GUARD_TYPE" != "bash" ]; then
  EVENT=$(jq -n --arg path "$PATH_VALUE" '{path: $path}')
fi

printf '%s' "$EVENT" | "$GUARD" --guard-type "$GUARD_TYPE"
