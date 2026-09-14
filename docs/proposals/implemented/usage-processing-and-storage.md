---
schema_version: 2
title: "Local Usage Processing and Analysis"
status: implemented
owner: agent-factory
created: 2026-07-28
updated: 2026-09-13
supersedes:

impact:
  scope: cross_project
  architecture_change: true
  external_contract_change: true
  boundaries:
    - packages/factory/scripts/usage-capture
    - packages/factory/scripts/init-factory
    - packages/factory/scripts/update-factory
    - packages/factory/scripts/remove-factory
    - packages/factory/contracts/usage-record/  # new: created by this feature
    - packages/usage/pyproject.toml
    - packages/usage/uv.lock
    - docs/spec/supplementary_specs/interface-contracts.md
    - docs/arc42/architecture.dsl
    - docs/arc42/CONTEXT-MAP.md

governance:
  assurance: critical
  risk_domains:
    - compatibility
    - data_integrity
    - privacy
    - reliability

estimate:
  as_of: 2026-09-11
  basis: decomposition
  confidence: low
  human_review_hours:
    min: 5
    max: 10
  normalized_tokens:
    min: 25000
    max: 55000
  estimated_consumption:
    min: 450000
    max: 990000
    overhead_multiplier: 18
    playbook: feature-addition
---

# Feature Request: Local Usage Processing and Analysis

## Summary

Add a local analytical layer over the JSONL records already written by Factory
usage capture. DuckDB queries the records in place and exposes version-controlled
views that convert CLI-specific cumulative snapshots into canonical runs and
session totals. A query command and DuckDB's bundled local UI consume those
views; Parquet is an optional export, not maintained state.

The first release answers: *where did Factory usage go, and can that answer be
reproduced from the retained local evidence without operating a database or
remote service?*

## Motivation

Factory already records usage under `.agent-factory/usage/`. The records carry
project, CLI, session, parent, agent, model, normalized token, provider token,
cache, outcome, Git, and transcript-reference fields. The data is durable and
auditable, but it is not convenient to query.

Correct interpretation is also CLI-specific. Claude Code and Pi require root
and child usage to be combined; Codex and Copilot root snapshots already include
child usage. Several CLIs emit cumulative snapshots, so summing every JSONL line
overcounts a session. A dataframe loaded directly from the files does not solve
these rules by itself.

The prior accepted design introduced PostgreSQL, a transactional projector,
Docker Compose, Grafana, credentials, remote-cluster configuration, and
retention workflows. Those components solve multi-user service operation and
central storage. They are not required for local monitoring and analysis of
files already retained on one machine.

The current
[`CONTEXT-MAP.md`](../../arc42/CONTEXT-MAP.md)
still describes Usage Accounting as a PostgreSQL-backed projector. That text
documents the superseded accepted design. Updating the context map and the
canonical architecture model to the local JSONL-to-DuckDB boundary is part of
this feature; proposal intake does not leave contradictory architecture as the
planning baseline.

## Core Principles

- Raw JSONL records remain the authoritative evidence and are never rewritten
  by analysis.
- Every derived result is reproducible from a declared set of JSONL files and a
  versioned query model.
- CLI accounting rules are named domain rules with deterministic fixture
  coverage, not dashboard expressions.
- Analysis is local, read-only, and independent of transcript contents.
- Capture never depends on DuckDB, a dashboard, or successful analysis.
- Parquet is a disposable export. It is not a second source of truth and has no
  automatic synchronization lifecycle.
- Agentic creation and deterministic validation remain separate: code and SQL
  create the model; executable gates decide whether its contracts hold.

## Design

### Boundary

Factory remains the producer. Its capture hooks and
[`usage-capture`](../../../packages/factory/scripts/usage-capture) continue to
append JSONL records without waiting for an analytical consumer.

A new `packages/usage/` subproject in the monorepo is the local analytical
consumer. At runtime it is installed into target projects as
`.agent-factory/usage-analysis/` through the `init-factory` lifecycle (see
*Distribution and lifecycle* below). It owns:

- DuckDB SQL views and accounting rules;
- the local query command;
- optional Parquet export;
- a documented DuckDB UI exploration path;
- fixtures and deterministic quality gates for those artifacts.

The boundary is the usage record, not the transcript. Analysis may expose the
`transcript_ref` value for audit navigation, but it must not open, copy, index,
or tokenize the referenced transcript.

**Contract ownership and placement.** Factory owns the usage-record contract.
The canonical source lives in the Factory package at
`packages/factory/contracts/usage-record/`, containing:

- `contract.yaml` — the YAML ownership and compatibility manifest (owner,
  current version, compatibility policy, accepted consumer version range);
- `v1.schema.json` — the JSON Schema Draft 2020-12 record schema.

At install time, `init-factory` copies the contract into the installed
analytical module at `.agent-factory/usage-analysis/contract/`. The consumer
reads only its installed copy and declares which contract versions it accepts.
The canonical source in `packages/factory/` is the authority; the installed
copy is a distribution artifact.

A dedicated `packages/usage/scripts/usage-contract-check` validates the
installed schema, each selected JSONL object, cross-field invariants that JSON
Schema cannot express, and producer/consumer version agreement. The existing
[`schema-validate`](../../../packages/factory/scripts/schema-validate) remains
scoped to research artifacts and is not extended for this contract.

### Data flow

1. Factory appends records beneath `.agent-factory/usage/` as it does today.
2. The query command snapshots the matching top-level JSONL paths at query
   start. It excludes the `transcripts/` subtree and lifecycle diagnostics.
3. A strict preflight validates every selected line. Valid lines and preflight
   failures are both registered as query-scoped DuckDB relations: the valid
   relation feeds downstream views; the failure relation (source file, line
   number, field, failure code) feeds the `capture_health` view. Both relations
   exist only for the duration of the query process.
4. DuckDB reads the valid relation with an explicit column schema and adds
   source-file identity. Schema inference is not part of the production path.
5. Version-controlled SQL views select canonical snapshots and apply the
   accounting rule for each CLI.
6. The query command returns a table, JSON, a dataframe-compatible result, or an
   optional Parquet export.
7. When selected, DuckDB's bundled UI opens the same published views for ad hoc
   SQL exploration. No repository-owned dashboard formulas exist in release 1.

No ingestion daemon, background projector, database server, container, or
remote data service participates in this flow. DuckDB's optional UI starts an
ephemeral localhost server for one operator session; it is not an application
service or data authority.

### Query model

The first release publishes these logical views:

| View                      | Contract                                                                                                                        |
| ------------------------- | ------------------------------------------------------------------------------------------------------------------------------- |
| `raw_usage_snapshots`     | One typed row per valid source line, including source file and line identity.                                                   |
| `latest_run_snapshots`    | The latest cumulative snapshot for each logical run, selected by capture sequence and deterministic tie-breakers.               |
| `canonical_session_usage` | One non-duplicated accounting result per session, using the registered conservation rule for its CLI.                           |
| `usage_by_dimension`      | Additive totals grouped by time period, project, CLI, provider, model, agent, branch, and exit status.                          |
| `cache_efficiency`        | Provider-qualified cache signals that preserve unavailable and input-only states instead of coercing them to zero.              |
| `capture_health`          | Counts of valid records and preflight failures from the query-scoped failure relation, grouped by failure code and source file. |

The query command exposes only published views. Experimental SQL may read raw
records, but stable exports depend on published views.

### Accounting registry

Accounting is driven by a closed registry using the exact producer CLI values:

- **`claude-code` (Claude Code):** select the latest root snapshot and add each distinct child
  run once.
