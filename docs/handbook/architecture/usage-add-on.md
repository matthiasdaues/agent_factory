---
title: The usage add-on pipeline
type: concept
status: implemented
order: 30
description: How the usage add-on turns JSONL records into six views in four stages.
---

# The usage add-on pipeline

You change the usage add-on in `packages/usage/`. The add-on reads the records that capture writes and publishes six views. [ADR-0015](../../adr/0015-query-authoritative-jsonl-with-ephemeral-duckdb-views.md) records why the JSONL stays authoritative and the DuckDB views stay ephemeral. The user side is in [The usage add-on](../../../packages/factory/docs/handbook/usage-capture/usage-add-on.md).

## Data pipeline

The package processes data in four stages:

1. **Contract check.** Every JSONL record is validated against the usage-record JSON Schema, `contracts/v1.schema.json`. A record with a missing required field, a wrong type, or a violated invariant is rejected.
2. **Preflight.** Valid records are classified by ancestry. A record belongs to a session, and a session may have a parent. Preflight detects six failures: self-parent, parent conflict, boundary crossing, missing parent, cycle, and root-count violation. It sorts records into `preflight_valid` and `preflight_failure`.
3. **Accounting.** The valid records are reduced to the latest snapshots, grouped into session trees, and summed. The total equals input plus output.
4. **Projection.** The six published views expose the accounting results for querying.

The directory layout of the package and the wrapper scripts are in [Usage add-on structure](usage-add-on-structure.md). To run the pipeline from a source checkout, follow [Run the usage add-on from source](run-usage-add-on-from-source.md).
