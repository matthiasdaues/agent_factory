---
schema_version: 2
title: "Matrix Project Channel and Spoken Clarification"
status: open
owner: agent-factory
created: 2026-08-07
updated: 2026-08-07
supersedes:

impact:
  scope: cross_project
  architecture_change: true
  external_contract_change: true
  boundaries:
    - factory/scripts/init-factory
    - factory/scripts/run-playbook
    - factory/skills/run-step/SKILL.md
    - factory/scripts/phase
    - factory/skills/grilling/SKILL.md
    - factory/docs/factory-guide.md
    - docs/arc42/architecture.dsl

governance:
  assurance: critical
  risk_domains:
    - security
    - privacy
    - data_integrity
    - compatibility
    - reliability
    - operations

estimate:
  as_of: 2026-08-07
  basis: judgment
  confidence: low
  human_review_hours: unknown
  normalized_tokens: unknown
---

# Feature Request: Matrix Project Channel and Spoken Clarification

## Summary

Give each Agent Factory project one encrypted Matrix room as its remote
operational interface. A human establishes the room, credentials, project
binding, runtime backend, and persistent services from a local terminal; after
a successful two-way verification and explicit activation, the human may exit
the terminal and use Element for text, spoken clarification, artifacts,
notifications, and bounded Factory commands.

The Matrix edge remains a message switchboard, not a workflow authority. A
Factory Session Controller acts as a third user peer over the same public
Factory CLI used by a human or the orchestrator, while Factory scripts retain
exclusive authority over workflow-state legality and deterministic gates. The
channel works with either today's host-native Factory installation or the
separate [execution-isolation proposal](agent-execution-isolation-and-distribution.md);
neither backend changes the Matrix protocol or grants Matrix administrative
control.

## Motivation

Agent Factory currently assumes that a human stays close to a terminal to
provide instructions, observe progress, answer human gates, and conduct
requirements or design interviews. The Factory already separates user
intent from workflow mechanics: humans and the orchestrator invoke the same
scripts, while scripts and deterministic gates own state. A remote interface
should add another peer at that boundary rather than bridge Matrix directly
into internal markers or duplicate workflow logic.

Matrix and Element provide encrypted project rooms, text, threads, voice
messages, and file transport. The required assistant is therefore not a
general autonomous personal agent. It is a narrow Matrix edge plus a
project-aware Factory conversational session. The edge transports and renders;
the conversational session supports clarifying discussion in text or voice
messages and may run a suitable project-local workflow, such as
[`grilling`](../../factory/skills/grilling/SKILL.md), when you ask for
that interview style. The Factory validates and records durable results.

The system must remain optional and independently deployable. Projects that
continue to run Factory host-native must receive the same Matrix behavior as
projects that select the proposed pinned container distribution.

## Core Principles

- One active Matrix room maps to exactly one Factory project.
- The room supplies project-routing context; it is not by itself a security
  boundary.
- Local terminal setup establishes administrative authority; Matrix never
  bootstraps or expands its own authority.
- Activation requires a successful encrypted two-way test and a final local
  confirmation.
- The Matrix edge has no shell, Git access, or project mount.
- The Factory runtime has no Matrix credentials or unquarantined media access.
- A Session Controller owns process and conversation lifecycle but not
  workflow-state legality.
- Host-native and containerized Factory execution implement one runtime port.
- Spoken conversation may supply design input; consequential workflow actions
  remain explicit, textual, expiring, and mechanically validated.
- Every message, decision, artifact, and notification is idempotent and
  correlated to a project and, where applicable, a run and gate.
- Local speech processing is the default; every external model boundary is
  explicit per project.
- Unsupported identity, room, media, state, or runtime conditions fail closed.

## Design

### System context

```text
Element
  │ Matrix E2EE: text, threads, voice messages, files
  ▼
Matrix Edge
  │ typed transport-independent records
  ▼
Factory Session Controller ───────► Media Sandbox
  │                                 validate · STT · TTS
  │ Factory Runtime Port
  ├───────────────────┬──────────────────────────┐
  ▼                   ▼                          │
Host-native Factory   Containerized Factory     │
  │                   │                          │
  └──────────────┬────┘                          │
                 ▼                               │
       Factory scripts, FSM, gates, Git ◄────────┘
```

The Matrix Edge, Session Controller, Media Sandbox, and runtime adapter are
separate trust boundaries. They may initially ship in one distribution, but
their credentials, mounts, processes, and interfaces remain distinct.

### One room per project

The authoritative binding is:

```text
Matrix room ID ↔ project UUID ↔ canonical project root
```

Room names and aliases are display metadata. A project has at most one active
control room; a room controls at most one project. The binding lives in
host-controlled configuration outside the agent-writable project.

Example:

```json
{
  "schema_version": 1,
  "room_id": "!abc123:example.org",
  "project_id": "687cf46a-25f6-4e98-9c62-278612aafd9f",
  "canonical_project_root": "/srv/projects/example",
  "runtime_backend": "host-native",
  "allowed_users": ["@matthias:example.org"],
  "enabled": true
}
```

Changing the room, project root, runtime backend, image trust, or user set
is a terminal-only administrative action. Rebinding is forbidden while a run,
human gate, or clarification session is active. A room upgrade creates a new
room ID and requires an explicit migration; it never inherits project authority
automatically.

The room lifecycle is:

```text
UNBOUND → VERIFYING → READY → ACTIVE → SUSPENDED → RETIRED
               ▲                 │
               └── MIGRATING ◄───┘
```

### Matrix Edge

The Matrix Edge is a regular Matrix client, not an application service. It
uses a dedicated bot account and verified device, receives and decrypts room
events, sends notifications, downloads media into quarantine, and translates
Matrix events into typed records.

It owns:

- Matrix authentication, sync position, and E2EE device state;
- exact room and sender policy;
- text, reply, thread, edit, redaction, voice-message, and file normalization;
- Matrix-event duplicate suppression;
- encrypted media download into quarantine;
- rendering and delivery of Factory events; and
- Matrix delivery attempts and acknowledgements.

It has no project mount, shell, Git access, container-runtime socket, Factory
state access, or authority to launch a Factory runtime.

One bot account may serve several project rooms in the standard deployment,
but this is a shared credential and key-compromise domain. A hardened profile
uses one bot account and device per project. Room separation supplies routing
and membership isolation; only separate credentials reduce cross-project
cryptographic blast radius.

### Factory Session Controller

The Session Controller is the explicit third user peer. It owns lifecycle
and routing that neither the Matrix Edge nor Factory scripts should own:

- load host-controlled room/project/runtime bindings;
- maintain the single fenced controller lease for the project room;
- start, resume, stop, and recover the selected Factory runtime;
- start or resume project-bound conversational sessions;
- deliver typed task messages, admitted artifacts, and candidate decisions;
- observe structured Factory events and enqueue Matrix notifications;
- create single-use decision challenges;
- reconcile ambiguous outcomes after crashes; and
- persist clarification-session state across terminal and process restarts.

It invokes only the public Factory CLI surface. It never writes FSM markers,
declares a gate passed, or treats an agent response as deterministic evidence.
Factory scripts such as [`phase`](../../factory/scripts/phase) and
[`run-playbook`](../../factory/scripts/run-playbook) remain authoritative.
[`run-step`](../../factory/skills/run-step/SKILL.md) is a dispatching skill over
that public surface, not an additional workflow authority.

### Factory Runtime Port

The Session Controller depends on one runtime interface:

```text
doctor(project)
start_session(project, purpose, context)
resume_session(session_id, message)
submit_decision(run_id, gate_id, decision_record)
observe_events(run_id, cursor)
stop_session(session_id)
```

Release 1 provides two adapters.

**Host-native adapter:**

- runs the installed project's Factory scripts and supported AI CLI as the
  dedicated identity defined by the execution-isolation proposal;
- uses the canonical project root as its working directory;
- receives only the host-controlled delegated paths and access modes; and
- does not require Docker or Podman.

**Container adapter:**

- invokes the trusted launcher and pinned image defined by the
  [execution-isolation proposal](agent-execution-isolation-and-distribution.md);
- mounts only the approved delegated paths and directional broker paths, with
  their declared access modes;
- uses the same dedicated identity and delegation model as the host-native
  adapter; and
- does not expose Matrix credentials or the container-runtime socket inside the
  Factory runner.

Runtime selection is made during terminal setup and stored in host-controlled
configuration. Matrix commands cannot change it. Both adapters must produce
the same typed events, decision results, and conversational behavior. Security
status reports the selected backend and effective delegation honestly;
enabling Matrix does not broaden either backend's authority.

### Directional message broker

The Matrix Edge and Session Controller exchange versioned,
transport-independent records through directional ownership. One component
never rewrites the other's source records.

Inbound types:

- `task_message`;
- `user_decision`;
- `cancellation_request`;
- `artifact_submission`; and
- `notification_acknowledgement`.

