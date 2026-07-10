# 0001. Clean Architecture with ports and adapters

**Status**: Accepted

## Context

The orchestrator must be CLI-agnostic (FR-C, Q5) — Copilot first, Claude and Gemini later — and it must be safe and testable (Q3, Q4). It also drives several concrete externalities: an AI CLI, git/pre-commit, and the filesystem (findings store, run state). The central logic — the phase state machine and loop policy — is the same regardless of which CLI, VCS, or storage sits underneath.

We need a decomposition that lets the central logic be written once and verified in isolation, while concrete CLIs, gates, and stores plug in without touching it. This is the Dependency Inversion Principle applied at the system boundary.

### Alternatives (Pugh Matrix)

Baseline **A**: a layered design where the core calls concrete externalities directly (imports `subprocess`, `git`, filesystem layout). **B**: Clean/hexagonal — the core depends only on abstract **ports**; concretions are **adapters** wired at a composition root. **C**: a single-module script with no layering (the design-proposal sketch).

| Criterion                                    | Weight | A: concrete layers | B: ports & adapters | C: single script |
| -------------------------------------------- | ------ | ------------------ | ------------------- | ---------------- |
| Portability — CLI-agnostic core (Q5)         | 2      | 0                  | +1                  | -1               |
| Testability of core in isolation (Q4)        | 2      | 0                  | +1                  | -1               |
| Dependency Inversion adherence (Clean/SOLID) | 3      | 0                  | +1                  | -1               |
| Extensibility — new CLI/gate/store (Q5)      | 2      | 0                  | +1                  | -1               |
| Simplicity — minimal indirection (Q7)        | 1      | 0                  | -1                  | +1               |
| **Weighted total**                           |        | **0**              | **+8**              | **-8**           |

B wins decisively. C's only edge (simplicity) is outweighed by every quality goal that the orchestrator exists to serve; the single-script proposal was an early sketch, not a target.

## Decision

Adopt **Clean Architecture** with an explicit ports-and-adapters seam:

- **Core** (`PhaseRunner`, `LoopPolicy`, `StatusService`, `ApprovalService`, `ModelResolver`, domain entities) depends **only** on ports.
- **Ports** are abstract interfaces (`CLIAdapter`, `GateRunner`, `FindingsStore`, `RunStateStore`, `RunLock`, `AgentRegistry`, `PromptComposer`, `Clock`), expressed as `typing.Protocol`/ABC.
- **Adapters** implement ports and hold all knowledge of concrete CLIs, git, and the filesystem.
- The **CLI entry point** is the composition root: it constructs adapters and injects them into the core.

The dependency rule points strictly inward: **CLI → Core → Ports ← Adapters**. No core module may import an adapter or a concrete CLI/VCS/filesystem type.

## Consequences

**Positive**

- The phase state machine and loop policy are written and unit-tested once, with fake ports — no CLI, git, or disk needed (QS-14, Q4).
- A new target CLI is a new `CLIAdapter`; a new deterministic check is a new hook behind `GateRunner`; neither touches the core (QS-14, QS-15).
- The seam is exactly where the interface contracts ([interface-contracts.md](../spec/supplementary_specs/interface-contracts.md)) already draw it, so the spec and the code agree.

**Negative / risks**

- More indirection and boilerplate than a flat script — justified by the portability and testability goals, but a real cost for a small tool.
- Discipline is required to keep adapter types from leaking across the seam (e.g. `InvocationResult` must not expose CLI-specific fields). Enforced by review.
