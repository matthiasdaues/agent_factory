---
type: inspect-spec
title: Spec review of finding-classification, pass 1
date: 2026-11-06
status: defects
reviewer: spec-review-agent
findings_filed: 9
story: finding-classification
scope: The finding-classification specification at commit 26faacef12ce14c08ffc3c33442b0834c1f1a9b3 on dev, read against the accepted proposal docs/proposals/finding-classification.md (DEC-01 to DEC-54)
---

# Spec review of finding-classification, pass 1

The specification of finding-classification covers every actor goal of the proposal with a Rule, and every Rule traces to the scope map. Four major findings block the next step. Two of them concern the stop: an agent can end a stop, or drop a blocking finding from the loop, by changing the status alone. The other two are contradictions between Scenarios and business rules. Five minor findings go to the register, and seven notes stay in this report.

The review applies the classification rules of the accepted proposal, as the brief requires. Spec review is the `document` class. A `major` finding is a file in `docs/findings/`, a `minor` finding is a line in `docs/findings/register/document.jsonl`, and a note stays here. No story or code encodes this specification yet, so every finding answers `in_use: false`. The stakeholder was not present. The review filed the findings without the pause point, and the stakeholder sees them in this report.

## Reviewed specification

- `docs/spec/features/finding-classification.feature`: 21 Rules and 125 Scenarios.
- `docs/spec/work/finding-classification-gaps.md`: FC-G01 to FC-G08, FC-C01 to FC-C17, and DEC-49 to DEC-54.
- `docs/spec/work/finding-classification-qa-strategy.md`.
- `docs/spec/scope-map.md`: the 21 finding-classification rows, read only.
- `docs/spec/glossary.md` § Finding Classification Vocabulary, with the shared terms User, Reviewer, Owner, Stakeholder, and Pause Point.
- `docs/spec/entity-model.md` § Finding Classification Entities.
- `docs/spec/state-machines.md` § Finding Lifecycle.
- `docs/spec/validation-rules.md`: BR-079 to BR-095.
- `docs/spec/interface-contracts.md`: § Finding Classification Contracts, § Child-result envelope, and the stop sentence of the `dispatch` contract.
- `docs/spec/schemas/finding-basis.json`.
- `docs/spec/work/term-candidates.md`.
- `docs/proposals/finding-classification.md`, DEC-01 to DEC-54.
- For facts only: `docs/findings/BUG-0037.md`, the open finding files, and `docs/findings/register/`.

`spec-lint`: `0 error(s), 0 warning(s), 58 info across 66 spec file(s).`

## Deterministic findings

| Rule     | Finding                                                | Disposition                                                                              |
| -------- | ------------------------------------------------------ | ---------------------------------------------------------------------------------------- |
| GLOSS001 | Glossary terms such as `Claim Register` are never used | Dismissed. No line names a term of § Finding Classification Vocabulary.                  |
| TODO001  | `todo.md` and `todos.md` hold unresolved items         | Dismissed. The count does not depend on this feature.                                    |
| TRACE003 | BR-011 to BR-055 are never referenced                  | Dismissed. These rules predate the feature. BR-079 to BR-095 are all referenced.         |
| TRACE004 | `EPIC_BUILDING_BLOCK` has no attribute block           | Dismissed. The entity predates the feature. Every finding-classification entity has one. |

No info line names BR-079 to BR-095 or a finding-classification file.

## Semantic findings

