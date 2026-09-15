# EPICs — Cycle-Based Orchestration

Proposal trace: [cycle-based-orchestration.md](../docs/proposals/cycle-based-orchestration.md)
Specification trace: [cycle-based-orchestration.feature](../docs/spec/cycle-based-orchestration.feature)
Architecture trace: [ADR-0017](../docs/adr/0017-cycle-based-orchestration-supersedes-linear-playbook-fsm.md), [ADR-0018](../docs/adr/0018-concept-internal-sequence-is-agent-owned.md), [§5.3 Cycle Engine](../docs/arc42/05_building_block_view.md#53-level-2-component-view----cycle-engine), [§5.4 State Adapter](../docs/arc42/05_building_block_view.md#54-level-2-component-view----state-adapter)
QA strategy trace: [cycle-based-orchestration-qa-strategy.md](../docs/spec/cycle-based-orchestration-qa-strategy.md)
Gaps trace: [cycle-based-orchestration-gaps.md](../docs/spec/cycle-based-orchestration-gaps.md)

Dependency order: 1 → {2, 3, 4, 6, 9, 11}, 4 → 5, {1, 2} → 10, 7 → 8, 6 → 8. EPIC 7 has no dependency and starts immediately. EPICs 2, 3, 4, 6, 9, and 11 are parallelizable after EPIC 1.

Story identifiers in the building-block inventories are provisional. Phase 4 allocates the final identifiers against the backlog at the time of writing.

## Shared vocabulary

These terms appear across every EPIC. Each is glossed once here and used without repetition afterwards.

- **Workstream** — one traversal of the delivery graph, recorded as a single YAML file under `.current-work/cycles/`. A repository may hold several at once.
- **Cycle** — the workstream's current stage. The engine models five: IDEA, CONCEPT, ROADMAP, REFINE, and REALIZE, plus a terminal DONE node.
- **Route** — a declared edge from one cycle to another, carrying the evidence that would support recommending it.
- **Delivery model** — the YAML file declaring every cycle, artifact, and route.
- **Cycle engine** — the code that computes decisions. It reads the repository and never writes to it.
- **State adapter** — the commands that write files. They ask the engine for a decision, then record the result.
- **Session binding** — a file recording which workstream the current command-line session is working on.
- **Delegation grant** — a human-authored record permitting the engine to advance through named cycles without asking again.

## EPIC 1: Traverse a workstream from a topic to a chosen next cycle

### Why this EPIC exists

The factory routes work today through a single repository-wide marker and a fixed playbook sequence. A user must name a process before starting and then follow it whether or not it fits. Nothing in the repository can represent two pieces of work in flight at once. This EPIC delivers the first working traversal — name a topic, see what the repository evidence supports, choose the next cycle — and every later EPIC thickens that path rather than replacing it.

### Actor Goals

- Human operator starts a named workstream from the session menu and enters IDEA
- Cycle engine loads the delivery model from tracked source and rejects a model that is structurally invalid
- Cycle engine recommends routes from artifact evidence, distinguishing zero, one, and several supported routes
- Human operator selects any cycle, with or without supporting evidence, and without an override ceremony

### Demo

1. Select option B in the session menu and give the topic "Add rate limiting to the public API".
2. Read `.current-work/cycles/add-rate-limiting.yaml` and confirm it records the topic, cycle IDEA, revision 1, and attempt 1.
3. Confirm a session binding file now exists for the current session.
4. Point the workstream at an accepted proposal and run the assessment.
5. Read the output: the route from IDEA to CONCEPT is recommended, its evidence is listed, and every other cycle is offered as an available choice.
6. Run `factory/scripts/cycle select CONCEPT` and confirm the state file records cycle CONCEPT at attempt 1 with revision 2.
7. Run `factory/scripts/cycle select REALIZE`, a route the model does not declare from CONCEPT. The command records the selection and prints a warning that no declared route exists. It does not ask for a justification.
8. Edit the delivery model to add a `direction` field to one route and reload. Validation rejects the route and names the offending field.

### Scope

**In:**

- Engine package scaffold — create `packages/factory/engine/` with its package metadata and a dependency boundary that forbids the engine from importing scripts, configuration, agent definitions, or the orchestrator package
- Delivery model — `packages/factory/engine/models/delivery.yaml` declaring the five cycles, the terminal DONE node, artifact types, trusted validator identifiers, per-cycle attempt limits, and every route with `from`, `to`, and `recommend_if`
- Cycle model and cycle state schemas — `packages/factory/engine/schemas/cycle-model-v1.schema.json` and `cycle-state-v1.schema.json`, both JSON Schema Draft 2020-12
- Model loading and validation — rejects unknown artifact references, unknown validator identifiers, executable commands in validator fields, and any `direction` or `classification` field on a route
- Route recommendation — evaluates each declared route from the current cycle and returns one of three results: no evidence-supported recommendation with warnings, a single recommendation with its evidence, or several supported routes presented as choices without ranking
- Proposal readiness validator — the one artifact validator needed to make the IDEA-to-CONCEPT route assessable, returning the shared result shape of artifact type, artifact reference, assessed commit, individual checks, and warnings
- Workstream creation and cycle selection — `factory/scripts/cycle select`, writing the state file and updating the session binding, with attempt reset to 1 on every cycle change
- Session menu option B — replace playbook selection with workstream creation, capturing the topic and the optional originating proposal path

**Out:**

- The remaining twelve artifact validators from the readiness table (EPIC 6)
- Semantic assessment and reconciliation (EPIC 6)
- Listing, reopening, and switching workstreams (EPIC 2)
- Revision conflict detection and locking (EPIC 3)
- Retry counting beyond the reset-to-1 rule (EPIC 4)
- Delegation grants (EPIC 5)

### Dependencies

None. This is the foundational EPIC.

### Boundaries

- Human touchpoint: `packages/factory/config/session-menu.md` (option B)
- Adapter: `packages/factory/scripts/cycle` (state-writing command)
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

3 stories.

### Building-Block Inventory

| Story   | Goal                                                                                                                                                                    | Tier     | Size | Basis                                                                                                                                                                      |
| ------- | ----------------------------------------------------------------------------------------------------------------------------------------------------------------------- | -------- | ---- | -------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| ST-0252 | The engine loads the delivery model from tracked source and rejects unknown artifacts, unknown validators, executable commands, and direction or classification fields. | standard | L    | New package with no existing code to extend. Two JSON schemas, the full route table, and a loader with five distinct rejection paths. Well specified, so ambiguity is low. |
| ST-0253 | Evaluating the declared routes from a cycle returns no recommendation, one recommendation, or several choices, each carrying its evidence and warnings.                 | standard | M    | Pure decision logic over loaded data. The cardinality table is explicit. Needs the proposal validator and the shared result shape.                                         |
| ST-0254 | Choosing option B creates a workstream and a session binding, and `cycle select` records the chosen cycle at attempt 1.                                                 | standard | L    | Crosses menu prose, a new command-line adapter, and two new state files. Replaces existing playbook-selection text in `session-menu.md`.                                   |

## EPIC 2: Resume and manage several workstreams across sessions

### Why this EPIC exists

A single traversal is only useful if it survives the end of a session. Today the factory holds one marker for the whole repository, so a second piece of work overwrites the first and an interrupted session has nothing to return to. This EPIC makes workstreams durable and plural: a user can leave, come back, pick up any of several topics, and be warned when the conversation has drifted onto different work.

### Actor Goals

- Human operator lists current workstreams with their topics and cycles, and continues one
- Human operator receives a suggestion to open a separate workstream when the conversation turns to a different objective, and the factory never switches without confirmation
- `run-step` skill resolves the next agent from cycle state rather than the playbook marker, and re-derives it after an interruption

### Demo

1. Create two workstreams on different topics.
2. Start a fresh session and select option C. Both topics appear with their current cycles.
3. Select the second one. The session binding records the workstream's revision and its content digest.
4. The factory assesses repository evidence for that cycle and presents route recommendations.
5. Begin describing unrelated work. The factory suggests opening a separate workstream and waits. Decline it.
6. Continue on the same unrelated objective. The factory does not repeat the suggestion.
7. Delete every workstream file and select option C. The factory offers option B or a return to the menu, and selects nothing on its own.
8. Interrupt a session mid-cycle, then run `run-step` in a new session. It names the next agent from the workstream file and never reads `.current-work/playbook-state.yml`.

### Scope

**In:**

- Session menu option C — replace playbook selection with a workstream list showing topic and cycle, binding the chosen workstream to the session and presenting its recommendations
- Empty-list handling — when no workstream file exists, offer option B or a return to the menu and select nothing automatically
- Session binding records — write the observed revision and the content digest of the state file at bind time
- Workstream switch suggestion — detect an explicit topic change, a new proposal reference, or a different deliverable, then suggest creating or reopening a workstream and wait for confirmation
- Declined-suggestion memory — record a declined suggestion so the same apparent boundary is not raised twice for the same objective
- Usage boundary capture on a confirmed switch, when the producing command-line tool supports it
- `run-step` migration — resolve the next agent from the workstream state file and the delivery model, and stop reading the playbook marker

**Out:**

- Conflict detection between two sessions holding the same workstream (EPIC 3)
- Workstream and cycle fields on captured usage records (EPIC 11)
- Removing the playbook marker from unrelated consumers (EPIC 10)

### Dependencies

EPIC 1 — workstream files, session bindings, and the delivery model must exist.

### Boundaries

- Human touchpoint: `packages/factory/config/session-menu.md` (option C, switch confirmation)
- Skill: `packages/factory/skills/run-step/SKILL.md` (next-action resolution)
- Adapter: `packages/factory/scripts/cycle`
- Dispatcher: `packages/factory/scripts/trigger` (agent launch after resolution)
- Storage: `.current-work/cycles/`, `.current-work/session-bindings/`

### Domain Rules

- The factory never selects or switches a workstream without human confirmation.
- The factory raises the same apparent boundary only once unless the objective changes again.
- Clarifications, supporting research, and implementation detail stay in the current workstream. Only a distinct objective justifies a suggestion.
- A session binding is navigation state, not delivery evidence. Losing it must never lose delivery work.
- Session binding paths use the existing usage-capture filesystem-key encoding.
- `run-step` resumes from observable repository state. It runs one invocation at a time and never retries blindly.

### Size

3 stories.

### Building-Block Inventory

| Story   | Goal                                                                                                                                             | Tier     | Size | Basis                                                                                                                                   |
| ------- | ------------------------------------------------------------------------------------------------------------------------------------------------ | -------- | ---- | --------------------------------------------------------------------------------------------------------------------------------------- |
| ST-0255 | Option C lists every workstream with its topic and cycle, binds the chosen one to the session, and presents its recommendations.                 | standard | M    | Extends the option B adapter work from ST-0254. The empty-list path and the digest record are the two additional behaviors.             |
| ST-0256 | The factory suggests a separate workstream on a detected objective change, acts only on confirmation, and does not repeat a declined suggestion. | standard | M    | Detection criteria are named in the gaps report and need pinning down during grilling. Declined-suggestion memory is new session state. |
| ST-0257 | `run-step` names the next agent from the workstream file and the delivery model, and re-derives it after an interruption.                        | standard | M    | Rewrites a 64-line skill. Small surface, but it changes the resume contract every playbook consumer depends on.                         |

## EPIC 3: Keep concurrent sessions from overwriting newer workstream state

### Why this EPIC exists

Once several workstreams exist and several sessions can reach them, two sessions can write the same file. The loser's change disappears silently, and a delegated run can continue against state that no longer exists. The quality strategy classifies every contract in this area as critical. This EPIC makes a losing write visible and harmless instead of silent and destructive.

### Actor Goals

- State adapter replaces a workstream file atomically, incrementing the revision and refreshing the session binding
- State adapter refuses a write from a session holding a stale revision or a mismatched digest, and changes nothing
- State adapter serializes two sessions on one workstream while leaving different workstreams independent
- Delegated execution pauses and returns control to the human when it meets a conflict

### Demo

1. Bind session A and session B to the same workstream at revision 5.
2. Write from session A. The state file reaches revision 6 and session A's binding is updated to match.
3. Write from session B, still expecting revision 5. The command returns `stale_workstream_state` with the expected and current revisions, and writes nothing.
4. Confirm the file still holds session A's change.
5. Edit the state file by hand without touching the revision. The next read detects a digest mismatch and the next write returns a conflict.
6. Hold the lock in session A and attempt a write from session B. After five seconds session B returns `workstream_busy` and writes nothing.
7. Write to two different workstreams at the same time. Both succeed.
8. Interrupt a write between the temporary file and the replacement. The state file holds either the complete previous content or the complete new content, never a fragment.

### Scope

**In:**

- Optimistic concurrency check — compare the session binding's observed revision and SHA-256 digest against the file on disk before any write, and return a conflict result carrying both revisions when they disagree
- Digest computation over the exact state-file bytes, so a hand edit that skips the revision is still detected
- Atomic replacement — write a temporary sibling file, flush it, and replace the state file in one operation
- Revision increment — exactly one increment per accepted mutation, followed by a session binding update
- Exclusive lock per workstream at `.current-work/cycles/.locks/<workstream-id>.lock`, covering only read, compare, validate, and replace
- Lock wait of at most five seconds, returning `workstream_busy` without writing when it expires
- Rejected-write handling — leave the rejected session's binding untouched so a later refresh, not a silent retry, reconciles it
- Delegated-execution conflict — pause the run and return control to the human

**Out:**

- Merging concurrent changes or retrying a rejected mutation. The engine does neither by design.
- Locking read-only assessment. Atomic replacement already exposes one complete file or the other.
- Cross-repository or networked coordination.

### Dependencies

EPIC 1 — the state file and session binding formats must exist.

### Boundaries

- Actor touchpoint A: a command-line session writing a workstream
- Actor touchpoint B: a second concurrent session writing the same workstream
- Adapter: `packages/factory/scripts/cycle` and the engine's state module
- Storage: `.current-work/cycles/`, `.current-work/cycles/.locks/`, `.current-work/session-bindings/`

### Domain Rules

- A stale session never overwrites newer workstream state.
- Every mutation uses the session binding's observed revision and digest as its expected state.
- An accepted mutation increments the revision exactly once.
- The lock holds no workflow data and is released by the operating system when the process exits.
- A rejected write leaves the state file byte-identical and the rejected binding unchanged.
- Sessions writing different workstreams never block each other.
- A refresh updates the observation. It never repeats the rejected mutation.

### Size

2 stories.

### Building-Block Inventory

| Story   | Goal                                                                                                                                                           | Tier   | Size | Basis                                                                                                                                                              |
| ------- | -------------------------------------------------------------------------------------------------------------------------------------------------------------- | ------ | ---- | ------------------------------------------------------------------------------------------------------------------------------------------------------------------ |
| ST-0258 | An accepted write replaces the state file atomically and increments the revision; a stale revision or mismatched digest returns a conflict and writes nothing. | strong | L    | Every contract here is classified critical. Interrupted-replacement and digest-mismatch behavior need careful test construction rather than large amounts of code. |
| ST-0259 | Two sessions on one workstream serialize through a per-workstream lock that times out to `workstream_busy`, while different workstreams stay independent.      | strong | M    | Concurrency tests must race real processes. The lock itself is small; proving the timeout and independence is the work.                                            |

## EPIC 4: Retry a cycle under delegated and human authority

### Why this EPIC exists

An unattended run that fails can repeat forever, spending tokens against an obstacle it cannot clear. A retry limit stops that loop. The limit must not become a wall for the human, who may have context the engine does not and needs no permission to try again. This EPIC separates the two cases so an automated caller stops and a person does not.

### Actor Goals

- Cycle engine allows a delegated retry below the declared limit and pauses at it, changing nothing
- Human operator retries at or above the limit with a warning and no override ceremony
- Cycle engine resets the attempt count when the cycle changes or the selected work changes
- State adapter refuses to count a retry when the recorded state is malformed

### Demo

1. Enter REALIZE, which declares an attempt limit of 5, and reach attempt 2.
2. Request a delegated retry. The result is `allowed` and the attempt becomes 3.
3. Reach attempt 5 and request another delegated retry. The result is `paused` with reason `delegated_attempt_limit_reached`, carrying the cycle, attempt, limit, and a next action of `request_human_direction`. The state file is untouched.
4. Request a human retry at attempt 5. The result is `allowed_with_warning` and the attempt becomes 6. Nothing asks for a justification.
5. From REFINE at attempt 4, select REALIZE. The attempt resets to 1.
6. At REALIZE with attempt 3, add a second story to the work list without changing the cycle. The attempt resets to 1.
7. Corrupt the attempt field and request a retry. The result is `invalid_state` and the file is unchanged.
8. Accept a retry to attempt 4, then let the cycle execution fail. The attempt stays 4.

### Scope

**In:**

- Per-cycle `delegated_attempt_limit` declarations in the delivery model
- Retry decision logic returning exactly one of `allowed`, `paused`, `allowed_with_warning`, or `invalid_state`
- Caller classification — the adapter identifies a retry request as human-authored or delegated and passes that to the engine
- Attempt reset on a cycle change and on a change to the selected work list, including when the cycle stays the same
- Non-reset cases — changing sessions, resuming a workstream, reassessing artifacts, and editing files leave the attempt alone
- Consumed-attempt semantics — once accepted, the increment stands through every later outcome, including a failure to start
- `factory/scripts/cycle retry` adapter with its exit codes and printed result

**Out:**

- Following a delegation grant across transitions (EPIC 5)
- Retry history. The state file keeps only the current attempt; usage and execution records supply history.

### Dependencies

EPIC 1 — the delivery model, state file, and adapter must exist.

### Boundaries

- Adapter: `packages/factory/scripts/cycle retry`
- Engine: retry decision module
- Storage: `packages/factory/engine/models/delivery.yaml` (limits), `.current-work/cycles/` (attempt)

### Domain Rules

- Retry limits stop unattended loops. They never stop a human.
- A human retry at or above the limit requires no override flag and no justification.
- A paused delegated retry changes no state.
- Entering a cycle, or changing the work list, sets the attempt to 1.
- An accepted attempt is consumed. The adapter never rolls it back.
- Malformed retry state is reported, not repaired.

### Size

2 stories.

### Building-Block Inventory

| Story   | Goal                                                                                                                         | Tier     | Size | Basis                                                                                                                                    |
| ------- | ---------------------------------------------------------------------------------------------------------------------------- | -------- | ---- | ---------------------------------------------------------------------------------------------------------------------------------------- |
| ST-0260 | The engine returns `allowed`, `paused`, `allowed_with_warning`, or `invalid_state` for a retry, and applies the reset rules. | strong   | M    | Three contracts here are classified critical, notably consumed-attempt semantics. The logic is compact; the state transitions are exact. |
| ST-0261 | `cycle retry` distinguishes a human caller from a delegated one and reports the limit result with a distinct exit code.      | standard | M    | Adapter work over ST-0260. Caller classification is the one design question needing resolution before implementation.                    |

## EPIC 5: Delegate a bounded route and let it run unattended

### Why this EPIC exists

Confirming every transition by hand removes the benefit of knowing where the work is going. A user who has already decided the next three cycles should be able to record that decision once. The risk is an engine that expands its own authority. This EPIC grants exactly the authority the human wrote down, and no more.

### Actor Goals

- Human operator records an ordered route and the engine follows it, showing evidence and warnings at each transition
- Human operator records a destination and the engine continues only while the evidence is unambiguous
- Cycle engine pauses for human direction when a grant runs out, reaches its destination, or meets an ambiguous choice
- Cycle engine and its agents are refused when they attempt to create, extend, or broaden a grant

### Demo

1. Record the grant `route: [CONCEPT, REFINE, REALIZE]` on a workstream entering CONCEPT.
2. Complete CONCEPT. The engine advances to REFINE and prints the recommendation evidence and warnings for that transition.
3. Force the REFINE route's evidence to fail and run again. The engine still proceeds to REFINE, with the failed evidence visible, because the human recorded that choice.
4. Complete the last cycle in the grant. The engine pauses for human direction rather than choosing a fourth cycle.
5. Replace the grant with `through: REALIZE` from CONCEPT, arranged so exactly one downstream route has passing evidence. The engine continues to that route on its own.
6. Arrange for no route to have passing evidence, then for two routes to have it. The engine pauses in both cases.
7. Reach REALIZE under the destination grant. The engine pauses at the named destination.
8. Have an agent attempt to add a cycle to the grant. The attempt is refused.
9. Cause a technical execution failure mid-run. The engine stops and does not advance to the next grant entry.

### Scope

**In:**

- Grant representation in the workstream file — exactly one of an ordered `route` list or a single `through` destination, and never both
- Ordered route following — take the next entry, show its evidence and warnings, and proceed even when the evidence failed
- Destination grant evaluation — continue only while exactly one route has passing evidence, and pause on zero, on several, and at the destination
- Exhaustion handling — pause for human direction when the ordered route runs out
- Grant immutability — reject any attempt by the engine or an agent to create, extend, replace, or broaden a grant
- Technical failure handling — stop the run and do not advance
- Conflict handling during a delegated run — pause and return control to the human
- `run-step` integration so a delegated transition dispatches the resolved agent

**Out:**

- Inferring a grant from behavior or history. The first release never creates a grant on its own.
- Ranking routes to break a tie under a destination grant. Ambiguity pauses.

### Dependencies

EPIC 1 — recommendations and cycle selection. EPIC 4 — an unattended run needs the retry limit to bound it.

### Boundaries

- Engine: delegation evaluation module
- Adapter: `packages/factory/scripts/cycle`
- Skill: `packages/factory/skills/run-step/SKILL.md`
- Dispatcher: `packages/factory/scripts/trigger` and the spawned agent sessions
- Storage: `.current-work/cycles/` (the grant)

### Domain Rules

- Only the human creates, replaces, or revokes a grant. The engine and its agents never widen their own authority.
- A grant holds exactly one form: an ordered route or a destination.
- Failed evidence does not invalidate a choice the human already recorded.
- A destination grant continues only while exactly one route has supporting evidence.
- A technical execution failure always stops the run.
- Delegated execution may continue without the human present. The grant supplies the authority; presence does not.

### Size

3 stories.

### Building-Block Inventory

| Story   | Goal                                                                                                                            | Tier     | Size | Basis                                                                                                                |
| ------- | ------------------------------------------------------------------------------------------------------------------------------- | -------- | ---- | -------------------------------------------------------------------------------------------------------------------- |
| ST-0262 | The engine follows an ordered route grant, showing evidence at each transition, and pauses when the route is exhausted.         | standard | M    | Decision logic over the grant and the recommendation result. The proceed-on-failed-evidence rule is the subtle part. |
| ST-0263 | A destination grant continues on exactly one supported route and pauses on zero routes, several routes, and at the destination. | standard | M    | Reuses the cardinality result from ST-0253. Four pause conditions, each separately testable.                         |
| ST-0264 | An attempt by the engine or an agent to create, extend, or broaden a grant is refused, and a technical failure stops the run.   | standard | S    | Classified critical but small. Needs a clear seam between human-authored and engine-originated grant writes.         |

## EPIC 6: See complete artifact evidence behind every recommendation

### Why this EPIC exists

EPIC 1 assesses one artifact so a route can be recommended at all. Real routing decisions rest on thirteen artifact types, and a recommendation built on a partial view is worse than none, because it looks authoritative. This EPIC completes the evidence table and adds the assessment that catches documentation drifting away from the code it describes.

### Actor Goals

- Cycle engine evaluates every artifact type named in the readiness table through a trusted validator returning one shared result shape
- Cycle engine runs mechanical validation unconditionally for referenced artifacts
- Transition recommender runs a semantic assessment when the cycle changed code or a canonical artifact, and reports it as not applicable otherwise

### Demo

1. Prepare a repository where the scope map and architecture model pass their checks and no entity model exists.
2. Run the assessment at cycle exit.
3. Read the per-artifact results: each names the artifact type, the artifact reference, the assessed commit, the individual checks, and any warnings.
4. Confirm the missing entity model appears as a warning and that the routes depending on it are reported as unsupported, while other routes keep their support.
5. Commit a change to a source file and run the assessment again. The semantic assessment runs and its result informs the recommendation.
6. Commit a change to `docs/spec/scope-map.md` and run again. The semantic assessment runs.
7. Commit a change to an unrelated file and run again. The result reports that the semantic assessment does not apply.

### Scope

**In:**

- Trusted validator registry — map each validator identifier named in the delivery model to its implementation, and reject a model naming an identifier that is not registered
- Shared validator result shape — artifact type, artifact reference, assessed commit, individual checks, warnings
- Mechanical validators for the remaining artifact types in the readiness table: scope map, entity model, architecture model, feature specifications, gaps report, architecture decision records, concept reviews, epic plan, selected stories, realization result, research brief, and research report
- Reuse of the existing check commands where one already covers an artifact, rather than a second implementation
- Change detection at cycle exit — decide whether the cycle produced commits touching source files or a canonical artifact
- Semantic assessment invocation on that condition, and an explicit not-applicable result otherwise
- Collection rules — a fixed path identifies a canonical artifact, an authoritative artifact lists the required members of a collection, and the workstream file lists selected runtime work; a file glob may find candidates but never defines a complete collection

**Out:**

- Ranking routes by semantic strength. Deferred by the proposal.
- Changing what the existing check commands assert. EPIC 10 owns their preserved contracts.
- The entity model's own definition and tooling (EPIC 7). This EPIC only assesses the artifact.

### Dependencies

EPIC 1 — the validator interface, the delivery model, and the recommendation path must exist.

### Boundaries

- Engine: readiness evaluation and recommendation modules
- Validator: the existing check commands under `packages/factory/scripts/`
- Repository artifacts: `docs/spec/`, `docs/arc42/`, `docs/adr/`, `docs/proposals/`, `backlog/`
- Version control: commit range inspection for change detection

### Domain Rules

- Neither validation layer authorizes a transition. Both only supply evidence.
- Mechanical validation runs unconditionally for referenced artifacts.
- Semantic assessment runs only when the cycle changed source code or a canonical artifact.
- Every validator returns the same result fields, so the engine treats them uniformly.
- The delivery model names validators by identifier. An unregistered identifier is a model error, not a runtime warning.
- A file glob never defines a complete collection.
- Reconciliation supplies recommendations when an artifact no longer describes the work. It never controls the human's selection.

### Size

3 stories.

### Building-Block Inventory

| Story   | Goal                                                                                                                                    | Tier     | Size | Basis                                                                                                                                 |
| ------- | --------------------------------------------------------------------------------------------------------------------------------------- | -------- | ---- | ------------------------------------------------------------------------------------------------------------------------------------- |
| ST-0265 | The engine resolves every validator identifier in the delivery model through a registry and rejects an unregistered name.               | standard | M    | Extends the single-validator seam from ST-0252. The registry and the shared result shape are the deliverable.                         |
| ST-0266 | Every artifact type in the readiness table has a mechanical validator returning per-check results and warnings.                         | standard | L    | Twelve validators. Most wrap an existing check command, so the work is breadth rather than depth. A candidate for slicing in Phase 7. |
| ST-0267 | The recommender runs the semantic assessment when the cycle changed code or a canonical artifact, and reports not applicable otherwise. | standard | M    | Change detection over a commit range plus the invocation seam. The three conditions are explicitly specified.                         |

## EPIC 7: Define domain entities once and generate every other representation

### Why this EPIC exists

The factory has no machine-readable model of its own domain entities. Entity information is scattered across prose, and nothing detects the moment two documents start disagreeing. The cycle model needs a canonical answer to "what do these things mean" that a validator can check. This EPIC establishes one source file and makes every other representation a product of it.

### Actor Goals

- Entity modeler defines domain entities, value objects, slots, relationships, identities, and invariants in one canonical file
- Entity modeler generates validation code and reader-facing projections from that file, with neither adding information of its own
- Developer sees an invalid payload rejected before it reaches storage

### Demo

1. Read `docs/spec/entity-model.yaml` and confirm it defines the factory's entities, their relationships, and their invariants.
2. Run the readiness checks. The file passes metamodel validation, the model linter reports no errors, every referenced class and slot resolves, every payload-backed slot points at a defined inline class, and every stored value-object class declares a schema-version slot.
3. Regenerate `docs/spec/entity-model.md` and `docs/assets/images/entity-model.svg`. Both match the current source.
4. Add a class to the generated Markdown by hand and re-run the projection check. It reports that the projection carries information absent from the source.
5. Generate the validation models and submit a payload that breaks a declared invariant. Validation raises an error before the payload reaches storage.
6. Store and retrieve a valid value object. No field and no schema-version information is lost.

### Scope

**In:**

- `docs/spec/entity-model.yaml` — the canonical model expressed in LinkML, covering entities, value objects, slots, relationships, identities, and invariants
- Readiness checks — metamodel validation, the model linter, class and slot resolution, inline-class references for payload-backed slots, and a schema-version slot on every stored value-object class
- Generated validation models owning payload shape and application invariants
- Derived projections — a Markdown rendering and a diagram, both generated from the current source
- Projection fidelity check — detect a projection carrying information the source does not have
- Versioning policy for stored payloads — declare whether the application reads an older version, migrates it, or rejects it with a named error
- Persistence integration test covering serialization and retrieval fidelity

**Out:**

- Database-level payload validation. The database owns column type, nullability, and storage constraints; it does not re-validate the payload.
- Migrating existing prose entity descriptions into the model beyond what the cycle feature needs.
- The domain vocabulary in `docs/CONTEXT.md`, which names and defines terms rather than modeling them.

### Dependencies

None. This EPIC starts alongside EPIC 1.

### Boundaries

- Specification source: `docs/spec/entity-model.yaml`
- Validation and generation tooling: model linter, metamodel validation, and the code generator
- Generated runtime code: validation models
- Derived documentation: `docs/spec/entity-model.md`, `docs/assets/images/entity-model.svg`

### Domain Rules

- The LinkML file is the single source of truth for the entity model.
- No derived projection introduces model information absent from the source.
- Every stored payload value object carries a schema-version discriminator.
- Generated models own payload shape and application invariants. The database owns column type, nullability, and storage constraints.
- A payload-backed slot references its value-object class and declares inline containment.
- The entity model is distinct from the domain vocabulary. One models structure; the other defines terms.

### Size

2 stories.

### Building-Block Inventory

| Story   | Goal                                                                                                               | Tier     | Size | Basis                                                                                                                               |
| ------- | ------------------------------------------------------------------------------------------------------------------ | -------- | ---- | ----------------------------------------------------------------------------------------------------------------------------------- |
| ST-0268 | `docs/spec/entity-model.yaml` defines the factory's entities and passes every readiness check.                     | standard | L    | A new modeling language and toolchain for this repository. Authoring the model is the bulk; the checks are mostly tool invocations. |
| ST-0269 | Validation models and reader-facing projections are generated from the source, and neither adds information to it. | standard | M    | Generator wiring plus the fidelity check. The versioning policy for stored payloads needs a decision before implementation.         |

## EPIC 8: Bootstrap an inherited repository into a reviewed concept baseline

### Why this EPIC exists

Every cycle after IDEA reads the canonical concept artifacts, and an inherited repository has none of them. Without a defined way in, a brownfield user faces a delivery graph that can recommend nothing. This EPIC gives that user a first cycle whose output is the baseline everything else assesses — and keeps it a recommendation, not a gate, so a user who knows better is not blocked.

### Actor Goals

- Brownfield operator turns existing code, tests, persistence schemas, and infrastructure definitions into the three canonical concept artifacts
- Brownfield operator receives a recommendation to proceed to feature delivery when that baseline is complete and reviewed
- Brownfield operator continues to another cycle on an incomplete baseline, seeing what is missing and performing no override ceremony

### Demo

1. Take an inherited repository that has been fitted but never onboarded.
2. Run the brownfield concept bootstrap.
3. Confirm `docs/arc42/architecture.dsl`, `docs/spec/scope-map.md`, and `docs/spec/entity-model.yaml` all exist.
4. Run the bootstrap assessment with all three present, passing their checks, and carrying no unresolved major finding. The assessment recommends proceeding to feature delivery.
5. Delete `docs/spec/entity-model.yaml` and select a cycle other than CONCEPT.
6. The factory names the missing evidence and continues. It asks for no override flag and no justification.

### Scope

**In:**

- Brownfield entry definition — after fitting, a brownfield repository enters a CONCEPT bootstrap, and an accepted proposal is not required for it
- Bootstrap procedure updates so its mandatory first stage produces all three canonical artifacts, including the entity model
- Entity relationship diagram promoted into that mandatory first stage
- Bootstrap assessment — recommend feature delivery when the three artifacts exist, pass their checks, and carry no unresolved major finding
- Incomplete-baseline reporting — name the missing evidence and continue without ceremony when the human selects another cycle
- Exit contract — the bootstrap leaves a delivery-ready repository. It creates no epic plan and does not enter REALIZE. New work then starts at IDEA with a proposal.

**Out:**

- The deeper reverse-engineering stage of brownfield onboarding, which stays optional
- Fitting itself, which is a prerequisite outside the delivery graph
- The entity model's tooling (EPIC 7). This EPIC consumes it.

### Dependencies

EPIC 7 — the entity model must be definable. EPIC 6 — the assessment needs the artifact validators.

### Boundaries

- Procedure: `packages/factory/playbooks/brownfield-onboarding.md`
- Canonical artifacts: `docs/arc42/architecture.dsl`, `docs/spec/scope-map.md`, `docs/spec/entity-model.yaml`
- Engine: bootstrap assessment and route recommendation
- Adapter: `packages/factory/scripts/cycle`

### Domain Rules

- Fitting configures the factory for a repository. It is a prerequisite, not a cycle.
- Brownfield entry reconstructs the canonical concept model from code, tests, persistence schemas, and infrastructure definitions.
- The factory recommends completing all three canonical artifacts before feature delivery. It does not require them.
- A human may continue on incomplete evidence, and the factory says what is missing without demanding an override.
- When artifacts disagree, the canonical concept model is authoritative.
- The bootstrap exits to a delivery-ready state. It does not produce a roadmap or enter realization.

### Size

2 stories.

### Building-Block Inventory

| Story   | Goal                                                                                                                        | Tier     | Size | Basis                                                                                                                               |
| ------- | --------------------------------------------------------------------------------------------------------------------------- | -------- | ---- | ----------------------------------------------------------------------------------------------------------------------------------- |
| ST-0270 | The brownfield bootstrap produces the architecture model, scope map, and entity model in its mandatory first stage.         | standard | L    | Rewrites an existing playbook and adds the entity model and diagram to its required output. Mostly procedure, verified by fixtures. |
| ST-0271 | The bootstrap assessment recommends feature delivery on a complete baseline and names missing evidence without an override. | standard | S    | Small assessment over ST-0266's validators. The no-ceremony rule is the contract worth testing.                                     |

## EPIC 9: Send a delivery question to research and bring the answer back

### Why this EPIC exists

A concept cycle regularly uncovers a question that delivery cannot answer from the repository. Today that question either stalls the work or is answered informally and forgotten. Research already has working procedures, but nothing connects a research result back to the cycle that needed it. This EPIC adds that connection without disturbing how research works.

### Actor Goals

- Research user opens a brief from a delivery cycle that records where the question came from and which decision it must inform
- Research user opens a standalone brief with no delivery link
- Human operator resumes the declared delivery cycle once the report passes validation, with the report reference available

### Demo

1. Work a delivery cycle at CONCEPT and identify a question the repository cannot answer.
2. Create a research brief from that cycle.
3. Read the brief and confirm it records the originating cycle, the originating artifact reference, the cycle that will consume the result, and the decision that result must inform.
4. Create a second brief with research as the primary goal and no active delivery cycle. It carries none of those four fields.
5. Complete the research and pass the report through validation.
6. The delivery graph resumes at the declared cycle, with the report reference available there.

### Scope

**In:**

- Four optional delivery-link fields on the research brief schema: originating cycle, originating artifact reference, returning cycle, and the decision needed
- Schema rules making the four fields present together on a linked brief and absent together on a standalone brief
- Brief creation from an active delivery cycle, populating the fields from the workstream
- Return path — on report validation, resume the workstream at the declared returning cycle with the report reference available as evidence
- Readiness validators for the brief and the report, feeding the evidence table

**Out:**

- Replacing the internal survey and falsification routes. They stay unchanged in this release.
- Research role-separation rules, which stay as they are.
- A research cycle inside the delivery graph. Research is a sibling graph.

### Dependencies

EPIC 1 — the workstream, cycle selection, and validator interface must exist.

### Boundaries

- Schema: `packages/factory/rulebooks/schemas/research-brief.schema.json`
- Template: `packages/factory/rulebooks/templates/research-brief.md`
- Procedures: the research survey and falsification playbooks
- Engine and adapter: resumption at the declared returning cycle

### Domain Rules

- Research is a sibling graph, never a sixth delivery cycle.
- A linked brief carries all four delivery-link fields. A standalone brief carries none.
- Linked research returns its report reference to the declared returning cycle.
- A validated report completes standalone research with no return path.
- The existing survey and falsification routes and their role separation stay unchanged.

### Size

2 stories.

### Building-Block Inventory

| Story   | Goal                                                                                                              | Tier     | Size | Basis                                                                                              |
| ------- | ----------------------------------------------------------------------------------------------------------------- | -------- | ---- | -------------------------------------------------------------------------------------------------- |
| ST-0272 | A brief created from a delivery cycle carries the four delivery-link fields, and a standalone brief carries none. | standard | M    | Schema change plus creation-path wiring. The all-or-nothing rule is the contract to prove.         |
| ST-0273 | A validated report resumes the workstream at the declared returning cycle with the report reference available.    | standard | M    | Connects report validation to cycle selection. Needs the brief and report validators from ST-0266. |

## EPIC 10: Move the whole factory off phase routing without losing any command

### Why this EPIC exists

The cycle machinery is useless while the rest of the factory still routes through phases. A cutover that quietly drops a command or renames an agent breaks users who depend on it and leaves no trace of what happened. This EPIC performs the switch and proves, mechanically, that everything the acceptance commit promised is still there.

### Actor Goals

- Agent maintainer replaces phase ordinals in agent definitions with cycle eligibility, keeping every agent and skill name
- transition-lint validates the cycle model and workstream files, reporting failed route evidence as warnings that still exit zero
- Human operator running a retired phase command is told which command replaced it
- Compatibility verifier confirms that the kept contracts and the installed engine still behave as promised

### Demo

01. Run `factory/scripts/phase advance`. It exits 2 and names `factory/scripts/cycle select` as the replacement. It does not emulate the old behavior.
02. Run `factory/scripts/phase retry`. It exits 2 and names `factory/scripts/cycle retry`.
03. Run `transition-lint` against a valid delivery model and a valid workstream file. It exits 0.
04. Remove a cycle node from the model and run again. It reports the structural error and exits non-zero.
05. Corrupt the schema version in a workstream file and run again. It reports the schema error and exits non-zero.
06. Arrange for a recommended transition's evidence to fail and run again. It prints warnings and exits 0.
07. Open an agent definition and confirm it lists the cycles where the agent is eligible and carries no phase ordinal.
08. Run the catalog check and confirm every agent and skill name from the acceptance commit still resolves.
09. Run the characterization suite over the ten standard check commands and the two branch-safety commands. Each keeps its name, triggers, result format, and exit behavior.
10. Run the installed-shape check. The installed delivery model is schema-valid and identical to the tracked source.

### Scope

**In:**

- `phase` reduced to a diagnostic stub exiting 2 and naming its replacement, retained for one release
- `transition-lint` migrated from phase-order enforcement to cycle model and workstream file validation, with failed route evidence reported as warnings at exit zero
- Agent frontmatter migration — remove `phase` and `phase-name` from the sixteen agent definitions and add cycle eligibility tags
- Catalog regeneration and a name-preservation check against the acceptance commit
- Characterization tests for the ten standard check commands and the two branch-safety commands
- Installed-shape test proving the installed factory loads the same schema-valid model as the tracked source
- Dependency boundary test enforcing that the engine imports no script, configuration, agent definition, skill, or the orchestrator package
- Epic plan naming — adopt `backlog/epics-<feature-name>.md` as the documented convention
- Playbook files retained as reference documentation with their runtime authority removed
- Minimum language version raised to Python 3.10 for the cycle commands

**Out:**

- Deleting playbook files. The proposal defers removal.
- Changing what the kept check commands assert. This EPIC proves they are unchanged.
- Removing the `phase` stub, which happens one release later.

### Dependencies

EPIC 1 — the cycle commands must exist before `phase` can point at them. EPIC 2 — `run-step` must read cycle state before the playbook marker loses authority.

### Boundaries

- Commands: `packages/factory/scripts/phase`, `packages/factory/scripts/transition-lint`
- Agent definitions: `packages/factory/agents/*.md`
- Catalog: `packages/factory/INDEX.yaml` and `index-lint`
- Distribution: the installed `factory/` copy

### Domain Rules

- Every agent and skill name indexed at the acceptance commit still exists after the migration.
- The ten standard check commands and the two branch-safety commands keep their name, triggers, result format, and exit behavior.
- The `phase` stub names its replacement and never emulates the old single-forward transition.
- transition-lint treats a structural error as a failure and failed route evidence as a warning.
- The engine never imports scripts, configuration, agent definitions, skills, or the orchestrator package. Those may call the engine.
- The tracked source under `packages/factory/` is the default test surface. The installed copy must match it.
- Unlisted orchestration behavior is not retained through a general compatibility promise.

### Size

4 stories.

### Building-Block Inventory

| Story   | Goal                                                                                                                                           | Tier     | Size | Basis                                                                                                                       |
| ------- | ---------------------------------------------------------------------------------------------------------------------------------------------- | -------- | ---- | --------------------------------------------------------------------------------------------------------------------------- |
| ST-0274 | `transition-lint` validates the delivery model and workstream files, failing on structural errors and warning at exit zero on failed evidence. | standard | M    | Rewrites a 389-line script against a new domain model. The warning-at-zero rule inverts its current behavior.               |
| ST-0275 | `phase advance` and `phase retry` exit 2 and name their replacement commands.                                                                  | economy  | S    | Replaces a 627-line script with a stub. Small and mechanical once the replacements exist.                                   |
| ST-0276 | Agent definitions carry cycle eligibility instead of phase ordinals, and every indexed name survives.                                          | standard | M    | Sixteen files plus catalog regeneration. Deciding each agent's eligible cycles is the judgment; the edit itself is routine. |
| ST-0277 | Characterization, installed-shape, and dependency-boundary checks prove the kept contracts and the engine boundary.                            | standard | M    | Test-only story. Breadth across twelve commands plus two structural checks. No production code changes.                     |

## EPIC 11: Attribute token usage to a workstream and a cycle

### Why this EPIC exists

The factory records what it spends but cannot say what it spent it on. Comparing a direct route to realization against a route through roadmap and refinement is exactly the question the cycle model raises, and today the data cannot answer it. The risk in answering it badly is worse than silence: a cumulative session total assigned to whichever workstream happened to be last would look precise and be wrong.

### Actor Goals

- Usage system records the workstream, its origin, and the cycle on every captured record when a binding exists
- Usage system captures records with those fields null when no binding exists, and never fails because of it
- Usage analyst groups usage by workstream, by cycle, and by both, and is told plainly when attribution is unavailable

### Demo

1. Bind a session to a workstream at CONCEPT and capture a usage record. It carries the workstream identifier, the workstream origin, and the cycle.
2. Remove the binding and capture another record. All three fields are null and capture succeeds.
3. Dispatch a child agent from a session bound at REALIZE. The child's records carry the same workstream identifier and its own dispatch cycle.
4. Query usage grouped by workstream. Records from two workstreams group separately.
5. Query usage grouped by cycle. Records group under IDEA, CONCEPT, and REALIZE.
6. Query usage grouped by workstream where some records have null fields. Those records are reported as unavailable, and no cumulative session total is assigned to the last active workstream.

### Scope

**In:**

- Three optional fields on the version 1 usage record contract: workstream identifier, workstream origin, and cycle, with a compatibility manifest update
- Capture adapter population — read the fields from the session binding when it exists, and write nulls when it does not
- Capture resilience — missing cycle context never fails capture
- Child-agent inheritance — a dispatched agent's records carry the parent's workstream and the agent's dispatch cycle
- Analysis dimensions — workstream, cycle, and workstream-by-cycle in the dimensional usage view
- Attribution rules — attribute per-invocation usage directly; attribute cumulative usage by subtracting snapshots at workstream boundaries; report unavailable when neither method applies
- Honest reporting — never assign a complete cumulative session to the workstream active at session end

**Out:**

- Reconstructing attribution for records captured before these fields existed
- Changing the accounting conservation rules for the four supported command-line tools
- Making analysis depend on retained working files. It reads immutable records only.

### Dependencies

EPIC 1 — session bindings must exist before the capture adapter can read them.

### Boundaries

- Storage: `packages/factory/contracts/usage-record/v1.schema.json` and its compatibility manifest
- Capture: `packages/factory/scripts/usage-capture` and the capture hooks
- Session state: `.current-work/session-bindings/`
- Analysis: `packages/usage/src/usage/views/`

### Domain Rules

- The orchestration adapter supplies the workstream fields. Usage capture never imports or queries the cycle engine.
- Missing cycle context leaves all three fields null and never fails capture.
- Child agents inherit the parent's workstream and their own dispatch cycle.
- Analysis never assigns a complete cumulative session to the workstream active at session end.
- Context carried from an earlier topic counts toward the workstream active for the current invocation.
- Analysis reads immutable usage records and never depends on retained working files.
- Unavailable attribution is reported as unavailable, never estimated.

### Size

2 stories.

### Building-Block Inventory

| Story   | Goal                                                                                                                      | Tier     | Size | Basis                                                                                                                  |
| ------- | ------------------------------------------------------------------------------------------------------------------------- | -------- | ---- | ---------------------------------------------------------------------------------------------------------------------- |
| ST-0278 | Captured usage records carry the workstream, its origin, and the cycle when a binding exists, and nulls when it does not. | standard | M    | Contract change plus capture adapter work across four command-line integrations. Child inheritance is the subtle path. |
| ST-0279 | Usage analysis groups by workstream and cycle and reports unattributable records as unavailable.                          | standard | M    | Extends the existing dimensional view. The honest-reporting rule is the contract that matters most.                    |
