[back to index](../README.md)

# 8. Cross-cutting Concepts

## 8.1 Agentic Creation, Deterministic Validation

**Principle**: Creation is agentic; validation is deterministic. Tests, phase-order gates, and dangerous-command checks are triggered mechanically rather than left to agent judgment. Agent guardrails prevent bypass in the managed workflow; human operators who control the Git client retain Git's standard `--no-verify` escape hatch. Other deterministic validators run *on demand*, invoked by a playbook, agent, or operator; their result remains trustworthy because it is a mechanical exit code, not an agent's word.

Derived from [`factory/rulebooks/conventions/foundational-principles.md`](../../factory/rulebooks/conventions/foundational-principles.md).

### What It Means

| Concern                      | Who/What Owns It                                                               | Enforced How                                                                                                   |
| ---------------------------- | ------------------------------------------------------------------------------ | -------------------------------------------------------------------------------------------------------------- |
| **Creation**                 | Agents and humans write specs, code, tests, docs, ADRs                         | Agentic — LLM-driven or human-authored, inherently non-deterministic                                           |
| **Validation**               | Scripts check artifacts against predefined, state-dependent rules              | Deterministic — hooks, exit codes, no judgment calls                                                           |
| Tests run                    | Hooks (pre-commit, pre-push, FSM gate) invoke `run-tests`                      | `script_exit_zero` gate condition, exit 0/1/2                                                                  |
| Commits gated                | Pre-commit hook runs `transition-lint`                                         | Blocks staged files outside current phase's `outputs:` globs                                                   |
| Git safety                   | PreToolUse hook runs `block-dangerous-git.sh`                                  | Denies commands before execution, exit 2                                                                       |
| Phase gates                  | `phase advance` evaluates FSM `entry_conditions`                               | Refuses (exit 1) if any condition unmet, lists all failures                                                    |
| Research artifacts validated | `schema-validate` (stage 1) and `policy-validate` (stage 2), invoked on demand | Deterministic — exit codes, no judgment; invoked by the research playbook/agents, not hook-enforced (see §8.6) |
| Semantic code quality gated  | `crap-score`, `mutation-analysis`, `dependency-check`, invoked by dispatcher   | Deterministic — exit codes; dispatcher-owned, not hook-enforced (see §8.7)                                     |
| Architecture phase routing   | `module-graph-check`, invoked by orchestrating session                         | Deterministic — compares module map from DSL against Phase 1 outputs (see §8.8)                                |

### Why It Matters

**Trust boundary**: Agents are noisy channels. You cannot trust an agent to validate its own work correctly, report test failures honestly, or obey soft guidelines ("please don't push"). Validation must be external and mechanical. Client-side Git hooks enforce the managed agent workflow and ordinary human operations; they are not a security boundary against a human who controls the client.

**Separation of concerns**: Agents are excellent at generation (specs, code, tests). They are poor at discipline (running the right tests, not bypassing gates). Hooks enforce discipline; agents create value. This separation makes AI-assisted output shippable.

**No self-validation**: An agent reporting "tests passed" is unverified hearsay. `run-tests` exiting 0 from a pre-commit hook is a fact. The architecture treats agent output as untrusted until a deterministic gate validates it.

### Concrete Manifestation: Test Execution

Test execution exemplifies this principle end-to-end:

1. **Agent writes test** — agentic creation. The agent authors a test file (e.g., `test_user_auth.py`).
2. **Agent commits** — `git commit` fires pre-commit hook.
3. **Hook runs tests** — `run-tests --changed-only` executes (deterministic validation). Agent does not run tests; hook does.
4. **Pass/fail mechanical** — exit 0 or 1 determines commit success. No agent judgment involved.
5. **Agent blocked from running tests directly** — `block-dangerous-git.sh` denies `pytest`, `npm test`, etc. at PreToolUse. Agent cannot bypass or "double-check" — only the hook's result is trustworthy.

