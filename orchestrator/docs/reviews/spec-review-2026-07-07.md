# Specification Review — TUI Menu Mode Addendum

**Date**: 2026-07-07
**Reviewer**: Specification Review Agent (separate session from the author)
**Commit under review**: `1c8bc233298b004b655e718986b4a70e48134062` — "new TUI user interface specified"
**Result**: Not clean — 1 Critical and 5 Major findings filed; the requirements gate currently fails.

## Reviewed specification

The review covered the full `docs/spec/` tree, with attention to the artifacts the commit changed:

- `prd.md` (one-line change) and the new `prd-tui-addendum.md`
- `cli_specification.md` v1.2.0
- `actor-goal-list.md` (TUI addendum goals AG-08 through AG-13)
- `use_cases/UC-08` through `UC-12`, and `use_cases/system-use-cases.md`
- `supplementary_specs/entity-model.md`, `interface-contracts.md`, `state-machines.md`, `validation-rules.md`
- `CONTEXT.md` as the terminology yardstick

`spec-lint --spec-dir docs/spec --graph docs/spec/traceability.json` reported **3 errors, 13 warnings, 22 info** across 22 spec files and exited non-zero. Because `spec-lint` is the requirements phase gate and the gate blocks on error-severity findings, the three errors mean the phase cannot pass in its current state.

## Deterministic findings (Pass 1)

| Code                                                  | Count | Severity | Verdict          | Disposition                                    |
| ----------------------------------------------------- | ----- | -------- | ---------------- | ---------------------------------------------- |
| STRUCT001 — UC missing Postconditions section         | 3     | error    | Confirmed        | Filed as **SPEC-0001** (Critical)              |
| TRACE001 — AG-13 realized by no use case              | 1     | warning  | Confirmed        | Filed as **SPEC-0005** (Major)                 |
| TRACE003 — BR-046…BR-055 defined but never referenced | 10    | info     | Confirmed        | Symptom of **SPEC-0002**; resolved by that fix |
| FMT004 — non-atomic requirement (multiple `shall`)    | 13    | warning  | Partly confirmed | Report finding **m2** (Minor)                  |
| FMT001 — possible non-EARS requirement (heuristic)    | 12    | info     | Dismissed        | False positives (see below)                    |

**FMT001 dismissed.** The flagged lines are valid EARS. "The planning agent shall …", "The agent registry shall …", and similar are well-formed ubiquitous requirements of the form `<entity> shall`; the heuristic simply does not recognize a leading article. "In menu mode, when the Operator selects …" is a valid Where/When construction. None require change.

**FMT004 partly confirmed.** Several requirements genuinely bundle multiple actions under one `shall` (the `release`, `abort`, and adapter-removal requirements), which contradicts the document's own claim that "Each requirement is atomic." Many other flagged lines state a single property in two clauses (for example, "shall be read-only and shall not mutate run state") and are acceptable. Recorded as Minor finding **m2**.

## Semantic findings (Pass 2)

Assessed against the requirements-quality characteristics. Findings are ordered by severity.

| #         | Finding                                                                                                                                                                                                                                                                                                                                                   | Characteristic         | Artifact                                                    | Category   | Severity |
| --------- | --------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- | ---------------------- | ----------------------------------------------------------- | ---------- | -------- |
| SPEC-0001 | UC-10, UC-11, and UC-12 carry no `Postconditions` section (they use `Minimal Guarantees`/`Success Guarantees`), so `spec-lint` errors and the requirements gate fails; the split is also inconsistent with UC-08/09. Add a `## Postconditions` heading grouping the existing guarantees.                                                                  | Consistent, Complete   | UC-10, UC-11, UC-12                                         | Defect     | Critical |
| SPEC-0002 | The business-rule citations in the five TUI sections of `system-use-cases.md` resolve to unrelated rules from earlier use cases (for example, "persist operator defaults … (BR-033)" cites UC-08 menu-state isolation instead of BR-037), and none of UC-11's BR-050…055 or UC-12's BR-056…060 is referenced. Re-map each citation to the governing rule. | Consistent, Verifiable | system-use-cases.md                                         | Defect     | Major    |
| SPEC-0003 | Phase-run model resolution is specified four ways that disagree: design rule 4 (max of tier and classification), the resolution-chain diagram / FR-R12 / system-use-cases (agent tier only), and FR-K2 / VR-023 (classification via the model matrix). Resolve T-34 and unify the statements.                                                             | Consistent, Feasible   | cli_specification.md, prd-tui-addendum, system-use-cases.md | Defect     | Major    |
| SPEC-0004 | The tier-to-model mapping is duplicated in the Model Matrix `[facts]` section and the per-adapter model dictionary, with no statement of which is authoritative. Designate a single source of truth.                                                                                                                                                      | Consistent, Necessary  | interface-contracts.md, entity-model.md                     | Defect     | Major    |
| SPEC-0005 | AG-13 is a User Goal that no use case realizes; the status-view requirements cite `UC-08, AG-13`, but UC-08 realizes AG-08 only. Add `Realizes: AG-13` to UC-08 or extend UC-05.                                                                                                                                                                          | Complete               | actor-goal-list.md, UC-08                                   | Defect     | Major    |
| SPEC-0006 | Model resolution is undefined when an agent declares no tier; `AgentInfo.tier` is nullable and no current agent declares one, yet FR-R11/R12 resolve from "the agent's declared tier." Specify the null-tier fallback.                                                                                                                                    | Complete, Verifiable   | prd-tui-addendum FR-R10…R12, interface-contracts.md         | Defect     | Major    |
| m1        | VR-035 drops BR-042's requirement that a validation probe identify the binary as a supported adapter, and cites only FR-R3 (omitting auto-detect, FR-R2). Align VR-035 with BR-042.                                                                                                                                                                       | Consistent             | validation-rules.md                                         | Defect     | Minor    |
| m2        | Several system requirements bundle multiple actions under one `shall` (release, abort, adapter remove-and-cascade), contradicting the document's atomicity claim. Split the genuinely compound ones.                                                                                                                                                      | Unambiguous            | system-use-cases.md                                         | Suggestion | Minor    |

## Traceability summary

- **Actor-goal coverage.** AG-08 → UC-08, AG-09 → UC-09, AG-10 → UC-10, AG-11 → UC-11, and AG-12 → UC-12 are all realized. **AG-13 is orphaned** (SPEC-0005).
- **Business rules.** BR-030 through BR-060 are all defined exactly once. BR-046 through BR-055 are defined but never referenced by any requirement; this is the visible symptom of the mis-numbered citations in `system-use-cases.md` (SPEC-0002), not a set of genuinely unused rules.
- **Cross-references.** No `TRACE002` (referenced-but-undefined) or `TRACE006` (dangling UC reference) findings. The traceability graph in `docs/spec/traceability.json` was regenerated during this review.

## Disposition

Six findings filed under `docs/findings/` (SPEC-0001 through SPEC-0006): one Critical and five Major, all `status: open`. The two Minor findings remain in this report only.

**Handoff.** Open `SPEC` findings exist. Start a new session and run the Requirements Agent to address SPEC-0001 through SPEC-0006, then re-run this review. SPEC-0001 must clear before the `spec-lint` gate can pass.
