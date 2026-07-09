---
id: INTEG-0001
source: grilling
severity: major
category: defect
artifact: README.md#setting-up-from-scratch
status: open
---

# No universal auto-loaded instruction file across the five target CLIs

**What is wrong:** Agent Factory targets five coding CLIs (Copilot CLI, Claude Code, Gemini CLI, Codex/OpenCode, Cursor — `README.md`'s "Exemplary AI coding CLIs" table). The repo needs one auto-loaded, repo-root instruction file to carry a hard rule (prepend `agent_factory-` to any skill/agent name from this repo before invoking it, to avoid colliding with a user's pre-existing same-named global skills/agents — collision reproduced empirically this session: invoking `grill-with-docs` silently resolved to the user's global `~/.claude/skills/grill-with-docs` instead of the repo's own). No single filename is read natively by all five CLIs. `AGENTS.md` covers three (Copilot CLI, Codex, and Gemini CLI only with a non-default `settings.json` override); Claude Code reads `CLAUDE.md` exclusively and does not fall back to `AGENTS.md`; Cursor reads neither — it requires `.cursor/rules/*.mdc` files with YAML frontmatter declaring an activation mode, which a plain symlink cannot satisfy.

**Fix:** Keep one canonical file at `config/AGENTS.md`. At CLI-selection init time, symlink the CLI's native root filename to it: `CLAUDE.md -> config/AGENTS.md` and `GEMINI.md -> config/AGENTS.md` (direct symlink, same mechanism already used for skill installation, cheaper than a `settings.json` edit); `AGENTS.md` itself at the root covers Copilot CLI and Codex natively. Cursor is the exception — it needs a distinct `.cursor/rules/agent-factory.mdc` file carrying real YAML frontmatter (activation mode: Always Apply), not a symlink, since `.mdc` is a different format from plain Markdown. Whether to build that Cursor adapter now or flag Cursor as unsupported for the first cut is still open — not resolved in this session.

## Research

| CLI | Native instruction file | Reads `AGENTS.md`? | Root-level integration |
| --- | --- | --- | --- |
| Copilot CLI | `AGENTS.md` (primary) + `.github/copilot-instructions.md` (secondary) | Native | None needed — `AGENTS.md` covers it |
| Codex / OpenCode | `AGENTS.md` | Native — one of the original drivers of the cross-vendor AGENTS.md standard | None needed |
| Claude Code | `CLAUDE.md` (+ `CLAUDE.local.md`) | No — docs state explicitly "Claude Code reads CLAUDE.md, not AGENTS.md" | Symlink `CLAUDE.md -> config/AGENTS.md` |
| Gemini CLI | `GEMINI.md`, loaded hierarchically (`~/.gemini/`, project root, subdirs) | Only via non-default `context.fileName` override in `settings.json` | Symlink `GEMINI.md -> config/AGENTS.md` (simpler than a settings.json edit) |
| Cursor | `.cursor/rules/*.mdc` (current convention; `.cursorrules` deprecated but still honored) | No | Needs a real `.mdc` file with frontmatter — plain symlink insufficient |

Sources: [GitHub Docs — Copilot CLI custom instructions](https://docs.github.com/en/copilot/how-tos/copilot-cli/customize-copilot/add-custom-instructions); [OpenAI Developers — Codex AGENTS.md guide](https://developers.openai.com/codex/guides/agents-md); [agents.md](https://agents.md/); [Claude Code Docs — Memory](https://code.claude.com/docs/en/memory); [Gemini CLI Docs — GEMINI.md files](https://geminicli.com/docs/cli/gemini-md/); [Cursor Docs — Rules](https://cursor.com/docs/rules).
