#!/bin/bash
# The one git guardrail of Claude Code, Codex, Copilot CLI, and pi (ADR-0039).
# Claude Code sends the shell command at .tool_input.command; Codex unified
# exec sends it at .tool_input.cmd; Copilot CLI sends it at .toolArgs.command,
# where toolArgs is an object or a JSON string; pi's extension
# config/extensions/block-dangerous-git.ts sends it at .input.command. All of
# them treat exit code 2 with a stderr reason as denial; the stdout JSON below
# supplies Copilot's CLI-specific reason and is harmless to the others.

INPUT=$(cat)
COMMAND=$(printf '%s' "$INPUT" | jq -r '
  (.toolArgs | if type == "string" then (fromjson? // {}) else . end) as $args
  | .tool_input.command // .tool_input.cmd // $args.command // .input.command // empty')

deny() {
  echo "BLOCKED: $1" >&2
  printf '{"permissionDecision":"deny","permissionDecisionReason":%s}\n' "$(printf '%s' "BLOCKED: $1" | jq -Rs .)"
  exit 2
}

# ST-0427 (ADR-0039, OI-11): dispatch return-story and dispatch close --drop
# destroy work and are always the User's decision, so they are refused in every
# session. The match finds dispatch at a command position: the start of a line,
# or after ; & | ( or a backtick. Before dispatch it skips the words that lead a
# command without being the command, as guard-human-fields does: the WRAPPERS
# words, nohup and exec, an assignment NAME=value, an interpreter such as
# python3, bash or uv run, and their options. dispatch may carry a path, and its
# options, such as --ledger <path>, may stand before the subcommand. A quote may
# surround each word. A quoted mention inside another command, such as a grep
# pattern or a commit message, passes. The script reads only the text, so a
# command built from variables passes too.
SQ="'"
Q="[\"$SQ]?"
PLAIN="[^[:space:];&|()\`\"$SQ]"
LEAD_NAME="(\\{|!|then|do|else|($PLAIN*/)?(env|command|time|sudo|nohup|exec|python[0-9.]*|bash|sh|zsh|dash|uv[[:space:]]+run))"
LEAD_ASSIGN="[A-Za-z_][A-Za-z0-9_]*=(\"[^\"]*\"|$SQ[^$SQ]*$SQ|$PLAIN*)"
OPTION="$Q-$PLAIN*$Q([[:space:]]+$Q[^-[:space:];&|()\`\"$SQ]$PLAIN*$Q)?"
LEAD="($LEAD_NAME|$LEAD_ASSIGN|$OPTION)[[:space:]]+"
DISPATCH_AT="(^|[;&|(\`])[[:space:]]*($LEAD)*$Q($PLAIN*/)?dispatch$Q[[:space:]]+($OPTION[[:space:]]+)*$Q"
DISPATCH_END="$Q([[:space:];&|)\`]|\$)"
if printf '%s\n' "$COMMAND" | grep -qE "${DISPATCH_AT}return-story${DISPATCH_END}"; then
  deny "'$COMMAND' runs dispatch return-story, which destroys the story's work. Only the User runs it."
fi
if printf '%s\n' "$COMMAND" | grep -qE "${DISPATCH_AT}close$Q[[:space:]]([^;&|\`\"$SQ]*[[:space:]])?$Q--drop${DISPATCH_END}"; then
  deny "'$COMMAND' runs dispatch close --drop, which destroys the run's work. Only the User runs it."
fi

# retro-2026-07-12 T-07: mechanical verify-base / premerge-check enforcement.
TOP=$(git rev-parse --show-toplevel 2>/dev/null)

# ST-0427: true when a ledger under <root>/.current-work/ has an entry with
# branch: <branch>. A ledger sits at .current-work/<feature-branch>/, so the
# search stops at depth 4 and does not walk the story worktrees.
ledger_lists_branch() {
  local root="$1" branch="$2" ledger pattern
  pattern="^[[:space:]]+branch:[[:space:]]*[\"']?$(printf '%s' "$branch" | sed 's/[.[\*^$]/\\&/g')[\"']?[[:space:]]*$"
  while IFS= read -r ledger; do
    grep -qE "$pattern" "$ledger" && return 0
  done < <(find "$root/.current-work" -maxdepth 4 -name dispatch-ledger.yaml 2>/dev/null)
  return 1
}

# BR-024 (ST-0150): Allow agent test commands declared in the project's
# testing.yaml, instead of a single hardcoded command.
# test_command, test_staged_command, and test_changed_command are each
# allowlisted when present, matched exactly against the full command string
# (no prefix matching). When no testing.yaml exists at either location, no
# agent test commands are allowed — bare test invocations fall through to
# the deny patterns below, same as before.
resolve_testing_yaml() {
  local root="$1"
  if [ -f "$root/docs/testing.yaml" ]; then
    echo "$root/docs/testing.yaml"
  elif [ -f "$root/docs/agent-context/testing.yaml" ]; then
    echo "$root/docs/agent-context/testing.yaml"
  elif [ -f "$root/docs/charter/testing.yaml" ]; then
    echo "$root/docs/charter/testing.yaml"
  fi
}
CHARTER=$(resolve_testing_yaml "$TOP")
if [ -n "$TOP" ] && [ -n "$CHARTER" ] && [ -f "$CHARTER" ]; then
  for field in test_command test_staged_command test_changed_command; do
    ALLOWED_CMD=$(grep "^${field}:" "$CHARTER" | head -1 \
      | sed -E "s/^${field}:[[:space:]]*//" | sed -E 's/^"(.*)"$/\1/' | sed -E "s/^'(.*)'$/\1/")
    if [ -n "$ALLOWED_CMD" ] && [ "$COMMAND" = "$ALLOWED_CMD" ]; then
      exit 0
    fi
  done
fi

# BR-024: an agent may run named test files under tests/, so a red or green
# check does not need the whole suite. The command is `uv run pytest`, then
# options and at least one file or node ID under tests/, and nothing else.
# A bare `uv run pytest`, a shell operator, a quote, a `$` or a path outside
# tests/ never matches, so the full suite still runs only through the hooks.
SCOPED_TEST_OPT='-[-A-Za-z0-9=:]+( [A-Za-z0-9_.=:-]+)?'
SCOPED_TEST_FILE='tests/[A-Za-z0-9_./-]+\.py(::[A-Za-z0-9_.,=-]+(\[[A-Za-z0-9_.,=-]+\])?)*'
# `--directory <path>` may name the worktree to run in, because an agent's
# shell may start each call in another folder and a `cd` makes a compound
# command.
SCOPED_TEST_RE="^uv run( --directory [A-Za-z0-9_./-]+)? pytest( ${SCOPED_TEST_OPT})*( ${SCOPED_TEST_FILE})+( ${SCOPED_TEST_OPT})*$"
if [[ "$COMMAND" =~ $SCOPED_TEST_RE ]] && [[ "$COMMAND" != *..* ]]; then
  exit 0
fi

if echo "$COMMAND" | grep -qE '^git[[:space:]]+commit([[:space:]]|$)'; then
  if [ "$(git rev-parse --git-dir 2>/dev/null)" != "$(git rev-parse --git-common-dir 2>/dev/null)" ] \
     && [ -n "$TOP" ]; then
    MARKER="$TOP/.current-work/verify-base-ok"
    # The installed factory lives only in the main checkout; a linked
    # worktree has no .agent-factory/ of its own.
    MAIN_ROOT=$(cd "$(git rev-parse --git-common-dir)/.." 2>/dev/null && pwd)
    if [ ! -f "$MARKER" ]; then
      deny "git commit in a worktree with no .current-work/verify-base-ok marker. Run $MAIN_ROOT/.agent-factory/factory/scripts/verify-base <target> [--expect-base <SHA>] first."
    fi
    # ST-0047: the marker must correspond to THIS worktree — its verified base
    # (head=) must be an ancestor of the current HEAD, so a stale or mismatched
    # marker (e.g. a reused worktree path) no longer authorizes a commit. HEAD
    # advancing during TDD still passes, since it descends from the verified base.
    MARKER_HEAD=$(sed -n 's/^head=//p' "$MARKER")
    if [ -z "$MARKER_HEAD" ] || ! git merge-base --is-ancestor "$MARKER_HEAD" HEAD 2>/dev/null; then
      deny "git commit in a worktree whose verify-base-ok marker does not match its base (marker head is not an ancestor of HEAD). Re-run $MAIN_ROOT/.agent-factory/factory/scripts/verify-base <target> [--expect-base <SHA>]."
    fi
    # ST-0214, ST-0427: a story branch belongs to the run whose ledger lists
    # it. A ledger of another branch never counts.
    BRANCH=$(git rev-parse --abbrev-ref HEAD 2>/dev/null)
    case "$BRANCH" in
      story/*)
        if ! ledger_lists_branch "$MAIN_ROOT" "$BRANCH"; then
          deny "git commit on $BRANCH with no dispatch ledger that lists $BRANCH. No .current-work/<feature-branch>/dispatch-ledger.yaml in the main checkout ($MAIN_ROOT) has an entry with branch: $BRANCH. Run $MAIN_ROOT/.agent-factory/factory/scripts/dispatch init on the feature branch and dispatch the story first."
        fi
        ;;
    esac
  fi
fi

# Branch creation must be atomic with linked-worktree creation.  Deny the
# standalone creation forms; `git worktree add -b/-B ...` is the only allowed
# branch-creation path. Listing, safe deletion, rename, and show-current remain
# available because they do not create a new branch.
if echo "$COMMAND" | grep -qE '^git[[:space:]]+switch[[:space:]]+([^|&;]*[[:space:]])?-[cC]([[:space:]]|$)' \
   || echo "$COMMAND" | grep -qE '^git[[:space:]]+checkout[[:space:]]+([^|&;]*[[:space:]])?-[bB]([[:space:]]|$)' \
   || echo "$COMMAND" | grep -qE '^git[[:space:]]+branch[[:space:]]+(--track[[:space:]]+|--copy[[:space:]]+|-c[[:space:]]+|-C[[:space:]]+)?[^-[:space:]][^[:space:]|&;]*([[:space:]]+[^[:space:]|&;]+)?([[:space:]]*[|&;]|[[:space:]]*$)'; then
  deny "standalone branch creation is forbidden. Create the branch and its linked worktree atomically with: git worktree add -b <branch> .current-work/<feature-branch>/<branch> <base>."
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
      *) deny "worktrees must be created under .current-work/<feature-branch>/. Got: $WT_PATH" ;;
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
  # BUG-0124 (BR-091): a stop denies the merge even when a premerge-check-ok
  # marker from before the stop exists. The check is a read-only call to
  # stop_notice. Like guard-human-fields, a gate that cannot run it fails closed.
  SCRIPTS_DIR="$(dirname "$(readlink -f "${BASH_SOURCE[0]}")")/../../scripts"
  if [ ! -f "$SCRIPTS_DIR/dispatch_lib.py" ]; then
    deny "git merge $MERGE_BRANCH: the stop check is missing at $SCRIPTS_DIR/dispatch_lib.py; run update-factory."
  fi
  STOP_NOTICE=$(python3 -c 'import sys; sys.path.insert(0, sys.argv[1]); from dispatch_lib import stop_notice; sys.stdout.write(stop_notice() or "")' "$SCRIPTS_DIR" 2>/dev/null) \
    || deny "git merge $MERGE_BRANCH: the stop check failed to run, so the merge is denied. Run update-factory."
  if [ -n "$STOP_NOTICE" ]; then
    deny "git merge $MERGE_BRANCH during a stop on a critical finding; no .current-work/premerge-check-ok marker counts until the stop lifts. $STOP_NOTICE"
  fi
  MERGE_HEAD=$(git rev-parse "$MERGE_BRANCH" 2>/dev/null)
  MARKER="$TOP/.current-work/premerge-check-ok"
  if [ -z "$TOP" ] || [ ! -f "$MARKER" ] \
     || ! grep -qx "branch=$MERGE_BRANCH" "$MARKER" \
     || ! grep -qx "head=$MERGE_HEAD" "$MARKER"; then
    deny "git merge $MERGE_BRANCH with no passing .current-work/premerge-check-ok marker for that branch's current head. Run .agent-factory/factory/scripts/premerge-check <target> $MERGE_BRANCH first."
  fi
fi

# BR-024: a command position is the start of a line or the place after
# ; & | ( or a backtick, followed by words that lead a command without being
# it: an assignment NAME=value, env, nohup, exec or time.
TEST_AT='(^|[;&|(`])[[:space:]]*(([A-Za-z_][A-Za-z0-9_]*=[^[:space:]]*|env|nohup|exec|time)[[:space:]]+)*'
# An option of `uv run`, with or without a value, such as --directory /x.
UV_OPT=' +-[^[:space:]]+( +[^-[:space:]][^[:space:]]*)?'
# The end of a test command word: a space, the end, or ; & | ) or a backtick.
TEST_END='([[:space:];&|)`]|$)'

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
)

# --- test commands (BR-024: tests run via hooks only) ---
# These patterns read TEST_SCAN, not COMMAND: the command with every quoted
# string and every here-document body blanked out, so a commit message or a
# grep pattern that names a test command passes. A command that holds `$(` or
# a backtick is read whole, because a command substitution runs even inside
# double quotes.
TEST_PATTERNS=(
  # Each pattern starts at a command position (TEST_AT), so a test run after
  # `cd x &&`, `;`, a pipe or `(` is blocked too, and so is `uv run` with its
  # own options before pytest. A quoted mention inside another command, such
  # as a grep pattern, does not stand at a command position and passes.
  "${TEST_AT}pytest${TEST_END}"
  "${TEST_AT}python[0-9.]* +-m +pytest"
  "${TEST_AT}uvx +pytest${TEST_END}"
  "${TEST_AT}uv +run(${UV_OPT})* +(python[0-9.]* +-m +)?pytest${TEST_END}"
  "npm test"
  "npm run test"
  "yarn test"
  "${TEST_AT}go +test"
  "${TEST_AT}cargo +test"
  "${TEST_AT}jest${TEST_END}"
  "${TEST_AT}vitest${TEST_END}"
  "${TEST_AT}mocha${TEST_END}"
)

# blank_quoted prints its input with the inside of each '…' and "…" string
# and each here-document body replaced by spaces; newlines stay, so a line
# start still counts as a command position.
blank_quoted() {
  awk -v sq="'" 'BEGIN { RS = "\001" }
  {
    s = $0; n = length(s); i = 1; q = ""; out = ""
    while (i <= n) {
      c = substr(s, i, 1)
      if (q != "") {
        if (c == q) { q = ""; out = out c }
        else if (c == "\n") { out = out "\n" }
        else { out = out " " }
        i++; continue
      }
      if (c == sq || c == "\"") { q = c; out = out c; i++; continue }
      if (c == "\\") { out = out "  "; i += 2; continue }
      if (substr(s, i, 2) == "<<") {
        rest = substr(s, i + 2)
        if (match(rest, /^-?[ \t]*["'"'"']?[A-Za-z_][A-Za-z0-9_]*["'"'"']?/)) {
          tag = substr(rest, RSTART, RLENGTH)
          gsub(/[- \t"'"'"']/, "", tag)
          eol = index(substr(s, i), "\n")
          if (eol == 0) { out = out substr(s, i); break }
          out = out substr(s, i, eol - 1) "\n"
          i += eol
          while (i <= n) {
            eol = index(substr(s, i), "\n")
            line = eol ? substr(s, i, eol - 1) : substr(s, i)
            i = eol ? i + eol : n + 1
            sub(/^\t+/, "", line)
            if (line == tag) { out = out tag "\n"; break }
            out = out "\n"
          }
          continue
        }
      }
      out = out c; i++
    }
    printf "%s", out
  }'
}

for pattern in "${DANGEROUS_PATTERNS[@]}"; do
  if echo "$COMMAND" | grep -qE -- "$pattern"; then
    REASON="BLOCKED: '$COMMAND' matches dangerous pattern '$pattern'. The user has prevented you from doing this."
    echo "$REASON" >&2
    printf '{"permissionDecision":"deny","permissionDecisionReason":%s}\n' "$(printf '%s' "$REASON" | jq -Rs .)"
    exit 2
  fi
done

case "$COMMAND" in
  *'$('* | *'`'*) TEST_SCAN="$COMMAND" ;;
  *) TEST_SCAN=$(printf '%s' "$COMMAND" | blank_quoted) ;;
esac
for pattern in "${TEST_PATTERNS[@]}"; do
  if printf '%s\n' "$TEST_SCAN" | grep -qE -- "$pattern"; then
    REASON="BLOCKED: '$COMMAND' matches dangerous pattern '$pattern'. The user has prevented you from doing this."
    echo "$REASON" >&2
    printf '{"permissionDecision":"deny","permissionDecisionReason":%s}\n' "$(printf '%s' "$REASON" | jq -Rs .)"
    exit 2
  fi
done

exit 0
