---
schema_version: 2
title: "Test Gate Presence over Test Execution"
status: open
owner: Matthias Daues
created: 2026-08-28
updated: 2026-08-28  # grilling complete, moved to open
supersedes:

impact:
  scope: cross_component
  architecture_change: true
  external_contract_change: true
  boundaries:
    - docs/spec/use_cases/UC-09-run-tests-via-hook.md
    - docs/adr/0003-test-execution-via-hooks.md
    - factory/scripts/run-tests
    - factory/config/pre-commit-config.yaml
    - factory/config/hooks/block-dangerous-git.sh

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

Factory must stop owning test execution in consumer projects. The current `factory/scripts/run-tests` detects framework markers and constructs host-side test commands — a boundary violation that breaks projects with their own test topology. Instead, testing becomes entirely project-owned infrastructure: the project declares its test commands in `docs/charter/testing.yaml`, Factory's guardrails and FSM gates read that declaration, and `init-factory` stops injecting any test-related hooks into `.pre-commit-config.yaml`. When a project has no test regime, Factory helps build project-owned test infrastructure during onboarding — infrastructure that survives `remove-factory`.

## Motivation

The current `factory/scripts/run-tests` detects framework markers (`pyproject.toml`, `package.json`, `go.mod`, `Cargo.toml`) and constructs host-side test commands (`uv run pytest`, `npm test`, etc.). This works only when the project's tests happen to run on the host with no special topology.

It breaks when the project has its own test infrastructure. The reproducing case is Gigacron: its tests require a Compose environment where `toxiproxy:15432` resolves. The project's entrypoint is `make test` → `./run-dev.sh test` → `docker compose exec app uv run pytest`. Factory's `run-tests` detects `pyproject.toml`, fires `uv run pytest` on the host, and the session migration fixture explodes because the database proxy is unreachable.

The root cause is a boundary violation: Factory imposes its own test execution strategy on the consumer project instead of serving the project's. This contradicts Factory's role as infrastructure that assists consumer projects without owning their runtime topology.

## Core Principles

- Factory owns structural gates (linting, formatting, spec consistency, architecture consistency, phase ordering). Testing is the project's domain.
- Test infrastructure in a consumer project must be project-owned and must survive `remove-factory`.
- Code is the source of truth for what test regime exists. The charter is a derived record, not the detection mechanism.
- When multiple plausible test entrypoints exist, Factory asks for disambiguation rather than guessing.
- The gate contract is exit-code-only: zero means pass, nonzero means fail. Structured test counts are the project's concern.

## Design

### 1. Remove `factory/scripts/run-tests` from the consumer distribution

The script's framework detection logic — scanning for marker files and constructing host-side commands — encodes the assumption that Factory knows how to run a project's tests. It does not. The script is removed from consumer projects entirely. It may remain in the Factory repository for Factory's own development tests, but `init-factory` and `update-factory` no longer copy it.

### 2. Remove the test hook from Factory's pre-commit config

The `agent_factory_hook-run-tests-full` entry in `factory/config/pre-commit-config.yaml` is removed. Factory stops injecting any test-related hook into `.pre-commit-config.yaml`. Testing hooks are project-owned: either the project already has them, or Factory helps build them during onboarding.

### 3. Introduce `docs/charter/testing.yaml`

A machine-readable file declaring the project's test commands. This is the first charter section to migrate from prose to structured YAML — setting a pattern for incremental charter migration as concrete consumers demand machine-readable access.

Minimal schema:

```yaml
test_command: "make test"
test_staged_command: "make test-staged"  # optional
test_changed_command: "make test-changed"  # optional
```

Fields are project-defined commands, not framework names. Optional mode commands are absent when the project's test entrypoint has no corresponding mode.

### 4. `block-dangerous-git.sh` reads the charter for the agent allowlist

The guardrail currently hardcodes `factory/scripts/run-tests --staged` as the sanctioned agent test path (BR-024). This changes to reading `docs/charter/testing.yaml` and allowlisting the declared commands. The agent uses whatever the project declared — Factory owns the guardrail logic, the project owns the command.

