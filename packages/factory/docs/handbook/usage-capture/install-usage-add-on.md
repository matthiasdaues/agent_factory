---
title: Install the usage add-on
type: how-to
status: implemented
order: 50
description: Install the optional usage add-on into a project and check that it can read your records.
---

# Install the usage add-on

You want to query the token use that capture recorded. Install the add-on first. The factory runs without it, so skip this page if you only need capture.

## Before you start

- Python 3.10 or later.
- uv, the package manager the factory uses. If you do not have it, follow the installation guide on the uv documentation site, docs.astral.sh/uv.
- At least one `.jsonl` file in `.agent-factory/usage/`. Capture writes these files. With an empty or missing folder, there is nothing to analyse.

## Steps

1. Install the add-on into the project. On a project that is already set up, run:

   ```bash
   .agent-factory/factory/scripts/init-factory --add usage
   ```

   On a new project, add the option `--with-usage` to the first `init-factory` call instead.

   The command copies the add-on to `.agent-factory/usage/analysis/`.

2. Install its dependencies. The first query does this for you, so the step is optional:

   ```bash
   cd .agent-factory/usage/analysis
   uv sync
   ```

   `uv sync` reads `pyproject.toml`, which declares DuckDB 1.3.0 or later, creates a virtual environment, and installs into it.

3. Check the installation from the project root:

   ```bash
   .agent-factory/factory/scripts/usage-query capture_health --diagnostic
   ```

   The command prints a JSON object with `total_records`, `valid_count`, and `failure_count`. If it prints `directory not found`, confirm that `.agent-factory/usage/` exists and holds `.jsonl` files.

Next, [query the views](query-usage-views.md).
