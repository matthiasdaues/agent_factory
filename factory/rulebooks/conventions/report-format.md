---
title: Review Report Format
category: review
enforcement: none — human-consumed; the findings a report cites are what the orchestrator mechanically ingests, per finding-format.md
version: 1.0.0
---

# Review Report Format

Shared format for all review and inspection skills.

## Finding table

Row format: [review-report.md template](../templates/review-report.md).

## Category rules

- **Defect** — the artifact is wrong: contradicts spec, breaks a principle with consequences, has a bug, or is unusable as-is.
- **Suggestion** — usable but improvable: sharper wording, simplification, idiomatic pattern.
- **Question** — needs the author to clarify intent. Also record in `docs/spec/todo.md` per [todo-format.md](todo-format.md).

Every finding must state **what is wrong** and **what to do** — no "this looks off" without a fix direction.

## Severity

- **Critical** — blocks the phase or introduces a security/correctness defect that will propagate.
- **Major** — significant defect that must be fixed before the review can pass.
- **Minor** — low-impact improvement; fix is optional for this pass.

## Findings drive the loop

File each Defect and blocking-severity finding as its own `docs/findings/*.md` per [finding-format.md](finding-format.md). Under the orchestrator, the review loop reads those files directly — an `open` finding loops back to the author, a `resolved` one drops out — so the report table is for the reader and the finding files are what the tool acts on.

## Referenced from

- [finding-format.md § When to file](finding-format.md#when-to-file)
- [todo-format.md § When to file](todo-format.md#when-to-file)
- [architecture-review-agent.md § Workflow](../../agents/architecture-review-agent.md#workflow)
- [reconciliation-agent.md § Workflow](../../agents/reconciliation-agent.md#workflow)
- [qa-agent.md § Workflow](../../agents/qa-agent.md#workflow)
- [spec-review-agent.md § Workflow](../../agents/spec-review-agent.md#workflow)
- [security-review § Step 3 — Write the review report](../../skills/security-review/SKILL.md#step-3-write-the-review-report)
- [reconcile-spec § Step 3 — Write the reconciliation report](../../skills/reconcile-spec/SKILL.md#step-3-write-the-reconciliation-report)
- [inspect-spec § Step 3 — Write the review report](../../skills/inspect-spec/SKILL.md#step-3-write-the-review-report)
- [atam-review § Step 4 — Write the review report](../../skills/atam-review/SKILL.md#step-4-write-the-review-report)
- [fagan-review § Step 3 — Write the review report](../../skills/fagan-review/SKILL.md#step-3-write-the-review-report)
