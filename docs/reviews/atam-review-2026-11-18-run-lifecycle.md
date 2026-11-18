---
type: atam-review
title: ATAM review of the run lifecycle architecture
date: 2026-11-18
status: pass
reviewer: architecture-review-agent
findings_filed: 6
story: run-lifecycle
scope: Commit 8b246fc2 — architecture.dsl, arc42 chapters 5 to 10, ADR-0037 to ADR-0040, the amendments of ADR-0012 and ADR-0029, the SVG exports, and ARCH-0403, measured against the accepted proposal docs/proposals/run-lifecycle.md and the reviewed spec
---

# ATAM review of the run lifecycle architecture

The architecture realizes the proposal and the spec in almost every part. Three risks block planning. By hand, `merge-story` switches the checkout before the merge check decides (ATAM-0021). The OpenCode git guardrail misses the `execute` tool (ATAM-0022). A crashed merge check leaves a worktree that blocks every retry (ATAM-0023). Three `minor` document defects go to the register. The architecture agent owns all six.

## Reviewed architecture

- `docs/spec/architecture.dsl`: the new components Ledger, `test-design-verify`, `mutation-testing`, `block-dangerous-git.ts`, the OpenCode guardrail entry, `code-review-agent`, and `qa-agent`; the container Run Worktrees; the views GateCheckStep, PremergeStoryCheck, GitGuardrailOneScript, RunLifecycleComponents, RunOrchestrated, RunByHand, StoryWorkflow, and WaveClose.
- arc42 chapters 5.1, 5.2.3, 5.4, 5.5, 5.13, 6.4, 6.12, 6.22 to 6.25, 7.1, 8.2, 8.7, 9, and 10 with QS-28 and QS-29.
- ADR-0037 to ADR-0040 and the amendment lines of ADR-0012 and ADR-0029.
- The spec as reference: the Ledger Entry Lifecycle, BR-111 to BR-122, BR-066, the `dispatch`, `premerge-check`, and `block-dangerous-git.sh` contracts, and `run-lifecycle.feature`.

`arch-lint --docs-dir docs/arc42` found 0 errors, 1 warning, and 0 info, and exited `0`. `structurizr validate` exited `0`. The PNG renders of the ten new and changed views lie in the session scratchpad, not in the repository.

## Deterministic findings

| Check      | Severity | Verdict   | Reason                                                                                                                         |
| ---------- | -------- | --------- | ------------------------------------------------------------------------------------------------------------------------------ |
| ARCH-PARSE | warning  | Dismissed | The DSL and chapter 5 describe ports as prose, not as a parseable list. Earlier reviews dismissed the warning for that reason. |

## Rules check

No mismatch. `docs/spec/dependency-rules.dsl` holds two rules, `factory must_not_depend_on usage` and the reverse. The commit adds no rule, and no new relationship crosses between Factory Flow Control and Usage Analysis.

## Quality scenarios

1. QS-28: A failing gate merges on neither way of driving a run (priority 1).
2. QS-29: No agent destroys work in any agent tool (priority 1).
3. QS-5: Observable-state resume (priority 1), which ADR-0037 and 6.22 claim for runs.
4. QS-2: Human authority (priority 1), which ADR-0037, ADR-0038, and ADR-0040 score.
5. QS-17: The specification lags the code by one wave at most (priority 2).
6. QS-24: A critical finding stops every dispatch and merge (priority 1), for the new `add` subcommand and the feature merge.
7. QS-6: Deterministic validation (priority 2), which ADR-0037 to ADR-0039 cite.

## Findings

### QS-28: A failing gate merges on neither way

- **Approach.** `premerge-check` reruns every gate and the test suite in a temporary detached worktree at the branch head, with the gate scripts of the calling checkout (ADR-0038). It reads no stored result except the result of `mutation-testing`.
- **Sensitivity points.** The response depends on the order inside `merge-story` by hand. It also depends on where `dispatch` finds the gate scripts: today `dispatch` calls `premerge-check` from its own script folder, so a call from a linked worktree still finds the installed copy.
- **Tradeoff.** Every gate runs twice per unit of work, and each rerun builds a fresh `uv` environment. Safety wins over merge time.
- **Risk.** ATAM-0021: by hand, `merge-story` checks out the feature branch before `premerge-check` runs. A changed tracked file makes the checkout refuse, and a refused merge leaves the primary checkout on the feature branch.
- **Non-risk.** The orchestrated half of QS-28 holds. Assumptions: the temporary worktree reads the same `docs/testing.yaml` as the branch head, and the gate scripts accept the worktree as source root.
- **Note.** The stored result of `mutation-testing` is a deliberate exception until `mutation-gate.md` settles the merge-time run. A fix commit after the gate-check step can therefore merge with an old mutation result. The proposal settles this, so it is no finding.

