---
title: Git Workflow Under the Guardrail and Hooks
category: implementation
enforcement: git guardrail (block-dangerous-git) + pre-commit hooks
version: 1.0.0
---

# Git Workflow Under the Guardrail and Hooks

Every CLI working in an Agent Factory project runs under two shared, CLI-agnostic mechanisms: the **git-safety guardrail** (blocks dangerous git before it runs) and the **pre-commit hooks** (deterministic validators that also rewrite files). This convention states how to issue git so both cooperate instead of costing round-trips. See [factory-guide § The git-safety guardrail](../../docs/factory-guide.md) for what the guardrail blocks.

## Issue git as lone commands

Run one git operation per shell invocation, never chained after `cd` or another command.

- The shell working directory persists between tool calls, so a `cd` prefix is redundant.
- The guardrail parses a command line to find the operative git argument. A compound line confuses it: `cd repo; git merge feat/x` was read as `git merge cd` and blocked. Running `git merge feat/x` alone parses correctly.
- A benign substring can also trip it — a `grep --no-verify` inside a larger command matches the blocked pattern. Keep such strings out of shell commands; put them in files instead.

## Merging requires the pre-merge marker

`git merge <branch>` is blocked unless a passing `.agent-factory/premerge-check-ok` marker exists for that branch's current head.

- Run `factory/scripts/premerge-check <target> <branch>` first; it writes the marker on PASS.
- Then run `git merge <branch> --no-ff -m "…"` as a **lone** command.

## Blocked operations and their safe forms

The guardrail blocks these in every session, including the operator's own:

| Blocked                                             | Use instead                                                       |
| --------------------------------------------------- | ----------------------------------------------------------------- |
| `git checkout .` / `git checkout -- .`              | `git checkout HEAD -- <path>`                                     |
| `git branch -D` (force delete)                      | `git branch -d` (merged only); ask the operator for force deletes |
| `git commit --no-verify`, `git ... --no-verify`     | Fix the failing hook; never bypass                                |
| `git config core.hooksPath …`                       | Do not repoint hooks                                              |
| `git reset --hard`, `git clean`, `git push --force` | Ask the operator                                                  |

`rm -rf` is separately gated by the safety classifier — ask before destructive removal.

## Commit through the pre-commit hooks — the two-pass rule

The pre-commit hooks **rewrite staged files** as part of committing: `mdformat` and `ruff` reformat, `index-lint` regenerates `factory/INDEX.yaml`, `arch-lint` re-exports diagrams. When a hook rewrites a file the commit aborts with "files were modified by this hook". This is expected, not a failure to investigate. Use a deterministic two-pass sequence:

1. `git add <explicit paths>` — never `git add -A`/`.`; the ignored local wiring (`.pi/`, `AGENTS.md`, `.agent-factory/`) and untracked scratch must not be swept in.
2. `git commit -m "<type>: … (<ID>)"`.
3. If it aborts with "files were modified by this hook", run `git add -u` and re-commit the same message. The second pass is clean because the hooks already rewrote the files.

Alternatively, pre-run the formatters on the staged set first (`factory/scripts/mdformat --number`, `factory/scripts/index-lint`) so the hooks are no-ops on the first pass. `factory/scripts/commit-safe` wraps the two-pass sequence into one command.

## Close absorbed work immediately

After a story or finding branch is merged and the target branch passes its
required verification:

1. Confirm the source worktree is clean with `git -C <worktree> status --short`.
2. Remove that exact worktree with `git worktree remove <worktree>`.
3. Delete the merged local branch with `git branch -d <branch>`.
4. Retain either only when it is named as an active base for a pending review or
   follow-up; record that reason in the handoff.

Use explicit paths and branch names. Never use globs, forced deletion, or a
broad filesystem command for phase cleanup. Cleanup is part of closing the
merged unit, not deferred housekeeping at the end of a feature.

## Record branch state explicitly

At merge and handoff boundaries, record the local branch tip, its configured
upstream tip (or `none`), and ahead/behind counts. Use exact SHAs; decorated log
labels alone can conflate a local branch with similarly named remote-tracking
refs. The required handoff shape is defined by
[handoff-format.md](handoff-format.md#authoritative-current-state).

## Referenced from

- [rules.md § Git workflow](../rules.md#git-workflow)
- [commit-conventions.md § Enforcement](commit-conventions.md#enforcement)
- [branching-policy.md § Pre-Merge Diff Check](branching-policy.md#pre-merge-diff-check)
- [handoff-format.md](handoff-format.md)
