---
schema_version: 2
title: Activity-Graph Orchestration
status: open
owner: Matthias Daues
created: 2026-09-16
updated: 2026-09-17
supersedes: docs/proposals/cycle-based-orchestration.md

impact:
  scope: cross_component
  architecture_change: true
  external_contract_change: true
  boundaries:
    - packages/factory
    - packages/factory/engine
    - packages/factory/scripts
    - packages/factory/scripts/cycle
    - packages/factory/agents
    - packages/factory/skills/run-step
    - packages/factory/config/session-menu.md
    - packages/factory/contracts/usage-record
    - .agent-factory
    - .current-work

governance:
  assurance: high
  risk_domains:
    - compatibility
    - reliability
    - operations

estimate:
  as_of: 2026-09-16
  basis: judgment
  confidence: low
  human_review_hours: unknown
  normalized_tokens: unknown
  estimated_consumption: unknown
---

# Feature Request: Activity-Graph Orchestration

## Summary

Replace stage-based orchestration with a precondition graph over activities and
artifacts. The system tracks what artifacts exist and what shape they are in.
Agents and skills declare their prerequisites. The system shows what can run
next given the current repository state. No named stages, no transition matrix,
no state machine. The sequence emerges from the dependency chain. Rework means
fixing the artifact that needs fixing.

The factory retains structured transcripts and enriches usage records with
workstream, skill, and activity context at capture time. These replace
stage-attributed usage.

## Motivation

The cycle-based orchestration proposal (2026-09-13) replaced the linear
playbook model with a five-cycle directed graph. That graph is less rigid than
a pipeline, but it is still prescriptive. Five named stages, eighteen declared
routes, per-artifact readiness tables, and a recommendation engine steer the
human toward one path. "You may select any cycle" is formally true. It is
unlikely in practice when the system shows green checks on one route and
warnings on all others.

The deeper problem showed up in practice. A story grilling session discovers a
concept-level flaw. The correct response is to pause grilling, fix the
specification, and return. The stage model frames this as a full-cycle
transition — REFINE back to CONCEPT — with reconciliation evidence and
recommendation checks. That is ceremony for what should be "this assumption is
wrong, let me fix it upstream."

The stage model describes the wrong unit. Real work does not move between
stages. It moves between an activity and the artifact that activity
invalidated, at whatever granularity the invalidation requires. Sometimes that
is "the whole proposal is wrong." Sometimes it is "this one entity definition
is missing a field." A stage model treats both as the same kind of event.

Stages imply completeness. "CONCEPT is done" means "we stopped finding
problems with the concept," not "the concept is correct." The next downstream
activity tests upstream assumptions again regardless of what the model says.
When the model says "in REFINE," concept work reads as regression. But the
grilling found something. That is a result, not a failure.

The cycle-based orchestration proposal's EPIC 1 (workstream identity, session
binding, menu integration, basic assessment) is implemented. This proposal
keeps that infrastructure and replaces the stage-transition model that
EPICs 2–7 would have built.

The timing follows the same drivers as the cycle proposal: the 2026-09-09
user-experience review, the window before further stage-model investment, and
the need for concurrent workstream attribution.

## Core Principles

- The human drives. The system shows what is possible. The human chooses what
  to do. No recommendation engine ranks choices or presents warnings that
  discourage legitimate work.
- Artifacts are the ground truth. "What exists and what shape is it in?"
  replaces "which stage are you in?"
- Activities have preconditions, not phase assignments. An agent or skill
  declares what must exist before it can run. The system checks those
  preconditions against the repository. No named stage is involved.
- Rework is invisible to the model. Fixing an upstream artifact is fixing an
  artifact. No transition, no ceremony, no "returning to an earlier stage."
  The dependency graph has no forward direction to violate.
- Observability comes from what happened, not from stage attribution. Agent
  invocations, skill calls, files touched, and timestamps are the activity
  record.
- The factory enriches usage records. Workstream identity, skill invocations,
  and activity context are factory concerns, added at capture time. The usage
  package stores and queries whatever it receives.

## Design

### Terminology

An **activity** is one agent invocation within a workstream. Activities are the
nodes in the precondition graph. The graph is computed from agent declarations;
skills, manual edits, and other work within a session are not separate
activities.

### From stages to preconditions

The current agent and skill definitions carry metadata that associates them
with a context — today a `phase` ordinal or `eligible_cycles` list. This
proposal replaces that with a structured `inputs` declaration that
distinguishes required artifacts from contextual reading material.

```yaml
# Agent definition example
name: architecture-agent
inputs:
  required:
    - artifact: proposal
      path_pattern: "docs/proposals/{name}.md"
      conditions:
        - field: status
          value: accepted
  context:
    - docs/arc42/CONTEXT.md
    - docs/spec/scope-map.md
    - docs/spec/*.feature
    - docs/reviews/atam-review.md
    - docs/agent-context.md
outputs:
  - docs/arc42/architecture.dsl
  - docs/arc42/*.md
  - docs/adr/*.md
```

`inputs.required` lists the artifacts that must exist and the conditions they
must satisfy before the agent can do useful work. The precondition evaluator
checks only these entries. A required entry with no `conditions` key means the
file must exist. A `conditions` list adds constraints checked against YAML
frontmatter:

- `field` + `value` — the frontmatter field must equal the value.
- `field` + `one_of` — the frontmatter field must be one of the listed values.
- `check` — a named validator must pass. The named validators are the same
  scripts the factory already runs (`spec-lint`, `arch-lint`, etc.). They
  return structured results. The evaluator calls them and interprets pass/fail.

A failed condition does not block selection. The human can still choose the
activity. The evaluator reports unsatisfied requirements so the human knows
the input is broken before committing to a session.

#### Path resolution

A `path_pattern` like `"docs/proposals/{name}.md"` contains placeholders that
must resolve to concrete file paths. The evaluator expands the pattern as a
glob against the repository, finds all matching files, and checks conditions
on each match.

When a workstream is bound, the evaluator narrows results using `origin_ref`:
if the pattern matches the origin artifact's path, that match is preferred
over other glob hits. For patterns that don't match the origin, the evaluator
returns all matches that satisfy conditions — the human picks the relevant one
if there are multiple.

