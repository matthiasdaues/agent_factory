# Usage

Local usage analysis for Agent Factory projects. Reads the JSONL evidence
that the factory's capture hooks write to `.agent-factory/usage/`, validates
every record against the usage-record contract, runs ancestry preflight,
and exposes six published views through a CLI, a Python API, and a
browser-based SQL explorer.

The package never captures data itself, never rewrites evidence, and never
requires a network connection. It is a read-only analytical consumer of the
records that [ADR-0015](../../docs/adr/0015-query-authoritative-jsonl-with-ephemeral-duckdb-views.md)
describes.

## Prerequisites

- **Python 3.10 or later.**
- **uv** (the package manager Agent Factory uses). Install it from
  [docs.astral.sh/uv](https://docs.astral.sh/uv/getting-started/installation/)
  if you do not have it yet.
- **Usage data.** The factory's capture hooks must have run at least once, so
  that `.agent-factory/usage/` contains one or more `.jsonl` files. If the
  directory is empty or missing, there is nothing to analyse.

## Installation

Agent Factory's `init-factory` script installs the usage component
automatically during project fitting. The steps below are for manual
installation or for working from the development source.

### 1. Navigate to the package directory

If you are working inside the Agent Factory repository:

```bash
cd packages/usage
```

If the usage component was installed into your project by `init-factory`:

```bash
cd .agent-factory/usage-analysis
```

### 2. Install the package and its dependencies

```bash
uv sync
```

This resolves the dependencies declared in `pyproject.toml` (including
DuckDB ≥ 1.3.0), creates a virtual environment if one does not exist, and
installs everything into it.

### 3. Verify the installation

Run a health check against your evidence spool. From the project root:

```bash
uv run --directory packages/usage usage-query capture_health --diagnostic
```

You should see a JSON object with `total_records`, `valid_count`, and
`failure_count`. If the command prints `directory not found`, confirm that
`.agent-factory/usage/` exists and contains `.jsonl` files.

## Usage

All commands below assume you are at the project root. Replace
`packages/usage` with `.agent-factory/usage-analysis` if you are using the
installed component rather than the development source.

### Query a view from the command line

```bash
uv run --directory packages/usage usage-query <view> [options]
```

The six published views are:

| View                   | What it shows                                   |
| ---------------------- | ----------------------------------------------- |
| `capture_health`       | Record counts and validation summary            |
| `raw_usage_snapshots`  | All valid records with evidence identity        |
| `latest_run_snapshots` | Latest snapshot per logical run                 |
| `session_usage`        | Per-session aggregated usage (input and output) |
| `usage_by_dimension`   | Contributing runs for flexible dimension splits |
| `cache_efficiency`     | Contributing runs for cache-hit analysis        |

Common options:

| Option           | Effect                                                  |
| ---------------- | ------------------------------------------------------- |
| `--format json`  | JSON output (default)                                   |
| `--format table` | Human-readable table                                    |
| `--diagnostic`   | Informational mode (only with `capture_health`)         |
| `--dimensions`   | Comma-separated dimension list for `usage_by_dimension` |
| `--granularity`  | Time bucket: `none`, `hour`, `day`, `week`, `month`     |
| `--persist PATH` | Materialize views into a persistent `.duckdb` file      |
| `-o PATH`        | Output file (required for `--format parquet`)           |

### Example: see total token usage per CLI tool

```bash
uv run --directory packages/usage usage-query session_usage --format table
```

### Create a persistent DuckDB file

The query pipeline runs in memory by default. To save the results for
interactive exploration:

```bash
uv run --directory packages/usage usage-query session_usage --persist usage.duckdb
```

This writes every published view as a table into `usage.duckdb`. The file
is an ordinary DuckDB database — any DuckDB client can open it.

### Explore interactively in the browser

There are two browser-based ways to explore usage data: a lightweight SQL
explorer bundled with this package, and DuckDB's full UI extension with
charting and dashboard capabilities. Both run locally and require no
network connection.

#### Path 1: Web-UI — simple SQL queries

The bundled explorer gives you a SQL editor with preset queries, a schema
sidebar, and formatted table output. It requires a persisted `.duckdb`
file.

**Step 1.** Create a persistent DuckDB file from the project root:

```bash
uv run --directory packages/usage usage-query session_usage --persist usage.duckdb
```

**Step 2.** Start the explorer:

```bash
uv run --directory packages/usage python -m usage.explorer usage.duckdb
```

A browser tab opens at `http://localhost:8642`. The sidebar lists every
table and view; click one to populate the editor. Six preset queries are
available as buttons above the results area. Press Ctrl+Enter to run a
query, Ctrl+C in the terminal to stop the server.

To use a different port:

```bash
uv run --directory packages/usage python -m usage.explorer usage.duckdb 9000
```

**Live refresh.** The explorer watches `.agent-factory/usage/` for new or
changed JSONL files. When the evidence changes, it rebuilds the DuckDB
file and refreshes the browser automatically.

#### Path 2: DuckDB UI — dashboards and charts

DuckDB's UI extension provides an interactive environment at
`localhost:4213` with a SQL editor, result-set charting (bar, line, area,
scatter, pie), column summaries, and dashboard composition. It reads the
JSONL evidence directly through the bootstrap SQL — no intermediate
`.duckdb` file is needed.

All commands run from the **project root** (the directory that contains
`.agent-factory/usage/`). The bootstrap SQL references that path, so it
will not resolve from any other working directory.

**Step 1.** Open DuckDB with the bootstrap SQL. This loads the evidence
and creates the six published views in memory:

```bash
uvx --from duckdb-cli duckdb -init .agent-factory/usage-analysis/sql/bootstrap-v1.sql
```

If you are working from the development source instead of an installed
project, use the development path:

```bash
uvx --from duckdb-cli duckdb -init packages/usage/sql/bootstrap-v1.sql
```

`uvx` runs the DuckDB CLI in an ephemeral environment — nothing is
installed permanently.

**Step 2.** Inside the DuckDB shell, install and start the UI extension.
The `INSTALL` step downloads the extension once and caches it; subsequent
sessions only need `LOAD`:

```sql
INSTALL ui;   -- first time only
LOAD ui;
CALL start_ui();
```

**Step 3.** Open `http://localhost:4213` in your browser. The six published
views (`session_usage`, `usage_by_dimension`, `cache_efficiency`, and
others) appear in the schema browser. Run any SQL query, then switch to
the chart view on the result set to visualize the data.

To stop, press Ctrl+C in the terminal or run `CALL stop_ui_server();` in
the DuckDB shell.

### Use the factory wrapper scripts

The project root provides wrapper scripts that find the usage component for
you. These are equivalent to the `uv run` commands above but shorter:

```bash
factory/scripts/usage-query session_usage --format table
factory/scripts/usage-query session_usage --persist usage.duckdb
factory/scripts/usage-explore usage.duckdb
```

### Use the Python API

Import the package in your own Python code:

```python
from pathlib import Path
from usage import input_snapshot, preflight, accounting

paths, digest = input_snapshot.snapshot(".agent-factory/usage/")
result = preflight.run_preflight(paths)

accounting.select_latest_snapshots(result.conn)
accounting.build_session_roots(result.conn)
accounting.build_session_contributions(result.conn)
accounting.compute_session_usage(result.conn)

rows = result.conn.execute("SELECT * FROM session_usage").fetchall()
```

The `result.conn` object is a standard DuckDB in-memory connection. Query
it with SQL or export it with the adapters module.

## Output formats

The CLI supports five output formats:

| Format     | Description                                          |
| ---------- | ---------------------------------------------------- |
| `json`     | JSON object to stdout (default)                      |
| `table`    | Human-readable aligned table to stdout               |
| `relation` | DuckDB relation (programmatic use via Python API)    |
| `arrow`    | Apache Arrow table (programmatic use via Python API) |
| `parquet`  | Apache Parquet file (requires `-o` output path)      |

The `arrow` and `parquet` formats require the optional `pyarrow` dependency:

```bash
uv sync --extra arrow
```

## Data pipeline

The package processes data through four stages:

1. **Contract check.** Every JSONL record is validated against the
   usage-record JSON Schema (`contracts/v1.schema.json`). Records with
   missing required fields, wrong types, or violated invariants are
   rejected.

2. **Preflight.** Valid records are classified by ancestry. Each record
   belongs to a session that may have a parent session. Preflight detects
   six categories of ancestry failures (self-parent, parent conflict,
   boundary crossing, missing parent, cycles, and root-count violations)
   and separates records into `preflight_valid` and `preflight_failure`.

3. **Accounting.** The valid records are deduplicated to latest snapshots,
   grouped into session trees, and aggregated under conservation (total
   equals input plus output).

4. **Projection.** The six published views expose the accounting results
   for querying.

## Project structure

```
packages/usage/
├── contracts/           Schema and compatibility policy
│   ├── contract.yaml
│   └── v1.schema.json
├── docs/                Component-level documentation
├── scripts/             Gate scripts (contract-check, dependency-check)
├── sql/
│   └── bootstrap-v1.sql DuckDB CLI bootstrap for the six published views
├── src/usage/
│   ├── accounting.py    Session tree and aggregation logic
│   ├── adapters.py      Output format adapters (JSON, table, Arrow, Parquet)
│   ├── cli.py           usage-query CLI entry point
│   ├── contract_check.py JSON Schema validation gate
│   ├── explorer.py      Web-based SQL explorer
│   ├── input_snapshot.py Directory snapshot and content digest
│   ├── parquet_exporter.py Parquet export from DuckDB views
│   ├── persist.py       Atomic DuckDB file export
│   ├── preflight.py     Ancestry validation and classification
│   ├── registry.py      CLI accounting registry
│   └── views/           One module per published view
├── tests/               Unit and integration tests
└── pyproject.toml       Package metadata and dependencies
```

## Related documentation

- [ADR-0015: Query authoritative JSONL with ephemeral DuckDB views](../../docs/adr/0015-query-authoritative-jsonl-with-ephemeral-duckdb-views.md) —
  the architecture decision that governs this component's design.
- [DuckDB UI Exploration](docs/ui-exploration.md) — additional notes on the
  web explorer and example queries.
- [Bootstrap SQL](sql/bootstrap-v1.sql) — the view definitions that the
  DuckDB CLI and the Python pipeline both implement.
