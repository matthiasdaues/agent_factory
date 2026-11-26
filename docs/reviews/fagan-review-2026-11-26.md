---
type: fagan-review
title: Fagan review of feature/handbooks
date: 2026-11-26
status: pass
reviewer: qa-agent
findings_filed: 1
story:
run: feature/handbooks
branch: feature/handbooks
branch_base: 43964dac1d1cb6bd933c1f459ead2b39b949c33c
branch_head: f1c6a265def3184eb7c938631af3783b6a85f14d
---

# Fagan review of feature/handbooks

## Verdict

The feature passes the Fagan inspection. It has no blocking finding and one minor finding, FAGAN-0036. The two scripts follow BR-140 to BR-146, and the repository hook runs them after the formatter without a mismatch.

## Scope

The review covers `git diff 43964dac..f1c6a265` for `packages/factory/scripts/handbook-index`, `handbook-lint`, the section-map part of `_link_rewrite.py`, the hook in `.pre-commit-config.yaml`, and the tests `tests/factory/test_handbook_*.py` and `test_precommit_config_contract.py`. It read BR-140 to BR-152, the proposal, and the feature file. It repeats nothing of [the code review](code-review-feature-handbooks-2026-11-26.md). IMPL-0204 and IMPL-0217 stay as the known minors. The 241 tests of the handbook, hook, and link files pass.

## Focus areas

| Area               | Result                                                                                                                                                                                                                                                                                                                                                      |
| ------------------ | ----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| Correctness        | BR-140 to BR-146 hold on the cases tried: odd titles, page names with spaces, percent signs, and umlauts, stub-only chapters, and an empty page list. The generated list is a fixed point of the repository mdformat, also for a title with a bracket, a pipe, or a comment opener. The gaps are filed as BUG-0154, BUG-0155, and BUG-0157 in the bug hunt. |
| Clean Architecture | `handbook-lint` imports the rules of `handbook-index` and adds the layout and title checks. The dependency runs one way. The loader of a hyphenated sibling script follows the pattern of seven other scripts.                                                                                                                                              |
| SOLID              | `parse_page`, the readers, the planners, and the writer are separate functions. No violation with a concrete cost.                                                                                                                                                                                                                                          |
| Maintainability    | `_read_folder` and `_check_below` repeat one loop, with a `deep` flag. That costs little at 20 lines each. The section map of `_link_rewrite.py` has no caller outside the tests (FAGAN-0036).                                                                                                                                                              |
| Consistency        | Failure lines, exit codes, and the `uv run --script` header follow the other lint scripts. The hook has no `stages` key, as `spec-lint` and `backlog-lint` have none.                                                                                                                                                                                       |

## Checks of the QA agent definition

| Check             | Result                                                                                                                                                                                   |
| ----------------- | ---------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| Acceptance test   | The feature file has no Gherkin runner. The scenarios run as the tests that carry the `FH-` marks, and all selected files pass.                                                          |
| Test-design pass  | The stories are governed by the feature file, so the field `test-design-pass` does not apply.                                                                                            |
| Contract to test  | Each contract of BR-140 to BR-148 has a test in `test_handbook_index.py`, `test_handbook_lint.py`, or `test_precommit_config_contract.py`. No test covers a write that fails (BUG-0155). |
| Testability flags | No red flag for these stories stands open in `backlog/epics.md`.                                                                                                                         |
| YAGNI             | One finding: the section-map code of the finished migration (FAGAN-0036). The `order` default, the symlink refusal, and the deep check below a chapter each serve a named rule.          |

## Findings

| Finding                                                                                                                                                                                                       | Artifact                                            | Category   | Type      | Severity | Basis                                                                                   | Filed as                                                |
| ------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- | --------------------------------------------------- | ---------- | --------- | -------- | --------------------------------------------------------------------------------------- | ------------------------------------------------------- |
| The section map of the finished migration has no caller outside the tests, and its guard tests read a work file and a deleted commit. Move the code and its tests out of the shared module after the release. | `packages/factory/scripts/_link_rewrite.py:227-569` | suggestion | structure | minor    | `in_use: false`, `harms_downstream: false`, `fails_purpose: false`, `raises_cost: true` | [FAGAN-0036](../findings/register/code/FAGAN-0036.json) |

## Notes

- N-1: `layout_failures` sets `holds_page = chapter.has_index or chapter.pages or chapter.page_failures` and then tests `not chapter.has_index`. The first operand is redundant.
- N-2: `_root_uninspectable` of `handbook-lint` infers a failed read from the path strings of failures. A flag on `Folder` would state it directly. It works today.
- N-3: `run` computes the planned lists twice in write mode, once for `stale_lists` and once for writing. Each run takes 0.3 s, so the cost is irrelevant.

## Next step

No change blocks the feature. The Implementation Agent may fix FAGAN-0036 after the release.
