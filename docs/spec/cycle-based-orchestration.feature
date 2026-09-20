# scope: global
Feature: Cycle-Based Orchestration

Replace the linear software-delivery playbook model with a cycle-based
directed graph. Artifact state drives transition recommendations. Humans
drive routing decisions. The system recommends what comes next. The human
selects a cycle or delegates that choice.

Proposal trace: docs/proposals/cycle-based-orchestration.md

Rule: Human operator starts a new workstream
\# actor: Human operator
\# @packages/factory/config/session-menu.md

```
Scenario: Session menu option B creates a named workstream
  Given the session menu is displayed
  When the human selects option B
  And the human provides a topic description
  Then a workstream state file is created at .current-work/cycles/<workstream-id>.yaml
  And the state file records the topic, cycle IDEA, revision 1, and attempt 1
  And a session binding is created for the current session
  And the session enters the IDEA cycle

Scenario: Workstream state file records the proposal origin when one exists
  Given the human provides a topic and names an existing proposal
  When the workstream state file is created
  Then the origin_ref field contains the proposal path
```

Rule: Human operator continues an existing workstream
\# actor: Human operator
\# @packages/factory/config/session-menu.md

```
Scenario: Session menu option C lists current workstreams
  Given at least one workstream state file exists under .current-work/cycles/
  When the human selects option C
  Then each workstream's topic and current cycle is displayed
  And the human selects a workstream from the list

Scenario: Selected workstream binds to the session and shows recommendations
  Given the human selects a workstream from the list
  When the session binding is created
  Then the binding records the workstream revision and SHA-256 digest
  And the factory assesses repository evidence for the current cycle
  And route recommendations are presented

Scenario: No workstreams exist when option C is selected
  Given no workstream state files exist under .current-work/cycles/
  When the human selects option C
  Then the factory offers option B or a return to the menu
  And the factory does not select a workstream automatically
```

Rule: Human operator switches workstreams mid-session
\# actor: Human operator

```
Scenario: Factory suggests a workstream switch on topic change
  Given the session is bound to workstream W1
  When the human begins work on a different objective
  Then the factory suggests creating or reopening a workstream for the new objective
  And the factory does not switch without human confirmation

Scenario: Confirmed switch captures the usage boundary
  Given the human confirms a workstream switch
  And the usage producer supports boundary capture
  When the switch executes
  Then the factory captures the usage boundary for the old workstream
  And the factory creates or reopens the target workstream
  And the session binding is updated to the target workstream

Scenario: Factory suggests the same boundary only once
  Given the factory suggested a workstream switch for objective X
  And the human declined the switch
  When the human continues working on the same objective
  Then the factory does not suggest the same switch again
```

Rule: Engine loads and validates the delivery model
\# actor: Cycle engine

```
Scenario: Valid delivery model loads from tracked source
  Given packages/factory/engine/models/delivery.yaml exists
  When the engine loads the model
  Then the model contains the five delivery cycles IDEA, CONCEPT, ROADMAP, REFINE, and REALIZE
  And the model contains the terminal DONE node
  And every route has from, to, and recommend_if fields
  And no route has a direction or classification field

Scenario: Installed model matches tracked source
  Given factory/engine/models/delivery.yaml is the installed copy
  When the installed-shape test runs
  Then the installed model is schema-valid
  And the installed model is identical to the tracked source under packages/factory/engine/models/
  # @packages/factory/engine/schemas/cycle-model-v1.schema.json

Scenario: Model with unknown artifact reference fails validation
  Given delivery.yaml references an artifact type that is not declared
  When the engine validates the model
  Then validation fails and names the unknown artifact reference

Scenario: Model with executable command in a validator field fails validation
  Given delivery.yaml contains a shell command in a validator field
  When the engine validates the model
  Then validation rejects the executable command

Scenario: Model with direction or classification field on a route fails validation
  Given a route in delivery.yaml contains a direction field
  When the engine validates the model
  Then validation rejects the route
```

Rule: Engine evaluates artifact readiness for route recommendations
\# actor: Cycle engine

