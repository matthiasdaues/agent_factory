---
schema_version: 2
title: Cycle-Based Orchestration
status: open
owner: Matthias Daues
created: 2026-09-13
updated: 2026-09-14
supersedes: docs/proposals/deterministic-factory-engine.md

impact:
  scope: cross_component
  architecture_change: true
  external_contract_change: true
  boundaries:
    - packages/factory/playbooks
    - packages/factory/playbooks/brownfield-onboarding.md
    - packages/factory/playbooks/research-survey.md
    - packages/factory/playbooks/research-topic.md
    - packages/factory/agents
    - packages/factory/skills/run-step
    - packages/factory/scripts/phase
    - packages/factory/scripts/transition-lint
    - packages/factory/config/session-menu.md
    - packages/factory/rulebooks/schemas/research-brief.schema.json
    - packages/factory/rulebooks/templates/research-brief.md
    - docs/proposals/deterministic-factory-engine.md
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

Replace the linear software-delivery playbook model with a cycle-based directed
graph. Artifact state drives transition recommendations. Humans drive routing
decisions. The system suggests what comes next. The human approves, redirects,
or delegates. Reconciliation becomes a standard exit-gate check.

The factory keeps every agent, skill, and deterministic gate it has today. The
delivery graph sequences them from available and required artifacts. Research
uses a sibling graph with its existing survey and falsification routes. A typed
handoff connects delivery questions to research evidence.

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

The cycle model removes that break. A delivery unit remains proposal-backed.
Brownfield bootstrap is the one repository-entry exception. The factory's job
is to establish the baseline, then deliver each proposal proportionally.

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
- Fitting configures the factory for a repository. Fitting is a prerequisite,
  not a delivery cycle.
- Brownfield entry reconstructs the canonical concept model from code, tests,
  persistence schemas, and infrastructure-as-code. Delivery cannot begin until
  all three canonical concept artifacts pass their gates.
- Research uses a sibling cycle graph. Research may return evidence to a
  delivery cycle or finish with a validated report.

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

### Repository entry modes

Fitting runs before the delivery graph. It configures the model matrix, project
fingerprint, agent context, test regime, and hooks. Fitting does not describe
the system's behavior or architecture.

A greenfield repository enters IDEA after fitting. A brownfield repository
enters a mandatory CONCEPT bootstrap after fitting. Existing code, tests,
persistence schemas, and infrastructure-as-code are evidence for this
bootstrap. An accepted feature proposal is not required for the bootstrap.

The brownfield CONCEPT bootstrap produces these canonical concept objects:

- `docs/arc42/architecture.dsl` — system structure, dependencies, runtime, and
  deployment
- `docs/spec/scope-map.md` — implemented behavior with evidence references
- `docs/spec/entity-model.md` — entities, relationships, and invariants

