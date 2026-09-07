# QA Strategy: agent-context

Generated from:

- Feature spec: `docs/spec/agent-context.feature`
- Entity model: `docs/spec/supplementary_specs/entity-model.md`
- Interface contracts: `docs/spec/supplementary_specs/interface-contracts.md`
- Charter layer bindings: `docs/charter/testing.yaml`
- Repo test infrastructure: `tests/conftest.py`, `tests/factory/`, `tests/orchestrator/`

## Feature

- Proposal trace: `docs/proposals/yaml-charter-lifecycle.md`
- Gherkin trace: `docs/spec/agent-context.feature`
- Summary: The agent context feature introduces a two-layer YAML-based routing interface between factory agents and project knowledge. The primary QA risk is in the validation script (`context-lint`), the format-detection chain shared across all factory consumers, and the mode lifecycle transitions. Backward compatibility with legacy markdown and YAML charter formats is a cross-cutting concern that touches every consumer in the factory inventory.
- Rules in scope:
  - `Rule: Factory agent reads project context through unified two-layer routing`
  - `Rule: User initializes agent context for a greenfield project`
  - `Rule: User onboards brownfield documentation into agent context`
  - `Rule: User updates agent context as decisions emerge`
  - `Rule: User transitions context from primary to index mode`
  - `Rule: context-lint validates agent context structure and references`
  - `Rule: Legacy projects continue working without migration`
  - `Rule: testing.yaml operates as a lifecycle-exempt peer file`
  - `Rule: Factory consumers resolve context file paths via format detection`
  - `Rule: Convention codifies agent context composition rules`

## Test Layers in Scope

| Layer                 | Status  | Charter binding                                                                          | Feature-specific scope                                                                                                                              | Owned contracts                                               |
| --------------------- | ------- | ---------------------------------------------------------------------------------------- | --------------------------------------------------------------------------------------------------------------------------------------------------- | ------------------------------------------------------------- |
| Deterministic linter  | planned | Factory convention fallback (no linter layer declared in charter)                        | Validate YAML structure, key presence, mode field values, and reference resolution in context-lint output                                           | CX-FILE, CX-PARSE, CX-KEYS, CX-NULL, CX-MODE, CX-MODE-INVALID |
| Contract test         | planned | `pytest`, infrastructure: `mock`, entry_point: `uv run pytest tests/`, fidelity: fs real | context-lint finding codes, format-detection chain logic, mode-transition condition evaluation, key-path reference resolution, deferred-field rules | CX-SRC, CX-SRC-EXIST, CX-SRC-STALE, CX-GUIDE-REF, CX-FORMAT   |
| Integration test      | planned | Factory convention fallback (no integration layer declared in charter)                   | Format detection across real directory structures with mixed locations; testing.yaml path resolution; legacy fallback with actual charter files     | Format detection, testing.yaml resolution                     |
| Acceptance test       | out     | Factory convention fallback                                                              | Not applicable — agent context is consumed by skills and scripts, not by end users through a Gherkin runner                                         | n/a                                                           |
| End-to-end smoke test | out     | Factory convention fallback                                                              | Not applicable — no single CLI journey exercises the full agent-context lifecycle in isolation                                                      | n/a                                                           |

## Contract Owners

