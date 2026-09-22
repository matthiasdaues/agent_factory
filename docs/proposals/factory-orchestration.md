---
schema_version: 2
title: Factory Orchestration
status: open
owner: Matthias Daues
created: 2026-09-21
updated: 2026-09-22
supersedes: docs/proposals/agent-execution-isolation-and-distribution.md

impact:
  scope: cross_component
  architecture_change: true
  external_contract_change: true
  boundaries:
    - packages/factory/engine/
    - packages/factory/agents/
    - packages/factory/config/
    - packages/factory/scripts/
    - .agent-factory/factory/scripts/init-factory
    - .agent-factory/factory/config/hooks/block-dangerous-git.sh
    - .agent-factory/factory/scripts/commit-safe
    - .agent-factory/factory/scripts/verify-base
    - .agent-factory/factory/scripts/premerge-check
    - docs/arc42/architecture.dsl

governance:
  assurance: high
  risk_domains:
    - security
    - reliability
    - operations

estimate:
  as_of: 2026-09-22
  basis: judgment
  confidence: low
  human_review_hours: unknown
  normalized_tokens: unknown
  estimated_consumption: unknown
---

# Feature Request: Factory Orchestration

## Summary

Build a CLI-agnostic orchestration layer that invokes one Factory activity at a
time through any supported runtime, validates its output with the existing
fence, and records the result as an immutable invocation record. The
orchestrator builds on the existing Eligibility Engine (`eligibility.py`) and
output fence (`fence.py`). It does not replace them.

This proposal absorbs the execution isolation concern from the
[Agent Execution Isolation proposal](agent-execution-isolation-and-distribution.md).
The orchestrator owns both the invocation path and the sandbox that confines it.

The first release delivers a property matrix across seven runtimes, a minimal
envelope schema, runtime configuration files, and one working adapter for
OpenCode — exercised with a developer-plus-reviewer fixture that proves the
full invocation loop.

## Motivation

