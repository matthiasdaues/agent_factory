#!/bin/bash
# GitHub Copilot CLI agentStop/subagentStop usage-capture hook.
# Best-effort observability only: every path exits zero and writes no stdout.

INPUT=$(cat)
TRANSCRIPT_PATH=$(echo "$INPUT" | jq -r '.transcriptPath // empty' 2>/dev/null)
SESSION_ID=$(echo "$INPUT" | jq -r '.sessionId // empty' 2>/dev/null)
AGENT_NAME=$(echo "$INPUT" | jq -r '.agentName // empty' 2>/dev/null)
CWD=$(echo "$INPUT" | jq -r '.cwd // empty' 2>/dev/null)

if [ -z "$TRANSCRIPT_PATH" ] || [ -z "$SESSION_ID" ]; then
  exit 0
fi

PROJECT_DIR="$CWD"
if [ -z "$PROJECT_DIR" ]; then
  PROJECT_DIR=$(git rev-parse --show-toplevel 2>/dev/null)
fi
if [ -z "$PROJECT_DIR" ]; then
  exit 0
fi

USAGE_CAPTURE="$PROJECT_DIR/factory/scripts/usage-capture-runtime"
if [ ! -x "$USAGE_CAPTURE" ]; then
  exit 0
fi

CMD=("$USAGE_CAPTURE" --lifecycle register --root "$PROJECT_DIR" --cli copilot --transcript "$TRANSCRIPT_PATH" --session "$SESSION_ID")
if [ -n "$AGENT_NAME" ]; then
  CMD+=(--agent "$AGENT_NAME")
fi

(cd "$PROJECT_DIR" && "${CMD[@]}") >/dev/null 2>&1
exit 0