| ID        | Severity | Category | Characteristic | Location                                                    | Finding                                                                                                                                                                                                 |
| --------- | -------- | -------- | -------------- | ----------------------------------------------------------- | ------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| SPEC-0071 | major    | defect   | Consistent     | `interface-contracts.md:1465`, stop contract                | The stop ends on any status other than `open`. The Finding Lifecycle lets **STOPPING** end only on **StopConfirmed**. An agent ends a stop with `status: deferred`, or with an uncommitted `resolved`.  |
| SPEC-0072 | major    | defect   | Complete       | `validation-rules.md:533`, BR-086                           | An agent may set `deferred` on a blocking finding, which drops it from the loop without a human. The Finding Lifecycle reaches **DEFERRED** only in the migration. No rule says who may defer, or when. |
| SPEC-0073 | major    | defect   | Consistent     | `finding-classification.feature:607-610`, `:643-646`        | Two git-check Scenarios list `dev` and `main` without `origin/dev` and `origin/main`, and one says "only". BR-088 and DEC-50 check both remote-tracking branches.                                       |
| SPEC-0074 | major    | defect   | Consistent     | `finding-classification.feature:149-152`, BR-084 and BR-087 | A capped suggestion with `fails_purpose` true is `minor`, but BR-087 requires its "no to fails_purpose" sentence. The lint rejects the line, or the reviewer writes a false marker.                     |
| SPEC-0075 | minor    | defect   | Verifiable     | `validation-rules.md:535`, BR-088                           | BR-088 runs the git check on a new register line, and no Scenario covers it.                                                                                                                            |
| SPEC-0076 | minor    | defect   | Consistent     | `interface-contracts.md:31`, `dispatch` contract            | The `dispatch` contract states the stop as "no `stop_confirmed_by`". BR-091 and DEC-52 hold it while either confirmation field is empty.                                                                |
| SPEC-0077 | minor    | defect   | Terminology    | `finding-classification.feature:135`, `:808`, BR-080        | The feature file and BR-080 say "the reviewer", which the glossary lists under Avoid for Reviewer Agent.                                                                                                |
| SPEC-0078 | minor    | defect   | Terminology    | `finding-classification.feature:812-844`, Rules FC-15 to 17 | One person is "the user", "the human", and "the stakeholder" in the confirm, waive, and raise steps. "Human" has no glossary entry.                                                                     |
| SPEC-0079 | minor    | defect   | Terminology    | `glossary.md` § Finding Classification Vocabulary           | Migration agent, calibration example, child-result envelope, and category have no glossary entry.                                                                                                       |

SPEC-0071 to SPEC-0074 are finding files. SPEC-0075 to SPEC-0079 are lines in `docs/findings/register/document.jsonl`. The register schema has no `owner` key, so each line names its owner in its `finding` text. SPEC-0077 to SPEC-0079 name `domain-modeling-agent`, as `inspect-spec` § Check the glossary requires.

SPEC-0071 and SPEC-0072 share one cause: the specification gives `deferred` no rule. The fix of SPEC-0072 needs a stakeholder answer, and the fix of SPEC-0071 depends on it. SPEC-0073 and SPEC-0074 are `major` because the document class counts two statements that contradict each other as `fails_purpose`. Each one has a small fix.

### Notes

These observations need no change now, or another record tracks them.

1. **A suggestion in a finding file.** The entity model and the finding-file contract allow the category `suggestion` in a finding file. A finding file holds only `critical` or `major`, and a suggestion is at most `minor`. So the value never passes the lint. It does no harm.
2. **Two Scenarios on parallel register lines.** "Two parallel reviews add lines without touching each other's lines" and "Two register lines from two branches merge without a conflict" test the same merge. The second one is the exact form. The QA strategy can let one test own both.
3. **The proposal still counts 39 migrated findings.** The completion criterion "None of the 39 migrated findings is `open` with severity `minor`" disagrees with DEC-54, which migrates every open finding without `review_class`. The feature file follows DEC-54. The proposal owner should align the criterion, as the gaps report already asks for the `schema-validate` criterion.
4. **An agent can lower a filed finding through its basis.** `guard-human-fields` does not guard the basis, so FC-G04 lets an agent raise a finding for the human. The same path lets an author agent change `fails_purpose` to false, move its own `major` finding into the register, and leave the loop. A headless run lists the new line in its final summary only after the loop ends. The proposal does not decide whether an agent may lower a filed finding. This is a question for the stakeholder, not a defect of the specification.
5. **The settings file is a new outside contract.** The feature description lists four outside contracts. `docs/factory-settings.yaml` is a fifth one that each project writes, and `finding-lint` fails without it. The description already states the file, and Rule FC-11 holds its Scenarios, so a reader finds it.
6. **The OpenCode guard has no place yet.** The plugin `packages/factory/config/plugins/agent-factory.ts` does not exist on `dev`. The guard contract and FC-QG24 route the gap to the architecture agent, as DEC-51 requires.
7. **The register-line git check changes no severity.** `in_use` affects only `harms_downstream`, the security Critical level, and the architecture raise. None of them can apply to a `minor` line. SPEC-0075 offers the removal of the check as one fix.

