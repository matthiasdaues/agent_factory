#!/bin/bash
# Shared PreToolUse guardrail for both Claude Code and Copilot CLI.
# Claude Code sends the shell command at .tool_input.command; Copilot CLI
# sends it at .toolArgs.command. Both treat exit code 2 as "deny" — Claude
# Code reads the reason from stderr, Copilot CLI from the stdout JSON below.

INPUT=$(cat)
COMMAND=$(echo "$INPUT" | jq -r '.tool_input.command // .toolArgs.command // empty')

DANGEROUS_PATTERNS=(
  "git push"
  "git reset --hard"
  "git clean -fd"
  "git clean -f"
  "git branch -D"
  "git checkout \."
  "git restore \."
  "push --force"
  "reset --hard"
  # --- pre-commit / gate-hook bypasses (never skip this repo's own gates) ---
  "--no-verify"
  "git[[:space:]]+commit[^|&;]*[[:space:]]-n([[:space:]]|\$)"
  "core\.hooksPath"
  "pre-commit uninstall"
  "SKIP=.*(git commit|pre-commit)"
)

for pattern in "${DANGEROUS_PATTERNS[@]}"; do
  if echo "$COMMAND" | grep -qE -- "$pattern"; then
    REASON="BLOCKED: '$COMMAND' matches dangerous pattern '$pattern'. The user has prevented you from doing this."
    echo "$REASON" >&2
    printf '{"permissionDecision":"deny","permissionDecisionReason":%s}\n' "$(printf '%s' "$REASON" | jq -Rs .)"
    exit 2
  fi
done

exit 0
