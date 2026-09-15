---
schema_version: 2
title: Usage Data Visualization
status: draft
owner: md@matthiasdaues.de
created: 2026-09-14
updated: 2026-09-14
supersedes:

impact:
  scope: local
  architecture_change: false
  external_contract_change: false
  boundaries:
    - packages/usage/sql/bootstrap-v1.sql
    - packages/usage/src/usage/explorer.py

governance:
  assurance: routine
  risk_domains:
    - operations

estimate:
  as_of: 2026-09-14
  basis: judgment
  confidence: low
  human_review_hours: unknown
  normalized_tokens: unknown
  estimated_consumption: unknown
---

# Feature Request: Usage Data Visualization

## Summary

Add a chart-based dashboard to the usage analysis component so that
token spend, model mix, agent cost, and cache efficiency are visible
without writing SQL. The first release answers one question: "Where
are my tokens going?"

## Motivation

The usage package collects 3,400+ JSONL evidence records across four
CLIs, twenty models, fifteen agent types, and seventeen branches. Six
published views expose the data through SQL, a CLI, and a web-based
query explorer. All three output channels return tables. No channel
returns a chart.

Tables answer precise questions ("how many tokens did session X use?").
Charts answer structural questions ("is spend growing?", "which model
dominates?", "are subagents expensive relative to root sessions?").
The structural questions matter for project steering, cost control, and
model selection — and they require visual patterns that tables do not
reveal.

The DuckDB UI extension (`LOAD ui; CALL start_ui();`) provides basic
charting at zero implementation cost, but it requires a manual
multi-step launch, offers no saved dashboards, and disappears when the
DuckDB shell exits. A repeatable, low-friction visualization layer is
missing.

## Core Principles

- Read-only consumer. The dashboard reads the same evidence the usage
  package reads. It does not capture, transform, or store data beyond
  what the six published views already expose.
- Ephemeral by default. No long-running server process is required
  outside of active use. The dashboard starts, renders, and stops.
- No new runtime dependencies in the usage package itself. The
  visualization layer may use tools outside the Python package
  (DuckDB CLI, uvx, Node.js) as long as the usage package's
  `pyproject.toml` stays unchanged.

## Design

### Data already available

The bootstrap SQL (`sql/bootstrap-v1.sql`) creates six published views
from the JSONL evidence spool:

| View                   | Key columns for charting                                                     |
| ---------------------- | ---------------------------------------------------------------------------- |
| `session_usage`        | session_id, cli, normalized_input/output/total                               |
| `usage_by_dimension`   | all session_contributions fields including agent, model, branch, recorded_at |
| `cache_efficiency`     | reported_cache_read, reported_cache_write, cache_miss_turns                  |
| `latest_run_snapshots` | per-run latest snapshot with all fields                                      |
| `raw_usage_snapshots`  | every valid record                                                           |
| `capture_health`       | total_records, valid_count, failure_count                                    |

### Charts that answer "where are my tokens going?"

1. **Spend over time.** Daily `normalized_total` by CLI, stacked area
   chart. X-axis: date (from `recorded_at`). Y-axis: tokens. One
   series per CLI.

2. **Model mix.** Horizontal bar chart of `normalized_total` per model.
   Shows which models consume the most tokens.

3. **Agent cost breakdown.** Bar chart of `normalized_total` per agent
   type (including "direct" for records with no agent). Answers whether
   subagents are expensive relative to interactive use.

4. **Cache efficiency over time.** Line chart of
   `reported_cache_read / (reported_cache_read + reported_input)` per
   day. Higher is better. One line per CLI or model.

5. **Branch cost.** Bar chart of `normalized_total` per branch. Answers
   how much each feature branch cost to build.

6. **Session size distribution.** Histogram of `normalized_total` per
   session, bucketed. Reveals whether cost is spread evenly or
   concentrated in a few large sessions.

7. **I/O ratio by agent.** Stacked bar of `normalized_input` vs.
   `normalized_output` per agent type. Shows which agents read heavy
   vs. write heavy.

### Tool options explored

| Tool                             | Friction                    | Charts  | Dashboards | Persistence       | Refresh        |
| -------------------------------- | --------------------------- | ------- | ---------- | ----------------- | -------------- |
| DuckDB UI ext.                   | zero (uvx)                  | basic   | no         | no                | manual restart |
| Shaper                           | one docker                  | yes     | yes        | git-based         | on query       |
| Evidence.dev                     | npm project                 | yes     | yes        | static site       | rebuild        |
| Rill Developer                   | one binary                  | yes     | yes        | YAML              | on file change |
| Custom (Chart.js in explorer.py) | code change                 | yes     | no         | in-memory         | live watch     |
| Apache Superset                  | docker-compose (5 services) | full BI | yes        | Postgres metadata | scheduled      |

## Scope

**In the first release:**

- The seven charts listed in the Design section are available through a
  single launch command from the project root.
- The dashboard reads from the JSONL evidence spool or a persisted
  `.duckdb` file without additional data preparation.
- The launch command works with `uvx` or an equivalent ephemeral
  runner — no global install required.

**Explicitly deferred (do NOT plan stories for these):**

- Saved dashboard state across sessions. The first release is
  stateless.
- User-defined custom charts or drag-and-drop composition.
- Multi-project or multi-user dashboards.
- Scheduled or automated report generation.
- Cost forecasting or budget alerting.
- Integration with external BI platforms (Superset, Grafana, Metabase).

## Design Details

Does not apply yet. The tool choice determines the implementation
shape. This section will be filled after the tool decision in Open
Questions is resolved.

## Open Questions

1. **Which tool?** The six options in the Design table span zero-code
   (DuckDB UI) to full BI (Superset). The decision depends on who the
   audience is and how often they need the dashboard. Which tool fits
   the project's friction tolerance?

2. **Audience.** Is the dashboard for the project operator (one person
   checking spend), the team (shared view during standups), or
   external stakeholders? The answer affects persistence, sharing, and
   access control requirements.

3. **Refresh model.** Should the dashboard show live data (watches the
   spool), snapshot data (rebuild on demand), or both? The existing
   explorer supports live watch; the DuckDB UI does not.

4. **Where does the dashboard code live?** Options: inside
   `packages/usage/` (co-located with the data pipeline), a new
   `packages/usage-dashboard/` package, or outside the repo entirely
   (e.g., an Evidence.dev project or a Shaper config repo).

5. **Should the bootstrap SQL grow chart-oriented views?** The current
   six views serve the query model. Chart-specific aggregations (daily
   totals, model buckets, agent summaries) could be added as additional
   views to reduce SQL in the dashboard layer.

## Completion Criteria

- A single command from the project root opens a browser with the seven
  charts rendered from current evidence data.
- The command requires no global install beyond `uvx` or an equivalent
  ephemeral runner.
- Each chart is labeled, axes are named, and the data source (view or
  query) is identifiable.
- The dashboard works with both the JSONL evidence spool and a
  persisted `.duckdb` file.
- The README in `packages/usage/` documents how to launch the
  dashboard.

## Guiding Rule

Show where the tokens go without making the operator learn SQL first.
