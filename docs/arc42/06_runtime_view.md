[back to index](../README.md)

# 6. Runtime View

## 6.1 Overview

This chapter describes key interaction sequences, focusing on **test gate presence** — the pattern where Factory ensures test gates exist while the project owns what runs inside them — and the **semantic gate loop** that the dispatcher runs after each developer-agent commit. Other runtime scenarios (phase advance, agent dispatch, retry loops) are documented here as needed for context but are not exhaustive; see use cases in [`spec/use_cases/`](../~archive/spec/use_cases/) for full flows.

## 6.2 Test Gate Presence

Derived from dynamic view `TestGatePresence` in [`architecture.dsl`](architecture.dsl).

Factory ensures test gates exist; the project decides what runs inside them. Testing is project-owned infrastructure declared in `docs/charter/testing.yaml`. Factory's guardrails and FSM gates read that declaration. Factory does not own test execution, framework detection, or structured test output.

### 6.2.1 Sequence: Charter Declaration and Phase Advance Gate

```mermaid
sequenceDiagram
    participant H as Human Operator
    participant PA as phase advance
    participant FSM as FSM + Marker
    participant C as docs/charter/testing.yaml

    H->>C: Declare test_command in testing.yaml
    H->>PA: factory/scripts/phase advance
    PA->>FSM: Read current state, resolve target state entry_conditions
    FSM-->>PA: Entry condition: script_exit_zero (charter:test_command)
    PA->>C: Read test_command from testing.yaml
    C-->>PA: test_command: "uv run pytest --tb=short --quiet"
    PA->>PA: Execute resolved command from repository root
    alt Exit 0
        PA->>FSM: Write marker: state=next, iteration=1
        PA->>H: Phase advanced
    else Exit nonzero
        PA-->>H: Refuse: tests_pass unmet (exit code only)
    end
```

**Key Points**:

- **Charter-driven**: FSM gate resolves `test_command` from `docs/charter/testing.yaml`, not a hardcoded script
- **Exit-code-only contract**: Factory reads only the exit code; structured test output is the project's concern (BR-027)
- **Blocks on missing charter**: When `testing.yaml` is absent or `test_command` is missing, the gate blocks with a clear message
- **Exhaustive reporting**: All unmet conditions listed (not short-circuited)

### 6.2.2 Sequence: Agent Uses Charter-Declared Test Command

```mermaid
sequenceDiagram
    participant A as CLI-Invoked Agent
    participant BDG as block-dangerous-git.sh
    participant C as docs/charter/testing.yaml

    A->>BDG: Attempt: uv run pytest --tb=short --quiet
    BDG->>C: Read test_command, test_staged_command, test_changed_command
    C-->>BDG: test_command: "uv run pytest --tb=short --quiet"
    BDG->>BDG: Exact match against charter-declared command
    BDG-->>A: Allow (exit 0)
    Note over A: Command executes normally
```

### 6.2.3 Sequence: Agent Blocked from Bare Test Command

```mermaid
sequenceDiagram
    participant A as CLI-Invoked Agent
    participant BDG as block-dangerous-git.sh
    participant C as docs/charter/testing.yaml
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
- **Deny patterns (BR-024)**: The canonical list is maintained in `factory/config/hooks/block-dangerous-git.sh`; representative entries include `pytest`, package-manager test scripts, `jest`, `vitest`, `go test`, `cargo test`, and Python/uv pytest invocations

## 6.3 Semantic Gate Loop

Derived from dynamic view `SemanticGateLoop` in [`architecture.dsl`](architecture.dsl).

The semantic gate loop runs after each developer-agent commit, before merge. The implementation-agent dispatcher owns execution. The developer agent never runs the gates; it only receives gate reports when a fix iteration is needed. See [ADR-0012](../adr/0012-dispatcher-owned-semantic-gate-loop.md).

### 6.3.1 Sequence: Gate Pass (All Gates Succeed)

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

### 6.3.2 Sequence: Gate Failure with Fix Iteration

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

### 6.3.3 Sequence: Module-Graph Check (Phase Routing)

```mermaid
sequenceDiagram
    participant S as Orchestrating Session
    participant MG as module-graph-check
    participant DSL as architecture.dsl
    participant P1 as Phase 1 Outputs

    S->>MG: Run at end of Phase 1
    MG->>DSL: Read current module map
    MG->>P1: Read interface-contracts.md, entity-model.md
    MG->>MG: Compare feature outputs against module map
    alt No module-graph change
        MG-->>S: Exit 0 — skip Phase 2, go to Phase 3
    else Module boundary changed
        MG-->>S: Exit 1 — enter Phase 2 (Architecture)
        MG->>MG: Update proposal frontmatter: architecture_change: true
    end
