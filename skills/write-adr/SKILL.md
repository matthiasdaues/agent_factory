---
name: write-adr
description: Document an architecture decision as an ADR (Nygard format) with Pugh Matrix evaluation.
disable-model-invocation: true
---

# Write ADR

Document a single architecture decision following **ADR according to Nygard**, evaluating alternatives with a **Pugh Matrix**. Apply **Clean Architecture** and **SOLID** as evaluation criteria where relevant.

Read `CONTEXT.md` if it exists — use the project's domain vocabulary.

## Step 1 — Check for conflicts

Read existing ADRs in `docs/adr/`. Identify any that this decision might conflict with or supersede.

**Completion**: conflicts identified, or confirmed none exist.

## Step 2 — Evaluate alternatives

Build a Pugh Matrix — see [PUGH-MATRIX.md](PUGH-MATRIX.md) for format, criteria, and scoring rules.

Present the matrix to the user. Ask: _"Do these criteria and scores reflect your assessment?"_

**Completion**: the user confirms the evaluation or adjusts scores.

## Step 3 — Write the ADR

Save as `docs/adr/NNNN-short-title.md` (next available number) using **ADR according to Nygard** — include the Pugh Matrix in the Context section.

If this decision supersedes an earlier ADR, update that ADR's status to "Superseded by ADR-NNNN".

Update `docs/09_architecture_decisions.md` to link to the new ADR.

**Completion**: ADR follows **ADR according to Nygard**, Pugh Matrix included, no unresolved conflicts with existing ADRs, index updated.
