---
title: Architecture Review Playbook
category: orchestration
type: runbook
scenario: architecture-review
version: 1.0.0
---

# Architecture Review Playbook

Operational procedure for **evaluating existing architecture** without implementing changes.

## Prerequisites

- [ ] Architecture documentation exists in `docs/`
- [ ] ADRs exist in `docs/adr/`
- [ ] Spec exists in `docs/spec/`
- [ ] `docs/spec/architecture.dsl` exists

## Use Cases

Run this playbook when:

- Annual architecture review
- Before major feature addition
- After significant technical debt accumulation
- Onboarding new architect
- Pre-acquisition due diligence

## Step 1 — Validate Architecture Documentation

### Step 1.1 — Check Completeness

Check that `docs/spec/architecture.dsl` exists. Review the arc42 chapters
declared by the project. The DSL supplies the building block, runtime, and
deployment views. When its workspace sets `arc42.projected` to `true`,
check the generated chapters as well.

If a required artifact is missing, use the
[documentation update playbook](documentation-update.md).

### Step 1.2 — Lint Architecture

```bash
.agent-factory/factory/scripts/arch-lint --docs-dir docs/arc42
```

**If errors** → Send the lint output to the architecture agent and rerun the check after the fix.
**If clean** → Go to Step 2

## Step 2 — Run Architecture Review

### Step 2.1 — Execute ATAM Review

```bash
# Start new session, activate architecture-review-agent
```

**Agent**: `architecture-review-agent`
**Expected outputs**: `docs/reviews/atam-review.md`, `docs/findings/ATAM-*.md`

### Step 2.2 — Analyze Findings

Review generated findings:

```bash
ls -la docs/findings/ATAM-*.md
cat docs/reviews/atam-review.md
```

Categorize findings:

- **Sensitivity points** — Where changes would significantly impact quality attributes
- **Tradeoff points** — Decisions that benefit one quality attribute at expense of another
- **Risks** — Architectural decisions that may not meet quality goals

## Step 3 — Risk Prioritization

### Step 3.1 — Count Findings by Severity

```bash
grep "^severity:" docs/findings/ATAM-*.md | sort | uniq -c
```

### Step 3.2 — Prioritize Risks

Use the report to discuss critical and major risks with the stakeholder.
Record deferred decisions and questions in `docs/spec/work/todo.md` using
the [todo format](../rulebooks/conventions/todo-format.md). Claim each ID
with `.agent-factory/factory/scripts/next-id T`.

## Decision Point

### Do you need to fix findings immediately?

**YES — Critical risks identified** → Go to Step 4
**NO — Document for future work** → Go to Step 5 (DONE)

## Step 4 — Address Findings (Optional)

### Step 4.1 — Run Architecture Agent

```bash
# Start new session, activate architecture-agent
```

**Agent**: `architecture-agent`
**Task**: Address open `ATAM-*` findings

### Step 4.2 — Re-review

```bash
# Start NEW session, activate architecture-review-agent
```

**Agent**: `architecture-review-agent`

### Decision Point 4.3

Check remaining open findings:

```bash
grep -l "^status: open" docs/findings/ATAM-*.md
```

**If blocking risks remain** → Return to Step 4.1
**If acceptable** → Go to Step 5

## Stop notice

When `dispatch` or `premerge-check` exits `1` and prints a notice that starts with `STOP:`, run no further step. In an interactive session, explain each stopping finding with `explain-review-finding` and wait; only the stakeholder confirms a stop ([finding-format.md § Confirming a stop](../rulebooks/conventions/finding-format.md#confirming-a-stop)). A headless run does not wait. It ends with the notice in its final summary.

## New minor findings

The final summary lists each new register file with its `why_this_severity` sentence. A headless run lists them only after the loop ends, so a wrong downgrade can still reach implementation, and the summary says so ([finding-format.md § Pause point](../rulebooks/conventions/finding-format.md#pause-point)).

## Step 5 — DONE (Review Complete)

✅ **Architecture review complete**

Deliverables:

- [ ] `docs/reviews/atam-review.md` (review report)
- [ ] `docs/findings/ATAM-*.md` (risk findings)
- [ ] Prioritized action items in `docs/spec/work/todo.md`
- [ ] Stakeholder presentation (optional)

**Next steps**: Schedule follow-up or proceed with fix implementation
