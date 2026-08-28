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

- [ ] Bug reported and filed as `docs/findings/BUG-*.md`
- [ ] Bug reproduced locally
- [ ] Existing codebase with tests

## Step 1 — File Bug Finding (If Not Already Filed)

If bug not yet in `docs/findings/`:

```bash
# Create finding manually or via QA agent
cat > docs/findings/BUG-NNNN.md << EOF
---
id: BUG-NNNN
source: bug-report
severity: <critical|major|minor>
category: defect
artifact: <file:line>
status: open
---

# <Bug title>

**What is wrong:** <description>

**Fix:** <expected behavior>
EOF
```

## Step 2 — Implement Fix

### Step 2.1 — Run Developer Agent

**Manual approach** (recommended for single bug):

```bash
# In new session
"Implement bug fix for BUG-NNNN using TDD"
```

**Orchestrator approach**:

```bash
# Create temporary story for the bug
cat > backlog/BUG-NNNN.md << EOF
---
id: BUG-NNNN
status: pending
deps: []
---

Fix BUG-NNNN

**Acceptance Criteria:**
- [ ] Bug reproduced with failing test
- [ ] Fix applied
- [ ] Test passes
- [ ] No regression in other tests
EOF

factory/scripts/phase advance --playbook implementation
```

**Agent**: `developer-agent`
**Expected**: Commit with message `fix: <description> (BUG-NNNN)`

### Step 2.2 — Verify Fix

Run test suite:

```bash
npm test
# OR
pytest
# OR
go test ./...
```

**If tests pass** → Go to Step 3
**If tests fail** → Return to Step 2.1

## Step 3 — QA Validation

### Step 3.1 — Run QA Agent

```bash
factory/scripts/phase advance --playbook qa
```

**Agent**: `qa-agent`
**Focus**: Regression testing, verify fix doesn't break other functionality

### Decision Point 3.2

Check for new defects:

```bash
grep -l "status: open" docs/findings/{FAGAN,SEC,BUG}-*.md | grep -v "BUG-NNNN"
```

**If new defects found** → Loop to Step 2.1
**If clean** → Go to Step 4

## Step 4 — Mark Bug Resolved

Update finding status:

```bash
# Update BUG-NNNN.md
sed -i 's/status: open/status: resolved/' docs/findings/BUG-NNNN.md
```

## DONE

✅ **Bug fixed**

Final checks:

- [ ] Bug finding status: `resolved`
- [ ] Fix committed with `fix: ... (BUG-NNNN)` format
- [ ] Test added that would catch this bug (regression test)
- [ ] All tests pass
- [ ] No new defects introduced

**Ready to merge**

## Fast-Track: Hotfix

For **critical production bugs**, skip the phase gate:

```bash
# 1. Write failing test
# 2. Fix bug
# 3. Commit: fix: <description> (BUG-NNNN)
# 4. All tests pass
# 5. Deploy
```

**Post-deployment**: Run QA agent to verify no regression.
