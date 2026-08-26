---
title: Feature Addition Playbook
category: orchestration
type: runbook
scenario: feature-addition
version: 1.2.0
steps:
  - name: clarify-requirements
    inputs:
      - 'docs/proposals/**/*.md'
      - 'docs/spec/**/*.md'
      - 'docs/charter/**/*.md'
    outputs:
      - 'docs/proposals/**/*.md'
    max_input_tokens: 40000
  - name: charter-amendment-check
    inputs:
      - 'docs/proposals/**/*.md'
      - 'docs/charter/**/*.md'
    outputs:
      - 'docs/charter/**/*.md'
      - 'backlog/ST-0*.md'
    max_input_tokens: 40000
  - name: accept-proposal
    inputs:
      - 'docs/proposals/**/*.md'
    outputs:
      - 'docs/proposals/**/*.md'
    max_input_tokens: 20000
  - name: route-from-declared-impact
    inputs:
      - 'docs/proposals/**/*.md'
    outputs: []
    max_input_tokens: 20000
  - name: update-specification
    inputs:
      - 'docs/proposals/**/*.md'
      - 'docs/spec/**/*.md'
    outputs:
      - 'docs/spec/**/*.md'
    max_input_tokens: 40000
  - name: spec-review
    inputs:
      - 'docs/proposals/**/*.md'
      - 'docs/spec/**/*.md'
    outputs:
      - 'docs/findings/SPEC-*.md'
    max_input_tokens: 40000
  - name: decision-point-1-3
    inputs:
      - 'docs/findings/SPEC-*.md'
    outputs: []
    max_input_tokens: 20000
  - name: update-architecture
    inputs:
      - 'docs/proposals/**/*.md'
      - 'docs/spec/**/*.md'
      - 'docs/adr/**/*.md'
      - 'docs/arc42/**/*.md'
    outputs:
      - 'docs/adr/**/*.md'
      - 'docs/arc42/**/*.md'
    max_input_tokens: 40000
  - name: architecture-review
    inputs:
      - 'docs/adr/**/*.md'
      - 'docs/arc42/**/*.md'
    outputs:
      - 'docs/findings/ATAM-*.md'
    max_input_tokens: 40000
  - name: decision-point-2-3
    inputs:
      - 'docs/findings/ATAM-*.md'
    outputs: []
    max_input_tokens: 20000
  - name: create-stories
    inputs:
      - 'docs/proposals/**/*.md'
      - 'docs/spec/**/*.md'
      - 'docs/arc42/**/*.md'
    outputs:
      - 'backlog/ST-*.md'
    max_input_tokens: 40000
  - name: validate-backlog
    inputs:
      - 'backlog/ST-*.md'
    outputs: []
    max_input_tokens: 20000
  - name: reconcile-plan-with-proposal
    inputs:
      - 'backlog/ST-*.md'
      - 'docs/proposals/**/*.md'
    outputs:
      - 'docs/proposals/**/*.md'
    max_input_tokens: 20000
  - name: approve-backlog
    inputs:
      - 'backlog/ST-*.md'
      - 'docs/proposals/**/*.md'
    outputs: []
    max_input_tokens: 20000
  - name: implement-stories
    inputs:
      - 'backlog/ST-*.md'
      - 'docs/spec/**/*.md'
      - 'factory/**/*.py'
      - 'orchestrator/**/*.py'
      - 'tests/**/*.py'
      - 'config/**/*.json'
    outputs:
      - 'factory/**/*.py'
      - 'orchestrator/**/*.py'
      - 'tests/**/*.py'
      - 'config/**/*.json'
      - 'docs/**/*.md'
      - 'backlog/ST-*.md'
    max_input_tokens: 100000
  - name: reconcile
    inputs:
      - 'backlog/ST-*.md'
      - 'docs/spec/**/*.md'
      - 'factory/**/*.py'
      - 'orchestrator/**/*.py'
      - 'tests/**/*.py'
      - 'config/**/*.json'
    outputs:
      - 'factory/**/*.py'
      - 'orchestrator/**/*.py'
      - 'tests/**/*.py'
      - 'config/**/*.json'
      - 'docs/**/*.md'
      - 'backlog/ST-*.md'
    max_input_tokens: 100000
  - name: decision-point-4-3
    inputs:
      - 'docs/findings/RECON-*.md'
    outputs: []
    max_input_tokens: 20000
  - name: qa
    inputs:
      - 'factory/**/*.py'
      - 'orchestrator/**/*.py'
      - 'tests/**/*.py'
      - 'docs/**/*.md'
      - 'config/**/*.json'
    outputs:
      - 'docs/findings/FAGAN-*.md'
      - 'docs/findings/BUG-*.md'
      - 'docs/findings/SEC-*.md'
      - 'docs/reviews/**/*.md'
    max_input_tokens: 100000
  - name: decision-point-5-2
    inputs:
      - 'docs/findings/FAGAN-*.md'
      - 'docs/findings/BUG-*.md'
      - 'docs/findings/SEC-*.md'
    outputs: []
    max_input_tokens: 20000
