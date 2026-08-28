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
- [ ] `docs/arc42/architecture.dsl` exists

## Use Cases

Run this playbook when:

- Annual architecture review
- Before major feature addition
- After significant technical debt accumulation
- Onboarding new architect
- Pre-acquisition due diligence

## Step 1 — Validate Architecture Documentation

### Step 1.1 — Check Completeness

Verify required files exist:

```bash
ls docs/arc42/01_introduction_and_goals.md \
   docs/arc42/02_architecture_constraints.md \
   docs/arc42/03_system_scope_and_context.md \
   docs/arc42/04_solution_strategy.md \
   docs/arc42/05_building_block_view.md \
   docs/arc42/06_runtime_view.md \
   docs/arc42/07_deployment_view.md \
   docs/arc42/08_crosscutting_concepts.md \
   docs/arc42/09_architecture_decisions.md \
   docs/arc42/10_quality_requirements.md \
   docs/arc42/11_risks_and_technical_debt.md \
   docs/arc42/12_glossary.md \
   docs/arc42/architecture.dsl
```

**If missing files** → Run `architecture-agent` to generate them (go to Playbook: documentation-update)
**If complete** → Go to Step 1.2

### Step 1.2 — Lint Architecture

```bash
factory/scripts/arch-lint --docs-dir docs/arc42
```

**If errors** → Document in `docs/spec/todos.md`, may need architecture-agent to fix
**If clean** → Go to Step 2

## Step 2 — Run Architecture Review

### Step 2.1 — Execute ATAM Review

```bash
factory/scripts/phase advance --playbook architecture-review
# OR manual: Start new session, activate architecture-review-agent
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

Example output:

```
  3 severity: high
  7 severity: medium
  2 severity: low
```

### Step 3.2 — Prioritize Risks

**Manual**: Review each high/medium finding with stakeholders

Create prioritized fix backlog:

```bash
# Add to docs/spec/todos.md
cat >> docs/spec/todos.md << EOF

## Architecture Review Action Items

- [ ] T-$(date +%s)-001: Address ATAM-0001 (high) - [description]
- [ ] T-$(date +%s)-002: Address ATAM-0003 (high) - [description]
- [ ] T-$(date +%s)-003: Address ATAM-0007 (medium) - [description]
EOF
```

## Decision Point

### Do you need to fix findings immediately?

**YES — Critical risks identified** → Go to Step 4
**NO — Document for future work** → Go to Step 5 (DONE)

## Step 4 — Address Findings (Optional)

### Step 4.1 — Run Architecture Agent

```bash
factory/scripts/phase advance --playbook architecture
```

**Agent**: `architecture-agent`
**Task**: Address open `ATAM-*` findings

### Step 4.2 — Re-review

```bash
factory/scripts/phase advance --playbook architecture-review
```

**Agent**: `architecture-review-agent`

### Decision Point 4.3

Check remaining open findings:

```bash
grep -l "status: open" docs/findings/ATAM-*.md
```

**If high/medium risks remain** → Loop to Step 4.1
**If acceptable** → Go to Step 5

## Step 5 — DONE (Review Complete)

✅ **Architecture review complete**

Deliverables:

- [ ] `docs/reviews/atam-review.md` (review report)
- [ ] `docs/findings/ATAM-*.md` (risk findings)
- [ ] Prioritized action items in `docs/spec/todos.md`
- [ ] Stakeholder presentation (optional)

**Next steps**: Schedule follow-up or proceed with fix implementation
