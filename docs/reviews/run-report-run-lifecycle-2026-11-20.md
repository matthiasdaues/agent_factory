---
status: draft
run: feature/run-lifecycle
date: 2026-11-20
---

# Run report: run lifecycle implementation

The orchestrated run on `feature/run-lifecycle` built 24 stories in ten waves between 2026-11-18 19:31 and 2026-11-19 22:31 (+01:00). The gate-check step recorded no failed attempt: the stories had empty `quality-gates` lists, and the `dependency-check` gate that `premerge-check` ran on every merge passed. Eleven stories needed at least one fix iteration after code review, and no story escalated to a stronger tier. The User decided at 11 points, and stepped in by hand 4 times. The run shipped as v1.11.0.

This is a first draft. Each figure names its source in the last section. Figures marked "transcript" come from the session transcript, because `dispatch close` deleted the ledger and the scratchpad with the merge logs was cleared.

## Overview

| Measure                                                          | Count                                       | Source |
| ---------------------------------------------------------------- | ------------------------------------------- | ------ |
| Stories merged                                                   | 24 (ST-0408 to ST-0431)                     | S1     |
| Waves                                                            | 10                                          | S1, S5 |
| Stories that passed the first code review                        | 13                                          | S2     |
| Stories with fix iterations after code review                    | 11                                          | S2     |
| Fix iterations after code review, in total                       | 14                                          | S2     |
| Review passes, in total                                          | 38                                          | S2     |
| Gate-check retries (`mark-failed`)                               | 0                                           | S5     |
| Tier escalations (`dispatch escalate`)                           | 0                                           | S5     |
| Merge attempts                                                   | 27, of which 3 failed                       | S1, S5 |
| Scope commits on the feature branch                              | 14                                          | S1     |
| Code findings filed (IMPL-0020 to IMPL-0062)                     | 43: 16 major, 27 minor                      | S3     |
| Code findings open at the end                                    | 4, all minor                                | S3     |
| Spec-review findings at the wave closes (SPEC-0109 to SPEC-0122) | 14: 6 major, 8 minor                        | S3     |
| Spec-review findings open at the end                             | 7, all minor                                | S3     |
| Other findings filed (BUG-0130 to BUG-0132)                      | 3 major, 2 open                             | S3     |
| Decisions by the User                                            | 11                                          | S5     |
| Interventions by the User                                        | 4                                           | S5     |
| Subagents started                                                | 97                                          | S6     |
| Tests in the suite                                               | 3,868 at the first merge, 4,415 at the last | S5     |

## Stories

A review pass is one review commit. A fix iteration is a fresh developer agent that fixed review findings, followed by a narrow re-review. The findings column names the code findings that the story's review filed.

| Story   | Wave | Tier     | Review passes | Fix iterations | Findings filed (major / minor)      | Merge attempts |
| ------- | ---- | -------- | ------------- | -------------- | ----------------------------------- | -------------- |
| ST-0408 | 2    | standard | 1             | 0              | —                                   | 1              |
| ST-0409 | 3    | standard | 3             | 2              | — / 0028, 0029                      | 1              |
| ST-0410 | 4    | strong   | 2             | 1              | 0031 / —                            | 1              |
| ST-0411 | 5    | standard | 1             | 0              | — / 0034, 0035, 0036                | 1              |
| ST-0412 | 1    | standard | 2             | 1              | 0022 / —                            | 1              |
| ST-0413 | 2    | strong   | 1             | 0              | — / 0025, 0026, 0027                | 1              |
| ST-0414 | 1    | strong   | 1             | 0              | —                                   | 1              |
| ST-0415 | 2    | standard | 2             | 1              | 0024 / —                            | 1              |
| ST-0416 | 5    | standard | 1             | 0              | — / 0038, 0039                      | 1              |
| ST-0417 | 1    | standard | 1             | 0              | — / 0023                            | 1              |
| ST-0418 | 3    | strong   | 2             | 1              | 0030 / —                            | 2              |
| ST-0419 | 4    | strong   | 1             | 0              | — / 0032, 0033                      | 1              |
| ST-0420 | 5    | standard | 1             | 0              | — / 0037                            | 1              |
| ST-0421 | 6    | standard | 1             | 0              | — / 0055                            | 1              |
| ST-0422 | 7    | strong   | 2             | 1              | 0056 / 0057                         | 1              |
| ST-0423 | 8    | standard | 1             | 0              | — / 0058, 0059                      | 1              |
| ST-0424 | 6    | strong   | 3             | 2              | 0050, 0051, 0054 / 0052             | 2              |
| ST-0425 | 5    | strong   | 2             | 1              | 0040, 0041, 0042 / 0043, 0044       | 1              |
| ST-0426 | 6    | strong   | 3             | 2              | 0045, 0046, 0053 / 0047, 0048, 0049 | 1              |
| ST-0427 | 1    | strong   | 2             | 1              | 0021 / —                            | 1              |
| ST-0428 | 2    | strong   | 1             | 0              | —                                   | 1              |
| ST-0429 | 1    | standard | 1             | 0              | — / 0020                            | 1              |
| ST-0430 | 9    | standard | 1             | 0              | — / 0060                            | 1              |
| ST-0431 | 10   | standard | 2             | 1              | 0061 / 0062                         | 2              |

