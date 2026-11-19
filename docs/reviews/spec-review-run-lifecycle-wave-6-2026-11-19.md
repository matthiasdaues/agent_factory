---
type: inspect-spec
title: Spec review of the run-lifecycle wave-6 close
date: 2026-11-19
status: pass
reviewer: spec-review-agent
findings_filed: 2
story: run-lifecycle
scope: The specification changes of 471f051a..4a02b2aa on feature/run-lifecycle, read against packages/factory/scripts/dispatch, dispatch_lib.py and premerge-check at 4a02b2aa
---

# Spec review of the run-lifecycle wave-6 close

The wave-6 specification changes pass, because no finding blocks. BR-120, the new BR-125, and the `close`, `close-wave`, and `premerge-check` contracts agree with each other, with BR-113, with the Prepare transition, and with the code as built. BR-125 is a new number that no file used before commit `28ec0830`.

The review filed two minor findings as register files:

- SPEC-0116: four new rules of the feature merge in `premerge-check` have no Scenario and no QA row. The requirements agent adds them.
- SPEC-0117: the runtime view of arc42 still says that `--orphans` cleans up branches, and it cites only BR-120. The architecture agent fixes the sentence.

This review confirms all fifteen `fixed` rows on core artifacts in the three spec-feedback reports and rejects none.

Spec review is the `document` class. The code of the wave lives on `feature/run-lifecycle`, the run's own workspace, and no story or code outside the run encodes the reviewed statements. So every finding answers `in_use: false`. The caller dispatched this review without the stakeholder, so the review filed the findings without the pause point. The stakeholder sees them first in this report.

Three known items are out of scope and have no finding:

- Ignored files, such as `.env`, go with their worktree (BR-119). The stakeholder decided this on 2026-11-19.
- A SHA of `dev` gets no feature checks (IMPL-0052, IMPL-0054).
- `dispatch add` (ST-0422) is not built yet.

## Reviewed specification

- The diff `git diff 471f051a..4a02b2aa`, from the commits `28ec0830` (domain modeling), `d38f16c9` (test strategy), and `4a02b2aa` (planning, backlog only).
- `docs/spec/validation-rules.md`: BR-119, BR-120, and BR-125, read with BR-062, BR-111 to BR-113, BR-116, and the rules of `close-wave <N>`.
- `docs/spec/interface-contracts.md`: the `close` bullet with its `--orphans` part, the `premerge-check` table and its Feature merge paragraph, and the `close-wave` table.
- `docs/spec/state-machines.md` § Ledger Entry Lifecycle: `On Prepare`.
- `docs/spec/work/spec-feedback-ST-0421.md`, `-ST-0424.md`, and `-ST-0426.md`.
- `docs/spec/glossary.md`, `docs/spec/features/run-lifecycle.feature` (the Rules on the feature merge and on `--orphans`), `docs/spec/work/run-lifecycle-qa-strategy.md`, `docs/arc42/06_runtime_view.md`, and `backlog/ST-0422.md`, `ST-0423.md`, `ST-0426.md`, and `ST-0430.md`, for consistency only.
- The code: `_untracked_ledgers`, `_find_ledgers`, `_LedgerClaim`, `_claim_of`, `_tracked_by`, `_removal_refusal`, `_sort_ledgers`, `_orphan_keep_reason`, and `cmd_close_orphans` in `packages/factory/scripts/dispatch`. In `packages/factory/scripts/dispatch_lib.py`: `held_back`, `close_refusals`, `orphan_stash_name`, `orphan_ledger_verdict`, and the row check of `close-wave`. In `packages/factory/scripts/premerge-check`: `is_feature_merge`, `names_dev`, `ledger_path`, `check_run_state`, the test suite check, and the file limit in `main`. The core list is `packages/factory/rulebooks/core-artifacts.yaml`.
- `docs/spec/scope-map.md`, read only.

`spec-lint --spec-dir docs/spec`: `spec-lint: 0 error(s), 0 warning(s), 57 info across 103 spec file(s).`

## Deterministic findings

