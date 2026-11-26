---
type: code-review
title: Code review of IMPL-0200, factory update documentation
date: 2026-11-26
status: defects
reviewer: code-review-agent
findings_filed: 1
story: IMPL-0200
run:
branch: story/IMPL-0200
branch_base: a73338e8be56195a5a55ec24ebc06290208b1288
branch_head: 3fc2b76ccc296cc3cfa799d7a65726e0c18998db
---

# Code review of IMPL-0200, factory update documentation

## Verdict

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
