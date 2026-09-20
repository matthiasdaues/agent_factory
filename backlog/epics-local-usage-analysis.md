---
scope: global
---

# EPICs — Local Usage Processing and Analysis

Proposal trace: usage-processing-and-storage (proposal removed)
Specification trace: [local-usage-processing-and-analysis.feature](../docs/spec/local-usage-processing-and-analysis.feature)
Architecture trace: [ADR-0015](../docs/adr/0015-query-authoritative-jsonl-with-ephemeral-duckdb-views.md), §5.7 Usage Analysis Runtime
QA strategy trace: [local-usage-processing-and-analysis-qa-strategy.md](../docs/spec/local-usage-processing-and-analysis-qa-strategy.md)

Dependency order: 1 → 2 → 3 → {4, 6} and 1 → 5. EPICs 2 and 5 are parallelizable after EPIC 1. EPICs 4 and 6 are parallelizable after EPIC 3.

## EPIC 1: Validate usage records against the published Factory contract

### Why this EPIC exists

No analytical query can produce trustworthy results from unvalidated input. Usage Analysis consumes Factory's raw JSONL spool, but neither the record format nor the expected field invariants are machine-checkable today — no schema file, no contract specification, and no standalone validation gate exist. This EPIC establishes the versioned record contract Factory owns and the deterministic gate that validates any JSONL record against it, creating the foundation every downstream EPIC depends on.

### Actor Goals

- Factory producer publishes a versioned record contract (`contract.yaml` and `v1.schema.json`) declaring Factory as owner with a compatibility policy
- Factory producer validates field names, types, nullability, identifiers, timestamps, non-negative counters, nested transcript reference shape, and the `normalized_total = normalized_input + normalized_output` cross-field invariant
- Quality maintainer establishes the deterministic-linter layer binding in `docs/testing.yaml` and assigns one owner per observable contract backlog-wide

### Demo

1. Inspect `packages/factory/contracts/usage-record/contract.yaml` and verify Factory is declared as the contract owner with a compatibility policy.
2. Inspect `packages/factory/contracts/usage-record/v1.schema.json` and verify it declares a JSON Schema Draft 2020-12 record contract.
3. Run `packages/usage/scripts/usage-contract-check fixtures/valid/` on a directory of synthetic valid JSONL records. The gate exits zero.
4. Run `packages/usage/scripts/usage-contract-check fixtures/invalid/` on a directory containing records with wrong types, missing fields, negative counters, and a `normalized_total` that does not equal `normalized_input + normalized_output`. The gate exits non-zero and reports field-level diagnostics with stable failure codes.
5. Run `packages/usage/scripts/usage-contract-check fixtures/unknown-cli/` on a record naming a CLI outside `claude-code`, `pi`, `codex`, `copilot`. The gate exits non-zero and names the unsupported CLI.
6. Inspect `docs/testing.yaml` and verify the deterministic-linter layer binding exists.

### Scope

**In:**

- Usage-record contract definition — `packages/factory/contracts/usage-record/contract.yaml` (owner declaration, compatibility policy) and `v1.schema.json` (JSON Schema Draft 2020-12 record schema covering field names, types, nullability, identifiers, timestamps, non-negative counters, nested transcript reference shape, and the `normalized_total = normalized_input + normalized_output` invariant)
- `usage-contract-check` standalone linter gate — `packages/usage/scripts/usage-contract-check` validates a JSONL file or directory against the installed contract copy, reports field-level diagnostics with stable failure codes, and checks the closed CLI set (`claude-code`, `pi`, `codex`, `copilot`)
- Accounting registry key declaration — the closed set of four supported CLI values, defined as a data structure in `packages/usage/` and consumed by the contract check gate
- `packages/usage/` subproject scaffolding — `pyproject.toml`, directory structure, and installed contract copy as infrastructure for the contract check gate
- Deterministic-linter layer binding — add the `deterministic_linter` layer to `docs/testing.yaml` with the usage subproject's gate commands
- Synthetic JSONL fixtures — valid, invalid, and boundary-case fixtures for the contract check gate, each naming one equivalence class

**Out:**

- Conservation rules mapping CLIs to accounting behavior (EPIC 3)
- Operational Preflight ancestry validation (EPIC 2)
- `usage-query` CLI entry point (EPIC 2)
- Published DuckDB views (EPICs 2–3)

### Dependencies

None. This is the foundational EPIC.

### Boundaries

- Storage: `packages/factory/contracts/usage-record/` (contract artifacts)
- Script: `packages/usage/scripts/usage-contract-check` (deterministic linter gate)
- Package: `packages/usage/` (subproject scaffold)
- Config: `docs/testing.yaml` (layer binding)

### Domain Rules

