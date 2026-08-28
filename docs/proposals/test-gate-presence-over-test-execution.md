---
schema_version: 2
title: "Test Gate Presence over Test Execution"
status: accepted
owner: Matthias Daues
created: 2026-08-28
updated: 2026-08-28
supersedes:
  - docs/proposals/contract-traced-testing-strategy.md

impact:
  scope: cross_component
  architecture_change: true
  external_contract_change: true
  boundaries:
    - docs/spec/use_cases/UC-09-run-tests-via-hook.md
    - docs/spec/use_cases/UC-10-invoke-a-factory-agent-under-pi.md
    - docs/spec/prd.md
    - docs/spec/supplementary_specs/interface-contracts.md
    - docs/spec/supplementary_specs/validation-rules.md
    - docs/adr/0003-test-execution-via-hooks.md
    - factory/scripts/run-tests
    - factory/scripts/init-factory
    - factory/scripts/update-factory
    - factory/config/pre-commit-config.yaml
    - factory/config/hooks/block-dangerous-git.sh
    - factory/playbooks/bug-fix.fsm.yml
    - factory/playbooks/greenfield-development.fsm.yml
    - factory/scripts/mutation-analysis
    - factory/skills/mutation-analysis/SKILL.md
    - docs/adr/0012-dispatcher-owned-semantic-gate-loop.md
    - factory/skills/qa-strategy-from-spec/SKILL.md
    - factory/agents/kit-manager.md
    - factory/agents/developer-agent.md
    - factory/agents/implementation-agent.md

governance:
  assurance: elevated
  risk_domains:
    - reliability
    - compatibility

estimate:
  as_of: 2026-08-28
  basis: judgment
  confidence: medium
  human_review_hours:
    min: 1.0
    max: 2.0
  normalized_tokens: unknown
  estimated_consumption: unknown
---

# Feature Request: Test Gate Presence over Test Execution

## Summary

Factory must stop owning test execution — in consumer projects and in its own repository. The current `factory/scripts/run-tests` detects framework markers and constructs host-side test commands, a boundary violation that breaks projects with their own test topology. The same boundary violation applies to `factory/scripts/mutation-analysis`, which hardcodes mutmut with pytest internals and cannot reach test infrastructure that runs inside containers or custom runners. Instead, testing becomes entirely project-owned infrastructure: every project (including Factory itself) declares its test commands and layer bindings in `docs/charter/testing.yaml`, Factory's guardrails and FSM gates read that declaration, and `init-factory` stops injecting any test-related hooks into `.pre-commit-config.yaml`. Both `run-tests` and `mutation-analysis` are deleted from the repository.

The charter declaration also closes a traceability gap in the QA strategy derivation chain. Today `qa-strategy-from-spec` applies the Factory testing convention as a generic backbone without consulting the project's declared testing decisions or actual test infrastructure. This proposal wires `qa-strategy-from-spec`, the kit-manager, the developer-agent, and the mutation-analysis skill into a closed loop where the charter is the authority, the repository is the ground truth, the Factory convention is shared vocabulary, and mutation analysis audits contract-ownership assignments. When a project has no test regime, Factory helps build project-owned test infrastructure during onboarding, infrastructure that survives `remove-factory`.

## Motivation

The current `factory/scripts/run-tests` detects framework markers (`pyproject.toml`, `package.json`, `go.mod`, `Cargo.toml`) and constructs host-side test commands (`uv run pytest`, `npm test`, etc.). This works only when the project's tests happen to run on the host with no special topology.

It breaks when the project has its own test infrastructure. The reproducing case is Gigacron: its tests require a Compose environment where `toxiproxy:15432` resolves. The project's entrypoint is `make test` → `./run-dev.sh test` → `docker compose exec app uv run pytest`. Factory's `run-tests` detects `pyproject.toml`, fires `uv run pytest` on the host, and the session migration fixture explodes because the database proxy is unreachable.

The root cause is a boundary violation: Factory imposes its own test execution strategy on the consumer project instead of serving the project's. This contradicts Factory's role as infrastructure that assists consumer projects without owning their runtime topology.

The same release must also close the traceability gap in the QA strategy derivation chain. Today `qa-strategy-from-spec` reads the feature file, entity model, and interface contracts, then applies the Factory testing convention as a generic backbone. It never consults the project's declared testing decisions (`docs/charter/development.md`) or scans the repository's actual test infrastructure. The result is a QA strategy that is coincidentally consistent with the charter, not traceably derived from it. An implementer must bridge the gap between what the QA strategy prescribes and how the repository actually runs tests — that bridging happens silently in each developer-agent session and the knowledge evaporates. These two problems share the same fix point: once the charter declares test infrastructure in `testing.yaml`, the QA strategy chain should read it. Shipping the charter declaration without the traceability wiring would create a new source of truth that nothing consumes, requiring a second cross-component change to wire it in later.

## Core Principles

- Factory owns structural gates (linting, formatting, spec consistency, architecture consistency, phase ordering). Testing is the project's domain.
- Test infrastructure must be project-owned and must survive `remove-factory`. This applies to consumer projects and to Factory itself.
- Code is the source of truth for what test regime exists. The charter is a derived record, not the detection mechanism.
- When multiple plausible test entrypoints exist, Factory asks for disambiguation rather than guessing.
- The gate contract is exit-code-only: zero means pass, nonzero means fail. Structured test counts are the project's concern.
- The project charter is the authority for testing decisions; the Factory convention provides vocabulary, not bindings.
- Every contract-ownership assignment in a QA strategy must be mechanically verifiable — mutation analysis is the verification method.
- Feedback flows backward: implementation reality feeds back to the QA strategy and charter, not just forward from spec to tests.

