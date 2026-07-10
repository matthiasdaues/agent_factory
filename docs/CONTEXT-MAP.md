# Context Map

Map of bounded contexts in the agent_factory repo. Each context has its own domain glossary and architecture documentation.

## Contexts

- [Orchestrator](../orchestrator/CONTEXT.md) — the thin Python CLI that drives the `ai_tooling` agent chain, running steps or whole chains with deterministic gates and human approval at phase gates. See also [orchestrator ADRs](../orchestrator/docs/adr/).

- **Factory** — the agent/skill/playbook system, dynamically run by an AI CLI. Real architecture exists (building blocks: agents, skills, gates; runtime view: phase handoffs) but documentation is created lazily per project convention — no docs yet.

- **Factory API** — future subproject; a vision-stub only. Planned as an API server connecting `run-step`/`run-phase` invocations to a web interface via message piping. No docs or code yet. Not scheduled for implementation.

## Relationships

Currently, each context operates independently. Factory and Factory API remain future work; integration points and data flows will be documented as contexts evolve.