- **`pi` (Pi):** select the root record and add each distinct descendant once.
- **`codex` (Codex):** select the latest inclusive root snapshot; child records provide
  attribution and are not added to the total.
- **`copilot` (GitHub Copilot CLI):** select the latest inclusive root snapshot; child
  records provide attribution and are not added to the total.

An unknown CLI is a contract error. It must not silently inherit another CLI's
rule. The registry and its fixture matrix change together.

For all four registry entries, logical-run identity is exactly
`(cli, session_id, run_id)`. Claude Code and Pi use that key to include each
additive child or descendant once. Codex and GitHub Copilot CLI use it to keep
descendant attribution distinct without adding it to the inclusive root.
`parent_run_id` defines ancestry but is not part of identity. Source position,
capture sequence, and record content are excluded from logical-run identity.
Before latest-snapshot selection, every evidence snapshot for one logical-run
key must carry the same `parent_run_id`, with null treated as a value. Any
disagreement fails strict preflight with
`USAGE_ANCESTRY_PARENT_CONFLICT`; no snapshot is allowed to establish or
override the logical run's parent.
Within each `(cli, session_id)` partition, exactly one root has a null
`parent_run_id`. Every other run names an existing run in the same partition,
and the resulting directed graph is acyclic and fully reachable from that root.
Missing parents, cross-session or cross-CLI parents, self-links, cycles, and
zero or multiple roots fail strict preflight with stable ancestry codes.

`usage_by_dimension` accepts an ordered, duplicate-free subset of `project`,
`cli`, `provider`, `model`, `agent`, `branch`, and `exit_status`, plus a time
granularity of `none`, `hour`, `day`, `week`, or `month`. For non-empty input,
the default is no dimensions and `none`, which returns one total over all
canonical sessions. Empty input returns the declared typed zero-row result.
Unknown or duplicate dimensions are errors. Time buckets use UTC and ISO Monday
week starts.

### Local Python and dataframe interface

DuckDB is the computation engine and SQL is the canonical transformation
language. The Python entry point supplies validated paths and parameters and
runs published queries.

**Release-1 required conversions:** DuckDB relations and `pyarrow.Table`
instances. The usage-analysis package declares both DuckDB and a compatible
PyArrow release as direct dependencies and locks their complete transitive
closure. DuckDB supplies the Arrow conversion API; the separately installed
PyArrow package supplies the Python table type.

**Explicitly deferred conversions:** Polars DataFrames and Pandas DataFrames.
Both require additional dependencies (polars, pandas) that are not part of the
release-1 locked dependency set. They can be added in a future release as
optional extras without changing the SQL model or accounting rules.

Presentation code outside the SQL model (formatting, sorting for display) may
use any available library. It must not reimplement snapshot selection or
conservation rules.

### Optional Parquet export

Parquet export is explicit and rebuildable:

```text
usage-query <published-view> --format parquet --output <path>
```

The command writes to a temporary sibling and replaces the destination only
after the export passes its round-trip check. It records the query-model
version and input-set digest in Parquet metadata or a colocated manifest.

There is no scheduled export, incremental checkpoint, automatic invalidation,
or freshness promise in release 1. A caller that needs current data reruns the
export.

## Quality Gates

The analytical layer is trusted only through deterministic gates. Each
observable contract has one owning layer; query-command and export tests do not
duplicate SQL accounting tests.

| Observable contract                                                                                                    | Owning gate                                   | Required proof                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                        | Blocking result                                                             |
| ---------------------------------------------------------------------------------------------------------------------- | --------------------------------------------- | ------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- | --------------------------------------------------------------------------- |
| A selected JSONL line has the accepted field names, types, nullability, invariants, and nested `transcript_ref` shape. | `packages/usage/scripts/usage-contract-check` | Producer-generated fixtures and retained compatibility fixtures validate against JSON Schema Draft 2020-12. The gate separately checks `normalized_total` equals input plus output; identifiers, timestamps, and non-negative counters satisfy their declared constraints.                                                                                                                                                                                                                                                            | Non-zero, with every detectable source file, line, field, and failure code. |
| Every supported CLI maps to exactly one conservation rule.                                                             | Accounting registry gate                      | Registry keys equal the exact producer set `claude-code`, `pi`, `codex`, and `copilot`. No unknown, aliased, or missing key is accepted.                                                                                                                                                                                                                                                                                                                                                                                              | Non-zero, naming missing and extra keys.                                    |
| Cumulative snapshots and child runs conserve usage without duplication.                                                | SQL accounting contract tests                 | A fixture matrix covers the unique rooted hierarchy, repeated root snapshots, distinct children, duplicate child evidence, nesting, zero values, null provider fields, failed runs, and equal-timestamp tie-breaks for all four CLIs. Exact expected totals are asserted.                                                                                                                                                                                                                                                             | Test failure with fixture and mismatched measure.                           |
| Published results do not depend on file enumeration order.                                                             | Reproducibility gate                          | The same fixture corpus queried in at least two path orders yields the same sorted logical rows and content digest.                                                                                                                                                                                                                                                                                                                                                                                                                   | Non-zero on any logical difference.                                         |
| A malformed line or run hierarchy cannot silently alter totals.                                                        | Operational preflight                         | A corpus containing valid, malformed, truncated, wrong-type, invariant-breaking, missing-parent, cross-boundary-parent, self-parent, cyclic, multiple-root, and two otherwise valid snapshots for one logical run with conflicting `parent_run_id` values produces all six expected `USAGE_ANCESTRY_*` diagnostics; stable queries refuse to run on an invalid selected set.                                                                                                                                                          | Query exits non-zero before DuckDB accounting runs.                         |
| Analysis remains local and transcript-blind.                                                                           | Boundary integration test                     | Queries pass when every referenced transcript is absent and when transcript references are unreadable. Production SQL contains no remote readers; the subproject declares no network client, server, cloud-secret, or container dependency.                                                                                                                                                                                                                                                                                           | Test or dependency gate failure.                                            |
| Published views are the sole source for stable output.                                                                 | Query-command integration tests               | Table and JSON outputs match the relevant published view; dataframe conversions preserve schema and nulls.                                                                                                                                                                                                                                                                                                                                                                                                                            | Test failure.                                                               |
| A Parquet export is complete, attributable, and rebuildable.                                                           | Parquet round-trip test                       | Exported logical rows and schema equal the source view, provenance identifies query-model version and input-set digest, and an interrupted write leaves the previous destination intact.                                                                                                                                                                                                                                                                                                                                              | Export fails and does not replace the destination.                          |
| Factory capture remains independent.                                                                                   | Existing capture contract tests               | Capture succeeds with the `usage/` subproject absent and with all analytical outputs missing or corrupt.                                                                                                                                                                                                                                                                                                                                                                                                                              | Existing Factory test gate failure.                                         |
| Install, update, and removal are manifest-tracked, data-safe, and idempotent.                                          | Distribution lifecycle tests                  | `--with-usage` at init time and `--add usage` post-hoc both install the module and record it in the manifest; `--update usage` replaces the module and preserves data; `--remove usage` deletes the module without touching `.agent-factory/usage/`; `remove-factory` removes `usage-analysis/` as part of full uninstall; re-running any operation is a clean no-op. Contract version incompatibility on update aborts before replacing files. The argparse model accepts component names alongside CLI names with correct dispatch. | Test failure or data-directory modification.                                |

### Gate placement

- The usage-record contract gate is a standalone read-only command usable both
  against fixtures and against a selected runtime usage directory.