- Factory owns the record contract. Usage Analysis reads only the installed contract copy.
- The schema declares JSON Schema Draft 2020-12.
- `normalized_total` equals `normalized_input` plus `normalized_output` for every valid record.
- The supported CLI set is exactly `claude-code`, `pi`, `codex`, `copilot` — a closed enumeration, not extensible without a contract version bump.
- Each fixture is synthetic and contains no copied transcript or prompt content.

### Size

2 stories.

### Building-Block Inventory

| Story   | Capability                                                                                              | Tier     | Size | Basis                                                                                                                                                                                                               |
| ------- | ------------------------------------------------------------------------------------------------------- | -------- | ---- | ------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| ST-0240 | Create the usage-record contract and scaffold `packages/usage/` with deterministic-linter layer binding | standard | M    | JSON Schema authoring with nested transcript reference shape, cross-field invariant declaration, contract YAML, pyproject.toml scaffold, and testing.yaml layer binding — moderate domain complexity, low ambiguity |
| ST-0241 | Implement `usage-contract-check` gate with schema, cross-field, and CLI set validation                  | standard | M    | Python validation script reading JSON Schema, checking JSONL against it, verifying cross-field invariants and closed CLI set, plus synthetic fixture suite — moderate complexity, well-specified inputs and outputs |

### Testability Assessment

All actor goals produce observable, assertable outcomes. The contract schema is machine-verifiable against fixture JSONL. The `usage-contract-check` gate returns exit codes and field-level diagnostics that tests assert on directly. The deterministic-linter layer binding is a YAML entry verified by reading the file. Instrumentation boundaries: `packages/factory/contracts/usage-record/` (file existence and content), `packages/usage/scripts/usage-contract-check` (exit code and stderr diagnostics), `docs/testing.yaml` (YAML key presence). No testability red flags.

### Ownership Resolution

| Contract                                                             | .feature Rule                                                                                                                     | Owner   | Rationale                                                            |
| -------------------------------------------------------------------- | --------------------------------------------------------------------------------------------------------------------------------- | ------- | -------------------------------------------------------------------- |
| Record schema, cross-field invariants, and version agreement (LU-01) | local-usage-processing-and-analysis.feature#Factory producer publishes a compatible record contract without depending on analysis | ST-0240 | introduces the contract schema and cross-field invariant declaration |
| Supported CLI set and registry keys (LU-02)                          | local-usage-processing-and-analysis.feature#Local operator obtains conservative canonical usage without duplication               | ST-0241 | introduces the contract check gate that validates the closed CLI set |

## EPIC 2: Diagnose all selected evidence and report capture health before accounting runs

### Why this EPIC exists

Accounting on partially valid or ancestry-broken evidence produces silent double-counts or missing sessions. Before any stable analytical view can run, the system must snapshot a deterministic input set, classify every selected line, and reject evidence with malformed run hierarchies. Without this foundation, downstream EPICs cannot trust their input. This EPIC also delivers the `usage-query` CLI entry point that all subsequent EPICs extend.

### Actor Goals

- Local operator queries only published views over a fixed local input set — Input Snapshot (sorted list of top-level JSONL paths frozen at query start) selects and normalizes files, `--usage-dir` overrides the default directory, subdirectories are excluded
- Local operator diagnoses all invalid evidence before accounting — Operational Preflight (strict all-line classification and ancestry validation) classifies every selected line and blocks stable views when any failure exists

### Demo

1. Create a directory with three top-level JSONL files and one subdirectory containing additional files.
2. Run `usage-query capture_health --usage-dir that-directory/`.
3. Verify the query snapshots only the three top-level files and excludes the subdirectory.
4. Add a malformed line (truncated JSON) and a record with a self-referencing parent run ID to one file.
5. Run `usage-query capture_health --usage-dir that-directory/` again.
6. Verify the health view reports valid counts and failures grouped by stable failure code (`USAGE_ANCESTRY_SELF_PARENT`) and source file.
7. Run `usage-query canonical_session_usage --usage-dir that-directory/`.
8. Verify the command exits non-zero before accounting runs and emits no partial stable result.

### Scope

**In:**

- Input Snapshot component — `packages/usage/` module that selects and sorts top-level JSONL files, normalizes paths, supports `--usage-dir` override, and excludes subdirectories
- Contract Check integration — validates each selected line against the installed contract copy (from EPIC 1)
- Operational Preflight component — classifies every selected line into exactly one valid or failure relation, validates rooted run ancestry per CLI-session partition (six stable failure codes: `USAGE_ANCESTRY_PARENT_CONFLICT`, `ROOT_COUNT`, `PARENT_MISSING`, `PARENT_BOUNDARY`, `SELF_PARENT`, `CYCLE`), and blocks stable views when any failure exists
- `usage-query` CLI entry point — argument parsing, view routing, format selection, `--usage-dir` override, exit code contract
- `capture_health` published view — DuckDB view reporting valid counts and failures by code and source file, available even when preflight finds failures
- Diagnostic mode — labels valid and invalid lines as incomplete, cannot emit stable export
- Reproducibility gate infrastructure — deterministic file-order check (LU-04)

