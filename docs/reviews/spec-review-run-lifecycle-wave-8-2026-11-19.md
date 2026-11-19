---
type: inspect-spec
title: Spec review of the run-lifecycle wave-8 close
date: 2026-11-19
status: defects
reviewer: spec-review-agent
findings_filed: 2
story: run-lifecycle
scope: The specification changes of d71c2eb5..072cd152 on feature/run-lifecycle, read against packages/factory/scripts/mutation-testing, premerge-check and skills/mutation-testing/SKILL.md at d71c2eb5
---

# Spec review of the run-lifecycle wave-8 close

The wave-8 specification changes do not pass yet, because one major finding blocks. § Gate result files, BR-066, and the renamed CAO-12 Rule agree with each other, with RL-12, and with the code that ST-0423 built. The code under `packages/` did not change after `d71c2eb5`. One older statement in the interface contracts now contradicts the new BR-066:

- SPEC-0120, major: the Gates pass row of `premerge-check` still lists the old conditions of a pass. Under that row, a survivor with `resolution_action: none-required` passes, while BR-066 and the code fail it. The domain-modeling agent adds the missing condition.

One minor finding is a register file:

- SPEC-0121: the CAO-12 row of the core-artifact-ownership QA strategy still gives every filed mutant the test-strategy agent as owner. The test-strategy agent changes the cell to the owner that follows the cause.

This review confirms all three `fixed` rows on core artifacts in `spec-feedback-ST-0423.md` and rejects none.

Spec review is the `document` class. The code of the wave lives on `feature/run-lifecycle`, the run's own workspace, and no story or code outside the run encodes the reviewed statements. So every finding answers `in_use: false`. The caller dispatched this review without the stakeholder, so the review filed the findings without the pause point. The stakeholder sees them first in this report.

Two known items are out of scope and have no finding:

- IMPL-0058 and IMPL-0059 are follow-up stories.
- Two design questions go to the stakeholder after the run. The first asks how the test-strategy agent resolves a mutant that no test should kill. The second asks whether a `planning-agent` QA finding may also close through a story that adds the test.

## Reviewed specification

- The diff `git diff d71c2eb5..072cd152`, from the commits `383abb1d` (domain modeling) and `072cd152` (requirements).
- `docs/spec/interface-contracts.md`: § Gate result files with its two tables, and the Gates pass row of the `premerge-check` Story merge table.
- `docs/spec/validation-rules.md`: BR-066, read with BR-121.
- `docs/spec/features/core-artifact-ownership.feature`: the Rule CAO-12 with its five Scenarios and its comment, and the test guardrails Scenario at line 516.
- `docs/spec/features/run-lifecycle.feature`: RL-12, the Outline "The gate-check step files a blocking QA finding for a mutant it cannot resolve" and the three Scenarios after it.
- Every reference to the CAO-12 Rule: `docs/spec/scope-map.md`, `docs/spec/work/core-artifact-ownership-gaps.md`, `docs/spec/work/run-lifecycle-gaps.md`, `docs/spec/work/core-artifact-ownership-qa-strategy.md`, `backlog/ST-0358.md`, and `backlog/epics-core-artifact-ownership.md`.
- `docs/spec/work/spec-feedback-ST-0423.md`.
- The code: `_entry_problem`, `judge`, `evaluate`, and `run_gate` in `packages/factory/scripts/mutation-testing`. In `packages/factory/scripts/premerge-check`: `stored_mutation_result`, `read_gate_result`, `judge_mutation_result`, `mutation_rerun_result`, and the rerun of the gate. `packages/factory/skills/mutation-testing/SKILL.md`: the three actions, the filing of a `QA` finding, the owner table, and the report format. The core list is `packages/factory/rulebooks/core-artifacts.yaml`.
- `docs/spec/scope-map.md`, read only.

`spec-lint --spec-dir docs/spec`: `spec-lint: 0 error(s), 0 warning(s), 57 info across 105 spec file(s).`

## Deterministic findings