- The project-owned pytest command declared in
  [`docs/testing.yaml`](../../testing.yaml) owns accounting, query-command,
  Parquet, and boundary contracts at commit and phase boundaries.
- [`dependency-check`](../../../packages/factory/scripts/dependency-check) owns the
  dependency rules declared in
  [`architecture.dsl`](../../arc42/architecture.dsl): Factory must not depend on
  Usage Analysis, and Usage Analysis must consume the published record contract
  without importing Factory implementation modules.
- Runtime JSONL files are local evidence, not repository fixtures. Repository
  gates validate synthetic and compatibility fixtures; a user explicitly runs
  the operational preflight against private runtime data.
- Distribution lifecycle tests own the install, update, removal, and contract
  version compatibility checks in `init-factory`. They run against a temporary
  target directory, not the developer's own project install.
- Gates return exit codes and structured diagnostics. A dashboard screenshot,
  notebook output, or agent report is not gate evidence.

### Fixture policy

Fixtures are minimal and synthetic. They contain no copied transcripts or user
prompts. Each fixture states which equivalence class, boundary, or failure mode
it owns. Adding a second test for an existing case requires identifying a new
boundary or replacing weaker coverage.

Compatibility fixtures include records produced by the implementation that
predates this proposal. A producer contract change must update the versioned
contract, add forward- and backward-compatibility cases, and demonstrate that
the supported reader range is explicit before the change can merge.

## Scope

**In the first release:**

- A local `usage/` subproject with isolated, directly declared DuckDB and
  PyArrow dependencies, a committed lockfile, SQL, Python entry points, tests,
  fixtures, and concise operating documentation.
- A versioned machine-readable contract for the existing Factory usage record,
  expressed as a JSON Schema Draft 2020-12 schema plus an ownership and
  compatibility manifest, owned by Factory and consumed by the analytical
  subproject.
- Strict JSONL preflight with complete structured diagnostics.
- DuckDB views for raw snapshots, latest runs, canonical session accounting,
  dimensional totals, cache efficiency, and capture health.
- A closed four-CLI accounting registry and its deterministic fixture matrix.
- A local query command with table and JSON output plus DuckDB relation and
  PyArrow table conversions.
- Explicit Parquet export with atomic replacement and provenance checks.
- A documented DuckDB UI launch path whose executable smoke check resolves the
  six-view query-model bootstrap without starting or fetching the UI. Actual
  launch remains optional local exploration, not gate evidence.
- Updates to [`architecture.dsl`](../../arc42/architecture.dsl), derived arc42
  explanations, and [`CONTEXT-MAP.md`](../../arc42/CONTEXT-MAP.md) that replace the
  PostgreSQL projector with the local Usage Analysis bounded context and its
  published-record dependency.
- Distribution through `init-factory`: `--with-usage` at init time,
  `--add usage` post-hoc, `--update usage` to upgrade in place, and
  `--remove usage` to uninstall — all manifest-tracked, data-safe, extending
  the existing argument model from CLI-only to CLI-and-component.
- Update to
  [`interface-contracts.md`](../../spec/supplementary_specs/interface-contracts.md)
  documenting the new init-factory component operations and the
  `update-factory` boundary with installed components.
- Quality gates and test ownership as specified above.

**Explicitly deferred (do NOT plan stories for these):**

- PostgreSQL, SQLite, or a persistent DuckDB database as an authoritative
  store: retained JSONL already supplies local durability.
- Automatic or incremental Parquet materialization: it adds freshness,
  checkpoint, and invalidation state before measurements justify it.
- Marimo, Jupyter, Grafana, and custom dashboard applications: release 1 first
  establishes which queries and visualizations are useful. A later proposal can
  promote stable views into a dashboard product without changing accounting.
- DuckDB's community `dash` extension: release 1 uses only the bundled UI and
  does not add a third-party dashboard extension to the trusted runtime.
- Docker Compose, containers, services, HTTP APIs, authentication, TLS, remote
  clusters, cloud storage, GitHub Secrets, and cloud secret managers: release 1
  is local and process-bound.
- Centralized multi-project collection, synchronization, multi-host ingestion,
  concurrent analytical writers, and user access control: there is no shared
  service boundary.
- Provider price catalogs and currency-cost calculations: provider rates and
  billing truth require a separate, time-versioned contract.
- Transcript-content search or indexing: the analytical boundary consumes
  usage records only.
- Automatic retention or deletion of raw usage evidence: analysis is read-only.
- Polars and Pandas DataFrame conversions: they add optional dependencies
  beyond the required DuckDB and PyArrow runtime and can be introduced without
  changing accounting or SQL views.

## Design Details

### Contract evolution

The JSON Schema Draft 2020-12 contract is versioned independently of the query
model. The first contract version describes the records already produced; it
does not require rewriting retained files. The adjacent YAML manifest records
ownership, compatibility policy, and the consumer's accepted version range. A
reader declares the contract versions it accepts. Additive producer changes are
not assumed compatible until fixtures prove the reader behavior.

### Estimate basis

The low-confidence estimate decomposes the release into the published contract
and gate, JSONL preflight, DuckDB query model, four-CLI accounting fixtures,
query and Parquet interfaces, the bundled-UI operating path, the
`init-factory` distribution lifecycle (install, update, remove with
manifest tracking and contract version checks),
architecture/specification updates, and review remedies. It excludes dashboard
development and every deferred service and remote-deployment component. The
18× consumption multiplier reflects the full feature-addition path with
specification, architecture, planning, implementation, and independent review
gates.

### Input identity and ordering

The query start snapshots an explicit, sorted file list. A source path is made
relative to the selected usage directory, converted to `/` separators, stripped
of `.` segments, rejected if absolute or containing `..`, decoded as valid
UTF-8, and Unicode-normalized to NFC per segment. The normalized path and
one-based positive line number form evidence identity and remain available in
raw diagnostic output.

Logical snapshot selection takes the maximum tuple
`(capture_sequence, normalized_source_path, source_line)`. Capture sequence and
line number compare numerically. Normalized paths compare lexicographically by
unsigned UTF-8 bytes. This means the later line wins within one file when the
capture sequence is equal.

Record IDs alone are not unique across all retained files. The analytical key
therefore includes source identity until records have been reduced to the
source-independent logical-run key defined in the accounting registry.

### Failure behavior

Stable queries are strict by default. When the selected set contains any
preflight failures, the query registers both the valid and the failure
relations. The `capture_health` view is always available; it reports valid
counts and failure diagnostics from the query-scoped failure relation. All
other published views (accounting, dimensional, cache) require the failure
count to be zero — they refuse to run and produce a non-zero exit rather than
report a partial total. A diagnostic mode can report all valid and invalid
lines without running accounting, but it labels the result incomplete and
cannot emit a stable export.

An empty usage directory is valid. Published views return typed empty results,
and the query command shows an empty result rather than an error.

### Privacy and filesystem behavior

The query process opens only selected top-level record files and its explicit
output path. It does not follow `transcript_ref`, recurse into transcript
directories, or send usage data over a network. Generated DuckDB, Parquet, and
UI state files are private, git-ignored, and safe to delete.

### Dependency isolation

Analytical dependencies do not enter Factory's capture runtime. The
`packages/usage/` subproject declares DuckDB and PyArrow directly in its own
`pyproject.toml` and commits its own `uv.lock`; neither package enters Factory's
dependency graph. At install time, `init-factory` copies the module into
`.agent-factory/usage-analysis/` without adding dependencies to Factory's
own runtime. Removing the installed module (`init-factory --remove usage`)
leaves capture behavior unchanged.

