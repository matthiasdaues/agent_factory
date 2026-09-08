# Reconciliation: Dispatch Lifecycle Close and Mechanical Enforcement

Branch: `impl/st-0212-st-0213-st-0215`
Date: 2026-09-08
Proposal: `docs/proposals/factory-dispatch-close-and-batch-fix.md`

## Proposal Completion Criteria

| #   | Criterion                                                                                                        | Status | Evidence                                                                                                                                                                       |
| --- | ---------------------------------------------------------------------------------------------------------------- | ------ | ------------------------------------------------------------------------------------------------------------------------------------------------------------------------------ |
| 1   | dispatch-contract.md contains a Close section with completed and abandoned paths                                 | Met    | `dispatch-contract.md` lines 221-244: "## Close" with "### Completed Close" (4 steps) and "### Abandoned Close" (3 steps)                                                      |
| 2   | branching-policy.md references the dispatch close for worktree removal                                           | Met    | `branching-policy.md` Enforcement section: "see [dispatch-contract.md SS Close]... for the authoritative procedure for removing worktrees and branches at dispatch close time" |
| 3   | commit-conventions.md contains batch-fix guidance                                                                | Met    | `commit-conventions.md` lines 43-44: "### Batch Fix" subsection with preference and rationale                                                                                  |
| 4   | rules.md contains a MUST rule requiring dispatch close on completion or abandonment                              | Met    | `rules.md` line 119: "MUST close every dispatch as completed or abandoned"                                                                                                     |
| 5   | implementation-agent.md contains a MUST requiring `dispatch init` before story branches                          | Met    | `implementation-agent.md` Step 1: "MUST call `factory/scripts/dispatch init ...` as the first action before creating any story branches"                                       |
| 6   | block-dangerous-git.sh denies commits on `story/*` branches without a dispatch ledger                            | Met    | `block-dangerous-git.sh` lines 63-76: resolves main checkout via `--git-common-dir`, globs `.current-work/*/dispatch-ledger.yaml`, denies on miss                              |
| 7   | The stale-factory chain is broken so `update-factory` runs without `--force` after hook-modified files           | Met    | `HOOK_REGENERATED_PATHS = ("INDEX.yaml",)` in both scripts; `_should_checksum` excludes them; 7 test cases in `test_update_factory.py` confirm                                 |
| 8   | dispatch-contract.md or qa-agent.md documents that QA in a worktree does not validate the installed factory copy | Met    | `dispatch-contract.md` lines 246-252: "## QA-in-Worktree Divergence" names path pair and mitigation                                                                            |

## Story Acceptance Criteria

### ST-0212 -- Add close ceremony to dispatch contract

| #   | Criterion                                                                      | Status | Evidence                     |
| --- | ------------------------------------------------------------------------------ | ------ | ---------------------------- |
| 1   | Close section with Completed close listing 4 steps                             | Met    | Lines 225-236                |
| 2   | Abandoned close listing 3 steps                                                | Met    | Lines 238-244                |
| 3   | branching-policy.md references dispatch close for worktree removal             | Met    | Enforcement section line 108 |
| 4   | rules.md MUST rule                                                             | Met    | Line 119                     |
| 5   | Close ceremony distinguishes merged (safe delete) from blocked (left in place) | Met    | Lines 232-234                |

### ST-0213 -- Add batch-fix guidance to commit conventions

| #   | Criterion                                                 | Status | Evidence                                                  |
| --- | --------------------------------------------------------- | ------ | --------------------------------------------------------- |
| 1   | Batch Fix subsection under Project-Specific Rule          | Met    | Line 43: `### Batch Fix` under `## Project-Specific Rule` |
| 2   | States preference for one commit over incremental patches | Met    | Line 44                                                   |
| 3   | Includes rationale about reviewability and bisectability  | Met    | Line 44: "hard to review, bisect, and reason about"       |

### ST-0214 -- Gate story-branch commits on dispatch-ledger existence

