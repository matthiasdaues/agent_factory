---
scope: activity-graph-orchestration
---

# EPICs — Activity-Graph Orchestration

Proposal trace: [activity-graph-orchestration.md](../docs/proposals/activity-graph-orchestration.md)
Feature spec: [activity-graph-orchestration.feature](../docs/spec/activity-graph-orchestration.feature)

## EPIC 1: Evaluate preconditions and select an activity

### Why this EPIC exists

Agent definitions today carry flat `inputs:` lists and `eligible_cycles:` fields. The engine checks cycle eligibility, not whether an agent's actual prerequisites exist in the repository. The developer cannot see which agents are ready to run or why. This EPIC restructures agent declarations, builds a precondition evaluator (engine module that checks whether required inputs exist and satisfy conditions), and exposes the results through an `intent select` command and the Project Work lane.

### Actor Goals

- Developer restructures agent and skill declarations from flat lists to structured `inputs.required`/`inputs.context` and `outputs` subkeys
- Developer runs `intent select` and sees every agent with each required input marked satisfied or unsatisfied, backed by evidence
- Developer selects any agent regardless of precondition status, with no override dialog or justification field
- Developer fixes an upstream artifact and re-runs the evaluator to see updated evidence
- Developer follows the precondition chain from proposal through implementation without named stage transitions

### Demo

1. Open `packages/factory/agents/architecture-agent.md` and observe the restructured frontmatter: `inputs.required` entries with `type`, `path_pattern`, and `conditions`; `inputs.context` entries as plain paths; `outputs.declarations` with `path_pattern`, `validator`, and `required`.
2. Run `intent select`. The terminal lists every agent with each required input shown as satisfied or unsatisfied. Evidence includes the checked path, condition, and result.
3. An agent shows one unsatisfied requirement: a proposal with `status: draft` does not satisfy the condition `field: status, value: accepted`.
4. Edit the proposal and set `status: accepted`.
5. Run `intent select` again. The previously unsatisfied requirement now shows as satisfied, with the accepted proposal path as evidence.
6. Select the agent with the unsatisfied requirement from step 3 (before fixing it). The agent is dispatched without a confirmation dialog.
7. In the Project Work lane, bind to a workstream. All agents appear with precondition evidence. Select one and proceed.

### Scope

**In:**

- Restructure all 17 agent definition frontmatter blocks — replace flat `inputs:` and `eligible_cycles:` with `inputs.required` (entries carry `type`, `path_pattern`, `conditions`) and `inputs.context` (plain paths), replace flat `outputs:` with `outputs.declarations` (entries carry `path_pattern`, `validator`, `required`) and `outputs.minimum_changed`
- Add `inputs.context` to skill definition frontmatter where skills reference reading material
- Update `index-lint` to parse the new declaration format and reject the old format
- Rewrite `packages/factory/engine/eligibility.py` as the precondition evaluator — read `inputs.required` declarations, resolve path patterns (glob expansion, scope filtering, condition checking, cardinality), report evidence per agent per requirement
- Build the `intent select` script at `packages/factory/scripts/intent` — call the evaluator, format output for the terminal
- Wire agent presentation into the Project Work lane after workstream binding — call the evaluator and display all agents with evidence
- Allow unrestricted agent selection: no filtering, no override dialog, no justification field
- Enable rework without ceremony: editing an artifact requires no state update; re-running the evaluator reflects the change
- Handle research agent outputs through the evaluator: research report satisfies downstream preconditions; no `origin_cycle` or `return_cycle` fields exist in research briefs
- Support a single delivery sequence from proposal through implementation under the activity model: each activity is selected based on satisfied preconditions, no named stage transitions

**Out:**

- Output fencing and validation (EPIC 2)
- Session menu restructuring (EPIC 3)
- Workstream state v2 and session binding file creation (EPIC 3)
- Scope declarations on governed artifacts (EPIC 5)
- Directory consolidation and path migration (EPIC 6)

### Dependencies

None. This is the foundational EPIC.

### Boundaries

- Engine: `packages/factory/engine/eligibility.py` (rewrite)
- Engine: `packages/factory/engine/readiness.py` (rewrite)
- Engine: `packages/factory/engine/recommendations.py` (rewrite)
- Agents: all 17 files in `packages/factory/agents/` (frontmatter restructure)
- Skills: all files in `packages/factory/skills/*/SKILL.md` that reference inputs (add `inputs.context`)
- Script: `packages/factory/scripts/intent` (new)
- Script: `packages/factory/scripts/index-lint` (parsing update)
- Config: `packages/factory/config/session-menu.md` (Project Work agent presentation)

### Domain Rules

- `inputs.required` entries carry `type` (artifact type), `path_pattern` (glob-like template), and `conditions` (optional)
- Condition types: `field` + `value` (frontmatter exact match), `field` + `one_of` (any listed value matches), `check` (named validator pass/fail)
- Path resolution runs four steps: glob expansion, scope filtering, condition checking, cardinality
- Zero survivors after filtering means unsatisfied; one survivor means satisfied; multiple survivors are reported for selection
- An agent with no `inputs.required` is always eligible
- Skills carry `inputs.context` only and do not appear in the precondition graph
- Evidence does not block selection — the developer can always pick any agent
- The precondition graph has no forward direction to violate; the developer works on any artifact at any time

### Size

