---
id: RECON-0016
source: reconcile-spec
severity: minor
category: defect
artifact: docs/spec/supplementary_specs/entity-model.md#L106
status: resolved
traces: [ADR-0005]
---

# Entity-model `MODEL_MATRIX_ENTRY.cli` lists `claude | copilot`, but `model.conf` rows are `copilot | codex | pi`

**What is wrong:** The `MODEL_MATRIX_ENTRY` entity in
`docs/spec/supplementary_specs/entity-model.md` annotates its `cli`
column as `string cli "claude | copilot"`. That vocabulary does not match
`config/model.conf` `[facts]`, which keys its tier rows as `copilot.*`,
`codex.*`, and `pi.*` — there is no `claude.*` row, and `codex` and `pi`
are absent from the entity's enum. The note directly below it already
states the lookup rule (`trigger` resolves an agent's dispatch model by
looking up `<cli>.<tier>` in `config/model.conf`), so the entity's
enumerated `cli` values should be exactly the row keys `model.conf`
exposes.

The `pi.*` portion of this drift pre-dated this delta; the `1bf179b`
commit that added `codex.*` tier rows to `model.conf` extended the gap
and makes the entity model describe the code-as-built incorrectly for two
of the three configured CLIs. The canonical four-CLI vocabulary
(Claude Code, GitHub Copilot CLI, Codex, Pi) was fixed across the
glossary, arc42, and ADRs in RECON-0013; this entity annotation was not
reached by that pass.

**Fix:** Update `MODEL_MATRIX_ENTRY.cli` in
`docs/spec/supplementary_specs/entity-model.md` from
`"claude | copilot"` to `"copilot | codex | pi"` to match the `model.conf`
`[facts]` row keys. If the intent is to keep the entity runtime-agnostic
rather than config-key-literal, annotate the column as
`"copilot | codex | pi (model.conf row keys)"` and add a one-line note
that Claude Code resolves its model outside `model.conf`. No code change
is required.
