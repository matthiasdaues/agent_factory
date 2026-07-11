# 0002. Session isolation via a fresh subprocess behind the CLIAdapter port

**Status**: Accepted

> **Superseded for the orchestrator, 2026-07-12 (PhaseRunner collapse):** Invoking agents as isolated subprocesses moved entirely to `factory/`; the orchestrator no longer invokes agents, so the `CLIAdapter` subprocess seam described below no longer lives here. See the repo-root `docs/spec/prd.md` and `docs/adr/0002-factory-owns-flow-control-orchestrator-is-a-trigger.md`.

## Context

Isolation (Q2, NFR-2, BR-004) is a top quality goal: a reviewer's judgement must be independent of the author's reasoning, exactly as a developer must not review their own pull request. The design proposal ([orchestrator-design-proposal.md](../../../scripts/orchestrator-design-proposal.md)) records the trigger — the existing `task` tool launches sub-agents *within the same session*, so it cannot provide the required blindness. Isolation must be a structural guarantee, not a matter of prompt discipline.

The question is *how* to run each agent so that no context leaks between an author and a reviewer.

### Alternatives (Pugh Matrix)

Baseline **A**: in-process sub-agents (the `task`-tool style) — the tempting automation. **B**: a fresh OS subprocess per invocation. **C**: a long-lived subprocess pooled/reused across invocations.

| Criterion                                      | Weight | A: in-process | B: fresh subprocess | C: pooled subprocess |
| ---------------------------------------------- | ------ | ------------- | ------------------- | -------------------- |
| Isolation — no inherited context (Q2)          | 3      | 0             | +1                  | 0                    |
| Determinism — clean-slate reproducibility (Q1) | 3      | 0             | +1                  | 0                    |
| Portability — works for any CLI binary (Q5)    | 2      | 0             | +1                  | +1                   |
| Bounded cost — process-spawn overhead (Q6)     | 2      | 0             | -1                  | 0                    |
| Simplicity (Q7)                                | 1      | 0             | 0                   | -1                   |
| **Weighted total**                             |        | **0**         | **+7**              | **+1**               |

B wins. In-process (A) structurally *cannot* provide isolation — the very reason the manual workflow uses fresh sessions. Pooling (C) reintroduces the leak risk it was meant to remove; the only thing it saves is process-spawn cost, which the per-invocation timeout already bounds.

## Decision

Every agent invocation runs in a **fresh OS subprocess** of the target CLI, spawned through the single `CLIAdapter.invoke(prompt, cwd, timeout_s) → InvocationResult` port. The core never spawns a process directly and never shares state between an author and a reviewer invocation. Concrete adapters own the CLI-specific non-interactive flags (T-01) and set `auth_error` so the core can distinguish an adapter failure (halt, BR-018) from an author failure (loop).

## Consequences

**Positive**

- Isolation is verifiable *structurally* — a process boundary — not by inspecting prompts (QS-04, VR-004).
- A hung CLI is killed at the timeout and treated as a failed iteration (QS-16, NFR-6); a crashed subprocess cannot corrupt the orchestrator's memory.
- The adapter seam keeps per-CLI headless-invocation differences out of the core (composes with [ADR-0001](0001-clean-architecture-ports-and-adapters.md)).

**Negative / risks**

- Process-spawn and prompt re-composition cost is paid on every iteration; acceptable given the cap and timeout bound total cost.
- Context that *should* carry forward (open findings on loop-back) must be re-injected explicitly by `PromptComposer` rather than persisting in a session — this is by design (isolation), but it puts the burden on prompt composition (risk R-4).

**Hardening (from the ATAM review)**

- A fresh *process* is necessary but not sufficient for isolation if the CLI silently auto-resumes its last session (ATAM-R11). Therefore each adapter must **force a clean session** — never pass a resume/continue flag (`--continue`, `--resume`) — and assert it in the adapter's tests (VR-021). The Copilot adapter's command construction is covered by such a test.
- Adapter failures now split three ways in `InvocationResult`: `auth_error` (BR-018), `config_error` (BR-020, added after a live spike looped a bad `--model` id to the cap), and a plain non-zero (author-fixable, loops). See [interface-contracts](../spec/supplementary_specs/interface-contracts.md).
