# QA Strategy: activity-graph-orchestration

Generated from:

- Feature spec: `docs/spec/activity-graph-orchestration.feature`
- Entity model: `docs/spec/supplementary_specs/entity-model.md`
- Interface contracts: `docs/spec/supplementary_specs/interface-contracts.md`
- Charter layer bindings: `docs/testing.yaml`
- Repo test infrastructure: `tests/conftest.py`, `tests/factory/`, `tests/integration/`, `packages/usage/tests/`, `pyproject.toml`

## Feature

- Proposal trace: `docs/proposals/activity-graph-orchestration.md`
- Gherkin trace: `docs/spec/activity-graph-orchestration.feature`
- Summary: The activity-graph feature replaces stage-based orchestration with a precondition graph over activities and artifacts. Agents declare structured inputs and outputs. A precondition evaluator checks inputs against the repository and reports evidence. A deterministic fence validates outputs after each activity. Workstream state is immutable after creation; session bindings carry a `workstream_id` key that distinguishes bound, Open Stage, and invalid states. The sequence of activities emerges from the dependency chain. No named stages, no transition matrix, no delegation, and no retry logic exist in the engine. The QA focus is on the precondition evaluator's path resolution algorithm, the fence runner's aggregate pass/fail logic, workstream and session state integrity, scope declaration enforcement across seven artifact formats, and backward compatibility with existing deterministic checks.
- Rules in scope:
  - `Rule: Session menu presents four lanes`
  - `Rule: Housekeeping shows factory state and offers maintenance actions`
  - `Rule: Human operator starts a new workstream`
  - `Rule: Human operator continues an existing workstream`
  - `Rule: Agent definition declares required and contextual inputs`
  - `Rule: Skill definition carries contextual inputs only`
  - `Rule: Precondition evaluator checks agent inputs against the repository`
  - `Rule: Precondition evaluator resolves path patterns with scope filtering`
  - `Rule: Graph-addressable artifact carries a scope declaration`
  - `Rule: Human operator sees all agents with precondition evidence`
  - `Rule: Human operator selects any agent regardless of precondition status`
  - `Rule: Every agent activity is fenced by a deterministic check`
  - `Rule: Human operator fixes an upstream artifact without transition ceremony`
  - `Rule: Workstream state file is immutable after creation`
  - `Rule: Session binding attaches a session to a workstream`
  - `Rule: Intent select lists all agents with precondition status`
  - `Rule: Intent assess runs validators and reports results`
  - `Rule: Usage capture retains structured transcripts`
  - `Rule: Factory content consolidates under .agent-factory/`
  - `Rule: Orchestrator package is retired`
  - `Rule: Cycle-based orchestration proposal is superseded`
  - `Rule: Kept contracts preserve acceptance-commit behavior`
  - `Rule: Rework requires no transition or state update`
  - `Rule: Research brief uses the precondition graph for routing`
  - `Rule: Single delivery sequence completes under the activity model`

## Test Layers in Scope

| Layer                 | Status    | Charter binding                                                          | Feature-specific scope                                                                                                        | Owned contracts                   |
| --------------------- | --------- | ------------------------------------------------------------------------ | ----------------------------------------------------------------------------------------------------------------------------- | --------------------------------- |
| Deterministic linter  | planned   | custom standalone scripts: `packages/usage/scripts/usage-contract-check` | Agent and skill definition structural validation; scope declaration enforcement; workstream state and session binding schemas | AGO-05-LN-01 through AGO-21-LN-01 |
| Acceptance test       | planned   | Factory convention fallback (no Gherkin runner configured)               | Session menu navigation, agent display and selection, upstream fix without ceremony, rework without transition                | AGO-01-AC-01 through AGO-23-AC-01 |
| Contract test         | available | pytest: `uv run pytest --tb=short --quiet tests/`                        | Precondition evaluator logic, path resolution algorithm, fence aggregate pass/fail, workstream immutability enforcement       | AGO-07-CT-01 through AGO-24-CT-01 |
| Integration test      | available | pytest: `uv run pytest --tb=short --quiet tests/`                        | Workstream creation on disk, session binding filesystem, intent CLI scripts, fence evidence storage, factory consolidation    | AGO-03-IT-01 through AGO-22-IT-01 |
| End-to-end smoke test | planned   | Factory convention fallback (no e2e infrastructure configured)           | One proposal-through-implementation sequence without named stage transitions                                                  | AGO-25-E2-01                      |

