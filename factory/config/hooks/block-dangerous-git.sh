#!/bin/bash
# Shared PreToolUse guardrail for Claude Code, Copilot CLI, and Codex.
# Claude Code sends the shell command at .tool_input.command; Copilot CLI
# sends it at .toolArgs.command; Codex unified exec sends it at
# .tool_input.cmd. All three treat exit code 2 with a stderr reason as denial;
# the stdout JSON below supplies Copilot's CLI-specific reason and is harmless
# to the other consumers.

INPUT=$(cat)
COMMAND=$(echo "$INPUT" | jq -r \
  '.tool_input.command // .toolArgs.command // .tool_input.cmd // empty')

deny() {
  echo "BLOCKED: $1" >&2
  printf '{"permissionDecision":"deny","permissionDecisionReason":%s}\n' "$(printf '%s' "BLOCKED: $1" | jq -Rs .)"
  exit 2
}

# BR-024: Allow factory/scripts/run-tests --staged for agent test iteration (ATAM-0001 fix)
# This is the only permitted test command for agents
if echo "$COMMAND" | grep -qE "^factory/scripts/run-tests[[:space:]]+--staged([[:space:]]|\$)"; then
  exit 0
fi

# retro-2026-07-12 T-07: mechanical verify-base / premerge-check enforcement.
TOP=$(git rev-parse --show-toplevel 2>/dev/null)

if echo "$COMMAND" | grep -qE '^git[[:space:]]+commit([[:space:]]|$)'; then
  if [ "$(git rev-parse --git-dir 2>/dev/null)" != "$(git rev-parse --git-common-dir 2>/dev/null)" ] \
     && [ -n "$TOP" ]; then
    MARKER="$TOP/.agent-factory/verify-base-ok"
    if [ ! -f "$MARKER" ]; then
      deny "git commit in a worktree with no .agent-factory/verify-base-ok marker. Run factory/scripts/verify-base <target> [--expect-base <SHA>] first."
    fi
    # ST-0047: the marker must correspond to THIS worktree — its verified base
    # (head=) must be an ancestor of the current HEAD, so a stale or mismatched
    # marker (e.g. a reused worktree path) no longer authorizes a commit. HEAD
    # advancing during TDD still passes, since it descends from the verified base.
    MARKER_HEAD=$(sed -n 's/^head=//p' "$MARKER")
    if [ -z "$MARKER_HEAD" ] || ! git merge-base --is-ancestor "$MARKER_HEAD" HEAD 2>/dev/null; then
      deny "git commit in a worktree whose verify-base-ok marker does not match its base (marker head is not an ancestor of HEAD). Re-run factory/scripts/verify-base <target> [--expect-base <SHA>]."
    fi
  fi
fi

# Branch creation must be atomic with linked-worktree creation.  Deny the
# standalone creation forms; `git worktree add -b/-B ...` is the only allowed
# branch-creation path. Listing, safe deletion, rename, and show-current remain
# available because they do not create a new branch.
if echo "$COMMAND" | grep -qE '^git[[:space:]]+switch[[:space:]]+([^|&;]*[[:space:]])?-[cC]([[:space:]]|$)' \
   || echo "$COMMAND" | grep -qE '^git[[:space:]]+checkout[[:space:]]+([^|&;]*[[:space:]])?-[bB]([[:space:]]|$)' \
   || echo "$COMMAND" | grep -qE '^git[[:space:]]+branch[[:space:]]+(--track[[:space:]]+|--copy[[:space:]]+|-c[[:space:]]+|-C[[:space:]]+)?[^-[:space:]][^[:space:]|&;]*([[:space:]]+[^[:space:]|&;]+)?([[:space:]]*[|&;]|[[:space:]]*$)'; then
  deny "standalone branch creation is forbidden. Create the branch and its linked worktree atomically with: git worktree add -b <branch> <worktree-path> <base>."
fi

if echo "$COMMAND" | grep -qE '^git[[:space:]]+merge[[:space:]]'; then
  # Isolate the `git merge …` invocation (up to a shell separator) before
  # parsing the branch, so a compound line like `cd repo; git merge feat/x`
  # does not leak `cd` as the operative branch (ST-0046).
  MERGE_SEG=$(echo "$COMMAND" | grep -oE 'git[[:space:]]+merge[[:space:]]+[^|&;]*' | head -1)
  MERGE_BRANCH=""
  for tok in $(echo "$MERGE_SEG" | sed -E 's/^git[[:space:]]+merge[[:space:]]+//'); do
    case "$tok" in
      -*) continue ;;
      *) MERGE_BRANCH="$tok"; break ;;
    esac
  done
  MERGE_HEAD=$(git rev-parse "$MERGE_BRANCH" 2>/dev/null)
  MARKER="$TOP/.agent-factory/premerge-check-ok"
  if [ -z "$TOP" ] || [ ! -f "$MARKER" ] \
     || ! grep -qx "branch=$MERGE_BRANCH" "$MARKER" \
     || ! grep -qx "head=$MERGE_HEAD" "$MARKER"; then
    deny "git merge $MERGE_BRANCH with no passing .agent-factory/premerge-check-ok marker for that branch's current head. Run factory/scripts/premerge-check <target> $MERGE_BRANCH first."
  fi
fi

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
  # Require a git context so a benign non-git command carrying the string
  # (e.g. `grep --no-verify …`) is not blocked, while every git bypass is (ST-0046).
  "git[[:space:]][^|&;]*--no-verify"
  "git[[:space:]]+commit[^|&;]*[[:space:]]-n([[:space:]]|\$)"
  "core\.hooksPath"
  "pre-commit uninstall"
  "SKIP=.*(git commit|pre-commit)"
  # --- test commands (BR-024: tests run via hooks only) ---
  "^pytest([[:space:]]|\$)"
  "^python[0-9]* -m pytest"
  "^uv run pytest"
  "npm test"
  "npm run test"
  "yarn test"
  "^go test"
  "^cargo test"
  "^jest([[:space:]]|\$)"
  "^vitest([[:space:]]|\$)"
  "^mocha([[:space:]]|\$)"
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
