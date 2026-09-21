[back to index](../README.md)

# 8. Cross-cutting Concepts

## 8.1 Agentic Creation, Deterministic Validation

**Principle**: Creation is agentic; validation is deterministic. Tests, precondition checks, and dangerous-command checks are triggered mechanically rather than left to agent judgment. Agent guardrails prevent bypass in the managed workflow; you retain Git's standard `--no-verify` escape hatch when you control the Git client. Other deterministic validators run *on demand*, invoked by a playbook, agent, or you; their result remains trustworthy because it is a mechanical exit code, not an agent's word.

Derived from [`factory/rulebooks/conventions/foundational-principles.md`](../../.agent-factory/factory/rulebooks/conventions/foundational-principles.md).

### What It Means

| Concern                      | Who/What Owns It                                                                          | Enforced How                                                                                                           |
| ---------------------------- | ----------------------------------------------------------------------------------------- | ---------------------------------------------------------------------------------------------------------------------- |
| **Creation**                 | Agents and humans write specs, code, tests, docs, ADRs                                    | Agentic -- LLM-driven or human-authored, inherently non-deterministic                                                  |
| **Validation**               | Scripts check artifacts against predefined, state-dependent rules                         | Deterministic -- hooks, exit codes, no judgment calls                                                                  |
| Test gates present           | Charter declares test commands; eligibility preconditions and guardrails read the charter | Precondition evaluator resolves `testing.yaml`; exit 0/1                                                               |
| Git safety                   | PreToolUse hook runs `block-dangerous-git.sh`                                             | Denies commands before execution, exit 2                                                                               |
| Agent eligibility            | `intent select` evaluates readiness via the Eligibility Engine                            | Precondition-based agent selection; warnings when preconditions unmet                                                  |
| Research artifacts validated | `schema-validate` (stage 1) and `policy-validate` (stage 2), invoked on demand            | Deterministic -- exit codes, no judgment; invoked by the research playbook/agents, not hook-enforced (see section 8.6) |
| Semantic code quality gated  | `crap-score`, `dependency-check`, invoked by dispatcher                                   | Deterministic -- exit codes; dispatcher-owned, not hook-enforced (see section 8.7)                                     |
| Architecture routing         | `module-graph-check`, invoked by orchestrating session                                    | Deterministic -- compares module map from DSL against concept outputs (see section 8.8)                                |

### Why It Matters

**Trust boundary**: Agents are noisy channels. You cannot trust an agent to validate its own work correctly, report test failures honestly, or obey soft guidelines ("please don't push"). Validation must be external and mechanical. Client-side Git hooks enforce the managed agent workflow and ordinary human operations; they are not a security boundary against a human who controls the client.

**Separation of concerns**: Agents are excellent at generation (specs, code, tests). They are poor at discipline (running the right tests, not bypassing gates). Hooks enforce discipline; agents create value. This separation makes AI-assisted output shippable.

**No self-validation**: An agent reporting "tests passed" is unverified hearsay. A charter-declared test command exiting 0 from a mechanically triggered gate is a fact. The architecture treats agent output as untrusted until a deterministic gate validates it.

### Concrete Manifestation: Test Gate Presence

Test gate presence exemplifies this principle end-to-end:

1. **Project declares test commands** -- you write `testing.yaml` (at `docs/testing.yaml`) with `test_command`, and optionally `test_staged_command` and `test_changed_command`.
2. **Precondition evaluation resolves the declared command** -- the Eligibility Engine evaluates `inputs.required` declarations against the repository, including test configuration presence.
3. **Agent uses the declared command** -- `block-dangerous-git.sh` reads all declared command fields from the testing configuration and allowlists them with exact-string matching. An agent running a declared command proceeds normally.
4. **Agent blocked from bare test commands** -- `block-dangerous-git.sh` denies `pytest`, `npm test`, etc. at PreToolUse unless they exactly match a declared command. Agent cannot bypass or "double-check" -- only the declared, mechanically gated result is trustworthy.

