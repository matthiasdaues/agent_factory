---
schema_version: 2
title: "Test Gate Presence over Test Execution"
status: draft
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
    - docs/adr/0003-test-execution-via-hooks.md
    - factory/scripts/run-tests
    - factory/config/pre-commit-config.yaml

governance:
  assurance: elevated
  risk_domains:
    - reliability
    - compatibility

estimate:
  as_of: 2026-08-28
  basis: judgment
  confidence: low
  human_review_hours:
    min: 1.0
    max: 2.0
  normalized_tokens: unknown
  estimated_consumption: unknown
---

# Feature Request: Test Gate Presence over Test Execution

## Summary

Factory must ensure that test gates fire at the right moments (pre-commit, pre-push, phase advance) without owning the test command itself. When a consumer project already has a test regime, Factory defers to it. When a project has no coherent test regime, Factory helps the user build one through kit-manager onboarding. Factory never constructs a host-side test command from marker-file heuristics and runs it against project code.

## Motivation

The current `factory/scripts/run-tests` detects framework markers (`pyproject.toml`, `package.json`, `go.mod`, `Cargo.toml`) and constructs host-side test commands (`uv run pytest`, `npm test`, etc.). This works only when the project's tests happen to run on the host with no special topology.

It breaks when the project has its own test infrastructure. The reproducing case is Gigacron: its tests require a Compose environment where `toxiproxy:15432` resolves. The project's entrypoint is `make test` → `./run-dev.sh test` → `docker compose exec app uv run pytest`. Factory's `run-tests` detects `pyproject.toml`, fires `uv run pytest` on the host, and the session migration fixture explodes because the database proxy is unreachable.

The root cause is a boundary violation: Factory imposes its own test execution strategy on the consumer project instead of serving the project's. This contradicts Factory's role as infrastructure that assists consumer projects without owning their runtime topology.

## Core Principles

- Factory owns test gate presence, not test execution. Its job is to ensure gates fire at the right hook points using whatever the project already has.
- A project's declared test entrypoint takes absolute precedence. Factory never wraps, reinterprets, or substitutes it.
- When no test regime exists, Factory surfaces the gap during onboarding and helps the user build one — a real setup designed for the project's topology, not a shim.
- The gate contract is exit-code-only: zero means pass, nonzero means fail. Structured test counts are the project's concern.

## Design

### What changes

1. **`run-tests` as a universal framework-detecting wrapper goes away.** The script's current framework detection logic — scanning for marker files and constructing host-side commands — is the wrong abstraction. It encodes the assumption that Factory knows how to run a project's tests. It does not.

2. **Project test entrypoint detection replaces framework detection.** Factory looks for evidence that the project already has a test regime:

   - `Makefile` with a `test` target
   - `package.json` with a `test` script
   - `tox.ini` or `tox` section in `pyproject.toml`
   - `noxfile.py`
   - `Justfile` with a `test` recipe
   - `Taskfile.yml` with a `test` task
   - Other conventional entrypoints as the detection surface grows

   The detection surface should be as broad as possible. When a project entrypoint is found, Factory wires its hooks to trigger it. When none is found, the hook reports "no project test strategy detected" and exits 2.

3. **Kit-manager onboarding gains a test-regime checkpoint.** During onboarding, kit-manager detects whether the project has a test regime. If it does, kit-manager records it and wires Factory's hooks to trigger it. If it does not, kit-manager raises the gap and helps the user establish one — including mode support (changed-only, full, staged) designed for the project's actual topology.

4. **Mode flags degrade gracefully.** If the project's test entrypoint supports modes, Factory passes them through. If it does not, Factory runs the entrypoint as-is. The project owns its mode story; Factory does not reinvent it.

5. **The JSON summary contract relaxes.** The gate contract becomes exit-code-based: exit 0 = pass, nonzero = fail, duration emitted when measurable. Structured counts (`passed`, `failed`, `skipped`) become optional — present when the project entrypoint provides them, absent otherwise.

6. **UC-09 and ADR-0003 are updated** to reflect the new precedence: project entrypoint first, no Factory-constructed fallback.

### What stays

- The hook integration points (pre-commit, pre-push, phase advance) remain unchanged.
- Agent prohibition on bare test commands (BR-024, `block-dangerous-git.sh`) remains unchanged.
- `factory/scripts/run-tests --staged` as the agent iteration affordance remains, but delegates to the project entrypoint.
- Exit code semantics (0 = pass, 1 = test failure, 2 = configuration error) remain unchanged.

## Scope

**In the first release:**

- Remove framework auto-detection and host-side command construction from `run-tests`.
- Implement project test entrypoint detection (broad detection surface).
- Wire hooks to trigger the detected project entrypoint.
- Relax JSON summary contract to exit-code-only gating.
- Update UC-09 to reflect the new precedence.
- Update ADR-0003 with an amendment documenting this design change.
- Update `factory/config/pre-commit-config.yaml` hook entries.

**Explicitly deferred (do NOT plan stories for these):**

- Kit-manager test-regime onboarding checkpoint — requires separate design work on the kit-manager interview flow.
- Factory distribution boundary fix (the separate defect that copies Factory development tests into consumer workspaces).
- Multi-framework project support (already deferred as T-06).
- Structured test output parsing from project entrypoints.

## Open Questions

- Should the detection order imply precedence when multiple entrypoints exist (e.g., both a Makefile `test` target and a `tox.ini`)? Or should Factory fail loudly, as it does today with multiple framework markers?
- Should Factory support an explicit override (e.g., `[tool.factory] test_command = "make test"`) so the user can declare the entrypoint without relying on detection?
- How should `--changed-only` and `--staged` behave when the detected project entrypoint has no corresponding mode? Silent full-run, or exit 2 with a message suggesting the user configure modes?

## Completion Criteria

- `run-tests` delegates to a detected project test entrypoint without constructing its own test command.
- A consumer project with a `Makefile` `test` target has its tests triggered correctly by Factory's pre-push hook.
- A consumer project with no detectable test entrypoint receives a clear "no project test strategy detected" error (exit 2), not a Factory-guessed command.
- UC-09 documents the new precedence: project entrypoint first, no framework-detection fallback.
- ADR-0003 carries an amendment recording the design change and its rationale.
- The Gigacron reproducer (`make test` via Compose) passes through Factory's pre-push gate without topology mismatch.

## Guiding Rule

Factory triggers the project's tests; it never decides how they run.
