---
title: Feature Addition Playbook
category: orchestration
type: runbook
scenario: feature-addition
version: 1.0.0
---

# Feature Addition Playbook

Operational procedure for **adding features to existing system**.

## Prerequisites

- [ ] Existing project with spec and architecture
- [ ] `CONTEXT.md` exists
- [ ] A proposal at `factory/docs/proposals/<name>.md` (per the [proposal template](../rulebooks/templates/proposal.md)) — the design origin the Planning phase consumes
- [ ] Feature request or user story defined

## Decision: Scope Assessment

### Is this a small, well-understood feature?

**Small**: Single story, clear implementation, no architectural impact
**If YES** → Skip to Phase 3 (Planning)

**Large**: Multiple stories, architectural decisions needed, cross-cutting concerns
**If NO** → Start at Phase 1 (Requirements)

## Approval Contract

At the start of each phase, present one bounded approval covering its reversible,
in-scope work. State:

- outputs and acceptance invariants;
- deterministic gates that must pass;
- stop conditions: a changed requirement, unresolved design choice, destructive
  action, external side effect, failed gate, or scope expansion.

After approval, execute the phase through its stated gates without requesting
confirmation for each routine reversible step. Existing decision points remain:
stakeholders still approve requirements, architecture decisions, backlog scope,
destructive cleanup, and any response to a stop condition. Batching must not be
used to infer broader authority.

## Phase 1: Requirements (Large Features Only)

### Step 1.1 — Update Specification

```bash
orchestrator run-phase requirements
# OR manual: Start new session, activate requirements-agent
```

**Agent**: `requirements-agent`
**Task**: Add use cases to existing spec, update supplementary specs

**Expected outputs**: Updated `docs/spec/use_cases/`, `docs/spec/supplementary_specs/`

### Step 1.2 — Spec Review

```bash
orchestrator run-phase spec-review
```

**Agent**: `spec-review-agent`

### Decision Point 1.3

Check for open `SPEC-*` findings:

```bash
grep -l "status: open" docs/findings/SPEC-*.md
```

**If open** → Loop to Step 1.1
**If clean** → Go to Phase 2

## Phase 2: Architecture (If Architectural Changes Needed)

### Decision: Does this feature require architectural changes?

Check with architect or review ADRs:

- New components?
- New external dependencies?
- New deployment requirements?
- State machine changes?

**If NO architectural changes** → Skip to Phase 3
**If YES** → Continue Step 2.1

### Step 2.1 — Update Architecture

```bash
orchestrator run-phase architecture
```

**Agent**: `architecture-agent`
**Task**: Update arc42 docs, add ADRs, update C4 model

### Step 2.2 — Architecture Review

```bash
orchestrator run-phase architecture-review
```

**Agent**: `architecture-review-agent`

### Decision Point 2.3

Check for open `ATAM-*` findings:

```bash
grep -l "status: open" docs/findings/ATAM-*.md
```

**If open** → Loop to Step 2.1
**If clean** → Go to Phase 3

## Phase 3: Planning

### Step 3.1 — Create Stories

```bash
orchestrator run-phase planning
```

**Agent**: `planning-agent`
**Task**: Create new `ST-*` stories, update EPIC grouping

**Expected outputs**: New `backlog/ST-*.md` files

### Step 3.2 — Validate

```bash
factory/scripts/backlog-lint --backlog-dir backlog
```

**If errors** → Fix and return to Step 3.1
**If clean** → Go to Step 3.3

### Step 3.3 — Approve

**Manual**: Stakeholder approval

**If approved** → Go to Phase 4
**If changes** → Return to Step 3.1

## Phase 4: Implementation

### Step 4.1 — Implement Stories

```bash
orchestrator run-phase implementation
```

**Agent**: `implementation-agent`

### Step 4.2 — Reconcile

```bash
orchestrator run-phase reconciliation
```

**Agent**: `reconciliation-agent`

### Decision Point 4.3

Check for code defects:

```bash
grep -l "status: open" docs/findings/RECON-*.md
```

**If defects** → Loop to Step 4.1
**If clean** → Go to Phase 5

## Phase 5: Quality

### Step 5.1 — QA

```bash
orchestrator run-phase qa
```

**Agent**: `qa-agent`

### Decision Point 5.2

Check for open defects:

```bash
grep -l "status: open" docs/findings/{FAGAN,SEC,BUG}-*.md
```

**If defects** → Loop to Step 4.1
**If clean** → DONE

## DONE

✅ **Feature complete**

Final checks:

- [ ] All new tests pass
- [ ] All existing tests still pass (no regression)
- [ ] Spec updated to reflect new feature
- [ ] Architecture docs updated (if applicable)
- [ ] All findings resolved
- [ ] Every absorbed story/finding worktree is clean and removed
- [ ] Every absorbed local branch is deleted safely with `git branch -d`, unless named as an active review base
- [ ] Handoff records exact local/upstream tips and ahead/behind counts per [handoff-format.md](../rulebooks/conventions/handoff-format.md)

**Ready to merge**
