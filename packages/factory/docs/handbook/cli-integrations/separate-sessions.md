---
title: How each CLI runs an agent in its own session
type: concept
status: implemented
order: 10
description: How Claude Code, Copilot CLI, Codex, and Pi start an agent in a separate session, and how Pi runs a parallel wave.
---

# How each CLI runs an agent in its own session

[Author and reviewer](../concepts/author-and-reviewer.md) explains why an agent that receives work starts in a session of its own. Each CLI creates that separate session in its own way:

- **Claude Code and GitHub Copilot CLI** start subagents natively. The parent session dispatches an agent and reads back its result.
- **Codex** gets native custom agents, which the factory generates under `.codex/agents/`. When a separate session is needed, the generated custom agent runs through Codex's native subagent mechanism. When you select an agent directly for interactive work, it may run in the current session unless a separation is needed. [Codex](codex.md) describes the Codex setup.
- **Pi** has no native subagent. `init-factory` installs a project-local extension, `.pi/extensions/run-agent.ts`, that registers a `run_agent` tool. A call to `run_agent` starts a separate `pi` subprocess with the chosen agent's Markdown as its system prompt and returns the child's result.

> Rule summary: **MUST (Pi only)** invoke the `run_agent` tool to run a factory agent. Do not read `.pi/agents/<name>.md` and act it out in the current session.
> Source: [rules.md § CLI integration](../../../rulebooks/rules.md#cli-integration)

Acting out the agent file in the current session would leak the author's reasoning into the review.

## How `run_agent` picks a model

`run_agent` takes the child's model from the row `pi.<tier>` of `.agent-factory/config/model.conf` for the tier the agent declares, unless the call passes an explicit model id. A cap on the recursion depth limits nested spawns. The git-safety guardrail extension loads in the child too, so a spawned agent stays under the same [guardrail](guardrails.md) as its parent. The ADR "Pi subagent invocation via subprocess spawn" (ADR-0004) in the Agent Factory repository records this design.

## Parallel waves under Pi

Under Claude Code, the `implementation-agent` runs a wave of stories with the native Agent tool, which starts several subagents at once, each in its own worktree. Under Pi, a second extension, `.pi/extensions/dispatch-wave.ts`, registers a `dispatch_wave` tool for the same job.

`dispatch_wave` takes one wave that the caller planned so that no two items write the same files. It creates a feature branch in its own git worktree for each item and starts each agent there in parallel. Unless told otherwise, it runs `premerge-check` before it merges each finished branch into the target. `premerge-check` runs against the frozen base of the wave, so a sibling merge that moves the target never flags a later branch as stale.

`dispatch_wave` does not plan the wave. The calling agent checks the overlap of output files and the order of dependencies, as `implementation-agent` documents.
