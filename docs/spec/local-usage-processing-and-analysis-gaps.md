# Gaps Report: Local Usage Processing and Analysis

Generated: 2026-09-11

Source: [accepted proposal](../proposals/usage-processing-and-storage.md)

## Actor-Goal Matrix

| Actor              | Goal                                                        | Rule                                                                                        | Status    |
| ------------------ | ----------------------------------------------------------- | ------------------------------------------------------------------------------------------- | --------- |
| Local operator     | Query only published views over a fixed local input set     | Local operator queries only published views over a fixed local input set                    | specified |
| Local operator     | Obtain conservative canonical usage without duplication     | Local operator obtains conservative canonical usage without duplication                     | specified |
| Local operator     | Diagnose all invalid evidence before accounting             | Local operator diagnoses all invalid evidence before accounting                             | specified |
| Local analyst      | Consume typed table, JSON, relation, and Arrow results      | Local analyst consumes typed table, JSON, relation, and Arrow results                       | specified |
| Local operator     | Export attributable Parquet without damaging prior output   | Local operator exports attributable Parquet without damaging prior output                   | specified |
| Local analyst      | Explore published views through DuckDB's bundled UI         | Local analyst explores published views through DuckDB's bundled UI                          | specified |
| Project maintainer | Manage the opt-in component without accidental data loss    | Project maintainer manages the opt-in usage-analysis component without accidental data loss | specified |
| Factory producer   | Publish a compatible contract without depending on analysis | Factory producer publishes a compatible record contract without depending on analysis       | specified |
| Quality maintainer | Assign one deterministic owner to each observable contract  | Quality maintainer assigns one deterministic owner to each observable contract              | specified |

## Missing Rules

None. Every accepted actor-goal pair has one Rule in the [feature specification](local-usage-processing-and-analysis.feature).

## Rules Without Scenarios

None. Every Rule has a main success, boundary, or failure Scenario.

## Ambiguous Wording

None detected. Counts, paths, formats, supported CLIs, views, failure behavior, lifecycle effects, and deferrals use explicit terms from the accepted proposal.

## Explicit Deferrals

The specification does not create actor goals for PostgreSQL, SQLite, a persistent authoritative DuckDB database, automatic Parquet materialization, Marimo, Jupyter, Grafana, dashboards, the community `dash` extension, containers, services, HTTP APIs, authentication, TLS, remote or cloud resources, centralized collection, access control, price catalogs, transcript-content indexing, raw-evidence retention automation, Pandas, or Polars. These remain deferred by the [proposal scope](../proposals/usage-processing-and-storage.md#scope).
