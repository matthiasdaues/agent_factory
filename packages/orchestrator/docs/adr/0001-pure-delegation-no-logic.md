---
id: "0001"
status: accepted
evaluation: none
---

# Orchestrator is pure delegation — no logic of its own

## Context

The orchestrator replaces you pressing "enter" between agent sessions. The question is how much intelligence it should carry.

Three layers already own every decision the orchestrator might need to make: `phase advance` owns gate evaluation and marker writes, `phase retry` owns iteration-cap enforcement, and `trigger` owns agent resolution, model selection, and prompt composition. These are deterministic, file-driven, and independently callable. ADR-0002 at the factory level established that the orchestrator is "a peer trigger, same standing as a human typing commands."

The temptation is to add value: parse CLI output to classify failures, enrich prompts with open findings on retry, select alternative models when agents fail, manage sessions across restarts. Each addition makes the orchestrator a second brain alongside the agents — one that holds opinions about how to recover, what context to inject, and when to deviate from the FSM's declared path.

## Decision

The orchestrator holds zero sequencing logic, zero gate evaluation, zero prompt composition, and zero failure-recovery intelligence. It is a while loop that calls three existing scripts in a fixed order and interprets only their exit codes:

- `phase advance --dry-run` → can we skip dispatch?
- `trigger agent <name> --background` → dispatch and wait
- `phase advance` → did the out-gate pass?
- `phase retry` → are we allowed to try again?

If any script refuses, the orchestrator stops. It does not override, retry with different parameters, or try to heal the situation. It reports and exits.

The orchestrator's own code path has exactly one branch per exit code (0, 1, 2) from each script. No heuristics, no pattern matching on output, no adaptive behavior.

## Consequences

**Positive**

- Trivial to understand: ~120 lines, no branching beyond exit-code dispatch. A reader can hold the entire control flow in working memory.
- Impossible to drift from the FSM: the orchestrator cannot advance a phase the gate doesn't allow, retry beyond the cap, or dispatch an agent the FSM doesn't name — because it delegates those decisions entirely.
- Testable with mocked scripts: replace `phase` and `trigger` with shell stubs that return fixed exit codes, and the orchestrator's entire behavior is deterministically exercisable.
- Crash recovery is free: the marker is the truth, the orchestrator holds no in-memory state that could be lost. Kill it at any point, re-run, same result.

**Negative / risks**

- No prompt enrichment on retry. When an agent is re-dispatched after a gate failure, it receives the same prompt as the first time. It must discover open findings by reading the filesystem. This works (agents are designed to do this) but is slower than injecting findings directly. Named gap — add it if latency matters in practice.
- No failure classification. A non-zero exit from `trigger` could mean auth failure, rate limit, network timeout, or genuine task failure. The orchestrator treats them all the same: check the gate, retry if allowed, halt if not. A smarter orchestrator could distinguish transient from permanent failures. YAGNI until it isn't.
- No multi-model fallback. If the configured model is unavailable, the orchestrator halts rather than trying a cheaper model. This is deliberate: model selection is a project decision (in `model.conf`), not a runtime optimization.
