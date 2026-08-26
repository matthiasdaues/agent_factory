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
  EVENT=$(jq -n --arg path "$PATH_VALUE" '{path: $path}')
fi

PROJECT_DIR=$(git rev-parse --show-toplevel 2>/dev/null)
if [ -z "$PROJECT_DIR" ]; then
  exit 0
fi

printf '%s' "$EVENT" | "$PROJECT_DIR/factory/scripts/step-guard" --guard-type "$GUARD_TYPE"
