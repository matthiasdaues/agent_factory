---
type: inspect-spec
title: Spec review of the run-lifecycle wave-5 close
date: 2026-11-19
status: defects
reviewer: spec-review-agent
findings_filed: 4
story: run-lifecycle
scope: The specification changes of f83c3624..c127c4c7 on feature/run-lifecycle, read against packages/factory/scripts/dispatch and dispatch_lib.py at c127c4c7
---

# Spec review of the run-lifecycle wave-5 close

The three reviewed artifacts agree with each other and with the code as built. BR-113, BR-119, the `merge-story` and `close` bullets, the `dispatch` section schema, and the Prepare transition each describe what `dispatch` does. The new BR-113, however, contradicts three statements that the wave-5 commits did not change. Three major findings block, and each has its own owner:

- SPEC-0112: the feature Scenario "The next wave waits for the wave record" still expects `prepare-wave 2` to refuse without a wave record.
- SPEC-0113: the glossary term Wave Record still says that both prepare commands refuse without one.
- SPEC-0114: the QA row RL-11-IT-02 plans the same refusal, and the pending story ST-0421 copies it.

One minor finding, SPEC-0115, is a register file. BR-113 says that `prepare-wave` names a dependency that is not done, but the code skips a chain link of the same wave without a message.

This review confirms all ten `fixed` rows on core artifacts in the four spec-feedback reports and rejects none.

Spec review is the `document` class. The code of the wave lives on `feature/run-lifecycle`, the run's own workspace, and no story or code outside the run encodes the reviewed statements. So every finding answers `in_use: false`. The caller dispatched this review without the stakeholder, so the review filed the findings without the pause point. The stakeholder sees them first in this report.

Three known items are out of scope and have no finding:

- The ST-0425 row on ignored files such as `.env` stays `open` until the stakeholder decides.
- Orchestrated `prepare-wave` starts the next wave while an earlier entry is `failed` with a retry left. BR-113 describes this as the code behaves.
- `close --orphans` (ST-0426) and `add` (ST-0422) are not built yet.

## Reviewed specification

- The diff `git diff f83c3624..c127c4c7 -- docs backlog`, from the commits `47618a65` (domain modeling), `483896ec` (test strategy), and `c127c4c7` (planning, backlog only).
- `docs/spec/validation-rules.md`: BR-113 and BR-119, read with BR-116, BR-123, and BR-124.
- `docs/spec/interface-contracts.md`: the `prepare-wave`, `merge-story`, and `close` bullets, and the section `docs/testing.yaml` — `dispatch` section schema.
- `docs/spec/state-machines.md` § Ledger Entry Lifecycle: `On Prepare` and the note on Prepare.
- `docs/testing.yaml`: the new `dispatch` section.
- `docs/spec/work/spec-feedback-ST-0411.md`, `-ST-0416.md`, `-ST-0420.md`, and `-ST-0425.md`.
- `docs/spec/glossary.md`, `docs/spec/entity-model.md` (DISPATCH_LEDGER), `docs/spec/features/run-lifecycle.feature`, `docs/spec/work/run-lifecycle-qa-strategy.md`, and `backlog/ST-0421.md`, for consistency only.
- The code: `cmd_prepare_wave`, `cmd_prepare_story`, `_read_refuse_dirty_feature_worktree`, `_refuse_dirty_feature_worktree`, `cmd_merge_story`, and `cmd_close` with its helpers `_close_run_dir`, `_unmerged_feature_refusal`, `_run_worktrees`, `_stash_and_remove`, `_remove_run_dir`, and `_delete_run_branches` in `packages/factory/scripts/dispatch`. In `packages/factory/scripts/dispatch_lib.py`: `held_back`, `returned_dependencies`, `close_refusals`, `stash_name`, `drift_row_problems`, and `ROW_STATUSES`. The core list is `packages/factory/rulebooks/core-artifacts.yaml`.
- `docs/spec/scope-map.md`, read only.

