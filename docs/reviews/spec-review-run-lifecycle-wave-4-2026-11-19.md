---
type: inspect-spec
title: Spec review of the run-lifecycle wave-4 close
date: 2026-11-19
status: pass
reviewer: spec-review-agent
findings_filed: 3
story: run-lifecycle
scope: The specification changes of 20ae7ecc..8537e747 on feature/run-lifecycle, read against packages/factory/scripts/dispatch and dispatch_lib.py at 8537e747
---

# Spec review of the run-lifecycle wave-4 close

The wave-4 specification changes are not ready. Two major findings block. SPEC-0109: BR-124 and a note of the state machine keep a merge that git refuses in an orchestrated run `dispatched`, while BR-116, the feature file, the area spec and the code set it `blocked`. SPEC-0110: the `merge-story` contract does not say whether the rerun after a refused amend meets the dirty-worktree refusal that ST-0416 builds. One minor finding, SPEC-0111, is a register file: three new refusals have no Scenario. The six rows of the two spec-feedback reports hold their fixes.

Spec review is the `document` class. The code of ST-0410 and ST-0419 lives on `feature/run-lifecycle`, the run's own workspace, and no story or code outside the run encodes the changed statements. So every finding answers `in_use: false`. The stakeholder was not present, so the review filed the findings without the pause point. The stakeholder sees them first in this report.

Two known gaps are out of scope and have no finding. `return-story` of a finding still writes `backlog/<id>.md` in the code, and ST-0422 changes that. `add` and `close` appear in the BR-091 Examples but are not built yet.

## Reviewed specification

- The diff `git diff 20ae7ecc..8537e747 -- docs/spec docs/arc42 backlog`, 12 files, from the commits `0e53d6aa`, `dc1448ea`, `087110b6`, `b18dd12c`, `81f710e8` and `8537e747`. `0f59fb41` changes only the scope of the review.
- `docs/spec/validation-rules.md`: BR-116 and BR-118, read with BR-091 and BR-124.
- `docs/spec/interface-contracts.md`: the `merge-story` and `return-story` bullets.
- `docs/spec/state-machines.md` § Ledger Entry Lifecycle: `On Block` and the Notes.
- `docs/spec/features/run-lifecycle.feature`: the `mark-done` Scenario, the Outline "A story stops in the state that names its cause", and the BR-124 Scenarios.
- `docs/spec/features/finding-classification.feature`: the two stop Outlines.
- `docs/spec/areas/mechanized-dispatch.md`: Story Lifecycle.
- `docs/spec/work/spec-feedback-ST-0410.md` and `docs/spec/work/spec-feedback-ST-0419.md`.
- `docs/spec/entity-model.md` (DISPATCH_LEDGER), `docs/spec/glossary.md`, `docs/spec/work/run-lifecycle-qa-strategy.md` and `docs/arc42/06_runtime_view.md`, for consistency only.
- The code: `cmd_return_story`, `cmd_merge_story`, `_amend_status_into_merge_commit`, `_amend_hook_names` and `build_parser` in `packages/factory/scripts/dispatch`, and `STOP_SUBCOMMANDS` and `READ_SUBCOMMANDS` in `packages/factory/scripts/dispatch_lib.py`.
- `docs/spec/scope-map.md`, read only.

`spec-lint --spec-dir docs/spec`: `spec-lint: 0 error(s), 0 warning(s), 57 info across 96 spec file(s).`

## Deterministic findings

| Rule     | Subject                                                              | Verdict                                                                     |
| -------- | -------------------------------------------------------------------- | --------------------------------------------------------------------------- |
| GLOSS001 | Glossary terms that no spec file uses, such as Workstream Resolver   | Dismissed. None is a run lifecycle term, and the skill files no such case.  |
| TODO001  | Open items in `docs/spec/work/todo.md` and `docs/spec/work/todos.md` | Dismissed. No item concerns the reviewed range.                             |
| TRACE003 | BR-011 to BR-054 defined but never referenced                        | Dismissed. BR-116, BR-118 and BR-124 are referenced, and the rest is older. |
| TRACE004 | `EPIC_BUILDING_BLOCK` in a relationship without an attribute block   | Dismissed. The entity belongs to the test-design entities, outside scope.   |

## Semantic findings

| ID        | Severity | Category   | Type         | Characteristic | Artifact                                          | Finding                                                                                                                                                                                                                                               | Acted on by           |
| --------- | -------- | ---------- | ------------ | -------------- | ------------------------------------------------- | ----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- | --------------------- |
| SPEC-0109 | major    | defect     | inconsistent | Consistent     | `docs/spec/validation-rules.md:186`               | BR-124 and the note "A refused merge is no edge" keep a merge that git refuses `dispatched` on both ways. BR-116, `On Block`, the feature Outline, the area Scenario and the code set it `blocked` in an orchestrated run.                            | domain-modeling-agent |
| SPEC-0110 | major    | defect     | incomplete   | Complete       | `docs/spec/interface-contracts.md:39`             | The rerun after a refused amend meets a worktree with a change to `backlog/<id>.md`. No sentence says whether the dirty-worktree refusal of ST-0416 and `premerge-check` run again, so the plain reading blocks the recovery.                         | domain-modeling-agent |
| SPEC-0111 | minor    | defect     | untraced     | Verifiable     | `docs/spec/features/run-lifecycle.feature:477`    | The refused amend, the refused `git reset --keep`, and `return-story` on a file without a status line have no Scenario.                                                                                                                               | requirements-agent    |
| —         | note     | suggestion | unverifiable | Verifiable     | `docs/spec/areas/mechanized-dispatch.md:451`      | The area Scenario says "the merge is aborted via git merge --abort". When git refuses a merge over an untracked file, no merge starts, so the step names a call and no observable result. "feature/login keeps its tip" would say what a test checks. | requirements-agent    |
| —         | note     | suggestion | inconsistent | Consistent     | `docs/spec/work/run-lifecycle-qa-strategy.md:126` | The row RL-06-IT-01 still says "a merge conflict" leaves the story `blocked`. The Outline now names the merge that git refuses over an untracked file in an orchestrated run.                                                                         | test-strategy-agent   |