4 stories.

### Building-Block Inventory

| Story   | Capability                                                                                                                                                                                                    | Tier     | Size | Basis                                                                                                                                                     |
| ------- | ------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- | -------- | ---- | --------------------------------------------------------------------------------------------------------------------------------------------------------- |
| ST-0262 | Restructure all 17 agent definitions and skill definitions with structured `inputs.required`/`inputs.context` and `outputs` declarations; update `index-lint` to parse and validate the new format            | standard | L    | 17 agent files, skill files, index-lint parser change; mechanical but broad; no new engine logic                                                          |
| ST-0263 | Build the precondition evaluator: rewrite `eligibility.py` to read `inputs.required`, resolve path patterns (glob expansion, scope filtering, condition checking, cardinality), and report evidence per agent | strong   | L    | Core engine rewrite; path resolution algorithm (4 steps); 3 condition types; evidence model; replaces cycle eligibility                                   |
| ST-0264 | Build `intent select` script and wire agent presentation into Project Work lane — call evaluator, format and display all agents with requirement evidence after workstream binding                            | standard | M    | CLI adapter + menu integration; calls evaluator; formats terminal output; no new engine logic                                                             |
| ST-0265 | Enable unrestricted selection, rework without ceremony, research routing, and end-to-end delivery sequence — behavioral properties of the evaluator                                                           | economy  | S    | No override dialog; evaluator re-checks on re-run; research output satisfies downstream preconditions; no origin_cycle/return_cycle; no stage transitions |

### Testability Assessment

All actor goals produce observable, assertable outcomes. Tests instrument: agent definition YAML files (structured `inputs.required`/`inputs.context`/`outputs` fields parsed by index-lint), `eligibility.py` function returns (evidence dicts with per-agent, per-requirement satisfied/unsatisfied status and checked paths), `intent select` stdout and exit code (formatted agent list with evidence), INDEX.yaml entries (new format accepted, old format rejected), session behavior (no confirmation dialog on unsatisfied selection), and evaluator re-run output (evidence reflects fixed artifacts). No red flags.

### Ownership Resolution

| Contract                | .feature Rule                                                         | Owner   | Rationale                                                                      |
| ----------------------- | --------------------------------------------------------------------- | ------- | ------------------------------------------------------------------------------ |
| Structured agent inputs | Agent definition declares required and contextual inputs              | ST-0262 | Introduces structured inputs.required/context format on all agent definitions  |
| Skill contextual inputs | Skill definition carries contextual inputs only                       | ST-0262 | Introduces inputs.context on skill definitions                                 |
| Evaluator evidence      | Precondition evaluator checks agent inputs against the repository     | ST-0263 | Introduces the evaluator that reads declarations and reports evidence          |
| Path resolution         | Precondition evaluator resolves path patterns with scope filtering    | ST-0263 | Introduces the path resolution algorithm (glob, scope, condition, cardinality) |
| Agent evidence display  | Human operator sees all agents with precondition evidence             | ST-0264 | Introduces intent select UI showing all agents with evidence                   |
| Intent select           | Intent select lists all agents with precondition status               | ST-0264 | Introduces the intent select script                                            |
| Unrestricted selection  | Human operator selects any agent regardless of precondition status    | ST-0265 | Introduces unrestricted selection with no override dialog                      |
| Ceremony-free rework    | Human operator fixes an upstream artifact without transition ceremony | ST-0265 | Introduces rework requiring no state update or ceremony                        |
| No-transition rework    | Rework requires no transition or state update                         | ST-0265 | Introduces the no-transition property of the activity model                    |
| Research routing        | Research brief uses the precondition graph for routing                | ST-0265 | Introduces research output satisfying downstream preconditions                 |
| Delivery sequence       | Single delivery sequence completes under the activity model           | ST-0265 | Introduces the stageless delivery sequence                                     |

## EPIC 2: Fence agent outputs and assess artifacts

### Why this EPIC exists

After an agent completes work, no deterministic check validates what it produced. The developer cannot tell whether outputs meet format and content requirements without manual inspection. This EPIC builds a fence runner (engine module that validates agent outputs after an activity) and an `intent assess` command. The fence checks whether declared outputs were created or modified, runs applicable validators, and stores evidence. Downstream agents can then rely on fence evidence when the evaluator checks preconditions.

### Actor Goals

- Developer sees a fence result after each agent activity, showing which declared outputs were created or modified and whether validators passed
- Developer runs `intent assess` to validate artifacts on disk and see results in the shared validator format
- Developer sees fence evidence carried forward into downstream precondition checks

### Demo

1. An agent definition declares `outputs.declarations` with two entries: one required (`backlog/ST-*.md`, validator `backlog-lint`, required `true`) and one optional (`docs/adr/*.md`, validator `adr-lint`, required `false`).
2. The agent activity completes. It created three story files and no ADR.
3. The fence runner (deterministic post-activity validator) checks: both required output patterns have matches. It runs `backlog-lint` against the new story files. All pass. The optional ADR output has no matches — the fence skips it.
4. The fence result is stored at `.agent-factory/checks/fences/<session-id>/<invocation-id>.yaml`. The result shows: required output satisfied, validator passed, optional output skipped.
5. The developer runs `intent assess`. The command runs all applicable validators against artifacts on disk and reports results: artifact type, artifact reference, assessed commit, individual checks, and warnings.
6. The evaluator checks a downstream agent. The fence evidence from step 4 satisfies the downstream agent's `inputs.required` entry that references story files.