## Contract Owners

| Contract                                                                           | Source scenario or gap                                                                      | Owner layer           | Test ID      | Test location                                 | Command                                   | State   |
| ---------------------------------------------------------------------------------- | ------------------------------------------------------------------------------------------- | --------------------- | ------------ | --------------------------------------------- | ----------------------------------------- | ------- |
| Agent definition structural parse (inputs.required, outputs)                       | `Scenario: Agent frontmatter carries structured inputs`                                     | Deterministic linter  | AGO-05-LN-01 | `tests/factory/test_agent_definition_lint.py` | lint script                               | planned |
| Skill definition structural parse (context only, no required)                      | `Scenario: Skill frontmatter uses inputs.context without inputs.required`                   | Deterministic linter  | AGO-06-LN-01 | `tests/factory/test_agent_definition_lint.py` | lint script                               | planned |
| Scope declaration present and valid on governed artifacts                          | `Scenario: Proposal carries scope in place of title in YAML frontmatter`                    | Deterministic linter  | AGO-09-LN-01 | `tests/factory/test_scope_lint.py`            | lint script                               | planned |
| Scope declaration absent or unknown rejected                                       | `Scenario: Governed artifact without scope declaration fails lint`                          | Deterministic linter  | AGO-09-LN-02 | `tests/factory/test_scope_lint.py`            | lint script                               | planned |
| Workstream state schema (schema_version 2, no forbidden fields)                    | `Scenario: Workstream state file contains only identity fields`                             | Deterministic linter  | AGO-14-LN-01 | `tests/factory/test_workstream_lint.py`       | lint script                               | planned |
| Session binding schema (workstream_id key present)                                 | `Scenario: Session binding file records binding metadata`                                   | Deterministic linter  | AGO-15-LN-01 | `tests/factory/test_workstream_lint.py`       | lint script                               | planned |
| No references to orchestrator package remain                                       | `Scenario: No references to orchestrator remain`                                            | Deterministic linter  | AGO-20-LN-01 | `tests/factory/test_retirement_lint.py`       | lint script                               | planned |
| Superseded proposal carries status: superseded                                     | `Scenario: Superseded proposal carries status superseded`                                   | Deterministic linter  | AGO-21-LN-01 | `tests/factory/test_retirement_lint.py`       | lint script                               | planned |
| Evaluator reports evidence for every agent                                         | `Scenario: Evaluator reports evidence for every agent`                                      | Contract test         | AGO-07-CT-01 | `tests/factory/test_eligibility.py`           | `uv run pytest --tb=short --quiet tests/` | planned |
| Agent with no required inputs always eligible                                      | `Scenario: Agent with no required inputs is always eligible`                                | Contract test         | AGO-07-CT-02 | `tests/factory/test_eligibility.py`           | `uv run pytest --tb=short --quiet tests/` | planned |
| Evaluator checks condition field+value against frontmatter                         | `Scenario: Required input with conditions checks frontmatter fields`                        | Contract test         | AGO-07-CT-03 | `tests/factory/test_eligibility.py`           | `uv run pytest --tb=short --quiet tests/` | planned |
| Evaluator checks condition field+one_of                                            | `Scenario: Required input with one_of condition accepts any listed value`                   | Contract test         | AGO-07-CT-04 | `tests/factory/test_eligibility.py`           | `uv run pytest --tb=short --quiet tests/` | planned |
| Evaluator checks condition with validator (pass and fail)                          | `Scenario: Required input with check condition that passes marks the requirement satisfied` | Contract test         | AGO-07-CT-05 | `tests/factory/test_eligibility.py`           | `uv run pytest --tb=short --quiet tests/` | planned |
| Path resolution: glob expansion from placeholders                                  | `Scenario: Placeholder in path pattern expands to glob`                                     | Contract test         | AGO-08-CT-01 | `tests/factory/test_path_resolution.py`       | `uv run pytest --tb=short --quiet tests/` | planned |
| Path resolution: scope filtering (bound workstream vs Open Stage)                  | `Scenario: Scope filtering narrows candidates when a workstream is bound`                   | Contract test         | AGO-08-CT-02 | `tests/factory/test_path_resolution.py`       | `uv run pytest --tb=short --quiet tests/` | planned |
| Path resolution: condition checking removes failing candidates                     | `Scenario: Condition checking removes failing candidates`                                   | Contract test         | AGO-08-CT-03 | `tests/factory/test_path_resolution.py`       | `uv run pytest --tb=short --quiet tests/` | planned |
| Path resolution: cardinality (zero / one / multiple survivors)                     | `Scenario: Zero survivors means unsatisfied precondition`                                   | Contract test         | AGO-08-CT-04 | `tests/factory/test_path_resolution.py`       | `uv run pytest --tb=short --quiet tests/` | planned |
| Fence: required output missing fails                                               | `Scenario: Agent outputs are validated by a deterministic fence after completion`           | Contract test         | AGO-12-CT-01 | `tests/factory/test_fence.py`                 | `uv run pytest --tb=short --quiet tests/` | planned |
| Fence: optional output unchanged is skipped                                        | `Scenario: Fence pass makes downstream preconditions satisfiable`                           | Contract test         | AGO-12-CT-02 | `tests/factory/test_fence.py`                 | `uv run pytest --tb=short --quiet tests/` | planned |
| Fence: aggregate pass/fail (minimum_changed, validator results)                    | `Scenario: Fence failure is reported without blocking human action`                         | Contract test         | AGO-12-CT-03 | `tests/factory/test_fence.py`                 | `uv run pytest --tb=short --quiet tests/` | planned |
| Workstream state file immutable after creation                                     | `Scenario: Attempted modification of an existing state file fails`                          | Contract test         | AGO-14-CT-01 | `tests/factory/test_workstream_state.py`      | `uv run pytest --tb=short --quiet tests/` | planned |
| Multiple sessions bind same workstream without modifying state                     | `Scenario: Multiple sessions bind to the same workstream`                                   | Contract test         | AGO-14-CT-02 | `tests/factory/test_workstream_state.py`      | `uv run pytest --tb=short --quiet tests/` | planned |
| Session binding: known workstream_id = bound, null = Open Stage, missing = invalid | `Scenario: Session binding file records binding metadata`                                   | Contract test         | AGO-15-CT-01 | `tests/factory/test_session_binding.py`       | `uv run pytest --tb=short --quiet tests/` | planned |
| Research agent output satisfies downstream preconditions                           | `Scenario: Research agent output satisfies downstream preconditions`                        | Contract test         | AGO-24-CT-01 | `tests/factory/test_eligibility.py`           | `uv run pytest --tb=short --quiet tests/` | planned |
| Workstream creation writes state file with correct fields                          | `Scenario: Project Work lane creates a named workstream`                                    | Integration test      | AGO-03-IT-01 | `tests/integration/test_workstream.py`        | `uv run pytest --tb=short --quiet tests/` | planned |
| Workstream continuation binds session and shows evidence                           | `Scenario: Selected workstream binds to the session and shows precondition evidence`        | Integration test      | AGO-04-IT-01 | `tests/integration/test_workstream.py`        | `uv run pytest --tb=short --quiet tests/` | planned |
| Fence runner invokes validators and stores evidence YAML                           | `Scenario: Agent outputs are validated by a deterministic fence after completion`           | Integration test      | AGO-12-IT-01 | `tests/integration/test_fence_runner.py`      | `uv run pytest --tb=short --quiet tests/` | planned |
| External chaining: orchestrator reads fence and evaluator evidence                 | `Scenario: Chaining happens externally when fences pass`                                    | Integration test      | AGO-12-IT-02 | `tests/integration/test_fence_runner.py`      | `uv run pytest --tb=short --quiet tests/` | planned |
| intent select lists agents with precondition status                                | `Scenario: intent select lists every agent with its precondition status`                    | Integration test      | AGO-16-IT-01 | `tests/integration/test_intent.py`            | `uv run pytest --tb=short --quiet tests/` | planned |
| intent assess runs validators and reports results                                  | `Scenario: intent assess runs all applicable validators`                                    | Integration test      | AGO-17-IT-01 | `tests/integration/test_intent.py`            | `uv run pytest --tb=short --quiet tests/` | planned |
| Structured transcript retained alongside text rendering                            | `Scenario: Structured transcript is retained alongside text rendering`                      | Integration test      | AGO-18-IT-01 | `tests/integration/test_transcript.py`        | `uv run pytest --tb=short --quiet tests/` | planned |
| Factory tree consolidated under .agent-factory/                                    | `Scenario: Installed factory tree lives under .agent-factory/factory/`                      | Integration test      | AGO-19-IT-01 | `tests/integration/test_init_factory.py`      | `uv run pytest --tb=short --quiet tests/` | planned |
| Internal naming drops factory- prefix                                              | `Scenario: Internal naming drops the factory- prefix`                                       | Integration test      | AGO-19-IT-02 | `tests/integration/test_init_factory.py`      | `uv run pytest --tb=short --quiet tests/` | planned |
| Kept contracts preserve command names and exit behavior                            | `Scenario: Standard check commands retain their contracts`                                  | Integration test      | AGO-22-IT-01 | `tests/integration/test_compatibility.py`     | `uv run pytest --tb=short --quiet tests/` | planned |
| Session menu displays four lanes                                                   | `Scenario: Menu displays Help, Housekeeping, Project Work, and Open Stage`                  | Acceptance test       | AGO-01-AC-01 | —                                             | —                                         | planned |
| Housekeeping shows factory state and runs maintenance actions                      | `Scenario: About section displays factory state`                                            | Acceptance test       | AGO-02-AC-01 | —                                             | —                                         | planned |
| All agents displayed with precondition evidence after binding                      | `Scenario: All agents displayed after workstream binding`                                   | Acceptance test       | AGO-10-AC-01 | —                                             | —                                         | planned |
| Human selects agent regardless of precondition status                              | `Scenario: Human selects an agent with unsatisfied inputs`                                  | Acceptance test       | AGO-11-AC-01 | —                                             | —                                         | planned |
| Upstream artifact fix requires no state update                                     | `Scenario: Fixing an artifact requires no state update`                                     | Acceptance test       | AGO-13-AC-01 | —                                             | —                                         | planned |
| Rework requires no transition or state update                                      | `Scenario: Fixing an upstream artifact is just fixing an artifact`                          | Acceptance test       | AGO-23-AC-01 | —                                             | —                                         | planned |
| Proposal through implementation without named stage transitions                    | `Scenario: Proposal through implementation without named stage transitions`                 | End-to-end smoke test | AGO-25-E2-01 | —                                             | —                                         | planned |

