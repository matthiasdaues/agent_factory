---
schema_version: 2
title: Cycle-Based Orchestration
status: draft
owner: Matthias Daues
created: 2026-09-13
updated: 2026-09-13
supersedes:

impact:
  scope: cross_component
  architecture_change: true
  external_contract_change: true
  boundaries:
    - packages/factory/playbooks
    - packages/factory/agents
    - packages/factory/skills/run-step
    - packages/factory/scripts/phase
    - packages/factory/scripts/transition-lint
    - packages/factory/config/session-menu.md
    - packages/factory/engine/flow_control
    - docs/arc42/architecture.dsl
    - docs/arc42/05_building_block_view.md
    - docs/arc42/06_runtime_view.md
    - docs/arc42/08_crosscutting_concepts.md

governance:
  assurance: high
  risk_domains:
    - compatibility
    - reliability
    - operations

estimate:
  as_of: 2026-09-13
  basis: analogous
  confidence: low
  human_review_hours: unknown
  normalized_tokens: unknown
  estimated_consumption: unknown
---

# Feature Request: Cycle-Based Orchestration

## Summary

Replace the linear playbook model with a cycle-based directed graph. Artifact
state drives transition recommendations. Humans drive routing decisions. The
system suggests what comes next; the human approves, redirects, or delegates.
Reconciliation dissolves from a standalone phase into a standard exit-gate check
on every cycle.

The factory keeps every agent, skill, and deterministic gate it has today. What
changes is how they are sequenced: not by a named playbook's prescribed steps,
but by the artifacts that exist and the artifacts that are needed.

## Motivation

The current playbook model is process-centered. It asks "which process are you
running?" and the human serves the process. A user who wants to add a feature
must first identify that their work is a "feature-addition," then accept a
nine-agent pipeline regardless of whether the change is a config flag or a new
subsystem.

This creates two problems:

1. **Too narrow.** The user must categorize their work before starting.
   Real work does not sort cleanly into fixed types. A bug fix becomes a
   refactoring. A feature addition turns out to need architectural rework. The
   playbook chosen at the start no longer fits, but the user is in it.

2. **Too far-reaching.** Each playbook prescribes full ceremony. There is no
   proportionality between the size of the work and the amount of process. A
   small, well-understood change receives the same pipeline as a
   system-level feature.

The ideation path (Phase 0 through accepted proposal) works well because it
follows the user's thinking: a vague idea sharpens through conversation, and a
proposal crystallizes when it is ready. No upfront commitment to a named process
is required. The break happens after the proposal is accepted, when the user must
pick a playbook and the playbook takes over.

The cycle model removes that break. The unit of work remains the proposal. The
factory's job is to deliver it proportionally.

## Core Principles

- The human drives. The system recommends the next cycle; the human approves
  or redirects.
- Artifact state is the routing signal. "What do you have, what do you need?"
  replaces "which playbook are you running?"
- Cycles are reentrant. Any cycle can discover that an upstream artifact is
  invalid and route back to the cycle that owns it.
- Reconciliation is not a phase. It is a standard exit-gate check built into
  every cycle transition.
- Proportionality emerges from the graph. A small change traverses fewer
  cycles and exits earlier. A large change traverses more. The system
  recommends a route from artifact state. The human decides.
- The canonical concept model consists of `docs/spec/scope-map.md`,
  `docs/spec/entity-model.md`, and `docs/arc42/architecture.dsl`. Their
  existence is non-negotiable. Their content is revisable. Every cycle
  checks whether implementation evidence requires them to be adapted,
  reconciled, or redesigned. Proposals are origins. Feature files, ADRs,
  and backlog files are elaborations or derived artifacts. When artifacts
  disagree, the canonical model is authoritative.

## Design

### User model and engine model

The user sees three stages. The engine operates five cycles. The five cycles
are the engine's internal model; the three stages are the user-facing model.

```text
USER MODEL

IDEATION  <->  CONCEPTUALIZATION  <->  REALIZATION


ENGINE MODEL

IDEA  <->  CONCEPT  <->  [ ROADMAP ]  <->  [ REFINE ]  <->  REALIZE
                              optional              repeat by batch
```

ROADMAP and REFINE are internal to the realization stage. The user thinks
"I need to build this"; the engine determines whether epic decomposition
and story refinement are needed or whether the concept is concrete enough
to build directly.

### The five cycles

Each cycle transforms input artifacts into output artifacts. The agents and
skills assigned to a cycle are the same ones the factory uses today; only their
sequencing changes.

#### 1. IDEA