**Out:**

- Conservation rules and accounting views (EPIC 3)
- Result format adapters beyond default table output (EPIC 4)
- Parquet export (EPIC 4)
- Component installation (EPIC 5)

### Dependencies

EPIC 1 (the contract check reads the installed contract copy and validates CLI values; the deterministic-linter layer binding must exist).

### Boundaries

- Storage: Raw Usage Spool (append-only JSONL files under `.agent-factory/usage/`)
- Package: Usage Analysis Runtime (`packages/usage/` — Input Snapshot, Contract Check, Operational Preflight components)
- CLI: `usage-query` entry point (installed at `.agent-factory/usage-analysis/`)
- Engine: DuckDB (ephemeral SQL views)

### Domain Rules

- Query input is the sorted set of top-level JSONL files in the selected directory. Subdirectories are excluded.
- The input set is snapshotted once at query start. No mid-query changes affect results.
- Every selected line appears in exactly one query-scoped valid or failure relation (exhaustive classification).
- Each CLI-session partition must have exactly one root (a run with no parent run ID), an acyclic parent graph, and every run reachable from the root.
- Six stable failure codes: `USAGE_ANCESTRY_PARENT_CONFLICT` (snapshots of one logical run disagree on parent ID), `USAGE_ANCESTRY_ROOT_COUNT` (no root or more than one), `USAGE_ANCESTRY_PARENT_MISSING` (parent absent from selected runs), `USAGE_ANCESTRY_PARENT_BOUNDARY` (parent found only under another CLI or session), `USAGE_ANCESTRY_SELF_PARENT` (run is its own parent), `USAGE_ANCESTRY_CYCLE` (directed cycle in parent chain).
- When preflight finds any failure, `capture_health` remains available. All other stable views refuse partial results and exit non-zero before accounting.
- File enumeration order does not affect sorted rows or content digest.

### Size

3 stories.

### Building-Block Inventory

| Story   | Capability                                                                                                         | Tier     | Size | Basis                                                                                                                                                                                                  |
| ------- | ------------------------------------------------------------------------------------------------------------------ | -------- | ---- | ------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------ |
| ST-0242 | Implement Input Snapshot and `usage-query` CLI entry point with sorted file selection and `--usage-dir` override   | standard | M    | File enumeration, path normalization, argument parsing, entry point scaffold, and integration with Contract Check — moderate complexity, clear contracts                                               |
| ST-0243 | Implement Operational Preflight with all-line classification, six ancestry failure codes, and reproducibility gate | standard | L    | Graph algorithm for rooted-tree ancestry validation (cycle detection, boundary checking, multi-root detection), exhaustive line classification, six stable failure codes — high algorithmic complexity |
| ST-0244 | Implement `capture_health` view, stable-view refusal on preflight failure, and diagnostic mode                     | standard | M    | DuckDB view creation, conditional routing (health available, others blocked), diagnostic labeling — moderate complexity, depends on preflight relations                                                |

### Testability Assessment

All actor goals produce observable, assertable outcomes. Input Snapshot is testable through file enumeration assertions on sorted paths. Operational Preflight produces stable failure codes and exit codes that tests assert on directly. `capture_health` returns structured DuckDB rows. Instrumentation boundaries: `usage-query` CLI (exit code, stdout), DuckDB relations (row content and schema), filesystem (file enumeration order, path normalization), JSONL fixtures (valid, malformed, ancestry-broken). No testability red flags.

### Ownership Resolution

| Contract                                                                                     | .feature Rule                                                                                                                     | Owner   | Rationale                                                               |
| -------------------------------------------------------------------------------------------- | --------------------------------------------------------------------------------------------------------------------------------- | ------- | ----------------------------------------------------------------------- |
| Selected file order cannot alter sorted rows or digest (LU-04)                               | local-usage-processing-and-analysis.feature#Local operator queries only published views over a fixed local input set              | ST-0242 | introduces the Input Snapshot with sorted file selection                |
| Every line and run hierarchy is classified; malformed ancestry blocks stable results (LU-05) | local-usage-processing-and-analysis.feature#Local operator diagnoses all invalid evidence before accounting                       | ST-0243 | introduces the Operational Preflight component with ancestry validation |
| Analysis is local and transcript-blind (LU-06)                                               | local-usage-processing-and-analysis.feature#Factory producer publishes a compatible record contract without depending on analysis | ST-0242 | introduces the first analytical code path with boundary constraints     |

