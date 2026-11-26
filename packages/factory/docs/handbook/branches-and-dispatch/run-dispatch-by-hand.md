---
title: Run dispatch by hand
type: how-to
status: implemented
order: 20
description: Build the stories of a feature one at a time in the primary checkout, with the ledger and checks of an orchestrated run.
---

# Run dispatch by hand

A run by hand builds one story at a time in the primary checkout and adds no worktree. Start it with the implementation agent's flag `--manual`.

1. `dispatch init --mode by-hand` creates the feature branch from its base branch, `dev`, and writes the ledger.
2. `dispatch prepare-story <story-id>` creates the story branch and checks it out in the primary checkout. The implementation agent stops first, and you give your go.
3. `dispatch mark-dispatching <story-id>` marks the story. Then the developer agent implements it and commits on the story branch.
4. `dispatch mark-dispatched <story-id>` records the finished work. `dispatch verify-story <story-id> --sha <sha>` checks each commit the developer agent reports.
5. The code-review agent reviews the commit. A fresh developer agent fixes each blocking finding, and the review repeats.
6. The implementation agent runs the gate-check step on the story branch.
7. After your go, `dispatch merge-story <story-id>` merges the story branch. Push the result.
8. `dispatch close-wave <wave>` closes the story's wave. Close it before the next story starts at step 2.

The implementation agent runs every command. It stops before steps 2 and 7, and you give the go. [The agent definition](../../../agents/implementation-agent.md#workflow--run-by-hand) holds the details of each step.

[Dispatch runs](dispatch-runs.md) explains the ledger and the waves that a run by hand shares with an orchestrated run.
