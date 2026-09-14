---
id: 0018
status: accepted
evaluation: none
---

# CONCEPT internal sequence is agent-owned

## Context

The cycle-based orchestration model ([ADR-0017](0017-cycle-based-orchestration-supersedes-linear-playbook-fsm.md)) defines five delivery cycles. The CONCEPT cycle produces specification artifacts: scope maps, consolidated Gherkin features, supplementary specs (entity model, interface contracts, state machines, validation rules), and a gaps report. These artifacts have a natural ordering -- the scope map precedes features, features precede supplementary specs -- but the ordering is methodological, not architectural.

Two approaches exist for managing the internal sequence within CONCEPT:

1. **Engine-modeled substates**: The delivery model declares CONCEPT substates (e.g., CONCEPT.SCOPE, CONCEPT.FEATURES, CONCEPT.SUPPLEMENTS) with routes between them. The Cycle Engine manages transitions within CONCEPT the same way it manages transitions between top-level cycles.
2. **Agent-owned ordering**: The engine sees CONCEPT as one cycle. The agent dispatched into CONCEPT (typically the requirements agent) manages its internal ordering through its own agent definition, skills, and playbook steps.

No formal alternative evaluation is needed because the design decision follows directly from two principles: YAGNI and the separation between engine concerns and agent concerns.

## Decision

The engine sees CONCEPT as one cycle. Agents manage their internal ordering.

The Cycle Engine does not model substates within any cycle. The delivery model declares CONCEPT with its artifact declarations and trusted validators. The agent dispatched into CONCEPT owns the sequencing of scope map, features, supplementary specs, and gaps report production. This sequencing is encoded in the agent definition and supporting skills, not in the delivery model.

## Consequences

**Positive**

- The delivery model remains simple: five cycles plus DONE, with no nested state machines or substate routing logic.
- The Cycle Engine needs no substate management, transition tracking, or nested lock acquisition.
- Agent definitions can evolve their internal methodology independently of the engine. A change to the requirements agent's workflow (e.g., reordering spec production) requires no model change.
- Other cycles benefit from the same principle: REALIZE does not need substates for coding, testing, and review; the implementation agent owns that sequence.

**Negative**

- The engine cannot enforce ordering within CONCEPT. An agent that produces artifacts in the wrong order will not be caught by the engine's readiness evaluation until the cycle boundary.
- Visibility into CONCEPT progress requires reading the agent's own state or output artifacts rather than querying the engine for the current substate.
