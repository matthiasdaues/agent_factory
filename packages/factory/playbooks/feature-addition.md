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
      - 'docs/spec/**/*.feature'
      - 'docs/agent-context.md'
    outputs:
      - 'docs/proposals/**/*.md'
    max_input_tokens: 40000
  - name: context-amendment-check
    inputs:
      - 'docs/proposals/**/*.md'
      - 'docs/agent-context.md'
    outputs:
      - 'docs/agent-context.md'
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
      - 'docs/findings/SPEC-*.md'
      - 'docs/proposals/**/*.md'
      - 'docs/spec/**/*.md'
      - 'docs/spec/**/*.feature'
    outputs:
      - 'docs/proposals/**/*.md'
      - 'docs/spec/**/*.md'
      - 'docs/spec/**/*.feature'
    max_input_tokens: 40000
  - name: spec-review
    inputs:
      - 'docs/CONTEXT.md'
      - 'docs/proposals/**/*.md'
      - 'docs/spec/**/*.md'
      - 'docs/spec/**/*.feature'
    outputs:
      - 'docs/findings/SPEC-*.md'
      - 'docs/reviews/spec-review-*.md'
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
      - 'docs/spec/**/*.feature'
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
      - 'docs/spec/**/*.feature'
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
      - 'docs/spec/**/*.feature'
      - '.agent-factory/factory/**/*.py'
      - 'tests/**/*.py'
      - 'config/**/*.json'
    outputs:
      - '.agent-factory/factory/**/*.py'
      - 'tests/**/*.py'
      - 'config/**/*.json'
      - 'docs/**/*.md'
      - 'backlog/ST-*.md'
    max_input_tokens: 100000
  - name: code-review
    inputs:
      - 'backlog/ST-*.md'
      - 'docs/spec/**/*.md'
      - 'docs/spec/**/*.feature'
      - '.agent-factory/factory/**/*.py'
      - 'tests/**/*.py'
      - 'config/**/*.json'
    outputs:
      - 'docs/reviews/code-review-*.md'
      - 'docs/findings/IMPL-*.md'
    max_input_tokens: 100000
  - name: decision-point-4-3
    inputs:
      - 'docs/findings/IMPL-*.md'
    outputs: []
    max_input_tokens: 20000
  - name: reconcile
    inputs:
      - 'backlog/ST-*.md'
      - 'docs/spec/**/*.md'
      - 'docs/spec/**/*.feature'
      - '.agent-factory/factory/**/*.py'
      - 'tests/**/*.py'
      - 'config/**/*.json'
    outputs:
      - '.agent-factory/factory/**/*.py'
      - 'tests/**/*.py'
      - 'config/**/*.json'
      - 'docs/**/*.md'
      - 'backlog/ST-*.md'
    max_input_tokens: 100000
  - name: decision-point-4-5
    inputs:
      - 'docs/findings/RECON-*.md'
    outputs: []
    max_input_tokens: 20000
  - name: qa
    inputs:
      - '.agent-factory/factory/**/*.py'
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

- [ ] `docs/arc42/architecture.dsl` exists
- [ ] `docs/spec/scope-map.md` exists
- [ ] `docs/CONTEXT.md` exists
- [ ] A proposal at `docs/proposals/<name>.md`, written to the [proposal template](../rulebooks/templates/proposal.md)

The three anchor files (`architecture.dsl`, `scope-map.md`, `docs/CONTEXT.md`)
are the minimum baseline. Full specification artifacts (PRD, use cases,
supplementary specs) add detail to the requirements and architecture activities when present but are not required. If
any anchor file is missing, suggest running `brownfield-onboarding` to
establish the baseline.

The proposal is the feature's authoritative design origin. Do not maintain a
parallel feature request, interview record, or design brief.

Each feature-addition run updates the anchor files: the
requirements-agent adds a Rule to `scope-map.md` with status "specified," the
architecture-agent updates `architecture.dsl` when the structural shape changes,
and the grilling and domain-modeling skills add new terms to `docs/CONTEXT.md`.

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

