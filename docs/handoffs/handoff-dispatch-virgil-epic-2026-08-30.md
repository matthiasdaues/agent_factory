# Handoff: Dispatch VIRGIL Unified Session Agent Epic

**Date:** 2026-08-30
**From:** Planning / user briefing
**To:** implementation-agent (dispatcher)
**Branch:** dev
**Base SHA:** 20fdbaea20941e26086015110126f609a3ae7671

## Objective

Dispatch 13 stories (ST-0169 through ST-0181) comprising the VIRGIL Unified Session Agent epic. All stories are `status: pending` on the `dev` branch. The epic introduces VIRGIL as a unified session agent replacing chat-agent and kit-manager, with supporting skills and reference updates.

## Proposal

`docs/proposals/newcomer-tour-as-portable-skill.md` — full design rationale and scope.

## Backlog files

All story files live at `backlog/ST-NNNN.md` and contain complete acceptance criteria, implementation notes, and literary frame references. Developer agents must read their story file before implementing.

## Wave Structure

### Wave 1 — No dependencies, parallel (2 stories)

| Story   | Title                                        | Tier     | Model  | Deps | Outputs                         |
| ------- | -------------------------------------------- | -------- | ------ | ---- | ------------------------------- |
| ST-0169 | Merge beginner content into factory-guide.md | standard | sonnet | none | `factory/docs/factory-guide.md` |
| ST-0170 | Create VIRGIL agent definition               | standard | sonnet | none | `factory/agents/virgil.md`      |

### Wave 2 — Depends on Wave 1, all file-disjoint, parallel (9 stories)

| Story   | Title                                        | Tier    | Model | Deps    | Outputs                                      |
| ------- | -------------------------------------------- | ------- | ----- | ------- | -------------------------------------------- |
| ST-0171 | Create newcomer-tour skill                   | economy | haiku | ST-0169 | `factory/skills/newcomer-tour/SKILL.md`      |
| ST-0172 | Create explain-concept skill                 | economy | haiku | ST-0169 | `factory/skills/explain-concept/SKILL.md`    |
| ST-0173 | Update AGENTS.md references                  | economy | haiku | ST-0170 | `factory/config/AGENTS.md`                   |
| ST-0174 | Update guided-tour skill                     | economy | haiku | ST-0170 | `factory/skills/guided-tour/SKILL.md`        |
| ST-0175 | Replace beginner-intro.md with redirect stub | economy | haiku | ST-0169 | `docs/arc42/beginner-intro.md`               |
| ST-0176 | Update factory README link                   | economy | haiku | ST-0169 | `factory/README.md`                          |
| ST-0177 | Update draft-proposal skill refs             | economy | haiku | ST-0170 | `factory/skills/draft-proposal/SKILL.md`     |
| ST-0178 | Update detect-test-regime skill refs         | economy | haiku | ST-0170 | `factory/skills/detect-test-regime/SKILL.md` |
| ST-0181 | Create comic-relief skill                    | economy | haiku | ST-0170 | `factory/skills/comic-relief/SKILL.md`       |

### Wave 3 — Depends on Wave 2, serial (2 stories)

| Story   | Title                           | Tier    | Model | Deps                                        | Outputs                                                         |
| ------- | ------------------------------- | ------- | ----- | ------------------------------------------- | --------------------------------------------------------------- |
| ST-0179 | Retire chat-agent + kit-manager | economy | haiku | ST-0170, ST-0173, ST-0174, ST-0177, ST-0178 | `factory/agents/chat-agent.md`, `factory/agents/kit-manager.md` |
| ST-0180 | Update INDEX.yaml               | economy | haiku | ST-0170, ST-0171, ST-0172, ST-0179, ST-0181 | `factory/INDEX.yaml`                                            |

**Wave 3 ordering:** ST-0179 before ST-0180 (ST-0180 depends on ST-0179). Both can use haiku.

## Tier-to-Model Mapping (Claude Code)

- `economy` → `haiku`
- `standard` → `sonnet`
- `strong` → `opus`

## Key Implementation Context

### ST-0169 (factory-guide.md)

- Source content: `docs/arc42/beginner-intro.md`
- Add "Getting Started" section before existing "Agents" section
- Remove orchestrator refs, `orchestrator/README.md` links, `docs/arc42/concepts.md` links
- Rewrite internal links to `factory/`-relative paths
- Replace opening line with direct lead-in
- Add seam: "Everything below is reference material. You don't need it yet."
- Manual mode only — no "Graduating to automatic mode" section

### ST-0170 (VIRGIL definition)

- Model on existing `factory/agents/chat-agent.md` structure
- Thin agent: role statement, skill table, boundaries, triggers
- Absorb kit-manager workflow (assess → fill → validate) as procedural guidance
- Literary DNA section with three core archetypes (Virgil/Dante, Vimes/Pratchett, Jeeves/Wodehouse) and two secondary frames (Sam Gamgee, Radar O'Reilly)
- Full acceptance criteria in `backlog/ST-0170.md`

### ST-0173 (AGENTS.md)

- Five references to update: option A (line 45), option B7 (line 80), option D (line 104), adopt-pattern routing (line 108), Codex example (line 22)
- All chat-agent/kit-manager → VIRGIL

### ST-0181 (comic-relief)

- Humor quadrangle: Dilbert × XKCD × South Park × Hornblower
- Context-aware, never mean, never in generated artifacts

### ST-0179 (retire agents)

- DELETE `factory/agents/chat-agent.md` and `factory/agents/kit-manager.md`
- Only after all references are updated (Wave 3)

### ST-0180 (INDEX.yaml)

- Register virgil agent + newcomer-tour, explain-concept, comic-relief skills
- Remove chat-agent and kit-manager entries

## File Overlap Analysis

All Wave 2 stories are file-disjoint — safe for full parallel dispatch. Wave 3 stories share no output files with each other but ST-0180 depends on ST-0179 (INDEX.yaml needs agent deletions complete first).

## Pre-existing Conditions

- `factory/config/AGENTS.md` shows as modified in working tree (git status `M`). Check whether drift is intentional before dispatching ST-0173.
- Four untracked handoff files exist in `docs/handoffs/` — unrelated to this epic.

## Suggested Skills

- **`handoff`** — at completion, write the implementation-complete handoff for reconciliation-agent + QA.
- **`run-step`** — if the dispatcher needs to invoke individual dispatch script subcommands.
- **`spec-feedback`** — developer agents use this at story completion per the developer-agent workflow.
- **`validate`** — for charter validation if any story touches charter-adjacent content.

## Next Action

Invoke the `implementation-agent` dispatcher with:

- Mode: `autonomous`
- Stories: ST-0169 through ST-0181
- Base branch: `dev`
- Base SHA: `20fdbaea20941e26086015110126f609a3ae7671`
- Wave plan as documented above

The dispatcher should call `factory/scripts/dispatch init` first, then proceed through waves 1–3 per the implementation-agent protocol.
