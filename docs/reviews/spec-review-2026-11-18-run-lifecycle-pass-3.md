---
type: inspect-spec
title: Spec review of run-lifecycle, pass 3
date: 2026-11-18
status: defects
reviewer: spec-review-agent
findings_filed: 2
story: run-lifecycle
scope: The run-lifecycle specification at commit 34e981d1 on dev, with the files that the pass 2 fixes changed in 9d0677ee..34e981d1, read against pass 2 in docs/reviews/spec-review-2026-11-18-run-lifecycle-pass-2.md
---

# Spec review of run-lifecycle, pass 3

The spec is not ready for the architecture step. Three major findings stay open. SPEC-0101 stays `open`, because `close-wave` cannot see two of the five refusals that HasStopped now names. Two new major findings come from the fix of SPEC-0102. SPEC-0107: the scope check refuses a story that carries the `QA` finding of its own mutant. SPEC-0108: an empty `mutants` list passes a mutation command that failed. SPEC-0102 is now `resolved`. The four minor register files SPEC-0103 to SPEC-0106 stay `resolved`.

Spec review is the `document` class. No story or code encodes the run lifecycle spec yet, so every finding answers `in_use: false`. The stakeholder was not present, so the review filed the findings without the pause point. The stakeholder sees them first in this report. The settled decisions on SPEC-0086, the field `returned`, RL-G24, SPEC-0101 A and RL-G25 stay as they are. Each new finding offers a fix inside those decisions.

## Reviewed specification

- The diff `git diff 9d0677ee..34e981d1 -- docs/spec docs/findings`, 17 files.
- `docs/spec/features/run-lifecycle.feature`: the description, RL-06, RL-07 and RL-12, with the five new Scenarios.
- `docs/spec/features/core-artifact-ownership.feature`: the mutation gate Scenario and the test guardrails Outline.
- `docs/spec/state-machines.md` § Ledger Entry Lifecycle: **Prepare**, **ReDispatch** from **FAILED**, and the Notes.
- `docs/spec/validation-rules.md`: BR-113, BR-115, BR-116, BR-066, and the renamed heading.
- `docs/spec/interface-contracts.md`: the `dispatch` bullets, the `premerge-check` rows, the gate result files, and the `close-wave` contract.
- `docs/spec/areas/mechanized-dispatch.md`: Story Lifecycle and Evidence-Gated Escalation.
- `docs/spec/work/run-lifecycle-gaps.md` (RL-G25), `docs/spec/work/run-lifecycle-qa-strategy.md`, `docs/spec/work/core-artifact-ownership-gaps.md` and `docs/spec/work/core-artifact-ownership-qa-strategy.md`.
- `docs/spec/entity-model.md` (DISPATCH_LEDGER) and `packages/factory/skills/mutation-testing/SKILL.md` (report format), for consistency only.
- `docs/spec/scope-map.md`, read only.

`spec-lint --spec-dir docs/spec`: `spec-lint: 0 error(s), 0 warning(s), 57 info across 82 spec file(s).` `statemachine-lint --spec-dir docs/spec`: `0 error(s), 0 warning(s), 0 info`.

## Verification of the pass 2 findings

| ID        | Severity | Verdict  | What the review checked                                                                                                                                                                                                                                                                                                                          |
| --------- | -------- | -------- | ------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------ |
| SPEC-0101 | major    | open     | HasStopped, the guard of **ReDispatch**, BR-115, BR-116, the `re-dispatch` bullet, the feature description and the area spec name the five reasons, and RL-06 has the new Scenario. `escalate` records no refusal, and `close-wave` reads only the ledger and the reports. So `close-wave` still refuses ST-0350 when its diff leaves the scope. |
| SPEC-0102 | major    | resolved | RL-G25, BR-066, the Gates pass row, the gate result table and the field `mutants` let ST-0350 merge with QA-0012 filed, and fail closed without a list. RL-12 has both new Scenarios. Two defects of the fix are filed as SPEC-0107 and SPEC-0108.                                                                                               |
| SPEC-0103 | minor    | resolved | **Prepare**, BR-113 and the `prepare-story` bullet refuse an entry with `returned: true`. RL-07 has "prepare-story refuses a returned story and names the return".                                                                                                                                                                               |
| SPEC-0104 | minor    | resolved | RL-12 has "A QA finding that the test-strategy agent hands to the planning agent runs in the next wave". The QA strategy names it in RL-12-LN-03.                                                                                                                                                                                                |
| SPEC-0105 | minor    | resolved | The heading reads "Ownership and spec-feedback reports". No file in `docs/spec`, `docs/findings` or `packages` links the old anchor.                                                                                                                                                                                                             |
| SPEC-0106 | minor    | resolved | The QA strategy counts 133 Scenarios and 15 Scenario Outlines, 148 in all, as the feature file and the gaps report do, and names RL-G01 to RL-G25.                                                                                                                                                                                               |

