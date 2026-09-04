---
name: qa-strategy-from-spec
description: Derive a per-feature QA strategy document from a consolidated .feature file, supplementary specs, charter layer bindings, and repository test infrastructure.
category: requirements
disable-model-invocation: false
---

# QA Strategy From Spec

Derive a **per-feature QA plan** from the consolidated Gherkin feature file,
the supplementary specs, the project charter's layer bindings, and the
repository's actual test infrastructure. The output tells the `qa-agent` how
to specialise the generic testing strategy for one feature's contracts,
boundaries, and risk profile.

This skill is **not** a rewrite of
`factory/rulebooks/conventions/testing-strategy.md`. That rulebook stays
generic policy and provides shared vocabulary and the overlap-deletion
protocol. This skill produces a feature-specific plan grounded in the
project charter for `docs/spec/<feature-name>-qa-strategy.md`.

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
- `testing.yaml (at docs/agent-context/testing.yaml, falling back to docs/charter/testing.yaml)` — charter layer bindings
  - Read the `layers` section. Each layer maps a Factory layer name to
    project-specific tooling, infrastructure, entry point, optional
    anti-patterns, and optional fidelity declarations.
  - If the file is absent or has no `layers` section, fall back to the
    Factory convention's generic five layers from
    [testing-strategy.md](../../rulebooks/conventions/testing-strategy.md)
    and emit a gap finding noting the absence.
- **Repository test infrastructure scan**
  - Scan root `conftest.py`, `tests/` and `packages/*/tests/` directories,
    `Makefile` test targets, `pyproject.toml` pytest configuration,
    `vitest.config.*`, and runner configs (`tox.ini`, `noxfile.py`,
    `Justfile`, `Taskfile.yml`).
  - This scan does not execute tests or parse CI pipeline YAML.
  - Use the scan to verify that the charter's declared infrastructure and
    entry points match what exists in the repository.

If any required spec input is missing (`.feature`, entity-model,
interface-contracts), fail with a diagnostic that names the missing path.
The charter and repository scan are optional inputs — their absence
triggers fallback behavior, not a hard failure.

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
5. Read `testing.yaml (at docs/agent-context/testing.yaml, falling back to docs/charter/testing.yaml)` if present. Record whether the `layers`
   section exists.
6. Scan the repository's test infrastructure. Record discovered entry
   points, test directories, fixture files, and runner configurations.
7. Cross-check charter declarations against the repository scan. Record
   mismatches as gap findings:
   - A charter-declared `entry_point` that does not resolve to an existing
     command or target.
   - A charter-declared `infrastructure` that has no corresponding fixture
     or configuration in the repository.
   - Test infrastructure present in the repository that the charter does
     not declare.

Fail loudly when a required spec input is absent:

```text
FAIL: missing required input docs/spec/payments.feature
FAIL: missing required input docs/spec/supplementary_specs/interface-contracts.md
```

When the charter is absent or lacks `layers`, emit a gap finding and
continue with the Factory convention fallback:

```text
Gap: testing.yaml (at docs/agent-context/testing.yaml, falling back to docs/charter/testing.yaml) missing — falling back to Factory convention layers
Gap: testing.yaml (at docs/agent-context/testing.yaml, falling back to docs/charter/testing.yaml) has no layers section — falling back to Factory convention layers
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

## Step 3 — Assign Contract Owners

Apply the charter's layer bindings from `testing.yaml (at docs/agent-context/testing.yaml, falling back to docs/charter/testing.yaml)` as the
governing policy for contract-owner assignments. Use
[testing-strategy.md](../../rulebooks/conventions/testing-strategy.md) for
shared vocabulary and the overlap-deletion protocol.

When charter layer bindings are absent, fall back to the Factory
convention's generic five layers:

| Layer                 | Owns                                                              |
| --------------------- | ----------------------------------------------------------------- |
| Deterministic linter  | Declarative structure: frontmatter, indexes, schemas, formatting  |
| Acceptance test       | Observable behavior via Gherkin runner                            |
| Contract test         | Internal behavior: parsing, normalization, policy, state machines |
| Integration test      | Boundaries: installation, persistence, subprocesses, filesystems  |
| End-to-end smoke test | One representative journey through a CLI or major workflow        |

For each observable contract, assign exactly one owning layer:

1. **Identify the contract's requirements.** What must the owning layer
   prove? Does the contract require real infrastructure, real transactions,
   or specific environmental fidelity?

2. **Check layer fidelity.** When the charter declares a `fidelity` map
   for the candidate layer, verify that the layer's fidelity declarations
   cover the contract's requirements. A contract that requires real
   transactions cannot be owned by a layer whose fidelity declares
   transactions as mocked. When fidelity is insufficient, emit a gap
   finding:

   ```text
   Gap: contract "<contract>" requires real transactions but layer
   "contract_test" declares transactions as mocked — fidelity insufficient
   ```

3. **Check layer availability.** When a contract needs a layer the charter
   has not declared, emit a gap finding rather than silently assuming the
   layer exists:

   ```text
   Gap: contract "<contract>" needs integration_test layer but charter
   does not declare it
   ```

4. **Assign the owner.** Record the owning layer, the justification, and
   the overlap risk. Do not restate the full generic policy — specialise
   it:

   - Which layer owns this feature's contract
   - Why that layer is sufficient (fidelity, infrastructure, scope)
   - Which layers are explicitly out of scope for this feature
   - Where overlap risk exists and which owner survives

### Layer status states

The "Test Layers in Scope" table uses status states that distinguish
infrastructure readiness from test coverage:

| Status              | Meaning                                                                                                                                             |
| ------------------- | --------------------------------------------------------------------------------------------------------------------------------------------------- |
| `available`         | The test layer and harness work but no tests exist yet for this feature at this layer.                                                              |
| `partially covered` | The harness works and some contracts have tests at this layer; others remain unimplemented. Takes precedence over `available` when any test exists. |
| `planned`           | Neither harness nor tests exist for this feature at this layer; an explicit gap, not missing coverage.                                              |
| `blocked`           | A production capability must exist before the test can be written.                                                                                  |
| `out`               | This layer is not used for the feature.                                                                                                             |

### Test-ID convention

Each contract-owner row emits a test ID following the pattern
`<scope-ID>-<layer-abbreviation>-<sequence>`:

| Abbreviation | Layer                 |
| ------------ | --------------------- |
| LN           | Deterministic linter  |
| AC           | Acceptance test       |
| CT           | Contract test         |
| IT           | Integration test      |
| E2           | End-to-end smoke test |

Example: `DSP-01-IT-01` is the first integration test for scope contract
DSP-01.

The test ID is a stable identifier tied to the scope ID, not to mutable
scenario prose.

### Contract-owner row state

Each row in the contract-owner table carries a `State` that reflects the
status of that individual contract-owner assignment:

| State         | Meaning                                                            |
| ------------- | ------------------------------------------------------------------ |
| `implemented` | The test exists and runs.                                          |
| `planned`     | The test does not yet exist; the row is an explicit gap.           |
| `blocked`     | A production capability must exist before the test can be written. |

These differ from the layer-level status states because a single
contract-owner row is either tested or not — it cannot be "partially
covered." This makes it mechanically answerable which rows are implemented
and which remain gaps.

### Spec marker convention

Projects that use pytest should carry the scope ID as a marker:

```python
@pytest.mark.spec("DSP-01")
@pytest.mark.integration
def test_dispatch_rolls_back_when_outbox_write_fails(): ...
```

The `@pytest.mark.spec("<scope-ID>")` marker ties each test to its scope
contract, enabling:

- Traceability from test back to the QA strategy's contract-owner table
- Mutation-analysis classification joining mutants to contracts via the
  marker (preferred over file-path join)
- Filtering tests by scope during targeted test runs

The marker taxonomy (`acceptance`, `contract`, `integration`, `e2e`) and
the test-ID naming convention are project-owned — this skill recommends the
convention through the QA strategy output, but the project wires the
markers into its own test configuration.

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

````markdown
# QA Strategy: <feature-name>

Generated from:

- Feature spec: `docs/spec/<feature-name>.feature`
- Entity model: `docs/spec/supplementary_specs/entity-model.md`
- Interface contracts: `docs/spec/supplementary_specs/interface-contracts.md`
- Charter layer bindings: `testing.yaml (at docs/agent-context/testing.yaml, falling back to docs/charter/testing.yaml)`
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

```python
@pytest.mark.spec("<scope-ID>")
@pytest.mark.<layer>
def test_<descriptive_name>(): ...
```

The marker enables traceability from test to contract-owner table and
supports mutation-analysis classification joining mutants to contracts.

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

## Step 6 — Feature-Specific Quality Check

Before finishing, confirm all of these:

01. The output is about **one feature**, not the whole project.
02. The `Feature` section includes both proposal and Gherkin traces; if the
    proposal trace cannot be recovered from the source artifacts, record that
    as a gap rather than inventing one.
03. The "Generated from" header includes charter layer bindings and repo test
    infrastructure sources.
04. `Test Layers in Scope` uses status states (`available`,
    `partially covered`, `planned`, `blocked`, `out`) — not the old
    `add / strengthen / out`.
05. `Test Layers in Scope` includes a `Charter binding` column showing the
    charter's tool and entry point, or "Factory convention fallback" when the
    charter is absent.
06. `Contract Owners` is a table with columns: Contract, Source scenario or
    gap, Owner layer, Test ID, Test location, Command, State.
07. Every contract-owner row has a test ID following `<scope-ID>-<layer-abbreviation>-<sequence>`.
08. Every contract-owner row has a `State` of `implemented`, `planned`, or
    `blocked`.
09. The spec marker convention (`@pytest.mark.spec("<scope-ID>")`) is
    documented in the Contract Owners section.
10. `Boundary Cases` contains only entries traced to a `Scenario:` or `Gap:`.
11. `Gap Findings` records all charter/repo mismatches, missing layer
    declarations, and fidelity insufficiencies found during Steps 1 and 3.
12. When a contract was assigned to a layer, fidelity declarations were
    checked against contract requirements.
13. `Defect Severity Triage` reflects the feature's risk profile, not
    boilerplate.
14. `Test Retention Policy` points back to
    [testing-strategy.md](../../rulebooks/conventions/testing-strategy.md)
    for overlap deletion protocol.
15. No section is just a paraphrase of the generic testing strategy.

## Report

When done, return:

- Output path written
- Missing inputs or explicit gaps, if any
- Charter grounding status: charter-grounded or Factory convention fallback
- Gap findings emitted (charter/repo mismatches, fidelity issues, missing
  layers)
- Short note on the highest-risk contracts for this feature
