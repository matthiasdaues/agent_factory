---
title: Bug Fix Playbook
category: orchestration
type: runbook
scenario: bug-fix
version: 1.0.0
---

# Bug Fix Playbook

Operational procedure for **fixing defects** in production or development.

## Prerequisites

- [ ] Bug reported
- [ ] Bug reproduced locally
- [ ] Existing codebase with tests

## Step 1 — File Bug Finding (If Not Already Filed)

For a new finding, run `.agent-factory/factory/scripts/next-id BUG`.
Read the ID from standard output. If the command fails, stop and report its
message.

Classify the report using the
[finding classification](../rulebooks/conventions/finding-classification.md).
For a blocking defect, use the
[finding template](../rulebooks/templates/finding.md) and set
`owner: developer-agent`. Record the reproduction and expected behavior.
For a minor finding, use the
[register format](../rulebooks/conventions/finding-format.md#register-files).

## Step 2 — Implement Fix

### Step 2.1 — Run Developer Agent

**Manual approach** (recommended for single bug):

```bash
# In new session
"Implement bug fix for BUG-NNNN using TDD"
```

**Agent**: `developer-agent`
**Expected**: Commit with message `fix: <description> (BUG-NNNN)`

### Step 2.2 — Verify Fix

Run the regression test and the project's configured test suite. Look for
`test_command` in `docs/testing.yaml`.

**If tests pass** → Go to Step 3
**If tests fail** → Return to Step 2.1

## Step 3 — QA Validation

### Step 3.1 — Run QA Agent

```bash
# Start new session, activate qa-agent
```

**Agent**: `qa-agent`
**Focus**: Regression testing, verify fix doesn't break other functionality

### Decision Point 3.2

Check the QA report for blocking findings from this review. Send any
blocking findings to their owners, then repeat the review.

## Step 4 — Mark Bug Resolved

On a repeat pass, the reviewer verifies the fix and sets the finding status to
`resolved`. For a register finding, the fix commit sets the register entry
to `resolved`. See [finding status](../rulebooks/conventions/finding-format.md#status-lifecycle).

## Stop notice

When `dispatch` or `premerge-check` exits `1` and prints a notice that starts with `STOP:`, run no further step. In an interactive session, explain each stopping finding with `explain-review-finding` and wait; only the stakeholder confirms a stop ([finding-format.md § Confirming a stop](../rulebooks/conventions/finding-format.md#confirming-a-stop)). A headless run does not wait. It ends with the notice in its final summary.

## New minor findings

The final summary lists each new register file with its `why_this_severity` sentence. A headless run lists them only after the loop ends, so a wrong downgrade can still reach implementation, and the summary says so ([finding-format.md § Pause point](../rulebooks/conventions/finding-format.md#pause-point)).

## DONE

✅ **Bug fixed**

Final checks:

- [ ] Bug finding or register entry status is `resolved`
- [ ] Fix committed with `fix: ... (BUG-NNNN)` format
- [ ] Test added that would catch this bug (regression test)
- [ ] All tests pass
- [ ] No new defects introduced

**Ready to merge**

## Fast-Track: Hotfix

For **critical production bugs**, use the fast-track approach:

```bash
# 1. Write failing test
# 2. Fix bug
# 3. Commit: fix: <description> (BUG-NNNN)
# 4. All tests pass
# 5. Deploy
```

**Post-deployment**: Run QA agent to verify no regression.