**Result**: Test gates exist by project declaration. Factory ensures the gates are present and reads exit codes only. The project owns test execution, framework choice, and structured test output. Agents use only declared commands.

## 8.2 Hook-Triggered Validation Pattern

Factory Flow Control uses **mechanically triggered gates** as the enforcement layer. Three trigger types participate:

| Hook Type                  | Fires When                 | Runs What                                          | Cannot Be Bypassed By         | Exit Codes          |
| -------------------------- | -------------------------- | -------------------------------------------------- | ----------------------------- | ------------------- |
| **PreToolUse**             | Before every shell command | `block-dangerous-git.sh` (charter-aware allowlist) | Agent or human (CLI enforces) | 0 (allow), 2 (deny) |
| **Eligibility evaluation** | `intent select` invocation | Precondition evaluator against agent definitions   | Manual invocation required    | (evidence table)    |

### Zero-Trust Command Execution

Agents do not have unrestricted shell access. Every command passes through a PreToolUse hook (`block-dangerous-git.sh`) before execution. The hook:

1. Receives the command through the runtime adapter: Claude Code, Copilot CLI,
   and Codex provide their native hook JSON shapes; Pi's extension receives the
   tool call and applies the same deny list.
2. Matches it against a deny list (destructive git commands, test commands).
3. Exits 0 (allow) or 2 (deny). Exit 2 surfaces as a denial message to the agent; the command never executes.

This is **preventive validation**, not reactive. The agent never sees test output from a run it initiated unless it runs a project-declared command.

## 8.3 Project-Declared Test Configuration

Testing is project-owned infrastructure. Factory does not detect frameworks, construct test commands, or own test execution. The project declares its test commands in `testing.yaml` (at `docs/testing.yaml`):

| Field                  | Purpose                                                          | Used By                                   |
| ---------------------- | ---------------------------------------------------------------- | ----------------------------------------- |
| `test_command`         | Full test suite command (required)                               | Eligibility precondition, agent allowlist |
| `test_staged_command`  | Fast TDD iteration on staged files (optional)                    | Agent allowlist                           |
| `test_changed_command` | Fast feedback on changed files (optional)                        | Agent allowlist                           |
| `layers`               | Layer bindings mapping Factory layer names to tooling (optional) | QA strategy grounding                     |

**Zero-install**: Factory does not install test frameworks. It reads the test configuration and executes the declared command as-is. If `testing.yaml` is absent or `test_command` is missing, the precondition evaluator reports the gap.

**Exit-code-only contract** (BR-027): Factory reads only the exit code; structured test output (JSON summaries, coverage reports) is the project's concern, not Factory's.

**Onboarding**: The `detect-test-regime` skill scans for existing test entrypoints during `init-factory` and populates the charter. When multiple entrypoints are detected, it asks for disambiguation.

## 8.4 JSON Output Convention

Machine-readable output from validation scripts goes to **stdout**, human-readable progress/errors to **stderr**. This separation allows:

- Hooks to parse structured results (exit code + JSON) without fragile string parsing.
- Humans/agents to see real-time progress on stderr while the command runs.
- Logs to capture both streams independently.

Example (`crap-score`):

