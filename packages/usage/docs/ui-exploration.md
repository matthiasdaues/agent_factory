# DuckDB UI Exploration

Interactive exploration of the same six published views that `usage-query`
exposes. Runs as an ephemeral localhost session — never a gate, never
authoritative state.

## Launch

From the project root, materialize the query pipeline into a persistent
DuckDB file, then open the web explorer:

```bash
factory/scripts/usage-query canonical_session_usage --persist usage.duckdb
factory/scripts/usage-explore usage.duckdb
```

The wrapper scripts discover the installed usage component
(`.agent-factory/usage-analysis/`) or the development source
(`packages/usage/`) and delegate via `uv run`.

The explorer opens a browser tab at `http://localhost:8642` with a sidebar
listing every materialized table, a SQL editor with preset queries, and
formatted results. Pass a custom port as a second argument if 8642 is taken.

### Direct invocation

If you prefer calling `uv` directly:

```bash
uv run --directory packages/usage usage-query canonical_session_usage --persist usage.duckdb
uv run --directory packages/usage python -m usage.explorer usage.duckdb
```

## Published Views

The query-model-v1 bootstrap SQL (`packages/usage/sql/bootstrap-v1.sql`)
defines these six published views:

| View                      | Description                                       |
| ------------------------- | ------------------------------------------------- |
| `raw_usage_snapshots`     | All valid records with evidence identity          |
| `latest_run_snapshots`    | Latest snapshot per logical run                   |
| `canonical_session_usage` | Per-session aggregated usage under conservation   |
| `usage_by_dimension`      | Contributing runs for flexible dimension grouping |
| `cache_efficiency`        | Contributing runs for cache-hit analysis          |
| `capture_health`          | Record counts and validation summary              |

## Alternative: DuckDB CLI

If the DuckDB CLI binary is installed separately:

```bash
duckdb -init packages/usage/sql/bootstrap-v1.sql
```

## Example Queries

```sql
SELECT * FROM canonical_session_usage ORDER BY normalized_total DESC;
```

```sql
SELECT cli, model, COUNT(*) AS runs, SUM(normalized_total) AS total_tokens
FROM usage_by_dimension
GROUP BY cli, model;
```

## Constraints

- The UI is optional. Analysis, query, and accounting gates never depend on it.
- The repository supplies no dashboard formulas or saved charts.
- The bootstrap SQL is read-only over the evidence spool.
