# Agent Factory

The inert tooling — agents, skills, playbooks, rulebooks, deterministic gate scripts — that drives an AI coding CLI through a structured development lifecycle, without any automation/dispatch layer of its own.

## Language

**Agent Factory**:
This repository. The methodology and tooling content, consumed by a human running an AI CLI directly, or by a separate automation layer (e.g. an orchestrator) built on top of it.
_Avoid_: "the factory" (fine in conversation, not the canonical written term)

**`agent_factory-` prefix**:
The hardcoded string every Agent Factory skill and agent name is invoked with once installed, so it never collides with a same-named skill or agent already present in a user's CLI setup ([ADR-0001](adr/0001-skill-agent-name-collision-avoidance.md#decision)).
_Avoid_: a configurable or user-chosen prefix — considered and retracted; the value is fixed, not a setting