When `remove-factory` runs, the guardrail is removed. Bare test commands become available again, and the project's declared test commands remain as regular project scripts.

### 5. FSM gate conditions reference the charter-declared command

Playbook FSMs (`bug-fix.fsm.yml`, `greenfield-development.fsm.yml`) currently reference `factory/scripts/run-tests --full` as a `script_exit_zero` gate condition. This changes to resolving the test command from `docs/charter/testing.yaml`. If the charter has no `test_command`, the gate reports the gap and blocks advancement.

### 6. Test regime detection during onboarding

When Factory onboards a project, it scans for evidence that a test regime already exists:

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

### 7. Mode handling

Factory calls the project's test entrypoint as-is. It does not engineer mode flags, warn about missing modes, or substitute its own mode logic. If the project's entrypoint supports modes, the project wires them. If it does not, the entrypoint runs however it runs. The project owns its mode story.

### 8. Documentation updates

- **UC-09**: rewrite to reflect that testing is project-owned infrastructure triggered by project-owned hooks, with Factory's role limited to guardrail enforcement (agent test prohibition) and FSM gate evaluation via the charter declaration.
- **ADR-0003**: amend to record this design change — Factory no longer owns test execution, only structural gates. The "Agentic Creation, Deterministic Validation" principle still holds, but the validation mechanism for tests is project-owned, not Factory-owned.

### What stays

- Agent prohibition on bare test commands (BR-024) remains. `block-dangerous-git.sh` still blocks bare `pytest`, `npm test`, etc. — the allowlist source changes from a hardcoded path to the charter declaration.
- Exit code semantics for gates (0 = pass, 1 = test failure, 2 = configuration error) remain unchanged.
- Factory's structural hooks (mdformat, ruff, spec-lint, arch-lint, transition-lint, etc.) are unaffected.

## Scope

**In the first release:**

- Remove `factory/scripts/run-tests` from the consumer distribution (`init-factory`, `update-factory`).
- Remove `agent_factory_hook-run-tests-full` from `factory/config/pre-commit-config.yaml`.
- Define the `docs/charter/testing.yaml` schema and create the template.
- Update `block-dangerous-git.sh` to read the agent test allowlist from `docs/charter/testing.yaml`.
- Update FSM gate evaluation to resolve the test command from `docs/charter/testing.yaml`.
- Implement test regime detection scan (broad surface) for use during onboarding.
- Update UC-09 and amend ADR-0003.

**Explicitly deferred (do NOT plan stories for these):**

- Full kit-manager onboarding interview for building test infrastructure from scratch — requires separate design work on the onboarding flow.
- Factory distribution boundary fix (the separate defect that copies Factory development tests into consumer workspaces).
- Incremental migration of other charter sections from prose to YAML.
- Structured test output parsing.

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

No remaining open questions.

## Completion Criteria

- `factory/scripts/run-tests` is absent from consumer projects after `init-factory`.
- `factory/config/pre-commit-config.yaml` contains no test-related hooks.
- `docs/charter/testing.yaml` schema is defined and a template exists.
- `block-dangerous-git.sh` reads the agent test allowlist from `docs/charter/testing.yaml` instead of hardcoding `factory/scripts/run-tests --staged`.
- FSM gate conditions resolve the test command from `docs/charter/testing.yaml` instead of referencing `factory/scripts/run-tests`.
- Test regime detection scan identifies existing entrypoints from a broad detection surface and records the result in `docs/charter/testing.yaml`.
- When multiple test entrypoints are detected, Factory asks for disambiguation instead of guessing.
- UC-09 documents testing as project-owned infrastructure.
- ADR-0003 carries an amendment recording this design change.
- The Gigacron reproducer (`make test` via Compose) works correctly when declared in `docs/charter/testing.yaml`.
- `remove-factory` leaves `docs/charter/testing.yaml` and project-owned test infrastructure intact.

## Guiding Rule

Factory ensures test gates exist; the project decides what runs inside them.