### QS-29: No agent destroys work in any agent tool

- **Approach.** One script holds every rule. Claude Code, Codex, and Copilot CLI call it from their native hook. pi and OpenCode call it from thin entries (ADR-0039).
- **Sensitivity point.** The guarantee holds only for the tool calls that reach an entry.
- **Risk.** ATAM-0022: the OpenCode entry passes only shell calls. The `execute` tool, which the human-fields guard already treats as a shell channel, reaches no git guardrail.
- **Non-risk.** The forms after `&&`, after `;`, inside `bash -c`, and through any path to `dispatch` are covered by one parser with one test suite. Assumption: the native hooks of Claude Code, Codex, and Copilot CLI fire for every shell tool. The variable-built command that passes is an accepted limit (OI-11).

### QS-5: Observable-state resume of a run

- **Approach.** Every `dispatch` subcommand reads the ledger and the branch state before it acts, and the Ledger allows only the transitions of the state machine.
- **Risk.** ATAM-0023: a temporary worktree left by a crash blocks every later `premerge-check` of its unit of work, and only `dispatch close` removes it.
- **Note.** QS-5 itself measures the eligibility result, not the run. ADR-0037 and 6.22 extend it to runs without a scenario of their own. A run-resume scenario in chapter 10 would make the claim checkable.

### QS-2: Human authority

- **Approach.** The User runs `return-story`, `close`, and `close --drop`, and merges into `dev`. By hand, the implementation agent stops at each decision point. The temporary worktree keeps the User's files unchanged (ADR-0038). `merge-story` copies nothing into the installed copy (ADR-0040).
- **Tradeoff.** On the last tier an agent can start a retry the User did not ask for, because `re-dispatch` takes no flag (BR-116). The spec accepts this limit.
- **Non-risk.** ADR-0040 keeps the installed copy under `update-factory`. Assumption: no test of this repository still reads `.agent-factory/factory/` after the change.

### QS-17: The specification lags the code by one wave at most

- **Approach.** Drift sessions run at the wave close on the feature branch, one at a time, and `prepare-wave` waits for the wave record (ADR-0037 amending ADR-0029).
- **Non-risk.** A story merge and a drift session never commit on the feature branch at the same time. Assumption: the implementation agent starts no `merge-story` while a wave close is in progress.

### QS-24: A critical finding stops every dispatch and merge

- **Non-risk.** The stop check now also runs before `dispatch add`, and `premerge-check dev <feature-branch>` calls it first. Assumption: the checkout that runs the feature merge check holds the finding files of the feature branch in its working tree or at `HEAD`.

### QS-6: Deterministic validation

- **Note.** The Pugh matrices of ADR-0037, ADR-0038, and ADR-0039 cite QS-6, which has priority 2. The scenario they serve is QS-28, which has priority 1. The totals do not change. QS-6 also still says "after each developer commit", while the gates now run in the gate-check step.

### ADRs and Pugh matrices

Every weighted total adds up: ADR-0037 gives +6 and +4, ADR-0038 gives −1 and +2, ADR-0039 gives +6 and 0, and ADR-0040 gives +5. The sensitivity sentences of ADR-0037 and ADR-0038 hold when recomputed. Each matrix weighs a real alternative and states the reason against it. The amendment lines of ADR-0012 and ADR-0029 name the changed step.

### Performers of the Ledger Entry Lifecycle

Every transition has a performer. The implementation agent runs the subcommands of Added, Prepare, MarkDispatching, MarkDispatched, Fail, Block, and ReDispatch. `merge-story` performs MergeSucceeds and the Block of a merge conflict or a red suite. The User performs Return. MarkDone has no subcommand. ATAM-0024 covers a view that skips two of these edges. ATAM-0025 covers the refused merge, which has no edge at all.

### Agreement of DSL, chapters, and views

The DSL, the component tables, and the Mermaid sequences agree step for step. Two gaps remain: GateCheckStep skips ledger transitions (ATAM-0024), and no view shows the path after a refused merge (ATAM-0025). The rendered views are hard to read (ATAM-0026). The heading of 5.2.3 still says `mutation-analysis` instead of `mutation-testing`, which is a note.

