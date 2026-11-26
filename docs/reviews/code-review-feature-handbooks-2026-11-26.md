---
type: code-review
title: Code review of feature/handbooks
date: 2026-11-26
status: defects
reviewer: code-review-agent
findings_filed: 5
run: feature/handbooks
branch: feature/handbooks
branch_base: 43964dac1d1cb6bd933c1f459ead2b39b949c33c
branch_head: c10510333491664d39643d24f7b43e7d579a18f6
---

# Code review of feature/handbooks

## Verdict

The feature fails code review. Four major findings block progression to feature QA. One minor finding remains open.

## Scope

The review covered the merged range for ST-0452 through ST-0458 against the proposal, feature file, validation rules, and QA strategy. It used the story reviews as evidence for story-local checks and inspected how the merged outputs work together. The review considered correctness, architecture, SOLID, maintainability, and consistency.

## Standards

The linter and generator share the page rules. The repository hook checks both handbooks and catches changes that only delete a page. The hook also runs after Markdown formatting, which can change generated text and cause a valid index to fail its byte comparison.

The migrated links outside the factory package follow L-62 and point to source handbook pages. The shipped handbook links also resolve within a separate installed project.

## Spec

The merged feature supplies both handbooks, generated navigation, contributor stubs, a migration map, and the new Help and contributor entry points. Install and update tests compare the installed handbook bytes with the source. The installed guidance gives incorrect steps for adding usage analysis, configuring models after skipping fitting, and finding the updater.

## Verification

`handbook-lint`, `handbook-index --check`, `usage-ui-doc-check`, and `git diff --check` passed. The live Markdown link scan and the installed handbook link scan passed. A scratch test reproduced the formatter changing a generated index that the generator then reported as stale.

The selected handbook, pre-commit, and updater test files returned 331 passes. Four hook tests failed because the default uv cache was read-only. All four passed on retry with a writable offline cache in the review directory. The full repository suite and a live AI Help session were outside this verification.

## Findings

| Finding                                                                               | Artifact                                                                              | Category | Type          | Severity | Basis                                                                                   | Filed as                                              |
| ------------------------------------------------------------------------------------- | ------------------------------------------------------------------------------------- | -------- | ------------- | -------- | --------------------------------------------------------------------------------------- | ----------------------------------------------------- |
| A generated index can fail the commit hook after formatting.                          | `packages/factory/scripts/handbook-index:321-337`                                     | defect   | checking      | major    | `in_use: false`, `harms_downstream: false`, `fails_purpose: true`, `raises_cost: false` | [IMPL-0197](../findings/IMPL-0197.md)                 |
| The installed usage guide omits the source checkout required to add usage.            | `packages/factory/docs/handbook/usage-capture/install-usage-add-on.md:21-27`          | defect   | documentation | major    | `in_use: false`, `harms_downstream: false`, `fails_purpose: true`, `raises_cost: false` | [IMPL-0198](../findings/IMPL-0198.md)                 |
| The first-session tutorial promises model defaults that installation does not supply. | `packages/factory/docs/handbook/getting-started/first-session.md:60-66`               | defect   | documentation | major    | `in_use: false`, `harms_downstream: false`, `fails_purpose: true`, `raises_cost: false` | [IMPL-0199](../findings/IMPL-0199.md)                 |
| The handbook update command requires an undocumented self-install.                    | `packages/factory/docs/handbook/installation-and-updates/update-the-factory.md:21-35` | defect   | documentation | major    | `in_use: false`, `harms_downstream: false`, `fails_purpose: true`, `raises_cost: false` | [IMPL-0200](../findings/IMPL-0200.md)                 |
| The usage health-check instructions name the wrong JSON field.                        | `packages/factory/docs/handbook/usage-capture/install-usage-add-on.md:42-46`          | defect   | documentation | minor    | `in_use: false`, `harms_downstream: false`, `fails_purpose: false`, `raises_cost: true` | [IMPL-0201](../findings/register/code/IMPL-0201.json) |

## Handoff

Fix the four major findings and submit the merged feature for repeat review.
