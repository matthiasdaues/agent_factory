---
title: Usage add-on structure
type: reference
status: implemented
order: 40
description: The directory tree of packages/usage/, the wrapper scripts that find it, and the documents that describe it.
---

# Usage add-on structure

You look for a source file of the usage add-on. [The usage add-on pipeline](usage-add-on.md) explains what each stage does.

## Directory tree

```
packages/usage/
├── contracts/           Schema and compatibility policy
│   ├── contract.yaml
│   └── v1.schema.json
├── scripts/             Gate scripts (contract-check, dependency-check, ui-doc-check)
├── sql/
│   └── bootstrap-v1.sql DuckDB CLI bootstrap for the six published views
├── src/usage/
│   ├── accounting.py    Session tree and aggregation logic
│   ├── adapters.py      Output format adapters (JSON, table, Arrow, Parquet)
│   ├── cli.py           usage-query CLI entry point
│   ├── contract_check.py JSON Schema validation gate
│   ├── explorer.py      Web-based SQL explorer
│   ├── input_snapshot.py Directory snapshot and content digest
│   ├── parquet_exporter.py Parquet export from DuckDB views
│   ├── persist.py       Atomic DuckDB file export
│   ├── preflight.py     Ancestry validation and classification
│   ├── registry.py      CLI accounting registry
│   └── views/           One module per published view
├── tests/               Unit and integration tests
└── pyproject.toml       Package metadata and dependencies
```

The project wrappers `usage-query` and `usage-explore` in `packages/factory/scripts/` find the add-on. They look for `.agent-factory/usage/analysis/` first and for `packages/usage/` next, so they also run in a source checkout.

## Related documentation

- [ADR-0015](../../adr/0015-query-authoritative-jsonl-with-ephemeral-duckdb-views.md): the decision that governs the design of the add-on.
- [Bootstrap SQL](../../../packages/usage/sql/bootstrap-v1.sql): the view definitions that the DuckDB CLI and the Python pipeline both implement.
- [Explore usage in the browser](../../../packages/factory/docs/handbook/usage-capture/explore-usage-in-the-browser.md): the launch commands of the two browser UIs, which `usage-ui-doc-check` reads.
- [Usage check scripts](../testing/usage-check-scripts.md): the three gates of the package.
