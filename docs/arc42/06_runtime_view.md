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

## 6.8 Other Runtime Scenarios (Summary)

Full sequences for these flows are in their respective use cases:

- **Agent dispatch (interactive vs. background)** -- [UC-04](../~archive/spec/use_cases/UC-04-dispatch-an-agent-via-trigger.md)

## Referenced from

- [05_building_block_view.md section 5.2.1](05_building_block_view.md#521-project-owned-test-gates-via-charter-declaration)
- [05_building_block_view.md section 5.2.3](05_building_block_view.md#523-semantic-quality-gates-crap-score-mutation-analysis-dependency-check)
- [08_crosscutting_concepts.md section 8.1](08_crosscutting_concepts.md#81-agentic-creation-deterministic-validation)
- [09_architecture_decisions.md](09_architecture_decisions.md)
