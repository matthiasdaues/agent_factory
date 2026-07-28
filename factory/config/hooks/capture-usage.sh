#!/bin/bash
# Claude Code Stop and SubagentStop hook script.
# Captures usage records when sessions end. On a Stop (human main session) or
# SubagentStop (dispatched sub-agent) event, reads the event's own transcript
# path and the shared session id from the hook payload and invokes
# usage-capture with --cli claude-code and the available context. Claude's
# SubagentStop transcript_path is the main transcript; agent_transcript_path is
# required for the child record.
#
# This script mirrors block-dangerous-git.sh: factory-owned under
# factory/config/hooks/, symlinked into a project by init-factory, and
# resolving its target through $CLAUDE_PROJECT_DIR.
#
# Contract: Pure non-blocking side-effect. Always exits 0 with no stdout.
# Capture failures are logged to stderr and swallowed (best-effort). Ending
# a session must never be delayed or failed by capture.

INPUT=$(cat)

# Extract required fields from the hook payload. Claude supplies the main
# transcript as transcript_path for both events; SubagentStop's own completed
# run is agent_transcript_path and must not fall back to the main transcript.
SESSION_ID=$(echo "$INPUT" | jq -r '.session_id // empty')
HOOK_EVENT=$(echo "$INPUT" | jq -r '.hook_event_name // empty')
if [ "$HOOK_EVENT" = "SubagentStop" ]; then
  TRANSCRIPT_PATH=$(echo "$INPUT" | jq -r '.agent_transcript_path // empty')
else
  TRANSCRIPT_PATH=$(echo "$INPUT" | jq -r '.transcript_path // empty')
fi

# If transcript_path or session_id is missing/empty, exit quietly (best-effort).
if [ -z "$TRANSCRIPT_PATH" ] || [ -z "$SESSION_ID" ]; then
  exit 0
fi

# Resolve the usage-capture script location.
# Prefer $CLAUDE_PROJECT_DIR (set by Claude Code); fallback to derive from
# the script's own location via git toplevel.
PROJECT_DIR="${CLAUDE_PROJECT_DIR}"
if [ -z "$PROJECT_DIR" ]; then
  # Fallback: derive from git toplevel if script is in a git repo.
  HOOK_DIR="$(cd "$(dirname "$(readlink -f "$0")")" && pwd)"
  PROJECT_DIR=$(git -C "$HOOK_DIR" rev-parse --show-toplevel 2>/dev/null)
  if [ -z "$PROJECT_DIR" ]; then
    # Last resort: assume factory is three levels up from factory/config/hooks/.
    PROJECT_DIR="$(cd "$(dirname "$(readlink -f "$0")")/../../../.." && pwd)"
  fi
fi

USAGE_CAPTURE="$PROJECT_DIR/factory/scripts/usage-capture-runtime"

# If usage-capture doesn't exist, exit quietly (best-effort).
if [ ! -x "$USAGE_CAPTURE" ]; then
  exit 0
fi

# Build the command. Start with required args.
USAGE_CAPTURE_CMD=("$USAGE_CAPTURE" --lifecycle register --root "$PROJECT_DIR" --cli claude-code --transcript "$TRANSCRIPT_PATH" --session "$SESSION_ID")
BRANCH=$(git -C "$PROJECT_DIR" symbolic-ref --quiet --short HEAD 2>/dev/null)
COMMIT_ID=$(git -C "$PROJECT_DIR" rev-parse --verify HEAD 2>/dev/null)
if [ -n "$BRANCH" ]; then
  USAGE_CAPTURE_CMD+=(--branch "$BRANCH")
fi
if [ -n "$COMMIT_ID" ]; then
  USAGE_CAPTURE_CMD+=(--commit "$COMMIT_ID")
fi

# For SubagentStop, add agent_type as --agent.
if [ "$HOOK_EVENT" = "SubagentStop" ]; then
  AGENT_TYPE=$(echo "$INPUT" | jq -r '.agent_type // empty')
  if [ -n "$AGENT_TYPE" ]; then
    USAGE_CAPTURE_CMD+=(--agent "$AGENT_TYPE")
  fi
fi

# Complete only the private snapshot/registration handoff synchronously.
# Normalization and persistence are detached by the lifecycle registrar.
(cd "$PROJECT_DIR" && "${USAGE_CAPTURE_CMD[@]}") >/dev/null 2>&1

# Always exit 0. Session end must never be delayed or failed by capture.
exit 0
