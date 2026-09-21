# Specification Review — Local Usage Processing and Analysis

Date: 2026-09-13

Disposition: **Fail** — five Major defects block Architecture.

## Reviewed specification

The review compared the accepted [Local Usage Processing and Analysis proposal](../proposals/implemented/usage-processing-and-storage.md) with:

- [local-usage-processing-and-analysis.feature](../spec/local-usage-processing-and-analysis.feature)
- [local-usage-processing-and-analysis-gaps.md](../spec/local-usage-processing-and-analysis-gaps.md)
- [local-usage-processing-and-analysis-qa-strategy.md](../spec/local-usage-processing-and-analysis-qa-strategy.md)
- [scope-map.md](../spec/scope-map.md)
- [entity-model.md](../spec/supplementary_specs/entity-model.md#local-usage-analysis-entities)
- [interface-contracts.md](../spec/supplementary_specs/interface-contracts.md#local-usage-processing-and-analysis)
- [state-machines.md](../spec/supplementary_specs/state-machines.md#usage-query-lifecycle)
- [validation-rules.md](../spec/supplementary_specs/validation-rules.md#local-usage-processing-and-analysis)

The review also compared the stakeholder-restored [agent-context.feature](../spec/agent-context.feature) with the implemented [Concern-Oriented Agent Context proposal](../proposals/factory-concern-oriented-agent-context.md) and the current [concern-lint interface contract](../spec/supplementary_specs/interface-contracts.md#agent-factoryfactoryscriptsconcern-lint).

`.agent-factory/factory/scripts/spec-lint --spec-dir docs/spec` reported 0 errors, 0 warnings, and 27 information findings across 18 files.

## Deterministic findings

| Finding                                                  | Artifact                                                               | Decision                | Reason                                                                         |
| -------------------------------------------------------- | ---------------------------------------------------------------------- | ----------------------- | ------------------------------------------------------------------------------ |
| TODO001: 8 unresolved todo items                         | [todos.md](../spec/todos.md)                                           | Confirmed, non-blocking | Pre-existing repository state; none is introduced by this feature.             |
| TRACE003: BR-008 unused                                  | [validation-rules.md](../spec/supplementary_specs/validation-rules.md) | Confirmed, non-blocking | Pre-existing informational trace notice.                                       |
| TRACE003: BR-009 unused                                  | [validation-rules.md](../spec/supplementary_specs/validation-rules.md) | Confirmed, non-blocking | Pre-existing informational trace notice.                                       |
| TRACE003: BR-010 unused                                  | [validation-rules.md](../spec/supplementary_specs/validation-rules.md) | Confirmed, non-blocking | Pre-existing informational trace notice.                                       |
| TRACE003: BR-011 unused                                  | [validation-rules.md](../spec/supplementary_specs/validation-rules.md) | Confirmed, non-blocking | Pre-existing informational trace notice.                                       |
| TRACE003: BR-012 unused                                  | [validation-rules.md](../spec/supplementary_specs/validation-rules.md) | Confirmed, non-blocking | Pre-existing informational trace notice.                                       |
| TRACE003: BR-015 unused                                  | [validation-rules.md](../spec/supplementary_specs/validation-rules.md) | Confirmed, non-blocking | Pre-existing informational trace notice.                                       |
| TRACE003: BR-016 unused                                  | [validation-rules.md](../spec/supplementary_specs/validation-rules.md) | Confirmed, non-blocking | Pre-existing informational trace notice.                                       |
| TRACE003: BR-028 unused                                  | [validation-rules.md](../spec/supplementary_specs/validation-rules.md) | Confirmed, non-blocking | Pre-existing informational trace notice.                                       |
| TRACE003: BR-036 unused                                  | [validation-rules.md](../spec/supplementary_specs/validation-rules.md) | Confirmed, non-blocking | Pre-existing informational trace notice.                                       |
| TRACE003: BR-037 unused                                  | [validation-rules.md](../spec/supplementary_specs/validation-rules.md) | Confirmed, non-blocking | Pre-existing informational trace notice.                                       |
| TRACE003: BR-038 unused                                  | [validation-rules.md](../spec/supplementary_specs/validation-rules.md) | Confirmed, non-blocking | Pre-existing informational trace notice.                                       |
| TRACE003: BR-039 unused                                  | [validation-rules.md](../spec/supplementary_specs/validation-rules.md) | Confirmed, non-blocking | Pre-existing informational trace notice.                                       |
| TRACE003: BR-041 unused                                  | [validation-rules.md](../spec/supplementary_specs/validation-rules.md) | Confirmed, non-blocking | Pre-existing informational trace notice.                                       |
| TRACE003: BR-043 unused                                  | [validation-rules.md](../spec/supplementary_specs/validation-rules.md) | Confirmed, non-blocking | Pre-existing informational trace notice.                                       |
| TRACE003: BR-044 unused                                  | [validation-rules.md](../spec/supplementary_specs/validation-rules.md) | Confirmed, non-blocking | Pre-existing informational trace notice.                                       |
| TRACE003: BR-045 unused                                  | [validation-rules.md](../spec/supplementary_specs/validation-rules.md) | Confirmed, non-blocking | Pre-existing informational trace notice.                                       |
| TRACE003: BR-046 unused                                  | [validation-rules.md](../spec/supplementary_specs/validation-rules.md) | Confirmed, non-blocking | Pre-existing informational trace notice.                                       |
| TRACE003: BR-047 unused                                  | [validation-rules.md](../spec/supplementary_specs/validation-rules.md) | Confirmed, non-blocking | Pre-existing informational trace notice.                                       |
| TRACE003: BR-048 unused                                  | [validation-rules.md](../spec/supplementary_specs/validation-rules.md) | Confirmed, non-blocking | Pre-existing informational trace notice.                                       |
| TRACE003: BR-050 unused                                  | [validation-rules.md](../spec/supplementary_specs/validation-rules.md) | Confirmed, non-blocking | Pre-existing informational trace notice.                                       |
| TRACE003: BR-051 unused                                  | [validation-rules.md](../spec/supplementary_specs/validation-rules.md) | Confirmed, non-blocking | Pre-existing informational trace notice.                                       |
| TRACE003: BR-052 unused                                  | [validation-rules.md](../spec/supplementary_specs/validation-rules.md) | Confirmed, non-blocking | Pre-existing informational trace notice.                                       |
| TRACE003: BR-053 unused                                  | [validation-rules.md](../spec/supplementary_specs/validation-rules.md) | Confirmed, non-blocking | Pre-existing informational trace notice.                                       |
| TRACE003: BR-054 unused                                  | [validation-rules.md](../spec/supplementary_specs/validation-rules.md) | Confirmed, non-blocking | Pre-existing informational trace notice.                                       |
| TRACE003: BR-055 unused                                  | [validation-rules.md](../spec/supplementary_specs/validation-rules.md) | Confirmed, non-blocking | Pre-existing informational trace notice.                                       |
| TRACE004: `EPIC_BUILDING_BLOCK` lacks an attribute block | [entity-model.md](../spec/supplementary_specs/entity-model.md)         | Confirmed, non-blocking | Pre-existing informational model notice outside this feature's added entities. |

## Semantic findings

| Finding                                                                                                                                                                                                                              | Artifact                                                                                                                                                                                                                                                                | Category | Severity | Characteristic                     |
| ------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------ | ----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- | -------- | -------- | ---------------------------------- |
| [SPEC-0015](../findings/SPEC-0015.md): the restored feature revives the superseded YAML agent-context model; retire it or rewrite and retrace it to the implemented concern-oriented contract.                                       | [agent-context.feature](../spec/agent-context.feature) and [scope-map.md](../spec/scope-map.md)                                                                                                                                                                         | Defect   | Major    | Consistent, necessary, terminology |
| [SPEC-0016](../findings/SPEC-0016.md): canonical accounting leaves logical-run identity and the source-position comparison order undefined; define both precisely.                                                                   | [local-usage-processing-and-analysis.feature](../spec/local-usage-processing-and-analysis.feature)                                                                                                                                                                      | Defect   | Major    | Unambiguous, verifiable, complete  |
| [SPEC-0017](../findings/SPEC-0017.md): the query contract names six views but does not declare their schemas or dimensional-grouping request semantics; add the observable columns, types, keys, null rules, and grouping interface. | [interface-contracts.md](../spec/supplementary_specs/interface-contracts.md#usage-query)                                                                                                                                                                                | Defect   | Major    | Verifiable, complete, unambiguous  |
| [SPEC-0018](../findings/SPEC-0018.md): the QA owner table has no contract ID or executable owner for the DuckDB UI rule; assign one or narrow the rule to a verifiable documentation contract.                                       | [local-usage-processing-and-analysis-qa-strategy.md](../spec/local-usage-processing-and-analysis-qa-strategy.md#contract-owners)                                                                                                                                        | Defect   | Major    | Complete, verifiable, consistent   |
| [SPEC-0019](../findings/SPEC-0019.md): PyArrow required, but dependency contract permits only DuckDB and its transitive closure; add and lock PyArrow or remove the required PyArrow result.                                         | [Local Python and dataframe interface](../proposals/implemented/usage-processing-and-storage.md#local-python-and-dataframe-interface) and [Installed runtime and invocation](../proposals/implemented/usage-processing-and-storage.md#installed-runtime-and-invocation) | Defect   | Major    | Feasible, consistent               |

No Critical or Minor semantic finding was identified. The local-usage scope contains no unjustified service, remote-storage, dashboard, notebook, price, transcript-indexing, or retention behavior.

## Traceability summary

The local-usage feature maps all nine accepted actor goals to one Rule each. Its scope-map additions repeat those nine Rules with `specified` status, and the proposal's 20 completion criteria have corresponding behavioral or supplementary statements. No local-usage Rule is orphaned.

Traceability is not clean overall. The restored [agent-context.feature](../spec/agent-context.feature) adds ten `specified` scope-map rows for behavior that the implemented [Concern-Oriented Agent Context proposal](../proposals/factory-concern-oriented-agent-context.md) superseded. Those rows are misleading rather than missing. The local-usage gaps report also states that no wording is ambiguous, but [SPEC-0016](../findings/SPEC-0016.md) and [SPEC-0017](../findings/SPEC-0017.md) identify unresolved accounting and query-contract ambiguity.

The deterministic BR cross-reference notices are pre-existing and informational. None of the local-usage additions introduces an undefined BR reference.

## Disposition

Fail. Requirements must resolve [SPEC-0015](../findings/SPEC-0015.md) through [SPEC-0019](../findings/SPEC-0019.md), then request a full repeat specification review. Architecture must not start.
