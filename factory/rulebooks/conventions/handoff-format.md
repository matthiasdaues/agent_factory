---
title: Session Handoff Format
category: orchestration
enforcement: handoff author and receiving agent
version: 1.0.0
---

# Session Handoff Format

A handoff is a restart contract, not an append-only transcript. The next agent
must be able to identify the current repository state and next safe action
without reconciling contradictory sections.

## Authoritative current state

Put one authoritative section first. It contains:

- current checkout path and branch;
- local branch tip as an exact SHA;
- configured upstream and its exact SHA, or `none`;
- ahead/behind counts relative to that upstream;
- modified and untracked files, including their owner when known;
- completed work and its verification evidence;
- open work, blockers, and the next safe action;
- intentionally retained worktrees or branches and why they are still active.

Gather branch evidence directly from Git. Do not infer local state from a
decorated log entry or use an approximate "about N commits ahead" statement.

## Historical context

History is optional. Keep only facts that explain a current constraint or
decision. When a milestone resolves an instruction, replace that instruction in
the current-state section. If older narrative must remain, move it below a
`Historical context` heading and mark it non-authoritative; do not leave stale
open issues inline with current ones.

## Resume rule

The receiving agent reads the authoritative section first and verifies its Git
claims before acting. A mismatch is reported and resolved from observable state;
the handoff never overrides the repository.

## References

- [git-workflow.md § Record branch state explicitly](git-workflow.md#record-branch-state-explicitly)
- [dispatch-contract.md § Verify Sub-Agent Reports Against State](dispatch-contract.md#verify-sub-agent-reports-against-state)