```
Scenario: Validator returns a structured result for each artifact
  Given a trusted validator is registered for an artifact type
  When the engine invokes the validator against the current commit
  Then the result contains artifact type, artifact reference, assessed commit, individual checks, and warnings

Scenario: Mechanical validation runs unconditionally for referenced artifacts
  Given the delivery model references a proposal artifact
  When the engine evaluates readiness
  Then mechanical validation checks file existence, format lint, and required fields

Scenario: Semantic assessment runs when the cycle changed code or a canonical artifact
  Given the current cycle produced commits that changed source code files
  When the engine evaluates readiness at cycle exit
  Then semantic assessment compares artifacts against each other and against code

Scenario: Semantic assessment does not run when nothing relevant changed
  Given the current cycle did not change code or a canonical artifact
  When the engine evaluates readiness at cycle exit
  Then only mechanical validation runs
```

Rule: Engine recommends routes based on artifact evidence
\# actor: Cycle engine

```
Scenario: One supported route produces a recommendation
  Given the engine evaluates all declared routes from the current cycle
  And exactly one route has all recommend_if evidence passing
  When the engine produces the recommendation result
  Then the result recommends that single route
  And the result includes the evidence and every other available cycle

Scenario: Zero supported routes produce no recommendation
  Given the engine evaluates all declared routes from the current cycle
  And no route has all recommend_if evidence passing
  When the engine produces the recommendation result
  Then the result reports no evidence-supported recommendation
  And the result shows warnings and every available cycle

Scenario: Multiple supported routes produce choices without ranking
  Given the engine evaluates all declared routes from the current cycle
  And more than one route has all recommend_if evidence passing
  When the engine produces the recommendation result
  Then the result presents the supported routes as choices
  And the engine does not select between them
```

Rule: Human operator selects the next cycle
\# actor: Human operator

```
Scenario: Human selects a recommended route
  Given the engine recommends route from CONCEPT to ROADMAP
  When the human selects ROADMAP
  Then the workstream state file records cycle ROADMAP and attempt 1

Scenario: Human selects a cycle whose evidence failed
  Given the engine recommends route from CONCEPT to ROADMAP
  When the human selects REALIZE instead
  Then the engine records the selection and shows warnings
  And no override flag or justification is required
  And the workstream state file records cycle REALIZE and attempt 1

Scenario: Human selects a cycle absent from the recommendation table
  Given the engine has no declared route from IDEA to REALIZE
  When the human selects REALIZE
  Then the engine records the selection and shows a warning that no declared route exists
  And no override flag or justification is required

Scenario: Selecting a different cycle resets the attempt counter
  Given the workstream is at cycle REFINE with attempt 3
  When the human selects cycle REALIZE
  Then the workstream state file records cycle REALIZE and attempt 1
```

Rule: Human operator delegates a route sequence
\# actor: Human operator

```
Scenario: Explicit route grant follows ordered cycle selections
  Given the human creates a delegation grant with route [CONCEPT, REFINE, REALIZE]
  And the workstream enters CONCEPT
  When the workstream completes CONCEPT
  Then the engine follows the grant and advances to REFINE
  And the engine shows recommendation evidence and warnings at each transition

Scenario: Failed evidence does not invalidate the human's recorded route choice
  Given an explicit route grant specifies REFINE as the next cycle
  And the REFINE route's recommendation evidence fails
  When the engine follows the grant
  Then the engine proceeds to REFINE with the failed evidence visible

Scenario: Engine pauses when the explicit route grant is exhausted
  Given the explicit route grant contains [CONCEPT, REALIZE]
  And the workstream has reached REALIZE and completed it
  When the engine looks for the next grant entry
  Then the engine pauses for human direction

Scenario: Technical execution failure stops delegated execution
  Given the engine is following a delegation grant
  When a technical execution failure occurs during the current cycle
  Then the engine stops the run
  And the engine does not advance to the next grant entry
```

Rule: Human operator delegates through a destination
\# actor: Human operator

```
Scenario: Destination grant continues while exactly one route has evidence
  Given the human creates a delegation grant with through REALIZE
  And the current cycle is CONCEPT
  And exactly one downstream route has all recommend_if evidence passing
  When the engine evaluates the grant
  Then the engine continues to the supported route automatically

Scenario: Destination grant pauses when zero routes have evidence
  Given the human creates a delegation grant with through REALIZE
  And no downstream route has passing evidence
  When the engine evaluates the grant
  Then the engine pauses for human direction

Scenario: Destination grant pauses when multiple routes have evidence
  Given the human creates a delegation grant with through REALIZE
  And both ROADMAP and REFINE routes have passing evidence
  When the engine evaluates the grant
  Then the engine pauses for human direction

Scenario: Destination grant pauses at the named destination
  Given the human creates a delegation grant with through REALIZE
  And the workstream reaches REALIZE
  When the engine evaluates the grant at REALIZE exit
  Then the engine pauses for human direction

Scenario: Only the human creates, replaces, or revokes a grant
  Given a delegation grant exists
  When the engine or an agent attempts to create, extend, or broaden the grant
  Then the attempt is rejected
```

