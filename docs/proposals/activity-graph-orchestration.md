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
next given the current repository state. There are no named stages, no
transition matrix, and no state machine. The happy path emerges from the
dependency chain. Rework is just going to fix the artifact that broke.

Granular observability replaces stage-attributed usage. The factory preserves
structured transcripts and enriches usage records with workstream, skill, and
activity context at capture time.

## Motivation

The cycle-based orchestration proposal (2026-09-13) replaced the linear
playbook model with a five-cycle directed graph. That graph is less rigid than
a pipeline, but it is still prescriptive. Five named stages, eighteen declared
routes, per-artifact readiness tables, and a recommendation engine exert strong
gravitational pull on the human's choices. "You may select any cycle" is
formally true and practically unlikely when the system shows green checks on
one route and warnings on everything else.

The deeper problem surfaced in practice: a story grilling session discovers a
concept-level flaw. The real move is to pause grilling, fix the specification
or rethink the premise, and return. But the stage model frames this as a
full-cycle transition — REFINE back to CONCEPT — with reconciliation evidence
and recommendation checks. It is heavyweight ceremony for what should be "this
assumption is wrong, let me fix it upstream."

The stage model describes the wrong unit. Real work does not move between
stages. It moves between an activity and the thing that activity just
invalidated, at whatever granularity the invalidation happens. Sometimes that
is "the whole proposal is wrong." Sometimes it is "this one entity definition
is missing a field." A stage model treats both as the same kind of event.

Stages also imply doneness. "CONCEPT is done" means "we stopped finding
problems with the concept," not "the concept is correct." The next downstream
activity will test upstream assumptions again whether the model accounts for it
or not. When the model says you are "in REFINE," concept work reads as going
backward. But what actually happened is the grilling worked — it found
something. That is success, not regression.

The cycle-based orchestration proposal's EPIC 1 (workstream identity, session
binding, menu integration, basic assessment) is implemented and working. This
proposal preserves that infrastructure and replaces the stage-transition model
that EPICs 2–7 would have built.

The timing follows the same drivers as the cycle proposal: the 2026-09-09
user-experience review, the opportunity before further stage-model investment,
and the need for concurrent workstream attribution.

## Core Principles

- The human drives. The system shows what is possible. The human chooses what
  to do. No recommendation engine ranks choices or presents warnings that
  discourage legitimate work.
- Artifacts are the ground truth. "What exists and what shape is it in?"
  replaces "which stage are you in?"
- Activities have preconditions, not phase assignments. An agent or skill
  declares what must exist before it can run. The system checks those
  preconditions against the repository. No named stage is involved.
- Rework is invisible to the model. Fixing an upstream artifact is just fixing
  an artifact. No transition, no ceremony, no "returning to an earlier stage."
  The dependency graph absorbs rework naturally because it never declared a
  forward direction.
- Observability comes from what actually happened, not from what stage it was
  attributed to. Agent invocations, skill calls, files touched, and timestamps
  are the activity record.
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
agent and skill definitions. No separate precondition schema or route table
exists.

Skills do not appear in the precondition graph. They are tools invoked by
agents or by the human mid-session, not standalone activities. Skills gain
`inputs.context` (their reading list) but not `inputs.required`. The grilling
skill is told what to grill via its argument — the precondition evaluator
does not need to determine whether a grilling target exists. Only agents
appear in the "what can run now?" eligibility list.

### The precondition graph

The graph is implicit: it is the transitive closure of every agent's
`inputs.required` and `outputs` declarations. No explicit edge list or route
table exists.

The system answers two questions:

1. **What can run now?** Given the artifacts on disk, which agents have their
   preconditions satisfied?
2. **What just broke?** Given that an artifact changed, which downstream
   artifacts or activities depend on it?

The first question drives the "what next?" interaction. The system presents
the agents whose preconditions are met. The human picks one. No
recommendation, no ranking, no warnings about "going backward."