### YAGNI pass

No artificial complexity. The Ledger component and the Run Worktrees container each name a real boundary of the code and the disk. The thin guardrail entries remove a second rule set instead of adding one.

## Risk summary

| ID        | Severity | Scenario | Risk                                                                                          | Mitigation                                                                      |
| --------- | -------- | -------- | --------------------------------------------------------------------------------------------- | ------------------------------------------------------------------------------- |
| ATAM-0021 | major    | QS-28    | By hand, the checkout of the feature branch comes before the merge check                      | Run `premerge-check` first and check out the feature branch only after exit `0` |
| ATAM-0022 | major    | QS-29    | The OpenCode `execute` tool reaches no git guardrail                                          | Pass the JavaScript of each `execute` call to the script as command text        |
| ATAM-0023 | major    | QS-5     | A temporary worktree left by a crash blocks every later merge check of its unit of work       | Remove an existing worktree at the own path before adding the new one           |
| ATAM-0024 | minor    | —        | GateCheckStep skips `mark-dispatching`, `mark-dispatched`, and the re-dispatch after escalate | Add the subcommands to the DSL view and 6.4.1                                   |
| ATAM-0025 | minor    | —        | No view shows what follows a refused story merge                                              | Add the path after a refusal and name the dry run in RunByHand                  |
| ATAM-0026 | minor    | —        | Long descriptions make the new views unreadable                                               | Shorten the descriptions, split RunLifecycleComponents, re-export, and look     |

The three `major` risks are finding files under `docs/findings/`. The three `minor` defects belong to the document class and are register files under `docs/findings/register/document/`.

## Tradeoff summary

| Tradeoff                                                   | Side chosen       | Cost                                                             |
| ---------------------------------------------------------- | ----------------- | ---------------------------------------------------------------- |
| Rerun every gate at the merge, or trust the stored results | Rerun (ADR-0038)  | Each gate runs twice, and each rerun builds a `uv` environment   |
| Temporary worktree, or rerun in the checkout               | Worktree          | State to create and remove; a crash leaves a worktree            |
| One lifecycle, or two processes                            | One (ADR-0037)    | A run by hand needs a ledger and story branches                  |
| One guardrail script, or one rule set per tool             | One (ADR-0039)    | One extra process per shell call in pi and OpenCode              |
| Tests against the source, or copy at the merge             | Source (ADR-0040) | A merged script reaches the sessions only after `update-factory` |
| Retry without a flag on the last tier                      | No flag (BR-116)  | An agent can start a retry the User did not ask for              |

## Verification of the fixes

Pass 2 checks the fixes of ATAM-0021 to ATAM-0026. It is a narrow check of the fixes, not a new review pass. It covers the architecture commits `5c41c1d6` and `92775baa`, the contract commits `37f779d9`, `b7041766`, and `5a68f29d`, and the feature file commits `6842e07b`, `5cfc3278`, and `4e5b34f7`. `arch-lint --docs-dir docs/arc42` again found 0 errors and the dismissed ARCH-PARSE warning, and exited `0`.

| ID        | Status   | Evidence                                                                                                                                                                                                                                                                                                                   |
| --------- | -------- | -------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| ATAM-0021 | resolved | By hand, `merge-story` runs `premerge-check` while the story branch is checked out and checks out the feature branch only after exit `0`. The `merge-story` contract, BR-124, the DSL relationship from `dispatch` to Project Filesystem, RunByHand, PremergeStoryCheck, 5.13, and 6.24 say so, and two Scenarios check it |
| ATAM-0022 | resolved | The OpenCode entry passes each `shell` command and the JavaScript of each `execute` call to `block-dangerous-git.sh`. ADR-0039, the DSL component, GitGuardrailOneScript, 5.13, 6.25, chapters 7 and 9, the guardrail contract, and a Scenario Outline name both tools                                                     |
| ATAM-0023 | resolved | `premerge-check` runs `git worktree remove --force` on its own path and then `git worktree prune` before it adds the worktree (BR-123). The paths are `premerge/<id>` and `premerge/feature` in the contract, ADR-0038, the DSL, 5.1, 5.13, 6.24, and the Scenarios                                                        |
| ATAM-0024 | resolved | GateCheckStep and 6.4.1 run `mark-dispatching` before the spawn and `mark-dispatched` after the fix commit, and `re-dispatch` follows `escalate` in every case                                                                                                                                                             |
| ATAM-0025 | resolved | 6.24.1 routes each cause of a refused merge, and the views PremergeStoryRefused and MergeCheckoutRefused show two of them. RunByHand names `merge-story --dry-run`, and the contract defines the dry run                                                                                                                   |
| ATAM-0026 | resolved | Each changed DSL description is one sentence of 102 to 176 characters. RunLifecycleComponents is split into RunLifecycleDispatch, RunLifecycleMergeCheck, and RunLifecycleGuardrail in 5.13. The renders of RunLifecycleDispatch and MergeCheckoutRefused show legible names and labels                                    |