### Spec marker convention

Projects that use pytest should carry the scope ID as a marker:

```python
@pytest.mark.spec("AGO-08-CT-02")
@pytest.mark.contract
def test_scope_filtering_narrows_to_bound_workstream(): ...
```

The marker enables traceability from test to contract-owner table and supports mutation-analysis classification joining mutants to contracts.

## Boundary Cases

| Boundary case                                                  | Source scenario or gap                                                                       | Risk addressed                         | Owner layer          | Notes                                                    |
| -------------------------------------------------------------- | -------------------------------------------------------------------------------------------- | -------------------------------------- | -------------------- | -------------------------------------------------------- |
| Path pattern matches zero files                                | `Scenario: Zero survivors means unsatisfied precondition`                                    | False eligibility on empty match       | Contract test        | Evaluator returns unsatisfied                            |
| Path pattern matches exactly one file                          | `Scenario: One survivor satisfies the precondition`                                          | Trivial satisfied case                 | Contract test        | Verified by AGO-08-CT-04                                 |
| Path pattern matches multiple files                            | `Scenario: Multiple survivors are reported for human selection`                              | Ambiguous precondition                 | Contract test        | Evaluator reports all candidates                         |
| Scope filtering with bound workstream, artifact scope = global | `Scenario: Scope filtering narrows candidates when a workstream is bound`                    | Global artifacts survive filtering     | Contract test        | Global always passes                                     |
| Scope filtering in Open Stage (workstream_id = null)           | `Scenario: Scope filtering is skipped in Open Stage`                                         | All files pass when unbound            | Contract test        | No scope check runs                                      |
| Condition field+value mismatch                                 | `Scenario: Condition checking removes failing candidates`                                    | Wrong artifact accepted                | Contract test        | Field check returns false                                |
| Condition check with failing validator                         | `Scenario: Required input with check condition that fails marks the requirement unsatisfied` | Validator failure reported as evidence | Contract test        | Human can still select the agent                         |
| Fence: required output not created or modified                 | `Scenario: Agent outputs are validated by a deterministic fence after completion`            | Invalid downstream chaining            | Contract test        | Fence fails, evidence stored                             |
| Fence: optional output not changed                             | `Scenario: Fence pass makes downstream preconditions satisfiable`                            | Unnecessary failure on optional output | Contract test        | Optional output skipped                                  |
| Fence: declarations_changed below minimum_changed              | `Gap: minimum_changed = 0 with no outputs changed is a valid no-output activity`             | Edge case for legitimate no-op agents  | Contract test        | minimum_changed = 0 means the fence cannot fail on count |
| Workstream state file modification attempted                   | `Scenario: Attempted modification of an existing state file fails`                           | Data corruption from stale binding     | Contract test        | Write rejected, file unchanged                           |
| Session binding workstream_id = null (Open Stage)              | `Scenario: Session binding file records binding metadata`                                    | Null vs missing key confusion          | Contract test        | Null is valid; missing key is rejected                   |
| Session binding workstream_id key absent                       | `Scenario: Session binding file records binding metadata`                                    | Invalid binding persisted              | Contract test        | Validation rejects the file                              |
| Session binding references nonexistent workstream              | `Gap: not explicitly covered`                                                                | Dangling reference                     | Contract test        | workstream_id must resolve to existing state file        |
| Agent with empty inputs.required list                          | `Scenario: Agent with no required inputs is always eligible`                                 | Always-eligible edge                   | Contract test        | Evaluator marks all requirements satisfied               |
| Workstream state with extra fields (cycle, attempt)            | `Scenario: Workstream state file contains only identity fields`                              | Stale v1 format accepted as v2         | Deterministic linter | Forbidden field presence fails validation                |
| Scope declaration with unknown workstream identifier           | `Scenario: Governed artifact with unknown scope value fails lint`                            | Orphaned artifact                      | Deterministic linter | Lint rejects unknown scope                               |
| Non-governed artifact (ADR) checked for scope                  | `Scenario: Non-governed artifact needs no scope declaration`                                 | False positive on unscoped artifact    | Deterministic linter | No scope check applies                                   |
| Transcript retention set to omit                               | `Scenario: Omit retention writes neither file`                                               | Partial write leaves orphan files      | Integration test     | Neither text nor structured file written                 |
| .current-work/ paths unchanged after consolidation             | `Scenario: .current-work/ remains the runtime root`                                          | Branching and dispatch paths break     | Integration test     | All existing path contracts preserved                    |