## Design

### 1. Delete `factory/scripts/run-tests` and `factory/scripts/mutation-analysis` from the repository

Both scripts are deleted entirely — not moved, not kept for Factory's own tests, not excluded from distribution. Because `init-factory` symlinks the entire `factory/scripts/` directory, any script that remains there is visible to consumer projects. Deleting them is the only clean resolution.

`run-tests` imposed a framework-detected host-side test command. `mutation-analysis` imposed mutmut with hardcoded pytest internals — it imports `mutmut.__main__`, writes a `setup.cfg` with pytest-specific config, and assumes the test runner is reachable on the host. Both encode assumptions about the project's test topology that Factory has no right to make.

Factory's own test regime uses the same `testing.yaml` mechanism as every consumer project. The `mutation-analysis` skill (`factory/skills/mutation-analysis/SKILL.md`) is retained as guidance for setting up project-owned mutation testing but is rewritten to describe the setup process rather than prescribe a specific tool chain. The `crap-score` script is unaffected — it analyzes source code structure without invoking any test runner.

### 2. Remove the test hook from Factory's pre-commit config

The `agent_factory_hook-run-tests-full` entry in `factory/config/pre-commit-config.yaml` is removed. Factory stops injecting any test-related hook into `.pre-commit-config.yaml`. Testing hooks are project-owned: either the project already has them, or Factory helps build them during onboarding.

### 3. Introduce `docs/charter/testing.yaml`

A machine-readable file declaring the project's test commands. This is the first charter section to migrate from prose to structured YAML — setting a pattern for incremental charter migration as concrete consumers demand machine-readable access.

Schema (defined by example in the template; no formal JSON Schema artifact):

```yaml
# docs/charter/testing.yaml — project test command declaration
# Factory guardrails and FSM gates read this file.
# All fields are shell commands executed from the repository root.

test_command: "make test"                # required — full test suite
test_staged_command: "make test-staged"  # optional — agent TDD iteration
test_changed_command: "make test-changed"  # optional — pre-commit fast feedback
```

The template lives at `factory/rulebooks/templates/charter-testing.yaml`. Fields are project-defined commands, not framework names. Optional mode commands are absent when the project's test entrypoint has no corresponding mode.

### 4. Factory's own `testing.yaml`

Factory eats its own cooking. The Factory repository gets its own `docs/charter/testing.yaml`:

```yaml
test_command: "uv run pytest --tb=short --quiet"
test_staged_command: "uv run pytest --tb=short --quiet"
```

This replaces the deleted `run-tests` script as Factory's own test declaration. Factory's pre-commit/pre-push hooks reference this declaration the same way any consumer project would.

### 5. `block-dangerous-git.sh` reads the charter for the agent allowlist

The guardrail currently hardcodes `factory/scripts/run-tests --staged` as the sanctioned agent test path (BR-024). This changes to reading `docs/charter/testing.yaml` and allowlisting the commands declared there. Specifically:

- `test_staged_command` is allowlisted if present (agent TDD iteration path).
- `test_changed_command` is allowlisted if present.
- `test_command` is allowlisted if present (full suite, for phase-advance invocation).
- The match is exact: the full command string from the YAML field must match the agent's command. No prefix matching.

The agent uses whatever the project declared — Factory owns the guardrail logic, the project owns the command.

When `remove-factory` runs, the guardrail is removed. Bare test commands become available again, and the project's declared test commands remain as regular project scripts.

### 6. FSM gate conditions reference the charter-declared command

Playbook FSMs (`bug-fix.fsm.yml`, `greenfield-development.fsm.yml`) currently reference `factory/scripts/run-tests --full` as a `script_exit_zero` gate condition. This changes to resolving `test_command` from `docs/charter/testing.yaml`. If the charter has no `test_command`, the gate reports the gap and blocks advancement.

### 7. Test regime detection during onboarding

When Factory onboards a project, it scans for evidence that a test regime already exists. The detection logic lives in a new Factory skill (`detect-test-regime`) invoked by `init-factory` and by the kit-manager during onboarding. The skill scans for:

- `Makefile` with a `test` target
- `package.json` with a `test` script
- `tox.ini` or `tox` section in `pyproject.toml`
- `noxfile.py`
- `Justfile` with a `test` recipe
- `Taskfile.yml` with a `test` task
- Other conventional entrypoints as the detection surface grows

The detection surface should be as broad as possible. Code is the source of truth — the scan goes to real files, not derived documentation.

- **One entrypoint found**: record it in `docs/charter/testing.yaml`.
- **Multiple entrypoints found**: ask the user for disambiguation. Do not guess.
- **No entrypoint found**: surface the gap. Help the user build project-owned test infrastructure if they choose — scripts, hooks, and config that belong to the project and survive `remove-factory`.

The charter serves as a backup reference when detection is ambiguous or when the project has an unconventional setup.

### 8. Mode handling

Factory calls the project's test entrypoint as-is. It does not engineer mode flags, warn about missing modes, or substitute its own mode logic. If the project's entrypoint supports modes, the project wires them. If it does not, the entrypoint runs however it runs. The project owns its mode story.

### 9. Documentation updates

The following specification documents reference `factory/scripts/run-tests` by path and must be updated to reflect the new charter-based mechanism:

- **UC-09** (`docs/spec/use_cases/UC-09-run-tests-via-hook.md`): rewrite to reflect that testing is project-owned infrastructure, with Factory's role limited to guardrail enforcement (agent test prohibition via charter-declared allowlist) and FSM gate evaluation via the charter declaration.
- **ADR-0003** (`docs/adr/0003-test-execution-via-hooks.md`): amend to record this design change — Factory no longer owns test execution, only structural gates. The "Agentic Creation, Deterministic Validation" principle still holds, but the validation mechanism for tests is project-owned, not Factory-owned.
- **prd.md** (`docs/spec/prd.md`): revise G9 (goal statement naming `run-tests`) and FR-I (six sub-requirements FR-I1 through FR-I6 describing auto-detection, modes, JSON summary, and gate invocation). These describe the deleted script's behavior and must be rewritten to reflect project-owned testing via charter declaration. FSM gate condition references update from `factory/scripts/run-tests` to charter-resolved `test_command`.
- **UC-10** (`docs/spec/use_cases/UC-10-invoke-a-factory-agent-under-pi.md`): update BR-033 allowlist reference and acceptance criteria from `factory/scripts/run-tests --staged` to charter-declared `test_staged_command`.
- **interface-contracts.md** (`docs/spec/supplementary_specs/interface-contracts.md`): update guardrail binding references.
- **validation-rules.md** (`docs/spec/supplementary_specs/validation-rules.md`): revise the entire Test execution section — BR-023 (framework detection), BR-024 (agent allowlist), BR-025 (`--changed-only` mode), BR-026 (`--full` mode), BR-027 (JSON summary), BR-028 (`--staged` mode), and BR-029 (pre-commit trigger conditions). All seven business rules describe the deleted script's behavior and must be rewritten to reflect the charter-declared, project-owned testing model.
- **ADR-0012** (`docs/adr/0012-dispatcher-owned-semantic-gate-loop.md`): the dispatcher's three-gate quality sequence (`crap-score`, `mutation-analysis`, `dependency-check`) loses its second gate. The sequence becomes two gates (`crap-score`, `dependency-check`). Mutation testing is entirely the project's responsibility — if the project sets it up, it runs through the project's own hooks or CI, not the dispatcher's gate loop. Amend the ADR to document this architectural change to the gate sequence.
- **implementation-agent** (`factory/agents/implementation-agent.md`): remove `factory/scripts/mutation-analysis` from `inputs:`, change the hardcoded three-gate default to two gates (`crap-score`, `dependency-check`), and remove the `mutation-analysis` CLI invocation from the gate execution section. This agent executes the gate sequence described in ADR-0012 and must stay consistent with the two-gate change.

### 10. Charter layer bindings in `testing.yaml`

The `testing.yaml` schema extends with an optional `layers` section that maps the Factory's five-layer testing vocabulary to project-specific tooling, infrastructure, and constraints:

```yaml
# docs/charter/testing.yaml — project test declaration
# Factory guardrails and FSM gates read the top-level command fields.
# qa-strategy-from-spec reads the layers section.

test_command: "make test"
test_staged_command: "make test-staged"
test_changed_command: "make test-changed"

layers:
  deterministic_linter:
    tool: "ruff, pre-commit scripts"
    infrastructure: "none"
    entry_point: "make check"
  acceptance_test:
    tool: "pytest"
    infrastructure: "PostgreSQL via Toxiproxy"
    entry_point: "make test"
    anti_patterns:
      - "no SQLite fallback"
      - "no mocked DB transactions"
  contract_test:
    tool: "pytest, Vitest"
    infrastructure: "none (golden fixtures)"
    entry_point: "make test"
  integration_test:
    tool: "pytest"
    infrastructure: "PostgreSQL, NATS JetStream, Toxiproxy"
    entry_point: "make test"
    anti_patterns:
      - "no mocked broker custody"
  e2e_smoke_test:
    tool: "pytest + docker compose"
    infrastructure: "full stack"
    entry_point: "make test"
    anti_patterns:
      - "no browser e2e beyond single smoke"
```

The top-level command fields are what gates and guardrails consume — unchanged from Design section 3. The `layers` section is read by `qa-strategy-from-spec` when grounding contract-owner assignments and by the `detect-test-regime` skill during onboarding. If `layers` is absent, `qa-strategy-from-spec` falls back to the Factory convention's generic five layers.

The kit-manager populates the `layers` section during charter completeness sweep and brownfield onboarding by scanning the repository's test infrastructure (conftest.py, test directories, Makefile targets, runner configs). The `detect-test-regime` skill shares this scan surface and records both command fields and layer bindings.

If a project does not use all five layers, the unused layers are omitted, not set to null. The layer names use the same vocabulary as `factory/rulebooks/conventions/testing-strategy.md`.

### 11. QA strategy grounded in charter

`qa-strategy-from-spec` (`factory/skills/qa-strategy-from-spec/SKILL.md`) adds two inputs before its current Step 1:

1. **`docs/charter/testing.yaml`** — read the `layers` section. Map feature contracts to the charter's declared layers, not the Factory convention's generic five. If a contract needs a layer the charter has not declared, emit a gap finding rather than silently assuming the layer exists.

2. **Repository scan** — read root `conftest.py`, each `packages/*/tests/conftest.py`, `Makefile` test targets, `run-dev.sh` test-related commands, `pyproject.toml` pytest configuration, and `vitest.config.*`. Verify that the charter's declared infrastructure and entry points match what exists. Record mismatches as gap findings. This scan does not execute tests or parse CI pipeline YAML.

Step 3 (Assign Test Owners) changes from "Apply `testing-strategy.md` as the governing policy" to "Apply the charter's layer bindings as the governing policy; use `testing-strategy.md` for vocabulary and the overlap-deletion protocol."

