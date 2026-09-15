---
name: qa-strategy-from-spec
description: Derive a per-feature QA strategy document from a consolidated .feature file, supplementary specs, testing.yaml layer bindings, and repository test infrastructure.
category: requirements
---

# QA Strategy From Spec

Derive a **per-feature QA plan** from the consolidated Gherkin feature file,
the supplementary specs, the `testing.yaml` layer bindings, and the
repository's actual test infrastructure. The output tells the `qa-agent` how
to specialise the generic testing strategy for one feature's contracts,
boundaries, and risk profile.

Read [writing-quality-gates.md](../../rulebooks/conventions/writing-quality-gates.md) now and hold every rule as a writing constraint. No prose reaches terminal output or a file until it passes all four gates. Do not write first and check later.
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
- `testing.yaml (at docs/testing.yaml)` — charter layer bindings
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
5. Read `testing.yaml (at docs/testing.yaml)` if present. Record whether the `layers`
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
Gap: testing.yaml (at docs/testing.yaml) missing — falling back to Factory convention layers
Gap: testing.yaml (at docs/testing.yaml) has no layers section — falling back to Factory convention layers
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

Apply the charter's layer bindings from `testing.yaml (at docs/testing.yaml)` as the
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

Write `docs/spec/<feature-name>-qa-strategy.md` using the
[QA strategy template](../../rulebooks/templates/qa-strategy.md).

## Step 6 — Feature-Specific Quality Check

Run the [QA strategy quality checklist](../../rulebooks/references/qa-strategy-checklist.md) — all 15 checks must pass.

## Report

When done, return:

- Output path written
- Missing inputs or explicit gaps, if any
- Charter grounding status: charter-grounded or Factory convention fallback
- Gap findings emitted (charter/repo mismatches, fidelity issues, missing
  layers)
- Short note on the highest-risk contracts for this feature
