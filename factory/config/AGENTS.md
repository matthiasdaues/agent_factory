# Agent Factory — CLI Orientation

Canonical orientation content for any AI coding CLI working in a project that uses Agent Factory. Symlinked to each CLI's expected root filename at project-init time.

## Rules

- **MUST**: before ANY Skill/Agent call, check this project's own local skill/agent directory first. Exists locally → use it, ignore any global copy of the same name. No exceptions, no trusting tool default resolution. Local directory, by CLI:

  - Claude Code: `.claude/skills/<name>/SKILL.md`, `.claude/agents/<name>.md`
  - GitHub Copilot CLI: `.github/skills/<name>/SKILL.md`, `.github/agents/<name>.md`
  - Pi: `.pi/skills/<name>/SKILL.md`, `.pi/agents/<name>.md`
  - Codex: `.agents/skills/<name>/SKILL.md`, `.codex/agents/<name>.toml`

- **MUST (Pi only)**: Pi has no native subagent. To run a factory *agent* — not a skill — invoke the `run_agent` tool (registered by the `run-agent` extension), passing the agent name and the task. Do not read `.pi/agents/<name>.md` and act it out in the current session: `run_agent` spawns the agent in a separate Pi session, and that separation is what preserves author/reviewer independence. To run several file-disjoint agents in parallel, invoke `dispatch_wave` (registered by the `dispatch-wave` extension), which isolates each in its own git worktree and merges through `premerge-check`. Claude Code and GitHub Copilot CLI spawn subagents natively and need no such tools.

- **MUST (Codex only)**: Factory agents are generated native custom agents. Spawn `.codex/agents/<name>.toml` through Codex's subagent mechanism; do not read the canonical Markdown and act it out in the parent session. Separate native threads preserve author/reviewer independence. Use `.codex/playbooks`, `.codex/rulebooks`, and `.codex/scripts` for the Factory aliases.

- **MUST**: Read the local `INDEX.yaml` first (`.claude/INDEX.yaml` for Claude Code, `.github/INDEX.yaml` for GitHub Copilot CLI, `.pi/INDEX.yaml` for Pi, `.codex/INDEX.yaml` for Codex). All locally available agents, skills, and playbooks are referenced there.

- **MUST**: Machine-consumed gates, markers, dispatch records, and handoffs use full 40-character Git SHAs. Abbreviated SHAs are display-only.

- **MUST**: Before you answer the first prompt, greet the user and acknowledge that you have read and understood the local first rule.
