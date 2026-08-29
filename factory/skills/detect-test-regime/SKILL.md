---
name: detect-test-regime
title: Detect Test Regime
description: >-
  Scan project for test entrypoints and record the result in
  docs/charter/testing.yaml. Code is the source of truth; the charter
  is a derived record.
inputs:
  - Makefile
  - package.json
  - pyproject.toml
  - tox.ini
  - noxfile.py
  - Justfile
  - Taskfile.yml
  - conftest.py
  - tests/
  - test/
outputs:
  - docs/charter/testing.yaml
version: 0.1.0
---

# Detect Test Regime

Scan the project for evidence that a test regime exists, then write or
update `docs/charter/testing.yaml` with what was found. Code is the source
of truth — the charter is a derived record, not the other way around. Never
invent a `test_command` the project cannot actually run.

## When to use this skill

- During `init-factory`, to seed the testing charter from an existing
  codebase.
- During brownfield onboarding, when `kit-manager` needs to know how a
  project runs its tests before scaffolding gates around it.
- Whenever `docs/charter/testing.yaml` is missing, empty, or suspected
  stale against the current repository.

## Workflow

### 1. Scan for test entrypoints

Check the project root for each of the following, in this order. Stop
recording candidates only after checking all of them — do not short-circuit
on the first hit, since disambiguation in step 2 needs the full set.

| Entrypoint                    | Evidence                                                  |
| ----------------------------- | --------------------------------------------------------- |
| `Makefile` `test` target      | A `test:` rule in `Makefile`                              |
| `package.json` `test` script  | A `"test"` key under `"scripts"` in `package.json`        |
| `tox`                         | `tox.ini`, or a `[tool.tox]` section in `pyproject.toml`  |
| `nox`                         | `noxfile.py`                                              |
| `Justfile` `test` recipe      | A `test:` recipe in `Justfile`                            |
| `Taskfile.yml` `test` task    | A `test:` task under `tasks:` in `Taskfile.yml`           |
| `pytest` via `pyproject.toml` | A `[tool.pytest.ini_options]` section in `pyproject.toml` |
| `pytest` via dedicated config | `pytest.ini`, or a `[tool:pytest]` section in `setup.cfg` |

Read each candidate file rather than assuming its shape from its mere
presence — a `Makefile` without a `test:` target, or a `package.json`
without a `test` script, is not evidence of a test entrypoint.

### 2. Disambiguate

- **One entrypoint found**: record its invocation command as `test_command`
  in `docs/charter/testing.yaml`. No further confirmation needed.
- **Multiple entrypoints found**: do not guess which one is primary. Present
  every candidate to the user — the file it came from and the command it
  implies — and ask which one is the project's canonical `test_command`.
  Record only the user's choice. Optionally record a second entrypoint as
  `test_staged_command` or `test_changed_command` if the user identifies one
  as serving that narrower purpose (see
  [charter-testing.yaml](../../rulebooks/templates/charter-testing.yaml)).
- **No entrypoint found**: do not fabricate a command. Surface the gap to
  the operator directly — state plainly that no test entrypoint was
  detected, and that `docs/charter/testing.yaml` cannot be populated until
  one exists or is named explicitly. Offer to help the operator build
  project-owned test infrastructure if they choose — scripts, hooks, and
  config that belong to the project and survive `remove-factory`. Building
  that infrastructure from scratch is a full onboarding interview owned by
  `kit-manager`, not this skill; this skill only makes the offer and hands
  off.

### 3. Scan for test layers

Look for identifiable test infrastructure that maps to the layer vocabulary
in
[testing-strategy.md](../../rulebooks/conventions/testing-strategy.md):

- `conftest.py` files anywhere in the tree — pytest fixtures, usually
  `contract_test` or `integration_test` infrastructure depending on what
  they set up (mocks vs. real filesystem/subprocess/persistence).
- `tests/` or `test/` directories — confirm whether subdirectories or
  naming conventions (`unit/`, `integration/`, `e2e/`, pytest markers such
  as `-m integration`) separate layers, or whether the suite is flat.