The second question drives the interrupt flow. When a grilling session
discovers a specification flaw, the system can show: "the scope map was
modified; these artifacts reference it: architecture.dsl, entity-model.yaml,
these feature files." The human decides what needs updating. No stage
transition is involved.

### The happy path and its absence

A typical delivery sequence — proposal, specification, architecture, stories,
implementation — emerges from the precondition chain without being declared.
The architecture agent requires an accepted proposal. The planning agent
requires concept artifacts. The developer agent requires a story or an epic.
Follow the dependencies and you get the familiar sequence.

But the sequence is not prescribed. A developer who already knows what to
build can go from an accepted proposal straight to implementation, provided
the implementation agent's preconditions are met (the proposal has boundaries
and completion criteria). A brownfield project can start from existing code
and reverse-engineer concept artifacts. The graph accommodates both without
special cases because it never declared a single correct path.

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

A workstream remains one body of work — one proposal being developed, one
feature being built, one research question being investigated. Workstream
identity, session binding, and the session menu integration from EPIC 1 are
preserved.

The workstream state file simplifies. It no longer tracks a current cycle,
attempt count, or delegation grant. It tracks:

```yaml
schema_version: 2
workstream_id: activity-graph-orchestration
topic: Replace stage orchestration with activity precondition graph
origin_ref: docs/proposals/activity-graph-orchestration.md
```

The `cycle`, `attempt`, `revision`, `delegation`, and `work` fields are
removed. Workstream scope is derived from the dependency graph: the
precondition evaluator traces which artifacts are reachable from the
workstream's `origin_ref` through `inputs.required` and `outputs`
declarations. No maintained artifact list. Concurrency control (locking,
revision checks) is retained for the workstream state file but simplified
since fewer fields change.

### Delegation

The cycle proposal defined explicit-route and destination grants to authorize
unattended execution. In the activity model, delegation becomes: "keep doing
whatever the precondition graph makes possible without asking."

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

Delegation is session-scoped. It dies when the session ends. The next session
starts with no standing delegation — the human must grant it again. This
prevents surprise auto-execution from a grant the human forgot about. No
delegation field exists in the workstream state file. The grant is stored in
the session binding file alongside the per-activity attempt counters:

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

This is persistent enough to survive context compaction within a session but
does not outlive the session binding.

### Retry limits

Retry limits remain. Each activity (agent or skill) can declare a
`delegated_attempt_limit`. The limit prevents unattended loops. A human can
always retry without limit or ceremony. The mechanism is unchanged from the
cycle proposal except that it is per-activity rather than per-cycle.

### Granular observability

#### Preserving structured transcripts

The usage capture pipeline currently reads the CLI's native structured
transcript (JSONL), tokenizes it, and writes a flattened plain-text copy. The
structured source is discarded. This proposal changes capture to preserve the
structured JSONL alongside the text rendering.

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

This is the activity log. No new instrumentation is needed at the agent or
skill level. The data is already captured; it is currently thrown away.

#### Structured transcript storage

The structured copy is stored alongside the existing text rendering:

```
.agent-factory/usage/transcripts/<session-key>/
├── <record-id>.jsonl        # existing text rendering (for tokenization)
├── <record-id>.structured.jsonl  # new: native JSONL preserved
```

The structured file is a verbatim copy of the source transcript the normalizer
read. No transformation, no CLI-specific rewriting. The normalizer already
opens and parses this file; copying it before or after normalization is
trivial.

Storage cost is bounded by the existing transcript retention policy. When
retention is `omit`, neither file is written. When retention is `full`, both
are written. A future `structured-only` retention mode may drop the text
rendering since its only consumer (tokenization) runs at capture time and the
counts are already on the usage record.

#### Activity extraction (deferred)

The preserved structured transcripts contain sufficient data for per-CLI
activity extraction — agent dispatches, skill invocations, and tool-call
results. The extractor design, common activity record format, and extraction
timing (capture-time vs. post-hoc) are deferred to a future proposal. The
first release preserves the raw material; extraction is built on top of it.

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
- **Rework visibility** — the sequence of invocations tells the story: "scope
  map was edited three times, each time after a grilling call"