**Result**: Tests run automatically in the managed workflow. Their mechanical exit codes are trustworthy. Agents cannot replace them with self-reported validation.

## 8.2 Hook-Triggered Validation Pattern

Factory Flow Control uses **mechanically triggered gates** as the enforcement layer. Four trigger types participate:

| Hook Type             | Fires When                 | Runs What                      | Cannot Be Bypassed By           | Exit Codes           |
| --------------------- | -------------------------- | ------------------------------ | ------------------------------- | -------------------- |
| **Pre-commit**        | `git commit`               | `transition-lint`, `run-tests` | Agent (human can `--no-verify`) | 0 (allow), 1 (block) |
| **Pre-push**          | `git push`                 | `run-tests --full`             | Agent (human can `--no-verify`) | 0 (allow), 1 (block) |
| **PreToolUse**        | Before every shell command | `block-dangerous-git.sh`       | Agent or human (CLI enforces)   | 0 (allow), 2 (deny)  |
| **FSM gate** (pseudo) | `phase advance` invocation | `script_exit_zero` condition   | Manual invocation required      | 0 (met), 1 (unmet)   |

### Zero-Trust Command Execution

Agents do not have unrestricted shell access. Every command passes through a PreToolUse hook (`block-dangerous-git.sh`) before execution. The hook:

1. Receives the command through the runtime adapter: Claude Code, Copilot CLI,
   and Codex provide their native hook JSON shapes; Pi's extension receives the
   tool call and applies the same deny list.
2. Matches it against a deny list (destructive git commands, test commands).
3. Exits 0 (allow) or 2 (deny). Exit 2 surfaces as a denial message to the agent; the command never executes.

This is **preventive validation**, not reactive. The agent never sees test output from a run it initiated, because it cannot initiate one.

## 8.3 Framework Detection and Zero-Install Principle

`run-tests` auto-detects the project's test framework from structure markers (BR-023):

| Marker                    | Framework Detected | Command Invoked                  |
| ------------------------- | ------------------ | -------------------------------- |
| `pyproject.toml` + pytest | pytest             | `uv run pytest ...`              |
| `package.json` + jest     | jest / npm test    | `npm test`                       |
| `go.mod`                  | go test            | `go test ./...`                  |
| `Cargo.toml`              | cargo test         | `cargo test`                     |
| None                      | (error)            | Exit 2, report missing framework |

**Zero-install**: Factory Flow Control does not install test frameworks. It uses what the project already has (`uv run`, `npm`, `go`, `cargo`). If the project has no test framework, `run-tests` exits 2 and reports the gap — the operator/agent must add one before test gates can pass.

**Mode-specific flags**:

- `--changed-only`: Fast subset (pytest `--lf`, jest `--onlyChanged`, go/cargo per-package filter)
- `--full`: Complete suite, no caching, no filters

Exact framework-specific filters are implementation-defined (BR-025); the intent is sub-second feedback for small changes in `--changed-only` mode, exhaustive coverage in `--full`.

## 8.4 JSON Output Convention

Machine-readable output from validation scripts goes to **stdout**, human-readable progress/errors to **stderr**. This separation allows:

- Hooks to parse structured results (exit code + JSON) without fragile string parsing.
- Humans/agents to see real-time progress on stderr while the command runs.
- Logs to capture both streams independently.

Example (`run-tests`):

```bash
$ factory/scripts/run-tests --full
# stderr: test framework detection, progress, failures
Running pytest tests (full)...
test_user_auth.py::test_login_success PASSED
test_user_auth.py::test_login_invalid FAILED
...

# stdout: JSON summary, one line, parseable
{"passed": 247, "failed": 1, "skipped": 3, "duration_ms": 1234}

# exit code: 0 (pass), 1 (fail), 2 (no framework)
$ echo $?
1
```

Hooks that need to act on results (e.g., `phase advance` evaluating `script_exit_zero`) read the exit code only. The JSON summary is for human/log consumption, not for gate decisions.

