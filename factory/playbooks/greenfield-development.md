---
title: Greenfield Development Playbook
category: orchestration
type: runbook
version: 1.1.0
---

# Greenfield Development Playbook

Operational procedure for **new project development** from requirements through deployment.

## Prerequisites

- [ ] Project repository initialized
- [ ] `CONTEXT.md` exists (or will be created in Phase 1)
- [ ] Orchestrator configured OR manual session management ready

## Phase Boundary Contract

Every transition in the table below is a Factory workflow phase boundary. The
outgoing participant must invoke `handoff`, obtain a clean `handoff-lint`
result and independent semantic review, then make a hard stop before doing any
work from the next row. The incoming participant starts a fresh session and
must read the handoff first, verify its Git state, and read referenced artifacts
through an initial bounded chunk, expanding further only on demand. Do not
replay a prior transcript.

Before any child returns, it persists its complete reports and findings in
canonical tracked artifacts. Its parent receives only disposition, severity
counts, every artifact path, and a one-to-three-sentence next action; finding
detail and full reasoning remain in the artifacts. No in-place transcript
compaction, prose-only cache-restabilisation ritual, or live cache control is
introduced.

| Transition                                     | Route                                        |
| ---------------------------------------------- | -------------------------------------------- |
| requirements-agent → spec-review-agent         | Requirements authoring completes             |
| spec-review-agent → requirements-agent         | Open specification findings require remedies |
| spec-review-agent → architecture-agent         | Specification review is clean                |
| architecture-agent → architecture-review-agent | Architecture authoring completes             |
| architecture-review-agent → architecture-agent | Open architecture findings require remedies  |
| architecture-review-agent → planning-agent     | Architecture review is clean                 |
| planning-agent → implementation-agent          | Backlog is approved                          |
| implementation-agent → reconciliation-agent    | Implementation wave completes                |
| reconciliation-agent → implementation-agent    | Reconciliation finds code defects            |
| reconciliation-agent → qa-agent                | Reconciliation is clean                      |
| qa-agent → implementation-agent                | Quality review finds defects                 |
| implementation-agent → qa-agent                | Quality remedies are ready for retest        |

Each listed route requires the reviewed handoff and restart even where agent
frontmatter groups author and reviewer roles under one broader phase name.
Work that remains inside one route's outgoing phase is exempt under
[handoff-format.md](../rulebooks/conventions/handoff-format.md).

## Phase 1: Requirements

### Step 1.1 — Run Requirements Agent

```bash
orchestrator run-phase requirements
# OR manual: Start new session, activate requirements-agent
```

**Agent**: `requirements-agent`
**Expected outputs**: `docs/spec/prd.md`, `docs/spec/actor-goal-list.md`, `docs/spec/use_cases/`, `docs/spec/supplementary_specs/`

### Step 1.2 — Run Spec Review Agent (Separate Session)

```bash
orchestrator run-phase spec-review
# OR manual: Start NEW session, activate spec-review-agent
```

**Agent**: `spec-review-agent`
**Expected outputs**: `docs/reviews/spec-review-*.md`, `docs/findings/SPEC-*.md`

### Decision Point 1.3

Check: `docs/findings/SPEC-*.md` files with `status: open`

```bash
grep -l "status: open" docs/findings/SPEC-*.md
```

**If open findings exist** → Go to Step 1.4
**If no open findings** (or all `status: resolved`) → Go to Phase 2

### Step 1.4 — Loop: Address Findings

```bash
orchestrator run-phase requirements
# OR manual: Start NEW session, activate requirements-agent
```

**Instructions**: Requirements agent reads open `SPEC-*` findings and addresses them

Return to Step 1.2 (run spec-review-agent again)

## Phase 2: Architecture

### Step 2.1 — Run Architecture Agent

```bash
orchestrator run-phase architecture
# OR manual: Start new session, activate architecture-agent
```

**Agent**: `architecture-agent`
**Expected outputs**: `docs/*.md` (arc42 chapters), `docs/adr/`, `docs/architecture.dsl`, `docs/assets/images/`

### Step 2.2 — Run Architecture Review Agent (Separate Session)

```bash
orchestrator run-phase architecture-review
# OR manual: Start NEW session, activate architecture-review-agent
```

**Agent**: `architecture-review-agent`
**Expected outputs**: `docs/reviews/atam-review.md`, `docs/findings/ATAM-*.md`

### Decision Point 2.3

Check: `docs/findings/ATAM-*.md` files with `status: open`

