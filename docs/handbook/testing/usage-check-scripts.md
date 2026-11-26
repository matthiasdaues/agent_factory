---
title: Usage check scripts
type: reference
status: implemented
order: 30
description: The three gate scripts in packages/usage/scripts/, what each checks, and how to run them.
---

# Usage check scripts

You change `packages/usage/` and want to know which gates guard it. Each script sits in `packages/usage/scripts/`. Run each from the repository root. It exits 0 when its check passes.

| Script                        | What it checks                                                                                                                                     |
| ----------------------------- | -------------------------------------------------------------------------------------------------------------------------------------------------- |
| `usage-contract-check <path>` | Validates JSONL records against the usage-record contract. Exits 1 on a failed record and 2 on an operational error.                               |
| `usage-dependency-check`      | Confirms that `pyproject.toml` declares DuckDB and pyarrow directly, and that pyarrow has a version bound.                                         |
| `usage-ui-doc-check`          | Reads [Explore usage in the browser](../../../packages/factory/docs/handbook/usage-capture/explore-usage-in-the-browser.md) and runs three checks. |

`usage-ui-doc-check` checks that the bootstrap SQL named on the page registers the six published views, that the page documents the `--persist` and explorer commands, and that `src/usage/explorer.py` exists. The page names the installed path `.agent-factory/usage/analysis/`, so the script maps it to `packages/usage/` before it reads the SQL. The script never starts, fetches, or installs the DuckDB UI.