| Rule     | Subject                                                              | Verdict                                                                           |
| -------- | -------------------------------------------------------------------- | --------------------------------------------------------------------------------- |
| GLOSS001 | Glossary terms that no spec file uses, such as Workstream Resolver   | Dismissed. None is a run lifecycle term, and the skill files no such case.        |
| TODO001  | Open items in `docs/spec/work/todo.md` and `docs/spec/work/todos.md` | Dismissed. No item concerns the reviewed range.                                   |
| TRACE003 | BR-011 to BR-054 defined but never referenced                        | Dismissed. BR-120 and BR-125 are referenced, and the rest is older.               |
| TRACE004 | `EPIC_BUILDING_BLOCK` in a relationship without an attribute block   | Dismissed. The entity belongs to the test-design entities, outside of this range. |

## Semantic findings

| ID        | Severity | Category | Type         | Characteristic | Artifact                                        | Finding                                                                                                                                                                                                                                                                                     | Acted on by        |
| --------- | -------- | -------- | ------------ | -------------- | ----------------------------------------------- | ------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- | ------------------ |
| SPEC-0116 | minor    | defect   | untraced     | Verifiable     | `docs/spec/features/run-lifecycle.feature:1086` | The feature merge refuses a missing or unreadable ledger, a `pending` unit of work that no return holds back, and a `docs/testing.yaml` without `test_command`. It also accepts `refs/heads/dev` and has no file limit without `--max-files`. No Scenario and no QA row traces these rules. | requirements-agent |
| SPEC-0117 | minor    | defect   | inconsistent | Consistent     | `docs/arc42/06_runtime_view.md:1316`            | The runtime view says that `--orphans` cleans up worktrees, branches, and ledgers (BR-120). BR-125 holds the worktrees, and `--orphans` deletes no branch.                                                                                                                                  | architecture-agent |

Four notes stay rows of this report and need no change now:

| Note                                                                                                                                                                                                                                                                      | Artifact                                                      | Severity |
| ------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- | ------------------------------------------------------------- | -------- |
| The section comment and the docstring of `cmd_close_orphans` cite only BR-120, also for the worktrees. ST-0422 touches `dispatch` and can add BR-125 there.                                                                                                               | `packages/factory/scripts/dispatch:2996`, `:3257`             | note     |
| The domain rules of E5 and the done story ST-0426 cite BR-120 for the removal of a worktree. Both are planning records of finished work, so the reference only shows where the rule stood when the story was cut.                                                         | `backlog/epics-run-lifecycle.md:560`, `backlog/ST-0426.md:26` | note     |
| The glossary defines Ledger as the file `.current-work/<feature-branch>/dispatch-ledger.yaml`. BR-120 also counts an untracked `dispatch-ledger.yaml` in a worktree checkout for `--orphans`. BR-120 defines that wider set itself, so a reader reaches the right result. | `docs/spec/glossary.md:175`                                   | note     |
| The keep cases of BR-125 (dispatch inside, locked, detached HEAD, `dev` missing, inner ledger or worktree) have no Scenario. They are edge cases of RL-G10, and the tests of ST-0426 cover them.                                                                          | `docs/spec/features/run-lifecycle.feature:1209`               | note     |

## Structure checks

### `docs/spec/validation-rules.md`

BR-125 is new. Before `28ec0830`, no file of the repository and no commit on any branch held the string `BR-125`. Its two uses in the spec are its definition and the citation in BR-120 and in the `close` bullet.

BR-120 agrees with `_find_ledgers`, `_sort_ledgers`, `_claim_of`, `_removal_refusal`, and `orphan_ledger_verdict`. A ledger whose feature branch exists stays without a line. A ledger is removed only when its valid feature branch is gone and every entry is `done`, and only the file goes. Each keep reason of the rule has its branch in the code: an entry not `done` with its state, no feature branch, an invalid name, an unreadable ledger or a symlink, a tracked file, and a symlinked folder. The claims match the rule: the ledger's own folder, `.current-work/<feature-branch>/` of the primary checkout for a valid name, the mirror folder, the worktrees and branches of the entries, and the text of an unreadable ledger. When `git ls-files` fails in a checkout, `_untracked_ledgers` returns the root path, and that path loads as an unreadable ledger. So the checkout counts as owned, as BR-120 says.

BR-125 agrees with `_orphan_keep_reason` and `cmd_close_orphans`. The five keep cases come in the order of the rule, and the lock check comes before `_stash_and_remove`. The walk sorts the worktrees deepest first and reads the worktree list again before each one, so an outer worktree can go after its inner one. The stash name is `orphan <branch> <date>` with the local date, and the stash follows BR-119. The code names the branch in the line of each worktree and calls no `git branch -d`.