```

**Key Points:**

- Runs once per feature, at the Phase 1 / Phase 3 boundary. Not per story, not per commit.
- Tests module-graph topology only: new modules, changed public interfaces, inverted dependency directions. A new entity in an existing module does not trigger Phase 2.
- The orchestrating session (hosting the `feature-addition` playbook) owns the check. It is not a hook or a dispatcher gate.

## 6.4 Agent Context Mode Transition

The agent-context index files have a two-mode lifecycle: `mode: primary` (greenfield, values written directly) and `mode: index` (mature, every non-null, non-deferred leaf has a `source:` pointer). The transition is one-directional and atomic. See [ADR-0014](../adr/0014-two-layer-routing-with-two-mode-lifecycle.md) and [state-machines.md § Agent Context Mode Lifecycle](../spec/supplementary_specs/state-machines.md#agent-context-mode-lifecycle).

### 6.4.1 Sequence: Mode Transition via update-context

```mermaid
sequenceDiagram
    participant H as Human Operator
    participant UC as update-context skill
    participant IF as Index Files (stack/workflow/governance)
    participant CL as context-lint

    H->>UC: Write source pointer for last uncovered field
    UC->>IF: Write name + source to index file
    UC->>IF: Check transition condition across all three files
    IF-->>UC: Every non-null, non-deferred leaf has source pointer
    UC->>H: "All fields have sources. Switch to index mode?"
    alt Operator confirms
        UC->>IF: Set mode: index in all three files (single commit)
        UC->>IF: Strip inline values to names only, preserve source pointers
        UC->>CL: Validate updated files
        CL-->>UC: CX-MODE: index (info), no CX-SRC findings
    else Operator declines
        UC-->>H: Files remain in mode: primary
    end
```

### 6.4.2 Sequence: context-lint Validates Mode Compliance

```mermaid
sequenceDiagram
    participant G as Git / pre-commit
    participant CL as context-lint
    participant IF as Index Files
    participant RG as reading-guides.yaml

    G->>CL: Pre-commit fires
    CL->>CL: Format detection (agent-context vs. legacy charter)
    CL->>IF: Parse YAML, check required keys (CX-PARSE, CX-KEYS)
    CL->>IF: Check mode field (CX-MODE / CX-MODE-INVALID)
    alt mode: index
        CL->>IF: Check every non-null, non-deferred leaf has source (CX-SRC)
        CL->>IF: Check each source pointer resolves to existing file (CX-SRC-EXIST)
        CL->>RG: Check reading-guide exists (CX-FILE)
    end
    CL->>RG: Validate key-path references resolve to index-file keys (CX-GUIDE-REF)
    CL-->>G: Exit code = count of error-severity findings
```

**Key Points:**

- The transition condition is mechanically testable: `context-lint` reports `CX-SRC` findings for fields missing source pointers when mode is index.
- `testing.yaml` is exempt from mode checks -- it receives `CX-PARSE` validation only.
- Format detection routes to either `CX-*` codes (YAML agent-context) or `CH-*` codes (legacy markdown charter), never both.

## 6.5 Other Runtime Scenarios (Summary)

Full sequences for these flows are in their respective use cases:

- **Phase advance with multiple entry conditions** → [UC-01](../~archive/spec/use_cases/UC-01-advance-a-playbook-phase.md)
- **Retry loop with iteration cap** → [UC-03](../~archive/spec/use_cases/UC-03-retry-a-phase-within-the-iteration-cap.md)
- **Agent dispatch (interactive vs. background)** → [UC-04](../~archive/spec/use_cases/UC-04-dispatch-an-agent-via-trigger.md)
- **Resume after interruption** → [UC-05](../~archive/spec/use_cases/UC-05-resume-an-interrupted-playbook-run.md)
- **Transition-lint blocking out-of-phase commit** → [UC-02](../~archive/spec/use_cases/UC-02-block-an-out-of-phase-commit.md)

## Referenced from

- [05_building_block_view.md § 5.2.1](05_building_block_view.md#521-project-owned-test-gates-via-charter-declaration)
- [05_building_block_view.md § 5.2.3](05_building_block_view.md#523-semantic-quality-gates-crap-score-mutation-analysis-dependency-check)
- [08_crosscutting_concepts.md § 8.1](08_crosscutting_concepts.md#81-agentic-creation-deterministic-validation)
- [09_architecture_decisions.md](09_architecture_decisions.md)