## Deterministic findings

| Rule     | Count | Subject                                                                       | Verdict                                                                                 |
| -------- | ----- | ----------------------------------------------------------------------------- | --------------------------------------------------------------------------------------- |
| GLOSS001 | 33    | Glossary terms that no spec file uses, such as Quorum and Workstream Resolver | Dismissed. None is a run lifecycle term, and the skill files no unused-term finding.    |
| TODO001  | 2     | Open items in `docs/spec/work/todo.md` and `docs/spec/work/todos.md`          | Dismissed. No item concerns the run lifecycle.                                          |
| TRACE003 | 21    | BR-011 to BR-054 defined but never referenced                                 | Dismissed. BR-111 to BR-122 are all referenced, and the listed rules are outside scope. |
| TRACE004 | 1     | `EPIC_BUILDING_BLOCK` in a relationship without an attribute block            | Dismissed. The entity belongs to the test-design entities, outside scope.               |

## Semantic findings

| ID        | Severity | Category | Type         | Characteristic | Artifact                              | Finding                                                                                                                                                         | Acted on by           |
| --------- | -------- | -------- | ------------ | -------------- | ------------------------------------- | --------------------------------------------------------------------------------------------------------------------------------------------------------------- | --------------------- |
| SPEC-0101 | major    | defect   | incomplete   | Complete       | `docs/spec/state-machines.md:1231`    | Still open: `close-wave` reads no record of a refusal of `escalate` for `verify-base` or the scope, so a story stopped that way still hangs its wave.           | domain-modeling-agent |
| SPEC-0107 | major    | defect   | inconsistent | Consistent     | `docs/spec/interface-contracts.md:38` | No statement says where the gate-check step commits the `QA` finding of a mutant, and on the story branch the scope check refuses the story for that finding.   | domain-modeling-agent |
| SPEC-0108 | major    | defect   | incomplete   | Complete       | `docs/spec/validation-rules.md:485`   | BR-066 passes a non-zero mutation run whose `mutants` list is empty or holds no survivor, so a mutation command that failed for another reason passes the gate. | domain-modeling-agent |

### What the fixes broke

The review read each fix for a new defect. Three findings come from the fixes:

- SPEC-0101 stays open, because its fix moved two runtime checks into HasStopped. `escalate` runs `verify-base` and the scope check, writes nothing on a refusal, and `close-wave` reads only the ledger. So the example of SPEC-0101 still hangs at the wave close.
- SPEC-0107 comes from the fix of SPEC-0102. The new existence check of BR-066 and the RL-12 Scenario need QA-0012 on the feature branch. The usual way, a commit on the story branch, meets the scope rule of `merge-story`, because QA-0012 names no story.
- SPEC-0108 comes from the fix of SPEC-0102 too. The pass condition after a non-zero exit checks the list for `unresolved` entries, but not that the list explains the exit.

The other fixes broke nothing that gives a wrong result. The notes below list what they left loose.

### Notes

| Note                                                                                                                                                                                                                            | Why no change is needed                                                                                                                                                 |
| ------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- | ----------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| `premerge-check` reads the stored result of `mutation-testing` and does not rerun the command. So an `add-missing-test` entry counts as resolved without a check that the new test kills the mutant.                            | RL-G25 lets the three actions of the skill resolve a survivor. The rerun of the test suite at the merge still runs the new test, and a later mutation run shows a miss. |
| The guard of **ReDispatch** reads "the counted attempts on the tier reached the limit and `dispatch escalate` would grant a promotion". The second clause repeats the attempt count of the first.                               | Both clauses give the same result, and the comment under the guard lists the conditions of BR-115.                                                                      |
| The Contract test row RL-12-CT-03 of the QA strategy lists "Survivors in the `mutants` list: none". It does not say whether "none" means an empty list after a non-zero exit, and so whether the test expects a pass or a fail. | The fix of SPEC-0108 decides the case, and the test-strategy agent then sets the expected result.                                                                       |

