# VFDE AI Copilot Marketplace — Integration Assessment

**Date:** 2026-09-17
**Type:** Exploration
**Subject:** `../vfde-ai-copilot` — feasibility and value of factory integration

## What It Is

A GitHub Copilot plugin marketplace for VFDE (Vodafone DE) projects. Four plugins,
each packaging agents and skills in the Copilot Chat convention
(`.agent.md` + `SKILL.md` files, invoked via `@agent-name` in the IDE):

| Plugin                         | What it does                                                                                                                  |
| ------------------------------ | ----------------------------------------------------------------------------------------------------------------------------- |
| `vfde-git-commit-manager`      | Conventional Commits assistant with ticket detection, pre-commit review                                                       |
| `unit-test-agent-plugin`       | Test generation agent, delegates to language-specific skills (Python/Flask so far)                                            |
| `vfde-code-reviewer`           | Anti-pattern, security, performance review across 5 stacks (Java/Spring, Angular, Next.js, Node/Express/Prisma, Python/Flask) |
| `vfde-marketplace-contributor` | Onboarding/validation tooling for contributing to the marketplace itself                                                      |

No application code. Pure agent/skill definitions in markdown, plus plugin metadata
(`plugin.yaml`, `plugin.json`), CI workflows, and templates.

## Shape and Conventions

- **Agent format:** YAML frontmatter (`name`, `description`, `argument-hint`, `plugin`,
  `version`) followed by a markdown system prompt with responsibilities, rules,
  workflow steps, output format, safety boundaries.
- **Skill format:** `SKILL.md` — narrower, language-specific rule sets loaded by the
  parent agent on demand.
- **Plugin metadata:** `plugin.yaml` declares agents, skills, compatibility, config
  options, dependencies. `plugin.json` is the machine-readable marketplace entry.
- **Distribution:** `copilot plugin install <name>@vfde-ai-copilot` CLI, installs
  into `.github/agents/` (gitignored in consuming repos).
- **Platform:** GitHub Copilot Chat only. No Claude Code, no MCP, no CLI hooks.

## Overlap with Factory Capabilities

| Marketplace plugin             | Factory equivalent                        | Notes                                                                                                                         |
| ------------------------------ | ----------------------------------------- | ----------------------------------------------------------------------------------------------------------------------------- |
| `vfde-code-reviewer`           | `code-review-agent`, `/code-review` skill | Factory version is diff-only + Fagan; marketplace version adds architecture/clean-code categories and 5 stack-specific skills |
| `unit-test-agent-plugin`       | `developer-agent` (TDD loop)              | Different approach — marketplace generates tests for existing code; factory writes tests first                                |
| `vfde-git-commit-manager`      | `commit` skill, git-guardrails            | Factory uses hooks + guardrails; marketplace uses conversational commit assistant                                             |
| `vfde-marketplace-contributor` | No equivalent                             | Self-referential — only relevant for contributing to the marketplace repo                                                     |

## Integration Value

**Low-to-medium for direct consumption.** The plugins target Copilot Chat's
`@agent` invocation model, which the factory doesn't use. The agent definitions are
markdown system prompts, not executable — they rely on Copilot Chat's orchestration
to route, load skills, and produce output.

**Medium-to-high as reference material.** The stack-specific review skills
(Java/Spring, Angular, Node/Express/Prisma, Next.js/React, Python/Flask) encode
concrete anti-pattern catalogs and review checklists that the factory's code-review
and QA agents could absorb. The review categories (security, correctness, performance,
architecture, clean code, API design) are well-structured and severity-tiered.

**Possible integration paths:**

1. **Extract review knowledge.** Pull the language-specific skill content into factory
   skill definitions that the code-review-agent and qa-agent can load based on
   project fingerprint. Requires format adaptation (Copilot SKILL.md → factory skill).

2. **Reference-only.** Point factory agents at the raw skill files when reviewing
   code in those stacks. No format conversion, but agents need to know the files
   exist and when to consult them.

3. **Cross-pollinate conventions.** The marketplace's plugin.yaml schema
   (agents, skills, compatibility, config, tags) is a simpler variant of what the
   factory already does with INDEX.yaml + agent definitions. Not directly useful,
   but confirms the pattern.

## Key Differences from Factory Model

- **No TDD loop.** Marketplace generates tests after the fact; factory writes tests
  first as part of implementation.
- **No lifecycle integration.** Marketplace plugins are point-of-use tools (invoke
  in chat); factory agents participate in a governed workflow
  (spec → plan → implement → QA → reconcile).
- **No isolation boundaries.** Marketplace agents run in the user's chat session;
  factory enforces reviewer ≠ author separation.
- **Copilot-only distribution.** No path to run these outside GitHub Copilot Chat
  without rewriting the orchestration layer.

## Reverse-Engineering Path: Copilot → Factory Import

The formats are structurally equivalent — both are markdown with YAML frontmatter.
A mechanical converter is feasible:

1. Read `plugin.yaml` → discover agents, skills, compatibility metadata.
2. Read each `.agent.md` / `SKILL.md` → extract frontmatter + prompt body.
3. Map frontmatter fields (`name`, `description`, `version`, `argument-hint` →
   factory equivalents: `model`, `tools`, `isolation`).
4. Preserve rule content verbatim (categories, severity tiers, examples are
   format-agnostic prose).
5. Add factory routing metadata: the `plugin.yaml` compatibility block
   (`java: ">=17"`, `node: ">=18"`) maps to the factory's project fingerprint,
   giving the activation key for when-to-load.
6. Register in INDEX.yaml.

This is the inverse of exporting factory skills to Copilot format — same bridge,
opposite direction. A factory script (`import-copilot-plugin`) could automate the
conversion. Export back to Copilot format is equally mechanical for upstream
contribution.

## Recommendation

Don't add as submodule — the consumption model doesn't fit. Instead:

1. **Build an import converter** (`import-copilot-plugin`) that transforms Copilot
   agent/skill definitions into factory format, preserving the review knowledge and
   mapping compatibility metadata to fingerprint-based routing.
2. **Start with `vfde-code-reviewer`** — five stack-specific review skills with
   concrete anti-pattern catalogs, already severity-tiered. Highest value, cleanest
   test case for the converter.
3. **Treat as bidirectional bridge** — changes to imported skills can be exported back
   to Copilot format for upstream contribution.
