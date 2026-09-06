---
name: detect-test-regime
title: Detect Test Regime
description: >-
  Scan project for test suites and record each one in
  testing.yaml (at docs/agent-context/testing.yaml, falling back to
  docs/charter/testing.yaml). Code is the source of truth; the record
  is derived.
inputs:
  - Makefile
  - GNUmakefile
  - package.json
  - pyproject.toml
  - tox.ini
  - noxfile.py
  - Justfile
  - Taskfile.yml
  - docker-compose.yml
  - docker-compose.*.yml
  - compose.yaml
  - .github/workflows/*.yml
  - .gitlab-ci.yml
  - conftest.py
  - pytest.ini
  - setup.cfg
  - vitest.config.*
  - jest.config.*
  - tests/
  - test/
outputs:
  - docs/agent-context/testing.yaml (falls back to docs/charter/testing.yaml)
category: utility
version: 0.2.0
---

# Detect Test Regime

Scan the project for every test suite it contains, then write or update
`testing.yaml` (at `docs/agent-context/testing.yaml`, falling back to
`docs/charter/testing.yaml` for legacy projects) with per-suite records.
Code is the source of truth — the record is derived, not the other way
around. Never
invent a command the project cannot actually run.

## When to use this skill

- During `init-factory`, to seed the testing charter from an existing
  codebase.
- During brownfield onboarding, when `capture-context` needs to know
  how a project runs its tests before scaffolding gates around it.
- Whenever `testing.yaml` is missing, empty, or suspected
  stale against the current repository.
- When the planning agent detects a missing or empty testing.yaml before
  slicing stories.

## Output schema

```yaml
testing_strategy: docs/charter/testing-strategy.md

test_all: "make test && make frontend_test"   # composite command, all suites

suites:
  - name: backend
    framework: pytest
    run_all: "docker compose exec app uv run pytest packages/server/backend/tests"
    run_file: "docker compose exec app uv run pytest {file}"
    run_match: "docker compose exec app uv run pytest -k {pattern}"
    root: packages/server/backend/tests
    pattern: "test_*.py"
    markers: [db]
    prerequisites: "Docker Compose stack running (make up)"
  - name: frontend
    framework: vitest
    run_all: "make frontend_test"
    run_file: "cd packages/server/frontend && npm run test:run -- {file}"
    root: packages/server/frontend/src
    pattern: "*.test.ts"
    prerequisites: "npm install (make frontend_deps)"

layers:
  contract_test:
    tool: "pytest"
    infrastructure: "mock"
    entry_point: "uv run pytest tests/"
```

Per-suite fields:

- `name` — short identifier (required)
- `framework` — test framework name (required)
- `run_all` — command to run the full suite (null if unknown)
- `run_file` — command template with `{file}` placeholder (null if unknown)
- `run_match` — command template with `{pattern}` placeholder (null if unknown)
- `root` — directory containing test files (null if unknown)
- `pattern` — filename glob for test files (null if unknown)
- `markers` — framework-specific markers/tags (optional)
- `prerequisites` — what must be running or installed first (null if unknown)

`test_all` is composed from the discovered suites' `run_all` commands,
joined with `&&`. When a suite is found but cannot be fully resolved
(command unclear, prerequisites unknown), record it with explicit nulls —
do not omit it. The human catches gaps during charter review before
planning starts.

`testing_strategy` is the path to the project's testing strategy document.
This field is always populated, never null — it defaults to
`factory/rulebooks/conventions/testing-strategy.md` when the project has no
project-specific document.

## Workflow

### 1. Makefile-first discovery

The skill MUST trace the full link tree from Makefile targets before
falling back to language-specific probes. The Makefile layer reveals how
suites are actually invoked — framework probes alone find "pytest exists"
but not "run it inside Docker via Make."

**Layer 1 — Makefile.** Find `Makefile`, `GNUmakefile`, or `makefile` in the
project root. Parse all targets whose name contains `test` (case-insensitive).
For each target:

- Extract the recipe lines verbatim.
- Record variables used in recipes (`$(VAR)`, `${VAR}`); resolve them from
  the same Makefile where possible, but do not chase multi-file includes
  exhaustively — record unresolved variables as-is.
- Follow `$(MAKE) -C <subdir>` and `-include` directives to sub-Makefiles;
  repeat the target scan there.

**Layer 2 — Indirection.** Recipes point to other systems. Follow each lead:

- `docker compose exec|run` → read `docker-compose.yml` /
  `docker-compose.*.yml` / `compose.yaml` for the named service's image,
  working directory, and volumes. This reveals prerequisites and
  execution context.
- `tox` / `nox` → read `tox.ini` / `noxfile.py` for environments and
  their test commands.
- `npm run|npx|yarn|pnpm` → read `package.json` `scripts` for the named
  script and its underlying command.
- Shell scripts (`bash`, `sh`, `./scripts/`) → read the script for the
  actual test invocation.

**Layer 3 — Framework configs.** Land on the actual framework
configuration. Now you know the framework *and* how it is invoked:

- **Python:** `conftest.py`, `pytest.ini`, `pyproject.toml`
  `[tool.pytest.ini_options]`, `setup.cfg` `[tool:pytest]`. Extract
  `testpaths`, `python_files`, `python_classes`, `python_functions`,
  markers.
- **JS/TS:** `vitest.config.*`, `jest.config.*`, `package.json` test
  scripts. Extract `include`/`exclude` patterns, `roots`, `testMatch`.

**Layer 4 — CI configs.** Cross-reference `.github/workflows/*.yml` and
`.gitlab-ci.yml` for anything the Makefile tree missed. Some suites only
run in CI — record them but note the CI-only context in `prerequisites`.
CI steps include caching, artifacts, and env setup that does not apply
locally — use CI for "which suites exist and in what order" but do not
derive `run_all` from CI commands unless no other source exists.

**Layer 5 — Orphan scan.** Language-specific probes for framework markers
not reachable from any of the above. These are the "exists but no known
command" suites — record them with `framework` and `root` populated but
`run_all: null`.

Also check for `Justfile` `test` recipes and `Taskfile.yml` `test` tasks
as alternative entrypoints equivalent to Makefile targets.

Read each candidate file rather than assuming its shape from its mere
presence — a `Makefile` without a `test:` target, or a `package.json`
without a `test` script, is not evidence of a test entrypoint.

### 2. Build suite records

For each distinct test suite discovered across all layers, build a suite
record:

- **One suite per framework-root pair.** Two pytest configurations rooted in
  different directories are two suites.
- **Merge information across layers.** A suite found via Makefile → Docker →
  pytest config gets its `run_all` from the Makefile recipe, its
  `prerequisites` from the Docker service, and its `root`/`pattern`/`markers`
  from the pytest config.
- **Name suites descriptively.** Use the directory or purpose: `backend`,
  `frontend`, `api-integration`, `e2e`. When the project has only one suite,
  name it `default`.

### 3. Disambiguate

- **One or more suites found:** present every suite with its populated and
  null fields to the user. Ask for confirmation and corrections — especially
  for null fields the human can fill in.
- **No suites found:** do not fabricate commands. Surface the gap plainly.
  Offer to help build test infrastructure; building from scratch is a full
  onboarding interview owned by `capture-charter`, not this skill.

### 4. Scan for test layers

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
entry on inference alone.

### 5. Compose test_all

Join each suite's `run_all` command with `&&` to form `test_all`. Suites
with `run_all: null` are excluded from the composite command. If no suite
has a resolved `run_all`, set `test_all: null`.

### 6. Ask about testing strategy

After suite discovery and confirmation (step 3), ask the user:

> "Does this project have a testing strategy document? If so, where is it?"

Record the answer as the `testing_strategy:` field:

- If the user names a path, record it verbatim.
- If the project has no testing strategy document, default to
  `factory/rulebooks/conventions/testing-strategy.md`.

This field is always populated, never null. The testing strategy document
tells planner and developer agents *how* to test — clusters, budgets,
markers, fixture rules, AI-generated test rules. The suites tell them
*where* and *what*.

### 7. Record

Write or update `testing.yaml` (at `docs/agent-context/testing.yaml` if that directory exists, otherwise `docs/charter/testing.yaml`):

- `testing_strategy` — path to the testing strategy document (step 6).
- `test_all` — the composite command (step 5).
- `suites` — one entry per discovered suite (step 2), with all fields
  populated or explicitly null.
- `layers` — one entry per layer with confirmed evidence (step 4), each
  with `tool`, `infrastructure`, and `entry_point` filled in from what was
  actually observed. Omit unused layers entirely; never set a layer to
  `null` as a placeholder.

If `testing.yaml` already exists, treat it as a prior scan
result, not ground truth — update fields whose evidence has changed, and
leave untouched fields that were not re-scanned. Do not silently delete a
suite or layer entry that this scan did not re-detect without flagging that
gap to the user first.

After writing, run:

```bash
factory/scripts/mdformat --number <resolved-testing-yaml-path>
```

`testing.yaml` is YAML, not Markdown — `mdformat` is a no-op on it here for
consistency with the write-time formatting convention; skip it if the
script rejects the extension.

## Notes

- Detection surface should stay broad — new entrypoint conventions
  (`justfile` lowercase, `mise.toml` tasks, language-specific runners) can
  be added to step 1's table as they are encountered.
- This skill is invoked by `init-factory` and by `capture-context`
  during onboarding. It does not itself gate anything — it only detects and
  records. Downstream gates consume `testing.yaml` afterward.
- The charter is a backup reference for ambiguous cases, not the primary
  source of truth. When code and charter disagree, re-run this skill rather
  than trusting the stale charter entry.
- Python ecosystem probes are implemented first. JS/TS probes cover vitest,
  jest, and package.json test scripts. Other language ecosystems (Go, Rust,
  Java/Gradle, etc.) are added later as encountered.