## EPIC 3: Query canonical session usage across four CLIs and by dimension

### Why this EPIC exists

Raw usage snapshots contain duplicates, nested hierarchies, and CLI-specific accounting semantics that make naive summation wrong. A Claude Code session double-counts children if added to the root. A Codex session double-counts if children are added at all. This EPIC implements the four conservation rules and the remaining five published DuckDB views, delivering the analytical core that every output format and export depends on.

### Actor Goals

- Local operator obtains conservative canonical usage without duplication — Accounting Registry (closed mapping from four CLI names to their conservation rules) applies the correct formula per CLI, and Query Model v1 (versioned set of six published DuckDB views) exposes the stable analytical surface

### Demo

1. Prepare a fixture directory with Claude Code sessions (repeated root snapshots, duplicate child evidence), Pi sessions (nested descendants), Codex sessions (inclusive root with child attribution), and Copilot sessions (inclusive root with child attribution).
2. Run `usage-query canonical_session_usage --usage-dir fixtures/multi-cli/`.
3. Verify Claude Code sessions add the latest root snapshot and each distinct child exactly once.
4. Verify Pi sessions add the root and each distinct descendant exactly once.
5. Verify Codex and Copilot sessions use the latest inclusive root snapshot only — children do not increase the total.
6. Run `usage-query usage_by_dimension --usage-dir fixtures/multi-cli/ --dimensions cli,project --granularity day`.
7. Verify each dimensional total equals the additive sum of its canonical session rows.
8. Run `usage-query cache_efficiency --usage-dir fixtures/multi-cli/`.
9. Verify null and input-only cache fields are preserved, not coerced to zero.

### Scope

**In:**

- Accounting Registry — data structure mapping `claude-code`, `pi`, `codex`, and `copilot` to their conservation rules (additive root-and-children, additive root-and-descendants, inclusive-root-only)
- Latest-snapshot selection — deterministic evidence identity using greatest capture sequence, then greatest normalized relative source path by unsigned UTF-8 byte order, then greatest one-based line number
- `canonical_session_usage` view — applies the correct conservation rule per CLI and deduplicates within each session
- `raw_usage_snapshots` view — all valid snapshots with their evidence identity
- `latest_run_snapshots` view — one canonical snapshot per logical run using deterministic evidence identity
- `usage_by_dimension` view — dimensional totals with ordered dimension list and time granularity (`none`, `hour`, `day`, `week`, `month`); rejects duplicate or unsupported dimensions and time dimension with granularity `none`
- `cache_efficiency` view — preserves null and input-only cache fields without coercing to zero
- Contract test suite for four-CLI accounting (LU-03) — pure SQL fixtures across the four-CLI matrix

**Out:**

- Output format conversion (EPIC 4)
- Parquet export (EPIC 4)
- Component installation (EPIC 5)
- DuckDB UI documentation (EPIC 6)

### Dependencies

EPIC 2 (Input Snapshot, Contract Check, and Operational Preflight produce the valid relation that accounting consumes; `capture_health` is already implemented).

### Boundaries

- Package: Usage Analysis Runtime (`packages/usage/` — Accounting Registry, Query Model v1 components)
- Engine: DuckDB (ephemeral SQL views — six published view definitions)
- CLI: `usage-query` (extended with remaining view names and dimension/granularity arguments)

### Domain Rules

- Logical-run identity is the tuple `(cli, session_id, run_id)`. Source path, line, capture sequence, and record content do not enter the key.
- Parent run ID establishes ancestry without changing identity. Every snapshot for a logical run has the same parent run ID (including null).
- Latest snapshot selection: greatest capture sequence, then greatest normalized path (unsigned UTF-8 byte order), then greatest one-based line number.
- `claude-code` conservation: latest root snapshot plus each distinct child run exactly once.
- `pi` conservation: root record plus each distinct descendant run exactly once.
- `codex` conservation: latest inclusive root snapshot only. Child attribution records do not increase the total.
- `copilot` conservation: same as `codex`.
- Unknown CLI exits non-zero and names the unsupported value.
- Dimensional totals equal the additive sum of canonical session rows. Omitted dimensions default to one all-input total. Duplicate or unsupported dimensions are rejected.
- Cache signals preserve null and input-only states. Unavailable values are never coerced to zero.

### Size

2 stories.

### Building-Block Inventory

