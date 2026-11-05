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
- [ ] `docs/spec/glossary.md` exists (or will be created during requirements work)
- [ ] Session management ready

## Session Boundaries

When work moves from one agent to another, the outgoing session writes a
handoff per [handoff-format.md](../rulebooks/conventions/handoff-format.md),
obtains a clean `handoff-lint` result and independent semantic review, then
makes a hard stop. The incoming agent starts a fresh session, reads the handoff
first, verifies its Git state, and reads referenced artifacts in bounded,
on-demand chunks. Do not replay a prior transcript.

Before any child returns, it persists its complete reports and findings in
canonical tracked artifacts. Its parent receives only disposition, severity
counts, every artifact path, and a one-to-three-sentence next action; finding
detail and full reasoning remain in the artifacts.

A handoff is required whenever the next activity is performed by a different
agent — for example, an author handing artifacts to a reviewer, or a reviewer
returning findings to an author for remediation. Work that continues within the
same agent's session needs no handoff.

## Requirements

### Step 1.0 — Scaffold Agent Context

```bash
# In the active session (stakeholder present), right after vision capture:
capture-context --init
```

**Skill**: `capture-context` (`--init` mode)
**Expected outputs**: `docs/agent-context.md` — skeleton created from the template, with
the answers already known from the vision conversation filled in

### Step 1.1 — Run Requirements Agent

```bash
# Start new session, activate requirements-agent
```

**Agent**: `requirements-agent`
**Expected outputs**: `docs/spec/work/prd.md`, `docs/spec/features/<feature-name>.feature`, `docs/spec/scope-map.md`, `docs/spec/work/<feature-name>-gaps.md`

After the feature file exists, two more agents write their own files, each in a new session:

- **Structure files** (`docs/spec/glossary.md`, `docs/spec/entity-model.md`, and the supplementary specs at the top of `docs/spec/`): `domain-modeling-agent`
- **QA strategy** (`docs/spec/work/<feature-name>-qa-strategy.md`): `test-strategy-agent`

As requirements decisions settle a project fact — a data store, a
licensing constraint, an integration requirement — the requirements agent
records it in `docs/agent-context.md` right away.

### Step 1.2 — Run Spec Review Agent (Separate Session)

```bash
# Start NEW session, activate spec-review-agent
```

**Agent**: `spec-review-agent`
**Expected outputs**: `docs/reviews/spec-review-*.md`, `docs/findings/SPEC-*.md`

### Decision Point 1.3

Check: `docs/findings/SPEC-*.md` files with `status: open`

```bash
grep -l "status: open" docs/findings/SPEC-*.md
```

**If open findings exist** → Go to Step 1.4
**If no open findings** (or all `status: resolved`) → The architecture-agent's
preconditions are satisfied.

### Step 1.4 — Loop: Address Findings

```bash
# Start NEW session, activate requirements-agent
```

**Instructions**: Requirements agent reads open `SPEC-*` findings and addresses them

Return to Step 1.2 (run spec-review-agent again)

## Architecture

### Step 2.1 — Run Architecture Agent

```bash
# Start new session, activate architecture-agent
```

**Agent**: `architecture-agent`
**Expected outputs**: `docs/arc42/*.md` (arc42 chapters), `docs/adr/`, `docs/spec/architecture.dsl`, `docs/assets/images/`

The workspace property `"arc42.projected"` defaults to `"false"` in fresh DSL files and is set to `"true"` by the architecture-agent only when the user requests arc42 chapter projection from the DSL.

As architecture decisions settle a project fact — infrastructure, deployment
topology, a cloud provider — the architecture agent records it in
`docs/agent-context.md` right away.

### Step 2.2 — Run Architecture Review Agent (Separate Session)

```bash
# Start NEW session, activate architecture-review-agent
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
# Start NEW session, activate architecture-agent
```

**Instructions**: Architecture agent reads open `ATAM-*` findings and addresses them

Return to Step 2.2 (run architecture-review-agent again)

### Step 2.5 — Agent Context

```bash
# In the active session (stakeholder present):
capture-context --update --scan
```

**Skill**: `capture-context` (`--update --scan`; Step 1.0 already created the file)
**Expected outputs**: `docs/agent-context.md` with new domain concerns from the scope map,
`Read:` paths to the specification and architecture documents, and every `Read:` path
resolving. A project without code yet has nothing to scan for its planned stack, so the
rescan may propose removing technical concerns taken from the vision. Decline those
removals.

### Step 2.6 — Planning Gate

```bash
.agent-factory/factory/scripts/concern-lint
```

**If exit code non-zero** → Return to Step 2.5 and resolve the reported findings
**If exit code 0** → Present `docs/agent-context.md` to the stakeholder for
approval — same manual-approval pattern as Step 3.3

**If approved** → The planning-agent's preconditions are satisfied.
**If changes needed** → Return to Step 2.5.

## Planning

### Step 3.1 — Run Planning Agent

```bash
# Start new session, activate planning-agent
```

**Agent**: `planning-agent`
**Expected outputs**: `backlog/ST-*.md` files

