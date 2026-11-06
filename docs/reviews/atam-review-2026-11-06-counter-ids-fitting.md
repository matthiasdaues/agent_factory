---
type: atam-review
title: ATAM review of the counter-ids-fitting local counter and move
date: 2026-11-06
status: pass
reviewer: architecture-review-agent
findings_filed: 1
story: counter-ids-fitting
scope: Commit 09f776da8911153ece75dff4d4439103a07d35c8 on dev — the Local Counter, the ID Allocation changes, and the view IdMoveToOrigin in architecture.dsl, arc42 5.11, 6.16, 8.18, chapter 9, QS-22, QS-23, ADR-0033, and the amendment line of ADR-0031 — checked against the counter-ids-fitting proposal, its feature file, BR-096 to BR-108, the next-id contract, and the Move Lifecycle
---

# ATAM review of the counter-ids-fitting local counter and move

The Local Counter reuses the leased push of ADR-0031 unchanged, so claims without `origin` keep QS-18. The marker-first move keeps QS-22 while the move runs to its end. One blocking risk remains:

- An interrupted move leaves no ref to the claim commit. The only recovery the specification offers is a new seed, and that seed can hand out an ID twice (ATAM-0014, `major`).

Two `minor` risks went to `docs/findings/register/architecture.jsonl` (ATAM-0015, ATAM-0016). Ten notes stay in this report: four sensitivity points, four non-risks, and two tradeoff points. Planning should wait for ATAM-0014. Next, the architecture agent fixes ATAM-0014 and asks the stakeholder to confirm the fix, because it settles gap CIF-G05.

Classification follows the accepted proposal `docs/proposals/finding-classification.md`, as the brief requires.

## Reviewed architecture

- `docs/spec/architecture.dsl`: the software system Local Counter, the changed container ID Allocation and its three components, the counter-ids relationships with `virgil` and `init-factory`, the view `IdAllocationComponents`, and the dynamic view `IdMoveToOrigin`.
- `docs/spec/dependency-rules.dsl`, which the commit leaves unchanged.
- ADR-0033 and the amendment line of ADR-0031.
- Sections 5.11, 6.16, 8.18, chapter 9, QS-22, QS-23, and their rows in 10.2.
- Reference material: `docs/proposals/counter-ids-fitting.md` with DEC-01 to DEC-13, `docs/spec/features/counter-ids-fitting.feature`, BR-096 to BR-108 and BR-072 to BR-077 in `docs/spec/validation-rules.md`, the `next-id` contract with its `--plan-seed` and `--move-to-origin` sections in `docs/spec/interface-contracts.md`, the Move Lifecycle in `docs/spec/state-machines.md`, and `docs/spec/work/counter-ids-fitting-gaps.md`.

`.agent-factory/factory/scripts/arch-lint --docs-dir docs/arc42` found 0 errors, 1 warning, and 0 info, and exited 0. `.agent-factory/factory/scripts/structurizr validate` exited 0.

## Deterministic findings

| Finding                                                             | Disposition                                                                                                                       |
| ------------------------------------------------------------------- | --------------------------------------------------------------------------------------------------------------------------------- |
| `ARCH-PARSE` warning: could not extract ports from DSL or chapter 5 | Dismissed. The warning exists before this commit. The Local Counter is a path on disk, and ID Allocation opens no listening port. |

## Prior findings

This is the first ATAM pass on counter-ids-fitting. ATAM-0010 to ATAM-0013 from the counter-ids review are still `open`. They belong to the repeat pass of that review, so this pass does not resolve them. QS-19 to QS-21 and BR-076 now answer ATAM-0012 and ATAM-0013 in substance.

## Rules check

No mismatch from this commit. The commit adds no rule, and section 5.11 states why: the three components ship as one script. The two existing rules name `factory` and `usage`. Both predate counter-ids and name no ID Allocation element, so the brief puts them out of scope.

## Quality scenarios

1. **QS-18: No ID is handed out twice** (priority 1), now also on the Local Counter.
2. **QS-22: A move hands out no ID twice** (priority 1).
3. **QS-23: A second counter on origin shows at the move** (priority 2).
4. **QS-20: A failed claim ends with a named cause** (priority 2), applied to the seed and the move that VIRGIL runs.
5. **QS-21: Only next-id and repository writers change the counter** (priority 2), applied to the Local Counter.
6. **QS-19: Parallel claims succeed within the retry budget** (priority 2), applied to claims without `origin`.