This keeps path resolution simple and stateless. No maintained artifact list
is needed.

`inputs.context` lists everything else the agent reads when running — material
it consumes if available, not gates on eligibility. `outputs` declares what
the agent creates or modifies, unchanged from the current format.

`outputs` is declarative for graph building: the evaluator uses it to compute
which activities become possible after a given agent runs. For delegation,
`outputs` serves as a success check: the delegation mechanism confirms that at
least one declared output was created or modified before proceeding to the next
eligible activity. In human sessions, `outputs` is informational only — no
enforcement, no warning for missing or unexpected outputs.

The dependency graph comes from `inputs.required` and `outputs` across all
agent definitions. No separate precondition schema or route table exists.

Skills do not appear in the precondition graph. They are tools invoked by
agents or by the human mid-session, not standalone activities. Skills gain
`inputs.context` (their reading list) but not `inputs.required`. The grilling
skill is told what to grill via its argument — the precondition evaluator
does not need to determine whether a grilling target exists. Only agents
appear in the "what can run now?" eligibility list.

### The precondition graph

The graph is implicit. It is the transitive closure of every agent's
`inputs.required` and `outputs` declarations. No explicit edge list or route
table exists.

The system answers one question:

**What can run now?** Given the artifacts on disk, which agents have their
preconditions satisfied?

The system presents eligible agents. The human picks one. No recommendation,
no ranking, no warnings about direction.

The human knows what they changed. When a grilling session finds a
specification flaw, the human fixes the artifact and runs the evaluator again.
The eligibility list reflects the new state. No automated change detection or
impact analysis is needed.

### The happy path and its absence

A typical delivery sequence — proposal, specification, architecture, stories,
implementation — emerges from the precondition chain without being declared.
The architecture agent requires an accepted proposal. The planning agent
requires concept artifacts. The developer agent requires a story or an epic.
Following the dependencies produces the familiar sequence.

The sequence is not prescribed. A developer who already knows what to build can
go from an accepted proposal to implementation if the implementation agent's
preconditions are met (boundaries and completion criteria exist). A brownfield
project can start from existing code and derive concept artifacts afterward.
The graph handles both cases because it never declared a single correct path.

### Artifact state detection

The system reads the repository and reports what exists. This requires two
layers, carried forward from the cycle proposal:

- **Mechanical validation:** file exists, passes format lint, required fields
  present. Scriptable and deterministic.
- **Semantic assessment:** "Does the code contradict the scope-map?" Requires
  LLM-based comparison. Human-triggered only (`intent assess`). No automatic
  post-activity assessment in the first release.

Both layers are informational. Neither prevents work or gates transitions
because there are no transitions to gate.

The artifact types and their validators are the same ones the cycle proposal
defined. The difference is how they are used: as precondition checks for
specific activities, not as readiness evidence for stage transitions.

### Workstreams

A workstream is one body of work — one proposal being developed, one feature
being built, one research question being investigated. Workstream identity,
session binding, and session menu integration from EPIC 1 are kept.

The workstream state file carries fewer fields. It no longer tracks a current
cycle, attempt count, or delegation grant. It contains:

```yaml
schema_version: 2
workstream_id: activity-graph-orchestration
topic: Replace stage orchestration with activity precondition graph
origin_ref: docs/proposals/activity-graph-orchestration.md
```

The `cycle`, `attempt`, `revision`, `delegation`, and `work` fields are
removed. No maintained artifact list. Concurrency control (locking, revision
checks) is kept for the workstream state file but simplified because fewer
fields change.

#### Artifact-to-workstream association

Artifacts are either workstream-scoped or global.

**Workstream-scoped artifacts** belong to one workstream and carry a
`workstream` field in their YAML frontmatter:

```yaml
workstream: activity-graph-orchestration
```

Proposals, epics, stories, and feature files are workstream-scoped. A lint
check at artifact creation time verifies the field is present and references a
known workstream identifier.

**Global artifacts** are shared across workstreams and do not carry a
`workstream` field. The architecture DSL (`architecture.dsl`), the scope map
(`scope-map.md`), and the entity model (`entity-model.yaml`) are global.

The evaluator uses the `workstream` field to narrow precondition matches when a
workstream is bound. Global artifacts are always included in precondition
evaluation regardless of the bound workstream. When an artifact in the
precondition chain is missing — a proposal and epic exist but no feature file
does — the evaluator reports unsatisfied preconditions. The graph reveals
incompleteness in the dependency chain, not workstream membership.

### Delegation

The cycle proposal defined explicit-route and destination grants to authorize
unattended execution. In the activity model, delegation means: "keep running
whatever the precondition graph makes eligible without asking."

The first release defines one delegation form:

```yaml
delegation:
  continue: true
```

A `continue` grant authorizes automatic execution while exactly one activity
has its preconditions satisfied and the previous activity completed
successfully. The system pauses when zero or multiple activities are eligible,
when an activity fails, or when an activity requires human judgment (proposal
acceptance, story shaping). The human creates, replaces, or revokes the grant.
The system cannot create, extend, or broaden it.

Delegation is session-scoped. It ends when the session ends. The next session
starts with no delegation — the human must grant it again. This prevents
auto-execution from a grant the human forgot about. No delegation field exists
in the workstream state file. The grant is stored in the session binding file
alongside the per-activity attempt counters:

```yaml
# session binding (session-scoped, dies with the session)
session_id: abc-123
bound_at: 2026-09-17T14:30:00Z
delegation:
  continue: true
attempts:
  architecture-agent: 1
  developer-agent: 0
```

The session binding file survives context compaction within a session but does
not outlive the session.

### Retry limits

Retry limits remain. Each activity (agent or skill) can declare a
`delegated_attempt_limit`. The limit prevents unattended loops. A human can
retry without limit. The mechanism is unchanged from the cycle proposal except
that the limit applies per activity rather than per cycle.

### Granular observability

#### Structured transcript retention

The usage capture pipeline reads the CLI's native structured transcript
(JSONL), tokenizes it, and writes a flattened plain-text copy. The structured
source is discarded. This proposal changes capture to retain the structured
JSONL alongside the text rendering.

Each CLI's native transcript contains tool-call records with full arguments:

