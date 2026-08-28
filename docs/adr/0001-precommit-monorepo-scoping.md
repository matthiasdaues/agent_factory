---
id: 0001
status: accepted
evaluation: none
---

> **Addendum (2026-08-28):** The orchestrator-scoped hooks described here were removed in dd4b964. The main hooks now cover all files without `exclude: ^orchestrator/` carve-outs. This ADR is retained as a historical record.

# Pre-commit monorepo scoping: one root config, namespaced and scoped hooks

## Context

This repository is a monorepo hosting several independently-tooled
subprojects under one root: `factory/` (the agent-factory scripts and
skills), `orchestrator/` (its own Python project with its own dev-tool
versions), and a future `factory_api/`. Each subproject wants its own
lint/format/test hooks running at commit time, pinned to its own tool
versions and scoped to its own paths.

`pre-commit` auto-discovers exactly one top-level `.pre-commit-config.yaml`
per repository — it does not walk into subdirectories looking for
additional configs. A per-subproject discovered config (e.g.
`orchestrator/.pre-commit-config.yaml` sitting next to a separate root
config) therefore cannot coexist: only the root file is ever picked up by
`pre-commit run`, `pre-commit install`, or the CI invocation, and any
subproject-local config silently never runs. This has already surfaced
once — orchestrator's own ST-0067
had to fold its dev-scoped hooks into the shared root file for exactly this
reason.

That fold is not an orchestrator-specific fix. It is the general shape
every subproject under this root must follow, now and for `factory_api/`
when it lands: one discovered config, many scoped hook sets. Recording it
only in orchestrator's own ADR log would misfile a whole-repo constraint as
a single-project one — this decision needs to be visible to every
subproject that joins the monorepo later, hence a root-level ADR sequence
(`docs/adr/`), separate from `orchestrator/docs/adr/`'s own 0001-0019.

This decision generalizes
orchestrator/docs/adr/0003-pre-commit-as-gate-bus.md (no longer present),
which decided `pre-commit` as the deterministic gate bus for a single
project (orchestrator). That decision still holds for *why* pre-commit is
the gate; this ADR answers the orthogonal, whole-repo question of how
multiple subprojects' hooks coexist under pre-commit's single-config
discovery once more than one subproject needs the gate.

## Decision

Use **one shared root `.pre-commit-config.yaml`**. No subproject keeps or
relies on its own discovered `.pre-commit-config.yaml`. Instead, each
subproject's hooks live as entries in the root file, distinguished by two
conventions:

- **Namespaced hook ids** — a subproject suffix on the id, e.g.
  `mdformat-orchestrator`, `ruff-check-orchestrator`,
  `ruff-format-orchestrator`, `arch-lint-orchestrator`,
  `backlog-lint-orchestrator`, `matrix-lint-orchestrator`,
  `statemachine-lint-orchestrator`, `spec-lint-orchestrator`. This keeps a
  subproject's hooks readable as a group and prevents id collisions with
  another subproject's hook of the same underlying tool (e.g. its own
  `ruff-check`).
- **Path scoping instead of directory discovery** — each namespaced hook
  carries `files:` (and `exclude:` where needed) regex pinning it to its
  own subproject's tree, e.g. `files: ^orchestrator/`, or a tighter
  existing pattern re-prefixed the same way (e.g.
  `^orchestrator/docs/spec/` for `spec-lint-orchestrator`). Generic,
  factory-level hooks that would otherwise double-touch a subproject's
  files with the wrong (unpinned) tool version gain the mirroring
  `exclude:` — e.g. root `mdformat`/`ruff-check`/`ruff-format` gain
  `exclude: ^orchestrator/` once orchestrator's own namespaced equivalents
  are in place.

This is what ST-0067 executes concretely for orchestrator: the root file
stops being a symlink and becomes a real, merged file carrying both the
generic factory hooks (excluding `^orchestrator/`) and the seven
`-orchestrator`-suffixed, `^orchestrator/`-scoped hooks above, invoking
`factory/scripts/<name>` rather than a bare `scripts/<name>`. The same
namespacing + scoping shape is what `factory_api/` (or any later
subproject) is expected to reproduce when it needs its own hooks: pick its
own suffix (e.g. `-factory-api`), scope with `files: ^factory_api/`, append
to the same root list.

### `merge-precommit-config` as the two-way splicing mechanism

`factory/scripts/merge-precommit-config` already exists and is documented
(README.md) for one direction of this problem: when `init-factory` runs
against a project that already has a real, non-symlinked
`.pre-commit-config.yaml`, it hands off to this script to splice Agent
Factory's own hook block into that file's `repos:` list, leaving the
project's existing hooks untouched. It works by finding the `repos:`
block-style list, checking the existing items' indent matches the
template's, and appending the template's `- repo: local` block verbatim —
deliberately not a general YAML merger (ADR-0006's zero-dependency
approach), so it aborts rather than guesses when the target's shape is
unfamiliar.

This decision generalizes that mechanism to the **other** direction as
well: a subproject that needs its own hooks in the shared root config
(orchestrator today, `factory_api/` tomorrow) is expected to keep its hook
set as its own `*/pre-commit-config.yaml` template — e.g.
`orchestrator/pre-commit-config.yaml` — and use the same
`merge-precommit-config --target .pre-commit-config.yaml --template orchestrator/pre-commit-config.yaml` splice to fold it into the root file,
rather than hand-editing the root list or maintaining a second discovered
config. The script does not care which side is "factory's" and which is
"the project's" — it only understands *a template block spliced into a
target's `repos:` list* — so the same tool serves both: factory-into-project
(its current, documented use) and subproject-into-root (this decision's
new use). No second script is needed.

## Consequences

**Positive**

- A single discovered config means `pre-commit run --all-files`, `pre-commit install`, and CI all see the complete, real hook set for every
  subproject — no silently-skipped subproject config.
- Namespacing + path scoping keeps each subproject's hooks independently
  pinned (own tool versions, own invocation prefix) and independently
  legible in the merged file, without one subproject's hook touching
  another's files.
- `factory_api/` (or any future subproject) has a known, reusable pattern
  to follow — pick a suffix, scope with `files:`, splice with
  `merge-precommit-config` — rather than re-deriving the shape from
  scratch.
- Reuses one existing, already-tested splicing script for both merge
  directions instead of building a second bespoke merge path.

**Negative / risks**

- The root file grows linearly with the number of subprojects; a large
  monorepo could eventually make it unwieldy to read end-to-end (mitigated
  by the namespacing convention keeping each subproject's block visually
  grouped).
- `merge-precommit-config` only understands one shape (`repos:` as a
  block-style list, 2-space item indent) — a subproject template or the
  root file drifting from that shape falls back to a manual merge. This is
  an accepted limitation carried over from the script's existing,
  documented behavior, not a new risk introduced here.
- Adding a subproject's hooks is now two edits by convention (its own
  `*/pre-commit-config.yaml` template, plus the splice into root) rather
  than one; this is the deliberate trade-off for keeping each subproject's
  hook set independently owned and reviewable before it lands in the
  shared file.