---

# Feature Addition Playbook

Operational procedure for **adding features to existing system**.

## Prerequisites

- [ ] Existing project with spec and architecture
- [ ] `CONTEXT.md` exists
- [ ] A proposal at `docs/proposals/<name>.md`, written to the [proposal template](../rulebooks/templates/proposal.md)

The proposal is the feature's authoritative design origin. Do not maintain a
parallel feature request, interview record, or design brief.

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

| Transition                                     | Route                                                 |
| ---------------------------------------------- | ----------------------------------------------------- |
| proposal intake → requirements-agent           | Declared impact requires specification work           |
| proposal intake → architecture-agent           | Specification is skipped; architecture change is true |
| proposal intake → planning-agent               | Specification and architecture are both skipped       |
| requirements-agent → spec-review-agent         | Specification update completes                        |
| spec-review-agent → requirements-agent         | Open specification findings require remedies          |
| spec-review-agent → architecture-agent         | Review is clean; architecture change is true          |
| spec-review-agent → planning-agent             | Review is clean; architecture change is false         |
| architecture-agent → architecture-review-agent | Architecture update completes                         |
| architecture-review-agent → architecture-agent | Open architecture findings require remedies           |
| architecture-review-agent → planning-agent     | Architecture review is clean                          |
| planning-agent → implementation-agent          | Backlog is approved                                   |
| implementation-agent → reconciliation-agent    | Implementation wave completes                         |
| reconciliation-agent → implementation-agent    | Reconciliation finds code defects                     |
| reconciliation-agent → qa-agent                | Reconciliation is clean                               |
| qa-agent → implementation-agent                | Quality review finds defects                          |
| implementation-agent → qa-agent                | Quality remedies are ready for retest                 |

Each listed route requires the reviewed handoff and restart even where agent
frontmatter groups author and reviewer roles under one broader phase name.
Work that remains inside one route's outgoing phase is exempt under
[handoff-format.md](../rulebooks/conventions/handoff-format.md).

## Proposal Intake

### Step 0.1 — Clarify

Read the proposal and its referenced boundaries.

- **`draft`** → Invoke `clarify-requirements` with the proposal as its target.
  The interview amends that file until the design is decision-complete, then
  moves it to `open`.
- **`open`** → Review or grill the proposal in place. Resolve every Open
  Question as a decision, explicit assumption, or deferral.
- **`accepted`** → Preserve its recorded baseline and continue to Step 0.2.
- **`implemented`, `cancelled`, or `superseded`** → Stop; this playbook cannot
  open implementation from a closed proposal.

Grilling may make an artifact ready for acceptance, but cannot accept it.

**Token discipline — grill before dispatch.** The orchestrating session (not a
spawned subagent) owns the grilling interview. Complete all design questions and
resolve Open Questions here, in direct conversation with the stakeholder. The
requirements-agent then receives a decision-complete proposal and performs
mechanical spec derivation without interactive round-trips. Each subagent
suspend/resume cycle replays its full context; grilling inside a subagent
multiplies cost by the number of questions asked.

### Step 0.1a — Charter Amendment Check

**Manual decision**: Does this feature require charter amendments?

Read [`docs/charter/`](../../docs/charter/) to understand current declarations
for tech stack, development practices, and house rules.

**If no amendments needed** → Skip to Step 0.2.

**If amendments needed**:

1. Invoke [`update-charter`](../skills/update-charter/SKILL.md) to update the
   relevant section(s) of `docs/charter/tech-stack.md`,
   `docs/charter/development.md`, or `docs/charter/house-rules.md`.
2. Run `factory/scripts/charter-lint --planning-gate` on changed documents to
   ensure completeness.
