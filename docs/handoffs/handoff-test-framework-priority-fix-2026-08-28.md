• # Phase Handoff

## Boundary

Outgoing phase: planning
Incoming phase: implementation
Boundary: planning -> implementation

## Repository state

Checkout: /home/matthiasdaues/Documents/datenschoenheit/agent_factory
Branch: dev
HEAD: bc92ba14fbeb59281f4614f4bbb0582072ba3e40
Upstream: agent_factory/dev
Upstream SHA: bc92ba14fbeb59281f4614f4bbb0582072ba3e40
Ahead: 0
Behind: 0
Working tree: user-owned modifications to `docs/proposals/newcomer-onboarding-and-incremental-brownfield.md`, `docs/spec/supplementary_specs/entity-   model.md`, `docs/spec/supplementary_specs/validation-rules.md`, `docs/spec/todos.md`, and `docs/spec/traceability.json`; user-owned untracked files `docs/   spec/newcomer-onboarding-gaps.md`, `docs/spec/newcomer-onboarding-qa-strategy.md`, `docs/spec/newcomer-onboarding.feature`, and `docs/spec/scope-map.md`;
this handoff is the only run-tests planning addition
Retained work: sole worktree on `dev`; the listed specification changes are unrelated user work and must not be reverted, reformatted wholesale, staged, or
committed with the run-tests change

## Decisions and open items

Decisions: `factory/scripts/run-tests` MUST defer to a pre-existing project test configuration because Factory assists consumer projects and does not own
their runtime topology. A project-declared test entrypoint takes precedence over framework inference. Framework auto-detection remains a fallback only when
no project entrypoint exists.

For the reproducing Gigacron consumer at `/home/matthiasdaues/Documents/repos/dt_vf/giga-x/gigacron/gigacron`, `make test` is the authoritative entrypoint.
It delegates to `./run-dev.sh test`, which executes pytest inside the Compose `app` container where `toxiproxy:15432` resolves.

The current Factory runner detects `pyproject.toml` and executes host-side `uv run pytest --tb=short --quiet`. Consequently, Gigacron’s pre-push check fails
during the session migration fixture before tests execute.

The change must:

- Be developed test-first through the public `factory/scripts/run-tests` CLI.
- Preserve selected command exit codes.
- Preserve the documented JSON summary contract.
- Update [UC-09](../spec/use_cases/UC-09-run-tests-via-hook.md) and [ADR-0003](../adr/0003-test-execution-via-hooks.md) where their documented precedence
  contradicts this requirement.
- Keep framework inference as a compatibility fallback.
- Avoid absorbing consumer-project environment knowledge into Factory.

Open items:

- Define the smallest deterministic precedence set, beginning with an existing Make `test` target.
- Decide whether current evidence requires support for additional standard project runners such as tox, nox, Just, or Task, or whether those should remain
  deferred.
- Define how `--full`, `--changed-only`, and `--staged` behave when the selected project entrypoint exposes no corresponding modes. Correct project
  execution takes precedence over silently substituting Factory-generated commands.
- Identify or add the owning integration-style tests for the `run-tests` CLI.
- Update installed-copy documentation and templates consistently.
- Do not address the separate Factory distribution defect that copies Factory development tests and fixtures into consumer workspaces as part of this
  change.

## Artifacts

- docs/handoffs/run-tests-project-entrypoint-2026-08-28.md
- factory/scripts/run-tests
- factory/config/pre-commit-config.yaml
- factory/README.md
- docs/spec/use_cases/UC-09-run-tests-via-hook.md
- docs/adr/0003-test-execution-via-hooks.md

## Gate and verification evidence

Gates: structural handoff lint and semantic review are pending because this draft has not yet been placed in the Factory checkout; no implementation gates
have run because no production or test code has changed

Verification:

- Gigacron standalone `.venv/bin/pytest -x -vv --tb=long` collected 86 tests and failed in the session migration fixture with `psycopg.OperationalError: failed to resolve host 'toxiproxy'`.
- An explicit infrastructure-free selection passed 66 tests.
- `docker compose ps --format json` showed no running services.
- Gigacron `run-dev.sh` line 385 defines the supported test command as `docker compose exec app uv run pytest`.
- Gigacron’s `Makefile` defines `test` as `./run-dev.sh test`.
- Factory `run-tests` currently maps pytest full mode to host-side `uv run pytest --tb=short --quiet`.
- The failure is therefore runner-topology mismatch, not a failing Gigacron assertion.
