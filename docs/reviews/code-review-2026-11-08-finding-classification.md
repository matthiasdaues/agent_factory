---
type: code-review
title: Code review of the finding-classification implementation
date: 2026-11-08
status: defects
reviewer: code-review-agent
findings_filed: 5
branch: feature/finding-classification
branch_base: 2e4cd6fb975db9b1bffbfab56696284ebbe66c68
branch_head: b2bd24a1ac5f05eef935135d5c957ec318c452e3
---

# Code review of the finding-classification implementation

## Result

The review found three major defects and two minor ones. None of them is in use, so none is critical. All three major defects let a human field or a stop slip past a gate that exists to hold it.

1. A commit that only deletes a finding file skips `finding-lint`, so it can end a stop.
2. `guard-human-fields` passes a shell write when the path stands in a heredoc or when the writing command is not the first word.
3. The Pi extension does not guard `write_file` and `create`.

The severity rules, the `in_use` git check, the HEAD comparison, the stop in `dispatch` and `premerge-check`, `next-id`, the OpenCode install, and the text of the agents, skills, and playbooks hold.

Next, the Implementation Agent fixes IMPL-0014, IMPL-0015, and IMPL-0016 and submits the branch for review again. The branch is not ready for reconciliation.

## Scope

The review covers `git diff dev...feature/finding-classification` at `b2bd24a1`, limited to `packages/factory/scripts/`, `config/`, `agents/`, `playbooks/`, `skills/`, `rulebooks/`, and `tests/factory/`. It checked them against `docs/spec/features/finding-classification.feature`, BR-079 to BR-095, BR-109, BR-110, and the contracts of `finding-lint` and `guard-human-fields` in `docs/spec/interface-contracts.md`. The classification follows `finding-classification.md`, code class.

The review read these in full: `finding-lint`, `guard-human-fields`, the Pi extension, the OpenCode plugin, the rulebook, `finding-format.md`, `report-format.md`, and the diffs of `dispatch`, `dispatch_lib.py`, `next-id`, `premerge-check`, `remove-factory`, `init-factory`, the hook configuration, and the agent, skill, playbook, and template text.

The review ran these:

- Twelve test modules of the feature. The first six are `test_finding_lint`, `test_finding_stop`, `test_guard_human_fields`, `test_finding_register`, `test_finding_classification_text`, and `test_precommit_config_contract`, with 518 tests. The other six are `test_finding_lint_git`, `test_finding_loop_grep`, `test_findings_repository`, `test_next_id_plan_seed`, `test_init_factory`, and `test_update_factory`, with 436 tests. All tests pass.
- `finding-lint` on the branch before and after filing, with exit 0 both times.
- `init-factory --cli opencode` in a temporary project. The plugin link was created. The run stopped at the prompt for the project name, so the install itself did not finish.
- The reproductions that IMPL-0014, IMPL-0015, and IMPL-0018 describe.

## Not checked

- The review did not read the test modules line by line. It searched them for named cases and ran the twelve modules above. The TypeScript tests did not run, and neither did the three smaller changed Python modules `test_block_dangerous_git`, `test_core_artifact_ownership_text`, and `test_hook_missing_factory`, or `test_structure_gates`.
- The review did not run a Pi, Codex, Copilot CLI, or OpenCode session. FC-QG23 and FC-QG24 hold that work.
- One case stays open and needs a real Pi session. A Pi child agent runs in a linked worktree, and `.agent-factory/` exists only in the main checkout. If the child loads the project-local extensions, `guard-human-fields.ts` finds no guard script and blocks every edit, write, and shell call. A session that spawns `dispatch-wave` settles the question. `finding-lint` solves the same problem with `_main_checkout.py`.

## Prior findings

No `IMPL` finding file is open. The open register files IMPL-0007, IMPL-0011, IMPL-0012, and IMPL-0013 are `minor` findings of earlier features and lie outside this diff, so this pass did not verify them.

## Findings

| Finding                                                                                                                                                                                                                                      | Artifact                                                                                | Category   | Severity | Filed as    |
| -------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- | --------------------------------------------------------------------------------------- | ---------- | -------- | ----------- |
| A commit that only deletes a finding file or a register file skips `finding-lint`, because pre-commit leaves deleted paths out of the list that `files:` filters. Replace `files:` with `always_run: true`.                                  | `packages/factory/config/pre-commit-config.yaml:172-183`                                | Defect     | major    | IMPL-0014   |
| The guard passes a shell write when the path stands in a heredoc body or when the writing command is not the first word. Read the heredoc body of an interpreter and skip leading shell keywords and wrappers.                               | `packages/factory/config/hooks/guard-human-fields:359-398`                              | Defect     | major    | IMPL-0015   |
| The Pi extension leaves `write_file` and `create` unguarded, and the contract names both. Add them to `GUARDED_TOOLS` and test them.                                                                                                         | `packages/factory/config/extensions/guard-human-fields.ts:10`                           | Defect     | major    | IMPL-0016   |
| A marker written before a stop stays valid during the stop, so a merge of the same head passes. Add the stop check to `block-dangerous-git.sh`, or change BR-091 so that the refusal removes the marker.                                     | `packages/factory/scripts/premerge-check:393-398`                                       | Defect     | minor    | IMPL-0017   |
| `finding-lint` and `dispatch_lib` parse a finding separately and disagree on a `* ` bullet and on `Null`. Move the parsing into one module.                                                                                                  | `packages/factory/scripts/dispatch_lib.py:1760-1899`                                    | Defect     | minor    | IMPL-0018   |
| The calibration tables of the rulebook link finding files of this repository. In an installed project, those links lead nowhere. The examples are complete without the link, so a reader can still act on them, and nothing needs to change. | `packages/factory/rulebooks/conventions/finding-classification.md#calibration-examples` | Suggestion | note     | report only |

The owner of IMPL-0017 and IMPL-0018 is `developer-agent`. A register file has no `owner:` key, so this report names the agent.

## New register files

This run had no pause point before filing, because the stakeholder was not present. So a wrong downgrade can reach implementation. The stakeholder can check each sentence here and raise a finding by changing an answer of its basis.

- IMPL-0017, class `code`, `packages/factory/scripts/premerge-check:393-398`: Every premerge-check during the stop refuses and writes no marker, and a new branch head has no valid marker, so the stop holds on the normal path (no to fails_purpose). A merge passes only when the finding arrives between a passing premerge-check and the merge of the same head, and then the operator must find and reverse that merge.
- IMPL-0018, class `code`, `packages/factory/scripts/dispatch_lib.py:1760-1899`: mdformat writes every bullet as `- ` and the template writes the human fields as null, so real files give the same result in both parsers (no to fails_purpose). Each later change of the finding format must be made in two places that already disagree, which is a duplicated rule.
