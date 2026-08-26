---
name: scope-map-migration
description: Backfill docs/spec/scope-map.md from existing derive-spec artifacts before the first derive-feature run.
category: requirements
disable-model-invocation: false
---

# Scope Map Migration

Backfill `docs/spec/scope-map.md` from existing `derive-spec` output artifacts.
This is a one-time migration skill for brownfield projects adopting
`derive-feature`.

Do not create any `.feature` files for old features. Leave the existing
`UC-XX` documents in place.

## Inputs

- `docs/spec/actor-goal-list.md` when present
- `docs/spec/UC-XX-*.md` use case files when the actor-goal list is missing
- Cross-check inputs, when present:
  - `docs/spec/use_cases/system-use-cases.md`
  - `docs/spec/supplementary_specs/entity-model.md`
  - `docs/spec/supplementary_specs/interface-contracts.md`
  - `docs/spec/supplementary_specs/state-machines.md`
  - `docs/spec/supplementary_specs/validation-rules.md`

## Output

- `docs/spec/scope-map.md`

## Step 1 — Validate the migration inputs

1. Read `docs/spec/actor-goal-list.md` if it exists.
2. Read every `docs/spec/UC-XX-*.md` file if the actor-goal list is absent.
3. Read the cross-check inputs when they exist, to confirm terminology and
   ensure the backfill does not miss any documented rule.
4. Fail only if the requested source files cannot be read.

## Step 2 — Derive scope-map rows

### Primary source: actor-goal list exists

When `actor-goal-list.md` exists, create one scope-map `Rule` row for each
actor-goal row.

- The `Rule` column mirrors the actor-goal wording.
- The `Status` column is always `implemented`.
- The `Source` column points to the originating `UC-XX` file for that row,
  not to a `.feature` file.

### Fallback source: actor-goal list is missing

When `actor-goal-list.md` is missing, derive one scope-map `Rule` row from
each `UC-XX-*.md` file.

- Use the `UC-XX` filename as the rule anchor.
- Use the file's `Summary` field as the rule description.
- Set `Status` to `implemented`.
- Set `Source` to that `UC-XX` file.

### Final fallback: both primary sources are missing

When both `actor-goal-list.md` and `UC-XX-*.md` inputs are missing, but other
spec artifacts exist, write a scope map with a single note row:

- `NOTE: manual population required`
- `Status`: `implemented`
- `Source`: `—`

Exit without error.

## Step 3 — Write the scope map

Write `docs/spec/scope-map.md` as the persistent backfill artifact.
Use a table with at least these columns:

| Rule | Status | Source |
| ---- | ------ | ------ |

All migrated rows are `implemented`. Do not use a `.feature` file path in the
source column for migrated rows.

## Step 4 — Preserve the old artifacts

1. Do not modify the `UC-XX` source files.
2. Do not create or rename `.feature` files for old features.
3. Keep the migration idempotent so reruns reproduce the same scope map from
   the same inputs.

## References

- [Agentic Quality Gates and Requirements Consolidation](../../../docs/proposals/agentic-quality-gates-and-specification-consolidation.md)
- [ADR-0011](../../../docs/adr/0011-gherkin-feature-as-consolidated-specification-format.md)
