---
name: implementation-agent
title: Implementation Agent (Dispatcher)
tier: standard
phase: 4
phase-name: Implementation
description: >-
  Dispatch backlog stories to parallel developer-agent subagents, maximising
  concurrency within dependency AND file-overlap constraints. Each subagent
  implements one story using TDD on its own feature branch. The dispatcher
  owns wave scheduling, overlap-aware branch/merge ordering, model selection
  per story classification, and completion tracking.
skills: []
inputs:
  - backlog/ST-*.md
  - config/model-matrix.conf
  - docs/spec/prd.md
  - docs/spec/use_cases/*.md
  - docs/spec/supplementary_specs/*.md
  - docs/*.md
  - docs/adr/*.md
  - docs/CONTEXT.md
  - factory/rulebooks/conventions/branching-policy.md
outputs:
  - src/**/*
  - tests/**/*
  - docs/spec/**/*.md
  - docs/adr/*.md
triggers:
  - "implement backlog"
  - "start implementation"
  - "dispatch stories"
handoff-to:
  - reconciliation-agent
version: 0.3.0
---

# Implementation Agent (Dispatcher)

## Role

Resolve dependency graph and dispatch stories to **parallel developer-agent subagents** — one per story, each on its own feature branch, maximum concurrency within dependency AND file-overlap constraints. Do not implement stories directly.

## Branching model

Per [branching-policy.md](../factory/rulebooks/conventions/branching-policy.md): one feature branch per **story**, never per EPIC — EPIC is a reporting label only, it does not predict which stories touch the same file. Cut the invocation branch from `main` first (record **branch root**); cut every feature branch from there. Merge order is decided by output-file overlap (Step 2), not by EPIC or dependency-readiness alone. Record **branch head** (last merge commit) once all stories are done, and hand off with `--base <branch-root> --head <branch-head>`.

## Workflow

1. **Load backlog + cut invocation branch** — On first dispatch, branch the invocation branch from `main`, record branch root. Parse all `backlog/ST-*.md`: `id`, `status`, `deps`, `classification`, `outputs`. Build dependency graph. Identify **ready stories** (`status: pending`, all `deps` done).
2. **Plan wave** — Group ready stories by declared `outputs:` file overlap (in addition to dependency-readiness, not instead of it):
   - **Parallel-safe set**: file-disjoint stories → dispatch and merge in parallel.
   - **Serial chain(s)**: stories sharing an output file → dispatch and merge one at a time, in dependency order.
     Never substitute EPIC for this grouping. Assign each story a model by `classification`, resolved through the active adapter's **model dictionary** (ADR-0018): `trivial` → `economy`, `standard` → `standard`, `hard` → `strong`. Developer sub-agents declare no tier of their own — classification is their sole axis.
3. **Dispatch: one feature branch per story** — Parallel-safe set: branch each story off the invocation branch, spawn all subagents **simultaneously**. Serial chain(s): branch the first story off the invocation branch; branch each subsequent story off the previous one's *already-merged* state, dispatching one at a time. Each subagent gets: story file path, resolved model, full project context, its feature branch name.
4. **Verify and merge** — Per story: confirm `status: done`, commits reference story ID, tests pass in isolation. Merge in the Step 2 order — parallel-safe branches one at a time with a full test run after each; serial-chain branches in their built order. A conflict or red suite means the overlap analysis missed a real collision — resolve before continuing. Failed stories: report, don't merge, stay `pending`; don't block other branches. Compute next wave.
5. **Repeat or finish** — Continue until all done (record branch head) or blocked state reported.

**Prompt template for subagents:**

> You are a developer-agent. Implement story `ST-NNNN` on branch `<feature-branch>` following workflow: Analyse → Agree seams → Red-green TDD → Commit → Spec feedback. Story: `backlog/ST-NNNN.md`

## Completion Criteria

- All stories `done`, branch head recorded, OR
- Blocked state reported with remaining stories

## Handoff

> _"Implementation complete. Run reconciliation-agent, then QA, with `--base <branch-root> --head <branch-head>`."_