- Makefile targets named for a layer, e.g. `test-unit`, `test-integration`,
  `lint` — each maps to one layer.
- Runner configuration that indicates layer separation: pytest marker
  definitions in `pyproject.toml`/`pytest.ini` (`markers = [...]`), tox
  environments (`[testenv:integration]`), or nox sessions.
- A `.feature` directory or Gherkin runner config (`behave.ini`,
  `cucumber.js`, `.godog.yml`) — evidence of the `acceptance_test` layer.
- Linter/formatter configuration invoked as a gate (`ruff`, `eslint`,
  `mdformat --check`) — evidence of the `deterministic_linter` layer.

Layer names to use when recording, exactly as defined in
[testing-strategy.md](../../rulebooks/conventions/testing-strategy.md):

- `deterministic_linter`
- `acceptance_test`
- `contract_test`
- `integration_test`
- `e2e_smoke_test`

Record only layers you found concrete evidence for. Do not populate a layer
entry on inference alone — an empty or absent `layers` section is more
honest than a guessed one.

### 4. Record

Write or update `docs/charter/testing.yaml` using
[charter-testing.yaml](../../rulebooks/templates/charter-testing.yaml) as
the schema:

- `test_command` — required once an entrypoint is confirmed (step 2).
- `test_staged_command` — optional; set only if a distinct staged-files
  invocation was identified or named by the user.
- `test_changed_command` — optional; same rule as above, for changed-files
  invocation.
- `layers` — one entry per layer with confirmed evidence (step 3), each
  with `tool`, `infrastructure`, and `entry_point` filled in from what was
  actually observed. `anti_patterns` and `fidelity` are optional per-layer
  fields — record them only when the scan turned up concrete evidence (a
  documented exclusion, a mocked-vs-real distinction visible in fixture or
  config code); do not infer them. Omit unused layers entirely; never set a
  layer to `null` as a placeholder.

If `docs/charter/testing.yaml` already exists, treat it as a prior scan
result, not ground truth — update fields whose evidence has changed, and
leave untouched fields that were not re-scanned. Do not silently delete a
layer entry that step 3 simply did not re-detect this run without flagging
that gap to the operator first, since a missing layer could mean the
infrastructure was removed or that this scan's detection surface missed it.

After writing, run:

```bash
factory/scripts/mdformat --number docs/charter/testing.yaml
```

`testing.yaml` is YAML, not Markdown — `mdformat` is a no-op on it here for
consistency with the write-time formatting convention; skip it if the
script rejects the extension.

## Example

**Scenario:** Onboarding a brownfield Python project. The scan finds
`pyproject.toml` with `[tool.pytest.ini_options]` and no other candidate.
It also finds `conftest.py` at the repo root and a flat `tests/` directory
with no marker-based separation.

**Result written to `docs/charter/testing.yaml`:**

```yaml
test_command: "uv run pytest --tb=short --quiet"

layers:
  contract_test:
    tool: "pytest"
    infrastructure: "mock"
    entry_point: "uv run pytest tests/"
    fidelity:
      filesystem: "real"
      external_services: "mocked"
      configuration: "mocked"
```

Only one entrypoint existed, so no disambiguation was needed. Only one
layer had concrete evidence (a flat suite gives no signal to split
`contract_test` from `integration_test`), so `layers` records just that
one.

## Notes

- Detection surface should stay broad — new entrypoint conventions
  (`justfile` lowercase, `mise.toml` tasks, language-specific runners) can
  be added to step 1's table as they are encountered; this skill is not
  the sole gate on what counts as a valid `test_command`.
- This skill is invoked by `init-factory` and by `kit-manager` during
  onboarding. It does not itself gate anything — it only detects and
  records. Downstream gates consume `docs/charter/testing.yaml` afterward.
- The charter is a backup reference for ambiguous cases, not the primary
  source of truth. When code and charter disagree, re-run this skill rather
  than trusting the stale charter entry.
