---
title: Documentation Update Playbook
category: orchestration
type: runbook
scenario: documentation-update
version: 1.0.0
---

# Documentation Update Playbook

Operational procedure for **syncing documentation with code** when they've drifted.

## Prerequisites

- [ ] Implemented code exists
- [ ] Documentation (spec and/or architecture) exists but may be outdated
- [ ] Code is stable (tests passing)

## Use Cases

Run this playbook when:

- Code evolved without updating docs
- After implementation sprint
- Pre-release documentation freeze
- Before architecture review
- When onboarding new team members

## Step 1 — Run Reconciliation Agent

### Step 1.1 — Code vs Spec Reconciliation

```bash
# Start new session, activate reconciliation-agent
```

**Agent**: `reconciliation-agent`
**Task**: Compare code-as-built with specification

**Expected outputs**:

- `docs/reviews/reconciliation-*.md` (discrepancy report, one row per drift, each naming the owner of the artifact)
- `docs/findings/BUG-*.md` (code defects, if found)

This agent changes no core file. The owner named in each row fixes its stale core file, for example the domain-modeling agent for `docs/spec/glossary.md`.

### Step 1.2 — Review Discrepancy Report

Read reconciliation report:

```bash
cat docs/reviews/reconciliation-*.md
```

Look for:

- **Spec stale** — Documentation doesn't match code behavior
- **Undocumented** — Features in code not in spec
- **Terminology drift** — Terms used differently in code vs `docs/spec/glossary.md`

## Decision Point 1.3

Check for open findings found during reconciliation:

```bash
grep -l "^status: open" docs/findings/*.md
```

**If open findings** → Go to Step 1.4 (fix code first)
**If only doc drift** → Go to Step 1.5

### Step 1.4 — Fix Code Defects (If Found)

Code defects = implementation doesn't match spec **intent**

```bash
# Start new session, activate implementation-agent
```

**Agent**: `implementation-agent`
**Task**: Send each open finding to the agent in its `owner:` field. A `BUG` finding names the developer agent.

Return to Step 1.1 (re-run reconciliation)

### Step 1.5 — Bring Each Row Back To Its Owner

**Agent**: the orchestrator, the session that runs this playbook
**Task**: Bring each reconciliation row back to its owner and then to the owner's reviewer.

Read every `docs/reviews/reconciliation-*.md`, not only the new report. A stopped session leaves rows in an earlier report, and this step picks them up. Read `rulebooks/core-artifacts.yaml` under the Factory root. A row is on the core list when its artifact matches an entry there.

Work one session at a time, in two passes:

1. First dispatch the owner of each `open` row, the agent in its Owner column. The brief names the row and the report and no skill. The owner changes the artifact with the skill or workflow step its own definition names for it. It sets the row to `fixed` in the same commit as the change.
2. Then dispatch the reviewer of each `fixed` row on the core list. The reviewer is the `reviewed_by:` entry of the owner's declaration that matches the row's artifact. It sets the row to `confirmed` or `rejected`.

When `reviewed_by:` is `[stakeholder]`, dispatch no reviewer agent. Present the owner's fix to the stakeholder in this session, and set `confirmed` or `rejected` as the stakeholder decides. When `reviewed_by:` names an agent and `stakeholder`, dispatch the agent first; the stakeholder sees the fix only after the agent set `confirmed`.

A `rejected` row becomes a `BUG` finding with `owner: developer-agent`. The reviewer agent files it, or the orchestrator files it for the stakeholder.

A `fixed` row on an artifact outside the core list closes at `fixed`, because the artifact has no declared review (DEC-35). An ADR is such an artifact.

The owner and the reviewer commit on the branch that holds the report, normally the feature branch before its merge into `dev`. A row stays in the report that first wrote it, and only its Status changes. No script reads the reports, so an unhandled row blocks no merge and no reconciliation run.

Go to Step 2.

## Step 2 — Validate Updated Documentation

### Step 2.1 — Lint Spec

```bash
.agent-factory/factory/scripts/spec-lint --spec-dir docs/spec
```

**If errors** → Fix manually or re-run reconciliation-agent
**If clean** → Go to Step 2.2

### Step 2.2 — Lint Architecture

```bash
.agent-factory/factory/scripts/arch-lint --docs-dir docs/arc42
```

**If errors** → Fix manually or run architecture-agent
**If clean** → Go to Step 3

## Step 3 — Optional: Formal Review

### Decision: Is formal review needed?

**Small updates** (minor corrections) → Skip to DONE
**Large updates** (structural changes) → Run review

### Step 3.1 — Spec Review (If Spec Changed Significantly)

```bash
# Start NEW session, activate spec-review-agent
```

**Agent**: `spec-review-agent`

Check findings:

```bash
grep -l "^status: open" docs/findings/SPEC-*.md
```

**If findings** → Address and loop
**If clean** → Continue

### Step 3.2 — Architecture Review (If Architecture Changed)

```bash
# Start NEW session, activate architecture-review-agent
```

**Agent**: `architecture-review-agent`

Check findings:

```bash
grep -l "^status: open" docs/findings/ATAM-*.md
```

**If findings** → Address via architecture-agent
**If clean** → Go to DONE

## Stop notice

When `dispatch` or `premerge-check` exits `1` and prints a notice that starts with `STOP:`, run no further step. In an interactive session, explain each stopping finding with `explain-review-finding` and wait; only the stakeholder confirms a stop ([finding-format.md § Confirming a stop](../rulebooks/conventions/finding-format.md#confirming-a-stop)). A headless run does not wait. It ends with the notice in its final summary.

## New minor findings

The final summary lists each new register file with its `why_this_severity` sentence. A headless run lists them only after the loop ends, so a wrong downgrade can still reach implementation, and the summary says so ([finding-format.md § Pause point](../rulebooks/conventions/finding-format.md#pause-point)).

## DONE

✅ **Documentation synchronized with code**

Final checks:

- [ ] `spec-lint` passes
- [ ] `arch-lint` passes
- [ ] No open finding remains in `docs/findings/`
- [ ] No row of any `docs/reviews/reconciliation-*.md` is `open`, or `fixed` on an artifact of the core list. While one is, the playbook stays open and names the report, the artifact, and the status of each such row.
- [ ] Terminology consistent between code and `docs/spec/glossary.md`
- [ ] Supplementary specs match implementation
- [ ] State machines match code behavior

**Documentation is now accurate**

## Fast-Track: Single File Update

For updating a **single document** without full reconciliation:

```bash
# Manual: Open session, ask agent
"Update docs/spec/interface-contracts.md to match current API implementation"
```

Use full reconciliation playbook for comprehensive sync.
