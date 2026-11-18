---
type: inspect-spec
title: Spec review of run-lifecycle, pass 2
date: 2026-11-18
status: defects
reviewer: spec-review-agent
findings_filed: 6
story: run-lifecycle
scope: The run-lifecycle specification at commit c2d09f330160ac5ca7c55b53d82b84d85ff93e43 on dev, read against the accepted proposal docs/proposals/run-lifecycle.md and against pass 1 in docs/reviews/spec-review-2026-11-18-run-lifecycle.md
---

# Spec review of run-lifecycle, pass 2

All sixteen findings of [pass 1](spec-review-2026-11-18-run-lifecycle.md) are fixed. The six major findings SPEC-0085 to SPEC-0090 are now `resolved`, and the ten minor findings SPEC-0091 to SPEC-0100 stay `resolved`. The fresh inspection found two new major findings, and both block architecture. A failed story can hang, because HasStopped leaves out two refusals of `dispatch escalate`. A story with an unresolved mutant cannot merge, so the `QA` finding of the mutant runs on a branch without the story's code. Four minor findings go to the register, and three notes stay in this report.

Spec review is the `document` class. No story or code encodes the run lifecycle specification yet, so every finding answers `in_use: false`. The stakeholder was not present. The review filed the findings without the pause point, so the stakeholder sees them first in this report. The stakeholder decisions on SPEC-0086 (no new state, one predicate HasStopped), on the entry field `returned`, and on RL-G24 (the owner of a mutant finding follows its cause) count as settled.

## Reviewed specification

- `docs/spec/features/run-lifecycle.feature`: 19 Rules, 128 Scenarios and 15 Scenario Outlines.
- `docs/spec/features/core-artifact-ownership.feature`: the Scenarios that SPEC-0089, SPEC-0090 and RL-G24 changed.
- `docs/spec/areas/mechanized-dispatch.md`: Ubiquitous Language, Dispatch Initialization, Wave Lifecycle, Story Lifecycle, and Evidence-Gated Escalation.
- `docs/spec/scope-map.md`: the 19 run lifecycle rows, read only.
- `docs/spec/validation-rules.md`: § Dispatch ledger, BR-111 to BR-122, and BR-066.
- `docs/spec/interface-contracts.md`: `dispatch`, `premerge-check`, the `gates` schema, `dispatch close-wave`, and the report rows.
- `docs/spec/state-machines.md` § Ledger Entry Lifecycle.
- `docs/spec/entity-model.md`: DISPATCH_LEDGER, REVIEW_REPORT, GATE_CONFIG and GATE_ENTRY.
- `docs/spec/glossary.md` § Run Lifecycle Vocabulary, and the entries User and Spec-Feedback Report.
- `docs/spec/work/run-lifecycle-gaps.md`, `docs/spec/work/run-lifecycle-qa-strategy.md`, and `docs/spec/work/term-candidates.md`.
- For consistency only: `docs/proposals/mutation-gate.md` (draft), DEC-09.

`spec-lint --spec-dir docs/spec`: `spec-lint: 0 error(s), 0 warning(s), 57 info across 82 spec file(s).`

## Verification of the pass 1 findings