| Story   | Capability                                                                                                  | Tier     | Size | Basis                                                                                                                                                                                          |
| ------- | ----------------------------------------------------------------------------------------------------------- | -------- | ---- | ---------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| ST-0245 | Implement four-CLI conservation rules, latest-snapshot selection, and `canonical_session_usage` view        | standard | L    | Four distinct conservation algorithms with tiebreaking snapshot selection, DuckDB SQL view creation, contract test matrix across four CLIs — high domain complexity, well-specified invariants |
| ST-0246 | Implement `raw_usage_snapshots`, `latest_run_snapshots`, `usage_by_dimension`, and `cache_efficiency` views | standard | M    | Four DuckDB views with dimensional grouping, time granularity routing, null preservation, and input validation — moderate complexity, depends on canonical session rows from ST-0245           |

### Testability Assessment

All actor goals produce observable, assertable outcomes. Conservation rules are pure SQL arithmetic testable against synthetic fixture matrices — each CLI's session total is a deterministic number given fixed input. Dimensional totals are additive sums verifiable by independent calculation. Cache null preservation is assertable at the column level. Instrumentation boundaries: DuckDB views (row content, column types, null states), `usage-query` CLI (exit code, stdout), contract test fixtures (four-CLI matrix with known expected totals). No testability red flags.

### Ownership Resolution

| Contract                                                                     | .feature Rule                                                                                                       | Owner   | Rationale                                                       |
| ---------------------------------------------------------------------------- | ------------------------------------------------------------------------------------------------------------------- | ------- | --------------------------------------------------------------- |
| Valid rooted ancestry, snapshot selection, and four-CLI conservation (LU-03) | local-usage-processing-and-analysis.feature#Local operator obtains conservative canonical usage without duplication | ST-0245 | introduces the four conservation rules and canonical accounting |

## EPIC 4: Export query results as typed table, JSON, Arrow, or verified Parquet

### Why this EPIC exists

The six published views produce DuckDB relations, but operators and analysts need results in multiple formats — terminal tables for quick inspection, JSON for scripting, PyArrow tables for programmatic analysis, and Parquet files for archival and sharing. Without verified format conversion, consumers must reimplement the SQL model. Without atomic Parquet export, an interrupted write destroys the prior valid output. This EPIC delivers the format layer and the explicit, attributable export path.

### Actor Goals

- Local analyst consumes typed table, JSON, relation, and Arrow results — Result Adapters (format converters from a DuckDB relation to table, JSON, Arrow, or PyArrow table) project one published view without reimplementing accounting
- Local operator exports attributable Parquet without damaging prior output — Parquet Exporter (atomic, attributable export writing a temporary sibling, verifying, then replacing the destination) produces an explicit derivative of one published view

### Demo

1. Run `usage-query canonical_session_usage --format table` and verify the terminal output preserves all column types and null values from the published view.
2. Run `usage-query canonical_session_usage --format json` and verify the JSON output represents the same logical rows, field types, and null states.
3. In Python, call the programmatic interface and request a DuckDB relation and a PyArrow table. Verify both preserve the published view's schema, logical rows, and null states.
4. Request a Pandas conversion. Verify the interface rejects the unsupported format without changing the SQL model.
5. Run `usage-query usage_by_dimension --format parquet -o report.parquet`.
6. Verify `report.parquet` contains the correct rows, schema, query-model version, and input-set digest as provenance metadata.
7. Run the same export command again with a corrupted intermediate. Verify the prior `report.parquet` remains unchanged.
8. Run `packages/usage/scripts/usage-dependency-check`. Verify it confirms that DuckDB and PyArrow are directly declared and locked, and the package executes from a complete offline cache.

### Scope

**In:**

- Result Adapters component — `packages/usage/` module projecting one published view as table (terminal-formatted), JSON (typed with nulls), DuckDB relation (pass-through), or PyArrow table (locked dependency); rejects Pandas and Polars without changing the SQL model
- PyArrow locked dependency — direct declaration in `pyproject.toml`, compatible version in lockfile, offline cache verification
- Parquet Exporter component — writes temporary sibling, verifies round-tripped rows and schema, records provenance (query-model version and input-set digest), atomically replaces destination
- Interrupted-export safety — failed or interrupted replacement leaves the prior destination unchanged (exit non-zero)
- No automatic Parquet materialization — export happens only on explicit operator request
- `usage-dependency-check` gate — deterministic linter verifying direct DuckDB and PyArrow declarations, lock compatibility, and network-disabled cached run (LU-13)

**Out:**

- DuckDB UI exploration path (EPIC 6)
- Component lifecycle (EPIC 5)
- Query model or accounting changes (EPICs 2–3)

### Dependencies

EPIC 3 (Result Adapters and Parquet Exporter consume published views that EPIC 3 creates; the format layer has no content to project without accounting results).

### Boundaries

