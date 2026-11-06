# State Machines — Factory Flow Control

Lifecycles for factory entities. Written per [state-machine-notation.md § Canonical Format](../../.agent-factory/factory/rulebooks/conventions/state-machine-notation.md#canonical-format): pseudocode is authoritative, Mermaid is derived.

## Workstream State Lifecycle

A workstream state file is immutable after creation. There are no state transitions — only creation.

### Pseudocode

```text
State: ABSENT
On CreateWorkstream:
  ChangeState(CREATED)

State: CREATED
On AttemptModification:
  Reject — file is immutable
  ChangeState(CREATED)
  # no outbound transitions
```

### Derived Mermaid

```mermaid
stateDiagram-v2
    [*] --> ABSENT
    ABSENT --> CREATED : CreateWorkstream
    CREATED --> CREATED : AttemptModification (rejected)
```

### Notes

- **ABSENT** means no workstream state file exists for this identifier.
- **CREATED** is the only active state. The file contains `schema_version: 2`, `workstream_id`, `topic`, and `origin_ref`. No other fields exist.
- **AttemptModification** is a self-transition that rejects the write. The state file is never modified after creation. Multiple sessions may bind to the same workstream without modifying its state.

## Session Binding Lifecycle

A session binding is session-scoped state that attaches a session to a workstream. It lives at `.agent-factory/workstreams/sessions/<session-id>.yaml`.

### Pseudocode

```text
State: UNBOUND
On BindToWorkstream:
  ChangeState(BOUND)
On BindToOpenStage:
  ChangeState(OPEN_STAGE)

State: BOUND
On SwitchWorkstream:
  ChangeState(BOUND)
On SwitchToOpenStage:
  ChangeState(OPEN_STAGE)
On SessionEnds:
  ChangeState(INACTIVE)

State: OPEN_STAGE
On BindToWorkstream:
  ChangeState(BOUND)
On SessionEnds:
  ChangeState(INACTIVE)

State: INACTIVE
  # terminal — binding file is no longer active
```

### Derived Mermaid

```mermaid
stateDiagram-v2
    [*] --> UNBOUND
    UNBOUND --> BOUND : BindToWorkstream
    UNBOUND --> OPEN_STAGE : BindToOpenStage
    BOUND --> BOUND : SwitchWorkstream
    BOUND --> OPEN_STAGE : SwitchToOpenStage
    BOUND --> INACTIVE : SessionEnds
    OPEN_STAGE --> BOUND : BindToWorkstream
    OPEN_STAGE --> INACTIVE : SessionEnds
    INACTIVE --> [*]
```

### Notes

- **UNBOUND** exists before the session binding file is written.
- **BOUND** means `workstream_id` contains a known workstream identifier. Switching workstreams updates `workstream_id` and `bound_at` without modifying any workstream state file.
- **OPEN_STAGE** means `workstream_id` is explicitly `null`. Precondition evaluation skips scope filtering.
- **INACTIVE** is terminal. The next session creates a fresh binding.
- The `workstream_id` key must always be present. A missing key fails validation and the binding is never written.

## Concern Registry Lifecycle

The lifecycle of the single `docs/agent-context.md` concern registry. Written per [state-machine-notation.md § Canonical Format](../../.agent-factory/factory/rulebooks/conventions/state-machine-notation.md#canonical-format): pseudocode is authoritative, Mermaid is derived.

### Pseudocode

```text
State: NO_CONTEXT
On CaptureContextInit[user_confirms]:
  ChangeState(CONCERN_REGISTRY)
On CaptureContextInitScan[user_confirms]:
  ChangeState(CONCERN_REGISTRY)
On DetectLegacyYaml:
  ChangeState(MIGRATION_PROPOSED)

State: MIGRATION_PROPOSED
On UserConfirmsMigration:
  ChangeState(CONCERN_REGISTRY)
On UserDeclinesMigration:
  ChangeState(LEGACY_UNCHANGED)

State: CONCERN_REGISTRY
On DirectRegistryEdit:
  ChangeState(CONCERN_REGISTRY)
On ConfirmNewConcern:
  ChangeState(CONCERN_REGISTRY)
On FoldContextMap:
  ChangeState(CONCERN_REGISTRY)
On UpdateScan:
  ChangeState(CONCERN_REGISTRY)

State: LEGACY_UNCHANGED
On DetectLegacyYaml:
  ChangeState(MIGRATION_PROPOSED)
```

### Derived Mermaid

```mermaid
stateDiagram-v2
    [*] --> NO_CONTEXT
    NO_CONTEXT --> CONCERN_REGISTRY : CaptureContextInit (confirm)
    NO_CONTEXT --> CONCERN_REGISTRY : CaptureContextInitScan (confirm)
    NO_CONTEXT --> MIGRATION_PROPOSED : DetectLegacyYaml
    MIGRATION_PROPOSED --> CONCERN_REGISTRY : UserConfirmsMigration
    MIGRATION_PROPOSED --> LEGACY_UNCHANGED : UserDeclinesMigration
    CONCERN_REGISTRY --> CONCERN_REGISTRY : DirectRegistryEdit
    CONCERN_REGISTRY --> CONCERN_REGISTRY : ConfirmNewConcern
    CONCERN_REGISTRY --> CONCERN_REGISTRY : FoldContextMap
    CONCERN_REGISTRY --> CONCERN_REGISTRY : UpdateScan
    LEGACY_UNCHANGED --> MIGRATION_PROPOSED : DetectLegacyYaml
```

### Notes

- **NO_CONTEXT** means the concern registry is absent. Initialization proposes concern batches and writes only after user confirmation.
- **MIGRATION_PROPOSED** preserves all legacy files until the user confirms the proposed mapping.
- **CONCERN_REGISTRY** is the current model. The team edits it directly, and new controlled-vocabulary entries require confirmation.
- **FoldContextMap** is `capture-context --fold-context-map`. It adds one domain concern marked as folded per context of a context map or a routing-only `CONTEXT.md`, and shows the result to the developer. **UpdateScan** is `capture-context --update --scan`; it never removes a folded concern. See [core-artifact-layout.feature](features/core-artifact-layout.feature).
- **LEGACY_UNCHANGED** records a declined migration. A later bare `capture-context` invocation may propose migration again.
- Confirmed migration moves test configuration to `docs/testing.yaml` and removes legacy routing formats. `concern-lint` validates the resulting single-format state.

## Referenced from

- [entity-model.md](entity-model.md)
- [activity-graph-orchestration.feature](features/activity-graph-orchestration.feature)
- [agent-context.feature](features/agent-context.feature)

## Usage Query Lifecycle

### Pseudocode

```text
State: IDLE
On StartQuery:
  ChangeState(INPUT_SNAPSHOTTED)

State: INPUT_SNAPSHOTTED
On PreflightPass:
  ChangeState(READY)
On PreflightFailure:
  ChangeState(DIAGNOSTIC_ONLY)

State: READY
On QueryHealth:
  ChangeState(COMPLETED)
On QueryStableView:
  ChangeState(COMPLETED)
On StartParquetExport:
  ChangeState(EXPORT_STAGED)

State: DIAGNOSTIC_ONLY
On QueryHealth:
  ChangeState(COMPLETED)
On QueryStableView:
  ChangeState(REFUSED)
On StartParquetExport:
  ChangeState(REFUSED)

State: EXPORT_STAGED
On RoundTripPass:
  ChangeState(COMPLETED)
On ExportInterrupted:
  ChangeState(FAILED_PRESERVED)
On RoundTripFailure:
  ChangeState(FAILED_PRESERVED)

State: COMPLETED
  # terminal — no outbound transitions

State: REFUSED
  # terminal — no outbound transitions

State: FAILED_PRESERVED
  # terminal — no outbound transitions
```

### Derived Mermaid

```mermaid
stateDiagram-v2
    [*] --> IDLE
    IDLE --> INPUT_SNAPSHOTTED : StartQuery
    INPUT_SNAPSHOTTED --> READY : PreflightPass
    INPUT_SNAPSHOTTED --> DIAGNOSTIC_ONLY : PreflightFailure
    READY --> COMPLETED : QueryHealth
    READY --> COMPLETED : QueryStableView
    READY --> EXPORT_STAGED : StartParquetExport
    DIAGNOSTIC_ONLY --> COMPLETED : QueryHealth
    DIAGNOSTIC_ONLY --> REFUSED : QueryStableView
    DIAGNOSTIC_ONLY --> REFUSED : StartParquetExport
    EXPORT_STAGED --> COMPLETED : RoundTripPass
    EXPORT_STAGED --> FAILED_PRESERVED : ExportInterrupted
    EXPORT_STAGED --> FAILED_PRESERVED : RoundTripFailure
    COMPLETED --> [*]
    REFUSED --> [*]
    FAILED_PRESERVED --> [*]
```

`FAILED_PRESERVED` means a pre-existing Parquet destination remains unchanged.

## Usage-Analysis Component Lifecycle

### Pseudocode

```text
State: ABSENT
On InstallUsage:
  ChangeState(INSTALLED)
On RemoveUsage:
  ChangeState(ABSENT)

State: INSTALLED
On InstallUsage:
  ChangeState(INSTALLED)
On UpdateUsage[compatible]:
  ChangeState(INSTALLED)
On UpdateUsage[incompatible]:
  ChangeState(INSTALLED)
On RemoveUsage:
  ChangeState(ABSENT)
On UpdateFactoryCore:
  ChangeState(INSTALLED)
On RemoveFactory:
  ChangeState(FULLY_REMOVED)

State: FULLY_REMOVED
  # terminal — no outbound transitions
```

### Derived Mermaid

```mermaid
stateDiagram-v2
    [*] --> ABSENT
    ABSENT --> INSTALLED : InstallUsage
    ABSENT --> ABSENT : RemoveUsage
    INSTALLED --> INSTALLED : InstallUsage
    INSTALLED --> INSTALLED : UpdateUsage (compatible)
    INSTALLED --> INSTALLED : UpdateUsage (incompatible)
    INSTALLED --> ABSENT : RemoveUsage
    INSTALLED --> INSTALLED : UpdateFactoryCore
    INSTALLED --> FULLY_REMOVED : RemoveFactory
    FULLY_REMOVED --> [*]
```

The incompatible-update self-transition represents refusal before replacement. `ABSENT` and `INSTALLED` component transitions preserve raw usage evidence. `FULLY_REMOVED` retains the existing complete-removal semantics and does not preserve it.

## Activity-Graph Orchestration State Machines

The activity-graph model has no delegation or retry state machines — chaining and retries are external. The workstream and session binding lifecycles are documented above. The fence execution lifecycle below captures the deterministic output-fencing flow.

Feature trace: [activity-graph-orchestration.feature](features/activity-graph-orchestration.feature)

### Fence Execution

The lifecycle of a single output fence invocation after an agent activity completes.

#### Pseudocode

```text
State: PENDING
On SnapshotOutputs:
  ChangeState(CHECKING)

State: CHECKING
On AllRequiredChanged_MinimumMet_AllValidatorsPass:
  ChangeState(PASSED)
On RequiredOutputMissing:
  ChangeState(FAILED)
On BelowMinimumChanged:
  ChangeState(FAILED)
On ValidatorFails:
  ChangeState(FAILED)

State: PASSED
  # terminal — evidence stored, downstream preconditions satisfiable

State: FAILED
  # terminal — evidence stored, human action not blocked
```

#### Derived Mermaid

```mermaid
stateDiagram-v2
    [*] --> PENDING
    PENDING --> CHECKING : SnapshotOutputs
    CHECKING --> PASSED : AllRequiredChanged_MinimumMet_AllValidatorsPass
    CHECKING --> FAILED : RequiredOutputMissing
    CHECKING --> FAILED : BelowMinimumChanged
    CHECKING --> FAILED : ValidatorFails
    PASSED --> [*]
    FAILED --> [*]
```

#### Notes

- **PENDING** exists between activity completion and output snapshot. The runner snapshots the agent's declared output patterns before comparing with post-activity state.
- **CHECKING** evaluates each output declaration: required outputs must have a created or modified match; optional outputs without a match are skipped; their validators run if they changed. The aggregate requires `declarations_changed >= minimum_changed` and every invoked validator to pass.
- **PASSED** means the aggregate fence passed. The fenced outputs become available as satisfied evidence for downstream preconditions. For external orchestrators, chaining may proceed.
- **FAILED** means one or more conditions were not met. The failure is recorded as unsatisfied evidence. Human action is not blocked — the human can still select any agent.
- Evidence is stored at `.agent-factory/checks/fences/<session-id>/<invocation-id>.yaml` and returned to the caller.
- No retry logic exists in the fence. An external orchestrator owns retry decisions.

### Referenced from

- [activity-graph-orchestration.feature](features/activity-graph-orchestration.feature)
- [entity-model.md](entity-model.md)
- [interface-contracts.md](interface-contracts.md)

## OpenCode Plugin Health Lifecycle

The lifecycle of the Factory plugin within an OpenCode session. The plugin must fail closed: an unhealthy state stops the Factory entry flow and names the recovery action.

Feature trace: [opencode-cli-integration.feature](features/opencode-cli-integration.feature)

### Pseudocode

```text
State: UNLOADED
On PluginSetup[success]:
  ChangeState(HEALTHY)
On PluginSetup[failure]:
  ChangeState(UNHEALTHY)

State: HEALTHY
On ManifestLoadFailure:
  ChangeState(UNHEALTHY)
On PermissionEvaluationFailure:
  ChangeState(UNHEALTHY)
On WorktreeCreationFailure:
  ChangeState(UNHEALTHY)
On SessionEnds:
  ChangeState(UNLOADED)

State: UNHEALTHY
On FactoryEntryAttempt:
  Reject — report failed control and recovery action
  ChangeState(UNHEALTHY)
On SessionEnds:
  ChangeState(UNLOADED)
```

### Derived Mermaid

```mermaid
stateDiagram-v2
    [*] --> UNLOADED
    UNLOADED --> HEALTHY : PluginSetup (success)
    UNLOADED --> UNHEALTHY : PluginSetup (failure)
    HEALTHY --> UNHEALTHY : ManifestLoadFailure
    HEALTHY --> UNHEALTHY : PermissionEvaluationFailure
    HEALTHY --> UNHEALTHY : WorktreeCreationFailure
    HEALTHY --> UNLOADED : SessionEnds
    UNHEALTHY --> UNHEALTHY : FactoryEntryAttempt (rejected)
    UNHEALTHY --> UNLOADED : SessionEnds
```

### Notes

- **UNLOADED** means the plugin is not active. This is the state before the OpenCode session loads the plugin and after the session ends.
- **HEALTHY** means the plugin initialized and all controls are operational. Tool invocations, permission evaluations, and worktree operations proceed normally.
- **UNHEALTHY** means one or more Factory controls failed. The plugin stops the Factory entry flow and names the failed control and the recovery action. The error message is specific: "Factory plugin: manifest loading failed — re-run init-factory" rather than a generic failure.
- Usage capture failure does not transition to UNHEALTHY. Usage capture is best-effort; its failure is reported but does not block the session.
- The plugin does not self-heal during a session. An UNHEALTHY plugin requires a new session after the underlying issue is resolved.

## OpenCode Session Isolation Lifecycle

The lifecycle of a write-denial lock on the primary checkout while isolated child work is active.

Feature trace: [opencode-cli-integration.feature](features/opencode-cli-integration.feature)

### Pseudocode

```text
State: UNLOCKED
On ChildSessionDispatched:
  ChangeState(LOCKED)

State: LOCKED
On WriteAttemptToPrimaryCheckout:
  Reject — session-scoped write denial
  ChangeState(LOCKED)
On AllChildSessionsComplete:
  ChangeState(UNLOCKED)

```

### Derived Mermaid

```mermaid
stateDiagram-v2
    [*] --> UNLOCKED
    UNLOCKED --> LOCKED : ChildSessionDispatched
    LOCKED --> LOCKED : WriteAttemptToPrimaryCheckout (rejected)
    LOCKED --> UNLOCKED : AllChildSessionsComplete
```

### Notes

- **UNLOCKED** means the primary checkout accepts writes normally. No isolated child work is active.
- **LOCKED** means one or more child sessions are running in isolated worktrees. Writes to the primary checkout are denied through a session-scoped write denial enforced by the plugin's permission hook.
- The lock is session-scoped. It does not persist across sessions.
- The lock applies to the primary checkout only. Each child session writes to its own worktree without restriction (within its step-manifest boundary).

## Value-First Installation Lifecycle

### Pseudocode

```text
State: START
On BeginPreflight:
  if source and target are valid and host is supported
    ChangeState(PREFLIGHTED)
  else
    ChangeState(STOPPED_UNCHANGED)

State: PREFLIGHTED
On ClassifyReadiness:
  if result is Blocked
    ChangeState(STOPPED_UNCHANGED)
  else if a supported fix exists for a failed check
    ChangeState(FIX_OFFERED)
  else
    ChangeState(PREVIEWED)

State: FIX_OFFERED
On DecideFix:
  if fix is confirmed
    ChangeState(FIX_VERIFYING)
  else
    ChangeState(PREVIEWED)

State: FIX_VERIFYING
On VerifyFix:
  if verification passes
    ChangeState(PREFLIGHTED)
  else
    ChangeState(PREVIEWED)

State: PREVIEWED
On DecideInstallation:
  if installation is approved and remote assets are verified
    ChangeState(INSTALLING)
  else
    ChangeState(STOPPED_UNCHANGED)

State: INSTALLING
On VerifyInstallation:
  if verification passes
    ChangeState(INSTALLED)
  else
    ChangeState(STOPPED_VALID)

State: INSTALLED
  # terminal — no outbound transitions

State: STOPPED_UNCHANGED
  # terminal — no outbound transitions

State: STOPPED_VALID
  # terminal — no outbound transitions
```

### Derived Mermaid

```mermaid
stateDiagram-v2
    [*] --> START
    START --> PREFLIGHTED : BeginPreflight (valid source, safe target, supported host)
    START --> STOPPED_UNCHANGED : BeginPreflight (invalid or unsupported)
    PREFLIGHTED --> FIX_OFFERED : ClassifyReadiness (supported fix exists for a failed check)
    PREFLIGHTED --> PREVIEWED : ClassifyReadiness (no supported fix exists)
    PREFLIGHTED --> STOPPED_UNCHANGED : ClassifyReadiness (Blocked)
    FIX_OFFERED --> FIX_VERIFYING : DecideFix (confirmed)
    FIX_OFFERED --> PREVIEWED : DecideFix (declined, cancelled, or blank)
    FIX_VERIFYING --> PREFLIGHTED : VerifyFix (passes, offers the next supported fix if any)
    FIX_VERIFYING --> PREVIEWED : VerifyFix (fails)
    PREVIEWED --> INSTALLING : DecideInstallation (approved and verified)
    PREVIEWED --> STOPPED_UNCHANGED : DecideInstallation (declined, cancelled, blank, or unverified)
    INSTALLING --> INSTALLED : VerifyInstallation (passes)
    INSTALLING --> STOPPED_VALID : VerifyInstallation (fails)
    INSTALLED --> [*]
    STOPPED_UNCHANGED --> [*]
    STOPPED_VALID --> [*]
```

`STOPPED_UNCHANGED` means the target received no installation change.
`STOPPED_VALID` means an approved installation began and then failed
verification; some effects may exist. A declined, blank, cancelled, or
unverified prerequisite fix reports completed fixes and their reversal
commands but does not stop the bootstrap: `Blocked` is the only readiness
that prevents installation, so once readiness is classified, an unresolved
optional fix still leads to `PREVIEWED`.

## First-Task Sandbox Lifecycle

### Pseudocode

```text
State: ABSENT
On DecideTask:
  if task is approved and HEAD exists
    Create detached worktree from HEAD
    ChangeState(READY)
  else if task is approved and HEAD does not exist
    Create plain sandbox
    ChangeState(READY)
  else
    ChangeState(CANCELLED)

State: READY
On RunPocSpike:
  ChangeState(RUNNING)

State: RUNNING
On FinishTask:
  Record result or failure evidence
  ChangeState(COMPLETED)

State: COMPLETED
On ChooseOutcome:
  if discard is selected
    Remove sandbox and verify absence
    ChangeState(REMOVED)
  else if reference retention is confirmed
    Copy selected artifacts to docs/spikes/
    ChangeState(RETAINED_REFERENCE)
  else if production work is approved
    Leave sandbox outside production work
    ChangeState(HANDED_OFF)

State: CANCELLED
  # terminal — no outbound transitions

State: REMOVED
  # terminal — no outbound transitions

State: RETAINED_REFERENCE
  # terminal — no outbound transitions

State: HANDED_OFF
  # terminal — no outbound transitions
```

### Derived Mermaid

```mermaid
stateDiagram-v2
    [*] --> ABSENT
    ABSENT --> READY : DecideTask (approved, HEAD exists) / Create detached worktree
    ABSENT --> READY : DecideTask (approved, no HEAD) / Create plain sandbox
    ABSENT --> CANCELLED : DecideTask (declined, cancelled, or blank)
    READY --> RUNNING : RunPocSpike
    RUNNING --> COMPLETED : FinishTask / Record result or failure evidence
    COMPLETED --> REMOVED : ChooseOutcome (discard) / Remove sandbox and verify absence
    COMPLETED --> RETAINED_REFERENCE : ChooseOutcome (retain) / Copy selected artifacts to docs/spikes/
    COMPLETED --> HANDED_OFF : ChooseOutcome (production) / Leave sandbox outside production work
    CANCELLED --> [*]
    REMOVED --> [*]
    RETAINED_REFERENCE --> [*]
    HANDED_OFF --> [*]
```

The first-task lifecycle never creates a branch or commit. Retention copies
reference artifacts after separate consent. Production work begins through a
normal workstream and does not reuse the sandbox as production state.

## Core Artifact Ownership State Machines

Two kinds of row move through statuses in
[core-artifact-ownership.feature](features/core-artifact-ownership.feature):
a row of a drift report and a row of the term-candidate file. Written per
[state-machine-notation.md § Canonical Format](../../.agent-factory/factory/rulebooks/conventions/state-machine-notation.md#canonical-format):
pseudocode is authoritative, Mermaid is derived.

### Report Row Lifecycle

A row of `docs/spec/work/spec-feedback-<story-id>.md` or of
`docs/reviews/reconciliation-<date>.md`. BR-061 names who sets each status,
and BR-062 names the statuses that block `dispatch close-wave`.

#### Pseudocode

```text
State: OPEN
  # initial — the developer agent or the reconciliation agent writes the row
On OwnerFixesArtifact:
  ChangeState(FIXED)

State: FIXED
  # terminal when the artifact has no declared review, such as a QA strategy or an ADR
On ReviewAccepts:
  ChangeState(CONFIRMED)
On ReviewRejects:
  ChangeState(REJECTED)

State: CONFIRMED
  # terminal — no outbound transitions

State: REJECTED
  # terminal — a BUG finding against the code takes the row's place
```

#### Derived Mermaid

```mermaid
stateDiagram-v2
    [*] --> OPEN
    OPEN --> FIXED : OwnerFixesArtifact
    FIXED --> CONFIRMED : ReviewAccepts
    FIXED --> REJECTED : ReviewRejects
    FIXED --> [*]
    CONFIRMED --> [*]
    REJECTED --> [*]
```

#### Notes

- **OPEN** is the status the developer agent or the reconciliation agent writes.
- **FIXED** ends the row when its artifact has no declared review, such as a QA strategy or an ADR (DEC-35). On a core or seam artifact the row waits for the review.
- **REJECTED** means the review found that the code breaks an accepted requirement. The reviewer files a `BUG` finding with the developer agent as owner.

### Term Candidate Lifecycle

A row of `docs/spec/work/term-candidates.md`. BR-065 holds the rules.

#### Pseudocode

```text
State: CANDIDATE
  # initial — reverse-map or another agent records a term it found
On DomainModelingProposesDefinition:
  ChangeState(PROPOSED)

State: PROPOSED
On StakeholderConfirms:
  ChangeState(CONFIRMED)
On StakeholderRejects:
  ChangeState(REJECTED)

State: CONFIRMED
  # initial when the stakeholder settled the term in a session of another agent
On DomainModelingMovesTerm:
  ChangeState(IN_GLOSSARY)

State: REJECTED
On DomainModelingProposesDefinition:
  # the new definition uses the stakeholder's note, and the row keeps the note
  ChangeState(PROPOSED)

State: IN_GLOSSARY
  # terminal — the row leaves the work file
```

#### Derived Mermaid

```mermaid
stateDiagram-v2
    [*] --> CANDIDATE
    [*] --> CONFIRMED
    CANDIDATE --> PROPOSED : DomainModelingProposesDefinition
    PROPOSED --> CONFIRMED : StakeholderConfirms
    PROPOSED --> REJECTED : StakeholderRejects
    REJECTED --> PROPOSED : DomainModelingProposesDefinition
    CONFIRMED --> IN_GLOSSARY : DomainModelingMovesTerm
    IN_GLOSSARY --> [*]
```

#### Notes

- **CANDIDATE** is the row that `reverse-map` writes: only the name and its source are known.
- A row starts at **CONFIRMED** when the stakeholder settled the term in a session of another agent, such as Virgil's `grilling`.
- **IN_GLOSSARY** is not a value of the Status column. It names the moment the domain-modeling agent writes the glossary row and removes the work-file row.
- **REJECTED** waits for a new definition. The domain-modeling agent writes it from the stakeholder's note, the row returns to **PROPOSED**, and the stakeholder sees it at the next pause point (CAO-G09).
- An unattended run of the domain-modeling agent leaves its rows at **PROPOSED**. The spec review files a finding for each of them.

## Counter IDs State Machines

One claim of `next-id` in
[counter-ids.feature](features/counter-ids.feature) loops until the remote
accepts its push or the claim fails. Written per
[state-machine-notation.md § Canonical Format](../../.agent-factory/factory/rulebooks/conventions/state-machine-notation.md#canonical-format):
pseudocode is authoritative, Mermaid is derived. A seed has no loop, so it
has no state machine.

### Claim Lifecycle

One call of `next-id <PREFIX>`, after the prefix check and the remote lookup
passed. BR-071, BR-072, and BR-076 hold the rules.

#### Pseudocode

```text
State: READING
  # initial — next-id fetches refs/ids/counters into its throwaway repository
On CounterRead:
  ChangeState(PUSHING)
On CounterMissing:
  ChangeState(FAILED)
On FetchRefused:
  # the remote answers but refuses the fetch, such as for missing credentials
  ChangeState(FAILED)
On RemoteUnreachable:
  ChangeState(FAILED)
On GitCallTimedOut:
  # the fetch runs longer than the time limit of BR-076
  ChangeState(FAILED)

State: PUSHING
  # next-id pushes the new claim commit with the lease on the old SHA
On PushAccepted:
  ChangeState(CLAIMED)
On LeaseStale:
  if fewer than ten stale leases in a row
    ChangeState(WAITING)
  else
    ChangeState(FAILED)
On PushRefused:
  ChangeState(FAILED)
On RemoteUnreachable:
  ChangeState(FAILED)
On GitCallTimedOut:
  # the push runs longer than the time limit of BR-076
  ChangeState(FAILED)

State: WAITING
  # a random wait of 0.1 to 1 second
On WaitEnds:
  ChangeState(READING)

State: CLAIMED
  # terminal — next-id prints the ID and exits 0

State: FAILED
  # terminal — next-id prints no ID and exits non-zero
```

#### Derived Mermaid

```mermaid
stateDiagram-v2
    [*] --> READING
    READING --> PUSHING : CounterRead
    READING --> FAILED : CounterMissing
    READING --> FAILED : FetchRefused
    READING --> FAILED : RemoteUnreachable
    READING --> FAILED : GitCallTimedOut
    PUSHING --> CLAIMED : PushAccepted
    PUSHING --> WAITING : LeaseStale (fewer than ten in a row)
    PUSHING --> FAILED : LeaseStale (tenth in a row)
    PUSHING --> FAILED : PushRefused
    PUSHING --> FAILED : RemoteUnreachable
    PUSHING --> FAILED : GitCallTimedOut
    WAITING --> READING : WaitEnds
    CLAIMED --> [*]
    FAILED --> [*]
```

#### Notes

- **READING** reads the claim commit again on every loop, so the next claim sees the number that the other caller took.
- **LeaseStale** is the event for the git messages `stale info` and `cannot lock ref … is at <sha> but expected <sha>`, which git prints in English because `next-id` runs it with `LC_ALL=C`. Every other refusal is **PushRefused** and ends the claim after one push (DEC-23).
- **FAILED** names the reason as the claim error table in [interface-contracts.md](interface-contracts.md#packagesfactoryscriptsnext-id) lists it. In every terminal state, `next-id` deletes its throwaway repository (BR-075).

## Finding Classification State Machines

A finding in
[finding-classification.feature](features/finding-classification.feature)
moves from its classification to a finding file, a register line, or the
review report. Written per
[state-machine-notation.md § Canonical Format](../../.agent-factory/factory/rulebooks/conventions/state-machine-notation.md#canonical-format):
pseudocode is authoritative, Mermaid is derived. The stop of a run is no
state of its own. `dispatch` and `premerge-check` read it from the findings in
**STOPPING** each time they run (BR-091).

### Finding Lifecycle

One finding, from the pause point to its end. The status field of a finding
file shows the state: **STOPPING** and **IN_LOOP** are both `open`. BR-085,
BR-086, BR-090, and BR-091 hold the rules.

#### Pseudocode

```text
State: CLASSIFIED
  # initial — the reviewer agent or the migration agent recorded the basis, and the rule computed the severity
  # the pause point shows the finding; no file is written yet
On AnswerChanged:
  # the user changes an answer of the basis at the pause point, and the rule computes the severity again
  ChangeState(CLASSIFIED)
On Recorded:
  if severity is critical
    ChangeState(STOPPING)
  else if severity is major
    ChangeState(IN_LOOP)
  else if severity is minor
    ChangeState(REGISTERED)
  else
    ChangeState(IN_REPORT)
On NoArtifact:
  # migration only — an old open finding that names no artifact moves into todo.md
  ChangeState(DEFERRED)

State: STOPPING
  # finding file with severity critical, status open, and an empty stop_confirmed_by or stop_confirmed_reason
  # dispatch and premerge-check refuse work and print the stop notice
On StopConfirmed:
  # the stakeholder ran the damage checks, and both stop_confirmed_by and stop_confirmed_reason hold text
  ChangeState(IN_LOOP)
On FixVerified:
  RejectCommand("finding-lint: a critical finding is resolved only after its stop is confirmed")
On Waived:
  RejectCommand("finding-lint: a critical finding is waived only after its stop is confirmed")
On AgentConfirms:
  RejectCommand("guard-human-fields: only a person writes stop_confirmed_by")

State: IN_LOOP
  # finding file with status open; the orchestrator sends it to its owner on each pass
On FixVerified:
  # a repeat pass of the review checks the fix and sets status resolved
  ChangeState(RESOLVED)
On Waived:
  # the stakeholder sets status waived with override_by and override_reason
  ChangeState(WAIVED)

State: REGISTERED
  # one line in docs/findings/register/<class>.jsonl; it never blocks
On Fixed:
  # the commit that fixes the finding deletes the line
  ChangeState(LINE_DELETED)
On Raised:
  # the human changes an answer of the basis, removes the line, and files a finding file under the same ID
  if severity is critical
    ChangeState(STOPPING)
  else
    ChangeState(IN_LOOP)

State: IN_REPORT
  # terminal — a note stays in the review report only

State: RESOLVED
  # terminal — the file stays as the record

State: WAIVED
  # terminal — accepted unfixed; the loop grep for status open skips it

State: DEFERRED
  # terminal — the file names the todo ID in its body

State: LINE_DELETED
  # terminal — git history keeps the line
```

#### Derived Mermaid

```mermaid
stateDiagram-v2
    [*] --> CLASSIFIED
    CLASSIFIED --> CLASSIFIED : AnswerChanged
    CLASSIFIED --> STOPPING : Recorded (critical)
    CLASSIFIED --> IN_LOOP : Recorded (major)
    CLASSIFIED --> REGISTERED : Recorded (minor)
    CLASSIFIED --> IN_REPORT : Recorded (note)
    CLASSIFIED --> DEFERRED : NoArtifact (migration only)
    STOPPING --> IN_LOOP : StopConfirmed
    IN_LOOP --> RESOLVED : FixVerified
    IN_LOOP --> WAIVED : Waived
    REGISTERED --> LINE_DELETED : Fixed
    REGISTERED --> STOPPING : Raised (critical)
    REGISTERED --> IN_LOOP : Raised (major)
    IN_REPORT --> [*]
    RESOLVED --> [*]
    WAIVED --> [*]
    DEFERRED --> [*]
    LINE_DELETED --> [*]
```

#### Notes

- **CLASSIFIED** covers the pause point of a review and the pause point of the migration. A headless run has no pause point, so **Recorded** follows at once, and the final summary lists each new register line (BR-090).
- **STOPPING** has no edge to **RESOLVED** or **WAIVED**. A `critical` finding is resolved or waived only after both confirmation fields hold text, so the damage checks run before the stop ends (DEC-47, DEC-52). While the stop holds, `dispatch` starts and merges no work. A person who fixes the defect by hand confirms the stop first.
- **IN_LOOP** of a confirmed `critical` finding keeps severity `critical`. The finding loops like a `major` one (DEC-28).
- **Waived** is open to a blocking finding only. A `minor` finding never blocks, so **REGISTERED** has no **Waived** edge, and no override raises it (DEC-25). The stakeholder raises it only through **Raised**.
- **AgentConfirms** and the agent's attempt to set `waived` are refused by `guard-human-fields` (BR-092). The finding stays in its state.
- A **question** never enters this machine. The reviewer agent writes it into `docs/spec/work/todo.md` (BR-085).
