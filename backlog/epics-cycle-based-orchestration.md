# Cycle-Based Orchestration EPICs

This plan implements the approved seven-EPIC decomposition for
[cycle-based orchestration](../docs/spec/cycle-based-orchestration.feature).
The architecture follows
[ADR-0017](../docs/adr/0017-cycle-based-orchestration-supersedes-linear-playbook-fsm.md).
Capacity tiers follow the
[dispatch tier rubric](../factory/rulebooks/conventions/dispatch-contract.md#tier-rubric).

Actor goals link directly to durable feature rules. The EPICs do not depend on
the phase-1 capability table.

Story slicing is complete. Each EPIC carries a confirmed Story Slices table
that maps actor-visible capabilities to candidate stories. EPIC 1 stories are
written and partially implemented. EPICs 2–7 await story file creation.

## Epic 1 — Start, Continue, and Execute a Workstream

### Why this EPIC exists

The current menu starts playbooks or agents without durable workstream identity.
Users need one place to start work, reopen it, assess evidence, and run the next
eligible agent.

### Actor Goals

- A human operator [starts a named workstream](../docs/spec/cycle-based-orchestration.feature)
  from menu option B.
- A human operator [continues an existing workstream](../docs/spec/cycle-based-orchestration.feature)
  from menu option C.
- An agent maintainer [assigns cycle eligibility](../docs/spec/cycle-based-orchestration.feature)
  without changing indexed identities.
- A human operator [runs the next eligible step](../docs/spec/cycle-based-orchestration.feature)
  from workstream state.

### Current State and Required Behavior

The Cycle Engine (`packages/factory/engine/`) exists with five modules:
`cycle_model.py` (model loader), `cycles.py` (canonical names),
`eligibility.py` (dispatch eligibility), `readiness.py` (readiness evaluator),
and `recommendations.py` (route recommender). The State Adapter
(`packages/factory/scripts/cycle`) supports `select`, `assess`, and `list`
subcommands. JSON Schemas (`cycle-model-v1`, `cycle-state-v1`) and the proposal
validator are shipped. Agent definitions carry `eligible_cycles`. Session
bindings and workstream state files work. Menu option B creates workstreams.

Remaining: menu option C (continue), reconciliation trigger (code-change
detection), and `run-step` rewrite from cycle state.

### Demo

1. Assign `planning-agent` to CONCEPT and regenerate the catalog.
2. Start a workstream named `Atlas` from menu option B.
3. Reopen `Atlas` from menu option C and view its recommendations.
4. Invoke `run-step` and observe `planning-agent` start from current evidence.

### Scope

**In**

- Make menu option B create and bind a named IDEA workstream.
- Make menu option C list, select, and bind existing workstreams.
- Validate the delivery model before assessing route evidence.
- Present zero, one, or several supported routes without automatic ranking.
- Run reconciliation after code or canonical artifacts change.
- Replace agent phase ordinals with cycle eligibility.
- Resolve `run-step` from workstream state and repository evidence.
- Keep indexed agent and skill identities from the acceptance commit.

**Out**

- Selecting or retrying a cycle through the `cycle` command.
- Delegating route decisions without a human present.
- Migrating the separate research graph to delivery cycles.

### Dependencies

None. This EPIC can begin from the current codebase.

### Boundaries

- Session menu → Workstream Resolver → Cycle State Files and Session Bindings.
- Session menu → Readiness Evaluator and Route Recommender → recommendations.
- Agent definition and `index-lint` → Dispatch Eligibility → Catalog.
- `run-step` → Dispatch Eligibility → Trigger and invoked-agent output.

### Size

Five stories and 7–12 engineering days. Two done (ST-0252, ST-0253), three
pending (ST-0254, ST-0255, ST-0256).

### Story Slices

| #   | Capability                                                    | Actor          | Story                 | Status  |
| --- | ------------------------------------------------------------- | -------------- | --------------------- | ------- |
| 1   | Start a workstream and select any cycle                       | Human operator | [ST-0252](ST-0252.md) | done    |
| 2   | See route recommendations and select a cycle                  | Human operator | [ST-0253](ST-0253.md) | done    |
| 3   | Continue a workstream and see recommendations                 | Human operator | [ST-0254](ST-0254.md) | pending |
| 4   | Detect code changes and run reconciliation assessment         | Human operator | [ST-0255](ST-0255.md) | pending |
| 5   | Resolve run-step from workstream state with cycle eligibility | Human operator | [ST-0256](ST-0256.md) | pending |

### Domain Rules

- A new workstream starts in IDEA with revision 1 and attempt 1.
- A session binding records the observed revision and SHA-256 digest.
- Menu option C never selects a workstream automatically.
- Mechanical readiness checks always run for referenced artifacts.
- Semantic assessment runs only after relevant changes.
- Supported-route cardinality yields none, one, or several unranked choices.
- Humans retain routing authority regardless of recommendation evidence.
- Acceptance-commit agent and skill names remain available.
- `run-step` never reads the legacy playbook marker.

### Building-Block Inventory

| Block                                | Tier     | Estimate | Goal                                                                        | Existing state                                                           | Adds or changes                                                     |
| ------------------------------------ | -------- | -------- | --------------------------------------------------------------------------- | ------------------------------------------------------------------------ | ------------------------------------------------------------------- |
| Start and reopen workstreams         | strong   | 2–4 days | Let an operator start `Atlas`, reopen it, and see its current cycle.        | Option B creates workstreams (ST-0252 done). Option C pending (ST-0254). | Listing, binding on reopen, and menu results for option C remain.   |
| Assess evidence and recommend routes | strong   | 3–5 days | Show which routes current repository evidence supports.                     | Readiness evaluator and route recommender shipped (ST-0253 done).        | Code-change detection for reconciliation trigger remains (ST-0255). |
| Assign and run eligible agents       | standard | 2–3 days | Let a maintainer assign eligibility and an operator run the eligible agent. | Agent defs carry `eligible_cycles`; eligibility module shipped.          | `run-step` rewrite from cycle state remains (ST-0256).              |

### Testability Assessment

All actor goals produce observable, assertable outcomes. Tests can inspect menu
output, workstream and binding files, model validation results, the generated
catalog, trigger output, and `run-step` behavior. The acceptance-commit
identifier is pinned when the feature branch is cut from `dev`;
`dispatch init --baseline-commit` records the full 40-character SHA in the
dispatch ledger. Characterization tests read the pinned SHA to snapshot the
pre-migration index and command contracts.

### Ownership Resolution

| Contract                                            | `.feature` Rule                                                                                                                                                                                  | Owner                                | Rationale                                |
| --------------------------------------------------- | ------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------ | ------------------------------------ | ---------------------------------------- |
| Start a new workstream                              | [Human operator starts a new workstream](../docs/spec/cycle-based-orchestration.feature#rule-human-operator-starts-a-new-workstream)                                                             | Start and reopen workstreams         | Introduces creation and session binding. |
| Continue an existing workstream                     | [Human operator continues an existing workstream](../docs/spec/cycle-based-orchestration.feature#rule-human-operator-continues-an-existing-workstream)                                           | Start and reopen workstreams         | Introduces listing and reopening.        |
| Load and validate the delivery model                | [Engine loads and validates the delivery model](../docs/spec/cycle-based-orchestration.feature#rule-engine-loads-and-validates-the-delivery-model)                                               | Assess evidence and recommend routes | Introduces the validated routing model.  |
| Evaluate artifact readiness                         | [Engine evaluates artifact readiness for route recommendations](../docs/spec/cycle-based-orchestration.feature#rule-engine-evaluates-artifact-readiness-for-route-recommendations)               | Assess evidence and recommend routes | Introduces structured readiness results. |
| Recommend routes from evidence                      | [Engine recommends routes based on artifact evidence](../docs/spec/cycle-based-orchestration.feature#rule-engine-recommends-routes-based-on-artifact-evidence)                                   | Assess evidence and recommend routes | Introduces recommendation cardinality.   |
| Reconcile changed code and canonical artifacts      | [Reconciliation runs when a cycle changes code or canonical artifacts](../docs/spec/cycle-based-orchestration.feature#rule-reconciliation-runs-when-a-cycle-changes-code-or-canonical-artifacts) | Assess evidence and recommend routes | First exercises reconciliation at exit.  |
| Replace agent phase ordinals with cycle eligibility | [Agent definitions carry cycle eligibility instead of phase ordinals](../docs/spec/cycle-based-orchestration.feature#rule-agent-definitions-carry-cycle-eligibility-instead-of-phase-ordinals)   | Assign and run eligible agents       | Introduces eligibility metadata.         |
| Execute cycle steps from observable state           | [`run-step` executes cycle steps instead of playbook steps](../docs/spec/cycle-based-orchestration.feature#rule-run-step-executes-cycle-steps-instead-of-playbook-steps)                         | Assign and run eligible agents       | Introduces cycle-based step resolution.  |

## Epic 2 — Select, Retry, and Check a Cycle

### Why this EPIC exists

Recommendations do not change workstream state. Operators need explicit
commands to select or retry a cycle and check the resulting state safely.

### Actor Goals

- A human operator [selects any cycle](../docs/spec/cycle-based-orchestration.feature)
  and sees evidence warnings.
- A human operator [retries the current cycle](../docs/spec/cycle-based-orchestration.feature)
  and sees the attempt result.
- A project maintainer [checks cycle models and workstream states](../docs/spec/cycle-based-orchestration.feature).

### Current State and Required Behavior

`packages/factory/scripts/cycle` exists with `select`, `assess`, and `list`
subcommands (EPIC 1). `cycle select` writes state without OS-level locking —
concurrent sessions can silently overwrite each other. No `cycle retry`
subcommand exists. `packages/factory/scripts/phase` and
`packages/factory/scripts/transition-lint` still use legacy flow control.

`cycle select` must acquire an OS-level lock, validate revision and digest, and
write state atomically through temp-file replacement. A stale revision, digest
mismatch, or five-second lock timeout must return a named conflict without
changing either file.

`cycle retry --state STATE` must distinguish human and delegated requests. An
accepted retry consumes its attempt before execution starts. A later execution
failure must not restore the previous attempt. Human retries may exceed the
delegated limit with a warning.

The migrated `transition-lint` must reject invalid delivery models and malformed
workstream states. Failed route evidence must remain a warning at exit zero.
The old `phase` command must exit 2 and name the matching replacement command.

### Demo

1. Select REALIZE for `Atlas` despite a failed recommendation.
2. Observe the warning and attempt 1.
3. Retry REALIZE and observe attempt 2.
4. Run `transition-lint` and observe warnings with exit code zero.

### Scope

**In**

- Add `cycle select` for human-authored cycle and work-list changes.
- Add `cycle retry` for human and delegated retries.
- Apply delegated attempt limits without limiting human retries.
- Write state and bindings atomically under per-workstream locks.
- Detect stale revisions, digest mismatches, timeouts, and interrupted writes.
- Make `transition-lint` validate cycle models and workstream states.
- Replace `phase` behavior with one-release diagnostic guidance.
- Characterize preserved command and branch-safety contracts.

**Out**

- Creating or managing delegation grants.
- Requiring override flags or justification for human choices.
- Keeping legacy phase commands as transition authorities.

### Dependencies

- [Epic 1](#epic-1--start-continue-and-execute-a-workstream) supplies the
  delivery model and workstream state.

### Boundaries

- `cycle select` or `cycle retry` → Route Recommender or Retry Evaluator → State
  Adapter, state files, bindings, and output.
- `transition-lint` → Cycle Model Loader and Readiness Evaluator → diagnostics.

### Size

Three stories and 7–12 engineering days.

### Story Slices

| #   | Capability                                                       | Actor              | Trigger                    | Observable outcome                                                                                                                                                              |
| --- | ---------------------------------------------------------------- | ------------------ | -------------------------- | ------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| 1   | Select a cycle with atomic state writes and conflict detection   | Human operator     | `cycle select`             | Lock acquired; revision and digest validated; atomic write; stale revision returns `conflict`; lock timeout returns `workstream_busy`; different workstreams lock independently |
| 2   | Retry a cycle with delegated attempt limits                      | Human operator     | `cycle retry` (new)        | Below limit: attempt increments; at limit: `paused`; human retry above limit: warning; work-list change resets attempt; failure after accepted retry keeps increment            |
| 3   | Check cycle models and workstream states for migration integrity | Project maintainer | `transition-lint`; `phase` | `transition-lint` validates model and state files; `phase` exits 2 naming replacement; characterization tests confirm kept contracts                                            |

### Domain Rules

- A human may select any cycle without an override ceremony.
- A new cycle or changed work list resets attempt to 1.
- A delegated retry at its limit pauses without changing state.
- A human retry above the limit proceeds with a warning.
- An accepted retry keeps its increment after later failure.
- Each mutation increments revision and updates the digest.
- Stale state returns a conflict without writing.
- Different workstreams use separate locks.
- A lock timeout returns `workstream_busy` after five seconds.
- Invalid structures make `transition-lint` fail.
- Failed recommendation evidence remains a warning at exit zero.
- The diagnostic `phase` command exits 2 and names its replacement.

### Building-Block Inventory

| Block                     | Tier     | Estimate | Goal                                                                          | Existing state                                         | Adds or changes                                                                          |
| ------------------------- | -------- | -------- | ----------------------------------------------------------------------------- | ------------------------------------------------------ | ---------------------------------------------------------------------------------------- |
| Select a cycle safely     | strong   | 3–5 days | Let an operator select any cycle and see its result with warnings.            | `cycle select` exists without locking (EPIC 1).        | Adds OS-level locking, atomic replacement, revision validation, and conflict detection.  |
| Retry a cycle safely      | strong   | 2–4 days | Let an operator retry and see whether work continued or paused.               | `phase retry` counts review iterations.                | Adds `cycle retry` subcommand, retry decisions, limits, warnings, and consumed attempts. |
| Check migration integrity | standard | 2–3 days | Let a maintainer check cycle state while existing contracts remain available. | Lint and phase commands still use legacy flow control. | Migrates linting to cycle model, adds the phase stub, and characterizes interfaces.      |

### Testability Assessment

All actor goals produce observable, assertable outcomes. Tests can inspect
command exit codes, diagnostic output, state and binding files, revisions,
digests, lock results, and preserved command contracts. No testability red flag
remains in this EPIC.

### Ownership Resolution

| Contract                                          | `.feature` Rule                                                                                                                                                      | Owner                     | Rationale                                       |
| ------------------------------------------------- | -------------------------------------------------------------------------------------------------------------------------------------------------------------------- | ------------------------- | ----------------------------------------------- |
| Select the next cycle                             | [Human operator selects the next cycle](../docs/spec/cycle-based-orchestration.feature#rule-human-operator-selects-the-next-cycle)                                   | Select a cycle safely     | Introduces human cycle selection.               |
| Enforce delegated retry limits                    | [Engine enforces delegated retry limits](../docs/spec/cycle-based-orchestration.feature#rule-engine-enforces-delegated-retry-limits)                                 | Retry a cycle safely      | Introduces retry decisions and attempt changes. |
| Transition workstream state atomically            | [Adapter transitions workstream state atomically](../docs/spec/cycle-based-orchestration.feature#rule-adapter-transitions-workstream-state-atomically)               | Select a cycle safely     | Introduces state mutation and binding updates.  |
| Handle concurrent workstream access               | [Adapter handles concurrent workstream access](../docs/spec/cycle-based-orchestration.feature#rule-adapter-handles-concurrent-workstream-access)                     | Select a cycle safely     | Introduces locking and conflict handling.       |
| Retire the phase command with diagnostic guidance | [phase command exits as a diagnostic stub](../docs/spec/cycle-based-orchestration.feature#rule-phase-command-exits-as-a-diagnostic-stub)                             | Check migration integrity | Introduces the diagnostic stub.                 |
| Validate cycle models and state files             | [transition-lint validates cycle models and state files](../docs/spec/cycle-based-orchestration.feature#rule-transition-lint-validates-cycle-models-and-state-files) | Check migration integrity | Introduces migrated integrity checks.           |
| Keep acceptance-commit contracts                  | [Kept contracts preserve acceptance-commit behavior](../docs/spec/cycle-based-orchestration.feature#rule-kept-contracts-preserve-acceptance-commit-behavior)         | Check migration integrity | First verifies compatibility after migration.   |

## Epic 3 — Switch Workstreams During a Session

### Why this EPIC exists

One session may encounter work for another objective. A confirmed switch must
keep state and usage attribution attached to the correct workstream.

Objective-change detection uses only mechanical signals defined below.

### Actor Goals

- A human operator [confirms or declines a workstream switch](../docs/spec/cycle-based-orchestration.feature).

### Current State and Required Behavior

The current session model has no workstream binding and cannot switch between
objectives. Usage capture records sessions and agents without a workstream
boundary.

The Factory detects an objective change through exactly these mechanical
signals:

1. The user names a different workstream explicitly (e.g. "let's work on
   Borealis").
2. The user references a proposal file (`docs/proposals/*.md`) not associated
   with the current workstream's work list.
3. The user invokes `cycle select` or menu option B/C targeting a different
   workstream.

Conversational semantics are not a detection signal. If no mechanical signal
fires, the Factory does not suggest a switch. The user can always switch
manually.

On detection, the Factory must suggest one specific target action: create a
workstream or reopen a named workstream. A declined suggestion must be
remembered for that objective during the session. A confirmed switch must
capture the old usage boundary before updating the binding. The user must
then see the active target name.

### Demo

1. Work in `Atlas` until a defined objective change occurs.
2. Confirm the suggested switch to `Borealis`.
3. Observe `Borealis` reported as active.
4. Decline the same suggestion and observe no repeated prompt.

### Scope

**In**

- Detect an objective change using stakeholder-approved criteria.
- Ask before creating or reopening another workstream.
- Record a supported usage boundary before rebinding.
- Update the binding atomically after confirmation.
- Suppress a declined suggestion for the same objective.

**Out**

- Switching without human confirmation.
- Inferring a workstream from arbitrary wording.
- Reassigning historical usage without boundary evidence.

### Dependencies

- [Epic 1](#epic-1--start-continue-and-execute-a-workstream) supplies bindings.

### Boundaries

In-session suggestion → Workstream Resolver and Usage Capture → Session
Bindings, Raw Usage Spool, and visible confirmation.

### Size

One story and 4–7 engineering days. The original estimate of two stories
separated detection from safe switching. Story slicing merged them: the two
building blocks serve one actor through one interaction — detection is the entry
point, the switch is the outcome. Splitting fails the serial-layer-chain gate.

### Story Slices

| #   | Capability                                         | Actor          | Trigger                                                                                                                     | Observable outcome                                                                                                                                                                   |
| --- | -------------------------------------------------- | -------------- | --------------------------------------------------------------------------------------------------------------------------- | ------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------ |
| 1   | Confirm or decline a workstream switch mid-session | Human operator | Mechanical signal: explicit workstream name, unrelated proposal reference, or menu/command targeting a different workstream | Suggestion to create or reopen target; confirmed switch captures usage boundary, updates binding atomically; declined suggestion suppressed for that objective; new target displayed |

### Domain Rules

- The Factory never switches without human confirmation.
- A confirmed switch captures a boundary before rebinding.
- A declined suggestion is not repeated for the same objective.
- A stale-state conflict returns control to the human.

### Building-Block Inventory

| Block                                    | Tier   | Estimate | Goal                                                                                                | Existing state                                                                    | Adds or changes                                                                                         |
| ---------------------------------------- | ------ | -------- | --------------------------------------------------------------------------------------------------- | --------------------------------------------------------------------------------- | ------------------------------------------------------------------------------------------------------- |
| Suggest and execute a mid-session switch | strong | 4–7 days | Let an operator accept or decline a switch and continue under the target without mixing boundaries. | Session bindings exist (EPIC 1). No detection, prompt, suppression, or switching. | Adds detection criteria, suggestion, confirmation, suppression, boundary capture, and locked rebinding. |

### Testability Assessment

All actor goals produce observable, assertable outcomes. Tests can inspect the
binding update, usage boundary file, suppression record, and visible target
through session output and stored files. Objective-change detection fires on
three mechanical signals (explicit workstream name, unrelated proposal
reference, menu or command targeting a different workstream). Tests can
supply each signal and assert that the suggestion appears, and verify that
no suggestion fires without a signal. No testability red flag remains in
this EPIC.

### Ownership Resolution

| Contract                              | `.feature` Rule                                                                                                                                        | Owner                                    | Rationale                                |
| ------------------------------------- | ------------------------------------------------------------------------------------------------------------------------------------------------------ | ---------------------------------------- | ---------------------------------------- |
| Switch workstreams during one session | [Human operator switches workstreams mid-session](../docs/spec/cycle-based-orchestration.feature#rule-human-operator-switches-workstreams-mid-session) | Suggest and execute a mid-session switch | First introduces the switching contract. |

## Epic 4 — Delegate Bounded Cycle Routing

### Why this EPIC exists

Users can decide some routes before unattended work begins. Delegation must
follow recorded human authority and pause at each defined boundary.

Grant management uses the `cycle grant` CLI command defined in the
[interface contracts](../docs/spec/supplementary_specs/interface-contracts.md#factoryscriptscycle-grant).

### Actor Goals

- A human operator [delegates an ordered route](../docs/spec/cycle-based-orchestration.feature).
- A human operator [delegates through a destination](../docs/spec/cycle-based-orchestration.feature).

### Current State and Required Behavior

The delivery specification defines route and destination grant data, but no
command contract manages grants. No engine currently follows a grant or returns
a structured pause reason.

The `cycle grant` command is the sole entry point for creating, replacing,
revoking, and inspecting a grant. The session menu lists it under workstream
management when a workstream is bound; the menu never suggests it
contextually. Each successful change passes through the same locked state
adapter as cycle selection. Agents and engine code cannot create, extend, or
broaden a grant.

An ordered grant must follow every recorded choice, even when recommendation
evidence fails. A destination grant must continue only while exactly one route
has support. Both forms must return control on technical failure, conflict,
retry limit, exhaustion, or destination arrival. The terminal result must name
the pause reason and next human action.

### Demo

1. Record `[CONCEPT, REFINE, REALIZE]` through the approved interface.
2. Observe execution pause after REALIZE completes.
3. Replace the grant with `through REALIZE`.
4. Observe ambiguous evidence pause and return control.

### Scope

**In**

- Create, replace, revoke, and resume one human-authored grant.
- Store exactly one grant form: ordered route or destination.
- Follow ordered choices despite failed recommendation evidence.
- Continue toward a destination only while one route has support.
- Show evidence and warnings at every delegated transition.
- Pause on exhaustion, arrival, ambiguity, failure, retry limit, or conflict.
- Reject attempts by engines or agents to broaden authority.

**Out**

- Inferring, creating, extending, or broadening grants automatically.
- Ranking several supported routes.
- Continuing after technical failure.

### Dependencies

- [Epic 2](#epic-2--select-retry-and-check-a-cycle) supplies mutation and
  conflict handling.

### Boundaries

Grant interface → Delegation Evaluator, Route Recommender, and Retry Evaluator
→ State Adapter, Cycle State Files, and execution output.

### Size

Two stories and 6–10 engineering days. The original estimate of three stories
separated grant management from both delegation forms. Story slicing merged
grant management into the first delegation story: grant CRUD (create, show,
revoke, replace) is shared infrastructure, not a standalone actor capability.

### Story Slices

| #   | Capability                           | Actor          | Trigger                     | Observable outcome                                                                                                                                                                                                                                     |
| --- | ------------------------------------ | -------------- | --------------------------- | ------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------ |
| 1   | Delegate an ordered route sequence   | Human operator | `cycle grant route` (new)   | Grant recorded; engine follows recorded choices regardless of evidence; warnings at each transition; pauses on exhaustion, failure, conflict, or retry limit; `cycle grant show` and `cycle grant revoke` work; agents cannot create or broaden grants |
| 2   | Delegate through a named destination | Human operator | `cycle grant through` (new) | Grant recorded; engine continues while exactly one route has evidence; pauses on zero evidence, multiple routes, arrival, failure, or conflict                                                                                                         |

### Domain Rules

- Only a human creates, replaces, revokes, or broadens a grant.
- An ordered route records explicit human choices.
- Failed evidence does not invalidate an ordered choice.
- A destination grant continues only with one supported route.
- Zero or several supported routes pause destination delegation.
- Grants pause at their destination or after their entries finish.
- Technical failure always stops delegated execution.

### Building-Block Inventory

| Block                          | Tier   | Estimate | Goal                                                                                                   | Existing state                                                          | Adds or changes                                                                                          |
| ------------------------------ | ------ | -------- | ------------------------------------------------------------------------------------------------------ | ----------------------------------------------------------------------- | -------------------------------------------------------------------------------------------------------- |
| Follow an ordered route        | strong | 3–5 days | Let an operator record a route, see it followed, and manage the grant through the approved interface.  | State Adapter and engine exist (EPIC 1). No grants or delegation.       | Adds `cycle grant` subcommand (route, show, revoke), Delegation Evaluator, ordered progress, and pauses. |
| Continue through a destination | strong | 3–5 days | Let an operator record a destination and see the engine continue while one route has evidence support. | Grant management and Delegation Evaluator from the ordered-route story. | Adds destination grant form, evidence-based routing, ambiguity pauses, and arrival pauses.               |

### Testability Assessment

All actor goals produce observable, assertable outcomes. Tests invoke
`cycle grant route|through|revoke|show` and inspect grant state, transition
output, pause reasons, and workstream state files. The `cycle grant` command
provides a concrete test interface for creating, replacing, revoking, and
inspecting grants. No testability red flag remains in this EPIC.

### Ownership Resolution

| Contract                               | `.feature` Rule                                                                                                                                      | Owner                          | Rationale                                     |
| -------------------------------------- | ---------------------------------------------------------------------------------------------------------------------------------------------------- | ------------------------------ | --------------------------------------------- |
| Follow a human-authored route sequence | [Human operator delegates a route sequence](../docs/spec/cycle-based-orchestration.feature#rule-human-operator-delegates-a-route-sequence)           | Follow an ordered route        | First completes ordered delegated execution.  |
| Continue through a named destination   | [Human operator delegates through a destination](../docs/spec/cycle-based-orchestration.feature#rule-human-operator-delegates-through-a-destination) | Continue through a destination | First completes destination-based delegation. |

## Epic 5 — Analyse Usage by Workstream and Cycle

### Why this EPIC exists

Usage cannot be evaluated by workstream when records omit that context.
Analysts need attributable totals without inventing ownership for unbound
records.

### Actor Goals

- A usage analyst [groups usage by workstream and cycle](../docs/spec/cycle-based-orchestration.feature).

### Current State and Required Behavior

The versioned usage record and `usage-query` command already exist. The record
contract lacks `workstream_id`, `workstream_origin`, and `cycle` fields.
`usage_by_dimension.py` supports time, project, command-line interface,
provider, model, agent, branch, and exit status only.

Usage capture must read the session binding when one exists and append the
three optional fields. Unbound sessions must emit explicit nulls without
failing. Child agents must inherit the workstream and the cycle active at
dispatch time.

`usage-query --view usage_by_dimension --dimensions workstream,cycle` must
group attributable records without reading `.current-work`. Records without a
reliable boundary must appear as unavailable. The query must never assign a
whole cumulative session total to the last active workstream.

### Demo

1. Produce usage in `Atlas` at CONCEPT and `Borealis` at IDEA.
2. Query the workstream and cycle dimensions.
3. Observe separate totals for both workstreams and cycles.
4. Observe unavailable attribution for unbound records.

### Scope

**In**

- Add optional workstream, origin, and cycle fields to usage records.
- Read bound context without failing unbound capture.
- Pass parent workstream and dispatch cycle to child records.
- Expose workstream and cycle as query dimensions.
- Report unavailable attribution without assigning cumulative usage elsewhere.

**Out**

- Reading `.current-work` during analysis.
- Retrospectively assigning unbound records.
- Adding remote collection, dashboards, or persistent databases.

### Dependencies

- [Epic 1](#epic-1--start-continue-and-execute-a-workstream) supplies identity
  and session bindings.

### Boundaries

- CLI sessions → Usage Capture and Usage Record Contract → Raw Usage Spool.
- `usage-query` → Query Model v1 and Result Adapters → terminal results.

### Size

Two stories and 4–7 engineering days.

### Story Slices

| #   | Capability                                      | Actor                           | Trigger                                                   | Observable outcome                                                                                                                                |
| --- | ----------------------------------------------- | ------------------------------- | --------------------------------------------------------- | ------------------------------------------------------------------------------------------------------------------------------------------------- |
| 1   | Capture usage with workstream and cycle context | Usage system (session operator) | Session start with bound workstream; child agent dispatch | Records contain `workstream_id`, `workstream_origin`, `cycle` when bound; null when unbound; child agents inherit; capture succeeds in both cases |
| 2   | Query usage totals by workstream and cycle      | Usage analyst                   | `usage-query --dimensions workstream,cycle`               | Results grouped by workstream and cycle; unavailable attribution for unbound records; no false assignment of cumulative totals                    |

### Domain Rules

- Bound records carry workstream ID, origin, and cycle.
- Unbound records carry null values and capture still succeeds.
- Child records inherit the workstream and dispatch cycle.
- Queries group by workstream, cycle, or both.
- Missing attribution is reported as unavailable.
- Analysis never assigns cumulative usage to the last workstream.

### Building-Block Inventory

| Block                      | Tier   | Estimate | Goal                                                               | Existing state                                   | Adds or changes                                                  |
| -------------------------- | ------ | -------- | ------------------------------------------------------------------ | ------------------------------------------------ | ---------------------------------------------------------------- |
| Capture attributable usage | strong | 2–4 days | Give analysts records with available workstream and cycle context. | Capture and its contract lack workstream fields. | Extends the contract, capture, child context, and null handling. |
| Query attributable totals  | strong | 2–3 days | Group totals by workstream and cycle without false attribution.    | The query supports other dimensions.             | Extends relations, views, adapters, and unavailable output.      |

### Testability Assessment

All actor goals produce observable, assertable outcomes. Tests can inspect
versioned usage records, inherited child context, query rows, command output,
and unavailable-attribution values. No testability red flag remains in this
EPIC.

### Ownership Resolution

| Contract                                   | `.feature` Rule                                                                                                                                                          | Owner                      | Rationale                              |
| ------------------------------------------ | ------------------------------------------------------------------------------------------------------------------------------------------------------------------------ | -------------------------- | -------------------------------------- |
| Capture workstream and cycle usage context | [Usage records carry workstream and cycle context](../docs/spec/cycle-based-orchestration.feature#rule-usage-records-carry-workstream-and-cycle-context)                 | Capture attributable usage | Introduces attributable record fields. |
| Query by workstream and cycle dimensions   | [Usage analyst queries by workstream and cycle dimensions](../docs/spec/cycle-based-orchestration.feature#rule-usage-analyst-queries-by-workstream-and-cycle-dimensions) | Query attributable totals  | Introduces both analysis dimensions.   |

## Epic 6 — Bootstrap a Brownfield Concept Model

### Why this EPIC exists

Brownfield delivery needs a shared description of behavior, structure, and
domain data. The current bootstrap omits a canonical machine-readable entity
model.

### Actor Goals

- A brownfield operator [creates and checks three canonical concept objects](../docs/spec/cycle-based-orchestration.feature).

### Current State and Required Behavior

`packages/factory/playbooks/brownfield-onboarding.md` currently produces
`docs/arc42/architecture.dsl` and `docs/spec/scope-map.md`. It treats the
handwritten supplementary entity-model document as optional later work. The
repository has no canonical `docs/spec/entity-model.yaml`.

The CONCEPT bootstrap must create a LinkML model beside the scope and
architecture models. Readiness must run LinkML metamodel validation,
`linkml-lint`, reference resolution, inline-class checks, and schema-version
checks. The bootstrap must generate Markdown and Scalable Vector Graphics from
the same source.

Generated Pydantic models must reject invalid value objects before persistence.
At least one persistence integration must store and retrieve a valid generated
object without losing fields or schema-version data. Missing concept evidence
must inform recommendations without preventing a human from choosing a cycle.

### Demo

1. Run the CONCEPT bootstrap on a fitted repository.
2. Observe creation of the scope map, architecture model, and LinkML model.
3. Run readiness checks through the bootstrap.
4. Observe a feature-delivery recommendation.

### Scope

**In**

- Produce all three canonical objects during brownfield bootstrap.
- Treat `docs/spec/entity-model.yaml` as the LinkML source.
- Validate classes, slots, inline value objects, and schema versions.
- Generate faithful Markdown and Scalable Vector Graphics projections.
- Generate Pydantic validation for persisted value objects.
- Check one valid persistence round-trip through SQLAlchemy.
- Report missing evidence without blocking human choice.

**Out**

- Treating generated projections as canonical sources.
- Requiring full reverse engineering before feature work.
- Blocking routing because one object is missing.

### Dependencies

None. This EPIC can proceed independently of cycle runtime work.

### Boundaries

Brownfield CONCEPT bootstrap → Architecture Agent, Reverse Map, and Entity
Modeler → canonical concept files and readiness output.

### Size

Two stories and 5–9 engineering days.

### Story Slices

| #   | Capability                                                                | Actor               | Trigger                                             | Observable outcome                                                                                                                                                                    |
| --- | ------------------------------------------------------------------------- | ------------------- | --------------------------------------------------- | ------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| 1   | Create a validated, documented, persistence-ready entity model            | Entity modeler      | Author `entity-model.yaml` and run readiness checks | LinkML validation and linting pass; classes and slots resolve; Markdown and SVG projections generated; Pydantic rejects invalid payloads; valid objects round-trip through SQLAlchemy |
| 2   | Run the brownfield bootstrap and see all three canonical objects assessed | Brownfield operator | CONCEPT bootstrap                                   | `architecture.dsl`, `scope-map.md`, and `entity-model.yaml` exist; readiness checks run; complete baseline recommends feature delivery; missing evidence reported without blocking    |

### Domain Rules

- The concept model contains scope, entity, and architecture models.
- Every referenced LinkML class and slot resolves.
- JSON-backed slots reference defined inline classes.
- Persisted value objects carry schema versions.
- Generated projections add no model information.
- Invalid generated objects fail before persistence.
- Valid objects round-trip without data loss.
- Missing evidence informs recommendations without blocking choice.

### Building-Block Inventory

| Block                             | Tier     | Estimate | Goal                                                     | Existing state                                           | Adds or changes                                                        |
| --------------------------------- | -------- | -------- | -------------------------------------------------------- | -------------------------------------------------------- | ---------------------------------------------------------------------- |
| Create the canonical LinkML model | strong   | 3–5 days | Validate one source and regenerate faithful projections. | A handwritten model exists without LinkML or generation. | Adds LinkML, linting, projections, Pydantic, and persistence checks.   |
| Complete the brownfield bootstrap | standard | 2–4 days | Create and assess all three canonical objects.           | Onboarding omits `entity-model.yaml`.                    | Integrates modeling, readiness, missing evidence, and recommendations. |

### Testability Assessment

All actor goals produce observable, assertable outcomes. Canonical files,
validator results, generated projections, model validation, and readiness
output are directly inspectable. The persistence round-trip binds to two
integration boundaries: Pydantic validation (generated models reject invalid
payloads before storage) and SQLAlchemy (a valid generated object is stored
and retrieved through an SQLAlchemy session without losing fields or
schema-version data). Test fixtures own an in-memory or temporary SQLite
database. No testability red flag remains in this EPIC.

### Ownership Resolution

| Contract                                  | `.feature` Rule                                                                                                                                                              | Owner                             | Rationale                                       |
| ----------------------------------------- | ---------------------------------------------------------------------------------------------------------------------------------------------------------------------------- | --------------------------------- | ----------------------------------------------- |
| Bootstrap the canonical concept model     | [Brownfield operator bootstraps the canonical concept model](../docs/spec/cycle-based-orchestration.feature#rule-brownfield-operator-bootstraps-the-canonical-concept-model) | Complete the brownfield bootstrap | Introduces the three-object bootstrap.          |
| Use LinkML as the canonical domain source | [LinkML entity model serves as canonical domain source](../docs/spec/cycle-based-orchestration.feature#rule-linkml-entity-model-serves-as-canonical-domain-source)           | Create the canonical LinkML model | Introduces validation, generation, and storage. |

## Epic 7 — Link Research to Delivery Work

### Why this EPIC exists

Delivery may expose a question that requires structured research. The answer
must return to its originating cycle without merging delivery and research
graphs.

### Actor Goals

- A research user [links a brief to delivery and returns a validated report](../docs/spec/cycle-based-orchestration.feature).

### Current State and Required Behavior

Research briefs, schemas, survey routing, falsification routing, and report
validation already exist. Their contracts do not record an originating
delivery cycle, a return cycle, or the decision that needs evidence.

A brief created from delivery work must add `origin_cycle`, `origin_ref`,
`return_cycle`, and `decision_needed`. A standalone research brief must omit
all four fields. Existing survey and falsification routes must otherwise keep
their current behavior.

After report validation succeeds, the delivery workstream must receive the
report reference and resume at the declared return cycle. Validation failure
must leave delivery state unchanged and keep the report unavailable to the
delivery graph.

### Demo

1. Identify an evidence gap while `Atlas` is in CONCEPT.
2. Create a linked brief with return cycle CONCEPT.
3. Complete and validate the report.
4. Observe `Atlas` resume with the report reference.

### Scope

**In**

- Add origin, return-cycle, and decision fields to linked briefs.
- Keep those fields absent from standalone briefs.
- Validate linked fields before research begins.
- Return a validated report reference to delivery.
- Keep current survey and falsification routes.

**Out**

- Replacing the research graph with delivery cycles.
- Returning unvalidated results.
- Choosing a delivery cycle automatically from research results.

### Dependencies

- [Epic 1](#epic-1--start-continue-and-execute-a-workstream) supplies the
  originating workstream and cycle.

### Boundaries

Research brief creation → Research Orchestrator, Schema Validator, and Policy
Validator → validated report, workstream reference, and output.

### Size

Two stories and 4–7 engineering days.

### Story Slices

| #   | Capability                                               | Actor         | Trigger                                  | Observable outcome                                                                                                                                              |
| --- | -------------------------------------------------------- | ------------- | ---------------------------------------- | --------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| 1   | Create a linked research brief from a delivery cycle     | Research user | Create brief while delivery cycle active | Brief includes `origin_cycle`, `origin_ref`, `return_cycle`, `decision_needed`; standalone briefs omit all four; linked fields validated before research begins |
| 2   | Return a validated research report to the delivery cycle | Research user | Report passes validation                 | Delivery workstream resumes at declared return cycle with report reference; validation failure leaves delivery state unchanged                                  |

### Domain Rules

- A linked brief records its origin, return cycle, and required decision.
- A standalone brief omits delivery-link fields.
- Research follows its current survey or falsification route.
- Only a validated report returns to delivery.
- Delivery resumes at the declared return cycle.

### Building-Block Inventory

| Block                     | Tier     | Estimate | Goal                                                              | Existing state                                | Adds or changes                                                  |
| ------------------------- | -------- | -------- | ----------------------------------------------------------------- | --------------------------------------------- | ---------------------------------------------------------------- |
| Create a linked brief     | standard | 2–3 days | Create either a valid linked brief or unchanged standalone brief. | Schemas and routes lack delivery-link fields. | Extends schemas, templates, validation, and creation.            |
| Return validated research | standard | 2–4 days | Return a validated report to the declared cycle.                  | Reports do not update delivery state.         | Adds cycle resolution, references, resumption, and confirmation. |

### Testability Assessment

All actor goals produce observable, assertable outcomes. Tests can inspect
brief fields, validation results, report references, workstream state, and
resume output. No testability red flag remains in this EPIC.

### Ownership Resolution

| Contract                       | `.feature` Rule                                                                                                                                      | Owner                 | Rationale                                   |
| ------------------------------ | ---------------------------------------------------------------------------------------------------------------------------------------------------- | --------------------- | ------------------------------------------- |
| Link research to delivery work | [Delivery cycle creates a linked research brief](../docs/spec/cycle-based-orchestration.feature#rule-delivery-cycle-creates-a-linked-research-brief) | Create a linked brief | First introduces the linked-brief contract. |
