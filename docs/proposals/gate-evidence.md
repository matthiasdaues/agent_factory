---
schema_version: 2
scope: global
title: Gate Evidence
status: draft
owner: agent-factory
created: 2026-11-04
updated: 2026-11-04
supersedes:

impact:
  scope: cross_component
  architecture_change: tbd
  external_contract_change: true
  boundaries:
    - packages/factory/scripts/premerge-check
    - packages/factory/scripts/verify-base
    - packages/factory/scripts/crap-score
    - packages/factory/scripts/dependency-check
    - packages/factory/scripts/test-design-verify
    - packages/factory/scripts/module-graph-check
    - packages/factory/config/hooks/block-dangerous-git.sh
    - packages/factory/agents/implementation-agent.md
    - packages/factory/rulebooks/rules.md

governance:
  assurance: elevated
  risk_domains:
    - security
    - reliability

estimate:
  as_of: 2026-11-04
  basis: judgment
  confidence: low
  human_review_hours: unknown
  normalized_tokens: unknown
  estimated_consumption: unknown
---

# Feature Request: Gate Evidence

## Primer

The primer is written last, by the `write-primer` skill, once the design is settled.

## Summary

Several Factory gates write an untracked receipt under `.current-work/`, and a later step trusts that receipt instead of checking for itself. This stub records the problem and three candidate directions. It decides nothing. A later grilling session picks a direction and turns the stub into a full proposal.

## Motivation

A gate checks the code and, on a pass, writes a file. A later step, such as the merge guardrail, reads that file and lets the work through. The later step never runs the check itself. These files are receipts. The table below lists the receipts in use today. All of them share three faults:

1. **Forgeable.** An agent with a shell can write any file the gate writes. The receipt lives on the agent's own machine, so no local check can tell a real receipt from a forged one.
2. **Invisible to review.** The receipts are untracked. A human who reads the git history cannot see that a gate ran.
3. **Stale or lost.** Removing a worktree, cloning fresh, or rebasing loses the receipt or detaches it from the code it checked.

| Receipt                                               | Written by                                                                   | Trusted by                                                               | Where it is described                                                                                                                                                                                                              |
| ----------------------------------------------------- | ---------------------------------------------------------------------------- | ------------------------------------------------------------------------ | ---------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| `.current-work/premerge-check-ok`                     | `premerge-check`                                                             | the merge check in the git guardrail                                     | [rules.md § Git workflow](../../packages/factory/rulebooks/rules.md#git-workflow); [premerge-check](../../packages/factory/scripts/premerge-check)                                                                                 |
| `.current-work/verify-base-ok`                        | `verify-base`                                                                | the commit check in a worktree, in the git guardrail                     | [block-dangerous-git.sh](../../packages/factory/config/hooks/block-dangerous-git.sh); [agent-execution-isolation-and-distribution.md § Defect register](agent-execution-isolation-and-distribution.md#defect-register--amendments) |
| `.current-work/<gate>/<story-id>.json`                | `crap-score`, `dependency-check`, `test-design-verify`, `module-graph-check` | `premerge-check`                                                         | [premerge-check](../../packages/factory/scripts/premerge-check); [implementation-agent.md § Gate execution](../../packages/factory/agents/implementation-agent.md#gate-execution)                                                  |
| `.current-work/<feature-branch>/dispatch-ledger.yaml` | the dispatcher agent                                                         | the next wave, the wave close, and the commit check in the git guardrail | [rules.md § Dispatch](../../packages/factory/rulebooks/rules.md#dispatch)                                                                                                                                                          |

[manual-mode-gates.md](manual-mode-gates.md) first proposed one more receipt, a `story-gates` marker. That proposal now avoids the receipt provisionally: its `story-done-gate` hook reruns `story-gates` on the closing commit. It leaves the general question to this proposal (DEC-01). [agent-execution-isolation-and-distribution.md § Intended future boundary](agent-execution-isolation-and-distribution.md#intended-future-boundary) already states that an agent session cannot turn a repository-local marker into authority. It does not say what replaces the markers.

## Design

### Candidate directions

One case serves all three directions: a developer agent sets story ST-0412 to `done` while one mutant survives.

- **The verifier reruns the check.** No receipt exists. The step that trusts a gate today runs the gate itself. The commit or the merge fails on the surviving mutant. The cost is time: the slow gate runs at the checking point.
- **The authoritative check runs where the agent cannot write.** CI runs the gates on the pushed branch, and the merge requires that status. Local receipts stay only as a convenience for the agent. The merge of ST-0412 waits for CI and fails on the surviving mutant. `.agent-factory/config/project-context.json` lists no CI for this repository, so this direction needs CI first.
- **Tracked evidence.** The gate writes its result into git, for example as a commit trailer or as git notes. A reviewer sees in the history that the mutation gate ran for ST-0412 and what it found. An agent can still write the trailer or the note without running the gate.

Only the first two directions remove forgery. In both, the agent cannot produce the pass without the check passing. Tracked evidence fixes the second and third fault, not the first. The directions can combine, for example a rerun at the merge with tracked evidence for review.

## Scope

**In the first release:**

- To be set when a direction is chosen. The receipts in the table under [Motivation](#motivation) are the candidates.

**Explicitly deferred (do NOT plan stories for these):**

- **The whole proposal.** It is a `draft` stub. No story is planned until a direction is chosen and the proposal is `open`.

## Open Questions

- **Which direction, or which combination?** The answer sets the Design and the Scope.
- **Which receipts must go, and which may stay as a convenience?** The dispatch ledger also records wave state, so it may stay as a record while no step trusts it as proof.
- **Does a rerun at the merge cost too much?** Mutation testing is the slowest gate. A rerun needs a measured time per story before it is chosen.

## Completion Criteria

- Set when a direction is chosen.

# Appendix

## Decisions

| ID     | Date       | Kind     | Decided by  | Decision                                                                                                              | Raised by                                                            |
| ------ | ---------- | -------- | ----------- | --------------------------------------------------------------------------------------------------------------------- | -------------------------------------------------------------------- |
| DEC-01 | 2026-11-04 | decision | stakeholder | The receipt problem gets its own proposal; manual-mode-gates uses a provisional rerun until this proposal settles it. | [manual-mode-gates open item 1](manual-mode-gates.md#open-questions) |

## Review findings

No review has run yet.

| ID  | Pass | Severity | Check | Status | Finding | Resolution |
| --- | ---- | -------- | ----- | ------ | ------- | ---------- |

## Review passes

| Pass | Date | Reviewed commit | Disposition | Failed checks | Summary |
| ---- | ---- | --------------- | ----------- | ------------- | ------- |
