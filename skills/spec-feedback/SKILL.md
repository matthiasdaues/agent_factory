---
name: spec-feedback
description: Check whether specification or architecture needs updating after implementation reveals gaps, changed rules, or inaccurate contracts. Use when the user mentions spec drift, docs are stale, or implementation contradicts the spec.
category: implementation
---

# Spec Feedback

After implementing one or more issues, check whether the specification or architecture documentation has drifted from reality. The spec is not throwaway — it remains the authoritative description of system behaviour.

## Step 1 — Detect drift

Read the recently changed code (use `git diff` against the last spec-aligned commit). Compare against:

- `docs/spec/use_cases/` — do the use case flows still match?
- `docs/spec/supplementary_specs/entity-model.md` — any new entities, changed attributes, or relationships?
- `docs/spec/supplementary_specs/state-machines.md` — any new states or transitions?
- `docs/spec/supplementary_specs/interface-contracts.md` — do DTOs and schemas match the code?
- `docs/spec/supplementary_specs/validation-rules.md` — any new or changed rules?
- `docs/` (arc42 chapters) — any new components, changed boundaries, or deployment changes?

List every discrepancy.

**Completion**: every spec file checked against the implementation, all discrepancies listed.

## Step 2 — Update

For each discrepancy:

- Update the spec file to match the implemented behaviour.
- If an architecture decision changed, invoke the `write-adr` skill.
- Check the update itself against **Clean Architecture** and **SOLID** — don't introduce a violation while fixing drift.

Format every updated file via `scripts/mdformat --number <path>` per [markdown-formatting.md](../../rulebooks/markdown-formatting.md).

**Completion**: spec matches implemented behaviour, no undocumented behaviour exists in the code, architecture documentation reflects the current system structure.

## Step 3 — Report

Summarise what changed and why — one bullet per updated file. This summary becomes a commit message or PR comment.

**Completion**: summary written, changes committed.
