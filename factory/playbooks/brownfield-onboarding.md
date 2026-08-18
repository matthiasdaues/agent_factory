---
title: Brownfield Onboarding Playbook
category: orchestration
type: runbook
scenario: brownfield-onboarding
version: 2.0.0
---

# Brownfield Onboarding Playbook

Operational procedure for **documenting an existing undocumented system** (reverse engineering).

## Prerequisites

- [ ] Codebase exists and is accessible
- [ ] Code builds and tests pass (or test suite exists)
- [ ] Basic understanding of system purpose

## Overview

**Reverse order workflow**: Code → Architecture baseline → Spec → Architecture deepening → Review → Reconciliation

Unlike greenfield (Spec → Architecture → Code), brownfield starts with existing code and works backwards. A two-pass architecture approach — baseline from code, then component resolution after specification extraction — produces documentation that is both structurally accurate and domain-aware.

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

Document discovered seams in `docs/spec/todos.md`.

## Phase 2: Architecture Docs Baseline

First architecture pass: structural skeleton from code and infrastructure-as-code. Scope is system context, containers, and deployment nodes. Component-level detail is deferred to Phase 4.

### Step 2.0 — Archive Superseded Documentation

Move all pre-existing documentation artifacts to `~archive/`, preserving each file's original relative path (for example, `docs/arc42/legacy.md` → `~archive/docs/arc42/legacy.md`).

### Step 2.1 — Locate Infrastructure-as-Code

Before dispatching the architecture agent, ask the user:

1. Does the project contain Terraform, OpenTofu, Pulumi, CloudFormation, or other IaC?
2. If yes, where does it live? (e.g. `infra/`, `terraform/`, repo root)

Record the answer. If IaC exists, pass the path to the architecture agent so it can model deployment nodes and connections from IaC.

### Step 2.2 — Build architecture.dsl First

**Agent**: `architecture-agent`
**Task**: Analyze code and IaC. Create `docs/arc42/architecture.dsl` with system context and container views. Derive initial arc42 prose chapters from the DSL. Document discovered architectural decisions as ADRs.

**Expected outputs**:

- `docs/arc42/architecture.dsl` (C4 model — system context, containers, deployment)
- `docs/arc42/01-12*.md` (arc42 chapters derived from DSL)
- `docs/adr/` (discovered decisions)

### Step 2.3 — Validate and Export Structurizr Model

```bash
factory/scripts/structurizr validate
factory/scripts/structurizr export-all
```

### Step 2.4 — Validate Architecture

```bash
factory/scripts/arch-lint --docs-dir docs/arc42
```

**If errors** → Fix and re-validate
**If clean** → Proceed to Phase 3

## Phase 3: Specification Extraction

### Step 3.1 — Extract Domain Vocabulary

Scan code for domain terms — type names, class names, module names. Build `CONTEXT.md` with ubiquitous language.

**Output**: `CONTEXT.md`

### Step 3.2 — Extract Entity Model

Analyze domain entities in code — relationships, attributes, constraints.

**Output**: `docs/spec/supplementary_specs/entity-model.md`

### Step 3.3 — Extract Use Cases

Derive use cases from test names, API endpoints, and user flows in code. Write as Cockburn use cases.

**Output**: `docs/spec/use_cases/UC-*.md`

### Step 3.4 — Create Actor-Goal List

**Output**: `docs/spec/actor-goal-list.md`

### Step 3.5 — Extract PRD

Based on use cases and architecture baseline.

**Output**: `docs/spec/prd.md`

### Step 3.6 — Extract Supplementary Specs

Document non-functional requirements found in code: performance characteristics (timeouts, rate limits), security measures (auth, encryption), validation rules, interface contracts.

**Output**: `docs/spec/supplementary_specs/*.md`

### Step 3.7 — Document State Machines

For stateful components found in code, extract state machines per [`state-machine-notation.md`](../rulebooks/conventions/state-machine-notation.md).

**Output**: `docs/spec/supplementary_specs/state-machines.md`

## Phase 4: Component-Resolution Pass

Second architecture pass: deepen the baseline architecture using domain knowledge from the specification.

### Step 4.1 — Resolve Components Within Containers

**Agent**: `architecture-agent`
**Task**: Using the specification artifacts from Phase 3 (entity model, use cases, supplementary specs) and the code, resolve component-level detail within each container. Update `architecture.dsl` with component views. Add dynamic views showing use-case flows through components. Refine deployment views where Phase 3 revealed runtime dependencies.

**Inputs**:

- `docs/arc42/architecture.dsl` (baseline from Phase 2)
- `docs/spec/` (all specification artifacts from Phase 3)
- Source code

**Expected outputs**:

- Updated `docs/arc42/architecture.dsl` (component views, dynamic views added)
- Updated arc42 chapters [05 (Building Block View)](../rulebooks/rules.md#architecture-documentation), [06 (Runtime View)](../rulebooks/rules.md#architecture-documentation), [07 (Deployment View)](../rulebooks/rules.md#architecture-documentation)
- New ADRs if component boundaries reveal undocumented decisions

### Step 4.2 — Validate and Export Updated Model

```bash
factory/scripts/structurizr validate
factory/scripts/structurizr export-all
factory/scripts/arch-lint --docs-dir docs/arc42
```

**If errors** → Fix and re-validate
**If clean** → Proceed to Phase 5

## Phase 5: Architecture Review

### Step 5.1 — ATAM Review

**Agent**: `architecture-review-agent`
**Task**: Review the complete architecture (structural baseline and component resolution) against quality attribute scenarios.

**Output**: `docs/reviews/atam-review.md`, findings in `docs/findings/`

### Step 5.2 — Address Findings

Fix findings from the ATAM review. Re-validate architecture after fixes.

**If blocking findings remain** → Loop to Step 5.1
**If clean** → Proceed to Phase 6

## Phase 6: Reconciliation / Gap Loop

Iterative loop: verify documentation matches code, identify gaps, fix, repeat.

### Step 6.1 — Reconciliation Check

**Agent**: `reconciliation-agent`
**Task**: Verify all documentation artifacts match the code-as-built.

**Output**: Reconciliation report, findings in `docs/findings/`

### Step 6.2 — Identify Undocumented Behavior

Check for untested code paths, undocumented decisions, unclear use cases. Add gaps to `docs/spec/todos.md`.

### Step 6.3 — Fix and Iterate

Address reconciliation findings and documentation gaps. Re-run reconciliation check.

**Exit criterion**: Reconciliation agent reports alignment with no blocking findings.

## DONE

Deliverables:

- [ ] `docs/arc42/architecture.dsl` (C4 model with component-level detail)
- [ ] `docs/arc42/01-12*.md` (arc42 chapters)
- [ ] `docs/adr/*.md` (documented decisions)
- [ ] `docs/spec/prd.md` (reverse-engineered)
- [ ] `docs/spec/use_cases/*.md` (extracted from code/tests)
- [ ] `docs/spec/actor-goal-list.md`
- [ ] `docs/spec/supplementary_specs/*.md` (entity model, state machines, NFRs)
- [ ] `CONTEXT.md` (domain glossary)
- [ ] `docs/spec/todos.md` (identified gaps)
- [ ] `docs/reviews/atam-review.md`

## Next Steps

With documentation in place:

1. Use [**feature-addition playbook**](feature-addition.md) for new features
2. Use [**refactoring playbook**](refactoring.md) to improve code quality
3. Use [**documentation-update playbook**](documentation-update.md) to keep docs in sync
4. Run [**architecture-review playbook**](architecture-review.md) periodically