```bash
$ .agent-factory/factory/scripts/crap-score --story-id ST-0042
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

Gates that evaluate results (e.g., the dispatcher checking gate reports) read the exit code only. JSON reports are for human/log consumption, not for gate decisions. Project-owned test commands follow the same contract: Factory reads only the exit code (BR-027).

## 8.5 Single Source of Truth: Workstream State and Agent Definitions

Workstream identity files under `.agent-factory/workstreams/` and agent
definitions in YAML frontmatter are the sources of truth for "which workstream
is active" and "which agents are eligible."

- **Observable-state resume** (ADR-0002): Every mechanism (`intent select`,
  dispatch, validation) derives its answer from files on disk, not from a
  separately persisted execution status.
- **No process-local state**: The Eligibility Engine is a pure function. It
  receives agent definitions and the repository as arguments and returns
  eligible agents. It does not hold state between invocations.
- **Workstream state is immutable identity**: Each workstream file records
  `schema_version`, `workstream_id`, `topic`, and `origin_ref`. No mutable
  fields, no revision history, no locks.
- **Session bindings are navigation, not truth**: Session bindings under
  `.agent-factory/workstreams/sessions/` track which workstream a session is
  observing. They record `session_id`, `workstream_id`, and `bound_at`.

This makes resumption trivial: start a new agent session, read the workstream
state, derive "what's next." No recovery logic, no stale state reconciliation.

## 8.6 Staged Validation: Research Artifacts

The falsification-driven research feature validates its JSON artifacts through a fixed three-stage order, layered by *whether a machine can decide the check* rather than bundled into one pass:

| Stage         | Owner                                            | Decides                                                                                          |
| ------------- | ------------------------------------------------ | ------------------------------------------------------------------------------------------------ |
| 1 -- schema   | `.agent-factory/factory/scripts/schema-validate` | Structure -- required fields, types, enums, identifier patterns, timestamps, array minimums      |
| 2 -- policy   | `.agent-factory/factory/scripts/policy-validate` | Enforceable cross-artifact policy -- role separation, references, quorum, current claim versions |
| 3 -- semantic | a qualified human or agent reviewer              | Meaning -- evidence support, source independence in substance, test severity, claim atomicity    |

The order is fixed: an artifact must pass stage 1, then stage 2, then stage 3 before the next playbook step begins, and progression blocks on the first failing stage (`policy-validate --pipeline` chains stages 1 and 2 and stops at the first failure). This is the same "Agentic Creation, Deterministic Validation" principle applied to a new domain: mechanise every check that can be mechanised (stages 1-2, stdlib-only exit-code validators, exactly like `spec-lint` and `arch-lint`), and name honestly the residue that a script cannot settle (stage 3).

Two distinctions from section 8.2 matter. First, these validators are **on demand, not hook-enforced**: the research playbook and agents invoke them, so they are deterministic and reproducible but do not run automatically at an operation boundary the way a pre-commit gate does. Second, the schemas they check against are **data, not prose** -- JSON-Schema files under `factory/rulebooks/schemas/`, a rulebook category deliberately outside `INDEX.yaml`. See [ADR-0006](09_architecture_decisions.md) and [`research-topic.md` section The Validation Gate](../../.agent-factory/factory/playbooks/research-topic.md).

## 8.7 Semantic Quality Gates

The two semantic gates (`crap-score`, `dependency-check`) extend the "Agentic Creation, Deterministic Validation" principle from syntactic checks to code meaning. They are **on-demand validators owned by the implementation-agent dispatcher**, not hook-triggered. This placement follows [ADR-0012](../adr/0012-dispatcher-owned-semantic-gate-loop.md). Mutation testing is project-owned infrastructure that Factory encourages: the `mutation-analysis` skill provides setup guidance, and the kit-manager carries it as an open question during charter setup until settled in `testing.yaml`.

### Why Dispatcher-Owned, Not Hook-Triggered

Hook-triggered gates (section 8.2) fire at operation boundaries that every commit or push crosses. Semantic gates fire once per developer-agent iteration in the gate loop, after the developer commits, and only for the story's changed files.

### Why Not Developer-Owned

A developer agent running its own quality gates is self-validation. The same principle that led ADR-0003 to block agents from running bare test commands applies here. The developer creates; the dispatcher validates. The developer never sees the gate scripts; it receives only the gate reports when a fix is needed.

### Coherence with Testing Strategy

The Factory's [testing-strategy.md](../../.agent-factory/factory/rulebooks/conventions/testing-strategy.md) says "Test count and coverage percentage are diagnostics, not quality targets." The semantic gates respect this:

- **CRAP score** is a composite structural gate. Coverage enters as a counterweight to cyclomatic complexity; the threshold is on the composite score (CRAP \<= 8 by default), not on coverage itself. The pressure it applies is toward smaller code -- not toward higher coverage percentages.
- **Dependency check** enforces what `architecture.dsl` already declares. Neither TDD nor the testing strategy addresses dependency direction; this gate fills an unoccupied gap.

## 8.8 Architecture as a Concern, Not a Phase

The `module-graph-check` script makes architecture routing mechanical: it reads the module map from `architecture.dsl`, compares it against the feature's concept outputs, and determines whether the feature actually changes module boundaries, dependency directions, or public interfaces.

This makes the routing decision deterministic. Features that add a new API endpoint to an existing module skip architecture work; features that introduce a new module or invert a dependency direction enter it. After implementation, the reconciliation-agent catches any module-graph changes that the earlier check missed.

The pattern is two-pass: coarse structural routing from requirements, precise reconciliation from code.

## 8.9 Consolidated Specification as Executable Artifact

The `.feature` file produced by `derive-feature` is both a specification document and a test input. Gherkin syntax is consumed directly by `behave` (Python), `cucumber` (JS/Java/Ruby), and `godog` (Go). This dual nature creates two distinct integration points:

- The **developer agent** reads the `.feature` file for acceptance criteria and writes step definitions that wire Given/When/Then steps to `@`-referenced code. Running the `.feature` through the test framework is part of the TDD cycle.
- The **QA agent** runs the `.feature` file as an acceptance test. Each Scenario is a contract to verify; the `@`-references point at the code to inspect.

The behavioral specification and the acceptance test are the same artifact. The [testing-strategy.md](../../.agent-factory/factory/rulebooks/conventions/testing-strategy.md) convention recognizes `.feature` file execution as the acceptance test layer, distinct from unit and integration tests that own internal contracts. See [ADR-0011](../adr/0011-gherkin-feature-as-consolidated-specification-format.md).

## 8.10 Code Traceability via @-References

The `@`-reference notation links Gherkin Rules and Scenarios to the source code that implements them. The notation is scoped to `.feature` files only -- prose documents continue to use full Markdown links per [cross-reference-format.md](../../.agent-factory/factory/rulebooks/conventions/cross-reference-format.md).

**Syntax:** `# @<path>::<Symbol>.<member>` (class or method), `# @<path>` (module-level).