Transform a vague idea into a decision-complete proposal.

- **In:** nothing (a stated intention)
- **Out:** `docs/proposals/<name>.md` at status `accepted`
- **Agents/skills:** virgil, grilling, draft-proposal, domain-modeling
- **Gate:** proposal exists, passes template lint, status = accepted
- **Human gate:** always. Acceptance is a human decision.
- **Review postures:** the proposal's status determines the review stance.
  A `draft` proposal receives consultative review (help it improve). An
  `open` proposal receives adversarial review (try to break it). Only
  stakeholder approval moves a proposal to `accepted`. These postures are
  not interchangeable iterations.

#### 2. CONCEPT

Give the proposal its technical shape. Produce the canonical concept model.

- **In:** accepted proposal
- **Out — canonical concept model:**
  - `docs/spec/scope-map.md` — what it does
  - `docs/spec/entity-model.md` — what things mean (domain entities,
    their relationships, and their invariants; distinct from the domain
    vocabulary in `docs/CONTEXT.md`, which names and defines terms)
  - `docs/arc42/architecture.dsl` — how it is shaped
- **Out — elaborations:**
  - `docs/spec/*.feature` — behavioral contracts derived from scope-map
  - `docs/adr/*.md` — decisions crystallized during concept work
- **Agents/skills:** requirements-agent, architecture-agent, derive-feature,
  capture-context, domain-modeling
- **Gate:** all three canonical artifacts exist, pass lint, review findings
  resolved
- **Reviews:** spec-review-agent, architecture-review-agent (internal to the
  cycle; findings loop back within CONCEPT until resolved)

CONCEPT has an internal sequence. The transformations within it are not
interchangeable:

```text
accepted proposal
        |
        v
scope-map + use cases + gaps report
        |
   specification review
        |
        v
entity-model + architecture.dsl
        |
   architecture review
        |
        v
reviewed concept model
```

The internal sequence is not a separate set of cycles. It is the working
order within CONCEPT. Reviews loop back within this sequence until findings
are resolved, then CONCEPT exits with the complete canonical model.

#### 3. ROADMAP

Decompose concept artifacts into an epic sequence.

- **In:** concept artifacts (architecture, scope-map, features, domain model)
- **Out:** `backlog/epics.md` with sequenced epics and testability assessments
- **Agents/skills:** planning-agent (create-backlog-epics, write-epics,
  testability-probe)
- **Gate:** epics.md exists, each epic has testability assessment, no
  unresolvable ownership gaps

#### 4. REFINE

Break epics into implementation-ready stories for the next batch.

- **In:** `backlog/epics.md` + concept artifacts
- **Out:** `backlog/ST-NNNN.md` stories with slices for the next batch
- **Agents/skills:** planning-agent (create-backlog-stories, grilling,
  make-concrete, slice-story)
- **Gate:** batch stories exist, pass frontmatter validation, dependencies
  declared, contract questions resolved
- **Human gate:** always. Story shaping and contract decisions require human
  judgment.

#### 5. REALIZE

Build the batch.

- **In:** one or more implementation units (see below)
- **Out:** merged code + tests on the target branch
- **Agents/skills:** implementation-agent, developer-agent, code-review-agent,
  qa-agent (risk-selected)
- **Gate:** all implementation units delivered, premerge-check passed,
  tests green, reconciliation exit-gate check passed

An **implementation unit** is the common input contract that makes all
forward edges into REALIZE executable. It is a machine-readable artifact
stored at `.current-work/<branch>/units/<id>.yaml`. It carries:

- **id:** unique identifier (e.g. `IU-0001`, or the story ID when derived
  from a story)
- **source:** `proposal | epic | story` (identifies the originating cycle)
- **source_ref:** path to the originating artifact
- **concept_version:** commit SHA of the canonical concept model at the time
  the unit was created (links implementation evidence to a specific model
  version for reconciliation)
- **required_behavior:** what the unit must do
- **affected_boundaries:** which files and interfaces change
- **acceptance_conditions:** how to verify correctness
- **test_ownership:** which layer owns the acceptance evidence

**Creation:** the cycle that transitions into REALIZE creates the
implementation units. When REFINE produces stories, each story maps to an
implementation unit. When CONCEPT or ROADMAP skips directly to REALIZE, the
transitioning cycle (or the human, assisted by the system) creates
implementation units from the proposal or epics. The transition recommender
verifies that at least one valid implementation unit exists before
recommending a forward edge to REALIZE.

**Validation:** a schema check runs on each unit file before REALIZE
accepts it. Missing required fields block entry into REALIZE.

