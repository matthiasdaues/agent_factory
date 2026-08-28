---
schema_version: 2
title: "Test Gate Presence over Test Execution"
status: open
owner: Matthias Daues
created: 2026-08-28
updated: 2026-08-28
supersedes:

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

Factory must stop owning test execution — in consumer projects and in its own repository. The current `factory/scripts/run-tests` detects framework markers and constructs host-side test commands, a boundary violation that breaks projects with their own test topology. The same boundary violation applies to `factory/scripts/mutation-analysis`, which hardcodes mutmut with pytest internals and cannot reach test infrastructure that runs inside containers or custom runners. Instead, testing becomes entirely project-owned infrastructure: every project (including Factory itself) declares its test commands in `docs/charter/testing.yaml`, Factory's guardrails and FSM gates read that declaration, and `init-factory` stops injecting any test-related hooks into `.pre-commit-config.yaml`. Both `run-tests` and `mutation-analysis` are deleted from the repository. The `mutation-analysis` skill is retained as guidance for setting up project-owned mutation testing, but the script that imposed a specific tool and runner is removed. When a project has no test regime, Factory helps build project-owned test infrastructure during onboarding, infrastructure that survives `remove-factory`.

## Motivation

The current `factory/scripts/run-tests` detects framework markers (`pyproject.toml`, `package.json`, `go.mod`, `Cargo.toml`) and constructs host-side test commands (`uv run pytest`, `npm test`, etc.). This works only when the project's tests happen to run on the host with no special topology.

It breaks when the project has its own test infrastructure. The reproducing case is Gigacron: its tests require a Compose environment where `toxiproxy:15432` resolves. The project's entrypoint is `make test` → `./run-dev.sh test` → `docker compose exec app uv run pytest`. Factory's `run-tests` detects `pyproject.toml`, fires `uv run pytest` on the host, and the session migration fixture explodes because the database proxy is unreachable.

The root cause is a boundary violation: Factory imposes its own test execution strategy on the consumer project instead of serving the project's. This contradicts Factory's role as infrastructure that assists consumer projects without owning their runtime topology.

## Core Principles

- Factory owns structural gates (linting, formatting, spec consistency, architecture consistency, phase ordering). Testing is the project's domain.
- Test infrastructure must be project-owned and must survive `remove-factory`. This applies to consumer projects and to Factory itself.
- Code is the source of truth for what test regime exists. The charter is a derived record, not the detection mechanism.
- When multiple plausible test entrypoints exist, Factory asks for disambiguation rather than guessing.
- The gate contract is exit-code-only: zero means pass, nonzero means fail. Structured test counts are the project's concern.

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
- **prd.md** (`docs/spec/prd.md`): update FSM gate condition references from `factory/scripts/run-tests` to charter-resolved `test_command`.
- **UC-10** (`docs/spec/use_cases/UC-10-invoke-a-factory-agent-under-pi.md`): update BR-033 allowlist reference and acceptance criteria from `factory/scripts/run-tests --staged` to charter-declared `test_staged_command`.
- **interface-contracts.md** (`docs/spec/supplementary_specs/interface-contracts.md`): update guardrail binding references.
- **validation-rules.md** (`docs/spec/supplementary_specs/validation-rules.md`): update BR-024 allowlist description from hardcoded path to charter-declared commands.
- **ADR-0012** (`docs/adr/0012-dispatcher-owned-semantic-gate-loop.md`): update mutation-analysis invocation references from `factory/scripts/mutation-analysis` to project-owned mutation testing.

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
- Create the `detect-test-regime` skill for use during onboarding.
- Rewrite `factory/skills/mutation-analysis/SKILL.md` as setup guidance rather than a prescribed tool chain.
- Update UC-09, ADR-0003, ADR-0012, prd.md, UC-10, interface-contracts.md, and validation-rules.md.

**Explicitly deferred (do NOT plan stories for these):**

- Full kit-manager onboarding interview for building test infrastructure from scratch — requires separate design work on the onboarding flow.
- Factory distribution boundary fix (the separate defect that copies Factory development tests into consumer workspaces via the symlinked `factory/` directory).
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
- prd.md, UC-10, ADR-0012, interface-contracts.md, and validation-rules.md are updated to reference charter-declared commands instead of `factory/scripts/run-tests`.
- The Gigacron reproducer (`make test` via Compose) works correctly when declared in `docs/charter/testing.yaml`.
- `remove-factory` leaves `docs/charter/testing.yaml` and project-owned test infrastructure intact.

## Guiding Rule

Factory ensures test gates exist; the project decides what runs inside them.

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