## Structure checks

### Entity model

No new finding. DISPATCH_LEDGER holds `reason`, defined as why the entry is `blocked` or `failed`. No field holds a refusal of `escalate`, which SPEC-0101 names.

### State machines

SPEC-0101. **Prepare** refuses an entry with `returned: true` before the dependency and wave checks. The guard of **ReDispatch** and the Notes use the meaning of SPEC-0101 A. `statemachine-lint` passes.

### Validation rules

SPEC-0108. BR-113 holds the refusal of a returned entry. BR-115 and BR-116 name the five reasons and the new example. BR-066 holds the pass condition of the mutation gate that RL-G25 settled.

### Interface contracts

SPEC-0107. The `prepare-wave` and `prepare-story` bullet, the `re-dispatch` bullet, the Gates pass row and the gate result table agree with the validation rules. The `merge-story` scope does not hold the `QA` finding of a mutant.

### Area spec

No finding. The Story Lifecycle comment and the Evidence-Gated Escalation description name the five reasons of BR-115.

### Glossary

No finding. "drift report" is gone from the living spec files. It appears only in the RL-19 Scenario that forbids it. The new Scenarios use the glossary terms.

### Term candidates

`docs/spec/work/term-candidates.md` holds no row, so the check found no `proposed` term.

## Traceability summary

- **Proposal to Rule.** Each completion criterion of the proposal traces to a Rule in the gaps report. The route of a mutant finding to a test on the story's code is now consistent through the gates, except for the commit of the finding (SPEC-0107).
- **Rule to scope map.** The scope map holds 19 run lifecycle rows, one for each Rule, each linking `run-lifecycle.feature`.
- **Scenario to test ID.** Each of the five new Scenarios has an owner row in the QA strategy: RL-06-IT-05, RL-07-CT-03, RL-12-IT-06, RL-12-IT-07 and RL-12-LN-03.
- **Rule to BR.** BR-111 to BR-122 and BR-066 are each referenced from a contract, a Scenario row, or another rule.
- **Across feature files.** core-artifact-ownership.feature follows BR-066 and RL-G25. DEC-09 of the draft `docs/proposals/mutation-gate.md` still says the opposite, as RL-G25 records.

## Next step

Hand SPEC-0101, SPEC-0107 and SPEC-0108 to the domain-modeling agent. For SPEC-0107 the requirements agent then adds the commit of the finding to the RL-12 Scenario. For SPEC-0101 the requirements agent adds a Scenario in which `close-wave 1` passes. Each fix stays inside the settled decisions, so no stakeholder question is due. Then run the spec review again as pass 4.

## Verification of the pass 3 fixes

The stakeholder chose way A for SPEC-0101 and SPEC-0107, and the proposed fix for SPEC-0108. The owners applied the fixes in `f076f586`, `786ead54` and `36d4e2f3`. The stakeholder decided against a full pass 4, so this section checks only the three fixes against the fix proposals of this report. `spec-lint` reports 0 errors and 0 warnings, and `statemachine-lint` reports 0 errors.

| ID        | Severity | Verdict  | What the review checked                                                                                                                                                                                                                                          |
| --------- | -------- | -------- | ---------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| SPEC-0101 | major    | resolved | `escalate` writes `escalate refused: verify-base` or `escalate refused: scope` into `reason`. HasStopped, BR-115, BR-116 and the `close-wave` contract read that record and no branch. RL-14 has a Scenario in which `close-wave 1` passes with ST-0350 stopped. |
| SPEC-0107 | major    | resolved | The gate-check step commits the `QA` finding on the story branch. The `merge-story` scope and the Scope row admit it through the `finding` field of a `mutants` entry, and BR-066 checks the file at the head of the story branch. The RL-12 Scenario agrees.    |
| SPEC-0108 | major    | resolved | After a non-zero exit, BR-066, the Gates pass row and the gate result table need at least one `survived` entry. An empty list fails, and RL-12 has a Scenario for it.                                                                                            |

The diff of the three commits shows no new problem that gives a wrong result. The gaps report counts 135 Scenarios, and the feature file holds 135. No finding of this spec review stays open, so the spec is ready for the architecture step.
