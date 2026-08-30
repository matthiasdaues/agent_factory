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
| Test gates present           | Charter declares test commands; FSM gates and guardrails read the charter      | `script_exit_zero` gate condition resolves `charter:test_command`; exit 0/1                                    |
| Commits gated                | Pre-commit hook runs `transition-lint`                                         | Blocks staged files outside current phase's `outputs:` globs                                                   |
| Git safety                   | PreToolUse hook runs `block-dangerous-git.sh`                                  | Denies commands before execution, exit 2                                                                       |
| Phase gates                  | `phase advance` evaluates FSM `entry_conditions`                               | Refuses (exit 1) if any condition unmet, lists all failures                                                    |
| Research artifacts validated | `schema-validate` (stage 1) and `policy-validate` (stage 2), invoked on demand | Deterministic — exit codes, no judgment; invoked by the research playbook/agents, not hook-enforced (see §8.6) |
| Semantic code quality gated  | `crap-score`, `dependency-check`, invoked by dispatcher                        | Deterministic — exit codes; dispatcher-owned, not hook-enforced (see §8.7)                                     |
| Architecture phase routing   | `module-graph-check`, invoked by orchestrating session                         | Deterministic — compares module map from DSL against Phase 1 outputs (see §8.8)                                |

### Why It Matters

**Trust boundary**: Agents are noisy channels. You cannot trust an agent to validate its own work correctly, report test failures honestly, or obey soft guidelines ("please don't push"). Validation must be external and mechanical. Client-side Git hooks enforce the managed agent workflow and ordinary human operations; they are not a security boundary against a human who controls the client.

**Separation of concerns**: Agents are excellent at generation (specs, code, tests). They are poor at discipline (running the right tests, not bypassing gates). Hooks enforce discipline; agents create value. This separation makes AI-assisted output shippable.

**No self-validation**: An agent reporting "tests passed" is unverified hearsay. A charter-declared test command exiting 0 from an FSM gate is a fact. The architecture treats agent output as untrusted until a deterministic gate validates it.

### Concrete Manifestation: Test Gate Presence

Test gate presence exemplifies this principle end-to-end:

1. **Project declares test commands** — the human operator writes `docs/charter/testing.yaml` with `test_command`, and optionally `test_staged_command` and `test_changed_command`.
2. **FSM gate resolves charter** — `phase advance` reads the FSM entry condition `script_exit_zero` with `charter:test_command`, resolves the actual command from the charter, and executes it. Exit 0 advances; nonzero blocks.
3. **Agent uses charter-declared command** — `block-dangerous-git.sh` reads all declared command fields from the charter and allowlists them with exact-string matching. An agent running a charter-declared command proceeds normally.
4. **Agent blocked from bare test commands** — `block-dangerous-git.sh` denies `pytest`, `npm test`, etc. at PreToolUse unless they exactly match a charter-declared command. Agent cannot bypass or "double-check" — only the charter-declared, mechanically gated result is trustworthy.

**Result**: Test gates exist by charter declaration. Factory ensures the gates are present and reads exit codes only. The project owns test execution, framework choice, and structured test output. Agents use only charter-declared commands.

## 8.2 Hook-Triggered Validation Pattern

Factory Flow Control uses **mechanically triggered gates** as the enforcement layer. Three trigger types participate:

| Hook Type             | Fires When                 | Runs What                                           | Cannot Be Bypassed By           | Exit Codes           |
| --------------------- | -------------------------- | --------------------------------------------------- | ------------------------------- | -------------------- |
| **Pre-commit**        | `git commit`               | `transition-lint`                                   | Agent (human can `--no-verify`) | 0 (allow), 1 (block) |
| **PreToolUse**        | Before every shell command | `block-dangerous-git.sh` (charter-aware allowlist)  | Agent or human (CLI enforces)   | 0 (allow), 2 (deny)  |
| **FSM gate** (pseudo) | `phase advance` invocation | `script_exit_zero` resolving `charter:test_command` | Manual invocation required      | 0 (met), 1 (unmet)   |

### Zero-Trust Command Execution

Agents do not have unrestricted shell access. Every command passes through a PreToolUse hook (`block-dangerous-git.sh`) before execution. The hook:

1. Receives the command through the runtime adapter: Claude Code, Copilot CLI,
   and Codex provide their native hook JSON shapes; Pi's extension receives the
   tool call and applies the same deny list.
2. Matches it against a deny list (destructive git commands, test commands).
3. Exits 0 (allow) or 2 (deny). Exit 2 surfaces as a denial message to the agent; the command never executes.

This is **preventive validation**, not reactive. The agent never sees test output from a run it initiated unless it runs a charter-declared command.

## 8.3 Charter Declaration and Test Entrypoint Discovery

Testing is project-owned infrastructure. Factory does not detect frameworks, construct test commands, or own test execution. The project declares its test commands in `docs/charter/testing.yaml`:

