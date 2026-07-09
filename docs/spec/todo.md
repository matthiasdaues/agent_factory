# Todo

## T-0001 — Cursor `.mdc` adapter for `config/AGENTS.md`

- status: open
- source: grilling
- traces: INTEG-0001

Cursor doesn't read `AGENTS.md` and can't consume a plain symlink to it — it needs a `.cursor/rules/agent-factory.mdc` file with real YAML frontmatter declaring an activation mode (Always Apply) before it auto-loads. Every other target CLI (Copilot CLI, Codex, Claude Code, Gemini CLI) resolves via a direct symlink to `config/AGENTS.md`; Cursor is a structurally different mechanism and was parked rather than bundled with the symlink-based fix. Resolve by building the `.mdc` wrapper (frontmatter + a reference to or copy of `config/AGENTS.md`'s content).
