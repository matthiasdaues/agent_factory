---
schema_version: 2
title: Deterministic Factory Engine
status: draft
owner: Matthias Daues
created: 2026-09-11
updated: 2026-09-11
supersedes:

impact:
  scope: cross_component
  architecture_change: true
  external_contract_change: false
  boundaries:
    - packages/factory/scripts
    - packages/factory/engine
    - packages/factory/config/hooks
    - packages/factory/config/extensions
    - tests/factory
    - tests/conftest.py
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

## Summary

Introduce `packages/factory/engine/` as the home of reusable deterministic
Factory logic while retaining `factory/scripts/*` as stable command-line
adapters in every installed Factory. The first release changes the tests to use
tracked source by default and extracts one canonical Factory Flow Control model
from `phase` and `transition-lint`. It does not reorganize every script.

The feature answers one question the repository cannot answer reliably today:
where does an invariant live when several scripts, hooks, extensions, humans,
and external automation must enforce the same Factory rule?

## Motivation

The architecture review found 51 tracked entries and 24,838 lines under
`packages/factory/scripts/`. Forty-three are Python, six are shell, one is
JavaScript, and one is a lockfile. The six largest files contain 45.9% of the
total. This is not primarily a dense import-cycle problem; it is a collection
of large command-oriented stovepipes with weak domain locality. Shared policy
is duplicated or hidden inside executable files, so callers reuse a command's
implementation rather than a domain interface.

The current test seam makes this harder to change safely. The shared fixture in
[`tests/conftest.py`](../../tests/conftest.py) loads scripts from the ignored,
installed `factory/scripts/` tree instead of the tracked
[`packages/factory/scripts/`](../../packages/factory/scripts) source. At review
time, four installed files differed from tracked source:

- `backlog-lint`
- `dispatch`
- `dispatch_lib.py`
- `premerge-check`

The installed tree also lacked `review-workspace-check`. A later refresh made
the trees agree again, but that only removed the snapshot difference; it did
not remove the test-selection defect that allowed the difference to affect
which implementation was exercised.

The repository has substantial tests, but their distribution is uneven. The
review counted 475 test functions. Seventeen script assets had focused test
owners and 34 did not. Of the tests that exercise Factory scripts, 411 load
extensionless scripts in-process, 63 invoke a command in a subprocess, and one
focuses on `review-workspace-check`. The suite therefore supplies useful
characterization evidence, but it is not yet a reliable contract surface for
tracked source or for all script entry points.

The Factory is itself the distributed unit: `init-factory` copies the complete
`packages/factory/` content into a target project's `factory/` directory. A
top-level application `src/` would split the executable product from the unit
that installs it. The engine must therefore live inside `packages/factory/` so
installation continues to distribute one self-contained tree.

## Core Principles

- The distributable boundary remains the complete Factory directory.
- `engine/` contains invariant-owning modules; `scripts/` contains stable CLI
  adapters and genuinely standalone utilities.
- A module is named for a domain responsibility, never for generic reuse.
- Existing script paths, arguments, exit codes, standard streams, reports, and
  filesystem effects are compatibility contracts.
- Tracked source is the default test surface. The installed copy is tested
  separately as a distribution artifact.
- Extract only behavior protected by characterization tests. Do not turn
  coincidental similarity into a framework.
- A shared rule is represented once as policy data or a domain operation;
  runtime-specific shell and TypeScript adapters may remain distinct.

## Design

### 1. Establish the source and distribution test seams

Change Factory tests so their default script root is
[`packages/factory/scripts/`](../../packages/factory/scripts), not the ignored
installed mirror. Name the two test modes explicitly:

1. **Source contract tests** load or execute tracked source and provide the fast
   development feedback loop.
2. **Installed-bundle smoke tests** create a temporary target through the
   installation path, then execute selected commands from the copied
   `factory/` tree. These tests detect omitted files, import failures, and
   packaging drift without making the ignored working copy authoritative.

Before moving behavior, add command-level characterization tests for the
affected adapters. The contract records arguments, exit codes, stdout/stderr
separation, report formats, and intended filesystem effects. In-process unit
tests remain useful for engine code, but extensionless CLI loading is no longer
the only evidence for command compatibility.

### 2. Add an engine inside the distributed Factory

Create `packages/factory/engine/` as a Python package. Its immediate child
packages are bounded capabilities, not technical buckets such as `common`,
`helpers`, or `validators`. A script may import an engine capability; engine
modules must not import script entry points.

The installed shape remains self-contained:

```text
factory/
├── engine/          # reusable deterministic capabilities
├── scripts/         # stable CLI adapters and standalone commands
├── config/          # runtime-specific hook and extension adapters
├── agents/
├── skills/
├── playbooks/
└── rulebooks/
```

The engine must run from a copied Factory without installing a separate Python
distribution. The architecture phase may choose the smallest bootstrap needed
for extensionless scripts to import their sibling package, but that mechanism
must be covered by the installed-bundle smoke test.

