---
id: 0040
status: proposed
evaluation: pugh-matrix
---

# The Factory tests run against the source

## Context

This repository holds the Factory twice. `packages/factory/` is the source. `.agent-factory/factory/` is the installed copy, which every session in this checkout runs: the scripts, the hooks, and the agent definitions.

Some tests run scripts from the installed copy. So `dispatch merge-story` copies the merged code into the installed copy before it runs the test suite. Take ST-0350, which changes `dispatch`. After its merge into the feature branch, the installed copy of the checkout where the merge ran holds the new `dispatch`. Every session in that checkout now runs code that has not reached `dev`, also sessions of other runs.

Two options were weighed:

- **A: `merge-story` copies the merged code into the installed copy** (baseline).
- **B: The tests run the code from `packages/factory/`, and `merge-story` copies nothing.** The installed copy changes only through `update-factory`, as in any other project.

## Decision

Option B. The Factory repository is a project like any other.

| Criterion                                                                            | Weight | A: Copy at the merge (baseline) | B: Tests run against the source |
| ------------------------------------------------------------------------------------ | ------ | ------------------------------- | ------------------------------- |
| Controllability (QS-2): sessions run only code that the human installed              | 3      | 0                               | +1                              |
| Testability (QS-3): the tests read the code under test, not a copy of it             | 2      | 0                               | +1                              |
| Simplicity: `merge-story` has no copy step                                           | 1      | 0                               | +1                              |
| Speed of use: a merged script runs in this checkout's sessions right after the merge | 1      | 0                               | −1                              |
| **Weighted total**                                                                   |        | **0**                           | **+5**                          |

B wins clearly.

The tests that read this repository's installed copy change to `packages/factory/`. A test that installs the Factory into a temporary project keeps reading that project's `.agent-factory/`. A link to this repository's `.agent-factory/` that only serves `scope-lint` with `.agent-factory/workstreams/` is no read of the installed copy (OI-08).

## Consequences

- `dispatch merge-story` leaves `.agent-factory/factory/` unchanged.
- In this repository, a changed script reaches the sessions only after `update-factory`. A run that changes `dispatch` or `premerge-check` still runs on the installed version of both scripts.
- `premerge-check` runs the gate scripts from the installed copy of the calling checkout ([ADR-0038](0038-premerge-check-reruns-the-gates-in-a-temporary-worktree.md)). So the gates of a run that changes a gate script measure the code with the installed version of that script. The test suite checks the new version.
- [7.1](../arc42/07_deployment_view.md#71-release-1-local-operator-workstation) describes the two copies.