### Distribution and lifecycle

The analytical module is developed in `packages/usage/` inside the monorepo and
distributed through the existing `init-factory` install mechanism — the same
path Factory itself uses. There is no separate `uv tool install` or PyPI
package.

**Interface change.** Today init-factory's `--add` and `--remove` accept only
CLI names (`claude`, `copilot`, `pi`, `codex`). This proposal extends them to
also accept *component* names. "usage" is the first component. A component
differs from a CLI: it has no dot-dir, no symlinks, no guardrails, and no
capture hooks. Instead it copies a self-contained module into
`.agent-factory/` and records that in the install manifest. The argparse model
changes from a flat `choices=KNOWN_CLIS` to a union of CLI names and component
names, with dispatch to the appropriate handler based on which namespace the
argument belongs to. The manifest gains an `installed_components` key (a dict
keyed by component name) alongside the existing `cli` key.

Today `--update` does not exist on init-factory; the separate `update-factory`
script handles Factory-core updates. This proposal adds `--update <component>`
to init-factory for component-scoped updates. `update-factory` continues to
own the Factory-core refresh (replacing `factory/`, re-deriving symlinks and
hooks). The division: `update-factory` updates the Factory install;
`init-factory --update usage` updates an individual opt-in component. When
`update-factory` runs, it does not touch installed components; when
`init-factory --update usage` runs, it does not touch Factory-core or CLI
wiring.

**Installation.** `init-factory --with-usage` at initial project setup, or
`init-factory --add usage` post-hoc, copies the usage-analysis module into the
target project. The installed location is `.agent-factory/usage-analysis/`,
distinct from the `.agent-factory/usage/` directory that holds JSONL data.
The install is recorded in the existing
`.agent-factory/factory-install.json` manifest under `installed_components` so
that removal, update, and re-install are tracked alongside the rest of the
Factory install.

**Installed layout:**

```text
.agent-factory/
  usage/                  # JSONL data (existing, untouched by install)
    *.jsonl
  usage-analysis/         # installed analytical module (new)
    contract/             # JSON Schema + YAML manifest + validator
    sql/                  # versioned .sql view definitions
    accounting/           # CLI registry + conservation rules
    query.py              # entry point
    manifest.json         # install metadata: source commit, version, date
```

**Update.** `init-factory --update usage` replaces the installed module from
the current source checkout and writes a new `manifest.json`. Before
replacing, the update reads the installed contract version; if the new module's
accepted contract range does not cover the installed contract version, the
update warns and aborts unless forced. Data in `.agent-factory/usage/` is
never touched. `update-factory` does not update components; it records their
presence but delegates component updates to `init-factory --update`.

**Removal.** `init-factory --remove usage` deletes `.agent-factory/usage-analysis/`
and its `installed_components` manifest entry. It never touches
`.agent-factory/usage/` (the data directory). Capture continues writing
regardless of whether the analytical module is installed. After removal, the
query command and DuckDB views are unavailable; raw JSONL remains.

**Full Factory removal.** The existing `remove-factory` script deletes the
entire `.agent-factory/` directory. This release updates `remove-factory` to
be component-aware: it removes `usage-analysis/` as part of its manifest-driven
cleanup but continues to delete `.agent-factory/usage/` (the data directory)
along with all other `.agent-factory/` contents, as it does today. Component
removal does not change the full-removal semantics; `remove-factory` remains
a complete uninstall. Users who want to preserve usage data before a full
removal must copy it themselves — the same as all other `.agent-factory/`
state.

**Contract synchronization.** Because `init-factory` installs both Factory
and the usage-analysis module from the same source checkout, the JSON Schema
contract ships inside the installed module and is guaranteed consistent at
install time. The `manifest.json` records the source commit, allowing
`update-factory` to detect version drift when reporting install status.

**Opt-in, not default.** The DuckDB dependency is heavier than the base
Factory scripts. Usage-analysis is never installed unless explicitly requested.
A Factory installation without `--with-usage` behaves exactly as it does today.

### Installed runtime and invocation

The installed module at `.agent-factory/usage-analysis/` is a self-contained
Python package with an inline dependency declaration (`[project]` table in a
bundled `pyproject.toml`). The query command is invoked through `uv run`:

```text
uv run --project .agent-factory/usage-analysis usage-query <view> [options]
```

`uv run --project` resolves and caches the declared direct dependencies
(DuckDB and PyArrow) and their transitive closure on first invocation, using
the lockfile shipped with the module. The lockfile pins a mutually compatible
pair and is copied with the installed package. No pre-installation step,
virtualenv creation, or system-wide package install is required; `uv` is the
only prerequisite, and it is already required by Factory.

**Input selection.** The default input location is `.agent-factory/usage/` —
the sibling data directory. The query command resolves this relative to the
project root (the directory containing `.agent-factory/`). An explicit
`--usage-dir <path>` overrides the default. The selected set is the sorted
list of `*.jsonl` files at the top level of the input directory; subdirectories
(`transcripts/`, `usage-control/`) are excluded.

**Offline operation.** The distribution gate verifies an install and query from
a cache containing every locked DuckDB, PyArrow, and transitive artifact while
network access is disabled. After the first online `uv run` populates that
cache, the query command therefore runs without network access. The SQL views,
accounting registry, and contract schema are bundled files, not fetched
resources. The only filesystem access is reading the selected JSONL files and
writing to the explicit output path (when `--format parquet` or `--output` is
given).

### Exploration surface

DuckDB's bundled UI is the release-1 exploration surface. The subproject
documents how to open the query model and inspect published views, but does not
ship saved charts or dashboard formulas. Query execution and usage data remain
local. Installing or opening the UI may fetch extension or frontend assets;
that optional bootstrap must not affect the query command or the deterministic
test path.

The UI is operator convenience, not gate evidence. Automated tests execute the
same published SQL through DuckDB's programmatic interface. Screenshots,
notebooks, and saved UI state are not release artifacts.

## Open Questions

None. The stakeholder selected DuckDB's bundled UI for initial exploration and
deferred dashboard products on 2026-09-11.

## Completion Criteria

01. Existing usage records can be queried locally without a database server,
    container, network connection, or transcript access.
02. Every selected JSONL line is either accepted by the versioned record
    contract or reported with source file, line number, field, and stable failure
    code before stable accounting begins.
03. The record schema, producer, fixtures, and accounting registry use exactly
    `claude-code`, `copilot`, `codex`, and `pi`.
04. The accounting fixture matrix proves the declared root, snapshot, child,
    nesting, null, zero, failure, duplicate, and tie-break behavior for every
    supported CLI, including all six malformed-ancestry preflight codes.
05. Canonical session totals conserve usage without double-counting children.
06. Reordering the same selected files does not change sorted logical output or
    its content digest.
07. Published views cover raw snapshots, latest runs, canonical sessions,
    dimensional usage, cache efficiency, and capture health. Query-model-v1
    declares every column, DuckDB type, key, null rule, and stable result order.
08. The query command emits typed table and JSON results from published views.
    DuckDB relation and PyArrow table conversions preserve field types and nulls.
09. An optional Parquet export round-trips to the same logical rows and schema,
    records query-model and input-set provenance, and never replaces a valid
    destination with a partial file.
10. An executable documentation smoke check verifies that the documented
    DuckDB UI command loads the query-model-v1 bootstrap for exactly the six
    published views without installing, starting, or fetching the UI. Actual UI
    launch remains optional operator activity and is not gate evidence.
11. Capture contract tests pass when all analytical components and derived
    outputs are absent.