| #   | Criterion                                                              | Status | Evidence                                                                                                 |
| --- | ---------------------------------------------------------------------- | ------ | -------------------------------------------------------------------------------------------------------- |
| 1   | block-dangerous-git.sh denies `git commit` on `story/*` without ledger | Met    | Lines 63-76                                                                                              |
| 2   | Hook resolves main checkout via `git rev-parse --git-common-dir`       | Met    | Line 68                                                                                                  |
| 3   | Denial message names missing ledger and suggests `dispatch init`       | Met    | Line 71                                                                                                  |
| 4   | implementation-agent.md MUST for `dispatch init`                       | Met    | Step 1, line 97                                                                                          |
| 5   | Non-story branches unaffected                                          | Met    | `case` statement only matches `story/*`; test `test_non_story_branch_without_ledger_is_allowed` confirms |

### ST-0215 -- Exclude hook-regenerated files from update-factory checksums

| #   | Criterion                                                            | Status | Evidence                                                                                                              |
| --- | -------------------------------------------------------------------- | ------ | --------------------------------------------------------------------------------------------------------------------- |
| 1   | update-factory does not flag INDEX.yaml as user modification         | Met    | Test `test_index_yaml_change_alone_is_not_detected`                                                                   |
| 2   | Named constant in both scripts                                       | Met    | `HOOK_REGENERATED_PATHS = ("INDEX.yaml",)` in update-factory line 91 and init-factory line 264                        |
| 3   | `_should_checksum` in update-factory excludes hook-regenerated paths | Met    | Lines 119-125                                                                                                         |
| 4   | `compute_factory_checksums` in init-factory excludes same paths      | Met    | init-factory lines 267-275                                                                                            |
| 5   | Excluded paths overwritten unconditionally (no `--force` needed)     | Met    | Full `factory/` replace architecture handles this; test `test_index_yaml_only_change_proceeds_without_force` confirms |

### ST-0216 -- Document QA-in-worktree vs installed-copy divergence

| #   | Criterion                                                    | Status | Evidence      |
| --- | ------------------------------------------------------------ | ------ | ------------- |
| 1   | QA-in-Worktree Divergence subsection in dispatch-contract.md | Met    | Lines 246-252 |
| 2   | Names path pair: `packages/factory/` vs `factory/`           | Met    | Line 248      |
| 3   | States mitigation: run `update-factory` before final merge   | Met    | Line 252      |

## Review Findings (PROP-11 through PROP-14)

| ID              | Status    | Resolution                                                                                                                                                                  |
| --------------- | --------- | --------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| PROP-11 (major) | Addressed | Open Question 1 resolved to "exclude hook-regenerated files from checksums." Design item 5 rewritten with clear approach. Implemented as `HOOK_REGENERATED_PATHS` constant. |
| PROP-12 (minor) | Addressed | Scope cross-reference corrected from "open question 2" to "open question 1" in the proposal text.                                                                           |
| PROP-13 (minor) | Addressed | Design item 3 rewritten to specify `--git-common-dir` path resolution from worktree to main checkout. Hook implements exactly this.                                         |
| PROP-14 (minor) | Addressed | `estimated_consumption.max` corrected to 180,000 (12,000 x 15 = 180,000).                                                                                                   |

## Doc Fixes Applied

| File                                                          | Change                                                                                                                    | Reason                                                                                                                                                                                                    |
| ------------------------------------------------------------- | ------------------------------------------------------------------------------------------------------------------------- | --------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| `packages/factory/rulebooks/conventions/dispatch-contract.md` | Changed "the commit already exists on main" to "the commit already exists on the target branch" in Completed Close step 3 | At dispatch-close time, story branches have been merged to the invocation/feature branch, not to main. The `git branch -d` safe delete works because the commit is reachable from the target branch HEAD. |

Also changed "the feature branch" to "the story branch" in the same sentence -- the branch being deleted is the story branch, not the feature (invocation) branch.

## Unresolved Gaps

None. All completion criteria met. All acceptance criteria met. All review findings addressed.

## Open Questions Resolution

| #   | Question                            | Resolution                                                                                                                                       |
| --- | ----------------------------------- | ------------------------------------------------------------------------------------------------------------------------------------------------ |
| 1   | Stale-factory fix mechanism         | Resolved: exclude hook-regenerated files from checksums. Implemented.                                                                            |
| 2   | Worktree cleanup scope tier         | Implicitly resolved: both options (dispatch-close script, guardrail allowlist) deferred to follow-up. Manual cleanup accepted for first release. |
| 3   | QA divergence: contract vs qa-agent | Resolved: convention guidance in dispatch-contract.md (ST-0216). Code change deferred to follow-up.                                              |
