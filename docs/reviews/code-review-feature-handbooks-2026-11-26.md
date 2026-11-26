---
type: code-review
title: Code review of feature/handbooks
date: 2026-11-26
status: defects
reviewer: code-review-agent
findings_filed: 6
run: feature/handbooks
branch: feature/handbooks
branch_base: 43964dac1d1cb6bd933c1f459ead2b39b949c33c
branch_head: 01342e30dfaedb67112ca639287887d63c5dcdae
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

## Repeat pass

### Verdict

The feature passes the blocking checks. All four pass-1 majors hold on the merged head, and the fixes introduce no blocking defect. One new minor finding remains open beside the pass-1 minor findings that the units left open.

### Scope

The pass reviewed `c1051033..01342e30` at feature level: the five pass-1 findings, and the seams between the fixed pages and the pages and scripts around them. It did not repeat the four unit reviews.

### Pass-1 findings on the merged head

| Finding                                                          | Result            | Evidence                                                                                                                                                                                                                                                                                                                     |
| ---------------------------------------------------------------- | ----------------- | ---------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| IMPL-0197, a generated index can fail the commit hook            | Holds             | `handbook-index` formats its output with mdformat and the gfm extension. `handbook-index --check` and `handbook-lint` exit 0 on the head. A probe list with escapes, emphasis, and a trailing backslash gave the same bytes from the script and from `scripts/mdformat --number`. 73 tests of `test_handbook_index.py` pass. |
| IMPL-0198, the usage guide omits the source checkout             | Holds, with a gap | The handbook page names `--source`. The usage README repeats the old command, filed as [IMPL-0217](../findings/register/code/IMPL-0217.json).                                                                                                                                                                                |
| IMPL-0199, the tutorial promises model defaults                  | Holds             | `init-factory` writes `CONFIGURE-ME` rows per selected CLI, no row for OpenCode, and `on_missing = halt`. `resolve-model` returns a row value as given and applies `on_missing` to every missing pair. `matrix-lint` reports `MX-EMPTY`.                                                                                     |
| IMPL-0200, the update command needs an undocumented self-install | Holds             | `update-factory` documents `--target` as the current directory and reads the source from the manifest. The page, the freshness hook text, and the troubleshooting page agree on the command.                                                                                                                                 |
| IMPL-0201, the health check names the wrong field                | Holds             | `capture_health.py` returns `total_lines`. The handbook page and `packages/usage/README.md` both name it.                                                                                                                                                                                                                    |

### Seams

- The hook runs mdformat with four plugins, and the generator uses only the gfm extension. The probe showed no difference for the constructs the generator can emit.
- The new `mdformat` and `mdformat-gfm` dependencies appear in the inline script header of both scripts and in `pyproject.toml`, so the installed copies and the repository hook resolve the same formatter.
- The freshness row in the local-configuration page matches `check-factory-freshness.sh`: it warns once per session on a missing or different tree hash and exits silently without `packages/factory/`.

### Findings

| Finding                                                               | Artifact                         | Category | Type          | Severity | Basis                                                                                   | Filed as                                              |
| --------------------------------------------------------------------- | -------------------------------- | -------- | ------------- | -------- | --------------------------------------------------------------------------------------- | ----------------------------------------------------- |
| The usage README still gives `--add usage` without a source checkout. | `packages/usage/README.md:25-28` | defect   | documentation | minor    | `in_use: false`, `harms_downstream: false`, `fails_purpose: false`, `raises_cost: true` | [IMPL-0217](../findings/register/code/IMPL-0217.json) |

IMPL-0204 stays open on purpose, as the brief states.

### Verification

`handbook-index --check`, `handbook-lint`, and `tests/factory/test_handbook_index.py` (73 passed) ran read-only on `01342e30`. The full repository suite was not run.

### Handoff

Fix IMPL-0217 when the feature next touches the usage README. The feature may proceed to QA on the feature branch.
