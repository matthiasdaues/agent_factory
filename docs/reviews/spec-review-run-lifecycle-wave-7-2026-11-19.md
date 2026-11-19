---
type: inspect-spec
title: Spec review of the run-lifecycle wave-7 close
date: 2026-11-19
status: pass
reviewer: spec-review-agent
findings_filed: 2
story: run-lifecycle
scope: The specification changes of de34d719..c8a5e531 on feature/run-lifecycle, read against packages/factory/scripts/dispatch, dispatch_lib.py and premerge-check at de34d719
---

# Spec review of the run-lifecycle wave-7 close

The wave-7 specification changes pass, because no finding blocks. BR-115, BR-116, and BR-117 agree with each other and with the code that ST-0422 built. The same holds for the `merge-story`, `premerge-check`, `add`, and Reads entries of the contracts and for the PENDING `On Block` comment. The code under `packages/factory/scripts/` did not change after `de34d719`.

The review filed two minor findings as register files:

- SPEC-0118: the contract bullet on `prepare-wave` and `prepare-story` still says that an orchestrated run creates a story worktree, and it does not mention a reused entry. The domain-modeling agent adds one sentence that points to BR-117.
- SPEC-0119: no Scenario traces the new file limit at `escalate` or the next attempt on a reused branch. The requirements agent adds two Scenarios.

This review confirms all six `fixed` rows on core artifacts in `spec-feedback-ST-0422.md` and rejects none.

Spec review is the `document` class. The code of the wave lives on `feature/run-lifecycle`, the run's own workspace, and no story or code outside the run encodes the reviewed statements. So every finding answers `in_use: false`. The caller dispatched this review without the stakeholder, so the review filed the findings without the pause point. The stakeholder sees them first in this report.

Three known items are out of scope and have no finding:

- The default tier of a finding is `economy`, the stakeholder's decision A of 2026-11-19.
- By hand, `prepare-story` on a reused branch also refuses an untracked file. That is a follow-up story after the run.
- `mechanized-dispatch.md:474` still says that the finding's `artifact` serves the overlap planning. That goes to the reconciliation.

## Reviewed specification

- The diff `git diff de34d719..c8a5e531`, from the commits `ec0db6a3` and `c8a5e531` of the domain-modeling agent.
- `docs/spec/validation-rules.md`: BR-115, BR-116, and BR-117, read with BR-113 and BR-114.
- `docs/spec/interface-contracts.md`: the Reads row of `dispatch`, the `prepare-wave` and `prepare-story`, `add`, and `merge-story` bullets, the `premerge-check` table, its first paragraph, and the Story merge paragraph.
- `docs/spec/state-machines.md` § Ledger Entry Lifecycle: the PENDING `On Block` comment and the Mermaid edge `PENDING --> BLOCKED`.
- `docs/spec/work/spec-feedback-ST-0422.md`.
- `docs/spec/glossary.md`, `docs/spec/features/run-lifecycle.feature` (the Rule on findings as units of work and the escalation Scenarios), and `backlog/ST-0423.md` and `ST-0430.md`, for consistency only.
- The code: `_story_scope_violation`, `_unit_scope`, `_scaled_max_files`, `_reuse_story_workspace`, `cmd_prepare_wave`, `_prepare_story_by_hand`, `cmd_prepare_story`, `_refresh_story_branch`, `_finding_text`, `cmd_add`, and `cmd_return_story` in `packages/factory/scripts/dispatch`. In `packages/factory/scripts/dispatch_lib.py`: `add_finding`, `next_free_wave`, the entry tier fallback, and the transition table. In `packages/factory/scripts/premerge-check`: `story_owned_files`, `merge_base`, the diff with `--no-renames`, and `check_out_of_scope`. The core list is `packages/factory/rulebooks/core-artifacts.yaml`.
- `docs/spec/scope-map.md`, read only.

`spec-lint --spec-dir docs/spec`: `spec-lint: 0 error(s), 0 warning(s), 57 info across 104 spec file(s).`

## Deterministic findings

