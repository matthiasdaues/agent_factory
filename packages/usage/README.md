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

The usage component is optional. Add it to a project that has Agent Factory
with `init-factory --add usage`, or pass `--with-usage` to the first
`init-factory` call. The steps below are for manual installation or for
working from the development source.

### 1. Navigate to the package directory

If you are working inside the Agent Factory repository:

```bash
cd packages/usage
```

If the usage component was installed into your project by `init-factory`:

```bash
cd .agent-factory/usage/analysis
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

In an installed project, use `--directory .agent-factory/usage/analysis`.
You should see a JSON object with `total_lines`, `valid_count`, and
`failure_count`. If the command prints `directory not found`, confirm that
`.agent-factory/usage/` exists and contains `.jsonl` files.

## Related documentation

- [Usage add-on chapter of the user handbook](../factory/docs/handbook/usage-capture/usage-add-on.md):
  queries, the two browser UIs, output formats, and the Python API.
- [Usage add-on in the contributor handbook](../../docs/handbook/architecture/usage-add-on.md):
  the data pipeline and the project structure.
- [ADR-0015: Query authoritative JSONL with ephemeral DuckDB views](../../docs/adr/0015-query-authoritative-jsonl-with-ephemeral-duckdb-views.md):
  the architecture decision that governs this component's design.
- [Bootstrap SQL](sql/bootstrap-v1.sql): the view definitions that the
  DuckDB CLI and the Python pipeline both implement.