Outbound types:

- `run_started`;
- `progress_updated`;
- `human_gate_opened`;
- `artifact_published`;
- `run_failed`;
- `run_blocked`; and
- `run_completed`.

An initial filesystem implementation uses exclusive creation, schema
validation, atomic rename, immutable record IDs, one writer per path, separate
acknowledgements, and duplicate detection. A database is deferred until
concurrency or query requirements justify it.

Controller ownership is local and fenced. Release 1 permits at most one active
Factory run per project room. A controller must hold an operating-system file
lock before it can allocate a monotonically increasing lease epoch. Every
runtime session and every state-changing Factory command carries that epoch;
the Factory command boundary rejects an epoch other than the current durable
epoch. Process exit releases the file lock. Recovery allocates a new epoch,
which fences a paused or stale controller, and reconciles durable Factory state
before resuming work or retrying an operation with an unknown outcome. The
filesystem inbox's one-writer rule is not treated as a lease mechanism.

Every record includes a schema version, UUID, project ID, creation time,
content hash, and source or destination. Run, session, gate, Matrix room,
event, thread, sender, and artifact identifiers are present when applicable.
The content hash detects accidental mutation; filesystem ownership and trusted
process boundaries provide authenticity.

### Local setup and handover

The human performs setup from the project directory:

```bash
agent-factory channel matrix setup
```

Setup:

01. Runs project, Factory, selected-runtime, storage, and service-manager
    diagnostics.
02. Resolves the project UUID and canonical root.
03. Selects `host-native` or `container` as the runtime backend.
04. Authenticates a dedicated Matrix bot device.
05. Stores its token, sync data, and E2EE keys outside the project.
06. Creates or selects an encrypted project room.
07. Registers the exact room ID and allowed user.
08. Configures local or explicitly external model, STT, and TTS profiles.
09. Starts the Matrix Edge, Session Controller, and Media Sandbox provisionally.
10. Performs a two-way encrypted verification.

The terminal displays the project, room, bot account, bot device, and a
single-use verification code. The bot sends the same project identity and code
to the room. The allowed human verifies the bot device in Element and replies
with the exact verification command. The controller proves outbound delivery,
inbound sender/room matching, challenge consumption, and device trust in the
terminal.

The final activation step is local:

```text
Activate this Matrix channel? [y/N]
```

A Matrix event cannot activate, bind, or expand its own authority.

For a host-native backend, activation additionally states that remote Factory
operations run as the configured host identity with that identity's filesystem,
credential, and network access. You must explicitly accept that risk;
the host-native adapter runs under a dedicated restricted operating-system
identity where the platform supports it. Setup fails if the configured identity
has broader access than the diagnostics and you have not explicitly
accepted the reported access profile. This is a security-policy distinction,
not merely a different status label.

Activation records the configuration atomically and hands the long-running
processes to a persistent user service. Setup succeeds only after the service
manager owns the processes and a post-handover health check passes. The human
may then exit the terminal. After reboot, the service restores Matrix sync,
E2EE state, bindings, broker cursors, pending notifications, and session/run
references.

### Administrative versus operational authority

The terminal remains the administrative interface for:

```text
setup                 activate
suspend               migrate-room
rotate-device         authorize-user
revoke-user           select-runtime
repair                update
remove
```

Matrix is the operational interface for:

```text
status                 project notes
spoken clarification   artifact submission
artifact listing       bounded Factory decisions
notification ack       cancellation request
```

Matrix cannot bind projects, authorize users, rotate devices, select runtimes,
change mounts, approve image digests, enable external speech/model services,
disable controls, update software, or remove the integration.

### Turn-based spoken clarification

Release 1 provides turn-based clarifying discussion with text and voice
messages, not a live MatrixRTC call. A clarification session is bound to one
project room, one Matrix thread, one subject, and one Factory conversational
session. The subject may be a project topic, active run, human gate, artifact,
or target document. One project has at most one active clarification session.

Spoken clarification is the capability; grilling is one optional interview
style. Starting a session selects a suitable conversational workflow and does
not change that workflow's own contract. In particular, the stock `grilling`
skill continues to amend a proposal in place when it is deliberately selected.
The general clarification session does not imply that behavior.

```text
!clarify start topic "deployment boundary"
!clarify start document docs/proposals/example.md
!clarify start run <run-id>
!clarify pause
!clarify resume
!clarify repeat
!clarify slower
!clarify text-only
!clarify voice-only
!clarify correction <event-id> <text>
!clarify summary
!clarify finish
!clarify discard
```