| CLI         | Agent dispatch tool | Skill tool | Tool call format |
| ----------- | ------------------- | ---------- | ---------------- |
| Claude Code | `Agent`             | `Skill`    | `tool_use` block |
| Pi          | `run_agent`         | n/a        | `toolCall` block |
| Copilot     | `read_agent`        | `skill`    | event stream     |
| Codex       | `exec_command`      | n/a        | `response_item`  |

From these structured transcripts, jq or a lightweight extractor can recover:

- Every agent dispatch: type, name, description, model
- Every skill invocation: skill name, arguments
- Every file read, edit, or write: paths and operations
- Every bash command: what was run
- Tool result status: success or failure

These records form the activity log. No new instrumentation is needed at the
agent or skill level. The data is already captured. It is currently discarded.

#### Structured transcript storage

The structured copy is stored alongside the existing text rendering:

```
.agent-factory/usage/transcripts/<session-key>/
├── <record-id>.jsonl        # existing text rendering (for tokenization)
├── <record-id>.structured.jsonl  # new: native JSONL retained
```

The structured file is a verbatim copy of the source transcript the normalizer
reads. No transformation, no CLI-specific rewriting. The normalizer already
opens and parses the file. Copying it before or after normalization is a small
addition.

Storage cost is bounded by the existing transcript retention policy. When
retention is `omit`, neither file is written. When retention is `full`, both
are written. A future `structured-only` retention mode may drop the text
rendering since its only consumer (tokenization) runs at capture time and the
counts are already on the usage record.

#### Activity extraction (deferred)

The retained structured transcripts contain data for per-CLI activity
extraction — agent dispatches, skill invocations, and tool-call results. The
extractor design, common activity record format, and extraction timing
(capture-time or post-hoc) are deferred to a future proposal. The first
release retains the raw material. Extraction is built on top of it.

#### Usage record enrichment

The usage-record contract (v1) gains these optional fields, supplied by the
factory at capture time:

- `workstream_id` — which body of work this invocation served
- `workstream_origin` — the proposal or origin reference
- `skills_invoked` — list of skill names called during the session

Missing values are null and never fail capture. The factory's capture hooks
supply the context; the usage package does not import or query the factory
engine or workstream state. The current `v1.schema.json` declares
`additionalProperties: false`; the three new fields are added to the existing
v1 schema as a compatible additive update per the contract's compatibility
policy.

#### Usage analysis

Usage analysis gains these dimensions without requiring stage attribution:

- **Cost per workstream** — sum invocations by `workstream_id`
- **Cost per activity type** — group by agent name or skill name
- **Rework visibility** — the invocation sequence shows patterns: "scope map
  was edited three times, each time after a grilling call"
- **Cross-CLI comparison** — normalized activity records are CLI-agnostic

These dimensions come from the usage record fields and, for deeper analysis,
from the retained structured transcripts. No stage label is needed.

### Session menu

The current menu (A–E) is restructured into four lanes:

| Lane             | Entry point | What it does                                          |
| ---------------- | ----------- | ----------------------------------------------------- |
| **Help**         | H           | Tours, explanations, "what is [concept]?"             |
| **Housekeeping** | K           | Factory maintenance: re-fit, update, module changes   |
| **Project Work** | P           | Start or continue a workstream                        |
| **Open Stage**   | O           | Freeform conversation — no structure, no deliverables |

**Help** combines the current newcomer tour (A) and reorientation (E). It
routes to the `newcomer-tour` or `guided-tour` skill as before.

**Housekeeping** is new. The first release presents a factory state inventory
(installed version, fitting status, CLI integrations, usage pipeline health)
and lists available manual actions. It does not automate maintenance actions or
use a precondition graph. Housekeeping automation is a separate future concern.

**Project Work** subsumes the current options B (start something new) and C
(continue an existing workstream). After workstream binding, the system checks
artifact state and presents the agents whose preconditions are currently
satisfied.

**Open Stage** is the current option D. Freeform conversation with no
structure. VIRGIL routes to the appropriate skill or agent when the
conversation reaches a concrete next step.

### Folder consolidation

All factory-delivered content is consolidated under `.agent-factory/`. The
top-level `factory/` directory, the `config/` directory, and the
`.current-work/` folder are eliminated as separate roots. Only CLI-specific
directories (`.claude/`, `.pi/`, `.codex/`, `.github/`), `.gitignore`,
`.pre-commit-config.yaml`, and `.git/` remain outside.

The unified layout:

```
.agent-factory/
├── install.json                     # factory version, installed CLIs
├── checksums.json                   # per-file integrity
│
├── factory/                         # installed factory tree
│   ├── scripts/                     # dispatch scripts (run-step, etc.)
│   ├── agents/                      # agent definitions
│   ├── skills/                      # skill definitions
│   ├── rulebooks/                   # rules.md, policies
│   └── engine/                      # deterministic engine
│       └── validators/
│
├── config/                          # project configuration
│   ├── project-context.json
│   └── testing.yaml
│
├── workstreams/                     # workstream state files
│   ├── <id>.yaml
│   └── sessions/                    # session bindings (delegation, attempts)
│       └── <session-id>.yaml
│
├── checks/                          # all quality gate output
│   ├── crap-score/
│   ├── dependency-check/
│   ├── mutation-analysis/
│   └── module-graph-check/
│
├── usage/                           # usage pipeline (one concern)
│   ├── records/                     # *.jsonl usage records
│   ├── transcripts/                 # text + structured transcripts
│   ├── control/                     # capture pipeline state
│   ├── runtime/                     # capture runtime (venv)
│   ├── analysis/                    # analysis tools, sql
│   └── store.duckdb                 # query database
│
└── maintenance/                     # factory update history
    ├── user-changes/
    └── freshness-check
```

Design rationale:

- **Single root.** Everything the factory delivers lives under one dotfolder.
  The project root carries only its own files plus CLI-specific configuration.
- **`factory/` and `config/` move inward.** They are factory artifacts, not
  project artifacts. Placing them under `.agent-factory/` makes the ownership
  boundary visible in the directory tree.
- **Sessions under workstreams.** A session binding serves a workstream. Open
  Stage sessions use `workstream_id: null`. Flat session lookup:
  `workstreams/sessions/<id>.yaml`.
