---
id: 0002
status: accepted
evaluation: pugh-matrix
---

# Factory owns flow control; orchestrator is one trigger among peers

## Context

`orchestrator/` used to run its own `PhaseRunner`: an independent state machine that decided which phase a run was in, whether a gate had passed, and when to advance. `factory/scripts/{transition-lint,phase,trigger}` existed, but as helpers `orchestrator/` called internally — a human or a different AI CLI session had no independent way to gate, advance, cap, or dispatch a playbook run without going through the orchestrator process.

That ownership has inverted. `factory/scripts/transition-lint`, `factory/scripts/phase`, `factory/scripts/trigger`, and the `run-step` skill now read and write the marker (`.current-work/playbook-state.yml`) and the playbook's `.fsm.yml` directly. They are deterministic, file-driven, and require no orchestrator process to run. `orchestrator/` still exists, and still calls these same mechanisms — but so does a Human Operator typing commands by hand, on equal footing. Neither owns sequencing or gating anymore; both are triggers of the same underlying mechanism.

This reverses this repo's own prior architecture. Anyone who last touched this code before the inversion would reasonably assume `orchestrator/`'s `PhaseRunner` still decides "what phase are we in" — it is surprising without this context, hard to reverse once `orchestrator/` stops maintaining its own competing phase logic, and the shape below is the result of a real trade-off among genuine alternatives. All three bars the [`write-adr` skill](../../factory/skills/write-adr/SKILL.md) sets for offering an ADR are met.

### Alternatives (Pugh Matrix)

**A**: status quo — `orchestrator/`'s `PhaseRunner` is the sole flow-control owner; `factory/scripts/*` are internal helpers it calls privately. **B**: factory owns flow control via the marker, the FSM, and deterministic gates on disk; `orchestrator/` becomes a peer trigger, the same standing as a human typing commands (what was built). **C**: duplicate — `orchestrator/` keeps its own `PhaseRunner` *and* `factory/` grows independent mechanisms, unreconciled. **D**: full merge — delete `orchestrator/`'s `PhaseRunner` entirely, including its `RUN`/`RUN_LOCK` bookkeeping; `orchestrator/` becomes a pure UI wrapper with no state of its own.

Criteria drawn from the planned `10_quality_requirements.md` quality tree; **Single source of truth** added per this project's Clean Architecture/SOLID evaluation criterion for decisions affecting a system boundary.

| Criterion                                                                                              | Weight | A: status quo | B: factory owns it, orchestrator is a trigger | C: duplicate, unreconciled | D: full merge, orchestrator has no state |
| ------------------------------------------------------------------------------------------------------ | ------ | ------------- | --------------------------------------------- | -------------------------- | ---------------------------------------- |
| CLI-agnosticism (a human or any CLI drives a run with no orchestrator process running)                 | 3      | 0             | +1                                            | -1                         | +1                                       |
| Single source of truth (one owner per concern, SOLID SRP)                                              | 3      | 0             | +1                                            | -2                         | +1                                       |
| Resumability (observable-state resume, never a trusted persisted status)                               | 3      | 0             | +1                                            | -1                         | 0                                        |
| Migration cost / reversibility                                                                         | 2      | 0             | -1                                            | -1                         | -2                                       |
| Preserves each subsystem's legitimate independent concerns (`orchestrator/`'s `RUN_LOCK`, audit trail) | 1      | 0             | +1                                            | 0                          | -1                                       |
| **Weighted total**                                                                                     |        | **0**         | **+8**                                        | **-14**                    | **+1**                                   |

B wins decisively. C is actively worse than the status quo — two independent, unreconciled models of "what phase are we in" is a direct SOLID Single-Responsibility violation, guaranteed to drift. D scores close to A only because deleting `orchestrator/`'s own `RUN`/`RUN_LOCK`/audit-trail bookkeeping — concerns `factory/`'s marker was never meant to absorb (see [PRD § NG1](../spec/prd.md#non-goals)) — both costs more to build and throws away functionality unrelated to flow-control ownership. B pays a real, already-incurred migration cost (building and wiring four mechanisms) but is the only option that is CLI-agnostic, has one clear owner of flow-control state, and leaves `orchestrator/`'s own, separate run-tracking concerns untouched.

## Decision

`factory/scripts/{transition-lint,phase,trigger}` and the `run-step` skill are the flow-control owner: they alone gate which files may be staged in which phase, advance the marker, cap retries, and dispatch agents, from state that lives in files (the marker, the FSM, `INDEX.yaml`) rather than inside any one process.

`orchestrator/` is one possible trigger of these mechanisms — a stand-in for a human manually running `transition-lint`, `phase advance`, `phase retry`, and `trigger` by hand. A Human Operator and the orchestrator CLI are peers: both only invoke `factory/` tooling; neither holds flow-control authority the other lacks.

`orchestrator/` keeps its own `RUN`/`RUN_LOCK` bookkeeping and invocation audit trail — concerns distinct from "what phase are we in," which `factory/` does not duplicate (see [PRD § NG1](../spec/prd.md#non-goals)).

This documentation ([docs/](../README.md)) supersedes the informal prior description in [docs/arc42/concepts.md § The phase chain](../arc42/concepts.md#the-phase-chain) and [factory/docs/factory-guide.md § Playbook phase gates](../../factory/docs/factory-guide.md#playbook-phase-gates) as the rigorous statement of this boundary.

## Consequences

**Positive**

- One clear owner of flow-control state. A human, `orchestrator/`, or a freshly started agent session all read the same marker and FSM and reach the same answer — no process-local state to be out of sync with.
- CLI-agnostic by construction: `greenfield-development.fsm.yml` can be driven end to end with `transition-lint`, `phase advance`/`retry`, and `trigger` alone, with `orchestrator/` never involved (see [PRD § 6 Success Criteria](../spec/prd.md#6-success-criteria)).
- `orchestrator/`'s own legitimate concerns — its `RUN_LOCK` single-active-run invariant, its invocation log — stay intact and untouched; this decision narrows what `orchestrator/` owns, it does not gut it.

**Negative / risks**

- The boundary is a documented convention, not a compiled one. Nothing in code stops a future change from quietly re-introducing a second, competing notion of "current phase" inside `orchestrator/` — a risk to record in the planned `11_risks_and_technical_debt.md` chapter.
- Two files now describe "state of a run," from different angles: the marker (`factory/`'s phase-and-gate state) and `orchestrator/`'s own `run.json` (its `RUN`/`RUN_LOCK` bookkeeping). They do not conflict today because they cover disjoint concerns, but a future reader unfamiliar with this ADR could reasonably ask why there are two.
- The migration cost (building `transition-lint`, `phase`, `trigger`, `run-step`, and moving `orchestrator/` to call them) is already paid, but reversing this decision — restoring `orchestrator/` as sole flow-control owner — would mean unwinding all four mechanisms' role in every playbook that has since come to depend on them being callable without `orchestrator/` running.

## Referenced from

- `04_solution_strategy.md` § 4.1 (planned chapter)
- [09_architecture_decisions.md](../arc42/09_architecture_decisions.md)
- [docs/spec/prd.md § 1 Problem Statement](../spec/prd.md#1-problem-statement)
