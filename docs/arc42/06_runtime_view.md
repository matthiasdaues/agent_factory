[back to index](../README.md)

# 6. Runtime View

## 6.1 Overview

This chapter describes key interaction sequences for Factory gates,
eligibility evaluation, and local usage analysis. Dynamic views in
[`architecture.dsl`](architecture.dsl) own the canonical step order.

## 6.2 Agent Selection

Derived from dynamic view `AgentSelection` in [`architecture.dsl`](architecture.dsl).

Agent selection is the primary routing operation. The `intent select` command loads agent definitions, evaluates each agent's declared preconditions against the repository, and presents per-agent eligibility evidence. The eligibility engine never writes state.

### 6.2.1 Sequence: Human Runs `intent select`

```mermaid
sequenceDiagram
    participant H as Human Operator
    participant I as intent select
    participant AL as Agent Loader
    participant PE as Precondition Evaluator
    participant RE as Readiness Evaluator

    H->>I: 1. Invokes intent select [--workstream ID]
    I->>AL: 2. load_agent_definitions(agents_dir)
    AL-->>I: List of agent dicts (from YAML frontmatter)
    I->>PE: 3. evaluate_all(agents, workstream_id)
    PE->>PE: 4. Per agent: resolve path patterns, check frontmatter conditions, run validator scripts
    PE-->>I: Per-agent evidence (satisfied/unsatisfied per requirement)
    I-->>H: Agent evidence table (eligible/ineligible with reasons)
```

**Key Points**:

- **Precondition-based**: Each agent declares `inputs.required` in its YAML frontmatter. The evaluator resolves each requirement's `path_pattern` against the filesystem, optionally filtering by workstream scope and checking frontmatter conditions or validator scripts.
- **Engine is read-only**: The eligibility engine reads agent definitions and the repository. It returns immutable evidence. It does not write state, acquire locks, or produce side effects.
- **Workstream scoping**: When `--workstream` is passed, candidates are filtered by the `scope` field in their frontmatter (matching the workstream ID or `"global"`). Files without a scope declaration are included.
- **Readiness derivation**: `derive_readiness()` accepts evaluation results and produces `AgentReadiness` dataclasses with `eligible`, `unsatisfied`, and `warnings` fields.

## 6.3 Test Gate Presence

Factory ensures test gates exist; the project decides what runs inside them. Testing is project-owned infrastructure declared in `docs/testing.yaml`. Factory's guardrails and eligibility preconditions read that declaration. Factory does not own test execution, framework detection, or structured test output.

### 6.3.1 Sequence: Precondition Evaluation with Test Gate

```mermaid
sequenceDiagram
    participant H as User
    participant I as intent select
    participant PE as Precondition Evaluator
    participant C as docs/testing.yaml

    H->>C: Declare test_command in testing.yaml
    H->>I: Invokes intent select
    I->>PE: Evaluates agent preconditions
    PE->>C: Resolves test_command from testing.yaml
    C-->>PE: test_command: "uv run pytest --tb=short --quiet"
    PE->>PE: Checks inputs.required declarations against filesystem
    alt Preconditions met
        PE-->>I: Agent eligible
        I-->>H: Agent listed with evidence
    else Preconditions unmet
        PE-->>I: Agent blocked (unsatisfied requirements)
        I-->>H: Agent listed with blocking reasons
    end
```

### 6.3.2 Sequence: Agent Uses Charter-Declared Test Command

```mermaid
sequenceDiagram
    participant A as CLI-Invoked Agent
    participant BDG as block-dangerous-git.sh
    participant C as docs/testing.yaml

    A->>BDG: Attempt: uv run pytest --tb=short --quiet
    BDG->>C: Read test_command, test_staged_command, test_changed_command
    C-->>BDG: test_command: "uv run pytest --tb=short --quiet"
    BDG->>BDG: Exact match against charter-declared command
    BDG-->>A: Allow (exit 0)
    Note over A: Command executes normally
```

### 6.3.3 Sequence: Agent Blocked from Bare Test Command

