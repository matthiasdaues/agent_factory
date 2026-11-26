---
title: Explore usage in the browser
type: how-to
status: implemented
order: 70
description: Open the usage views in the bundled SQL explorer or in the DuckDB UI, and start DuckDB from the command line.
---

# Explore usage in the browser

You want to run SQL over your usage data and see the results. Two browser tools do that. Both run on localhost and read the same records as `usage-query`. The bundled explorer needs no network connection once the add-on's dependencies are installed. The DuckDB UI downloads software on its first run, as [Path 2](#path-2-the-duckdb-ui) describes.

Run every command from the project root, the folder that holds `.agent-factory/usage/`. The usage add-on is optional and not installed by default. If `.agent-factory/usage/` is missing, [install the add-on](install-usage-add-on.md) first.

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

   Without the wrappers, call uv directly. The option `--directory` makes uv run in the add-on's folder, so the explorer would look for a relative database path there. Give it an absolute path and an absolute spool path. The query command resolves `--persist` against the project root, so it needs no change. Run these from the project root:

   ```bash
   uv run --directory .agent-factory/usage/analysis usage-query session_usage --persist usage.duckdb
   uv run --directory .agent-factory/usage/analysis python -m usage.explorer "$PWD/usage.duckdb" --watch "$PWD/.agent-factory/usage"
   ```

The `usage-explore` wrapper passes `--watch` with the spool folder `.agent-factory/usage/` for you and turns it off with `--no-watch`. The direct command watches only when you add `--watch`. With watching on, the explorer rebuilds the DuckDB file when a JSONL file changes and refreshes the browser. The rebuild writes the same tables as `--persist` with `session_usage`.

## Path 2: the DuckDB UI

The DuckDB UI adds charts (bar, line, area, scatter, pie), column summaries, and dashboards. It reads the JSONL records through the bootstrap SQL, so it needs no `.duckdb` file. The bootstrap SQL names `.agent-factory/usage/`, so it resolves only from the project root. This path needs the network on its first run. `uvx` fetches the DuckDB command-line client unless it is cached, and `INSTALL ui` downloads the extension. This page makes no offline claim for the UI itself. DuckDB's own documentation says what the UI loads in later sessions.

1. Open DuckDB with the bootstrap SQL. It loads the records and creates the six views in memory:

   ```bash
   uvx --from duckdb-cli duckdb -init .agent-factory/usage/analysis/sql/bootstrap-v1.sql
   ```

   `uvx` runs the DuckDB command-line client in a throwaway environment and installs nothing permanently. If you already have the `duckdb` binary, call `duckdb -init` with the same file.

2. In the DuckDB shell, start the UI. `INSTALL` downloads the extension once, so it needs the network. Later sessions need only `LOAD`:

   ```sql
   INSTALL ui;   -- first time only
   LOAD ui;
   CALL start_ui();
   ```

3. Open `http://localhost:4213`. The views appear in the schema browser. Run a query, then switch the result to the chart view.

To stop, press Ctrl+C or run `CALL stop_ui_server();` in the shell.
