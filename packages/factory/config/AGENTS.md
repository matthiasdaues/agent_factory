# Agent Factory — CLI Orientation

Read and follow `.agent-factory/factory/rulebooks/rules.md` in full — every MUST and MUST NOT is binding for the entire session. If the file is missing or unreadable, stop and tell the user.

## CLI detection

Determine which CLI you are running in and read the matching orientation file. The orientation file contains your CLI-specific capabilities, tools, and session-start procedure.

| CLI            | INDEX.yaml           | Orientation file                                  |
| -------------- | -------------------- | ------------------------------------------------- |
| Claude Code    | `.claude/INDEX.yaml` | `.agent-factory/factory/config/AGENTS.claude.md`  |
| GitHub Copilot | `.github/INDEX.yaml` | `.agent-factory/factory/config/AGENTS.copilot.md` |
| Stackblitz Pi  | `.pi/INDEX.yaml`     | `.agent-factory/factory/config/AGENTS.pi.md`      |
| OpenAI Codex   | `.codex/INDEX.yaml`  | `.agent-factory/factory/config/AGENTS.codex.md`   |

Read the orientation file for your CLI now and follow its instructions instead of this file.
