---
title: Usage add-on reference
type: reference
status: implemented
order: 50
description: The six published views, the options and output formats of usage-query, and the Python API of the usage add-on.
---

# Usage add-on reference

[Query usage views](query-usage-views.md) shows how to run the commands below.

## Published views

| View                   | What it shows                                   |
| ---------------------- | ----------------------------------------------- |
| `capture_health`       | Record counts and validation summary            |
| `raw_usage_snapshots`  | All valid records with evidence identity        |
| `latest_run_snapshots` | Latest snapshot per logical run                 |
| `session_usage`        | Per-session aggregated usage (input and output) |
| `usage_by_dimension`   | Contributing runs for flexible dimension splits |
| `cache_efficiency`     | Contributing runs for cache-hit analysis        |

## Options of `usage-query`

| Option           | Effect                                                    |
| ---------------- | --------------------------------------------------------- |
| `--format json`  | JSON output (default)                                     |
| `--format table` | Human-readable table                                      |
| `--diagnostic`   | Informational mode (only with `capture_health`)           |
| `--dimensions`   | Comma-separated dimension list for `usage_by_dimension`   |
| `--granularity`  | Time bucket: `none`, `hour`, `day`, `week`, `month`       |
| `--persist PATH` | Write the query's tables into a persistent `.duckdb` file |
| `-o PATH`        | Output file (needed for `--format parquet`)               |

## Output formats

| Format     | Description                                      |
| ---------- | ------------------------------------------------ |
| `json`     | JSON object to stdout (default)                  |
| `table`    | Human-readable aligned table to stdout           |
| `relation` | DuckDB relation (Python API only)                |
| `arrow`    | Apache Arrow table (Python API only)             |
| `parquet`  | Apache Parquet file (needs the `-o` output path) |

The command line accepts `--format relation` and `--format arrow`, but it cannot return those objects. It prints the JSON result instead. When preflight ran, it also prints a note on stderr that points to the Python API.

The `arrow` and `parquet` formats need the optional `pyarrow` dependency. Install it in `.agent-factory/usage/analysis`:

```bash
uv sync --extra arrow
```

## Python API

Run your script from the project root with the add-on's environment, for example `uv run --project .agent-factory/usage/analysis python script.py`. The option `--project` selects the environment and keeps the project root as the working directory, so the relative path `.agent-factory/usage/` below resolves. The option `--directory` would change the working directory to the add-on's folder. The script imports the package:

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

`result.conn` is a standard DuckDB in-memory connection. Query it with SQL or export it with the `adapters` module.