Rule: Engine enforces delegated retry limits
\# actor: Cycle engine

```
Scenario: Delegated retry below the limit is allowed
  Given the workstream is at cycle REALIZE with attempt 2
  And REALIZE declares delegated_attempt_limit 5
  When a delegated retry is requested
  Then the adapter returns allowed
  And attempt increments to 3

Scenario: Delegated retry at the limit pauses without changing state
  Given the workstream is at cycle REALIZE with attempt 5
  And REALIZE declares delegated_attempt_limit 5
  When a delegated retry is requested
  Then the adapter returns status paused with reason delegated_attempt_limit_reached
  And the state file is not modified
  And the result includes cycle, attempt, limit, and next_action request_human_direction

Scenario: Human retry at or above the limit proceeds with a warning
  Given the workstream is at cycle REALIZE with attempt 5
  And REALIZE declares delegated_attempt_limit 5
  When a human-authored retry is requested
  Then the adapter returns allowed_with_warning
  And attempt increments to 6
  And no override flag or justification is required

Scenario: Selecting a different cycle resets attempt to 1
  Given the workstream is at cycle REFINE with attempt 4
  When the human selects cycle REALIZE
  Then the workstream records cycle REALIZE with attempt 1

Scenario: Changing the work list resets attempt to 1
  Given the workstream is at cycle REALIZE with attempt 3
  And the work list is [ST-0001.md]
  When the work list changes to [ST-0001.md, ST-0002.md] while the cycle stays REALIZE
  Then attempt resets to 1

Scenario: Invalid retry state does not increment the attempt
  Given the workstream state file has a malformed attempt field
  When a retry is requested
  Then the adapter returns invalid_state
  And the state file is not modified

Scenario: Failure after an accepted retry retains the increment
  Given a retry is accepted and attempt increments to 4
  When the cycle execution fails after acceptance
  Then attempt remains 4
```

Rule: Adapter transitions workstream state atomically
\# actor: State adapter

```
Scenario: Successful mutation increments revision and updates the digest
  Given the session binding holds revision 7 and digest D1
  And the state file on disk matches revision 7 and digest D1
  When the adapter writes the new state
  Then the adapter writes a temporary sibling file and atomically replaces the state file
  And the new state file has revision 8
  And the session binding is updated with revision 8 and the new digest

Scenario: Stale revision returns a conflict without writing
  Given the session binding holds revision 7
  And the state file on disk has revision 8
  When the adapter attempts to write
  Then the adapter returns status conflict with reason stale_workstream_state
  And the result includes expected_revision 7 and current_revision 8
  And the state file is not modified

Scenario: Direct edit causes a digest mismatch
  Given the session binding holds revision 7 and digest D1
  And the state file was edited directly without incrementing revision
  When the adapter reads the state file
  Then the digest no longer matches D1
  And a subsequent mutation returns a conflict
```

Rule: Adapter handles concurrent workstream access
\# actor: State adapter

```
Scenario: Two sessions mutating the same workstream — one succeeds
  Given session S1 and session S2 both observe workstream W at revision 5
  When S1 acquires the lock and writes revision 6
  And S2 attempts to write with expected revision 5
  Then S2 receives stale_workstream_state without writing
  And W contains S1's changes at revision 6

Scenario: Lock timeout returns workstream_busy
  Given session S1 holds the lock on workstream W
  When session S2 waits for the lock
  And five seconds elapse without acquiring it
  Then S2 receives workstream_busy without writing

Scenario: Different workstreams use separate locks
  Given session S1 mutates workstream W1
  And session S2 mutates workstream W2
  When both sessions write concurrently
  Then both succeed independently

Scenario: Interrupted replacement leaves one complete state file
  Given the adapter is replacing the state file for workstream W
  When the process is interrupted between the temporary write and the atomic replacement
  Then the state file contains either the previous complete content or the new complete content

Scenario: Conflict during delegated execution pauses for human direction
  Given delegated execution is proceeding on workstream W
  When the adapter encounters a stale_workstream_state conflict
  Then delegated execution pauses
  And control returns to the human
```

