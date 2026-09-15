# EPICs — Cycle-Based Orchestration

Proposal trace: [cycle-based-orchestration.md](../docs/proposals/cycle-based-orchestration.md)
Specification trace: [cycle-based-orchestration.feature](../docs/spec/cycle-based-orchestration.feature)
Architecture trace: [ADR-0017](../docs/adr/0017-cycle-based-orchestration-supersedes-linear-playbook-fsm.md), [ADR-0018](../docs/adr/0018-concept-internal-sequence-is-agent-owned.md), [§5.3 Cycle Engine](../docs/arc42/05_building_block_view.md#53-level-2-component-view----cycle-engine), [§5.4 State Adapter](../docs/arc42/05_building_block_view.md#54-level-2-component-view----state-adapter)
QA strategy trace: [cycle-based-orchestration-qa-strategy.md](../docs/spec/cycle-based-orchestration-qa-strategy.md)
Gaps trace: [cycle-based-orchestration-gaps.md](../docs/spec/cycle-based-orchestration-gaps.md)

Dependency order: 1 → {2, 4, 5, 7, 11}, 10 → 6 → 9, {1, 7} → 8, 2 → 12. EPIC 10 starts immediately, in parallel with EPIC 1. EPICs 2, 4, 5, 7, and 11 run in parallel once EPIC 1 lands.

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

## EPIC 1: Start a named workstream and record a chosen cycle

### Why this EPIC exists

The factory routes work today through one repository-wide marker and a fixed playbook sequence. A user must name a process before starting, then follow it whether or not it fits. Nothing in the repository can hold two pieces of work at once. This EPIC delivers the first working traversal — name a topic, read what the repository evidence supports, choose the next cycle — and every later EPIC thickens that path instead of replacing it.

### Actor Goals

- Human operator starts a named workstream from the session menu and enters IDEA
- Cycle engine loads the delivery model from tracked source and rejects a model that breaks its schema
- Cycle engine recommends routes from artifact evidence, separating the zero, one, and several cases
- Human operator selects any cycle, with or without supporting evidence, and without an override step

### Demo

1. Select option B in the session menu and give the topic "Add rate limiting to the public API".
2. Read `.current-work/cycles/add-rate-limiting.yaml` and confirm it records the topic, cycle IDEA, revision 1, and attempt 1.
3. Confirm that a session binding file now exists for the current session.
4. Point the workstream at an accepted proposal and run the assessment.
5. Read the output. The route from IDEA to CONCEPT is recommended, its evidence is listed, and every other cycle is offered as an available choice.
6. Run `factory/scripts/cycle select CONCEPT` and confirm the state file records cycle CONCEPT at attempt 1 with revision 2.
7. Run `factory/scripts/cycle select REALIZE`, a route the model does not declare from CONCEPT. The command records the selection and warns that no declared route exists. It does not ask for a justification.
8. Add a `direction` field to one route in the delivery model and reload. Validation rejects the route and names the offending field.

### Scope

**In:**

- Engine package scaffold — create `packages/factory/engine/` with its package metadata and a dependency boundary that forbids the engine from importing scripts, configuration, agent definitions, skills, or the orchestrator package
- Delivery model — `packages/factory/engine/models/delivery.yaml` declaring the five cycles, the terminal DONE node, artifact declarations, trusted validator identifiers, per-cycle attempt limits, and every route with `from`, `to`, and `recommend_if`
- Cycle-model and cycle-state schemas — `packages/factory/engine/schemas/cycle-model-v1.schema.json` and `cycle-state-v1.schema.json`, both JSON Schema Draft 2020-12
- Model loading and validation — rejects unknown artifact references, unknown validator identifiers, executable commands in validator fields, and any `direction` or `classification` field on a route
- Route recommendation — evaluates each declared route from the current cycle and returns one of three results: no evidence-supported recommendation with warnings, one recommendation with its evidence, or several supported routes offered as choices without ranking
- Proposal readiness validator — the one artifact validator needed to make the IDEA-to-CONCEPT route assessable, returning the shared result shape of artifact type, artifact reference, assessed commit, individual checks, and warnings
- Workstream creation and cycle selection — `factory/scripts/cycle select`, writing the state file and updating the session binding, with attempt reset to 1 on every cycle change
- Session menu option B — replace playbook selection with workstream creation, capturing the topic and the optional originating proposal path

**Out:**

- The remaining twelve artifact validators from the readiness table (EPIC 6)
- Semantic assessment and reconciliation (EPIC 6)
- Listing, reopening, and switching workstreams (EPIC 2)
- Revision conflict detection and locking (EPIC 3)
- Attempt counting beyond the reset-to-1 rule (EPIC 4)
- Delegation grants (EPIC 5)

### Dependencies

None. This is the foundational EPIC.

### Boundaries

- Human touchpoint: `packages/factory/config/session-menu.md` (option B)
- Adapter: `packages/factory/scripts/cycle` (the one state-writing command)
- Engine: `packages/factory/engine/` (decision logic, writes nothing)
- Storage: `packages/factory/engine/models/`, `packages/factory/engine/schemas/`, `.current-work/cycles/`, `.current-work/session-bindings/`

### Domain Rules

- The engine returns immutable decisions and never writes repository state. Adapters own every write.
- A route declares only a source, a target, and its recommendation evidence. Direction and classification fields are rejected.
- The delivery model names validators by identifier. It can never contain a shell command.
- Failed or missing evidence produces a warning. It never removes a route and never prevents a human from selecting a cycle.
- The engine does not rank supported routes. When several qualify, the human chooses.
- Entering a cycle sets attempt to 1.
- A new workstream starts at revision 1 and attempt 1.
- Assessments read the current commit. The state file never copies requirements or assessment results.

### Size

2 stories.

Phase 3 reconciliation: the Phase 2 estimate was 3 stories (loader/validation, recommendations, adapter/menu). Phase 3 identified two natural capability seams instead: traversal (everything needed for a human to start a workstream and select any cycle) and recommendations (assessing evidence and presenting route choices). The old three-story split separated engine internals from the adapter, which produced horizontal stories that individually delivered nothing a human could demonstrate. The recut merges engine, adapter, and menu work into each vertical slice. ST-0254 is retired; its scope is folded into ST-0252.

### Building-Block Inventory

| Story   | Goal                                                                                                                                                                             | Tier     | Size | Basis                                                                                                                                                                                                           |
| ------- | -------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- | -------- | ---- | --------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| ST-0252 | The human starts a workstream from option B, the engine loads and validates the delivery model, and `cycle select` records any chosen cycle with warnings for undeclared routes. | standard | L    | New package `packages/factory/engine/`, two JSON schemas, the delivery model, model loader with five rejection paths, session menu option B, the `cycle select` adapter, state file and session binding writes. |
| ST-0253 | The adapter assesses each declared route's evidence and presents zero, one, or several recommendations; the human selects a cycle informed by the result.                        | standard | M    | Readiness evaluator, route recommender, proposal validator, shared result shape. Depends on ST-0252 for the loaded model and the selection path.                                                                |

## EPIC 2: Reopen one workstream and switch to another

### Why this EPIC exists

A traversal is only useful if it survives the end of a session. The factory holds one marker for the whole repository today, so a second piece of work overwrites the first and an interrupted session has nothing to return to. This EPIC makes workstreams durable and plural. A user can leave, return, pick up any of several topics, and be warned when the conversation has drifted onto different work.

### Actor Goals

- Human operator lists current workstreams with their topics and cycles, then continues one
- Human operator receives a suggestion to open a separate workstream when the conversation turns to a different objective
- Human operator confirms every switch. The factory never changes workstreams on its own.

### Demo

1. Create two workstreams on different topics and leave them at different cycles.
2. Start a fresh session and select option C. Both topics appear with their current cycles.
3. Select the second one. The session binding records that workstream's revision and the digest of its file contents.
4. The factory assesses repository evidence for that cycle and presents its route recommendations.
5. Confirm that neither state file changed during the reopen.
6. Begin describing unrelated work. The factory suggests opening a separate workstream and waits. Decline the suggestion.
7. Continue on the same unrelated objective. The factory does not repeat the suggestion.
8. Describe a third, different objective and accept the suggestion. The factory captures the usage boundary, creates the workstream, and rebinds the session.
9. Delete every workstream file and select option C. The factory offers option B or a return to the menu, and selects nothing on its own.

### Scope

**In:**

- Session menu option C — replace direct agent and playbook selection with a workstream list showing topic and cycle, binding the chosen workstream to the session and presenting its recommendations
- Empty-list handling — when no workstream file exists, offer option B or a return to the menu and select nothing automatically
- Session binding records — write the observed revision and the SHA-256 digest of the state file at bind time, using the existing usage-capture filesystem-key encoding for the path
- Workstream switch suggestion — detect an explicit topic change, a new proposal reference, or a different deliverable, then suggest creating or reopening a workstream and wait for confirmation
- Declined-suggestion memory — record a declined suggestion so the same apparent boundary is not raised twice for the same objective
- Usage boundary capture on a confirmed switch, when the producing command-line tool supports it

**Out:**

- Conflict detection between two sessions holding one workstream (EPIC 3)
- Workstream and cycle fields on captured usage records (EPIC 12)
- Resolving the next agent from cycle state (EPIC 7)

### Dependencies

EPIC 1 — workstream files, session bindings, and the delivery model must exist.

### Boundaries

- Human touchpoint: `packages/factory/config/session-menu.md` (option C, switch confirmation)
- Engine: Workstream Resolver in `packages/factory/engine/workstreams.py`
- Adapter: `packages/factory/scripts/cycle`
- Storage: `.current-work/cycles/`, `.current-work/session-bindings/`

### Domain Rules

- The factory never selects or switches a workstream without human confirmation.
- The factory raises the same apparent boundary only once unless the objective changes again.
- Clarifications, supporting research, and implementation detail stay in the current workstream. Only a distinct objective justifies a suggestion.
- A session binding is navigation state, not delivery evidence. Losing a binding must never lose delivery work.
- No repository-global active-workstream file exists. Each session resolves its workstream from its own binding.
- Session binding paths use the existing usage-capture filesystem-key encoding.

### Size

2 stories.

### Building-Block Inventory

| Story   | Goal                                                                                                                                             | Tier     | Size | Basis                                                                                                                                                       |
| ------- | ------------------------------------------------------------------------------------------------------------------------------------------------ | -------- | ---- | ----------------------------------------------------------------------------------------------------------------------------------------------------------- |
| ST-0255 | Option C lists every workstream with its topic and cycle, binds the chosen one to the session, and presents its recommendations.                 | standard | M    | Extends the option B adapter from ST-0252. The empty-list path and the digest record are the two additional behaviors. Replaces the existing option C tree. |
| ST-0256 | The factory suggests a separate workstream on a detected objective change, acts only on confirmation, and does not repeat a declined suggestion. | standard | M    | Detection criteria are named in the gaps report and need pinning down during grilling. Declined-suggestion memory is new session state.                     |

## EPIC 3: Run two sessions against one workstream without overwriting either

### Why this EPIC exists

Once several workstreams exist and several sessions can reach them, two sessions can write the same file. The losing change disappears silently, and a delegated run can continue against state that no longer exists. The quality strategy classifies every contract in this area as critical. This EPIC makes a losing write visible and harmless instead of silent and destructive.

### Actor Goals

- State adapter replaces a workstream file atomically, increments the revision, and refreshes the session binding
- State adapter refuses a write from a session holding a stale revision or a mismatched digest, and changes nothing
- State adapter serializes two sessions on one workstream while leaving different workstreams independent
- Delegated execution pauses and returns control to the human when it meets a conflict

### Demo

1. Bind session A and session B to the same workstream at revision 5.
2. Write from session A. The state file reaches revision 6 and session A's binding is updated to match.
3. Write from session B, which still expects revision 5. The command returns `stale_workstream_state` with the expected and current revisions, and writes nothing.
4. Confirm that the file still holds session A's change and that session B's binding is unchanged.
5. Edit the state file by hand without changing the revision. The next write from a session that observed the previous content returns a digest conflict.
6. Hold the lock in session A and attempt a write from session B. After five seconds session B returns `workstream_busy` and writes nothing.
7. Write to a second workstream from session B while session A holds the first lock. The second write succeeds immediately.
8. Interrupt a replacement mid-write. Read the state file and confirm it holds one complete version, either the previous one or the next one.
9. Meet a conflict during a delegated run. The run pauses and returns control to the human instead of retrying.

### Scope

**In:**

- Exclusive file lock per workstream at `.current-work/cycles/.locks/<workstream-id>.lock`, covering only the read, comparison, validation, and replacement, and released by the operating system when the process exits
- Five-second lock wait with a `workstream_busy` result that writes nothing when the wait expires
- Expected-state comparison — every mutation supplies the binding's observed revision and SHA-256 digest, and a mismatch returns `stale_workstream_state` with the expected and current revisions and a `refresh_and_confirm` next action
- Atomic replacement — write a temporary sibling file, flush it, then replace the state file in one operation, so an interruption always leaves one complete file
- Revision increment on every accepted mutation, followed by a binding update with the new revision and digest
- Stale-binding detection — an interruption between the two writes leaves a stale binding that the next mutation detects
- Delegated-run conflict handling — pause and hand control to the human rather than merge or retry

**Out:**

- Merging two concurrent changes. The engine never merges and never retries a rejected mutation.
- Replacing the locking primitive. A later implementation may swap it while keeping these observable rules.
- Locking read-only assessment. Atomic replacement already exposes one complete file.

### Dependencies

EPIC 1 — the state file and the writing adapter must exist.

### Boundaries

- Adapter: `packages/factory/scripts/cycle` (lock, compare, replace)
- Engine: Workstream Resolver (revision and digest consistency)
- Storage: `.current-work/cycles/`, `.current-work/cycles/.locks/`, `.current-work/session-bindings/`

### Domain Rules

- A stale session never overwrites newer workstream state.
- One concurrent change succeeds. The other pauses without writing.
- Sessions that change different workstreams never block each other.
- The digest covers the exact state-file bytes, so it detects a direct edit that leaves the revision untouched.
- A rejected mutation leaves the rejecting session's binding unchanged. A refresh updates the observation and never repeats the rejected mutation.
- An accepted mutation increments the revision exactly once.
- The lock file contains no workflow data.

### Size

2 stories.

### Building-Block Inventory

| Story   | Goal                                                                                                                                               | Tier     | Size | Basis                                                                                                                                         |
| ------- | -------------------------------------------------------------------------------------------------------------------------------------------------- | -------- | ---- | --------------------------------------------------------------------------------------------------------------------------------------------- |
| ST-0257 | An accepted write replaces the state file atomically and increments the revision, and a stale revision or digest is refused unchanged.             | standard | M    | Adds the compare-and-replace path to the ST-0252 adapter. Interruption behavior needs a fault-injection test rather than new production code. |
| ST-0258 | Two sessions on one workstream serialize under a five-second lock, different workstreams stay independent, and a delegated run pauses on conflict. | standard | M    | Concurrency tests are the bulk of the work. The lock itself is small. The delegated-run pause needs a seam that EPIC 5 later fills.           |

## EPIC 4: Retry a cycle until the delegated attempt limit stops the loop

### Why this EPIC exists

Delegated execution can repeat a failing cycle forever and spend a budget with nobody watching. A limit on unattended attempts is the only mechanism in this proposal that bounds that cost. The limit must never become a gate against the human, so the same command has to behave differently depending on who asked. This EPIC delivers both behaviors and the counter they share.

### Actor Goals

- Cycle engine allows a delegated retry below the declared limit and pauses at the limit without changing state
- Human operator retries at or above the limit and continues with a warning, without an override step
- State adapter resets the attempt counter when the cycle changes or the selected work changes, and leaves it alone otherwise
- Cycle engine refuses to count an attempt when the retry state is malformed

### Demo

1. Enter REALIZE, whose declared limit is 5. The state file records attempt 1.
2. Run four delegated retries. The attempt reaches 5 and each retry returns `allowed`.
3. Run a fifth delegated retry. The command returns `paused` with reason `delegated_attempt_limit_reached`, the cycle, attempt 5, limit 5, and the next action `request_human_direction`. The state file is unchanged.
4. Run a human retry. The command returns `allowed_with_warning`, the attempt becomes 6, and no override flag is required.
5. Select a different cycle. The attempt returns to 1.
6. Return to the previous cycle and change the `work` list without changing the cycle. The attempt returns to 1.
7. Reassess artifacts, edit a file, and start a new session. The attempt does not change.
8. Corrupt the attempt field and retry. The command returns `invalid_state` and writes nothing.
9. Accept a retry, then let the assigned execution fail to start. Read the state file and confirm the increment remains.

### Scope

**In:**

- Per-cycle `delegated_attempt_limit` in the delivery model, one positive integer for each of the five cycles
- Retry evaluator returning one of four results — `allowed`, `paused`, `allowed_with_warning`, or `invalid_state` — from the attempt, the limit, and whether the request is human-authored or delegated
- `factory/scripts/cycle retry` — identifies the requester, asks the engine, and increments the attempt only on an allowed result
- Reset rules — a cycle change or a `work` list change sets the attempt to 1, including when the cycle stays the same
- Non-reset rules — changing sessions, resuming a workstream, reassessing artifacts, and editing files leave the attempt alone
- Attempt consumption — once the adapter accepts a retry, the increment stands through every later outcome, including a failure to start or complete the execution

**Out:**

- Retry history. The state file keeps only the current attempt; usage and execution records supply history.
- Delegation grants themselves (EPIC 5). This EPIC only distinguishes a delegated request from a human one.

### Dependencies

EPIC 1 — the delivery model, the state file, and the writing adapter must exist.

### Boundaries

- Adapter: `packages/factory/scripts/cycle` (`retry` subcommand)
- Engine: Retry Evaluator in `packages/factory/engine/delegation.py`
- Storage: `packages/factory/engine/models/delivery.yaml`, `.current-work/cycles/`

### Domain Rules

- Retry limits stop unattended loops. They never prevent a human from continuing.
- A delegated retry at the limit changes nothing and returns an immutable paused result.
- A human retry at or above the limit proceeds with a warning and needs no override flag or justification.
- Entering a cycle starts at attempt 1. Selecting a different cycle or changing the work list resets the attempt to 1.
- Malformed retry state returns `invalid_state` without writing.
- The adapter never rolls an accepted attempt back.
- Every cycle declares a positive `delegated_attempt_limit`.

### Size

2 stories.

### Building-Block Inventory

| Story   | Goal                                                                                                                                   | Tier     | Size | Basis                                                                                                                         |
| ------- | -------------------------------------------------------------------------------------------------------------------------------------- | -------- | ---- | ----------------------------------------------------------------------------------------------------------------------------- |
| ST-0259 | The retry evaluator returns allowed, paused, allowed with warning, or invalid state from the attempt, the limit, and the requester.    | standard | M    | Pure decision logic with an explicit result table. The limit values extend the ST-0252 model and schema.                      |
| ST-0260 | `cycle retry` increments the attempt only on an allowed result, and cycle or work changes reset it to 1 while other activity does not. | standard | M    | Adapter work on the ST-0257 write path. The reset and non-reset lists are the test surface and each entry needs its own case. |

## EPIC 5: Grant a route and let the factory advance without asking again

### Why this EPIC exists

Without delegation, every transition needs a human at the keyboard, and a five-cycle traversal becomes five interruptions. Delegation is also the sharpest safety boundary in the proposal: an engine that could widen its own authority would remove the human from the loop entirely. This EPIC delivers unattended advancement and fixes the boundary that keeps the grant human-owned.

### Actor Goals

- Human operator records an ordered sequence of cycle selections that the engine follows without asking
- Human operator records a destination and lets the engine continue only while the evidence is unambiguous
- Cycle engine pauses when a grant ends, when the choice falls outside the grant, or when execution fails
- Cycle engine never creates, extends, or broadens a grant

### Demo

01. Write the grant `route: [CONCEPT, REFINE, REALIZE]` into a workstream at IDEA and start a delegated run.
02. The engine selects CONCEPT, then REFINE, then REALIZE, showing the recommendation evidence and any warnings at each step.
03. Remove the evidence supporting one of those routes and run the same grant again. The engine still follows the recorded choice and records the warning.
04. Let the run reach the end of the sequence. The engine pauses and asks for human direction.
05. Replace the grant with `through: REALIZE` from a cycle where exactly one route has supporting evidence. The engine continues.
06. Remove that evidence so no route qualifies. The engine pauses.
07. Restore evidence for two routes. The engine pauses and presents both choices without ranking them.
08. Restore a single-evidence path and let the run reach REALIZE. The engine pauses at the named destination.
09. Make the assigned execution fail for a technical reason. The run stops.
10. Ask the engine to widen the grant. It refuses and names the human as the only author.

### Scope

**In:**

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
- The delegated attempt limit itself (EPIC 4). This EPIC consumes the delegated-or-human distinction that EPIC 4 delivers.

### Dependencies

EPIC 1 — the delivery model, route recommendation, and the writing adapter must exist.

### Boundaries

- Human touchpoint: the `delegation` block a human writes into the workstream state file
- Engine: Delegation Evaluator in `packages/factory/engine/delegation.py`, Route Recommender in `recommendations.py`
- Adapter: `packages/factory/scripts/cycle`
- Storage: `packages/factory/engine/schemas/cycle-state-v1.schema.json`, `.current-work/cycles/`

### Domain Rules

- A grant contains exactly one form: an explicit route or a destination.
- An explicit route is a recorded human choice. Failed recommendation evidence does not invalidate it.
- A destination grant continues only while exactly one route has supporting evidence.
- The engine pauses at the named destination, at the end of a grant, and when the next choice falls outside it.
- A technical execution failure always stops the run.
- Only the human creates, replaces, revokes, or broadens a grant.
- Delegated execution may continue without the human present. The grant supplies the authority; presence does not.
- IDEA and REFINE request human direction when no grant contains the needed decision.

### Size

2 stories.

### Building-Block Inventory

| Story   | Goal                                                                                                                                   | Tier     | Size | Basis                                                                                                                                                 |
| ------- | -------------------------------------------------------------------------------------------------------------------------------------- | -------- | ---- | ----------------------------------------------------------------------------------------------------------------------------------------------------- |
| ST-0261 | An explicit route grant follows its ordered cycle selections, keeps a choice whose evidence failed, and pauses when the sequence ends. | standard | M    | Extends the ST-0252 state schema with the grant block and adds an evaluator over the ST-0253 recommender. The pause seam already exists from ST-0258. |
| ST-0262 | A destination grant continues only on exactly one supported route, pauses on zero, several, or the destination, and stops on failure.  | standard | M    | Second evaluation mode over the same recommender result. Five distinct pause conditions, each with its own test.                                      |

## EPIC 6: Read the evidence behind every route the factory offers

### Why this EPIC exists

EPIC 1 makes one route assessable through the proposal validator. The other twelve artifacts in the readiness table have no validator, so every route beyond IDEA-to-CONCEPT recommends nothing and shows no evidence. Until the readiness table is complete, the factory can record a human's choice but cannot inform it. This EPIC delivers the evidence that makes the recommendation useful.

### Actor Goals

- Cycle engine reports each referenced artifact's readiness in one shared result shape
- Cycle engine runs mechanical validation unconditionally for every referenced artifact
- Cycle engine runs semantic assessment when the cycle changed code or a canonical artifact, and reports it as not applicable otherwise
- Human operator reads per-artifact checks and warnings before choosing the next cycle

### Demo

1. Prepare a repository with a scope map, an entity model, an architecture model, feature files, a gaps report, decision records, concept reviews, an epic plan, and selected stories.
2. Run the cycle assessment. Every artifact reports its type, its reference, the assessed commit, its individual checks, and its warnings.
3. Break one feature file so it no longer parses. The assessment reports that check as failed and keeps every other result intact.
4. Confirm that the route depending on that artifact is no longer recommended, that a warning explains why, and that the cycle remains selectable.
5. Change a source file and rerun. The assessment reports that reconciliation ran and gives its result.
6. Change `docs/spec/scope-map.md` and rerun. Reconciliation runs again.
7. Change neither code nor a canonical artifact and rerun. The assessment reports reconciliation as not applicable.
8. Rename an artifact referenced by the delivery model. The assessment reports the missing artifact rather than skipping it.

### Scope

**In:**

- Twelve further trusted validators covering the scope map, entity model, architecture model, feature specifications, gaps report, decision records, concept reviews, epic plan, selected stories, realization result, research brief, and research report
- The shared validator result shape — artifact type, artifact reference, assessed commit, individual check results, and warnings — applied to every validator including the proposal validator from EPIC 1
- Mechanical validation that runs unconditionally for every artifact the delivery model references
- Semantic assessment that runs only when the cycle changed code or a canonical artifact, and reports as not applicable otherwise
- Reconciliation as a standard transition assessment rather than a separate phase
- Collection rules — fixed paths identify canonical artifacts, an authoritative artifact lists the required members of a collection, and a file glob never defines a complete collection
- The generic route invariant that visits every route loaded from the delivery model and fails when a source, target, artifact, validator, or predicate reference does not resolve
- Assessment output that shows evidence, warnings, and every other cycle at each cycle exit

**Out:**

- Automated semantic ranking between downstream routes (deferred by the proposal)
- Project-declared validators and artifact declarations. These wait for an extension contract that defines namespacing and failure behavior.
- Producing the canonical concept artifacts themselves (EPICs 9 and 10). This EPIC assesses them.

### Dependencies

EPIC 1 — the delivery model, the shared result shape, and the recommender must exist.
EPIC 10 — the entity-model validator needs the canonical LinkML contract.

### Boundaries

- Human touchpoint: `packages/factory/scripts/cycle` (assessment output)
- Engine: Readiness Evaluator in `packages/factory/engine/readiness.py`, Route Recommender in `recommendations.py`
- Existing checks reused as evidence: `spec-lint`, `arch-lint`, `backlog-lint`, `link-check`, `mermaid-lint`, `mdformat`, `schema-validate`, `policy-validate`
- Storage: `docs/spec/`, `docs/arc42/`, `docs/adr/`, `docs/reviews/`, `backlog/`

### Domain Rules

- Every validator returns the same result fields: artifact type, artifact reference, assessed commit, individual checks, and warnings.
- Mechanical validation runs unconditionally for referenced artifacts.
- Semantic assessment runs only when the cycle changed code or a canonical artifact.
- Neither validation layer authorizes a transition. Both only supply evidence.
- Reconciliation is a transition assessment, not a cycle.
- Fixed paths identify canonical artifacts. An authoritative artifact lists a collection's required members.
- A file glob may discover candidates. It never defines a complete collection.
- The canonical concept model is authoritative when artifacts disagree.

### Size

4 stories.

### Building-Block Inventory

| Story   | Goal                                                                                                                                       | Tier     | Size | Basis                                                                                                                                                          |
| ------- | ------------------------------------------------------------------------------------------------------------------------------------------ | -------- | ---- | -------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| ST-0263 | Validators for the scope map, entity model, architecture model, and feature specifications report readiness in the shared result shape.    | standard | L    | Four validators wrapping existing checks — `spec-lint`, `arch-lint`, and the EPIC 10 entity-model checks. Each needs valid, invalid, and stale-evidence tests. |
| ST-0264 | Validators for the gaps report, decision records, concept reviews, epic plan, and selected stories report readiness in the same shape.     | standard | L    | Five validators. `backlog-lint` covers two of them; the review and decision-record checks are new parsing work.                                                |
| ST-0265 | Validators for the realization result, research brief, and research report report readiness in the same shape.                             | standard | M    | Three validators over existing gates and `schema-validate`. The realization validator aggregates test, quality, review, and reconciliation results.            |
| ST-0266 | The assessment runs mechanical checks unconditionally, runs reconciliation only on code or canonical-artifact change, and prints evidence. | standard | M    | Wires the twelve validators into the recommender and adds the change-detection rule and the generic route invariant.                                           |

## EPIC 7: Let run-step pick the next agent from cycle state

### Why this EPIC exists

The delivery model can describe a traversal, but nothing in the factory acts on it until `run-step` stops reading the playbook marker. Agent definitions still carry `phase:` ordinals from the linear model, which the engine cannot map onto cycles. Sixteen agents are affected. This EPIC connects the cycle state to the dispatcher so the model starts driving real work.

### Actor Goals

- Agent definition declares which cycles it is eligible for instead of a phase ordinal
- Cycle engine determines which agents and skills are eligible for the current cycle and work selection
- `run-step` resolves the next agent from cycle state and the delivery model, then dispatches it
- `run-step` re-derives the next action from observable state after an interruption

### Demo

1. Read any agent definition and confirm it carries cycle eligibility tags and no `phase:` ordinal.
2. Regenerate the catalog and confirm every agent and skill name from the acceptance commit is still indexed.
3. Put a workstream into CONCEPT and run `run-step`. It names the requirements agent from cycle eligibility and starts it.
4. Confirm that `run-step` never reads `.current-work/playbook-state.yml`.
5. Interrupt the session and run `run-step` again in a new session. It derives the same next action from the workstream file and the repository.
6. Move the workstream to REALIZE and run `run-step`. It resolves the implementation agent instead.
7. Run `run-step` twice at once. The second invocation refuses rather than starting a duplicate.

### Scope

**In:**

- Cycle eligibility metadata on every agent definition, replacing the `phase:` ordinal that 16 agents carry today
- Catalog regeneration so `index-lint` reads the new field and keeps every indexed name
- Dispatch eligibility in the engine — determine which agents and skills apply to the current cycle and the selected work
- `run-step` migration — resolve the next agent from the workstream state file and the delivery model, and stop reading the playbook marker
- Kept `run-step` contract — the same skill name, repository-derived resume, one invocation at a time, and no blind retry

**Out:**

- Deleting playbook files. They remain as reference documentation for known-good sequences.
- The `phase` command stub and cycle-native `transition-lint` (EPIC 8)
- Changing the dispatcher's own contract. `trigger` keeps its behavior.

### Dependencies

EPIC 1 — cycle state and the delivery model must exist.

### Boundaries

- Human touchpoint: `packages/factory/skills/run-step/SKILL.md`
- Engine: Dispatch Eligibility in `packages/factory/engine/dispatch.py`
- Dispatcher: `packages/factory/scripts/trigger`, `packages/factory/scripts/index-lint`
- Storage: `packages/factory/agents/*.md`, `packages/factory/INDEX.yaml`, `.current-work/cycles/`

### Domain Rules

- Agent definitions carry cycle eligibility. Phase ordinals no longer exist.
- Every agent and skill name indexed at the acceptance commit remains available.
- `run-step` keeps its skill name, its repository-derived resume, one invocation at a time, and no blind retry.
- No delivery transition reads a playbook finite state machine file as its authority after cutover.
- The engine determines eligibility. It does not launch anything; the dispatcher does.

### Size

2 stories.

### Building-Block Inventory

| Story   | Goal                                                                                                                          | Tier     | Size | Basis                                                                                                                                     |
| ------- | ----------------------------------------------------------------------------------------------------------------------------- | -------- | ---- | ----------------------------------------------------------------------------------------------------------------------------------------- |
| ST-0267 | Every agent definition carries cycle eligibility instead of a phase ordinal, and the engine resolves eligible agents from it. | standard | M    | Mechanical edit across 16 agent files plus `index-lint` and the generated integrations. The eligibility resolver itself is small.         |
| ST-0268 | `run-step` names the next agent from the workstream file and the delivery model, and re-derives it after an interruption.     | standard | M    | Rewrites one skill file. Small surface, but it changes the resume contract every consumer depends on. Needs characterization tests first. |

## EPIC 8: Retire the phase command while every existing check behaves as before

### Why this EPIC exists

The proposal replaces the routing authority but promises that every other command keeps its behavior. That promise is only worth the checks that verify it. Two commands must change — `phase` becomes a diagnostic stub and `transition-lint` moves to the cycle model — while roughly twenty other commands must be shown not to have changed. This EPIC performs the cutover and supplies the evidence that nothing else moved.

### Actor Goals

- Human operator running the old `phase` command receives a message naming the replacement instead of a silent failure
- `transition-lint` validates cycle models and workstream state files, and reports failed recommendation evidence as a warning
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

- `phase` diagnostic stub — replace the 627-line transition implementation with a stub that exits 2 and names the corresponding `cycle` command, and keep it for one release
- Cycle-native `transition-lint` — replace phase-order rejection with cycle-model and workstream-state integrity checks, and exit zero on failed recommendation evidence with warnings
- Catalog compatibility check — compare indexed agent and skill names against the acceptance commit and permit only the intentional replacements
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

EPIC 1 — the cycle command and the delivery model must exist.
EPIC 7 — every factory consumer must use cycle state before `phase` can be retired.

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

| Story   | Goal                                                                                                                          | Tier     | Size | Basis                                                                                                                            |
| ------- | ----------------------------------------------------------------------------------------------------------------------------- | -------- | ---- | -------------------------------------------------------------------------------------------------------------------------------- |
| ST-0269 | `phase advance` and `phase retry` exit 2 and name their `cycle` replacements without performing any transition.               | standard | S    | Deletes 627 lines and adds a stub. Small code change, but the removal must land only after ST-0268 lands.                        |
| ST-0270 | `transition-lint` accepts a valid cycle model and state file, rejects invalid ones, and warns at exit zero on evidence.       | standard | M    | Rewrites a 389-line script against the ST-0252 schemas. The warning-at-exit-zero rule inverts the current failure behavior.      |
| ST-0271 | Characterization tests fix the behavior of every kept command, and a catalog comparison permits only the listed replacements. | standard | L    | Roughly twenty commands, each with known-good and known-bad cases. Also holds the installed-shape and dependency-boundary tests. |

## EPIC 9: Turn an inherited repository into a reviewed concept baseline

### Why this EPIC exists

Every delivery route beyond IDEA assumes a scope map, an entity model, and an architecture model already exist. An inherited repository has none of them, so a brownfield user meets a graph that recommends nothing. This EPIC gives that user a defined entry: reconstruct the three canonical objects from code, tests, persistence schemas, and infrastructure definitions, then see exactly what evidence is still missing.

### Actor Goals

- Brownfield operator receives all three canonical concept objects from the mandatory first stage of onboarding
- Cycle engine recommends feature delivery when all three objects exist, validate, and carry no unresolved major review finding
- Brownfield operator selects another cycle with an incomplete baseline and continues with warnings, without an override step

### Demo

1. Fit a repository that has code and tests but no specification.
2. Run brownfield onboarding. Its first stage produces `docs/spec/scope-map.md`, `docs/spec/entity-model.yaml`, and `docs/arc42/architecture.dsl`.
3. Confirm that the entity relationship diagram is part of that first stage, not the optional second stage.
4. Run the bootstrap assessment. All three objects validate, no major review finding is open, and the assessment recommends feature delivery.
5. Delete the entity model and rerun. The assessment names the missing evidence and still recommends completing CONCEPT.
6. Select REALIZE anyway. The command records the selection, repeats the warnings, and asks for no justification.
7. Confirm that the bootstrap created no epic plan and entered no REALIZE cycle on its own.
8. Start a new change from IDEA with a proposal and confirm the normal delivery route applies.

### Scope

**In:**

- Brownfield onboarding first stage produces all three canonical concept objects, with the entity relationship diagram included
- Bootstrap assessment — recommend feature delivery when the three objects exist, pass deterministic validation, and have no unresolved major review finding
- Missing-evidence reporting — name each absent or failing object when the baseline is incomplete
- Continue-with-warnings path — a human selection of another cycle proceeds and repeats the warnings
- Bootstrap exit — leave the repository delivery-ready without creating an epic plan or entering REALIZE
- Fitting recorded as a prerequisite outside the delivery graph

**Out:**

- The deeper reverse-engineering second stage of onboarding. It stays optional and is not a delivery prerequisite.
- Requiring an accepted proposal for the bootstrap. Existing code is the evidence.
- The entity-model contract itself (EPIC 10). This EPIC consumes it.

### Dependencies

EPIC 6 — the concept validators must exist before the bootstrap can assess the baseline.
EPIC 10 — the canonical entity-model contract must exist before onboarding can produce it.

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
| ST-0272 | The mandatory first stage of brownfield onboarding produces the scope map, the entity model, and the architecture model. | standard | M    | Restructures an existing playbook and moves the entity relationship diagram from the optional stage into the mandatory one. |
| ST-0273 | The bootstrap assessment recommends feature delivery on a complete baseline and names the missing evidence otherwise.    | standard | M    | Composes the ST-0263 validators into one entry assessment. The continue-with-warnings path reuses the ST-0252 selection.    |

## EPIC 10: Keep one machine-readable entity model and generate everything else from it

### Why this EPIC exists

The factory has no canonical domain model today: `docs/spec/entity-model.yaml` does not exist, and entity descriptions live in prose that no check can read. Three routes depend on entity-model evidence, and none of them can produce it. This EPIC establishes the machine-readable source, the checks that decide whether it is ready, and the rule that every other representation is generated from it.

### Actor Goals

- Modeller writes one machine-readable entity model that passes mechanical readiness checks
- Modeller regenerates the Markdown and diagram projections and confirms they add no model information of their own
- Developer generates validation code from the model and sees an invalid payload rejected before it reaches storage

### Demo

1. Write `docs/spec/entity-model.yaml` in LinkML, a schema language for describing entities, their slots, and their relationships.
2. Run the entity-model readiness check. The file passes metamodel validation, the linter reports no error, and every referenced class and slot resolves.
3. Add a slot backed by a JSON column without declaring its value-object class. The check fails and names the unresolved reference.
4. Declare the value-object class inline and remove its schema-version slot. The check fails again and names the missing slot.
5. Fix both faults and regenerate `docs/spec/entity-model.md` and `docs/assets/images/entity-model.svg`. Both follow the source.
6. Add a sentence to the Markdown projection that the source does not contain. The check reports the projection as out of date with its source.
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
- Wiring the entity-model validator into the route assessment (EPIC 6).

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
| ST-0274 | `docs/spec/entity-model.yaml` exists in LinkML and a readiness check reports each mechanical criterion as a separate result.                      | standard | L    | New file and new tooling. Seven readiness criteria, each needing a failing case. LinkML is a new dependency for this repository. |
| ST-0275 | The Markdown and diagram projections regenerate from the model, and a hand-edited projection is reported as out of date.                          | standard | M    | Generation plus a staleness comparison. Follows the existing derived-artifact pattern used for architecture diagrams.            |
| ST-0276 | A JSON-backed slot resolves to an inline value-object class, generated validation rejects an invalid payload, and a round trip keeps every field. | standard | M    | Code generation and a persistence integration test. This repository has no database, so the test needs a representative fixture. |

## EPIC 11: Send a delivery question to research and bring the answer back

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
| ST-0277 | A brief created from a delivery cycle records all four delivery-link fields, and a standalone brief omits them. | standard | S    | Adds four optional fields to an existing schema and template. The conditional requirement rule is the only subtle part. |
| ST-0278 | A validated report from a linked brief resumes the declared return cycle and records the report reference.      | standard | M    | Connects report validation to the ST-0252 selection path. Standalone completion must stay outside the delivery graph.   |

## EPIC 12: Compare what each workstream and each cycle cost

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
4. Run a per-invocation producer and a cumulative producer across a confirmed workstream switch. Both attribute the work on either side of the boundary to the right workstream.
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

EPIC 2 — session bindings must record the workstream before capture can read them.

### Boundaries

- Producer: `packages/factory/scripts/usage-capture`
- Contract: `packages/factory/contracts/usage-record/`
- Consumer: Usage Analysis Runtime, `packages/factory/scripts/usage-query`
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
| ST-0279 | The usage-record contract carries three optional workstream fields, and capture populates them from the binding or leaves them null. | standard | M    | Extends a published schema and its compatibility manifest. The no-import rule between capture and the engine needs a boundary test.   |
| ST-0280 | A child agent inherits the parent workstream, and boundary snapshots attribute cumulative usage to the right workstream.             | standard | M    | Touches the dispatch path and the snapshot arithmetic. Cumulative producers are the hard case and need a cross-boundary fixture.      |
| ST-0281 | Usage analysis groups by workstream, by cycle, and by both, and reports unattributable records as unavailable.                       | standard | M    | Adds dimensions to the existing published view. Follows the established query-model pattern. The unavailable case must not be silent. |
