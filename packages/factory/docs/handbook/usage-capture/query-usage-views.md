---
title: Query usage views
type: how-to
status: implemented
order: 60
description: Query the six usage views from the command line, read per-tool token use, and save the result to a DuckDB file.
---

# Query usage views

You want to see how many tokens each CLI tool used. Run every command from the project root. The wrapper scripts in `.agent-factory/factory/scripts/` find the installed add-on, so you need not change into its folder.

1. Query a view. The call has the form `usage-query <view> [options]`. This one prints the token use per CLI tool:

   ```bash
   .agent-factory/factory/scripts/usage-query session_usage --format table
   ```

2. Pick another view or option. The [add-on reference](usage-add-on-reference.md) lists the six views and the options.

3. Save the result for later work. The query runs in memory by default. To keep the result as tables in a file, add `--persist`:

   ```bash
   .agent-factory/factory/scripts/usage-query session_usage --persist usage.duckdb
   ```

   The file is an ordinary DuckDB database, so any DuckDB client opens it. [Explore usage in the browser](explore-usage-in-the-browser.md) shows two ways to read it.

   The file holds the tables that the chosen query built, not the six published views by name. The query `session_usage` writes six tables: `latest_run_snapshots`, `preflight_failure`, `preflight_valid`, `session_contributions`, `session_roots`, and `session_usage`. The other views write fewer tables. `capture_health` and `raw_usage_snapshots` write two. `latest_run_snapshots` writes three. `usage_by_dimension` and `cache_efficiency` write five and no `session_usage`.

## Example queries

Run these in a DuckDB shell or in the browser explorer, on a file that you wrote with `usage-query session_usage --persist`.

Sessions with the most tokens first:

```sql
SELECT * FROM session_usage ORDER BY normalized_total DESC;
```

Runs and tokens per CLI and model. The table `session_contributions` holds the rows that the view `usage_by_dimension` publishes:

```sql
SELECT cli, model, COUNT(*) AS runs, SUM(normalized_total) AS total_tokens
FROM session_contributions
GROUP BY cli, model;
```

The DuckDB UI path in [Explore usage in the browser](explore-usage-in-the-browser.md) creates all six views, so there you can query `usage_by_dimension` by name.