## Structure checks

### `docs/spec/validation-rules.md`

BR-116 names the fields `reason` and `returned` of the entity model and traces to the Outline "A story stops in the state that names its cause". BR-118 names `status` of the backlog file and traces to "Only dispatch merge-story sets a story to done". The check found SPEC-0109 between BR-116 and BR-124. BR-091 lists the same subcommands as both Outlines of `finding-classification.feature` and as `STOP_SUBCOMMANDS` and `READ_SUBCOMMANDS`, apart from the known `add` and `close`.

### `docs/spec/interface-contracts.md`

The `return-story` bullet agrees with `cmd_return_story`. The command refuses a state other than `failed` or `blocked` with exit `1`. It writes `status: pending` into `backlog/<id>.md` of the current checkout, and commits nothing. On a missing file or a missing status line, it exits `1`, names the file, and saves no ledger. The `merge-story` bullet agrees with the code on the amend, the hook names, the rerun at `HEAD`, the status read from `HEAD`, and `git reset --keep`. The check found SPEC-0110.

### `docs/spec/state-machines.md`

The edges agree with the Scenarios and with `VALID_TRANSITIONS`. The `On Block` comment and the note on refused merges contradict each other, as SPEC-0109 describes. The new sentence on the two refusals after the merge agrees with the code.

### `docs/spec/features/run-lifecycle.feature` and `finding-classification.feature`

The `mark-done` Scenario now points to `build_parser`, which has no `mark-done` subcommand. The Outline rows hold in an orchestrated run and match `cmd_merge_story`. The two stop Outlines match BR-091. SPEC-0111 names the missing Scenarios.

### `docs/spec/areas/mechanized-dispatch.md`

The Story Lifecycle Scenario now sets the orchestrated run and the untracked file, and it agrees with the feature Outline. One `note` row covers the `git merge --abort` step.

### Spec-feedback reports

All six rows of `spec-feedback-ST-0410.md` and `spec-feedback-ST-0419.md` are `fixed`, and each fix holds in the artifact it names. `docs/arc42/06_runtime_view.md` and `finding-classification.feature` no longer list `mark-done`. The QA strategy names `tests/factory/test_run_lifecycle_dispatch.py` for RL-06-IT-02 and drops the edge case of a moved feature branch. The `return-story` contract and the feature Outline carry the requested text. The spec-feedback skill lets the owner's reviewer set `confirmed`. This review changes no reviewed artifact, so the rows stay `fixed` until their owners' reviewers confirm them.

### Glossary

The changed text uses Unit of Work, Ledger, orchestrated, by hand, Feature Branch, Story Branch and Primary Checkout as the glossary defines them. The check found no avoided term and no second term for one concept.

### Term candidates

`docs/spec/work/term-candidates.md` holds no row with status `proposed`.

### Entity model

DISPATCH_LEDGER holds `reason`, `returned` and `commit_sha`, which the changed rules use. The check found no defect.

## Traceability summary

- Every changed rule traces to a Rule of `run-lifecycle.feature` or `finding-classification.feature` in the scope map.
- Three new refusals of BR-118 and the contract bullets have no Scenario (SPEC-0111).
- No open `SPEC` finding file existed before this pass, so no prior finding needed a check.

## Next step

The domain-modeling agent fixes SPEC-0109 and SPEC-0110. The requirements agent adds the Scenarios of SPEC-0111. A repeat pass of the spec review then checks both majors.

## Repeat pass

The repeat pass checked only `11dbeaac..b421bdad`, as the coordinator set the scope. Both major findings are now `resolved`, so no blocking finding stays open. The stakeholder approved the resolutions on 2026-11-19. SPEC-0111 and the two `note` rows go to the reconciliation after the run and stay as they are.

| ID        | Severity | Verdict  | What the review checked                                                                                                                                                                                                                                                                         |
| --------- | -------- | -------- | ----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| SPEC-0109 | major    | resolved | `affcf8aa` limits the refused checkout and merge of BR-124 to a run by hand and points to BR-116 for the orchestrated `blocked` case. The state-machine note and the `merge-story` bullet say the same. `a97692ea` adds the case to arc42 § 6.24.1. The rules now agree with `cmd_merge_story`. |
| SPEC-0110 | major    | resolved | `affcf8aa` states in BR-118, BR-124, the state-machine note and the `merge-story` bullet that the rerun runs no refresh, no `premerge-check`, no merge and no dirty-worktree refusal. By hand, it starts on the feature branch. `b421bdad` adds the rule and RL-08-IT-16 to ST-0416.            |
| SPEC-0111 | minor    | deferred | The finding goes to the reconciliation after the run, by the coordinator's instruction. The register file stays `open`.                                                                                                                                                                         |

The three commits change no other statement, and the pass found no new defect in them. The next step is the architecture agent, or the next wave of the run.
