---
name: qa-strategy-from-spec
description: Derive a per-feature QA strategy document from a consolidated .feature file and supplementary specs.
category: requirements
disable-model-invocation: false
---

# QA Strategy From Spec

Derive a **per-feature QA plan** from the consolidated Gherkin feature file
and the supplementary specs. The output tells the `qa-agent` how to
specialise the generic testing strategy for one feature's contracts,
boundaries, and risk profile.

This skill is **not** a rewrite of
`factory/rulebooks/conventions/testing-strategy.md`. That rulebook stays
generic policy. This skill produces a feature-specific plan for
`docs/spec/<feature-name>-qa-strategy.md`.

## Inputs

Read these source artifacts:

- `docs/spec/<feature-name>.feature`
  - Treat each `Rule:` grouping as the actor-goal matrix for the feature.
  - Use each `Scenario:` as the primary source of observable behavior.
- `docs/spec/supplementary_specs/entity-model.md`
  - Use it to find entity boundaries, value ranges, lifecycle constraints,
    and relationships that create QA risk.
- `docs/spec/supplementary_specs/interface-contracts.md`
  - Use it to find API, CLI, event, file, or DTO contracts and their owners.

If any required input is missing, fail with a diagnostic that names the
missing path.

## Output

Write one file:

| File                                      | Purpose                                              |
| ----------------------------------------- | ---------------------------------------------------- |
| `docs/spec/<feature-name>-qa-strategy.md` | Per-feature QA strategy for Phase 5 and later review |

## Step 1 — Validate Inputs

1. Verify `docs/spec/<feature-name>.feature` exists.
2. Verify `docs/spec/supplementary_specs/entity-model.md` exists.
3. Verify `docs/spec/supplementary_specs/interface-contracts.md` exists.
4. Infer `<feature-name>` from the `.feature` filename.

Fail loudly when an input is absent:

```text
FAIL: missing required input docs/spec/payments.feature
FAIL: missing required input docs/spec/supplementary_specs/interface-contracts.md
```

## Step 2 — Extract Feature-Specific QA Signals

From the `.feature` file, extract:

- Feature name
- Proposal trace if the feature file records one; if not, record an explicit
  gap in the output
- Gherkin trace: `docs/spec/<feature-name>.feature`
- Rule names, actors, and Scenarios
- Any explicit gaps already called out by the spec artifacts

From `entity-model.md`, extract:

- Entities this feature reads, writes, or constrains
- Field-level boundaries, enumerations, cardinality rules, and lifecycle edges
- Invariants whose failure would create data-integrity or state defects

From `interface-contracts.md`, extract:

- Request/response schemas, commands, events, files, or message boundaries
- Ownership boundaries between components or roles
- Validation and compatibility risks at those boundaries

## Step 3 — Assign Test Owners

Apply `factory/rulebooks/conventions/testing-strategy.md` as the governing
policy, but only record the parts that matter for this feature.

For each observable contract, assign exactly one owning layer:

- Deterministic linter
- Acceptance test
- Contract test
- Integration test
- End-to-end smoke test

Do not restate the full generic policy. Specialise it:

- Which layer owns this feature's contract
- Why that layer is sufficient
- Which layers are explicitly out of scope for this feature
- Where overlap risk exists and which owner survives

## Step 4 — Derive Boundary Cases

List the boundary cases that matter for this feature:

- Equivalence classes
- Edge values
- Null / empty / missing cases
- State-transition edges
- Permission and security boundaries
- Cross-component contract mismatches

**Every boundary case must map to one of:**

- A concrete Gherkin scenario from `docs/spec/<feature-name>.feature`, or
- An explicit gap that the spec does not yet cover

Never leave a boundary case untraced. If no Scenario covers it, name the gap
plainly.

## Step 5 — Write the QA Strategy Document

Write `docs/spec/<feature-name>-qa-strategy.md` using this template.

```markdown
# QA Strategy: <feature-name>

Generated from:

- Feature spec: `docs/spec/<feature-name>.feature`
- Entity model: `docs/spec/supplementary_specs/entity-model.md`
- Interface contracts: `docs/spec/supplementary_specs/interface-contracts.md`

## Feature

- Proposal trace: <proposal path or `Gap: proposal trace missing`>
- Gherkin trace: `docs/spec/<feature-name>.feature`
- Summary: <one-paragraph feature-specific QA focus>
- Rules in scope:
  - `Rule: ...`
  - `Rule: ...`

## Test Layers in Scope

| Layer | Status | Feature-specific scope | Owned contracts |
| ----- | ------ | ---------------------- | --------------- |
| Deterministic linter | add / strengthen / out | <why> | <contract names or n/a> |
| Acceptance test | add / strengthen / out | <why> | <contract names or n/a> |
| Contract test | add / strengthen / out | <why> | <contract names or n/a> |
| Integration test | add / strengthen / out | <why> | <contract names or n/a> |
| End-to-end smoke test | add / strengthen / out | <why> | <contract names or n/a> |

## Contract Owners

| Contract | Source scenario or gap | Owner layer | Failure mode | Test strategy note |
| -------- | ---------------------- | ----------- | ------------ | ------------------ |
| <contract> | `Scenario: ...` | Contract test | <what breaks> | <why this layer owns it> |
| <contract> | `Gap: ...` | Acceptance test | <what remains unverified> | <follow-up needed> |

## Boundary Cases

| Boundary case | Source scenario or gap | Risk addressed | Owner layer | Notes |
| ------------- | ---------------------- | -------------- | ----------- | ----- |
| <edge or class> | `Scenario: ...` | <risk> | <layer> | <expected observation> |
| <missing edge> | `Gap: ...` | <risk> | <proposed layer> | <clarification needed> |

## Defect Severity Triage

| Impact on this feature | Severity | Expected action |
| ---------------------- | -------- | --------------- |
| Data loss, privilege breach, broken safety/security boundary | blocking | stop release, fix before merge |
| Broken primary actor-goal path or contract-owner failure | fix-in-same-story | repair in current story or QA loop |
| Minor copy, low-risk observability gap, non-blocking overlap cleanup | defer | file finding or backlog follow-up |

Tailor the table to this feature's real risk profile. Keep the severity names
feature-specific in meaning, not generic in prose.

## Test Retention Policy

- Surviving owner per major contract: <owner layer and retained case>
- Expected overlap to remove later: <where duplication is likely>
- Consolidation rule: keep one owner per contract per `testing-strategy.md`
- Deletion protocol: follow `testing-strategy.md` § Delete overlapping tests
  safely
```

## Step 6 — Feature-Specific Quality Check

Before finishing, confirm all of these:

1. The output is about **one feature**, not the whole project.
2. The `Feature` section includes both proposal and Gherkin traces; if the
   proposal trace cannot be recovered from the source artifacts, record that as
   a gap rather than inventing one.
3. `Contract Owners` is a table.
4. `Boundary Cases` contains only entries traced to a `Scenario:` or `Gap:`.
5. `Defect Severity Triage` reflects the feature's risk profile, not boilerplate.
6. `Test Retention Policy` points back to `testing-strategy.md` for overlap
   deletion protocol.
7. No section is just a paraphrase of the generic testing strategy.

## Report

When done, return:

- Output path written
- Missing inputs or explicit gaps, if any
- Short note on the highest-risk contracts for this feature