3. If new decisions emerge that imply infrastructure, setup, or configuration
   artifacts not already in the repository, derive corresponding Epic 0 stories
   (using the [`capture-charter`](../skills/capture-charter/SKILL.md) Step 3
   workflow as reference).
4. Proceed to Step 0.2.

### Decision Point 0.2 — Accept

**Manual**: Stakeholder accepts the proposal.

Record the full 40-character SHA of the commit containing the accepted proposal
as the immutable planning baseline. Do not embed that SHA in the proposal.

**If accepted** → Set `status: accepted`, update `updated`, commit, then route
the work using Step 0.3.
**If changes requested** → Return to Step 0.1.

### Step 0.3 — Route from Declared Impact

Routing to Phase 1 (Requirements) and Phase 2 (Architecture) is based on the
proposal's declared impact and refined by a mechanical verification of the
architecture change declaration after Phase 1 completes.

**Routing to Phase 1:**

Specification work is required when the accepted design changes behavior, use
cases, quality requirements, or an external contract. Otherwise, specification
is not required.

- **If specification work is required:** Proceed to Phase 1.
- **If specification work is not required:** Skip Phase 1 and proceed to Step
  1.4 (Mechanical Architecture Check).

**Routing to Phase 2 and Phase 3:**

After Phase 1 completes (or is skipped), execute Step 1.4 to run the mechanical
architecture check. This check examines the proposal's Phase 1 outputs and may
update the proposal's `impact.architecture_change` field. Then:

- `impact.architecture_change: true` (after possible mechanical update)
  requires Phase 2.
- `impact.architecture_change: false` skips Phase 2 and proceeds directly to
  Phase 3.

**Planning constraint:** Do not infer a small/large shortcut independently of
the accepted proposal. `impact`, `governance`, and Completion Criteria are the
routing inputs.

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

**Token discipline — fresh agents for review-fix loops.** When a review finds
defects and the loop returns to the authoring step, spawn a fresh agent for the
fix pass rather than resuming the original. The original agent's context
contains the full grilling transcript, every prior tool call, and every file
read; resuming it replays all of that before the fix work begins. A fresh agent
reads only the findings and the affected files, cutting the fix-cycle cost by
50–70%.

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
**If clean** → Proceed to Step 1.4

### Step 1.4 — Mechanical Architecture Check

*Execute this step after Phase 1 is complete (if it ran), or immediately if
Phase 1 was skipped.*

Run the mechanical module-graph check to verify whether the feature's Phase 1
outputs declare architectural changes:

```bash
factory/scripts/module-graph-check
```

**What the check does:**

1. Reads the current module structure from `docs/arc42/architecture.dsl`
2. Analyzes the feature's Phase 1 outputs (`docs/spec/supplementary_specs/interface-contracts.md`,
   `docs/spec/supplementary_specs/entity-model.md`) to identify new or changed
   interfaces and entities
3. Determines whether the feature changes module boundaries, dependency
   directions, or public interfaces
4. Updates the proposal's `impact.architecture_change` field based on the
   findings

**Override semantics:**

- **Field is `false`, check detects change (`true`):** Machine detection wins.
  Update the field to `true`, annotated `# mechanical detection`.
- **Field is `true`, check detects no change (`false`):** Human declaration
  stands conservatively. Log the check result, but leave the field as `true`.
  A later manual review may update it to `false` if Phase 2 produces no changes.
- **Human override:** After seeing the check result, record any override as a
  comment on the field
  (e.g., `architecture_change: false  # manual override — no boundary change despite new interface`).

**Constraints and safety:**

- The check uses Phase 1 outputs only; it does not depend on story files or
  implementation artifacts.
- After implementation (Phase 5), the `reconciliation-agent` reconciles
  `architecture.dsl` and arc42 documentation against the code-as-built, catching
  any module-graph changes missed by this Phase 1 check.

**Routing result:**

Proceed based on the (possibly updated) `impact.architecture_change` value:
- If `true`, go to Phase 2
- If `false`, skip Phase 2 and go to Phase 3

## Phase 2: Architecture (If Architectural Changes Needed)

Enter this phase when `impact.architecture_change` is `true` (as determined by
Step 0.3 declaration and refined by Step 1.4's mechanical check). If
implementation discovery contradicts that determination, the proposal has
materially changed: return it to `open`, amend it, and repeat acceptance before
continuing.

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