- **Usage consolidated.** The four `usage-*` siblings and `usage.duckdb` become
  one `usage/` folder with internal structure. Pipeline internals are hidden.
- **Checks absorb all gate output.** CRAP scores, dependency checks, mutation
  analysis, module graph checks, and premerge markers in one place.
- **`factory-` prefix dropped.** Redundant under `.agent-factory/`.
- **Dropped artifacts:** `playbook-state.yml`, `step-guard-debug.json`,
  `dispatch-ledger.yaml.bak` — obsolete under the new model. Dispatch ledgers
  for active features are kept under `workstreams/`.

All scripts, hooks, agent definitions, skill definitions, CLI index files, and
configuration that reference `factory/`, `config/`, `.current-work/`, or the
old `.agent-factory/` sub-paths are updated. The `.gitignore` is updated to
cover the new layout. The install script writes to `.agent-factory/factory/`
and `.agent-factory/config/` instead of the project root.

### Compatibility with EPIC 1

EPIC 1 implemented workstream identity, session binding, the `cycle select`
and `cycle assess` commands, menu integration, and basic delivery-model
validation. This proposal keeps:

- Workstream state files (moved to `.agent-factory/workstreams/`)
- Session bindings
- The command family (renamed from `cycle` to `intent`)
- Menu options B and C behavior
- Agent and skill identity contracts
- All deterministic checks and branch-safety commands

This proposal replaces:

| EPIC 1 artifact                  | Replacement                                         |
| -------------------------------- | --------------------------------------------------- |
| `cycle` command family           | `intent` command family                             |
| `cycle assess` route recommender | Precondition checker: what can run now?             |
| `eligible_cycles` agent metadata | `inputs.required` declarations                      |
| `delivery.yaml` route table      | Implicit graph from `inputs.required` and `outputs` |
| Cycle-state `cycle` field        | Removed; workstream tracks work references only     |
| Cycle-state `attempt` field      | Per-activity attempt tracking                       |
| Cycle-state `delegation` field   | Simplified `continue: true` delegation              |

EPICs 2–7 of the cycle proposal are not implemented and are fully superseded.

#### Engine module disposition

The EPIC 1 engine code is built around the cycle model. Replacing cycles with
preconditions requires a clean break at the engine level:

| Module                 | Disposition                                                 |
| ---------------------- | ----------------------------------------------------------- |
| `cycle_model.py`       | Delete                                                      |
| `cycles.py`            | Delete                                                      |
| `models/delivery.yaml` | Delete                                                      |
| `eligibility.py`       | Rewrite (precondition evaluator replaces cycle eligibility) |
| `readiness.py`         | Rewrite (artifact state checks replace readiness tables)    |
| `recommendations.py`   | Rewrite (eligible-activity list replaces route recommender) |
| `validators/`          | Keep (adapt to precondition condition types)                |
| `schemas/`             | Keep (adapt to new workstream state schema)                 |

"Keep EPIC 1" means keeping the workstream and session plumbing. The engine's
conceptual foundation — cycles, routes, the delivery YAML model — is replaced.

#### Engine architectural constraints

The cycle proposal established architectural constraints for the engine. These
carry forward unchanged:

- **Scripts are thin adapters.** They own CLI parsing, output formatting, exit
  codes, process lifecycle, and state-file writes. They contain no evaluation
  or decision logic.
- **The engine returns immutable decisions.** It evaluates preconditions and
  reports eligible activities. It never writes repository state.
- **Dependency direction is enforced.** Scripts may call the engine. The engine
  never imports scripts, configuration, agent definitions, or skills. A
  deterministic boundary test enforces this.
- **Trusted validator identifiers.** The `check` condition type references
  validators by name. The engine resolves the name to an executable — bash
  scripts under `factory/scripts/` (e.g. `spec-lint`) or Python validators
  under `engine/validators/` (e.g. `proposal.py`). The model never contains
  shell commands.
- **Shared validator result format.** Every validator returns: artifact type,
  artifact reference, assessed commit, individual check results, and warnings.
  The precondition evaluator interprets pass/fail from these results.
- **Installed-shape tests.** The distributed factory must contain and be able
  to execute the engine. Tests verify this.
- **Tracked source is the test surface.** `packages/factory/engine/` is the
  source of truth. Installation copies the same tree to `factory/engine/`.

#### Workstream state migration

Existing `schema_version: 1` workstream state files are deleted. This is a
clean break. The user re-creates workstreams under `schema_version: 2`. There
are three v1 files in this project. Manual recreation takes less time than
writing a migration script. No migration script is needed.

#### Dispatch and diagnostic scripts

The `run-step` skill is rewritten to call the precondition evaluator instead
of filtering agents by cycle eligibility. The `phase` diagnostic stub is
deleted — there are no cycles to diagnose.

### Sibling research graph

Research uses a sibling precondition set. A research agent requires a research
brief. The existing survey and falsification routes are unchanged.

The cycle proposal's brief fields `origin_cycle` and `return_cycle` reference
named cycles that no longer exist. These fields are removed. The precondition
graph handles routing: a research agent's output is an artifact, and any agent
that declares that artifact as a required input becomes eligible when the
research completes. No explicit origin or return field is needed.

The `decision_needed` field is unchanged.

## Scope

### In the first release

- Restructure the session menu into four lanes: Help, Housekeeping, Project
  Work, Open Stage.
- Housekeeping lane: present a factory state inventory and list of manual
  actions. No automation or precondition graph.
- Restructure agent `inputs` into `required` (artifact type, path pattern,
  conditions) and `context` (plain paths). `outputs` unchanged. Skills gain
  `inputs.context` only — they do not appear in the precondition graph.
- Implement a precondition evaluator that reads `inputs.required` declarations
  and checks them against the repository.
- Present eligible agents (those with satisfied required inputs) after
  workstream binding in the Project Work lane.
- Retain structured transcripts at capture time alongside the text rendering.
- Add `workstream_id`, `workstream_origin`, and `skills_invoked` to the usage-
  record contract as optional fields (v1 additive schema update).
- Supply workstream context from the factory's capture hooks.
- Add workstream dimension to usage analysis.
- Simplify the workstream state file: remove `cycle`, `attempt`, `revision`,
  `delegation`, and `work` fields. Retain only `workstream_id`, `topic`, and
  `origin_ref`.
