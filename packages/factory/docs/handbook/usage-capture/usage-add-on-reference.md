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

| Option           | Effect                                                  |
| ---------------- | ------------------------------------------------------- |
| `--format json`  | JSON output (default)                                   |
| `--format table` | Human-readable table                                    |
| `--diagnostic`   | Informational mode (only with `capture_health`)         |
| `--dimensions`   | Comma-separated dimension list for `usage_by_dimension` |
| `--granularity`  | Time bucket: `none`, `hour`, `day`, `week`, `month`     |
| `--persist PATH` | Write the views into a persistent `.duckdb` file        |
| `-o PATH`        | Output file (needed for `--format parquet`)             |

## Output formats

| Format     | Description                                          |
| ---------- | ---------------------------------------------------- |
| `json`     | JSON object to stdout (default)                      |
| `table`    | Human-readable aligned table to stdout               |
| `relation` | DuckDB relation (programmatic use via Python API)    |
| `arrow`    | Apache Arrow table (programmatic use via Python API) |
| `parquet`  | Apache Parquet file (needs the `-o` output path)     |

The `arrow` and `parquet` formats need the optional `pyarrow` dependency. Install it in `.agent-factory/usage/analysis`:

```bash
uv sync --extra arrow
```

## Python API

Run your script with the add-on's environment, for example `uv run --directory .agent-factory/usage/analysis python script.py`. The script imports the package:

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
