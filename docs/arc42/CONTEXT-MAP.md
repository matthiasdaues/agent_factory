# Context Map

Map of bounded contexts in the agent_factory repo. Each context has its own domain glossary and architecture documentation.

## Contexts

- **Factory** — the agent/skill/playbook system, dynamically run by an AI CLI, plus its own deterministic flow-control harness (`transition-lint`, `phase`, `trigger`, `run-step`). See [spec/prd.md](../spec/prd.md) for its specification and [README.md](../README.md) for its arc42 architecture documentation.

- **Usage Accounting** — planned `usage/` subproject that ingests Factory's versioned raw usage spool, projects cumulative CLI captures into interaction deltas, and persists canonical usage in PostgreSQL. Factory owns capture; Usage Accounting owns processing, retention, storage, and reporting. No code or context documentation yet.

- **Factory API** — future subproject; a vision-stub only. Planned as an API server connecting `run-step`/`run-phase` invocations to a web interface via message piping. No docs or code yet. Not scheduled for implementation.

- **Orchestrator** — a stub Python CLI (`orchestrator/`); an earlier experiment at a standalone automation driver. Not functional. Factory's own phase scripts serve the same purpose.

## Relationships

Factory publishes the versioned raw usage spool consumed by Usage Accounting;
database availability never blocks Factory capture. Factory API has no
implemented integration.