**Completion:** REALIZE reaches DONE when all implementation units are
delivered and their acceptance conditions pass.

REALIZE has an internal sequence. Not every step runs on every unit;
risk selection determines depth:

```text
implementation
      |
code review
      |
tests and deterministic gates
      |
risk-based QA (security review, bug hunt — when warranted)
      |
reconciliation exit-gate check
```

### Forward edges

Not every cycle can reach every downstream cycle. The valid forward transitions
and their conditions:

| From    | To      | Condition                                                      |
| ------- | ------- | -------------------------------------------------------------- |
| IDEA    | CONCEPT | always (the only forward edge from IDEA)                       |
| CONCEPT | ROADMAP | normal path                                                    |
| CONCEPT | REFINE  | scope small enough that epic decomposition adds nothing        |
| CONCEPT | REALIZE | change is fully shaped and implementation-ready                |
| ROADMAP | REFINE  | normal path                                                    |
| ROADMAP | REALIZE | epics are small enough to build without story refinement       |
| REFINE  | REALIZE | always (the only forward edge from REFINE)                     |
| REALIZE | DONE    | all implementation units delivered, acceptance conditions pass |

IDEA has exactly one forward edge. DONE is reachable only from REALIZE. CONCEPT
and ROADMAP both have forward skip options, determined by scope and artifact
completeness. CONCEPT-to-REALIZE skips both human-gate cycles (ROADMAP and
REFINE), which is safe only when the concept already contains
implementation-ready detail. ROADMAP-to-REALIZE skips REFINE, which is safe when
the epics are small and concrete enough to build directly without story-level
decomposition.

### Back edges

Any cycle can route back to any upstream cycle. The target is determined by
which artifact turned out to be wrong, not by sequence position.

| From    | Can route back to              |
| ------- | ------------------------------ |
| CONCEPT | IDEA                           |
| ROADMAP | IDEA, CONCEPT                  |
| REFINE  | IDEA, CONCEPT, ROADMAP         |
| REALIZE | IDEA, CONCEPT, ROADMAP, REFINE |

Back edges are triggered by artifact invalidation, detected at exit gates. When
a cycle's exit-gate check discovers that an upstream artifact no longer holds,
the system recommends routing back to the cycle that owns the broken artifact.
The human confirms or overrides the routing decision.

This is what reconciliation becomes: a standard back-edge evaluation at every
exit gate, not a separate phase at the end of a pipeline.

### Human gates and delegation

Two cycles always require human input:

- **IDEA** — divergent-to-convergent thinking with the stakeholder present.
  Proposal acceptance is a human decision.
- **REFINE** — contract decisions and story shaping require human judgment.

The remaining cycles (CONCEPT, ROADMAP, REALIZE) can run autonomously when
the human delegates. Delegation is explicit and per-transition:

- **Default:** the system presents the recommended next cycle with rationale.
  The human approves, redirects, or modifies scope.
- **Delegation grant:** the human says "run through to REALIZE without
  stopping" and the system chains autonomous cycles, stopping at:
  a human-gate cycle, a reconciliation trigger, an unresolved finding,
  or a fork where more than one mechanically valid forward edge exists
  (choosing between them requires semantic judgment that the first release
  defers to the human).

### Transition recommender

At every cycle exit, the system:

1. Runs the mechanical exit gate (artifacts exist, pass validation).
2. Runs the reconciliation check (are upstream artifacts still valid?).
3. Evaluates which forward edge conditions are met.
4. Presents the recommendation: continue forward (to which cycle), stop for
   human input, or route back (to which cycle, naming the broken artifact).

The human makes the final routing decision. The recommender's quality
determines usability, but the human retains authority.

### Artifact state detection

The system must be able to read the repository and determine which artifacts
exist and whether they satisfy a cycle's input requirements. This requires
two layers:

- **Mechanical validation:** file exists, passes format lint, required fields
  present. Scriptable and deterministic.
- **Semantic assessment:** "Does the code contradict the scope-map?" "Has
  an architecture boundary been disproved by implementation?" Requires
  LLM-based comparison of artifacts against each other or against code.

These two layers serve different purposes:

- **Forward-edge routing** (which cycle comes next, whether to skip): the
  first release uses mechanical validation to identify which forward edges
  are structurally possible and presents them to the human, who decides.
  Automated semantic forward-skip recommendations are deferred.
