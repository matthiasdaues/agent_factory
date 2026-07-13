---
title: Dispatch Contract
category: implementation
enforcement: dispatch-prompt clause (human/agent-authored discipline) — not mechanically gate-checked
version: 1.0.0
---

# Dispatch Contract

Governs how any agent that spawns its own sub-agents must address them, and how large a single dispatch is allowed to grow before it must be split and checkpointed. Distinct from [branching-policy.md](branching-policy.md): that rulebook governs branch/worktree mechanics for a dispatch; this one governs the dispatch's messaging contract and its size. Both are cited together from any agent's dispatch step.

## Project-Specific Rules

Canonical statements: [rules.md § Dispatch](../rules.md#dispatch).

### Sub-Agent Addressing

An agent that spawns its own sub-agents must give each one **a resolvable instance ID** to report back to — never its own agent *type* name. A type name (for example `reconciliation-agent`) names a role, not a routable recipient; a reply addressed to it cannot be delivered back to the specific instance that sent the sub-agent out; it strands, and surfaces to whatever session is listening instead, requiring a manual relay.

Every dispatch prompt that may itself spawn sub-agents carries this clause, verbatim:

> If you spawn sub-agents, give each one **your resolvable instance ID** as the address to report back to — never your agent *type* name. Include, verbatim, in each sub-agent's prompt: "Report your result to instance `<PARENT_INSTANCE_ID>`." Do not block indefinitely waiting on a sub-agent's reply: if a sub-agent declines out-of-scope work or does not respond, do the work yourself rather than waiting.

Motivating example: a reconciliation-agent instance in the 2026-07-12 session addressed its own sub-agents by type name; their replies stranded, surfaced to the orchestrating session for manual relay, and the parent blocked indefinitely on a reply that was never coming until told to stop waiting.

### Dispatch Scope Cap And Checkpointing

A single dispatch that tries to cover an entire codebase in one pass ("relentless weeding of the whole codebase," "reconcile everything") is also the dispatch most likely to be reasoning against a stale base for the longest before anyone checks it, and the one an API spend limit is most likely to kill mid-run.

- **Cap the scope of a single dispatch.** Split a whole-codebase task into per-module or per-directory dispatches, each independently verifiable and mergeable via [branching-policy.md § Pre-Merge Diff Check](branching-policy.md#pre-merge-diff-check). A smaller dispatch fails cheaper, and its diff is easier to certify as in-scope.
- **Checkpoint long tasks with commits between rounds.** A dispatch that must stay large commits its work between rounds rather than holding everything uncommitted until the end — a spend-limit death mid-round then loses only that round's work on resume, not the whole dispatch.

Motivating example: the 2026-07-12 session's orchestrator-weeding and doc-reconciliation dispatches each hit the org API spend limit multiple times, at 300k–465k tokens per resume cycle; both were single, whole-codebase-scoped dispatches.

## Enforcement

Human/agent-authored discipline, not a git hook or lint gate — a sub-agent's addressing choice and a dispatcher's scope-splitting decision both happen inside the dispatching agent's own prompt-composition step, before any tool call a hook could intercept. Enforced by including the clauses above, verbatim, in every dispatch prompt that spawns sub-agents or covers more than one module/directory. See [implementation-agent.md § Workflow](../../agents/implementation-agent.md#workflow) for the current concrete application.

## References

- [rules.md § Dispatch](../rules.md#dispatch)
- [branching-policy.md](branching-policy.md) — the branch/worktree half of the dispatch contract (Verify-Base Preamble, Declared Base SHA, Pre-Merge Diff Check)
- [implementation-agent.md § Workflow](../../agents/implementation-agent.md#workflow) — the current dispatcher applying this contract
- [reconciliation-agent.md](../../agents/reconciliation-agent.md) — the agent whose incident motivated the Sub-Agent Addressing rule
- [docs/reviews/retro-2026-07-12.md](../../../docs/reviews/retro-2026-07-12.md) — the session that motivated both rules
