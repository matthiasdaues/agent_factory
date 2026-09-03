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

**Reverse order workflow**: Code → Architecture baseline → Scope map → (optional) Spec → Architecture deepening → Review → Reconciliation

Unlike greenfield (Spec → Architecture → Code), brownfield starts with existing code and works backwards. The playbook is split into two stages with an explicit exit point between them:

- **Stage 1 — Enough to work**: produces three anchor files (`docs/arc42/architecture.dsl`, `docs/spec/scope-map.md`, `docs/CONTEXT.md`). The user can start feature work from here.
- **Stage 2 — Full reverse engineering** (opt-in): specification extraction, component resolution, ATAM review, and reconciliation. Available when the user or the change warrants it.

## Stage 1 — Enough to Work

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

The workspace property `"arc42.projected"` defaults to `"false"` and is set to `"true"` by the architecture-agent only when the user requests arc42 chapter projection from the DSL.

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

## Phase 2b: Scope Map and Domain Vocabulary

### Step 2.5 — Populate Scope Map via Reverse-Map

Invoke the `reverse-map` skill. It sweeps tests first (highest confidence), then code entry points, then accepts additional sources from the stakeholder. Results are presented in batches by domain area for stakeholder confirmation.

**Expected outputs**:

- `docs/spec/scope-map.md` (5-column format: Rule, Status, Confidence, Sources, Feature Link)
- `docs/CONTEXT.md` (domain vocabulary seeded from type names, class names, module names)

### Step 2.6 — Validate Stage 1 Exit

Verify the three anchor files exist and are valid:

- [ ] `docs/arc42/architecture.dsl` exists with system context and container views
- [ ] `docs/spec/scope-map.md` exists with Rules marked `implemented`
- [ ] `docs/CONTEXT.md` exists seeded with domain vocabulary
- [ ] Structurizr validation passes on the DSL

### Stage 1 Exit Point

Present the user with the choice:

> "You now have the structural shape and the functional inventory. You can start feature work from here. Want to go deeper, or start building?"

**If the user exits** → Stage 1 is complete. The user can start a `feature-addition` from the brownfield-lite baseline (anchor file presence is the prerequisite, not a gate marker).

**If the user continues** → Proceed to Stage 2.

______________________________________________________________________

## Stage 2 — Full Reverse Engineering (Opt-In)

Stage 2 deepens the baseline with full specification extraction, component-level architecture resolution, ATAM review, and reconciliation. Available when the user or the change warrants it, but not required before the first feature-addition.

## Phase 3: Specification Extraction

### Step 3.1 — Extract Domain Vocabulary

Scan code for domain terms — type names, class names, module names. Build `CONTEXT.md` with ubiquitous language.

**Output**: `CONTEXT.md`

### Step 3.2 — Extract Entity Model

Analyze domain entities in code — relationships, attributes, constraints.

**Output**: `docs/spec/supplementary_specs/entity-model.md`

### Step 3.3 — Derive Feature Spec

Derive a consolidated Gherkin feature file from test names, API endpoints, and user flows in code. Use Cockburn actor-goal reasoning as internal process; output Rule-per-actor-goal `.feature` structure with `@`-references to existing code. Update the scope map with all Rules marked `implemented`.

**Output**: `docs/spec/<project-name>.feature`, `docs/spec/scope-map.md` (updated), `docs/spec/<project-name>-gaps.md`

### Step 3.4 — Extract PRD

Based on the feature spec and architecture baseline.

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
**If clean** → Proceed to Step 5.3

### Step 5.3 — Capture Project Charter

**Manual**: Invoke `capture-charter --init --scan` to scan the codebase and bootstrap the project charter.

The charter records foundational decisions the team has already made: languages,
frameworks, databases, testing practices, CI/CD, and team rules. Brownfield
onboarding surfaces these from the code and infrastructure-as-code.

The skill:

1. Scans for signals (package manifests, test configs, linter configs, IaC, CI/CD
   pipelines)
2. Pre-populates the three charter files (`docs/charter/tech-stack.md`,
   `docs/charter/development.md`, `docs/charter/house-rules.md`)
3. Presents findings to the stakeholder for confirmation

**⚠️ No Epic 0 derivation in brownfield** — the mise en place (infrastructure,
setup scripts, configurations) already exists in the scanned codebase. Unlike
greenfield, which must *create* those artifacts, brownfield *documents* them.
The charter records reality as it stands.

**Expected output**: `docs/charter/` (three documents), confirmed by
stakeholder

**If scan incomplete** → Stakeholder corrects or adds findings
**If complete** → Proceed to Step 5.4

### Step 5.4 — Planning Gate (Charter & Specification Readiness)

**Manual**: Stakeholder approval + deterministic gate

Present the completed charter to the stakeholder. Run the planning gate to
verify no `To be decided.` entries remain in tech-stack.md or development.md:

```bash
factory/scripts/charter-lint --planning-gate
```

This gate must pass before any specification work or planning decisions that
follow onboarding.

**If gate fails** → Return to Step 5.3 and correct charter entries
**If gate passes + stakeholder approves** → Proceed to Phase 6

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

## Terminal Condition: Project Ready for Feature Delivery

✅ **DONE**

The playbook ends when the following terminal artifacts exist:

**Terminal Artifacts:**

- [ ] `docs/spec/scope-map.md` exists with Rules backfilled from the existing codebase (all marked `implemented`); the scope-map migration skill handles the backfill if `derive-spec` artifacts exist from prior specification work; otherwise the scope map is populated directly from code inspection
- [ ] `docs/arc42/architecture.dsl` models the as-built module structure (C4 components and dependencies reverse-engineered from code)
- [ ] Arc42 prose chapters (01–12) pass architecture review with no blocking findings

**Supporting Deliverables:**

- [ ] `docs/adr/*.md` (documented architectural decisions)
- [ ] `CONTEXT.md` (domain glossary / ubiquitous language)
- [ ] `docs/spec/supplementary_specs/*.md` (entity model, state machines, validation rules, interface contracts)
- [ ] `docs/spec/prd.md` (reverse-engineered product requirements)
- [ ] `docs/spec/todos.md` (identified specification gaps and technical debt)
- [ ] `docs/charter/*.md` (project charter: tech-stack, development practices, house rules)
- [ ] `docs/reviews/atam-review.md` (architecture review findings — all addressed)

**Next Phase:**

After this playbook completes, **all feature work enters through the `feature-addition` playbook**. Each feature-addition slice produces a per-feature `.feature` file from one or more Rules in the scope map (matching implemented code). The scope map and quality baselines are established through this onboarding pass; new feature delivery is a single pipeline regardless of how the project started.

**Quality Baseline Note:**

Brownfield onboarding produces the architectural and specification baseline. The quality baseline (CRAP scores, mutation coverage, dependency conformance) is established incrementally through the feature pipeline's semantic gates as new feature work enters via `feature-addition`.
