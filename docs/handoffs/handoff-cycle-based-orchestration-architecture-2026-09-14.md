# Handoff: Cycle-Based Orchestration Architecture Documentation

**Date**: 2026-09-14
**From**: Architecture Agent
**To**: Architecture Review Agent

## Summary

Architecture documentation and C4 model updates completed for the accepted
cycle-based orchestration proposal. The Structurizr DSL single source of truth
has been rewritten, arc42 prose chapters derived from it, and ADRs written for
the key decisions.

## Completed Deliverables

### Structurizr DSL (`docs/arc42/architecture.dsl`)

- Workspace renamed from "Factory Flow Control" to "Agent Factory"
- Added Cycle Engine container with 7 components: Cycle Model Loader, Readiness
  Evaluator, Route Recommender, Delegation Evaluator, Retry Evaluator,
  Workstream Resolver, Dispatch Eligibility
- Renamed State Manager to State Adapter with components: cycle select, cycle
  retry, phase stub, run-step skill
- Added 4 storage containers: Delivery Model, Cycle Schemas, Cycle State Files,
  Session Bindings
- Updated all relationships to reflect cycle commands replacing phase commands
- Added views: CycleEngineComponents, StateAdapterComponents, CycleTransition
  (dynamic)
- Removed TestGatePresence dynamic view (replaced by CycleTransition)
- Updated deployment to include all containers
- Validated and exported 10 SVG views

### Arc42 Prose Chapters

- **Chapter 05** (Building Block View): New Cycle Engine and State Adapter
  component sections; updated container table, validator descriptions,
  interfaces summary, and usage capture section
- **Chapter 06** (Runtime View): New cycle transition sequence (sections 6.2.1
  and 6.2.2); updated test gate presence to reference cycle gates; updated
  module-graph check references
- **Chapter 07** (Deployment View): Updated for cycle orchestration containers
  and state file locations
- **Chapter 08** (Cross-cutting Concepts): Updated validation tables for cycle
  gates; new section 8.13 on cycle-based orchestration model (declarative
  delivery model, artifact-driven routing, delegation and retry, workstream
  concurrency)
- **Chapter 09** (Architecture Decisions): Added ADR-0016, ADR-0017, ADR-0018
  to the decision index; added cycle-based orchestration key decisions section
- **Chapter 12** (Glossary): Added 14 cycle orchestration terms; marked legacy
  FSM terms with "(Legacy)" prefix
- **CONTEXT-MAP.md**: Updated Factory context description to include Cycle
  Engine and State Adapter

### ADRs

- **ADR-0017**: Cycle-based orchestration supersedes linear playbook FSM
  (evaluation: pugh-matrix, status: proposed)
- **ADR-0018**: CONCEPT internal sequence is agent-owned (evaluation: none,
  status: proposed)

## Input Artifacts Referenced

- `docs/proposals/cycle-based-orchestration.md` (accepted proposal)
- `docs/spec/supplementary_specs/interface-contracts.md` (cycle command
  contracts)
- `docs/spec/supplementary_specs/entity-model.md` (cycle orchestration
  entities)
- `docs/spec/supplementary_specs/state-machines.md` (workstream lifecycle,
  delegation execution, retry state)
- `docs/spec/supplementary_specs/validation-rules.md` (cycle model, state,
  session binding, workstream mutation, retry validation)

## Design Decisions Recorded

1. CONCEPT internal sequence is agent-owned, not engine-modeled. The engine
   sees CONCEPT as one cycle. Agents manage their internal ordering.
2. Cycle Engine is a pure domain-logic container with inward-only dependencies
   (Clean Architecture). It never writes state.
3. State Adapter acquires OS-level exclusive locks for concurrent workstream
   safety.

## Next Action

Start a new session and run `architecture-review-agent` against `docs/`.

## Suggested Skills

- `validate` -- run `structurizr validate` and `arch-lint` as part of review
- `adversarial-review` -- adversarial review of the ADRs