## Gap Findings

| Finding                                                                           | Source              | Severity | Recommended action                                                                                                                                                                              |
| --------------------------------------------------------------------------------- | ------------------- | -------- | ----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| Acceptance test layer has no Gherkin runner configured                            | Charter / repo scan | minor    | Record as planned layer; session-level behaviors (menu navigation, agent selection, rework without ceremony) are verifiable only through manual acceptance or future Gherkin runner integration |
| End-to-end smoke test layer not declared in charter                               | Charter / repo scan | minor    | Record as planned; the full delivery sequence (AGO-25-E2-01) needs infrastructure for a scripted multi-agent walkthrough                                                                        |
| Charter deterministic_linter entry_point references usage-contract-check only     | Charter / repo scan | minor    | The activity-graph feature introduces new lint scripts (scope-lint, workstream-lint, agent-definition-lint) that the charter does not yet declare; update testing.yaml after implementation     |
| Session binding referencing nonexistent workstream not explicitly covered         | Spec completeness   | minor    | Add a scenario covering the case where workstream_id names a nonexistent state file; validation-rules.md says it must reference an existing file                                                |
| minimum_changed = 0 boundary not explicitly covered in a scenario                 | Spec completeness   | info     | Validation rules permit it; a scenario demonstrating a legitimate no-output activity would anchor the edge case                                                                                 |
| Research brief omits cycle fields but no scenario tests rejection of stale fields | Spec completeness   | info     | Add a scenario confirming that a brief with origin_cycle or return_cycle fails validation                                                                                                       |
| Existing pyproject.toml markers reference only ACX-\* scope IDs                   | Repo scan           | info     | After implementation, add AGO-\* as a recognized spec marker pattern in pyproject.toml                                                                                                          |