## Structure checks

### `docs/spec/entity-model.md`

Every entity that the feature file names has an attribute block. FINDING_FILE, REGISTER_LINE, and BASIS agree with the field Scenarios of Rules FC-06 and FC-07, and REGISTER_LINE has the twelve keys of the register contract. LINE_IDENTITY holds the three values of BR-088. The `suggestion` value of FINDING_FILE.category can never pass the lint (note 1).

### `docs/spec/state-machines.md`

The Finding Lifecycle belongs to FINDING_FILE and REGISTER_LINE. Its pseudocode and its Mermaid edges correspond one to one, and the stop, waive, raise, and migration Scenarios follow its transitions. It disagrees with the stop contract on how **STOPPING** ends (SPEC-0071). It has no edge from **IN_LOOP** or **STOPPING** to **DEFERRED**, while BR-086 lets an agent set `deferred` (SPEC-0072).

### `docs/spec/validation-rules.md`

BR-079 to BR-095 each name an attribute of the entity model and trace to a Rule of the feature file and to a decision or gap. BR-084 and BR-087 contradict each other for a capped suggestion (SPEC-0074). BR-086 gives `deferred` no rule (SPEC-0072). BR-088 covers register lines without a Scenario (SPEC-0075). BR-080 uses the avoided word "reviewer" (SPEC-0077).

### `docs/spec/interface-contracts.md`

Each field of the finding-file and register-line contracts matches an attribute of the entity model. A Scenario reaches each operation: the finding file, the register line, the envelope counts, `finding-lint`, the settings file, the stop, the guard, and the proposal review row. The Lift row of the stop contract ends a stop on a status change (SPEC-0071). The `dispatch` contract states the stop condition too narrowly (SPEC-0076).

### `docs/spec/schemas/finding-basis.json`

The three shapes agree with BR-080, the BASIS entity, and the basis Scenario Outline of Rule FC-06. The enums of `effect`, `confidence`, `importance`, and `exposure` match BR-082 and BR-083. The check found no finding.

### `docs/spec/glossary.md`

The 23 terms of § Finding Classification Vocabulary agree with the feature file. "Waived" and "Register" are used as defined, and the avoided words `blocking_override`, "overridden", and `register.md` do not appear. "Priority" appears only as the arc42 scenario priority, which is not the concept of Severity. Three defects remain: the avoided word "reviewer" (SPEC-0077), three names for one person (SPEC-0078), and four undefined terms (SPEC-0079).

### `docs/spec/work/term-candidates.md`

The file holds no row with the status `proposed`, so the check found no finding.

### `docs/spec/work/finding-classification-qa-strategy.md`

Every Rule FC-01 to FC-21 has at least one contract row, and the boundary cases add tests that the Scenarios do not name. The Defect Severity Triage table uses the `Consequence` column that Rule FC-19 requires. The strategy plans FC-11-CT-03 for a register line that `HEAD` holds, but no Scenario backs it (SPEC-0075). No test row covers a `deferred` critical finding (SPEC-0071).

The specification has no area spec for this feature, as FC-G08 decided, so that check did not run.

## Traceability summary

