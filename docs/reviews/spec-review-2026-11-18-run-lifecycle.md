---
type: inspect-spec
title: Spec review of run-lifecycle, pass 1
date: 2026-11-18
status: defects
reviewer: spec-review-agent
findings_filed: 16
story: run-lifecycle
scope: The run-lifecycle specification at commit 5f1170e788eaae81b2652cbf371eed85511589c0 on dev, read against the accepted proposal docs/proposals/run-lifecycle.md
---

# Spec review of run-lifecycle, pass 1

The run lifecycle specification covers every actor goal of the proposal with a Rule, and every Scenario has an owner row with a test ID in the QA strategy. Six major findings block architecture. Three concern the ledger states: `failed` names both a failed attempt and a stop, the states that let a wave close contradict each other, and the area spec rejects the feature branch that the feature file creates. The other three are a gate that fails every merge without dependency rules, a contract that runs the drift sessions after each merge, and four Scenarios of core-artifact-ownership.feature that the run lifecycle replaces. Ten minor findings go to the register, and five notes stay in this report.

Spec review is the `document` class. A `major` finding is a file in `docs/findings/`, a `minor` finding is a register file in `docs/findings/register/document/`, and a note stays here. No story or code encodes the run lifecycle specification yet, so every finding answers `in_use: false`. The stakeholder was not present. The review filed the findings without the pause point, so the stakeholder sees them first in this report.

## Reviewed specification

- `docs/spec/features/run-lifecycle.feature`: 19 Rules, 124 Scenarios and 13 Scenario Outlines.
- `docs/spec/areas/mechanized-dispatch.md`: Dispatch Initialization, Wave Lifecycle, Story Lifecycle, Evidence-Gated Escalation, Ledger Integrity, Interruption Safety, and the traceability table.
- `docs/spec/scope-map.md`: the 19 run lifecycle rows, read only.
- `docs/spec/validation-rules.md`: BR-055, BR-062 to BR-066, BR-085, BR-091, and BR-111 to BR-122.
- `docs/spec/interface-contracts.md`: `dispatch`, `premerge-check`, `block-dangerous-git.sh`, the `gates` schema, `dispatch close-wave`, and the report rows.
- `docs/spec/state-machines.md` § Ledger Entry Lifecycle.
- `docs/spec/entity-model.md`: DISPATCH_LEDGER, GATE_CONFIG, GATE_ENTRY, and FINDING_FILE.
- `docs/spec/glossary.md` § Run Lifecycle Vocabulary, and the entries User, Unattended Run, Logical Run, and Spec-Feedback Report.
- `docs/spec/work/run-lifecycle-gaps.md`, `docs/spec/work/run-lifecycle-qa-strategy.md`, and `docs/spec/work/term-candidates.md`.
- For consistency only: `docs/spec/features/core-artifact-ownership.feature`, and `packages/factory/scripts/dispatch` lines 620 to 720 to check one contradiction against the code.

`spec-lint --spec-dir docs/spec`: `spec-lint: 0 error(s), 0 warning(s), 57 info across 82 spec file(s).`

## Deterministic findings

| Rule     | Count | Subject                                                                       | Verdict                                                                                 |
| -------- | ----- | ----------------------------------------------------------------------------- | --------------------------------------------------------------------------------------- |
| GLOSS001 | 33    | Glossary terms that no spec file uses, such as Quorum and Workstream Resolver | Dismissed. None is a run lifecycle term, and the skill files no unused-term finding.    |
| TODO001  | 2     | 25 open items in `docs/spec/work/todo.md` and 5 in `docs/spec/work/todos.md`  | Dismissed. No item concerns the run lifecycle.                                          |
| TRACE003 | 21    | BR-011 to BR-054 defined but never referenced                                 | Dismissed. BR-111 to BR-122 are all referenced, and the listed rules are outside scope. |
| TRACE004 | 1     | `EPIC_BUILDING_BLOCK` in a relationship without an attribute block            | Dismissed. The entity belongs to the test-design entities, outside scope.               |

## Semantic findings

