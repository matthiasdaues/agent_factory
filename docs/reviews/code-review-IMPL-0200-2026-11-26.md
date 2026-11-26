---
type: code-review
title: Code review of IMPL-0200, factory update documentation
date: 2026-11-26
status: defects
reviewer: code-review-agent
findings_filed: 2
story: IMPL-0200
run:
branch: story/IMPL-0200
branch_base: a73338e8be56195a5a55ec24ebc06290208b1288
branch_head: a73df13847597ff81721fb46cbd7576162dec95e
---

# Code review of IMPL-0200, factory update documentation

## Verdict

Repeat pass requires a fix for [IMPL-0216](../findings/IMPL-0216.md). IMPL-0215 is resolved.

### Pass 1 verdict

One major documentation defect blocks the review.

## Scope

The review covered both changed handbook pages against the Fix section of IMPL-0200. It checked the commands against the installed updater and checked the freshness row against the shell hook and Pi extension.

## Standards

The update page remains a how-to, and the configuration inventory remains a reference. The link stays within the installed handbook. The diff adds no binding rules or code dependencies.

## Spec

The installed updater runs from the target project root, as the package README shows. It defaults to the current directory and uses the checkout recorded in `factory_source` for local installs. The explicit `--source` example selects the supplied checkout. The freshness row links to the how-to but leaves out the condition that limits the warning to the source checkout.

## Verification

`handbook-lint`, `handbook-index --check`, the link check for both changed pages, and `git diff --check` passed. In a scratch Claude installation, both documented updater commands displayed the source, installed version, candidate version, and planned effects. The probe declined both prompts before the update. The installed freshness hook exited 0 with empty stdout and stderr when the project lacked `packages/factory/` and the recorded tree hash was set to zeros.

## Findings

| Finding                                                                    | Artifact                                                             | Category | Type          | Severity | Basis                                                                                   | Filed as                              |
| -------------------------------------------------------------------------- | -------------------------------------------------------------------- | -------- | ------------- | -------- | --------------------------------------------------------------------------------------- | ------------------------------------- |
| The freshness row promises a warning that consumer projects never receive. | `packages/factory/docs/handbook/reference/local-configuration.md:49` | defect   | documentation | major    | `in_use: false`, `harms_downstream: false`, `fails_purpose: true`, `raises_cost: false` | [IMPL-0215](../findings/IMPL-0215.md) |

## Repeat pass

The repeat pass reviewed `a73338e8..a73df138` and checked the IMPL-0215 fix in `654e49b4..a73df138`. The later range changes the freshness row and its table spacing.

The update how-to runs the installed updater from the project root, consistent with the package README. The reference links to that procedure and describes a warning. Both pages keep their documented page types. They add no binding rules. The diff changes no runtime interfaces, dependencies, or responsibilities. The review also checked the prior finding and report against the same scoped diff.

[IMPL-0215](../findings/IMPL-0215.md) is resolved. Both checks return silently when the project lacks `packages/factory/`. The revised row states that condition.

### Verification

In a scratch Git repository, the shell hook and the Pi extension callback each ran twice per case. Both were silent for a matching hash and an absent source directory. Both printed the update command once per case for a mismatched, missing, or null hash. The probe called the Pi callback directly. The updater commands were checked against the README and updater source in this pass.

The local link check for both pages and `git diff --check` passed. The handbook lint and index checks could not run to completion. The default uv cache was read-only, and system Python lacked the mdformat GFM extension.

### New findings

| Finding                                                                                                                            | Artifact                                                             | Category | Type          | Severity | Basis                                                                                   | Filed as                              |
| ---------------------------------------------------------------------------------------------------------------------------------- | -------------------------------------------------------------------- | -------- | ------------- | -------- | --------------------------------------------------------------------------------------- | ------------------------------------- |
| The freshness row omits the warning for an install with no recorded tree hash. This is an edge case introduced by the new wording. | `packages/factory/docs/handbook/reference/local-configuration.md:49` | defect   | documentation | major    | `in_use: false`, `harms_downstream: false`, `fails_purpose: true`, `raises_cost: false` | [IMPL-0216](../findings/IMPL-0216.md) |