- All 21 Rules appear in the scope map, the Actor-Goal Matrix, and the QA strategy. The review found no orphan.
- Each completion criterion of the proposal traces to a Rule or a gap in the gaps report.
- The entity model, the contracts, and the state machine cite BR-079 to BR-095, and `spec-lint` reports none of them as unreferenced.
- Gaps: the stop that ends on a status change (SPEC-0071), the missing rule for `deferred` (SPEC-0072), the register-line git check without a Scenario (SPEC-0075), and the proposal criterion that still counts 39 findings (note 3).

## Verdict

The specification is not ready for architecture. SPEC-0071 to SPEC-0074 block it. The requirements agent asks the stakeholder the `deferred` question of SPEC-0072 first, because the fix of SPEC-0071 depends on it. SPEC-0073 and SPEC-0074 change two Scenarios and two business rules. The five register lines do not block.

## Handoff

Requirements agent: the spec review found 4 open blocking findings, SPEC-0071 to SPEC-0074. Ask the stakeholder the `deferred` question of SPEC-0072, then fix SPEC-0072 to SPEC-0074, and hand SPEC-0071 to the domain-modeling agent.

## Pass 2

The fixes of pass 1 hold, and the specification now states the five stakeholder decisions of 2026-11-06 in every file. One new major finding blocks the next step. The fixes key the stop and the ban on `deferred` to the field `review_class`, and no rule keeps that field on a file. Three new minor findings go to the register, and six notes stay here.

Pass 2 read the specification at commit `df5c5cc18da0dbd78c2bcd61ced2eb6d49d1e076` on `dev`. It read the fixes of `410b5025`, `e34afaa0`, `e12b464c`, `db0381be`, `b321e298`, and `df5c5cc1` as one diff from `2b1a540f`, and then each changed section in full. The inputs are those of pass 1, with BR-109, DEC-55 to DEC-59, FC-G09, FC-G10, and FC-C18 to FC-C21 added. The stakeholder was not present, so the review filed the findings without the pause point.

### Reviewed specification, pass 2

- `docs/spec/features/finding-classification.feature`: 21 Rules and 141 Scenarios.
- `docs/spec/work/finding-classification-gaps.md`: FC-G09, FC-G10, and FC-C18 to FC-C21 added.
- `docs/spec/work/finding-classification-qa-strategy.md`, at `b321e298` and `df5c5cc1`.
- The finding-classification sections of the glossary, the entity model, the state machines, the validation rules (BR-079 to BR-095 and BR-109), and the interface contracts.
- `docs/spec/schemas/finding-basis.json`, unchanged since pass 1.
- `docs/spec/scope-map.md`, read only.
- `docs/proposals/finding-classification.md`, DEC-55 to DEC-59 and the changed sections of § Design.

`spec-lint`: `0 error(s), 0 warning(s), 58 info across 66 spec file(s).` The info lines are the four kinds that pass 1 dismissed, and none names BR-109 or a finding-classification file.

### Pass-1 findings

| ID        | Pass-1 record | Verdict  | Evidence                                                                                                                                                                                                                                                           |
| --------- | ------------- | -------- | ------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------ |
| SPEC-0071 | finding file  | resolved | BR-091, the stop contract, the `dispatch` sentence, and the Finding Lifecycle end a stop only on the confirmation. The Outline "Only the confirmation lifts the stop" covers `deferred`, `resolved`, a lower severity, and a removed file. SPEC-0080 is a new path |
| SPEC-0072 | finding file  | resolved | BR-086, the finding-file contract, the entity model, and the Finding Lifecycle let only the migration set `deferred` (DEC-55). BR-109 closes the path of a lowering (DEC-56). SPEC-0080 is a new path                                                              |
| SPEC-0073 | finding file  | resolved | Both Then steps name `origin/dev` and `origin/main`, and the word "only" is gone                                                                                                                                                                                   |
| SPEC-0074 | finding file  | resolved | BR-084 lets a suggestion of the consequence tree classes answer only false to `harms_downstream` and `fails_purpose`. The Scenario expects exit `1`, and a structural row backs it                                                                                 |
| SPEC-0075 | register line | fixed    | "A new register line gets the git check" and "A register line that HEAD holds is not checked again" cover BR-088 for register lines                                                                                                                                |
| SPEC-0076 | register line | fixed    | The `dispatch` sentence names both confirmation fields                                                                                                                                                                                                             |
| SPEC-0077 | register line | fixed    | The feature file and BR-080 say "the reviewer agent" in every place                                                                                                                                                                                                |
| SPEC-0078 | register line | fixed    | The feature file names the stakeholder where a person confirms, waives, lowers, or raises a finding, and the user where a person runs `validate` or commits. No structure file says "the human"                                                                    |
| SPEC-0079 | register line | fixed    | The glossary defines Migration Agent, Calibration Example, Child-Result Envelope, and Category                                                                                                                                                                     |

