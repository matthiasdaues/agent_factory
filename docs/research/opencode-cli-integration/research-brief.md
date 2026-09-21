# Research Brief — OpenCode CLI Integration

```json
{
  "mode": "survey",
  "research_question": "What extension points does OpenCode CLI expose (configuration, system prompts, agent/tool definitions, subagent dispatch, MCP support), and how do they map to the Agent Factory multi-CLI integration pattern used by Claude Code, Copilot CLI, Pi, and Codex?",
  "intended_use": "Design a factory integration shim for OpenCode CLI — directory conventions, INDEX.yaml mapping, agent definitions, skill routing, and dispatch mechanism — so the factory can target OpenCode as a fifth supported CLI.",
  "audience": "Agent Factory maintainers and users who want to run factory workflows from OpenCode CLI.",
  "scope": "OpenCode CLI's project-level configuration format, system prompt injection mechanism, tool protocol (file read/write/bash/MCP), agent or custom-instruction definitions, session management, subagent or parallel-execution capabilities, and any plugin or extension API. Also covers how the existing four CLI integrations are structured in the factory, as the target pattern to map onto.",
  "exclusions": [
    "OpenCode's internal implementation details (Go source internals beyond what the public API/config exposes)",
    "Comparison or evaluation of OpenCode vs other CLIs as products",
    "Pricing, licensing, or commercial considerations",
    "OpenCode's UI/TUI features unrelated to agent integration"
  ],
  "freshness_requirements": [
    "OpenCode CLI documentation and repository state as of 2026-09",
    "Sources older than 12 months are acceptable only for stable, unchanged configuration formats"
  ],
  "source_requirements": [
    "OpenCode's official GitHub repository and README",
    "OpenCode's configuration documentation or schema files",
    "OpenCode's source code for configuration loading and prompt injection (as primary source when docs are thin)",
    "Agent Factory's existing CLI integration code and rules.md for the target pattern"
  ],
  "cost_of_error": "Building a non-functional integration shim that doesn't match OpenCode's actual extension model, wasting implementation effort. Low external risk — this is an internal tooling decision.",
  "completion_criteria": [
    "OpenCode's configuration directory and file conventions are documented",
    "OpenCode's system prompt / custom instructions mechanism is documented",
    "OpenCode's tool protocol (file ops, bash, MCP) is documented",
    "OpenCode's subagent or parallel execution capabilities (or lack thereof) are documented",
    "A mapping table exists showing each factory integration point and its OpenCode equivalent (or 'not available')",
    "Gaps and blockers for a full integration are identified"
  ]
}
```
