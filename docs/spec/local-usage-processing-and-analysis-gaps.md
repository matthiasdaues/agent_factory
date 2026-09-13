# Gaps Report: Local Usage Processing and Analysis

Generated: 2026-09-13

Source: [accepted proposal](../proposals/usage-processing-and-storage.md)

## Actor-Goal Matrix

| Actor              | Goal                                                        | Rule                                                                                        | Status    |
| ------------------ | ----------------------------------------------------------- | ------------------------------------------------------------------------------------------- | --------- |
| Local operator     | Query only published views over a fixed local input set     | Local operator queries only published views over a fixed local input set                    | specified |
| Local operator     | Obtain conservative canonical usage without duplication     | Local operator obtains conservative canonical usage without duplication                     | specified |
| Local operator     | Diagnose all invalid evidence before accounting             | Local operator diagnoses all invalid evidence before accounting                             | specified |
| Local analyst      | Consume typed table, JSON, relation, and Arrow results      | Local analyst consumes typed table, JSON, relation, and Arrow results                       | specified |
| Local operator     | Export attributable Parquet without damaging prior output   | Local operator exports attributable Parquet without damaging prior output                   | specified |
| Local analyst      | Receive a verified DuckDB UI exploration path               | Local analyst receives a verified DuckDB UI exploration path                                | specified |
| Project maintainer | Manage the opt-in component without accidental data loss    | Project maintainer manages the opt-in usage-analysis component without accidental data loss | specified |
| Factory producer   | Publish a compatible contract without depending on analysis | Factory producer publishes a compatible record contract without depending on analysis       | specified |
| Quality maintainer | Assign one deterministic owner to each observable contract  | Quality maintainer assigns one deterministic owner to each observable contract              | specified |

## Missing Rules

None. Every accepted actor-goal pair has one Rule in the [feature specification](local-usage-processing-and-analysis.feature).

## Rules Without Scenarios

None. Every Rule has a main success, boundary, or failure Scenario.

## Ambiguous Wording

None detected. The specification defines counts, paths, formats, the four exact producer CLI values and logical-run keys, rooted-tree ancestry invariants and failure codes, source normalization and comparison order, all six query-model-v1 schemas, dimension and time parameters, failure behavior, dependency locking, UI smoke ownership, lifecycle effects, and deferrals in testable terms from the accepted proposal.

## Review Trace

- [SPEC-0015](../findings/SPEC-0015.md) traces to the single `docs/testing.yaml` path across the concern, PRD, test-design, test-gate, scope-map, entity, interface, and validation contracts.
- [SPEC-0016](../findings/SPEC-0016.md) traces to the logical-run and source-position contracts in the feature, entity model, interface contract, validation rules, and LU-03 owner fixtures.
- [SPEC-0017](../findings/SPEC-0017.md) traces to the six query-model-v1 schemas and dimension request contract, owned by LU-07 integration tests.
- [SPEC-0018](../findings/SPEC-0018.md) traces to the UI documentation smoke scenario and the distinct LU-12 deterministic owner.
- [SPEC-0019](../findings/SPEC-0019.md) traces to direct DuckDB and PyArrow declarations, the shipped lockfile, the offline-cache contract, and the distinct LU-13 deterministic owner.
- [SPEC-0020](../findings/SPEC-0020.md) traces to the rooted-tree ancestry contract, five stable preflight codes, and the LU-05 deterministic owner.

Finding status remains owned by the independent repeat specification reviewer.

## Explicit Deferrals

The specification does not create actor goals for PostgreSQL, SQLite, a persistent authoritative DuckDB database, automatic Parquet materialization, Marimo, Jupyter, Grafana, dashboards, the community `dash` extension, containers, services, HTTP APIs, authentication, TLS, remote or cloud resources, centralized collection, access control, price catalogs, transcript-content indexing, raw-evidence retention automation, Pandas, or Polars. These remain deferred by the [proposal scope](../proposals/usage-processing-and-storage.md#scope).