### Scope

**In:**

- Build the fence runner at `packages/factory/engine/fencing.py` — snapshot output patterns before invocation, compare after, run validators, check required/optional/minimum_changed, aggregate pass/fail, store evidence
- Define the fence evidence format at `.agent-factory/checks/fences/<session-id>/<invocation-id>.yaml`
- Build the `intent assess` script at `packages/factory/scripts/intent` (subcommand) — run validators, format results in the shared validator result format
- Wire fence results into the precondition evaluator so downstream agents see fence evidence

**Out:**

- Agent definition restructuring (EPIC 1 delivers the `outputs` declarations this EPIC reads)
- New validators (this EPIC calls existing validators; creating new ones is per-agent story work)

### Dependencies

EPIC 1 (the fence runner reads `outputs.declarations` from agent definitions; the `intent assess` command uses the evaluator's evidence model).

### Boundaries

- Engine: `packages/factory/engine/fencing.py` (new)
- Engine: `packages/factory/engine/eligibility.py` (wire fence evidence into evaluator)
- Script: `packages/factory/scripts/intent` (add `assess` subcommand)
- Runtime: `.agent-factory/checks/fences/` (evidence storage)

### Domain Rules

- The fence snapshots output path patterns before the activity and compares after
- A required output with no created or modified match fails the fence
- An optional output without a match is skipped; if a match changed, its validator runs
- Fewer than `minimum_changed` declarations with changes fails the fence
- Aggregate passes only when: all required outputs changed, minimum met, every invoked validator passed
- Evidence is stored at `.agent-factory/checks/fences/<session-id>/<invocation-id>.yaml`
- Fence failure is reported without blocking the developer

### Size

2 stories.

### Building-Block Inventory

| Story   | Capability                                                                                                                                                                   | Tier     | Size | Basis                                                                                                           |
| ------- | ---------------------------------------------------------------------------------------------------------------------------------------------------------------------------- | -------- | ---- | --------------------------------------------------------------------------------------------------------------- |
| ST-0266 | Build the fence runner: snapshot outputs, invoke validators, check required/optional/minimum_changed, aggregate pass/fail, store evidence at `.agent-factory/checks/fences/` | strong   | L    | New engine module; snapshot/compare logic; validator invocation; evidence format; integration with evaluator    |
| ST-0267 | Build `intent assess` subcommand: run validators against artifacts on disk, report results in the shared validator format                                                    | standard | M    | CLI adapter calling validators; format terminal output; no new engine logic beyond invoking existing validators |

### Testability Assessment

All actor goals produce observable, assertable outcomes. Tests instrument: fence evidence YAML files at `.agent-factory/checks/fences/<session-id>/<invocation-id>.yaml` (field checks for required/optional status, validator results, aggregate pass/fail), `intent assess` stdout and exit code (validator result format: artifact type, reference, assessed commit, checks, warnings), and the evaluator's evidence model (downstream precondition satisfied when fence passes, unsatisfied when fence fails). No red flags.

### Ownership Resolution

| Contract              | .feature Rule                                           | Owner   | Rationale                                                                   |
| --------------------- | ------------------------------------------------------- | ------- | --------------------------------------------------------------------------- |
| Deterministic fencing | Every agent activity is fenced by a deterministic check | ST-0266 | Introduces the fence runner with snapshot, validation, and evidence storage |
| Artifact assessment   | Intent assess runs validators and reports results       | ST-0267 | Introduces the assess subcommand calling validators                         |

## EPIC 3: Navigate the session menu and manage workstreams

### Why this EPIC exists

The session menu today offers five options (A through E) with no clear separation between help, maintenance, and project work. Workstream state files carry cycle-era fields (`current_cycle`, `attempt`, `delegation`, `work`) and live under `.current-work/cycles/`. Session bindings reference cycle concepts. This EPIC restructures the menu into four lanes (Help, Housekeeping, Project Work, Open Stage), implements workstream state v2 (immutable identity-only files), and creates a session binding format that attaches sessions to workstreams without cycle vocabulary.

### Actor Goals

- Developer sees a four-lane session menu: H (Help), K (Housekeeping), P (Project Work), O (Open Stage)
- Developer creates a new workstream (persistent identity for one body of work) through the Project Work lane, with an immutable state file recording only identity fields
- Developer continues an existing workstream by selecting it from a list and seeing agents with precondition evidence
- Developer enters Open Stage for freeform conversation with no workstream binding

### Demo

1. Start a factory session. The menu displays four lanes: H (Help), K (Housekeeping), P (Project Work), O (Open Stage).
2. Select H. The session routes to the newcomer-tour or guided-tour skill.
3. Return to the menu. Select O. VIRGIL enters freeform conversation. No workstream binding is created.
4. Return to the menu. Select P. No workstream exists yet. The developer provides a topic description.
5. A workstream state file is created at `.agent-factory/workstreams/<workstream-id>.yaml`. Inspect the file: it contains `schema_version: 2`, `workstream_id`, `topic`, and `origin_ref`. No other fields exist.
6. A session binding file is created at `.agent-factory/workstreams/sessions/<session-id>.yaml`. It records `session_id`, `workstream_id`, and `bound_at`.
7. Start a new session. Select P, choose to continue. The workstream from step 4 appears in the list. Select it. Agents appear with precondition evidence.
8. Verify that no v1 cycle state files remain under `.current-work/cycles/`.

### Scope

**In:**

- Rewrite `packages/factory/config/session-menu.md` with four lanes: H routes to tour skills, K routes to Housekeeping (EPIC 4), P routes to Project Work (workstream creation/continuation), O routes to VIRGIL for freeform conversation
- Implement workstream state v2: state files at `.agent-factory/workstreams/<workstream-id>.yaml` with `schema_version: 2`, `workstream_id`, `topic`, `origin_ref`; immutable after creation
- Implement session binding: binding files at `.agent-factory/workstreams/sessions/<session-id>.yaml` with `session_id`, `workstream_id`, `bound_at`; known identifier means bound, null means Open Stage, missing key fails validation
- Wire the Project Work lane: create new workstream or list/continue existing; bind session; call evaluator to present agents with evidence after binding
- Delete v1 cycle state files from `.current-work/cycles/` and v1 session binding files from `.current-work/session-bindings/`
- Create `.agent-factory/workstreams/` and `.agent-factory/workstreams/sessions/` directories

**Out:**

- Housekeeping lane actions (EPIC 4)
- Precondition evaluator and agent presentation logic (EPIC 1 delivers these; this EPIC calls them)
- Scope filtering in the evaluator based on workstream binding (EPIC 5)

### Dependencies

EPIC 1 (the Project Work lane calls the evaluator to present agents with evidence after workstream binding; EPIC 1 must deliver the evaluator and `intent select`).

### Boundaries

- Config: `packages/factory/config/session-menu.md` (rewrite)
- Agent: `packages/factory/agents/virgil.md` (Open Stage routing update)
- Runtime: `.agent-factory/workstreams/` (new directory, state files)
- Runtime: `.agent-factory/workstreams/sessions/` (new directory, binding files)
- Runtime: `.current-work/cycles/` (delete v1 files)
- Runtime: `.current-work/session-bindings/` (delete v1 files)

### Domain Rules

- Workstream state file contains only: `schema_version: 2`, `workstream_id`, `topic`, `origin_ref`; no other fields
- The state file is immutable after creation — modification attempts fail
- Session binding records `session_id`, `workstream_id` (must be present), `bound_at`
- `workstream_id` with a known identifier means bound; explicit null means Open Stage; missing key fails validation
- Multiple sessions can bind to the same workstream; the state file stays unchanged
- Selecting a different workstream updates the binding, not the state file
- Open Stage creates a session binding with `workstream_id: null`

### Size

3 stories.

### Building-Block Inventory

| Story   | Capability                                                                                                                                   | Tier     | Size | Basis                                                                                                               |
| ------- | -------------------------------------------------------------------------------------------------------------------------------------------- | -------- | ---- | ------------------------------------------------------------------------------------------------------------------- |
| ST-0268 | Restructure session menu to four lanes (H, K, P, O) with routing to tour skills, Housekeeping stub, Project Work, and Open Stage             | economy  | M    | Rewrite session-menu.md; update VIRGIL routing; no engine logic; mostly configuration and prose                     |
| ST-0269 | Implement workstream state v2 (immutable identity-only files) and session binding format; delete v1 cycle state and session binding files    | standard | L    | New state file format; immutability enforcement; binding creation; v1 cleanup; directory creation; validation logic |
| ST-0270 | Wire Project Work lane for workstream creation and continuation — create or list workstreams, bind session, call evaluator to present agents | standard | M    | Menu integration; list/select workflow; session binding creation; evaluator call; depends on ST-0263 and ST-0269    |

### Testability Assessment

All actor goals produce observable, assertable outcomes. Tests instrument: session-menu.md content (menu text matching four lanes H/K/P/O), workstream state files at `.agent-factory/workstreams/<id>.yaml` (YAML field checks for schema_version, workstream_id, topic, origin_ref; absence of other fields), session binding files at `.agent-factory/workstreams/sessions/<id>.yaml` (field checks for session_id, workstream_id, bound_at), file system for v1 deletion (absence of files under `.current-work/cycles/` and `.current-work/session-bindings/`), and immutability enforcement (write attempt returns error, file unchanged). No red flags.

### Ownership Resolution

| Contract                   | .feature Rule                                      | Owner   | Rationale                                                           |
| -------------------------- | -------------------------------------------------- | ------- | ------------------------------------------------------------------- |
| Four-lane menu             | Session menu presents four lanes                   | ST-0268 | Introduces the restructured menu with H/K/P/O lanes                 |
| Immutable workstream state | Workstream state file is immutable after creation  | ST-0269 | Introduces workstream state v2 with immutability enforcement        |
| Session binding format     | Session binding attaches a session to a workstream | ST-0269 | Introduces the session binding file format and validation           |
| Start workstream           | Human operator starts a new workstream             | ST-0270 | Introduces workstream creation through the Project Work lane        |
| Continue workstream        | Human operator continues an existing workstream    | ST-0270 | Introduces workstream listing and continuation through Project Work |

## EPIC 4: Inspect factory state and run maintenance

### Why this EPIC exists

The current menu has no dedicated place to inspect factory health or run maintenance tasks. The developer cannot see the installed version, fitting status, or usage pipeline health without reading files manually. The `capture-context` skill lacks an `--update --scan` mode for refreshing `docs/agent-context.md` (concern registry that maps domain and technical concerns to source files). This EPIC builds the Housekeeping lane actions: About (state display), Re-fit, Update Factory, and Update agent context.

### Actor Goals

- Developer opens the Housekeeping lane and sees installed version, fitting status, configured CLI integrations, and usage pipeline health
- Developer runs Re-fit to rerun all five fitting steps
- Developer runs Update Factory to install the latest factory version and refresh the About display
- Developer runs Update agent context to scan the repository, compare concerns and Read paths against `docs/agent-context.md`, confirm changes, and verify with `concern-lint`

### Demo

1. Start a factory session. Select K (Housekeeping).
2. The About section shows: installed Factory version, fitting status (3/5 done), configured CLI integrations (Claude, Codex), usage pipeline health (healthy). One value is unreadable — it shows "unknown" with the source error.
3. Select Re-fit. The factory runs all five fitting steps and reports results.
4. Select Update Factory. The factory runs `init-factory --update --force`, relays the command output, and refreshes the About section.
5. Select Update agent context. The factory runs `capture-context --update --scan`. It discovers a new technical concern not in `docs/agent-context.md`. The difference is presented. The developer confirms. The concern is added. `concern-lint` passes.
6. Select Update agent context again, but `docs/agent-context.md` does not exist. The factory directs the developer to run `capture-context --init --scan` instead.

### Scope

**In:**

- Build the Housekeeping About section — read installed version from `install.json`, fitting status from `project-context.json`, CLI integrations from project configuration, usage pipeline health from usage state; show "unknown" with source error for unreadable values
- Build Re-fit action — rerun all five fitting steps, report completed and remaining steps
- Build Update Factory action — run `init-factory --update <project-root> --force`, relay output and exit status, refresh About
- Extend `capture-context` with `--update --scan` mode — require existing `docs/agent-context.md`, scan repository and documentation, compare discovered concerns and Read paths with existing file, present differences, write confirmed changes, verify with `concern-lint`
- Handle missing `docs/agent-context.md` — direct developer to `--init --scan`

**Out:**

- Session menu restructuring (EPIC 3 delivers the four-lane menu; this EPIC fills the K lane)
- Changes to the fitting procedure itself (Re-fit calls the existing procedure)

### Dependencies

EPIC 3 (soft — the Housekeeping lane exists in the four-lane menu; this EPIC fills its content. The Housekeeping stub from EPIC 3 is sufficient to start, but the full menu must exist for end-to-end demo).

### Boundaries

- Config: `packages/factory/config/session-menu.md` (Housekeeping lane content)
- Skill: `packages/factory/skills/capture-context/SKILL.md` (add `--update --scan` mode)
- Script: `packages/factory/scripts/concern-lint` (called after context update, not modified)

### Domain Rules

- About section shows: installed version, fitting status, CLI integrations, usage pipeline health
- Unreadable values appear as "unknown" with their source error
- Re-fit reruns all five fitting steps (model matrix, fingerprint, agent context, test regime, hooks)
- Update Factory runs `init-factory --update <project-root> --force`, relays output, refreshes About on success
- `capture-context --update --scan` requires existing `docs/agent-context.md`; absent file directs to `--init --scan`
- Changes from the scan are written only after developer confirmation
- `concern-lint` must pass after writing changes

### Size

2 stories.

### Building-Block Inventory

| Story   | Capability                                                                                                                                                                            | Tier     | Size | Basis                                                                                                                                                                                           |
| ------- | ------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- | -------- | ---- | ----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| ST-0271 | Build Housekeeping About section displaying factory state, and Re-fit/Update Factory actions that rerun fitting and install updates                                                   | standard | M    | Read from 4 sources (install.json, project-context.json, project config, usage state); Re-fit calls existing procedure; Update Factory calls init-factory; error handling for unreadable values |
| ST-0272 | Extend `capture-context` with `--update --scan` mode: scan repository, compare with existing agent-context.md, present differences, write confirmed changes, verify with concern-lint | standard | L    | New mode for existing skill; repository scanning; diffing concerns and Read paths; interactive confirmation; concern-lint integration; guard for missing file                                   |

### Testability Assessment

All actor goals produce observable, assertable outcomes. Tests instrument: About section terminal output (version string, fitting status counts, CLI integration names, health indicator, "unknown" with error for unreadable sources), init-factory exit code and stdout (Update Factory), fitting procedure results (Re-fit), capture-context skill output (discovered differences, confirmed changes), concern-lint exit code (passes after writing). The "unreadable values" scenario is testable by removing or corrupting the source file. No red flags.

### Ownership Resolution

| Contract                           | .feature Rule                                                   | Owner   | Rationale                                                        |
| ---------------------------------- | --------------------------------------------------------------- | ------- | ---------------------------------------------------------------- |
| Housekeeping state and maintenance | Housekeeping shows factory state and offers maintenance actions | ST-0271 | Introduces the About section, Re-fit, and Update Factory actions |

## EPIC 5: Declare and enforce artifact scope

### Why this EPIC exists

The precondition evaluator (EPIC 1) filters candidates by workstream scope, but no governed artifact (artifact type that must carry a scope declaration) carries a scope declaration today. Without scope declarations, scope filtering passes every candidate — the evaluator cannot distinguish which artifacts belong to which workstream. This EPIC defines scope declarations for seven governed artifact types and builds `scope-lint` to validate them.

### Actor Goals

- Developer adds a scope field to each governed artifact in the format required by its type (YAML frontmatter, top-level YAML, or first-line comment)
- Developer runs `scope-lint` and sees validation results: missing declarations, unknown scope values, correct declarations
- Developer creates a new governed artifact and receives a lint rejection if the scope declaration is missing or carries an unknown value

### Demo

1. Create a proposal under `docs/proposals/` without a `scope` field in the YAML frontmatter.
2. Run `scope-lint`. The lint rejects the proposal and names the missing declaration.
3. Add `scope: my-workstream` to the proposal frontmatter. Run `scope-lint` again. The lint rejects it: `my-workstream` is not a known workstream identifier.
4. Create a workstream with identifier `my-workstream`. Run `scope-lint`. The proposal passes.
5. Open `docs/spec/activity-graph-orchestration.feature`. The first line reads `# scope: activity-graph-orchestration`.
6. Open `docs/arc42/architecture.dsl`. The first line reads `// scope: global`.
7. Open `docs/spec/supplementary_specs/entity-model.yaml`. The top-level YAML contains `scope: global`.
8. Run `scope-lint` across all governed artifacts. All pass. An ADR under `docs/adr/` is skipped — non-governed artifacts need no scope declaration.

### Scope

**In:**

- Define scope declaration format for each governed artifact type:
  - Proposals: `scope` in YAML frontmatter (replaces `title` field; display name moves to the document heading)
  - Epics: `scope` in YAML frontmatter
  - Stories: `scope` in YAML frontmatter
  - Gherkin feature files: first-line comment `# scope: <value>`
  - Structurizr DSL: first-line comment `// scope: global`
  - Entity model YAML: top-level YAML field `scope: <value>`
  - Scope map: `scope` in YAML frontmatter with value `global`
- Build `scope-lint` script at `packages/factory/scripts/scope-lint` — check each governed artifact for presence and valid value; reject missing declarations and unknown scope values; skip non-governed artifacts
- Add scope declarations to existing governed artifacts in the repository
- Wire scope-lint into the evaluator's scope filtering step (EPIC 1 builds filtering; this EPIC provides the declarations it reads)

**Out:**

- Precondition evaluator logic (EPIC 1)
- Workstream creation (EPIC 3 creates workstreams whose identifiers become valid scope values)

### Dependencies

EPIC 3 (scope-lint validates scope values against known workstream identifiers; EPIC 3 creates workstreams).

### Boundaries

- Script: `packages/factory/scripts/scope-lint` (new)
- Artifacts: all existing proposals, epics, stories, feature files, DSL, entity model, scope map (add scope declarations)
- Engine: `packages/factory/engine/eligibility.py` (scope filtering reads declarations; integration point)

### Domain Rules

- Seven governed artifact types: proposals, epics, stories, features, architecture.dsl, scope-map.md, entity-model.yaml
- Proposals carry scope in YAML frontmatter, replacing the title field; display name is in the document heading
- Epics, stories, and scope-map carry scope in YAML frontmatter
- Feature files carry scope as a first-line comment: `# scope: <value>`
- Structurizr DSL carries scope as a first-line comment: `// scope: global`
- Entity model YAML carries scope as a top-level field
- Valid scope values: a known workstream identifier, or `global`
- A governed artifact without a scope declaration fails lint
- A governed artifact with an unknown scope value fails lint
- Non-governed artifacts (ADRs, conventions, templates) need no scope declaration

### Size

2 stories.

### Building-Block Inventory

| Story   | Capability                                                                                                                                                   | Tier     | Size | Basis                                                                                                                              |
| ------- | ------------------------------------------------------------------------------------------------------------------------------------------------------------ | -------- | ---- | ---------------------------------------------------------------------------------------------------------------------------------- |
| ST-0273 | Build `scope-lint` script that validates scope declarations across 7 governed artifact types, checking presence, format, and value against known workstreams | standard | M    | New script; 3 format representations (YAML frontmatter, top-level YAML, first-line comment); workstream lookup; rejection messages |
| ST-0274 | Add scope declarations to all existing governed artifacts and wire scope-lint into the evaluator's scope filtering step                                      | economy  | M    | Mechanical across many files (proposals, epics, stories, features, DSL, entity model, scope map); integration point in evaluator   |

### Testability Assessment

All actor goals produce observable, assertable outcomes. Tests instrument: governed artifact files (YAML frontmatter `scope` field, first-line comment format, top-level YAML field), scope-lint stdout and exit code (rejection messages for missing or unknown values, pass for valid declarations), and the evaluator's scope filtering results (candidate list narrowed by workstream). Non-governed artifacts (ADRs, conventions) are checked to confirm they are skipped. No red flags.

### Ownership Resolution

| Contract           | .feature Rule                                          | Owner   | Rationale                                                                 |
| ------------------ | ------------------------------------------------------ | ------- | ------------------------------------------------------------------------- |
| Scope declarations | Graph-addressable artifact carries a scope declaration | ST-0273 | Introduces scope-lint and the declaration format for all 7 governed types |

## EPIC 6: Consolidate layout, retire orchestrator, assure compatibility

### Why this EPIC exists

Factory-delivered content is spread across three top-level directories (`factory/`, `config/`, `.agent-factory/`) with inconsistent naming (prefixed `factory-install.json`, `factory-checksums.json`) and sibling usage directories (`usage-analysis/`, `usage-control/`, `usage-runtime/`). The `packages/orchestrator/` package was created for cycle-based orchestration and is now superseded. Every script, agent definition, and path reference must point to the consolidated layout before the old directories can be removed. This EPIC moves all factory content under `.agent-factory/`, retires the orchestrator, and writes characterization tests to verify that existing contracts survive the migration.

### Actor Goals

- Developer runs `init-factory` and finds all factory content under `.agent-factory/`: scripts, agents, skills, rulebooks, engine at `.agent-factory/factory/`; project configuration at `.agent-factory/config/`; usage state under `.agent-factory/usage/`
- Developer verifies that no top-level `factory/` or `config/` directory exists after installation
- Developer verifies that `packages/orchestrator/` no longer exists and no reference to it remains
- Developer runs characterization tests (tests that verify existing contracts survive the migration) and confirms that every standard check, branch safety command, and indexed agent/skill name from the acceptance commit still works

### Demo

1. Run `init-factory`. Inspect the project root: `.agent-factory/factory/` contains scripts, agents, skills, rulebooks, and engine. `.agent-factory/config/` contains `project-context.json` and `testing.yaml`. No top-level `factory/` or `config/` directory exists.
2. Inspect `.agent-factory/`: `install.json` exists (not `factory-install.json`); `checksums.json` exists (not `factory-checksums.json`).
3. Inspect `.agent-factory/usage/`: records, transcripts, control, and `store.duckdb` are under `usage/` subfolders. No sibling `usage-analysis/`, `usage-control/`, `usage-runtime/` directories exist.
4. Inspect `.current-work/`: worktrees, dispatch ledgers, and verification markers are unchanged.
5. Verify that `packages/orchestrator/` does not exist. Search documentation and backlog — no file references the orchestrator package.
6. Run characterization tests: every standard check retains its command name, triggers, result format, and exit behavior. `verify-base` and `premerge-check` retain their contracts. Every indexed agent and skill name from the acceptance commit still exists.
7. Inspect `docs/proposals/cycle-based-orchestration.md`: frontmatter `status` is `superseded`.

### Scope

**In:**

- Update `init-factory` to install factory content at `.agent-factory/factory/` instead of `factory/`; install project configuration at `.agent-factory/config/` instead of `config/`
- Rename installed metadata files: `factory-install.json` to `install.json`, `factory-checksums.json` to `checksums.json`
- Consolidate usage directories: collapse `usage-analysis/`, `usage-control/`, `usage-runtime/` into `.agent-factory/usage/` subfolders (records, transcripts, control, store.duckdb)
- Update all path references in scripts, hooks, agent definitions, skill definitions, CLI index files, session menu, and `.gitignore` to use `.agent-factory/` paths
- Keep `.current-work/` unchanged for worktrees, dispatch ledgers, and verification markers
- Delete `packages/orchestrator/` directory; remove all references from documentation, backlog, and CI configuration
- Migrate still-needed tests from `packages/orchestrator/` to `packages/factory/engine/` or the appropriate package
- Set `status: superseded` on `docs/proposals/cycle-based-orchestration.md` frontmatter
- Write characterization tests verifying: standard check command contracts, branch safety command contracts, and indexed agent/skill name preservation

**Out:**

- Workstream state files and session bindings (EPIC 3 writes these to `.agent-factory/workstreams/`)
- Quality gate result storage at `.agent-factory/checks/` (EPIC 2 writes fence evidence there)
- Transcript storage at `.agent-factory/usage/transcripts/` (EPIC 7)

### Dependencies

None. This EPIC can proceed in parallel with EPICs 1-5. Path references in agent definitions updated by EPIC 1 should use `.agent-factory/` paths; coordinate with EPIC 1 on the final path format.

### Boundaries

- Script: `packages/factory/scripts/init-factory` (output path change, metadata rename)
- All scripts in `packages/factory/scripts/` (path reference updates)
- All agents in `packages/factory/agents/` (path reference updates)
- All skills in `packages/factory/skills/*/SKILL.md` (path reference updates)
- Config: `.gitignore` (update ignore patterns)
- Package: `packages/orchestrator/` (delete)
- Proposal: `docs/proposals/cycle-based-orchestration.md` (status change)
- Tests: `packages/factory/engine/` or `tests/` (characterization tests, migrated tests)

### Domain Rules

- All factory-delivered content lives under `.agent-factory/`
- `factory/` moves to `.agent-factory/factory/`; `config/` moves to `.agent-factory/config/`
- `factory-install.json` becomes `install.json`; `factory-checksums.json` becomes `checksums.json`
- Usage siblings collapse into `.agent-factory/usage/` subfolders
- `.current-work/` retains all existing path contracts unchanged
- `packages/orchestrator/` is deleted; no references remain in any file
- Still-needed tests migrate to `packages/factory/engine/` or the appropriate package
- Every standard check retains its command name, triggers, result format, and exit behavior after migration
- Every indexed agent and skill name from the acceptance commit still exists in the post-migration index

### Size

3 stories.

### Building-Block Inventory

| Story   | Capability                                                                                                                                                                                           | Tier     | Size | Basis                                                                                                                      |
| ------- | ---------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- | -------- | ---- | -------------------------------------------------------------------------------------------------------------------------- |
| ST-0275 | Consolidate factory layout under `.agent-factory/` — update init-factory output paths, rename metadata files, collapse usage directories, update all path references in scripts/agents/skills/config | strong   | XL   | Touches every script, agent, skill, and config file; init-factory rewrite; .gitignore; high coordination across boundaries |
| ST-0276 | Retire `packages/orchestrator/` — delete directory, remove all references from docs/backlog/CI, migrate still-needed tests                                                                           | standard | M    | Deletion and reference cleanup; test migration from orchestrator to factory engine; grep-and-fix across docs               |
| ST-0277 | Supersede cycle-based orchestration proposal and write characterization tests verifying standard checks, branch safety commands, and indexed name preservation                                       | standard | M    | Proposal status change; characterization tests for 3 contract areas; tests run against post-migration state                |

### Testability Assessment

All actor goals produce observable, assertable outcomes. Tests instrument: file system paths (`.agent-factory/factory/`, `.agent-factory/config/`, absence of `factory/`, `config/`, `packages/orchestrator/`), installed metadata files (`install.json`, `checksums.json`), init-factory exit code, INDEX.yaml entries (agent and skill name preservation), proposal YAML frontmatter (`status: superseded`), and characterization test pass/fail via pytest. No red flags.

### Ownership Resolution

| Contract                | .feature Rule                                      | Owner   | Rationale                                                                  |
| ----------------------- | -------------------------------------------------- | ------- | -------------------------------------------------------------------------- |
| Layout consolidation    | Factory content consolidates under .agent-factory/ | ST-0275 | Introduces the consolidated directory layout and init-factory path changes |
| Orchestrator retirement | Orchestrator package is retired                    | ST-0276 | Introduces orchestrator deletion and reference cleanup                     |
| Proposal supersession   | Cycle-based orchestration proposal is superseded   | ST-0277 | Introduces the superseded status on the cycle proposal                     |
| Contract preservation   | Kept contracts preserve acceptance-commit behavior | ST-0277 | Introduces characterization tests verifying command and name contracts     |

## EPIC 7: Retain structured transcripts

### Why this EPIC exists

The usage capture pipeline today renders transcripts as text only. Structured data (tool calls, timing, token counts) is lost at capture time. Downstream analysis requires parsing unstructured text. This EPIC adds a structured JSONL retention path: the capture pipeline copies the source transcript verbatim alongside the text rendering, so both representations are available for analysis.

### Actor Goals

- Developer sees a structured JSONL file alongside the text rendering after usage capture processes a session
- Developer finds both files under the same session key at `.agent-factory/usage/transcripts/<session-key>/`
- Developer sees no files written when retention is set to omit

### Demo

1. Complete a factory session with transcript retention set to `full`.
2. The usage capture pipeline processes the session.
3. Inspect `.agent-factory/usage/transcripts/<session-key>/`. Two files exist: the text rendering and a `.structured.jsonl` file.
4. The `.structured.jsonl` file is a verbatim copy of the source transcript.
5. Set retention to `omit`. Complete another session. No text rendering and no structured transcript are written.

### Scope

**In:**

- Modify the usage capture pipeline to copy the source transcript as a `.structured.jsonl` file alongside the text rendering at capture time
- Store both files under `.agent-factory/usage/transcripts/<session-key>/`
- Respect retention setting: `full` writes both files; `omit` writes neither

**Out:**

- Analysis tooling that reads the structured JSONL (future work)
- Changes to the text rendering format
- Directory consolidation of usage paths (EPIC 6)

### Dependencies

EPIC 6 (the transcript storage path `.agent-factory/usage/transcripts/` is created by the layout consolidation; this EPIC writes files there).

### Boundaries

- Script/skill: usage capture pipeline (add structured copy step)
- Runtime: `.agent-factory/usage/transcripts/<session-key>/` (new file alongside existing)

### Domain Rules

- Structured JSONL is a verbatim copy of the source transcript
- File is stored alongside the text rendering: `<record-id>.structured.jsonl`
- `retention=full`: both files are written
- `retention=omit`: neither file is written

### Size

1 story.

### Building-Block Inventory

| Story   | Capability                                                                                         | Tier    | Size | Basis                                                                                     |
| ------- | -------------------------------------------------------------------------------------------------- | ------- | ---- | ----------------------------------------------------------------------------------------- |
| ST-0278 | Retain structured JSONL alongside text rendering at capture time, respecting the retention setting | economy | S    | Single copy step in existing pipeline; conditional on retention flag; no new engine logic |

### Testability Assessment

All actor goals produce observable, assertable outcomes. Tests instrument the usage capture pipeline's output directory at `.agent-factory/usage/transcripts/<session-key>/`: file existence checks confirm the JSONL file appears alongside the text rendering, byte-level comparison confirms verbatim content, and the omit case checks that neither file is written. No red flags.

### Ownership Resolution

| Contract                        | .feature Rule                                | Owner   | Rationale                                              |
| ------------------------------- | -------------------------------------------- | ------- | ------------------------------------------------------ |
| Structured transcript retention | Usage capture retains structured transcripts | ST-0278 | Introduces the JSONL copy step in the capture pipeline |
