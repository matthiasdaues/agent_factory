---
title: Run the usage add-on from source
type: how-to
status: implemented
order: 50
description: Install, query, and explore the usage add-on from a checkout of the factory repository.
---

# Run the usage add-on from source

You work in a checkout of the factory repository and want to run the add-on from `packages/usage/`. The commands match the installed ones in the user handbook, except for the folder. Replace `.agent-factory/usage/analysis` with `packages/usage`. Run every command from the repository root.

1. Install the dependencies. The first query does this for you, so the step is optional:

   ```bash
   uv sync --directory packages/usage
   ```

2. Check the installation from the repository root:

   ```bash
   uv run --directory packages/usage usage-query capture_health --diagnostic
   ```

   The command prints a JSON object with `total_lines`, `valid_count`, and `failure_count`. If it prints `directory not found`, confirm that `.agent-factory/usage/` exists and holds `.jsonl` files.

3. Query a view and save the result:

   ```bash
   uv run --directory packages/usage usage-query session_usage --format table
   uv run --directory packages/usage usage-query session_usage --persist usage.duckdb
   ```

   The option `--persist` resolves its path against the folder that holds `.agent-factory/`, so `usage.duckdb` lands in the repository root.

4. Start the bundled explorer. The option `--directory` changes the working directory to `packages/usage`, so pass absolute paths:

   ```bash
   uv run --directory packages/usage python -m usage.explorer "$PWD/usage.duckdb" --watch "$PWD/.agent-factory/usage"
   ```

5. Or open the DuckDB shell with the bootstrap SQL, and start the UI as the [browser guide](../../../packages/factory/docs/handbook/usage-capture/explore-usage-in-the-browser.md) describes:

   ```bash
   duckdb -init packages/usage/sql/bootstrap-v1.sql
   ```

The wrappers `packages/factory/scripts/usage-query` and `packages/factory/scripts/usage-explore` also work in a checkout. They look for `.agent-factory/usage/analysis/` first and for `packages/usage/` next, so you can run them in place of the `uv run` commands above.