- **Back-edge routing** (whether an upstream artifact is invalidated): the
  first release uses the existing reconciliation-agent to perform semantic
  code-to-model comparison as part of the exit-gate check. This is not
  new capability; it is the reconciliation agent's current responsibility,
  relocated from a standalone phase into the exit gate. Back edges are
  therefore semantically informed from the first release. The system
  presents detected invalidations and recommends a target cycle; the human
  confirms the routing.

The boundary between mechanical and semantic checks is defined per artifact
type. Mechanical checks run unconditionally. Semantic comparison via the
reconciliation agent runs at exit gates when the cycle produced or modified
code or canonical-model artifacts.

## Scope

### In scope

- Define the five cycle types with their input artifacts, output artifacts,
  eligible agents and skills, and exit gates.
- Define the forward-edge and back-edge transition tables.
- Define the reconciliation exit-gate check as a standard cycle behavior.
- Define the transition recommender's interface and recommendation format.
- Define the human-gate and delegation-grant interaction model.
- Define per-artifact mechanical readiness criteria.
- Replace the session menu's playbook-selection paths with cycle-aware
  artifact-state suggestions.
- Remove `phase:` ordinal metadata from agent definitions; replace with
  cycle eligibility tags.
- Migrate `run-step` from playbook-step execution to cycle-step execution.

### Explicitly deferred

- Automated semantic forward-skip recommendations. The first release uses
  mechanical validation to identify structurally possible forward edges and
  presents them to the human, who decides whether to skip. Automated
  assessment of whether skipping is appropriate is a later capability.
  Back-edge semantic detection is not deferred; it uses the existing
  reconciliation-agent capability from the first release.
- Modifying the deterministic factory engine's flow-control model. The
  existing FSM-based engine serves playbooks; cycle-based flow control is a
  separate evolution that depends on this proposal's acceptance.
- Removing playbook files. Playbooks remain as reference documentation for
  known-good sequences. They lose their role as the orchestration mechanism
  but are not deleted.
- Automated delegation without human presence. The default is human-driven;
  autonomous chaining is an opt-in extension.
- Batch identity tracking across refinement-realization-reconciliation loops.
  Required for multi-batch delivery but not for single-batch operation.
  Multi-batch identity is necessary before the proposal can deliver its
  complete learning-loop model; without it, reconciliation cannot trace
  which concept version shaped which implementation batch. This deferral
  is acceptable for the first release but must follow promptly.

## Open Questions

1. **Mechanical readiness criteria per artifact type.** Forward-edge
   routing in the first release depends on mechanical validation: file
   exists, passes lint, required fields present. The per-artifact
   checklist must be defined for each canonical and derived artifact type.
   Back-edge semantic detection uses the existing reconciliation-agent
   and is not blocked by this question.

2. **Relationship to deterministic-factory-engine.** The engine proposal
   extracts flow control based on linear playbook FSMs. Under the cycle model,
   the FSM shape changes: states are cycles, not playbook phases; transitions
   are artifact-driven, not sequence-driven. The engine's model, codec, and
   service interfaces may need redesign. Should this proposal supersede or
   amend the engine proposal?

3. **Brownfield entry.** The current brownfield-onboarding playbook enters
   at a different point than greenfield. Under cycles, a brownfield project
   would enter at CONCEPT with existing code as additional input. The cycle
   definitions may need a "brownfield variant" for CONCEPT that includes
   reverse-engineering steps, or brownfield entry may be a separate concern.

4. **Research and review playbooks.** The research-topic and research-survey
   playbooks do not map cleanly onto the five development cycles. They may
   need their own cycle graph, or they may remain as standalone workflows
   outside the cycle model.

## Completion Criteria

- The five cycle types are defined with input artifacts, output artifacts,
  agents/skills, and exit gates in a machine-readable format.
- The forward-edge and back-edge transition tables are defined and enforced.
- The session menu presents artifact-state-aware suggestions instead of
  playbook selections.
- Agent definitions carry cycle eligibility tags instead of phase ordinals.
- `run-step` executes cycle steps, not playbook steps.
- The reconciliation exit-gate check runs at every cycle transition.
- The transition recommender presents a recommendation with rationale at
  every cycle exit.
- Human-gate cycles (IDEA, REFINE) always stop for human input.
- Delegation grants allow chaining of autonomous cycles with automatic
  stop on human-gate cycles and reconciliation triggers.
- Existing agents, skills, and deterministic gates preserve their
  responsibilities and outputs. Internal logic may change where cycle
  eligibility replaces phase metadata, where REALIZE receives
  implementation units instead of stories only, or where quality
  responsibilities move into REALIZE's internal sequence.
- A single-batch delivery (IDEA through REALIZE to DONE) completes
  successfully under the cycle model.