| Contract                                             | Source scenario or gap                                                                          | Owner layer      | Test ID      | Test location                                   | Command                        | State   |
| ---------------------------------------------------- | ----------------------------------------------------------------------------------------------- | ---------------- | ------------ | ----------------------------------------------- | ------------------------------ | ------- |
| CX-FILE reports missing required file                | `Scenario: CX-FILE reports missing required file`                                               | Contract test    | ACX-01-CT-01 | `tests/factory/test_context_lint.py`            | `uv run pytest tests/factory/` | planned |
| CX-FILE reading-guides.yaml not required in primary  | `Scenario: CX-FILE does not require reading-guides.yaml when mode is primary`                   | Contract test    | ACX-01-CT-02 | `tests/factory/test_context_lint.py`            | `uv run pytest tests/factory/` | planned |
| CX-PARSE reports invalid YAML                        | `Scenario: CX-PARSE reports invalid YAML`                                                       | Contract test    | ACX-02-CT-01 | `tests/factory/test_context_lint.py`            | `uv run pytest tests/factory/` | planned |
| CX-KEYS reports missing required top-level keys      | `Scenario: CX-KEYS reports missing required top-level keys`                                     | Contract test    | ACX-03-CT-01 | `tests/factory/test_context_lint.py`            | `uv run pytest tests/factory/` | planned |
| CX-KEYS reports deferred coexisting with name/source | `Scenario: CX-KEYS reports deferred coexisting with name or source`                             | Contract test    | ACX-03-CT-02 | `tests/factory/test_context_lint.py`            | `uv run pytest tests/factory/` | planned |
| CX-NULL warning in default mode                      | `Scenario: CX-NULL reports null values in default mode`                                         | Contract test    | ACX-04-CT-01 | `tests/factory/test_context_lint.py`            | `uv run pytest tests/factory/` | planned |
| CX-NULL error in planning-gate mode                  | `Scenario: CX-NULL reports null values as error in planning-gate mode`                          | Contract test    | ACX-04-CT-02 | `tests/factory/test_context_lint.py`            | `uv run pytest tests/factory/` | planned |
| CX-MODE reports valid mode field                     | `Scenario: CX-MODE reports valid mode field`                                                    | Contract test    | ACX-05-CT-01 | `tests/factory/test_context_lint.py`            | `uv run pytest tests/factory/` | planned |
| CX-MODE-INVALID reports unrecognized mode value      | `Scenario: CX-MODE-INVALID reports unrecognized mode value`                                     | Contract test    | ACX-05-CT-02 | `tests/factory/test_context_lint.py`            | `uv run pytest tests/factory/` | planned |
| CX-SRC reports missing source pointer in index mode  | `Scenario: CX-SRC reports missing source pointer when mode is index`                            | Contract test    | ACX-06-CT-01 | `tests/factory/test_context_lint.py`            | `uv run pytest tests/factory/` | planned |
| CX-SRC-EXIST reports unresolvable source path        | `Scenario: CX-SRC-EXIST reports unresolvable source path`                                       | Contract test    | ACX-07-CT-01 | `tests/factory/test_context_lint.py`            | `uv run pytest tests/factory/` | planned |
| CX-SRC-STALE reports stale index entry               | `Scenario: CX-SRC-STALE reports stale index entry`                                              | Contract test    | ACX-08-CT-01 | `tests/factory/test_context_lint.py`            | `uv run pytest tests/factory/` | planned |
| CX-GUIDE-REF validates key-path references           | `Scenario: CX-GUIDE-REF validates key-path references`                                          | Contract test    | ACX-09-CT-01 | `tests/factory/test_context_lint.py`            | `uv run pytest tests/factory/` | planned |
| CX-GUIDE-REF reports unresolvable key path           | `Scenario: CX-GUIDE-REF reports unresolvable key path`                                          | Contract test    | ACX-09-CT-02 | `tests/factory/test_context_lint.py`            | `uv run pytest tests/factory/` | planned |
| CX-GUIDE-REF checks key existence only               | `Scenario: CX-GUIDE-REF checks key existence only not value`                                    | Contract test    | ACX-09-CT-03 | `tests/factory/test_context_lint.py`            | `uv run pytest tests/factory/` | planned |
| CX-FORMAT reports mixed locations                    | `Scenario: CX-FORMAT reports mixed locations`                                                   | Contract test    | ACX-10-CT-01 | `tests/factory/test_context_lint.py`            | `uv run pytest tests/factory/` | planned |
| CX-FORMAT does not flag split testing.yaml location  | `Scenario: CX-FORMAT does not flag split testing.yaml location`                                 | Contract test    | ACX-10-CT-02 | `tests/factory/test_context_lint.py`            | `uv run pytest tests/factory/` | planned |
| Format detection selects YAML agent-context mode     | `Scenario: Format detection selects YAML agent-context mode`                                    | Contract test    | ACX-11-CT-01 | `tests/factory/test_format_detection.py`        | `uv run pytest tests/factory/` | planned |
| Format detection falls back to legacy YAML charter   | `Scenario: Format detection falls back to legacy YAML charter`                                  | Contract test    | ACX-11-CT-02 | `tests/factory/test_format_detection.py`        | `uv run pytest tests/factory/` | planned |
| Format detection falls back to legacy markdown       | `Scenario: Format detection falls back to legacy markdown charter`                              | Contract test    | ACX-11-CT-03 | `tests/factory/test_format_detection.py`        | `uv run pytest tests/factory/` | planned |
| Format detection reports error on mixed locations    | `Scenario: Format detection reports error on mixed locations`                                   | Contract test    | ACX-11-CT-04 | `tests/factory/test_format_detection.py`        | `uv run pytest tests/factory/` | planned |
| Legacy markdown charter passes context-lint          | `Scenario: Legacy markdown charter passes context-lint`                                         | Integration test | ACX-12-IT-01 | `tests/factory/test_context_lint_legacy.py`     | `uv run pytest tests/factory/` | planned |
| testing.yaml CX-PARSE only validation                | `Scenario: context-lint validates testing.yaml with CX-PARSE only`                              | Contract test    | ACX-13-CT-01 | `tests/factory/test_context_lint.py`            | `uv run pytest tests/factory/` | planned |
| testing.yaml resolution walks both paths             | `Scenario: testing.yaml resolution walks both paths`                                            | Integration test | ACX-14-IT-01 | `tests/factory/test_testing_yaml_resolution.py` | `uv run pytest tests/factory/` | planned |
| testing.yaml at new path takes precedence            | `Scenario: testing.yaml at new path takes precedence`                                           | Integration test | ACX-14-IT-02 | `tests/factory/test_testing_yaml_resolution.py` | `uv run pytest tests/factory/` | planned |
| Deferred field is sole key at leaf position          | `Scenario: update-context writes deferred field`                                                | Contract test    | ACX-15-CT-01 | `tests/factory/test_context_lint.py`            | `uv run pytest tests/factory/` | planned |
| Transition condition excludes null and deferred      | `Scenario: Transition not blocked by deferred fields` + `Transition not blocked by null fields` | Contract test    | ACX-16-CT-01 | `tests/factory/test_mode_transition.py`         | `uv run pytest tests/factory/` | planned |
| Transition blocked by null field without deferral    | `Scenario: Transition blocked by null field without deferral`                                   | Contract test    | ACX-16-CT-02 | `tests/factory/test_mode_transition.py`         | `uv run pytest tests/factory/` | planned |

