---
title: Phase Handoff Format
category: orchestration
enforcement: handoff-lint, handoff author, and semantic reviewer
version: 2.0.0
---

# Phase Handoff Format

A phase handoff is a CLI-neutral restart contract, not a transcript summary.
Dense prose removes wording, never informational detail. The next participant
must be able to identify what was decided, what remains open, the exact
repository state, the durable evidence, and the next safe action without
replaying the outgoing session.

## Boundary set

The accepted Factory delivery flow contains these boundaries:

- requirements → review;
- review → architecture;
- architecture → review;
- review → remedies;
- remedies → planning;
- planning → implementation.

Every arrow is a mandatory handoff. The outgoing session must stop after
structural lint and independent semantic review pass. The incoming phase starts
in a fresh session, reads the handoff first, verifies its Git claims, and then
reads referenced artifacts in bounded, on-demand chunks. Work that continues
within the same phase is exempt; it needs neither a handoff nor a restart.

Later playbook steps may name more specific author, reviewer, reconciliation,
quality, or remedy roles. They apply this contract whenever the next work
crosses one of the Factory phases above; role labels do not weaken the boundary.

## Required document shape

Use these exact level-two headings and declared fields. Values are dense prose,
not placeholders. A literal `none` is required when there are no open items,
upstream, retained worktrees/branches, or other applicable entries.

```markdown
# Phase Handoff

## Boundary

Outgoing phase: <phase>
Incoming phase: <phase or review/remedy role>
Boundary: <outgoing> -> <incoming>

## Repository state

Checkout: <absolute path or path relative to repository root>
Branch: <local branch>
HEAD: <exact lowercase 40-character SHA>
Upstream: <configured upstream ref or none>
Upstream SHA: <exact lowercase 40-character SHA or none>
Ahead: <non-negative integer>
Behind: <non-negative integer>
Working tree: <clean or complete modified/untracked paths and owners>
Retained work: <worktrees/branches with reasons or none>

## Decisions and open items

Decisions: <every material decision and its durable origin, or none>
Open items: <every finding, blocker, question, or none>

## Artifacts

- <repository-relative existing path>

## Gate and verification evidence

Gates: <commands and outcomes, including zero/error counts>
Verification: <tests, reviews, or other evidence and outcomes>

## Next action

<one unambiguous entry action for the fresh incoming session>

## Semantic review

Reviewer: <designated reviewer or pending assignment>
Status: <pending, passed, or failed>
Evidence: <outgoing artifacts, decisions, open items, and evidence compared>
```

The artifact list is authoritative and complete. Each entry is a
repository-relative path that exists when `handoff-lint` runs. Machine-consumed
SHAs are exact lowercase 40-character values; abbreviated or uppercase SHAs are
display-only and invalid here. Branch and upstream values come directly from
Git, including exact ahead/behind counts. History is omitted unless it explains
a current decision or constraint.

## Structural and semantic closure gates

Run `factory/scripts/handoff-lint <handoff-path> --repo-root <root>` before
closure. It reports every mechanically detectable missing section or field,
placeholder, malformed SHA or repository-state value, and missing referenced
path in one non-zero run. A clean result certifies structure and reference
integrity only. It cannot infer an undeclared decision, open item, evidence
item, or artifact, and therefore makes no semantic-losslessness claim.

After structural lint passes, a designated reviewer independently compares the
handoff with the outgoing phase's durable artifacts, decisions, open items, and
gate/verification evidence. An omission or distortion keeps phase closure
blocked. Correct the handoff, repeat structural lint, and repeat semantic review
until both pass. Only then may the outgoing session stop; it must not begin the
incoming phase itself.

## Resume rule

The fresh incoming session reads this document before any prior transcript or
large artifact. It verifies the declared checkout, branch, exact SHAs,
upstream, ahead/behind counts, and working tree against Git. A mismatch is
reported and resolved from observable repository state; the handoff never
overrides the repository. The prior transcript is not replayed.

## References

- [UC-11 — Cross a Phase Boundary Without Transcript Replay](../../../docs/spec/use_cases/UC-11-cross-a-phase-boundary.md)
- [git-workflow.md § Record branch state explicitly](git-workflow.md#record-branch-state-explicitly)
- [dispatch-contract.md § Verify Sub-Agent Reports Against State](dispatch-contract.md#verify-sub-agent-reports-against-state)
- [Accepted session-transcript proposal](../../../docs/proposals/proposal-session-transcript-token-control.md)
