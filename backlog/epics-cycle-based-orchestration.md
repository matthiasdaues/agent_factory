# EPICs — Cycle-Based Orchestration

Proposal trace: [cycle-based-orchestration.md](../docs/proposals/cycle-based-orchestration.md)
Specification trace: [cycle-based-orchestration.feature](../docs/spec/cycle-based-orchestration.feature)
Architecture trace: [ADR-0017](../docs/adr/0017-cycle-based-orchestration-supersedes-linear-playbook-fsm.md), [§5.3 Cycle Engine](../docs/arc42/05_building_block_view.md#53-level-2-component-view----cycle-engine), [§5.4 State Adapter](../docs/arc42/05_building_block_view.md#54-level-2-component-view----state-adapter)
QA strategy trace: [cycle-based-orchestration-qa-strategy.md](../docs/spec/cycle-based-orchestration-qa-strategy.md)
Gaps trace: [cycle-based-orchestration-gaps.md](../docs/spec/cycle-based-orchestration-gaps.md)

Dependency order: EPICs 1 and 7 start immediately in parallel. EPICs 2 and 6 follow EPIC 1. EPICs 3, 5, and 9 follow EPIC 2. EPIC 4 follows EPIC 3. EPIC 8 follows EPICs 2 and 7.

Story identifiers in the building-block inventories are provisional. Phase 4 allocates the final identifiers against the backlog at the time of writing.

## Shared vocabulary

These terms appear in every EPIC. Each is defined once here and used without repetition afterwards.

- **Workstream** — one traversal of the delivery graph, recorded as one YAML file under `.current-work/cycles/`. A repository may hold several at once.
- **Cycle** — the workstream's current stage. The engine models five stages — IDEA, CONCEPT, ROADMAP, REFINE, and REALIZE — plus a terminal DONE node.
- **Route** — a declared edge from one cycle to another, carrying the evidence that would support recommending it.
- **Delivery model** — the YAML file that declares every cycle, artifact, and route.
- **Cycle engine** — the code that computes decisions. It reads the repository and never writes to it.
- **State adapter** — the commands that write files. Each asks the engine for a decision, then records the result.
- **Session binding** — a file recording which workstream the current command-line session is working on.
- **Delegation grant** — a human-authored record that lets the engine advance through named cycles without asking again.
- **Trusted validator** — a named check that reports one artifact's readiness. The delivery model refers to it by identifier and can never carry a shell command.

## EPIC 1: Start, continue, and switch delivery workstreams without losing data under concurrent use

### Why this EPIC exists

The factory routes work today through one repository-wide marker and a fixed playbook sequence. A user who starts two pieces of work overwrites the first with the second. An interrupted session has nothing to return to. Two sessions writing to the same file cause silent data loss. This EPIC delivers the workstream infrastructure — naming topics, resuming them, switching between them, and refusing a stale write rather than applying it.

### Actor Goals

- Human operator starts a named workstream from the session menu and enters IDEA
- Human operator lists current workstreams with their topics and cycles, then continues one
- Human operator receives a suggestion to open a separate workstream when the conversation turns to a different objective, and confirms every switch
- State adapter replaces a workstream file atomically, increments the revision, and refuses a write from a stale session
- State adapter serializes two sessions on one workstream while leaving different workstreams independent

### Demo

01. Select option B in the session menu and give the topic "Add rate limiting to the public API".
02. Read `.current-work/cycles/add-rate-limiting.yaml` and confirm it records the topic, cycle IDEA, revision 1, and attempt 1.
03. Confirm that a session binding file exists for the current session.
04. Create a second workstream on a different topic and leave both at different cycles.
05. Start a fresh session and select option C. Both topics appear with their current cycles.
06. Select the second workstream. The session binding records that workstream's revision and digest.
07. Begin describing unrelated work. The factory suggests opening a separate workstream and waits. Decline the suggestion.
08. Continue on the same unrelated objective. The factory does not repeat the suggestion.
09. Bind session A and session B to the same workstream at revision 5.
10. Write from session A. The state file reaches revision 6.
11. Write from session B with expected revision 5. The command returns `stale_workstream_state` and writes nothing.
12. Hold the lock in session A and attempt a write from session B. After five seconds session B returns `workstream_busy`.
13. Write to a second workstream from session B while session A holds the first lock. The write succeeds immediately.
14. Interrupt a replacement mid-write. The state file holds one complete version.

### Scope

**In:**

- Engine package scaffold — create `packages/factory/engine/` with package metadata and a dependency boundary that forbids the engine from importing scripts, configuration, agent definitions, skills, or the orchestrator
- Cycle-state schema — `packages/factory/engine/schemas/cycle-state-v1.schema.json`, JSON Schema Draft 2020-12, defining workstream_id, topic, origin_ref, cycle, attempt, revision, work list, and delegation grant
- Workstream creation from session menu option B — capture the topic and optional originating proposal path, write the state file at `.current-work/cycles/<workstream-id>.yaml` with cycle IDEA, revision 1, and attempt 1, and create the session binding
- Session menu option C — list every workstream with its topic and cycle, bind the selected workstream, and present its recommendations; when no workstream exists, offer option B or a return to the menu
- Session binding records — write the observed revision and SHA-256 digest of the state file at bind time, using the existing usage-capture filesystem-key encoding for the path
- Workstream switch suggestion — detect an explicit topic change, a new proposal reference, or a different deliverable, suggest creating or reopening a workstream, and wait for confirmation; record a declined suggestion so the same boundary is not raised twice
- Usage boundary capture on a confirmed switch, when the producing command-line tool supports it
- Exclusive file lock per workstream at `.current-work/cycles/.locks/<workstream-id>.lock`, covering only the read, comparison, validation, and replacement, released by the operating system when the process exits
- Five-second lock wait with a `workstream_busy` result that writes nothing when the wait expires
- Expected-state comparison — every mutation supplies the binding's observed revision and SHA-256 digest, and a mismatch returns `stale_workstream_state` with the expected and current revisions
- Atomic replacement — write a temporary sibling file, flush it, then replace the state file in one operation so an interruption leaves one complete file
- Revision increment on every accepted mutation, followed by a binding update with the new revision and digest
- Stale-binding detection — an interruption between the state write and the binding update leaves a stale binding that the next mutation detects
- Delegated-run conflict handling — pause and return control to the human rather than merge or retry

**Out:**

- Delivery model, model loading, and route recommendation (EPIC 2)
- Cycle selection and retry commands (EPIC 3)
- Delegation grants (EPIC 4)
- Usage record workstream/cycle fields (EPIC 6)

### Dependencies

None. This is the foundational EPIC.

### Boundaries

- Human touchpoint: `packages/factory/config/session-menu.md` (options B and C, switch confirmation)
- Engine: Workstream Resolver in `packages/factory/engine/workstreams.py`
- Adapter: `packages/factory/scripts/cycle` (workstream creation and state writes)
- Storage: `.current-work/cycles/`, `.current-work/cycles/.locks/`, `.current-work/session-bindings/`

### Domain Rules

- The engine returns immutable decisions and never writes repository state. Adapters own every write.
- A new workstream starts at revision 1 and attempt 1.
- The factory never selects or switches a workstream without human confirmation.
- The factory raises the same apparent boundary only once unless the objective changes again.
- A session binding is navigation state, not delivery evidence. Losing a binding must never lose delivery work.
- No repository-global active-workstream file exists. Each session resolves its workstream from its own binding.
- A stale session never overwrites newer workstream state.
- One concurrent change succeeds. The other pauses without writing.
- Sessions that change different workstreams never block each other.
- The digest covers the exact state-file bytes, detecting a direct edit that leaves the revision untouched.
- A rejected mutation leaves the rejecting session's binding unchanged. A refresh updates the observation and never repeats the rejected mutation.
- An accepted mutation increments the revision exactly once.
- The lock file contains no workflow data.

### Size

4 stories.

### Building-Block Inventory

| Story   | Goal                                                                                                                                                                                                                                               | Tier     | Size | Basis                                                                                                                                                                                           |
| ------- | -------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- | -------- | ---- | ----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| ST-0252 | The human starts a workstream from option B, the state file records the topic, cycle IDEA, revision 1, and attempt 1, and a session binding is created for the current session.                                                                    | standard | L    | New package `packages/factory/engine/`, cycle-state schema, state-file creation, session binding, session menu option B replacement.                                                            |
| ST-0253 | Option C lists every workstream with its topic and cycle, binds the chosen one to the session, and presents its recommendations; an empty list offers option B or a return to the menu.                                                            | standard | M    | Extends the option B adapter from ST-0252. The empty-list path and the digest record are additional behaviors. Replaces the existing option C tree.                                             |
| ST-0254 | The factory suggests a separate workstream on a detected objective change, acts only on confirmation, and does not repeat a declined suggestion.                                                                                                   | standard | M    | Detection criteria are named in the gaps report and need pinning down during grilling. Declined-suggestion memory is new session state.                                                         |
| ST-0255 | An accepted write replaces the state file atomically and increments the revision; a stale revision or digest is refused unchanged; two sessions on one workstream serialize under a five-second lock while different workstreams stay independent. | standard | L    | Compare-and-replace path on the ST-0252 adapter, fault-injection test for interruption, concurrency tests for lock timeout, stale revision, digest mismatch, and cross-workstream independence. |

### Testability Assessment

All actor goals produce observable, assertable outcomes at the following boundaries: YAML state files under `.current-work/cycles/` (content assertions on topic, cycle, revision, attempt), session binding files under `.current-work/session-bindings/` (revision and digest fields), lock files under `.current-work/cycles/.locks/` (existence and timing), CLI exit codes and result codes (`stale_workstream_state`, `workstream_busy`), and session menu output (option B creation, option C listing). Concurrency scenarios instrument the file lock wait and cross-workstream independence through two-process test fixtures.

### Ownership Resolution

| Contract                                         | .feature Rule                                                                     | Owner   | Rationale                                              |
| ------------------------------------------------ | --------------------------------------------------------------------------------- | ------- | ------------------------------------------------------ |
| Workstream creation from session menu            | cycle-based-orchestration.feature#Human operator starts a new workstream          | ST-0252 | introduces workstream creation and session binding     |
| Workstream listing, binding, and recommendations | cycle-based-orchestration.feature#Human operator continues an existing workstream | ST-0253 | introduces option C listing and workstream resume      |
| Topic-change detection and switch suggestion     | cycle-based-orchestration.feature#Human operator switches workstreams mid-session | ST-0254 | introduces objective-change detection and confirmation |
| Atomic state replacement and revision comparison | cycle-based-orchestration.feature#Adapter transitions workstream state atomically | ST-0255 | introduces atomic write, revision check, digest check  |
| File lock, timeout, and workstream independence  | cycle-based-orchestration.feature#Adapter handles concurrent workstream access    | ST-0255 | introduces lock acquisition, timeout, and independence |

## EPIC 2: Check which cycle the engine recommends and see the evidence behind it

### Why this EPIC exists

A workstream records the current cycle, but nothing in the factory can tell the human what the repository evidence supports. Every route beyond IDEA-to-CONCEPT recommends nothing and shows no evidence. Until the delivery model, the recommendation engine, and the artifact validators exist, the factory can record a human's choice but cannot inform it. This EPIC delivers the evidence that makes the recommendation useful, including reconciliation when code or canonical artifacts changed.

### Actor Goals

- Cycle engine loads the delivery model from tracked source and rejects a model that breaks its schema
- Cycle engine evaluates artifact readiness through trusted validators in a shared result shape
- Cycle engine recommends routes from artifact evidence, separating the zero, one, and several cases
- Transition recommender runs reconciliation when the cycle changed code or a canonical artifact, and reports it as not applicable otherwise
- Human operator reads per-artifact checks and warnings before choosing the next cycle

### Demo

01. Run the model loader against `packages/factory/engine/models/delivery.yaml`. It accepts five cycles with DONE and all declared routes.
02. Add a `direction` field to one route. The loader rejects the route and names the offending field.
03. Replace a validator reference with a shell command. The loader rejects it.
04. Point the workstream at an accepted proposal and run the assessment. The route from IDEA to CONCEPT is recommended, its evidence is listed, and every other cycle is offered.
05. Remove the proposal. The assessment reports no evidence-supported recommendation and shows warnings.
06. Prepare a repository with a scope map, entity model, architecture model, feature files, a gaps report, decision records, concept reviews, an epic plan, and selected stories. Every artifact reports its type, reference, assessed commit, checks, and warnings.
07. Break one feature file. The assessment reports that check as failed and keeps every other result intact. The route depending on that artifact loses its recommendation.
08. Change a source file and rerun. Reconciliation runs and gives its result.
09. Change `docs/spec/scope-map.md` and rerun. Reconciliation runs again.
10. Change neither code nor a canonical artifact and rerun. Reconciliation reports as not applicable.

### Scope

**In:**

- Delivery model — `packages/factory/engine/models/delivery.yaml` declaring the five cycles, the terminal DONE node, artifact declarations, trusted validator identifiers, per-cycle attempt limits, and every route with `from`, `to`, and `recommend_if`
- Cycle-model schema — `packages/factory/engine/schemas/cycle-model-v1.schema.json`, JSON Schema Draft 2020-12
- Model loading and validation — rejects unknown artifact references, unknown validator identifiers, executable commands in validator fields, and any `direction` or `classification` field on a route
- Route recommendation — evaluates each declared route from the current cycle and returns one of three results: no evidence-supported recommendation with warnings, one recommendation with its evidence, or several supported routes offered as choices without ranking
- Thirteen trusted validators covering the proposal, scope map, entity model, architecture model, feature specifications, gaps report, decision records, concept reviews, epic plan, selected stories, realization result, research brief, and research report, all using the shared result shape of artifact type, artifact reference, assessed commit, individual checks, and warnings
- Mechanical validation that runs unconditionally for every artifact the delivery model references
- Semantic assessment that runs only when the cycle changed code or a canonical artifact, and reports as not applicable otherwise
- Reconciliation as a standard transition assessment rather than a separate phase
- Collection rules — fixed paths identify canonical artifacts, an authoritative artifact lists a collection's required members, and a file glob never defines a complete collection
- Generic route invariant — visits every route loaded from the delivery model and fails when a source, target, artifact, validator, or predicate reference does not resolve
- Assessment output — shows evidence, warnings, and every other cycle at each cycle exit

**Out:**

- Workstream creation or management (EPIC 1)
- Cycle selection and retry commands (EPIC 3)
- Project-declared validators and artifact declarations; these wait for an extension contract that defines namespacing and failure behavior
- Automated semantic ranking between downstream routes (deferred by the proposal)

### Dependencies

EPIC 1 — workstream files and session bindings must exist.

### Boundaries

- Human touchpoint: assessment output from `packages/factory/scripts/cycle`
- Engine: Cycle Model Loader, Readiness Evaluator, and Route Recommender in `packages/factory/engine/`
- Existing checks reused as evidence: `spec-lint`, `arch-lint`, `backlog-lint`, `link-check`, `schema-validate`, `policy-validate`
- Storage: `packages/factory/engine/models/`, `packages/factory/engine/schemas/`, `docs/spec/`, `docs/arc42/`, `docs/adr/`, `docs/reviews/`, `backlog/`

### Domain Rules

- The delivery model names validators by identifier. It can never contain a shell command.
- A route declares only a source, a target, and its recommendation evidence. Direction and classification fields are rejected.
- The engine does not rank supported routes. When several qualify, the human chooses.
- Every validator returns the same result fields: artifact type, artifact reference, assessed commit, individual checks, and warnings.
- Mechanical validation runs unconditionally for referenced artifacts.
- Semantic assessment runs only when the cycle changed code or a canonical artifact.
- Neither validation layer authorizes a transition. Both only supply evidence.
- Reconciliation is a transition assessment, not a cycle.
- Fixed paths identify canonical artifacts. An authoritative artifact lists a collection's required members.
- A file glob may discover candidates. It never defines a complete collection.
- Failed or missing evidence produces a warning. It never removes a route and never prevents a human from selecting a cycle.
- Assessments read the current commit. The state file never copies requirements or assessment results.

### Size

4 stories.

### Building-Block Inventory

| Story   | Goal                                                                                                                                                                                                                                                                                                        | Tier     | Size | Basis                                                                                                                                                                |
| ------- | ----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- | -------- | ---- | -------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| ST-0256 | The engine loads the delivery model, validates it against the cycle-model schema, and rejects unknown references, executable commands, and direction fields; the proposal readiness validator and route recommendation (zero, one, and several supported routes) make the IDEA-to-CONCEPT route assessable. | standard | L    | Delivery model file, cycle-model schema, model loader with five rejection paths, proposal validator, route recommender with the three-case cardinality table.        |
| ST-0257 | Validators for the scope map, entity model, architecture model, feature specifications, gaps report, and decision records report readiness in the shared result shape.                                                                                                                                      | standard | L    | Six validators wrapping existing checks — `spec-lint`, `arch-lint`, and the EPIC 7 entity-model checks. Each needs valid, invalid, and stale-evidence tests.         |
| ST-0258 | Validators for the concept reviews, epic plan, selected stories, realization result, research brief, and research report report readiness in the same shape.                                                                                                                                                | standard | L    | Six validators. `backlog-lint` covers two; `schema-validate` and `policy-validate` cover two; the review and realization validators aggregate existing gate results. |
| ST-0259 | The assessment runs mechanical checks unconditionally, runs reconciliation only when code or canonical artifacts changed, prints evidence with warnings and all available cycles, and the generic route invariant rejects an unresolvable reference.                                                        | standard | M    | Wires the thirteen validators into the recommender, adds the change-detection rule, the reconciliation trigger, and the generic route invariant.                     |

### Testability Assessment

All actor goals produce observable, assertable outcomes at the following boundaries: model loader accept/reject results with named error fields, validator return values in the shared result shape (artifact type, reference, assessed commit, checks, warnings), route recommendation results (zero, one, or several supported routes), reconciliation applicable/not-applicable result, and the generic route invariant exit code. Tests instrument `packages/factory/engine/` function return values and CLI output from the assessment command. Existing lint scripts (`spec-lint`, `arch-lint`, `backlog-lint`) supply evidence through their exit codes.

### Ownership Resolution

| Contract                                             | .feature Rule                                                                                          | Owner   | Rationale                                                           |
| ---------------------------------------------------- | ------------------------------------------------------------------------------------------------------ | ------- | ------------------------------------------------------------------- |
| Delivery model loading and schema validation         | cycle-based-orchestration.feature#Engine loads and validates the delivery model                        | ST-0256 | introduces model loader, schema, and five rejection paths           |
| Artifact readiness evaluation in shared result shape | cycle-based-orchestration.feature#Engine evaluates artifact readiness for route recommendations        | ST-0256 | introduces the shared validator result shape and proposal validator |
| Route recommendation with three-case cardinality     | cycle-based-orchestration.feature#Engine recommends routes based on artifact evidence                  | ST-0256 | introduces route recommendation (zero, one, several)                |
| Reconciliation trigger on code or artifact change    | cycle-based-orchestration.feature#Reconciliation runs when a cycle changes code or canonical artifacts | ST-0259 | introduces change-detection rule and reconciliation assessment      |

## EPIC 3: Advance to a chosen cycle and retry it within delegated attempt limits

### Why this EPIC exists

The factory can recommend a route and record a workstream, but the human cannot yet act on a recommendation. There is no command to select a cycle and no way to retry a failing one. Delegated execution can repeat a failing cycle forever without a limit on unattended attempts. This EPIC delivers the commands that change a workstream's cycle and the counter that bounds unattended repetition.

### Actor Goals

- Human operator selects any cycle, with or without supporting evidence, and without an override step
- Cycle engine allows a delegated retry below the declared limit and pauses at the limit without changing state
- Human operator retries at or above the limit and continues with a warning, without an override step
- State adapter resets the attempt counter when the cycle changes or the selected work changes, and leaves it alone otherwise

### Demo

01. Run `factory/scripts/cycle select CONCEPT`. The state file records cycle CONCEPT at attempt 1 with the revision incremented.
02. Run `factory/scripts/cycle select REALIZE`, a route the model does not declare from CONCEPT. The command records the selection and warns that no declared route exists. It asks for no justification.
03. Enter REALIZE, whose declared limit is 5. The state file records attempt 1.
04. Run four delegated retries. The attempt reaches 5 and each retry returns `allowed`.
05. Run a fifth delegated retry. The command returns `paused` with reason `delegated_attempt_limit_reached`, the cycle, attempt 5, limit 5, and the next action `request_human_direction`. The state file is unchanged.
06. Run a human retry. The command returns `allowed_with_warning`, the attempt becomes 6, and no override flag is required.
07. Select a different cycle. The attempt returns to 1.
08. Return to the previous cycle and change the `work` list without changing the cycle. The attempt returns to 1.
09. Reassess artifacts, edit a file, and start a new session. The attempt does not change.
10. Corrupt the attempt field and retry. The command returns `invalid_state` and writes nothing.
11. Accept a retry, then let the assigned execution fail. The increment remains.

### Scope

**In:**

- `factory/scripts/cycle select` — records the chosen cycle with attempt reset to 1, shows warnings for undeclared routes, and increments the workstream revision through the atomic write path from EPIC 1
- `factory/scripts/cycle retry` — identifies the requester as human-authored or delegated, asks the engine for a retry decision, and increments the attempt only on an allowed result
- Per-cycle `delegated_attempt_limit` in the delivery model, one positive integer for each of the five cycles
- Retry evaluator returning one of four results — `allowed`, `paused`, `allowed_with_warning`, or `invalid_state` — from the attempt, the limit, and whether the request is human-authored or delegated
- Reset rules — a cycle change or a `work` list change sets the attempt to 1, including when the cycle stays the same
- Non-reset rules — changing sessions, resuming a workstream, reassessing artifacts, and editing files leave the attempt alone
- Attempt consumption — once the adapter accepts a retry, the increment stands through every later outcome, including a failure to start or complete the execution

**Out:**

- Delegation grants (EPIC 4). This EPIC only distinguishes a delegated request from a human one.
- Retry history. The state file keeps only the current attempt; usage and execution records supply history.

### Dependencies

EPIC 2 — the delivery model with its per-cycle attempt limits must exist.

### Boundaries

- Human touchpoint: `factory/scripts/cycle select`, `factory/scripts/cycle retry`
- Engine: Retry Evaluator in `packages/factory/engine/decisions.py`
- Storage: `packages/factory/engine/models/delivery.yaml`, `.current-work/cycles/`

### Domain Rules

- Retry limits stop unattended loops. They never prevent a human from continuing.
- A delegated retry at the limit changes nothing and returns an immutable paused result.
- A human retry at or above the limit proceeds with a warning and needs no override flag or justification.
- Entering a cycle sets attempt to 1. Selecting a different cycle or changing the work list resets the attempt to 1.
- Malformed retry state returns `invalid_state` without writing.
- The adapter never rolls an accepted attempt back.
- Every cycle declares a positive `delegated_attempt_limit`.

### Size

2 stories.

### Building-Block Inventory

| Story   | Goal                                                                                                                                                                                                                              | Tier     | Size | Basis                                                                                                                                                                                  |
| ------- | --------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- | -------- | ---- | -------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| ST-0260 | `cycle select` records any chosen cycle with attempt reset to 1 and warns on undeclared routes; `cycle retry` increments the attempt only on an allowed result, and cycle or work changes reset it while other activity does not. | standard | L    | Two adapter commands over the ST-0255 atomic write path. The retry evaluator is pure decision logic with an explicit result table. Reset and non-reset cases each need their own test. |
| ST-0261 | The retry evaluator returns allowed, paused, allowed with warning, or invalid state from the attempt, the limit, and the requester type; an accepted retry increment stands through any later failure.                            | standard | M    | Pure decision logic. The four result cases, the consumed-attempt rule, and the delegated/human distinction are the test surface.                                                       |

### Testability Assessment

All actor goals produce observable, assertable outcomes at the following boundaries: workstream state file content (cycle field and attempt field after each command), CLI result codes from `factory/scripts/cycle select` and `factory/scripts/cycle retry` (`allowed`, `paused`, `allowed_with_warning`, `invalid_state`), and CLI warning output for undeclared routes. The retry evaluator is pure decision logic with a finite four-result table, testable without filesystem or concurrency fixtures.

### Ownership Resolution

| Contract                                    | .feature Rule                                                            | Owner   | Rationale                                         |
| ------------------------------------------- | ------------------------------------------------------------------------ | ------- | ------------------------------------------------- |
| Cycle selection and attempt reset           | cycle-based-orchestration.feature#Human operator selects the next cycle  | ST-0260 | introduces `cycle select` and attempt reset rules |
| Delegated retry limits and pause conditions | cycle-based-orchestration.feature#Engine enforces delegated retry limits | ST-0261 | introduces retry evaluator with four-result table |

## EPIC 4: Delegate a route sequence and dispatch agents from cycle state

### Why this EPIC exists

Without delegation, every transition needs a human at the keyboard, and a five-cycle traversal becomes five interruptions. Without cycle-aware agent dispatch, `run-step` still reads the playbook marker instead of the workstream file. Delegation is also the sharpest safety boundary in the proposal: an engine that could widen its own authority would remove the human from the loop entirely. This EPIC delivers unattended advancement, fixes the boundary that keeps the grant human-owned, and connects cycle state to the dispatcher so the model starts driving real work.

### Actor Goals

- Human operator records an ordered sequence of cycle selections that the engine follows without asking
- Human operator records a destination and lets the engine continue only while the evidence is unambiguous
- Cycle engine pauses when a grant ends, when the choice falls outside the grant, or when execution fails
- Cycle engine never creates, extends, or broadens a grant
- Agent definition declares which cycles it is eligible for instead of a phase ordinal
- `run-step` resolves the next agent from cycle state and the delivery model, then dispatches it
- `run-step` re-derives the next action from observable state after an interruption

### Demo

01. Read any agent definition and confirm it carries cycle eligibility tags and no `phase:` ordinal.
02. Regenerate the catalog and confirm every agent and skill name from the acceptance commit is still indexed.
03. Put a workstream into CONCEPT and run `run-step`. It names the requirements agent from cycle eligibility and starts it.
04. Interrupt the session and run `run-step` again. It derives the same next action from the workstream file and the repository.
05. Write the grant `route: [CONCEPT, REFINE, REALIZE]` into a workstream at IDEA and start a delegated run.
06. The engine selects CONCEPT, then REFINE, then REALIZE, showing the recommendation evidence and any warnings at each step.
07. Remove the evidence supporting one route and run the same grant again. The engine still follows the recorded choice and records the warning.
08. Let the run reach the end of the sequence. The engine pauses and asks for human direction.
09. Replace the grant with `through: REALIZE` from a cycle where exactly one route has supporting evidence. The engine continues.
10. Remove that evidence so no route qualifies. The engine pauses.
11. Restore evidence for two routes. The engine pauses and presents both choices without ranking them.
12. Make the assigned execution fail. The run stops.
13. Ask the engine to widen the grant. It refuses.

### Scope

**In:**

- Cycle eligibility metadata on every agent definition, replacing the `phase:` ordinal that 16 agents carry today
- Catalog regeneration so `index-lint` reads the new field and keeps every indexed name
- Dispatch eligibility in the engine — determine which agents and skills apply to the current cycle and the selected work
- `run-step` migration — resolve the next agent from the workstream state file and the delivery model, and stop reading the playbook marker
- Kept `run-step` contract — the same skill name, repository-derived resume, one invocation at a time, and no blind retry
- Grant shapes in the cycle-state schema — exactly one of `route` (an ordered list of cycles) or `through` (one destination cycle), with a null grant permitted
- Explicit-route evaluation — follow the recorded sequence in order, showing evidence and warnings, and continue even when the recommendation evidence for a step failed
- Destination evaluation — continue only while exactly one route has supporting evidence, and pause on zero or several
- Pause conditions — the grant is exhausted, the engine reaches the named destination, or the next choice falls outside the grant
- Technical-failure stop — any failure of the assigned execution stops the delegated run
- Grant authorship — the engine and its agents can read a grant but can never create, extend, or broaden one
- Human-direction pauses at IDEA and REFINE when no grant supplies the required decision

**Out:**

- Inferring a grant from past behavior. The first release never infers, creates, or broadens delegation.
- Automated ranking between several supported routes (deferred by the proposal).
- Deleting playbook files. They remain as reference documentation.
- The `phase` diagnostic stub and cycle-native `transition-lint` (EPIC 5).

### Dependencies

EPIC 3 — `cycle select` and `cycle retry` must exist.

### Boundaries

- Human touchpoint: `packages/factory/skills/run-step/SKILL.md`, the `delegation` block in the workstream state file
- Engine: Delegation Evaluator in `packages/factory/engine/delegation.py`, Dispatch Eligibility in `packages/factory/engine/dispatch.py`
- Dispatcher: `packages/factory/scripts/trigger`, `packages/factory/scripts/index-lint`
- Storage: `packages/factory/agents/*.md`, `.claude/INDEX.yaml`, `.current-work/cycles/`

### Domain Rules

- A grant contains exactly one form: an explicit route or a destination.
- An explicit route is a recorded human choice. Failed recommendation evidence does not invalidate it.
- A destination grant continues only while exactly one route has supporting evidence.
- The engine pauses at the named destination, at the end of a grant, and when the next choice falls outside it.
- A technical execution failure always stops the run.
- Only the human creates, replaces, revokes, or broadens a grant.
- Delegated execution may continue without the human present. The grant supplies the authority; presence does not.
- IDEA and REFINE request human direction when no grant contains the needed decision.
- Agent definitions carry cycle eligibility. Phase ordinals no longer exist.
- Every agent and skill name indexed at the acceptance commit remains available.
- `run-step` keeps its skill name, its repository-derived resume, one invocation at a time, and no blind retry.
- No delivery transition reads a playbook finite state machine file as its authority after cutover.
- The engine determines eligibility. It does not launch anything; the dispatcher does.

### Size

3 stories.

### Building-Block Inventory

| Story   | Goal                                                                                                                                                                                                                                       | Tier     | Size | Basis                                                                                                                                            |
| ------- | ------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------ | -------- | ---- | ------------------------------------------------------------------------------------------------------------------------------------------------ |
| ST-0262 | Every agent definition carries cycle eligibility instead of a phase ordinal, and the engine resolves eligible agents for the current cycle and work.                                                                                       | standard | M    | Mechanical edit across 16 agent files plus `index-lint` and the generated integrations. The eligibility resolver itself is small.                |
| ST-0263 | An explicit-route grant follows its ordered selections and a destination grant continues on exactly one supported route; both pause on exhaustion, ambiguity, destination arrival, or technical failure; the engine never creates a grant. | standard | L    | Extends the ST-0260 selection and the ST-0256 recommender with the delegation evaluator. Five distinct pause conditions, each with its own test. |
| ST-0264 | `run-step` names the next agent from the workstream file and the delivery model, dispatches it, and re-derives the same action after an interruption.                                                                                      | standard | M    | Rewrites one skill file. Small surface, but it changes the resume contract every consumer depends on. Needs characterization tests first.        |

### Testability Assessment

All actor goals produce observable, assertable outcomes at the following boundaries: agent definition YAML frontmatter (cycle eligibility fields present, phase ordinals absent), `.claude/INDEX.yaml` entries (all acceptance-commit names preserved), grant block in the workstream state file (route or through field), delegation evaluator result codes (pause conditions), `run-step` resolution output (named agent from cycle state, not playbook state), and dispatcher invocation records. The grant authorship invariant — the engine never creates a grant — is testable by asserting that no engine code path writes to the delegation block.

### Ownership Resolution

| Contract                                           | .feature Rule                                                                                         | Owner   | Rationale                                                  |
| -------------------------------------------------- | ----------------------------------------------------------------------------------------------------- | ------- | ---------------------------------------------------------- |
| Cycle eligibility metadata on agent definitions    | cycle-based-orchestration.feature#Agent definitions carry cycle eligibility instead of phase ordinals | ST-0262 | introduces cycle eligibility fields across 16 agent files  |
| Explicit-route and destination grant evaluation    | cycle-based-orchestration.feature#Human operator delegates a route sequence                           | ST-0263 | introduces explicit-route grant evaluation and pause rules |
| Destination grant with evidence-based continuation | cycle-based-orchestration.feature#Human operator delegates through a destination                      | ST-0263 | introduces destination grant evaluation in the same story  |
| Cycle-state resolution in run-step                 | cycle-based-orchestration.feature#run-step executes cycle steps instead of playbook steps             | ST-0264 | introduces workstream-based agent resolution in run-step   |

## EPIC 5: Run existing phase and lint commands after the cycle cutover

### Why this EPIC exists

The proposal replaces the routing authority but promises that every other command keeps its behavior. That promise is only worth the checks that verify it. Two commands must change — `phase` becomes a diagnostic stub and `transition-lint` moves to the cycle model — while roughly twenty other commands must be shown not to have changed. This EPIC performs the cutover and supplies the evidence that nothing else moved.

### Actor Goals

- Human operator running the old `phase` command receives a message naming the replacement instead of a silent failure
- `transition-lint` validates cycle models and workstream state files, and reports failed recommendation evidence as a warning that exits zero
- Maintainer compares the current catalog against the acceptance commit and sees only the intended replacements

### Demo

1. Run `factory/scripts/phase advance`. It exits 2 and names `factory/scripts/cycle select`. It performs no transition.
2. Run `factory/scripts/phase retry`. It exits 2 and names `factory/scripts/cycle retry`.
3. Run `transition-lint` against a valid delivery model and a valid workstream state file. It passes.
4. Break the delivery model and rerun. It fails and names the fault.
5. Corrupt a workstream state file and rerun. It fails and names the fault.
6. Point `transition-lint` at a state whose recommendation evidence failed. It prints warnings and exits zero.
7. Run the comparison against the acceptance commit. Every agent and skill name indexed there is still present, and only the listed replacements appear as differences.
8. Run each standard check, each branch-safety command, and each REALIZE quality command on known-good and known-bad input. Every command name, trigger, result format, and exit code matches the acceptance commit.

### Scope

**In:**

- `phase` diagnostic stub — replace the transition implementation with a stub that exits 2 and names the corresponding `cycle` command, and keep it for one release
- Cycle-native `transition-lint` — replace phase-order rejection with cycle-model and workstream-state integrity checks, and exit zero on failed recommendation evidence with warnings
- Catalog compatibility check — compare indexed agent and skill names against the acceptance commit and permit only the intentional replacements from the compatibility contract
- Characterization tests for the standard checks `mdformat`, `link-check`, `mermaid-lint`, `spec-lint`, `arch-lint`, `backlog-lint`, `concern-lint`, `matrix-lint`, `statemachine-lint`, and `index-lint`
- Characterization tests for `verify-base` and `premerge-check`
- Characterization tests for the REALIZE quality commands `crap-score`, `dependency-check`, and `test-design-verify`
- Installed-shape test proving that the installed factory loads the same schema-valid model as the tracked source
- Dependency-boundary test rejecting engine imports from scripts, configuration, agent definitions, skills, or orchestrator code
- Python 3.10 minimum for every cycle-based orchestration command

**Out:**

- Deleting `factory/scripts/phase`. The stub stays for one release.
- Deleting playbook finite state machine files. They remain as reference documents without runtime authority.
- Emulating the old single-forward-transition behavior in the stub.

### Dependencies

EPIC 2 — the delivery model and cycle-model schema must exist.

### Boundaries

- Human touchpoint: `packages/factory/scripts/phase`, `packages/factory/scripts/transition-lint`
- Validator: the ten standard checks and three quality commands named above
- Dispatcher: `packages/factory/scripts/index-lint` (catalog comparison)
- Storage: `packages/factory/INDEX.yaml`, `factory/engine/` (installed copy)

### Domain Rules

- The stub exits 2 and names its replacement. It never emulates the old transition behavior.
- `transition-lint` fails on an invalid cycle model or a malformed state file. Failed recommendation evidence produces warnings and exits zero.
- Every kept contract retains its command name, trigger, result format, and exit behavior from the acceptance commit.
- Only the intentional replacement table permits a difference from the acceptance commit.
- Tracked factory source is the default test surface.
- Scripts are thin adapters. One engine implementation owns the decisions.
- The engine never imports scripts, configuration, agent definitions, skills, or the orchestrator. Those may call the engine.
- The existing commands stay operational until the cycle-native replacements pass their characterization and installed-shape tests.

### Size

3 stories.

### Building-Block Inventory

| Story   | Goal                                                                                                                           | Tier     | Size | Basis                                                                                                                            |
| ------- | ------------------------------------------------------------------------------------------------------------------------------ | -------- | ---- | -------------------------------------------------------------------------------------------------------------------------------- |
| ST-0265 | `phase advance` and `phase retry` exit 2 and name their `cycle` replacements without performing any transition.                | standard | S    | Deletes 627 lines and adds a stub. Small code change, but the removal must land only after EPIC 4 lands.                         |
| ST-0266 | `transition-lint` accepts a valid cycle model and state file, rejects invalid ones, and warns at exit zero on failed evidence. | standard | M    | Rewrites a 389-line script against the ST-0256 schemas. The warning-at-exit-zero rule inverts the current failure behavior.      |
| ST-0267 | Characterization tests fix the behavior of every kept command, and a catalog comparison permits only the listed replacements.  | standard | L    | Roughly twenty commands, each with known-good and known-bad cases. Also holds the installed-shape and dependency-boundary tests. |

### Testability Assessment

All actor goals produce observable, assertable outcomes at the following boundaries: `factory/scripts/phase` exit code (2) and stdout (replacement name), `factory/scripts/transition-lint` exit code (0 on valid input, non-zero on invalid, 0-with-warnings on failed evidence) and stderr (error and warning messages), and `factory/scripts/index-lint` catalog comparison output (names present, replacements listed). Characterization tests for roughly twenty commands instrument each command's exit code, stdout format, and trigger behavior against known-good and known-bad fixtures. The installed-shape test compares the installed model file byte-for-byte against the tracked source.

### Ownership Resolution

| Contract                                                 | .feature Rule                                                                            | Owner   | Rationale                                               |
| -------------------------------------------------------- | ---------------------------------------------------------------------------------------- | ------- | ------------------------------------------------------- |
| Phase command diagnostic stub                            | cycle-based-orchestration.feature#phase command exits as a diagnostic stub               | ST-0265 | introduces the exit-2 stub naming the replacement       |
| Cycle-model and state-file validation in transition-lint | cycle-based-orchestration.feature#transition-lint validates cycle models and state files | ST-0266 | introduces cycle-native model and state validation      |
| Characterization tests and catalog compatibility         | cycle-based-orchestration.feature#Kept contracts preserve acceptance-commit behavior     | ST-0267 | introduces characterization tests for all kept commands |

## EPIC 6: Query usage records grouped by workstream and cycle

### Why this EPIC exists

The proposal claims that a small change should traverse fewer cycles and cost less. Nothing in the factory can test that claim today, because usage records carry no workstream or cycle context. Without this EPIC the routing model has no measurable effect and the choice between direct realization and a full traversal stays a matter of opinion. This EPIC supplies the evidence.

### Actor Goals

- Usage capture records the workstream and cycle when a session binding exists, and records nothing rather than guessing when it does not
- Child agent inherits its parent's workstream and its own dispatch cycle
- Usage analyst groups records by workstream, by cycle, and by both, and reads no `.current-work` file
- Usage analyst sees unattributable records reported as unavailable rather than assigned to the wrong workstream

### Demo

1. Bind a session to a workstream and run a captured invocation. The usage record carries `workstream_id`, `workstream_origin`, and `cycle`.
2. Remove the binding and run another invocation. Capture succeeds and all three fields are null.
3. Dispatch a child agent. Its records carry the parent's workstream and the child's own dispatch cycle.
4. Run a per-invocation producer and a cumulative producer across a confirmed workstream switch. Both attribute the work on either side to the right workstream.
5. Group usage by workstream. Each workstream's total appears separately.
6. Group usage by cycle. Compare the cost of a direct route to REALIZE against a route through ROADMAP and REFINE.
7. Group by both dimensions at once.
8. Produce records that support neither attribution method. Analysis reports them as unavailable and assigns them to no workstream.
9. Delete every `.current-work` file and rerun the analysis. The results are unchanged.

### Scope

**In:**

- Three optional fields on the usage-record v1 contract — `workstream_id`, `workstream_origin`, and `cycle` — with the compatibility manifest updated
- Capture population — the orchestration adapter supplies the fields from the session binding, and capture never imports or queries the cycle engine
- Null-safe capture — a missing binding leaves all three fields null and never fails capture
- Child inheritance — a dispatched agent inherits the parent workstream and records its own dispatch cycle
- Attribution rules — per-invocation usage is attributed directly, monotonic cumulative usage is attributed by subtracting snapshots at workstream boundaries, and an invocation is counted against the workstream active for that invocation
- Honest unavailability — analysis reports attribution as unavailable when neither method applies, and never assigns a whole cumulative session to the workstream active at session end
- Workstream, cycle, and workstream-by-cycle dimensions in the published query model

**Out:**

- Reading `.current-work` during analysis. Analysis reads immutable usage records only.
- Retroactive attribution of records captured before this EPIC. Those records keep null fields.
- New usage producers. The four existing producer values keep their conservation rules.

### Dependencies

EPIC 1 — session bindings must record the workstream before capture can read them.

### Boundaries

- Producer: `packages/factory/scripts/usage-capture`
- Contract: `packages/factory/contracts/usage-record/`
- Consumer: Usage Analysis Runtime, `packages/usage/src/usage`
- Storage: `.agent-factory/usage/`, `.agent-factory/usage-analysis/`

### Domain Rules

- Missing cycle context leaves all three fields null and never fails capture.
- The orchestration adapter supplies the fields. Usage capture never imports or queries the cycle engine.
- Child agents inherit the workstream and record their dispatch cycle.
- Context carried from an earlier topic counts toward the workstream active for the current invocation.
- Analysis never assigns a complete cumulative session to the workstream active at session end.
- Analysis reads immutable usage records and never depends on retained `.current-work` files.
- When neither attribution method applies, analysis reports the attribution as unavailable.

### Size

3 stories.

### Building-Block Inventory

| Story   | Goal                                                                                                                                 | Tier     | Size | Basis                                                                                                                                 |
| ------- | ------------------------------------------------------------------------------------------------------------------------------------ | -------- | ---- | ------------------------------------------------------------------------------------------------------------------------------------- |
| ST-0268 | The usage-record contract carries three optional workstream fields, and capture populates them from the binding or leaves them null. | standard | M    | Extends a published schema and its compatibility manifest. The no-import rule between capture and the engine needs a boundary test.   |
| ST-0269 | A child agent inherits the parent workstream, and boundary snapshots attribute cumulative usage to the right workstream.             | standard | M    | Touches the dispatch path and the snapshot arithmetic. Cumulative producers are the hard case and need a cross-boundary fixture.      |
| ST-0270 | Usage analysis groups by workstream, by cycle, and by both, and reports unattributable records as unavailable.                       | standard | M    | Adds dimensions to the existing published view. Follows the established query-model pattern. The unavailable case must not be silent. |

### Testability Assessment

All actor goals produce observable, assertable outcomes at the following boundaries: usage record JSON files under `.agent-factory/usage/` (presence and value of `workstream_id`, `workstream_origin`, and `cycle` fields), `packages/factory/contracts/usage-record/v1.schema.json` (schema validation of the three new fields), child agent usage records (inherited workstream, own dispatch cycle), and usage analysis CLI output (grouped totals by workstream, by cycle, and by both dimensions). The null-field path and the unavailable-attribution report are assertable through records captured without a session binding. A boundary test confirms that `usage-capture` never imports the cycle engine.

### Ownership Resolution

| Contract                                          | .feature Rule                                                                              | Owner   | Rationale                                                     |
| ------------------------------------------------- | ------------------------------------------------------------------------------------------ | ------- | ------------------------------------------------------------- |
| Workstream and cycle fields on usage records      | cycle-based-orchestration.feature#Usage records carry workstream and cycle context         | ST-0268 | introduces three optional fields on the usage-record contract |
| Workstream and cycle query dimensions in analysis | cycle-based-orchestration.feature#Usage analyst queries by workstream and cycle dimensions | ST-0270 | introduces grouping dimensions in the published query model   |

## EPIC 7: Define domain entities in LinkML and validate generated Pydantic models

### Why this EPIC exists

The factory has no canonical domain model today: `docs/spec/entity-model.yaml` does not exist, and entity descriptions live in prose that no check can read. Three routes depend on entity-model evidence, and none of them can produce it. This EPIC establishes the machine-readable source, the checks that decide whether it is ready, and the rule that every other representation is generated from it.

### Actor Goals

- Entity modeler writes one machine-readable entity model that passes mechanical readiness checks
- Entity modeler regenerates the Markdown and diagram projections and confirms they add no model information of their own
- Developer generates validation code from the model and sees an invalid payload rejected before it reaches storage

### Demo

1. Write `docs/spec/entity-model.yaml` in LinkML (a schema language for describing entities, their slots, and their relationships).
2. Run the entity-model readiness check. The file passes metamodel validation, the linter reports no error, and every referenced class and slot resolves.
3. Add a slot backed by a JSON column without declaring its value-object class. The check fails and names the unresolved reference.
4. Declare the value-object class inline and remove its schema-version slot. The check fails and names the missing slot.
5. Fix both faults and regenerate `docs/spec/entity-model.md` and `docs/assets/images/entity-model.svg`. Both follow the source.
6. Add a sentence to the Markdown projection that the source does not contain. The check reports the projection as out of date.
7. Generate validation code from the model and submit a payload that breaks an invariant. The payload is rejected before storage.
8. Store and retrieve a valid value object. Every field and the schema version survive the round trip.

### Scope

**In:**

- `docs/spec/entity-model.yaml` as the canonical source for domain entities, value objects, slots, relationships, identities, and invariants
- Entity-model readiness checks — metamodel validation passes, the linter reports no error, every referenced class and slot resolves, every JSON-backed slot references a defined inline class, every persisted JSON value-object class defines the schema-version slot, the projections are generated from the current source, and no major review finding is open
- Derived projections — `docs/spec/entity-model.md` and `docs/assets/images/entity-model.svg`, generated from the source and carrying no independently authored model information
- Value-object contract — structured JSON payloads are declared as inline classes in the same model, and the persistence adapter stores the validated object in a JSON or JSONB column
- Generated validation code owning payload shape and application invariants, while the database owns column type, nullability, and storage constraints
- Schema-version discriminator on every persisted JSON value object, with a policy stating whether the application reads, migrates, or rejects an older version
- Persistence integration tests owning serialization and retrieval fidelity

**Out:**

- Database-level JSON Schema validation. The generated code and the integration tests own that responsibility.
- The domain vocabulary in `docs/CONTEXT.md`. That file names and defines terms; the entity model records entities, relationships, and invariants.
- Wiring the entity-model validator into the route assessment (EPIC 2).

### Dependencies

None. This EPIC starts immediately, in parallel with EPIC 1.

### Boundaries

- Human touchpoint: `docs/spec/entity-model.yaml` and the generation command
- Validator: the entity-model readiness check
- Agents: domain-modeling, requirements-agent
- Storage: `docs/spec/entity-model.md`, `docs/assets/images/entity-model.svg`

### Domain Rules

- The LinkML file is the canonical entity model. Markdown and diagram files are derived projections.
- No derived artifact may introduce model information absent from the source.
- A JSON-backed slot references its value-object class and declares inline containment.
- Generated models own payload shape and application invariants. The database owns column type, nullability, and storage constraints.
- Every persisted JSON value object carries a schema-version discriminator.
- A versioning policy decides whether the application reads, migrates, or rejects an older version, and names the error when it rejects.
- Database-level JSON Schema validation is not required.

### Size

3 stories.

### Building-Block Inventory

| Story   | Goal                                                                                                                                              | Tier     | Size | Basis                                                                                                                            |
| ------- | ------------------------------------------------------------------------------------------------------------------------------------------------- | -------- | ---- | -------------------------------------------------------------------------------------------------------------------------------- |
| ST-0271 | `docs/spec/entity-model.yaml` exists in LinkML and a readiness check reports each mechanical criterion as a separate result.                      | standard | L    | New file and new tooling. Seven readiness criteria, each needing a failing case. LinkML is a new dependency for this repository. |
| ST-0272 | The Markdown and diagram projections regenerate from the model, and a hand-edited projection is reported as out of date.                          | standard | M    | Generation plus a staleness comparison. Follows the existing derived-artifact pattern used for architecture diagrams.            |
| ST-0273 | A JSON-backed slot resolves to an inline value-object class, generated validation rejects an invalid payload, and a round trip keeps every field. | standard | M    | Code generation and a persistence integration test. This repository has no database, so the test needs a representative fixture. |

### Testability Assessment

All actor goals produce observable, assertable outcomes at the following boundaries: readiness check exit codes and per-criterion pass/fail results (metamodel validation, linter, class resolution, JSON-slot reference, schema-version slot, projection staleness, review findings), generated projection files (`docs/spec/entity-model.md` and `docs/assets/images/entity-model.svg`) compared against the source, generated Pydantic model validation errors on invalid payloads, and persistence integration test assertions on round-trip field equality. Seven named readiness criteria each produce a distinct pass or fail, making every criterion independently assertable.

### Ownership Resolution

| Contract                                     | .feature Rule                                                                           | Owner   | Rationale                                                 |
| -------------------------------------------- | --------------------------------------------------------------------------------------- | ------- | --------------------------------------------------------- |
| Entity model and mechanical readiness checks | cycle-based-orchestration.feature#LinkML entity model serves as canonical domain source | ST-0271 | introduces entity-model file and seven readiness criteria |

## EPIC 8: Bootstrap a brownfield repository into the canonical concept baseline

### Why this EPIC exists

Every delivery route beyond IDEA assumes a scope map, an entity model, and an architecture model already exist. An inherited repository has none of them, so a brownfield user meets a graph that recommends nothing. This EPIC gives that user a defined entry: reconstruct the three canonical objects from code, tests, persistence schemas, and infrastructure definitions, then see what evidence is still missing.

### Actor Goals

- Brownfield operator receives all three canonical concept objects from the mandatory first stage of onboarding
- Cycle engine recommends feature delivery when all three objects exist, validate, and carry no unresolved major review finding
- Brownfield operator selects another cycle with an incomplete baseline and continues with warnings, without an override step

### Demo

1. Fit a repository that has code and tests but no specification.
2. Run brownfield onboarding. Its first stage produces `docs/spec/scope-map.md`, `docs/spec/entity-model.yaml`, and `docs/arc42/architecture.dsl`.
3. Confirm that the entity relationship diagram is part of that first stage, not the optional second stage.
4. Run the bootstrap assessment. All three objects validate, no major review finding is open, and the assessment recommends feature delivery.
5. Delete the entity model and rerun. The assessment names the missing evidence and recommends completing CONCEPT.
6. Select REALIZE anyway. The command records the selection, repeats the warnings, and asks for no justification.
7. Confirm that the bootstrap created no epic plan and entered no REALIZE cycle on its own.
8. Start a new change from IDEA with a proposal and confirm the normal delivery route applies.

### Scope

**In:**

- Brownfield onboarding first stage produces all three canonical concept objects, with the entity relationship diagram included in the mandatory stage
- Bootstrap assessment — recommend feature delivery when the three objects exist, pass deterministic validation, and have no unresolved major review finding
- Missing-evidence reporting — name each absent or failing object when the baseline is incomplete
- Continue-with-warnings path — a human selection of another cycle proceeds and repeats the warnings
- Bootstrap exit — leave the repository delivery-ready without creating an epic plan or entering REALIZE
- Fitting recorded as a prerequisite outside the delivery graph

**Out:**

- The deeper reverse-engineering second stage of onboarding. It stays optional and is not a delivery prerequisite.
- Requiring an accepted proposal for the bootstrap. Existing code is the evidence.
- The entity-model contract itself (EPIC 7). This EPIC consumes it.

### Dependencies

EPIC 2 — the readiness evaluator and concept validators must exist.
EPIC 7 — the canonical entity-model contract must exist before onboarding can produce it.

### Boundaries

- Human touchpoint: `packages/factory/playbooks/brownfield-onboarding.md`, session menu
- Engine: Readiness Evaluator (bootstrap assessment)
- Agents: reverse-map, requirements-agent, architecture-agent, domain-modeling
- Storage: `docs/spec/scope-map.md`, `docs/spec/entity-model.yaml`, `docs/arc42/architecture.dsl`

### Domain Rules

- Fitting is a prerequisite, not a delivery cycle.
- A greenfield repository enters IDEA after fitting. A brownfield repository enters a mandatory CONCEPT bootstrap after fitting.
- The canonical concept model is the scope map, the entity model, and the architecture model. Their existence is the recommended baseline; their content stays revisable.
- Proposals are origins. Feature files, decision records, and backlog files are elaborations.
- A human may select another cycle before the baseline is complete. The factory reports the missing evidence and continues.
- The bootstrap exits to a delivery-ready repository. It creates no epic plan and enters no REALIZE cycle.

### Size

2 stories.

### Building-Block Inventory

| Story   | Goal                                                                                                                     | Tier     | Size | Basis                                                                                                                       |
| ------- | ------------------------------------------------------------------------------------------------------------------------ | -------- | ---- | --------------------------------------------------------------------------------------------------------------------------- |
| ST-0274 | The mandatory first stage of brownfield onboarding produces the scope map, the entity model, and the architecture model. | standard | M    | Restructures an existing playbook and moves the entity relationship diagram from the optional stage into the mandatory one. |
| ST-0275 | The bootstrap assessment recommends feature delivery on a complete baseline and names the missing evidence otherwise.    | standard | M    | Composes the ST-0257 validators into one entry assessment. The continue-with-warnings path reuses the ST-0260 selection.    |

### Testability Assessment

All actor goals produce observable, assertable outcomes at the following boundaries: file existence of the three canonical objects (`docs/spec/scope-map.md`, `docs/spec/entity-model.yaml`, `docs/arc42/architecture.dsl`) after bootstrap, validation results for each object (pass or fail with named criteria), bootstrap assessment output (recommend feature delivery or name missing evidence), and `cycle select` warning output when the baseline is incomplete. The mandatory-stage boundary — entity relationship diagram included in the first stage — is assertable by checking which files the first stage produces.

### Ownership Resolution

| Contract                                           | .feature Rule                                                                                | Owner   | Rationale                                                     |
| -------------------------------------------------- | -------------------------------------------------------------------------------------------- | ------- | ------------------------------------------------------------- |
| Brownfield bootstrap producing three canon objects | cycle-based-orchestration.feature#Brownfield operator bootstraps the canonical concept model | ST-0274 | introduces mandatory first stage with three canonical objects |

## EPIC 9: Create a delivery-linked research brief and return results to the requesting cycle

### Why this EPIC exists

A delivery cycle often stops on a question that delivery work cannot answer. Today the user leaves the delivery context, runs research separately, and carries the result back by hand, with nothing recording which decision the research was meant to inform. This EPIC makes that round trip explicit, so a returning report names the cycle that will consume it and the decision it answers.

### Actor Goals

- Human operator opens a research brief from a delivery cycle that records where it came from and where the answer returns
- Human operator runs standalone research without any delivery-link fields
- Cycle engine resumes the named delivery cycle when a validated report returns

### Demo

1. Work a workstream to CONCEPT and meet a question the concept work cannot answer.
2. Create a research brief from that cycle. The brief records the origin cycle CONCEPT, the origin reference of the artifact needing evidence, the return cycle, and the decision the result must inform.
3. Validate the brief. Its schema passes and all four delivery-link fields resolve.
4. Create a standalone brief instead. It omits the four delivery-link fields and still validates.
5. Run a survey and a falsification study through their existing routes. Both complete without entering the delivery graph.
6. Validate the returned report. It references the brief and records how it disposed of the evidence.
7. Return the report. The delivery graph resumes at the cycle the brief named, and the report reference is recorded.

### Scope

**In:**

- Four optional delivery-link fields on the research brief — `origin_cycle`, `origin_ref`, `return_cycle`, and `decision_needed` — added to the brief schema and template
- Brief validation — a linked brief declares all four fields; a standalone brief omits them and still validates
- Report validation — the report references its brief and records its evidence disposition
- Return path — a validated report from a linked brief resumes the delivery cycle named in `return_cycle` and records the report reference
- Standalone completion — a validated survey or falsification report completes standalone research without touching the delivery graph

**Out:**

- Replacing the internal survey and falsification routes. They stay unchanged in the first release.
- A research cycle model at `engine/models/research.yaml`. The first release neither creates nor reads that file.
- Research role-separation rules. They stay as they are.

### Dependencies

EPIC 1 — cycle state must exist before a brief can name an origin cycle and a return cycle.

### Boundaries

- Human touchpoint: `packages/factory/rulebooks/templates/research-brief.md`
- Validator: `packages/factory/scripts/schema-validate`, `packages/factory/scripts/policy-validate`
- Engine: route resumption from the returned report
- Storage: `packages/factory/rulebooks/schemas/research-brief.schema.json`, `.current-work/cycles/`

### Domain Rules

- Research is a sibling graph, not a sixth delivery cycle.
- A linked brief declares its origin cycle, origin reference, return cycle, and the decision needed.
- A standalone brief omits every delivery-link field.
- A validated report completes standalone research. Linked research returns the report reference to the declared return cycle.
- The first release defines and validates the handoff and leaves the internal research routes unchanged.

### Size

2 stories.

### Building-Block Inventory

| Story   | Goal                                                                                                            | Tier     | Size | Basis                                                                                                                   |
| ------- | --------------------------------------------------------------------------------------------------------------- | -------- | ---- | ----------------------------------------------------------------------------------------------------------------------- |
| ST-0276 | A brief created from a delivery cycle records all four delivery-link fields, and a standalone brief omits them. | standard | S    | Adds four optional fields to an existing schema and template. The conditional requirement rule is the only subtle part. |
| ST-0277 | A validated report from a linked brief resumes the declared return cycle and records the report reference.      | standard | M    | Connects report validation to the ST-0260 selection path. Standalone completion must stay outside the delivery graph.   |

### Testability Assessment

All actor goals produce observable, assertable outcomes at the following boundaries: research brief schema validation results from `factory/scripts/schema-validate` (pass with four delivery-link fields present, pass with all four absent, fail on partial presence), `factory/scripts/policy-validate` results for the returned report (references its brief, records evidence disposition), workstream state file content after return (cycle matches `return_cycle`, report reference recorded), and standalone completion (delivery graph state unchanged). The conditional-requirement rule — all four fields present or all four absent — is the only subtle validation path.

### Ownership Resolution

| Contract                               | .feature Rule                                                                    | Owner   | Rationale                                                  |
| -------------------------------------- | -------------------------------------------------------------------------------- | ------- | ---------------------------------------------------------- |
| Delivery-link fields on research brief | cycle-based-orchestration.feature#Delivery cycle creates a linked research brief | ST-0276 | introduces four optional delivery-link fields on the brief |