| Field                  | Purpose                                                          | Used By                                      |
| ---------------------- | ---------------------------------------------------------------- | -------------------------------------------- |
| `test_command`         | Full test suite command (required)                               | FSM `script_exit_zero` gate, agent allowlist |
| `test_staged_command`  | Fast TDD iteration on staged files (optional)                    | Agent allowlist                              |
| `test_changed_command` | Fast feedback on changed files (optional)                        | Agent allowlist                              |
| `layers`               | Layer bindings mapping Factory layer names to tooling (optional) | QA strategy grounding                        |

**Zero-install**: Factory does not install test frameworks. It reads the charter and executes the declared command as-is. If the charter is absent or `test_command` is missing, the FSM gate blocks with a clear message.

**Exit-code-only contract** (BR-027): Factory reads only the exit code; structured test output (JSON summaries, coverage reports) is the project's concern, not Factory's.

**Onboarding**: The `detect-test-regime` skill scans for existing test entrypoints during `init-factory` and populates the charter. When multiple entrypoints are detected, it asks for disambiguation.

## 8.4 JSON Output Convention

Machine-readable output from validation scripts goes to **stdout**, human-readable progress/errors to **stderr**. This separation allows:

- Hooks to parse structured results (exit code + JSON) without fragile string parsing.
- Humans/agents to see real-time progress on stderr while the command runs.
- Logs to capture both streams independently.

Example (`crap-score`):

```bash
$ factory/scripts/crap-score --story-id ST-0042
# stderr: progress, per-function analysis
Analyzing 3 changed functions...
src/auth.py::login PASS (CRAP=4)
src/auth.py::validate_token FAIL (CRAP=42)
...

# stdout: JSON report, parseable
{"functions": [{"name": "login", "crap": 4, "pass": true}, ...]}

# exit code: 0 (all pass), 1 (any fail)
$ echo $?
1
```

Gates that evaluate results (e.g., `phase advance` evaluating `script_exit_zero`, the dispatcher checking gate reports) read the exit code only. JSON reports are for human/log consumption, not for gate decisions. Project-owned test commands follow the same contract: Factory reads only the exit code (BR-027).

## 8.5 Single Source of Truth: Marker and FSM

The playbook state marker (`.current-work/playbook-state.yml`) and the FSM (e.g., `greenfield-development.fsm.yml`) are the **only** sources of truth for "what phase are we in" and "what's next."

- **Observable-state resume** (ADR-0002): Every mechanism (`phase advance`, `run-step`, `transition-lint`) derives its answer from these files on disk, not from a separately persisted execution status. If the marker says `state: PHASE_2`, then the run is in PHASE_2 — regardless of what any orchestrator process last remembered.
- **No process-local state**: `orchestrator/` (work in progress — not yet operational) has its own `RUN`/`RUN_LOCK` bookkeeping (a distinct concern), but it does not hold a competing notion of "current phase." It reads the marker like everyone else.

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

The two semantic gates (`crap-score`, `dependency-check`) extend the "Agentic Creation, Deterministic Validation" principle from syntactic checks to code meaning. They are **on-demand validators owned by the implementation-agent dispatcher**, not hook-triggered. This placement follows [ADR-0012](../adr/0012-dispatcher-owned-semantic-gate-loop.md). Mutation testing is project-owned infrastructure that Factory encourages: the `mutation-analysis` skill provides setup guidance, and the kit-manager carries it as an open question during charter setup until settled in `testing.yaml`.

### Why Dispatcher-Owned, Not Hook-Triggered

Hook-triggered gates (§8.2) fire at operation boundaries that every commit or push crosses. Semantic gates fire once per developer-agent iteration in the gate loop, after the developer commits, and only for the story's changed files.

### Why Not Developer-Owned

A developer agent running its own quality gates is self-validation. The same principle that led ADR-0003 to block agents from running bare test commands applies here. The developer creates; the dispatcher validates. The developer never sees the gate scripts; it receives only the gate reports when a fix is needed.

### Coherence with Testing Strategy

The Factory's [testing-strategy.md](../../factory/rulebooks/conventions/testing-strategy.md) says "Test count and coverage percentage are diagnostics, not quality targets." The semantic gates respect this:

- **CRAP score** is a composite structural gate. Coverage enters as a counterweight to cyclomatic complexity; the threshold is on the composite score (CRAP ≤ 8 by default), not on coverage itself. The pressure it applies is toward smaller code — not toward higher coverage percentages.
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
- [05_building_block_view.md § 5.2.1](05_building_block_view.md#521-project-owned-test-gates-via-charter-declaration)
- [05_building_block_view.md § 5.2.3](05_building_block_view.md#523-semantic-quality-gates-crap-score-mutation-analysis-dependency-check)
- [06_runtime_view.md § 6.2](06_runtime_view.md#62-test-gate-presence)
- [06_runtime_view.md § 6.3](06_runtime_view.md#63-semantic-gate-loop)
- [09_architecture_decisions.md](09_architecture_decisions.md)