Only messages in the registered clarification thread become conversational
input. Unthreaded audio becomes a project note; voice messages in other threads
remain unrouted until explicitly attached to a session. Turns are sequential. A
new message may cancel an unsent synthesized response but cannot create
concurrent reasoning turns against the same session.

The project-local conversational agent runs the workflow selected for the
session; [`grilling`](../../factory/skills/grilling/SKILL.md) is one available
example. The Matrix Edge does not perform requirements reasoning. Each response
contains complete text and, unless text-only mode is selected, synthesized
audio. Code, paths, commands, identifiers, decisions, and proposed document
wording always appear as text even when summarized in speech.

The system publishes what it transcribed. Corrections create append-only
transcript revisions rather than rewriting the source event. A correction
invalidates every derived summary, working decision, candidate command, or
document diff that depended on the corrected turn. Those outputs are re-derived
and remain unconfirmed until the user confirms them again. It does not rely
on a supposedly calibrated speech-model confidence score; detectable ambiguity,
terminology mismatch, or a user correction triggers clarification.

At `finish`, the conversational agent produces a summary and any outputs
appropriate to the selected workflow. A document-bound workflow may amend its
target during the session if that is part of its declared contract, or propose
a document diff at the end. Applying a proposed diff requires an explicit
textual challenge response.

A document-bound session records the target's canonical path and content hash
when it starts and before every write or proposed diff. A move, deletion, or
conflicting content change suspends document mutation and finish until the
user explicitly restarts against the new target or accepts a conflict-aware
rebase. Unrelated changes that rebase cleanly do not force the discussion to be
discarded.

### Audio and attachment processing

Element voice messages and ordinary uploaded audio enter an isolated Media
Sandbox:

```text
encrypted Matrix media
  → Matrix Edge decrypts into quarantine
  → generated name and ciphertext/plaintext hashes
  → byte, duration, format, and decoder limits
  → sandboxed decode
  → local transcription
  → provisional transcript record
  → optional local speech synthesis for replies
```

Sender filename, MIME type, size, duration, and waveform are hints, never
trusted paths or validation evidence. The Media Sandbox has no project mount,
Matrix token, or network in the local profile. It runs with bounded CPU,
memory, output size, and wall time. Temporary decoded audio is deleted after
processing.

An audio event may create a task message, project note, or artifact submission.
It cannot directly accept a proposal, advance a phase, approve a destructive
operation, cancel a run, admit an artifact, or acknowledge a security event.
If speech suggests such an action, the system renders the exact textual command
and requires the human to send it.

Raw-audio, transcript, TTS-output, quarantine, and admitted-artifact retention
are separate host-controlled project policies. Setup must present and record a
choice for every surface; it must not silently invent retention periods.
Terminal `repair` or `update` is required to change them. Local STT and TTS are
defaults. A project that
uses an external reasoning model still transmits the transcript to that model;
the setup and status output disclose the full selected processing profile
rather than calling the conversation local merely because STT is local.

### Decisions and workflow authority

Consequential commands use exact syntax and a versioned external protocol:

```text
!factory/v1 decide <gate-id> <accept|reject|changes> <nonce>
!factory/v1 cancel <run-id> <nonce>
!factory/v1 admit <submission-id> <nonce>
!factory/v1 ack <notification-id>
```

Setup pins the accepted protocol major version. The Matrix Edge rejects unknown
versions and exact-syntax violations; there is no implicit downgrade or
best-effort interpretation.

Free-form prose and reactions are non-authoritative. A nonce binds a response
to a transaction; it does not protect against a compromised authorized Matrix
account or device and is not represented as strong identity proof.

The Factory-side command atomically validates project, run, gate, expected
state and revision, actor, allowed decision, nonce, expiry, and unused status
while performing the accepted operation. A stale, duplicate, expired,
wrong-room, wrong-actor, or wrong-state decision fails without mutation.
Challenge expiry is measured from receipt by the trusted controller using the
host monotonic clock, never a Matrix event timestamp. Outstanding challenges
are bound to the current host boot identifier and become invalid after reboot.

### Artifact admission

Every attachment receives a generated artifact ID and content hash. Original
filenames remain display metadata. Quarantine enforces byte, decoded-size,
format, archive, and processing-time limits. The project runtime sees only an
immutable artifact that has crossed an explicit admission challenge; it never
sees the Matrix media cache or quarantine path.

### Reliability and recovery

