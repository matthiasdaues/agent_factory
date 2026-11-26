---
title: Files that init-factory creates
type: reference
status: implemented
order: 20
description: Every file and folder that setup writes, which of them git tracks, and what each configuration file holds.
---

# Files that init-factory creates

| File                                         | Holds                                                                                                                                                                                                                                                                                                                                                      | Appears                                                                                                                                                                                                             |
| -------------------------------------------- | ---------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- | ------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| `.agent-factory/config/project.json`         | The project identity: a stable UUID `project_id`, the name `project_name` you gave at installation, and your declared test command. Every usage record carries `project_id`, so a record stays attributable when the folder moves. The list `safety_critical_paths` feeds the tier rubric: work whose outputs match one of its globs gets the strong tier. | At installation. You do not edit it by hand in normal use.                                                                                                                                                          |
| `.agent-factory/config/model.conf`           | The model matrix: which AI model handles which tier, per CLI. [Model matrix](model-matrix.md) describes it.                                                                                                                                                                                                                                                | At installation. A greenfield project gets defaults, and the fitting walk-through helps you configure it.                                                                                                           |
| `.agent-factory/config/project-context.json` | A deterministic scan of the project's languages, frameworks, CI, linters, test runners, and documentation structure. The fitting uses it to confirm what the scan found.                                                                                                                                                                                   | Once, at installation. A greenfield project gets an empty scan with `fitting.status: "greenfield"`.                                                                                                                 |
| `docs/testing.yaml`                          | The `test_command` of the project.                                                                                                                                                                                                                                                                                                                         | When `init-factory` finds one clear test entry point, such as a `Makefile` test target, `pytest.ini`, or a `package.json` test script. With several candidates it asks you to choose. With none it creates no file. |
| `docs/agent-context.md`                      | The routing of agents to your project's knowledge. [What the agent context does](../agent-context/what-agent-context-does.md) explains it.                                                                                                                                                                                                                 | Not at installation. The `capture-context` skill creates it during the fitting.                                                                                                                                     |

The files under `.agent-factory/config/` are local configuration, not project source. They are git-ignored and belong to your machine.

## Everything init-factory installs

Git tracks only two of these entries: the hook block in `.pre-commit-config.yaml` and the block in `.gitignore`. The `.gitignore` block lists everything else, so git ignores it.

| What                 | Where                                                                                                                                                                 | Tracked? |
| -------------------- | --------------------------------------------------------------------------------------------------------------------------------------------------------------------- | -------- |
| Toolset copy         | `.agent-factory/factory/`                                                                                                                                             | No       |
| CLI symlinks         | `.claude/`, `.github/`, `.pi/`, `.codex/`, `.agents/` — pointing into `.agent-factory/factory/`                                                                       | No       |
| Git safety guardrail | `.claude/hooks/block-dangerous-git.sh`, `.github/hooks/`, `.pi/extensions/`, `.codex/hooks/`                                                                          | No       |
| Step guard hooks     | `.claude/hooks/step-guard.sh`, `.github/hooks/step-guard.*`, `.pi/extensions/step-guard.ts`, `.codex/hooks/step-guard.sh`                                             | No       |
| Freshness check      | `.claude/hooks/check-factory-freshness.sh`, `.github/hooks/`, `.pi/extensions/`, `.codex/hooks/` — auto-runs `update-factory` when `.agent-factory/factory/` is stale | No       |
| Usage capture hooks  | `.claude/hooks/capture-usage.sh` (Stop/SubagentStop), `.github/hooks/capture-*.sh`, `.pi/extensions/capture-usage.ts`, `.codex/hooks/capture-codex-usage.sh`          | No       |
| Orientation file     | `.claude/CLAUDE.md`, `.github/copilot-instructions.md`, `AGENTS.md` — prepends a marker block if the file exists                                                      | No       |
| Generated agents     | `.github/agents/*.md` (Copilot, with tools: frontmatter), `.codex/agents/*.toml` (Codex, native format)                                                               | No       |
| Hook config          | `.claude/settings.json` (hook entries), `.codex/hooks.json` (hook entries)                                                                                            | No       |
| Pre-commit hooks     | `.pre-commit-config.yaml` — `agent_factory_hook-*` block                                                                                                              | Yes      |
| Gitignore block      | `.gitignore` — `agent_factory related` section                                                                                                                        | Yes      |
| Project config       | `.agent-factory/config/project.json` (name + UUID), `.agent-factory/config/project-context.json` (scan results)                                                       | No       |
| Test regime          | `docs/testing.yaml` — `test_command` if a single unambiguous entrypoint is detected                                                                                   | No       |
| Usage runtime        | `.agent-factory/usage/runtime/` — hash-verified tokenizer venv                                                                                                        | No       |
| Usage lifecycle      | `.agent-factory/usage/control/` — registration fence and capture state                                                                                                | No       |
| Install manifest     | `.agent-factory/install.json`                                                                                                                                         | No       |
| Install checksums    | `.agent-factory/checksums.json` — per-file SHA-256 for modification detection by `update-factory`                                                                     | No       |

You can run `init-factory` again safely. When `.agent-factory/factory/` exists, it stays as it is. Run `.agent-factory/factory/scripts/update-factory` instead.
