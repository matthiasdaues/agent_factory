# Handoff: Monorepo Restructure & Documentation Gap Remediation

**Session date:** 2026-09-06
**Branch:** `dev`
**Latest commit:** `f5deffe` (docs: rewrite pre-commit hook comments for clarity)
**Repo:** `/home/matthiasdaues/Documents/datenschoenheit/agent_factory`

## What happened this session

Two threads of work, both uncommitted.

### Thread 1 — Monorepo-aware init/update scripts

Made `init-factory` and `update-factory` aware of the monorepo layout where
product source lives at `packages/factory/` (not `factory/`).

**Problem:** `./init-factory --update .` failed because `update-factory`
moved `factory/` aside, then tried to call `factory/scripts/init-factory` —
which no longer existed. Same issue in `init-factory` itself when called with
`--source` pointing at this repo.

**Fix (three files):**

- `packages/factory/scripts/init-factory` (line ~2260): checks
  `packages/factory/` before `factory/` when resolving source.
- `packages/factory/scripts/update-factory` (lines ~97, ~158): same
  monorepo-first resolution for both `_run_init()` and `source_factory`.
- `init-factory` (root convenience script): added `--update <target>` option
  that delegates to `update-factory`.

**Verified:** `./init-factory --update .` completes successfully. The
consumer hook block gets re-spliced from the template (with factory guards),
the dev hooks block is preserved, and `factory/` is refreshed from
`packages/factory/`.

### Thread 2 — Documentation gap audit

Traced the newcomer path (root README → factory README → factory guide) and
identified eight gaps where a newcomer encounters something undocumented.
Appended the full audit to `docs/proposals/context-aware-init-factory.md`
under "Documentation gaps — newcomer path audit (2026-09-06)".

Also added missing `context-lint` hook to the pre-commit template at
`packages/factory/config/pre-commit-config.yaml`.

## Uncommitted changes

| File                                             | What changed                                                      |
| ------------------------------------------------ | ----------------------------------------------------------------- |
| `init-factory`                                   | Added `--update` routing                                          |
| `packages/factory/scripts/init-factory`          | Monorepo-aware source resolution                                  |
| `packages/factory/scripts/update-factory`        | Monorepo-aware source + init resolution                           |
| `packages/factory/config/pre-commit-config.yaml` | Added `context-lint` hook                                         |
| `.pre-commit-config.yaml`                        | Consumer block re-spliced from template (factory guards restored) |
| `.gitignore`                                     | New skill symlinks from init-factory run                          |
| `docs/proposals/context-aware-init-factory.md`   | Eight documentation gaps appended                                 |
| `sys`                                            | Empty file deleted                                                |

## What the next session should do

Work through the eight documentation gaps one by one. The list is at the
bottom of `docs/proposals/context-aware-init-factory.md` § "Documentation
gaps — newcomer path audit (2026-09-06)". Each gap needs a fix in the
appropriate doc (factory README, factory guide, or both).

### The eight gaps

1. **Model matrix (`config/model.conf`)** — no doc explains what it is, the
   tier system, or the `cli.tier = model-id` format. Needs a section in the
   factory guide and a mention in the factory README.

2. **Tiers (economy/standard/strong)** — the concept behind the model
   matrix. Agents declare tiers in frontmatter (`tier: strong`). No
   user-facing definition exists. Tightly coupled with gap 1 — fix together.

3. **Stale ruff references in factory guide** — five mentions at lines 554,
   560, 574, 586, 687 of `packages/factory/docs/factory-guide.md` still
   describe ruff as a built-in hook. Ruff was removed in commit `3b83eaa`.

4. **`config/project.json`** — mentioned in reference table and usage
   capture section but never explained standalone.

5. **Factory directory layout** — no map of what's inside `factory/` after
   install.

6. **Factory README "How it works" section** — omits agent context, model
   matrix, config/. Needs updating.

7. **Agent context not mentioned in factory README** — root README mentions
   it, factory guide has a section, but factory README (the setup doc) never
   does.

8. **Agent context creation timing** — guide describes `docs/agent-context/`
   without saying it's created during onboarding, not at init time.

### Where to start

The session was about to work through gap 1 (model matrix / tiers) when
interrupted. The agent had already located the tier declarations: each agent
has `tier: economy|standard|strong` in its frontmatter.
`config/model.conf` maps `cli.tier = model-id`. The dispatch-contract
rulebook is referenced as the authoritative tier rubric but needs to be
verified — an `rg` for tier/economy/standard/strong there returned empty.

### Quality bar

"A junior gets it and a senior with a distinct dislike of marketing
hyperbole, adverbs, and adjectives would respect it." This applies to all
documentation written.

## Suggested skills

- **`commit`** — commit the uncommitted changes before starting new work.
- **`guided-tour`** — useful context for understanding the newcomer path
  these gaps affect.
- **`explain-concept`** — for drafting the model matrix / tier explanation
  at the right level.

## Key references

- Proposal with gap list: `docs/proposals/context-aware-init-factory.md`
- Factory guide (where most fixes go): `packages/factory/docs/factory-guide.md`
- Factory README: `packages/factory/README.md`
- Root README: `README.md`
- Model matrix: `packages/factory/config/model.conf`
- Pre-commit template: `packages/factory/config/pre-commit-config.yaml`
- Agent tier declarations: `packages/factory/agents/*.md` (frontmatter `tier:` field)
- Dispatch contract: `packages/factory/rulebooks/conventions/dispatch-contract.md`
- Session commits: `eb22486..f5deffe` on `dev`