### The stakeholder decisions of 2026-11-18

The contracts and the architecture match each decision:

- By hand, `merge-story` runs `premerge-check` first and checks out the feature branch only after exit `0`.
- The OpenCode guardrail checks the JavaScript of every `execute` call, and no document records a residual risk.
- `premerge-check` removes a leftover worktree at `premerge/<id>` or `premerge/feature` first.
- A refused checkout or merge exits `1`, names the files and the checkout, merges nothing, and leaves the entry `dispatched` (BR-124). In an orchestrated run, `merge-story` refuses on an uncommitted tracked change in the worktree of the feature branch. `dispatch.refuse_dirty_feature_worktree` in `docs/testing.yaml` turns the refusal off and defaults to `true`.
- A gate that passes in the story worktree and fails in the temporary worktree gets no rule. The gate row of 6.24.1 ends with the attempt limit (HasStopped).

The order of the worktree check is open in the text: the contract and BR-124 say only "before it merges", and only the DSL relationship, the 6.24.1 row "no check fails", and the Scenario step "premerge-check exits 0" imply that it runs after `premerge-check`.

### Backing of the refusal routes in 6.24.1

- A failing gate goes back to the gate-check step. The Scenario "A refused premerge-check sends a story in an orchestrated run back to the gate-check step" and BR-116 back this route.
- An open blocking finding, or no code review of the current branch head, gets a fresh developer agent and a repeat review. The refusal itself is backed by the Scenarios "An open blocking finding at the branch head is refused and named" and "A story branch without a matching review report is refused". The loop is backed by "A repeat review follows each fix of a blocking finding". No rule or Scenario sends a refused merge into that loop, so the link from the refusal to the loop has no backing.
- A failed base, diff size, or scope check stops for the User. No rule or Scenario backs this route. BR-115 and HasStopped stop a unit of work for its scope only when `dispatch escalate` refuses it. After a refused merge check the entry stays `dispatched`, so HasStopped does not hold, and the decision-point Scenario Outline lists no refused merge check.

### Rows of the spec-feedback report

- The row for `docs/spec/interface-contracts.md` is `confirmed`. The `merge-story` contract defines `--dry-run`: it runs `premerge-check` with the same scope and `--max-files`, merges nothing, changes no ledger entry, and by hand runs while the story branch is checked out.
- The row for `run-lifecycle.feature` is `rejected`. Commit `4e5b34f7` adds a Scenario for the gate route only. The routes for an open blocking finding and for a failed base, diff size, or scope check still have no Scenario, as the section above shows. The stakeholder settled the case of the gate that passes only in the story worktree, so that part of the row needs no Scenario.

### Notes of this pass

These notes go to the architecture agent. None of them blocks planning, so this pass files no finding.

- Chapter 10 has no QS-30. ADR-0037 scores QS-30 as a Pugh criterion with weight 3, and ADR-0038 and 6.22 cite it. The resolution of ATAM-0023 names QS-30 as added, but commit `5c41c1d6` changes chapter 10 only in one link of QS-6. The criterion has no measure until chapter 10 and its priority table hold QS-30.
- The stimulus of QS-29 names only shell forms. An `execute` call in OpenCode is missing from it, although ADR-0039 and the Scenarios cover the call.
- In MergeCheckoutRefused, the orchestrated steps 5 to 7 show no `premerge-check` call before the worktree check.
- QS-6 still says that the gates run "after each developer commit", as Pass 1 noted.

## Readiness

The architecture is ready for planning. All six findings are resolved, and no new defect or risk blocks planning. Next, run the planning agent.

Two gaps stay open beside planning. The stakeholder decides whether the requirements agent adds Scenarios for the two unbacked refusal routes before the story of the implementation agent is cut. The architecture agent adds QS-30 to chapter 10.