## Defect Severity Triage

| Impact on this feature                                                                                                                                        | Severity          | Expected action                              |
| ------------------------------------------------------------------------------------------------------------------------------------------------------------- | ----------------- | -------------------------------------------- |
| Precondition evaluator gives wrong evidence (eligible when unsatisfied, or vice versa), causing agents to run against missing inputs or blocking ready agents | blocking          | Stop release, fix before merge               |
| Fence runner passes when a required output is missing or a validator fails, enabling invalid downstream chaining                                              | blocking          | Stop release, fix before merge               |
| Workstream state file modified after creation, breaking the immutability guarantee and corrupting shared state                                                | blocking          | Stop release, fix before merge               |
| Scope filtering accepts wrong workstream's artifacts, causing agents to work on out-of-scope inputs                                                           | fix-in-same-story | Repair in current story or QA loop           |
| Session binding allows missing workstream_id key, persisting structurally invalid state                                                                       | fix-in-same-story | Repair in current story or QA loop           |
| intent select shows stale or incomplete evidence, causing human to work from wrong information                                                                | fix-in-same-story | Repair in current story or QA loop           |
| Factory consolidation misses a path contract, breaking scripts that depend on old locations                                                                   | fix-in-same-story | Repair in current story or QA loop           |
| Scope lint rejects a valid artifact format or misses a governed artifact type                                                                                 | fix-in-same-story | Repair in current story                      |
| Superseded proposal status not set after migration                                                                                                            | defer             | File finding, fix in documentation follow-up |
| Orchestrator references remain in non-critical documentation                                                                                                  | defer             | File finding or backlog follow-up            |

## Test Retention Policy

- Surviving owner per major contract: path resolution and fence logic at the contract test layer; CLI scripts and filesystem operations at the integration test layer; structural validation at the deterministic linter layer.
- Expected overlap to remove later: integration tests that exercise path resolution end-to-end may duplicate contract test assertions on evaluator evidence; the contract test owns the logic, and the integration test owns the filesystem boundary.
- Consolidation rule: keep one owner per contract per [testing-strategy.md](../../factory/rulebooks/conventions/testing-strategy.md).
- Deletion protocol: follow [testing-strategy.md § Delete overlapping tests safely](../../factory/rulebooks/conventions/testing-strategy.md#delete-overlapping-tests-safely).
