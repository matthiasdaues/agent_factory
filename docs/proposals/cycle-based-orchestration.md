---
scope: global
schema_version: 2
status: superseded
owner: Matthias Daues
created: 2026-09-13
updated: 2026-09-14
supersedes: docs/proposals/deterministic-factory-engine.md

impact:
  scope: cross_component
  architecture_change: true
  external_contract_change: true
  boundaries:
    - packages/factory
    - packages/factory/playbooks
    - packages/factory/playbooks/brownfield-onboarding.md
    - packages/factory/playbooks/research-survey.md
    - packages/factory/playbooks/research-topic.md
    - packages/factory/agents
    - packages/factory/skills/run-step
    - packages/factory/skills/create-backlog
    - packages/factory/contracts
    - packages/factory/contracts/usage-record
    - packages/factory/scripts
    - packages/factory/scripts/phase
    - packages/factory/scripts/transition-lint
    - packages/factory/config/session-menu.md
    - packages/factory/rulebooks/schemas/research-brief.schema.json
    - packages/factory/rulebooks/templates/research-brief.md
    - packages/usage
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
  as_of: 2026-09-14
  basis: judgment
  confidence: low
  human_review_hours: unknown
  normalized_tokens: unknown
  estimated_consumption: unknown
---

# Feature Request: Cycle-Based Orchestration

## Summary

Replace the linear software-delivery playbook model with a cycle-based directed
graph. Artifact state drives transition recommendations. Humans drive routing
decisions. The system suggests what comes next. The human selects a cycle or
delegates that choice. Reconciliation becomes a standard transition assessment.

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

The [user-experience review](../reviews/ux-review-2026-09-09-new-user-journey.md)
documented fixed workflow selection, disproportionate ceremony, and fragmented
session state on 2026-09-09. Two days later, the deterministic-engine proposal
prepared to extract the current linear playbook model into a reusable core.
That extraction has not been implemented, and `packages/factory/engine/` does
not exist yet. The factory can therefore define the cycle-native model before
investing in linear-model engine code, tests, and adapters. Concurrent
workstreams and their usage attribution also require state that one
repository-global playbook marker cannot represent.

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
- Reconciliation is not a phase. It is a standard assessment at every cycle
  transition.
- Proportionality emerges from the graph. A small change traverses fewer
  cycles and exits earlier. A large change traverses more. The system
  recommends a route from artifact state. The human decides.
- The canonical concept model consists of `docs/spec/scope-map.md`,
  `docs/spec/entity-model.yaml`, and `docs/arc42/architecture.dsl`. Their
  existence provides the factory's recommended baseline. Their content is
  revisable. Every cycle checks whether implementation evidence requires them
  to be adapted, reconciled, or redesigned. Proposals are origins. Feature
  files, ADRs, and backlog files are elaborations or derived artifacts. When
  artifacts disagree, the canonical model is authoritative.
- Fitting configures the factory for a repository. Fitting is a prerequisite,
  not a delivery cycle.
- Brownfield entry reconstructs the canonical concept model from code, tests,
  persistence schemas, and infrastructure-as-code. The factory recommends
  completing all three canonical concept artifacts before feature delivery. A
  human may continue with explicit warnings when that evidence is incomplete.
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
- `docs/spec/entity-model.yaml` — LinkML entities, relationships, and invariants

