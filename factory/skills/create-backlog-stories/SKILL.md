---
name: create-backlog-stories
description: "Read confirmed slice tables, write backlog/ST-NNNN.md story files with MoSCoW priorities, dependencies, and quality gates. Phase 4 of 4 in the create-backlog sequence."
category: planning
inputs:
  - docs/charter/testing.yaml
disable-model-invocation: false
---

# Create Backlog — Phase 4: Write Stories

Write story files from confirmed slice tables, validate, and present the final backlog. This is phase 4 of the [create-backlog sequence](../create-backlog/SKILL.md#operational-sequence). Story format, composition rules, and the done check live in the [parent skill](../create-backlog/SKILL.md).

**Prerequisite:** story-level slice tables have been confirmed by the user (output of [`create-backlog-story-slices`](../create-backlog-story-slices/SKILL.md)).

## Step 2 — Break EPICs into User Stories

For each EPIC, create `backlog/ST-NNNN.md` stories meeting **INVEST** — particularly: Independent (dependencies explicit in `deps`), Small (one implementation session), Testable (acceptance criteria as falsifiable invariants).

Apply the [story composition rules](../create-backlog/SKILL.md#story-composition-rules): write the Demo section first (Rule 1), define scope as a step forward from the status quo of depended-on stories (Rule 2), write acceptance criteria as invariants (Rule 3). Every story is a vertical slice that crosses all system boundaries its capability requires. A story that touches only one boundary (only schema, only service, only UI) and delivers nothing a person can demonstrate is not a story — fold it into the first story that needs it as a line item.

Each story records in `traces`: Use Case ID(s) it implements (e.g. `UC-01`, `UC-A2`), the arc42 component(s) it touches, and any constraining ADR(s).

Judge each story's `tier` (`economy | standard | strong`) — the model strength its work needs, same vocabulary as agent frontmatter's `tier`.

When charter files exist, extract concrete implementation names (test framework, deployment target, API framework) and use them in acceptance criteria instead of placeholders.

For each story, cross-reference against the testing regime:

1. Read `docs/charter/testing.yaml` and its `suites` list.
2. For each suite, scan the suite's `root` directory for files matching its `pattern`.
3. Compare discovered test files against the story's acceptance criteria — by filename, test function names, and docstrings where available.
4. When pre-existing tests match, record their file paths in the story's `tests:` field.
5. When no existing test covers a criterion, record the target suite for new tests in the story's Notes for the Implementer section (e.g. "New tests target the `backend` suite under `packages/server/backend/tests`").
6. Read the document referenced by `testing_strategy:` in `docs/charter/testing.yaml` to determine cluster assignment and test budget for the story.

See the [story template](../../rulebooks/templates/story.md) for the complete frontmatter schema and body structure.

Format each story file via `factory/scripts/mdformat --number <path>` per [markdown-formatting.md](../../rulebooks/conventions/markdown-formatting.md).

## Step 3 — Prioritise with MoSCoW

Record each story's **MoSCoW** priority in its body: `**Priority:** must-have | should-have | could-have | wont-have`.

## Step 4 — Mark dependencies

List blocking stories in `deps` (by `ST-NNNN` id). Run `factory/scripts/backlog-lint --backlog-dir backlog` — it checks acyclicity — and fix any errors.

## Quality gate

Review every story through two lenses:

**Junior Clarity:** Read the story as a junior developer. Can you start working right now — do you know which file to open first, what the first test asserts, and what "done" looks like? If not, the story is underspecified.

**Senior Acceptance:** Read the story as a senior grooming the backlog. Would you hand this to your team without a follow-up conversation — is the scope bounded, the demo concrete, every criterion testable, and nothing left to interpret? If not, the story is not ready.

Present the complete backlog to the user. Ask:

- _"Are the MoSCoW priorities correct?"_
- _"Any missing stories?"_
- _"Should any dependencies be reordered?"_

## This skill ends here

The backlog is written and validated. Run the [done check](../create-backlog/SKILL.md#done-check) to verify completeness. The user confirms the backlog, then the planning agent commits to `dev` and hands off to the implementation agent.
