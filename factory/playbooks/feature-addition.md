---
title: Feature Addition Playbook
category: orchestration
type: runbook
scenario: feature-addition
version: 1.1.0
---

# Feature Addition Playbook

Operational procedure for **adding features to existing system**.

## Prerequisites

- [ ] Existing project with spec and architecture
- [ ] `CONTEXT.md` exists
- [ ] A proposal at `docs/proposals/<name>.md`, written to the [proposal template](../rulebooks/templates/proposal.md)

The proposal is the feature's authoritative design origin. Do not maintain a
parallel feature request, interview record, or design brief.

## Proposal Intake

### Step 0.1 — Clarify

Read the proposal and its referenced boundaries.

- **`draft`** → Invoke `clarify-requirements` with the proposal as its target.
  The interview amends that file until the design is decision-complete, then
  moves it to `open`.
- **`open`** → Review or grill the proposal in place. Resolve every Open
  Question as a decision, explicit assumption, or deferral.
- **`accepted`** → Preserve its recorded baseline and continue to Step 0.3.
- **`implemented`, `cancelled`, or `superseded`** → Stop; this playbook cannot
  open implementation from a closed proposal.

Grilling may make an artifact ready for acceptance, but cannot accept it.

### Decision Point 0.2 — Accept

**Manual**: Stakeholder accepts the proposal.

Record the full 40-character SHA of the commit containing the accepted proposal
as the immutable planning baseline. Do not embed that SHA in the proposal.

**If accepted** → Set `status: accepted`, update `updated`, commit, then route
the work using Step 0.3.
**If changes requested** → Return to Step 0.1.

### Step 0.3 — Route from Declared Impact

- Specification work is required when the accepted design changes behavior,
  use cases, quality requirements, or an external contract. Otherwise, skip to
  Phase 2.
- `impact.architecture_change: true` requires Phase 2.
- `impact.architecture_change: false` skips Phase 2 after required specification
  work.

Do not infer a small/large shortcut independently of the accepted proposal.
`impact`, `governance`, and Completion Criteria are the planning inputs.

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

## Phase 1: Requirements (If Specification Changes Are Needed)

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

Enter this phase when `impact.architecture_change` is `true`. If implementation
discovery contradicts that declaration, the proposal has materially changed:
return it to `open`, amend it, and repeat acceptance before continuing.

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

### Step 3.3 — Reconcile Plan with Proposal

Check that the backlog covers every Completion Criterion, excludes explicitly
deferred scope, and applies the declared governance and risk domains.

- If the proposal estimate has `confidence: low`, reforecast it from the
  decomposition, updating `estimate.as_of`, `basis`, and ranges.
- If planning changes accepted scope, impact, governance, or completion
  criteria materially, set the proposal back to `open` and return to Step 0.1.

### Step 3.4 — Approve Backlog

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
- [ ] Every proposal Completion Criterion is satisfied
- [ ] Proposal status is `implemented` and `updated` records the completion date
- [ ] Actual effort remains in the external calibration store, keyed by proposal path and accepted commit SHA; forecast values were not overwritten with actuals
- [ ] Every absorbed story/finding worktree is clean and removed
- [ ] Every absorbed local branch is deleted safely with `git branch -d`, unless named as an active review base
- [ ] Handoff records exact local/upstream tips and ahead/behind counts per [handoff-format.md](../rulebooks/conventions/handoff-format.md)

**Ready to merge**