- Package: Usage Analysis Runtime (`packages/usage/` — Result Adapters, Parquet Exporter components)
- Library: PyArrow (locked direct dependency for Arrow and Parquet output)
- Filesystem: atomic temporary-sibling replacement for Parquet exports
- Script: `packages/usage/scripts/usage-dependency-check` (deterministic linter gate)

### Domain Rules

- Table and JSON outputs represent the same logical rows, field types, and null states as the published view.
- Programmatic DuckDB relation and PyArrow table outputs preserve the same schema, rows, and null states.
- PyArrow is a direct locked dependency. Factory capture does not import DuckDB or PyArrow.
- Pandas and Polars conversions are rejected without changing the SQL model.
- Parquet export writes a temporary sibling, verifies rows and schema, records provenance (query-model version plus input-set digest), and atomically replaces the destination.
- Interrupted or failed export leaves the prior destination unchanged.
- No scheduled, incremental, or automatically refreshed Parquet state is created.

### Size

2 stories.

### Building-Block Inventory

| Story   | Capability                                                                                           | Tier     | Size | Basis                                                                                                                                                                                                       |
| ------- | ---------------------------------------------------------------------------------------------------- | -------- | ---- | ----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| ST-0247 | Implement Result Adapters for table, JSON, relation, and Arrow output with locked PyArrow dependency | standard | M    | Four format converters (table formatter, JSON serializer, relation pass-through, PyArrow conversion), null preservation, dependency locking in pyproject.toml — moderate complexity, clear format contracts |
| ST-0248 | Implement Parquet Exporter with atomic replacement, provenance, and `usage-dependency-check` gate    | standard | M    | Atomic write (temporary sibling plus os.rename), round-trip schema verification, provenance metadata embedding, plus dependency-check linter script — moderate complexity, well-defined I/O contract        |

### Testability Assessment

All actor goals produce observable, assertable outcomes. Result Adapters are testable by comparing output rows, types, and null states against the source DuckDB relation. Parquet export is testable by reading the written file and verifying schema, rows, and provenance metadata. Interrupted-export safety is testable by simulating failure and checking the prior file remains unchanged. Instrumentation boundaries: `usage-query` CLI (exit code, stdout, file output), Parquet files (schema, row content, metadata), PyArrow API (table schema and nulls), `usage-dependency-check` (exit code). No testability red flags.

### Ownership Resolution

| Contract                                                                                              | .feature Rule                                                                                                         | Owner   | Rationale                                                                      |
| ----------------------------------------------------------------------------------------------------- | --------------------------------------------------------------------------------------------------------------------- | ------- | ------------------------------------------------------------------------------ |
| Stable outputs preserve all six published-view schemas, rows, ordering, dimensions, and nulls (LU-07) | local-usage-processing-and-analysis.feature#Local analyst consumes typed table, JSON, relation, and Arrow results     | ST-0247 | introduces Result Adapters projecting published views to typed outputs         |
| Parquet replacement is attributable, round-trippable, and atomic (LU-08)                              | local-usage-processing-and-analysis.feature#Local operator exports attributable Parquet without damaging prior output | ST-0248 | introduces the Parquet Exporter with atomic replacement                        |
| Usage Analysis directly declares and locks compatible DuckDB and PyArrow dependencies (LU-13)         | local-usage-processing-and-analysis.feature#Local analyst consumes typed table, JSON, relation, and Arrow results     | ST-0248 | introduces the `usage-dependency-check` gate that enforces locked dependencies |

## EPIC 5: Manage the opt-in usage-analysis component without data loss

### Why this EPIC exists

Usage Analysis is an opt-in component that must be installable, updatable, and removable without damaging the raw evidence it reads or the capture pipeline that writes it. The distribution scripts (`init-factory`, `update-factory`, `remove-factory`) already exist but have no component management. Without lifecycle operations, a project maintainer cannot adopt, upgrade, or retire the analytical layer. Without a dependency boundary gate, import leaks between Factory and Usage Analysis would silently couple the two.

### Actor Goals

- Project maintainer manages the opt-in usage-analysis component without accidental data loss — Distribution scripts (init-factory, update-factory, remove-factory) gain component lifecycle operations that install, update, and remove the analytical module while preserving raw evidence and capture independence

### Demo

01. Run `init-factory --with-usage` on a target project with no usage-analysis component.
02. Verify `.agent-factory/usage-analysis/` contains the self-contained module and installed contract copy.
03. Verify `factory-install.json` (Install Manifest — JSON file tracking installed components) records `usage` under `installed_components`.
04. Verify `.agent-factory/usage/` (Raw Usage Spool) remains untouched.
05. Run `init-factory --update usage` with a compatible replacement module. Verify only the component is replaced and install metadata records the new source version.
06. Run `init-factory --update usage` with an incompatible contract version. Verify the command exits non-zero with a compatibility diagnostic and the installed component remains unchanged.
07. Run `init-factory --remove usage`. Verify the component and manifest entry are removed. Verify raw evidence remains unchanged and capture can append another record.
08. Run `update-factory`. Verify Factory core may refresh but the installed component remains unchanged.
09. Run `remove-factory`. Verify the complete `.agent-factory/` installation including raw evidence is removed.
10. Run `packages/factory/scripts/dependency-check`. Verify Factory has no import dependency on Usage Analysis and Usage Analysis consumes only the published record contract.

