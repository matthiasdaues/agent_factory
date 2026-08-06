[back to index](README.md)

# 6. Runtime View

## 6.1 Overview

This chapter describes key interaction sequences, focusing on **test execution** — the newest flow and the one most central to the "Agentic Creation, Deterministic Validation" principle. Other runtime scenarios (phase advance, agent dispatch, retry loops) are documented here as needed for context but are not exhaustive; see use cases in [`spec/use_cases/`](spec/use_cases/) for full flows.

## 6.2 Test Execution Flow

Derived from dynamic view `TestExecutionFlow` in [`architecture.dsl`](architecture.dsl).

Test execution happens via three mechanically triggered integration points, never via bare agent-commanded shell execution. Agents can write test files; Factory guardrails require them to use the staged test runner for iteration.

### 6.2.1 Sequence: Pre-Commit Hook (Changed Files Only)

```mermaid
sequenceDiagram
    participant H as Human Operator
    participant G as git
    participant RT as run-tests
    participant P as Project Test Framework

    H->>G: git commit
    G->>RT: Pre-commit hook fires (--changed-only)
    RT->>P: Detect framework (pyproject.toml → pytest)
    P-->>RT: Framework: pytest
    RT->>P: uv run pytest --lf --quiet
    P-->>RT: Test results (exit 0 or 1)
    RT->>G: Emit JSON summary on stdout
    RT->>G: Exit 0 (pass) or 1 (fail)
    alt Tests pass
        G->>H: Commit succeeds
    else Tests fail
        G-->>H: Commit blocked, stderr shows failures
        Note over H: Fix tests and retry, or --no-verify to bypass (discouraged)
    end
```

**Key Points**:

- **Fast feedback**: `--changed-only` mode uses framework-specific fast filters (pytest `--lf`, jest `--onlyChanged`)
- **Bypassable**: Human can use `git commit --no-verify` for WIP commits (not recommended)
- **Agent path**: If agent commits, same hook fires; agent sees hook output (pass/fail) but cannot bypass

### 6.2.2 Sequence: Pre-Push Hook (Full Suite)

```mermaid
sequenceDiagram
    participant H as Human Operator
    participant G as git
    participant RT as run-tests

    H->>G: git push
    G->>RT: Pre-push hook fires (--full)
    RT->>RT: Detect framework, run complete test suite
    RT->>G: Emit JSON summary, exit 0 or 1
    alt Tests pass
        G->>H: Push succeeds
    else Tests fail
        G-->>H: Ordinary push blocked
        Note over H: Fix tests, or explicitly use git push --no-verify
    end
```

**Key Points**:

- **Complete validation**: `--full` mode runs entire test suite, no filtering
- **Default ready-to-share gate**: Ordinary pushes run the full suite and stop on failure
- **Client-side boundary**: A human can bypass the hook with `git push --no-verify`; repository-wide enforcement requires a server-side or required-CI gate

### 6.2.3 Sequence: Phase Advance Gate Evaluation

```mermaid
sequenceDiagram
    participant H as Human / Orchestrator
    participant PA as phase advance
    participant FSM as FSM + Marker
    participant RT as run-tests

    H->>PA: factory/scripts/phase advance
    PA->>FSM: Read current state, resolve target state entry_conditions
    FSM-->>PA: Entry condition: script_exit_zero (run-tests --full)
    PA->>RT: Invoke run-tests --full
    RT->>RT: Detect framework, run complete suite
    RT-->>PA: Exit 0 (pass) or 1 (fail), JSON summary on stdout
    alt Tests pass (exit 0)
        PA->>FSM: Write marker: state=<next>, iteration=1
        PA->>H: Phase advanced
    else Tests fail (exit 1)
        PA-->>H: Refuse advancement: tests_pass unmet (stderr shows failures)
        Note over H: Fix tests, retry phase advance
    end
```

**Key Points**:

- **FSM-driven**: Test execution is an entry condition (`script_exit_zero: factory/scripts/run-tests --full`)
- **Blocks phase transition**: Phase cannot advance while tests are red
- **Exhaustive reporting**: All unmet conditions listed (not short-circuited)

