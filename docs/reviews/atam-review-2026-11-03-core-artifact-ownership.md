---
type: atam-review
title: ATAM review of the core artifact ownership architecture
date: 2026-11-03
status: defects
reviewer: architecture-review-agent
findings_filed: 3
story: core-artifact-ownership
scope: Commit c3ed5dda9ec3a946696c2dae948a2126f0f4def2 on dev — ADR-0027, ADR-0028, ADR-0029, the ADR-0012 amendment, architecture.dsl, and arc42 sections 5.10, 6.11, 6.12, 8.3, 8.7, 8.17, chapter 9, QS-16, and QS-17 — checked against core-artifact-ownership.feature, BR-056 to BR-066, interface-contracts.md, and the dispatch script at HEAD
---

# ATAM review of the core artifact ownership architecture

The ownership checks of QS-16 hold. The wave close of QS-17 does not yet hold, for three reasons:

- A failing `close-wave` does not stop the next wave, because `prepare-wave` never reads the closeout (ATAM-0007, High).
- `close-wave` has no defined result for an unreadable report or a missing core list, so a silent pass fits the text (ATAM-0008, Medium).
- The owner and reviewer sessions after a merge have no defined branch and no order, so two sessions can edit one core file at once (ATAM-0009, Medium).

Each fix stays inside the architecture and the specification and reopens no decision. Next, the Architecture Agent addresses the three open findings. ADRs 0027 and 0028 can be accepted as they stand. ADR-0029 should wait for the fixes of ATAM-0007 to ATAM-0009.

## Reviewed architecture

- ADR-0027, ADR-0028, and ADR-0029, all `proposed`, and the amendment note on ADR-0012.
- `docs/spec/architecture.dsl`: the Factory Agents container, the containers Core Artifacts, Working Output, and Core List, the components `dispatch`, `index-lint`, `Ownership Contract Test`, and `dependency-check`, and the views `AgentOwnershipComponents`, `SpecificationHandoff`, and `SpecFeedbackWaveClose`.
- Sections 5.1, 5.2.3, 5.4, 5.5, 5.10, 6.4.2, 6.11, 6.12, 8.3, 8.7, 8.17, chapter 9, QS-16, and QS-17.
- Reference material: `docs/spec/features/core-artifact-ownership.feature`, BR-056 to BR-066 in `docs/spec/validation-rules.md`, `docs/spec/interface-contracts.md`, `docs/spec/work/core-artifact-ownership-gaps.md`, `dispatch-contract.md`, and `packages/factory/scripts/dispatch` at HEAD.

`.agent-factory/factory/scripts/arch-lint --docs-dir docs/arc42` found 0 errors, 1 warning, and 0 info, and exited 0. `.agent-factory/factory/scripts/structurizr validate` exited 0.

## Deterministic findings

| Finding                                                             | Disposition                                                                            |
| ------------------------------------------------------------------- | -------------------------------------------------------------------------------------- |
| `ARCH-PARSE` warning: could not extract ports from DSL or chapter 5 | Dismissed. The warning exists before this change, and `c3ed5dda` adds no network port. |

## Prior findings

This is the first ATAM pass on this feature. ATAM-0001 to ATAM-0006 belong to other features and are all `resolved`.

## Quality scenarios

1. **QS-16 (maintainability, artifact ownership):** A change to an agent definition that breaks a producer or a review fails before it merges.
2. **QS-17 (maintainability, specification currency):** The specification lags the code by one wave at most.
3. **QS-1 (flexibility, precondition routing), touched:** `run-step` routes the two new agents by the existence of their input files.
4. **QS-6 (safety, deterministic validation), touched:** The mutation gate now runs the project's command.

## Findings

### QS-16: Every core artifact has a known producer and review

- **Approach:** One core list in the factory names every core and seam artifact with a sample path. The ownership contract test counts producing output patterns per sample path and checks `reviewed_by:`. `index-lint --check` checks each reviewer's name and inputs.
- **Sensitivity points:** The check is only as complete as the core list. A new core file without an entry has no check, as ADR-0028 states. The sample path is a second sensitivity point. A producer pattern narrower than the family still matches a well-chosen sample, so `schemas/*.json` passes against `schemas/example.json` while `.yaml` schemas have no producer.
- **Tradeoff points:** Sample-path matching keeps both checks simple and in agreement (CAO-G05, CAO-G06). It gives up a full pattern-overlap test. `edits: wording` keeps the lector agent's wide pattern and exempts it from the count, so a lector change of meaning goes unchecked.
- **Risks and non-risks:** Non-risk: the test and `index-lint --check` both run before a merge, and the two together cover all four stimuli of QS-16. Low risk: the narrow-pattern case above. The sample paths in `interface-contracts.md` decide it, so no finding is filed.

### QS-17: The specification lags the code by one wave at most