**Lifecycle:** `derive-feature` annotates existing code at the concept phase; the developer agent writes step definitions against `@`-referenced code during implementation; the reconciliation agent fills missing `@`-references after implementation. After reconciliation, every Rule carries at least one `@`-reference. Absence of an `@`-reference in the concept `.feature` file means "this behavior does not exist yet." After reconciliation, absence means "this behavior was specified but no code implements it" -- a finding.

## 8.11 Agent Context as Cross-Cutting Concern

The agent context (`docs/agent-context.md`) is the factory-facing interface to all project knowledge. It is a cross-cutting concern: every factory agent, skill, playbook, script, and hook that needs project knowledge reads the agent context rather than scanning the project's documentation tree directly.

**Concern-oriented routing** organizes project knowledge into three concern categories: cross-cutting (always active), technical (per story), and domain (per story). Each concern section carries `Read:` paths that point agents to the relevant project documents. Stories declare their concerns in frontmatter (`concerns: {domain: [...], technical: [...]}`); agents follow matching sections in the context file.

**Single file.** The four YAML files (`stack.yaml`, `workflow.yaml`, `governance.yaml`, `reading-guides.yaml`) and their two-layer/two-mode lifecycle were replaced in 0.9.0 by one CLI-agnostic markdown file. See the [concern-oriented agent context proposal](../proposals/factory-concern-oriented-agent-context.md). ADR-0013 and ADR-0014 are superseded.

**`testing.yaml`** remains a separate file at `docs/testing.yaml`, written by `detect-test-regime`. It is not part of the concern routing.

**Validation** is deterministic. `concern-lint` enforces structure, category headings, `Read:` path resolution, story concern vocabulary, and absence of residual YAML files via `CTX-*` finding codes. It runs both as a pre-commit hook and on demand.

**Guiding rule**: The agent context is a routing table, not a knowledge base -- it tells agents where to look, never what they will find.

## 8.12 Local Usage Evidence and Derived Results

Factory and Usage Analysis meet at one published contract. Factory owns the
usage-record schema and append-only JSONL spool. Usage Analysis owns validation,
accounting, published views, and presentation. The dependency points from
analysis to the contract; capture never calls analysis.