| Rule     | Subject                                                              | Verdict                                                                           |
| -------- | -------------------------------------------------------------------- | --------------------------------------------------------------------------------- |
| GLOSS001 | Glossary terms that no spec file uses, such as Workstream Resolver   | Dismissed. None is a run lifecycle term, and the skill files no such case.        |
| TODO001  | Open items in `docs/spec/work/todo.md` and `docs/spec/work/todos.md` | Dismissed. No item concerns the reviewed range.                                   |
| TRACE003 | BR-011 to BR-054 defined but never referenced                        | Dismissed. BR-115 to BR-117 are referenced, and the rest is older.                |
| TRACE004 | `EPIC_BUILDING_BLOCK` in a relationship without an attribute block   | Dismissed. The entity belongs to the test-design entities, outside of this range. |

## Semantic findings

| ID        | Severity | Category | Type       | Characteristic | Artifact                                       | Finding                                                                                                                                                                                                                          | Acted on by           |
| --------- | -------- | -------- | ---------- | -------------- | ---------------------------------------------- | -------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- | --------------------- |
| SPEC-0118 | minor    | defect   | incomplete | Complete       | `docs/spec/interface-contracts.md:33`          | The bullet says that an orchestrated `prepare-wave` creates a story worktree and points only to BR-113. BR-117 keeps the worktree of a reused entry, refreshes the branch, and refuses or blocks. The bullet names none of this. | domain-modeling-agent |
| SPEC-0119 | minor    | defect   | untraced   | Verifiable     | `docs/spec/features/run-lifecycle.feature:966` | No Scenario traces the file limit at `escalate` (BR-115), and none traces the refresh, the refusals, or the `refresh conflict` block of a reused branch (BR-117, BR-116).                                                        | requirements-agent    |

Two notes stay rows of this report and need no change now:

| Note                                                                                                                                                                                                                                                    | Artifact                                | Severity |
| ------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- | --------------------------------------- | -------- |
| The PENDING `On Block` comment names only the refresh conflict of a reused branch. `dispatch mark-blocked` also moves a `pending` entry to `blocked`, so the comment reads as the only cause. Writing "for example" before it would fix the reading.    | `docs/spec/state-machines.md:1144`      | note     |
| `_story_scope_violation` returns a violation when the diff of the branch is empty, so `escalate` records `escalate refused: scope` for a branch without a commit. BR-115 does not name that case. An empty branch after three counted attempts is rare. | `packages/factory/scripts/dispatch:582` | note     |

## Structure checks

### `docs/spec/validation-rules.md`

BR-115 agrees with `_story_scope_violation`. The diff runs from the entry's feature branch to its branch, with `--no-renames`, as in `premerge-check`. The scope and the limit come from `_unit_scope`, so `escalate` and `merge-story` use the same values: `max(20, len(outputs) * 2)` for a story and 20 for a finding. The files of the unit of work stay out of the count. A finding has no scope entries, and `check_out_of_scope` skips the scope check then, so only the file limit applies, as the rule says.

BR-116 and BR-117 agree with `_reuse_story_workspace`, `cmd_prepare_wave`, `_prepare_story_by_hand`, and `_refresh_story_branch`. An orchestrated `prepare-wave` refuses with exit `1` when `git worktree list` reports no worktree of the branch at the entry's path. Both commands merge nothing when the branch already contains the feature branch. They refuse a dirty checkout and abort a conflicting merge with the reason `refresh conflict` and the state `blocked`. After a block, `prepare-wave` saves the ledger, goes on with the other entries, and exits `1`. By hand, `_undo_checkout_by_hand` checks out the previous branch after each refusal that follows the checkout. Orchestrated `prepare-story` refuses an entry without dependencies, so it never prepares a reused finding. `add_finding` resets the attempts, the grants, the tier, the reason, and `returned`, keeps the branch, and writes the next free wave.

BR-116 now says that a refresh conflict of a reused branch sets `blocked` on both ways. That agrees with its earlier sentence that only an orchestrated run blocks on the refresh conflict of a merge, because the two sentences name different commands.

### `docs/spec/interface-contracts.md`

