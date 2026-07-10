# Agent Factory — CLI Orientation

Canonical orientation content for any AI coding CLI working in a project that uses Agent Factory. Symlinked to this CLI's expected root filename (`CLAUDE.md`, or read natively as `AGENTS.md`) at project-init time.

## Rules

- **MUST**: before ANY Skill/Agent call, check this project's own local skill/agent directory first. Exists locally → use it, ignore any global copy of the same name. No exceptions, no trusting tool default resolution. Local directory, by CLI:

  - Claude Code: `.claude/skills/<name>/SKILL.md`, `.claude/agents/<name>.md`
  - GitHub Copilot CLI: `.github/skills/<name>/SKILL.md`, `.github/agents/<name>.md`

- **MUST**: Read the local `INDEX.md` first, same directory as above (`.claude/INDEX.md` for Claude Code, `.github/INDEX.md` for GitHub Copilot CLI). All locally available skills and agents are referenced there.

- **MUST**: Before you answer the first prompt, greet the user and acknowledge that you have read and understood the local first rule.