The "Generated from" header in the QA strategy output adds:

```markdown
- Charter layer bindings: `docs/charter/testing.yaml`
- Repo test infrastructure: conftest.py, packages/*/tests/
```

When `docs/charter/testing.yaml` is missing or lacks a `layers` section, `qa-strategy-from-spec` falls back to the Factory convention and emits a gap finding noting the absence. It does not fail — the charter-grounded path is preferred, not mandatory.

### 12. Developer-agent test-harness feedback

When the developer-agent implements a story's tests and encounters a mismatch between the QA strategy's prescribed layer or tooling and the repository's actual test harness (missing fixture pattern, no marker support, wrong entry point, missing infrastructure), it invokes `spec-feedback` against the QA strategy document. The finding names the contract, the prescribed layer, and the concrete obstacle.

This uses the existing `spec-feedback` mechanism. The change is that the developer-agent's workflow explicitly checks for harness mismatches after writing tests and before reporting the story as complete.

When `spec-feedback` files a finding against the QA strategy, the finding names the specific contract-owner row that is wrong and proposes a correction. The QA strategy is updated in the same story or in a follow-up QA loop, not deferred indefinitely.

### 13. Mutation-analysis contract-ownership classification

The mutation-analysis skill (`factory/skills/mutation-analysis/SKILL.md`) is rewritten with two sections:

1. **Setup guidance** — how to set up project-owned mutation testing. The skill describes the process and trade-offs, not a prescribed tool chain. The Factory-owned script (`factory/scripts/mutation-analysis`) is deleted (Design section 1), and the skill no longer references it.

2. **Contract-ownership classification** — when a per-feature QA strategy with a contract-owner table is available, the skill instructs the agent to classify each surviving mutant by ownership status:

   - `owner_held` — the declared owner killed the mutant. If overlap tests also killed it, that overlap is safe to trim.
   - `owner_failed` — the declared owner did not kill the mutant, but another layer did. The ownership assignment in the QA strategy is wrong. File a `spec-feedback` finding against the contract-owner row.
   - `uncaught` — no layer caught the mutant. Existing resolution actions apply (`add-missing-test`, `remove-dead-code`, `file-qa-finding`), directed at the declared owner.

The contract-owner table maps contracts to source scenarios. The join between mutants and contracts is by file path: a mutant in a file that a contract's source scenario exercises is attributed to that contract. This is approximate — a file may contain code for multiple contracts — but sufficient for the first release. Finer-grained mapping (function-level, AST-level) is deferred.

This replaces the manual "representative fault" protocol in the testing strategy's safe-deletion procedure with a mechanical equivalent. When the developer-agent or a QA consolidation pass wants to delete overlapping tests, the mutation-analysis classification provides the evidence that the surviving owner still detects the fault class.

### What stays

- Agent prohibition on bare test commands (BR-024) remains. `block-dangerous-git.sh` still blocks bare `pytest`, `npm test`, etc. — the allowlist source changes from a hardcoded path to the charter declaration.
- Exit code semantics for gates (0 = pass, 1 = test failure, 2 = configuration error) remain unchanged.
- Factory's structural hooks (mdformat, ruff, spec-lint, arch-lint, transition-lint, etc.) are unaffected.

## Scope

**In the first release:**

- Delete `factory/scripts/run-tests` and `factory/scripts/mutation-analysis` from the repository.
- Remove `agent_factory_hook-run-tests-full` from `factory/config/pre-commit-config.yaml`.
- Create the `testing.yaml` template at `factory/rulebooks/templates/charter-testing.yaml` (schema defined by example, no formal JSON Schema artifact).
- Create Factory's own `docs/charter/testing.yaml`.
- Update `block-dangerous-git.sh` to read the agent test allowlist from `docs/charter/testing.yaml`, with exact matching on all declared command fields.
- Update FSM gate evaluation in `bug-fix.fsm.yml` and `greenfield-development.fsm.yml` to resolve the test command from `docs/charter/testing.yaml`.
- Create the `detect-test-regime` skill for use during onboarding and wire it into `init-factory`.
- Rewrite `factory/skills/mutation-analysis/SKILL.md` with setup guidance and contract-ownership classification methodology.
- Update UC-09, ADR-0003, ADR-0012, prd.md, UC-10, interface-contracts.md, validation-rules.md, and implementation-agent.md.
- Extend the `testing.yaml` schema with a `layers` section for layer bindings (tool, infrastructure, entry point, anti-patterns per layer).
- Update `qa-strategy-from-spec` to read charter layer bindings and scan the repository before assigning contract owners. Emit gap findings for undeclared layers and charter/repo mismatches.
- Update the developer-agent workflow to invoke `spec-feedback` when test-harness mismatches are found during story implementation.
- Update the kit-manager to populate layer bindings in `testing.yaml` during charter completeness sweep and brownfield onboarding.

**Explicitly deferred (do NOT plan stories for these):**

- Full kit-manager onboarding interview for building test infrastructure from scratch — requires separate design work on the onboarding flow.
- Factory distribution boundary fix (the separate defect that copies Factory development tests into consumer workspaces via the symlinked `factory/` directory).
- Incremental migration of other charter sections from prose to YAML.
- Structured test output parsing.
- Automated reconciliation of charter layer bindings against CI pipeline definitions.
- A formal JSON Schema for the `layers` section of `testing.yaml` — the first release uses schema-by-example.
- Integration with external test-analytics or coverage-tracking systems.
- Function-level or AST-level mutation-to-contract mapping — the first release joins by file path.