| Rule     | Subject                                                              | Verdict                                                                           |
| -------- | -------------------------------------------------------------------- | --------------------------------------------------------------------------------- |
| GLOSS001 | Glossary terms that no spec file uses, such as Workstream Resolver   | Dismissed. None is a run lifecycle term, and the skill files no such case.        |
| TODO001  | Open items in `docs/spec/work/todo.md` and `docs/spec/work/todos.md` | Dismissed. No item concerns the reviewed range.                                   |
| TRACE003 | BR-011 to BR-054 defined but never referenced                        | Dismissed. BR-066 is referenced, and the rest is older.                           |
| TRACE004 | `EPIC_BUILDING_BLOCK` in a relationship without an attribute block   | Dismissed. The entity belongs to the test-design entities, outside of this range. |

## Semantic findings

| ID        | Severity | Category | Type         | Characteristic | Artifact                                                   | Finding                                                                                                                                                                                            | Acted on by           |
| --------- | -------- | -------- | ------------ | -------------- | ---------------------------------------------------------- | -------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- | --------------------- |
| SPEC-0120 | major    | defect   | inconsistent | Consistent     | `docs/spec/interface-contracts.md:64`                      | The Gates pass row lists the conditions of a pass without "every survivor has one of the three actions". A survivor with `none-required` passes under the row and fails under BR-066 and the code. | domain-modeling-agent |
| SPEC-0121 | minor    | defect   | inconsistent | Consistent     | `docs/spec/work/core-artifact-ownership-qa-strategy.md:84` | The CAO-12 row says that a filed mutant gets the test-strategy agent as owner. The renamed Rule, RL-12, and the skill let the owner follow the cause.                                              | test-strategy-agent   |

Four notes stay rows of this report and need no change now:

| Note                                                                                                                                                                                                                                                                                          | Artifact                                                 | Severity |
| --------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- | -------------------------------------------------------- | -------- |
| The renamed Rule names the goals of two actors, the test-strategy agent and the planning agent, while its actor comment names only the test-strategy agent. The second design question of the stakeholder may move the planning agent's part to a Rule of its own.                            | `docs/spec/features/core-artifact-ownership.feature:574` | note     |
| The skill says that the gate-check step writes the list into the result file of the invocation worktree. § Gate result files adds the primary checkout for a run by hand. In a run by hand, the primary checkout is the folder where the run works, so the skill's text is narrow, not wrong. | `packages/factory/skills/mutation-testing/SKILL.md:136`  | note     |
| § Gate result files says that a file that is not valid JSON fails as `invalid result`. `mutation_rerun_result` reports `result not found` for a rerun file that is not valid JSON. Both messages fail the gate, so only the wording differs.                                                  | `packages/factory/scripts/premerge-check:957`            | note     |
| The QA row of `read_gate_result` says "no entry is `unresolved`". The skill uses `unresolved` for every survivor without one of the three actions, so the row reads correctly with the skill's meaning. SPEC-0120 fixes the contract row, and the QA row can take the same words then.        | `docs/spec/work/run-lifecycle-qa-strategy.md:191`        | note     |

## Structure checks

### `docs/spec/interface-contracts.md`

§ Gate result files agrees with `mutation_rerun_result` and `stored_mutation_result`. After a non-zero exit, `premerge-check` takes the exit code and the time-out from the rerun's file in its temporary worktree. It replaces `mutants` with the list of the stored result `.current-work/mutation-testing/<story-id>.json` at `git rev-parse --show-toplevel`. A stored result without the list leaves the rerun without `mutants`, and `judge` then fails. The row `mutation-testing` of the first table points to BR-066. The field table names `mutants` with its four fields and `finding`. The check found SPEC-0120 in the Gates pass row of the Story merge table, which the range did not change.

### `docs/spec/validation-rules.md`

