---
schema_version: 2
title: Deterministic Factory Engine
status: superseded
owner: Matthias Daues
created: 2026-09-11
updated: 2026-09-14
supersedes:

impact:
  scope: cross_component
  architecture_change: true
  external_contract_change: false
  boundaries:
    - tests/conftest.py
    - tests/factory/test_source_script_loading.py
    - tests/factory/test_phase.py
    - tests/factory/test_transition_lint.py
    - tests/factory/test_installed_engine_smoke.py
    - tests/factory/test_engine_boundaries.py
    - packages/factory/engine/__init__.py
    - packages/factory/engine/flow_control/__init__.py
    - packages/factory/engine/flow_control/model.py
    - packages/factory/engine/flow_control/codec.py
    - packages/factory/engine/flow_control/service.py
    - packages/factory/scripts/phase
    - packages/factory/scripts/transition-lint
    - packages/factory/scripts/init-factory
    - docs/arc42/architecture.dsl
    - docs/arc42/05_building_block_view.md
    - docs/arc42/06_runtime_view.md
    - docs/arc42/08_crosscutting_concepts.md

governance:
  assurance: high
  risk_domains:
    - data_integrity
    - compatibility
    - reliability
    - operations

estimate:
  as_of: 2026-09-11
  basis: decomposition
  confidence: low
  human_review_hours: unknown
  normalized_tokens: unknown
  estimated_consumption: unknown
---

# Feature Request: Deterministic Factory Engine

Superseded by the
[Cycle-Based Orchestration proposal](cycle-based-orchestration.md). Do not plan
or implement the linear playbook-engine extraction described below. The
replacement retains the thin-adapter and deterministic-engine constraints but
defines a cycle-native flow-control model.

## Summary

Introduce `packages/factory/engine/` as the home of reusable deterministic
Factory capabilities while retaining `factory/scripts/*` as the installed
command interface. The first release changes the tests to exercise tracked
source and extracts one canonical Flow Control model from `phase` and
`transition-lint`. Usage capture, runtime adapters, dispatch, and installation
remain later decisions.

The feature answers one question the repository cannot answer reliably today:
where does a deterministic invariant live when several commands, runtime
adapters, humans, and automated triggers must reach the same decision?

## Motivation

The architecture review found 51 tracked entries and 24,838 lines under
`packages/factory/scripts/`: 43 Python files, six shell files, one JavaScript
file, and one lockfile. The six largest files—`init-factory`, `dispatch`,
`usage-capture`, `dispatch_lib.py`, `test-design-verify`, and `context-lint`—hold
45.9% of those lines. The main problem is not dense import cycles. It is a set
of large command-oriented stovepipes with weak domain locality. Invariants are
duplicated or embedded in executable files, so new callers must reuse command
implementation details.

The current test seam can select the wrong source. The shared fixture in
[`tests/conftest.py`](../../tests/conftest.py) loads scripts from the ignored,
installed `factory/scripts/` tree rather than tracked
[`packages/factory/scripts/`](../../packages/factory/scripts). At review time,
these installed files differed from tracked source:

- `backlog-lint`
- `dispatch`
- `dispatch_lib.py`
- `premerge-check`

The installed tree also lacked `review-workspace-check`. A later Factory
refresh removed those differences, but not the test-selection defect that made
them capable of changing the test result.

The review counted 475 test functions. Seventeen script assets had a focused
test owner and 34 did not. Of the script tests, 411 loaded extensionless scripts
in-process, 63 exercised subprocess command behavior, and one focused on
`review-workspace-check`. This is useful characterization evidence, but it is
not yet a complete command-contract surface and does not reliably test tracked
source.

The complete Factory directory is the distributed product. `init-factory`
copies `packages/factory/` into a target project's `factory/` directory. A
repository-level `src/` would separate the reusable code from the unit that
must carry it. The engine therefore belongs inside `packages/factory/` and is
copied with the rest of the Factory.

## Core Principles

- The complete Factory directory remains the distributable boundary.
- `engine/` owns invariant-bearing capabilities. `scripts/` owns stable command
  adapters and genuinely standalone utilities.