- Add a `workstream` frontmatter field to all artifact types (proposals,
  epics, stories, feature files, architecture documents). Add a lint check
  at artifact creation time that verifies the field is present and references
  a known workstream identifier.
- Define a single `continue: true` delegation form.
- Keep per-activity retry limits with the same consumed-attempt semantics.
- Rename the `cycle` command family to `intent`: `intent select` and
  `intent assess`. The old `cycle` commands are removed; no alias is provided.
- Clean-break the engine: delete `cycle_model.py`, `cycles.py`, and
  `models/delivery.yaml`. Rewrite `eligibility.py`, `readiness.py`, and
  `recommendations.py`. Keep `validators/` and `schemas/` (adapted).
- Delete existing v1 workstream state files. No migration script.
- Rewrite `run-step` to use the precondition evaluator. Delete the `phase`
  diagnostic stub.
- Store session-scoped delegation grants and per-activity attempt counters in
  the session binding file.
- Keep EPIC 1 infrastructure: workstream and session plumbing, menu
  integration, deterministic checks.
- Replace `eligible_cycles` metadata and flat `inputs` lists with structured
  `inputs.required` / `inputs.context` on agent definitions. Add
  `inputs.context` to skill definitions.
- Consolidate all factory content under `.agent-factory/`. Move `factory/`
  to `.agent-factory/factory/`, `config/` to `.agent-factory/config/`.
  Eliminate `.current-work/`. Move workstream state to
  `.agent-factory/workstreams/`, session bindings to
  `.agent-factory/workstreams/sessions/`, quality gate results to
  `.agent-factory/checks/`. Update all path references in scripts, hooks,
  agent definitions, skill definitions, CLI index files, and configuration.
  Update the install script to write the new layout.
- Restructure `.agent-factory/` internals: rename `factory-install.json` →
  `install.json`, `factory-checksums.json` → `checksums.json`. Collapse
  `usage-control/`, `usage-runtime/`, `usage-analysis/`, and `usage.duckdb`
  into `usage/` subfolders (`control/`, `runtime/`, `analysis/`,
  `store.duckdb`). Move flat usage records into `usage/records/`. Move
  `factory-user-changes/` and `.freshness-check` into `maintenance/`.
- Update branching policy and git-hook enforcement: `block-dangerous-git.sh`
  worktree path allowlist, `branching-policy.md`, and `git-workflow.md`
  references from `.current-work/` to the new `.agent-factory/` layout.
- Retire `packages/orchestrator`. Delete the `packages/orchestrator/`
  directory. Remove references to the orchestrator from documentation,
  backlog stories, and CI configuration. Review existing orchestrator tests
  for any that cover behavior still needed (e.g. engine-level validation,
  workstream state handling) and migrate those tests to their new homes
  (e.g. `packages/factory/engine/`). The playbook FSM runner, `phase`
  script dependency, playbook FSM files, and linear state machine model are
  all superseded. No consumers remain under the activity-graph model.
- Supersede the cycle-based orchestration proposal.

### Explicitly deferred

- Housekeeping automation: precondition graph or drift-detection engine for
  factory state. The first release shows inventory and manual actions only.
  Housekeeping's own model is a separate future concern.
- Per-CLI activity extractors and the common activity record format. The
  first release retains structured transcripts; extraction from them is a
  separate concern.
- Git-diff-based change tracking for activity impact analysis.
- Capture-time activity extraction.
- Automated artifact-impact analysis: given that an artifact changed, surface
  which other artifacts reference it and may need reconciliation.
- `structured-only` transcript retention mode.
- Removing playbook files (they remain as reference documentation).
- Self-directed delegation beyond a human-authored `continue` grant.
- Batch identity tracking across refinement-realization loops.
- Replacing the internal survey and falsification research routes.

## Open Questions

None.

## Completion Criteria

- The session menu presents four lanes: Help, Housekeeping, Project Work, and
  Open Stage. Help routes to tour skills. Housekeeping shows a factory state
  inventory and available manual actions. Project Work starts or continues a
  workstream. Open Stage opens freeform conversation.
- Every agent definition carries structured `inputs` with `required` and
  `context` subkeys. Required entries reference artifact types, path patterns,
  and conditions. Context entries are plain paths. Neither references stage
  names. Skills carry `inputs.context` only.
- A precondition evaluator reads `inputs.required` declarations, checks them
  against the repository, and returns a list of eligible activities with
  evidence for each satisfied and unsatisfied requirement.
- After workstream binding in the Project Work lane, the session presents
  eligible activities instead of route recommendations. A human can select any
  listed activity.
- An agent whose required inputs are not fully satisfied can still be selected
  by a human. The system reports unsatisfied requirements without preventing
  selection.
- Workstream state files contain `workstream_id`, `topic`, and `origin_ref`.
  They do not contain `cycle`, `attempt`, `delegation`, or `work` fields.
- Every artifact belonging to a workstream carries a `workstream` frontmatter
  field referencing a known workstream identifier. A lint check at artifact
  creation time rejects artifacts missing the field or referencing an unknown
  identifier.
- Structured transcripts are retained at capture time for all four supported
  CLIs (Claude Code, Pi, Copilot, Codex) when transcript retention is `full`.
- The usage-record contract includes optional `workstream_id`,
  `workstream_origin`, and `skills_invoked` fields. Capture succeeds with null
  values when no workstream context exists.
- Usage analysis groups records by workstream without reading `.current-work`
  files or relying on stage labels.
- A `continue: true` delegation grant authorizes automatic execution while
  exactly one activity is eligible and the previous activity succeeded. Zero or
  multiple eligible activities pause for human direction.
- Per-activity retry limits use the same consumed-attempt semantics as the
  cycle proposal. A human can retry without limit.
- Workstream state files load, create, and update under
  `.agent-factory/workstreams/`. Fields are `workstream_id`, `topic`, and
  `origin_ref` only.
- Session bindings attach to a workstream, persist delegation grants and
  attempt counters, and tear down cleanly at session end. Path:
  `.agent-factory/workstreams/sessions/<session-id>.yaml`.
