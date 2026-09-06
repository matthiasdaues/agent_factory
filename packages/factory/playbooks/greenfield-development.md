---
title: Greenfield Development Playbook
category: orchestration
type: runbook
version: 1.2.0
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

| Transition                                     | Route                                                                           |
| ---------------------------------------------- | ------------------------------------------------------------------------------- |
| requirements-agent → spec-review-agent         | Requirements authoring completes                                                |
| spec-review-agent → requirements-agent         | Open specification findings require remedies                                    |
| spec-review-agent → architecture-agent         | Specification review is clean                                                   |
| architecture-agent → architecture-review-agent | Architecture authoring completes                                                |
| architecture-review-agent → architecture-agent | Open architecture findings require remedies                                     |
| architecture-review-agent → planning-agent     | Architecture review is clean, charter completeness sweep and planning gate pass |
| planning-agent → implementation-agent          | Backlog is approved                                                             |
| implementation-agent → reconciliation-agent    | Implementation wave completes                                                   |
| reconciliation-agent → implementation-agent    | Reconciliation finds code defects                                               |
| reconciliation-agent → qa-agent                | Reconciliation is clean                                                         |
| qa-agent → implementation-agent                | Quality review finds defects                                                    |
| implementation-agent → qa-agent                | Quality remedies are ready for retest                                           |

Each listed route requires the reviewed handoff and restart even where agent
frontmatter groups author and reviewer roles under one broader phase name.
Work that remains inside one route's outgoing phase is exempt under
[handoff-format.md](../rulebooks/conventions/handoff-format.md).

## Phase 1: Requirements

### Step 1.0 — Scaffold Project Charter

```bash
# In the active session (stakeholder present), right after vision capture:
capture-charter --init
```

**Skill**: `capture-charter` (`--init` mode)
**Expected outputs**: `docs/agent-context/stack.yaml`, `docs/agent-context/workflow.yaml`,
`docs/agent-context/governance.yaml` (falls back to `docs/charter/*.md` for legacy projects) — skeleton created from the templates, answers
already known from the vision conversation filled in, everything else left
`To be decided.`

### Step 1.1 — Run Requirements Agent

```bash
orchestrator run-phase requirements
# OR manual: Start new session, activate requirements-agent
```

**Agent**: `requirements-agent`
**Expected outputs**: `docs/spec/prd.md`, `docs/spec/<feature-name>.feature`, `docs/spec/scope-map.md`, `docs/spec/<feature-name>-gaps.md`, `docs/spec/<feature-name>-qa-strategy.md`, `docs/spec/supplementary_specs/`

As requirements decisions settle a charter entry — a data store, a
licensing constraint, an integration requirement — the requirements agent
invokes `update-context` to record it in `docs/agent-context/stack.yaml` (falls back to `docs/charter/tech-stack.md`)
incrementally, rather than waiting for the completeness sweep.

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
**Expected outputs**: `docs/arc42/*.md` (arc42 chapters), `docs/adr/`, `docs/arc42/architecture.dsl`, `docs/assets/images/`

The workspace property `"arc42.projected"` defaults to `"false"` in fresh DSL files and is set to `"true"` by the architecture-agent only when the user requests arc42 chapter projection from the DSL.

As architecture decisions settle a charter entry — infrastructure, deployment
topology, a cloud provider — the architecture agent invokes `update-charter`
to record it in `docs/agent-context/stack.yaml` (falls back to `docs/charter/tech-stack.md`) incrementally.

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
**If no open findings** → Go to Step 2.5

### Step 2.4 — Loop: Address Findings

```bash
orchestrator run-phase architecture
# OR manual: Start NEW session, activate architecture-agent
```

**Instructions**: Architecture agent reads open `ATAM-*` findings and addresses them

Return to Step 2.2 (run architecture-review-agent again)

### Step 2.5 — Charter Completeness Sweep

```bash
# In the active session (stakeholder present):
capture-charter
```

