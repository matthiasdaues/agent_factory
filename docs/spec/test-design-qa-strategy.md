# QA Strategy: test-design

Generated from:

- Feature spec: `docs/spec/test-design.feature`
- Entity model: `docs/spec/supplementary_specs/entity-model.md`
- Interface contracts: `docs/spec/supplementary_specs/interface-contracts.md`
- Charter layer bindings: `docs/charter/testing.yaml`
- Repo test infrastructure: `conftest.py`, `tests/`, `pyproject.toml`

## Feature

- Proposal trace: `docs/proposals/test-design-skill.md`
- Gherkin trace: `docs/spec/test-design.feature`
- Summary: The test-design feature introduces a planning-phase skill that assigns test ownership, classifies contracts by risk class, and writes prescribed failure scenarios before stories are cut. It also extends `testing.yaml` with `gates` and `risk_classes` schema sections, migrates the CRAP threshold, adds a `test-design-verify` gate script, and changes the developer-agent's RED phase to consume prescribed test-design output instead of inventing its own tests. The QA focus is on the ownership resolution algorithm, the risk-class precedence chain, the gate's trace-to-scenario resolution chain, and backward compatibility with stories that lack test-design output.
- Rules in scope:
  - `Rule: Planning Agent designs test scenarios from feature contracts`
  - `Rule: Test-design skill guards on detect-test-regime prerequisite`
  - `Rule: Test-design skill assigns one test owner per contract across the backlog`
  - `Rule: Test-design skill classifies contracts by risk class`
  - `Rule: Test-design skill propagates prior tests to non-owning stories`
  - `Rule: Create-backlog sequence integrates test-design as optional step`
  - `Rule: Create-backlog-stories carries test-design sections into story files`
  - `Rule: Developer-Agent consumes test-design as prescribed RED phase`
  - `Rule: Developer-Agent falls back without test-design output`
  - `Rule: Testing strategy defines risk-class conventions`
  - `Rule: Human Operator configures risk classes per project in testing.yaml`
  - `Rule: Human Operator configures gate thresholds in testing.yaml`
  - `Rule: Dispatcher reads gate configuration from testing.yaml`
  - `Rule: Test-design-verify gate validates test-design completeness`
  - `Rule: CRAP score reads threshold from testing.yaml gates section`

## Test Layers in Scope

| Layer                 | Status    | Charter binding                                             | Feature-specific scope                                                                                                                | Owned contracts                    |
| --------------------- | --------- | ----------------------------------------------------------- | ------------------------------------------------------------------------------------------------------------------------------------- | ---------------------------------- |
| Deterministic linter  | available | ruff: `uvx ruff check --fix && uvx ruff format`             | YAML schema validation of `gates` and `risk_classes` sections; markdown formatting of skill documents                                 | TD-LN-01 through TD-LN-03          |
| Acceptance test       | planned   | Factory convention fallback (no behave/cucumber configured) | Observable skill behavior: test-design reads contracts and writes Test Design sections; developer-agent consumes output               | n/a — no Gherkin runner configured |
| Contract test         | available | pytest: `uv run pytest tests/ -m contract`                  | Ownership resolution algorithm; risk-class precedence chain; gate resolution chain; CRAP threshold resolution; prerequisite guard     | TD-CT-01 through TD-CT-10          |
| Integration test      | available | pytest: `uv run pytest tests/ -m integration`               | Gate script end-to-end with real story files and scope map; CRAP script with testing.yaml; create-backlog-stories section propagation | TD-IT-01 through TD-IT-05          |
| End-to-end smoke test | out       | —                                                           | The test-design skill is a planning-phase document transformation, not a CLI workflow with a user-observable journey                  | n/a                                |

## Contract Owners