- The `intent` command family (`intent select`, `intent assess`) operates
  against the activity-graph model. `intent select` lists eligible activities
  based on precondition evaluation. `intent assess` runs validators and
  reports results per the shared result format.
- All deterministic checks (CRAP score, dependency check, mutation analysis,
  module graph check) run and write results to `.agent-factory/checks/`.
- All factory-delivered content lives under `.agent-factory/`. The project root
  contains only its own files and CLI-specific directories. The installed
  factory tree is at `.agent-factory/factory/`, project configuration at
  `.agent-factory/config/`. Neither `factory/` nor `config/` nor
  `.current-work/` exists at the project root. Workstream state files are under
  `workstreams/`, session bindings under `workstreams/sessions/`, quality gate
  results under `checks/`, and usage pipeline state under `usage/` with
  `records/`, `transcripts/`, `control/`, `runtime/`, `analysis/` subfolders.
  No script, hook, agent definition, or CLI index references `factory/`,
  `config/`, `.current-work/`, or the old `.agent-factory/` sub-paths at the
  project root.
- `packages/orchestrator/` does not exist. No documentation, backlog story,
  or CI configuration references the orchestrator. Tests that covered
  still-needed behavior have been migrated to `packages/factory/engine/` or
  the appropriate package.
- The cycle-based orchestration proposal has status `superseded`.
- A single delivery sequence (proposal through concept through implementation)
  completes successfully under the activity model without named stage
  transitions.
- Rework (fixing an upstream artifact mid-activity) requires no transition or
  state-machine update. The human edits the artifact and resumes the
  interrupted activity.

## Guiding Rule

The system tracks what exists, shows what is possible, and records what
happened. It never prescribes what comes next.

## Consult Review — 2026-09-17

Reviewer: proposal-review-agent
Reviewed commit: e50cc9dcda7473689743bd95dfce6d88edf79082

The proposal is well-structured and the grilling has resolved the design
to a level of detail that is close to planning-ready. The motivation is
clear and well-grounded. The following observations identify structural
risks and gaps that could cause planning work to stall or come back with
questions.

### 1. Boundary reference does not exist at current commit

`packages/factory/scripts/intent` is listed in `impact.boundaries` but
does not exist on disk. This is the renamed `cycle` command family — it
will be created by this proposal. The impact boundaries should reference
what exists today and will be affected: `packages/factory/scripts/cycle`.
The `intent` path is an output, not a boundary to be inspected.

### 2. Existing engine code fate is unaddressed

`packages/factory/engine/` already exists from EPIC 1 and contains:
`cycle_model.py`, `eligibility.py`, `readiness.py`,
`recommendations.py`, `cycles.py`, `models/delivery.yaml`,
`schemas/`, and `validators/`. The proposal says "EPIC 1 infrastructure
is preserved" but then replaces the core engine concepts — cycles become
activities, routes become preconditions, `delivery.yaml` becomes an
implicit graph derived from agent declarations.

The word "preserved" needs qualification. Which engine modules survive
unchanged? Which are rewritten? Which are deleted? A planner reading
"preserve EPIC 1" will assume the engine code stays and build stories
on top of it, when in reality most of the engine needs to change. The
`delivery.yaml` file in particular disappears entirely under the implicit
graph model, but the proposal never mentions its removal.

Consider adding a replacement table similar to the one in the cycle
proposal's "Compatibility with EPIC 1" section, but at the engine-module
level: what stays, what changes, what goes.

### 3. Scope item contradicts design on skill eligibility

The in-scope list says: "Present eligible activities (agents and skills
with satisfied required inputs)." The Design section says: "Only agents
appear in the 'what can run now?' eligibility list" and "Skills do not
appear in the precondition graph." Since skills have no
`inputs.required`, they would vacuously always be eligible if included in
the list. Listing them adds noise without information. The scope item
should say "agents" to match the design, or the design should explain why
skills appear in the eligibility presentation despite having no required
inputs.

### 4. Workstream state migration path is undefined

Three workstream state files exist at `schema_version: 1` with fields
`cycle`, `attempt`, `revision`, `delegation`, `work`, and
`cycle_entry_commit`. The proposal moves to `schema_version: 2` with
only `workstream_id`, `topic`, and `origin_ref`. But it does not say
what happens to the existing files. Are they migrated automatically?
Discarded? Manually re-created? A planning agent needs to know whether
this is a migration story or a clean break.

### 5. Usage record `additionalProperties: false` blocks field addition

The current `v1.schema.json` declares `"additionalProperties": false`.
Adding `workstream_id`, `workstream_origin`, and `skills_invoked` will
fail schema validation unless the schema is updated. The contract's
compatibility policy says "additive changes (new optional fields) are
compatible within the current version," but the schema as written rejects
any field not already declared. The proposal should state whether this is
a v1-additive schema update (add the fields to the existing schema) or a
v2 contract (new schema version).

### 6. Delegation storage location is unspecified

Delegation is session-scoped and dies when the session ends. The
workstream state file no longer carries a `delegation` field. But where
is the grant stored during the session? In-memory only? In the session
binding file? If in-memory only, it would not survive context compaction
or an accidental session restart within the same terminal window. The
cycle proposal stored delegation in the workstream state file, which was
persistent but created the "forgotten grant" problem the new proposal
solves. A middle ground might be the session binding file — persistent
within the session, dies with the binding — but the proposal should state
the mechanism.

### 7. Retry state persistence is unclear

The proposal says "Preserve per-activity retry limits with the same
consumed-attempt semantics" and the workstream state file retains only
`workstream_id`, `topic`, and `origin_ref`. The `attempt` field is
explicitly removed. Where is the per-activity attempt counter stored? The
retry mechanism needs a persistent counter somewhere — either the
workstream state file needs to retain an attempt-tracking structure, or
the attempt counter moves to the session binding, or a separate tracker
file is introduced. Without this decision, a planner cannot write a
retry-limit story.

### 8. Research brief fields reference named cycles that no longer exist

