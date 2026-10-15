# Handoff: OpenCode CLI Integration — to Architecture Agent

## Current State

| Field                 | Value                                      |
| --------------------- | ------------------------------------------ |
| Workstream            | `opencode-cli-integration`                 |
| Branch                | `dev`                                      |
| Local tip             | `e12ad36e033fffaf915d2bcf864d95397fd23826` |
| Upstream tip (`main`) | `890a8596f05de61245ca94cf0cc0a750a8af8b83` |
| Ahead of main         | 5 commits                                  |
| Behind main           | 0 commits                                  |
| Working tree          | clean                                      |

## What is done

### Research (complete)

Seventeen source records document OpenCode CLI's extension points and the V2
plugin API surface. The original survey (SR-0001 through SR-0012) covered V1
configuration, agents, skills, dispatch, and session management. A follow-up
(SR-0013 through SR-0017) confirmed V2 plugin capabilities: tool interception,
permission evaluation, session observation, worktree management, and tool
restriction per agent.

- Survey report: `docs/research/opencode-cli-integration/survey-report.md`
- Source records: `docs/research/opencode-cli-integration/sources/SR-0001.md` through `SR-0017.md`

### Proposal (accepted)

The proposal adds OpenCode V2 as a fifth Factory CLI target. It covers
installation and discovery, orientation and catalog routing, a safety plugin
using the V2 plugin API, usage capture, isolated dispatch via worktrees, and
model mapping with a workaround for the model inheritance bug.

Two adversarial review passes (all eight checks pass, all findings resolved).

- Proposal: `docs/proposals/opencode-cli-integration.md` (status: accepted)
- Proposal commit on main: `0d747f9`

### Specification (reviewed, clean)

The requirements agent derived a full specification. Two spec review passes
(deterministic spec-lint plus semantic inspection), all findings resolved.

- Feature file: `docs/spec/opencode-cli-integration.feature` (11 Rules, 46 Scenarios)
- Scope map: `docs/spec/scope-map.md` (17 new rows: 10 specified, 7 deferred)
- Gaps report: `docs/spec/opencode-cli-integration-gaps.md` (5 open questions, 7 deferred items)
- QA strategy: `docs/spec/opencode-cli-integration-qa-strategy.md` (31 contract owners, OCI-01 through OCI-30)
- Entity model: `docs/spec/supplementary_specs/entity-model.md` (OpenCode entities section)
- Interface contracts: `docs/spec/supplementary_specs/interface-contracts.md` (OpenCode contracts section)
- State machines: `docs/spec/supplementary_specs/state-machines.md` (Plugin Health Lifecycle, Session Isolation Lifecycle)
- Validation rules: `docs/spec/supplementary_specs/validation-rules.md` (OpenCode validation rules section)

## What is next

The architecture agent should:

1. Read the accepted proposal and reviewed specification.
2. Update `docs/arc42/architecture.dsl` with OpenCode components, containers, and deployment views.
3. Write or update arc42 chapters that the OpenCode integration touches (likely chapters 05 Building Block View, 06 Runtime View, 08 Crosscutting Concepts, 09 Architecture Decisions).
4. Write ADRs for significant decisions (e.g., V2 plugin as enforcement boundary, model inheritance workaround, skill placement at `.agents/skills/`).

### Known constraints

- The model inheritance bug (OpenCode issue #49765) is open. The workaround is explicit `model` fields in generated agent definitions. This is an architecture decision worth recording.
- Four open questions about V2 plugin API behavior (see gaps report) may affect interface contracts but do not block architecture.
- The proposal explicitly defers task tracking, workflow orchestration, persistent memory, OS sandboxing, remote workspaces, Desktop support, and MCP-based adapter.
- The spec's closed CLI registry now includes five values. The architecture must reflect `opencode` as a first-class CLI alongside the existing four.

### Commit not on main

The specification commits (`8412767`, `3f483ae`, `e12ad36`) and one pre-existing fix (`813d94e`) are on `dev`, not `main`. The architecture agent works on `dev`.

## Suggested skills

| Skill                     | When to use                                                                                                            |
| ------------------------- | ---------------------------------------------------------------------------------------------------------------------- |
| `scaffold-arc42`          | If new arc42 chapters are needed for OpenCode                                                                          |
| `maintain-architecture`   | For DSL-first workflow and image export                                                                                |
| `model-structurizr-slice` | To model the OpenCode integration as a Structurizr slice                                                               |
| `write-adr`               | For each significant architecture decision                                                                             |
| `pugh-matrix`             | If genuine alternatives exist (e.g., plugin vs. MCP adapter — though MCP is deferred, the decision should be recorded) |
