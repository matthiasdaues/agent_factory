# Gaps Report: agent-context

Generated: 2026-09-03
Source: docs/proposals/yaml-charter-lifecycle.md

## Actor-Goal Matrix

| Actor              | Goal                                                   | Rule                                                                        | Status    |
| ------------------ | ------------------------------------------------------ | --------------------------------------------------------------------------- | --------- |
| Factory Agent      | Read project context through unified two-layer routing | Rule: Factory agent reads project context through unified two-layer routing | specified |
| Human Operator     | Initialize agent context for a greenfield project      | Rule: Operator initializes agent context for a greenfield project           | specified |
| Human Operator     | Onboard brownfield documentation into agent context    | Rule: Operator onboards brownfield documentation into agent context         | specified |
| Human Operator     | Update agent context as decisions emerge               | Rule: Operator updates agent context as decisions emerge                    | specified |
| Human Operator     | Transition context from primary to index mode          | Rule: Operator transitions context from primary to index mode               | specified |
| context-lint       | Validate agent context structure and references        | Rule: context-lint validates agent context structure and references         | specified |
| Human Operator     | Continue using a legacy project without migration      | Rule: Legacy projects continue working without migration                    | specified |
| detect-test-regime | Write testing.yaml independently of lifecycle          | Rule: testing.yaml operates as a lifecycle-exempt peer file                 | specified |
| Factory Consumer   | Resolve context file paths via format detection        | Rule: Factory consumers resolve context file paths via format detection     | specified |
| Factory governance | Codify agent context composition rules                 | Rule: Convention codifies agent context composition rules                   | specified |

## Missing Rules

None. Every actor-goal pair in the matrix has a corresponding Rule.

## Rules Without Scenarios

None. Every Rule has at least one Scenario.

## Ambiguous Wording

| Location                                                                                    | Step Text                                                               | Issue                                                                              | Suggested Fix                                                                                                                                                                |
| ------------------------------------------------------------------------------------------- | ----------------------------------------------------------------------- | ---------------------------------------------------------------------------------- | ---------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| Rule: Operator onboards brownfield documentation, Scenario: Concern-based interview         | "When the concern interview completes for backend and testing concerns" | The set of concerns is open-ended; unclear which concerns are mandatory            | Clarify: "When the concern interview completes for each applicable concern discovered during the scan"                                                                       |
| Rule: Convention codifies agent context composition rules, Scenario: Path updates completed | "no hardcoded docs/charter/ path remains in active factory code"        | "active factory code" is ambiguous — retained legacy templates are not active code | Clarify: "no hardcoded docs/charter/ path remains in factory agents, skills, playbooks, scripts, or hooks (legacy templates retained for backward compatibility are exempt)" |

## Grilling-Resolved Design Decisions

The following design decisions were resolved during the grill-with-docs interview and are recorded here for traceability:

1. **testing.yaml location resolution**: Format detection for testing.yaml walks both `docs/agent-context/testing.yaml` and `docs/charter/testing.yaml` independently. No CX-FORMAT error for a testing.yaml at the old path when index files are at the new path.

2. **capture-context backward compatibility**: `capture-context` operates on whatever format it detects (markdown or YAML). The `--init --scan` variant offers migration as an optional step but never forces it.

3. **deferred field semantics**: `deferred: "reason"` replaces the entire field value. Coexistence of `deferred` with `name`/`source` keys is a CX-KEYS error.

4. **update-context write scope in index mode**: `update-context` writes both `name` and `source` together. A stale name with a correct source is not permitted.

5. **CX-GUIDE-REF validation scope**: Checks key-path existence only. Whether the value is null, deferred, or missing a source pointer is owned by CX-NULL, CX-SRC, and CX-MODE respectively.

## Spec Divergences from Proposal

The following intentional divergences from the accepted proposal are recorded here. The proposal is frozen and not edited.

1. **CX-MODE-INVALID added (SPEC-0013)**: The proposal defines `CX-MODE` as a single info-severity code covering all mode-field reporting. The spec splits this into `CX-MODE` (info, valid values) and `CX-MODE-INVALID` (error, unrecognized values). Rationale: an invalid mode value like `staging` governs the entire lifecycle; blocking on it prevents silent misconfiguration. See [validation-rules.md](supplementary_specs/validation-rules.md) and [interface-contracts.md](supplementary_specs/interface-contracts.md).

## Deferred Items (from proposal)

The following items are explicitly deferred per the proposal's scope section and are NOT covered by Rules in this feature file:

- Automated migration tool (docs/charter/ to docs/agent-context/ rename + file transform)
- Spec, arc42, and ADR document updates (reconciliation pass after implementation)
- Backlog story path updates (bulk find-replace, separate chore)
- SVG diagram regeneration
- Gigacron pilot migration (done by Gigacron project, not factory)