## Design Details

### `testing.yaml` placement and discovery

The file lives at `docs/charter/testing.yaml`, consistent with the existing charter directory. Scripts that need the test command resolve it by reading this file relative to the repository root. If the file is absent, the consumer has no declared test regime — gates that require it block with a clear message.

### `remove-factory` behavior

When `remove-factory` runs:

- `block-dangerous-git.sh` is removed (Factory guardrail infrastructure).
- `docs/charter/testing.yaml` remains (project-owned declaration).
- Any project-owned test scripts, hooks, and pre-commit entries remain.
- The project can run tests freely without Factory's guardrail mediation.

### Backward compatibility

Factory is pre-beta with a small user base. There is no backward-compatibility concern with this change. Existing consumer projects that relied on `run-tests` will need to declare their test command in `docs/charter/testing.yaml` and set up their own test hooks — a one-time migration that kit-manager can assist with.

## Open Questions

All questions from the initial draft have been resolved through the grilling interview:

- **Multiple entrypoints**: Factory fails loudly and asks for disambiguation (resolved).
- **Explicit override vs. detection**: code scan is the primary mechanism; charter is the machine-readable record; no separate override key needed (resolved).
- **Mode degradation**: Factory calls the entrypoint as-is, no mode engineering (resolved).

No remaining open questions. The contract-traced-testing-strategy proposal asked whether testing bindings should live in their own charter file or in `development.md`. The answer is `docs/charter/testing.yaml` — the same file that declares test commands also declares layer bindings (Design section 10).

## Completion Criteria

- `factory/scripts/run-tests` and `factory/scripts/mutation-analysis` are deleted from the repository (not moved, not kept).
- `factory/config/pre-commit-config.yaml` contains no test-related hooks.
- `factory/rulebooks/templates/charter-testing.yaml` exists as the template (schema defined by example).
- Factory's own `docs/charter/testing.yaml` declares its test commands.
- `block-dangerous-git.sh` reads the agent test allowlist from `docs/charter/testing.yaml`, matching all declared command fields (`test_command`, `test_staged_command`, `test_changed_command`) exactly.
- FSM gate conditions in `bug-fix.fsm.yml` and `greenfield-development.fsm.yml` resolve the test command from `docs/charter/testing.yaml`.
- The `detect-test-regime` skill identifies existing entrypoints from a broad detection surface and records the result in `docs/charter/testing.yaml`.
- When multiple test entrypoints are detected, Factory asks for disambiguation instead of guessing.
- UC-09 documents testing as project-owned infrastructure.
- ADR-0003 carries an amendment recording this design change.
- `factory/skills/mutation-analysis/SKILL.md` describes how to set up project-owned mutation testing, not a prescribed tool chain.
- prd.md, UC-10, ADR-0012, interface-contracts.md, validation-rules.md, and implementation-agent.md are updated to reference charter-declared commands instead of `factory/scripts/run-tests`. The implementation-agent no longer lists `factory/scripts/mutation-analysis` as an input, uses a two-gate default (`crap-score`, `dependency-check`), and does not invoke `mutation-analysis` in its gate execution section.
- The Gigacron reproducer (`make test` via Compose) works correctly when declared in `docs/charter/testing.yaml`.
- `remove-factory` leaves `docs/charter/testing.yaml` and project-owned test infrastructure intact.
- The `testing.yaml` template includes the `layers` section schema defined by example.
- `qa-strategy-from-spec` reads charter layer bindings when present and falls back to the Factory convention when absent.
- A per-feature QA strategy produced after this change traces every contract-owner assignment to a charter-declared layer when layer bindings are present.
- The mutation-analysis skill describes contract-ownership classification (`owner_held`, `owner_failed`, `uncaught`) for use when a QA strategy's contract-owner table is available.
- The developer-agent invokes `spec-feedback` when a test-harness mismatch is found during story implementation, naming the contract, prescribed layer, and concrete obstacle.
- The kit-manager populates layer bindings in `testing.yaml` during charter completeness sweep, and a human reviewer confirms the bindings match the repository's actual test infrastructure.

## Guiding Rule

Factory ensures test gates exist; the project decides what runs inside them. The Factory convention names the layers; the charter binds them to the project; the QA strategy maps contracts to those bindings; mutation analysis verifies the map holds; and mismatches flow backward, not into silence.

## Review — 2026-08-28

Reviewer: proposal-review-agent
Reviewed commit: 085ed8891cbfb83be26410cc0fee3e1501a77e64
Disposition: findings

### Findings

