---
name: spec-feedback
description: Check whether specification or architecture drifted after implementation reveals gaps, changed rules, or inaccurate contracts, and write each drift as a row of the story's spec-feedback report. Use when the user mentions spec drift, docs are stale, or implementation contradicts the spec.
category: implementation
---

# Spec Feedback

After implementing one or more issues, check whether the specification or architecture documentation has drifted from reality. The spec is not throwaway — it remains the authoritative description of system behaviour. This skill changes no specification file. It records each drift for the artifact's owner.

Read [factory-voice.md](../../rulebooks/conventions/factory-voice.md) now and hold every rule as a writing constraint. No prose reaches terminal output or a file until it passes all four gates and clears the final pass.

## Step 1 — Detect drift

Read the recently changed code (use `git diff` against the last spec-aligned commit). Compare against:

- `docs/spec/features/*.feature` — do the Gherkin Scenarios still match?
- `docs/spec/entity-model.md` — any new entities, changed attributes, or relationships?
- `docs/spec/state-machines.md` — any new states or transitions?
- `docs/spec/interface-contracts.md` — do DTOs and schemas match the code?
- `docs/spec/validation-rules.md` — any new or changed rules?
- `docs/` (arc42 chapters) — any new components, changed boundaries, or deployment changes?

List every discrepancy.

**Completion**: every spec file checked against the implementation, all discrepancies listed.

## Step 2 — Write a row

Write each discrepancy as a row of `docs/spec/work/spec-feedback-<story-id>.md`. `<story-id>` is the ID of the story you implement, such as `ST-0318`. Change no specification file. The owner of the artifact fixes it after the story merges, and the owner's reviewer checks the fix.

Each story has its own report, because the developer agents of a wave run in parallel. Write only into the report of your own story. Create the report with its first row. A story without drift has no report.

The report holds one table with these columns:

| Artifact                        | Drift                                                                                        | Evidence                         | Owner                   | Status |
| ------------------------------- | -------------------------------------------------------------------------------------------- | -------------------------------- | ----------------------- | ------ |
| `docs/spec/validation-rules.md` | The migration script must refuse a repository with uncommitted changes, and no rule says so. | `scripts/migrate-spec-layout:88` | `domain-modeling-agent` | `open` |

- **Artifact:** the path of the artifact that drifted.
- **Drift:** the mismatch between the artifact and the code, in one sentence.
- **Evidence:** the code path and line that show the mismatch.
- **Owner:** the producer of the artifact, read from the output declarations in `INDEX.yaml`. For `docs/spec/validation-rules.md` the owner is `domain-modeling-agent`. For a QA strategy the owner is `test-strategy-agent`.
- **Status:** Set the status to `open`. The owner sets `fixed` after it changed the artifact. The owner's reviewer sets `confirmed` or `rejected`.

Format the report via `scripts/mdformat --number <path>` per [markdown-formatting.md](../../rulebooks/conventions/markdown-formatting.md).

**Completion**: every discrepancy is a row with status `open` in the story's report, and no specification file changed.

## Step 3 — Report

Summarise the rows for the caller: one bullet per row, with its Artifact and Owner. The report travels with the story's changes and follows the caller's commit mode.

**Completion**: summary written, report saved with the story's changes.
