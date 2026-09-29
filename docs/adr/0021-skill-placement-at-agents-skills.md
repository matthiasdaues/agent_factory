---
id: 0021
status: proposed
evaluation: pugh-matrix
---

# Skill placement at `.agents/skills/`

## Context

OpenCode discovers skills at `.agents/skills/` as a native path. Factory skills are currently placed at `.claude/skills/` for Claude Code and referenced from INDEX.yaml for other CLIs. When OpenCode is added as a CLI target, the installer must decide where to place skills so that OpenCode sessions discover them without additional configuration.

Three options exist:

- **`.agents/skills/`** -- OpenCode's native discovery path, independent of any CLI-specific directory.
- **`.opencode/skills/`** -- under the CLI-specific directory, following the pattern of `.opencode/agents/`.
- **`.claude/skills/`** -- rely on OpenCode's Claude Code compatibility mode, which reads `.claude/` paths when `OPENCODE_DISABLE_CLAUDE_CODE` is not set.

## Decision

Place skills at `.agents/skills/` for OpenCode discovery.

| Criterion                           | Weight | `.agents/skills/` (baseline) | `.opencode/skills/` | `.claude/skills/` (compat) |
| ----------------------------------- | ------ | ---------------------------- | ------------------- | -------------------------- |
| Native discovery (QS-1 flexibility) | 3      | 0                            | -1                  | 0                          |
| CLI independence                    | 2      | 0                            | +1                  | -1                         |
| Compatibility mode dependency       | 2      | 0                            | 0                   | -1                         |
| CLI coexistence (QS-8)              | 2      | 0                            | 0                   | -1                         |
| Simplicity / YAGNI                  | 1      | 0                            | 0                   | +1                         |
| **Weighted total**                  |        | **0**                        | **-1**              | **-5**                     |

**Native discovery (weight 3, `.opencode/skills/` scores -1):** OpenCode looks at `.agents/skills/` for skill discovery. Placing skills at `.opencode/skills/` requires additional configuration or a symlink to make them discoverable -- an extra step that contradicts the principle of working with the tool's native paths.

**CLI independence (weight 2, `.opencode/skills/` scores +1, `.claude/skills/` scores -1):** `.opencode/skills/` is clearly namespaced to one CLI. `.claude/skills/` couples OpenCode to Claude Code's directory structure. `.agents/skills/` is CLI-neutral by design -- the directory name contains no CLI reference.

**Compatibility mode dependency (weight 2, `.claude/skills/` scores -1):** The `.claude/skills/` path works only when `OPENCODE_DISABLE_CLAUDE_CODE` is not set. If a project disables compatibility mode (a supported configuration), skill discovery breaks silently.

**CLI coexistence (weight 2, `.claude/skills/` scores -1):** Placing OpenCode skills in `.claude/` blurs the ownership boundary between CLIs. When both Claude Code and OpenCode are installed, it becomes unclear which CLI "owns" the skills under `.claude/skills/`.

**Simplicity (weight 1, `.claude/skills/` scores +1):** Reusing `.claude/skills/` avoids creating a new directory. This advantage is minor -- one `mkdir` during installation.

The `.claude/skills/` option loses decisively (-5). The `.opencode/skills/` option is close to baseline (-1) but loses on the highest-weighted criterion (native discovery). No weight adjustment within the stated ranges flips the baseline result.

## Consequences

- `init-factory` places OpenCode skills under `.agents/skills/` and records the paths in `install.json`.
- `.agents/skills/` is a shared, CLI-neutral directory. If other CLIs adopt this path in the future, the skills are already in place.
- Claude Code continues to discover its skills at `.claude/skills/`. The two paths are independent; no symlinks or compatibility-mode assumptions connect them.
- `remove-factory` removes Factory-owned entries from `.agents/skills/` using the install manifest, leaving user-owned skills intact.
- `.opencode/INDEX.yaml` references the `.agents/skills/` paths for skill listings.
