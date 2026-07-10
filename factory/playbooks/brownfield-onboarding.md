---
title: Brownfield Onboarding Playbook
category: orchestration
type: runbook
scenario: brownfield-onboarding
version: 1.0.0
---

# Brownfield Onboarding Playbook

Operational procedure for **documenting existing undocumented system** (reverse engineering).

## Prerequisites

- [ ] Codebase exists and is accessible
- [ ] Code builds and tests pass (or test suite exists)
- [ ] Basic understanding of system purpose

## Overview

**Reverse order workflow**: Code → Architecture → Spec

Unlike greenfield (Spec → Architecture → Code), brownfield starts with existing code and works backwards to document it.

## Phase 1: Code Understanding

### Step 1.1 — Establish Baseline

Run existing tests:

```bash
npm test
# OR pytest / go test / cargo test
```

Document test coverage:

```bash
npm run coverage
```

**If tests exist** → Use as behavioral specification
**If no tests** → Document in `docs/spec/todos.md` as technical debt

### Step 1.2 — Identify Seams

Find public APIs, interfaces, entry points:

```bash
# For TypeScript/JavaScript
grep -r "export.*function" src/
grep -r "export.*class" src/

# For Python
grep -r "^def " src/
grep -r "^class " src/

# For Go
grep -r "^func " **/*.go
```

Document in `docs/spec/todos.md`:

```markdown
## Identified Seams

- API endpoints: [list]
- Public classes: [list]
- CLI commands: [list]
```

## Phase 2: Architecture Documentation

### Step 2.1 — Run Architecture Agent (Reverse Mode)

```bash
# Manual session
"Document the existing architecture in docs/. Analyze the codebase in src/ and create arc42 documentation describing what exists, not what should exist."
```

**Agent**: `architecture-agent`
**Task**: Analyze code, create arc42 docs describing current state

**Expected outputs**:

- `docs/01-12*.md` (arc42 chapters)
- `docs/architecture.dsl` (C4 model of existing system)
- `docs/adr/` (document discovered decisions as ADRs)

### Step 2.2 — Document State Machines

For stateful components found in code:

```bash
# Manual session
"Extract state machines from [file/module] and document per factory/rulebooks/conventions/state-machine-notation.md"
```

Output: `docs/spec/supplementary_specs/state-machines.md`

### Step 2.3 — Validate Architecture

```bash
factory/scripts/arch-lint --docs-dir docs/
```

**If errors** → Fix and loop to Step 2.1
**If clean** → Go to Phase 3

## Phase 3: Specification Extraction

### Step 3.1 — Extract Entity Model

Analyze domain entities in code:

```bash
# Manual session
"Extract entity model from codebase. Document relationships, attributes, and constraints in docs/spec/supplementary_specs/entity-model.md"
```

**Output**: `docs/spec/supplementary_specs/entity-model.md` (ERD)

### Step 3.2 — Extract Use Cases

Derive use cases from:

- Test names
- API endpoints
- User flows in code

```bash
# Manual session
"Derive use cases from the test suite and API endpoints. Create Cockburn use cases in docs/spec/use_cases/"
```

**Output**: `docs/spec/use_cases/UC-*.md`

### Step 3.3 — Extract PRD

Based on use cases and architecture:

```bash
# Manual session
"Create a PRD that describes the system's purpose, actors, and goals based on the documented use cases and architecture"
```

**Output**: `docs/spec/prd.md`

### Step 3.4 — Create Actor-Goal List

```bash
# Manual session
"Create actor-goal list from the use cases in docs/spec/actor-goal-list.md"
```

**Output**: `docs/spec/actor-goal-list.md`

### Step 3.5 — Extract Supplementary Specs

Document non-functional requirements found in code:

- Performance characteristics (timeouts, rate limits)
- Security measures (auth, encryption)
- Validation rules
- Interface contracts

```bash
# Manual session
"Document supplementary specifications based on code analysis: validation rules, interface contracts, security measures"
```

**Output**: `docs/spec/supplementary_specs/*.md`

## Phase 4: Create CONTEXT.md

### Step 4.1 — Extract Domain Vocabulary

Scan code for domain terms:

```bash
# Find type/class names
grep -rh "^class " src/ | sort -u
grep -rh "^type " src/ | sort -u
```

### Step 4.2 — Build Glossary

```bash
# Manual session
"Create CONTEXT.md glossary from domain terms found in code. Include ubiquitous language used in variable names, types, and comments"
```

**Output**: `CONTEXT.md`

## Phase 5: Validation

### Step 5.1 — Spec Review

```bash
orchestrator run-phase spec-review
```

**Agent**: `spec-review-agent`
**Output**: `docs/reviews/spec-review-*.md`, findings

### Step 5.2 — Architecture Review

```bash
orchestrator run-phase architecture-review
```

**Agent**: `architecture-review-agent`
**Output**: `docs/reviews/atam-review.md`, findings

### Step 5.3 — Reconciliation Check

Verify documentation matches code:

```bash
orchestrator run-phase reconciliation
```

**Agent**: `reconciliation-agent`
**Expected**: Should show "aligned" since we documented from code

## Phase 6: Gap Analysis

### Step 6.1 — Identify Undocumented Behavior

Check for:

```bash
# Untested code
npm run coverage
# Look for low-coverage modules

# Undocumented decisions
diff <(find docs/adr/ -name "*.md" | wc -l) <(echo 10)
# If < 5-10 ADRs, likely missing architectural decisions
```

### Step 6.2 — Document Gaps

Add to `docs/spec/todos.md`:

```markdown
## Documentation Gaps

- [ ] T-001: No tests for [module] — behavioral spec unknown
- [ ] T-002: Decision rationale for [architecture choice] not documented
- [ ] T-003: Use case for [feature] unclear
```

## DONE

✅ **System documented**

Deliverables:

- [ ] `docs/spec/prd.md` (reverse-engineered)
- [ ] `docs/spec/use_cases/*.md` (extracted from code/tests)
- [ ] `docs/*.md` (arc42 architecture docs)
- [ ] `docs/adr/*.md` (documented decisions)
- [ ] `docs/architecture.dsl` (C4 model)
- [ ] `CONTEXT.md` (domain glossary)
- [ ] `docs/spec/todos.md` (identified gaps)

**Now use greenfield playbook for new features**

## Next Steps

With documentation in place, you can now:

1. Use **feature-addition playbook** for new features
2. Use **refactoring playbook** to improve code quality
3. Use **documentation-update playbook** to keep docs in sync
4. Run **architecture-review playbook** periodically

**System is now manageable with documented workflow**