BR-119 did not change in the range. BR-125 refers to it for the stash, and the two rules use the same `_stash_and_remove`. The check found no contradiction.

### `docs/spec/interface-contracts.md`

The `--orphans` part of the `close` bullet agrees with `cmd_close_orphans`. Each of the six output lines and the last line `dispatch close --orphans: done` matches a `print` call. A worktree with a detached HEAD shows only the reason. A failed `git worktree list`, ledger removal, `git status`, `git stash`, or `git worktree remove` exits `1`. A failed `git merge-base` and a failed `git ls-files` only keep the item, as BR-125 and BR-120 say. The code reads no `--ledger`.

The `premerge-check` Reads row names the ledger of the primary checkout, as `ledger_path` builds it. The Feature merge paragraph agrees with `is_feature_merge`, `names_dev`, `check_run_state`, the test suite check, and the file limit in `main`. A `pending` entry blocks unless `held_back` holds. That is the held-back entry of BR-113: `returned: true`, or a dependency on a returned story, directly or through another story. A held-back entry also lets its wave close and lets `dispatch close` end the run (BR-119), so the three rules agree on it. The check found SPEC-0116 in the trace of these rules.

The `close-wave` Fails row now names the owner of each row and the text `no owner named` for an empty cell. This matches the row check in `dispatch_lib.py`. The Refuses row lists the same five states as the `close-wave <N>` rule and BR-113.

### `docs/spec/state-machines.md`

The range does not change `On Prepare`. Its three refusals, a returned entry, a dependency that is not `done`, and a missing wave record, match BR-113. The new feature merge check reads the same held-back set, so a `pending` entry that `On Prepare` can still move to **PREPARED** blocks the feature merge. The check found nothing.

### `docs/spec/glossary.md`

The range adds no term. The check found no second term for a concept of the range and no avoided term in use. The narrow definition of Ledger is a note above.

### `docs/spec/work/term-candidates.md`

The file holds no row with status `proposed`. The check found nothing.

## References to BR-120 after the split

BR-120 now holds the ledgers, and BR-125 holds the worktrees of no ledger. Each reference was checked against that split:

- `docs/spec/validation-rules.md` (BR-125) and `docs/spec/interface-contracts.md` (`close`) cite both rules in the right roles.
- `dispatch_lib.py::orphan_ledger_verdict` and the test at `tests/factory/test_run_lifecycle_close.py:1047` decide or check a ledger, so BR-120 is right.
- `docs/arc42/06_runtime_view.md:1316` cites BR-120 for the worktrees and names branches (SPEC-0117).
- `dispatch:2996` and `dispatch:3257` cite BR-120 for the whole subcommand (note).
- `backlog/epics-run-lifecycle.md:560`, `backlog/ST-0426.md`, the findings IMPL-0041, IMPL-0045, IMPL-0046, and IMPL-0053, the code review of ST-0426, and the code review of ST-0408 are records of finished work. They keep the number the rule had when they were written.

No pending story owns SPEC-0116 or SPEC-0117. ST-0422 and ST-0423 touch neither the feature file nor `docs/arc42/`. ST-0430 touches `docs/spec/` for one vocabulary, not for new Scenarios, and not `docs/arc42/`.

## Spec-feedback rows on core artifacts

The core list is `packages/factory/rulebooks/core-artifacts.yaml`. The reviewer sets each `fixed` row on a core artifact to `confirmed` or `rejected`.

