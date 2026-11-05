---
schema_version: 2
scope: global
title: Project Agent Flows
status: draft
owner: Matthias Daues
created: 2026-11-03
updated: 2026-11-05
supersedes: docs/proposals/factory-orchestration.md

impact:
  scope: cross_project
  architecture_change: true
  external_contract_change: true
  boundaries:
    - packages/factory/engine
    - packages/factory/agents
    - packages/factory/playbooks
    - packages/factory/scripts/update-factory
    - packages/factory/scripts/verify-base
    - packages/factory/scripts/premerge-check
    - packages/factory/config
    - backlog/
    - docs/proposals/activity-graph-orchestration.md
    - docs/proposals/factory-orchestration.md
    - docs/proposals/external-artifact-sync.md
    - docs/proposals/counter-ids.md
    - docs/proposals/finding-classification.md
    - docs/proposals/review-loop-cap.md

governance:
  assurance: high
  risk_domains:
    - security
    - data_integrity
    - compatibility
    - reliability
    - operations

estimate:
  as_of: 2026-11-03
  basis: judgment
  confidence: low
  human_review_hours: unknown
  normalized_tokens: unknown
  estimated_consumption: unknown
---

# Feature Request: Project Agent Flows

## Primer

The primer is written last, by the `write-primer` skill, once the design is
settled.

## Summary

Each project combines Factory agents into its own flows. A Windmill automation
reads the project flow and decides which activity runs next. It starts an
activity when a brief or a handoff arrives, or when the activity's required
artifacts exist and the flow allows the step. The Factory runs each activity as
one turn behind a versioned API, on a machine of its own, with the agent inside
Herdr. Tickets carry the work through a platform-neutral port: briefs,
handoffs, stories, findings, and the record of each review and proposal. Git
carries the product: code, specification, architecture, and the design text of
each proposal.

The first release answers one question the Factory cannot answer today: how
does one activity hand its work to the next without a human typing the next
command? It runs one project flow with two activities, with the local-file and
GitHub ticket adapters.

## Motivation

