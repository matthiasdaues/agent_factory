---
scope: global
schema_version: 2
status: accepted
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
    - packages/orchestrator
    - .agent-factory
    - .current-work
    - docs/proposals/cycle-based-orchestration.md
    - docs/
    - backlog/
    - .pre-commit-config.yaml
    - .gitignore

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
Agents declare their prerequisites. The system shows what can run next given
the current repository state. No named stages, no transition matrix,
no state machine. The sequence emerges from the dependency chain. Rework means
fixing the artifact that needs fixing.

The factory retains structured transcripts at capture time. Usage record
enrichment with workstream and activity context is deferred.

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
- Activities have preconditions, not phase assignments. An agent declares what
  must exist before it can run. The system checks those preconditions against
  the repository. No named stage is involved.
- Rework is invisible to the model. Fixing an upstream artifact is fixing an
  artifact. No transition, no ceremony, no "returning to an earlier stage."
  The dependency graph has no forward direction to violate.
- Observability comes from what happened, not from stage attribution. Agent
  invocations, skill calls, files touched, and timestamps are the activity
  record.
- The factory retains structured transcripts at capture time. Usage record
  enrichment is a separate concern addressed after the activity graph is in
  place.

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
  minimum_changed: 2
  declarations:
    - path_pattern: docs/arc42/architecture.dsl
      validator: arch-lint
      required: true
    - path_pattern: docs/arc42/*.md
      validator: arch-lint
      required: true
    - path_pattern: docs/adr/*.md
      validator: arch-lint
      required: false
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

A `path_pattern` like `"docs/proposals/{name}.md"` contains placeholders.
The evaluator resolves a pattern in four steps:

1. **Glob expansion.** Replace each placeholder with `*` and expand against
   the filesystem. Every matching file is a candidate.
2. **Scope filtering.** When a workstream is bound, keep only candidates whose
   `scope` frontmatter matches the bound workstream identifier or equals
   `global`. Without a bound workstream (Open Stage), skip this step.
3. **Condition checking.** Evaluate all `conditions` entries against each
   surviving candidate. Remove candidates that fail any condition.
4. **Cardinality.**
   - **Zero survivors** — the precondition is unsatisfied.
   - **One survivor** — the precondition is satisfied against that artifact.
   - **Multiple survivors** — the evaluator reports all. The human picks one.
     For external chaining, an orchestrator must supply one of the reported
     artifact references before dispatching the agent; without an explicit
     selection, it stops for human direction.

No maintained artifact list is needed. The `scope` field and the filesystem
are the only inputs.

`inputs.context` lists everything else the agent reads when running — material
it consumes if available, not gates on eligibility. `outputs.minimum_changed`
declares how many output declarations must have a created or modified match for
the activity. Each `outputs.declarations` entry declares a `path_pattern`, a
trusted `validator` identifier, and whether that specific output is `required`
for every invocation. Agent definitions with a missing `minimum_changed`,
validator, or required flag are invalid. `minimum_changed: 0` permits a
legitimate no-output activity; conditional and mode-exclusive outputs use
`required: false` with a positive minimum when at least one must change.

`outputs` is declarative for graph building: the evaluator uses it to compute
which activities become possible after a given agent runs. The deterministic
fence runs against declared outputs after each activity. For external
orchestrators, the fence result determines whether chaining proceeds. In human
sessions, the fence result is informational — no enforcement, no warning for
missing or unexpected outputs.

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

The system presents all agents and reports whether each required input is
satisfied, with evidence. The human picks any agent. No recommendation, no
ranking, no hiding of options.

The human knows what they changed. When a grilling session finds a
specification flaw, the human fixes the artifact and runs the evaluator again.
The requirement evidence reflects the new state. No automated change detection
or impact analysis is needed.

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
cycle or attempt count. It contains:

```yaml
schema_version: 2
workstream_id: activity-graph-orchestration
topic: Replace stage orchestration with activity precondition graph
origin_ref: docs/proposals/activity-graph-orchestration.md
```

The `cycle`, `attempt`, `revision`, `delegation`, and `work` fields are
removed. No delegation or attempt-tracking fields exist in workstream state
or session bindings. No maintained artifact list. The workstream state file is written at
creation and is immutable. Multiple sessions may bind to the same workstream.
The first release provides no workstream-level concurrency exclusion; branch,
worktree, and artifact-write rules remain responsible for preventing
conflicting changes.

#### Artifact-to-workstream association

Every graph-addressable artifact carries a `scope` declaration. The
first-release governed set is proposals, epics, stories, Gherkin feature files,
`architecture.dsl`, `scope-map.md`, and `entity-model.yaml`. Other artifacts do
not require a `scope` declaration. Adding an artifact type to the precondition
registry also requires defining its scope representation and lint rule. The
value is either `global` or a workstream identifier. The representation depends
on the artifact format:

**YAML frontmatter** (epics, stories, `scope-map.md`):

```yaml
---
scope: activity-graph-orchestration
---
```

**Proposals** use `scope` in place of `title`. The proposal filename already
carries the workstream identity, and the display name lives in the document
heading. The `scope` field replaces `title` rather than adding a field:

```yaml
---
schema_version: 2
scope: activity-graph-orchestration
status: accepted
owner: Matthias Daues
---
```

The proposal template is updated as part of the implementation.

**Top-level YAML field** (`entity-model.yaml`):

```yaml
scope: global
```

**First-line comment** (formats without YAML frontmatter):

```gherkin
# scope: activity-graph-orchestration
Feature: Story slicing
```

```dsl
// scope: global
workspace {
```

The evaluator reads `scope` from YAML frontmatter when present, otherwise from
a `scope:` declaration on the first line of the file. The comment prefix (`#`,
`//`) is format-dependent.

Proposals carry the workstream identifier in `scope`, which replaces `title` in
their frontmatter. Epics and stories carry the workstream identifier in `scope`
alongside their other frontmatter fields. The architecture DSL
(`architecture.dsl`), the scope map (`scope-map.md`), and the entity model
(`entity-model.yaml`) carry `global`. Feature files carry the workstream
identifier of the workstream they belong to. A lint check at artifact creation
time verifies the declaration is present and carries either `global` or a known
workstream identifier.

The evaluator uses the `scope` field to narrow precondition matches when a
workstream is bound. Artifacts with `scope: global` are always included in
precondition evaluation. When an artifact in the precondition chain is
missing — a proposal and epic exist but no feature file does — the evaluator
reports unsatisfied preconditions. The graph reveals incompleteness in the
dependency chain, not workstream membership.

### Deterministic fencing

Every agent activity is bookended by deterministic checks. The precondition
evaluator checks inputs before an activity. The runner snapshots the agent's
declared output patterns before invocation and runs the validator named by each
output declaration against files created or modified by the activity.

A required output with no created or modified match fails the fence. An
optional output with no match is skipped; if it changed, its validator runs.
The fence fails when fewer than `minimum_changed` declarations have a created
or modified match. When one declaration matches several changed files, its
validator receives the resolved file list in one invocation. When several
declarations match, all applicable validators run. The aggregate fence passes
only when every required output changed, the minimum was met, and every invoked
validator passed.

Each validator returns the shared structured result format. The runner returns
the aggregate result to its caller and stores the per-output and aggregate
evidence at
`.agent-factory/checks/fences/<session-id>/<invocation-id>.yaml`. A passing
output becomes available as satisfied evidence for downstream preconditions.
A failing output carries unsatisfied evidence. Neither outcome blocks human
action. Validator selection comes only from the invoked agent's output
declarations; there is no central artifact-type-to-validator registry.

Delegation is not an engine concept. When every activity is delimited by
deterministic fences, chaining happens from the outside. An external
orchestrator (the implementation-agent dispatcher, a script, or the human)
inspects the evaluator evidence after each fence. If exactly one downstream
agent has all preconditions satisfied, every multiple-match input has an
explicit artifact selection, and the fence passed, the orchestrator dispatches
it. If zero or multiple agents are eligible, an input selection is missing, or
the fence failed, the orchestrator pauses for human direction.

No delegation grant, no `delegated_attempt_limit`, and no attempt counter
exist in the engine, in agent definitions, or in session bindings. Retry logic
belongs to the external orchestrator. The engine reports what can run now and
whether the last fence passed. That is all.

The session binding file carries session identity and its workstream reference:

```yaml
# session binding (session-scoped, dies with the session)
session_id: abc-123
workstream_id: activity-graph-orchestration
bound_at: 2026-09-17T14:30:00Z
```

The `workstream_id` key must be present. A missing key makes the binding
invalid. A known workstream identifier means the session is bound; an explicit
`workstream_id: null` means Open Stage. Validation checks key presence rather
than using a lookup that treats missing and null as equivalent. Selecting a
different workstream updates `workstream_id` and `bound_at`; no workstream state
file is modified.

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
| **Housekeeping** | K           | Factory state, re-fit, update, agent-context guidance |
| **Project Work** | P           | Start or continue a workstream                        |
| **Open Stage**   | O           | Freeform conversation — no structure, no deliverables |

**Help** combines the current newcomer tour (A) and reorientation (E). It
routes to the `newcomer-tour` or `guided-tour` skill as before.

**Housekeeping** is new. It opens with a read-only **About** section that shows
the installed Factory version, fitting status, configured CLI integrations,
and usage pipeline health. A value that cannot be read is shown as `unknown`
with its source error; it is not omitted. The About section is followed by
exactly three manual actions. Housekeeping does not use a precondition graph:

1. **Re-fit** reruns the complete five-step fitting procedure. It reports the
   resulting completed and remaining fitting steps.
2. **Update Factory** runs
   `.agent-factory/factory/scripts/init-factory --update <project-root> --force`, relays its output and exit status, and refreshes the inventory
   after success.
3. **Update agent context** invokes `capture-context --update --scan`. The new
   mode scans the repository and documentation, compares the discovered
   concerns and `Read:` paths with the existing `docs/agent-context.md`, and
   presents proposed changes interactively. It preserves existing content
   unless the user confirms a change, writes only after confirmation, and runs
   `.agent-factory/factory/scripts/concern-lint` after writing.

Automated maintenance recommendations and additional actions are separate
future concerns.

**Project Work** subsumes the current options B (start something new) and C
(continue an existing workstream). After workstream binding, the system checks
artifact state and presents all agents with their precondition status. The
human selects any agent.

**Open Stage** is the current option D. Freeform conversation with no
structure. VIRGIL routes to the appropriate skill or agent when the
conversation reaches a concrete next step.

### Folder consolidation

All factory-delivered content is consolidated under `.agent-factory/`. The
top-level `.agent-factory/factory/` and `config/` directories are eliminated as separate
roots. `.current-work/` remains the runtime root for linked worktrees, dispatch
ledgers, and verification markers; it is not factory-delivered content.
CLI-specific directories (`.claude/`, `.pi/`, `.codex/`, `.github/`),
`.gitignore`, `.pre-commit-config.yaml`, and `.git/` also remain outside.

The unified layout:

```
.agent-factory/
├── install.json                     # factory version, installed CLIs
├── checksums.json                   # per-file integrity
│
├── .agent-factory/factory/                         # installed factory tree
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
│   └── sessions/                    # session bindings
│       └── <session-id>.yaml
│
├── checks/                          # all quality gate output
│   ├── fences/                      # per-invocation output-fence evidence
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

The layout migration has one bootstrap exception. The existing
`factory/scripts/init-factory --update <project-root> --force` command starts
the migration from the pre-migration layout. It installs and validates the new
tree, including `.agent-factory/factory/scripts/init-factory`, before removing
the old top-level `.agent-factory/factory/` and `config/` directories. After that successful
migration, every runtime command and internal reference uses
`.agent-factory/factory/`; no compatibility shim remains at `factory/`.

Design rationale:

- **Single root.** Everything the factory delivers lives under one dotfolder.
  The project root carries only its own files, CLI-specific configuration, and
  the `.current-work/` runtime root.
- **Runtime stays separate.** Linked worktrees, dispatch ledgers, and
  verification markers remain under `.current-work/` with their existing path
  contracts and safety enforcement.
- **`.agent-factory/factory/` and `config/` move inward.** They are factory artifacts, not
  project artifacts. Placing them under `.agent-factory/` makes the ownership
  boundary visible in the directory tree.
- **Sessions under workstreams.** A session binding serves a workstream. Open
  Stage sessions use `workstream_id: null`. Flat session lookup:
  `workstreams/sessions/<id>.yaml`.
- **Usage consolidated.** The four `usage-*` siblings and `usage.duckdb` become
  one `usage/` folder with internal structure. Pipeline internals are hidden.
- **Checks absorb deterministic quality output.** CRAP scores, dependency
  checks, mutation analysis, and module graph checks live in one place.
  Dispatch safety markers remain under `.current-work/`.
- **`factory-` prefix dropped.** Redundant under `.agent-factory/`.
- **Dropped artifacts:** `playbook-state.yml`, `step-guard-debug.json`,
  `dispatch-ledger.yaml.bak` — obsolete under the new model. Dispatch ledgers
  for active features remain under `.current-work/<feature-branch>/`.

All scripts, hooks, agent definitions, skill definitions, CLI index files, and
configuration that reference `.agent-factory/factory/`, `config/`, `.current-work/cycles/`,
or the old `.agent-factory/` sub-paths are updated. Branching, worktree,
dispatch-ledger, and verification-marker references to `.current-work/` remain
unchanged. The `.gitignore` is updated to cover the new layout. The install
script writes to `.agent-factory/factory/` and `.agent-factory/config/` instead
of the project root.

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

| EPIC 1 artifact                  | Replacement                                            |
| -------------------------------- | ------------------------------------------------------ |
| `cycle` command family           | `intent` command family                                |
| `cycle assess` route recommender | Precondition checker: what can run now?                |
| `eligible_cycles` agent metadata | `inputs.required` declarations                         |
| `delivery.yaml` route table      | Implicit graph from `inputs.required` and `outputs`    |
| Cycle-state `cycle` field        | Removed; workstream tracks work references only        |
| Cycle-state `attempt` field      | Removed; external orchestrator owns retry logic        |
| Cycle-state `delegation` field   | Removed; chaining is external via deterministic fences |

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
- **The engine returns immutable assessments.** It reports requirement evidence
  for every agent. It never writes repository state.
- **Dependency direction is enforced.** Scripts may call the engine. The engine
  never imports scripts, configuration, agent definitions, or skills. A
  deterministic boundary test enforces this.
- **Trusted validator identifiers.** The `check` condition type references
  validators by name. The engine resolves the name to an executable — bash
  scripts under `.agent-factory/factory/scripts/` (e.g. `spec-lint`) or Python
  validators under `.agent-factory/factory/engine/validators/` (e.g.
  `proposal.py`). The model never contains shell commands.
- **Shared validator result format.** Every validator returns: artifact type,
  artifact reference, assessed commit, individual check results, and warnings.
  The precondition evaluator interprets pass/fail from these results.
- **Installed-shape tests.** The distributed factory must contain and be able
  to execute the engine. Tests verify this.
- **Tracked source is the test surface.** `packages/factory/engine/` is the
  source of truth. Installation copies the same tree to
  `.agent-factory/factory/engine/`.

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
that declares that artifact as a required input sees that requirement become
satisfied when the research completes. No explicit origin or return field is
needed.

The `decision_needed` field is unchanged.

## Scope

### In the first release

- Restructure the session menu into four lanes: Help, Housekeeping, Project
  Work, Open Stage.
- Housekeeping lane: present a read-only About section followed by exactly three
  manual actions. About shows the installed Factory version, fitting status,
  configured CLI integrations, and usage pipeline health; unreadable values
  appear as `unknown` with their source error. Re-fit reruns the complete
  five-step fitting procedure. Update Factory runs
  `.agent-factory/factory/scripts/init-factory --update <project-root> --force`, relays its result, and refreshes About after success. Update agent
  context invokes the interactive `capture-context --update --scan` mode. No
  precondition graph.
- Extend `capture-context` with `--update --scan`. It requires an existing
  `docs/agent-context.md`, scans the repository and documentation, compares
  discovered concerns and `Read:` paths with the existing file, and presents
  proposed changes for confirmation. It preserves unconfirmed content, writes
  only confirmed changes, and runs
  `.agent-factory/factory/scripts/concern-lint` after writing. If the file does
  not exist, it directs the user to `capture-context --init --scan` without
  writing.
- Restructure agent `inputs` into `required` (artifact type, path pattern,
  conditions) and `context` (plain paths). Restructure every agent `outputs`
  declaration into `path_pattern`, `validator`, and `required` fields under an
  agent-level `minimum_changed`. Skills gain `inputs.context` only — they do not
  appear in the precondition graph.
- Implement a precondition evaluator that reads `inputs.required` declarations
  and checks them against the repository.
- Present all agents after workstream binding in the Project Work lane,
  showing satisfied and unsatisfied required inputs with evidence. Human
  selection remains unrestricted.
- Retain structured transcripts at capture time alongside the text rendering.
- Simplify the workstream state file: remove `cycle`, `attempt`, `revision`,
  `delegation`, and `work` fields. Retain only `workstream_id`, `topic`, and
  `origin_ref`.
- Add a `scope` declaration to every graph-addressable artifact in the closed
  first-release governed set: proposals, epics, stories, Gherkin feature files,
  `architecture.dsl`, `scope-map.md`, and `entity-model.yaml`. Markdown
  artifacts carry it in YAML frontmatter, `entity-model.yaml` as a top-level
  field, and Structurizr DSL and Gherkin feature files as a first-line comment
  (`// scope: ...` or `# scope: ...`). Workstream-scoped artifacts carry the
  workstream identifier. Global artifacts carry `global`. Other artifacts do
  not require `scope`. Adding a type to the precondition registry requires its
  scope representation and lint rule. Add a lint check at artifact creation
  time that verifies required declarations are present and valid.
- Fence every agent activity using the validators named by its output
  declarations. Reject agent definitions whose outputs omit `minimum_changed`
  or whose declarations omit `path_pattern`, `validator`, or `required`. Record
  per-output and aggregate evidence under `.agent-factory/checks/fences/`.
  Chaining is external — no delegation grant, attempt counter, or retry limit
  in the engine.
- Rename the `cycle` command family to `intent`: `intent select` and
  `intent assess`. The old `cycle` commands are removed; no alias is provided.
- Clean-break the engine: delete `cycle_model.py`, `cycles.py`, and
  `models/delivery.yaml`. Rewrite `eligibility.py`, `readiness.py`, and
  `recommendations.py`. Keep `validators/` and `schemas/` (adapted).
- Delete existing v1 workstream state files. No migration script.
- Rewrite `run-step` to use the precondition evaluator. Delete the `phase`
  diagnostic stub.
- Session bindings carry `session_id`, `workstream_id`, and `bound_at`. The
  `workstream_id` key must be present: a known identifier means bound, explicit
  `null` means Open Stage, and a missing key is invalid. No delegation or
  attempt fields. Selecting a workstream updates the binding.
- Keep EPIC 1 infrastructure: workstream and session plumbing, menu
  integration, deterministic checks.
- Replace `eligible_cycles` metadata and flat `inputs` lists with structured
  `inputs.required` / `inputs.context` on agent definitions. Add
  `inputs.context` to skill definitions.
- Consolidate all factory content under `.agent-factory/`. Move `factory/`
  to `.agent-factory/factory/`, `config/` to `.agent-factory/config/`.
  Retain `.current-work/` for linked worktrees, dispatch ledgers, and
  verification markers. Move workstream state from `.current-work/cycles/` to
  `.agent-factory/workstreams/` and session bindings to
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

- Housekeeping automation beyond the three defined actions: automated
  recommendations, additional maintenance actions, a precondition graph, or a
  drift-detection engine for factory state. Housekeeping's own model is a
  separate future concern.
- Per-CLI activity extractors and the common activity record format. The
  first release retains structured transcripts; extraction from them is a
  separate concern.
- Git-diff-based change tracking for activity impact analysis.
- Capture-time activity extraction.
- Automated artifact-impact analysis: given that an artifact changed, surface
  which other artifacts reference it and may need reconciliation.
- `structured-only` transcript retention mode.
- Removing playbook files (they remain as reference documentation).
- Self-directed delegation beyond external chaining.
- Batch identity tracking across refinement-realization loops.
- Replacing the internal survey and falsification research routes.
- Usage record enrichment: adding `workstream_id`, `workstream_origin`, and
  `skills_invoked` to the usage-record contract, workstream-dimension usage
  analysis, and capture-hook integration. Addressed in bulk after the
  activity-graph orchestration is in place.

## Open Questions

None.

## Completion Criteria

- The session menu presents four lanes: Help, Housekeeping, Project Work, and
  Open Stage. Help routes to tour skills. Housekeeping first shows a read-only
  About section containing installed Factory version, fitting status,
  configured CLI integrations, and usage pipeline health. Unreadable values
  display as `unknown` with their source error. About is followed by exactly
  three actions: Re-fit reruns all five fitting steps and reports their
  resulting status; Update Factory runs
  `.agent-factory/factory/scripts/init-factory --update <project-root> --force`, relays its output and exit status, and refreshes About after
  success; Update agent context invokes `capture-context --update --scan`.
  Project Work starts or continues a workstream. Open Stage opens freeform
  conversation.
- `capture-context --update --scan` requires an existing
  `docs/agent-context.md`, reports discovered differences in concerns and
  `Read:` paths, and waits for confirmation before writing. Unconfirmed content
  remains unchanged. Confirmed changes are written and
  `.agent-factory/factory/scripts/concern-lint` passes. When the file is absent,
  the mode directs the user to `capture-context --init --scan` and performs no
  write.
- Every agent definition carries structured `inputs` with `required` and
  `context` subkeys. Required entries reference artifact types, path patterns,
  and conditions. Context entries are plain paths. Neither references stage
  names. Skills carry `inputs.context` only.
- A precondition evaluator reads `inputs.required` declarations, checks them
  against the repository, and reports evidence for every agent and every
  required input, marking each requirement satisfied or unsatisfied. This
  evidence does not block human selection.
- After workstream binding in the Project Work lane, the session presents all
  agents with their requirement evidence. The human can select any agent
  regardless of which requirements are satisfied.
- Workstream state files contain `workstream_id`, `topic`, and `origin_ref`.
  They do not contain `cycle`, `attempt`, `delegation`, or `work` fields.
- Every graph-addressable artifact in the governed set carries a `scope`
  declaration with a value of `global` or a known workstream identifier. The
  governed set is proposals, epics, stories, Gherkin feature files,
  `architecture.dsl`, `scope-map.md`, and `entity-model.yaml`. A lint check at
  artifact creation time rejects governed artifacts missing the declaration or
  carrying an unknown value. Other artifacts do not require `scope`.
- Structured transcripts are retained at capture time for all four supported
  CLIs (Claude Code, Pi, Copilot, Codex) when transcript retention is `full`.
- Every agent defines `outputs.minimum_changed`; every output declaration
  contains `path_pattern`, `validator`, and `required`. Missing fields make the
  agent definition invalid. After an activity, required outputs must have a
  created or modified match; optional outputs without a match are skipped; and
  fewer changed declarations than `minimum_changed` fails the fence. Every
  changed output is checked by its declared validator. The aggregate passes
  only when all required outputs changed, the minimum was met, and every
  invoked validator passed. Per-output and aggregate evidence is returned to
  the caller and stored under
  `.agent-factory/checks/fences/<session-id>/<invocation-id>.yaml`. Fence
  failure does not block human action. Chaining is external — no delegation
  grant, attempt counter, or retry limit exists in the engine, agent
  definitions, or session bindings.
- Workstream state files can be created and loaded under
  `.agent-factory/workstreams/`. Fields are `workstream_id`, `topic`, and
  `origin_ref` only. Attempts to modify an existing state file fail without
  changing it.
- Session bindings contain `session_id`, `workstream_id`, and `bound_at`, and
  tear down cleanly at session end. The `workstream_id` key is always present:
  a known identifier means bound, explicit `null` means Open Stage, and a
  missing key fails validation. Selecting a different workstream updates
  `workstream_id` and `bound_at` without modifying workstream state. Path:
  `.agent-factory/workstreams/sessions/<session-id>.yaml`.
- The `intent` command family (`intent select`, `intent assess`) operates
  against the activity-graph model. `intent select` lists all agents with
  their precondition status (satisfied and unsatisfied requirements).
  `intent assess` runs validators and reports results per the shared result
  format.
- All deterministic checks (output fences, CRAP score, dependency check,
  mutation analysis, module graph check) run and write results to
  `.agent-factory/checks/`.
- All factory-delivered content lives under `.agent-factory/`. The project root
  contains only its own files, CLI-specific directories, and `.current-work/`
  as the runtime root for linked worktrees, dispatch ledgers, and verification
  markers. The installed factory tree is at `.agent-factory/factory/`, project
  configuration at `.agent-factory/config/`. Neither `factory/` nor `config/`
  exists at the project root. Workstream state files are under `workstreams/`,
  session bindings under `workstreams/sessions/`, quality gate results under
  `checks/`, and usage pipeline state under `usage/` with `records/`,
  `transcripts/`, `control/`, `runtime/`, `analysis/` subfolders. No script,
  hook, agent definition, or CLI index references the old `.agent-factory/factory/`, `config/`,
  `.current-work/cycles/`, or `.agent-factory/` sub-paths at the project root.
  Existing branching, worktree, dispatch-ledger, and verification-marker paths
  under `.current-work/` remain unchanged.
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

The cycle proposal kept `.agent-factory/factory/scripts/phase` as a diagnostic stub for
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
| PROP-05 | minor    | 03    | resolved  | The `check` condition type says named validators are "the same scripts the factory already runs" but the codebase has two validator forms: Python classes in `engine/validators/` (e.g. `proposal.py`) and bash scripts in `.agent-factory/factory/scripts/` (e.g. `spec-lint`). The design does not specify how the evaluator resolves a validator name to an executable or what interface it expects. **Resolution:** Engine architectural constraints section added. Validator resolution specified.                                                    |
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

| ID      | Severity | Check | Status   | Finding                                                                                                                                                                                                                                                                                                                                                                                                                                                                                         |
| ------- | -------- | ----- | -------- | ----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| PROP-09 | minor    | 02    | resolved | Scope lists four `intent` commands (`select`, `assess`, `status`, `delegate`) at line 643 but completion criteria at line 742 specify behavior for `select` and `assess` only. The `intent status` output content and the `intent delegate` command interface have no testable endpoint in the proposal. A planner cannot write acceptance tests for these two commands from the criteria alone. **Resolution:** Scope and completion criteria now define only intent select and intent assess. |
| PROP-10 | minor    | 02    | resolved | `packages/orchestrator` retirement is in scope (line 675) but has no matching completion criterion. "Retire" is ambiguous without a verifiable endpoint: delete the directory, remove from CI, mark deprecated, or some combination. **Resolution:** Completion criteria now require deletion of packages/orchestrator, removal of references, and migration of still-needed tests.                                                                                                             |
| PROP-11 | minor    | 01    | resolved | Completion criterion 6 (line 721) contains "Workstream scope is derived from the dependency graph" — a design mechanism description, not a testable assertion. The field-presence checks in the same criterion are testable; this sentence is not. **Resolution:** The untestable dependency-graph clause was removed from the completion criterion.                                                                                                                                            |
| PROP-12 | minor    | 03    | resolved | Design line 196 says the dependency graph comes from "agent and skill definitions" but lines 200-205 exclude skills from the graph and line 209 restricts the computation to "every agent's" declarations. A planner reading line 196 alone would incorrectly include skill outputs in the graph. **Resolution:** Design now states that the graph comes from agent definitions only.                                                                                                           |

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

## Review — 2026-09-17 (pass 4)

Reviewer: proposal-review-agent
Reviewed commit: 72f466e33415578a1cd6c14cb170cb73d3b6721e
Disposition: findings

### Prior findings

| ID      | Severity | Check | Status   | Verification                                                                                                                 |
| ------- | -------- | ----- | -------- | ---------------------------------------------------------------------------------------------------------------------------- |
| PROP-09 | minor    | 02    | resolved | Scope and completion criteria now define only `intent select` and `intent assess`.                                           |
| PROP-10 | minor    | 02    | resolved | Completion criteria require deletion of `packages/orchestrator`, removal of references, and migration of still-needed tests. |
| PROP-11 | minor    | 01    | resolved | The untestable dependency-graph clause was removed from the completion criterion.                                            |
| PROP-12 | minor    | 03    | resolved | Design now states that the graph comes from agent definitions only.                                                          |

### Findings

| ID      | Severity | Check | Status   | Finding                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                         |
| ------- | -------- | ----- | -------- | ----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| PROP-13 | major    | 03    | open     | The workstream schema removes `revision`, but the Design keeps revision checks for concurrency control. A revision check has no declared value to compare. Retain a revision value or define the replacement concurrency contract. **Verification:** The direct contradiction was removed, but no replacement concurrency contract is defined. Workstream state remains updateable, and the retained session plumbing permits several sessions to bind to one workstream.                                                                       |
| PROP-14 | major    | 01    | open     | The Project Work lane presents eligible agents only. The proposal also requires humans to select agents with failed requirements. Define how a human discovers and selects an ineligible agent, then add a matching completion criterion. **Verification:** The precondition-graph and completion sections now show all agents, but the Session Menu section still presents only agents with satisfied preconditions. The intent-select criterion also lists eligible activities only.                                                          |
| PROP-15 | major    | 03    | resolved | Delegation pauses when an activity requires human judgment, but no declaration or evaluator rule marks such activities. Define that signal and how the dispatcher checks it, or remove this pause condition. **Resolution:** Human judgment is handled inside the invoked agent. Delegation waits because the agent does not complete until the human responds.                                                                                                                                                                                 |
| PROP-16 | major    | 03    | open     | The retry design says each activity, “agent or skill,” declares `delegated_attempt_limit`. The terminology defines activities as agent invocations and excludes skills from the graph. State which definitions own the limit and specify its schema after `delivery.yaml` is deleted. **Verification:** Agent frontmatter now owns the limit, but its type, allowed range, required/default behavior, and omitted-value semantics remain undefined. Scope and completion criteria also still call the limit per-activity rather than per-agent. |
| PROP-17 | major    | 02    | resolved | The first release records `skills_invoked`, but capture-time activity extraction is deferred. Pi and Codex have no skill tool in the proposal’s own table. Include the required extraction or instrumentation, or defer `skills_invoked`. **Resolution:** Usage-record enrichment, capture-hook integration, and workstream analysis moved to Explicitly deferred.                                                                                                                                                                              |
| PROP-18 | major    | 02    | resolved | Design classifies architecture DSL as global, while Scope requires a `workstream` field on “architecture documents.” Define which architecture artifacts are global and which are workstream-scoped. Align the lint rule and completion criteria with that partition. **Resolution:** The proposal now partitions named artifact types into workstream-scoped and global groups and aligns Scope and Completion Criteria with that partition. PROP-21 covers the separate representation defect introduced by the resolution.                   |
| PROP-19 | major    | 04    | open     | `impact.boundaries` omits affected areas named by Scope: `packages/orchestrator`, the superseded proposal, backlog documents, and CI configuration. Add the concrete tracked boundaries so planning and review inspect the full impact. **Verification:** Boundaries now include packages/orchestrator, the superseded proposal, and backlog. They still omit the documentation tree and CI configuration that Scope requires changing.                                                                                                         |
| PROP-20 | major    | 03    | open     | Path resolution does not define placeholder expansion, match cardinality, or delegation behavior when several artifacts satisfy one required input. Define those rules so eligibility and unattended execution are deterministic. **Verification:** Placeholder expansion, cardinality, and delegation behavior are now defined. The cardinality rules run after scope filtering but do not state whether condition-failing candidates are removed before counting.                                                                             |

### Check results

| #   | Check                            | Result                                                                                                                      |
| --- | -------------------------------- | --------------------------------------------------------------------------------------------------------------------------- |
| 1   | Completion criteria testable     | Fail — human override has no discoverable interface or complete criterion (PROP-14).                                        |
| 2   | Scope boundary sharp             | Fail — skill capture and architecture ownership conflict with deferrals and Design (PROP-17, PROP-18).                      |
| 3   | Design decomposable              | Fail — concurrency, delegation, retry, and path-resolution contracts remain undecided (PROP-13, PROP-15, PROP-16, PROP-20). |
| 4   | Impact classification consistent | Fail — declared boundaries omit several affected areas (PROP-19).                                                           |
| 5   | Boundary references exist        | Pass — all ten declared paths resolve at the reviewed commit.                                                               |
| 6   | Open questions genuine           | Pass — `None` contains no padding, but the findings identify decisions that must move into the proposal.                    |
| 7   | Motivation justifies timing      | Pass — it identifies prior investment, observed workflow friction, and the cost of further stage-model work.                |
| 8   | Estimate plausible               | Pass — `unknown` is permitted and more honest than an unsupported range.                                                    |

### Summary

The four prior open findings are resolved. Eight major findings remain. The proposal still needs deterministic contracts for concurrency, manual override, delegation, retries, and path resolution. It must also align skill capture, architecture ownership, and impact boundaries before Planning can decompose it without re-deriving the design.

Handoff: 8 open findings. Address and re-open when ready.

## Review — 2026-09-17 (pass 5)

Reviewer: proposal-review-agent
Reviewed commit: 0be4b38bf994114ec651d301b95154ccfce4dc69
Reviewed content: working tree with uncommitted proposal changes
Disposition: findings

### Prior findings

| ID      | Severity | Check | Status    | Verification                                                                                                                                                                                                                                                                                                                                                                        |
| ------- | -------- | ----- | --------- | ----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| PROP-01 | major    | 02    | resolved  | “What just broke?” remains deferred as automated artifact-impact analysis.                                                                                                                                                                                                                                                                                                          |
| PROP-02 | major    | 02    | resolved  | `.agent-factory/` restructuring remains a separate first-release scope item.                                                                                                                                                                                                                                                                                                        |
| PROP-03 | major    | 02    | resolved  | Branching-policy and git-hook changes remain explicit in Scope.                                                                                                                                                                                                                                                                                                                     |
| PROP-04 | major    | 05    | resolved  | `packages/orchestrator` retirement remains explicit and is now a declared boundary.                                                                                                                                                                                                                                                                                                 |
| PROP-05 | minor    | 03    | resolved  | Validator resolution and the shared result format remain defined.                                                                                                                                                                                                                                                                                                                   |
| PROP-06 | minor    | 01    | resolved  | The completion criteria still separate state, bindings, commands, and checks.                                                                                                                                                                                                                                                                                                       |
| PROP-07 | minor    | 02    | resolved  | Research routing still uses the graph without invented origin or return fields.                                                                                                                                                                                                                                                                                                     |
| PROP-08 | minor    | 08    | no change | Estimate fields remain `unknown`, which policy permits.                                                                                                                                                                                                                                                                                                                             |
| PROP-09 | minor    | 02    | resolved  | Scope and criteria still define only `intent select` and `intent assess`.                                                                                                                                                                                                                                                                                                           |
| PROP-10 | minor    | 02    | resolved  | Orchestrator retirement retains a testable completion criterion.                                                                                                                                                                                                                                                                                                                    |
| PROP-11 | minor    | 01    | resolved  | The untestable mechanism clause remains absent from completion criteria.                                                                                                                                                                                                                                                                                                            |
| PROP-12 | minor    | 03    | resolved  | The graph still comes from agent definitions only.                                                                                                                                                                                                                                                                                                                                  |
| PROP-13 | major    | 03    | open      | The direct revision-check contradiction is gone, but replacement concurrency behavior is still undefined. **Verification:** The Design now says the state file is immutable after creation, which removes the need for concurrency control. Completion Criteria still require state files to “load, create, and update.” Remove “update” or define update and concurrency behavior. |
| PROP-14 | major    | 01    | resolved  | Two sections show all agents, but Session Menu and `intent select` still expose eligible agents only. **Resolution:** Precondition Graph, Session Menu, Scope, Completion Criteria, and intent-select behavior now present all agents with eligible or ineligible status.                                                                                                           |
| PROP-15 | major    | 03    | resolved  | Human judgment now pauses inside the invoked agent until it completes.                                                                                                                                                                                                                                                                                                              |
| PROP-16 | major    | 03    | resolved  | Agent frontmatter owns the retry limit, but the field schema and omitted-value behavior remain undefined. **Resolution:** Agent frontmatter owns the integer field with minimum 1. Omission disables delegated dispatch. Scope, storage, reset behavior, and Completion Criteria now use per-agent semantics.                                                                       |
| PROP-17 | major    | 02    | resolved  | Usage-record enrichment and its capture integration are explicitly deferred.                                                                                                                                                                                                                                                                                                        |
| PROP-18 | major    | 02    | resolved  | Named artifact types are partitioned into workstream-scoped and global groups.                                                                                                                                                                                                                                                                                                      |
| PROP-19 | major    | 04    | resolved  | Three boundaries were added, but documentation and CI configuration remain omitted. **Resolution:** Boundaries now include docs, backlog, the superseded proposal, pre-commit configuration, and gitignore. No tracked CI configuration currently references the orchestrator.                                                                                                      |
| PROP-20 | major    | 03    | resolved  | Expansion and cardinality are defined, but condition filtering is not ordered before cardinality. **Resolution:** Path resolution now orders glob expansion, scope filtering, condition checking, and cardinality. Failed candidates are removed before counting.                                                                                                                   |

### Findings

| ID      | Severity | Check | Status   | Finding                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                 |
| ------- | -------- | ----- | -------- | ------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| PROP-21 | major    | 03    | open     | The proposal requires every artifact to carry `scope` in YAML frontmatter. Structurizr DSL and Gherkin feature files do not support YAML frontmatter, and adding it would break their parsers. Define a valid representation per artifact format, then narrow “every artifact” to an explicit artifact-type list. **Verification:** The proposal now defines valid YAML, Gherkin, and Structurizr representations. It still says “every artifact” and “all artifact types” while naming only seven types; reviews, findings, ADRs, research records, and other artifacts remain mechanically ambiguous. |
| PROP-22 | minor    | 03    | resolved | Summary and Core Principles say skills declare prerequisites. Design and Scope give skills contextual inputs only and exclude them from the graph. Use one rule throughout: either skills declare prerequisites or they do not. **Resolution:** Summary and Core Principles now state that agents declare prerequisites. Skills carry contextual inputs only and remain outside the graph.                                                                                                                                                                                                              |

### Check results

| #   | Check                            | Result                                                                                                                                                                                                 |
| --- | -------------------------------- | ------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------ |
| 1   | Completion criteria testable     | Fail — agent presentation conflicts across criteria and command behavior, while “every artifact” is not enumerable (PROP-14, PROP-21).                                                                 |
| 2   | Scope boundary sharp             | Fail — documentation and CI impact remain outside declared boundaries, and “every artifact” is broader than the named types (PROP-19, PROP-21).                                                        |
| 3   | Design decomposable              | Fail — concurrency, retry schema, condition-filter ordering, artifact metadata representation, and skill prerequisites remain undecided or inconsistent (PROP-13, PROP-16, PROP-20, PROP-21, PROP-22). |
| 4   | Impact classification consistent | Fail — the flags are correct, but declared boundaries still omit affected documentation and CI paths (PROP-19).                                                                                        |
| 5   | Boundary references exist        | Pass — all twelve declared paths resolve in the reviewed working tree.                                                                                                                                 |
| 6   | Open questions genuine           | Pass — `None` contains no padding, but the open findings identify decisions that belong in the proposal body.                                                                                          |
| 7   | Motivation justifies timing      | Pass — it ties the change to observed workflow friction and the window before further stage-model investment.                                                                                          |
| 8   | Estimate plausible               | Pass — `unknown` remains preferable to an unsupported range.                                                                                                                                           |

### Summary

Three pass-4 findings are resolved. Five remain open, and two new findings were found. Six major findings and one minor finding now block planning. The proposal needs consistent agent presentation, deterministic concurrency and retry contracts, ordered condition filtering, format-valid scope metadata, complete impact boundaries, and one rule for skill prerequisites.

Handoff: 7 open findings. Address and re-open when ready.

## Review — 2026-09-17 (pass 6)

Reviewer: proposal-review-agent
Reviewed commit: 0be4b38bf994114ec651d301b95154ccfce4dc69
Reviewed content: working tree with uncommitted proposal changes
Disposition: findings

### Prior findings

| ID      | Severity | Check | Status    | Verification                                                                                                                                                                                                                                                                                                                   |
| ------- | -------- | ----- | --------- | ------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------ |
| PROP-01 | major    | 02    | resolved  | Automated artifact-impact analysis remains deferred.                                                                                                                                                                                                                                                                           |
| PROP-02 | major    | 02    | resolved  | `.agent-factory/` restructuring remains explicit in Scope.                                                                                                                                                                                                                                                                     |
| PROP-03 | major    | 02    | resolved  | Branching-policy and hook changes remain explicit in Scope.                                                                                                                                                                                                                                                                    |
| PROP-04 | major    | 05    | resolved  | Orchestrator retirement remains explicit and bounded.                                                                                                                                                                                                                                                                          |
| PROP-05 | minor    | 03    | resolved  | Validator resolution and result format remain defined.                                                                                                                                                                                                                                                                         |
| PROP-06 | minor    | 01    | resolved  | Completion criteria remain separated by capability.                                                                                                                                                                                                                                                                            |
| PROP-07 | minor    | 02    | resolved  | Research routing remains graph-based without cycle fields.                                                                                                                                                                                                                                                                     |
| PROP-08 | minor    | 08    | no change | Estimate fields remain `unknown`, as policy permits.                                                                                                                                                                                                                                                                           |
| PROP-09 | minor    | 02    | resolved  | The command family remains limited to `intent select` and `intent assess`.                                                                                                                                                                                                                                                     |
| PROP-10 | minor    | 02    | resolved  | Orchestrator retirement retains a testable endpoint.                                                                                                                                                                                                                                                                           |
| PROP-11 | minor    | 01    | resolved  | The untestable mechanism clause remains absent.                                                                                                                                                                                                                                                                                |
| PROP-12 | minor    | 03    | resolved  | Only agent definitions form the graph.                                                                                                                                                                                                                                                                                         |
| PROP-13 | major    | 03    | resolved  | Design declares immutable state, but Completion Criteria still require updates. **Resolution:** Workstream state is immutable after creation. Completion Criteria now allow create and load only and require attempted modification to fail without changing the file.                                                         |
| PROP-14 | major    | 01    | resolved  | All relevant sections and `intent select` now expose every agent with status.                                                                                                                                                                                                                                                  |
| PROP-15 | major    | 03    | resolved  | Human judgment remains inside the invoked agent.                                                                                                                                                                                                                                                                               |
| PROP-16 | major    | 03    | resolved  | Retry field schema, omission behavior, storage, reset, and per-agent semantics are defined.                                                                                                                                                                                                                                    |
| PROP-17 | major    | 02    | resolved  | Usage enrichment remains explicitly deferred.                                                                                                                                                                                                                                                                                  |
| PROP-18 | major    | 02    | resolved  | Workstream and global artifact groups remain defined.                                                                                                                                                                                                                                                                          |
| PROP-19 | major    | 04    | resolved  | Declared boundaries now cover the affected tracked areas.                                                                                                                                                                                                                                                                      |
| PROP-20 | major    | 03    | resolved  | Condition filtering now occurs before cardinality.                                                                                                                                                                                                                                                                             |
| PROP-21 | major    | 03    | resolved  | Format-specific scope declarations are valid, but the governed artifact set remains undefined. **Resolution:** The governed set is closed to seven named artifact types. The proposal defines YAML-frontmatter, top-level-YAML, Gherkin-comment, and Structurizr-comment representations; other artifacts need no declaration. |
| PROP-22 | minor    | 03    | resolved  | Agents declare prerequisites; skills carry context only.                                                                                                                                                                                                                                                                       |

### Findings

| ID      | Severity | Check | Status   | Finding                                                                                                                                                                                                                                                                                                                                                                                                                                                                                |
| ------- | -------- | ----- | -------- | -------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| PROP-23 | major    | 03    | resolved | Scope eliminates `.current-work/` and updates worktree enforcement to the new layout, but the unified layout defines no worktree directory. Specify the exact worktree root plus the new ledger and verification-marker paths. **Resolution:** `.current-work/` remains the runtime root for linked worktrees, dispatch ledgers, and verification markers. Existing branching and safety path contracts remain unchanged.                                                              |
| PROP-24 | major    | 01    | resolved | Housekeeping must list “available manual actions,” but Design, Scope, and Completion Criteria never enumerate them. Define the first-release action list and observable output, or limit Housekeeping to inventory display. **Resolution:** Housekeeping now defines a read-only About section and exactly three actions: Re-fit, Update Factory, and Update agent context. Scope and Completion Criteria define their commands, outputs, confirmation behavior, and failure behavior. |

### Check results

| #   | Check                            | Result                                                                                                                                             |
| --- | -------------------------------- | -------------------------------------------------------------------------------------------------------------------------------------------------- |
| 1   | Completion criteria testable     | Fail — state updates conflict with Design, the artifact set is not enumerable, and Housekeeping actions are undefined (PROP-13, PROP-21, PROP-24). |
| 2   | Scope boundary sharp             | Fail — “all artifact types” has no closed list, and Housekeeping’s action surface is unspecified (PROP-21, PROP-24).                               |
| 3   | Design decomposable              | Fail — workstream updates and the replacement worktree layout remain undefined (PROP-13, PROP-23).                                                 |
| 4   | Impact classification consistent | Pass — cross-component reach and both change flags match the Design; boundaries cover affected tracked areas.                                      |
| 5   | Boundary references exist        | Pass — all fifteen declared paths resolve in the reviewed working tree.                                                                            |
| 6   | Open questions genuine           | Pass — `None` contains no padding, but the open findings identify decisions that must move into the body.                                          |
| 7   | Motivation justifies timing      | Pass — observed workflow friction and the window before further stage-model investment justify timing.                                             |
| 8   | Estimate plausible               | Pass — `unknown` remains preferable to an unsupported range.                                                                                       |

### Summary

Five pass-5 findings are resolved. Two remain open, and two new major findings were found. Four major findings block planning: state mutability, the governed artifact set, the replacement worktree layout, and Housekeeping’s manual-action contract.

Handoff: 4 open findings. Address and re-open when ready.

## Review — 2026-09-17 (pass 7)

Reviewer: proposal-review-agent
Reviewed commit: 0be4b38bf994114ec651d301b95154ccfce4dc69
Reviewed content: working tree with uncommitted proposal changes
Disposition: findings

### Prior findings

| ID      | Severity | Check | Status    | Verification                                                              |
| ------- | -------- | ----- | --------- | ------------------------------------------------------------------------- |
| PROP-01 | major    | 02    | resolved  | Automated artifact-impact analysis remains deferred.                      |
| PROP-02 | major    | 02    | resolved  | `.agent-factory/` restructuring remains explicit in Scope.                |
| PROP-03 | major    | 02    | resolved  | Branching and hook behavior remains explicit.                             |
| PROP-04 | major    | 05    | resolved  | Orchestrator retirement remains explicit and bounded.                     |
| PROP-05 | minor    | 03    | resolved  | Validator resolution and result format remain defined.                    |
| PROP-06 | minor    | 01    | resolved  | Completion criteria remain separated by capability.                       |
| PROP-07 | minor    | 02    | resolved  | Research routing remains graph-based without cycle fields.                |
| PROP-08 | minor    | 08    | no change | Estimate fields remain `unknown`, as policy permits.                      |
| PROP-09 | minor    | 02    | resolved  | The command family remains limited to two commands.                       |
| PROP-10 | minor    | 02    | resolved  | Orchestrator retirement retains a testable endpoint.                      |
| PROP-11 | minor    | 01    | resolved  | The untestable mechanism clause remains absent.                           |
| PROP-12 | minor    | 03    | resolved  | Only agent definitions form the graph.                                    |
| PROP-13 | major    | 03    | resolved  | State is immutable; create, load, and rejected modification are testable. |
| PROP-14 | major    | 01    | resolved  | Every agent remains visible with its precondition status.                 |
| PROP-15 | major    | 03    | resolved  | Human judgment remains inside the invoked agent.                          |
| PROP-16 | major    | 03    | resolved  | Retry schema and per-agent semantics remain defined.                      |
| PROP-17 | major    | 02    | resolved  | Usage enrichment remains explicitly deferred.                             |
| PROP-18 | major    | 02    | resolved  | Workstream and global artifact groups remain defined.                     |
| PROP-19 | major    | 04    | resolved  | Declared boundaries cover affected tracked areas.                         |
| PROP-20 | major    | 03    | resolved  | Condition filtering occurs before cardinality.                            |
| PROP-21 | major    | 03    | resolved  | Seven governed types and their representations are explicit.              |
| PROP-22 | minor    | 03    | resolved  | Agents declare prerequisites; skills carry context only.                  |
| PROP-23 | major    | 03    | resolved  | `.current-work/` retains all existing runtime path contracts.             |
| PROP-24 | major    | 01    | resolved  | Housekeeping exposes one defined inventory and three defined actions.     |

### Findings

| ID      | Severity | Check | Status | Finding                                                                                                                                                                                                                                                                                                                                            |
| ------- | -------- | ----- | ------ | -------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| PROP-25 | major    | 01    | open   | The evaluator criterion returns “a list of eligible activities” with evidence for satisfied and unsatisfied requirements. Eligible activities cannot have unsatisfied requirements, while the menu requires every agent’s status. Define one result shape that covers all evaluated agents or separate eligible results from rejected evaluations. |
| PROP-26 | major    | 03    | open   | Folder consolidation removes the top-level `factory/` directory, but runtime design and criteria still invoke `factory/scripts/init-factory`, `factory/scripts/concern-lint`, resolve validators under `factory/scripts/`, and install the engine to `factory/engine/`. Update these to `.agent-factory/factory/...` or define retained shims.     |

### Check results

| #   | Check                            | Result                                                                                                                                     |
| --- | -------------------------------- | ------------------------------------------------------------------------------------------------------------------------------------------ |
| 1   | Completion criteria testable     | Fail — the evaluator result is internally contradictory, and Housekeeping invokes paths that the same proposal removes (PROP-25, PROP-26). |
| 2   | Scope boundary sharp             | Pass — first-release and deferred lists now partition the work, including the closed artifact set and Housekeeping actions.                |
| 3   | Design decomposable              | Fail — Planning must still invent the evaluator result contract and installed runtime paths (PROP-25, PROP-26).                            |
| 4   | Impact classification consistent | Pass — cross-component reach and both change flags match the Design; boundaries cover affected tracked areas.                              |
| 5   | Boundary references exist        | Pass — all fifteen declared paths resolve in the reviewed working tree.                                                                    |
| 6   | Open questions genuine           | Pass — `None` contains no padding, but the two open findings identify decisions that belong in the body.                                   |
| 7   | Motivation justifies timing      | Pass — observed workflow friction and the window before further stage-model investment justify timing.                                     |
| 8   | Estimate plausible               | Pass — `unknown` remains preferable to an unsupported range.                                                                               |

### Summary

All four pass-6 findings are resolved. Two new major findings block planning: the evaluator needs one coherent result contract, and runtime commands must use paths that survive folder consolidation.

Handoff: 2 open findings. Address and re-open when ready.

## Review — 2026-09-18 (pass 8)

Reviewer: proposal-review-agent
Reviewed commit: 4949e0d92300b755cb9800eda82322a895dad8eb
Reviewed content: working tree with uncommitted proposal changes
Disposition: clean

### Prior findings

| ID      | Severity | Check | Status   | Verification                                                                                                                                                                                                                                                                                                                                                                                                                           |
| ------- | -------- | ----- | -------- | -------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| PROP-25 | major    | 01    | resolved | The evaluator criterion now reads "reports evidence for every agent and every required input, marking each requirement satisfied or unsatisfied." The `intent select` criterion says "lists all agents with their precondition status." The session menu and precondition graph sections present "all agents." "Eligible activities" no longer appears in any criterion — only in delegation context and the engine disposition table. |
| PROP-26 | major    | 03    | resolved | Every runtime path in Design, Scope, and Completion Criteria now uses `.agent-factory/factory/...` prefixes. The sole bare `factory/` reference is the intentional bootstrap exception describing the pre-migration entry point. `packages/factory/` references are to tracked source code, not the installed runtime.                                                                                                                 |

### Check results

| #   | Check                            | Result                                                                                                                                                                                                                                   |
| --- | -------------------------------- | ---------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| 1   | Completion criteria testable     | Pass — every criterion specifies observable, verifiable conditions without requiring authorial interpretation.                                                                                                                           |
| 2   | Scope boundary sharp             | Pass — in-scope and deferred lists partition the space; the governed artifact set is closed to seven named types; Housekeeping actions are enumerated.                                                                                   |
| 3   | Design decomposable              | Pass — input format, condition types, path resolution, delegation, retry limits, transcript retention, session menu, folder consolidation, and engine disposition are all specified to a level that supports INVEST story decomposition. |
| 4   | Impact classification consistent | Pass — cross-component scope, both change flags, and fifteen boundary paths match the Design's reach.                                                                                                                                    |
| 5   | Boundary references exist        | Pass — all fifteen declared paths resolve in the reviewed working tree.                                                                                                                                                                  |
| 6   | Open questions genuine           | Pass — "None" is appropriate after eight review passes resolving twenty-six findings.                                                                                                                                                    |
| 7   | Motivation justifies timing      | Pass — observed workflow friction, the wrong unit of work in the stage model, and the window before further investment justify acting now.                                                                                               |
| 8   | Estimate plausible               | Pass — `unknown` remains preferable to an unsupported range given the scope.                                                                                                                                                             |

### Summary

Both pass-7 findings are resolved. All eight checks pass. No new findings. The proposal is planning-ready: a planning agent can decompose it into stories without re-deriving the design. The twenty-six findings accumulated across eight review passes are all resolved or accepted.

## Review — 2026-09-18 (pass 9)

Reviewer: proposal-review-agent
Reviewed commit: 2b9374934b0b1912b38bf580dee11e2de2be2df0
Reviewed content: working tree with uncommitted proposal changes
Disposition: findings

### Prior findings

| ID      | Severity | Check | Status    | Verification                                                                                                                                 |
| ------- | -------- | ----- | --------- | -------------------------------------------------------------------------------------------------------------------------------------------- |
| PROP-01 | major    | 02    | resolved  | Automated artifact-impact analysis remains deferred.                                                                                         |
| PROP-02 | major    | 02    | resolved  | `.agent-factory/` restructuring remains explicit.                                                                                            |
| PROP-03 | major    | 02    | resolved  | Branching and hook behavior remains explicit.                                                                                                |
| PROP-04 | major    | 05    | resolved  | Orchestrator retirement remains explicit and bounded.                                                                                        |
| PROP-05 | minor    | 03    | resolved  | Validator resolution and result format remain defined.                                                                                       |
| PROP-06 | minor    | 01    | resolved  | Completion criteria remain separated by capability.                                                                                          |
| PROP-07 | minor    | 02    | resolved  | Research routing remains graph-based without cycle fields.                                                                                   |
| PROP-08 | minor    | 08    | no change | Estimate fields remain `unknown`, as policy permits.                                                                                         |
| PROP-09 | minor    | 02    | resolved  | The command family remains limited to two commands.                                                                                          |
| PROP-10 | minor    | 02    | resolved  | Orchestrator retirement retains a testable endpoint.                                                                                         |
| PROP-11 | minor    | 01    | resolved  | The untestable mechanism clause remains absent.                                                                                              |
| PROP-12 | minor    | 03    | resolved  | Only agent definitions form the graph.                                                                                                       |
| PROP-13 | major    | 03    | resolved  | Workstream state remains immutable and testable.                                                                                             |
| PROP-14 | major    | 01    | resolved  | Every agent remains visible with requirement evidence.                                                                                       |
| PROP-15 | major    | 03    | resolved  | Engine-managed delegation was removed, making the former human-judgment signal unnecessary.                                                  |
| PROP-16 | major    | 03    | resolved  | Retry limits and counters were removed from engine, agent, and session contracts. External orchestrators own retries.                        |
| PROP-17 | major    | 02    | resolved  | Usage enrichment remains explicitly deferred.                                                                                                |
| PROP-18 | major    | 02    | resolved  | Workstream and global artifact groups remain defined.                                                                                        |
| PROP-19 | major    | 04    | resolved  | Declared boundaries cover affected tracked areas.                                                                                            |
| PROP-20 | major    | 03    | resolved  | Path resolution multiple-survivor rule now says “orchestrator must supply” and “stops for human direction” — no delegation language remains. |
| PROP-21 | major    | 03    | resolved  | Seven governed artifact types and their representations remain explicit.                                                                     |
| PROP-22 | minor    | 03    | resolved  | Agents declare prerequisites; skills carry context only.                                                                                     |
| PROP-23 | major    | 03    | resolved  | `.current-work/` retains existing runtime path contracts.                                                                                    |
| PROP-24 | major    | 01    | resolved  | Housekeeping retains one inventory and three defined actions.                                                                                |
| PROP-25 | major    | 01    | resolved  | The evaluator reports evidence for every agent and required input. No regression.                                                            |
| PROP-26 | major    | 03    | resolved  | Installed runtime paths use `.agent-factory/factory/...`; the documented bootstrap exception is explicit. No regression.                     |

### Findings

| ID      | Severity | Check | Status   | Finding                                                                                                                                                                                                                                                                         |
| ------- | -------- | ----- | -------- | ------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| PROP-27 | major    | 03    | resolved | Deterministic fencing section defines validator selection from output declarations, required/optional behavior, minimum_changed, aggregate pass/fail, and evidence storage at `.agent-factory/checks/fences/`. No central registry — each agent's outputs name their validator. |
| PROP-28 | major    | 03    | resolved | Session binding carries `session_id`, `workstream_id`, `bound_at`. The `workstream_id` key must be present: known identifier = bound, `null` = Open Stage, missing key = invalid.                                                                                               |

### Check results

| #   | Check                            | Result                                                                                                       |
| --- | -------------------------------- | ------------------------------------------------------------------------------------------------------------ |
| 1   | Completion criteria testable     | Pass — fence evidence, session binding, and path resolution are fully specified.                             |
| 2   | Scope boundary sharp             | Pass — engine delegation, retry state, and counters are removed; external chaining is distinct and deferred. |
| 3   | Design decomposable              | Pass — fencing, session binding, and path resolution contracts are complete.                                 |
| 4   | Impact classification consistent | Pass — cross-component reach, both change flags, and declared boundaries match the revised Design.           |
| 5   | Boundary references exist        | Pass — all fifteen declared paths resolve in the reviewed working tree.                                      |
| 6   | Open questions genuine           | Pass — `None` is appropriate after nine review passes resolving twenty-eight findings.                       |
| 7   | Motivation justifies timing      | Pass — observed workflow friction and the window before further stage-model investment justify timing.       |
| 8   | Estimate plausible               | Pass — `unknown` remains preferable to an unsupported range after the scope change.                          |

### Summary

All twenty-eight findings across nine review passes are resolved. All eight checks pass. The proposal is planning-ready.
