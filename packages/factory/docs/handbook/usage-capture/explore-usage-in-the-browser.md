---
title: Explore usage in the browser
type: how-to
status: implemented
order: 70
description: Open the usage views in the bundled SQL explorer or in the DuckDB UI, and start DuckDB from the command line.
---

# Explore usage in the browser

You want to run SQL over your usage data and see the results. Two browser tools do that. Both run on localhost and need no network connection. The tools read the same six views as `usage-query`.

Run every command from the project root, the folder that holds `.agent-factory/usage/`.

## Path 1: the bundled SQL explorer

The explorer gives you a SQL editor with preset queries, a schema sidebar, and formatted tables. It reads a persisted `.duckdb` file.

1. Write the file:

   ```bash
   .agent-factory/factory/scripts/usage-query session_usage --persist usage.duckdb
   ```

2. Start the explorer:

   ```bash
   .agent-factory/factory/scripts/usage-explore usage.duckdb
   ```

   A browser tab opens at `http://localhost:8642`. The sidebar lists every table and view, and a click fills the editor. Six preset queries sit above the results. Press Ctrl+Enter to run a query and Ctrl+C in the terminal to stop the server. To use another port, add it as a second argument.

   Without the wrappers, call uv directly:

   ```bash
   uv run --directory .agent-factory/usage/analysis usage-query session_usage --persist usage.duckdb
   uv run --directory .agent-factory/usage/analysis python -m usage.explorer usage.duckdb
   ```

The explorer watches `.agent-factory/usage/`. When a JSONL file changes, it rebuilds the DuckDB file and refreshes the browser.

## Path 2: the DuckDB UI

The DuckDB UI adds charts (bar, line, area, scatter, pie), column summaries, and dashboards. It reads the JSONL records through the bootstrap SQL, so it needs no `.duckdb` file. The bootstrap SQL names `.agent-factory/usage/`, so it resolves only from the project root.

1. Open DuckDB with the bootstrap SQL. It loads the records and creates the six views in memory:

   ```bash
   uvx --from duckdb-cli duckdb -init .agent-factory/usage/analysis/sql/bootstrap-v1.sql
   ```

   `uvx` runs the DuckDB command-line client in a throwaway environment and installs nothing permanently. If you already have the `duckdb` binary, call `duckdb -init` with the same file.

2. In the DuckDB shell, start the UI. `INSTALL` downloads the extension once. Later sessions need only `LOAD`:

   ```sql
   INSTALL ui;   -- first time only
   LOAD ui;
   CALL start_ui();
   ```

3. Open `http://localhost:4213`. The views appear in the schema browser. Run a query, then switch the result to the chart view.

To stop, press Ctrl+C or run `CALL stop_ui_server();` in the shell.
