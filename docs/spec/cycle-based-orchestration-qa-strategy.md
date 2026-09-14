# QA Strategy — Cycle-Based Orchestration

Feature trace: [cycle-based-orchestration.feature](cycle-based-orchestration.feature)
Proposal trace: [cycle-based-orchestration.md](../proposals/cycle-based-orchestration.md)

## 1. Feature

The cycle-based orchestration feature replaces the linear playbook-FSM model with a directed-graph delivery model. Five delivery cycles (IDEA, CONCEPT, ROADMAP, REFINE, REALIZE) plus a terminal DONE node form the graph. Artifact state drives transition recommendations. Humans drive routing decisions through cycle selection and delegation grants. The cycle engine is new code under `packages/factory/engine/`. The feature also migrates existing commands (`phase`, `transition-lint`), adds workstream context to usage records, extends the research-brief schema, migrates agent metadata from phase ordinals to cycle eligibility tags, and introduces a LinkML entity model as the canonical domain source.

The feature spans fourteen actors and twenty-five Rules with behavioral scenarios covering workstream lifecycle, cycle navigation, retry management, state concurrency, reconciliation, usage attribution, brownfield entry, research handoff, migration, compatibility, and entity modeling.

## 2. Test Layers in Scope

The project's three-layer model (structural gates, contract tests, behavioral verification) applies. The table below assigns each contract group to its primary owning layer and risk class following the conventions in `factory/rulebooks/conventions/testing-strategy.md`.

### Base — structural gates

| Contract group                             | Mechanism                                                                              | Risk class |
| ------------------------------------------ | -------------------------------------------------------------------------------------- | ---------- |
| Cycle model schema conformance             | `cycle-model-v1.schema.json` validated by transition-lint or a standalone schema check | structural |
| Cycle state schema conformance             | `cycle-state-v1.schema.json` validated by transition-lint                              | structural |
| Session binding schema conformance         | Schema validation in the state adapter                                                 | structural |
| Delivery model structural rules (VR 01-10) | transition-lint finding codes `TL-CYCLE-MODEL`                                         | structural |
| Entity model metamodel validity            | `linkml-lint` and LinkML metamodel validation against `docs/spec/entity-model.yaml`    | structural |
| Feature file syntax                        | `spec-lint` Gherkin parsing                                                            | structural |
| Agent metadata migration shape             | `index-lint` on post-migration INDEX.yaml                                              | structural |

### Middle — contract tests

| Contract group                                       | Module under test                        | Risk class |
| ---------------------------------------------------- | ---------------------------------------- | ---------- |
| Model loading and validation                         | `engine/cycle_model.py`                  | standard   |
| Artifact readiness evaluation                        | `engine/readiness.py`                    | standard   |
| Route recommendation logic (0/1/N routes)            | `engine/recommendations.py`              | standard   |
| Atomic state mutation                                | `engine/state.py`                        | critical   |
| Concurrent workstream access                         | `engine/state.py`                        | critical   |
| Workstream lifecycle (create, continue, switch)      | `engine/workstreams.py`                  | standard   |
| Cycle selection and attempt reset                    | `engine/workstreams.py`                  | standard   |
| Delegation grant creation and following              | `engine/delegation.py`                   | standard   |
| Destination-grant pause conditions                   | `engine/delegation.py`                   | standard   |
| Delegation grant immutability                        | `engine/delegation.py`                   | critical   |
| Retry limit enforcement (consumed-attempt semantics) | `engine/decisions.py`                    | critical   |
| Human retry above limit (allowed_with_warning)       | `engine/decisions.py`                    | standard   |
| Reconciliation trigger conditions                    | `engine/recommendations.py` or readiness | standard   |
| Usage record workstream/cycle field population       | Usage capture adapter                    | standard   |
| Usage null-field behavior when unbound               | Usage capture adapter                    | standard   |
| Research brief linked-field population               | Research brief writer                    | standard   |

### Top — behavioral verification

