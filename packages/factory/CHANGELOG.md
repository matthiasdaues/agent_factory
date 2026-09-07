# Changelog

## 0.6.0 — 2026-09-07

Documentation release. Closes the gap between running `init-factory` and
starting your first playbook, and hardens the hooks and rulebook for
day-to-day use.

### Documentation

- **Onboarding bridge.** Getting Started now explains what `init-factory`
  put on disk — `project-context.json`, `model.conf`, `agent-context/` —
  so newcomers are not surprised when a playbook references them. Context
  added as a fifth vocabulary entry; INDEX.yaml positioned as a human
  reference, not just a machine lookup.
- **Newcomer tour expanded.** Tour steps now cover config artifacts and
  the fitting session, with greenfield model-matrix awareness in VIRGIL.
- **READMEs refreshed.** Root and `packages/factory/` READMEs updated
  for current structure.
- **Nine broken doc links repaired.** `orchestrator/` →
  `packages/orchestrator/`, `tests/orchestrator/` → `tests/factory/`,
  `spec/use_cases/` → `~archive/spec/use_cases/`, and one dead README
  anchor removed.

### Features

- **Factory-freshness check.** A new hook warns (never blocks) on the
  first tool call of each session when the installed `factory/` is out of
  sync with `packages/factory/`. Implemented for all CLIs: bash hook
  (Claude/Copilot/Codex), TypeScript extension (Pi), and Copilot hook
  config. `init-factory` stamps and `update-factory` refreshes the tree
  hash.

### Fixes

- **step-guard: no manifest, no restriction.** The empty-path rejection
  fired before checking whether a step manifest was loaded, blocking
  sessions without `.current-work/current-step.yml`. Reordered: no
  manifest means no restrictions. Adds a debug dump for path-extraction
  misses.
- **Codex skill resolution path.** The rulebook's INDEX.yaml resolution
  example said `.codex/skills/` but init-factory installs skills to
  `.agents/skills/`.

## 0.5.0 — 2026-09-07

First versioned release. Factory version is tracked in `factory/VERSION`
and recorded in the install manifest (`.agent-factory/factory-install.json`
→ `factory_version`).

### Fitting lifecycle

The factory now learns your project before it starts working. When
init-factory runs against an existing codebase, it scans for languages,
frameworks, package managers, CI, linters, test runners, and docs
structure. The results go into `config/project-context.json` with a
fitting state that tracks what has been confirmed.

- **Brownfield projects** get `fitting.status = "unfitted"`. The first
  session offers a guided fitting — a short walk-through to confirm the
  scan, populate agent context, configure the model matrix, and decide on
  hooks.
- **Greenfield projects** (no signals detected) get
  `fitting.status = "greenfield"` and skip the fitting entirely.
- Fitting progress persists across sessions. Stop any time; the next
  session picks up where you left off.

### Selective CLI wiring

`init-factory` now asks which CLIs you use and wires up only those. Pass
`--cli claude copilot` or choose interactively. Add a CLI later with
`init-factory --add copilot`; remove one with `init-factory --remove pi`.

### One-hop orientation

The CLI orientation file (`AGENTS.md` / `CLAUDE.md` /
`copilot-instructions.md`) is self-contained for the model's first turn.
It checks fitting state and presents the session menu without chaining to
a second file. Weak models that read only the orientation file still do
the right thing.

VIRGIL is demoted from mandatory session persona to optional enrichment.
Strong models that chain to `virgil.md` get richer guidance; weak models
skip it and still work.

### Model matrix

`config/model.conf` is now generated with only the installed CLIs'
stanzas, using `CONFIGURE-ME` placeholders instead of real model IDs. The
file includes a howto header with per-CLI model ID examples and validation
instructions. VIRGIL's fitting step 0 walks through configuration.

### Orientation non-interference

init-factory never overwrites an existing instruction file. Four cases:
no file → symlink; our symlink → skip; foreign symlink → leave it;
existing file → prepend a marker-fenced block. `remove-factory` reverses
all of them.

### Hooks

- `step-guard.sh` exits 0 gracefully when `factory/scripts/step-guard` is
  absent (fresh clone, partial install).
- Brownfield projects with an existing `.pre-commit-config.yaml` get no
  automatic hook merge — deferred to the fitting session.

### Documentation

- README rewritten: before/after value contrast, reversibility as
  first-class promise, fitting mention for brownfield.
- All eight newcomer-path doc gaps closed (model matrix, tiers, stale ruff
  refs, project.json, directory layout, factory README, agent context).
- Pre-commit hook comments rewritten for clarity.
- "Operator" → "user" across 127 files.
- Editorial pass over all 58 skills.
- Orientation architecture documented in the init-factory proposal.

### Monorepo

Product source lives under `packages/factory/`. The root `factory/` is
the installed copy (git-ignored), synced by `update-factory`. Root
`init-factory` is a thin wrapper.
