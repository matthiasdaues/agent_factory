---
id: 0037
status: accepted
evaluation: pugh-matrix
---

# One lifecycle for runs orchestrated and by hand

Amends [ADR-0012](0012-dispatcher-owned-semantic-gate-loop.md) and [ADR-0029](0029-per-story-drift-reports-block-the-wave-close.md).

## Context

A run is everything the Factory does for one feature branch, from `dispatch init` to `dispatch close`. The Factory has two ways to drive a run. In an orchestrated run, the implementation agent starts stories in waves. In a run by hand, the human decides when each story starts.

Take a function with a CRAP score of 42 against the threshold of 30. In an orchestrated run, `premerge-check` blocks its merge. By hand, there is no story branch, no ledger, and no merge step, so `premerge-check` never runs. The developer agent runs the gates itself, and nobody reads the result. So the function merges.

The documents also disagree with each other and with the code. Three sources name three owners for setting a story to `done`. At the cap on attempts, ADR-0012 marks a story `blocked`, and the implementation agent marks it `failed`. ADR-0029 runs the drift sessions after each merge and makes the next `merge-story` wait for them.

The accepted proposal [run-lifecycle.md](../proposals/run-lifecycle.md) settles the design. The [feature file](../spec/features/run-lifecycle.feature) and the [Ledger Entry Lifecycle](../spec/state-machines.md#ledger-entry-lifecycle) hold its behaviour. Three options were weighed:

- **A: Two processes** (baseline). By hand keeps its own process without branches, ledger, or merge step.
- **B: One lifecycle, two ways to drive it.** Both ways use the same branches, ledger states, story workflow, checks, and close. They differ only in who starts a story, whether stories run in parallel, and who runs the commands that need a person.
- **C: By hand as a one-story orchestrated run.** Each story runs in its own worktree, as in an orchestrated run, and the human only gives the go.

## Decision

Option B. A run by hand works in the primary checkout, and an orchestrated run works in worktrees under `.current-work/`. Everything else is shared.

| Criterion                                                                      | Weight | A: Two processes (baseline) | B: One lifecycle | C: One-story orchestrated run |
| ------------------------------------------------------------------------------ | ------ | --------------------------- | ---------------- | ----------------------------- |
| Safety (QS-28): a failing gate cannot merge on either way                      | 3      | 0                           | +1               | +1                            |
| Resilience (QS-30): a new session continues an interrupted run from the ledger | 3      | 0                           | +1               | +1                            |
| Controllability (QS-2): the human sees each step in the checkout they work in  | 2      | 0                           | 0                | −1                            |
| Clean Architecture: one code path and one rule set for both ways               | 2      | 0                           | +1               | +1                            |
| Simplicity: the commands and state that a run by hand needs                    | 2      | 0                           | −1               | −1                            |
| **Weighted total**                                                             |        | **0**                       | **+6**           | **+4**                        |

B wins by two points over C. The difference is the controllability criterion. A weight of 1 on it would leave B one point ahead.

The shared lifecycle has these parts:

1. **The story workflow.** The developer agent implements the story test first and commits. The code-review agent reviews the story branch, and a fresh developer agent fixes each blocking finding until a repeat review leaves none open. The implementation agent then runs the gate-check step. `dispatch merge-story` merges the story. The developer agent never runs a gate script and never sets `done`.
2. **The gate-check step on both ways.** The implementation agent runs the gates in both ways. This amends the gate execution sequence of ADR-0012: a failing gate gets a fresh developer agent within `gates.attempts` counted attempts on the story's tier, and then `gates.attempts_escalated` attempts on the next tier. Both values live in `docs/testing.yaml`, and `0` turns escalation off. Every story that uses up its attempts may escalate. A story whose gate still fails at the end is `failed`, not `blocked` (BR-114 to BR-116).
3. **One owner for `done`.** Only `dispatch merge-story` sets `done` for a story, or `resolved` for a finding, in the merge commit (BR-118).
4. **A red test suite moves the branch back.** When the test suite fails after a merge, `merge-story` moves the feature branch back to the commit before the merge and sets the story `blocked`. A revert commit would make git treat the story's commits as merged, so a second attempt would bring in nothing. The feature branch is not shared yet, so nobody has built on the failed merge.
5. **Drift sessions at the wave close.** This amends ADR-0029. The implementation agent spawns the owner and then the reviewer of each drift row at the wave close, not after each merge, and `merge-story` no longer waits for them. So a story merge and a drift session never commit on the feature branch at the same time. By hand, each story is a wave of its own, so its report is handled before the next story starts (BR-064).
6. **Guidance by hand.** The implementation agent runs every `dispatch` command in both ways, except `return-story`, `close`, and `close --drop`, which the human runs. By hand, it stops before a story starts, before a story merges, when a story stops, and before the merge into `dev`, and it waits for the human's go. Before the go for a merge, it shows the output of `dispatch merge-story --dry-run`. By hand, `merge-story` runs `premerge-check` while the story branch is checked out and checks out the feature branch only after exit `0`. So a refused merge leaves the primary checkout on the story branch, and a changed file of the human cannot make the checkout fail before the check decides.

## Consequences

- A run by hand needs a ledger and story branches. The human starts it with the implementation agent, not with a plain developer session.
- Only one run by hand can be active, because it needs the primary checkout. Orchestrated runs can be active beside it (BR-112).
- `dispatch merge-story` no longer waits for drift sessions, so the merges of a wave run back to back. The specification still lags the code by one wave at most (QS-17).
- A story with persistent gate failures still costs up to six developer spawns with the defaults. ADR-0012 states the same bound.
- `dispatch` loses `mark-done`. A tool or document that calls it breaks and must use `merge-story`.
- [6.22](../arc42/06_runtime_view.md#622-a-run-from-init-to-close) shows both ways, [6.23](../arc42/06_runtime_view.md#623-the-story-workflow) shows the story workflow, and [6.4](../arc42/06_runtime_view.md#64-gate-check-step) shows the gate-check step.