The planning agent reads the project context from `docs/agent-context.md`.
A new project has no test runner, CI, or linters yet. That setup work enters
as a line item inside the first story that needs it, like any other
infrastructure; there is no separate setup epic.

### Step 3.2 — Validate Backlog

```bash
.agent-factory/factory/scripts/backlog-lint --backlog-dir backlog
```

**If exit code 0** → Go to Step 3.3
**If exit code non-zero** → Fix errors, return to Step 3.1

### Step 3.3 — Confirm Backlog

**Manual approval required**: Review backlog with stakeholder

**If approved** → The implementation-agent's preconditions are satisfied.
**If changes needed** → Return to the planning-agent (Step 3.1).

## Implementation

### Step 4.1 — Run Implementation Agent (Dispatcher)

```bash
# Start new session, activate implementation-agent
```

**Agent**: `implementation-agent` (spawns parallel `developer-agent` subagents)
**Expected outputs**: `src/**/*`, `tests/**/*`, commits per story

### Step 4.2 — Run Code Review Agent (Separate Session)

```bash
# Start NEW session, activate code-review-agent
```

**Agent**: `code-review-agent`
**Expected outputs**: `docs/reviews/code-review-*.md`, `docs/findings/IMPL-*.md`

### Decision Point 4.3

Check: `docs/findings/IMPL-*.md` files with `status: open`

```bash
grep -l "status: open" docs/findings/IMPL-*.md
```

**If implementation defects exist** → Go to Step 4.4
**If no defects** → The reconciliation-agent's preconditions are satisfied.

### Step 4.4 — Loop: Fix Implementation Defects

```bash
# Start NEW session, activate implementation-agent
```

**Instructions**: Implementation agent reads open `IMPL-*` findings and fixes code

Return to Step 4.2 (run code-review-agent again)

### Step 4.5 — Run Reconciliation Agent (Separate Session)

```bash
# Start NEW session, activate reconciliation-agent
```

**Agent**: `reconciliation-agent`
**Expected outputs**: `docs/reviews/reconciliation-*.md` (one row per drift, each naming its owner), `docs/findings/BUG-*.md` (code defects, if found)

### Decision Point 4.6

Check: `docs/findings/*.md` files with `status: open`

```bash
grep -l "status: open" docs/findings/*.md
```

**If open findings exist** → Go to Step 4.7
**If no open findings** → The qa-agent's preconditions are satisfied.

### Step 4.7 — Loop: Address Open Findings

```bash
# Start NEW session, activate implementation-agent
```

**Instructions**: Send each open finding to the agent in its `owner:` field. A `BUG` finding names the developer agent. Each owner fixes its artifact, and reconciliation rows in `docs/reviews/` go to the owner named in each row.

Return to Step 4.5 (run reconciliation-agent again)

## Quality

### Step 5.1 — Run QA Agent

```bash
# Start new session, activate qa-agent
```

**Agent**: `qa-agent` (Fagan + Security + Bug Hunt)
**Expected outputs**: `docs/reviews/fagan-review-*.md`, `docs/reviews/security-review-*.md`, `docs/findings/FAGAN-*.md`, `docs/findings/SEC-*.md`, `docs/findings/BUG-*.md`

### Decision Point 5.2

Check: Open defects in findings

```bash
grep -l "status: open" docs/findings/{FAGAN,SEC,BUG}-*.md
```

**If open defects exist** → Go to Step 5.3
**If no defects** → DONE (Step 5.4).

### Step 5.3 — Loop: Fix Defects

```bash
# Start NEW session, activate implementation-agent
```

**Instructions**: Implementation agent reads open findings and fixes them

Return to Step 5.1 (run qa-agent again)

### Step 5.4 — DONE

✅ **Terminal Condition: Project Ready for Feature Delivery**

The playbook ends when the following terminal artifacts exist:

**Terminal Artifacts:**

- [ ] `docs/spec/scope-map.md` exists with all Rules from the initial specification marked `deferred` (ready to be implemented as features)
- [ ] `docs/spec/architecture.dsl` models the planned module structure (C4 components and dependencies as designed)
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

**Next:**

After this playbook completes, **all feature work enters through the `feature-addition` playbook**. Each feature-addition slice produces a per-feature `.feature` file from one or more deferred Rules in the scope map. The scope map is the specification baseline that guides feature delivery.

## Halt Conditions

**Stop immediately if:**

1. Adapter auth failure (not author-fixable)
2. Adapter config error (not author-fixable)
3. Circular dependencies detected in backlog
4. Iteration cap exceeded (e.g., 5 review-fix loops on the same activity)

**Action**: Escalate to the user.

## Utility: Retrospective

Run ad-hoc at end of any session. The coaching-agent runs in the current session (adopt pattern — read the definition, assume its role, do not spawn a subagent):

```bash
# In active session
"Run a retrospective"
```

**Agent**: `coaching-agent` (adopted in current session)
**Output**: `docs/reviews/retro-*.md`

## State Tracking

**Current activity**: Track in session notes
**Open findings**: `grep -r "status: open" docs/findings/`
**Eligible agents**: Run `intent select` to see precondition status
