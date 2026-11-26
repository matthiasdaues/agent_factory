---
title: Query usage views
type: how-to
status: implemented
order: 60
description: Query the six usage views from the command line, read per-tool token use, and save the views to a DuckDB file.
---

# Query usage views

You want to see how many tokens each CLI tool used. Run every command from the project root. The wrapper scripts in `.agent-factory/factory/scripts/` find the installed add-on, so you need not change into its folder.

1. Query a view. The call has the form `usage-query <view> [options]`. This one prints the token use per CLI tool:

   ```bash
   .agent-factory/factory/scripts/usage-query session_usage --format table
   ```

2. Pick another view or option. The [add-on reference](usage-add-on-reference.md) lists the six views and the options.

3. Save the result for later work. The query runs in memory by default. To keep every published view as a table in a file, add `--persist`:

   ```bash
   .agent-factory/factory/scripts/usage-query session_usage --persist usage.duckdb
   ```

   The file is an ordinary DuckDB database, so any DuckDB client opens it. [Explore usage in the browser](explore-usage-in-the-browser.md) shows two ways to read it.

## Example queries

Run these in a DuckDB shell or in the browser explorer, after you persisted the views.

Sessions with the most tokens first:

```sql
SELECT * FROM session_usage ORDER BY normalized_total DESC;
```

Runs and tokens per CLI and model:

```sql
SELECT cli, model, COUNT(*) AS runs, SUM(normalized_total) AS total_tokens
FROM usage_by_dimension
GROUP BY cli, model;
```