Read project context from [`docs/agent-context.md`](../../../docs/agent-context.md) to understand current declarations
for tech stack, development practices, and house rules.

**If no amendments needed** → Skip to Step 0.2.

**If amendments needed**:

1. Invoke [`capture-context`](../skills/capture-context/SKILL.md) with `--update --scan` to update
   the relevant sections of `docs/agent-context.md`.
2. Run `.agent-factory/factory/scripts/concern-lint` on the changed document to
   ensure completeness.
3. If new decisions emerge that imply infrastructure, setup, or configuration
   artifacts not already in the repository, derive corresponding Epic 0 stories.
4. Proceed to Step 0.2.

### Decision Point 0.2 — Accept

**Manual**: Stakeholder accepts the proposal.

Record the full 40-character SHA of the commit containing the accepted proposal
as the immutable planning baseline. Do not embed that SHA in the proposal.

**If accepted** → Set `status: accepted`, update `updated`, commit, then route
the work using Step 0.3.
**If changes requested** → Return to Step 0.1.

### Step 0.3 — Route from Declared Impact

The accepted proposal's declared impact determines which activities are needed.
Run `intent select` to see which agents have their preconditions satisfied.

**Specification work** is needed when the accepted design changes behavior, use
cases, quality requirements, or an external contract. When it is not needed,
skip directly to the mechanical architecture check (Step 1.4).

**Architecture work** is needed when `impact.architecture_change` is `true`
(as declared in the proposal or updated by the mechanical check in Step 1.4).
When it is not needed, the planning-agent's preconditions are already
satisfied by the existing anchor files.

**Planning constraint:** Do not infer a small/large shortcut independently of
the accepted proposal. `impact`, `governance`, and Completion Criteria are the
inputs to this decision.

## Approval Contract

At the start of each activity, present one bounded approval covering its
reversible, in-scope work. State:

- outputs and acceptance invariants;
- deterministic gates that must pass;
- stop conditions: a changed requirement, unresolved design choice, destructive
  action, external side effect, failed gate, or scope expansion.

After approval, execute the activity through its stated gates without requesting
confirmation for each routine reversible step. Existing decision points remain:
stakeholders still approve requirements, architecture decisions, backlog scope,
destructive cleanup, and any response to a stop condition. Batching must not be
used to infer broader authority.

**Token discipline — fresh agents for review-fix loops.** When a review finds
defects and the work returns to the authoring agent, spawn a fresh agent for the
fix pass rather than resuming the original. The original agent's context
contains the full grilling transcript, every prior tool call, and every file
read; resuming it replays all of that before the fix work begins. A fresh agent
reads only the findings and the affected files, cutting the fix-cycle cost by
50–70%.

## Requirements (If Specification Changes Are Needed)

### Step 1.1 — Update Specification

```bash
# Start new session, activate requirements-agent
```

**Agent**: `requirements-agent`
**Task**: Derive feature spec, update scope map, produce QA strategy

**Expected outputs**: `docs/spec/<feature-name>.feature`, `docs/spec/scope-map.md`, `docs/spec/<feature-name>-gaps.md`, `docs/spec/<feature-name>-qa-strategy.md`, updated `docs/spec/supplementary_specs/`

### Step 1.2 — Spec Review

```bash
# Start NEW session, activate spec-review-agent
```

**Agent**: `spec-review-agent`

### Decision Point 1.3

Check for open `SPEC-*` findings:

```bash
grep -l "status: open" docs/findings/SPEC-*.md
```

**If open** → Return to the requirements-agent to address findings, then
re-run the spec-review-agent.
**If clean** → Proceed to the mechanical architecture check (Step 1.4).

### Step 1.4 — Mechanical Architecture Check

*Execute this step after specification work completes (if it ran), or
immediately if specification work was not needed.*

Run the mechanical module-graph check to verify whether the specification
outputs declare architectural changes:

```bash
.agent-factory/factory/scripts/module-graph-check
```

**What the check does:**

1. Reads the current module structure from `docs/arc42/architecture.dsl`
2. Analyzes the specification outputs (`docs/spec/supplementary_specs/interface-contracts.md`,
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
  A later manual review may update it to `false` if architecture work produces
  no changes.
- **Human override:** After seeing the check result, record any override as a
  comment on the field
  (e.g., `architecture_change: false  # manual override — no boundary change despite new interface`).

**Constraints and safety:**

- The check uses specification outputs only; it does not depend on story files
  or implementation artifacts.
- After implementation, the `reconciliation-agent` reconciles
  `architecture.dsl` and arc42 documentation against the code-as-built, catching
  any module-graph changes missed by this check.

**Routing result:**

Proceed based on the (possibly updated) `impact.architecture_change` value:

- If `true`, the architecture-agent's preconditions are satisfied — select it
  via `intent select`.
- If `false`, the planning-agent's preconditions are already satisfied by the
  existing anchor files.

## Architecture (If Architectural Changes Needed)

Select the architecture-agent when `impact.architecture_change` is `true` (as
determined by Step 0.3 and refined by Step 1.4's mechanical check). If
implementation discovery contradicts that determination, the proposal has
materially changed: return it to `open`, amend it, and repeat acceptance before
continuing.

### Step 2.1 — Update Architecture

```bash
# Start new session, activate architecture-agent
```

**Agent**: `architecture-agent`
**Task**: Update arc42 docs, add ADRs, update C4 model

### Step 2.2 — Architecture Review

```bash
# Start NEW session, activate architecture-review-agent
```

**Agent**: `architecture-review-agent`

### Decision Point 2.3

Check for open `ATAM-*` findings:

```bash
grep -l "status: open" docs/findings/ATAM-*.md
```

**If open** → Return to the architecture-agent to address findings, then
re-run the architecture-review-agent.
**If clean** → The planning-agent's preconditions are satisfied.

## Planning

### Step 3.1 — Create Stories

```bash
# Start new session, activate planning-agent
```

**Agent**: `planning-agent`
**Task**: Create new `ST-*` stories, update EPIC grouping

**Expected outputs**: New `backlog/ST-*.md` files

### Step 3.2 — Validate

```bash
.agent-factory/factory/scripts/backlog-lint --backlog-dir backlog
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

**If approved** → The implementation-agent's preconditions are satisfied.
**If changes** → Return to the planning-agent (Step 3.1).

## Implementation

### Step 4.1 — Implement Stories

```bash
# Start new session, activate implementation-agent
```

**Agent**: `implementation-agent`

### Step 4.2 — Code Review (Separate Session)

```bash
# Start NEW session, activate code-review-agent
```

**Agent**: `code-review-agent`
**Expected outputs**: `docs/reviews/code-review-*.md`, `docs/findings/IMPL-*.md`

### Decision Point 4.3

Check for implementation defects:

```bash
grep -l "status: open" docs/findings/IMPL-*.md
```

**If defects** → Return to the implementation-agent to address findings, then
re-run the code-review-agent.
**If clean** → The reconciliation-agent's preconditions are satisfied.

### Step 4.4 — Reconcile

```bash
# Start NEW session, activate reconciliation-agent
```

**Agent**: `reconciliation-agent`

### Decision Point 4.5

Check for reconciliation defects:

```bash
grep -l "status: open" docs/findings/RECON-*.md
```

**If defects** → Return to the implementation-agent to address findings, then
re-run the reconciliation-agent.
**If clean** → The qa-agent's preconditions are satisfied.

## Quality

### Step 5.1 — QA

```bash
# Start new session, activate qa-agent
```

**Agent**: `qa-agent`

### Decision Point 5.2

Check for open defects:

```bash
grep -l "status: open" docs/findings/{FAGAN,SEC,BUG}-*.md
```

**If defects** → Return to the implementation-agent to address findings, then
re-run the qa-agent.
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