- **Approach:** The developer agent writes drift rows into a per-story report. After each merge the implementation agent dispatches the row's owner and then the reviewer. `dispatch close-wave` fails while a core or seam row is `open` or `fixed`.
- **Sensitivity points:** The scenario depends on three things the architecture leaves out. First, the next wave must wait for `close-wave`, and `prepare-wave` checks only story states ([ATAM-0007](../findings/ATAM-0007.md)). Second, `close-wave` must fail when it cannot read a report or the core list ([ATAM-0008](../findings/ATAM-0008.md)). Third, the owner sessions must not write one core file at the same time ([ATAM-0009](../findings/ATAM-0009.md)).
- **Tradeoff points:** A row whose reviewer is the stakeholder, such as one on `scope-map.md` or `testing.yaml`, keeps the wave open until a human session confirms it. That trades unattended throughput for human authority (DEC-28, DEC-34). Rows on QA strategies and ADRs close at `fixed`, so they get no review (DEC-35).
- **Risks and non-risks:** High risk: ATAM-0007. Medium risks: ATAM-0008 and ATAM-0009. Non-risk: per-story reports remove concurrent writers among developer agents (DEC-27). Non-risk: a drift the developer agent does not notice is outside the scenario, and the reconciliation report covers it later.

### QS-1: The declared inputs set the order of the producers

- **Approach:** `run-step` counts an agent as eligible when the files of its required inputs exist. The handoff text names the next producer.
- **Sensitivity points:** The architecture agent can run before the entity model exists, and only the domain-modeling agent's handoff starts its component pass again. An operator who skips the handoff leaves the architecture unchecked against the domain structure.
- **Tradeoff points:** Eligibility stays file-based and simple (DEC-21). The price is two orderings that no gate enforces: the architecture re-run, and a QA strategy written before the spec review changes a contract.
- **Risks and non-risks:** Low risk. ADR-0027 and section 6.11 state both cases, and the feature file has scenarios for them. No finding is filed.

### QS-6: The mutation gate runs the project's command

- **Approach:** The test-strategy agent sets `gates.mutation_testing` in `testing.yaml`. The implementation agent runs the command as a gate.
- **Sensitivity points:** The project's command must exit non-zero on surviving mutants. Factory reads only the exit code (BR-027).
- **Tradeoff points:** The fail-closed default never runs mutation testing, because only the `gates` section holds the command (BR-066). That keeps the default safe and leaves mutation testing off until someone sets it.
- **Risks and non-risks:** Non-risk: an enabled gate without a command fails and names its owner.

### YAGNI pass

No artificial complexity found. The Core List and Working Output containers each have readers that need them. The Factory Agents container is the one place the ownership rules live.

### Minor observations (not filed)

- The `GateLoop` relationship in `architecture.dsl` (line 418) and the `dependency-check` row in section 5.2 still say "architecture.dsl" instead of `dependency-rules.dsl`.
- The DSL models only the domain-modeling agent as a dispatched owner and the spec-review agent as a dispatched reviewer. The requirements, architecture, and test-strategy agents as owners, and the architecture-review agent as reviewer, have no `implementationAgent` relationship.
- `glossary.md` names two reviewers. BR-061 does not say whether `confirmed` needs both. The term-candidate flow already requires the stakeholder, so the spec-review agent's confirmation is enough for a row.

## Risk summary

| ID        | Risk                                                                    | Severity | Blocks planning | Mitigation                                                                                   |
| --------- | ----------------------------------------------------------------------- | -------- | --------------- | -------------------------------------------------------------------------------------------- |
| ATAM-0007 | `prepare-wave N+1` runs although `close-wave N` failed                  | High     | Yes             | `prepare-wave` and `prepare-story` fail until wave N has a closeout record                   |
| ATAM-0008 | An unreadable report or core list lets `close-wave` pass                | Medium   | Yes             | `close-wave` fails on a wrong header, an unknown status, or a missing list; name the path    |
| ATAM-0009 | Two owner sessions edit one core file at once, or commit on stale bases | Medium   | Yes             | Owner and reviewer sessions run one at a time on the invocation branch before the next merge |
| —         | A narrow producer pattern passes against a well-chosen sample path      | Low      | No              | Choose sample paths that cover each format the family allows                                 |
| —         | The architecture re-run and the QA strategy revision depend on handoffs | Low      | No              | Accepted by DEC-21                                                                           |

## Tradeoff summary

| Tradeoff                                                   | Gains                                        | Gives up                                         |
| ---------------------------------------------------------- | -------------------------------------------- | ------------------------------------------------ |
| Sample-path matching instead of pattern overlap (CAO-G05)  | Two simple checks that agree                 | Detection of a producer narrower than its family |
| `edits: wording` exempts the lector agent (DEC-32)         | The lector keeps its whole job               | A check that the lector changes no meaning       |
| Stakeholder rows block the wave close (DEC-28, DEC-34)     | Human authority over scope and test practice | Unattended wave closes                           |
| Rows on artifacts without review close at `fixed` (DEC-35) | Waves can close                              | A review of QA strategy and ADR fixes            |
| File-based eligibility (DEC-21)                            | Simple, observable routing                   | Enforced order of re-runs after a change         |
| Mutation testing off by default (BR-066)                   | A safe default without a command             | Mutation coverage until the project sets it      |