- Engine packages use domain names such as `flow_control`, never technical
  catch-alls such as `common`, `helpers`, or `validators`.
- Tracked source is the default test surface. An installed Factory is a
  separate distribution-test surface.
- Existing script paths, argument grammars, semantic exit codes, output
  channels, machine-readable formats, and filesystem effects remain compatible.
- Characterization precedes extraction. Similar-looking code is not shared
  until tests prove that it represents the same rule.
- The engine evaluates gates and returns decisions; adapters own marker writes,
  process lifecycle, and runtime protocol.

## Design

### 1. Start at the test seam

The first implementation file is
`tests/factory/test_source_script_loading.py`. Its first test is
`test_load_script_uses_tracked_factory_source`. It loads `phase` through the
shared helper and asserts that the resolved module file is exactly
`REPO_ROOT / "packages" / "factory" / "scripts" / "phase"`.

Make that test pass by changing [`tests/conftest.py`](../../tests/conftest.py):

```python
TRACKED_FACTORY_ROOT = REPO_ROOT / "packages" / "factory"
SCRIPTS_DIR = TRACKED_FACTORY_ROOT / "scripts"
```

All existing `load_script(...)` consumers then exercise tracked source. Tests
that intentionally exercise an installed Factory must create a temporary
installation and address its paths explicitly; they must not use the ignored
working-tree mirror.

The focused source-suite command is:

```text
uv run pytest --tb=short --quiet tests/factory
```

The repository completion command remains the project-declared command from
[`docs/testing.yaml`](../testing.yaml):

```text
uv run pytest --tb=short --quiet
```

### 2. Characterize the two command adapters

Create `tests/factory/test_phase.py` and extend
[`tests/factory/test_transition_lint.py`](../../tests/factory/test_transition_lint.py)
before moving implementation. The tests invoke the tracked scripts as
subprocesses and freeze these public contracts.

#### `phase`

The accepted commands remain:

```text
factory/scripts/phase advance [--by NAME] [--dry-run]
    [--repo-root PATH] [--marker PATH] [--playbooks-dir PATH]
    [--playbook NAME]
factory/scripts/phase retry [--repo-root PATH] [--marker PATH]
    [--playbooks-dir PATH] [--default-max-iterations N]
```

Exit and output behavior remains:

- exit 0: the action is allowed; print the result to stdout;
- exit 1: configuration is absent or invalid, a forward transition is absent,
  or entry conditions fail; print the refusal to stderr and do not mutate the
  marker;
- exit 2: the retry cap is exceeded or command parsing fails; print to stderr
  and do not mutate the marker;
- `advance --dry-run`: evaluate the same decision as `advance`, never write the
  marker;
- successful `advance`: write the marker fields in the existing order
  `playbook`, `state`, `gate`, `result`, `open_findings`, `next`, `iteration`,
  `recorded_by`, `recorded_at`;
- successful `retry`: increment `iteration`, refresh `recorded_at`, and preserve
  all other marker fields.

#### `transition-lint`

The accepted options remain `--repo-root`, `--marker`, `--playbooks-dir`,
`--format text|json`, and `--report-only`.

Exit and output behavior remains:

- without `--report-only`, return the number of error findings;
- with `--report-only`, always return 0;
- text and JSON reports are written to stdout;
- command-parsing errors use argparse's stderr and exit 2;
- JSON output retains top-level `findings` and `summary`; every finding retains
  `code`, `severity`, `artifact`, and `message`;
- existing finding codes remain `TL-NOMARKER`, `TL-MARKER`, `TL-NOFSM`,
  `TL-STATE`, and `TL-ORDER`;
- an absent marker produces the informational `TL-NOMARKER` no-op;
- staged files owned by the current state pass; files owned only by another
  state produce `TL-ORDER`.

Human-readable sentence wording may be clarified later. The listed exit,
channel, field, code, and filesystem contracts may not change in this release.

### 3. Create the Flow Control package

Add this package inside the tracked and distributed Factory:

```text
packages/factory/engine/
├── __init__.py
└── flow_control/
    ├── __init__.py
    ├── model.py
    ├── codec.py
    └── service.py
```

`model.py` defines immutable domain values:

- `RunMarker`: the nine marker fields listed in the `phase` contract;
- `StateMachine`: states, transitions, gate conditions, and halt conditions;
- `FlowProblem`: `code`, `severity`, `artifact`, and `message`;
- `FlowResult`: `status`, `operation`, `current_state`, `target_state`,
  `problems`, and `next_marker`.

`FlowResult.status` is exactly one of `allowed`, `blocked`, or
`operational_error`. `operation` is exactly one of `advance`, `retry`, or
`check_staged`. `problems` is an immutable sequence. `next_marker` is present
only when an allowed operation would write a marker. These values are the
in-process automation contract; callers never need to parse terminal prose.

`codec.py` owns `parse_marker`, `render_marker`, and `parse_fsm`.
`service.py` owns these public operations, re-exported by
`engine.flow_control`:

```text
assess_advance(marker_text, fsm_text, repo_root, recorded_by, now) -> FlowResult
assess_retry(marker_text, fsm_text, default_limit, now) -> FlowResult
assess_staged_paths(marker_text, fsm_text, staged_paths) -> FlowResult
```

`now` is supplied by the adapter so tests are deterministic. `assess_advance`
evaluates the existing `file_exists`, `files_exist`, `no_open_findings`, and
`script_exit_zero` entry conditions relative to `repo_root`. The engine returns
the next marker value but does not write it. The `phase` adapter performs the
atomic write only for an allowed, non-dry-run result.

### 4. Preserve the current marker and FSM language

The extraction supports exactly the syntax both scripts implement today:

- a marker is a flat `key: value` mapping;
- blank lines and full-line comments are ignored;
- a trailing comment begins at a whitespace-prefixed `#`;
- FSM input supports indentation-based block mappings and block sequences,
  including multi-key mapping items;
- scalars support null (`null`, `~`, or empty), booleans, quoted strings, and
  unquoted strings;
- inline collections, anchors, aliases, multiline scalars, and general YAML
  type coercion are not supported.

The canonical domain keys and lifecycle remain documented by
[`greenfield-development.fsm.yml`](../../packages/factory/playbooks/greenfield-development.fsm.yml)
and
[`state-machines.md`](../spec/supplementary_specs/state-machines.md). Tests feed
the same fixtures through both old adapter contracts and the extracted codec
before duplicate parsers are deleted.

### 5. Keep scripts executable without installing a Python package

Both adapters remain extensionless executable files at their existing paths.
Before importing the engine, each adapter adds its containing Factory directory
to `sys.path`:

```python
FACTORY_ROOT = Path(__file__).resolve().parent.parent
if str(FACTORY_ROOT) not in sys.path:
    sys.path.insert(0, str(FACTORY_ROOT))
```

It then imports `engine.flow_control`. This is the selected zero-install
bootstrap. No environment variable, current-working-directory assumption, or
separately installed wheel is required. Engine modules never modify
`sys.path`.

### 6. Test the distributed shape

Add `tests/factory/test_installed_engine_smoke.py`. The test creates a temporary
git repository and runs the public installer with
explicit non-interactive inputs:

```text
packages/factory/scripts/init-factory --source <repository-root>
    --target <temporary-project> --project-name EngineSmoke
    --cli codex --usage-transcript-retention omit
```

It then asserts that `factory/engine/flow_control/` exists and invokes both
copied commands:

```text
factory/scripts/transition-lint --repo-root <temporary-project>
factory/scripts/phase advance --dry-run --repo-root <temporary-project>
```

Both commands must import the copied engine and return their characterized
result. A second fixture omits `factory/engine/flow_control/` from the copied
tree and proves both commands fail loudly with an import error; a silently
partial installation is not acceptable.

### 7. Enforce the dependency direction

The permitted dependency direction is:

```text
scripts/phase and scripts/transition-lint → engine/flow_control
engine/flow_control → Python standard library
```

Add `tests/factory/test_engine_boundaries.py`. It parses every Python file below
`packages/factory/engine/` with `ast` and
fails if an import resolves to `scripts`, `config`, or another top-level
Factory area. This focused test is the mechanical enforcement for the first
release. The architecture DSL records the same direction; the existing
`dependency-check` is not extended because it normalizes module names to their
first root token and cannot distinguish sibling paths below `packages`.