`spec-lint --spec-dir docs/spec`: `spec-lint: 0 error(s), 0 warning(s), 57 info across 100 spec file(s).`

## Deterministic findings

| Rule     | Subject                                                              | Verdict                                                                           |
| -------- | -------------------------------------------------------------------- | --------------------------------------------------------------------------------- |
| GLOSS001 | Glossary terms that no spec file uses, such as Workstream Resolver   | Dismissed. None is a run lifecycle term, and the skill files no such case.        |
| TODO001  | Open items in `docs/spec/work/todo.md` and `docs/spec/work/todos.md` | Dismissed. No item concerns the reviewed range.                                   |
| TRACE003 | BR-011 to BR-054 defined but never referenced                        | Dismissed. BR-113 and BR-119 are referenced, and the rest is older.               |
| TRACE004 | `EPIC_BUILDING_BLOCK` in a relationship without an attribute block   | Dismissed. The entity belongs to the test-design entities, outside of this range. |

## Semantic findings

| ID        | Severity | Category | Type         | Characteristic | Artifact                                          | Finding                                                                                                                                                                                                             | Acted on by           |
| --------- | -------- | -------- | ------------ | -------------- | ------------------------------------------------- | ------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- | --------------------- |
| SPEC-0112 | major    | defect   | inconsistent | Consistent     | `docs/spec/features/run-lifecycle.feature:930`    | The Scenario "The next wave waits for the wave record" expects `prepare-wave 2` to exit non-zero when wave 1 has no wave record. BR-113, the state machine, and the code let wave 2 start once wave 1 has finished. | requirements-agent    |
| SPEC-0113 | major    | defect   | inconsistent | Terminology    | `docs/spec/glossary.md:177`                       | The definition of Wave Record says that `prepare-wave` and `prepare-story` refuse until the previous wave has one. BR-113 limits that check to `prepare-story` in a run by hand.                                    | domain-modeling-agent |
| SPEC-0114 | major    | defect   | inconsistent | Verifiable     | `docs/spec/work/run-lifecycle-qa-strategy.md:172` | The row RL-11-IT-02 plans the refusal of `prepare-wave 2` without a wave record, and the Evidence of the pending ST-0421 copies it. A test from the row fails against the built code.                               | test-strategy-agent   |
| SPEC-0115 | minor    | defect   | incorrect    | Consistent     | `docs/spec/validation-rules.md:175`               | BR-113 says that `prepare-wave` names each dependency that is not done. The code skips an entry whose dependency lies in the same wave without a message, because `prepare-story` prepares that link of the chain.  | domain-modeling-agent |

SPEC-0112, SPEC-0113, and SPEC-0114 share one cause. The wave-5 domain commit moved BR-113 and the state machine to the code, and three statements that cite the old rule stayed. The requirements agent fixes the Scenario first, because the QA row and ST-0421 derive from it. The planning agent then changes the Evidence line of ST-0421 to the new row.

## Structure checks

### `docs/spec/validation-rules.md`

BR-113 agrees with `cmd_prepare_wave`. The command refuses while an earlier-wave entry is not `done`, `failed`, or `blocked` and not held back, and it names each entry with its state. `held_back` and `returned_dependencies` match the definition of a held-back entry, directly or through another story. Orchestrated `prepare-story` checks no wave and refuses until its first dependency is `done` with a merge commit, as `cmd_prepare_story` does. The example with ST-0350, ST-0351, and ST-0352 holds. The check found SPEC-0115, and it found the contradictions SPEC-0112 to SPEC-0114 in the files that cite BR-113.

BR-119 agrees with `close_refusals`, `_unmerged_feature_refusal`, `_close_run_dir`, and `stash_name`. The close checks the branch name and the symlinks first, then the states, then the merge into `dev`. Each refusal exits `1` before any removal. The stash labels match `_run_worktrees`, and the date is local.

### `docs/spec/interface-contracts.md`

