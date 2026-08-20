---
id: SPEC-007
source: spec-review
severity: major
category: defect
artifact: docs/proposals/mechanize-dispatch-orchestration.md#dispatch-verify-story-story-id-sha-commit-sha
status: resolved
traces: []
---

# verify-story / merge-story split breaks the premerge-check marker pairing rule

**What is wrong:** The proposal runs `premerge-check` inside `dispatch verify-story` and defers the merge to a separate `dispatch merge-story`, and the rewritten workflow batches them ("`verify-story` for each", then "`merge-story` for each"). This contradicts [branching-policy.md § Pre-Merge Diff Check](../../factory/rulebooks/conventions/branching-policy.md#pre-merge-diff-check): the `premerge-check-ok` marker is one slot per checkout, keyed to the checked branch's current head, and each check "must be immediately followed by that branch's own `git merge`, one pair at a time". `factory/config/hooks/block-dangerous-git.sh` denies any `git merge <branch>` whose marker does not match that branch's name and head — so verifying story A, then story B, then merging A fails mechanically: B's check overwrote the marker. The proposal also never states in which checkout subcommands execute; `premerge-check` writes its marker at the toplevel of the checkout it runs in, while the merge must run in the invocation-branch worktree — run from the wrong cwd the marker lands where the hook never looks.

**Fix:** Move the `premerge-check` call out of `verify-story` and into `merge-story`, immediately before `git merge` (verify-story keeps the SHA checks only), or mandate a strict per-story verify→merge interleave. State explicitly that all merge-path subcommands execute in the invocation-branch worktree, so the marker is written where `block-dangerous-git.sh` checks it.

**Resolution (2026-08-18, repeat pass):** Fixed in commit c1507a1. The proposal now states that all git-mutating subcommands execute in the invocation-branch worktree, with the marker/hook rationale spelled out. `verify-story` keeps only the SHA checks and carries an explicit note explaining why `premerge-check` is deliberately excluded (one-slot marker keyed to branch head; check must immediately precede its own merge). `merge-story` runs `premerge-check` immediately before its own `git merge` in the same subcommand invocation, so the pairing holds by construction. Verified against the current proposal text.
