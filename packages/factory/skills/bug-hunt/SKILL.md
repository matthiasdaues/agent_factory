---
name: bug-hunt
description: Exploratory testing followed by a TDD bug-fix loop. Find bugs, file findings, fix with regression tests, retest.
category: quality
---

# Bug Hunt

A loop with two phases: **hunt** (find bugs through exploratory testing) and **fix** (**TDD** regression test per bug). Repeat until a retest cycle finds no new bugs.

Read [factory-voice.md](../../rulebooks/conventions/factory-voice.md) now and hold every rule as a writing constraint. No prose reaches terminal output or a file until it passes all four gates and clears the final pass.

## Scope

Identify the code to review using this three-tier fallback:

1. **Explicit commits (highest priority)**: if base and head commit SHAs are provided, use `git diff <base>..<head>` to scope the hunt.
2. **Pull request**: if a PR number is provided, use `gh pr diff <PR>` to scope the hunt.
3. **Main branch (fallback only)**: if neither explicit commits nor a PR number is given, fall back to `git diff $(git merge-base HEAD main)..HEAD`.

## Phase: Hunt

Execute the system, testing with intent to break it — not to confirm it works.

Focus areas:

- **Edge cases and boundary values** — empty, null, oversized, malformed inputs
- **Error handling and recovery** — does the system degrade gracefully?
- **State transitions that shouldn't be possible** — check against state machines in `docs/spec/state-machines.md`
- **Concurrency and timing** — race conditions, stale reads, double submissions
- **Extension paths** — every alternative Scenario of the Rule, not just the happy path. Verify against the **Gherkin** Scenarios in `docs/spec/features/`.

File each bug immediately. This review classifies findings of the review class `runtime`. Classify each finding by [Class: runtime](../../rulebooks/conventions/finding-classification.md#class-runtime): record its basis, and let the rule of the class compute the severity. File each finding by that severity. A `critical` or `major` finding of the category `defect` or `risk` becomes a finding file with tag `BUG` from the [finding template](../../rulebooks/templates/finding.md), as [finding-format.md](../../rulebooks/conventions/finding-format.md) describes. A `minor` finding becomes one register file `docs/findings/register/runtime/<ID>.json` with `status: open` and gets no finding file. The commit that fixes it sets `status` of the register file to `resolved`. A `note` stays a row of the review report, and a `question` becomes an entry of `docs/spec/work/todo.md`. A register file takes its ID from `next-id`, as a finding file does. Run `.agent-factory/factory/scripts/next-id BUG` and read the ID from its standard output, because a shell variable does not survive from one agent command to the next. When `next-id` fails, stop and report its message; never pick a number by hand. Record reproduction steps, expected vs actual behaviour, violated Rule or Scenario of the feature file in `traces`. Format the finding file via `scripts/mdformat --number <path>` per [markdown-formatting.md](../../rulebooks/conventions/markdown-formatting.md).

## Phase: Fix

For each bug finding, in priority order:

1. **Red**: write a failing test that reproduces the bug. The test name references the finding id (e.g. `BUG-0001`) and the violated Scenario.
2. **Green**: fix the code to make the test pass.
3. Verify no existing tests broke.
4. Commit using **Conventional Commits** (see [commit-conventions.md](../../rulebooks/conventions/commit-conventions.md)): `fix: <description> (BUG-0001)`
5. Set the `status` of the finding file to `resolved`. A `minor` bug has a register file instead, and the commit of step 4 sets its `status` to `resolved`.

After fixing all bugs, return to the Hunt phase. Repeat until a full hunt cycle finds zero new bugs.
