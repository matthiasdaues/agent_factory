---
name: commit
description: Compose a Conventional Commit message from the session's context and commit — invoked explicitly, never automatically.
category: utility
disable-model-invocation: true
---

# Commit

Compose a correctly-formatted commit per [commit-conventions.md](../../rulebooks/conventions/commit-conventions.md) and commit — invoked only when explicitly asked to commit, never proactively. Invoking this skill *is* the explicit ask; it does not itself decide whether to commit.

## Step 1 — Gate first

If `validate` hasn't run against the current changes yet this session, run it now. If any gate fails, stop and report — do not proceed to Step 2. This is a courtesy check, not a replacement for the pre-commit hook: the hook still fires on the actual `git commit` and is the real gate.

## Step 2 — Compose the message

1. Determine `<type>` from the change: `feat`, `fix`, `docs`, `style`, `refactor`, `test`, `chore`.
2. Determine the `(<ID>)` suffix, if any, from session context — a story (`ST-NNNN`), bug (`BUG-NNNN`), or other finding tag the change addresses. Omit only when the change genuinely traces to no story or finding (e.g. a drive-by typo fix); do not invent an ID to satisfy the format.
3. Write `<type>: <description> (<ID>)` — imperative mood, no period, per the rulebook's examples.

## Step 3 — Show, then confirm

Present the composed message and the files about to be staged (`git status --short`). Wait for explicit confirmation before committing — do not commit on the same turn the message is first shown, unless the user's original request already confirmed both the content and the act of committing.

## Step 4 — Stage and commit

Stage the specific files discussed (never `git add -A`/`.` blindly — review `git status` output first for anything unexpected, per the same discipline as any other commit). Commit with the confirmed message. Never `--no-verify`, never `--amend` unless explicitly asked. If the pre-commit hook modifies files (e.g. `mdformat`/`ruff --fix`), re-stage exactly those files and commit again — do not re-run Step 2.

**Completion**: commit created, working tree matches what was shown in Step 3 plus any hook-applied formatting.
