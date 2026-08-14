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
orchestrator run-phase reconciliation
# OR manual: Start new session, activate reconciliation-agent
```

**Agent**: `reconciliation-agent`
**Task**: Compare code-as-built with specification

**Expected outputs**:

- `docs/reviews/reconciliation-*.md` (discrepancy report)
- Updated `docs/spec/supplementary_specs/` (if spec was stale)
- Updated `CONTEXT.md` (if terminology drifted)
- `docs/findings/RECON-*.md` (code defects, if found)

### Step 1.2 — Review Discrepancy Report

Read reconciliation report:

```bash
cat docs/reviews/reconciliation-*.md
```

Look for:

- **Spec stale** — Documentation doesn't match code behavior
- **Undocumented** — Features in code not in spec
- **Terminology drift** — Terms used differently in code vs `CONTEXT.md`

## Decision Point 1.3

Check for code defects found during reconciliation:

```bash
grep -l "status: open" docs/findings/RECON-*.md
```

**If code defects** → Go to Step 1.4 (fix code first)
**If only doc drift** → Go to Step 2

### Step 1.4 — Fix Code Defects (If Found)

Code defects = implementation doesn't match spec **intent**

```bash
orchestrator run-phase implementation
```

**Agent**: `implementation-agent`
**Task**: Fix open `RECON-*` findings

Return to Step 1.1 (re-run reconciliation)

## Step 2 — Validate Updated Documentation

### Step 2.1 — Lint Spec

```bash
factory/scripts/spec-lint --spec-dir docs/spec --graph docs/spec/traceability.json
```

**If errors** → Fix manually or re-run reconciliation-agent
**If clean** → Go to Step 2.2

### Step 2.2 — Lint Architecture

```bash
factory/scripts/arch-lint --docs-dir docs/arc42
```

**If errors** → Fix manually or run architecture-agent
**If clean** → Go to Step 3

## Step 3 — Optional: Formal Review

### Decision: Is formal review needed?

**Small updates** (minor corrections) → Skip to DONE
**Large updates** (structural changes) → Run review

### Step 3.1 — Spec Review (If Spec Changed Significantly)

```bash
orchestrator run-phase spec-review
```

**Agent**: `spec-review-agent`

Check findings:

```bash
grep -l "status: open" docs/findings/SPEC-*.md
```

**If findings** → Address and loop
**If clean** → Continue

### Step 3.2 — Architecture Review (If Architecture Changed)

```bash
orchestrator run-phase architecture-review
```

**Agent**: `architecture-review-agent`

Check findings:

```bash
grep -l "status: open" docs/findings/ATAM-*.md
```

**If findings** → Address via architecture-agent
**If clean** → Go to DONE

## DONE

✅ **Documentation synchronized with code**

Final checks:

- [ ] `spec-lint` passes
- [ ] `arch-lint` passes
- [ ] All `RECON-*` findings resolved
- [ ] Terminology consistent between code and `CONTEXT.md`
- [ ] Supplementary specs match implementation
- [ ] State machines match code behavior

**Documentation is now accurate**

## Fast-Track: Single File Update

For updating a **single document** without full reconciliation:

```bash
# Manual: Open session, ask agent
"Update docs/spec/supplementary_specs/interface-contracts.md to match current API implementation"
```

Use full reconciliation playbook for comprehensive sync.
