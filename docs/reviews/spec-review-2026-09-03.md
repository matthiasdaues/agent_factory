# Specification Review: agent-context

**Date:** 2026-09-03\
**Reviewer:** spec-review-agent\
**Specification:** `docs/spec/agent-context.feature` (10 Rules, 56 Scenarios)\
**Proposal trace:** `docs/proposals/yaml-charter-lifecycle.md`

## Reviewed Specification

Artifacts read:

- `docs/spec/agent-context.feature` -- 10 Rules, 56 Scenarios
- `docs/spec/agent-context-gaps.md` -- completeness report
- `docs/spec/agent-context-qa-strategy.md` -- per-feature QA strategy
- `docs/spec/scope-map.md` -- 10 new rows with status "specified"
- `docs/spec/supplementary_specs/entity-model.md` -- agent-context entities section
- `docs/spec/supplementary_specs/interface-contracts.md` -- context-lint CLI contract
- `docs/spec/supplementary_specs/state-machines.md` -- mode lifecycle state machine
- `docs/spec/supplementary_specs/validation-rules.md` -- CX-\* validation rules
- `docs/proposals/yaml-charter-lifecycle.md` -- accepted proposal (design origin)
- `docs/arc42/12_glossary.md` -- domain vocabulary

`spec-lint` summary: 0 error(s), 8 warning(s), 27 info across 18 spec file(s). All warnings and info findings are pre-existing (BR-\* reference warnings from earlier specifications, unresolved todo items, and unreferenced BR definitions). No new errors introduced by the agent-context specification.

## Deterministic Findings (Pass 1)

| Finding                                                              | Source                           | Severity | Disposition                                                             |
| -------------------------------------------------------------------- | -------------------------------- | -------- | ----------------------------------------------------------------------- |
| TRACE002: 8 BR-\* references not defined in a Business Rules section | Pre-existing spec files          | warning  | Dismissed -- pre-existing, not agent-context-related                    |
| TODO001: 8 unresolved todo items                                     | `docs/spec/todos.md`             | info     | Dismissed -- pre-existing                                               |
| TRACE003: 19 BR-\* definitions unreferenced                          | Pre-existing validation-rules.md | info     | Dismissed -- pre-existing, referenced within prose not cross-ref format |
| TRACE004: EPIC_BUILDING_BLOCK has no attribute block                 | Pre-existing entity-model.md     | info     | Dismissed -- pre-existing test-design entity                            |

No deterministic findings attributable to the agent-context specification.

## Semantic Findings (Pass 2)

| ID                                    | Finding                                                                                                                                             | Artifact                                            | Characteristic | Category   | Severity |
| ------------------------------------- | --------------------------------------------------------------------------------------------------------------------------------------------------- | --------------------------------------------------- | -------------- | ---------- | -------- |
| [SPEC-0012](../findings/SPEC-0012.md) | .feature @ references use pre-rename paths (capture-charter, update-charter, charter-lint instead of capture-context, update-context, context-lint) | `docs/spec/agent-context.feature`                   | Consistent     | Defect     | Major    |
| [SPEC-0013](../findings/SPEC-0013.md) | CX-MODE severity (info) contradicts field-level rule that mode must be primary or index -- invalid mode values pass unchecked                       | `docs/spec/supplementary_specs/validation-rules.md` | Consistent     | Defect     | Major    |
| S-01                                  | Term "concern" (reading-guide routing axis) is undefined in the glossary                                                                            | `docs/arc42/12_glossary.md`                         | Terminology    | Suggestion | Minor    |
| S-02                                  | "Path updates completed across all factory consumers" scenario uses universal quantifier -- verifiable only by grep, not a unit test runner         | `docs/spec/agent-context.feature`                   | Verifiable     | Suggestion | Minor    |
| S-03                                  | Gaps report correctly identifies two ambiguous wordings; suggested fixes are adequate                                                               | `docs/spec/agent-context-gaps.md`                   | Unambiguous    | Suggestion | Minor    |

## Traceability Summary

### Proposal Completion Criteria to Scenarios

All nine completion criteria from the proposal trace to at least one scenario:

| Completion Criterion                                                         | Covering Scenario(s)                                                                                                                      |
| ---------------------------------------------------------------------------- | ----------------------------------------------------------------------------------------------------------------------------------------- |
| Four YAML files as documented, tested, lint-validated interface              | Multiple CX-\* scenarios, "Agent reads all four context files"                                                                            |
| `capture-context --init` creates three index-file templates                  | "capture-context --init creates three index-file templates"                                                                               |
| `capture-context --init --scan` runs concern-based brownfield onboarding     | "capture-context --init --scan discovers documentation signals", "Concern-based interview populates indexes and reading guide"            |
| `update-context` writes fields, manages source pointers, triggers transition | "update-context writes inline values", "update-context writes name and source together", "update-context proposes reading-guide creation" |
| `context-lint` validates with CX-\* codes                                    | 16 CX-\* validation scenarios                                                                                                             |
| `agent-context-composition.md` convention and rules.md entries               | "agent-context-composition.md convention exists", "rules.md carries MUST entries"                                                         |
| All factory consumers have updated paths                                     | "Path updates completed across all factory consumers"                                                                                     |
| Legacy markdown charter backward compatibility                               | 4 legacy compatibility scenarios                                                                                                          |
| testing.yaml excluded from two-mode lifecycle                                | 4 testing.yaml carve-out scenarios                                                                                                        |

### Scope Map to .feature Rules

All 10 scope-map rows with status "specified" trace to a corresponding Rule in `agent-context.feature`. Rule text matches exactly except for the "(subfunction)" annotation on the format-detection row, which follows the existing scope-map convention for subfunctions.

### Deferred Items

All five deferred items from the proposal scope section are correctly excluded from the .feature file and documented in the gaps report.

### State Machine Consistency

The mode lifecycle state machine in `state-machines.md` is consistent between pseudocode and derived Mermaid. Every `ChangeState(X)` in pseudocode corresponds to a Mermaid edge, and vice versa. The state machine covers all transitions described in the .feature scenarios for mode initialization and transition.

### CX-\* Validation Codes

All 10 CX-\* codes are consistently defined across four artifacts: the proposal, validation-rules.md, interface-contracts.md, and the .feature scenarios. Severities and conditions match across all four sources, with the exception of SPEC-0013 (CX-MODE).

### Entity Model Coverage

The entity model's Agent Context Entities section covers all entities referenced in .feature scenarios: READING_GUIDE, CONCERN_ENTRY, KEY_PATH_REFERENCE, INDEX_FILE, INDEX_FIELD, MODE_STATE, DEFERRED_MARKER, SOURCE_POINTER, TESTING_YAML, FORMAT_DETECTION, and CX_FINDING.

### QA Strategy

The QA strategy maps 24 contract-owner entries to specific scenarios and test locations. All CX-\* codes have assigned test IDs and planned test files. The boundary cases table identifies 11 edge cases with owner-layer assignments. The gap findings section correctly identifies 5 items at info/low severity.

## Orphans and Gaps

- No orphan scenarios (every scenario belongs to a Rule with a scope-map row).
- No orphan Rules (every Rule has at least one scenario).
- Two gaps identified in the gaps report (invalid CX-MODE scenario, equal-mtime CX-SRC-STALE behavior) -- the CX-MODE gap is elevated to Major via SPEC-0013.