BR-066 agrees with `judge` and `_entry_problem`. An entry with `resolution_action: unresolved` blocks, also when it is not a survivor. A survivor whose action is not one of `remove-dead-code`, `add-missing-test`, and `file-qa-finding` blocks as unresolved. A `file-qa-finding` entry blocks when `finding` is no finding ID or names no file at the head of the story branch. A time-out and a command that did not run fail first, whatever `mutants` holds. The skill says the same in its resolution rules, and RL-12 says it in the Scenario "An unresolved surviving mutant blocks the merge of its story".

### `docs/spec/features/core-artifact-ownership.feature`

The renamed Rule agrees with RL-12 and with the skill. The planning agent owns a mutant that needs a test, and the test-strategy agent owns a mutant that no test should kill, as the owner table of the skill and the Outline at `run-lifecycle.feature:1002` say. The first Scenario now dispatches the test-strategy agent only for a finding with `owner: test-strategy-agent`. That matches "The wave close routes the open QA findings by owner" in RL-12. The comment at line 578 points to the RL-12 Outline as the one home of the owner.

Every reference to the Rule uses the new name. These are the scope map, both gaps reports, the core-artifact-ownership QA strategy, `backlog/ST-0358.md`, and the list of Rules in `backlog/epics-core-artifact-ownership.md`. The old name appears only in records of finished work: SPEC-0090, the ST-0423 story, and the row of `spec-feedback-ST-0423.md` itself. Line 531 of the epics file uses the old words as prose about the motivation, not as the Rule name. The renamed Scenario "… for each open QA finding with owner test-strategy-agent" is cited with its new name in `core-artifact-ownership-gaps.md:100`. The check found SPEC-0121 in the Behavior cell of the QA strategy row that cites the Rule.

### `docs/spec/glossary.md`

The range adds no term. The check found no second term for a concept of the range and no avoided term in use.

### `docs/spec/work/term-candidates.md`

The file holds no row with status `proposed`. The check found nothing.

### Pending stories

No pending story owns SPEC-0120 or SPEC-0121. ST-0430 changes words, never rules, and edits no specification or QA strategy. ST-0423 is done.

## Spec-feedback rows on core artifacts

The core list is `packages/factory/rulebooks/core-artifacts.yaml`. The reviewer sets each `fixed` row on a core artifact to `confirmed` or `rejected`.

| Report                     | Artifact                                             | Drift                                                   | Verdict     | Reason                                                                                                                                                                            |
| -------------------------- | ---------------------------------------------------- | ------------------------------------------------------- | ----------- | --------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| `spec-feedback-ST-0423.md` | `docs/spec/interface-contracts.md`                   | Which result file `premerge-check` reads                | `confirmed` | § Gate result files names the stored result, the folder, and what comes from the rerun, as `mutation_rerun_result` does. SPEC-0120 concerns the Gates pass row, not this section. |
| `spec-feedback-ST-0423.md` | `docs/spec/validation-rules.md`                      | A survivor with another action, such as `none-required` | `confirmed` | BR-066 fails every survivor without one of the three actions, as `_entry_problem` does.                                                                                           |
| `spec-feedback-ST-0423.md` | `docs/spec/features/core-artifact-ownership.feature` | The name of the CAO-12 Rule                             | `confirmed` | The Rule names both owners, as the skill routes them, and every citation of the Rule uses the new name.                                                                           |

The report holds no row on `docs/testing.yaml`.

## Prior findings

SPEC-0111, SPEC-0116, SPEC-0117, SPEC-0118, and SPEC-0119 stay `open`, because the range changes none of their artifacts. The open register files SPEC-0056 to SPEC-0070 concern the counter-ids feature and lie outside this range. This pass inspected the reviewed artifacts fresh and did not only check the prior list.

## Traceability summary

BR-066 traces to RL-12, to CAO-G25 and CAO-G27, and to the Scenario of the mutation gate in `core-artifact-ownership.feature`. The CAO-12 Rule traces to the scope map and to CAO-12-LN-01 in the QA strategy, and its owner comes from RL-G24 through the RL-12 Outline. The citations IMPL-0059, RL-G24, and RL-G25 in the range each name an existing item. `docs/spec/scope-map.md` was read only, and the review files nothing on its content.