| Contract group                                           | Entry point                       | Risk class |
| -------------------------------------------------------- | --------------------------------- | ---------- |
| `cycle select` end-to-end (state file + binding update)  | `factory/scripts/cycle`           | standard   |
| `cycle retry` end-to-end (limit enforcement, exit codes) | `factory/scripts/cycle`           | standard   |
| `phase` diagnostic stub (exit 2, replacement message)    | `factory/scripts/phase`           | structural |
| `transition-lint` cycle-model and state-file validation  | `factory/scripts/transition-lint` | standard   |
| Characterization tests for kept contracts                | Existing lint and check commands  | standard   |
| Agent and skill name preservation after migration        | `index-lint --check`              | structural |
| Brownfield bootstrap produces three canonical objects    | Brownfield onboarding playbook    | standard   |
| Workstream switch captures usage boundary                | Session menu + usage adapter      | standard   |
| Usage analyst queries by workstream and cycle            | Usage analysis views              | standard   |

## 3. Contract Owners

Each contract has one owning test or linter. Higher layers may exercise the same path as part of a journey but must not duplicate the owner's assertions.

| Contract                                                      | Risk       | Owning layer | Owner                                    |
| ------------------------------------------------------------- | ---------- | ------------ | ---------------------------------------- |
| Cycle model declares exactly five cycles + DONE               | structural | base         | transition-lint `TL-CYCLE-MODEL`         |
| Routes have from/to/recommend_if, no direction/classification | structural | base         | transition-lint `TL-CYCLE-MODEL`         |
| No executable commands in validator fields                    | structural | base         | transition-lint `TL-CYCLE-MODEL`         |
| Every artifact reference resolves to a declared type          | structural | base         | transition-lint `TL-CYCLE-MODEL`         |
| Cycle state schema conforms to v1                             | structural | base         | transition-lint `TL-CYCLE-STATE`         |
| Session binding digest is 64-char hex                         | structural | base         | schema validation in state adapter       |
| Entity model passes LinkML metamodel                          | structural | base         | `linkml-lint`                            |
| Model loads from tracked source                               | standard   | middle       | `test_cycle_model.py`                    |
| Installed model matches tracked source                        | standard   | top          | installed-shape integration test         |
| Unknown artifact reference fails validation                   | standard   | middle       | `test_cycle_model.py`                    |
| Validator with executable command rejected                    | standard   | middle       | `test_cycle_model.py`                    |
| Route with direction field rejected                           | standard   | middle       | `test_cycle_model.py`                    |
| Readiness: mechanical validation runs unconditionally         | standard   | middle       | `test_readiness.py`                      |
| Readiness: semantic runs only when code/artifacts changed     | standard   | middle       | `test_readiness.py`                      |
| Recommendation: one supported route                           | standard   | middle       | `test_recommendations.py`                |
| Recommendation: zero supported routes                         | standard   | middle       | `test_recommendations.py`                |
| Recommendation: multiple routes, no ranking                   | standard   | middle       | `test_recommendations.py`                |
| Cycle selection resets attempt to 1                           | standard   | middle       | `test_workstreams.py`                    |
| Work-list change resets attempt to 1                          | standard   | middle       | `test_workstreams.py`                    |
| Atomic mutation increments revision                           | critical   | middle       | `test_state.py`                          |
| Stale revision returns conflict without writing               | critical   | middle       | `test_state.py`                          |
| Digest mismatch returns conflict                              | critical   | middle       | `test_state.py`                          |
| Temporary file + atomic replace                               | critical   | middle       | `test_state.py`                          |
| Lock timeout returns workstream_busy                          | critical   | middle       | `test_state.py`                          |
| Two sessions: one succeeds, one gets stale                    | critical   | middle       | `test_state.py`                          |
| Interrupted replacement leaves one complete file              | critical   | middle       | `test_state.py`                          |
| Different workstreams use separate locks                      | critical   | middle       | `test_state.py`                          |
| Conflict during delegation pauses for human                   | critical   | middle       | `test_delegation.py`                     |
| Explicit route grant follows ordered selections               | standard   | middle       | `test_delegation.py`                     |
| Failed evidence does not invalidate grant choice              | standard   | middle       | `test_delegation.py`                     |
| Engine pauses when route grant exhausted                      | standard   | middle       | `test_delegation.py`                     |
| Technical failure stops delegated execution                   | standard   | middle       | `test_delegation.py`                     |
| Destination grant: exactly one route continues                | standard   | middle       | `test_delegation.py`                     |
| Destination grant: zero/multiple routes pause                 | standard   | middle       | `test_delegation.py`                     |
| Destination grant pauses at named destination                 | standard   | middle       | `test_delegation.py`                     |
| Only human creates/replaces/revokes a grant                   | critical   | middle       | `test_delegation.py`                     |
| Delegated retry below limit: allowed                          | critical   | middle       | `test_decisions.py`                      |
| Delegated retry at limit: paused, no state change             | critical   | middle       | `test_decisions.py`                      |
| Human retry at limit: allowed_with_warning                    | standard   | middle       | `test_decisions.py`                      |
| Malformed attempt returns invalid_state                       | standard   | middle       | `test_decisions.py`                      |
| Accepted retry increment is permanent                         | critical   | middle       | `test_decisions.py`                      |
| Usage record includes workstream fields when bound            | standard   | middle       | `test_usage_adapter.py`                  |
| Usage record null fields when unbound                         | standard   | middle       | `test_usage_adapter.py`                  |
| Child agents inherit workstream context                       | standard   | middle       | `test_usage_adapter.py`                  |
| Unavailable attribution reported honestly                     | standard   | middle       | `test_usage_views.py`                    |
| Linked brief includes delivery fields                         | standard   | middle       | `test_research_brief.py`                 |
| Standalone brief omits delivery fields                        | standard   | middle       | `test_research_brief.py`                 |
| `cycle select` exit codes and state update                    | standard   | top          | `test_cycle_select_integration.py`       |
| `cycle retry` exit codes and state update                     | standard   | top          | `test_cycle_retry_integration.py`        |
| `phase advance` exits 2 with replacement message              | structural | top          | `test_phase_stub.py`                     |
| `phase retry` exits 2 with replacement message                | structural | top          | `test_phase_stub.py`                     |
| transition-lint cycle-model validation                        | standard   | top          | `test_transition_lint_integration.py`    |
| transition-lint cycle-state validation                        | standard   | top          | `test_transition_lint_integration.py`    |
| Characterization: standard checks retain contracts            | standard   | top          | characterization test suite              |
| Characterization: branch safety commands                      | standard   | top          | characterization test suite              |
| Every indexed agent/skill name preserved                      | structural | top          | `index-lint --check`                     |
| Pydantic rejects invalid payload before persistence           | standard   | middle       | `test_entity_model.py`                   |
| Persistence round-trips a valid value object                  | standard   | top          | `test_entity_persistence_integration.py` |
| Derived projections match LinkML source                       | structural | top          | `test_entity_projections.py`             |