### Scope

**In:**

- Component lifecycle in `init-factory` — `--with-usage` (initial install), `--add usage` (post-hoc add), `--update usage` (compatible update), `--remove usage` (component removal), compatibility checking before update, idempotent no-op on repeat
- `update-factory` component awareness — refreshes Factory core without changing installed components
- `remove-factory` complete-uninstall semantics — removes `.agent-factory/` including components and raw evidence
- Install Manifest management — `factory-install.json` records and removes `usage` under `installed_components`
- Capture independence test (LU-09) — prove that Factory capture appends records when analysis is absent or corrupt
- Dependency boundary rule (LU-11) — add Usage Analysis boundary to `dependency-check` to prevent import leaks in either direction

**Out:**

- Analytical query logic (EPICs 2–3)
- Output format adapters (EPIC 4)
- DuckDB UI documentation (EPIC 6)

### Dependencies

EPIC 1 (the installed module needs a buildable `packages/usage/` package with a contract version for compatibility checking and manifest management).

### Boundaries

- Script: Distribution (`packages/factory/scripts/init-factory`, `update-factory`, `remove-factory`)
- Storage: Install Manifest (`factory-install.json`)
- Package: Usage Analysis (installed at `.agent-factory/usage-analysis/`)
- Storage: Raw Usage Spool (`.agent-factory/usage/` — must survive component operations)
- Script: `packages/factory/scripts/dependency-check` (import boundary rule)

### Domain Rules

- `--with-usage` and `--add usage` install the component at `.agent-factory/usage-analysis/` with the self-contained module and installed contract copy.
- `factory-install.json` records `usage` under `installed_components`.
- Raw evidence (`.agent-factory/usage/`) is never modified by component install, add, update, or remove. Only full Factory removal (`remove-factory`) deletes it.
- Compatible component updates replace only the module and update install metadata. Incompatible updates abort before replacement.
- Capture appends records without invoking DuckDB or analysis components.
- Component lifecycle operations are idempotent — repeating a completed operation against the resulting state succeeds as a clean no-op.
- Factory has no import dependency on Usage Analysis. Usage Analysis consumes only the published record contract.

### Size

2 stories.

### Building-Block Inventory

| Story   | Capability                                                                                            | Tier     | Size | Basis                                                                                                                                                                                                              |
| ------- | ----------------------------------------------------------------------------------------------------- | -------- | ---- | ------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------ |
| ST-0249 | Extend distribution scripts with component lifecycle, compatibility checking, and manifest management | standard | L    | Significant extension of three existing Python scripts (new CLI flags, compatibility version comparison, manifest JSON management, idempotency logic) — high effort, moderate ambiguity in compatibility semantics |
| ST-0250 | Prove capture independence and Factory/Usage Analysis dependency boundary                             | economy  | S    | Adding test case to existing Factory capture tests (LU-09) and boundary rule to existing `dependency-check` script (LU-11) — low complexity, well-defined assertions                                               |

### Testability Assessment

All actor goals produce observable, assertable outcomes. Component lifecycle operations return exit codes and produce verifiable filesystem state (installed files, manifest entries, preserved evidence). Capture independence is testable by removing the analysis component and verifying capture still appends. Dependency boundary is testable by running `dependency-check` and asserting exit zero. Instrumentation boundaries: `init-factory` / `update-factory` / `remove-factory` (exit codes, filesystem state), `factory-install.json` (JSON content), `.agent-factory/usage/` (file presence), `.agent-factory/usage-analysis/` (directory presence), `dependency-check` (exit code). No testability red flags.

### Ownership Resolution

| Contract                                                                                                         | .feature Rule                                                                                                                           | Owner   | Rationale                                                   |
| ---------------------------------------------------------------------------------------------------------------- | --------------------------------------------------------------------------------------------------------------------------------------- | ------- | ----------------------------------------------------------- |
| Capture does not depend on analysis (LU-09)                                                                      | local-usage-processing-and-analysis.feature#Factory producer publishes a compatible record contract without depending on analysis       | ST-0250 | introduces the capture-independence assertion               |
| Component install, update, remove, full remove, and idempotency preserve declared data boundaries (LU-10)        | local-usage-processing-and-analysis.feature#Project maintainer manages the opt-in usage-analysis component without accidental data loss | ST-0249 | introduces lifecycle operations in the distribution scripts |
| Factory does not depend on Usage Analysis and Usage Analysis consumes only the published record contract (LU-11) | local-usage-processing-and-analysis.feature#Factory producer publishes a compatible record contract without depending on analysis       | ST-0250 | introduces the boundary rule in `dependency-check`          |

