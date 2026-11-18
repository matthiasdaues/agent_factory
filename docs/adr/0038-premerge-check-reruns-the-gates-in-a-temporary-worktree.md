---
id: 0038
status: proposed
evaluation: pugh-matrix
---

# premerge-check reruns the gates in a temporary worktree

Amends [ADR-0012](0012-dispatcher-owned-semantic-gate-loop.md).

## Context

`premerge-check` decides whether a unit of work may merge. Today it reads the result files that the gate-check step wrote under `.current-work/<gate>/<id>.json`. A result file says nothing about the code that merges. Take ST-0350: `dependency-check` passed and wrote its result, and then a fix commit added an import that breaks a rule. The stored result still passes, so the merge goes through. A result file is also a plain file that any session can write.

[run-lifecycle.md § Checks at the merge](../proposals/run-lifecycle.md#checks-at-the-merge) settles that `premerge-check` runs every gate again at the branch head. The question is where it runs them. Three options were weighed:

- **A: Read the stored results** (baseline).
- **B: Rerun in the checkout that holds the branch.** That is the story worktree in an orchestrated run and the primary checkout in a run by hand.
- **C: Rerun in a temporary worktree at the branch head.** `premerge-check` adds a detached worktree at the head commit under `.current-work/<feature-branch>/premerge/<id>`, runs the gates and the test suite there, and removes it.

Option B touches the files the human works on. By hand, the primary checkout may hold a changed tracked file or an untracked test file. Such a file takes part in the run, and the gates measure code that does not merge. A stash would hide it, but a stash in the primary checkout is a step the human does not expect.

## Decision

Option C.

| Criterion                                                       | Weight | A: Stored results (baseline) | B: Rerun in the checkout | C: Rerun in a temporary worktree |
| --------------------------------------------------------------- | ------ | ---------------------------- | ------------------------ | -------------------------------- |
| Safety (QS-6): a stale or forged result cannot pass the merge   | 3      | 0                            | +1                       | +1                               |
| Safety (QS-6): the gates measure exactly the commit that merges | 2      | 0                            | 0                        | +1                               |
| Controllability (QS-2): no file of the human's checkout changes | 3      | 0                            | −1                       | 0                                |
| Cost: time per merge                                            | 1      | 0                            | −1                       | −1                               |
| Simplicity: state that the check creates and must remove        | 2      | 0                            | 0                        | −1                               |
| **Weighted total**                                              |        | **0**                        | **−1**                   | **+2**                           |

C wins by two points over the baseline. With a weight of 3 on simplicity, C still leads by one point.

The rerun works as follows:

- The worktree is detached at the head commit, because git does not check out one branch in two worktrees, and the branch is checked out already.
- Git ignores `.agent-factory/`, so the temporary worktree holds no installed copy. `premerge-check` runs each gate script from the installed copy of the checkout it was called from, with the temporary worktree as the source root (OI-10). The worktree builds its own `uv` environment.
- `premerge-check` reads the review reports, the finding files, and the register files at the branch head with git, not from the folder it runs in.
- The one stored result it reads is the result file of `mutation-testing`, until [mutation-gate.md](../proposals/mutation-gate.md) settles how that gate runs at the merge (BR-066).
- The feature merge check `premerge-check dev <feature-branch>` runs the full test suite in a temporary worktree at the head of the feature branch in the same way (RL-G13).

This amends step 6 of the gate execution sequence of ADR-0012: the gate-check step still runs every gate, and `premerge-check` runs them again instead of reading their results.

## Consequences

- A slow gate runs twice per unit of work, once in the gate-check step and once at the merge. The first rerun in a worktree also builds the `uv` environment.
- No file in the story's checkout or the primary checkout changes, and no stash is made.
- A crash can leave a temporary worktree behind. `dispatch close` removes it with the other worktrees of the run.
- The gate result files stay, because the implementation agent hands a failing gate's output to the next developer agent. `dispatch close` removes them.
- A trusted receipt that would let the merge skip a gate is the subject of [gate-evidence.md](../proposals/gate-evidence.md), not of this decision.
- [6.24](../arc42/06_runtime_view.md#624-the-merge-check-of-a-story) shows the rerun.