| ID      | Severity | Check  | Status   | Finding                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                      |
| ------- | -------- | ------ | -------- | ------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------ |
| PROP-01 | major    | 02, 03 | resolved | Design section 1 assumes init-factory copies run-tests individually, but init-factory symlinks the entire `factory/scripts/` directory (lines 58, 373-376 of init-factory). If run-tests "may remain in the Factory repository for Factory's own development tests," consumer projects still see it through the symlink. The Design must specify which resolution to use: delete the script from `factory/scripts/` entirely, move Factory's own copy outside `factory/scripts/`, or change the distribution mechanism. **Resolution**: script is deleted from the repository entirely. Factory uses the same `testing.yaml` mechanism as consumer projects. |
| PROP-02 | major    | 02     | resolved | Scope says "Update UC-09 and amend ADR-0003" but at least four other specification documents reference `factory/scripts/run-tests` by path: `prd.md` (FSM gate condition), UC-10 (BR-033 allowlist, acceptance criteria), `interface-contracts.md` (guardrail binding), and `validation-rules.md` (BR-024 allowlist description). Implementing without updating these leaves the specification internally inconsistent. **Resolution**: all six documents now listed in Design section 9 and in Scope.                                                                                                                                                       |
| PROP-03 | minor    | 03     | resolved | Design section 4 says `block-dangerous-git.sh` will "allowlist the declared commands" but does not specify WHICH declared commands are allowlisted (`test_command`, `test_staged_command`, `test_changed_command`, or all three), nor whether the match is exact or prefix-based. The current allowlist permits exactly one command for one use case (agent TDD iteration via `--staged`). The new allowlist needs the same precision. **Resolution**: all three fields allowlisted, exact match specified in Design section 5.                                                                                                                              |
| PROP-04 | minor    | 03     | resolved | Design section 6 specifies the detection surface but does not state where the detection code lives — a new Factory script, a skill, part of init-factory, or part of the kit-manager. A planning agent cannot write a story for this without deciding the artifact type and location. **Resolution**: new `detect-test-regime` skill, specified in Design section 7.                                                                                                                                                                                                                                                                                         |
| PROP-05 | minor    | 01     | resolved | Completion criterion 3 ("testing.yaml schema is defined and a template exists") does not specify where the schema definition or template lives, nor what "defined" means (prose, JSON Schema, example-only). The inline example in Design section 3 is insufficient for a planning agent to determine whether a formal schema artifact is required. **Resolution**: template at `factory/rulebooks/templates/charter-testing.yaml`, schema defined by example, no formal JSON Schema artifact. Specified in Design section 3 and Completion Criteria.                                                                                                        |
| PROP-06 | minor    | 04     | resolved | `impact.boundaries` omits files the proposal explicitly describes changing: `bug-fix.fsm.yml` and `greenfield-development.fsm.yml` (contain the `tests_pass` gate referencing `run-tests`), `init-factory` and `update-factory` (distribution scripts), and UC-10 (agent allowlist reference). **Resolution**: all missing boundaries added to frontmatter.                                                                                                                                                                                                                                                                                                  |

### Summary

All six findings resolved in the revision following the first review pass.

## Review — 2026-08-28 (repeat pass)

Reviewer: proposal-review-agent
Reviewed commit: 054432f92be8736cabe9ad5fa2093bb62141b7c7
Disposition: findings

### Prior findings

All six prior findings (PROP-01 through PROP-06) verified as resolved. The init-factory symlink concern (PROP-01) now covers both `run-tests` and `mutation-analysis`. The documentation scope (PROP-02) has been extended to seven documents including ADR-0012. The allowlist precision (PROP-03), detection skill location (PROP-04), template specification (PROP-05), and boundary completeness (PROP-06) all hold after the mutation-analysis additions.

### Eight-check results

1. **Completion criteria testable** — PASS. All 14 criteria are mechanically verifiable.
2. **Scope boundary sharp** — PASS with one minor finding (PROP-09). The In/Deferred partition is clear except for init-factory wiring.
3. **Design decomposable** — PASS with three minor findings (PROP-07, PROP-08, PROP-10). Design is decomposable overall, but the documentation update descriptions in section 9 understate the scope of changes needed for three files.
4. **Impact classification consistent** — PASS. `cross_component`, `architecture_change: true`, `external_contract_change: true` all match the Design.
5. **Boundary references exist** — PASS. All 16 paths resolve at the reviewed commit.
6. **Open questions genuine** — PASS. Three questions resolved with concrete design decisions; no padding.
7. **Motivation justifies timing** — PASS. Concrete reproducer (Gigacron) with demonstrated failure.
8. **Estimate plausible** — PASS. Uses `unknown` for token estimates; human review hours (1-2h) reasonable for the scope.

### Findings

| ID      | Severity | Check | Status | Finding                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                          |
| ------- | -------- | ----- | ------ | -------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| PROP-07 | minor    | 03    | open   | Design section 9 understates prd.md update scope. It says "update FSM gate condition references from factory/scripts/run-tests to charter-resolved test_command" but prd.md's G9 (goal statement naming run-tests) and FR-I (six sub-requirements describing auto-detection, modes, JSON summary, and gate invocation) all need substantial revision or removal. A planning agent reading "update FSM gate condition references" would undersize the prd.md story, leaving G9 and FR-I1 through FR-I6 describing the deleted script's behavior.                                                                                  |
| PROP-08 | minor    | 03    | open   | Design section 9 understates validation-rules.md update scope. It says "update BR-024 allowlist description from hardcoded path to charter-declared commands" but the Test execution section contains BR-023 through BR-029 (seven business rules). BR-023 (framework detection), BR-025 (--changed-only mode), BR-026 (--full mode), BR-027 (JSON summary), BR-028 (--staged mode), and BR-029 (pre-commit trigger conditions) all describe deleted or obsolete behavior, not just BR-024.                                                                                                                                      |
| PROP-09 | minor    | 02    | open   | Scope does not explicitly state init-factory modification. Design section 7 says detect-test-regime is "invoked by init-factory," and init-factory is a boundary file, but the scope list says only "Create the detect-test-regime skill for use during onboarding." A planning agent cannot determine from scope alone whether wiring the skill into init-factory is part of skill creation or a separate story.                                                                                                                                                                                                                |
| PROP-10 | minor    | 03    | open   | Design section 9 understates ADR-0012 update scope. It says "update mutation-analysis invocation references from factory/scripts/mutation-analysis to project-owned mutation testing," but the dispatcher's three-gate sequence (crap-score, mutation-analysis, dependency-check) loses its second gate with no charter-based replacement. The actual change removes a gate from the dispatcher's quality loop — an architectural change to the gate sequence, not a reference update. The Design should state whether the sequence becomes two gates or whether a project-declared mutation command is conditionally evaluated. |