The accepted
[Activity-Graph Orchestration proposal](activity-graph-orchestration.md#from-stages-to-preconditions)
built the precondition graph, the Eligibility Engine, and the output fence.
These components report which activities can run and validate what they
produce. Execution still depends on a human typing commands inside a CLI
session.

The Factory supports seven command-line interfaces: Claude Code, OpenCode,
Hermes Agent, Agent Zero, Pi, Codex, and Copilot. Each has a different way to
accept instructions, select a model, and report results. A human who switches
between CLIs must know each one's invocation surface.

This proposal adds the layer between "what can run" and "run it":

- The Eligibility Engine reports which activities can run.
- A human selects which activity to run.
- The orchestrator builds a portable envelope, translates it through a
  runtime-specific adapter, invokes the runtime, and validates the result
  with the fence.

The orchestrator must be CLI-agnostic. Adding a new runtime means writing a
configuration file and a thin adapter — not redesigning the invocation path.

The superseded
[Agent Execution Isolation proposal](agent-execution-isolation-and-distribution.md)
designed sandbox execution under a dedicated operating-system identity with
filesystem delegation, mount namespaces, and cgroup confinement. That design
belongs here because the orchestrator's launcher constructs the sandbox before
invoking the runtime. Isolation is not a separate system — it is the
orchestrator's execution environment.

## Core Principles

- **Eligibility is not routing.** The dependency graph answers "what can run
  now?" It does not answer "what should run next?"
- **One invocation runs one activity.** An execution node cannot select or
  invoke its successor.
- **The orchestrator owns execution settings.** It builds the envelope, selects
  the adapter, and invokes the runtime.
- **The agent owns the bounded task.** It follows its instructions and produces
  its declared deliverables from its required inputs.
- **Review is an activity.** A reviewer has its own `inputs.required`,
  instructions, and `outputs`. The orchestrator does not treat review as a
  privileged control path.
- **Factory contracts remain authoritative.** External runtimes execute an
  activity. They do not replace eligibility checks, output fences, or Factory
  policy.
- **Runtime-native delegation stays disabled.** The orchestrator does not let a
  model choose subagents or extend the activity graph.
- **CLI-agnostic by design.** The portable envelope speaks in logical,
  runtime-neutral terms. Each adapter translates to runtime-specific calls.
- **Isolation wraps execution.** The launcher constructs the sandbox before the
  runtime starts. The runtime runs inside it. The fence runs after it.

## Design

### Vision layers

The full capability stack, from what exists today to the end state:

| Layer | Capability                                                               | Status                 |
| ----- | ------------------------------------------------------------------------ | ---------------------- |
| 0     | Eligibility engine, output fence, agent definitions, `intent select`     | Exists                 |
| 1     | Property matrix across seven runtimes                                    | First release (step 0) |
| 2     | Envelope schema, adapter result schema, runtime config format            | First release          |
| 3     | Library core, one working adapter (OpenCode), invocation records         | First release          |
| 4     | Author-reviewer fixture proving the full invocation loop                 | First release          |
| 5     | Execution isolation (launcher, sandbox, dedicated UID, mount namespace)  | Second release         |
| 6     | Additional adapters for viable runtimes from the matrix                  | After layer 5          |
| 7     | Automatic selection policies (no human in the loop)                      | Deferred               |
| 8     | Production operations (retry, monitoring, queues, distributed execution) | Deferred               |

Layer 5 can be built independently of layers 3 and 4. It wraps around whatever
the adapter produces. Layers 7 and 8 are outside this proposal's scope.

### Eligibility protocol

The Eligibility Engine already derives a dependency graph from
`inputs.required` and `outputs` across agent definitions. For a bound
workstream, it returns each activity with resolved evidence for every required
input. This proposal builds on that — it does not modify the engine's contract.

The orchestrator calls the engine, presents eligible activities to the human,
and accepts a selection. If the human cannot select exactly one activity,
execution stops.

### Portable envelope

The orchestrator creates one immutable invocation envelope for the selected
activity. The envelope carries logical, runtime-neutral values. The adapter
translates each value into runtime-specific form.

Portable fields (every adapter must handle these):

- **Invocation ID** — unique identifier for this execution.
- **Workstream ID** — which workstream this belongs to.
- **Agent definition** — the full instruction set, with content hash.
- **Resolved inputs** — file paths the agent needs to read.
- **Declared outputs** — file paths the fence will check.
- **Model tier** — logical tier (`strong`, `standard`, `economy`). The adapter
  maps it to a runtime-specific model ID through the runtime configuration
  file.
- **Token limit** — maximum tokens the runtime may consume. The adapter
  translates to whatever mechanism the runtime provides, or reports the gap.

Fields that move to portable when the property matrix confirms broad support:

- **Wall-clock timeout** — maximum execution time.
- **Tool restrictions** — which tools the agent may use.

Extension fields (adapter-specific, not in the portable contract):

- Provider routing, approval behavior, process exit format, secret references,
  sandbox configuration.

The Factory's instructions must arrive at the runtime complete and unmodified.
Runtimes may add their own system text around them. The adapter documents what
the runtime added as evidence in the invocation record.

### Runtime configuration

Each supported CLI has a configuration file at
`packages/factory/config/runtimes/<cli-name>.yaml`. The file maps logical
envelope values to runtime-specific equivalents: model tier to model ID (as
`model.conf` does today for models alone), tool names to runtime tool names,
limit flags, instruction delivery mechanism, and capability declarations.

The adapter reads its configuration file and translates the envelope. A new
runtime requires a new configuration file and a thin adapter class.

### Adapter interface

Each adapter implements a single blocking call:

```python
result = adapter.invoke(envelope) -> AdapterResult
```

The adapter translates the envelope into runtime-specific calls, starts the
runtime, waits for it to exit, and returns a normalized result. The adapter
cannot alter the selected agent, grant extra tools, choose another activity,
or declare an invalid output valid.

The `AdapterResult` carries: exit status, files changed, token usage (when the
runtime reports it), wall-clock duration, and any runtime-added system text.

### Execution sequence

One invocation follows this sequence:

01. Evaluate `inputs.required` for the bound workstream (Eligibility Engine).
02. Present eligible activities. Human selects one.
03. Resolve every input. Build the portable envelope.
04. Write the immutable envelope to the invocation record.
05. Call `adapter.invoke(envelope)`.
06. Wait for the adapter to return.
07. Run the Factory output fence against declared outputs.
08. Write the adapter result and fence evidence to the invocation record.
09. If the fence fails, stop and report. The human decides what to do.
10. If the fence passes, recompute eligibility and present the next eligible
    set. The human selects or stops.

### Invocation records

Each invocation produces one file at:

```
.current-work/invocations/<timestamp>-<workstream>-<agent>-<short-id>.yaml
```

Example:

```
.current-work/invocations/2026-09-22T1430-factory-orchestration-developer-agent-a1b2c3d4.yaml
```

The file contains the envelope, the adapter result, and the fence evidence.
It is the complete audit record for one execution.

### Reviewer activities

A reviewer consumes the author's deliverables through its own
`inputs.required` declaration. It produces findings or a structured verdict
through its own `outputs` declaration. The orchestrator treats it like any
other activity — same envelope, same adapter, same fence.

The human may choose to run a reviewer after an author activity. That decision
is the human's. The author cannot invoke its own reviewer, and the reviewer
cannot start remediation work.

### Controller shape

The orchestrator is a Python library at `packages/factory/engine/`. It exposes:

- Envelope builder (reads agent definition, resolves inputs, builds the
  portable envelope).
- Adapter registry (loads the right adapter for the selected runtime).
- Invocation runner (calls the adapter, runs the fence, writes the record).

A thin CLI command at `packages/factory/scripts/orchestrate` wraps the library.
The human runs the command, picks an activity, and watches the result.

### Property matrix

Before building any adapter, the project fills a property matrix documenting
what each of the seven runtimes can express. The matrix is the research
deliverable (step 0).

Runtimes:

1. Claude Code
2. OpenCode
3. Hermes Agent
4. Agent Zero
5. Pi
6. Codex
7. Copilot

Properties:

| Property             | What it answers                                                              |
| -------------------- | ---------------------------------------------------------------------------- |
| Instruction delivery | Can the runtime accept a complete agent definition and system prompt?        |
| Model selection      | Can the runtime use a specific model the envelope names?                     |
| Tool restriction     | Can the runtime limit which tools the agent may use?                         |
| File read boundary   | Can the runtime restrict which files the agent reads?                        |
| File write boundary  | Can the runtime restrict which files the agent writes?                       |
| Network access       | Can the runtime control whether the agent reaches the internet?              |
| Process isolation    | Does the runtime run the agent in a sandbox, container, or separate process? |
| Token limits         | Can the runtime enforce a token budget?                                      |
| Wall-clock timeout   | Can the runtime enforce a time limit?                                        |
| Exit reporting       | Does the runtime report success/failure and why?                             |
| Usage evidence       | Does the runtime report tokens consumed, model used, and duration?           |
| Subagent control     | Can the runtime prevent the agent from spawning subagents?                   |
| Reproducibility      | Given the same envelope, does the runtime produce a comparable execution?    |

Each cell records: supported / partially supported / not available, with
evidence from the runtime's documentation or a test run. The matrix determines
which runtimes are viable adapter targets and which envelope fields are broadly
portable.

Where the orchestrator's launcher provides container or sandbox isolation
(layer 5), the runtime does not need to enforce file boundaries, network
access, or process isolation natively. The matrix still records the runtime's
native capability so the project can assess defense-in-depth and choose whether
to rely on the launcher alone or layer runtime-native controls on top.

### Execution isolation

This proposal absorbs the execution isolation design from the
[Agent Execution Isolation proposal](agent-execution-isolation-and-distribution.md).
The full design, threat model, alternatives analysis, acceptance proof, and
review history remain in that document as the audit trail. This section
summarizes the design decisions this proposal owns.

**Core design:** Run agent processes under a dedicated, unprivileged
operating-system UID (`agent-factory`). Grant that UID access only to declared
project paths through filesystem ownership, POSIX ACLs, and mount permissions.
Remove every supported route to escalate privileges.

**Launcher:** A root-owned launcher constructs a private mount namespace,
drops capabilities and supplementary groups, changes to the agent UID, enables
`no-new-privileges`, denies user and mount namespace creation, and starts the
runtime inside the resulting sandbox. The launcher creates a per-session cgroup
the agent cannot leave. Namespace construction and mount locking precede the
UID transition.

**Delegation policy:** A human-controlled YAML file outside delegated paths
declares which project paths the agent may access and at which mode
(read-only or read-write). Each grant is a separate bind mount. No common
parent is implied. The launcher validates every path, rejects unsafe
ownership, and fails closed on any violation.

**Profiles:**

- Host-native (first release of isolation): dedicated UID, ACLs, private mount
  namespace, cgroup confinement.
- Containerized (deferred): versioned OCI image consuming the same delegation
  policy. Deferred until a runtime is evidenced that satisfies the identity
  model without subordinate UID/GID ranges.

**Git and publication:** Existing guardrails (`block-dangerous-git.sh`,
`commit-safe`, `verify-base`, `premerge-check`) remain active. They are
accident prevention, not security boundaries. A future privileged orchestrator
capability will mediate protected Git mutations. No release may demote a
control unless the same release ships its replacement.

**Network:** Two postures — `standard` (unrestricted, required for model
provider access) and `deny` (blocked, for offline gates). The orchestrator
confines filesystem access, not disclosure: readable content can leave through
the provider channel.

**Carried open findings from the superseded proposal:**

| ID  | Finding                                                                               | Status                                                 |
| --- | ------------------------------------------------------------------------------------- | ------------------------------------------------------ |
| A12 | Full predecessor-finding carry-forward register required before acceptance            | Open                                                   |
| A13 | Alternatives analysis (Pugh matrix) required before acceptance; survived four reviews | Open — proposed matrix included in superseded proposal |
| A15 | Release estimate remains unknown until decomposition                                  | Open                                                   |
| —   | Provider-credential provisioning to the dedicated identity                            | Open                                                   |
| —   | Deferred containerized profile prerequisites                                          | Deferred                                               |
| —   | Future orchestrator Git authorization protocol                                        | Deferred to separate proposal                          |

### Test fixture

The prototype exercises a developer-plus-code-reviewer pair on a small,
self-contained task. The developer agent writes a small piece of code. The code
reviewer reviews it. Both run through the OpenCode adapter.

The fixture proves:

- The envelope is sufficient to drive a real activity.
- The adapter translates the envelope into a working OpenCode call.
- The fence validates the developer's deliverables.
- Eligibility recomputation connects the first invocation to the second.
- The reviewer runs from its own `inputs.required` as a separate invocation.
- Both invocation records capture complete evidence.

### Relationship to other proposals

The accepted
[OpenCode CLI Integration proposal](opencode-cli-integration.md) addresses
OpenCode as an interactive host — a human works inside OpenCode and the Factory
runs within it. This proposal uses OpenCode as a programmatic runtime the
Factory's controller calls from outside. Both integrations are independent.

The
[Hermes Host Adapter proposal](hermes-host-adapter.md) addresses Hermes as an
interactive host. This proposal's property matrix covers Hermes as a
programmatic runtime. Both integrations are independent.

## Scope

**Step 0 — Research (all seven runtimes):**

- Fill the property matrix from official documentation and, where necessary,
  test runs.
- Record each cell with evidence (documentation URL, test result, or "not
  documented").
- Identify which runtimes are viable adapter targets.
- Identify which envelope fields are broadly portable.

**First release — OpenCode adapter (layers 2 through 4):**

- Define the minimal portable envelope schema (JSON Schema).
- Define the adapter result schema.
- Create runtime configuration files for OpenCode.
- Build the orchestration library (`packages/factory/engine/`): envelope
  builder, adapter interface, OpenCode adapter, invocation recorder.
- Build the CLI command (`packages/factory/scripts/orchestrate`).
- Wire the adapter to the existing output fence.
- Run the developer-plus-reviewer fixture through OpenCode.
- Write invocation records for both activities.

**Second release — Execution isolation (layer 5):**

- Implement the host-native isolation profile: dedicated UID, ACLs, mount
  namespace, cgroup confinement, launcher.
- Resolve the carried open findings from the absorbed isolation proposal.
- The launcher wraps the adapter call — the adapter runs inside the sandbox.

**Third release — Additional adapters (layer 6):**

- Build adapters for viable runtimes identified by the property matrix.
- Create runtime configuration files for each.
- Run the same fixture through each adapter.

**Explicitly deferred (do NOT plan stories for these):**

- Automatic selection policies. Selection is the human's job in this proposal.
- Production operations: retry policies, monitoring, queues, daemon,
  distributed execution.
- Containerized isolation profile. Deferred until a runtime satisfies the
  identity model without subordinate UID/GID ranges.
- Privileged Git authorization and publication. Requires a separate proposal.
- Changes to the activity graph or agent input/output schema unless the
  prototype shows a concrete incompatibility.
- Runtime-native multi-agent delegation. That would move selection into an
  execution node.

## Design Details

### Envelope translation

The portable envelope carries logical values. The adapter translates them using
the runtime configuration file. Example:

The envelope says `model: strong`. The OpenCode configuration file maps
`strong` to the OpenCode-specific model ID. The adapter reads the mapping and
passes the translated value to the runtime.

The same pattern applies to tool names, limit mechanisms, and instruction
delivery format. The runtime configuration file is the dictionary. The adapter
is the translator. The property matrix documents what each adapter can and
cannot translate.

### Failure handling

If the fence rejects an activity's output, the controller stops and reports the
failure to the human. No automatic retry. The human decides: re-run, fix
manually, or abandon. Each retry is a new invocation with a new ID and a fresh
eligibility evaluation.

### Agent completion text

Agent completion text is diagnostic, not authoritative. Declared file
deliverables and fence results determine success. A reviewer verdict is a
deliverable only when its agent definition declares the verdict artifact and a
deterministic validator accepts its structure.

## Open Questions

No open questions block the research or the first release.

The following questions are prerequisites for the second release (execution
isolation) and must be resolved before its stories are planned:

- How are provider credentials provisioned to the dedicated execution identity
  without exposing unrelated credential stores? Carried from the absorbed
  isolation proposal; never resolved across four review rounds.
- What is the minimum set of acceptance proof cases for the host-native
  isolation profile? The superseded proposal carries a 30+ row matrix. This
  proposal must confirm which cases still apply given the absorbed scope.

## Completion Criteria

### Step 0 — Research

- The property matrix covers all thirteen properties across all seven runtimes.
- Each cell has documented evidence.
- A written summary identifies viable adapter targets and broadly portable
  envelope fields.

### First release — OpenCode adapter

- A JSON Schema validates the portable envelope and rejects any call that omits
  a required field.
- A JSON Schema validates the adapter result.
- The OpenCode runtime configuration file maps all portable fields to
  OpenCode-specific values.
- The orchestration library builds an envelope from an agent definition and
  resolved inputs.
- The OpenCode adapter translates the envelope into an OpenCode call and
  returns a normalized result.
- The output fence validates the developer activity's deliverables and records
  its result against the invocation ID.
- Eligibility is recomputed after the developer invocation without starting the
  reviewer automatically.
- A separate human decision invokes the reviewer from its own required inputs.
- The reviewer's deliverables pass the fence.
- Both invocations produce complete invocation record files with the agreed
  naming scheme.
- The developer activity cannot invoke another Factory agent through a native
  OpenCode subagent mechanism.

### Second release — Execution isolation

- The host-native isolation profile passes the acceptance proof from the
  absorbed isolation proposal.
- Agent processes run under a dedicated UID with no supported escalation path.
- Filesystem access is confined to declared grants through ACLs and mount
  namespace.
- Each session runs in a launcher-owned cgroup the agent cannot leave.
- Existing Git guardrails remain active.
- A per-invocation audit record is written outside delegated paths.
- The carried open findings (A12, A13, A15, credential provisioning) are
  resolved or explicitly re-deferred with rationale.

### Third release — Additional adapters

- Each viable runtime from the property matrix has an adapter that passes the
  developer-plus-reviewer fixture.
- Each adapter has a runtime configuration file.
- Unsupported envelope fields are documented as known limitations per adapter.

## Guiding Rule

The graph reports what can run; the controller decides what will run; the node
runs only itself.

## Review — 2026-09-22

Reviewer: proposal-review-agent
Reviewed commit: 5e74401d5cff8211f5b8dd49f18b2b6ab50ed6ba
Disposition: findings

### Findings

| ID      | Severity | Check | Status | Finding                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                      |
| ------- | -------- | ----- | ------ | ---------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| PROP-01 | major    | 04    | open   | Governance downgraded from `critical` to `high` when absorbing the isolation concern. The superseded proposal declares `governance.assurance: critical` with `risk_domains` including `privacy` and `data_integrity`. This proposal declares `assurance: high` and drops `privacy`, `data_integrity`, and `compatibility`. The second release implements a security boundary with dedicated UIDs, ACLs, mount namespaces, and credential provisioning. Either raise assurance to `critical` and restore the dropped risk domains, or record why the downgrade is justified.  |
| PROP-02 | major    | 06    | open   | Carried acceptance prerequisites A12 and A13 positioned as second-release-only. Both findings say "required before acceptance" — the superseded proposal's acceptance, inherited by absorbing its scope. The Open Questions section says "No open questions block the research or the first release" and lists only two credential and proof questions as second-release prerequisites. A12 (carry-forward register) and A13 (alternatives analysis) block this proposal's move to `accepted`, not just the second release. Reposition them as whole-proposal prerequisites. |
| PROP-03 | major    | 01    | open   | Second release completion criterion references the acceptance proof without an anchored cross-reference. "The host-native isolation profile passes the acceptance proof from the absorbed isolation proposal" — the superseded proposal carries a 30+ row acceptance proof table amended across four review rounds. This proposal does not reproduce the table, cross-reference its section, or identify which rows still apply. Either reproduce the applicable subset or add an explicit cross-reference with section anchor to the superseded proposal.                   |
| PROP-04 | minor    | 02    | open   | Relationship between the new `orchestrate` command and the existing `intent` commands is undefined. The execution sequence (steps 1 through 10) combines eligibility evaluation (which `intent select` already performs) with envelope building and adapter invocation. The proposal does not state whether `orchestrate` replaces, wraps, or coexists alongside `intent`. State the relationship so a planner can scope both commands without overlap.                                                                                                                      |
| PROP-05 | minor    | 03    | open   | Portable envelope omits working directory or project root. The envelope lists seven portable fields including "Resolved inputs — file paths the agent needs to read." The adapter must start the runtime in a specific location. The path resolution contract — absolute versus relative, how the adapter translates envelope paths to runtime-accessible locations — is not defined. Add working directory to the envelope or specify the path resolution contract.                                                                                                         |
| PROP-06 | minor    | 06    | open   | Alternatives analysis from the superseded proposal not cross-referenced. The carried findings table records A13 as "Open — proposed matrix included in superseded proposal." The superseded proposal resolved A13 with a weighted Pugh matrix in its Alternatives Analysis section. For a proposal declaring `architecture_change: true`, the analysis should be traceable from this document. Add a cross-reference with section anchor to the superseded proposal's Pugh matrix.                                                                                           |
| PROP-07 | minor    | 08    | open   | First release has countable units but the estimate is entirely `unknown`. The first release comprises one property matrix (91 cells), two JSON Schemas, one runtime configuration file, four library modules, one CLI script, and one test fixture. A rough normalized-token range is derivable. Derive a range for the first release or record why a rough estimate is not possible.                                                                                                                                                                                        |

### Check Results

| #   | Check                            | Result                                                                                                                                                                |
| --- | -------------------------------- | --------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| 01  | Completion criteria testable     | Weak — most criteria pass; the second release references an unanchored acceptance proof in another document (PROP-03)                                                 |
| 02  | Scope boundary sharp             | Pass — four releases clearly separated, deferred list explicit; minor gap in command relationship (PROP-04)                                                           |
| 03  | Design decomposable              | Pass — envelope fields, adapter interface, execution sequence, and property matrix are concrete; minor: envelope omits working directory (PROP-05)                    |
| 04  | Impact classification consistent | Fail — governance assurance and risk domains do not reflect the absorbed critical-assurance isolation concern (PROP-01)                                               |
| 05  | Boundary references exist        | Pass — all 10 paths resolve at the reviewed commit                                                                                                                    |
| 06  | Open questions genuine           | Fail — carried findings A12 and A13 are acceptance-gate prerequisites mispositioned in the document structure; alternatives analysis not traceable (PROP-02, PROP-06) |
| 07  | Motivation justifies timing      | Pass — precondition infrastructure exists, execution is the gap, isolation concern needs a home                                                                       |
| 08  | Estimate plausible               | Pass — `unknown` at low confidence is defensible for a multi-release proposal; the first release is estimable (PROP-07)                                               |

### Summary

The core design is sound: a portable envelope translated by runtime-specific adapters, validated by the existing output fence, with a concrete property matrix research step before any adapter work begins. The execution sequence, controller shape, and test fixture are decomposable. Three major findings must be resolved before this proposal is ready to plan from. The governance classification does not reflect the critical-assurance security boundary the second release absorbs (PROP-01). Carried findings A12 and A13 are whole-proposal acceptance prerequisites that the document structure positions as second-release-only (PROP-02). The second release's key completion criterion references a 30-row acceptance proof table in another document without a section anchor or subset identification (PROP-03).