Raw JSONL is authoritative and immutable to analysis. Every query snapshots a
sorted top-level file set, normalizes source identity, and classifies every
selected line before accounting. The valid and failure relations, embedded
DuckDB state, UI state, and Parquet files are derived and safe to delete.

Privacy follows the same boundary. Analysis may expose `transcript_ref` as an
opaque audit value but must not follow, open, copy, index, or tokenize the
referenced transcript. Production analysis has no remote reader or network
client. The optional bundled UI may fetch assets only when the operator starts
it and is not part of deterministic analysis.

Stable output comes only from the six `query-model-v1` views. Snapshot selection
and four-CLI conservation remain inside the accounting registry and SQL model;
table, JSON, relation, Arrow, Parquet, and UI adapters must not reimplement
them. Strict preflight leaves `capture_health` available for diagnosis but
blocks every other stable view when any selected line or ancestry is invalid.

See [ADR-0015](../adr/0015-query-authoritative-jsonl-with-ephemeral-duckdb-views.md)
and [validation rules section Local usage processing and analysis](../spec/supplementary_specs/validation-rules.md#local-usage-processing-and-analysis).

## 8.13 Precondition-Based Agent Eligibility

Agent selection is driven by precondition evaluation against the repository.

### What exists

The `intent` CLI (`packages/factory/scripts/intent`) provides two subcommands:

- **`intent select`**: Loads agent definitions from YAML frontmatter (`engine.agent_loader.load_agent_definitions`), evaluates each agent's `inputs.required` declarations against the filesystem (`engine.eligibility.evaluate_all`), and presents per-agent eligibility evidence. Workstream-scoped filtering is supported via `--workstream`.
- **`intent assess`**: Discovers governed artifacts by type (proposals, features, stories, arc42 chapters, ADRs), validates each against frontmatter checks and lint scripts, and reports per-artifact assessment results.

The eligibility engine is composed of three modules:

1. **Precondition evaluator** (`engine/eligibility.py`): Resolves each requirement's `path_pattern` against the filesystem, filters by workstream scope, checks frontmatter conditions or runs validator scripts, and returns per-requirement evidence.
2. **Readiness derivation** (`engine/readiness.py`): Accepts evaluation evidence and produces `AgentReadiness` dataclasses with `eligible`, `unsatisfied`, and `warnings` fields.
3. **Recommendation classifier** (`engine/recommendations.py`): Classifies agents into eligible and blocked groups from readiness verdicts.

The engine is read-only: it reads agent definitions and the repository, returns immutable decisions, and never writes state.

### Workstream concurrency

Multiple workstreams may be active simultaneously within a project. Each workstream has its own immutable identity file under `.agent-factory/workstreams/`. Session bindings under `.agent-factory/workstreams/sessions/` track which workstream each CLI session is observing.

## Referenced from

- [foundational-principles.md](../../.agent-factory/factory/rulebooks/conventions/foundational-principles.md)
- [05_building_block_view.md section 5.2.1](05_building_block_view.md#521-project-owned-test-gates-via-charter-declaration)
- [05_building_block_view.md section 5.2.3](05_building_block_view.md#523-semantic-quality-gates-crap-score-mutation-analysis-dependency-check)
- [05_building_block_view.md section 5.2.5](05_building_block_view.md#525-agent-context-validation-concern-lint)
- [06_runtime_view.md section 6.2](06_runtime_view.md#62-agent-selection)
- [06_runtime_view.md section 6.3](06_runtime_view.md#63-test-gate-presence)
- [06_runtime_view.md section 6.4](06_runtime_view.md#64-semantic-gate-loop)
- [06_runtime_view.md section 6.5](06_runtime_view.md#65-agent-context-validation)
- [09_architecture_decisions.md](09_architecture_decisions.md)
- [05_building_block_view.md section 5.7](05_building_block_view.md#57-level-2-component-view----usage-analysis-runtime)
- [07_deployment_view.md](07_deployment_view.md)