The Reads row of `dispatch` agrees with `_finding_text`, which reads the finding at `refs/heads/<feature-branch>` and falls back to the current checkout. The `add` bullet points to BR-117 and says nothing that differs from it. The `merge-story` bullet and the Story merge paragraph agree with `story_owned_files`. The `story` field counts at the merge base for a file that exists there, and at the branch head for a new file. A deleted file exists at the merge base, so its field counts there. The first paragraph of `premerge-check` names `git diff --no-renames <target>...<branch>`, as the code runs it. The check found SPEC-0118 in the bullet on `prepare-wave` and `prepare-story`.

### `docs/spec/state-machines.md`

The PENDING `On Block` transition exists in the pseudocode, in the Mermaid edge `PENDING --> BLOCKED`, and in the transition table of `dispatch_lib.py`. The new comment names a real cause of the transition. The narrow reading of the comment is a note above.

### `docs/spec/glossary.md`

The range adds no term. The check found no second term for a concept of the range and no avoided term in use.

### `docs/spec/work/term-candidates.md`

The file holds no row with status `proposed`. The check found nothing.

### Pending stories

No pending story owns SPEC-0118 or SPEC-0119. ST-0423 touches `premerge-check`, `mutation-testing`, and `implementation-agent.md`, but neither the contract bullet nor the feature file. ST-0430 touches `docs/spec/` for one vocabulary, not for new Scenarios or new contract content.

## Spec-feedback rows on core artifacts

The core list is `packages/factory/rulebooks/core-artifacts.yaml`. The reviewer sets each `fixed` row on a core artifact to `confirmed` or `rejected`.

| Report                     | Artifact                           | Drift                                           | Verdict     | Reason                                                                                                                                            |
| -------------------------- | ---------------------------------- | ----------------------------------------------- | ----------- | ------------------------------------------------------------------------------------------------------------------------------------------------- |
| `spec-feedback-ST-0422.md` | `docs/spec/interface-contracts.md` | The `story` field at the merge base (IMPL-0027) | `confirmed` | The `merge-story` bullet, the Reads row, and the Story merge paragraph name the merge base, as `story_owned_files` reads it.                      |
| `spec-feedback-ST-0422.md` | `docs/spec/validation-rules.md`    | BR-115 and the file limit at `escalate`         | `confirmed` | BR-115 applies the scope check and the file limit of `merge-story`, as `_story_scope_violation` does.                                             |
| `spec-feedback-ST-0422.md` | `docs/spec/validation-rules.md`    | No rule names the default tier                  | `confirmed` | BR-117 names `economy`, the fallback of the entry tier in `dispatch_lib.py`, and the stakeholder's decision A.                                    |
| `spec-feedback-ST-0422.md` | `docs/spec/validation-rules.md`    | The `artifact` and the overlap planning         | `confirmed` | BR-117 says that no planning step reads the `artifact`, because `add_finding` puts each finding alone into a new wave.                            |
| `spec-feedback-ST-0422.md` | `docs/spec/interface-contracts.md` | The commit from which `add` reads the finding   | `confirmed` | The Reads row names the head of the feature branch, else the current checkout, as `_finding_text` does.                                           |
| `spec-feedback-ST-0422.md` | `docs/spec/validation-rules.md`    | The next attempt on a reused branch             | `confirmed` | BR-117 defines the kept worktree, the refresh, the refusals, and the block, as the code does. SPEC-0118 covers the contract bullet, not this row. |

The report holds no row on `docs/testing.yaml`.

## Prior findings

SPEC-0111, SPEC-0116, and SPEC-0117 stay `open`, because the range changes neither the feature file nor `docs/arc42/`. SPEC-0119 is the same kind of gap as SPEC-0111 and SPEC-0116, and the requirements agent can fix all three in one pass. The open register files SPEC-0056 to SPEC-0070 concern the counter-ids feature and lie outside this range. This pass inspected the reviewed artifacts fresh and did not only check the prior list.

## Traceability summary

BR-115 traces to the escalation Scenarios, and BR-117 traces to the Rule "Implementation agent runs a blocking finding from the feature checks as a unit of work". The new parts of both rules have no Scenario (SPEC-0119). The citations IMPL-0027, IMPL-0056, IMPL-0057, and RL-G20 in the range each name an existing item. `docs/spec/scope-map.md` was read only, and the review files nothing on its content.