### Spec marker convention

Projects that use pytest should carry the scope ID as a marker:

```python
@pytest.mark.spec("ACX-01")
@pytest.mark.contract
def test_cx_file_reports_missing_required_file(): ...
```

The marker enables traceability from test to contract-owner table and supports mutation-analysis classification joining mutants to contracts.

## Boundary Cases

| Boundary case                                              | Source scenario or gap                                              | Risk addressed                                                            | Owner layer      | Notes                                                                      |
| ---------------------------------------------------------- | ------------------------------------------------------------------- | ------------------------------------------------------------------------- | ---------------- | -------------------------------------------------------------------------- |
| Empty `docs/agent-context/` directory (no files)           | `Scenario: CX-FILE reports missing required file`                   | All three index files missing produces three CX-FILE errors               | Contract test    | Each missing file is reported independently, not short-circuited           |
| YAML syntax error in index file                            | `Scenario: CX-PARSE reports invalid YAML`                           | Malformed YAML stops further validation of that file                      | Contract test    | Subsequent CX-KEYS and CX-SRC checks should not run on an unparseable file |
| `deferred` key coexists with `name`                        | `Scenario: CX-KEYS reports deferred coexisting with name or source` | Data integrity — deferred must be sole key                                | Contract test    | Exact error: CX-KEYS, not CX-SRC or CX-NULL                                |
| `mode` field has invalid value (not primary or index)      | `Scenario: CX-MODE-INVALID reports unrecognized mode value`         | Unrecognized mode could silently pass or crash                            | Contract test    | CX-MODE-INVALID error severity; scenario added per SPEC-0013 resolution    |
| All fields null, no deferred — transition condition        | `Scenario: Transition blocked by null field without deferral`       | Transition should not fire when fields are null without explicit deferral | Contract test    | Null without deferral means the field needs a value, not a source pointer  |
| Source file exists but was never modified (mtime = 0)      | Gap: edge case for CX-SRC-STALE mtime comparison                    | Zero or equal mtime edge in staleness check                               | Contract test    | Recommend specifying behavior when mtimes are equal                        |
| Reading guide references a file that does not exist        | `Scenario: CX-GUIDE-REF reports unresolvable key path`              | Broken routing — agent follows dead reference                             | Contract test    | File existence vs. key-path existence are two different failures           |
| Both `docs/agent-context/` and `docs/charter/` exist       | `Scenario: CX-FORMAT reports mixed locations`                       | Ambiguous context source                                                  | Contract test    | CX-FORMAT is error severity — blocks, not warns                            |
| `docs/charter/testing.yaml` only, no `docs/agent-context/` | `Scenario: testing.yaml resolution walks both paths`                | Backward compat — testing.yaml at old path must still work                | Integration test | No CX-FORMAT error for this specific case                                  |
| All fields have sources, user declines transition          | `Scenario: User declines mode transition`                           | User agency — transition is never automatic                               | Contract test    | Files must remain in mode: primary after decline                           |
| Key-path reference to array-typed key                      | `Scenario: CX-GUIDE-REF validates key-path references`              | Array keys are referenced by parent, not by index                         | Contract test    | e.g., `stack.yaml#languages` references the entire list                    |
| Greenfield project with no reading guide                   | `Scenario: Greenfield project has no reading guide`                 | No CX-FILE error for missing reading-guides.yaml in primary mode          | Contract test    | Reading guide absence is legal when all index files are mode: primary      |

