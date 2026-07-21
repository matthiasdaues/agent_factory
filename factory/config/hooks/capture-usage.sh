#!/bin/bash
# Claude Code Stop and SubagentStop hook script.
# Captures usage records when sessions end. On a Stop (human main session) or
# SubagentStop (dispatched sub-agent) event, reads the transcript path and
# session id from the hook payload and invokes usage-capture with --cli
# claude-code and the available context.
#
# This script mirrors block-dangerous-git.sh: factory-owned under
# factory/config/hooks/, symlinked into a project by init-factory, and
# resolving its target through $CLAUDE_PROJECT_DIR.
#
# Contract: Pure non-blocking side-effect. Always exits 0 with no stdout.
# Capture failures are logged to stderr and swallowed (best-effort). Ending
# a session must never be delayed or failed by capture.

INPUT=$(cat)

# Extract required fields from the hook payload.
TRANSCRIPT_PATH=$(echo "$INPUT" | jq -r '.transcript_path // empty')
SESSION_ID=$(echo "$INPUT" | jq -r '.session_id // empty')
HOOK_EVENT=$(echo "$INPUT" | jq -r '.hook_event_name // empty')

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

USAGE_CAPTURE="$PROJECT_DIR/factory/scripts/usage-capture"

# If usage-capture doesn't exist, exit quietly (best-effort).
if [ ! -x "$USAGE_CAPTURE" ]; then
  exit 0
fi

# Build the command. Start with required args.
USAGE_CAPTURE_CMD=("$USAGE_CAPTURE" --cli claude-code --transcript "$TRANSCRIPT_PATH" --session "$SESSION_ID")

# For SubagentStop, add agent_type as --agent.
if [ "$HOOK_EVENT" = "SubagentStop" ]; then
  AGENT_TYPE=$(echo "$INPUT" | jq -r '.agent_type // empty')
  if [ -n "$AGENT_TYPE" ]; then
    USAGE_CAPTURE_CMD+=(--agent "$AGENT_TYPE")
  fi
fi

# Invoke usage-capture in the background so we never block session end.
# Redirect stderr to null to silence any transient errors; capture is best-effort.
"${USAGE_CAPTURE_CMD[@]}" >/dev/null 2>&1 &

# Always exit 0. Session end must never be delayed or failed by capture.
exit 0