### 6.2.4 Sequence: Agent Iteration with Staged Mode

```mermaid
sequenceDiagram
    participant A as CLI-Invoked Agent
    participant G as git
    participant RT as run-tests
    participant P as Project Test Framework

    Note over A: Agent writes test_foo.py
    A->>G: git add test_foo.py
    A->>RT: factory/scripts/run-tests --staged
    RT->>G: Read staged files (git diff --staged --name-only)
    G-->>RT: test_foo.py
    RT->>P: Detect framework, run tests on staged files only
    P-->>RT: Test results (exit 0 or 1), stderr shows failures
    RT-->>A: JSON summary + stderr output
    alt Tests pass
        Note over A: Proceed to commit or continue development
    else Tests fail
        Note over A: Fix test, re-stage, run --staged again
        A->>A: Edit test_foo.py
        A->>G: git add test_foo.py
        A->>RT: factory/scripts/run-tests --staged (iterate)
    end
```

**Key Points**:

- **Tight feedback loop**: Agent can iterate on tests without committing
- **Same validation path**: Uses `run-tests` script, not bare test commands
- **Staged scope only**: Tests only what's staged, fast iteration
- **Agent allowlist**: `factory/scripts/run-tests --staged` permitted (BR-024); bare `pytest` still blocked
- **Pre-commit still runs**: When agent commits, hook runs `--changed-only` authoritatively

### 6.2.5 Sequence: Agent Blocked from Running Tests

```mermaid
sequenceDiagram
    participant A as CLI-Invoked Agent
    participant BDG as block-dangerous-git.sh
    participant CLI as Claude Code / Copilot CLI / Codex

    A->>CLI: Attempt: pytest .
    CLI->>BDG: PreToolUse hook fires (command JSON on stdin)
    BDG->>BDG: Match command against deny patterns (BR-024)
    BDG-->>CLI: Deny (exit 2): "Test execution blocked. Tests run via hooks only."
    CLI-->>A: Command denied, exit 2 message surfaced
    Note over A: Agent sees denial, cannot run tests<br/>Must rely on hook output instead
```

**Key Points**:

- **Preventive**: Command blocked *before* execution (PreToolUse hook, not post-facto)
- **Three native-hook CLIs**: Claude Code, Copilot CLI, and Codex invoke the
  shared shell guardrail; Pi enforces the same deny list through its
  project-local extension
- **No workaround**: Agent has no shell access that bypasses PreToolUse; bare test commands are unavailable
- **Allowed alternative**: `factory/scripts/run-tests --staged` is permitted for agent iteration
- **Deny patterns (BR-024)**: The canonical list is maintained in
  `factory/config/hooks/block-dangerous-git.sh`; representative entries include
  `pytest`, package-manager test scripts, `jest`, `vitest`, `mocha`, `go test`,
  `cargo test`, and Python/uv pytest invocations.

## 6.3 Other Runtime Scenarios (Summary)

Full sequences for these flows are in their respective use cases:

- **Phase advance with multiple entry conditions** → [UC-01](spec/use_cases/UC-01-advance-a-playbook-phase.md)
- **Retry loop with iteration cap** → [UC-03](spec/use_cases/UC-03-retry-a-phase-within-the-iteration-cap.md)
- **Agent dispatch (interactive vs. background)** → [UC-04](spec/use_cases/UC-04-dispatch-an-agent-via-trigger.md)
- **Resume after interruption** → [UC-05](spec/use_cases/UC-05-resume-an-interrupted-playbook-run.md)
- **Transition-lint blocking out-of-phase commit** → [UC-02](spec/use_cases/UC-02-block-an-out-of-phase-commit.md)

## Referenced from

- [05_building_block_view.md § 5.2.1](05_building_block_view.md#521-run-tests--test-execution-component)
- [08_crosscutting_concepts.md § 8.1](08_crosscutting_concepts.md#81-agentic-creation-deterministic-validation)
- [09_architecture_decisions.md](09_architecture_decisions.md)