The scope says "Define the delivery-to-research brief fields (unchanged
from the cycle proposal)." The cycle proposal's brief fields include
`origin_cycle` (one of IDEA, CONCEPT, ROADMAP, REFINE, REALIZE) and
`return_cycle`. In the activity model, named cycles do not exist. A
research brief that says `origin_cycle: CONCEPT` has no meaning when
CONCEPT is not a named stage. Either the brief contract changes (the
fields become artifact references or activity names instead of cycle
names), or the proposal needs to say it keeps the cycle vocabulary as a
convenience label for research briefs even though cycles are not an
engine concept. "Unchanged from the cycle proposal" cannot be literally
true when the referenced vocabulary is gone.

### 9. The term "activity" lacks a precise definition

The title says "Activity-Graph Orchestration," but the design describes a
graph over agents' `inputs.required` and `outputs`. The word "activity"
appears throughout but is never formally defined. Is an activity the same
thing as an agent invocation? If so, why introduce a new term? If
activities are broader — encompassing skill invocations, manual edits,
or other work — the relationship between activities and agents needs to
be spelled out. A precondition graph over agents is clear. A precondition
graph over undefined "activities" requires the reader to guess.

### 10. `run-step` migration deserves explicit treatment

`run-step` is the primary dispatch mechanism. Today it reads the
workstream state, filters agents by `eligible_cycles`, checks outputs
against gates, and dispatches. Under the new model, it needs to call the
precondition evaluator instead of filtering by cycle eligibility. The
proposal lists `run-step` in the boundaries and mentions the `intent`
command family, but does not discuss how `run-step` itself changes. Since
`run-step` is the skill that ties the engine to agent dispatch, its
migration path is important enough to state explicitly in the Design or
Compatibility section.

### 11. `phase` script stub is unmentioned

The cycle proposal kept `factory/scripts/phase` as a diagnostic stub for
one release. The activity-graph proposal is silent on `phase`. Since
EPIC 1 is preserved and `phase` already exists as a stub, the proposal
should say whether the stub survives unchanged, is removed, or is updated
to point to `intent` instead of `cycle`.

### Disposition

All 11 findings resolved in the proposal body:

| #   | Finding                       | Resolution                                                     |
| --- | ----------------------------- | -------------------------------------------------------------- |
| 1   | Boundary reference            | Changed back to `scripts/cycle`                                |
| 2   | Engine code fate              | Engine module disposition table added                          |
| 3   | Scope vs. design on skills    | Scope item says "agents"                                       |
| 4   | Workstream migration          | Clean break: delete v1 files                                   |
| 5   | Schema `additionalProperties` | v1 additive update stated                                      |
| 6   | Delegation storage            | Session binding file                                           |
| 7   | Retry persistence             | Attempt counters in session binding                            |
| 8   | Research brief fields         | `origin_cycle` / `return_cycle` removed; graph handles routing |
| 9   | "Activity" undefined          | Terminology section added                                      |
| 10  | `run-step` migration          | Dispatch scripts section added                                 |
| 11  | `phase` stub                  | Deleted, stated in dispatch scripts section                    |

### Structural observations

The proposal makes a strong philosophical case for replacing stages with
preconditions. The core insight — that rework is invisible to a
dependency graph because a dependency graph never declared a forward
direction — is sound and well-articulated.

The main structural risk is that the proposal treats the engine as
mostly new while also claiming to preserve EPIC 1. In practice, the
EPIC 1 engine code is built around cycles, routes, and the delivery YAML
model. Preserving the workstream/session plumbing while replacing the
engine's conceptual foundation is closer to a rewrite than a
modification. Being explicit about this will help the planner estimate
accurately and avoid stories that assume surviving code where none
exists.

The observability design (structured transcript preservation, usage
record enrichment) is well-scoped and separable. It could be planned and
implemented independently of the precondition-graph work. Consider
whether the proposal should note this separability, since it enables
parallel work and reduces risk — the observability stories deliver value
even if the precondition evaluator takes longer than expected.

## Review — 2026-09-17

Reviewer: proposal-review-agent
Reviewed commit: b684671f4b5bd2960f026535cf687b5feb0015f2
Disposition: findings

### Findings

| ID      | Severity | Check | Status    | Finding                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                    |
| ------- | -------- | ----- | --------- | ---------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| PROP-01 | major    | 02    | resolved  | Design describes "what just broke?" as half of the core model (lines 209-231) but Scope defers it under "Automated dependency impact analysis" without flagging the gap in the Design section. A planner reading the Design would scope stories for both questions. **Resolution:** "What just broke?" removed from Design. Deferred item reworded to "Automated artifact-impact analysis."                                                                                                                                                                |
| PROP-02 | major    | 02    | resolved  | `.agent-factory/` internal restructuring has no Scope item. The current layout (`factory-install.json`, `factory-checksums.json`, four `usage-*` siblings, flat usage records in `usage/`) differs from the Design layout (`install.json`, `checksums.json`, `usage/records/`, `usage/control/`, etc.). Completion Criteria describe the target state but no scope item covers the migration from current to target. **Resolution:** Separate scope item added for `.agent-factory/` internal restructuring.                                               |
| PROP-03 | major    | 02    | resolved  | Folder consolidation changes the branching policy. `block-dangerous-git.sh` hardcodes `.current-work/*` as the sole allowed worktree path (lines 91-108). `branching-policy.md` and `git-workflow.md` prescribe `.current-work/` as the worktree root. Changing the folder name changes the project's branching and safety enforcement model. The scope buries this under "Update all path references" rather than acknowledging it as a distinct concern. **Resolution:** Separate scope item added for branching policy and git-hook enforcement update. |
| PROP-04 | major    | 05    | resolved  | `packages/orchestrator` is not in the boundary list but has 30+ `.current-work/` references including hardcoded paths in source code (`cli.py` lines 27-28), the PRD, demo script, README, backlog stories, and supplementary specs. It is a separate package from `packages/factory` and is not covered by any listed boundary. **Resolution:** `packages/orchestrator` retired wholesale. Scope item added.                                                                                                                                              |
| PROP-05 | minor    | 03    | resolved  | The `check` condition type says named validators are "the same scripts the factory already runs" but the codebase has two validator forms: Python classes in `engine/validators/` (e.g. `proposal.py`) and bash scripts in `factory/scripts/` (e.g. `spec-lint`). The design does not specify how the evaluator resolves a validator name to an executable or what interface it expects. **Resolution:** Engine architectural constraints section added. Validator resolution specified.                                                                   |
| PROP-06 | minor    | 01    | resolved  | "EPIC 1 infrastructure remains functional" groups four capabilities (state files, session bindings, intent commands, deterministic checks) into one assertion. Each should be a separately testable criterion, or the single criterion should enumerate what "functional" means for each. **Resolution:** Split into four separate completion criteria.                                                                                                                                                                                                    |
| PROP-07 | minor    | 02    | resolved  | Scope says "replace `origin_cycle` and `return_cycle` with `origin_artifact` and `return_artifact`" but neither field exists in the current research brief schema (`research-brief.schema.json`) or template. EPICs 2-7 where these would have been added were never implemented. The scope item should say "add" not "replace." **Resolution:** Scope item dropped. The precondition graph handles routing; no explicit origin/return fields needed.                                                                                                      |
| PROP-08 | minor    | 08    | no change | All estimate fields are `unknown` for a scope with countable units: 17 agent definition restructurings, 6 engine module rewrites/deletes, 150+ `.current-work/` path references, two folder migrations, new evaluator, and contract changes. While `unknown` is permitted by policy, even a rough token range would provide planning signal. **Resolution:** Estimates stay `unknown` per policy.                                                                                                                                                          |

