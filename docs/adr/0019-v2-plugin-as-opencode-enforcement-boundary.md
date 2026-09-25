---
id: 0019
status: proposed
evaluation: pugh-matrix
---

# V2 plugin as OpenCode enforcement boundary

## Context

Factory safety controls for Claude Code, Copilot CLI, and Codex run through native PreToolUse hooks. Pi uses a project-local extension to enforce the same deny list. OpenCode exposes a V2 Plugin API (`Plugin.define()`) with hooks that fire before tool execution (`execute.before`), after execution (`execute.after`), during permission evaluation (`permission.hook("evaluate")`), session context assembly (`session.hook("context")`), and worktree creation (`ctx.worktree.transform()`).

An alternative enforcement path is an MCP-based adapter: a Factory-owned MCP server that OpenCode connects to, providing Factory operations as MCP tools with guards. The proposal deferred this path. The question is whether the V2 plugin or an MCP server should carry the enforcement boundary.

The model field in generated agent definitions resolves from the model matrix tier mapping in `model.conf`. Both approaches require explicit `model` fields due to OpenCode issue #49765. This is a property of the generated definitions, not of the enforcement mechanism.

## Decision

Use the OpenCode V2 Plugin API as the enforcement boundary.

| Criterion                      | Weight | V2 Plugin (baseline) | MCP Adapter |
| ------------------------------ | ------ | -------------------- | ----------- |
| Safety: fail-closed (QS-7)     | 3      | 0                    | -1          |
| Clean Architecture (QS-3)      | 3      | 0                    | 0           |
| Simplicity / YAGNI             | 2      | 0                    | -1          |
| Testability                    | 2      | 0                    | -1          |
| Resilience (QS-5)              | 2      | 0                    | -1          |
| Compatibility (QS-8)           | 2      | 0                    | 0           |
| Model inheritance independence | 1      | 0                    | 0           |
| **Weighted total**             |        | **0**                | **-10**     |

**Safety (weight 3, MCP scores -1):** The V2 plugin's `execute.before` hook fires in-process before every tool invocation, giving the Permission Enforcer a synchronous denial point. An MCP server is out-of-process and cannot intercept native OpenCode tool calls (file reads, writes, shell commands). MCP tools are additive -- they cannot deny or gate tools the MCP server did not provide.

**Simplicity (weight 2, MCP scores -1):** The V2 plugin is a single TypeScript module loaded by OpenCode's plugin system. An MCP adapter requires a separate server process, JSON-RPC transport, lifecycle management (startup, health, reconnection), and a mapping layer between Factory operations and MCP tool definitions.

**Testability (weight 2, MCP scores -1):** The plugin runs in OpenCode's test harness. An MCP adapter needs protocol-level integration tests across a process boundary.

**Resilience (weight 2, MCP scores -1):** The plugin shares the OpenCode process lifecycle. An MCP server can crash independently, creating a partial-failure mode where OpenCode runs without enforcement unless the plugin also monitors MCP server health.

**Clean Architecture, Compatibility, Model inheritance (scores 0):** Both options sit at the adapter layer. Both create OpenCode-specific files. Both require explicit model fields due to the inheritance bug -- this criterion is illusory because the model field is just the resolved value of the tier field from the model matrix, not an independent architectural concern.

The MCP adapter scores negatively on every differentiating criterion. No weight adjustment flips the result.

## Consequences

- The Factory plugin uses OpenCode's V2 Plugin API for all enforcement: permissions, tool restriction, usage capture, worktree isolation, and orientation injection.
- Four open questions about V2 API behavior (documented in the gaps report) must be resolved empirically during implementation. If any answer invalidates the plugin approach, the MCP adapter becomes the fallback.
- The MCP-based adapter remains a deferred option. If OpenCode deprecates the V2 Plugin API, or if a future CLI lacks a plugin mechanism, MCP becomes the alternative enforcement path.
- The plugin's six components (Permission Enforcer, Tool Restrictor, Usage Observer, Worktree Strategy, Orientation Injector, Health Monitor) are documented in the architecture DSL and building block view.