```mermaid
sequenceDiagram
    participant A as CLI-Invoked Agent
    participant BDG as block-dangerous-git.sh
    participant C as docs/testing.yaml
    participant CLI as Claude Code / Copilot CLI / Codex

    A->>CLI: Attempt: pytest .
    CLI->>BDG: PreToolUse hook fires (command JSON on stdin)
    BDG->>C: Read charter (if exists)
    BDG->>BDG: "pytest ." does not exactly match any charter-declared command
    BDG->>BDG: Matches deny pattern "^pytest" (BR-024)
    BDG-->>CLI: Deny (exit 2): "BLOCKED: bare test command"
    CLI-->>A: Command denied, exit 2 message surfaced
    Note over A: Agent sees denial, directed to charter-declared command
```

**Key Points**:

- **Preventive**: Command blocked *before* execution (PreToolUse hook, not post-facto)
- **Exact match only**: Charter-declared commands are allowlisted with exact-string matching; no prefix matching (BR-024)
- **Three native-hook CLIs**: Claude Code, Copilot CLI, and Codex invoke the shared shell guardrail; Pi enforces the same deny list through its project-local extension
- **No charter means no agent test commands**: When `testing.yaml` does not exist, no agent test commands are allowlisted; bare test commands remain blocked
- **Deny patterns (BR-024)**: The canonical list is maintained in `.agent-factory/factory/config/hooks/block-dangerous-git.sh`; representative entries include `pytest`, package-manager test scripts, `jest`, `vitest`, `go test`, `cargo test`, and Python/uv pytest invocations

## 6.4 Semantic Gate Loop

Derived from dynamic view `SemanticGateLoop` in [`architecture.dsl`](architecture.dsl).

The semantic gate loop runs after each developer-agent commit, before merge. The implementation-agent dispatcher owns execution. The developer agent never runs the gates; it only receives gate reports when a fix iteration is needed. See [ADR-0012](../adr/0012-dispatcher-owned-semantic-gate-loop.md).

### 6.4.1 Sequence: Gate Pass (All Gates Succeed)

```mermaid
sequenceDiagram
    participant D as Developer Agent
    participant IA as Implementation Agent (Dispatcher)
    participant CS as crap-score
    participant DC as dependency-check
    participant PM as premerge-check

    D->>IA: Commit on story branch
    IA->>CS: Run crap-score on committed artifacts
    CS-->>IA: JSON report (all functions PASS)
    IA->>DC: Run dependency-check against architecture.dsl
    DC-->>IA: JSON report (zero violations)
    Note over IA: All gates pass
    IA->>PM: Run premerge-check
    PM-->>IA: Exit 0 (merge allowed)
    IA->>IA: Merge story branch
```

### 6.4.2 Sequence: Gate Failure with Fix Iteration

```mermaid
sequenceDiagram
    participant D1 as Developer Agent (iteration 1)
    participant IA as Implementation Agent (Dispatcher)
    participant CS as crap-score
    participant DC as dependency-check
    participant D2 as Developer Agent (iteration 2, fresh context)

    D1->>IA: Commit on story branch
    IA->>CS: Run crap-score
    CS-->>IA: JSON report (function X: FAIL, CRAP=42)
    Note over IA: Gate failed — spawn fresh developer
    IA->>D2: Gate reports + affected files only
    D2->>D2: Fix function X (reduce complexity or add coverage)
    D2->>IA: Commit fix
    IA->>CS: Run crap-score (iteration 2)
    CS-->>IA: JSON report (all functions PASS)
    IA->>DC: Run dependency-check
    DC-->>IA: JSON report (zero violations)
    Note over IA: All gates pass on iteration 2
```

**Key Points:**

- Each fix iteration spawns a fresh developer agent. No context contamination from prior gate output.
- Maximum three fix iterations per tier (configurable in `house-rules.md`). After the cap, the story escalates or is marked blocked.
- The two gates run in sequence: CRAP, dependency. All must pass before `premerge-check`. Mutation testing is project-owned infrastructure that Factory encourages via the `mutation-analysis` skill.
- Gate reports are written to `.current-work/<gate-name>/<story-id>.json` for traceability.