## EPIC 6: Verify the DuckDB UI exploration path via executable documentation

### Why this EPIC exists

The specification promises a verified path for analysts to explore published views interactively using DuckDB's bundled UI. Without executable documentation, the launch command drifts from the actual query model — the bootstrap SQL could register five views instead of six, or reference a model version the code no longer ships. The smoke gate catches this drift deterministically without starting or fetching the UI, keeping optional exploration honest.

### Actor Goals

- Local analyst receives a verified DuckDB UI exploration path — Bootstrap SQL (SQL script registering all six published views when the UI launches) and `usage-ui-doc-check` (deterministic linter verifying the bootstrap resolves correctly without starting the UI)

### Demo

1. Read the usage-analysis component's documented DuckDB UI launch command.
2. Run `packages/usage/scripts/usage-ui-doc-check`.
3. Verify the smoke check parses the documented command, resolves the query-model-v1 bootstrap SQL, and confirms it registers exactly six views: `raw_usage_snapshots`, `latest_run_snapshots`, `canonical_session_usage`, `usage_by_dimension`, `cache_efficiency`, and `capture_health`.
4. Verify the smoke check completes without starting, fetching, or installing the DuckDB UI.
5. Verify the documentation supplies no repository-owned dashboard formulas or saved charts.

### Scope

**In:**

- DuckDB UI launch documentation — component-level documentation specifying the exact launch command and its relationship to the query model
- Bootstrap SQL file — SQL script that registers the six published views for UI exploration
- `usage-ui-doc-check` smoke gate — deterministic linter that parses the documented command, resolves the bootstrap SQL, verifies six-view registration, and runs without starting the UI (LU-12)
- UI-independence assertion — deterministic query and accounting gates complete without installing or starting the UI

**Out:**

- DuckDB UI implementation (external, not repository-owned)
- Dashboard formulas, saved charts, or custom UI plugins
- Analytical query or accounting changes (EPICs 2–3)

### Dependencies

EPIC 3 (the bootstrap SQL references the six published views that EPIC 3 creates; the smoke check cannot verify view registration without the query model).

### Boundaries

- Package: Usage Analysis Runtime (`packages/usage/` — bootstrap SQL and documentation)
- External: DuckDB UI (optional, not started or fetched by the gate)
- Script: `packages/usage/scripts/usage-ui-doc-check` (deterministic linter gate)

### Domain Rules

- The documented UI launch command resolves the query-model-v1 bootstrap SQL.
- The bootstrap SQL registers exactly six published views.
- DuckDB UI assets being absent or unavailable does not block deterministic analysis, query, or accounting gates.
- The repository supplies no dashboard formulas or saved charts.

### Size

1 story.

### Building-Block Inventory

| Story   | Capability                                                                                | Tier    | Size | Basis                                                                                                                                                     |
| ------- | ----------------------------------------------------------------------------------------- | ------- | ---- | --------------------------------------------------------------------------------------------------------------------------------------------------------- |
| ST-0251 | Create DuckDB UI launch documentation, bootstrap SQL, and `usage-ui-doc-check` smoke gate | economy | S    | Documentation file, SQL file referencing existing views, and a parsing script that resolves and verifies view registration — low complexity, narrow scope |

### Testability Assessment

All actor goals produce observable, assertable outcomes. The smoke gate returns an exit code and parses a concrete SQL file. Six-view registration is assertable by comparing registered view names against the published set. UI independence is testable by running the gate without UI assets present and verifying it completes. Instrumentation boundaries: `usage-ui-doc-check` (exit code, stdout), bootstrap SQL file (content), `packages/usage/` documentation (file presence). No testability red flags.

### Ownership Resolution

| Contract                                                                                                                                   | .feature Rule                                                                                            | Owner   | Rationale                                                        |
| ------------------------------------------------------------------------------------------------------------------------------------------ | -------------------------------------------------------------------------------------------------------- | ------- | ---------------------------------------------------------------- |
| DuckDB UI documentation resolves the query-model-v1 bootstrap and exactly six published views without launching or fetching the UI (LU-12) | local-usage-processing-and-analysis.feature#Local analyst receives a verified DuckDB UI exploration path | ST-0251 | introduces the bootstrap SQL and `usage-ui-doc-check` smoke gate |
