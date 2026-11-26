---
title: Dispatch runs
type: concept
status: implemented
order: 10
description: How the dispatch script owns branches, worktrees, and the ledger in an orchestrated run and in a run by hand.
---

# Dispatch runs

When a backlog is ready, the implementation agent builds its stories on story branches. The `.agent-factory/factory/scripts/dispatch` script owns the git state, the ledger, and the life of each branch and worktree. The agent decides the order of the script calls, and the scripts make every change of state.

The ledger is `.current-work/<feature-branch>/dispatch-ledger.yaml`. It is machine-readable and tracks the preparation, dispatch, verification, and merge of every story. The main subcommands:

- `dispatch init` starts the ledger of a feature branch.
- `dispatch prepare-wave` and `dispatch prepare-story` create the story branches and worktrees, record the declared base SHA, and run `verify-base`.
- `dispatch verify-story <story-id> --sha <sha>` checks that the reported commit exists on the expected branch.
- `dispatch merge-story <story-id>` runs `premerge-check`, merges the story, and runs the tests after the merge.
- `dispatch close-wave <wave>` appends a closing record with the completed, blocked, and next ready stories.

Stories run in waves. In an orchestrated run, the stories of one wave run in parallel, and the waves run one after another.

> Rule summary: The next wave launches only after the wave record exists. `dispatch close-wave` writes it once every story of the wave has merged or stopped and the wave's drift rows are handled.
> Source: [dispatch-contract.md § Wave Boundary As Hard Gate](../../../rulebooks/conventions/dispatch-contract.md#wave-boundary-as-hard-gate)

The tier rubric in [dispatch-contract.md](../../../rulebooks/conventions/dispatch-contract.md#tier-rubric) assigns each story the tier economy, standard, or strong. [Model matrix](../reference/model-matrix.md) explains the tiers.

## A run by hand

A run by hand keeps the ledger, the story workflow, and the checks of an orchestrated run. It runs one story at a time in the primary checkout and adds no worktree. Each story is a wave of its own, as [Run By Hand](../../../rulebooks/conventions/dispatch-contract.md#run-by-hand) defines. The implementation agent stops before each decision point and waits for your go. [Run dispatch by hand](run-dispatch-by-hand.md) shows the steps.

## Step boundaries

Each step has a manifest at `.current-work/<feature-branch>/<story-branch>/current-step.yml`. It declares the step's inputs, its outputs, and its `max_input_tokens`. The `step-guard` hook is installed, but it does not enforce these boundaries yet, because it does not find the manifests. Agents keep to their step boundary by discipline.
