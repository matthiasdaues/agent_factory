---
schema_version: 2
scope: global
title: Ledger as Run Receipt
status: draft
owner: stakeholder
created: 2026-11-22
updated: 2026-11-22
supersedes:

impact:
  scope: cross_component
  architecture_change: false
  external_contract_change: true
  boundaries:
    - packages/factory/scripts/dispatch
    - packages/factory/scripts/dispatch_lib.py
    - packages/factory/scripts/premerge-check
    - packages/factory/agents/implementation-agent.md
    - docs/spec/validation-rules.md
    - docs/spec/interface-contracts.md
    - docs/spec/state-machines.md

governance:
  assurance: elevated
  risk_domains:
    - data_integrity
    - operations

estimate:
  as_of: 2026-11-22
  basis: judgment
  confidence: low
  human_review_hours: unknown
  normalized_tokens: unknown
  estimated_consumption: unknown
---

# Feature Request: Ledger as Run Receipt

## Primer

An orchestrated run keeps a ledger: one file that lists every unit of work of
the run, with its state, its attempts, its branch and the reason it stopped,
plus one record per closed wave. The ledger is the inventory of the running
run. Today `dispatch close` deletes it after the merge into `dev`, so nothing
of it reaches the repository.

## Summary

Before the feature branch merges into `dev`, the run freezes a copy of its
ledger at a fixed path in the repository. The merge carries the copy into
`dev` as the receipt and log of the run.

## Motivation

The run report of `feature/run-lifecycle` had to rebuild attempts, waves and
merge counts from the session transcript, because `dispatch close` had
deleted the ledger. A frozen copy makes those figures a lookup, and it shows
later readers which units of work the merge contains and how each one ended.

## Core Principles

- The receipt is a copy of the ledger as it stood, not a new summary.
- The receipt is made by a script, never by hand.
- The merge check refuses a merge without a current receipt.

## Design

- **The copy:** a new step writes the ledger to
  `docs/reviews/runs/<feature-branch>/dispatch-ledger.yaml`, with the slash of
  the branch name replaced by a hyphen, and commits it on the feature branch.
  The step runs after the last wave closes and after the feature checks.
- **The check:** `premerge-check dev <feature-branch>` refuses the merge when
  the receipt is missing or differs from the live ledger.
- **The close:** `dispatch close` deletes the working ledger as before. The
  receipt stays in `dev`.

## Scope

- In: the copy step, the merge check, the text of the implementation agent,
  and the rules and contracts that describe them.
- Out: a new format or a summary of the ledger; receipts of runs that already
  closed.

## Design Details

The run `feature/crap-gate-setup` made its receipt by hand, as a one-time
copy, so the step can be checked against a real ledger.

## Open Questions

- Does the copy step belong to `dispatch close-wave` of the last wave, to a
  new subcommand, or to the feature checks?
- Does the receipt keep the ledger's paths to worktrees, which no longer
  exist after the close?
- How does `dispatch` stop finding a receipt as a ledger? In the CRAP gate
  run, `dispatch close` found the receipt inside the invocation worktree as a
  second ledger. The search could read only
  `.current-work/<branch>/dispatch-ledger.yaml` at the top of a run folder, or
  the receipt could get another file name. The error's hint "pass --ledger
  <path>" should also say that the option goes before the subcommand (T-0426).

## Completion Criteria

- A run that reaches the merge check has its receipt committed on the feature
  branch.
- `premerge-check dev <feature-branch>` refuses a merge without a current
  receipt.
- After `dispatch close`, the receipt is in `dev` and the working ledger is
  gone.

## Guiding Rule

The run leaves its own record.

# Appendix

## Decisions

| ID     | Date       | Type     | By          | Decision                                                                                                                                                                       | Source                       |
| ------ | ---------- | -------- | ----------- | ------------------------------------------------------------------------------------------------------------------------------------------------------------------------------ | ---------------------------- |
| DEC-01 | 2026-11-22 | decision | stakeholder | The ledger of a run goes into the repository before the merge into `dev`, as the receipt and log of the run. A frozen copy on the feature branch carries it through the merge. | session of the CRAP gate run |

## Review findings

| ID  | Pass | Severity | Class | Status | Finding | Resolution |
| --- | ---- | -------- | ----- | ------ | ------- | ---------- |
