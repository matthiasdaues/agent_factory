---
name: bug-hunt
description: Exploratory testing followed by a TDD bug-fix loop. Find bugs, file findings, fix with regression tests, retest.
category: quality
disable-model-invocation: true
---

# Bug Hunt

A loop with two phases: **hunt** (find bugs through exploratory testing) and **fix** (**TDD** regression test per bug). Repeat until a retest cycle finds no new bugs.

## Phase: Hunt

Execute the system, testing with intent to break it — not to confirm it works.

Focus areas:

- **Edge cases and boundary values** — empty, null, oversized, malformed inputs
- **Error handling and recovery** — does the system degrade gracefully?
- **State transitions that shouldn't be possible** — check against state machines in `docs/spec/supplementary_specs/state-machines.md`
- **Concurrency and timing** — race conditions, stale reads, double submissions
- **Extension paths** — every extension in the persona use cases, not just the happy path. Verify against **Gherkin** acceptance criteria where they exist.

File each bug immediately per [finding-format.md](../../rulebooks/conventions/finding-format.md) with tag `BUG`: reproduction steps, expected vs actual behaviour, violated Use Case ID in `traces`. Format the finding file via `scripts/mdformat --number <path>` per [markdown-formatting.md](../../rulebooks/conventions/markdown-formatting.md).

## Phase: Fix

For each bug finding, in priority order:

1. **Red**: write a failing test that reproduces the bug. The test name references the finding id (e.g. `BUG-0001`) and Use Case ID.
2. **Green**: fix the code to make the test pass.
3. Verify no existing tests broke.
4. Commit using **Conventional Commits** (see [commit-conventions.md](../../rulebooks/conventions/commit-conventions.md)): `fix: <description> (BUG-0001)`
5. Set the finding's `status` to `resolved`.

After fixing all bugs, return to the Hunt phase. Repeat until a full hunt cycle finds zero new bugs.