## 4. Boundary Cases

These cross-boundary interactions deserve dedicated attention because they exercise seams between independently testable components.

### State adapter and filesystem

- **Lock file on a read-only filesystem.** The `.current-work/cycles/.locks/` directory must be writable. A read-only parent prevents lock acquisition, which must return `workstream_busy` rather than crash.
- **State file deleted between lock acquisition and read.** The adapter acquires the lock, then finds the state file missing. Must return a clear error, not a partial write.
- **Temporary file persisted without rename.** A crash after temp-file write but before atomic rename leaves a `.tmp` sibling. The next adapter call must not read the `.tmp` file as state.

### Session binding and workstream state

- **Binding outlives its workstream.** A workstream state file is manually deleted while a session binding still references it. The next mutation attempt must detect the missing state file and return an error rather than creating a new state file from the binding alone.
- **Multiple CLIs with different session-binding directories.** Two CLI types (Claude, Copilot) produce bindings under separate directories. The adapter must resolve the correct binding path for the calling CLI.

### Delegation grant and recommendation engine

- **Grant specifies a cycle that does not exist in the model.** The engine must report the unknown cycle rather than silently skip it.
- **Destination grant with the current cycle as destination.** A `through CONCEPT` grant while already at CONCEPT must pause immediately rather than loop.

### Usage record and workstream context