Rule: Reconciliation runs when a cycle changes code or canonical artifacts
\# actor: Transition recommender

```
Scenario: Reconciliation runs after code changes
  Given the current cycle produced commits that changed source code files
  When the transition recommender evaluates at cycle exit
  Then reconciliation assessment runs
  And its result informs the route recommendation

Scenario: Reconciliation runs after a canonical artifact changes
  Given the current cycle changed docs/spec/scope-map.md
  When the transition recommender evaluates at cycle exit
  Then reconciliation assessment runs

Scenario: Other transitions report reconciliation as not applicable
  Given the current cycle did not change code or any canonical artifact
  When the transition recommender evaluates at cycle exit
  Then the result reports that reconciliation does not apply
```

Rule: Usage records carry workstream and cycle context
\# actor: Usage system
\# @packages/factory/contracts/usage-record/v1.schema.json

```
Scenario: Usage record includes workstream fields when the session is bound
  Given the session is bound to workstream W at cycle CONCEPT
  When a usage record is captured
  Then the record includes workstream_id, workstream_origin, and cycle fields

Scenario: Usage record has null workstream fields when no binding exists
  Given no session binding exists
  When a usage record is captured
  Then workstream_id, workstream_origin, and cycle are all null
  And capture succeeds without error

Scenario: Child agents inherit the workstream and dispatch cycle
  Given the parent session is bound to workstream W at cycle REALIZE
  When a child agent is dispatched
  Then the child agent's usage records carry the same workstream_id and its dispatch cycle
```

Rule: Usage analyst queries by workstream and cycle dimensions
\# actor: Usage analyst
\# @packages/usage/src/usage

```
Scenario: Analysis groups records by workstream
  Given usage records exist for workstreams W1 and W2
  When the analyst queries by workstream dimension
  Then results group records by workstream_id

Scenario: Analysis groups records by cycle
  Given usage records exist with cycle values IDEA, CONCEPT, and REALIZE
  When the analyst queries by cycle dimension
  Then results group records by cycle

Scenario: Unavailable workstream attribution is reported honestly
  Given usage records exist with null workstream fields
  When the analyst queries by workstream dimension
  Then the analysis reports workstream attribution as unavailable for those records
  And the analysis does not assign a full cumulative session total to the last-active workstream
```

Rule: Brownfield operator bootstraps the canonical concept model
\# actor: Brownfield operator
\# @packages/factory/playbooks/brownfield-onboarding.md

```
Scenario: Brownfield bootstrap produces three canonical objects
  Given a fitted brownfield repository with existing code, tests, and persistence schemas
  When the brownfield CONCEPT bootstrap completes
  Then docs/arc42/architecture.dsl exists
  And docs/spec/scope-map.md exists
  And docs/spec/entity-model.yaml exists

Scenario: Complete baseline recommends feature delivery
  Given all three canonical objects exist, pass deterministic validation, and have no unresolved major finding
  When the bootstrap assessment runs
  Then the assessment recommends proceeding to feature delivery

Scenario: Incomplete baseline reports missing evidence without blocking
  Given docs/spec/entity-model.yaml does not exist
  When the human selects a cycle other than CONCEPT
  Then the factory reports the missing evidence
  And the factory continues without requiring an override ceremony
```

Rule: Delivery cycle creates a linked research brief
\# actor: Research user
\# @packages/factory/rulebooks/schemas/research-brief.schema.json

```
Scenario: Linked brief includes delivery-context fields
  Given a delivery cycle at CONCEPT identifies an evidence gap
  When the user creates a research brief from that cycle
  Then the brief includes origin_cycle, origin_ref, return_cycle, and decision_needed fields

Scenario: Standalone brief omits delivery-link fields
  Given research is the user's primary goal with no delivery cycle active
  When the user creates a research brief
  Then the brief omits origin_cycle, origin_ref, return_cycle, and decision_needed

Scenario: Validated research report returns to the delivery cycle
  Given a linked research brief declares return_cycle CONCEPT
  When the research report passes validation
  Then the delivery graph resumes at CONCEPT with the report reference available
```

Rule: Agent definitions carry cycle eligibility instead of phase ordinals
\# actor: Agent maintainer

