---
title: QA Strategy Template
version: 1.0.0
---

# QA Strategy Template

Skeleton for `docs/spec/<feature-name>-qa-strategy.md`. Governed by
[qa-strategy-from-spec](../../skills/qa-strategy-from-spec/SKILL.md).

````markdown
# QA Strategy: <feature-name>

Generated from:

- Feature spec: `docs/spec/<feature-name>.feature`
- Entity model: `docs/spec/supplementary_specs/entity-model.md`
- Interface contracts: `docs/spec/supplementary_specs/interface-contracts.md`
- Charter layer bindings: `testing.yaml (at docs/testing.yaml)`
- Repo test infrastructure: conftest.py, tests/, packages/*/tests/

## Feature

- Proposal trace: <proposal path or `Gap: proposal trace missing`>
- Gherkin trace: `docs/spec/<feature-name>.feature`
- Summary: <one-paragraph feature-specific QA focus>
- Rules in scope:
  - `Rule: ...`
  - `Rule: ...`

## Test Layers in Scope

| Layer | Status | Charter binding | Feature-specific scope | Owned contracts |
| ----- | ------ | --------------- | ---------------------- | --------------- |
| Deterministic linter | available / partially covered / planned / blocked / out | <charter tool and entry_point, or "Factory convention fallback"> | <why> | <contract names or n/a> |
| Acceptance test | available / partially covered / planned / blocked / out | <charter binding or fallback> | <why> | <contract names or n/a> |
| Contract test | available / partially covered / planned / blocked / out | <charter binding or fallback> | <why> | <contract names or n/a> |
| Integration test | available / partially covered / planned / blocked / out | <charter binding or fallback> | <why> | <contract names or n/a> |
| End-to-end smoke test | available / partially covered / planned / blocked / out | <charter binding or fallback> | <why> | <contract names or n/a> |

## Contract Owners

| Contract | Source scenario or gap | Owner layer | Test ID | Test location | Command | State |
| -------- | ---------------------- | ----------- | ------- | ------------- | ------- | ----- |
| <contract> | `Scenario: ...` | Contract test | <scope-ID>-CT-01 | `tests/contract/test_<module>.py` | `<charter entry_point>` | planned |
| <contract> | `Gap: ...` | Integration test | <scope-ID>-IT-01 | `tests/integration/test_<module>.py` | `<charter entry_point>` | planned |

### Spec marker convention

Projects that use pytest should carry the scope ID as a marker:

\```python
@pytest.mark.spec("<scope-ID>")
@pytest.mark.<layer>
def test_<descriptive_name>(): ...
\```

The marker enables traceability from test to contract-owner table and
supports mutation-testing classification joining mutants to contracts.

## Boundary Cases

| Boundary case | Source scenario or gap | Risk addressed | Owner layer | Notes |
| ------------- | ---------------------- | -------------- | ----------- | ----- |
| <edge or class> | `Scenario: ...` | <risk> | <layer> | <expected observation> |
| <missing edge> | `Gap: ...` | <risk> | <proposed layer> | <clarification needed> |

## Gap Findings

| Finding | Source | Severity | Recommended action |
| ------- | ------ | -------- | ------------------ |
| <description> | charter / repo scan / fidelity check | <severity> | <action> |

Record all gap findings emitted during Steps 1 and 3 here. Include:

- Charter/repo mismatches (declared entry points that do not resolve,
  undeclared test infrastructure)
- Missing layer declarations (contract needs a layer the charter omits)
- Fidelity insufficiencies (contract requires fidelity the layer cannot
  provide)
- Absent charter (fallback to Factory convention)

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
- Consolidation rule: keep one owner per contract per
  [testing-strategy.md](../../factory/rulebooks/conventions/testing-strategy.md)
- Deletion protocol: follow
  [testing-strategy.md § Delete overlapping tests safely](../../factory/rulebooks/conventions/testing-strategy.md#delete-overlapping-tests-safely)
````
