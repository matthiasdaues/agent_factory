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

# retro-2026-07-12 T-07: mechanical verify-base / premerge-check enforcement.
TOP=$(git rev-parse --show-toplevel 2>/dev/null)

# BR-024 (ST-0150): Allow agent test commands declared in the project's
# charter, docs/charter/testing.yaml, instead of a single hardcoded command.
# test_command, test_staged_command, and test_changed_command are each
# allowlisted when present, matched exactly against the full command string
# (no prefix matching). When the charter file does not exist, no agent test
# commands are allowed — bare test invocations fall through to the deny
# patterns below, same as before this charter existed.
CHARTER="$TOP/docs/charter/testing.yaml"
if [ -n "$TOP" ] && [ -f "$CHARTER" ]; then
  for field in test_command test_staged_command test_changed_command; do
    ALLOWED_CMD=$(grep "^${field}:" "$CHARTER" | head -1 \
      | sed -E "s/^${field}:[[:space:]]*//" | sed -E 's/^"(.*)"$/\1/' | sed -E "s/^'(.*)'$/\1/")
    if [ -n "$ALLOWED_CMD" ] && [ "$COMMAND" = "$ALLOWED_CMD" ]; then
      exit 0
    fi
  done
fi

if echo "$COMMAND" | grep -qE '^git[[:space:]]+commit([[:space:]]|$)'; then
  if [ "$(git rev-parse --git-dir 2>/dev/null)" != "$(git rev-parse --git-common-dir 2>/dev/null)" ] \
     && [ -n "$TOP" ]; then
    MARKER="$TOP/.current-work/verify-base-ok"
    if [ ! -f "$MARKER" ]; then
      deny "git commit in a worktree with no .current-work/verify-base-ok marker. Run factory/scripts/verify-base <target> [--expect-base <SHA>] first."
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
  deny "standalone branch creation is forbidden. Create the branch and its linked worktree atomically with: git worktree add -b <branch> .current-work/<branch> <base>."
fi

# Worktrees must live under .current-work/.  Deny `git worktree add`
# when the path argument does not start with that prefix.
if echo "$COMMAND" | grep -qE '^git[[:space:]]+worktree[[:space:]]+add[[:space:]]'; then
  WT_PATH=""
  SKIP_NEXT=false
  for tok in $(echo "$COMMAND" | sed -E 's/^git[[:space:]]+worktree[[:space:]]+add[[:space:]]+//'); do
    case "$tok" in
      -b|-B) SKIP_NEXT=true; continue ;;
      -*) continue ;;
      *)
        if $SKIP_NEXT; then SKIP_NEXT=false; continue; fi
        WT_PATH="$tok"; break ;;
    esac
  done
  if [ -n "$WT_PATH" ]; then
    case "$WT_PATH" in
      .current-work/*) ;; # allowed
      *) deny "worktrees must be created under .current-work/. Got: $WT_PATH" ;;
    esac
  fi
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
  MARKER="$TOP/.current-work/premerge-check-ok"
  if [ -z "$TOP" ] || [ ! -f "$MARKER" ] \
     || ! grep -qx "branch=$MERGE_BRANCH" "$MARKER" \
     || ! grep -qx "head=$MERGE_HEAD" "$MARKER"; then
    deny "git merge $MERGE_BRANCH with no passing .current-work/premerge-check-ok marker for that branch's current head. Run factory/scripts/premerge-check <target> $MERGE_BRANCH first."
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
