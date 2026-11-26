---
type: code-review
title: Code review of IMPL-0199, model setup in the first-session handbook
date: 2026-11-26
status: defects
reviewer: code-review-agent
findings_filed: 2
story: IMPL-0199
run:
branch: story/IMPL-0199
branch_base: 56634d75e181cf6320b5b98a9a1b33fd40e06a8a
branch_head: 6dc2ea46e302d15b26d232502169cc1caaa7b9fd
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
