---
name: reconcile-spec
description: Comprehensive code-vs-spec reconciliation — build truth maps, diff, update or flag every discrepancy.
category: implementation
disable-model-invocation: true
---

# Reconcile Specification

After a full implementation phase, compare **implemented code** against **specification and architecture documentation** and bring them into alignment: code right and spec stale → fix the spec; spec right and code diverged → flag a defect.

Differs from `spec-feedback` in scope: that skill runs per-issue; this one runs once per implementation phase, against the entire codebase and spec surface.

## Step 1 — Build truth maps and diff

Read the code and the spec side by side. For each contract surface, record a tuple: `(artifact, spec location, code location, match | drift | missing-from-spec | missing-from-code)`.

| Contract surface  | Spec source                 | Code source                            |
| ----------------- | --------------------------- | -------------------------------------- |
| Port interfaces   | `interface-contracts.md`    | Protocol classes, method signatures    |
| Entity model      | `entity-model.md`           | Dataclasses, enums, fields             |
| State machines    | `state-machines.md`         | Status enums, transition logic         |
| Validation rules  | `validation-rules.md`       | Guard clauses, assertions              |
| CLI / API surface | `system-use-cases.md`       | Parser definitions, route handlers     |
| Components        | `05_building_block_view.md` | Adapter constructors, module structure |

Classify each discrepancy:

| Classification        | Meaning                                 | Action                                        |
| --------------------- | --------------------------------------- | --------------------------------------------- |
| **Spec stale**        | Code is correct; spec lagged            | Update the spec                               |
| **Code defect**       | Spec is correct; code diverged          | File as Defect                                |
| **Undocumented**      | Code exists with no spec coverage       | Add to spec, or flag as gold-plating          |
| **Speculative**       | Spec declares something not implemented | Mark deferred, or remove if descoped          |
| **Terminology drift** | Code term ≠ `docs/CONTEXT.md` term      | Align; update glossary if code term is better |

Order by severity: code defects → spec-stale (most-referenced first) → undocumented → speculative.

## Step 2 — Update

For **spec stale** and **undocumented** items: update the affected spec or architecture file. For new ADRs, invoke `write-adr`. For **terminology drift**: update `docs/CONTEXT.md` via the `domain-modeling` skill. Run `spec-lint` and `arch-lint` after updates.

For **code defects**: do not fix — file per [finding-format.md](../../rulebooks/conventions/finding-format.md) with tag `RECON`.

Format every updated spec/architecture file via `scripts/mdformat --number <path>` per [markdown-formatting.md](../../rulebooks/conventions/markdown-formatting.md).

## Step 3 — Write the reconciliation report

Save as `docs/reviews/reconciliation-YYYY-MM-DD.md` per [report-format.md](../../rulebooks/conventions/report-format.md), adding:

1. **Scope** — code paths and spec files compared.
2. **Discrepancy table** — one row per finding with classification and action taken.
3. **Spec files updated** — list with one-line summary per change.
4. **Code defects filed** — findings handed to the implementation agent.
5. **Linter results** — `spec-lint` and `arch-lint` exit codes after updates.

## Step 4 — Verify prior findings (repeat passes only)

Per [review-loop-discipline.md](../../rulebooks/conventions/review-loop-discipline.md): for each open `RECON` finding, verify the fix and set `resolved` or annotate what's still missing — **and** re-run Step 1's full truth-map diff fresh, not just the prior findings list, to catch drift the fix itself introduced.
