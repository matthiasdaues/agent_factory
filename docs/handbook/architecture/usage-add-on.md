---
title: The usage add-on pipeline and structure
type: concept
status: implemented
order: 30
description: How the usage add-on turns JSONL records into six views, and where its files live in packages/usage/.
---

# The usage add-on pipeline and structure

You change the usage add-on in `packages/usage/`. The add-on reads the records that capture writes and publishes six views. [ADR-0015](../../adr/0015-query-authoritative-jsonl-with-ephemeral-duckdb-views.md) records why the JSONL stays authoritative and the DuckDB views stay ephemeral. The user side is in [The usage add-on](../../../packages/factory/docs/handbook/usage-capture/usage-add-on.md).

## Data pipeline

The package processes data in four stages:

1. **Contract check.** Every JSONL record is validated against the usage-record JSON Schema, `contracts/v1.schema.json`. A record with a missing required field, a wrong type, or a violated invariant is rejected.
2. **Preflight.** Valid records are classified by ancestry. A record belongs to a session, and a session may have a parent. Preflight detects six failures: self-parent, parent conflict, boundary crossing, missing parent, cycle, and root-count violation. It sorts records into `preflight_valid` and `preflight_failure`.
3. **Accounting.** The valid records are reduced to the latest snapshots, grouped into session trees, and summed. The total equals input plus output.
4. **Projection.** The six published views expose the accounting results for querying.

## Project structure

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
- [Usage check scripts](../testing/usage-check-scripts.md): the three gates of the package.