| Contract                                         | Source scenario or gap                                                   | Owner layer          | Test ID  | Test location                                      | Command                                   | State   |
| ------------------------------------------------ | ------------------------------------------------------------------------ | -------------------- | -------- | -------------------------------------------------- | ----------------------------------------- | ------- |
| Prerequisite guard: testing_strategy present     | `Scenario: Prerequisite met when testing_strategy is present`            | Contract test        | TD-CT-01 | `tests/factory/test_test_design.py`                | `uv run pytest tests/ -m contract`        | planned |
| Prerequisite guard: testing_strategy absent      | `Scenario: Prerequisite fails when testing_strategy is absent`           | Contract test        | TD-CT-02 | `tests/factory/test_test_design.py`                | `uv run pytest tests/ -m contract`        | planned |
| Ownership resolution: introducing story owns     | `Scenario: Ownership assigned to the story that introduces the contract` | Contract test        | TD-CT-03 | `tests/factory/test_test_design.py`                | `uv run pytest tests/ -m contract`        | planned |
| Ownership resolution: cross-epic                 | `Scenario: Ownership resolved across multiple epics`                     | Contract test        | TD-CT-04 | `tests/factory/test_test_design.py`                | `uv run pytest tests/ -m contract`        | planned |
| Ownership resolution: no duplicate at same layer | `Scenario: No contract tested twice at the same layer`                   | Contract test        | TD-CT-05 | `tests/factory/test_test_design.py`                | `uv run pytest tests/ -m contract`        | planned |
| Risk-class precedence: testing.yaml override     | `Scenario: Risk class resolved from testing.yaml overrides`              | Contract test        | TD-CT-06 | `tests/factory/test_test_design.py`                | `uv run pytest tests/ -m contract`        | planned |
| Risk-class precedence: convention fallback       | `Scenario: Risk class resolved from convention defaults`                 | Contract test        | TD-CT-07 | `tests/factory/test_test_design.py`                | `uv run pytest tests/ -m contract`        | planned |
| Risk-class precedence: custom class              | `Scenario: Custom project risk class applied`                            | Contract test        | TD-CT-08 | `tests/factory/test_test_design.py`                | `uv run pytest tests/ -m contract`        | planned |
| CRAP threshold from testing.yaml                 | `Scenario: CRAP script reads threshold from testing.yaml`                | Contract test        | TD-CT-09 | `tests/factory/test_crap_score.py`                 | `uv run pytest tests/ -m contract`        | planned |
| CRAP threshold fallback                          | `Scenario: CRAP script falls back to hardcoded default`                  | Contract test        | TD-CT-10 | `tests/factory/test_crap_score.py`                 | `uv run pytest tests/ -m contract`        | planned |
| Gate resolution: trace-to-scenario chain         | `Scenario: Gate resolves trace-to-scenario chain`                        | Integration test     | TD-IT-01 | `tests/factory/test_test_design_verify.py`         | `uv run pytest tests/ -m integration`     | planned |
| Gate: pass on complete coverage                  | `Scenario: Gate passes when all owned contracts have assertions`         | Integration test     | TD-IT-02 | `tests/factory/test_test_design_verify.py`         | `uv run pytest tests/ -m integration`     | planned |
| Gate: fail on missing assertion                  | `Scenario: Gate fails when an owned contract lacks an assertion`         | Integration test     | TD-IT-03 | `tests/factory/test_test_design_verify.py`         | `uv run pytest tests/ -m integration`     | planned |
| Gate: waiver validation                          | `Scenario: Gate accepts valid waivers`                                   | Integration test     | TD-IT-04 | `tests/factory/test_test_design_verify.py`         | `uv run pytest tests/ -m integration`     | planned |
| Gate: skip on no test-design output              | `Scenario: Gate skips stories without test-design output`                | Integration test     | TD-IT-05 | `tests/factory/test_test_design_verify.py`         | `uv run pytest tests/ -m integration`     | planned |
| YAML gates section schema                        | `Scenario: Gates section declares crap_score configuration`              | Deterministic linter | TD-LN-01 | `tests/factory/test_charter_lint.py`               | `uvx ruff check --fix && uvx ruff format` | planned |
| YAML risk_classes section schema                 | `Scenario: Project overrides default risk class settings`                | Deterministic linter | TD-LN-02 | `tests/factory/test_charter_lint.py`               | `uvx ruff check --fix && uvx ruff format` | planned |
| Template includes gates and risk_classes         | `Scenario: Template includes risk_classes schema by example`             | Deterministic linter | TD-LN-03 | `factory/rulebooks/templates/charter-testing.yaml` | visual inspection                         | planned |

### Spec marker convention

Projects that use pytest should carry the scope ID as a marker:

```python
@pytest.mark.spec("TD-CT-03")
@pytest.mark.contract
def test_ownership_goes_to_introducing_story(): ...
```

The marker enables traceability from test to contract-owner table and supports mutation-analysis classification joining mutants to contracts.

## Boundary Cases