12. `uv run pytest --tb=short --quiet`, as declared in
    [`docs/testing.yaml`](../../testing.yaml), owns the analytical contract and
    integration tests;
    [`dependency-check`](../../../packages/factory/scripts/dependency-check) owns
    the two architecture dependency rules. Both run locally and return non-zero
    on a blocking failure.
13. [`architecture.dsl`](../../arc42/architecture.dsl), its derived arc42
    explanations, and [`CONTEXT-MAP.md`](../../arc42/CONTEXT-MAP.md) describe local
    JSONL-to-DuckDB analysis and contain no PostgreSQL projector or remote Usage
    Accounting dependency.
14. `init-factory --with-usage` and `init-factory --add usage` install the
    analytical module into `.agent-factory/usage-analysis/`, record it in the
    install manifest, and leave `.agent-factory/usage/` (the data directory)
    untouched.
15. `init-factory --update usage` replaces the installed module, preserves data,
    and aborts with a diagnostic when the new module's accepted contract range
    does not cover the installed contract version.
16. `init-factory --remove usage` deletes the analytical module and its manifest
    entries without modifying data files. Capture continues writing after
    removal.
17. Each distribution operation is idempotent: re-running it is a clean no-op.
18. [`interface-contracts.md`](../../spec/supplementary_specs/interface-contracts.md)
    documents the new init-factory component operations (`--with-usage`,
    `--add usage`, `--update usage`, `--remove usage`) and the division of
    responsibility between `init-factory --update` (components) and
    `update-factory` (Factory-core).
19. `remove-factory` removes `usage-analysis/` as part of its manifest-driven
    full uninstall. Full removal continues to delete the entire
    `.agent-factory/` directory including usage data.
20. The query command is invocable through
    `uv run --project .agent-factory/usage-analysis` with no prior installation
    step beyond `init-factory`. The default input location is
    `.agent-factory/usage/`; `--usage-dir` overrides it. DuckDB and PyArrow are
    direct dependencies pinned with their transitive closure. A complete
    locked-artifact cache supports
    installation and query execution with network access disabled.

## Guiding Rule

Retain evidence once; derive every answer locally; trust only results whose
accounting rules pass deterministic gates.

## Review — 2026-09-11

Reviewer: proposal-review-agent
Reviewed commit: 2320570f62d28c8b1f8e20f3517d6047bcf27f5d
Note: proposal has uncommitted working-tree changes; review is against working-tree content.
Disposition: findings

### Findings

| ID      | Severity | Check | Status   | Finding                                                                                                                                                                                                                                                                                                                                                               |
| ------- | -------- | ----- | -------- | --------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| PROP-01 | major    | 05    | resolved | Boundary path `factory/scripts/usage-capture` is gitignored (installed copy). The tracked source is `packages/factory/scripts/usage-capture`. `git show HEAD:factory/scripts/usage-capture` fails at the reviewed commit. The proposal claims to affect a boundary that cannot be inspected in the repository's version-controlled tree.                              |
| PROP-02 | minor    | 01    | resolved | Completion criterion 12 is a meta-constraint ("declared test and dependency-gate mechanisms") that does not name the mechanisms. A verifier cannot check it without first identifying what those mechanisms are. Naming them (e.g., pytest, the dependency-direction gate, pre-commit hooks) would make the criterion directly testable.                              |
| PROP-03 | minor    | 02    | resolved | The architecture model update needed to register the new `usage/` bounded context is not in the explicit "In" scope list, yet the Quality Gates section assumes it: "the existing dependency-direction gate owns the declared Factory-to-Usage direction after the architecture model includes the new subproject." Planning needs this as an explicit scope item.    |
| PROP-04 | minor    | 06    | resolved | The machine-readable contract format (JSON Schema, YAML schema, TypedDict, custom DSL) is an unresolved design decision that affects the contract gate, fixture format, and compatibility testing approach. It is neither decided in the Design section, listed as an open question, nor explicitly deferred.                                                         |
| PROP-05 | minor    | 08    | resolved | All three estimate fields are `unknown` despite well-defined scope (6 SQL views, 4 CLI accounting rules, a query command, Parquet export, a dashboard, 10 quality gates across a new subproject with architecture change). A rough range at low confidence would give Planning a resource signal.                                                                     |
| PROP-06 | minor    | 04    | resolved | The context map (`docs/arc42/CONTEXT-MAP.md`, a declared boundary) describes Usage Accounting as persisting "canonical usage in PostgreSQL" — the approach this proposal explicitly replaces. The proposal neither notes this contradiction nor includes a context-map update in its scope. Planning would encounter a boundary document that contradicts the design. |

### Summary

The proposal is well-structured and substantially ready to plan from. The design is highly decomposable, the accounting registry is sound and consistent with the capture implementation, the core principles are achievable by the described architecture, the scope partition is defensible, and the motivation clearly distinguishes this work from the backlog. One major finding blocks: the primary boundary reference uses a gitignored path instead of the tracked source path (PROP-01). Five minor findings address a non-specific completion criterion (PROP-02), an implicit but unlisted scope item for the architecture model update (PROP-03), an unresolved contract-format decision (PROP-04), uninformative estimates (PROP-05), and a boundary document whose content contradicts the proposed design (PROP-06). PROP-01 must be corrected; PROP-03 and PROP-06 should be resolved before this reaches a planning agent.

### Resolutions — 2026-09-11

| ID      | Status   | Verification                                                                                                                                                                                 |
| ------- | -------- | -------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| PROP-01 | resolved | All active boundary references name the tracked [`packages/factory/scripts/usage-capture`](../../../packages/factory/scripts/usage-capture) source.                                          |
| PROP-02 | resolved | Completion criterion 12 names the exact pytest command from [`docs/testing.yaml`](../../testing.yaml) and the [`dependency-check`](../../../packages/factory/scripts/dependency-check) gate. |
| PROP-03 | resolved | First-release scope now requires the canonical architecture model, its derived explanations, and the context map to register the local Usage Analysis bounded context.                       |
| PROP-04 | resolved | Design fixes the contract format as JSON Schema Draft 2020-12 plus a YAML ownership and compatibility manifest, checked by a dedicated local contract gate.                                  |
| PROP-05 | resolved | The decomposition estimate now gives ranges for review hours, normalized edit volume, and total feature-addition consumption at low confidence.                                              |
| PROP-06 | resolved | Motivation records the stale PostgreSQL description; scope and completion criterion 13 require its replacement in [`CONTEXT-MAP.md`](../../arc42/CONTEXT-MAP.md) and the architecture model. |

## Review — 2026-09-11 (repeat pass)

Reviewer: proposal-review-agent
Reviewed commit: 2320570f62d28c8b1f8e20f3517d6047bcf27f5d
Note: proposal has uncommitted working-tree changes; review is against working-tree content.
Disposition: findings

### Prior findings

| ID      | Severity | Check | Prior status | Current status | Verification                                                                                              |
| ------- | -------- | ----- | ------------ | -------------- | --------------------------------------------------------------------------------------------------------- |
| PROP-01 | major    | 05    | resolved     | confirmed      | All boundary paths use tracked `packages/factory/scripts/` prefix. Seven boundary paths verified at HEAD. |
| PROP-02 | minor    | 01    | resolved     | confirmed      | CC-12 names `uv run pytest --tb=short --quiet` and `dependency-check`.                                    |
| PROP-03 | minor    | 02    | resolved     | confirmed      | Scope includes architecture.dsl, arc42 explanations, and CONTEXT-MAP.md updates.                          |
| PROP-04 | minor    | 06    | resolved     | confirmed      | Design fixes JSON Schema Draft 2020-12 plus YAML manifest.                                                |
| PROP-05 | minor    | 08    | resolved     | confirmed      | Estimate gives ranges (25k-55k tokens, 450k-990k consumption, 18x multiplier) at low confidence.          |
| PROP-06 | minor    | 04    | resolved     | confirmed      | Motivation notes stale PostgreSQL description; CC-13 requires replacement.                                |