```bash
grep -l "status: open" docs/findings/ATAM-*.md
```

**If open findings exist** → Go to Step 2.4
**If no open findings** → Go to Phase 3

### Step 2.4 — Loop: Address Findings

```bash
orchestrator run-phase architecture
# OR manual: Start NEW session, activate architecture-agent
```

**Instructions**: Architecture agent reads open `ATAM-*` findings and addresses them

Return to Step 2.2 (run architecture-review-agent again)

## Phase 3: Planning

### Step 3.1 — Run Planning Agent

```bash
orchestrator run-phase planning
# OR manual: Start new session, activate planning-agent
```

**Agent**: `planning-agent`
**Expected outputs**: `backlog/ST-*.md` files

### Step 3.2 — Validate Backlog

```bash
factory/scripts/backlog-lint --backlog-dir backlog
```

**If exit code 0** → Go to Step 3.3
**If exit code non-zero** → Fix errors, return to Step 3.1

### Step 3.3 — Confirm Backlog

**Manual approval required**: Review backlog with stakeholder

**If approved** → Go to Phase 4
**If changes needed** → Return to Step 3.1

## Phase 4: Implementation

### Step 4.1 — Run Implementation Agent (Dispatcher)

```bash
orchestrator run-phase implementation
# OR manual: Start new session, activate implementation-agent
```

**Agent**: `implementation-agent` (spawns parallel `developer-agent` subagents)
**Expected outputs**: `src/**/*`, `tests/**/*`, commits per story

### Step 4.2 — Run Reconciliation Agent (Separate Session)

```bash
orchestrator run-phase reconciliation
# OR manual: Start NEW session, activate reconciliation-agent
```

**Agent**: `reconciliation-agent`
**Expected outputs**: `docs/reviews/reconciliation-*.md`, `docs/findings/RECON-*.md`, updated specs

### Decision Point 4.3

Check: `docs/findings/RECON-*.md` files with `status: open`

```bash
grep -l "status: open" docs/findings/RECON-*.md
```

**If code defects exist** → Go to Step 4.4
**If no defects** → Go to Phase 5

### Step 4.4 — Loop: Fix Code Defects

```bash
orchestrator run-phase implementation
# OR manual: Start NEW session, activate implementation-agent
```

**Instructions**: Implementation agent reads open `RECON-*` findings and fixes code

Return to Step 4.2 (run reconciliation-agent again)

## Phase 5: Quality

### Step 5.1 — Run QA Agent

```bash
orchestrator run-phase qa
# OR manual: Start new session, activate qa-agent
```

**Agent**: `qa-agent` (Fagan + Security + Bug Hunt)
**Expected outputs**: `docs/reviews/fagan-review-*.md`, `docs/reviews/security-review-*.md`, `docs/findings/FAGAN-*.md`, `docs/findings/SEC-*.md`, `docs/findings/BUG-*.md`

### Decision Point 5.2

Check: Open defects in findings

```bash
grep -l "status: open" docs/findings/{FAGAN,SEC,BUG}-*.md
```

**If open defects exist** → Go to Step 5.3
**If no defects** → Go to Step 5.4 (DONE)

### Step 5.3 — Loop: Fix Defects

```bash
orchestrator run-phase implementation
# OR manual: Start NEW session, activate implementation-agent
```

**Instructions**: Implementation agent reads open findings and fixes them

Return to Step 5.1 (run qa-agent again)

### Step 5.4 — DONE

✅ **All phases complete**

Final checklist:

- [ ] All findings resolved (`status: resolved`)
- [ ] `spec-lint` passes
- [ ] `arch-lint` passes
- [ ] `backlog-lint` passes
- [ ] All tests pass
- [ ] No open findings

**Ready to merge** or proceed to release.

## Halt Conditions

**Stop immediately if:**

1. Adapter auth failure (not author-fixable)
2. Adapter config error (not author-fixable)
3. Circular dependencies detected in backlog
4. Iteration cap exceeded (e.g., 5 loops on same phase)

**Action**: Escalate to human operator.

## Utility: Retrospective

Run ad-hoc at end of any session:

```bash
# In active session
"Run a retrospective"
```

**Agent**: `coaching-agent`
**Output**: `docs/reviews/retro-*.md`

## State Tracking

**Current phase**: Check orchestrator state OR manually track in session notes
**Open findings**: `grep -r "status: open" docs/findings/`
**Loop count**: Track manually or via orchestrator iteration counter