The `merge-story` bullet agrees with `cmd_merge_story`. The dry run skips `_refuse_dirty_feature_worktree`, so the key does not change its result. The `close` bullet agrees with `cmd_close`. A failure during the removals exits `1` and keeps the ledger, the stashes made before the failure are printed, and a foreign worktree in the run's folder keeps the folder with the line `kept <run folder>: ...` and exit `0`. A registered worktree inside a removed worktree is a failure, and one elsewhere in the run's folder only keeps the folder. The two sentences cover these two cases without a contradiction. The output lines match `_delete_run_branches`.

The `dispatch` section schema agrees with `_read_refuse_dirty_feature_worktree`. A missing file, section, or key means `true`. A value that is not a bool and a file that cannot be parsed both refuse after `premerge-check` passes, and the message names the file and the value. Only an orchestrated run reads the key. The check found nothing.

### `docs/spec/state-machines.md`

`On Prepare` and the note on Prepare agree with BR-113 and with the code. The pseudocode lists the checks of one entry, while `cmd_prepare_wave` checks the earlier waves before it looks at any entry. Both orders leave a refused entry **PENDING**, so the order needs no finding. The check found nothing.

### `docs/spec/glossary.md`

The check found SPEC-0113. It found no second term for a concept of the range and no avoided term in use.

### `docs/spec/work/term-candidates.md`

The file holds no row with status `proposed`. The check found nothing.

### `docs/testing.yaml`

The new top-level `dispatch` section holds `refuse_dirty_feature_worktree: true` and parses as a bool. Its comment says what the key does and that a missing key means `true`.

## Spec-feedback rows on core artifacts

The core list is `packages/factory/rulebooks/core-artifacts.yaml`. `drift_row_problems` keeps a wave open while a row on a core artifact is `fixed`. So the reviewer sets `confirmed` or `rejected`, the values of `ROW_STATUSES`.

| Report                     | Artifact                           | Drift                                                     | Verdict     | Reason                                                                                                          |
| -------------------------- | ---------------------------------- | --------------------------------------------------------- | ----------- | --------------------------------------------------------------------------------------------------------------- |
| `spec-feedback-ST-0416.md` | `docs/testing.yaml`                | No `dispatch` section                                     | `confirmed` | The section holds `refuse_dirty_feature_worktree: true`.                                                        |
| `spec-feedback-ST-0416.md` | `docs/spec/interface-contracts.md` | No outcome for a value other than a bool                  | `confirmed` | The schema row names the refusal, the exit `1`, and the message, as `_read_refuse_dirty_feature_worktree` does. |
| `spec-feedback-ST-0416.md` | `docs/spec/interface-contracts.md` | `--dry-run` and the worktree check                        | `confirmed` | The bullet says that the dry run does not check the worktree, as `cmd_merge_story` does.                        |
| `spec-feedback-ST-0420.md` | `docs/spec/state-machines.md`      | Prepare checks the wave record in an orchestrated run     | `confirmed` | `On Prepare` and its note give both checks and the held-back entry.                                             |
| `spec-feedback-ST-0420.md` | `docs/spec/validation-rules.md`    | BR-113 checks the wave record in an orchestrated run      | `confirmed` | BR-113 gives both checks and defines the held-back entry. SPEC-0115 covers one message, not this drift.         |
| `spec-feedback-ST-0425.md` | `docs/spec/validation-rules.md`    | BR-119 omits `prepared`, `dispatching`, and `dispatched`  | `confirmed` | BR-119 refuses the three states and gives the reason, as `close_refusals` does.                                 |
| `spec-feedback-ST-0425.md` | `docs/spec/validation-rules.md`    | BR-119 names only the stash of a story worktree           | `confirmed` | BR-119 names the labels `<id>`, `feature`, and `premerge/<id>`, with an example.                                |
| `spec-feedback-ST-0425.md` | `docs/spec/validation-rules.md`    | No rule for a missing feature branch or `dev`             | `confirmed` | BR-119 refuses and names `dispatch close --drop`, as `_unmerged_feature_refusal` does.                          |
| `spec-feedback-ST-0425.md` | `docs/spec/interface-contracts.md` | The `close` bullet omits failures, kept folder, and lines | `confirmed` | The bullet lists the four failures, the kept folder, and the four output lines with the last line.              |
| `spec-feedback-ST-0425.md` | `docs/spec/validation-rules.md`    | No rule for a bad branch name or a symlink                | `confirmed` | BR-119 refuses both with exit `1` and keeps the ledger, as `_close_run_dir` does.                               |