### New findings

| ID      | Severity | Check | Status | Finding                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                   |
| ------- | -------- | ----- | ------ | ----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| PROP-07 | major    | 02    | open   | **CLI-vs-component semantic overload in init-factory.** The proposal introduces `--add usage`, `--remove usage`, `--update usage`, and `--with-usage` to init-factory, but the current init-factory argparse constrains `--add` and `--remove` to `choices=KNOWN_CLIS` (claude, copilot, pi, codex) and has no `--update` subcommand at all (update is a separate `update-factory` script). "usage" is not a CLI — it is a fundamentally different kind of installable entity (a module copied from `packages/usage/` to `.agent-factory/usage-analysis/`) with different installation mechanics than CLI wiring (no dot-dirs, no symlinks, no guardrails, no capture hooks). The scope claims these operations are "consistent with the existing CLI add/remove pattern" without noting the semantic shift from a CLI namespace to a mixed CLI-and-component namespace. A planning agent implementing this would discover the argparse constraint and need to redesign the init-factory interface — undescribed design work. The proposal must either (a) describe how init-factory's argument model changes to accept components alongside CLIs, or (b) route component operations through a different mechanism. Additionally, the relationship between `init-factory --update usage` and the existing `update-factory` script is undefined: the Design section says `update-factory` detects version drift (line 428), but the actual update command is `init-factory --update usage` — the division of responsibility is not stated. |
| PROP-08 | minor    | 02    | open   | **Distribution gate omits `--with-usage` path.** The quality gate's required proof for the distribution lifecycle tests mentions `--add usage`, `--update usage`, and `--remove usage` but does not mention the init-time `--with-usage` path. Completion criterion 14 and the scope section both include `--with-usage` as an installation path. The gate should cover all installation paths that the completion criteria assert.                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                       |
| PROP-09 | minor    | 05    | open   | **Boundary reference without corresponding scope item.** `docs/spec/supplementary_specs/interface-contracts.md` is listed as a boundary and contains the init-factory interface contract (currently showing only `init-factory [--source DIR] [--target DIR]`). The proposal adds new operations to init-factory (`--with-usage`, `--add usage`, `--update usage`, `--remove usage`) but neither the scope nor any completion criterion requires updating the interface contracts document. Either add an interface-contracts update to scope, or remove the document from the boundary list if no update is intended.                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                    |

### Eight-check summary

| Check                               | Result | Notes                                                                                                      |
| ----------------------------------- | ------ | ---------------------------------------------------------------------------------------------------------- |
| 01 Completion criteria testable     | pass   | All 17 criteria specify observable outcomes.                                                               |
| 02 Scope boundary sharp             | fail   | PROP-07: CLI-vs-component semantic overload unacknowledged. PROP-08: gate coverage gap for `--with-usage`. |
| 03 Design decomposable              | pass   | Design sections are concrete enough for INVEST stories.                                                    |
| 04 Impact classification consistent | pass   | scope, architecture_change, and external_contract_change match the design.                                 |
| 05 Boundary references exist        | fail   | PROP-09: interface-contracts.md listed as boundary but no scope/CC covers updating it. All paths resolve.  |
| 06 Open questions genuine           | pass   | None remaining; DuckDB UI decision documented.                                                             |
| 07 Motivation justifies timing      | pass   | Clear distinction from backlog; stale architecture is a forcing function.                                  |
| 08 Estimate plausible               | pass   | 25k-55k tokens and 18x multiplier within range for feature-addition at low confidence.                     |

### Summary

All six prior findings (PROP-01 through PROP-06) remain correctly resolved. The new distribution and lifecycle design section is internally consistent across design, scope, gates, and completion criteria with two exceptions. One major finding blocks: the proposal extends init-factory's `--add` and `--remove` to accept a component name ("usage") without acknowledging that the current interface only accepts CLI names, that `--update` does not exist, and that the relationship between `init-factory --update usage` and the existing `update-factory` script is undefined (PROP-07). Two minor findings address a gate-to-criteria coverage gap for the `--with-usage` installation path (PROP-08) and a boundary reference to interface-contracts.md with no corresponding scope item (PROP-09). PROP-07 must be resolved before this reaches a planning agent; it requires describing how init-factory's argument model accommodates components, or routing component operations through a separate mechanism.

## Review — 2026-09-11 (second repeat pass)

Reviewer: proposal-review-agent
Reviewed commit: 2320570f62d28c8b1f8e20f3517d6047bcf27f5d
Note: proposal has uncommitted working-tree changes; review is against working-tree content.
Disposition: clean

### Prior findings

| ID      | Severity | Check | Prior status | Current status | Verification                                                                                                                                                                                                                                                                   |
| ------- | -------- | ----- | ------------ | -------------- | ------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------ |
| PROP-01 | major    | 05    | confirmed    | confirmed      | All boundary paths use tracked `packages/factory/scripts/` prefix. Seven paths verified at HEAD.                                                                                                                                                                               |
| PROP-02 | minor    | 01    | confirmed    | confirmed      | CC-12 names `uv run pytest --tb=short --quiet` and `dependency-check`.                                                                                                                                                                                                         |
| PROP-03 | minor    | 02    | confirmed    | confirmed      | Scope includes architecture.dsl, arc42 explanations, and CONTEXT-MAP.md updates.                                                                                                                                                                                               |
| PROP-04 | minor    | 06    | confirmed    | confirmed      | Design fixes JSON Schema Draft 2020-12 plus YAML manifest.                                                                                                                                                                                                                     |
| PROP-05 | minor    | 08    | confirmed    | confirmed      | Estimate gives ranges (25k-55k tokens, 450k-990k consumption, 18x multiplier) at low confidence.                                                                                                                                                                               |
| PROP-06 | minor    | 04    | confirmed    | confirmed      | Motivation notes stale PostgreSQL description; CC-13 requires replacement.                                                                                                                                                                                                     |
| PROP-07 | major    | 02    | open         | resolved       | Design section describes argparse union model (CLI + component), component definition (no dot-dir, symlinks, guardrails, or hooks), `init-factory --update` vs `update-factory` division, and `installed_components` manifest key. Scope, gates, and CCs 14-18 are consistent. |
| PROP-08 | minor    | 02    | open         | resolved       | Distribution gate row now names `--with-usage` alongside `--add usage`, `--update usage`, and `--remove usage`.                                                                                                                                                                |
| PROP-09 | minor    | 05    | open         | resolved       | Scope includes interface-contracts.md update; CC-18 specifies the four component operations and the update-factory boundary.                                                                                                                                                   |

### Eight-check summary