### Summary

The proposal's conceptual model is sound and the motivation is well-grounded. Five of eight checks pass. The three failures center on one theme: the folder consolidation is larger and more consequential than the proposal acknowledges. It encompasses two distinct migrations (`.current-work/` elimination and `.agent-factory/` internal restructuring), changes the project's branching policy and git-hook enforcement model, and reaches into a sibling package (`packages/orchestrator`) that is not in the boundary list. These omissions would cause a planning agent to underscope the folder consolidation work and miss the orchestrator package entirely. The Design section's presentation of "what just broke?" alongside "what can run now?" as a pair would lead a planner to include both in scope when only the first is intended. Address the four major findings before this proposal is ready to plan from.

## Review — 2026-09-17 (pass 3)

Reviewer: proposal-review-agent
Reviewed content: working tree (uncommitted changes on 41dfd301d15e2846cbc0a5cf7fe867dce55d1027)
Disposition: findings (minor only)

### Prior findings

| ID      | Severity | Check | Status    | Verification                                                                                                                            |
| ------- | -------- | ----- | --------- | --------------------------------------------------------------------------------------------------------------------------------------- |
| PROP-01 | major    | 02    | resolved  | "What just broke?" removed from Design. Deferred item reworded to "Automated artifact-impact analysis." Confirmed in working tree.      |
| PROP-02 | major    | 02    | resolved  | Separate scope item for `.agent-factory/` internal restructuring at line 666. Confirmed.                                                |
| PROP-03 | major    | 02    | resolved  | Separate scope item for branching policy and git-hook enforcement at line 672. Confirmed.                                               |
| PROP-04 | major    | 05    | resolved  | `packages/orchestrator` retirement in scope at line 675. Confirmed on disk.                                                             |
| PROP-05 | minor    | 03    | resolved  | Engine architectural constraints section at lines 568-591. Validator resolution specified. Confirmed.                                   |
| PROP-06 | minor    | 01    | resolved  | Split into four separate completion criteria (workstream state, session bindings, intent commands, deterministic checks). Confirmed.    |
| PROP-07 | minor    | 02    | resolved  | Scope item dropped. Research brief routing handled by precondition graph. `origin_cycle`/`return_cycle` removed at line 612. Confirmed. |
| PROP-08 | minor    | 08    | no change | All estimate fields remain `unknown`. Accepted per policy.                                                                              |

### New findings

| ID      | Severity | Check | Status | Finding                                                                                                                                                                                                                                                                                                                                                                                          |
| ------- | -------- | ----- | ------ | ------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------ |
| PROP-09 | minor    | 02    | open   | Scope lists four `intent` commands (`select`, `assess`, `status`, `delegate`) at line 643 but completion criteria at line 742 specify behavior for `select` and `assess` only. The `intent status` output content and the `intent delegate` command interface have no testable endpoint in the proposal. A planner cannot write acceptance tests for these two commands from the criteria alone. |
| PROP-10 | minor    | 02    | open   | `packages/orchestrator` retirement is in scope (line 675) but has no matching completion criterion. "Retire" is ambiguous without a verifiable endpoint: delete the directory, remove from CI, mark deprecated, or some combination.                                                                                                                                                             |
| PROP-11 | minor    | 01    | open   | Completion criterion 6 (line 721) contains "Workstream scope is derived from the dependency graph" — a design mechanism description, not a testable assertion. The field-presence checks in the same criterion are testable; this sentence is not.                                                                                                                                               |
| PROP-12 | minor    | 03    | open   | Design line 196 says the dependency graph comes from "agent and skill definitions" but lines 200-205 exclude skills from the graph and line 209 restricts the computation to "every agent's" declarations. A planner reading line 196 alone would incorrectly include skill outputs in the graph.                                                                                                |

### Check results

| #   | Check                            | Result                                                           |
| --- | -------------------------------- | ---------------------------------------------------------------- |
| 1   | Completion criteria testable     | Pass — one minor untestable clause (PROP-11)                     |
| 2   | Scope boundary sharp             | Pass — two scope items lack matching criteria (PROP-09, PROP-10) |
| 3   | Design decomposable              | Pass — one wording inconsistency (PROP-12)                       |
| 4   | Impact classification consistent | Pass                                                             |
| 5   | Boundary references exist        | Pass — all 10 paths resolve                                      |
| 6   | Open questions genuine           | Pass — "None" appropriate after two prior passes                 |
| 7   | Motivation justifies timing      | Pass                                                             |
| 8   | Estimate plausible               | Pass — `unknown` accepted per PROP-08                            |

### Summary

All eight checks pass at the major level. Four minor findings remain: two scope-criteria alignment gaps where in-scope commands and a retirement action lack testable completion criteria (PROP-09, PROP-10), one untestable mechanism clause embedded in a completion criterion (PROP-11), and one wording inconsistency between a paragraph and its surrounding context in the Design section (PROP-12). The four prior major findings are verified resolved. The quality-gate rewrite improved prose clarity without introducing structural problems. The proposal is planning-ready; addressing these minor findings would sharpen precision but does not block story decomposition.