Three fix iterations created the next major finding: IMPL-0054 came from the fix of IMPL-0052, IMPL-0053 from the fix of IMPL-0045 and IMPL-0046, and IMPL-0061 from the approved option (a) for the empty wave. Every major code finding was resolved before its story merged.

## Failed merges

| Story   | Cause                                                                                                       | Recovery                                                                                             | Source |
| ------- | ----------------------------------------------------------------------------------------------------------- | ---------------------------------------------------------------------------------------------------- | ------ |
| ST-0418 | One test failed after the merge; the log did not keep its name.                                             | The feature branch was reset, the story re-dispatched, and the second merge passed with 4,110 tests. | S4, S5 |
| ST-0424 | `premerge-check` refused `docs/findings/BUG-0130.md` as out of scope, because the reviewer had resolved it. | A scope commit, then the second merge passed with 4,306 tests.                                       | S5     |
| ST-0431 | The suite after the merge failed with `No space left on device`; the usage capture had filled the disk.     | The User freed space, the story was re-dispatched, and the second merge passed with 4,415 tests.     | S5     |

## The User's part

Decisions are answers to a question the run put to the User. Interventions are actions the User took by hand.

| When (2026-11-) | Kind         | Subject                                                          | Answer or action                                  |
| --------------- | ------------ | ---------------------------------------------------------------- | ------------------------------------------------- |
| 18 19:31        | Decision     | `crap-score` gate during the run                                 | A: stay off until crap-gate-setup lands           |
| 18 22:51        | Decision     | `docs/testing.yaml` rows of wave 2                               | Confirmed                                         |
| 18 23:05        | Decision     | `prepare-story` by hand with a dirty checkout (ST-0409)          | a: refuse                                         |
| 19 09:21        | Decision     | A hook refuses the amend that writes `status: done` (ST-0410)    | A: fix in the same iteration, no critical finding |
| 19 12:21        | Decision     | SPEC-0109, SPEC-0110, SPEC-0111 at the wave-4 close              | Fix as recommended; SPEC-0111 to reconciliation   |
| 19 15:36        | Decision     | Ignored files at `dispatch close`                                | A: they go with the worktree                      |
| 19 15:37        | Decision     | `docs/testing.yaml` row `dispatch.refuse_dirty_feature_worktree` | Confirmed                                         |
| 19 18:52        | Decision     | Default tier of a finding                                        | A: `economy`                                      |
| 19 20:39        | Decision     | Checks of the whole feature before the merge                     | A smoke run instead of another code review        |
| 19 20:42        | Decision     | Four feature reports in the feature merge check                  | Replace by a scripted smoke test; design later    |
| 19 21:12        | Decision     | Three smoke-run defects and the `--class` gap                    | Fix all in ST-0431, option (a) for the empty wave |
| 19 ~18:10       | Intervention | Three hanging wait loops of finished agents                      | Killed by the User                                |
| 19 ~20:40       | Intervention | `dev` 21 commits ahead, guard blocked the agent's merge          | The User merged `dev` into the feature branch     |
| 19 ~22:20       | Intervention | Full disk during the ST-0431 merge                               | The User freed space                              |
| 20              | Intervention | One more hanging wait loop of the ST-0430 developer              | Killed by the User                                |

