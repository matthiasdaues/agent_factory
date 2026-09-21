# Context Map

Map of bounded contexts in the agent_factory repo. Each context has its own domain glossary and architecture documentation.

## Contexts

- **Factory** — the agent/skill/playbook system, dynamically run by an AI CLI, plus its deterministic flow-control harness. The harness includes a pure Eligibility Engine (`packages/factory/engine/`) that evaluates agent preconditions against the repository and returns immutable readiness verdicts, and deterministic validators (`block-dangerous-git.sh`, `concern-lint`). See [spec/prd.md](../spec/prd.md) for its specification and [README.md](../README.md) for its arc42 architecture documentation.

- **Usage Analysis** — opt-in local `packages/usage/` subproject that consumes
  Factory's versioned raw usage spool read-only. At runtime it is installed at
  `.agent-factory/usage-analysis/`. It validates a snapshotted input set and
  publishes six ephemeral DuckDB views for canonical accounting, diagnostics,
  and explicit output. Raw JSONL remains authoritative; Parquet and DuckDB UI
  state are derived. Factory owns capture and the record contract; Usage
  Analysis owns preflight, accounting, queries, and export.

- **Factory API** — future subproject; a vision-stub only. Planned as an API server connecting factory invocations to a web interface via message piping. No docs or code yet. Not scheduled for implementation.

## Relationships

Factory publishes the versioned usage-record contract and appends raw JSONL
consumed by Usage Analysis. The dependency points from Usage Analysis to that
contract; analysis availability never blocks Factory capture. Both contexts
remain local and transcript-blind at their shared boundary. Factory API has
no implemented integration.
