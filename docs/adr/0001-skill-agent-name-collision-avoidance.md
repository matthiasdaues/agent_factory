---
id: 0001
status: accepted
evaluation: pugh-matrix
---

# Skill/Agent Name-Collision Avoidance

## Context

Agent Factory ships its own `agents/` and `skills/` directories, meant to be installed into a user's existing coding-CLI setup across five target CLIs (Copilot CLI, Claude Code, Gemini CLI, Codex/OpenCode, Cursor — `README.md`'s "Exemplary AI coding CLIs" table).

Empirically discovered this session: invoking this repo's own `grill-with-docs` skill silently resolved to the user's pre-existing global `~/.claude/skills/grill-with-docs` (a different, same-named skill from mattpocock/skills) instead of this repo's own copy. Claude Code's project-vs-user skill-name precedence is undocumented; observed behavior favored the global scope. The same failure mode applies to agents (subagent-type resolution) and to internal cross-references between this repo's own skills — e.g. `grill-with-docs` invoking `grilling` by bare name.

Needed: a way for Agent Factory's agents/skills to be invoked reliably and unambiguously regardless of what is already installed in a user's global CLI configuration, without depending on any single CLI's proprietary namespacing feature — only Claude Code's plugin system offers real platform-guaranteed namespacing, and the repo targets five CLIs.

## Decision

Adopt a universal (CLI-agnostic) name-collision-avoidance mechanism, chosen via Pugh Matrix over four alternatives:

| Criterion (weight)                                  | E — Do nothing (baseline) | B — CLI-native plugin packaging | C — Selective renaming | D — Copy-and-rewrite install | A — Universal prefix + symlink + AGENTS.md rule (chosen) |
| --------------------------------------------------- | ------------------------- | ------------------------------- | ---------------------- | ---------------------------- | -------------------------------------------------------- |
| CLI portability (3)                                 | 0                         | +1                              | +2                     | +2                           | +2                                                       |
| Collision robustness / future-proof (3)             | 0                         | +1                              | 0                      | +2                           | +2                                                       |
| Invocation reliability (2)                          | 0                         | +1                              | +1                     | +2                           | +1                                                       |
| Maintainability / no drift (2)                      | 0                         | +1                              | -1                     | -1                           | +1                                                       |
| Implementation cost (1, lower-effort scores higher) | 0                         | +1                              | +1                     | -1                           | -1                                                       |
| **Weighted total**                                  | **0**                     | **11**                          | **7**                  | **13**                       | **15**                                                   |

D (copy-and-rewrite) scores close to A and beats it on reliability (fully deterministic, no reliance on the model following a prose rule at every invocation) — the gap is carried by maintainability (symlinks give a single source of truth; copies drift from the repo over time). A small weight shift (maintainability 2→1, reliability 2→3) would flip the result toward D; this was a genuine, closely argued trade-off, not a lopsided call. B (plugin packaging) caps low on every criterion because it only covers 1 of 5 CLIs. C (selective renaming) loses hardest on robustness (0) — it fixes today's known collisions but guarantees nothing against a collision introduced by a skill the user installs next month.

Composed of three parts:

1. **Blanket hardcoded prefix.** Every skill/agent in Agent Factory is invoked with a hardcoded `agent_factory-` prefix (e.g. `agent_factory-grill-with-docs`) — applied uniformly, not selectively, since selective renaming leaves the repo exposed to any future same-named skill the user installs later. The prefix value itself was initially designed as user-configurable (a `~/.agents/agent-factory.env` file with an `AGENT_FACTORY_PREFIX` variable), then retracted mid-session in favor of a hardcoded literal — trading configurability for zero indirection: nothing to look up, nothing to default, one less step that can silently fail.
2. **Install by symlink, not copy.** `~/.claude/skills/agent_factory-<name> -> <repo>/skills/<name>` — mirrors the working precedent already in place for mattpocock's own skill distribution (`~/.claude/skills/<name> -> ~/.agents/skills/<name>`). Canonical source stays single, in the repo; nothing is duplicated into the target CLI's own config directory.
3. **Hard rule for internal cross-references.** Symlinked content can't fork per-install, so internal cross-references between skills/agents (one invoking another by name) cannot be statically rewritten with the prefix baked in. Instead, a hard rule lives in an auto-loaded orientation file — canonical copy at `config/AGENTS.md`, symlinked to the CLI-appropriate root filename at init. `CLAUDE.md` and `GEMINI.md` get a direct symlink to it; native `AGENTS.md` covers Copilot CLI and Codex without any extra step; Cursor is the one exception, needing a structurally different `.cursor/rules/*.mdc` file with real YAML frontmatter, tracked separately ([T-0001](../spec/todo.md#t-0001-cursor-mdc-adapter-for-configagentsmd), [INTEG-0001](../findings/INTEG-0001.md#no-universal-auto-loaded-instruction-file-across-the-five-target-clis)). The rule: prepend `agent_factory-` to any skill/agent name from this repo before invoking it.

## Consequences

Easier:

- New skills/agents added to the repo automatically inherit collision-safety — no per-file changes required, no lint gate needed to catch missed cross-references.
- Zero duplication of skill/agent content: one source of truth, no drift between the repo and any installed copy.
- Works identically across Copilot CLI, Codex, Gemini CLI, and (via symlink) Claude Code, without depending on any CLI-specific namespace feature.

Harder:

- Invocation correctness depends on the model faithfully reading and following the `AGENTS.md` hard rule every session — not deterministic the way a platform-level namespace (e.g. a genuine Claude Code plugin) would be. A forgotten lookup silently invokes the wrong same-named skill instead of erroring.
- Cursor has no working mechanism yet — `.cursor/rules/*.mdc` needs a structurally different, non-symlink adapter. Open, tracked in [T-0001](../spec/todo.md#t-0001-cursor-mdc-adapter-for-configagentsmd).
- The `agent_factory-` prefix mixes underscore with the rest of the repo's kebab-case naming convention (e.g. `agent_factory-grill-with-docs`) — cosmetic, flagged, not blocking.