### 3. Prove the boundary with Factory Flow Control

The first engine capability is `engine/flow_control/`. It owns:

- parsing and validation of the playbook-state marker;
- parsing and validation of the supported FSM YAML subset;
- state graph navigation and output-glob ownership;
- transition and retry eligibility; and
- structured outcomes for allowed, blocked, and operational-error results.

[`phase`](../../packages/factory/scripts/phase) and
[`transition-lint`](../../packages/factory/scripts/transition-lint) become thin
adapters over this model. Each adapter retains its current command contract and
owns only argument parsing, environment/filesystem binding, presentation, and
process exit mapping. The extraction must preserve
[`ADR-0002`](../adr/0002-factory-owns-flow-control-orchestrator-is-a-trigger.md#decision):
Factory files remain the flow-control authority, while a human, skill, or
orchestrator remains a peer trigger.

The structured outcome is also the automation seam. An external trigger can
ask the model what is allowed and act on a typed result instead of scraping
terminal prose. The first release proves this seam in-process; it does not add
a daemon, service API, scheduler, or remote execution protocol.

### 4. Keep compatibility cleanup independent

Before extraction, plan one standalone cleanup story for known dead command
references. It must not be combined with behavior moves, so failures can be
attributed to either compatibility cleanup or structural change. The story
removes or corrects these current references:

- `feature-addition`, `greenfield-development`, and `brownfield-onboarding`
  call the deleted `charter-lint`, while `interface-contracts` still publishes
  it.
- `scope-map` assigns tests to the deleted `run-tests` command.
- `factory-guide` advertises a nonexistent `mutation-testing` script.
- `scaffold-arc42` and `STRUCTURIZR.md` advertise the unsupported
  `export-png` command.

Historical documents that explicitly describe a command's deletion remain
unchanged.

### 5. Order later extraction by evidence and blast radius

The remaining candidates are not equal-strength commitments. Planning uses the
following order and promotion rules:

| Order | Candidate                  | Current decision      | Risk / effort       | Entry condition                                                                    |
| ----: | -------------------------- | --------------------- | ------------------- | ---------------------------------------------------------------------------------- |
|     1 | Tracked-source test seam   | Commit                | Low / low           | None; prerequisite for structural work                                             |
|     2 | Factory Flow Control model | Commit                | Medium / high       | Characterize `phase` and `transition-lint` command contracts                       |
|     3 | Usage pipeline             | Later release         | Medium-high / high  | Flow Control extraction proves the engine packaging and adapter pattern            |
|     4 | Runtime adapter ownership  | Later release         | High / very high    | Policy contracts and cross-runtime fixtures exist for each adapter family          |
|     5 | Dispatch lifecycle         | Explore conditionally | High / very high    | Both dispatch promotion conditions below are met                                   |
|     6 | Installation lifecycle     | Last                  | Very high / highest | Earlier engine modules survive copied-bundle tests and update compatibility checks |

Dispatch is promoted from exploration to a committed module only when both of
these conditions hold:

1. Autonomous and review lifecycles have characterization tests through the
   command interface.
2. Either an external trigger needs structured non-terminal outcomes, or the
   next dispatch change crosses at least three of CLI routing, ledger
   transitions, worktree effects, gate execution, and merge closeout.

Until then, dispatch work extracts only already-proven leakage such as shared
glob matching; it does not pre-emptively split the lifecycle.

### 6. Assign runtime adapters to capabilities

The review found 17 production adapter files and 2,837 lines under
`config/hooks` and `config/extensions`. Their current and intended ownership is:

| Capability        | Before                                                                                      | After                                                                                                                                 |
| ----------------- | ------------------------------------------------------------------------------------------- | ------------------------------------------------------------------------------------------------------------------------------------- |
| Safety and scope  | Six shell, JSON, and TypeScript files contain related command-blocking and step-scope rules | A safety/scope engine capability owns policy data and contract fixtures; native adapters retain runtime parsing and response encoding |
| Usage capture     | Six hook and extension files bridge different CLI lifecycle events into usage capture       | A usage engine capability owns the canonical event and record operations; each runtime adapter maps native events into them           |
| Factory freshness | Three adapters independently expose freshness checks                                        | An installation capability owns freshness decisions; adapters retain lifecycle integration                                            |
| Pi dispatch       | Two TypeScript extensions contain dispatch and worktree orchestration                       | Dispatch owns lifecycle policy only after its promotion gate; Pi retains tool protocol and process integration                        |

Python, shell, and TypeScript are not forced through one implementation. Shared
policy data, schemas, and contract fixtures establish semantic parity where a
shared runtime library is impossible. Physical relocation of adapters is not
required to establish ownership.

## Scope

**In the first release:**

- Make tracked `packages/factory/scripts/` source the default Factory test
  surface.
- Add a separate installed-bundle smoke-test seam.
- Add command characterization for `phase` and `transition-lint` before moving
  their behavior.
- Create `packages/factory/engine/` with dependency rules that prevent imports
  from engine modules back into script entry points.
- Extract the canonical Flow Control marker, FSM, state-navigation, and decision
  model into `engine/flow_control/`.
- Retain `factory/scripts/phase` and `factory/scripts/transition-lint` as
  compatible thin adapters.
- Prove an in-process caller can consume a structured Flow Control outcome
  without parsing CLI prose.
- Verify `init-factory` distributes the engine and the copied commands execute
  without a separately installed package.
- Deliver the dead-command compatibility cleanup as a separate preparatory
  story and commit.
- Update the C4/arc42 model to show the engine capability and adapter
  boundaries.

**Explicitly deferred (do NOT plan stories for these):**

- Usage-capture extraction, until the Flow Control slice proves the engine and
  adapter pattern.
- Runtime hook and extension reorganization, because it needs policy contracts
  and cross-runtime fixtures before high-blast-radius edits are safe.
- Dispatch lifecycle modularization, until both promotion conditions in the
  Design are met.
- Installation lifecycle extraction, because it changes the mechanism that
  distributes and refreshes every other module and therefore remains last.
- A public automation API, daemon, scheduler, remote trigger, or orchestration
  service. The first release creates a callable seam but no external protocol.
- A generic parser, validation framework, `common.py`, or repository-wide
  rewrite. Reuse alone is not a module boundary.
- Moving Markdown or YAML process definitions out of their existing
  `agents/`, `skills/`, `playbooks/`, and `rulebooks/` locations.

## Design Details

### Compatibility contract

For each changed script, existing tests and new characterization fixtures form
an explicit adapter contract. A refactor is incompatible if, for the same
inputs and filesystem state, it changes any of the following without a later,
separately accepted proposal:

- executable path or argument grammar;
- semantic exit-code category;
- machine-readable stdout or human-readable stderr placement;
- finding/report shape and stable finding codes;
- state-marker, report, or other filesystem effects; or
- supported zero-install execution from a copied Factory.

### Dependency direction

The permitted direction is:

```text
scripts/ and config adapters → engine capability → policy data / schemas
```

The reverse direction is forbidden. Engine capabilities may depend on another
engine capability only when the architecture model declares the relationship;
they may not acquire a generic shared layer to avoid making that decision.

### Slice and rollback discipline

Each module extraction is a behavior-preserving slice with three separable
changes: characterization, engine extraction, then adapter thinning. The old
adapter contract remains available throughout the slice. If copied-bundle or
contract tests fail, the extraction can be reverted without reverting the
independent compatibility cleanup.

### Automation boundary

Structured Flow Control results express decisions such as `allowed`, `blocked`,
and `operational_error`, together with stable reason data. They do not execute
an external scheduler or grant a caller new authority. Trigger identity and
authorization remain concerns of the invoking adapter.

## Open Questions

There are no unresolved decisions for the first release. Later module work is
governed by the explicit entry conditions and deferrals above; meeting an entry
condition permits a new proposal or scope amendment, not automatic inclusion
in this release.

## Completion Criteria

- Factory tests load tracked scripts from `packages/factory/scripts/` by
  default, and no shared fixture silently selects the ignored installed mirror.
- An installed-bundle smoke test installs the Factory into a temporary target
  and successfully invokes `phase` and `transition-lint` from that copy,
  including their imports from `factory/engine/`.
- A distribution test fails if an engine file required by either adapter is
  omitted from the installed Factory.
- Command-level characterization tests cover the supported arguments, exit-code
  categories, stdout/stderr placement, and filesystem effects of `phase` and
  `transition-lint` before and after extraction.
- One implementation under `packages/factory/engine/flow_control/` owns marker
  parsing, supported FSM parsing, state navigation, output ownership, and
  transition decisions; `phase` and `transition-lint` contain no duplicate
  implementation of those rules.
- An in-process contract test obtains and asserts a structured Flow Control
  outcome without invoking a subprocess or parsing rendered terminal output.
- Existing `factory/scripts/phase` and `factory/scripts/transition-lint`
  commands retain their paths, accepted arguments, semantic exit codes,
  output-channel contract, stable finding codes, and filesystem effects.
- Dependency enforcement rejects an import from `engine/` back into
  `scripts/` and allows the declared adapter-to-engine direction.
- The standalone compatibility-cleanup story removes or corrects every active
  dead-command reference itemized in the Design while preserving historical
  deletion records.
- [`architecture.dsl`](../arc42/architecture.dsl) and the arc42 building-block,
  runtime, and cross-cutting views describe the engine, its Flow Control
  capability, the stable adapters, and their dependency direction.
- The complete Factory test suite passes against tracked source, and the
  installed-bundle smoke suite passes against a freshly copied Factory.

## Guiding Rule

Move an invariant into `engine/` only when more than one adapter needs the same
decision and tests can prove that every existing command contract survives the
move.