### Summary

All six prior findings (PROP-01 through PROP-06) remain resolved. The mutation-analysis scope expansion is internally consistent at the boundary and completion-criteria level. Four new minor findings identify places where Design section 9's documentation update descriptions understate the actual scope of changes needed — particularly for prd.md (G9 and FR-I revision), validation-rules.md (BR-023 through BR-029 revision), and ADR-0012 (gate sequence architectural change). One scope-boundary finding (PROP-09) asks for explicit init-factory wiring in the scope list. No major findings. The proposal is close to planning-ready; addressing the four minor findings would make the documentation update stories precisely sizeable.

## Review — 2026-08-28 (third pass, post-scope-expansion)

Reviewer: proposal-review-agent
Reviewed commit: c36544dbb2e9acd17226610d95cfd9ac2f7b9516
Disposition: findings

### Prior findings

All ten prior findings (PROP-01 through PROP-10) verified as resolved at the reviewed commit. The scope expansion that folded in the contract-traced-testing-strategy proposal did not reopen any prior finding. Specifically:

- PROP-01 (init-factory symlink): still resolved — Design section 1 deletes both `run-tests` and `mutation-analysis` entirely.
- PROP-02 (documentation scope): still resolved — Design section 9 now lists seven documents, including the three added for the mutation-analysis expansion.
- PROP-03 (allowlist precision): still resolved — Design section 5 specifies all three fields with exact matching.
- PROP-04 (detection skill location): still resolved — Design section 7 specifies the `detect-test-regime` skill.
- PROP-05 (template specification): still resolved — template at `factory/rulebooks/templates/charter-testing.yaml`, schema by example.
- PROP-06 (boundary completeness): still resolved for the 16 original files. The expanded scope added three new boundary files (`factory/skills/qa-strategy-from-spec/SKILL.md`, `factory/agents/kit-manager.md`, `factory/agents/developer-agent.md`), bringing the total to 19. One additional affected artifact is undeclared (PROP-11).
- PROP-07 (prd.md update scope): still resolved — Design section 9 now names G9 and FR-I1 through FR-I6 explicitly.
- PROP-08 (validation-rules.md update scope): still resolved — Design section 9 now names BR-023 through BR-029.
- PROP-09 (init-factory wiring in scope): still resolved — Scope now says "wire it into init-factory."
- PROP-10 (ADR-0012 gate sequence change): still resolved — Design section 9 now describes the architectural change from three gates to two.

### Eight-check results

1. **Completion criteria testable** — PASS. All 21 criteria are mechanically verifiable without asking the author. The seven new criteria (15–21) added for the expanded scope follow the same precision standard as the original fourteen.
2. **Scope boundary sharp** — PASS. The In/Deferred partition cleanly separates what ships from what does not. The boundary between "kit-manager populates layer bindings from existing infrastructure" (In) and "full kit-manager onboarding interview for building test infrastructure from scratch" (Deferred) is clear from the design text. The boundary between "file-path-level mutation-to-contract join" (In) and "function-level or AST-level mapping" (Deferred) is mechanically decidable.
3. **Design decomposable** — PASS. Design sections 10–13 are specific enough for Planning to write INVEST stories: section 10 includes the YAML schema by example, section 11 specifies the two new inputs and the Step 3 change, section 12 names the trigger condition and mechanism, and section 13 defines the three classification statuses and the join method.
4. **Impact classification consistent** — PASS. `cross_component`, `architecture_change: true`, `external_contract_change: true` all match the expanded Design. The scope expansion strengthens each classification: charter layer bindings add cross-component reach, the ADR-0012 gate sequence change is architectural, and the QA strategy and developer-agent workflow changes affect external contracts.
5. **Boundary references exist** — FAIL. All 19 declared paths resolve at the reviewed commit. However, one directly affected artifact is undeclared (PROP-11).
6. **Open questions genuine** — PASS. All questions are resolved with concrete design decisions. The expanded scope introduces no new unresolved questions. The superseded proposal's question about whether testing bindings should live in their own file or in `development.md` is resolved in the Open Questions section.
7. **Motivation justifies timing** — PASS with one minor finding (PROP-12). The Gigacron reproducer and boundary-violation argument are strong for the original scope. The expanded scope's timing justification is present in the Summary but absent from the Motivation section.
8. **Estimate plausible** — PASS. Token estimates use `unknown`, which is honest given the scope growth from 10 to 14 In-scope items, 16 to 19 boundary files, 14 to 21 completion criteria, and 29 to 42 feature scenarios. Human review hours (1.0–2.0h) are tight for a cross-component change at this scale but not implausible.

### Findings

