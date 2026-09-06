---
name: implement-issue
description: Implement a single backlog story with TDD — analyse, red-green, commit, check docs.
category: implementation
disable-model-invocation: true
---

# Implement Issue

Pick a single story from the backlog (`backlog/ST-NNNN.md`) and implement it using **TDD**. Apply **Clean Architecture** and **SOLID** throughout.

Read `docs/CONTEXT.md` if it exists — match test names and interface vocabulary to the project's domain language. Respect ADRs in the area you're touching. Read `docs/agent-context/reading-guides.yaml` to discover which index-file sections are relevant to the story's concern, then follow the key-path references into the index files for project context (falls back to `docs/charter/*.md` for legacy projects).

## Step 1 — Analyse

Read the story. Follow its `traces` links into `docs/spec/*.feature`, `docs/spec/scope-map.md`, and `docs/spec/supplementary_specs/`. Understand:

- What behaviour is being added
- Which system boundaries are involved
- Which Business Rules apply

Record the analysis in the story file under an `## Analysis` section:

- What will be implemented
- Which files will be created or modified
- Which `.feature` Scenarios the tests will cover
- Any concerns or ambiguities

Ask the user: _"Does this analysis look right before I start coding?"_

**Completion**: analysis recorded, user confirms.

## Step 2 — Agree seams

Read `testing.yaml` (at `docs/agent-context/testing.yaml`, falling back to `docs/charter/testing.yaml` for legacy projects) to identify which suite targets the code under test — use its `root`, `pattern`, and `run_all` command. Read the document referenced by `testing_strategy:` for cluster assignment and test budget.

Identify the **seams** — public boundaries where tests observe behaviour. Prefer existing, highest-level seams; fewer seams overall is better.

Ask: _"These are the seams I'll test at: [list]. Do they match your expectations?"_

**Completion**: seams confirmed by the user.

## Step 3 — Red-green loop

Work in **vertical slices** — one test, one implementation, repeat. Each test is a **tracer bullet** that responds to what the last cycle taught you. No horizontal slicing (all tests first, then all code).

Choose **London School** or **Chicago School** as appropriate for the issue.

For each slice:

1. **Red**: write a failing test. The test name references its Use Case ID (e.g. `test_UC_O1_submit_command_happy_path`).
2. **Green**: write the minimum code to pass the test.

Do not refactor during the loop — that belongs to review.

**Completion**: all planned scenarios from step 1 have passing tests, all existing tests still pass.

## Step 4 — Commit

Use **Conventional Commits** (see [commit-conventions.md](../../rulebooks/conventions/commit-conventions.md)):

```bash
git commit -m "feat: <description> (ST-NNNN)"
```

One commit per vertical slice or per full story. Set the story's `status` to `done` when the story is complete.

If invoked with `--no-commit`: stage all changed files, skip the commit, and return. Do not set `status: done`.

**Completion**: committed, story id referenced, `status: done`, all tests pass. With `--no-commit`: all changes staged, all tests pass.

## Step 5 — Check docs

Ask: _"Did implementation reveal any spec gaps, changed Business Rules, or inaccurate interface contracts?"_

If yes, invoke the `spec-feedback` skill. If no, move to the next issue.

**Completion**: spec is either confirmed accurate or updated.