The brief names an interrupted move as an operability concern. Chapter 10 has no scenario for it, so this review measures it against QS-22, whose promise it threatens.

## Findings

### QS-18 and QS-19: claims on the Local Counter

- **Approach.** The Git-Ref Adapter pushes to the path in `agent-factory.counterRemote` exactly as to `origin` (BR-096). Every worktree shares the `.git/config`, and a local clone reaches the same ref through its `origin`.
- **Sensitivity point.** The setting holds the parent of `git rev-parse --git-common-dir`. In a submodule or a repository with a separate git directory, that parent is no repository, so every claim fails as unreachable. The claim fails loudly, so this is a note. Storing the common directory itself would remove the case.
- **Sensitivity point.** A claim on the Local Counter runs the receive-side hooks of the main repository, such as `pre-receive` or `reference-transaction`. The throwaway repository uses `--template=`, so it runs no hooks of its own.
- **Non-risk.** The lease check of a local push holds under git's ref lock, so QS-18 and QS-19 hold on the Local Counter. Assumptions: no receive hook in the main repository refuses refs outside `refs/heads/`, and `receive.denyCurrentBranch` touches only the checked-out branch.

### QS-22: the move hands out no ID twice

- **Approach.** The marker goes on the Local Counter under a lease on the claim commit `C` before the create-only push to `origin` (DEC-09, BR-102, BR-103).
- **Sensitivity point.** `MARKING` is the one step where a parallel claim changes the outcome. A claim before it makes the lease stale, and a claim after it reads the marker and fails.
- **Non-risk.** For a move that runs to its end, every ordering of one move and one claim keeps QS-22. Assumption: the push of the marker and the claim push meet the same ref lock.
- **Risk (ATAM-0014, `major`).** The marker holds one line and no parent, and the claim commit is parentless. After the marker, no ref points to `C`, and the main repository keeps no reflog for `refs/ids/counters`. A move killed between the marker and the push loses `C`. A new seed through `--plan-seed` counts only committed IDs (BR-099, CIF-G10), so a claimed but uncommitted number goes out a second time.
- **Tradeoff point.** Marker first protects parallel claims during the move. It also makes every claim fail while the move hangs or after it dies.

### QS-23: a second counter on origin

- **Approach.** The create-only lease refuses the push. The move puts `C` back under a lease on the marker and names both counters (BR-102, BR-106).
- **Non-risk.** Both refs end with their earlier SHA, as QS-23 measures. Assumption: no claim writes to the Local Counter while it holds the marker, which BR-097 ensures.
- **Tradeoff point.** DEC-05 accepts that a collision shows at the move, not before. Until the User confirms the move, a colleague can seed `origin` and claim from it. So two counters can already have handed out the same number when QS-23 detects them. Gap CIF-G03 leaves the resolution open, which DEC-13 allows. This is a note, not a finding, because it follows from DEC-05.
- **Risk (ATAM-0016, `minor`).** Only a claim and `--plan-seed` recognise the marker. The read of the move has no outcome for a marker or a missing counter. Both occur when two worktrees start sessions at once, or when the User declines the seed and the setting stays (CIF-G06). `init-factory` also counts a marker as a seeded counter (BR-105).

### QS-20: the seed and the move end with a named cause

- **Approach.** BR-076 makes every git call of a claim run without prompts and within 30 seconds. The seed keeps git's prompts.
- **Risk (ATAM-0015, `minor`).** DEC-03 and DEC-09 let VIRGIL run the seed and the move in an agent shell. BR-076 still exempts the seed "because a person runs it", and no rule covers the move, which also restarts on a stale lease without a bound. A new `origin` without stored credentials can make the move wait on a prompt until the shell kills it. That kill is the trigger of ATAM-0014.

### QS-21: who can move the counter

- **Approach.** ADR-0032 lets agents push the ref only through `next-id`. The move is a mode of `next-id` for that reason (DEC-09).
- **Sensitivity point.** On `origin`, write access limits who can move the ref. On the Local Counter, every local process can write it, also with `git update-ref` and no push at all. Section 8.18 says the counter rests on the `next-id` rule and on write access to the remote. Without `origin`, only the rule is left. QS-21 already accepts that a writer is not refused, so this is a note.
- **Non-risk.** The marker stores the URL of `origin` redacted by BR-077, so no token reaches the git object store. Assumption: the redaction runs before the marker commit is written, as the marker contract states.