### 8. Preserve Factory ownership while enabling automation

The extraction preserves
[`ADR-0002`](../adr/0002-factory-owns-flow-control-orchestrator-is-a-trigger.md#decision).
The marker, FSM, and deterministic gates remain the authority. A human, the
`run-step` skill, or an orchestrator is a peer trigger of the same model.

An automated trigger may call `engine.flow_control` and receive `FlowResult`.
It gains no new authority: adapters still decide which files and processes are
available, and only `phase` writes the marker. This release adds no service
API, daemon, scheduler, remote execution protocol, or background lifecycle.

### 9. Record the later extraction order

The review produced this risk and effort order. Only rows 1 and 2 belong to the
first release.

| Order | Candidate                 | Decision              | Risk / effort       | Entry condition                                                           |
| ----: | ------------------------- | --------------------- | ------------------- | ------------------------------------------------------------------------- |
|     1 | Tracked-source test seam  | First release         | Low / low           | None                                                                      |
|     2 | Flow Control model        | First release         | Medium / high       | Command characterization is green                                         |
|     3 | Usage pipeline            | Later proposal        | Medium-high / high  | The copied-engine and thin-adapter pattern has survived the first release |
|     4 | Runtime adapter ownership | Later proposal        | High / very high    | Policy contracts and cross-runtime fixtures exist for each adapter family |
|     5 | Dispatch lifecycle        | Explore conditionally | High / very high    | Both dispatch promotion conditions below hold                             |
|     6 | Installation lifecycle    | Last                  | Very high / highest | Earlier engine modules pass install and update compatibility tests        |

Dispatch becomes a committed module candidate only when both conditions hold:

1. Autonomous and review lifecycles have characterization tests through the
   command interface.
2. Either an external trigger needs structured non-terminal outcomes, or the
   next dispatch change crosses at least three of CLI routing, ledger
   transitions, worktree effects, gate execution, and merge closeout.

Until then, dispatch work may extract only already-proven leakage such as glob
matching. It must not pre-emptively split the lifecycle.

The 17 production adapters and 2,837 lines under `config/hooks` and
`config/extensions` receive this intended later ownership:

| Capability        | Existing adapters                                                                                                  | Ownership after a later extraction                                                                                              |
| ----------------- | ------------------------------------------------------------------------------------------------------------------ | ------------------------------------------------------------------------------------------------------------------------------- |
| Safety and scope  | `block-dangerous-git.{sh,json}`, `step-guard.{sh,json}`, `block-dangerous-git.ts`, `step-guard.ts`                 | A safety/scope capability owns policy data and contract fixtures; adapters retain runtime request parsing and response encoding |
| Usage capture     | `capture-usage.{sh,json}`, `capture-codex-usage.sh`, `capture-copilot-usage.sh`, `capture-usage.ts`, `pi-usage.ts` | A usage capability owns canonical events and record operations; adapters map native lifecycle events                            |
| Factory freshness | `check-factory-freshness.{sh,json}`, `check-factory-freshness.ts`                                                  | An installation capability owns freshness decisions; adapters retain lifecycle integration                                      |
| Pi dispatch       | `dispatch-wave.ts`, `run-agent.ts`                                                                                 | A dispatch capability owns lifecycle policy after its promotion gate; Pi retains its tool protocol and process integration      |

Shell and TypeScript adapters are not forced through a Python runtime. Shared
policy data, schemas, and cross-runtime fixtures establish parity where code
cannot be shared.

### 10. File compatibility drift separately

The dead-command findings are a standalone cleanup concern, not a dependency
or completion condition of this proposal. File a separate cleanup story
covering these exact active sources:

- [`feature-addition.md`](../../packages/factory/playbooks/feature-addition.md),
  [`greenfield-development.md`](../../packages/factory/playbooks/greenfield-development.md),
  and
  [`brownfield-onboarding.md`](../../packages/factory/playbooks/brownfield-onboarding.md)
  call the deleted `factory/scripts/charter-lint`;
- [`interface-contracts.md`](../spec/supplementary_specs/interface-contracts.md)
  still publishes the deleted `charter-lint` command;
- [`scope-map.md`](../spec/scope-map.md) assigns a feature to the deleted
  `factory/scripts/run-tests` command;
- [`factory-guide.md`](../../packages/factory/docs/factory-guide.md) advertises
  the nonexistent `factory/scripts/mutation-testing` command; and
- [`STRUCTURIZR.md`](../../packages/factory/skills/scaffold-arc42/STRUCTURIZR.md)
  advertises the unsupported `factory/scripts/structurizr export-png` command.

The cleanup must preserve historical proposals, ADR amendments, findings, and
other records that deliberately describe the removed commands.

## Scope

**In the first release:**

- Redirect the shared Factory test loader from the ignored installed mirror to
  tracked `packages/factory/scripts/` source.
- Add subprocess characterization for the existing `phase` and
  `transition-lint` contracts listed in the Design.
- Create the five named `engine` and `engine/flow_control` files with the
  specified model, codec, and service responsibilities.
- Replace duplicate marker parsing, FSM parsing, state navigation, output
  ownership, transition, gate, and retry decisions in `phase` and
  `transition-lint` with calls to `engine.flow_control`.
- Retain both executable paths and every enumerated command contract.
- Use the specified sibling-directory `sys.path` bootstrap in the two adapters.
- Add the installed-engine smoke test using the public `init-factory` command.
- Add the AST-based engine dependency-boundary test.
- Update the architecture DSL and the building-block, runtime, and
  cross-cutting views for the engine and adapter direction.

**Explicitly deferred (do NOT plan stories for these):**

- The dead-command compatibility cleanup. It must be filed and delivered as an
  independent cleanup story, not hidden inside this structural change.
- Usage-capture extraction, until the first engine slice proves the packaging
  and adapter pattern.
- Runtime hook and extension reorganization, until each adapter family has
  policy contracts and cross-runtime fixtures.
- Dispatch lifecycle modularization, until both promotion conditions in the
  Design hold.
- Installation lifecycle extraction, because it changes the mechanism that
  distributes every other capability and therefore remains last.
- A public automation API, daemon, scheduler, remote trigger, or orchestration
  service. The in-process `FlowResult` is the only automation seam added here.
- A generic YAML parser, validation framework, `common.py`, or repository-wide
  script rewrite.
- Moving Markdown or YAML process definitions out of `agents/`, `skills/`,
  `playbooks/`, or `rulebooks/`.

## Design Details

### Implementation sequence

Planning must preserve this dependency order:

1. Prove tracked-source loading with the named first test, then change
   `tests/conftest.py`.
2. Characterize both command adapters through subprocess tests.
3. Add the engine package, model, codec, and service with direct unit tests.
4. Redirect one adapter at a time, running its characterization tests after
   each move.
5. Add the boundary test and update the architecture model.
6. Run the temporary installed-Factory smoke test.
7. Run the complete project-declared test command.

The compatibility-cleanup story has no code dependency on this sequence and
must use a separate commit and review.

### Failure and rollback behavior

An invalid marker or FSM produces an `operational_error` result. A valid
request that cannot proceed produces `blocked`. An allowed dry run returns the
same target and problems as a real advance but has no `next_marker` write
effect in the adapter.

Each adapter is redirected only after its subprocess characterization passes.
If the installed smoke test fails, revert the adapter redirection while
retaining the characterization tests; do not weaken the command contract or
fall back to the ignored installed mirror.

### Demonstration

A reviewer can demonstrate the first release without implementation knowledge:

1. Run the focused source suite and observe that the loader test resolves
   `phase` below `packages/factory/scripts/`.
2. Run an in-process test that calls `assess_advance` with a fixed clock and
   receives an `allowed` `FlowResult` containing the expected target and next
   marker.
3. Run the public installer into a temporary repository.
4. Invoke the copied `transition-lint` and `phase advance --dry-run` commands
   and observe the characterized exits and outputs.
5. Remove the copied `engine/flow_control` directory in a disposable fixture
   and observe both adapters fail loudly rather than silently using another
   source tree.

## Open Questions

There are no unresolved first-release decisions. Later capabilities require
their own proposal or an explicitly re-opened scope decision after satisfying
the entry conditions above.

## Completion Criteria

- `test_load_script_uses_tracked_factory_source` fails against the old shared
  fixture and passes after `tests/conftest.py` selects
  `packages/factory/scripts/`.
- No shared Factory test helper selects the ignored root `factory/` mirror.
- The subprocess characterization tests assert every `phase` and
  `transition-lint` contract enumerated in the Design and pass before and after
  extraction.
- The five named engine files exist and expose `RunMarker`, `StateMachine`,
  `FlowProblem`, `FlowResult`, `assess_advance`, `assess_retry`, and
  `assess_staged_paths` from `engine.flow_control`.
- One implementation under `engine/flow_control` owns the supported marker and
  FSM codec, state navigation, output ownership, gate evaluation, transition
  decisions, and retry-cap decisions. Neither adapter retains a duplicate
  implementation.
- A direct unit test passes a fixed clock to `assess_advance` and asserts the
  exact `FlowResult` and `next_marker` without invoking a subprocess or parsing
  terminal output.
- `phase` and `transition-lint` retain their executable paths and all listed
  argument, exit, output-channel, JSON/finding, and marker-effect contracts.
- The two adapters use the specified zero-install bootstrap; engine modules do
  not modify `sys.path`.
- The AST boundary test fails on a fixture that imports `scripts` from
  `engine`, passes for standard-library imports, and scans every engine Python
  file.
- The temporary installation contains `factory/engine/flow_control` and both
  copied adapters execute successfully without a separately installed Factory
  package.
- The missing-engine installation fixture makes both adapters fail loudly and
  cannot import tracked source from the repository checkout.
- The architecture DSL and the three named arc42 views describe the Flow
  Control engine, stable adapters, and permitted dependency direction.
- `uv run pytest --tb=short --quiet tests/factory` passes.
- `uv run pytest --tb=short --quiet` passes.

## Guiding Rule

Move an invariant into `engine/` only when more than one adapter needs the same
decision and tests prove that the installed command contracts survive the move.

## Consult Review — 2026-09-11

Reviewer: proposal-review-agent
Reviewed commit: ef844121a41212b9256183673c4f13e42266575c
Stance: consultative (draft)

### Filed Findings

| ID                                    | Severity | Area      | Summary                                                       |
| ------------------------------------- | -------- | --------- | ------------------------------------------------------------- |
| [PROP-0021](../findings/PROP-0021.md) | major    | estimate  | Decomposition basis with all-unknown ranges is contradictory  |
| [PROP-0022](../findings/PROP-0022.md) | major    | Design §2 | 23 existing in-process tests have no specified migration path |
| [PROP-0023](../findings/PROP-0023.md) | major    | Design §3 | `assess_staged_paths` FlowResult semantics undefined          |
| [PROP-0024](../findings/PROP-0024.md) | major    | Design §3 | `StateMachine` model omits per-state `outputs` globs          |

### Observations

1. `engine/__init__.py` contents unspecified — empty marker or re-exports?
2. `init-factory` listed as boundary but not modified — clarify test-exercised-only.
3. Boundary test could enforce stdlib-only imports as a hardening measure.
4. `FlowProblem` mirrors `Finding` dataclass 1:1 — note the correspondence.
5. Rollback granularity: both adapters or only the most recently redirected?
6. `conftest.py` sys.path change has suite-wide reach (411 test loads) — safe but worth noting.
7. Subprocess characterization tests need `--repo-root`/`--marker` isolation to avoid writing to the real marker.

### Summary

The proposal is thorough and well-structured for a draft. Motivation is grounded, scope boundaries are sharp, ADR-0002 alignment holds, and the extraction order with entry conditions prevents premature scope creep. Four gaps need closing before this is ready for `open`: the estimate contradiction, the existing test migration path, the `check_staged` FlowResult semantics, and the missing `outputs` field in the StateMachine model. Full review at [`docs/reviews/proposal-review-2026-09-11-deterministic-factory-engine.md`](../reviews/proposal-review-2026-09-11-deterministic-factory-engine.md).
