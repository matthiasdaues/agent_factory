# Specification Review Final Repeat — Local Usage Processing and Analysis

Date: 2026-09-13

Reviewed commit: `476d0b4770f3695a3d98b485bc3c4b58cf102269`

Disposition: **Fail** — one open Major defect blocks Architecture. One previously filed Minor defect also remains open.

## Reviewed specification

The final repeat review inspected the accepted [Local Usage Processing and Analysis proposal](../proposals/usage-processing-and-storage.md) and the proposal/specification artifacts named by the requirements-remediation handoff:

- [agent-context.feature](../spec/agent-context.feature)
- [local-usage-processing-and-analysis.feature](../spec/local-usage-processing-and-analysis.feature)
- [local-usage-processing-and-analysis-gaps.md](../spec/local-usage-processing-and-analysis-gaps.md)
- [local-usage-processing-and-analysis-qa-strategy.md](../spec/local-usage-processing-and-analysis-qa-strategy.md)
- [prd.md](../spec/prd.md)
- [scope-map.md](../spec/scope-map.md)
- [test-design.feature](../spec/test-design.feature)
- [test-gate-presence.feature](../spec/test-gate-presence.feature)
- [test-design-qa-strategy.md](../spec/test-design-qa-strategy.md)
- [entity-model.md](../spec/supplementary_specs/entity-model.md)
- [interface-contracts.md](../spec/supplementary_specs/interface-contracts.md)
- [validation-rules.md](../spec/supplementary_specs/validation-rules.md)
- [todos.md](../spec/todos.md)

`factory/scripts/spec-lint --spec-dir docs/spec` reported 0 errors, 0 warnings, and 27 information findings across 18 files.

## Deterministic findings

| Finding                                      | Decision                | Reason                                                                 |
| -------------------------------------------- | ----------------------- | ---------------------------------------------------------------------- |
| TODO001: 8 unresolved todo items             | Confirmed, non-blocking | Pre-existing repository state; none is introduced by the remediation.  |
| TRACE003: 25 unused business-rule references | Confirmed, non-blocking | Pre-existing informational trace notices.                              |
| TRACE004: undefined `EPIC_BUILDING_BLOCK`    | Confirmed, non-blocking | Pre-existing entity-model notice outside the local-usage entity model. |

## Prior-finding verification

| Finding                               | Result         | Verification                                                                                                                                                                                                                                                         |
| ------------------------------------- | -------------- | -------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| [SPEC-0015](../findings/SPEC-0015.md) | Resolved       | The obsolete live `charter-lint` contract is absent. Live contracts consistently use `docs/agent-context.md` for concern routing and `docs/testing.yaml` for machine-consumed test configuration; no live contract requires `docs/charter/`.                         |
| [SPEC-0016](../findings/SPEC-0016.md) | Still resolved | The exact four-value CLI registry, logical-run key, normalized source identity, and deterministic latest-snapshot tuple remain consistent.                                                                                                                           |
| [SPEC-0017](../findings/SPEC-0017.md) | Still resolved | The six query-model-v1 schemas and their dimension request interface remain complete and testable under LU-07.                                                                                                                                                       |
| [SPEC-0018](../findings/SPEC-0018.md) | Still resolved | LU-12 remains the sole executable owner of the UI documentation and six-view bootstrap contract.                                                                                                                                                                     |
| [SPEC-0019](../findings/SPEC-0019.md) | Still resolved | DuckDB and PyArrow remain isolated direct dependencies with compatible lock and offline-cache proof under LU-13.                                                                                                                                                     |
| [SPEC-0020](../findings/SPEC-0020.md) | Resolved       | Parent identity is invariant across evidence for one logical-run key before snapshot selection. Disagreement produces `USAGE_ANCESTRY_PARENT_CONFLICT` for every snapshot and blocks accounting under LU-05.                                                         |
| [SPEC-0021](../findings/SPEC-0021.md) | Remains open   | The entity diagram still permits multiple logical runs per latest snapshot, while the prose requires one latest snapshot per logical-run key. This pre-existing Minor finding was omitted from the handoff but exists at the reviewed commit and on canonical `dev`. |

Verified status changes and the newly filed Major finding are committed canonically on `dev` at `7e88a413264bcc2de5540b02888a217ccabe6eed`.

## Fresh semantic inspection

| Finding                                                                                                                              | Artifact                                                                                            | Category | Severity | Characteristic                   |
| ------------------------------------------------------------------------------------------------------------------------------------ | --------------------------------------------------------------------------------------------------- | -------- | -------- | -------------------------------- |
| [SPEC-0022](https://github.com/matthiasdaues/agent_factory/blob/7e88a413264bcc2de5540b02888a217ccabe6eed/docs/findings/SPEC-0022.md) | [usage-processing-and-storage.md](../proposals/usage-processing-and-storage.md#completion-criteria) | Defect   | Major    | Consistent, complete, verifiable |
| [SPEC-0021](../findings/SPEC-0021.md)                                                                                                | [entity-model.md](../spec/supplementary_specs/entity-model.md#local-usage-analysis-entities)        | Defect   | Minor    | Consistent, terminology          |

[SPEC-0022](https://github.com/matthiasdaues/agent_factory/blob/7e88a413264bcc2de5540b02888a217ccabe6eed/docs/findings/SPEC-0022.md) records that the accepted proposal defines six ancestry failure codes but completion criterion 04 still requires fixture coverage for “all five,” and the operational-preflight gate's required proof omits `USAGE_ANCESTRY_PARENT_CONFLICT`. The feature and QA strategy assign the conflict to LU-05, so the accepted design origin and executable owner disagree on required deterministic coverage.

No Critical finding was identified. The specification remains feasible and contains no unjustified service, remote-storage, dashboard, notebook, pricing, transcript-indexing, or retention scope.

## Traceability summary

The local-usage actor goals remain traced through the feature, scope map, supplementary contracts, QA owners, and gaps report. The SPEC-0015 and SPEC-0020 remedies are consistently traced across their affected artifacts.

Traceability is not clean because the proposal's completion criterion and gate proof omit the new parent-conflict fixture while LU-05 requires it. The open [SPEC-0021](../findings/SPEC-0021.md) diagram defect also remains visible. No undefined business-rule reference was introduced by the remediation.

## Disposition

Fail. Requirements must resolve [SPEC-0022](https://github.com/matthiasdaues/agent_factory/blob/7e88a413264bcc2de5540b02888a217ccabe6eed/docs/findings/SPEC-0022.md). [SPEC-0021](../findings/SPEC-0021.md) remains a non-blocking Minor defect but must be resolved or explicitly accepted before the no-open-findings gate can pass. Architecture must not start.