| ID        | Severity | Verdict  | What the review checked                                                                                                                                                                         |
| --------- | -------- | -------- | ----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| SPEC-0085 | major    | resolved | The area spec Outline creates a missing feature branch from the base tip, with a worktree only in an orchestrated run. The adopted branch gets a worktree in an orchestrated run.               |
| SPEC-0086 | major    | resolved | HasStopped is defined once and used in BR-116, BR-119, the close-wave rule and contract, the feature description, and the decision points. Its gap toward BR-115 is new and filed as SPEC-0101. |
| SPEC-0087 | major    | resolved | The close-wave rule and contract list five states. `returned` is set by `return-story` and reset by `add`. Scenarios cover a returned story and a chain behind a returned head.                 |
| SPEC-0088 | major    | resolved | The new Scenario, BR-066, the `premerge-check` contract and the gate-check step skip `dependency-check` without a rules file and name the skip.                                                 |
| SPEC-0089 | major    | resolved | The report contract and the core-artifact-ownership Scenario run the drift sessions at the wave close.                                                                                          |
| SPEC-0090 | major    | resolved | The four core-artifact-ownership Scenarios follow the run lifecycle. The gaps report and the Test Retention Policy list the changed Scenarios and tests.                                        |
| SPEC-0091 | minor    | resolved | The implementation agent runs `dispatch init` in every RL-01 Scenario, and RL-C07 records why the Rule keeps the User as actor.                                                                 |
| SPEC-0092 | minor    | resolved | `dispatch add of QA-0012` is a decision point of a run by hand (RL-C08).                                                                                                                        |
| SPEC-0093 | minor    | resolved | The Outline files a blocking `QA` finding with an owner, and the routing Scenario starts from open blocking findings.                                                                           |
| SPEC-0094 | minor    | resolved | The `close` bullet defines the markers of a run and keys the removal in the primary checkout to the `branch` line.                                                                              |
| SPEC-0095 | minor    | resolved | BR-113 and the `prepare-story` bullet keep the wave that `add` wrote.                                                                                                                           |
| SPEC-0096 | minor    | resolved | The vocabulary Scenario searches the `.feature` files, and the gaps report names the two feature files whose stories change the old terms.                                                      |
| SPEC-0097 | minor    | resolved | The glossary defines the missing terms, fills the seven Avoid cells, rewords User, and drops Playbook Run. The heading in SPEC-0105 is a new use of an avoided term.                            |
| SPEC-0098 | minor    | resolved | The entity model holds the gate fields, the ledger entry fields, and REVIEW_REPORT.                                                                                                             |
| SPEC-0099 | minor    | resolved | Both structure files point to RL-G01 to RL-G23 and to the Settled Items of the QA strategy.                                                                                                     |
| SPEC-0100 | minor    | resolved | The gaps report counts 128 Scenarios and 15 Scenario Outlines, 143 in all, which matches the file. The OI-01 sentence is correct.                                                               |

## Deterministic findings

| Rule     | Count | Subject                                                                       | Verdict                                                                                 |
| -------- | ----- | ----------------------------------------------------------------------------- | --------------------------------------------------------------------------------------- |
| GLOSS001 | 33    | Glossary terms that no spec file uses, such as Quorum and Workstream Resolver | Dismissed. None is a run lifecycle term, and the skill files no unused-term finding.    |
| TODO001  | 2     | Open items in `docs/spec/work/todo.md` and `docs/spec/work/todos.md`          | Dismissed. No item concerns the run lifecycle.                                          |
| TRACE003 | 21    | BR-011 to BR-054 defined but never referenced                                 | Dismissed. BR-111 to BR-122 are all referenced, and the listed rules are outside scope. |
| TRACE004 | 1     | `EPIC_BUILDING_BLOCK` in a relationship without an attribute block            | Dismissed. The entity belongs to the test-design entities, outside scope.               |

## Semantic findings

| ID        | Severity | Category | Type         | Characteristic | Artifact                                        | Finding                                                                                                                                | Acted on by           |
| --------- | -------- | -------- | ------------ | -------------- | ----------------------------------------------- | -------------------------------------------------------------------------------------------------------------------------------------- | --------------------- |
| SPEC-0101 | major    | defect   | incomplete   | Complete       | `docs/spec/state-machines.md:1231`              | HasStopped and the guard of ReDispatch leave out two refusals of `escalate`, so a failed story that `escalate` refuses hangs the wave. | domain-modeling-agent |
| SPEC-0102 | major    | defect   | inconsistent | Consistent     | `docs/spec/features/run-lifecycle.feature:862`  | A story with an unresolved mutant fails its mutation gate, so its `QA` finding runs on a branch that lacks the story's code.           | requirements-agent    |
| SPEC-0103 | minor    | defect   | incomplete   | Complete       | `docs/spec/state-machines.md:1132`              | **Prepare** does not refuse an entry with `returned: true`, so `prepare-story` can start a returned story again.                       | domain-modeling-agent |
| SPEC-0104 | minor    | defect   | incomplete   | Complete       | `docs/spec/features/run-lifecycle.feature:886`  | No Scenario routes a `QA` finding that the test-strategy agent hands to the planning agent after the wave close.                       | requirements-agent    |
| SPEC-0105 | minor    | defect   | inconsistent | Terminology    | `docs/spec/validation-rules.md:468`             | A heading of the validation rules uses "drift reports", a term that the glossary avoids and RL-19 forbids.                             | domain-modeling-agent |
| SPEC-0106 | minor    | defect   | inconsistent | Consistent     | `docs/spec/work/run-lifecycle-qa-strategy.md:5` | The QA strategy counts 14 Scenario Outlines, while the feature file holds 15, and names RL-G01 to RL-G23 beside RL-G24.                | test-strategy-agent   |

The register files hold the `why_this_severity` sentence of each minor finding, with its reason for the "no" to `fails_purpose`:

- SPEC-0103: By hand a story starts only after the User's go, and `prepare-wave` prepares only its own wave.
- SPEC-0104: `premerge-check dev` refuses the run and names QA-0013, so nothing merges wrong.
- SPEC-0105: The heading names the right rules.
- SPEC-0106: No row or test depends on the count.

### What the fixes broke

The review looked at each fix for a new defect. Two findings come from the fixes:

- SPEC-0101 comes from the predicate of SPEC-0086. Before the fix, the same case only left the agent with two refusals. Now HasStopped decides the wave close and the decision points, so the same gap stops the whole run.
- SPEC-0102 comes to light through the RL-G24 Outline. The Outline names the cause "a test that the step could not write within its attempts", so the story has stopped as `failed` before its finding runs.

The other fixes broke nothing that gives a wrong result. The notes below list what they left loose.

### Notes

| Note                                                                                                                                                                                                                  | Why no change is needed                                                                                  |
| --------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- | -------------------------------------------------------------------------------------------------------- |
| The core-artifact-ownership Outline "The test guardrails come from the story first, then from testing.yaml, then from the default" lists `dependency-check` in every row, without the condition that SPEC-0088 added. | A test writer adds `docs/spec/dependency-rules.dsl` to the fixture, and BR-066 states the condition.     |
| `validation-rules.md` and `interface-contracts.md` name the settled items RL-G01 to RL-G23, while the gaps report now ends with RL-G24.                                                                               | The sentence stays true, because neither structure file cites RL-G24, and the link opens the full table. |
| The close-wave contract does not say whether `close-wave` lists the drift rows while a unit of work of the wave can still go on.                                                                                      | The implementation agent waits for the wave either way, and the next run of `close-wave` lists the rows. |

## Structure checks

### Entity model

No finding. DISPATCH_LEDGER holds `deps`, `branch`, `worktree`, `escalation_granted`, `reason`, `returned` and `attempt_grants`. GATE_CONFIG and GATE_ENTRY hold the fields that RL-05 and RL-09 read. REVIEW_REPORT holds `story`, `run` and `branch_head`.

### State machines

SPEC-0101 and SPEC-0103. Ledger Entry Lifecycle belongs to DISPATCH_LEDGER, and its states and edges agree with the Scenarios. The Notes define HasStopped and the field `returned`.

### Validation rules

SPEC-0105. Each of BR-111 to BR-122 names a ledger, finding, or report attribute and a Scenario that needs it. BR-066 states the skip of `dependency-check`. BR-115 lists the refusals that SPEC-0101 compares with HasStopped.

### Interface contracts

No new finding beyond SPEC-0101, whose `re-dispatch` bullet repeats the predicate. A Scenario reaches each operation of `dispatch`, `premerge-check` and `close-wave`. The Refuses row of `close-wave` matches the validation rules.

### Area spec

No finding. The Dispatch Initialization, Wave Lifecycle and Story Lifecycle Scenarios agree with the feature file. Evidence-Gated Escalation holds the refusals of BR-115 that SPEC-0101 names.

### Glossary

SPEC-0105. The glossary defines every run lifecycle term that the files use, and the Avoid cells name the seven replaced terms. One heading in `validation-rules.md` still uses an avoided term.

### Term candidates

`docs/spec/work/term-candidates.md` holds no row, so the check found no `proposed` term.

## Traceability summary

- **Proposal to Rule.** Each completion criterion of the proposal traces to a Rule in the gaps report. The proposal's route of a `planning-agent` finding to a test that kills the mutant has no consistent path through the gates (SPEC-0102).
- **Rule to scope map.** The scope map holds 19 run lifecycle rows, one for each Rule, each linking `run-lifecycle.feature`.
- **Scenario to test ID.** Every Scenario and Scenario Outline of the feature file names an owner row in the QA strategy. The Contract Owners table holds 132 rows and no duplicate Test ID.
- **Rule to BR.** BR-111 to BR-122 are each referenced from a contract, a Scenario row, or another rule.
- **Across feature files.** core-artifact-ownership.feature agrees with the run lifecycle. counter-ids.feature and finding-classification.feature keep the old terms until the vocabulary story, as the gaps report states.

## Next step

Hand SPEC-0102 and SPEC-0104 to the requirements agent. SPEC-0102 needs the stakeholder's answer on whether a story with filed mutants merges. Hand SPEC-0101, SPEC-0103 and SPEC-0105 to the domain-modeling agent. SPEC-0101 offers an option with a new transition, so the domain-modeling agent asks the stakeholder before it takes that option. Hand SPEC-0106 to the test-strategy agent. Then run the spec review again as pass 3.
