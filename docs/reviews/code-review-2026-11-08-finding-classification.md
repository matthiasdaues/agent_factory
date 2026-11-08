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

## Pass 2

### Result of pass 2

Both fixes hold, so IMPL-0015 and IMPL-0016 stay `resolved`. This pass adds no blocking finding. It adds one `minor` finding, IMPL-0019, and five `note` findings.

IMPL-0014 is with the stakeholder, and this pass did not review it. Reconciliation waits only on that decision.

### Scope of pass 2

This pass covers the commits `34719f65` (IMPL-0016, Pi extension) and `2a20afc7` (IMPL-0015, `guard-human-fields`). It checks them against the Refuses and Passes rows of the guard contract in `docs/spec/interface-contracts.md`, against BR-092, and against the Fix line of each finding. The classification follows `finding-classification.md`, code class.

### What the pass ran

The pass sent real payloads to the guard in a temporary git project and read the exit code of each call.

| Group                                                                                                                         | Calls | Result                                                                 |
| ----------------------------------------------------------------------------------------------------------------------------- | ----- | ---------------------------------------------------------------------- |
| The eight commands that IMPL-0015 lists                                                                                       | 8     | All exit 2                                                             |
| The leading words of the Fix: `do`, `else`, `!`, `command`, `time`, `sudo`                                                    | 6     | All exit 2                                                             |
| More heredoc forms: `<<-`, `perl`, `node`, `sh`, after `env`, after `&&`, a register file, and a proposal                     | 10    | All exit 2                                                             |
| Passing cases of the contract: read-only `grep`, fixture heredocs through `cat`, `python3`, and `bash`, the template, an edit | 13    | 12 exit 0 as expected. The other one is IMPL-0019                      |
| `write_file` and `create`, in the `tool_name` format and in the `toolName` and `input` format of Pi                           | 7     | A human value gives exit 2, and a new finding without one gives exit 0 |

The test file `packages/factory/config/extensions/__tests__/guard-human-fields.test.ts` ran with 20 tests, and all 20 pass.

### Not checked in pass 2

`tests/factory/test_guard_human_fields.py` did not run. A hook of this session denies `python3 -m pytest` and `uv run pytest`, and the pass did not go around it. The pass sent the thirteen forms that the commit adds to the guard by hand instead, and each gave the expected exit code. Someone must run the module before the merge. No Pi session ran, so the case that pass 1 left open about a linked worktree stays open.

### Prior findings of pass 2

| Finding   | Verdict                                                                                                                                                                                                                 |
| --------- | ----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| IMPL-0015 | Fixed. Each row of the finding gives the required exit code, `<<<` no longer starts a heredoc, and a fixture heredoc passes. Each row has a test or an existing test.                                                   |
| IMPL-0016 | Fixed. `GUARDED_TOOLS` holds the six calls of the Pi row in the contract, and the guard script refuses a human value for `write_file` and `create`. The test file has one case per name for each of the three outcomes. |

### Findings of pass 2

The brief of this pass limits a shell form outside the list of IMPL-0015 and outside the contract to a `note`. The first two rows below stand at `note` for that reason. Without the limit, the first row would need a decision, because the docstring of the guard says that the guard follows each literal `cd`.

| Finding                                                                                                                                                                                                                                                                                                                                                                     | Artifact                                                   | Category   | Severity | Filed as    |
| --------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- | ---------------------------------------------------------- | ---------- | -------- | ----------- |
| A shell write of a new finding with blank human fields is refused, because the gap after the colon crosses a line break. Commit `2a20afc7` extends the refusal to a Python heredoc. Replace `\s*` with `[ \t]*` in `SHELL_FIELD` and exclude a backslash and `#` from the value.                                                                                            | `packages/factory/config/hooks/guard-human-fields:77-79`   | Defect     | minor    | IMPL-0019   |
| The new forms do not follow a `cd`. `cd docs/findings && python3 - <<'PY'` with a relative path in the body gives exit 0, and the same script through `python3 -c` gives exit 2. `shell_write_targets` reads the heredocs before it walks the `cd` commands. `then cd docs/findings; sed -i ...` also gives exit 0, because the `cd` check reads the first word only.       | `packages/factory/config/hooks/guard-human-fields:335-347` | Defect     | note     | report only |
| These forms still give exit 0, and none of them stands in the list of IMPL-0015: an unterminated heredoc, `cat <<'PY' \| python3 -`, `bash <<<`, `if` and `while` before the writer, `sudo -u`, `env -i`, `xargs`, a line continuation before the heredoc, `<<` inside a quote on an earlier line, and two heredocs on one line.                                            | `packages/factory/config/hooks/guard-human-fields:366-442` | Defect     | note     | report only |
| A Python heredoc whose body names a project-relative guarded path and a human value is refused, also when it only reads the file or writes under a temporary directory. Those calls went from exit 0 to exit 2. `python3 -c` behaves the same, and the Fix of IMPL-0015 asks for it. A fixture heredoc whose body names no guarded path passes, as the Passes row requires. | `packages/factory/config/hooks/guard-human-fields:437-438` | Suggestion | note     | report only |
| `_heredoc_script_targets` repeats the lexer setup and the loop over leading words of `shell_write_targets` and `_simple_targets`. The words stand in one constant, `WRAPPERS`, so a new word changes one place, and nothing needs to change now.                                                                                                                            | `packages/factory/config/hooks/guard-human-fields:418-442` | Suggestion | note     | report only |
| The word `else` has no test. The Fix asks for a test per row of its list, and `else` is not such a row. The guard refuses it, as the first table of this pass shows.                                                                                                                                                                                                        | `tests/factory/test_guard_human_fields.py:238-262`         | Suggestion | note     | report only |

### New register file of pass 2

This run had no pause point before filing, because the stakeholder was not present. The stakeholder can check the sentence here and raise the finding by changing an answer of its basis. The owner is `developer-agent`.

- IMPL-0019, class `code`, `packages/factory/config/hooks/guard-human-fields:77-79`: The guard still refuses every human value, the literal null that the Passes row names goes through in every form, and a Write call takes the blank fields (no to fails_purpose). An agent that files through the shell gets a message that names a field it did not set, and must file again with a Write call.