| Check                               | Result | Notes                                                                                                                                                                           |
| ----------------------------------- | ------ | ------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| 01 Completion criteria testable     | pass   | All 18 criteria specify observable outcomes with named commands, paths, and conditions.                                                                                         |
| 02 Scope boundary sharp             | pass   | CLI-vs-component distinction defined; all four distribution operations in scope, gates, and CCs.                                                                                |
| 03 Design decomposable              | pass   | Distribution subsection, query model, accounting registry, contract format, and gate ownership are concrete enough for INVEST stories.                                          |
| 04 Impact classification consistent | pass   | `scope: cross_project`, `architecture_change: true`, `external_contract_change: true` match design (new subproject, architecture model updates, init-factory interface change). |
| 05 Boundary references exist        | pass   | All seven boundary paths resolve at HEAD. Interface-contracts.md has corresponding scope item and CC-18.                                                                        |
| 06 Open questions genuine           | pass   | None remaining; all prior open questions resolved as decisions.                                                                                                                 |
| 07 Motivation justifies timing      | pass   | Stale PostgreSQL architecture documentation is an active forcing function; query convenience is secondary.                                                                      |
| 08 Estimate plausible               | pass   | 25k-55k normalized tokens with 18x multiplier (450k-990k consumption) at low confidence. Range accommodates the added distribution lifecycle complexity.                        |

### Summary

All nine prior findings (PROP-01 through PROP-09) are resolved and confirmed. No new inconsistencies were introduced by the fixes. The proposal is ready to plan from: its scope is partitioned cleanly, its design is decomposable into stories without re-derivation, its gates cover every declared contract, and its completion criteria are independently verifiable.

## Review — 2026-09-11 (third repeat pass)

Reviewer: proposal-review-agent
Reviewed commit: 2320570f62d28c8b1f8e20f3517d6047bcf27f5d
Note: proposal has uncommitted working-tree changes; review is against working-tree content.
Disposition: findings

### Prior findings

| ID      | Severity | Check | Prior status | Current status | Verification                                                                                                                                                                                       |
| ------- | -------- | ----- | ------------ | -------------- | -------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| PROP-01 | major    | 05    | confirmed    | confirmed      | All seven boundary paths resolve at the reviewed commit; the capture boundary remains the tracked `packages/factory/scripts/usage-capture` source.                                                 |
| PROP-02 | minor    | 01    | confirmed    | confirmed      | Completion criterion 12 still names the exact pytest command from [`docs/testing.yaml`](../../testing.yaml) and the [`dependency-check`](../../../packages/factory/scripts/dependency-check) gate. |
| PROP-03 | minor    | 02    | confirmed    | confirmed      | First-release scope still includes [`architecture.dsl`](../../arc42/architecture.dsl), its derived explanations, and [`CONTEXT-MAP.md`](../../arc42/CONTEXT-MAP.md).                               |
| PROP-04 | minor    | 06    | confirmed    | confirmed      | The proposal still selects JSON Schema Draft 2020-12 plus a YAML ownership and compatibility manifest.                                                                                             |
| PROP-05 | minor    | 08    | confirmed    | confirmed      | The estimate remains 25,000–55,000 normalized tokens and 450,000–990,000 consumed tokens at 18×, with low confidence.                                                                              |
| PROP-06 | minor    | 04    | confirmed    | confirmed      | Motivation identifies the stale PostgreSQL design and completion criterion 13 requires its replacement in the architecture artifacts.                                                              |
| PROP-07 | major    | 02    | resolved     | confirmed      | The distribution design still defines the CLI/component union, `installed_components`, and the responsibility split between `init-factory --update usage` and `update-factory`.                    |
| PROP-08 | minor    | 02    | resolved     | confirmed      | The distribution lifecycle gate still covers `--with-usage`, `--add usage`, `--update usage`, and `--remove usage`.                                                                                |
| PROP-09 | minor    | 05    | resolved     | confirmed      | [`interface-contracts.md`](../../spec/supplementary_specs/interface-contracts.md) remains in scope and completion criterion 18 defines its required update.                                        |

### New findings

| ID      | Severity | Check | Status | Finding                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                          |
| ------- | -------- | ----- | ------ | ------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------ |
| PROP-10 | major    | 03    | open   | **The query command and its runtime are not decision-complete.** The proposal shows `usage query <published-view> --format parquet --output <path>`, but does not define how an installed module exposes `usage`, how a caller selects or overrides the JSONL input set, the default input location, or how the isolated locked DuckDB dependency becomes executable. Copying `packages/usage/` into `.agent-factory/usage-analysis/` does not by itself create a command or an offline-capable runtime. Planning would have to design a public interface and deployment mechanism that completion criteria 01, 07–10, and 14 assume. Specify the installed invocation, input-selection contract, dependency provisioning, and offline boundary. |
| PROP-11 | major    | 03    | open   | **The `capture_health` view has no defined data source for preflight failures.** The data flow says preflight rejects an invalid selected set before DuckDB accounting runs, while `capture_health` promises failure counts grouped by failure code and source file. No persisted diagnostic store or in-memory relation feeding those failures into the published view is defined, and persistence is otherwise explicitly excluded. Planning cannot implement the stated view contract without choosing a new data flow. Define whether diagnostics are registered as a query-scoped DuckDB relation, exposed outside the published views, or removed from `capture_health`.                                                                   |
| PROP-12 | major    | 03    | open   | **The published contract has conflicting ownership and paths.** The Boundary section says `packages/usage/` owns the record contract it accepts, then says the manifest names Factory as owner. It names repository paths `contracts/usage-record/contract.yaml` and `contracts/usage-record/v1.schema.json`, while the installed layout contains `usage-analysis/contract/` and the gate is named `usage/scripts/usage-contract-check`. These differences determine the authoritative source, installed copy, dependency direction, and gate location for an external contract. Choose one Factory-owned canonical source path and specify its projection into the consumer and installed layout.                                               |
| PROP-13 | minor    | 02    | open   | **The declared `remove-factory` boundary has no release contract.** [`packages/factory/scripts/remove-factory`](../../../packages/factory/scripts/remove-factory) is listed in `impact.boundaries`, but Design, Scope, gates, and completion criteria only define component removal through `init-factory --remove usage`. The current full remover deletes `.agent-factory/`, including usage data. State whether full Factory removal changes in this release and what it must do with `usage-analysis/`, `installed_components`, and `.agent-factory/usage/`; otherwise remove this boundary from the impact list.                                                                                                                            |
| PROP-14 | minor    | 02    | open   | **Required dataframe support is ambiguous.** Design says the Python entry point “may return” DuckDB relations, Polars DataFrames, Pandas DataFrames, or Arrow tables; Scope and completion criterion 08 require supported conversions without naming them. The choices have different dependency and test implications, so an arbitrary conversion story cannot be classified in or out. Name the required release-1 conversions and defer the rest.                                                                                                                                                                                                                                                                                             |

### Eight-check summary

| Check                               | Result | Notes                                                                                                                                                                                  |
| ----------------------------------- | ------ | -------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| 01 Completion criteria testable     | pass   | The 18 criteria describe observable outcomes, although PROP-10 through PROP-12 leave design work behind several of them.                                                               |
| 02 Scope boundary sharp             | fail   | PROP-13 leaves the full-removal boundary undecided; PROP-14 does not partition dataframe conversions into required and deferred support.                                               |
| 03 Design decomposable              | fail   | PROP-10 leaves the installed command and runtime undefined; PROP-11 leaves the health-view data flow undefined; PROP-12 leaves contract ownership and artifact placement inconsistent. |
| 04 Impact classification consistent | pass   | `cross_project`, `architecture_change: true`, and `external_contract_change: true` match the described subproject, architecture, and CLI contract changes.                             |
| 05 Boundary references exist        | pass   | All seven declared paths resolve at commit `2320570f62d28c8b1f8e20f3517d6047bcf27f5d`.                                                                                                 |
| 06 Open questions genuine           | pass   | The stated DuckDB UI decision is settled; the unresolved design defects are filed above rather than treated as optional questions.                                                     |
| 07 Motivation justifies timing      | pass   | Existing JSONL evidence is difficult to interpret correctly, and the accepted PostgreSQL design has left the architecture baseline stale.                                              |
| 08 Estimate plausible               | pass   | The low-confidence 25,000–55,000 edit-token range and 18× feature-addition multiplier are plausible for the declared scope.                                                            |