- **Session switches workstream mid-capture.** A usage record captured between the old binding teardown and the new binding creation must carry null workstream fields, not a stale binding.
- **Child agent dispatch inherits then outlives parent binding.** The child's records must carry the workstream context from dispatch time, even if the parent switches workstreams later.

### Migration and compatibility

- **Agent definition with both phase and cycle fields.** A partially migrated agent definition that retains both `phase:` and `cycle-eligibility:` must fail validation rather than silently prefer one over the other.
- **transition-lint invoked against a pre-migration repository.** If `.current-work/playbook-state.yml` exists but no cycle state files exist, transition-lint must report the absence cleanly (no findings, exit 0) rather than crash on the missing cycle model.

### Research brief and delivery cycle

- **Linked brief with an invalid return_cycle.** A brief declaring `return_cycle: INVALID` must fail schema validation rather than silently break the delivery graph resume.

## 5. Defect Severity Triage

| Severity      | Definition                                                                        | Examples in this feature                                                                                                                                                                             |
| ------------- | --------------------------------------------------------------------------------- | ---------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| S1 — blocker  | Data loss or corruption; silent wrong state; security invariant broken            | State adapter writes without holding the lock. Accepted retry does not persist the increment. Stale revision overwrites newer state. Agent or engine creates a delegation grant.                     |
| S2 — critical | Feature unusable for a common path; wrong recommendation acted on without warning | Recommendation engine ranks when it must not. Delegation grant ignores exhaustion and advances. Cycle selection does not reset attempt. `cycle select` writes state but does not update the binding. |
| S3 — major    | Feature works but produces misleading output; migration gap                       | Usage record carries stale workstream after switch. `phase advance` exits 0 instead of 2. Characterization test fails for a kept contract. Linked research brief missing `origin_cycle`.             |
| S4 — minor    | Cosmetic, wording, or non-blocking inconvenience                                  | Warning message unclear. Recommendation table formatting. Diagnostic stub message names the wrong replacement command.                                                                               |

### Triage rules

1. Any defect where state is silently written when it should not be, or not written when it should be, is S1.
2. Any defect where the human loses routing control (engine acts without human confirmation, grant created by non-human) is S1.
3. Any defect in the concurrency model (lock, digest, revision) is S1.
4. Consumed-attempt semantics violations (increment lost, or increment applied when paused) are S1.
5. Recommendation logic errors that produce a wrong ranking or suppress available routes are S2.
6. Migration defects that break an existing command's contract are S3.
7. Everything else follows the standard severity definitions above.

## 6. Test Retention Policy

### Tests to keep

- **Every critical-risk contract test.** The state adapter, concurrency, retry-limit, and grant-immutability tests are the highest-value investment in this feature. They catch the semantic drift that structural checks miss.
- **One representative per equivalence class for standard-risk contracts.** Model loading (valid, invalid-reference, executable-command, direction-field), recommendation (0/1/N routes), delegation (explicit grant, destination grant, exhaustion, pause conditions).
- **Characterization tests for kept contracts.** These are the migration safety net. They must persist as long as the compatibility contract holds.
- **The phase diagnostic stub test.** Cheap to maintain, catches accidental reactivation of the old command.

### Tests to drop or not write

- **No pytest for structural-risk contracts.** The cycle-model schema, cycle-state schema, session-binding schema, and entity-model metamodel are owned by linters and schema validators. Do not duplicate their assertions in pytest.
- **No separate integration test for every recommendation permutation.** The contract test covers the recommendation logic. The `cycle select` integration test exercises one representative path. Additional integration permutations add maintenance cost without catching different faults.
- **No end-to-end brownfield bootstrap test.** The bootstrap produces three files. Each file has its own structural gate (scope-map via spec-lint, entity-model via linkml-lint, architecture via arch-lint). The contract test for the bootstrap logic verifies the orchestration. An end-to-end test against a real brownfield repository is prohibitively expensive to fixture and maintain.

### Consolidation guard

Before removing any test, apply the five-step safe-deletion protocol from the testing strategy: record before-state, name the surviving owner, introduce a controlled fault, observe the owner fail, record after-state. A test may be removed only when its owning contract is covered by another retained test at the same or lower layer.