| Report                     | Artifact                           | Drift                                                      | Verdict     | Reason                                                                                                                   |
| -------------------------- | ---------------------------------- | ---------------------------------------------------------- | ----------- | ------------------------------------------------------------------------------------------------------------------------ |
| `spec-feedback-ST-0421.md` | `docs/spec/interface-contracts.md` | The `close-wave` error omits the owner                     | `confirmed` | The Fails row names the owner and `no owner named`, as `dispatch_lib.py:1399` does.                                      |
| `spec-feedback-ST-0424.md` | `docs/spec/interface-contracts.md` | No place of the ledger and no refusal when it is missing   | `confirmed` | The Reads row names the path in the primary checkout, and the Feature merge list refuses a missing or unreadable ledger. |
| `spec-feedback-ST-0424.md` | `docs/spec/interface-contracts.md` | No refusal without `test_command` on the feature merge     | `confirmed` | The Feature merge list refuses it and says that the skip of a story branch does not apply.                               |
| `spec-feedback-ST-0424.md` | `docs/spec/interface-contracts.md` | The file limit on the feature merge                        | `confirmed` | The paragraph applies the limit only with `--max-files` and gives the SKIP line, as `main` prints it.                    |
| `spec-feedback-ST-0424.md` | `docs/spec/interface-contracts.md` | No refusal of an unstarted `pending` unit of work          | `confirmed` | The Feature merge list refuses a `pending` unit of work that no return holds back, with BR-113 and IMPL-0050.            |
| `spec-feedback-ST-0424.md` | `docs/spec/interface-contracts.md` | The target `refs/heads/dev`                                | `confirmed` | The paragraph names `dev` and `refs/heads/dev` and excludes a SHA, as `names_dev` does.                                  |
| `spec-feedback-ST-0426.md` | `docs/spec/validation-rules.md`    | Unreadable ledgers, no branch, invalid names, mirror claim | `confirmed` | BR-120 keeps and lists each one and defines the claims, including the mirror folder.                                     |
| `spec-feedback-ST-0426.md` | `docs/spec/validation-rules.md`    | Worktrees kept although merged                             | `confirmed` | BR-125 lists the four cases and puts the lock check before the stash.                                                    |
| `spec-feedback-ST-0426.md` | `docs/spec/validation-rules.md`    | Detached HEAD and a missing `dev`                          | `confirmed` | BR-125 keeps both as the third case.                                                                                     |
| `spec-feedback-ST-0426.md` | `docs/spec/validation-rules.md`    | Which branches are listed                                  | `confirmed` | BR-125 names the branch of each worktree, lists no branch without a worktree, and deletes no branch.                     |
| `spec-feedback-ST-0426.md` | `docs/spec/validation-rules.md`    | The stash before a removal                                 | `confirmed` | BR-125 stashes as BR-119 defines, under `orphan <branch> <date>`.                                                        |
| `spec-feedback-ST-0426.md` | `docs/spec/validation-rules.md`    | What the removal of a ledger removes                       | `confirmed` | BR-120 removes only the ledger file and keeps the briefs, gate results, and markers.                                     |
| `spec-feedback-ST-0426.md` | `docs/spec/interface-contracts.md` | No output for `--orphans`                                  | `confirmed` | The `close` bullet gives every line, the last line, exit `0`, and the five failures with exit `1`.                       |
| `spec-feedback-ST-0426.md` | `docs/spec/validation-rules.md`    | Which files count as ledgers                               | `confirmed` | BR-120 defines the search, the untracked ledger in a worktree checkout, and the tracked ledger as a keep reason.         |
| `spec-feedback-ST-0426.md` | `docs/spec/validation-rules.md`    | Symlinked folders                                          | `confirmed` | BR-120 lists the link, reads the ledgers behind it with their claims, and removes none of them.                          |

The ST-0421 row on `docs/spec/work/run-lifecycle-qa-strategy.md` is not on the core list, so it stays `fixed` and passes BR-062. The three reports hold no row on `docs/testing.yaml`.

## Prior findings

SPEC-0111, the missing Scenarios for the refused amend, the refused `git reset --keep`, and `return-story` without a status line, stays `open`, because the range does not change the feature file. SPEC-0116 is of the same kind, and the requirements agent can fix both in one pass. The open register files SPEC-0056 to SPEC-0070 concern the counter-ids feature and lie outside this range. This pass inspected the reviewed artifacts fresh and did not only check the prior list.

## Traceability summary

BR-120 and BR-125 trace to RL-G10 and to the Rule "User cleans up the runs that no active run owns". The Feature merge rules trace to BR-113 and to IMPL-0050, IMPL-0052, and IMPL-0054, but four of them have no Scenario (SPEC-0116). `backlog/ST-0423.md` traces its new item to BR-062, BR-113, IMPL-0055, and RL-11-LN-01, and each target exists. `docs/spec/scope-map.md` was read only, and the review files nothing on its content.