The LinkML file is the canonical entity model. Markdown and rendered Entity
Relationship Diagram (ERD) files are derived projections. The canonical path
resolves the location decision recorded in
[T-0006](../spec/todo.md#t-0006--harmonize-the-canonical-erd-location-across-scenarios).

The bootstrap assessment recommends feature delivery when all three objects
exist, pass deterministic validation, and have no unresolved major review
findings. The brownfield onboarding procedure produces all three during its
first stage. Its deeper reverse-engineering stage remains optional. A human may
select another cycle before the baseline is complete. The factory then reports
the missing evidence and continues without requiring an override ceremony.

The bootstrap exits to a delivery-ready repository state. It does not create a
ROADMAP or enter REALIZE. New changes then begin at IDEA with a proposal.

### LinkML entity-model contract

`docs/spec/entity-model.yaml` is the machine-readable source of truth for domain
entities, value objects, slots, relationships, identities, and invariants. The
factory derives `docs/spec/entity-model.md` and
`docs/assets/images/entity-model.svg` from that source. Neither derived artifact
may introduce model information absent from the LinkML source.

The LinkML model defines table-backed entities and structured JSON value objects
as classes in the same model. A JSON-backed slot references its value-object
class and declares inline containment. The persistence adapter serializes the
validated value object into a JSON or JSONB column.

Generated Pydantic models own payload shape and application business
invariants. The database owns the JSON column type, nullability, and storage
constraints. Persistence integration tests own serialization and retrieval
fidelity. Database-level JSON Schema validation is not required.

Every persisted JSON value object carries a schema-version discriminator. A
versioning policy defines whether the application reads an older version,
migrates it, or rejects it with a declared error.

Mechanical entity-model readiness requires all of these results:

- The canonical LinkML file exists and passes LinkML metamodel validation.
- `linkml-lint` reports no errors.
- Every referenced class and slot resolves.
- Every JSON-backed slot references a defined inline class.
- Every persisted JSON value-object class defines the schema-version slot.
- The Markdown and SVG projections are generated from the current LinkML file.
- No major entity-model review finding remains open.

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

The tracked engine source lives under `packages/factory/engine/`. Installation
copies the same relative tree to `factory/engine/`. The engine contains every
component that evaluates, recommends, selects, resumes, retries, delegates, or
dispatches work:

```text
packages/factory/engine/
├── README.md
├── __init__.py
├── models/
│   └── delivery.yaml
├── schemas/
│   ├── cycle-model-v1.schema.json
│   └── cycle-state-v1.schema.json
├── cycle_model.py
├── readiness.py
├── recommendations.py
├── state.py
├── workstreams.py
├── delegation.py
├── dispatch.py
└── decisions.py
```

The deferred research-engine migration may add `models/research.yaml`. The
first release does not create or consume that file.

Commands under `packages/factory/scripts/` remain thin adapters. They own
command-line parsing, output, exit codes, process lifecycle, and cycle-state
writes. Agents remain the actors, and skills remain their procedures. Session
menu content remains user-interface configuration. External integration
schemas, including the usage-record contract, remain under
`packages/factory/contracts/`.

The engine does not import scripts, configuration, agent definitions, skills,
or the separately packaged orchestrator. Scripts and the orchestrator may call
the engine. The engine model and private schemas live with the engine because
they define how the factory moves.

The cycle proposal replaces these linear contracts as one change:

- Playbook `.fsm.yml` files stop being the authority for software-delivery
  routing.
- `.current-work/playbook-state.yml` is replaced by one cycle-state file per
  workstream.
- The engine model represents cycles, artifact assessments, declared routes,
  recommendation evidence, human selection, and retry limits.
- `run-step`, the new `cycle` command, and `transition-lint` consume the same
  cycle-native decision model. None retains a private parser or transition
  implementation.

The existing commands remain operational until the cycle-native replacements
pass their characterization and installed-shape tests. The cutover does not
create an intermediate engine that treats linear playbook phases as its domain
model.

### Compatibility contract

The acceptance commit fixes the compatibility baseline. Agent and skill names
come from `packages/factory/INDEX.yaml` at that commit. Agent frontmatter at the
same commit defines the baseline output paths.

The cycle migration keeps these observable contracts:

| Surface          | Contract kept                                                                                                                                                                                                           |
| ---------------- | ----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| Agent identities | Every agent name indexed at the acceptance commit                                                                                                                                                                       |
| Skill identities | Every skill name indexed at the acceptance commit, including `run-step`                                                                                                                                                 |
| Agent outputs    | Declared output paths and meanings, except the entity-model and epic-plan migrations listed below                                                                                                                       |
| Standard checks  | Command names, triggers, result formats, and exit behavior for `mdformat`, `link-check`, `mermaid-lint`, `spec-lint`, `arch-lint`, `backlog-lint`, `concern-lint`, `matrix-lint`, `statemachine-lint`, and `index-lint` |
| Branch safety    | `verify-base` and `premerge-check` command contracts                                                                                                                                                                    |
| REALIZE quality  | Project tests, `crap-score`, `dependency-check`, `test-design-verify`, code review, and risk-selected quality assurance                                                                                                 |
| Review artifacts | Existing specification, architecture, code, quality-assurance, and reconciliation review outputs                                                                                                                        |
| `run-step`       | Skill name, repository-derived resume, one invocation at a time, and no blind retry                                                                                                                                     |

The cycle migration intentionally replaces these contracts:

| Current contract                        | Replacement                                                                     |
| --------------------------------------- | ------------------------------------------------------------------------------- |
| Playbook `.fsm.yml` routing authority   | `factory/engine/models/delivery.yaml` recommendation model                      |
| `.current-work/playbook-state.yml`      | One `.current-work/cycles/<workstream-id>.yaml` file per workstream             |
| Agent `phase` metadata                  | Cycle eligibility metadata                                                      |
| `run-step` playbook resolution          | Cycle-state and recommendation-model resolution                                 |
| `phase advance`                         | `factory/scripts/cycle select --state STATE TARGET [--work REF ...]`            |
| `phase retry`                           | `factory/scripts/cycle retry --state STATE`                                     |
| `transition-lint` phase-order rejection | Cycle-model and cycle-state integrity checks; recommendation warnings exit zero |
| Supplementary entity-model path         | The canonical LinkML entity-model contract defined above                        |
| Python 3.8+ minimum for phase commands  | Python 3.10+ minimum for all cycle-based orchestration commands                 |
| `backlog/epics.md`                      | `backlog/epics-<feature-name>.md`                                               |

The cutover retires `phase` after all factory consumers use `cycle`.
`factory/scripts/phase` remains for one release as a diagnostic stub. It exits
2 and names the replacement command. It does not emulate the old
single-forward-transition behavior. Playbook Finite State Machine files remain
reference documents and lose runtime authority.

### Declarative recommendation model

The tracked product source is
`packages/factory/engine/models/delivery.yaml`. An installed project reads
`factory/engine/models/delivery.yaml`. The file contains the five delivery
cycles, the terminal `DONE` node, artifact declarations, and every route that
the factory can recommend. Its schema and compatibility rules live under
`packages/factory/engine/schemas/`.

Every route has `from`, `to`, and `recommend_if` fields. Routes have no
direction or classification field. The source and target define the directed
edge. Recommendation evidence explains why the factory suggests that edge.
Failed or missing evidence produces warnings; it never removes a route or
prevents a human from selecting a cycle.

The evaluator does not rank mechanically supported routes. Its result depends
on the number of routes whose recommendation evidence passes:

| Supported routes | Result                                                                     |
| ---------------: | -------------------------------------------------------------------------- |
|             Zero | Report no evidence-supported recommendation; show warnings and every cycle |
|              One | Recommend that route; show its evidence and every other cycle              |
|    More than one | Present the supported routes as choices; do not select between them        |

The YAML refers to trusted validators by identifier. It cannot contain shell
commands. Each validator reports the artifact reference, the evaluated commit,
individual check results, and warnings. The engine computes recommendations
from those reports. It does not write repository state.

Each graph instance uses `.current-work/cycles/<workstream-id>.yaml`. No global
active-cycle file exists. A state file contains only these fields:

```yaml
schema_version: 1
revision: 1
workstream_id: cycle-based-orchestration
topic: Replace playbook orchestration with adaptive cycles
origin_ref: docs/proposals/cycle-based-orchestration.md
cycle: IDEA
attempt: 1
work:
  - docs/proposals/cycle-based-orchestration.md
delegation:
  route:
    - CONCEPT
    - REFINE
    - REALIZE
```

`revision` and `attempt` are positive integers. A new workstream starts at
`revision: 1` and `attempt: 1`. `origin_ref` and `delegation` may be null. The
`work` list contains references to existing proposals, epic sections, or story
files. The state file never copies requirements or assessment results.
Assessments use the current commit.

The first release does not support project overrides of the factory graph.
Projects may add validators and artifact declarations after an extension
contract defines namespacing, compatibility, and failure behavior.

### Workstreams, sessions, and usage attribution

A workstream is one traversal of the delivery graph. A cycle is the
workstream's current stage. A session is one command-line interface conversation
or agent session. A run is one captured invocation within a session.

A repository may contain several workstream state files. Several sessions may
use one workstream, and one session may switch workstreams. A session binding
under `.current-work/session-bindings/<cli>/<session-id>.yaml` identifies the
active workstream. Path components use the existing usage-capture filesystem-key
encoding. The binding records the last observed workstream revision and SHA-256
digest. The binding is session-local navigation state, not delivery evidence.

The factory suggests a new workstream before starting substantial work on an
independent objective. Explicit topic changes, a new deliverable, or a different
proposal or story set trigger the suggestion. Clarifications, supporting
research, and implementation details remain in the current workstream. The
factory never switches workstreams without human confirmation. It suggests the
same apparent boundary only once unless the objective changes again.

After confirmation, the factory captures the old usage boundary when the
producer supports it. The factory then creates or reopens the workstream,
updates the session binding, and continues the request. Subsequent invocations
use the new attribution context.

The usage-record v1 contract gains three optional fields:

- `workstream_id`
- `workstream_origin`
- `cycle`

Missing cycle context leaves all three fields null and never fails capture. The
orchestration adapter supplies the fields; usage capture does not import or
query the cycle engine. Child agents inherit the workstream and their dispatch
cycle.

Per-invocation usage is attributed directly. Monotonic cumulative usage is
attributed by subtracting snapshots at workstream boundaries. When neither
method is available, analysis reports workstream attribution as unavailable.
Analysis never assigns a complete cumulative session to the workstream active
at session end. Context carried from an earlier topic counts toward the
workstream active for the current invocation.

Usage analysis adds workstream, cycle, and workstream-by-cycle dimensions. This
supports comparisons between direct realization and delivery through ROADMAP or
REFINE. Analysis reads immutable usage records and never depends on retained
`.current-work` files.

### Same-workstream concurrency

If two sessions change one workstream concurrently, one change succeeds and the
other pauses. A stale session never overwrites newer workstream state. Sessions
that change different workstreams do not block each other.

Every workstream mutation uses its session binding's observed revision and
SHA-256 digest as the expected state. The digest covers the exact state-file
bytes. It detects direct edits that do not increment `revision`.

The adapter acquires an exclusive operating-system lock at
`.current-work/cycles/.locks/<workstream-id>.lock`. The lock covers only the
read, comparison, validation, and replacement. It contains no workflow data.
The operating system releases the lock when the process exits.

While holding the lock, the adapter reads and validates the current state. A
revision or digest mismatch returns this result without writing:

```yaml
status: conflict
reason: stale_workstream_state
workstream_id: cycle-based-orchestration
expected_revision: 7
current_revision: 8
next_action: refresh_and_confirm
```

A valid mutation increments `revision` once. The adapter writes a temporary
sibling file, flushes it, and atomically replaces the state file. The adapter
then updates the successful session binding with the new revision and digest.
An interruption between these writes leaves a stale binding. The next mutation
detects that stale binding.

A command waits at most five seconds for the workstream lock. It returns
`workstream_busy` without writing when the wait expires. A stale-state conflict
also leaves the rejected session binding unchanged. Workstream-menu selection
or an explicit refresh updates the observation. Refresh never repeats the
rejected mutation.

The engine does not merge state changes or retry a rejected mutation. A human
sees the current state and confirms a new command. Delegated execution pauses
and returns control to the human. Read-only assessment needs no lock because
atomic replacement exposes either the previous complete file or the next one.

This mechanism is the first-release implementation. A later implementation may
replace the locking primitive if it keeps the observable concurrency rules.

### Session menu

Options A, D, and E keep their existing behavior. Option B becomes **Start a
new workstream**. It captures the topic, creates the state file, binds the
session, and enters IDEA. Option C becomes **Continue a workstream**.

Option C lists each current workstream's topic and cycle. After selection, the
factory binds the session, assesses repository evidence, and presents route
recommendations. If no current workstream exists, option C offers option B or a
return to the menu. The factory never selects a workstream automatically.

### The five cycles

Each cycle transforms input artifacts into output artifacts. The agents and
skills assigned to a cycle are the same ones the factory uses today; only their
sequencing changes.

#### 1. IDEA

Transform a vague idea into a decision-complete proposal.

- **In:** nothing (a stated intention)
- **Out:** `docs/proposals/<name>.md` at status `accepted`
- **Agents/skills:** virgil, grilling, draft-proposal, domain-modeling
- **Assessment:** recommend CONCEPT when the proposal exists, passes template
  lint, and has status `accepted`
- **Human interaction:** proposal acceptance is a human decision
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
  - `docs/spec/entity-model.yaml` — what things mean (domain entities,
    their relationships, and their invariants; distinct from the domain
    vocabulary in `docs/CONTEXT.md`, which names and defines terms)
  - `docs/arc42/architecture.dsl` — how it is shaped
- **Out — elaborations:**
  - `docs/spec/*.feature` — behavioral contracts derived from scope-map
  - `docs/adr/*.md` — decisions crystallized during concept work
- **Agents/skills:** requirements-agent, architecture-agent, derive-feature,
  reverse-map, capture-context, domain-modeling
- **Assessment:** recommend a downstream cycle when the three canonical
  artifacts pass validation and concept review has no unresolved major finding
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
- **Out:** `backlog/epics-<feature-name>.md` with sequenced epics and
  testability assessments
- **Agents/skills:** planning-agent (create-backlog-epics, write-epics,
  testability-probe)
- **Assessment:** recommend REFINE or REALIZE when the epic plan passes backlog
  validation, each selected epic has a testability assessment, and ownership
  gaps are resolved

#### 4. REFINE

Produce implementation-ready stories for the next batch.

- **In — from CONCEPT:** accepted proposal plus concept artifacts
- **In — from ROADMAP:** selected epics from
  `backlog/epics-<feature-name>.md` plus concept artifacts
- **Out:** `backlog/ST-NNNN.md` stories with slices for the next batch
- **Agents/skills:** planning-agent (create-backlog-stories, grilling,
  make-concrete, slice-story)
- **Assessment:** recommend REALIZE when the selected stories pass backlog
  validation, dependencies resolve, and contract questions are resolved
- **Human interaction:** story shaping and contract decisions normally request
  human direction unless an explicit delegation grant supplies it

#### 5. REALIZE

Build the batch.

- **In — from CONCEPT:** the accepted proposal
- **In — from ROADMAP:** selected epics from
  `backlog/epics-<feature-name>.md`
- **In — from REFINE:** selected `backlog/ST-NNNN.md` stories
- **Out:** merged code + tests on the target branch
- **Agents/skills:** implementation-agent, developer-agent, code-review-agent,
  qa-agent (risk-selected)
- **Assessment:** recommend DONE when the selected work's acceptance checks,
  required tests, quality checks, code review, and reconciliation pass for the
  assessed commit

REALIZE consumes existing planning artifacts. It does not generate an
implementation-unit file. The cycle-state marker stores references to the
selected proposal, epic sections, or story files without copying their
requirements. A direct CONCEPT-to-REALIZE route uses the proposal's boundaries
and completion criteria. A direct ROADMAP-to-REALIZE route uses the selected
epics' scope, dependencies, and testability ownership. The REFINE-to-REALIZE
route uses the selected stories.

REALIZE has an internal sequence. Risk selection determines which steps run for
each selected work item:

```text
implementation
      |
code review
      |
tests and deterministic gates
      |
risk-based QA (security review, bug hunt — when warranted)
      |
reconciliation assessment
```

### Declared routes

`delivery.yaml` declares the routes that the factory can recommend. It does not
classify them as forward, backward, progression, or rework. Each declaration
uses only a source, a target, and evidence that supports the recommendation.

| From    | To      | Recommendation evidence                                                                                            |
| ------- | ------- | ------------------------------------------------------------------------------------------------------------------ |
| IDEA    | CONCEPT | Proposal status is `accepted`; proposal validation passes                                                          |
| CONCEPT | ROADMAP | Scope map, entity model, architecture, required feature specifications, and concept reviews pass their assessments |
| CONCEPT | REFINE  | Concept assessment passes; proposal boundaries and completion criteria are present                                 |
| CONCEPT | REALIZE | Concept assessment passes; proposal boundaries, completion criteria, and test evidence expectations are present    |
| ROADMAP | REFINE  | Epic plan validation and testability assessment pass                                                               |
| ROADMAP | REALIZE | Selected epics define buildable scope, resolved dependencies, acceptance checks, and test ownership                |
| REFINE  | REALIZE | Selected stories pass backlog validation; dependencies resolve; contract questions have answers                    |
| REALIZE | DONE    | Selected work acceptance, tests, quality checks, code review, and reconciliation pass for the assessed commit      |
| CONCEPT | IDEA    | Reconciliation reports that the proposal no longer describes the intended change                                   |
| ROADMAP | IDEA    | Reconciliation reports that the proposal no longer describes the intended change                                   |
| ROADMAP | CONCEPT | Reconciliation reports an invalid concept artifact                                                                 |
| REFINE  | IDEA    | Reconciliation reports that the proposal no longer describes the intended change                                   |
| REFINE  | CONCEPT | Reconciliation reports an invalid concept artifact                                                                 |
| REFINE  | ROADMAP | Reconciliation reports that the epic plan must change                                                              |
| REALIZE | IDEA    | Reconciliation reports that the proposal no longer describes the intended change                                   |
| REALIZE | CONCEPT | Reconciliation reports an invalid concept artifact                                                                 |
| REALIZE | ROADMAP | Reconciliation reports that the epic plan must change                                                              |
| REALIZE | REFINE  | Reconciliation reports that selected stories must change                                                           |

A human may select any cycle, including a route absent from this table. Missing
recommendation evidence produces a visible warning. The factory continues
without requiring an override flag or justification. Reconciliation supplies
recommendations when an existing artifact no longer describes the work; it does
not control the human's selection.

### Human interaction and delegation

IDEA and REFINE normally pause for human direction because proposal acceptance
and story shaping require human judgment. The pause collects a decision; it does
not enforce a readiness policy. A prior delegation grant may already contain
that decision.

The system presents its recommendation, evidence, and warnings. The human may
select any cycle without an override flag or required justification. An explicit
delegation grant records routing decisions that the engine may execute without
asking again. The human creates, replaces, or revokes the grant. The engine and
its agents cannot create, extend, or broaden it.

A grant contains exactly one of these forms:

```yaml
delegation:
  route:
    - CONCEPT
    - REFINE
    - REALIZE
```

An explicit `route` is an ordered sequence of human-authored cycle selections.
The engine follows that sequence while showing recommendation evidence and
warnings. Failed recommendation evidence does not invalidate the human's
recorded choice.

```yaml
delegation:
  through: REALIZE
```

A `through` grant authorizes automatic continuation only while exactly one
route has supporting evidence. The engine pauses when zero or multiple routes
have supporting evidence. The engine also pauses when it reaches the named
destination or the next choice falls outside the grant. A technical execution
failure always stops the run.

Delegated execution may continue without the human present. The grant supplies
the authority; human presence does not define the boundary.

### Retry limits

Retry limits stop unattended loops. They do not prevent a human from
continuing. Each cycle in `engine/models/delivery.yaml` declares a positive
`delegated_attempt_limit`:

```yaml
cycles:
  REALIZE:
    delegated_attempt_limit: 5
```

Entering a cycle starts at `attempt: 1`. `cycle retry` requests another attempt
at the current cycle and work selection. An allowed retry increments `attempt`
before the adapter reruns the cycle.

Selecting a different cycle resets `attempt` to `1`. Changing the `work` list
also resets it to `1`, including when the cycle stays the same. Changing
sessions, resuming a workstream, reassessing artifacts, or editing files does
not reset it.

The adapter identifies a retry request as human-authored or delegated. A
delegated retry below the limit returns `allowed`. At the limit, it returns this
immutable result and leaves the state unchanged:

```yaml
status: paused
reason: delegated_attempt_limit_reached
cycle: REALIZE
attempt: 5
limit: 5
next_action: request_human_direction
```

A human-authored retry at or above the limit returns `allowed_with_warning` and
increments `attempt`. It requires no override flag or justification. Malformed
retry state returns `invalid_state` without writing. Once the adapter accepts a
retry, the attempt is consumed. Every later outcome retains the increment,
including failure to start or complete the assigned execution. The adapter
never rolls an accepted attempt back.

The cycle-state file retains only the current attempt. Usage and execution
records provide history when available.

### Transition recommender

At every cycle exit, the system:

1. Runs the artifact assessments.
2. Runs reconciliation when the cycle changed code or a canonical artifact.
3. Evaluates the `recommend_if` evidence for each declared route.
4. Presents the result defined by the supported-route table, including evidence,
   warnings, and the other cycles.

The human selects the next cycle. Failed assessments inform that selection but
do not restrict it. A technical failure states why the receiving tool cannot
run; it does not present a process rule as the cause.

### Artifact state detection

The system reads the repository and reports the evidence available for a route
recommendation. This requires two layers:

- **Mechanical validation:** file exists, passes format lint, required fields
  present. Scriptable and deterministic.
- **Semantic assessment:** "Does the code contradict the scope-map?" "Has
  an architecture boundary been disproved by implementation?" Requires
  LLM-based comparison of artifacts against each other or against code.

Mechanical validation runs unconditionally for referenced artifacts. Semantic
comparison runs when a cycle changed code or a canonical artifact. Neither
layer authorizes a transition.

Each trusted validator returns the same result fields: artifact type, artifact
reference, assessed commit, individual checks, and warnings. The following
table defines the complete first-release readiness evidence.

| Artifact                     | Required inventory                                                  | Evidence supporting a recommendation                                                                              |
| ---------------------------- | ------------------------------------------------------------------- | ----------------------------------------------------------------------------------------------------------------- |
| Proposal                     | Active `docs/proposals/<name>.md`                                   | Proposal format passes; required sections exist; recorded status matches the route                                |
| Scope map                    | `docs/spec/scope-map.md`                                            | Scope-map validation passes; behavior identifiers are unique; evidence and feature references resolve             |
| Entity model                 | `docs/spec/entity-model.yaml`                                       | The LinkML readiness checks in this proposal pass; derived projections match the assessed source                  |
| Architecture                 | `docs/arc42/architecture.dsl`                                       | Structurizr validation and architecture lint pass; referenced views resolve                                       |
| Feature specifications       | Feature references declared by the scope map                        | Every referenced Gherkin file parses; required tags exist; scope-map identifiers resolve                          |
| Gaps report                  | Gaps report derived for the active proposal                         | Required sections exist; every recorded gap has an identifier and disposition                                     |
| Architecture Decision Record | Decision references declared by the proposal or architecture        | Every referenced Architecture Decision Record has valid metadata, status, context, and decision sections          |
| Concept reviews              | Reviews of the active specification and architecture                | Review records parse; every major finding has a recorded disposition; repeat-review status is reported            |
| Epic plan                    | `backlog/epics-<feature-name>.md` for the active proposal           | Backlog validation passes; epic identifiers and dependencies resolve; each epic records testability and ownership |
| Selected stories             | Explicitly selected `backlog/ST-NNNN.md` files                      | Backlog validation passes; dependencies resolve; acceptance checks and contract decisions are present             |
| Realization result           | Selected proposal, epic sections, or stories at the assessed commit | Acceptance checks, required tests, quality checks, code review, and reconciliation report their current results   |
| Research brief               | Brief selected by the delivery or research session                  | Brief schema passes; linked briefs declare origin cycle, origin reference, return cycle, and decision needed      |
| Research report              | Report declared by the selected research brief                      | Route-specific research validation passes; the report references the brief and records its evidence disposition   |

Fixed paths identify canonical artifacts. An authoritative artifact lists the
required members of a collection. The cycle-state marker lists selected runtime
work by reference. File globs may discover candidates, but they never define a
complete collection.

### Verification contract

Verification checks the model and interpreter without maintaining a second
registry of route fixtures.

| Surface             | Required verification                                                                                                                 |
| ------------------- | ------------------------------------------------------------------------------------------------------------------------------------- |
| Cycle model         | Schema rejects missing nodes, unknown artifacts, unknown validators, executable commands, direction fields, and classification fields |
| Loaded routes       | A generic invariant visits every route and confirms that its source, target, and predicates resolve                                   |
| Route evaluator     | Focused tests cover zero, one, and multiple supported routes                                                                          |
| Predicates          | Each trusted predicate has focused passing and failing tests                                                                          |
| Artifact validators | Each validator has focused valid, invalid, and stale-evidence tests                                                                   |
| Human selection     | Tests cover a supported route, a route with failed evidence, and a cycle absent from the recommendation table                         |
| Reconciliation      | Tests cover code changed, canonical artifact changed, and neither changed                                                             |
| Retry evaluator     | Tests cover delegated and human retries below, at, and above the limit; reset rules; invalid state; and technical failure             |
| State concurrency   | Tests race same-workstream and different-workstream mutations, direct edits, lock timeout, interruption, and delegated conflict       |
| Installed shape     | The installed factory loads the same schema-valid model as the tracked product source                                                 |

The generic route invariant reads route declarations directly from
`delivery.yaml`. No fixture declares route coverage, and no separate
route-coverage manifest exists.

## Scope

### In scope

- Define the five cycle types with their input artifacts, output artifacts,
  eligible agents and skills, and assessments.
- Define the declared routes and their `recommend_if` evidence in
  `packages/factory/engine/models/delivery.yaml`.
- Define the cycle-model and cycle-state schemas under
  `packages/factory/engine/schemas/`.
- Define reconciliation as a standard transition assessment when a cycle
  changes code or a canonical artifact.
- Define the transition recommender's interface and recommendation format.
- Define human selection and delegation grants without an override workflow.
- Define delegated retry limits, current-attempt persistence, reset rules, and
  human retry behavior.
- Apply the explicit compatibility and replacement tables. Do not retain
  unlisted orchestration behavior through a general compatibility promise.
- Support concurrent workstreams, session-to-workstream binding, and confirmed
  mid-session workstream changes.
- Prevent stale or concurrent sessions from overwriting newer workstream state.
- Add optional workstream and cycle context to usage capture and dimensional
  usage analysis.
- Implement the complete artifact readiness table in this proposal through
  trusted validator identifiers and a shared result format.
- Define fitting as a prerequisite outside the delivery graph.
- Define CONCEPT bootstrap as the recommended brownfield entry. Report missing
  concept evidence when a human selects another cycle.
- Make the Entity Relationship Diagram (ERD) part of the mandatory first stage
  of brownfield onboarding.
- Adopt `docs/spec/entity-model.yaml` in LinkML as the canonical entity model.
  Treat Markdown and SVG representations as derived projections.
- Define structured JSON payloads as LinkML value-object classes. Generate
  Pydantic validation and store validated instances in JSON or JSONB columns.
- Define and validate the delivery-to-research brief fields. Keep the existing
  survey and falsification routes unchanged.
- Create one cycle-native deterministic orchestration engine under
  `packages/factory/engine/`. The engine owns every mechanism that moves work.
  Retain the thin adapter, immutable decision, tracked-source, installed-shape,
  and dependency-boundary constraints from the superseded engine proposal.
- Replace playbook FSM authority and the playbook-state marker with cycle-native
  graph and state contracts.
- Change session-menu option B to start a workstream and option C to continue a
  listed workstream. Keep options A, D, and E unchanged.
- Remove `phase:` ordinal metadata from agent definitions; replace with
  cycle eligibility tags.
- Migrate `run-step` and `transition-lint` to the cycle-native engine. Replace
  `phase` with the `cycle` command in the same cutover.

### Explicitly deferred

- Automated semantic ranking among downstream routes. The first release uses
  mechanical evidence for downstream recommendations and reconciliation for
  invalidation recommendations. The human may select any cycle regardless of
  either result.
- Removing playbook files. Playbooks remain as reference documentation for
  known-good sequences. They lose their role as the orchestration mechanism
  but are not deleted.
- Self-directed routing beyond a human-authored delegation grant. The first
  release does not infer, create, extend, or broaden delegation grants.
- Batch identity tracking across refinement-realization-reconciliation loops.
  Required for multi-batch delivery but not for single-batch operation.
  Multi-batch identity is necessary before the proposal can deliver its
  complete learning-loop model; without it, reconciliation cannot trace
  which concept version shaped which implementation batch. This deferral
  is acceptable for the first release but must follow promptly.
- Replacing the internal survey and falsification routes with a new research
  orchestration engine. Research keeps its current routes in the first release.

## Open Questions

None.

## Completion Criteria

- `packages/factory/engine/models/delivery.yaml` validates against the versioned
  cycle-model contract and declares IDEA, CONCEPT, ROADMAP, REFINE, REALIZE,
  DONE, every artifact in the readiness table, and every route in the declared
  route table.
- Each declared route contains `from`, `to`, and `recommend_if`. The schema
  rejects direction and route-classification fields.
- Each artifact declaration references a trusted validator identifier. The
  schema rejects executable command fields.
- Every artifact validator has valid, invalid, and stale-evidence tests. Every
  result contains artifact type, reference, assessed commit, checks, and
  warnings.
- A generic invariant visits every route loaded from `delivery.yaml`. It fails
  when a source, target, artifact, validator, or predicate reference does not
  resolve.
- Route-evaluator tests cover zero, one, and multiple supported routes. Multiple
  supported routes produce choices without automatic ranking.
- Session-menu option B creates and binds a named workstream. Option C lists
  current workstream topics and cycles before binding the selected workstream.
  Options A, D, and E retain their acceptance-commit behavior.
- Agent definitions carry cycle eligibility tags instead of phase ordinals.
- `run-step` executes cycle steps, not playbook steps.
- Reconciliation runs when a cycle changes code or a canonical artifact. Other
  transitions report that reconciliation does not apply.
- The transition recommender follows the supported-route result table and shows
  evidence, warnings, and the other cycles at every cycle exit.
- A human can select a cycle whose recommendation evidence failed. The engine
  records the selection and warnings without requesting an override flag or
  justification.
- IDEA and REFINE request human direction when no delegation grant contains the
  required decision.
- An explicit-route grant follows its ordered human-authored cycle selections,
  including selections with failed recommendation evidence.
- A destination grant continues only while exactly one route has supporting
  evidence. Zero or multiple supported routes pause for human direction.
- The engine pauses when a grant ends and stops on technical failure. Only the
  human can create, replace, revoke, or broaden a grant.
- A compatibility check compares indexed agent and skill names with the
  acceptance commit. The result permits only the exceptions in the intentional
  replacement table.
- Characterization tests for every standard check, branch-safety command, and
  REALIZE quality command in the compatibility table retain their existing
  success, failure, and result-format behavior.
- A single-batch delivery (IDEA through REALIZE to DONE) completes
  successfully under the cycle model.
- A fitted brownfield repository with an incomplete concept baseline receives a
  recommendation to complete CONCEPT and a list of missing evidence. A human
  selection of another cycle proceeds with those warnings.
- Brownfield onboarding produces all three canonical concept objects in its
  mandatory first stage. Its optional second stage is not a delivery
  prerequisite.
- A delivery cycle can create a schema-valid linked research brief. A validated
  research report returns to the brief's declared `return_cycle`.
- Standalone survey and falsification runs complete through their existing
  routes without entering the delivery graph.
- The deterministic-engine proposal has status `superseded`. No implementation
  story extracts the linear playbook model into the engine.
- One implementation under `packages/factory/engine/` owns cycle-model loading,
  artifact assessments, route recommendations, workstream resolution,
  delegation coverage, dispatch eligibility, and retry-limit decisions. It
  does not authorize human selections or write cycle state.
- `run-step`, `phase`, and `transition-lint` consume that engine. No delivery
  transition reads a playbook FSM as its authority after cutover.
- Installed-shape tests find the same engine tree and model under
  `factory/engine/`. Dependency-boundary tests reject engine imports from
  scripts, configuration, agent definitions, skills, or orchestrator code.
- Two workstream state files can hold different cycles and work references in
  one repository. Selecting either file does not modify the other.
- Two sessions that mutate the same observed workstream state cannot both
  succeed. One increments the revision; the other returns
  `stale_workstream_state` without writing or merging.
- A direct state-file edit causes a digest conflict for sessions that observed
  the previous content. A five-second lock timeout returns `workstream_busy`
  without writing.
- Interrupted replacement leaves one complete workstream state. Interrupted
  session-binding update leaves a stale binding that the next mutation detects.
- Different-workstream mutations proceed under separate locks. A conflict in a
  delegated run pauses and returns control to the human.
- No repository-global active-cycle file exists. Each session resolves its
  active workstream from its own binding.
- A confirmed topic change captures a supported usage boundary, updates the
  session binding, and attributes subsequent invocations to the new workstream.
- Usage capture succeeds with null workstream fields when no binding exists.
  Workstream attribution reports unavailable when no invocation or cumulative
  boundary measurement exists.
- Usage analysis groups records by workstream, cycle, and both dimensions
  without reading `.current-work`.
- `factory/scripts/cycle select` changes the selected workstream's cycle and
  work references. `factory/scripts/cycle retry` retries that workstream's
  current cycle.
- Every cycle declares `delegated_attempt_limit`. Entering another cycle or
  changing selected work resets `attempt` to `1`; other activity does not.
- A delegated retry below the limit increments `attempt`. A delegated retry at
  the limit pauses without changing state and returns
  `delegated_attempt_limit_reached` with the cycle, attempt, limit, and next
  action.
- A human retry at or above the delegated limit proceeds with a warning and no
  override ceremony. Invalid state does not increment the attempt. Any failure
  after a retry is accepted retains the incremented attempt.
- `factory/scripts/phase` no longer implements transitions. Its one-release
  diagnostic stub exits 2 and names the corresponding `cycle` command.
- `transition-lint` rejects invalid cycle models and malformed state files.
  Failed recommendation evidence produces warnings and exits zero.
- REALIZE uses references to the selected proposal, epic sections, or story
  files. No implementation-unit artifact is created.
- CONCEPT can recommend REFINE without an epic plan. REFINE then derives its
  selected stories from the active proposal and concept artifacts.
- ROADMAP writes `backlog/epics-<feature-name>.md`. REALIZE can use selected
  epics from that file without generating stories.
- `docs/spec/entity-model.yaml` passes the mechanical LinkML readiness checks.
  The Markdown and SVG projections contain no independently authored model
  information.
- A JSON-backed slot resolves to an inline LinkML value-object class. Generated
  Pydantic validation rejects an invalid payload before persistence.
- A persistence integration test stores and retrieves a valid generated value
  object without losing fields or schema-version information.

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

## Author Remediation Notes — 2026-09-14

These notes record author changes after the latest review. They do not change
the historical reviewer verdict. An independent repeat review determines the
finding status.

| Finding | Author disposition                | Basis                                                                                                                                                                                                                                                                                                                                              |
| ------- | --------------------------------- | -------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| PROP-01 | Remediated; pending repeat review | [Compatibility contract](#compatibility-contract) enumerates preserved and replaced contracts. [Workstreams, sessions, and usage attribution](#workstreams-sessions-and-usage-attribution) defines concurrent state and usage behavior. [Session menu](#session-menu) and [Completion Criteria](#completion-criteria) provide observable checks.   |
| PROP-02 | Remediated; pending repeat review | [Declarative recommendation model](#declarative-recommendation-model) names the YAML format and versioned schema. [Verification contract](#verification-contract) defines generic route invariants, focused validator tests, result-cardinality tests, human-selection tests, and three reconciliation cases without a route-fixture registry.     |
| PROP-05 | Remediated; pending repeat review | [Human interaction and delegation](#human-interaction-and-delegation) defines explicit-route and destination grants, their pause conditions, and sole human ownership of grant changes. [Explicitly deferred](#explicitly-deferred) excludes self-directed routing beyond those human-authored decisions.                                          |
| PROP-06 | Remediated; pending repeat review | [Cycle-native deterministic engine](#cycle-native-deterministic-engine) defines `packages/factory/engine/` as a new implementation tree beneath the existing `packages/factory` impact boundary. It assigns movement mechanics to the engine, keeps commands as adapters, and defines the installed and dependency boundaries.                     |
| PROP-07 | Remediated; pending repeat review | The estimate uses the template-defined `judgment` basis with low confidence and unknown ranges. No completed analogous change supports `analogous_change`; planning may replace the basis with `decomposition` after producing independently estimated stories.                                                                                    |
| PROP-08 | Remediated; pending repeat review | [Motivation](#motivation) identifies the 2026-09-09 user-experience review, the unimplemented linear-engine extraction, and concurrent workstream attribution as the events that make the cycle-native decision timely.                                                                                                                            |
| PROP-10 | Remediated; pending repeat review | Resolved by the PROP-03 recommendation-model remediation. [Artifact state detection](#artifact-state-detection) requires artifact assessments at every exit. Reconciliation runs only after code or canonical-artifact changes. [Completion Criteria](#completion-criteria) requires other transitions to report reconciliation as not applicable. |

## Review — 2026-09-14

Reviewer: proposal-review-agent
Reviewed commit: 38d23d2e3560504e152d033a09c9cccd82877f60
Disposition: findings

### Findings

| ID      | Severity | Check | Status   | Finding                                                                                                                                                                                                                                                      |
| ------- | -------- | ----- | -------- | ------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------ |
| PROP-01 | major    | 01    | resolved | The compatibility tables enumerate kept and replaced contracts. Completion criteria require baseline comparison and characterization tests.                                                                                                                  |
| PROP-02 | major    | 01    | resolved | The design names the YAML model, versioned schemas, validator result fields, route invariant, and focused tests.                                                                                                                                             |
| PROP-03 | major    | 02    | resolved | The readiness table defines the complete first-release artifact inventory and evidence. No readiness decision remains open.                                                                                                                                  |
| PROP-04 | major    | 02    | resolved | The design now creates a cycle-native engine and replaces the playbook state, FSM authority, and affected commands in one cutover.                                                                                                                           |
| PROP-05 | minor    | 02    | resolved | The two human-authored grant forms define unattended execution. Self-directed grant creation or expansion is deferred.                                                                                                                                       |
| PROP-06 | major    | 05    | resolved | Every current boundary resolves at the reviewed commit. The nonexistent `packages/factory/engine/flow_control` boundary was removed.                                                                                                                         |
| PROP-07 | minor    | 08    | resolved | The estimate now uses the valid `judgment` basis and records unknown ranges at low confidence.                                                                                                                                                               |
| PROP-08 | minor    | 07    | resolved | Motivation ties timing to the user-experience review, the unimplemented linear extraction, and concurrent attribution needs.                                                                                                                                 |
| PROP-09 | major    | 02    | resolved | Brownfield bootstrap and delivery-linked research are in scope. Internal research-route replacement is explicitly deferred.                                                                                                                                  |
| PROP-10 | major    | 01    | resolved | Artifact assessment runs at every exit. Reconciliation runs after relevant changes, and other transitions report it as not applicable.                                                                                                                       |
| PROP-11 | major    | 03    | open     | Retry limits are not decomposable. The state schema excludes retry history, yet the engine owns retry-limit decisions. Define the cap source, persisted counter, reset rules, and refusal result.                                                            |
| PROP-12 | major    | 03    | open     | Shared-workstream updates are not decomposable. Several sessions may use one workstream, but concurrent state-write behavior is undefined. Define atomicity, stale-write detection, and conflict handling, then add a same-workstream concurrency criterion. |

### Checks

| Check | Result | Evaluation                                                                                                                  |
| ----- | ------ | --------------------------------------------------------------------------------------------------------------------------- |
| 01    | PASS   | Completion criteria identify observable formats, cases, compatibility surfaces, command behavior, and end-to-end outcomes.  |
| 02    | PASS   | First-release and deferred lists separate routing, compatibility, brownfield, research, entity-model, and multi-batch work. |
| 03    | FAIL   | Planning must invent retry-limit persistence and concurrent update behavior for sessions that share one workstream.         |
| 04    | PASS   | Cross-component scope, architecture change, external contract change, assurance, and risk domains match the design.         |
| 05    | PASS   | Every declared boundary exists at `38d23d2e3560504e152d033a09c9cccd82877f60`.                                               |
| 06    | PASS   | The proposal records no open questions. The two remaining gaps are missing contracts, not genuine unresolved alternatives.  |
| 07    | PASS   | The timing follows documented user-experience findings and precedes investment in the superseded linear engine.             |
| 08    | PASS   | `judgment`, low confidence, and unknown ranges honestly reflect the undecomposed cross-component scope.                     |

### Summary

All ten prior findings are resolved, and seven checks pass. Two major design
gaps still require Planning to invent runtime state rules. Define retry-limit
state and same-workstream concurrency behavior before planning.

## Author Remediation Notes — 2026-09-14, repeat review

These notes record author changes after the latest independent review. They do
not change the historical reviewer verdict. Another independent repeat review
determines the finding status.

| Finding | Author disposition                | Basis                                                                                                                                                                                                                                                                                                   |
| ------- | --------------------------------- | ------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| PROP-11 | Remediated; pending repeat review | [Retry limits](#retry-limits) defines the model-owned delegated cap, persisted current attempt, reset rules, and engine results. [Completion Criteria](#completion-criteria) covers delegated and human retries, invalid state, technical failure, and state mutation behavior.                         |
| PROP-12 | Remediated; pending repeat review | [Same-workstream concurrency](#same-workstream-concurrency) defines atomic replacement, per-workstream locking, revision and digest checks, conflicts, timeouts, interruption behavior, and separate-workstream independence. [Completion Criteria](#completion-criteria) makes those cases observable. |

## Review — 2026-09-14

Reviewer: proposal-review-agent
Reviewed commit: 38d23d2e3560504e152d033a09c9cccd82877f60
Disposition: findings

This targeted repeat review covers the working-tree remediation for PROP-11 and
PROP-12. It also checks directly affected contracts and regressions in resolved
PROP-01 through PROP-10.

### Findings

| ID      | Severity | Check | Status               | Finding                                                                                                                                                          |
| ------- | -------- | ----- | -------------------- | ---------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| PROP-01 | major    | 01    | resolved (unchanged) | The retry and concurrency remediation does not weaken the compatibility baseline or its completion checks.                                                       |
| PROP-02 | major    | 01    | resolved (unchanged) | The added verification rows remain concrete and do not weaken the model or validator contracts.                                                                  |
| PROP-03 | major    | 02    | resolved (unchanged) | The added retry and concurrency scope matches the new design contracts.                                                                                          |
| PROP-04 | major    | 02    | resolved (unchanged) | Adapter-owned state mutation remains consistent with the cycle-native engine boundary.                                                                           |
| PROP-05 | minor    | 02    | resolved (unchanged) | Delegated retries remain bounded by human-authored grants and the delegated attempt limit.                                                                       |
| PROP-06 | major    | 05    | resolved (unchanged) | Every declared impact boundary exists in the reviewed working tree.                                                                                              |
| PROP-07 | minor    | 08    | resolved (unchanged) | The remediation does not change the estimate.                                                                                                                    |
| PROP-08 | minor    | 07    | resolved (unchanged) | The remediation does not change the timing argument.                                                                                                             |
| PROP-09 | major    | 02    | resolved (unchanged) | The remediation does not change brownfield or research routing scope.                                                                                            |
| PROP-10 | major    | 01    | resolved (unchanged) | Retry and concurrency verification does not change the reconciliation trigger contract.                                                                          |
| PROP-11 | major    | 03    | open                 | Retry failure semantics conflict. The adapter increments `attempt` before execution, but technical execution failure must not increment it. Define one behavior. |
| PROP-12 | major    | 03    | resolved             | The design defines locking, expected revision and digest checks, atomic replacement, conflicts, timeouts, and interruption behavior.                             |

### Checks

| Check | Result | Evaluation                                                                                                                                     |
| ----- | ------ | ---------------------------------------------------------------------------------------------------------------------------------------------- |
| 01    | FAIL   | Completion says technical failure does not increment `attempt`. The retry sequence increments it before the execution that can fail.           |
| 02    | PASS   | Retry limits and concurrency are in scope. Self-directed delegation and alternate future locking implementations remain deferred.              |
| 03    | FAIL   | PROP-12 is decomposable. PROP-11 still requires Planning to choose rollback or consumed-attempt semantics after a technical failure.           |
| 04    | PASS   | The cross-component, architecture, and external-contract classifications still match the affected contracts.                                   |
| 05    | PASS   | Every declared impact boundary exists in the reviewed working tree.                                                                            |
| 06    | PASS   | The remediation creates no open question. The PROP-11 conflict is a missing decision, not a genuine alternative recorded for later resolution. |
| 07    | PASS   | The remediation does not weaken the previously accepted timing case.                                                                           |
| 08    | PASS   | The unchanged low-confidence judgment estimate remains honest for this cross-component proposal.                                               |

### Summary

PROP-12 is resolved, and the remediation creates no regression in PROP-01
through PROP-10. PROP-11 remains open because retry state mutation conflicts
with the technical-failure completion criterion. One major finding remains
before this proposal is ready for planning.

## Author Remediation Notes — 2026-09-14, targeted repeat review

These notes record author changes after the targeted independent review. They
do not change the historical reviewer verdict. Another independent repeat
review determines the finding status.

| Finding | Author disposition                | Basis                                                                                                                                                                                                                                                |
| ------- | --------------------------------- | ---------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| PROP-11 | Remediated; pending repeat review | [Retry limits](#retry-limits) now states that every accepted retry consumes an attempt. Invalid state prevents acceptance and leaves the counter unchanged. Failure to start or complete execution after acceptance retains the incremented attempt. |

## Review — 2026-09-14

Reviewer: proposal-review-agent
Reviewed commit: 38d23d2e3560504e152d033a09c9cccd82877f60
Disposition: clean

### Findings

| ID      | Severity | Check | Status   | Finding                                                                                                                                                                                                                                                                          |
| ------- | -------- | ----- | -------- | -------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| PROP-01 | major    | 01    | resolved | The compatibility tables enumerate kept and replaced contracts. Completion criteria require baseline comparison and characterization tests. No regression from the PROP-11 remediation.                                                                                          |
| PROP-02 | major    | 01    | resolved | The YAML model, versioned schemas, validator result fields, route invariant, and focused tests remain concrete. No regression.                                                                                                                                                   |
| PROP-03 | major    | 02    | resolved | The readiness table defines the complete first-release artifact inventory and evidence. No regression.                                                                                                                                                                           |
| PROP-04 | major    | 02    | resolved | The cycle-native engine replaces playbook state, FSM authority, and affected commands in one cutover. No regression.                                                                                                                                                             |
| PROP-05 | minor    | 02    | resolved | Explicit-route and destination grants define unattended execution. Self-directed grant creation is deferred. No regression.                                                                                                                                                      |
| PROP-06 | major    | 05    | resolved | Every declared boundary resolves at the reviewed commit. No regression.                                                                                                                                                                                                          |
| PROP-07 | minor    | 08    | resolved | The estimate uses the valid `judgment` basis with low confidence and unknown ranges. No regression.                                                                                                                                                                              |
| PROP-08 | minor    | 07    | resolved | Motivation ties timing to the user-experience review, the unimplemented linear extraction, and concurrent attribution needs. No regression.                                                                                                                                      |
| PROP-09 | major    | 02    | resolved | Brownfield bootstrap and delivery-linked research are in scope. Internal research-route replacement is deferred. No regression.                                                                                                                                                  |
| PROP-10 | major    | 01    | resolved | Artifact assessment runs at every exit. Reconciliation runs after relevant changes. Other transitions report it as not applicable. No regression.                                                                                                                                |
| PROP-11 | major    | 03    | resolved | The retry section defines consumed-attempt semantics: once the adapter accepts a retry, the attempt increment is permanent. Invalid state prevents acceptance. Failure after acceptance retains the increment. The completion criteria match this behavior. No conflict remains. |
| PROP-12 | major    | 03    | resolved | Locking, revision-and-digest checks, atomic replacement, conflicts, timeouts, and interruption behavior are defined. No regression.                                                                                                                                              |

### Checks

| Check | Result | Evaluation                                                                                                                                                                          |
| ----- | ------ | ----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| 01    | PASS   | Every completion criterion identifies an observable format, behavior, or test case. The retry criteria now consistently define consumed-attempt semantics.                          |
| 02    | PASS   | The in-scope and deferred lists partition the space. No item appears in both. Each boundary is sharp enough to classify an arbitrary story.                                         |
| 03    | PASS   | Planning can write INVEST stories from the design without re-deriving it. The retry limits, concurrency, and all other sections define their contracts, state, and results.         |
| 04    | PASS   | Cross-component scope, architecture change, and external contract change match the engine, command, and usage-record changes described.                                             |
| 05    | PASS   | All 22 declared boundary paths resolve at the reviewed commit.                                                                                                                      |
| 06    | PASS   | No open questions remain. The prior gaps were missing contracts resolved through design decisions, not unresolved alternatives.                                                     |
| 07    | PASS   | The motivation identifies the 2026-09-09 user-experience review, the opportunity before linear-engine investment, and concurrent workstream attribution as specific timing drivers. |
| 08    | PASS   | The `judgment` basis, low confidence, and unknown ranges honestly reflect the undecomposed cross-component scope.                                                                   |

### Summary

All twelve prior findings are resolved. All eight checks pass. The proposal is ready for planning. No open findings remain.
