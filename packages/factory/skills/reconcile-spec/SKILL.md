---
name: reconcile-spec
description: Comprehensive code-vs-spec reconciliation — build truth maps, diff, update or flag every discrepancy.
category: implementation
---

# Reconcile Specification

After a full implementation phase, compare **implemented code** against **specification and architecture documentation** and bring them into alignment: code right and spec stale → fix the spec; spec right and code diverged → flag a defect.

Read [factory-voice.md](../../rulebooks/conventions/factory-voice.md) now and hold every rule as a writing constraint. No prose reaches terminal output or a file until it passes all four gates and clears the final pass.
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

| Classification        | Meaning                                  | Action                                   |
| --------------------- | ---------------------------------------- | ---------------------------------------- |
| **Spec stale**        | Code is correct; spec lagged             | Update the spec                          |
| **Code defect**       | Spec is correct; code diverged           | File as Defect                           |
| **Undocumented**      | Code exists with no spec coverage        | Add to spec, or flag as gold-plating     |
| **Speculative**       | Spec declares something not implemented  | Mark deferred, or remove if descoped     |
| **Terminology drift** | Code term ≠ `docs/spec/glossary.md` term | Report row for the domain-modeling agent |

Order by severity: code defects → spec-stale (most-referenced first) → undocumented → speculative.

## Step 2 — Write the rows

This skill changes no specification, architecture, ADR, or agent-context file. It writes one row per drift, for the owner of the artifact. Never edit the artifact.

Each row has the columns Artifact, Drift, Evidence, Owner, and Status, as [interface-contracts.md § Report rows](../../../../docs/spec/interface-contracts.md#report-rows-spec-feedback-and-reconciliation) defines them. Status is `open`. Owner is the producer of the artifact:

| Artifact                                                                           | Owner                   |
| ---------------------------------------------------------------------------------- | ----------------------- |
| Scope map, `.feature` files, `docs/spec/areas/*.md`                                | `requirements-agent`    |
| `glossary.md`, entity model, state machines, validation rules, interface contracts | `domain-modeling-agent` |
| `docs/*.md`, `docs/adr/*.md`, `architecture.dsl`                                   | `architecture-agent`    |
| `docs/agent-context.md`                                                            | `virgil`                |
| `backlog/ST-NNNN.md` (`tests:` field)                                              | `planning-agent`        |

For **terminology drift**: the row has Artifact `docs/spec/glossary.md`, Drift naming both terms, Evidence naming the code path and line, Owner `domain-modeling-agent`, and Status `open`. It changes neither `docs/spec/glossary.md` nor `docs/spec/work/term-candidates.md`. Only the domain-modeling agent writes the glossary, and it acts on the row first.

For a **drift** that you record as a finding: Run `.agent-factory/factory/scripts/next-id RECON` and read the ID from its standard output, because a shell variable does not survive from one agent command to the next. When `next-id` fails, stop and report its message; never pick a number by hand. File it per [finding-format.md](../../rulebooks/conventions/finding-format.md) with tag `RECON`. Its row still goes to the owner of the artifact.

For **code defects**: do not fix and do not write a row. File per [finding-format.md](../../rulebooks/conventions/finding-format.md) with tag `BUG`. Run `.agent-factory/factory/scripts/next-id BUG` and read the ID from its standard output, because a shell variable does not survive from one agent command to the next. When `next-id` fails, stop and report its message; never pick a number by hand.

## Step 3 — Write the reconciliation report

The report is the only output besides `BUG` findings. Save it per [report-format.md](../../rulebooks/conventions/report-format.md) under these names:

- The first run of a day writes `docs/reviews/reconciliation-YYYY-MM-DD.md`.
- A second run on the same day writes `reconciliation-YYYY-MM-DD-2.md`, a third `-3`, and so on. Never change an earlier report.
- Reports sort by date, then by suffix. The file without a suffix is run 1 of its day, and the highest suffix of the latest date is the previous report.

The report holds:

1. **Scope** — code paths and spec files compared.
2. **Discrepancy table** — one row per drift, with the five columns above.
3. **Code defects filed** — `BUG` findings handed to the developer agent.

## Step 4 — Check the earlier reports (repeat passes only)

Read the rows of every earlier report and check each against the code. Write no row for a drift that has a row in an earlier report, unless that row is closed: `confirmed`, or `fixed` on an artifact outside the core list. For a row still `open`, or `fixed` on an artifact of the core list, record nothing, because the backfeed step of `documentation-update` still waits on it. When the drift of a closed row appears again, write a new `open` row; the closed row stays unchanged. The core list is `rulebooks/core-artifacts.yaml` under the Factory root.

Per [review-loop-discipline.md](../../rulebooks/conventions/review-loop-discipline.md), also re-run Step 1's full truth-map diff fresh, to catch drift the fixes introduced.
