#!/bin/bash
# Codex Stop/SubagentStop usage-capture hook. Best effort and silent.

INPUT=$(cat)
TRANSCRIPT_PATH=$(echo "$INPUT" | jq -r '.transcript_path // .transcriptPath // empty' 2>/dev/null)
SESSION_ID=$(echo "$INPUT" | jq -r '.session_id // .sessionId // empty' 2>/dev/null)
PARENT_SESSION_ID=$(echo "$INPUT" | jq -r '.parent_session_id // .parentSessionId // empty' 2>/dev/null)
AGENT_NAME=$(echo "$INPUT" | jq -r '.agent_name // .agentName // empty' 2>/dev/null)
PROJECT_DIR=$(echo "$INPUT" | jq -r '.cwd // empty' 2>/dev/null)

if [ -z "$TRANSCRIPT_PATH" ] || [ -z "$SESSION_ID" ]; then
  exit 0
fi

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

CMD=("$USAGE_CAPTURE" --lifecycle register --root "$PROJECT_DIR" --cli codex --transcript "$TRANSCRIPT_PATH" --session "$SESSION_ID")
if [ -n "$PARENT_SESSION_ID" ]; then
  CMD+=(--parent-session "$PARENT_SESSION_ID")
fi
if [ -n "$AGENT_NAME" ]; then
  CMD+=(--agent "$AGENT_NAME")
fi

(cd "$PROJECT_DIR" && "${CMD[@]}") >/dev/null 2>&1
exit 0