| Boundary case                                           | Source scenario or gap                                                              | Risk addressed                             | Owner layer      | Notes                                                        |
| ------------------------------------------------------- | ----------------------------------------------------------------------------------- | ------------------------------------------ | ---------------- | ------------------------------------------------------------ |
| testing.yaml missing entirely                           | `Scenario: Prerequisite fails when testing.yaml is missing`                         | Skill runs against an unconfigured project | Contract test    | Exit with diagnostic, no output                              |
| testing_strategy link present but suites absent         | `Gap: not explicitly covered — testing_strategy present but suites section missing` | Partial charter configuration              | Contract test    | Should fail the prerequisite guard                           |
| Contract traced by exactly one story                    | `Scenario: Ownership assigned to the story that introduces the contract`            | Trivial ownership case                     | Contract test    | The introducing story owns it                                |
| Contract traced by multiple stories in same epic        | `Scenario: Ownership assigned to the story that introduces the contract`            | Intra-epic ownership                       | Contract test    | Dependency order resolves                                    |
| Contract traced by stories in different epics           | `Scenario: Ownership resolved across multiple epics`                                | Cross-epic ownership                       | Contract test    | Single backlog-wide pass                                     |
| Contract with circular dependency among tracing stories | `Gap: not explicitly covered — circular deps among stories tracing same contract`   | Ownership unresolvable                     | Contract test    | Should fail or fall back to first by ID                      |
| Empty risk_classes section in testing.yaml              | `Scenario: Risk class resolved from convention defaults`                            | YAML present but empty                     | Contract test    | Fall through to convention defaults                          |
| Custom risk class with missing format field             | `Gap: not explicitly covered`                                                       | Malformed project config                   | Contract test    | Should reject with diagnostic                                |
| CRAP threshold of zero                                  | `Gap: not explicitly covered`                                                       | Edge value for threshold                   | Contract test    | Valid but flags every function                               |
| Story with traces but no scope-map entry                | `Scenario: Gate exits with code 2 on configuration error`                           | Unresolvable trace                         | Integration test | Exit code 2                                                  |
| Story with empty traces field                           | `Scenario: Gate skips stories without test-design output`                           | No traces to resolve                       | Integration test | Gate passes trivially                                        |
| Waiver pointing to non-existent test module             | `Scenario: Gate rejects waivers without a resolvable owner path`                    | Invalid waiver                             | Integration test | Exit code 1                                                  |
| Waiver pointing to existing module but wrong function   | `Gap: not explicitly covered`                                                       | Partially valid waiver                     | Integration test | Should the gate validate function names or only module paths |
| Prior Tests section with empty test list                | `Gap: not explicitly covered`                                                       | Empty inheritance                          | Integration test | Should fail validation                                       |

## Gap Findings

| Finding                                                             | Source              | Severity | Recommended action                                                                                           |
| ------------------------------------------------------------------- | ------------------- | -------- | ------------------------------------------------------------------------------------------------------------ |
| Acceptance test layer has no Gherkin runner configured              | Charter / repo scan | minor    | Record as planned layer; the test-design skill's behavior is testable through contract and integration tests |
| End-to-end smoke test layer not applicable                          | Feature analysis    | info     | The skill is a document transformation, not a user-facing CLI journey                                        |
| Circular dependency among stories tracing same contract not covered | Spec completeness   | minor    | Add a scenario or clarify that backlog-lint prevents circular deps before test-design runs                   |
| Custom risk class with missing required fields not covered          | Spec completeness   | minor    | Add validation logic to the skill or document the failure mode                                               |
| Waiver function-level validation ambiguous                          | Spec completeness   | minor    | Clarify whether the gate validates module path only or module::function                                      |
| Prior Tests section with empty list not covered                     | Spec completeness   | minor    | Add a scenario covering this edge case                                                                       |
| testing_strategy present but suites absent not explicitly covered   | Spec completeness   | minor    | The prerequisite guard should check both fields independently                                                |

## Defect Severity Triage

| Impact on this feature                                                                                            | Severity          | Expected action                                 |
| ----------------------------------------------------------------------------------------------------------------- | ----------------- | ----------------------------------------------- |
| Ownership resolution assigns wrong owner or duplicates ownership, leading to untested contracts or test conflicts | blocking          | Stop release, fix before merge                  |
| Gate accepts invalid waiver or misses an uncovered scenario, allowing hollow stories through                      | fix-in-same-story | Repair in current story or QA loop              |
| Risk-class precedence chain applies wrong level, producing incorrect test-design format                           | fix-in-same-story | Repair in current story or QA loop              |
| CRAP threshold not read from testing.yaml, silently using hardcoded default                                       | fix-in-same-story | Repair in current story                         |
| Developer-agent invents tests when test-design output exists                                                      | blocking          | Stop release, fix the agent's conditional logic |
| Template missing risk_classes example or gates section                                                            | defer             | File finding, fix in documentation follow-up    |
| create-backlog-write-epics missing the test-design prompt                                                         | defer             | File finding, non-blocking                      |

## Test Retention Policy

- Surviving owner per major contract: contract test layer owns ownership resolution, risk-class precedence, prerequisite guard, and CRAP threshold resolution. Integration test layer owns the gate script's trace-to-scenario chain and waiver validation.
- Expected overlap to remove later: if an acceptance test layer is added later (Gherkin runner), it may overlap with contract tests on ownership resolution scenarios. The contract test survives as the owner; the acceptance test covers only the user-observable integration.
- Consolidation rule: keep one owner per contract per [testing-strategy.md](../../factory/rulebooks/conventions/testing-strategy.md).
- Deletion protocol: follow [testing-strategy.md § Delete overlapping tests safely](../../factory/rulebooks/conventions/testing-strategy.md#delete-overlapping-tests-safely).
