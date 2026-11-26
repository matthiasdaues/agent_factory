---
title: Codex
type: concept
status: implemented
order: 20
description: What init-factory installs for Codex, which permissions the generated agents inherit, and why you approve the hooks yourself.
---

# Codex

`init-factory` installs the Codex repository skills one by one under `.agents/skills/`. It generates native custom agents as TOML files under `.codex/agents/`. It links the catalogue, the playbooks, the rulebooks, and the scripts under `.codex/`. Codex reads `.codex/INDEX.yaml` first. Native subagents give a separate thread when author and reviewer sessions must stay independent, when a workflow must stay isolated, or when work runs in parallel.

The generated agents pin no model, reasoning level, sandbox, or approval policy. They inherit the permissions of the parent session and cannot widen them. A narrower custom-agent policy still takes precedence. The setting `agents.max_concurrent_threads_per_session` limits how many agents Codex runs in parallel. Parallel work does not lift the factory's rules for dependencies, overlapping outputs, and worktree isolation.

Trusting the project and activating its hooks are your decisions. After the installation, you trust the project, open `/hooks`, review the installed `PreToolUse`, `Stop`, and `SubagentStop` commands, and approve them. The installer reports this step but cannot approve it for you. A new or changed hook definition stays inactive until you review it again.