### 6.4.3 Sequence: Module-Graph Check (Architecture Routing)

```mermaid
sequenceDiagram
    participant S as Orchestrating Session
    participant MG as module-graph-check
    participant DSL as architecture.dsl
    participant CO as Concept Outputs

    S->>MG: Run at architecture boundary
    MG->>DSL: Read current module map
    MG->>CO: Read interface-contracts.md, entity-model.md
    MG->>MG: Compare feature outputs against module map
    alt No module-graph change
        MG-->>S: Exit 0 — skip architecture
    else Module boundary changed
        MG-->>S: Exit 1 — enter architecture
        MG->>MG: Update proposal frontmatter: architecture_change: true
    end
```

**Key Points:**

- Runs once per feature, at the architecture boundary. Not per story, not per commit.
- Tests module-graph topology only: new modules, changed public interfaces, inverted dependency directions. A new entity in an existing module does not trigger the architecture check.
- The orchestrating session owns the check. It is not a hook or a dispatcher gate.

## 6.5 Agent Context Validation

The concern-oriented agent context (`docs/agent-context.md`) is a single markdown file that replaced the four-file YAML model in 0.9.0. The team maintains the file directly; `update-context` is retired. See [section 8.11](08_crosscutting_concepts.md#811-agent-context-as-cross-cutting-concern).

### 6.5.1 Sequence: concern-lint Validates Agent Context

```mermaid
sequenceDiagram
    participant G as Git / pre-commit
    participant CL as concern-lint
    participant AC as docs/agent-context.md
    participant ST as backlog/ST-*.md

    G->>CL: Pre-commit fires
    CL->>AC: Parse markdown, check category headings (CTX-SECTIONS)
    CL->>AC: Verify each concern has description and Read path (CTX-SECTIONS)
    CL->>AC: Resolve every Read/Boundary path against repo (CTX-PATHS)
    CL->>CL: Check for legacy YAML files or docs/charter/ (CTX-LEGACY)
    opt Story files exist
        CL->>ST: Read concerns from story frontmatter
        CL->>AC: Match each concern name to a heading (CTX-REFS)
    end
    CL-->>G: Exit code = count of error-severity findings
```

**Key Points:**

- All `CTX-*` findings are errors. A single finding fails the gate.
- The three required categories are `## Always (cross-cutting)`, `## Technical concerns`, and `## Domain concerns`.
- `docs/testing.yaml` is the only accepted test-configuration path and is not validated by `concern-lint`.
- `CTX-LEGACY` rejects mixed formats: the concern-oriented file must not coexist with YAML agent-context files or a `docs/charter/` directory.

## 6.6 Local Usage Query

Derived from dynamic view `UsageQuery` in
[`architecture.dsl`](architecture.dsl).

```mermaid
sequenceDiagram
    participant humanOperator as Human Operator
    participant inputSnapshot as Input Snapshot
    participant rawUsageSpool as Raw Usage Spool
    participant contractCheck as Contract Check
    participant operationalPreflight as Operational Preflight
    participant accountingRegistry as Accounting Registry
    participant queryModel as Query Model v1
    participant resultAdapters as Result Adapters

    humanOperator->>inputSnapshot: 1. Invokes usage-query for a published view
    inputSnapshot->>rawUsageSpool: 2. Snapshots sorted top-level JSONL evidence
    inputSnapshot->>contractCheck: 3. Supplies normalized evidence and records
    contractCheck->>operationalPreflight: 4. Registers valid rows and structured failures
    operationalPreflight->>accountingRegistry: 5. Supplies a valid rooted run graph
    accountingRegistry->>queryModel: 6. Applies the registered conservation rule
    operationalPreflight->>queryModel: 7. Registers valid and failure relations
    queryModel->>resultAdapters: 8. Projects the selected published view
```

The query snapshots its input once. Every selected line becomes either a valid
row or a structured failure. `capture_health` remains queryable when failures
exist; all other stable views refuse partial output. Empty input is valid and
returns each view's declared typed empty result.

## 6.7 Explicit Parquet Export

Derived from dynamic view `UsageParquetExport` in
[`architecture.dsl`](architecture.dsl).

```mermaid
sequenceDiagram
    participant humanOperator as Human Operator
    participant queryModel as Query Model v1
    participant parquetExporter as Parquet Exporter
    participant parquetFile as Parquet Export

    humanOperator->>parquetExporter: 1. Requests a published view as Parquet
    queryModel->>parquetExporter: 2. Supplies the selected stable view
    parquetExporter->>parquetFile: 3. Replaces the destination after verification
```

The exporter writes a temporary sibling, verifies logical rows and schema, and
records query-model and input-set provenance before replacement. Any failure
leaves an existing destination unchanged. No scheduled refresh exists.

## 6.8 OpenCode Permission Enforcement

Derived from dynamic view `OpenCodePermissionEnforcement` in [`architecture.dsl`](architecture.dsl).

The Factory plugin enforces permissions and step boundaries for every tool invocation in an OpenCode session. The permission enforcer evaluates ordered allow, ask, and deny rules. Explicit denials are final and cannot be broadened by the plugin's permission hook.

### 6.8.1 Sequence: Plugin Evaluates a Tool Invocation

```mermaid
sequenceDiagram
    participant A as CLI-Invoked Agent (OpenCode)
    participant PE as Permission Enforcer
    participant SM as Step Manifest
    participant P as Plugin Permission Rules

    A->>PE: 1. Tool invocation reaches execute.before hook
    PE->>SM: 2. Reads active step manifest
    PE->>P: 3. Evaluates allow/ask/deny rules in order
    alt Path within step boundary and allowed
        PE-->>A: Allow invocation
    else Path outside step boundary or denied
        PE-->>A: Deny with named failed control and recovery action
    end
```

**Key Points:**

- The plugin reads `.current-work/current-step.yml` to determine the active step boundary.
- Reads outside declared inputs are denied before tool execution.
- Writes outside declared outputs are denied before tool execution.
- Shell commands matching denied Git patterns are denied before execution.
- Review agents whose definitions declare no write outputs receive read-only tool sets. The Tool Restrictor removes write tools from the agent's available set.
- Permission hooks may narrow an OpenCode decision but never broaden a configured denial.

## 6.9 OpenCode Worktree Isolation

Derived from dynamic view `OpenCodeWorktreeIsolation` in [`architecture.dsl`](architecture.dsl).

The plugin isolates each dispatched child session in a Factory-managed worktree. The worktree strategy delegates branch and path creation to Factory scripts so that the Factory's naming, base, path, and verification rules remain authoritative.

### 6.9.1 Sequence: Plugin Isolates a Child Session

```mermaid
sequenceDiagram
    participant IA as Dispatcher (root session)
    participant WS as Worktree Strategy
    participant FS as Factory Scripts
    participant PE as Permission Enforcer
    participant C as Child Session

    IA->>WS: 1. Request child session workspace
    WS->>FS: 2. Delegates branch and worktree creation
    FS-->>WS: Worktree at .current-work/<feature-branch>/
    WS-->>IA: Child workspace ready
    PE->>IA: 3. Primary checkout receives session-scoped write denial
    IA->>C: 4. Child starts in isolated worktree
    C->>C: 5. Verifies declared base before reading or changing files
    Note over IA: Primary checkout rejects writes while child is active
    C-->>IA: Child completes
    PE-->>IA: Write denial released
```

**Key Points:**

- Each child receives its own Factory branch and Git worktree under `.current-work/<feature-branch>/`.
- Each child verifies its declared base commit before reading or changing files.
- The primary checkout rejects writes through a session-scoped write denial while any child is active.
- Worktree creation failure fails closed: the dispatch is denied with a named recovery action.
- The Factory's naming, base, path, and verification rules remain authoritative. OpenCode tracks the resulting location and starts each child session there.

## 6.10 Value-First Onboarding

The value-first onboarding journey guides a newcomer from diagnosis to one safe result before asking for advanced configuration. Five runtime sequences cover the key interactions: installation, release build, first-session insight, the first-task sandbox lifecycle, and the update transaction.

### 6.10.1 Sequence: Newcomer Installs a Verified Factory Release

Derived from dynamic view `OnboardingInstallation` in [`architecture.dsl`](architecture.dsl).

```mermaid
sequenceDiagram
    participant N as Newcomer
    participant B as install-agent-factory
    participant DR as Distribution Remote
    participant IF as init-factory
    participant IM as Install Manifest

    N->>B: 1. Runs the bootstrap with source selector and target
    B->>B: 2. Read-only preflight: host, tools, Git state, network, interfaces
    alt Blocked
        B-->>N: Incompatibility explanation, exit without changes
    else Ready or Ready with limitations
        B-->>N: 3. Installation preview from preflight and planned effects
        N->>B: 4. Affirmative consent (blank input is not consent)
        B->>DR: 5. Downloads and verifies release assets (SHA-256)
        alt Digest mismatch
            B-->>N: Refuse extraction, target unchanged
        else Digest verified
            B->>IF: 6. Delegates project-level setup after verification
            IF->>IM: 7. Records installed paths, source selector, and metadata
            B->>IM: 8. Records source selector and installation metadata
            B-->>N: 9. Receipt: changed paths, version, next command
        end
    end
```

**Key Points:**

- Preflight is read-only. No software is installed, no files are edited, and no configuration is changed during diagnosis.
- The installation preview derives from preflight results and the source selector. No install manifest exists before first installation.
- The installation preview precedes download. No remote assets are fetched until the newcomer gives affirmative consent. This satisfies the consent-before-mutation rule.
- Each prerequisite fix requires separate affirmative consent, shows its scope and reversal, and passes verification before the next fix. Blank input stops the sequence.
- The bootstrap delegates to `init-factory` for the actual file operations. See [ADR-0022](../adr/0022-layered-installation-bootstrap-wraps-init-factory.md) (superseded by [ADR-0023](../adr/0023-update-transaction-with-approval-staging-and-rollback.md); the layered first-install design is preserved).
- The receipt names one exact command that opens the first Factory session.

### 6.10.2 Sequence: Release Maintainer Builds Reproducible Assets

Derived from dynamic view `ReleaseBuild` in [`architecture.dsl`](architecture.dsl).

```mermaid
sequenceDiagram
    participant RM as Release Maintainer
    participant BR as build-release
    participant DR as Distribution Remote

    RM->>BR: 1. Runs build-release for a versioned source tree
    BR->>BR: 2. Normalizes archive metadata for reproducibility
    BR->>DR: 3. Publishes install-agent-factory, agent-factory.tar.gz, SHA256SUMS
    Note over BR: Repeated builds from the same source and version produce the same archive digest
```

### 6.10.3 Sequence: First Session Delivers Project Insight

Derived from dynamic view `FirstSessionInsight` in [`architecture.dsl`](architecture.dsl).

```mermaid
sequenceDiagram
    participant N as Newcomer
    participant V as CLI-Invoked Agent (Virgil)
    participant IM as Install Manifest
    participant FS as Project Filesystem
    participant HD as hook-demo
    participant SF as State Files

    N->>V: Opens first Factory session via the receipt command
    V->>IM: Reads installation state
    V->>FS: Read-only project scan
    FS-->>V: Detected stack, test entry point, safety signals
    V-->>N: Reports observed evidence, unknowns, and one recommended action
    Note over V: No files changed, no advanced configuration requested
    opt Selected action needs context
        V-->>N: Explains capture-context scope, output, and validation
        N->>V: Gives affirmative consent for context capture
        V->>V: Runs capture-context to create docs/agent-context.md
        V-->>N: Presents captured concerns for review
    end
    opt Newcomer accepts gate demonstration
        V-->>N: Offers gate demonstration
        N->>V: Gives affirmative consent for gate demonstration
        V->>HD: Runs gate demonstration on disposable fixture
        HD->>SF: Creates disposable fixture
        HD-->>N: Shows failure-to-pass cycle
        HD->>SF: Removes fixture
        V-->>N: Hook choices grouped by protected outcome
    end
```

**Component ownership:**

| Behavior                       | Owner                                                                                                                                       |
| ------------------------------ | ------------------------------------------------------------------------------------------------------------------------------------------- |
| Read-only project insight      | Virgil reads the install manifest and scans the project filesystem without side effects                                                     |
| Deferred configuration routing | Virgil delays model-tier, hook, and context decisions until the selected action requires them                                               |
| Context capture                | `capture-context` skill creates `docs/agent-context.md` after the newcomer gives affirmative consent; Virgil presents captured concerns     |
| Gate demonstration             | `hook-demo` (Distribution) creates a disposable fixture, runs a real gate, and removes the fixture after newcomer gives affirmative consent |

**Key Points:**

- The first session reads installation state and scans the project, then reports what the Factory found, what remains unknown, and one recommended action without changing project files.
- Model-tier selection, hook decisions, and extended context capture wait until the chosen action requires them.
- Before context capture, onboarding explains the scan, the output (`docs/agent-context.md`), validation (`concern-lint`), and defines `concern` as a routing topic. Context capture requires affirmative consent before scanning. The capture invocation follows consent, and the captured concerns are presented for review.
- The gate demonstration requires affirmative consent before running. It uses a disposable fixture and leaves the target project unchanged.

### 6.10.4 Sequence: First Task Runs in an Isolated Sandbox

The shared execution paths are derived from dynamic views `FirstTaskLifecycle`
and `FirstTaskLifecycleNoHead` in [`architecture.dsl`](architecture.dsl). The
first-task state machine owns the mutually exclusive discard, reference
retention, and production-handoff branches.

The first-task sandbox lifecycle follows the state machine at [`state-machines.md`](../spec/supplementary_specs/state-machines.md#first-task-sandbox-lifecycle) and the contract at [`interface-contracts.md`](../spec/supplementary_specs/interface-contracts.md#first-task-sandbox).

```mermaid
sequenceDiagram
    participant N as Newcomer
    participant V as CLI-Invoked Agent (Virgil)
    participant PF as Project Filesystem
    participant G as Git / pre-commit
    participant D as Dispatcher
    participant WS as Workstream State
    participant SB as Session Bindings

    V-->>N: Task preview: goal, duration, artifacts, decisions, cleanup
    N->>V: Approves first task
    alt Repository has HEAD
        V->>G: Creates detached worktree from HEAD at .current-work/onboarding-spike/
    else Repository has no HEAD
        V->>PF: Creates plain sandbox directory at .current-work/onboarding-spike/
    end
    V->>D: Dispatches poc-spike inside sandbox
    D-->>V: poc-spike completes with result and check evidence
    V-->>N: Shows inspectable result and removal instructions
    alt Newcomer chooses discard
        Note over V: No artifacts retained
    else Newcomer retains reference artifacts
        N->>V: Confirms retention of selected artifacts
        V->>PF: Copies confirmed artifacts to docs/spikes/
    else Newcomer begins real work
        V->>WS: Creates or selects production workstream
        V->>SB: Creates session binding for production workstream
        Note over V: Sandbox is not promoted to production work
    end
    alt Sandbox is a Git worktree
        V->>G: Removes worktree and verifies absence
    else Sandbox is a plain directory
        V->>PF: Removes directory and verifies absence
    end
```

**Component ownership:**

| Behavior                        | Owner                                                                                                                         |
| ------------------------------- | ----------------------------------------------------------------------------------------------------------------------------- |
| First-task preview and approval | Virgil presents goal, duration, artifacts, decisions, and cleanup; blank or declined approval creates no sandbox              |
| Sandbox creation                | Virgil creates a detached worktree via Git (HEAD exists) or a plain sandbox directory under `.current-work/` (no HEAD)        |
| Task execution and checking     | Dispatcher resolves and dispatches `poc-spike` playbook inside the sandbox                                                    |
| Discard and cleanup             | Virgil removes the sandbox via Git (worktree) or filesystem and verifies the sandbox path no longer exists                    |
| Reference-artifact retention    | Newcomer confirms retention of selected artifacts; Virgil copies confirmed artifacts to `docs/spikes/` before sandbox removal |
| Production-workstream handoff   | Virgil creates or selects a workstream identity and binds the session to it; the sandbox is never promoted                    |

**Key Points:**

- The sandbox creates no branch or commit. Uncommitted active-working-tree changes are absent from the sandbox.
- When the repository has no HEAD, Virgil creates a plain directory instead of a Git worktree. This is not a Git operation.
- The `poc-spike` workflow runs only inside the sandbox. Its result is directly inspectable by the newcomer.
- Retention requires separate consent per artifact. The newcomer confirms before Virgil copies. Retained files are reference copies, not production state.
- Production handoff creates a normal workstream through the existing workstream creation path. The sandbox does not become production work.
- The ready-host budget is an inspectable result within ten minutes and five decisions after installation approval.

### 6.10.5 Sequence: Project Maintainer Updates an Installation

Derived from dynamic views `UpdateTransaction` and `UpdateTransactionCheck` in [`architecture.dsl`](architecture.dsl).

The update transaction follows [ADR-0023](../adr/0023-update-transaction-with-approval-staging-and-rollback.md), which supersedes ADR-0010 and ADR-0022 for the update path while preserving the layered first-install design.

```mermaid
sequenceDiagram
    participant M as Project Maintainer
    participant UF as update-factory
    participant IM as Install Manifest
    participant DR as Distribution Remote

    alt Check mode (--check)
        M->>UF: 1. Runs update-factory --check
        UF->>IM: 2. Reads source selector and installed version
        UF->>DR: Queries candidate version and digest
        UF-->>M: Reports installed vs. candidate, local modifications, planned effects
    else Normal update
        M->>UF: 1. Runs update-factory
        UF->>IM: 2. Reads source selector and installed version
        UF-->>M: Preview: source, versions, planned effects
        M->>UF: Affirmative approval (blank is not consent)
        opt Source selector or remote URL changed (--source)
            UF-->>M: Presents source-change confirmation
            M->>UF: Confirms source change
        end
        UF->>DR: 3. Downloads and verifies release assets (SHA-256)
        alt Digest mismatch
            UF-->>M: Abort, no changes
        else Digest verified
            UF->>UF: Stages verified replacement alongside current installation
            UF->>UF: Moves current Factory tree aside, applies staged replacement
            alt Application failure
                UF->>UF: Restores previous Factory tree and instruction headers
                UF-->>M: Reports rolled-back state
            else Application succeeds
                UF->>IM: 4. Writes receipt: source, version, digest, changed paths
                UF-->>M: Receipt with changed paths and version
            end
        end
    end
```

**Key Points:**

- Check mode is read-only. It reports the same information as the approval preview without downloading or mutating.
- Modified Factory-owned files stop the update before staging. The user may select the existing preservation flow to proceed.
- A different source selector or remote URL requires a separate `--source` option and its own confirmation step. No automatic fallback crosses the source boundary.
- The previous Factory tree is moved aside, not deleted, before application. Rollback restores it if application fails.
- `update-factory` owns the full transaction. It no longer delegates to `init-factory` for the replacement.

## 6.11 Other Runtime Scenarios (Summary)

Full sequences for these flows are in their respective use cases:

- **Agent dispatch (interactive vs. background)** -- [UC-04](../~archive/spec/use_cases/UC-04-dispatch-an-agent-via-trigger.md)

## Referenced from

- [05_building_block_view.md section 5.2.1](05_building_block_view.md#521-project-owned-test-gates-via-charter-declaration)
- [05_building_block_view.md section 5.2.3](05_building_block_view.md#523-semantic-quality-gates-crap-score-mutation-analysis-dependency-check)
- [08_crosscutting_concepts.md section 8.1](08_crosscutting_concepts.md#81-agentic-creation-deterministic-validation)
- [09_architecture_decisions.md](09_architecture_decisions.md)
