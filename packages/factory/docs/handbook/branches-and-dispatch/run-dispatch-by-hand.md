---
title: Run dispatch by hand
type: how-to
status: implemented
order: 20
description: Build the stories of a feature one at a time in the primary checkout, with the ledger and checks of an orchestrated run.
---

# Run dispatch by hand

A run by hand builds one story at a time in the primary checkout and adds no worktree. Start it with the implementation agent's flag `--manual`.

1. `dispatch init --mode by-hand` creates the feature branch from its base branch, `dev`.
2. `dispatch prepare-story` creates each story branch and checks it out in the primary checkout.
3. The developer agent commits on the story branch, and the code-review agent reviews the commit. A fresh developer agent fixes each blocking finding.
4. The implementation agent stops before each decision point. Give your go to continue.
5. `dispatch merge-story` merges the story branch. Push the result.

[Dispatch runs](dispatch-runs.md) explains the ledger and the waves that a run by hand shares with an orchestrated run.