## Risk summary

| ID        | Risk                                                                                      | Scenario | Severity | Mitigation                                                                                                              |
| --------- | ----------------------------------------------------------------------------------------- | -------- | -------- | ----------------------------------------------------------------------------------------------------------------------- |
| ATAM-0014 | An interrupted move leaves no ref to `C`, and recovery by a new seed can repeat an ID.    | QS-22    | major    | Make `C` the parent of the marker; let a second move finish the first; add an interrupted-move environment to QS-22.    |
| ATAM-0015 | The seed and the move, run by VIRGIL, keep prompts and have no time limit or retry bound. | QS-20    | minor    | Apply BR-076 to every git call of the seed and the move; bound the restarts of the move as BR-072 bounds a claim.       |
| ATAM-0016 | The move and `init-factory` have no defined outcome for a marker or a missing counter.    | QS-23    | minor    | Define the outcome of a move that reads a marker or no counter; state whether `fitting.counter_seeded` counts a marker. |

Risk theme: the marker state. All three risks concern what the system does while the Local Counter holds a marker that the move has not finished.

## Tradeoff summary

| Tradeoff                                           | Gains                                                          | Costs                                                                                |
| -------------------------------------------------- | -------------------------------------------------------------- | ------------------------------------------------------------------------------------ |
| Marker before push (DEC-09)                        | No claim lands on the Local Counter while `C` travels.         | Every claim fails while the move hangs or after it dies.                             |
| Collision shown at the move (DEC-05)               | A second counter never goes unnoticed.                         | Duplicates can exist before the move detects them (CIF-G03).                         |
| Setting before `origin` in the remote order        | Adding `origin` does not split the counter before the move.    | The project keeps claiming locally while colleagues may already use `origin`.        |
| Local Counter in the project's own `.git` (DEC-05) | No extra repository; every worktree and local clone shares it. | Write access no longer limits who changes the counter; only the `next-id` rule does. |

## Pass 2

Pass 2 checks only ATAM-0014 and the text its fix changed, on commit `54f1678dcf209f6c7f9fccb09b11e8ee722223ee`. The stakeholder accepted the fix as DEC-14. ATAM-0014 is resolved, and no new finding blocks. Planning may start.

`arch-lint` found 0 errors, 1 warning, and 0 info, and exited 0. The `ARCH-PARSE` warning is the one dismissed in pass 1.

### ATAM-0014: resolved

The marker now has `C` as its only parent, so `C` stays reachable in the main repository and `git gc` keeps it. A second move reads the marker, takes `C`, and goes on at the push (`RESUMING` to `PUSHING`). When `origin` already holds `C`, it only removes the setting (`RESUMING` to `CLEARING`). No step needs a new seed, so `--plan-seed` no longer decides the next number after a cut-off. QS-22 measures the case with 20 rounds of a move killed after the marker. ADR-0033, 6.16.1, the view `IdMoveToOriginResume`, 8.18, BR-102, the marker and move contracts, and the Move Lifecycle agree with each other and with DEC-14.

### Changed text: QS-22 after the fix

- **Non-risk.** While the marker stands, every claim through the setting fails, and a local clone reaches the same marker through its `origin`. So no claim lands on `C` between two calls. Assumption: nobody removes the setting or the marker by hand.
- **Risk (ATAM-0017, `minor`, register).** A cut-off after the push and before the setting is removed leaves `C` on `origin`. A clone of the new `origin` on another machine can claim there before the next session start. The second move then sees a claim commit other than `C` and reports a collision, although the move went through. No ID goes out twice, but local claims stay blocked until a human acts (CIF-G03). The fix lets the collision message print the lines of both claim commits.
- **Note.** `MARKING` has no `CutOff` event. A cut-off there leaves either `C` or the marker, and the next call reads both correctly, so nothing changes.
- **Note.** The QS-22 environment still says `origin` holds no counter. The case where `origin` already holds `C` has no measure. The contract row and the lifecycle state it, so a test writer can derive the check.

ATAM-0015 and ATAM-0016 stay in the register. DEC-14 gives a move that reads a marker an outcome, which answers part of ATAM-0016. The case of a missing counter and the fitting key remain.
