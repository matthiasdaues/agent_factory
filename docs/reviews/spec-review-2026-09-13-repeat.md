# Specification Review Repeat — Local Usage Processing and Analysis

Date: 2026-09-13

Reviewed commit: `47dc7920fdd31eca12f9f3bd54ec0435d3c26598`

Disposition: **Fail** — three open Major defects block Architecture.

## Reviewed specification

The repeat review verified the remediation against the accepted [Local Usage Processing and Analysis proposal](../proposals/usage-processing-and-storage.md), the implemented [Concern-Oriented Agent Context proposal](../proposals/factory-concern-oriented-agent-context.md), and the complete changed specification set:

- [agent-context.feature](../spec/agent-context.feature)
- [local-usage-processing-and-analysis.feature](../spec/local-usage-processing-and-analysis.feature)
- [local-usage-processing-and-analysis-gaps.md](../spec/local-usage-processing-and-analysis-gaps.md)
- [local-usage-processing-and-analysis-qa-strategy.md](../spec/local-usage-processing-and-analysis-qa-strategy.md)
- [scope-map.md](../spec/scope-map.md)
- [entity-model.md](../spec/supplementary_specs/entity-model.md#local-usage-analysis-entities)
- [interface-contracts.md](../spec/supplementary_specs/interface-contracts.md#local-usage-processing-and-analysis)
- [state-machines.md](../spec/supplementary_specs/state-machines.md#usage-query-lifecycle)
- [validation-rules.md](../spec/supplementary_specs/validation-rules.md#local-usage-processing-and-analysis)

The fresh semantic pass also inspected the other live feature, PRD, test-design, test-gate, interface, entity, and validation contracts where they intersect the concern-oriented test-configuration migration.

`factory/scripts/spec-lint --spec-dir docs/spec` reported 0 errors, 0 warnings, and 27 information findings across 18 files.

## Deterministic findings

| Finding                                      | Decision                | Reason                                                                 |
| -------------------------------------------- | ----------------------- | ---------------------------------------------------------------------- |
| TODO001: 8 unresolved todo items             | Confirmed, non-blocking | Pre-existing repository state; none is introduced by this remediation. |
| TRACE003: 25 unused business-rule references | Confirmed, non-blocking | Pre-existing informational trace notices.                              |
| TRACE004: undefined `EPIC_BUILDING_BLOCK`    | Confirmed, non-blocking | Pre-existing entity-model notice outside the reviewed feature.         |

## Prior-finding verification

| Finding                               | Result   | Verification                                                                                                                                                                                                                                                                                                                       |
| ------------------------------------- | -------- | ---------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| [SPEC-0015](../findings/SPEC-0015.md) | Open     | The feature now specifies the concern model, but the PRD, test-design and test-gate feature files, scope map, entity model, interface contracts, and validation rules still require `docs/charter/testing.yaml`. That contradicts the new single `docs/testing.yaml` contract and the rule that `docs/charter/` is legacy residue. |
| [SPEC-0016](../findings/SPEC-0016.md) | Open     | The key and source-position tuple are now defined, but `usage-capture` emits `claude-code` while the accounting registry contract names `claude`. Since `cli` is part of logical-run identity and unknown registry values fail, the canonical Claude Code identifier remains contradictory.                                        |
| [SPEC-0017](../findings/SPEC-0017.md) | Resolved | Six versioned schemas now define columns, DuckDB types, keys, nullability, empty results, and stable ordering. The CLI and Python dimension interfaces define supported ordered dimensions, time granularities, defaults, invalid requests, and UTC bucket semantics; LU-07 owns verification.                                     |
| [SPEC-0018](../findings/SPEC-0018.md) | Resolved | The feature narrows automation to a documentation/bootstrap contract. LU-12 assigns `usage-ui-doc-check` as the sole executable owner without launching or fetching the UI or duplicating accounting assertions.                                                                                                                   |
| [SPEC-0019](../findings/SPEC-0019.md) | Resolved | The proposal and specification now require isolated direct DuckDB and PyArrow dependencies, a compatible locked transitive closure, `pyarrow.Table` output, and LU-13 proof of lock compatibility and network-disabled operation from a complete cache.                                                                            |

Statuses and evidence are committed canonically on `dev` at `edf2303bb457941f1e20c16208b8c27b1e9b1a72` and `b963b7b2bd924f8cf6ff60636b29752f89a472ff`.

## Fresh semantic inspection

| Finding                                                                                                                              | Artifact                                                                                                              | Category | Severity | Characteristic                    |
| ------------------------------------------------------------------------------------------------------------------------------------ | --------------------------------------------------------------------------------------------------------------------- | -------- | -------- | --------------------------------- |
| [SPEC-0015](../findings/SPEC-0015.md)                                                                                                | [agent-context.feature](../spec/agent-context.feature) and the intersecting live test-configuration contracts         | Defect   | Major    | Consistent, complete, terminology |
| [SPEC-0016](../findings/SPEC-0016.md)                                                                                                | [interface-contracts.md](../spec/supplementary_specs/interface-contracts.md#logical-run-and-source-position-contract) | Defect   | Major    | Consistent, unambiguous           |
| [SPEC-0020](https://github.com/matthiasdaues/agent_factory/blob/edf2303bb457941f1e20c16208b8c27b1e9b1a72/docs/findings/SPEC-0020.md) | [interface-contracts.md](../spec/supplementary_specs/interface-contracts.md#logical-run-and-source-position-contract) | Defect   | Major    | Complete, unambiguous, verifiable |

[SPEC-0020](https://github.com/matthiasdaues/agent_factory/blob/edf2303bb457941f1e20c16208b8c27b1e9b1a72/docs/findings/SPEC-0020.md) records that `parent_run_id` is said to define ancestry without defining root identity or rejecting missing parents, cross-session or cross-CLI parents, self-links, cycles, and multiple roots. Those cases can change Claude Code, Pi, Codex, and Copilot totals while passing the declared record contract.

No Critical or Minor finding was identified. The local-usage scope contains no unjustified service, remote-storage, dashboard, notebook, price, transcript-indexing, or retention behavior.

## Traceability summary

All nine local-usage actor goals still map to one feature Rule and one `specified` scope-map row. The six-view schemas, dimension interface, UI smoke owner, and dependency owner now trace through the feature, supplementary contracts, QA table, and gaps report.

Traceability is not clean overall. The concern-oriented feature declares `docs/testing.yaml` as the sole test-configuration path while other live specifications still trace implemented behavior to `docs/charter/testing.yaml`. The local-usage gaps report also claims no ambiguity even though the Claude Code registry value and ancestry validity remain unresolved. No new undefined business-rule reference was introduced.

## Disposition

Fail. Requirements must resolve [SPEC-0015](../findings/SPEC-0015.md), [SPEC-0016](../findings/SPEC-0016.md), and [SPEC-0020](https://github.com/matthiasdaues/agent_factory/blob/edf2303bb457941f1e20c16208b8c27b1e9b1a72/docs/findings/SPEC-0020.md), then request another full repeat specification review. Architecture must not start.