The User also paused the run twice (2026-11-18 22:16 and 23:06) and asked four questions that changed nothing in the run: the crap-score design, the "vicious circle" of the refused amend, the escalation that was not one, and the hanging shells.

## Agents

| Agent                 | Started | Role in the run                                         |
| --------------------- | ------- | ------------------------------------------------------- |
| developer-agent       | 34      | Implementation, fix iterations, one wave-close text fix |
| code-review-agent     | 26      | Story reviews and narrow re-reviews                     |
| domain-modeling-agent | 10      | Drift rows at the wave closes                           |
| test-strategy-agent   | 8       | Drift rows and QA row states                            |
| planning-agent        | 6       | Finding placement, ST-0431                              |
| spec-review-agent     | 6       | Spec review and row confirmation at the wave closes     |
| architecture-agent    | 3       | Drift rows on arc42                                     |
| requirements-agent    | 3       | Drift rows on the feature files and rules               |
| general-purpose       | 1       | The smoke run                                           |
| Total                 | 97      |                                                         |

A resumed agent counts once: follow-up messages through `SendMessage` reuse the agent's transcript.

## Token spend

From 2026-11-18 19:31 over the main session and the 97 subagent transcripts, all on `claude-opus-5-5`: input 10,156; cache writes 17,065,906; cache reads 669,498,961; output 3,143,688. Normalized with `cl100k_base`: 4,284,329 input and 1,262,534 output, 5,546,863 in total. Source: S6.

## Sources

| ID  | Source                                                                                                                                                                                                                                                                                                                                                  | What it gives                                                                 |
| --- | ------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- | ----------------------------------------------------------------------------- |
| S1  | `git log dev`: the 24 commits `merge: story/ST-04NN into feature/run-lifecycle`, and the 14 commits `fix: admit … in the ST-04NN scope`                                                                                                                                                                                                                 | Stories, waves, scope commits, successful merges                              |
| S2  | The commits of each story branch, read as `git log <merge>^1..<merge>^2` per merge commit: `feat` commits, review commits (`docs: review …`, `docs: re-review …`, `docs: resolve … after the re-review`), and `fix` commits after a review                                                                                                              | Review passes and fix iterations                                              |
| S3  | `docs/findings/IMPL-*.md`, `docs/findings/SPEC-*.md`, `docs/findings/BUG-*.md` and `docs/findings/register/*/*.json`: the fields `severity`, `status` and `story`                                                                                                                                                                                       | Findings per story, severity, open at the end                                 |
| S4  | `docs/handoffs/handoff-run-lifecycle-implementation-2026-11-19.md` and its 2026-11-19 predecessor in the same commit history                                                                                                                                                                                                                            | The ST-0418 merge failure                                                     |
| S5  | The session transcript `~/.claude/projects/-home-matthiasdaues-Documents-datenschoenheit-agent-factory/9f81748e-d987-4164-8d2f-82836fdc0b2c.jsonl`: the User's messages from 2026-11-18 19:31 on, the `merge-story` outputs with their test counts, and the ledger check of 2026-11-19 (no attempts and every `active_tier` equal to the declared tier) | Decisions, interventions, failed merges, test counts, retries and escalations |
| S6  | The subagent transcripts in `…/9f81748e-d987-4164-8d2f-82836fdc0b2c/subagents/` that start after 2026-11-18 19:31, their `.meta.json` files, and the factory normalizer `ClaudeCodeNormalizer` with `count_tokens` from `packages/factory/scripts/usage-capture`                                                                                        | Subagents per type, token spend                                               |

## Limits of this draft

- The ledger is gone, so the counts of retries and escalations rest on one ledger check during the run (S5) and on the absence of `mark-failed` and `escalate` calls in the transcript. ST-0431's re-dispatch after the full disk was a `blocked` story, not a gate retry.
- A review pass counts commits. ST-0412 has a re-review commit but no separate fix commit; its fix sits in the review-resolve commit.
- ST-0416's `fix` commit repaired a formatting issue before its review and is not counted as a fix iteration.
- IMPL-0021 has no `story` field; the table places it under ST-0427 from the commit that filed it.
- The decisions and interventions of 2026-11-18 rest on the transcript and the summary of the session before the context compaction of 2026-11-19 08:35.