| ID        | Severity | Category | Type         | Characteristic | Artifact                                                     | Finding                                                                                                                             | Acted on by           |
| --------- | -------- | -------- | ------------ | -------------- | ------------------------------------------------------------ | ----------------------------------------------------------------------------------------------------------------------------------- | --------------------- |
| SPEC-0085 | major    | defect   | inconsistent | Consistent     | `docs/spec/areas/mechanized-dispatch.md:216`                 | The area spec rejects a missing `--feature-branch`, while every RL-01 Scenario creates `feature/login` that way.                    | requirements-agent    |
| SPEC-0086 | major    | defect   | ambiguous    | Unambiguous    | `docs/spec/state-machines.md:1165`                           | `failed` names both each failed attempt and the stop that waits for the User, so stops and wave closes fire too early.              | domain-modeling-agent |
| SPEC-0087 | major    | defect   | inconsistent | Consistent     | `docs/spec/validation-rules.md:171`                          | close-wave refuses "non-terminal" stories, the area spec lets a `blocked` one close, and a returned `pending` one is never covered. | domain-modeling-agent |
| SPEC-0088 | major    | defect   | incomplete   | Complete       | `docs/spec/features/run-lifecycle.feature:635`               | The proposal skips `dependency-check` at the merge without a rules file; the spec runs it always, and it exits 2.                   | requirements-agent    |
| SPEC-0089 | major    | defect   | inconsistent | Consistent     | `docs/spec/interface-contracts.md:1105`                      | The report contract dispatches the drift sessions after each merge, not at the wave close.                                          | domain-modeling-agent |
| SPEC-0090 | major    | defect   | inconsistent | Consistent     | `docs/spec/features/core-artifact-ownership.feature:537-557` | Four CAO Scenarios keep the developer's gate run by hand, the replacing `quality-gates`, and the close by hand.                     | requirements-agent    |
| SPEC-0091 | minor    | defect   | inconsistent | Consistent     | `docs/spec/features/run-lifecycle.feature:187`               | The User runs "only three commands" by hand, yet RL-01 makes the User run `dispatch init`.                                          | requirements-agent    |
| SPEC-0092 | minor    | defect   | incomplete   | Complete       | `docs/spec/features/run-lifecycle.feature:157`               | The spec does not say whether `dispatch add` waits for the User's go by hand, as the proposal's table requires.                     | requirements-agent    |
| SPEC-0093 | minor    | defect   | incomplete   | Complete       | `docs/spec/features/run-lifecycle.feature:777`               | No Scenario files the `QA` finding of the gate-check step, and the routing Scenario does not make it blocking.                      | requirements-agent    |
| SPEC-0094 | minor    | defect   | ambiguous    | Verifiable     | `docs/spec/interface-contracts.md:52`                        | The spec does not say which marker files are "the markers of the run" while several runs share one checkout.                        | domain-modeling-agent |
| SPEC-0095 | minor    | defect   | ambiguous    | Unambiguous    | `docs/spec/validation-rules.md:175`                          | By hand, `add` and `prepare-story` may each write a new wave number for the same finding.                                           | domain-modeling-agent |
| SPEC-0096 | minor    | defect   | incomplete   | Terminology    | `docs/spec/features/run-lifecycle.feature:1121`              | The vocabulary check skips `.feature` files, which keep "manual mode" and "main checkout".                                          | requirements-agent    |
| SPEC-0097 | minor    | defect   | incomplete   | Terminology    | `docs/spec/glossary.md#run-lifecycle-vocabulary`             | Ten run lifecycle terms lack an entry, the Avoid cells are empty, and "by hand" and "run" carry two senses.                         | domain-modeling-agent |
| SPEC-0098 | minor    | defect   | incomplete   | Consistent     | `docs/spec/entity-model.md:127`                              | GATE_ENTRY, the ledger entry, and the review report lack attributes that the Scenarios read.                                        | domain-modeling-agent |
| SPEC-0099 | minor    | defect   | inconsistent | Consistent     | `docs/spec/validation-rules.md:167`                          | Two structure files point to RL-G01 to RL-G21 and to an Open Items section that is empty.                                           | domain-modeling-agent |
| SPEC-0100 | minor    | defect   | inconsistent | Consistent     | `docs/spec/work/run-lifecycle-gaps.md:94`                    | The gaps report counts 132 Scenarios, while the file holds 137, and says that OI-01 is still open.                                  | requirements-agent    |

The register files hold the `why_this_severity` sentence of each minor finding, with its reason for the "no" to `fails_purpose`:

- SPEC-0091: Either actor can run `init`, and the guardrail refuses neither, so the implementer can act.
- SPEC-0092: The User still gives the go before `prepare-story` starts the added unit of work, so nothing starts without the User.
- SPEC-0093: BR-117 and the proposal say which findings `add` accepts, so a test writer can add the missing severity.
- SPEC-0094: A marker only lets a merge of its exact head through, so removing the markers keyed to the run's branches is safe.
- SPEC-0095: Keeping the wave that `add` wrote is the plain reading of "a new wave".
- SPEC-0096: The proposal's criterion names Markdown files, so the Scenario as written can pass.
- SPEC-0097: The feature file defines each missing term in its description.
- SPEC-0098: `dispatch-contract.md` and `interface-contracts.md` list each field.
- SPEC-0099: The links still open the right files.
- SPEC-0100: No Rule or test depends on the count.

### Notes

| Note                                                                                                                                                                                               | Why no change is needed                                                                                                            |
| -------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- | ---------------------------------------------------------------------------------------------------------------------------------- |
| The area spec Scenario "Successful merge with green test suite" removes the story branch and worktree at the merge, while `dispatch close` also removes merged branches and story worktrees.       | `git worktree remove` without `--force` keeps a worktree with untracked files, so `dispatch close` still stashes them.             |
| The Outline "premerge-check builds the call of a gate that it names" runs the built-in call of `mutation-testing` without a command, and BR-066 fails that gate and names the test-strategy agent. | Both hold together: the built-in call runs, and the gate script then fails. A test can assert both.                                |
| No rule defines `gates.attempts: 0` or a negative value.                                                                                                                                           | The QA strategy's boundary rows test absent, `0` and `1` for `attempts_escalated` only. A planner may add the case to RL-05-CT-02. |
| BR-121 and BR-122 speak of the "story ID" in the `story` field, while a unit of work can be a finding such as BUG-0090.                                                                            | The `premerge-check` contract and BR-118 say "the ID of the unit of work", so the reading for a finding is clear.                  |
| Two answers read narrower than the proposal: RL-G04 keeps the no-op for a ledger with the same stories, and RL-G14 leaves `docs/spec/work/` out of the vocabulary check.                           | The gaps report records that the stakeholder keeps both answers.                                                                   |

## Structure checks

### Entity model

SPEC-0098. Every entity that the feature file names is in the model, but GATE_ENTRY, the ledger entry, and the review report lack attributes that the Scenarios read.

### State machines

SPEC-0086. Ledger Entry Lifecycle belongs to DISPATCH_LEDGER, and its states match the Scenarios. Its **Fail** edge and its Notes give `failed` two meanings.

### Validation rules

SPEC-0087, SPEC-0095, and SPEC-0099. Each of BR-111 to BR-122 names a ledger, finding, or report attribute and a Scenario that needs it. BR-066 lacks the skip of SPEC-0088.

### Interface contracts

SPEC-0089 and SPEC-0094. A Scenario reaches each new operation of `dispatch`, `premerge-check`, and `block-dangerous-git.sh`.

### Area spec

SPEC-0085. The other area spec Scenarios agree with the feature file. The note on the merge cleanup above needs no change.

### Glossary

SPEC-0097. The check found no avoided term in use, because the run lifecycle terms have no Avoid cells yet.

### Term candidates

`docs/spec/work/term-candidates.md` holds no row, so the check found no `proposed` term. The four run lifecycle terms are in the glossary.

## Traceability summary

- **Proposal to Rule.** Each completion criterion of the proposal traces to a Rule in the gaps report. One design statement has no Scenario: the skip of `dependency-check` at the merge without a rules file (SPEC-0088). The filing of a `QA` finding by the implementation agent has none either (SPEC-0093).
- **Rule to scope map.** The scope map holds 19 run lifecycle rows, one for each Rule, each linking `run-lifecycle.feature`.
- **Scenario to test ID.** Every Scenario and Scenario Outline of the feature file names an owner row in the QA strategy, and every Scenario that a row cites exists in the feature file or the area spec. The Test ID column holds 128 rows and no duplicate ID.
- **Rule to BR.** BR-111 to BR-122 are each referenced from a contract, a Scenario row, or another rule.
- **Across feature files.** core-artifact-ownership.feature holds four Scenarios that the run lifecycle replaces (SPEC-0090).

## Next step

Hand SPEC-0085, SPEC-0088, SPEC-0090 and the minor findings of the requirements agent to the requirements agent. Hand SPEC-0086, SPEC-0087, SPEC-0089 and the minor findings of the domain-modeling agent to the domain-modeling agent. SPEC-0086 offers an option that changes the proposal's state table, so the domain-modeling agent asks the stakeholder before it takes that option. Then run the spec review again as pass 2.