### Summary

All nine prior findings remain resolved. Three major findings block planning: the installed query/runtime contract is incomplete, the `capture_health` view cannot obtain the failures it promises under the stated data flow, and the published record contract has conflicting ownership and paths. Two minor findings require a decision about the full `remove-factory` boundary and an explicit release-1 dataframe support set. Address the five open findings and re-open the proposal for another repeat review.

## Review — 2026-09-11 (fourth repeat pass)

Reviewer: proposal-review-agent
Reviewed commit: 2320570f62d28c8b1f8e20f3517d6047bcf27f5d
Note: proposal has uncommitted working-tree changes; review is against working-tree content.
Disposition: clean

### Prior findings

| ID      | Severity | Check | Prior status | Current status | Verification                                                                                                                                                                                                                                                                                                                                                                                |
| ------- | -------- | ----- | ------------ | -------------- | ------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| PROP-01 | major    | 05    | confirmed    | confirmed      | All seven existing boundary paths still resolve at HEAD. The capture boundary remains `packages/factory/scripts/usage-capture`.                                                                                                                                                                                                                                                             |
| PROP-02 | minor    | 01    | confirmed    | confirmed      | CC-12 names the exact pytest command and dependency-check gate.                                                                                                                                                                                                                                                                                                                             |
| PROP-03 | minor    | 02    | confirmed    | confirmed      | Scope includes architecture.dsl, arc42 explanations, and CONTEXT-MAP.md updates.                                                                                                                                                                                                                                                                                                            |
| PROP-04 | minor    | 06    | confirmed    | confirmed      | Design fixes JSON Schema Draft 2020-12 plus YAML manifest.                                                                                                                                                                                                                                                                                                                                  |
| PROP-05 | minor    | 08    | confirmed    | confirmed      | Estimate gives ranges (25k-55k tokens, 450k-990k consumption, 18x multiplier) at low confidence.                                                                                                                                                                                                                                                                                            |
| PROP-06 | minor    | 04    | confirmed    | confirmed      | Motivation identifies stale PostgreSQL description; CC-13 requires replacement.                                                                                                                                                                                                                                                                                                             |
| PROP-07 | major    | 02    | confirmed    | confirmed      | Distribution design defines CLI/component union, `installed_components`, and responsibility split between `init-factory --update usage` and `update-factory`.                                                                                                                                                                                                                               |
| PROP-08 | minor    | 02    | confirmed    | confirmed      | Distribution lifecycle gate covers `--with-usage`, `--add usage`, `--update usage`, `--remove usage`, and `remove-factory`.                                                                                                                                                                                                                                                                 |
| PROP-09 | minor    | 05    | confirmed    | confirmed      | Interface-contracts.md remains in scope; CC-18 defines the required update.                                                                                                                                                                                                                                                                                                                 |
| PROP-10 | major    | 03    | open         | resolved       | New "Installed runtime and invocation" subsection (lines 499-535) defines `uv run --project .agent-factory/usage-analysis usage-query`, default input `.agent-factory/usage/`, `--usage-dir` override, and offline operation. CC-20 matches. Invocation model is consistent with installed layout's `query.py` and bundled `pyproject.toml`.                                                |
| PROP-11 | major    | 03    | open         | resolved       | Data flow step 3 registers preflight failures as a query-scoped DuckDB relation feeding `capture_health`. Failure behavior section describes the split: accounting views require zero failures; `capture_health` is always available. Query model table description explicitly references the failure relation.                                                                             |
| PROP-12 | major    | 03    | open         | resolved       | Factory is explicitly the owner with canonical source at `packages/factory/contracts/usage-record/`. Installed copy at `.agent-factory/usage-analysis/contract/` described as a distribution artifact. Gate references `packages/usage/scripts/usage-contract-check`. All four mention sites (boundary list, contract ownership paragraph, quality gates, installed layout) are consistent. |
| PROP-13 | minor    | 02    | open         | resolved       | "Full Factory removal" subsection describes `remove-factory`'s component-aware behavior. CC-19 covers it. Distribution lifecycle gate includes `remove-factory`.                                                                                                                                                                                                                            |
| PROP-14 | minor    | 02    | open         | resolved       | Required conversions are DuckDB relations and PyArrow tables. Polars and Pandas explicitly deferred. CC-08, scope "In" list, and deferred scope are all consistent.                                                                                                                                                                                                                         |
| PROP-15 | minor    | 05    | open         | resolved       | Boundary entry now carries `# new: created by this feature` annotation, distinguishing it from existing inspectable paths. The seven existing boundary paths continue to resolve at HEAD.                                                                                                                                                                                                   |
| PROP-16 | minor    | 03    | open         | resolved       | Parquet export code block now uses `usage-query` (hyphenated), matching the installed entry point defined in the runtime subsection.                                                                                                                                                                                                                                                        |

### Eight-check summary

| Check                               | Result | Notes                                                                                                                                                                                                |
| ----------------------------------- | ------ | ---------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| 01 Completion criteria testable     | pass   | All 20 criteria specify observable outcomes with named commands, paths, and conditions. CC-19 and CC-20 are well-formed additions.                                                                   |
| 02 Scope boundary sharp             | pass   | CLI-vs-component distinction is defined; all distribution operations, `remove-factory`, and dataframe conversions are partitioned in/out.                                                            |
| 03 Design decomposable              | pass   | PROP-10, PROP-11, PROP-12, and PROP-16 are resolved; the installed runtime, health-view data flow, contract placement, and Parquet invocation syntax are now defined and consistent.                 |
| 04 Impact classification consistent | pass   | `cross_project`, `architecture_change: true`, `external_contract_change: true` match the design.                                                                                                     |
| 05 Boundary references exist        | pass   | Seven existing paths resolve at HEAD. The eighth (`packages/factory/contracts/usage-record/`) is annotated as a new artifact created by this feature, distinguishing it from inspectable boundaries. |
| 06 Open questions genuine           | pass   | None remaining.                                                                                                                                                                                      |
| 07 Motivation justifies timing      | pass   | Stale PostgreSQL architecture and inconvenient raw JSONL are forcing functions.                                                                                                                      |
| 08 Estimate plausible               | pass   | 25k-55k normalized tokens, 18x multiplier, low confidence — plausible for the expanded scope including CC-19 and CC-20.                                                                              |

### Summary

All sixteen findings (PROP-01 through PROP-16) are resolved and confirmed. The five targeted findings from the third repeat pass are addressed: the installed runtime subsection defines the invocation model, dependency provisioning, input selection, and offline boundary (PROP-10); the data flow registers preflight failures as a query-scoped DuckDB relation with a clear accounting/health split (PROP-11); contract ownership and paths are internally consistent across all mention sites (PROP-12); `remove-factory`'s component behavior is documented with a matching completion criterion and gate (PROP-13); and dataframe conversions are explicitly partitioned between release-1 and deferred (PROP-14). Two minor findings introduced during this pass (PROP-15, PROP-16) were resolved in the working tree before this section was appended. The proposal is ready to plan from: all eight checks pass, its scope is partitioned cleanly, its design is decomposable into stories without re-derivation, its gates cover every declared contract, and its 20 completion criteria are independently verifiable.