## Gap Findings

| Finding                                                                                                                                                         | Source         | Severity | Recommended action                                                                |
| --------------------------------------------------------------------------------------------------------------------------------------------------------------- | -------------- | -------- | --------------------------------------------------------------------------------- |
| No integration test layer declared in charter                                                                                                                   | Charter scan   | info     | Add integration test layer to `docs/charter/testing.yaml` when tests are written  |
| No deterministic linter layer declared in charter                                                                                                               | Charter scan   | info     | Add linter layer binding when context-lint is used as a gate                      |
| No scenario for CX-SRC-STALE when mtimes are equal                                                                                                              | Feature spec   | low      | Clarify: equal mtime means not stale                                              |
| Charter declares `contract_test` with `fidelity.external_services: mocked` — context-lint tests are filesystem-heavy, not service-heavy; fidelity is sufficient | Fidelity check | info     | No action needed — filesystem fidelity is real, which covers context-lint's needs |

## Defect Severity Triage

| Impact on this feature                                                                                   | Severity          | Expected action                                       |
| -------------------------------------------------------------------------------------------------------- | ----------------- | ----------------------------------------------------- |
| context-lint silently passes invalid YAML or missing keys (false negative on CX-PARSE, CX-KEYS, CX-FILE) | blocking          | Stop release, fix before merge                        |
| CX-FORMAT fails to detect mixed locations (legacy project corruption risk)                               | blocking          | Stop release, fix before merge                        |
| Format detection returns wrong mode (agents read wrong files)                                            | blocking          | Stop release, fix before merge                        |
| Mode transition fires without user confirmation                                                          | blocking          | Stop release, fix before merge                        |
| CX-GUIDE-REF fails to detect broken key-path reference                                                   | fix-in-same-story | Repair in current story or QA loop                    |
| CX-SRC-STALE false positive on equal mtime                                                               | defer             | File finding or backlog follow-up                     |
| CX-NULL severity not elevated in `--planning-gate` mode                                                  | fix-in-same-story | Repair in current story or QA loop                    |
| testing.yaml validation applies CX-SRC checks incorrectly                                                | fix-in-same-story | Repair in current story — violates carve-out contract |
| Minor wording in CX-MODE info message                                                                    | defer             | File finding or backlog follow-up                     |

## Test Retention Policy

- Surviving owner per major contract: contract tests own all CX-\* finding codes and format-detection logic; integration tests own legacy-fallback and testing.yaml resolution across real directory structures.
- Expected overlap to remove later: format-detection logic may be tested in both contract tests (unit-level) and integration tests (directory-level). Once contract tests stabilize, integration tests for the same detection logic should be reviewed for overlap.
- Consolidation rule: keep one owner per contract per [testing-strategy.md](../../factory/rulebooks/conventions/testing-strategy.md).
- Deletion protocol: follow [testing-strategy.md § Delete overlapping tests safely](../../factory/rulebooks/conventions/testing-strategy.md#delete-overlapping-tests-safely).
