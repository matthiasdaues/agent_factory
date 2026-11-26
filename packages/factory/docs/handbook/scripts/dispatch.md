---
title: dispatch
type: reference
status: implemented
description: Manage implementation stories, worktrees, waves, and merges.
---

# dispatch

## Name

`dispatch` — Manage implementation stories, worktrees, waves, and merges.

## Synopsis

```text
.agent-factory/factory/scripts/dispatch <command> [<arguments> ...]
```

Use `--help` for argument values and defaults supported by your installed version.

## Subcommands

- `status`. render the current ledger
- `init`. initialize a dispatch run
- `plan`. compute wave plan from stories
- `prepare-wave`. prepare all stories in a wave
- `prepare-story`. prepare a serial chain link
- `mark-dispatching`. mark story as dispatching
- `mark-dispatched`. mark story as dispatched
- `clear-manifest`. force-remove a stale step manifest
- `mark-blocked`. mark story as blocked
- `mark-failed`. mark story as failed
- `re-dispatch`. return story to prepared
- `resume-gates`. return a story blocked by a gate that cannot measure to dispatched
- `return-story`. set a failed or blocked story back to pending (User only)
- `verify-story`. verify a story's commit SHA
- `add`. put an open blocking finding into a new wave of the run
- `escalate`. escalate a story to the next tier
- `refresh-story`. merge the feature branch into a story branch
- `merge-story`. merge a story's feature branch
- `close-wave`. close a completed wave
- `close`. end a finished run, or with --drop a dropped run
- `suggest-merge-args`. print recommended --max-files for the final feature-to-dev merge

## Arguments and options across subcommands

- `--ledger`. path to dispatch ledger (default: derived from current branch)
- `--base`
- `--stories`
- `--baseline-commit`
- `--feature-branch`
- `--mode`
- `--yes`. skip confirmation prompts
- `--backlog-dir`
- `--dry-run`. print wave plan without persisting to the dispatch ledger
- `wave`
- `story_id`
- `--force`. required: confirms forced recovery
- `--worktree`. path to the story's worktree
- `--reason`
- `--class`
- `--evidence`
- `--sha`
- `finding_id`
- `--drop`. end a run whose feature branch is not merged into dev
- `--orphans`. clean up the worktrees and ledgers that no active run owns

## See also

- [Command source](../../../scripts/dispatch)
- [Workflow guide](../branches-and-dispatch/dispatch-runs.md)
