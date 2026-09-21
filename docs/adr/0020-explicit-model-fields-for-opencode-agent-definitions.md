---
id: 0020
status: proposed
evaluation: none
---

# Explicit model fields for OpenCode agent definitions

## Context

OpenCode issue #49765 prevents child sessions from inheriting the parent session's model setting. When a dispatcher creates a child session for a developer agent, the child falls back to the global default model instead of using the tier-appropriate model from `model.conf`.

Factory's model matrix maps each agent tier (economy, standard, strong) to a provider/model identifier per CLI. For Claude Code and Pi, the dispatcher passes the resolved model at spawn time and the child inherits it. OpenCode's inheritance bug breaks this path.

## Decision

Each generated OpenCode agent definition carries an explicit `model` field. The value is resolved from the agent's tier mapping in `model.conf` at generation time by `init-factory`.

This is a workaround, not a design choice. There is no genuine alternative until OpenCode fixes the inheritance bug. Omitting the field would cause every child session to run on the wrong model.

## Consequences

- Every OpenCode agent definition under `.opencode/agents/` includes a `model` field with the resolved provider/model identifier.
- When `model.conf` changes, `init-factory --update` must regenerate agent definitions to pick up the new model mappings.
- When OpenCode fixes issue #49765, the explicit `model` fields become unnecessary. The workaround is removable: delete the `model` field from the agent definition template and regenerate.
- No other CLI is affected. Claude Code and Pi resolve models at dispatch time without needing the field in the definition.
