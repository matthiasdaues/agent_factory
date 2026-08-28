---
title: Refactoring Playbook
category: orchestration
type: runbook
scenario: refactoring
version: 1.0.0
---

# Refactoring Playbook

Operational procedure for **improving code structure without changing behavior**.

## Prerequisites

- [ ] Code exists with test coverage
- [ ] Refactoring goal defined (improve maintainability, reduce complexity, apply pattern)
- [ ] All tests currently passing

## Definition

**Refactoring**: Restructuring existing code without changing its external behavior.

**Not refactoring**:

- Adding new features (use feature-addition playbook)
- Fixing bugs (use bug-fix playbook)
- Changing behavior

## Step 1 — Establish Baseline

### Step 1.1 — Run All Tests

Ensure tests pass before refactoring:

```bash
npm test
# OR pytest / go test / cargo test
```

**If tests fail** → Fix tests first, then return here
**If tests pass** → Go to Step 1.2

### Step 1.2 — Measure Code Quality (Optional)

Capture baseline metrics:

```bash
# Complexity
npx complexity-report src/

# Coverage
npm run coverage

# Technical debt
npx sonarqube-scanner
```

Save metrics for comparison later.

## Step 2 — Define Refactoring Scope

### Step 2.1 — Create Refactoring Finding

Document what needs refactoring:

```bash
cat > docs/findings/REFACTOR-001.md << EOF
---
id: REFACTOR-001
source: technical-debt
severity: medium
category: refactor
artifact: src/module.ts
status: open
---

# Refactor: [Goal]

**Current state:** [What's wrong - complexity, duplication, etc.]

**Target state:** [What it should look like after refactoring]

**Constraints:**
- [ ] All tests must still pass
- [ ] No behavior changes
- [ ] Performance maintained or improved
EOF
```

## Step 3 — Implement Refactoring

### Step 3.1 — Run Developer Agent

```bash
# Manual session (recommended for refactoring)
"Refactor [module] per REFACTOR-001. Apply [pattern/principle]. Keep all tests passing."
```

**OR via orchestrator:**

```bash
# Create temporary story
cat > backlog/REFACTOR-001.md << EOF
---
id: REFACTOR-001
status: pending
deps: []
---

Refactor [module]

**Acceptance Criteria:**
- [ ] Code complexity reduced
- [ ] [Specific pattern] applied
- [ ] All existing tests pass unchanged
- [ ] No behavior changes
EOF

orchestrator run-phase implementation
```

**Agent**: `developer-agent`
**Approach**:

- Refactor in small steps
- Run tests after each step
- Commit frequently: `refactor: <description> (REFACTOR-001)`

### Step 3.2 — Verify Tests Still Pass

After each refactoring step:

```bash
npm test
```

**If tests fail** → Revert last change, debug, try smaller step
**If tests pass** → Continue refactoring or go to Step 4

## Step 4 — Quality Validation

### Step 4.1 — Run QA Agent

```bash
orchestrator run-phase qa
```

**Agent**: `qa-agent`
**Focus**:

- **Fagan review** — Check code quality improved
- **Regression testing** — Verify no behavior changes
- **YAGNI** — Check refactoring didn't add unnecessary abstractions

### Decision Point 4.2

Check for defects:

```bash
grep -l "status: open" docs/findings/{FAGAN,BUG}-*.md
```

**If defects found** → Return to Step 3.1 (fix and refactor again)
**If clean** → Go to Step 5

## Step 5 — Measure Improvement

### Step 5.1 — Re-run Quality Metrics

```bash
# Complexity (should be lower)
npx complexity-report src/

# Coverage (should be same or higher)
npm run coverage
```

### Step 5.2 — Verify Improvement

Compare before/after metrics:

**Expected results:**

- ✅ Cyclomatic complexity reduced
- ✅ Code duplication reduced
- ✅ Test coverage maintained or improved
- ✅ All tests pass
- ✅ No behavior changes

**If metrics didn't improve** → Consider reverting, refactoring didn't achieve goal
**If metrics improved** → Go to DONE

## DONE

✅ **Refactoring complete**

Final checks:

- [ ] All tests pass (same tests, no modifications)
- [ ] Code quality metrics improved
- [ ] No behavior changes (verified by tests)
- [ ] Commits follow convention: `refactor: <desc> (REFACTOR-NNN)`
- [ ] `REFACTOR-*` finding status: `resolved`

**Ready to merge**

## Common Refactoring Patterns

| Pattern                 | When                                   | Agent Instruction                                  |
| ----------------------- | -------------------------------------- | -------------------------------------------------- |
| Extract Method          | Long functions (>20 lines)             | "Extract methods from [function] to reduce length" |
| Extract Class           | Classes with multiple responsibilities | "Apply SRP to [class]"                             |
| Replace Conditional     | Complex if/else chains                 | "Replace conditionals with polymorphism in [file]" |
| Introduce Parameter Obj | Functions with many parameters         | "Introduce parameter object for [function]"        |
| Dependency Injection    | Hard-coded dependencies                | "Apply DI to [class]"                              |
| Simplify Boolean Logic  | Nested boolean expressions             | "Simplify boolean logic in [function]"             |

## Refactoring Safety Net

**Before starting:**

1. All tests pass ✓
2. Code committed ✓
3. Branch created ✓

**After each step:**

1. Tests still pass ✓
2. Commit ✓

**If stuck:** `git revert` and try smaller steps.