The entity model is the canonical Entity Relationship Diagram (ERD) artifact.
The project-wide path remains subject to the deferred harmonization recorded in
[T-0006](../spec/todo.md#t-0006--harmonize-the-canonical-erd-location-across-scenarios).

The bootstrap exit gate requires all three objects to exist, pass deterministic
validation, and have no unresolved blocking review findings. The brownfield
onboarding procedure must produce all three during its mandatory first stage.
Its deeper reverse-engineering stage remains optional.

The bootstrap exits to a delivery-ready repository state. It does not create a
ROADMAP or enter REALIZE. New changes then begin at IDEA with a proposal.

### Sibling research graph

Research is not a sixth delivery cycle. It uses a sibling graph with the
existing survey and falsification routes. Research can start as the user's
primary goal or from an evidence gap in a delivery cycle.

A delivery-to-research handoff uses the existing research brief. A brief opened
from delivery also records these fields:

- **origin_cycle:** `IDEA | CONCEPT | ROADMAP | REFINE | REALIZE`
- **origin_ref:** the repository path of the artifact that needs evidence
- **return_cycle:** the delivery cycle that will consume the result
- **decision_needed:** the decision that the research result must inform

Standalone research omits these delivery-link fields. A validated survey or
falsification report completes standalone research. Linked research returns the
report reference to `return_cycle`. The delivery graph then resumes there.

The first release defines and validates this handoff. It keeps the internal
research routes and their role-separation rules unchanged.

### Cycle-native deterministic engine

This proposal supersedes the
[Deterministic Factory Engine proposal](deterministic-factory-engine.md). The
factory will not extract the linear playbook model into a reusable engine before
implementing cycle orchestration. That extraction would make a model with poor
user experience harder to remove.

The cycle-native engine retains these constraints from the superseded proposal:

- Tracked Factory source is the default test surface.
- Scripts are thin command adapters around one engine implementation.
- The engine returns immutable decisions and does not write repository state.
- Adapters own marker writes, process lifecycle, and runtime protocols.
- Installed-shape tests verify that the distributed Factory contains and can
  execute the engine.
- A deterministic boundary test enforces the dependency direction from scripts
  to the engine.

The cycle proposal replaces these linear contracts as one change:

- Playbook `.fsm.yml` files stop being the authority for software-delivery
  routing.
- `.current-work/playbook-state.yml` is replaced by a cycle-state marker.
- The engine model represents cycles, artifact readiness, valid edges, human
  gates, back-edge recommendations, and retry limits.
- `run-step`, `phase`, and `transition-lint` consume the same cycle-native
  decision model. None retains a private parser or transition implementation.

The existing commands remain operational until the cycle-native replacements
pass their characterization and installed-shape tests. The cutover does not
create an intermediate engine that treats linear playbook phases as its domain
model.

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

- **In — delivery:** accepted proposal
- **In — brownfield bootstrap:** fitted repository with existing code, tests,
  persistence schemas, and infrastructure-as-code
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
  reverse-map, capture-context, domain-modeling
- **Gate:** all three canonical artifacts exist, pass lint, review findings
  resolved
- **Reviews:** spec-review-agent, architecture-review-agent (internal to the
  cycle; findings loop back within CONCEPT until resolved)

CONCEPT delivery has an internal sequence. The transformations within it are
not interchangeable:

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

The delivery sequence is not a separate set of cycles. It is the working order
within CONCEPT. Brownfield bootstrap follows the repository-entry sequence
above. Reviews loop within either sequence until findings are resolved.
CONCEPT then exits with the complete canonical model.

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
- Define fitting as a prerequisite outside the delivery graph.
- Define mandatory brownfield entry through a CONCEPT bootstrap that produces
  all three canonical concept objects.
- Make the Entity Relationship Diagram (ERD) part of the mandatory first stage
  of brownfield onboarding.
- Define and validate the delivery-to-research brief fields. Keep the existing
  survey and falsification routes unchanged.
- Create one cycle-native deterministic flow-control engine. Retain the thin
  adapter, immutable decision, tracked-source, installed-shape, and dependency
  boundary constraints from the superseded engine proposal.
- Replace playbook FSM authority and the playbook-state marker with cycle-native
  graph and state contracts.
- Replace the session menu's playbook-selection paths with cycle-aware
  artifact-state suggestions.
- Remove `phase:` ordinal metadata from agent definitions; replace with
  cycle eligibility tags.
- Migrate `run-step`, `phase`, and `transition-lint` together to the
  cycle-native engine.

### Explicitly deferred

- Automated semantic forward-skip recommendations. The first release uses
  mechanical validation to identify structurally possible forward edges and
  presents them to the human, who decides whether to skip. Automated
  assessment of whether skipping is appropriate is a later capability.
  Back-edge semantic detection is not deferred; it uses the existing
  reconciliation-agent capability from the first release.
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
- Replacing the internal survey and falsification routes with a new research
  orchestration engine. Research keeps its current routes in the first release.

## Open Questions

1. **Mechanical readiness criteria per artifact type.** Forward-edge
   routing in the first release depends on mechanical validation: file
   exists, passes lint, required fields present. The per-artifact
   checklist must be defined for each canonical and derived artifact type.
   Back-edge semantic detection uses the existing reconciliation-agent
   and is not blocked by this question.

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
- A fitted brownfield repository cannot enter feature delivery until
  `architecture.dsl`, the scope map, and the Entity Relationship Diagram (ERD)
  pass the CONCEPT bootstrap exit gate.
- Brownfield onboarding produces all three canonical concept objects in its
  mandatory first stage. Its optional second stage is not a delivery
  prerequisite.
- A delivery cycle can create a schema-valid linked research brief. A validated
  research report returns to the brief's declared `return_cycle`.
- Standalone survey and falsification runs complete through their existing
  routes without entering the delivery graph.
- The deterministic-engine proposal has status `superseded`. No implementation
  story extracts the linear playbook model into the engine.
- One cycle-native engine implementation owns artifact readiness, transition,
  human-gate, back-edge, and retry-limit decisions.
- `run-step`, `phase`, and `transition-lint` consume that engine. No delivery
  transition reads a playbook FSM as its authority after cutover.
- Installed-shape and dependency-boundary tests enforce the retained engine
  constraints.

## Review — 2026-09-13

Reviewer: proposal-review-agent
Reviewed commit: 29a1cf2d7404d172b4a3a7bb3e04f72ed2e858c2
Disposition: findings

### Findings

| ID      | Severity | Check | Status           | Finding                                                                                                                                                                                                                                                                                                                                                                                                                                                                                  |
| ------- | -------- | ----- | ---------------- | ---------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| PROP-01 | major    | 01    | open (unchanged) | Completion criterion 10 ("Existing agents, skills, and deterministic gates preserve their responsibilities and outputs") is not testable. It is an open-ended backward compatibility guarantee with no enumerable set of behaviors to verify. A planning agent cannot write a story for it because it cannot determine when the story is done.                                                                                                                                           |
| PROP-02 | major    | 01    | open (unchanged) | Completion criteria 1, 2, and 6 use undefined verification terms. "Machine-readable format" (criterion 1) does not name the format. "Enforced" (criterion 2) does not name the enforcement mechanism. "Runs at every cycle transition" (criterion 6) does not specify how coverage is confirmed.                                                                                                                                                                                         |
| PROP-03 | major    | 02    | open (unchanged) | "Define per-artifact mechanical readiness criteria" is simultaneously in scope and listed as Open Question 1. A scope item that is also an open question cannot be mechanically decided in or out. Resolve the question or move the item to deferred.                                                                                                                                                                                                                                    |
| PROP-04 | major    | 02    | open (unchanged) | The deferral of "modifying the deterministic factory engine's flow-control model" conflicts with the in-scope item "Migrate `run-step` from playbook-step execution to cycle-step execution." `run-step` currently depends on `playbook-state.yml`, FSM states, and `factory/scripts/phase` — all engine flow-control artifacts. Migrating `run-step` without modifying the engine's flow-control model is not obviously possible. State which engine artifacts change and which do not. |
| PROP-05 | minor    | 02    | open (unchanged) | The boundary between the in-scope "delegation-grant interaction model" and the deferred "automated delegation without human presence" is unclear. The in-scope Design section says "the system chains autonomous cycles," which reads as the deferred automation. Clarify where definition ends and automation begins.                                                                                                                                                                   |
| PROP-06 | major    | 05    | open (unchanged) | Boundary reference `packages/factory/engine/flow_control` does not exist at the reviewed commit. The entire `packages/factory/engine/` directory is absent from the dev tree. The proposal claims to affect something that cannot be inspected. Remove the reference or point to the actual path.                                                                                                                                                                                        |
| PROP-07 | minor    | 08    | open (unchanged) | Estimate field `basis: analogous` does not match the template schema value `analogous_change`, and no analogous prior change is identified. If no comparable change exists, the basis should be `judgment`, not `analogous`.                                                                                                                                                                                                                                                             |
| PROP-08 | minor    | 07    | open (unchanged) | The motivation identifies structural limitations but does not state "why now." What has changed that makes this the time to restructure orchestration rather than continue with the working playbook model?                                                                                                                                                                                                                                                                              |

### Summary

Checks 04 (impact classification), 06 (open questions genuine), and 03 (design decomposable) pass. The design is detailed enough to plan from. Five major findings block planning readiness: two completion criteria are untestable (PROP-01, PROP-02), two scope boundary conflicts prevent mechanical in/out decisions (PROP-03, PROP-04), and one boundary reference points to a path that does not exist (PROP-06). Address the five major findings before the proposal can move to planning.

## Review — 2026-09-14

Reviewer: proposal-review-agent
Reviewed commit: 5fec3e3f9c26b8a0284320ec47df3993ca293a06
Disposition: findings

### Findings

| ID      | Severity | Check | Status | Finding                                                                                                                                               |
| ------- | -------- | ----- | ------ | ----------------------------------------------------------------------------------------------------------------------------------------------------- |
| PROP-01 | major    | 01    | open   | Criterion 10 still lacks an enumerable compatibility baseline. The criterion cannot be verified without author interpretation.                        |
| PROP-02 | major    | 01    | open   | Criteria 1, 2, and 6 still omit the format, enforcement mechanism, and transition coverage matrix needed to derive tests.                             |
| PROP-03 | major    | 02    | open   | Per-artifact readiness criteria remain both in scope and unresolved in Open Question 1.                                                               |
| PROP-04 | major    | 02    | open   | The proposal still defers engine flow-control changes while requiring `run-step` to replace its engine-backed execution model.                        |
| PROP-05 | minor    | 02    | open   | The proposal still includes autonomous chaining but defers automated delegation without human presence. The boundary remains unclear.                 |
| PROP-06 | major    | 05    | open   | Boundary `packages/factory/engine/flow_control` does not exist at the reviewed commit.                                                                |
| PROP-07 | minor    | 08    | open   | `basis: analogous` remains outside the template schema. The proposal still identifies no analogous change.                                            |
| PROP-08 | minor    | 07    | open   | The Motivation still describes structural limits but gives no event or constraint that explains why work should start now.                            |
| PROP-09 | major    | 02    | open   | The Summary replaces playbook orchestration, but brownfield and research routing remain undecided. Their migration cannot be classified as in or out. |
| PROP-10 | major    | 01    | open   | Criterion 6 requires reconciliation at every transition. Design limits semantic reconciliation to exits after code or canonical-model changes.        |

### Checks

| Check | Result | Evaluation                                                                                                                 |
| ----- | ------ | -------------------------------------------------------------------------------------------------------------------------- |
| 01    | FAIL   | Criteria 1, 2, 6, and 10 lack one testable contract. Criterion 6 also conflicts with Design.                               |
| 02    | FAIL   | Readiness, engine changes, delegation, brownfield entry, and research routing do not have sharp in-or-deferred boundaries. |
| 03    | FAIL   | Planning must still decide readiness contracts, engine ownership, and non-development workflow routing.                    |
| 04    | PASS   | The cross-component scope and both contract flags match the described orchestration and architecture changes.              |
| 05    | FAIL   | One declared boundary does not exist at the reviewed commit.                                                               |
| 06    | PASS   | The four questions identify real design decisions. Several must be resolved before planning.                               |
| 07    | FAIL   | Motivation explains the problem but does not justify its timing.                                                           |
| 08    | FAIL   | Unknown ranges fit low confidence, but the estimate basis is not template-conformant or supported.                         |

### Summary

Checks 04 and 06 pass. Seven major and three minor findings remain open, including all eight prior findings. Resolve the completion contracts, scope boundaries, missing boundary, timing, and estimate basis before planning.