Processing is idempotent by Matrix room ID and event ID. Edits create new
candidate records and never mutate consumed commands. Redactions affect Matrix
presentation and retention processing but do not erase an immutable Factory
audit record.

Every project room has at most one active run in Release 1, protected by the
fenced controller lease. On restart, the controller acquires a new epoch and
reconciles Factory state before retrying a command whose outcome is unknown. It
does not blindly replay consequential operations. Matrix outages queue outbound
events; missing E2EE keys suspend the channel rather than falling back to
plaintext.

Room migration, bot-device rotation, credential compromise, runtime-backend
change, project-path change, or user revocation suspends active remote
control, invalidates outstanding challenges, and requires local verification
before reactivation.

### Health and observability

`!factory status` reports project identity, channel lifecycle, bot/E2EE health,
runtime backend, Factory security posture, active run, active clarification
session, audio availability, processing profile, pending action, and last
successful health check. A host-native backend is labeled host-native and
states that remote operations use the configured host identity and its reported
filesystem, credential, and network access; it is never presented as
container-isolated.

Metrics and structured logs cover Matrix sync, E2EE failures, queue depth,
duplicate suppression, delivery attempts, media validation, transcription and
TTS duration, active sessions, controller leases, rejected challenges, and
runtime health. They omit Matrix tokens, encryption keys, raw audio, and full
transcript bodies by default.

## Scope

**In the first release:**

- Matrix and Element only; no Telegram or Signal adapters.
- One encrypted Matrix control room per Factory project.
- A host-controlled room/project/user/runtime registry.
- A regular Matrix bot with a dedicated verified device.
- Standard shared-bot and hardened per-project-bot deployment profiles.
- Local terminal setup, two-way verification, explicit activation, persistent
  user services, reboot recovery, suspension, repair, migration, and removal.
- A Factory Session Controller with one fenced lease and at most one active run
  per project room.
- Host-native and containerized Factory runtime adapters with equivalent
  external behavior.
- Typed directional inbox/outbox records and idempotent processing.
- Text, threads, voice messages, and quarantined file submission.
- One turn-based spoken clarification session per project room, with grilling
  available as one optional interview style.
- Local audio validation, STT, and TTS, with text always available.
- Transcript correction, decision summaries, proposed document diffs, and
  explicit diff application.
- Outbound progress, gate, failure, artifact, blocked, and completion
  notifications.
- Versioned, nonce-bound textual decisions for bounded workflow actions.
- Explicit disclosure of host-native versus container security and local
  versus external processing profiles.
- Automated refutation tests for identity, replay, state races, lifecycle,
  crashes, media, routing, and runtime equivalence.

**Explicitly deferred (do NOT plan stories for these):**

- Live MatrixRTC calls, streaming transcription, barge-in audio, speaker
  identification, and voice biometrics.
- Audio-authorized proposal acceptance, workflow transitions, destructive
  operations, cancellation, or artifact admission.
- Matrix application-service privileges.
- Multiple active clarification sessions in one project.
- Rooms controlling multiple projects or projects with multiple active rooms.
- Multi-user consensus and quorum decisions.
- Automatic room-upgrade inheritance.
- General-purpose assistant tools in the Matrix Edge.
- Cloud STT or TTS by default.
- Claiming that room separation cryptographically isolates projects when bot
  credentials are shared.
- Making container distribution mandatory for Matrix operation.

## Design Details

### Activation invariant

Matrix operational authority exists only when all of these remain true:

```text
binding is ACTIVE
AND room ID matches the host registry
AND room remains encrypted
AND bot device state is available and trusted
AND sender is joined and host-authorized
AND selected runtime passes doctor
AND exactly one controller holds the run lease
```

Failure suspends new commands. Messaging may remain available to explain the
degraded state, but it must not claim that Factory work can proceed.

### Severe proof cases

The owning automated or integration-test layer must cover:

| Case                                                        | Required result                                                    |
| ----------------------------------------------------------- | ------------------------------------------------------------------ |
| Outbound verification without valid inbound reply           | Activation blocked                                                 |
| Valid Matrix reply without local confirmation               | Activation blocked                                                 |
| Wrong room, sender, project, nonce, gate, or state          | No Factory mutation                                                |
| Replayed, duplicated, expired, edited, or redacted decision | At most one original outcome                                       |
| Two controllers resume one run                              | One lease wins; the other stops                                    |
| Crash after command consumption with unknown outcome        | Reconcile state before retry                                       |
| Factory state changes while approval is in transit          | Stale decision rejected                                            |
| Room upgraded or migrated                                   | Old room loses authority                                           |
| Bot device state lost or rotated                            | Channel suspended pending verification                             |
| User revoked with outstanding challenges                    | Challenges invalidated                                             |
| Unauthorized user invited to room                           | No user authority gained                                           |
| Voice event outside active clarification thread             | Stored as note, not routed as answer                               |
| Stale controller submits an old lease epoch                 | Factory command rejects it without mutation                        |
| Corrected turn fed a derived decision or diff               | Derived output invalidated pending reconfirmation                  |
| Document target changes during clarification                | Clean rebase or explicit suspension; no blind overwrite            |
| Critical technical term mistranscribed                      | Transcript visible and correctable                                 |
| Malformed, oversized, disguised, or explosive media         | Sandbox rejects without cross-boundary effect                      |
| Matrix unavailable during a Factory run                     | Durable events delivered after recovery                            |
| TTS output addressed to wrong room/project                  | Delivery rejected before send                                      |
| Host-native and container adapters receive the same fixture | Equivalent protocol-visible result                                 |
| Host-native backend active                                  | Status reports absence of container isolation                      |
| External reasoning model configured                         | Data-egress profile visible before activation                      |
| Matrix Edge compromised                                     | No project mount, Factory credentials, or runtime socket available |
| Factory runtime compromised                                 | No Matrix token, E2EE keys, or quarantine access available         |

### Delivery slices

Implementation proceeds in authority-increasing slices:

1. Terminal setup, room binding, E2EE verification, persistent service, status,
   and outbound notifications.
2. Inbound project notes and quarantined artifacts without workflow authority.
3. Turn-based spoken clarification, correction, summaries, and optional
   workflow-specific outputs such as proposed diffs.
4. Explicit diff application through an atomic Factory command.
5. Bounded human-gate decisions and cancellation only after lifecycle, replay,
   and stale-state proof cases pass.

Each slice retains useful behavior if later authority is never enabled.

## Open Questions

None for the first release. Live audio, additional transports, broader room
topologies, and stronger multi-project credential isolation beyond the defined
hardened profile require a separate proposal or a material revision that
returns this proposal to `open`.

## Completion Criteria

- A human can configure either a host-native or containerized Factory project
  from a terminal without writing Matrix secrets into the project.
- Setup cannot become active until an encrypted outbound message, authorized
  inbound verification response, verified bot device, and final local
  confirmation all succeed.
- Persistent user services pass a post-handover health check, survive terminal
  exit, and restore safe state after reboot.
- Exactly one active Matrix room binds to one project UUID and canonical root;
  rebind, migration, and retirement invalidate prior authority.
- The Matrix Edge has no shell, project mount, Git access, Factory state access,
  or runtime socket.
- The Factory runtime has no Matrix credentials, E2EE state, or unquarantined
  media access.
- The Session Controller provides one recoverable lifecycle and fenced lease
  owner, serializing runs per project room in Release 1.
- Host-native and container runtime adapters pass the same protocol-level
  conformance suite while reporting their different security postures.
- Matrix events and broker records are idempotent, directional, versioned, and
  recoverable after process failure.
- A project room supports threaded text and turn-based spoken clarification
  with complete text responses, optional synthesized speech, transcript
  correction, and a decision summary. The selected workflow may additionally
  produce a proposed diff or another typed output.
- Spoken input, free-form prose, and reactions cannot directly authorize a
  consequential Factory operation.
- Every consequential decision is textual, actor/project/run/gate/state-bound,
  expiring, single-use, and atomically validated by a Factory command.
- Media validation and speech processing run within bounded sandboxes and
  cannot access projects, Matrix credentials, or the network in the local
  profile.
- Only explicitly admitted immutable artifacts become visible to the selected
  Factory runtime.
- Status and setup disclose runtime security and all local or external model,
  STT, and TTS boundaries accurately.
- The full severe proof matrix passes for both runtime adapters where the case
  applies.
- Specifications and arc42 architecture document the Matrix Edge, Session
  Controller, runtime port, Media Sandbox, broker records, lifecycle states,
  authority boundaries, and failure behavior.
- User documentation covers setup, verification, activation, normal Matrix
  use, host-native and container selection, health, suspension, repair, room
  migration, key rotation, backup, recovery, retention, and removal.
- Independent architecture and security reviews have no open blocking or major
  findings.

## Guiding Rule

The terminal establishes trust, Matrix carries project conversation, the
Session Controller operates the selected runtime, and Factory scripts alone
decide and record workflow state.
