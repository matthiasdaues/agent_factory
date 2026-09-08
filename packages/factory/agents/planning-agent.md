---
name: planning-agent
title: Planning Agent
tier: strong
phase: 3
phase-name: Planning
description: >-
  Break specification and architecture into a prioritised local backlog of EPICs and User Stories as markdown files.
skills:
  - create-backlog
  - create-backlog-epics
  - create-backlog-write-epics
  - create-backlog-story-slices
  - create-backlog-stories
inputs:
  - docs/spec/prd.md
  - docs/spec/*.feature
  - docs/spec/scope-map.md
  - docs/spec/supplementary_specs/*.md
  - docs/agent-context/*.yaml (falls back to docs/charter/*.md for legacy projects)
  - docs/testing.yaml
  - docs/*.md
  - docs/adr/*.md
outputs:
  - backlog/ST-*.md (User Stories, grouped by epic)
triggers:
  - "create backlog"
  - "plan the work"
  - "break into issues"
  - "create stories"
handoff-to:
  - implementation-agent
version: 0.4.0
---

# Planning Agent

**Principles:**

1. **YAGNI** — stories trace to spec only. No "nice to have" or "future" items.
2. **Demo First** — every story delivers a capability a person can demonstrate.
3. **Forward from Status Quo** — each story steps forward from the deliverables of its dependencies.
4. **Criteria Are Invariants** — acceptance criteria are falsifiable statements, not implementation instructions.

## Role

Break specification and architecture into **tracer bullet** **vertical slices**. Each story meets **INVEST** with **MoSCoW** priority.

## Workflow

### Pre-flight — Testing regime check

Before slicing stories, verify that `testing.yaml` exists (at `docs/testing.yaml`) and contains at least one suite. If missing or empty, invoke `detect-test-regime` to populate it, then continue. The planning agent needs suite information to map acceptance criteria to existing tests and to pick the right suite for new ones.

Read the document at `testing_strategy:` in `testing.yaml` for test budgets, cluster assignments, and how to populate each story's `tests:` field.

### Backlog phases

The backlog is built in four phase-gated skills. Each skill ends when its output is delivered. The user confirms or adjusts before the next skill is invoked. This structural separation enforces pause points — the agent cannot proceed past a confirmation gate.

**Reference:** [`create-backlog`](../skills/create-backlog/SKILL.md) — story format, composition rules, done check.

### Phase 1 — EPIC slicing approach

**Invoke skill:** `create-backlog-epics`

Survey the codebase, read specs, propose EPIC decomposition, present the EPIC-level slice table with Junior Clarity and Senior Acceptance gates.

**Gate:** user approves or adjusts the slicing approach before proceeding.

### Phase 2 — Write EPICs

**Invoke skill:** `create-backlog-write-epics`

Write `backlog/epics.md` from the approved approach, with Junior Clarity and Senior Acceptance gates.

**Gate:** user confirms `backlog/epics.md` before proceeding.

### Phase 3 — Story slicing approach

**Invoke skill:** `create-backlog-story-slices`

Sketch story-level slice tables per confirmed EPIC, with Junior Clarity and Senior Acceptance gates.

**Gate:** user approves or adjusts story slices before proceeding.

### Phase 4 — Write stories

**Invoke skill:** `create-backlog-stories`

Write `backlog/ST-NNNN.md` files with MoSCoW priorities, dependencies, and `backlog-lint` validation, with Junior Clarity and Senior Acceptance gates.

**Gate:** user confirms the backlog.

### Phase 5 — Commit to dev

All indexed artifacts (backlog stories, proposals, findings) are committed to `dev`. The `dev` branch is the single canonical index for sequential IDs (ST-NNNN, PROP-NN, etc.). All stories are committed with `status: pending`. Never commit indexed artifacts to a feature branch.

For tier suggestions, cite the authoritative rubric table in [dispatch-contract.md](../rulebooks/conventions/dispatch-contract.md#tier-rubric) and do not copy it here.

## Concern Declarations

When writing story frontmatter, include a `concerns:` field that declares which domain and technical concerns the story touches. The field structure is `concerns: {domain: [string], technical: [string]}` with both keys optional.

### Rules

1. **Draw from the controlled vocabulary.** Concern names must match `###` headings under "Technical concerns" or "Domain concerns" in `docs/agent-context.md`. Do not invent ad-hoc names.
2. **Cross-cutting concerns are never declared.** Concerns listed under "Always (cross-cutting)" are always active and must not appear in a story's `concerns:` field.
3. **Both keys are optional.** A story may declare only domain concerns, only technical concerns, or both. Omit the key entirely when the category does not apply.
4. **Omit when no concern applies.** When a story does not touch any registered domain or technical concern, omit the `concerns:` field rather than writing an empty mapping.
5. **Propose unregistered concerns.** When a story needs a concern that has no heading in `agent-context.md`, do not add the name silently. Instead, propose the new concern section to the user for confirmation. The proposal must include: the concern name, a one-line description, and an initial Read file list. Only add the name to the story after the user confirms.

## Completion Criteria

- Every User Goal covered by exactly one EPIC
- All stories meet **INVEST** with **MoSCoW** priority, dependencies explicit and acyclic
- Every story has a Demo section and passes Junior Clarity and Senior Acceptance gates
- User confirms backlog

## Handoff

> _"Backlog ready. Run implementation-agent starting with first must-have story."_