`spec-feedback-ST-0411.md` has no row on a core artifact. The `open` ST-0425 row on ignored files and the rows on `implement-issue/SKILL.md` and the QA strategy stay as they are.

## Prior findings

SPEC-0109 and SPEC-0110 of the wave-4 review are `resolved`. SPEC-0111, the missing Scenarios for the refused amend, the refused `git reset --keep`, and `return-story` without a status line, stays `open`, because the range does not change the feature file. The open register files SPEC-0056 to SPEC-0070 concern the counter-ids feature and lie outside this range. This pass inspected the reviewed artifacts fresh and did not only check the prior list.

## Traceability summary

BR-113 and BR-119 each trace to Scenarios of `run-lifecycle.feature` and to the code. The Scenario at line 930 traces to BR-113 but states the old rule (SPEC-0112). `docs/spec/scope-map.md` was read only, and the review files nothing on its content. No orphan or gap was found in the BR cross-references of the range.

## Repeat pass

The repeat pass reviews `8737eb88..87cc12ca`, the commit `87cc12ca` of the domain-modeling agent. All three majors and the minor finding are now `resolved`, and no new finding is filed. So the wave-5 specification changes pass.

The three majors had one cause. The first pass read the rewrite of BR-113 in `47618a65` as the rule, but that rewrite described the code before ST-0421. The pending ST-0421 builds the wave-record check for both prepare commands, under its Domain Rule and BR-064. So `87cc12ca` puts BR-113 and `On Prepare` back to the target rule, and it leaves the feature file, the glossary, and the QA strategy unchanged.

| ID        | Verdict    | Evidence                                                                                                                                                                                                                           |
| --------- | ---------- | ---------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| SPEC-0112 | `resolved` | BR-113 and `On Prepare` say that both commands refuse until the previous wave has a wave record. The Scenario at `run-lifecycle.feature:930` says the same.                                                                        |
| SPEC-0113 | `resolved` | The glossary definition of Wave Record and BR-113 state the same rule.                                                                                                                                                             |
| SPEC-0114 | `resolved` | The row RL-11-IT-02 and the Evidence line of ST-0421 plan the check that BR-113 now defines and that ST-0421 builds.                                                                                                               |
| SPEC-0115 | `resolved` | BR-113 now says that `prepare-wave` names a dependency in an earlier wave and prints nothing for a dependency in the same wave, with the ST-0350, ST-0351 example. This matches the `same_wave_deps` branch of `cmd_prepare_wave`. |

Until ST-0421 merges, `cmd_prepare_wave` still reads the states of the earlier waves and not the wave record. That gap is the known work of ST-0421, so this review files no finding on it.

The two rows of `spec-feedback-ST-0420.md` stay `confirmed`. `87cc12ca` adds the sentence "ST-0421 builds the check for `prepare-wave` and the orchestrated `prepare-story` (BR-064)" to each row. The fix now holds as a target rule with the story that builds it.

One verdict of the first pass is corrected. The `docs/testing.yaml` row of `spec-feedback-ST-0416.md` goes back to `fixed`. The test-strategy agent declares `reviewed_by: [stakeholder]` for that file, so the stakeholder confirms the row, not the spec reviewer. The row keeps the wave open until the stakeholder sets it. The other nine verdicts on core artifacts stand.

This repeat pass checks only the four findings and the changed rows, as the coordinator asked. It does not run the full inspection again.