| ID      | Severity | Check | Status | Finding                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                  |
| ------- | -------- | ----- | ------ | -------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| PROP-11 | major    | 05    | open   | `factory/agents/implementation-agent.md` is missing from `impact.boundaries` and from the Scope. The implementation-agent lists `factory/scripts/mutation-analysis` as an input (line 28), references the three-gate hardcoded default including `mutation-analysis` (line 129), and shows the `mutation-analysis` CLI invocation in its gate execution section (line 137). This agent is the artifact that executes the gate sequence described in ADR-0012. Deleting the script and amending the ADR without updating the implementation-agent leaves it referencing a deleted script and a superseded three-gate sequence. A planning agent would not generate a story for this update without the boundary reference. The implementation-agent needs: (a) `factory/scripts/mutation-analysis` removed from `inputs:`, (b) the hardcoded default changed to two gates, (c) the `mutation-analysis` CLI invocation removed from the gate execution section, and (d) a Scope item covering this update. |
| PROP-12 | minor    | 07    | open   | The Motivation section justifies only the original scope (Gigacron reproducer, boundary violation in `run-tests`) but not the expanded scope (Design sections 10–13). The Summary mentions a "traceability gap in the QA strategy derivation chain," but the Motivation section — where the template says "Why now" belongs — does not argue why charter layer bindings, QA strategy grounding, developer-agent feedback, and mutation-analysis classification must ship in this release rather than in a follow-up. The `supersedes` field references `contract-traced-testing-strategy.md`, but the Motivation should stand on its own without requiring the reader to locate the superseded proposal's rationale.                                                                                                                                                                                                                                                                                     |

### Summary

All ten prior findings (PROP-01 through PROP-10) remain resolved. The scope expansion from folding in the contract-traced-testing-strategy proposal is internally consistent at the Design, Scope, completion-criteria, and feature-file level — Design sections 10–13 are decomposable, the 21 completion criteria are testable, and 42 feature scenarios cover the full scope. One major finding: the implementation-agent — the artifact that executes the gate sequence being changed — is missing from boundaries and scope (PROP-11). One minor finding: the Motivation section does not justify the timing for the expanded scope (PROP-12). Address PROP-11 before planning; PROP-12 is a documentation gap that does not block planning.

## Review — 2026-08-28 (fourth pass)

Reviewer: proposal-review-agent
Reviewed commit: 671315705204e812a51cb8f308b7c56b004aa7e4
Disposition: findings

### Prior findings

All twelve prior findings (PROP-01 through PROP-12) verified as resolved at the reviewed commit.

- PROP-01 through PROP-10: remain resolved. No changes to the sections they addressed between the third review commit and the current HEAD.
- PROP-11 (major, check 05): RESOLVED. `factory/agents/implementation-agent.md` added to `impact.boundaries` (line 35 of frontmatter). Design section 9 includes a specific entry describing three changes: remove `factory/scripts/mutation-analysis` from `inputs:`, change three-gate default to two gates (`crap-score`, `dependency-check`), remove `mutation-analysis` CLI invocation from the gate execution section. Scope list updated to include `implementation-agent.md`. The actual implementation-agent.md confirms the references exist at lines 28, 129, and 137 as described.
- PROP-12 (minor, check 07): RESOLVED. Motivation section now includes a paragraph arguing that the charter declaration and QA strategy traceability share the same fix point, and shipping one without the other creates a new source of truth that nothing consumes — a genuine "why now" argument for the expanded scope.

### Eight-check results

1. **Completion criteria testable** — PASS with one minor finding (PROP-13). All 20 criteria are mechanically verifiable without asking the author. However, the implementation-agent update described in Design section 9 and listed in Scope has no corresponding completion criterion.
2. **Scope boundary sharp** — PASS. The In/Deferred partition cleanly separates what ships from what does not. All 14 In-scope items are mechanically distinguishable from the 8 Deferred items.
3. **Design decomposable** — PASS. All 13 Design sections are specific enough for Planning to write INVEST stories without re-deriving the design.
4. **Impact classification consistent** — PASS. `cross_component`, `architecture_change: true`, `external_contract_change: true` all match the Design. The 20 boundary files span scripts, config, skills, agents, ADRs, specs, and playbooks — consistent with cross-component scope.
5. **Boundary references exist** — PASS. All 20 declared paths resolve at the reviewed commit.
6. **Open questions genuine** — PASS. All questions resolved with concrete design decisions. No padding.
7. **Motivation justifies timing** — PASS. The Gigacron reproducer provides a concrete failure for the original scope. The new Motivation paragraph justifies the expanded scope with a shared-fix-point argument.
8. **Estimate plausible** — PASS. Token estimates use `unknown`, which is honest given the 20-boundary, 14-item scope. Human review hours (1.0–2.0h) are tight but not implausible at `medium` confidence with `judgment` basis.

### Findings

| ID      | Severity | Check | Status   | Finding                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                      |
| ------- | -------- | ----- | -------- | ---------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| PROP-11 | major    | 05    | resolved | `factory/agents/implementation-agent.md` added to boundaries, Design section 9, and Scope. The three specific changes (remove mutation-analysis input, change three-gate to two-gate default, remove CLI invocation) are accurately described.                                                                                                                                                                                                                                                                                                                                                                                                                                                                               |
| PROP-12 | minor    | 07    | resolved | Motivation section now justifies the expanded scope timing with a shared-fix-point argument.                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                 |
| PROP-13 | minor    | 01    | open     | The implementation-agent update is in the Scope and described with three specific changes in Design section 9 but has no corresponding completion criterion. The documentation-update criterion (criterion 12) names prd.md, UC-10, ADR-0012, interface-contracts.md, and validation-rules.md — five documents. UC-09 and ADR-0003 have separate criteria. The implementation-agent is the eighth document in the Scope's documentation update list with no verifiable completion check. The changes it requires (remove an input, change a gate count, remove a CLI invocation) are structurally different from the five documents in criterion 12 (which update references from `run-tests` to charter-declared commands). |

### Summary

All twelve prior findings (PROP-01 through PROP-12) are resolved. One new minor finding: the implementation-agent update has no completion criterion (PROP-13). All eight checks pass, with PROP-13 the sole open item. The proposal is planning-ready once the implementation-agent completion criterion is added — a one-line addition to the Completion Criteria section.