SPEC-0071 and SPEC-0072 stay resolved. Each fix closes the paths its finding names: an agent can no longer end a stop or leave the loop by a change of the status alone. SPEC-0080 needs a second edit, the deletion of `review_class`, so it is a new defect of the new text and gets its own ID.

### Semantic findings, pass 2

| ID        | Severity | Category | Characteristic | Location                                                    | Finding                                                                                                                                                                                                                      |
| --------- | -------- | -------- | -------------- | ----------------------------------------------------------- | ---------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| SPEC-0080 | major    | defect   | Complete       | `validation-rules.md:538`, BR-109 with BR-086 and BR-091    | An agent deletes `review_class` from BUG-0037 and sets `deferred` in one commit. The lint passes, because BR-086 skips a file without the field and BR-109 checks only severity and removal. The stop then ends unconfirmed. |
| SPEC-0081 | minor    | defect   | Consistent     | `state-machines.md:1005`, Lowered on **IN_LOOP**            | A finding confirmed only in the working tree is in **IN_LOOP**, whose Lowered event accepts the lowering. BR-109 rejects it until `HEAD` holds the confirmation.                                                             |
| SPEC-0082 | minor    | defect   | Verifiable     | `finding-classification-qa-strategy.md:235`, boundary table | The row still waits for FC-QG27, which line 282 and the stop contract answer.                                                                                                                                                |
| SPEC-0083 | minor    | defect   | Terminology    | `glossary.md` § Finding Classification Vocabulary           | Lower has no glossary entry, although BR-109 rules it and the Finding Lifecycle names the events Lowered and AgentLowers.                                                                                                    |

SPEC-0080 is a finding file with `status: open`. SPEC-0081 to SPEC-0083 are lines in `docs/findings/register/document.jsonl`, each with its owner in its `finding` text. SPEC-0080 is `major` because the planner who builds the lint from BR-086 and BR-109 builds the hole, and BR-091 then states a property that the rules do not deliver.

### Notes, pass 2

1. **The review loop reads the working tree only.** The loop greps `docs/findings/*.md` for `status: open` (glossary, Review Loop). An uncommitted agent change, such as `deferred`, a lower severity, or a removed file, drops a `major` finding from the loop until `finding-lint` runs at the next commit or `validate`. The stakeholder decided the `HEAD` read for the stop only (DEC-57). The architecture agent can check whether the loop step ends with a commit or a `validate` run, which closes the gap.
2. **DEC-57 reads as two rules.** It says that a confirmation in either version ends the stop, and then that a change in the working tree that nobody commits does not end a stop. BR-091 and FC-C19 state the meant rule: a confirmation in the working tree ends the stop, and every other change does not. The decision log is a record, so no fix is due.
3. **The gaps report says "the person".** FC-G10 says "for the person" and "only the person lowers a filed finding". The feature file and the structure files say the stakeholder.
4. **The stop notice uses BUG-0037 as a worked example.** BR-091 names the resolved BUG-0037 without `review_class` as a file that stops no run. The notice example and the FC-14 Scenarios show BUG-0037 as it would stand after a classification with `review_class: code`. When an agent has removed the file, the confirmation step names a path that the working tree lacks, so the stakeholder restores the file first.
5. **Override keys on a line that replaces nothing.** The entity model gives `override_by` and `override_reason` to a register line "only on a line that replaces a finding file". The register contract lets the schema allow them on any line, and no lint rule rejects them on another line. The guard keeps agents from writing them, so only the stakeholder can add such a line.
6. **The guard names no pass case for a register line.** The Passes row of `guard-human-fields` lists no new register line without override keys. Every review appends such lines. BR-092 refuses only a call that sets a human field, so the rule is exact, and the guard tests can add the case.