## 8.5 Single Source of Truth: Marker and FSM

The playbook state marker (`.agent-factory/playbook-state.yml`) and the FSM (e.g., `greenfield-development.fsm.yml`) are the **only** sources of truth for "what phase are we in" and "what's next."

- **Observable-state resume** (ADR-0002): Every mechanism (`phase advance`, `run-step`, `transition-lint`) derives its answer from these files on disk, not from a separately persisted execution status. If the marker says `state: PHASE_2`, then the run is in PHASE_2 — regardless of what any orchestrator process last remembered.
- **No process-local state**: `orchestrator/` has its own `RUN`/`RUN_LOCK` bookkeeping (a distinct concern), but it does not hold a competing notion of "current phase." It reads the marker like everyone else.

This makes resumption trivial: start a new agent session, read the marker, derive "what's next." No recovery logic, no stale state reconciliation.

## 8.6 Staged Validation: Research Artifacts

The falsification-driven research feature validates its JSON artifacts through a fixed three-stage order, layered by *whether a machine can decide the check* rather than bundled into one pass:

| Stage        | Owner                               | Decides                                                                                         |
| ------------ | ----------------------------------- | ----------------------------------------------------------------------------------------------- |
| 1 — schema   | `factory/scripts/schema-validate`   | Structure — required fields, types, enums, identifier patterns, timestamps, array minimums      |
| 2 — policy   | `factory/scripts/policy-validate`   | Enforceable cross-artifact policy — role separation, references, quorum, current claim versions |
| 3 — semantic | a qualified human or agent reviewer | Meaning — evidence support, source independence in substance, test severity, claim atomicity    |

The order is fixed: an artifact must pass stage 1, then stage 2, then stage 3 before the next playbook step begins, and progression blocks on the first failing stage (`policy-validate --pipeline` chains stages 1 and 2 and stops at the first failure). This is the same "Agentic Creation, Deterministic Validation" principle applied to a new domain: mechanise every check that can be mechanised (stages 1–2, stdlib-only exit-code validators, exactly like `spec-lint` and `arch-lint`), and name honestly the residue that a script cannot settle (stage 3).

Two distinctions from §8.2 matter. First, these validators are **on demand, not hook-enforced**: the research playbook and agents invoke them, so they are deterministic and reproducible but do not run automatically at an operation boundary the way a pre-commit gate does. Second, the schemas they check against are **data, not prose** — JSON-Schema files under `factory/rulebooks/schemas/`, a rulebook category deliberately outside `INDEX.yaml`. See [ADR-0006](09_architecture_decisions.md) and [`research-topic.md` § The Validation Gate](../../factory/playbooks/research-topic.md).

## 8.7 Semantic Quality Gates

The three semantic gates (`crap-score`, `mutation-analysis`, `dependency-check`) extend the "Agentic Creation, Deterministic Validation" principle from syntactic checks to code meaning. They are **on-demand validators owned by the implementation-agent dispatcher**, not hook-triggered. This placement follows [ADR-0012](../adr/0012-dispatcher-owned-semantic-gate-loop.md).

### Why Dispatcher-Owned, Not Hook-Triggered

Hook-triggered gates (§8.2) fire at operation boundaries that every commit or push crosses. Semantic gates are too expensive for that: mutation analysis on a 500-line module runs 30--70 minutes. They fire once per developer-agent iteration in the gate loop, after the developer commits, and only for the story's changed files.

### Why Not Developer-Owned

A developer agent running its own quality gates is self-validation. The same principle that led ADR-0003 to block agents from running bare test commands applies here. The developer creates; the dispatcher validates. The developer never sees the gate scripts; it receives only the gate reports when a fix is needed.

### Coherence with Testing Strategy

The Factory's [testing-strategy.md](../../factory/rulebooks/conventions/testing-strategy.md) says "Test count and coverage percentage are diagnostics, not quality targets." The semantic gates respect this:

- **CRAP score** is a composite structural gate. Coverage enters as a counterweight to cyclomatic complexity; the threshold is on the composite score (CRAP ≤ 8 by default), not on coverage itself. The pressure it applies is toward smaller code — not toward higher coverage percentages.
- **Mutation analysis** is a code-smell gate. A surviving mutant means code does something no test observes. The response is investigation (remove dead code or add the missing contract test), not unconditional test creation.
- **Dependency check** enforces what `architecture.dsl` already declares. Neither TDD nor the testing strategy addresses dependency direction; this gate fills an unoccupied gap.

## 8.8 Architecture as a Concern, Not a Phase

The `feature-addition` playbook historically routed through the full architecture phase whenever `impact.architecture_change: true` was declared in the proposal. This routing was manual and unverified. The `module-graph-check` script replaces the manual declaration with mechanical detection: it reads the module map from `architecture.dsl`, compares it against the feature's Phase 1 outputs, and determines whether the feature actually changes module boundaries, dependency directions, or public interfaces.

This does not eliminate the architecture phase. It makes the routing decision deterministic. Features that add a new API endpoint to an existing module skip Phase 2; features that introduce a new module or invert a dependency direction enter Phase 2. After implementation, the reconciliation-agent catches any module-graph changes that the Phase 1 check missed.

The pattern is two-pass: coarse structural routing from requirements, precise reconciliation from code.

## 8.9 Consolidated Specification as Executable Artifact

The `.feature` file produced by `derive-feature` is both a specification document and a test input. Gherkin syntax is consumed directly by `behave` (Python), `cucumber` (JS/Java/Ruby), and `godog` (Go). This dual nature creates two distinct integration points:

- The **developer agent** reads the `.feature` file for acceptance criteria and writes step definitions that wire Given/When/Then steps to `@`-referenced code. Running the `.feature` through the test framework is part of the TDD cycle.
- The **QA agent** runs the `.feature` file as an acceptance test. Each Scenario is a contract to verify; the `@`-references point at the code to inspect.

The behavioral specification and the acceptance test are the same artifact. The [testing-strategy.md](../../factory/rulebooks/conventions/testing-strategy.md) convention recognizes `.feature` file execution as the acceptance test layer, distinct from unit and integration tests that own internal contracts. See [ADR-0011](../adr/0011-gherkin-feature-as-consolidated-specification-format.md).

## 8.10 Code Traceability via @-References

The `@`-reference notation links Gherkin Rules and Scenarios to the source code that implements them. The notation is scoped to `.feature` files only — prose documents continue to use full Markdown links per [cross-reference-format.md](../../factory/rulebooks/conventions/cross-reference-format.md).

**Syntax:** `# @<path>::<Symbol>.<member>` (class or method), `# @<path>` (module-level).

**Lifecycle:** `derive-feature` annotates existing code at Phase 1; the developer agent writes step definitions against `@`-referenced code at Phase 4; the reconciliation agent fills missing `@`-references at Phase 5. After reconciliation, every Rule carries at least one `@`-reference. Absence of an `@`-reference in the Phase 1 `.feature` file means "this behavior does not exist yet." After reconciliation, absence means "this behavior was specified but no code implements it" — a finding.

## Referenced from

- [foundational-principles.md](../../factory/rulebooks/conventions/foundational-principles.md)
- [05_building_block_view.md § 5.2.1](05_building_block_view.md#521-run-tests--test-execution-component)
- [05_building_block_view.md § 5.2.3](05_building_block_view.md#523-semantic-quality-gates-crap-score-mutation-analysis-dependency-check)
- [06_runtime_view.md § 6.2](06_runtime_view.md#62-test-execution-flow)
- [06_runtime_view.md § 6.3](06_runtime_view.md#63-semantic-gate-loop)
- [09_architecture_decisions.md](09_architecture_decisions.md)
