---
type: code-review
title: Code review of IMPL-0199, model setup in the first-session handbook
date: 2026-11-26
status: defects
verdict: Both prior findings resolved. One major and one minor defect remain.
reviewer: code-review-agent
findings_filed: 4
story: IMPL-0199
run:
branch: story/IMPL-0199
branch_base: 56634d75e181cf6320b5b98a9a1b33fd40e06a8a
branch_head: 136b82c0eb0eada1b9aa702ab08d34861fc96561
---

# Code review of IMPL-0199, model setup in the first-session handbook

## Verdict

One major defect blocks the fix for IMPL-0199. One minor defect overstates which CLI selections receive model rows.

## Scope

The review covered the first-session tutorial, the local configuration inventory, and the model matrix reference. The Fix section of IMPL-0199 defines the scope.

## Standards

All three pages retain their handbook types and their existing links. The edits add no binding policy or code dependencies. The phrase “each selected CLI” needs the same qualification across the three pages.

## Spec

The tutorial keeps the option to skip fitting for orientation and tells readers to configure the matrix before model-routed work. Replacing placeholders with valid model IDs fulfills that requirement. The fallback instructions leave a placeholder value in the tier row that dispatch reads.

The reference sample matches the curated Copilot and Pi rows in `packages/factory/config/model.conf`. The new installation guidance correctly includes Claude Code, which receives three placeholders when selected. OpenCode has no installer stanza because its integration is guard-only.

## Verification

The review checked `_generate_model_matrix` for each CLI that the installer accepts. Claude Code, Copilot, Pi, and Codex each produced three placeholders. OpenCode produced zero. All five matrices used `on_missing = halt`.

In scratch, `resolve-model` printed `CONFIGURE-ME` when the matrix contained a placeholder row and `on_missing = auto`. Removing the requested tier row gave empty output with exit 0. The review checked the same precedence in `trigger`. It did not run a full installation or invoke the provider CLI. `git diff --check` passed.

## Findings

| Finding                                                                | Artifact                                                             | Category | Type          | Severity | Basis                                                                                   | Filed as                                              |
| ---------------------------------------------------------------------- | -------------------------------------------------------------------- | -------- | ------------- | -------- | --------------------------------------------------------------------------------------- | ----------------------------------------------------- |
| The tutorial's fallback instructions leave dispatch using CONFIGURE-ME | `packages/factory/docs/handbook/getting-started/first-session.md:65` | defect   | documentation | major    | `in_use: false`, `harms_downstream: false`, `fails_purpose: true`, `raises_cost: false` | [IMPL-0211](../findings/IMPL-0211.md)                 |
| The handbook promises model rows for guard-only OpenCode               | `packages/factory/docs/handbook/reference/model-matrix.md:38`        | defect   | documentation | minor    | `in_use: false`, `harms_downstream: false`, `fails_purpose: false`, `raises_cost: true` | [IMPL-0212](../findings/register/code/IMPL-0212.json) |

## Repeat pass

**Verdict.** The fix resolves both prior findings. One major defect blocks approval. The repeat pass files two new findings.

The review covered `56634d75..136b82c0` and checked the repeat fix in `f1decb72..136b82c0`. The first-session tutorial still lets readers skip fitting for orientation. Its setup instructions now reflect the generated matrix, with the two fallback issues below. The inventory accurately describes the generated file. The reference keeps the curated example and the documented fallback rules. The handbook edits add no code dependencies or responsibility changes. The three pages agree on which CLIs receive model rows.

| Prior finding | Status   | Verification                                                                                                                                                                                                                                                                                                                                |
| ------------- | -------- | ------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| IMPL-0211     | Resolved | The tutorial now directs readers to delete the requested tier row and set `on_missing = auto`. In scratch, the placeholder resolved to `CONFIGURE-ME` before deletion. After deletion, the resolver exited 0 with empty output. The reference describes the missing-row condition and reports `MX-EMPTY` for a matrix with zero model rows. |
| IMPL-0212     | Resolved | All three pages exclude OpenCode from the installer claim. The generator wrote three placeholder rows each for Claude Code, Copilot, Pi, and Codex. It wrote zero rows for OpenCode and set `on_missing = halt` in all five cases.                                                                                                          |

The scratch probe also checked a matrix with two missing rows. Under `auto`, both used the default and `matrix-lint` returned two `MX-COVERAGE` warnings with exit 0. With no model rows, the resolver still exited 0 and the linter reported `MX-EMPTY` with exit 1. That test covered a matrix with `[facts]` and `on_missing = auto`. The review read the dispatch command builder and ran the generator and resolver directly. It did not run a full installation or launch a provider CLI. `handbook-lint` and `git diff --check` passed.

| Finding                                                                        | Category | Type          | Severity | Basis                                                                                   | Filed as                                              | Edge case created by the fix                                        |
| ------------------------------------------------------------------------------ | -------- | ------------- | -------- | --------------------------------------------------------------------------------------- | ----------------------------------------------------- | ------------------------------------------------------------------- |
| The fallback instructions also enable dispatch for tiers deliberately left out | defect   | documentation | major    | `in_use: false`, `harms_downstream: false`, `fails_purpose: true`, `raises_cost: false` | [IMPL-0213](../findings/IMPL-0213.md)                 | Yes. The new procedure changes the fallback for other missing rows. |
| The tutorial's fallback instructions can leave a matrix that fails validation  | defect   | documentation | minor    | `in_use: false`, `harms_downstream: false`, `fails_purpose: false`, `raises_cost: true` | [IMPL-0214](../findings/register/code/IMPL-0214.json) | Yes. The new procedure lets readers delete the last model row.      |