**Skill**: `capture-charter` (completeness sweep mode, no flag)
**Expected outputs**: `docs/agent-context/stack.yaml` and `docs/agent-context/workflow.yaml` (falls back to `docs/charter/tech-stack.md` and `docs/charter/development.md`)
with every entry resolved to a concrete answer or an explicit deferral
(`docs/agent-context/governance.yaml` or `docs/charter/house-rules.md` may still carry open items), Epic 0 stories
(`epic: "Epic 0 — Project Setup"`) written to `backlog/ST-*.md`, including the
closing "update development.md" story that depends on every other Epic 0 story

### Step 2.6 — Planning Gate

```bash
factory/scripts/charter-lint --planning-gate
```

**If exit code non-zero** → Return to Step 2.5, resolve the reported `To be decided.` entries
**If exit code 0** → Present the completed charter and the Epic 0 batch to the
stakeholder for approval together — same manual-approval pattern as Step 3.3

**If approved** → Go to Phase 3
**If changes needed** → Return to Step 2.5

## Phase 3: Planning

### Step 3.1 — Run Planning Agent

```bash
orchestrator run-phase planning
# OR manual: Start new session, activate planning-agent
```

**Agent**: `planning-agent`
**Expected outputs**: `backlog/ST-*.md` files

The planning agent reads the project context from `docs/agent-context/*.yaml` (falls back to `docs/charter/*.md`) and acknowledges that Epic 0
stories already exist in `backlog/` — written by the charter completeness
sweep in Step 2.5. It derives feature stories after them: each feature
story's `deps:` chains to the closing Epic 0 "update development.md" story,
so no feature story is dependency-ready until Epic 0 is done.

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

Wave 1 is Epic 0 (`epic: "Epic 0 — Project Setup"`) — no feature story
dispatches until every must-have Epic 0 story reaches a terminal state. This
is enforced by the `deps:` chain the planning agent wrote in Step 3.1, not by
separate scheduling logic.

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

✅ **Terminal Condition: Project Ready for Feature Delivery**

The playbook ends when the following terminal artifacts exist:

**Terminal Artifacts:**

- [ ] `docs/spec/scope-map.md` exists with all Rules from the initial specification marked `deferred` (ready to be implemented as features)
- [ ] `docs/arc42/architecture.dsl` models the planned module structure (C4 components and dependencies as designed)
- [ ] Arc42 prose chapters (01–12) pass architecture review with no blocking findings
- [ ] No `.feature` files exist yet (those are produced per-slice when `feature-addition` begins)

**Process Checklist:**

- [ ] All specification review findings resolved (`status: resolved`)
- [ ] All architecture review findings resolved (`status: resolved`)
- [ ] `spec-lint` passes
- [ ] `arch-lint` passes
- [ ] `backlog-lint` passes
- [ ] All tests pass
- [ ] No open findings

**Next Phase:**

After this playbook completes, **all feature work enters through the `feature-addition` playbook**. Each feature-addition slice produces a per-feature `.feature` file from one or more deferred Rules in the scope map. The scope map is the specification baseline that guides feature delivery.

## Halt Conditions

**Stop immediately if:**

1. Adapter auth failure (not author-fixable)
2. Adapter config error (not author-fixable)
3. Circular dependencies detected in backlog
4. Iteration cap exceeded (e.g., 5 loops on same phase)

**Action**: Escalate to human operator.

## Utility: Retrospective

Run ad-hoc at end of any session. The coaching-agent runs in the current session (adopt pattern — read the definition, assume its role, do not spawn a subagent):

```bash
# In active session
"Run a retrospective"
```

**Agent**: `coaching-agent` (adopted in current session)
**Output**: `docs/reviews/retro-*.md`

## State Tracking

**Current phase**: Check orchestrator state OR manually track in session notes
**Open findings**: `grep -r "status: open" docs/findings/`
**Loop count**: Track manually or via orchestrator iteration counter