The question whether a register line should get an append-only status line instead of its deletion is an open design question for the architecture agent. The review files no finding on it.

### Structure checks, pass 2

- **`docs/spec/entity-model.md`**: FINDING_FILE and REGISTER_LINE carry the new status rule and the two override keys, and they agree with BR-086 and BR-109. Note 5 applies.
- **`docs/spec/state-machines.md`**: the new edges Raised, Lowered (major), and Lowered (minor) of **IN_LOOP** match the Mermaid diagram and the FC-10 Scenarios. The rejected events Deferred and Lowered on **STOPPING** match BR-086 and BR-109. Lowered on **IN_LOOP** lacks the `HEAD` guard (SPEC-0081).
- **`docs/spec/validation-rules.md`**: BR-109 names its attributes and traces to DEC-56, and FC-10 reaches each of its rules. Its rules for a `critical` finding carry DEC-58 and DEC-59, which FC-C20 and FC-C21 cite. BR-086, BR-091, and BR-109 leave `review_class` unguarded (SPEC-0080).
- **`docs/spec/interface-contracts.md`**: the finding-file, register-line, `finding-lint`, stop, and `guard-human-fields` contracts agree with BR-086, BR-091, BR-092, and BR-109. The stop notice states which version it reads (FC-QG27). Notes 4 and 6 apply.
- **`docs/spec/schemas/finding-basis.json`**: unchanged, and BR-084 asks nothing new of it. The check found no finding.
- **`docs/spec/glossary.md`**: the four entries of SPEC-0079 are in place, and Stop and Human Field follow BR-091 and BR-092. Lower has no entry (SPEC-0083).
- **`docs/spec/work/term-candidates.md`**: the file holds no row with the status `proposed`. The check found no finding.
- **`docs/spec/work/finding-classification-qa-strategy.md`**: every new Scenario has a contract row, and FC-10-CT-06, FC-10-CT-07, FC-10-IT-02, and FC-14-IT-09 own BR-109 and the `HEAD` read. The structural Outline has 23 rows, as the strategy counts. One row is stale (SPEC-0082).

### Traceability summary, pass 2

- All 21 Rules appear in the scope map, the Actor-Goal Matrix, and the QA strategy. The two renamed Rules, FC-14 and FC-18, carry the same names in all three.
- DEC-55 to DEC-59 each trace to a gap or a choice and to a Scenario: DEC-55 to FC-G09, DEC-56 to FC-G10, and DEC-57 to DEC-59 to FC-C19 to FC-C21.
- BR-109 is cited by the entity model, the state machines, the contracts, and the QA strategy, and `spec-lint` reports it as referenced.
- Gap: no Scenario covers a commit that deletes `review_class` from a filed finding (SPEC-0080).

### Verdict, pass 2

The specification is not ready for architecture. SPEC-0080 blocks it. Its fix is one rule in BR-109 and one Scenario in FC-10, and it needs no stakeholder decision. The three register lines do not block.

### Handoff, pass 2

Requirements agent: the spec review found 1 open blocking finding, SPEC-0080. Add the rule and the Scenario, and hand the mirror in the Finding Lifecycle and the `finding-lint` contract to the domain-modeling agent. Then run spec review pass 3.