- **Cross-CLI comparison** — normalized activity records are CLI-agnostic

These dimensions come from the usage record fields and, for deeper analysis,
from the preserved structured transcripts. No stage label is needed.

### Session menu

The current menu (A–E) is restructured into four lanes that reflect what a
human actually comes to do:

| Lane             | Entry point | What it does                                          |
| ---------------- | ----------- | ----------------------------------------------------- |
| **Help**         | H           | Tours, explanations, "what is [concept]?"             |
| **Housekeeping** | K           | Factory maintenance: re-fit, update, module changes   |
| **Project Work** | P           | Start or continue a workstream                        |
| **Open Stage**   | O           | Freeform conversation — no structure, no deliverables |

**Help** combines the current newcomer tour (A) and reorientation (E). It
routes to the `newcomer-tour` or `guided-tour` skill as before.

**Housekeeping** is new. The first release presents a brief inventory of
factory state (installed version, fitting status, CLI integrations, usage
pipeline health) and lists what the human can do manually. It does not yet
automate maintenance actions or use a precondition graph. That is a separate
future concern with its own model.

**Project Work** subsumes the current options B (start something new) and C
(continue an existing workstream). After workstream binding, the system checks
artifact state and presents the agents whose preconditions are currently
satisfied.

**Open Stage** is the current option D. VIRGIL's resting state — follow the
conversation wherever it leads, route to the right next step when the idea
finds its shape.

### Folder consolidation

All factory runtime state is consolidated under `.agent-factory/`. The
`.current-work/` folder is eliminated. The unified layout:

```
.agent-factory/
├── install.json                     # factory version, installed CLIs
├── checksums.json                   # per-file integrity
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

- **Six top-level entries.** Each is a named concern. `ls .agent-factory/`
  tells the full story.
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
  for active features are preserved under `workstreams/`.

All scripts and hooks that reference `.current-work/` or the old
`.agent-factory/` sub-paths are updated. The `.gitignore` is updated to
cover the new layout.

### Compatibility with EPIC 1

EPIC 1 implemented workstream identity, session binding, the `cycle select`
and `cycle assess` commands, menu integration, and basic delivery-model
validation. This proposal preserves:

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

"Preserve EPIC 1" means preserving the workstream and session plumbing. The
engine's conceptual foundation — cycles, routes, the delivery YAML model — is
replaced.

#### Workstream state migration

Existing `schema_version: 1` workstream state files are deleted. This is a
clean break. The user re-creates workstreams under `schema_version: 2`. There
are three v1 files in this project; manual recreation is trivial. No
migration script is needed.

#### Dispatch and diagnostic scripts

The `run-step` skill is rewritten to call the precondition evaluator instead
of filtering agents by cycle eligibility. The `phase` diagnostic stub is
deleted — there are no cycles to diagnose.

### Sibling research graph

Research uses a sibling precondition set. A research agent requires a research
brief. The existing survey and falsification routes are unchanged.

The cycle proposal's brief fields `origin_cycle` and `return_cycle` reference
named cycles that no longer exist. They are replaced with artifact references:

- `origin_artifact` — the artifact path that triggered the research question
- `return_artifact` — the artifact path where the research result will be
  consumed
- `decision_needed` — unchanged

This makes the brief concrete (paths to real files) instead of abstract
(cycle names).

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
- Preserve structured transcripts at capture time alongside the text rendering.
- Add `workstream_id`, `workstream_origin`, and `skills_invoked` to the usage-
  record contract as optional fields (v1 additive schema update).
- Supply workstream context from the factory's capture hooks.
- Add workstream dimension to usage analysis.
- Simplify the workstream state file: remove `cycle`, `attempt`, `revision`,
  `delegation`, and `work` fields. Retain only `workstream_id`, `topic`, and
  `origin_ref`.
- Define a single `continue: true` delegation form.
- Preserve per-activity retry limits with the same consumed-attempt semantics.
- Rename the `cycle` command family to `intent`: `intent select`, `intent assess`, `intent status`, `intent delegate`. The old `cycle` commands are
  removed; no alias is provided.
- Clean-break the engine: delete `cycle_model.py`, `cycles.py`, and
  `models/delivery.yaml`. Rewrite `eligibility.py`, `readiness.py`, and
  `recommendations.py`. Keep `validators/` and `schemas/` (adapted).
- Delete existing v1 workstream state files. No migration script.
- Rewrite `run-step` to use the precondition evaluator. Delete the `phase`
  diagnostic stub.
- Store session-scoped delegation grants and per-activity attempt counters in
  the session binding file.
- Keep EPIC 1 infrastructure: workstream/session plumbing, menu integration,
  deterministic checks.
- Replace `eligible_cycles` metadata and flat `inputs` lists with structured
  `inputs.required` / `inputs.context` on agent definitions. Add
  `inputs.context` to skill definitions.
- Update delivery-to-research brief fields: replace `origin_cycle` and
  `return_cycle` with `origin_artifact` and `return_artifact`.
- Consolidate all factory runtime state under `.agent-factory/`. Eliminate
  `.current-work/`. Move workstream state to `workstreams/`, session bindings
  to `workstreams/sessions/`, quality gate results to `checks/`, usage
  pipeline internals into `usage/` subfolders. Update all path references in
  scripts, hooks, and configuration.
- Supersede the cycle-based orchestration proposal.

### Explicitly deferred

- Housekeeping automation: precondition graph or drift-detection engine for
  factory state. The first release shows inventory and manual actions only.
  Housekeeping's own model is a separate future concern.
- Per-CLI activity extractors and the common activity record format. The
  first release preserves structured transcripts; extraction from them is a
  separate concern.
- Git-diff-based change tracking for activity impact analysis.
- Capture-time activity extraction.
- Automated dependency impact analysis ("this artifact changed; these
  downstream artifacts may be affected").
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
  Workstream scope is derived from the dependency graph.
- Structured transcripts are preserved at capture time for all four supported
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
  cycle proposal. A human can retry without limit or ceremony.
- EPIC 1 infrastructure remains functional: workstream state files, session
  bindings, the `intent` command family, and all deterministic checks.
- All factory runtime state lives under `.agent-factory/`. The `.current-work/`
  folder does not exist. Workstream state files are under `workstreams/`,
  session bindings under `workstreams/sessions/`, quality gate results under
  `checks/`, and usage pipeline state under `usage/` with `records/`,
  `transcripts/`, `control/`, `runtime/`, `analysis/` subfolders. No script
  or hook references `.current-work/` or the old `.agent-factory/` sub-paths.
- The cycle-based orchestration proposal has status `superseded`.
- A single delivery sequence (proposal through concept through implementation)
  completes successfully under the activity model without named stage
  transitions.
- Rework (fixing an upstream artifact mid-activity) requires no transition,
  ceremony, or state-machine update. The human edits the artifact and resumes
  the interrupted activity.

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

| #   | Finding                       | Resolution                                               |
| --- | ----------------------------- | -------------------------------------------------------- |
| 1   | Boundary reference            | Changed back to `scripts/cycle`                          |
| 2   | Engine code fate              | Engine module disposition table added                    |
| 3   | Scope vs. design on skills    | Scope item says "agents"                                 |
| 4   | Workstream migration          | Clean break: delete v1 files                             |
| 5   | Schema `additionalProperties` | v1 additive update stated                                |
| 6   | Delegation storage            | Session binding file                                     |
| 7   | Retry persistence             | Attempt counters in session binding                      |
| 8   | Research brief fields         | `origin_artifact` / `return_artifact` replace cycle refs |
| 9   | "Activity" undefined          | Terminology section added                                |
| 10  | `run-step` migration          | Dispatch scripts section added                           |
| 11  | `phase` stub                  | Deleted, stated in dispatch scripts section              |

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