```
Scenario: Agent frontmatter uses cycle eligibility tags
  Given an agent definition carries phase: 2 and phase-name: Architecture
  When the cycle migration applies
  Then the agent carries cycle eligibility tags listing the cycles where the agent is eligible
  And the phase and phase-name fields are removed

Scenario: Every indexed agent and skill name at the acceptance commit is preserved
  Given the INDEX.yaml lists agent and skill names at the acceptance commit
  When the cycle migration completes
  Then every agent name and skill name from the acceptance commit exists in the post-migration index
```

Rule: run-step executes cycle steps instead of playbook steps
\# actor: run-step skill
\# @packages/factory/skills/run-step/SKILL.md

```
Scenario: run-step resolves the next agent from cycle state
  Given a workstream state file exists with cycle CONCEPT
  When run-step determines the next agent
  Then run-step reads the cycle-state and the recommendation model
  And run-step does not read .current-work/playbook-state.yml

Scenario: run-step resumes from observable state after interruption
  Given a session was interrupted mid-cycle
  When run-step runs in a fresh session
  Then run-step re-derives the next step from the workstream state file and repository evidence
```

Rule: phase command exits as a diagnostic stub
\# actor: phase command
\# @packages/factory/scripts/phase

```
Scenario: phase advance exits 2 and names the replacement
  Given the phase command is invoked with subcommand advance
  When the command runs
  Then it exits with code 2
  And it prints a message naming factory/scripts/cycle select as the replacement

Scenario: phase retry exits 2 and names the replacement
  Given the phase command is invoked with subcommand retry
  When the command runs
  Then it exits with code 2
  And it prints a message naming factory/scripts/cycle retry as the replacement
```

Rule: transition-lint validates cycle models and state files
\# actor: transition-lint
\# @packages/factory/scripts/transition-lint

```
Scenario: Valid cycle model and state file pass
  Given a valid delivery.yaml and a valid workstream state file exist
  When transition-lint runs
  Then it exits with code 0

Scenario: Invalid cycle model fails
  Given delivery.yaml has a missing cycle node
  When transition-lint runs
  Then it reports the structural error and exits non-zero

Scenario: Malformed state file fails
  Given a workstream state file has an invalid schema_version
  When transition-lint runs
  Then it reports the schema error and exits non-zero

Scenario: Failed recommendation evidence produces warnings at exit zero
  Given the workstream state is valid but route evidence for a recommended transition fails
  When transition-lint runs
  Then it reports warnings for the failed evidence
  And it exits with code 0
```

Rule: Kept contracts preserve acceptance-commit behavior
\# actor: Compatibility verifier

```
Scenario: Standard check commands retain their contracts
  Given the acceptance commit defines mdformat, link-check, mermaid-lint, spec-lint, arch-lint, backlog-lint, concern-lint, matrix-lint, statemachine-lint, and index-lint
  When characterization tests run after the cycle migration
  Then every standard check retains its command name, triggers, result format, and exit behavior

Scenario: Branch safety commands retain their contracts
  Given verify-base and premerge-check exist at the acceptance commit
  When characterization tests run after the cycle migration
  Then both commands retain their existing contract

Scenario: Every indexed agent and skill name from the acceptance commit still exists
  Given the INDEX.yaml at the acceptance commit lists agent and skill names
  When the compatibility check runs after migration
  Then every listed name still exists in the post-migration index
```

Rule: LinkML entity model serves as canonical domain source
\# actor: Entity modeler

```
Scenario: Entity model passes mechanical readiness checks
  Given docs/spec/entity-model.yaml exists
  When the readiness checks run
  Then the file passes LinkML metamodel validation
  And linkml-lint reports no errors
  And every referenced class and slot resolves
  And every JSON-backed slot references a defined inline class
  And every persisted JSON value-object class defines a schema-version slot

Scenario: Derived projections contain no independently authored model information
  Given docs/spec/entity-model.yaml is valid
  When the derived projections are generated
  Then docs/spec/entity-model.md and docs/assets/images/entity-model.svg are produced from the current LinkML source
  And neither projection introduces information absent from the source

Scenario: Generated Pydantic model rejects an invalid payload before persistence
  Given a Pydantic model is generated from a LinkML value-object class
  When an invalid payload is submitted
  Then validation raises an error before the payload reaches persistence

Scenario: Persistence integration test round-trips a valid value object
  Given a valid generated value object with a schema-version discriminator
  When the object is stored and retrieved
  Then no fields or schema-version information is lost
```