The accepted
[Activity-Graph Orchestration proposal](activity-graph-orchestration.md#the-precondition-graph)
answers "what can run now?" from the artifacts on disk. It leaves chaining to
an external orchestrator. The open
[Factory Orchestration proposal](factory-orchestration.md#execution-sequence)
designs that orchestrator as a local Python library. It also designs its own
sandbox with a dedicated operating-system user, mount namespaces, and cgroups.
Queues, retries, and monitoring stay deferred there.

The draft
[External Artifact Sync proposal](external-artifact-sync.md#push-channel-github-action)
copies markdown stories to GitHub Issues after each commit. It keeps the
markdown backlog as the source, so it binds the Factory to one platform.

Two needs remain open:

- **Handover without a human command.** A developer agent finishes ST-0343.
  The code review still waits until a human starts it.
- **One process for every project.** Each project needs its own flow. One
  project needs a QA step after the code review, and another does not.

A working setup already shows how the pieces fit. Patrick's agent setup runs
stories from GitHub issues, schedules them with Windmill, and runs the agents
in Herdr. Its decision record 0011 gives two reasons why Windmill does not run
the agents itself.[^0011] On the community edition of Windmill:

> **Windmill CE costs workarounds**: no error handlers, no job isolation,
> operators per folder through the API.

On Windmill workers next to the agents, which the record rejects:

> **Windmill workers on the factory VM**, which would make the factory a
> Windmill automation in the literal sense. Every worker connects to the
> database, which holds every secret.

The record splits the work between the two sides like this:

> The automation (`f/stories`) decides what a story needs: its states, the
> routing, what the agent is told, and what a run's result means.
>
> The factory knows how to run a turn. It checks every request (the gate),
> prepares the workspace, keeps the run records, and calls two kinds of
> adapters: one per harness, one for the runtime. It holds no story logic.

So the agents run on a separate machine, and Windmill only decides and calls.
This proposal adopts that split (DEC-12).

## Core Principles

- **The activity graph stays the basis.** Eligibility comes from artifacts and
  preconditions. A project flow selects and combines activities. It does not
  replace the graph with a fixed sequence (DEC-04).
- **The human drives unless the flow says otherwise.** The system suggests the
  next eligible activity. It starts that activity on its own only where the
  project flow allows it (DEC-05).
- **Windmill decides, the Factory runs.** The Windmill automation holds the
  routing. The Factory runs one turn per call and holds no routing (DEC-12).
- **The machine is the wall.** Agents run on a machine that holds no platform
  secret. Windmill, its database, and the secrets run on another (DEC-12).
- **One turn runs one activity.** A turn cannot select or start its successor.
- **Git holds the product, the ticket layer holds the work.** Code,
  specification, architecture, and proposal design text live in git. Stories,
  findings, reviews, action items, and each proposal's record live in tickets.
  A ticket points at git by the full 40-character commit SHA (DEC-15).
- **The ticket platform is replaceable.** The Factory speaks only the ticket
  port contract. Each platform has an adapter (DEC-02).
- **The project owns its flows.** A project flow is a copy of a Factory
  default, pinned to the Factory version it came from (DEC-06).

## Design

### Layers

| Layer            | Tool                                | Holds                                                         |
| ---------------- | ----------------------------------- | ------------------------------------------------------------- |
| Automation       | Windmill, on the platform machine   | Triggers, routing by the project flow, retries, and approvals |
| Execution        | Factory service, on its own machine | Request check, workspace, eligibility, fence, and run records |
| Runtime and view | Herdr, on the Factory machine       | The agent's terminal, its state, and the human's takeover     |
| Work             | Ticket port with platform adapters  | Briefs, handoffs, stories, findings, reviews, and approvals   |
| Product          | Git                                 | Code, specification, architecture, and proposal design text   |

### Two machines

The **platform machine** runs Windmill with every automation, the ticket
adapters, the platform credentials, and the backups.

The **Factory machine** runs the Factory service, the agent harnesses with
their model credentials, and the Factory's Herdr server. It is rebuilt from git
and holds nothing that needs a backup.

The two machines meet in two places only: the Factory API, called over SSH from
the platform machine, and git. No Windmill worker runs on the Factory machine,
so no agent shares a machine with the Windmill database. The machines can be
two virtual machines on the same hardware.

### Factory service

The Factory service runs one turn per call. It answers three calls:

| Call       | Input                                                 | Result                                                  |
| ---------- | ----------------------------------------------------- | ------------------------------------------------------- |
| `version`  | none                                                  | The API version                                         |
| `eligible` | Project, workstream, head commit SHA                  | Each activity with its satisfied and unsatisfied inputs |
| `run-turn` | Project, workstream, activity, base commit SHA, brief | Head commit SHA, fence result, run record path          |

Both sides check the API version on every call. A mismatch stops the pipeline
with an error. Neither side carries compatibility code for an older version.

A `run-turn` call runs these steps:

1. Check the request: the activity exists, the base commit exists, and the
   activity's required inputs are satisfied at that commit.
2. Prepare the workspace: a story home on the Factory machine with a worktree
   at the base commit. `verify-base` runs against that worktree.
3. Build the portable envelope from the agent definition and the resolved
   inputs.
4. Start the agent in a Herdr pane through the runtime adapter. The harness
   adapter turns the envelope into the harness's own invocation.
5. Run the output fence against the files the agent created or changed and
   the ticket writes it queued, as [Turn output](#turn-output) describes.
6. If files changed, commit them as one commit on the story branch, and push
   it. Hand the queued ticket writes to the outbox.
7. Write the run record and return the result.

The envelope, the harness adapters, the runtime configuration files, and the
run records keep the shape the Factory Orchestration proposal gives them
([portable envelope](factory-orchestration.md#portable-envelope)). This
proposal replaces the controller loop and the sandbox launcher of that
proposal (DEC-07).

The Factory service holds no routing. It does not read the project flow, and
it does not decide what a turn's result means for the story.

### Herdr as runtime and view

The Factory's Herdr server runs every agent turn. The runtime adapter starts
the agent in a pane, sends the prompt, reads the pane, and reports the turn's
state as working, done, or blocked.

The human runs a Herdr server of their own. It shows the Factory's server as a
saved machine, reached over SSH. So the human sees the Factory's turns and
their own sessions in one sidebar. The human takes a turn over by hand with
`/takeover` on the ticket, and the automation stops routing that story until
the human hands it back.

Herdr has misread Claude Code's first-start screens in earlier versions, in
both directions. So the runtime adapter reads the pane before it sends the
prompt, and it stops with `blocked` if a first-start screen shows.

### Triggers

The platform machine has no public port, so the ticket adapters poll the
platform instead of taking webhooks. A Windmill schedule runs each poll.

An activity starts from one of two triggers.

- **Message trigger.** A brief or a handoff arrives in the ticket inbox. It
  names the activity, the workstream, and the base commit. The automation
  calls `run-turn` for that activity.
- **Artifact trigger.** A turn returns its head commit. The automation calls
  `eligible` at that commit. For each eligible activity, the project flow
  decides what happens next.

The project flow marks each transition between two activities as `auto` or
`suggest`:

- `auto`: the automation calls `run-turn` for the next activity as soon as the
  fence of the previous turn passes.
- `suggest`: the automation posts the eligible activity to the ticket. It calls
  `run-turn` only after an `approval-given` event.

A failed fence never starts a successor. The automation posts the failure to
the ticket, and the human decides what happens.

### Project flows

A project flow names the activities a project uses for one kind of work, the
transitions between them, and the states it reports. It lives in the project at
`.agent-factory/flows/<flow-name>.yaml`. The Windmill automation reads it from
git at the workstream's head commit.

```yaml
---
flow: feature-addition
pinned_from:
  factory_version: 1.4.0
  source: packages/factory/flows/feature-addition.yaml
activities:
  - agent: developer-agent
  - agent: code-review-agent
  - agent: qa-agent
transitions:
  - from: developer-agent
    to: code-review-agent
    mode: auto
  - from: code-review-agent
    to: qa-agent
    mode: suggest
    when: verdict == pass
states:
  in-progress: developer-agent running or eligible
  review: code-review-agent running or eligible
  qa: qa-agent running or eligible
  done: qa-agent fence passed with verdict pass
```

The Factory ships one default flow per playbook. A project copies a default
flow into `.agent-factory/flows/` and changes the copy. `update-factory` never
changes a project flow. It compares the pinned version with the current
default and reports each upstream change. The human merges those changes by
hand.

A transition only orders activities that the activity graph already allows.
The automation cannot start an activity whose required inputs are
unsatisfied, because `run-turn` checks them first. When a review sends a story
back, the developer activity becomes eligible again through its own
preconditions. The flow needs no back edge for that.

### Ticket port

The Factory speaks to every ticket platform through one contract. An adapter
translates the contract into one platform's API. The adapters run on the
platform machine, next to the platform credentials.

**Identity.** Each item has a Factory ID that never changes, such as
`ST-0343`. The adapter stores the platform ID beside it, such as GitHub `#812`
or Jira `FAC-812`. The Factory never uses a platform ID as a key. When the adapter
creates an item, it gets the Factory ID from `next-id`, as the
[Counter IDs proposal](counter-ids.md#the-script-next-id) defines. So every
ticket adapter and every CLI session draw from the same counter (DEC-08). The platform
machine has no clone, so the adapter passes the project's remote with
`next-id --remote <url>`.

**Hierarchy.** Each item has a kind: `epic`, `story`, `subtask`, `proposal`,
`review`, `finding`, or `action`. The kind decides the allowed parent:

| Kind       | Allowed parent        |
| ---------- | --------------------- |
| `epic`     | none                  |
| `story`    | `epic`                |
| `subtask`  | `story`               |
| `proposal` | none                  |
| `review`   | `story` or `proposal` |
| `finding`  | `review`              |
| `action`   | `review` or none      |

So no chain is deeper than three levels. The adapter maps each kind to a
platform item type or label, for example a GitHub label or a Jira issue type.
It rejects an item whose parent the table does not allow (DEC-19).

Take the code review of ST-0350. It is a `review` item under the story, and
its finding IMPL-0004 is a `finding` item under the review. The review item
holds the passes table and the verdict. A retrospective is a `review` item
with no story, and each of its action items is an `action` item.

**Outbox.** The automation sends five kinds of message:

| Message        | Carries                                                   |
| -------------- | --------------------------------------------------------- |
| `create-item`  | Kind, parent, title, body                                 |
| `post-brief`   | Activity, workstream, base commit SHA, brief text         |
| `post-handoff` | From activity, to activity, head commit SHA, handoff text |
| `change-state` | Flow state                                                |
| `link-commit`  | Commit SHA, changed paths, fence result                   |

Each message carries an idempotency key. A repeated message with the same key
changes nothing, so a Windmill retry never creates a second item.

**Inbox.** The adapter turns platform changes into five Factory events:
`brief-received`, `handoff-received`, `approval-given`, `takeover`, and
`state-changed`. The automation reacts to these Factory events only, never to
raw platform data.

**State mapping.** Each project keeps one mapping file per platform at
`.agent-factory/ticketing/<platform>.yaml`. It maps each flow state to a
platform state, for example `review` to the Jira state `Code Review` or to the
GitHub label `in-review`. If the project moves to another platform, only the
mapping file changes.

**Content.** The ticket layer holds the work (DEC-15):

- **A story** is one ticket with its whole body and fields, including the
  fields that `story-gates` and the step manifests read. A contract decision
  that must outlive the story goes into the specification during
  make-concrete.
- **A proposal** keeps its design text in git. Its status, Decisions table,
  review findings, and review passes are items of the proposal's ticket. When
  the proposal is accepted, the ticket records the commit SHA of the design
  text.
- **A finding** is a `finding` item with the fields of
  [finding-classification.md](finding-classification.md). The register of
  `minor` findings is a list of `finding` items (DEC-16).
- **A review** is a `review` item that holds the passes table of
  [review-loop-cap.md](review-loop-cap.md) and the verdict. Quality scenarios
  and risk themes from an ATAM review describe the product, so they go into
  arc42 chapters 10 and 11 in git (DEC-17).

A ticket links to git by the full commit SHA and the path.

**Read.** The port also answers two queries: `get-item` returns one item by
its Factory ID, and `list-items` returns the children of an item, filtered by
kind. `story-gates`, `finding-lint`, and `review-pass-check` read through these
queries, so they work the same under every adapter (DEC-20).

**Adapters.** The first release ships two adapters:

- The local-file adapter keeps items as markdown files in git: stories under
  `backlog/`, findings under `docs/findings/`, review documents under
  `docs/reviews/`, and a proposal's record in the Appendix of the proposal
  file. These are the places that finding-classification.md and
  review-loop-cap.md name. The adapter serves manual mode, projects without a
  ticket platform, and the tests.
- The GitHub adapter uses GitHub Issues, sub-issues, and labels.

Jira and Azure DevOps adapters follow the same contract. The first release
checks the contract against their item models on paper, without building the
adapters.

### Turn output

A turn writes to two places. File changes go into one commit on the story
branch. Ticket writes go out as outbox messages. A turn that changes no file
makes no commit (DEC-18).

The agent declares both kinds of output. The fence checks the commit diff
against the declared paths and the outbox messages against the declared ticket
writes. A path or a ticket write outside the declaration fails the fence. Take
the code review of ST-0350 under the GitHub adapter. It changes no file and
sends one `create-item` for IMPL-0004, so the fence checks that message against
the declaration.

The run record lists the commit SHA and every outbox message of the turn. It
stays on the Factory machine under `.current-work/invocations/` and is not
committed.

### Merges

Only the human merges a story branch. The last activity of a flow runs
`premerge-check` inside its turn and links the result to the ticket. The human
reads the result and merges on the platform.

## Scope

**In the first release:**

- Step 0: check each Windmill and Herdr feature the design relies on against
  the versions the first release runs, and record each result with its version
  and date.
- The Factory service with the `version`, `eligible`, and `run-turn` calls, and
  the API version check on both sides.
- The Herdr runtime adapter, with the pane check before the prompt.
- One harness adapter, the one the fixture needs.
- The Windmill automation: message triggers, artifact triggers, `auto` and
  `suggest` transitions, and `takeover`.
- The project flow format, one default flow (`feature-addition`), and the
  `update-factory` report of upstream changes for pinned flows.
- The ticket port contract: identity, item kinds and their parents, outbox,
  inbox, the `get-item` and `list-items` queries, state mapping, and
  idempotency keys.
- The local-file adapter and the GitHub adapter.
- A paper check of the contract against the Jira and Azure DevOps item models.
- The fence check of the commit diff and the outbox messages against the
  declared outputs.
- A fixture that runs developer-agent and code-review-agent on one story
  through the whole loop, on two machines.

**Explicitly deferred (do NOT plan stories for these):**

- Jira and Azure DevOps adapters. The contract must prove itself with two
  adapters before more are built.
- Overlay flows that store only a project's changes to a default. Pinned
  copies cover the first release. Overlays pay off only when many projects
  make the same small change.
- More harness adapters than the one the fixture needs. The Factory
  Orchestration property matrix decides which harnesses come next.
- A separate operating-system user per harness on the Factory machine. The
  machine boundary is the wall for the first release.
- Automatic selection between several eligible activities without a flow
  transition. The human chooses in that case.

## Design Details

**Idempotency key.** The key is the workstream ID, the activity, the base
commit SHA, and the message kind, joined by `:`. A retry of the same call sends
the same key.

**Failure.** A failed turn keeps its story home, its branch, and its run
record. The automation retries a `run-turn` call only when the Factory API did
not answer. A failed fence is a result, not an error, so the automation never
retries it.

**Prerequisite.** The Counter IDs proposal ships before this release, because
both adapters call `next-id`.

**Credentials.** The Factory machine holds the model credentials and one
platform token per turn, valid for that turn's repository only. The platform
credentials and the Windmill database never reach it.

**Manual mode.** In manual mode, neither machine is needed. The human runs
activities in the CLI as today, and the local-file adapter keeps the tickets
as files in git. So manual mode keeps today's files for stories, findings, and
review documents.

**Superseded proposals.** This proposal supersedes the Factory Orchestration
proposal and the External Artifact Sync proposal. It carries forward the
envelope, adapter, and run record designs of the former, and its open
isolation findings A12, A13, and A15 (DEC-07, DEC-09).

## Open Questions

- **Approvals across tools.** A human can approve a `suggest` transition on
  the ticket or in the Windmill UI. Does the first approval win, or does the
  project pick one place? The ticket is the likely answer, because the human
  already steers there.
- **Per-turn token for other platforms.** GitHub can issue a token for one
  repository that is valid for an hour. Jira and Azure DevOps may not offer the
  same scope. The paper check must say what each platform allows, and what the
  Factory machine holds where it does not.

## Completion Criteria

- Step 0 produces a written check for each Windmill and Herdr feature named in
  the Design, with the version, the date, and the result "works as
  described", "works differently", or "missing".
- A commit by developer-agent on the fixture story starts code-review-agent
  through an `auto` transition, with no human command.
- A `suggest` transition posts the eligible activity to the ticket and calls
  `run-turn` only after an `approval-given` event.
- A `takeover` event stops the automation from routing the story until the
  human hands it back.
- A turn whose commit diff contains a path outside the agent's declared outputs
  fails its fence, and no successor starts. A turn that sends a ticket write
  outside its declared outputs fails the same way.
- A review turn that changes no file makes no commit. Its finding is a
  `finding` item under the review's ticket on GitHub, and a file under
  `docs/findings/` with the local-file adapter.
- The adapter rejects an item whose kind does not allow its parent, for
  example a `finding` directly under a `story`.
- `finding-lint` reads the same finding through `get-item` under both
  adapters and computes the same severity.
- An agent process on the Factory machine has no network route to the Windmill
  database and no file that holds a platform credential.
- A Factory API version mismatch stops the automation with an error that names
  both versions.
- The same outbox message sent twice creates one ticket item.
- The fixture runs once with the local-file adapter and once with the GitHub
  adapter, and the flow file stays unchanged between the two runs.
- The local-file adapter and the GitHub adapter each take the Factory ID of a
  new item from `next-id`.
- `update-factory` reports an upstream change to the default
  `feature-addition` flow and leaves the project's pinned copy unchanged.
- The paper check lists, for Jira and Azure DevOps, how each contract level,
  message, and event maps to the platform, and names every gap.

## Guiding Rule

The graph says what can run, the project flow says what runs next, the Factory
runs it, git holds the product, and the ticket holds the work.

# Appendix

## Decisions

| ID     | Date       | Kind       | Decided by     | Decision                                                                                                                                                                                                                                                  | Raised by                              |
| ------ | ---------- | ---------- | -------------- | --------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- | -------------------------------------- |
| DEC-01 | 2026-11-03 | decision   | Matthias Daues | Herdr is the presentation and interaction layer. Windmill is the automation layer. Where Windmill runs the agents is replaced by DEC-12.                                                                                                                  | Open Stage conversation                |
| DEC-02 | 2026-11-03 | decision   | Matthias Daues | The ticket platform sits behind a port with stable outbox and inbox contracts. GitHub, Jira, and Azure DevOps each get an adapter. The markdown backlog stays as the local-file adapter.                                                                  | Open Stage conversation                |
| DEC-03 | 2026-11-03 | decision   | Matthias Daues | Tickets hold text and links only. Every artifact lives in git, referenced by its full commit SHA. The commit diff is the container of an activity's artifacts. Replaced by DEC-15.                                                                        | Open Stage conversation                |
| DEC-04 | 2026-11-03 | decision   | Matthias Daues | The accepted activity graph is the basis. Project flows combine agents on top of it and do not replace it with a fixed sequence.                                                                                                                          | Overlap with existing proposals        |
| DEC-05 | 2026-11-03 | decision   | Matthias Daues | A job starts from a brief or handoff, or from satisfied required artifacts. The approach is consultative: the system suggests, the human approves.                                                                                                        | Overlap with existing proposals        |
| DEC-06 | 2026-11-03 | decision   | Matthias Daues | A project owns full copies of its flows, pinned to the Factory version. `update-factory` reports upstream changes and the human merges them.                                                                                                              | Playbook storage question              |
| DEC-07 | 2026-11-03 | assumption | Matthias Daues | This proposal supersedes the Factory Orchestration proposal. It keeps its envelope, adapters, and run records, and replaces its controller loop and sandbox launcher.                                                                                     | Overlap with existing proposals        |
| DEC-08 | 2026-11-04 | decision   | Matthias Daues | Every ticket adapter gets each Factory ID from `next-id`. The Counter IDs proposal stays separate and ships first, as a prerequisite.                                                                                                                     | Overlap with `counter-ids.md`          |
| DEC-09 | 2026-11-03 | assumption | Matthias Daues | This proposal supersedes the External Artifact Sync proposal, because the ticket platform, not the markdown backlog, becomes the home of tickets.                                                                                                         | Overlap with existing proposals        |
| DEC-10 | 2026-11-03 | assumption | Matthias Daues | Project flows mark each transition `auto` or `suggest`. Only `auto` starts a turn without a human approval.                                                                                                                                               | Consultative approach (DEC-05)         |
| DEC-11 | 2026-11-03 | assumption | Matthias Daues | Each turn ends with exactly one commit, and a review verdict is a committed file. Replaced by DEC-18.                                                                                                                                                     | Artifact container (DEC-03)            |
| DEC-12 | 2026-11-03 | decision   | Matthias Daues | The setup follows PatrickPT/context decision 0011: Windmill decides and calls, a thin Factory service runs each turn on its own machine with the agent in Herdr, and the machine is the wall.                                                             | Review of `../context`                 |
| DEC-13 | 2026-11-03 | assumption | Matthias Daues | Only the human merges. The last activity of a flow runs `premerge-check` and links the result to the ticket.                                                                                                                                              | Open question on merges                |
| DEC-14 | 2026-11-03 | assumption | Matthias Daues | The ticket adapters poll the platform, because the platform machine has no public port.                                                                                                                                                                   | Review of `../context`                 |
| DEC-15 | 2026-11-05 | decision   | Matthias Daues | Git holds the product: code, specification, architecture, and proposal design text. The ticket layer holds the work: whole stories and each proposal's record of status, decisions, review findings, and passes. Replaces DEC-03.                         | Manual-mode-gates grilling, 2026-11-03 |
| DEC-16 | 2026-11-05 | decision   | Matthias Daues | A review finding is a ticket item, and the register of `minor` findings is a list of items. The local-file adapter keeps both as today's files.                                                                                                           | Manual-mode-gates grilling, 2026-11-03 |
| DEC-17 | 2026-11-05 | decision   | Matthias Daues | Review documents split by content. The passes table, the verdict, and the findings go to the review's ticket; a retrospective goes to the ticket layer with one item per action. ATAM quality scenarios and risk themes go into arc42 chapters 10 and 11. | Manual-mode-gates grilling, 2026-11-03 |
| DEC-18 | 2026-11-05 | decision   | Matthias Daues | A turn commits only when it changed files. Its ticket writes go out as outbox messages, and the fence checks both against the declared outputs. Replaces DEC-11.                                                                                          | Turn output after DEC-15               |
| DEC-19 | 2026-11-05 | decision   | Matthias Daues | Each ticket item carries a kind: epic, story, subtask, proposal, review, finding, or action. The kind decides the allowed parent, and no chain is deeper than three levels.                                                                               | Hierarchy after DEC-16                 |
| DEC-20 | 2026-11-05 | assumption | Matthias Daues | The port answers the queries `get-item` and `list-items`, so `story-gates`, `finding-lint`, and `review-pass-check` read the same way under every adapter.                                                                                                | Readers of findings after DEC-16       |

## Review findings

| ID  | Pass | Severity | Check | Status | Finding | Resolution |
| --- | ---- | -------- | ----- | ------ | ------- | ---------- |

## Review passes

| Pass | Date | Reviewed commit | Disposition | Failed checks | Summary |
| ---- | ---- | --------------- | ----------- | ------------- | ------- |

[^0011]: Decision record "0011: Windmill stays; the factory gets a VM of its
    own and becomes a thin service", dated 2026-10-30, in the private repository
    `PatrickPT/context`, quoted verbatim from commit
    `e8ecbb42f98debd8ca4c5bfa5a2643cb108e3c6f`. Source URL:
    `https://github.com/PatrickPT/context/blob/main/decisions/0011-two-vms-thin-factory.md`.
