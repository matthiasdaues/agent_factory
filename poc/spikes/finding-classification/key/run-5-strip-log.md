# Strip log

## ATAM-0002

```
severity: major
category: defect
status: open
```

## ATAM-0003

```
severity: major
category: defect
status: open
```

## ATAM-0004

```
severity: major
category: defect
status: open
```

## ATAM-0005

```
severity: major
category: defect
status: open
```

## ATAM-0006

```
severity: minor
category: question
status: open
```

## ATAM-0007

```
severity: major
category: defect
status: open
```

## ATAM-0008

```
severity: major
category: defect
status: open
```

## ATAM-0009

```
severity: major
category: defect
status: open
```

## FAGAN-0001

```
severity: major
category: defect
status: open
```

## FAGAN-0002

```
severity: critical
category: defect
status: open
```

## FAGAN-0003

```
severity: minor
category: defect
status: open
If ST-0003E is deferred or dropped, this finding returns to major, because
```

## RECON-0001

```
severity: minor
category: defect
status: open
```

## SPEC-0001

```
severity: major
category: defect
status: open
```

## SPEC-0002

```
severity: major
category: defect
status: open
```

## SPEC-0003

```
severity: major
category: question
status: open
```

## SPEC-0004

```
severity: major
category: defect
status: open
```

## SPEC-0005

```
severity: major
category: defect
status: open
```

## SPEC-0006

```
severity: major
category: defect
status: open
```

## SPEC-0007

```
severity: major
category: defect
status: open
```

## SPEC-0008

```
severity: major
category: defect
status: open
```

## SPEC-0009

```
severity: major
category: defect
status: open
```

## SPEC-0010

```
severity: major
category: question
status: open
```

## SPEC-0011

```
severity: major
category: defect
status: open
```

## SPEC-0012

```
severity: major
category: defect
status: open
```

## SPEC-0013

```
severity: major
category: defect
status: open
```

## SPEC-0014

```
severity: major
category: question
status: open
```

## SPEC-0015

```
severity: major
category: defect
status: open
```

## SPEC-0016

```
severity: major
category: defect
status: resolved
**Resolution:** Resolved in the working tree on `dev`, not yet committed. A final `RETURN` in `UNKNOWN` waits for nothing, because `UNKNOWN` waits for exactly this proof. The wait rule in `interface-contracts.md` and `state-machines.md` says so, the contract table accepts the final `RETURN` with a `process_identity` from `RUNNING` or `UNKNOWN`, and the Scenario "Final RETURN ends UNKNOWN" under RES-01 asserts it.
```

## SPEC-0017

```
severity: major
category: defect
status: resolved
**Resolution:** Resolved in the working tree on `dev`, not yet committed. Manual Execute has the new ID `DSP-06` in the scope map, the feature Rule, the QA strategy, `runtime-views.md`, `epics.md`, and the companion. `DSP-05` stays on the intervention rule.
```

## SPEC-0018

```
severity: major
category: defect
status: resolved
**Resolution:** Resolved in the working tree on `dev`, not yet committed. Way 2: the global model stays unchanged. `interface-contracts.md`, the feature Rule, `state-machines.md`, and `entity-model.md` mark the start in `RUN` without a `plan_id` as the Increment 01 stage of the first execution slice, with a link to the companion's "What we left out".
```

## SPEC-0019

```
severity: major
category: defect
status: resolved
**Resolution:** Resolved in the working tree on `dev`, not yet committed. The DEC-29 case is a **contradiction** (not stored), and the case that passes the wait but matches no state change is an **unmatched message** (stored without `applied`). Both terms are defined in `interface-contracts.md` and `docs/CONTEXT.md` and used in the feature file, the gaps report, the QA strategy, the scope map, and `epics.md`.
```

## SPEC-0020

```
severity: major
category: defect
status: resolved
**Resolution:** Resolved in the working tree on `dev`, not yet committed. The Manual Execute Rule has Scenarios for `NO_AGENT_SLOT`, `INVALID_COMMAND_SYNTAX`, a future `runs_from`, and the `GET` route. The QA strategy has the row `DSP-06-IT-01`, EPIC 3 names Manual Execute, and `runtime-views.md` cites `DSP-06`.
```

## SPEC-0021

```
severity: major
category: defect
status: resolved
**Resolution:** Resolved in the working tree on `dev`, not yet committed. RES-09 is `specified` for the execution path (`TASK_INSTANCE`, `ATTEMPT`, `OUTBOX`, `INBOX`), with the Rule "Every state change records its time", one Scenario per table plus a retry Scenario, and the QA row `RES-09-IT-01`. T-0058 keeps the other state machines open.
```

## SPEC-0022

```
severity: major
category: defect
status: resolved
**Resolution:** Resolved in the working tree on `dev`, not yet committed. RES-03 links to the Rule "One client per Agent ID receives offers" and to the runtime view "One pinned Agent client". `epics.md` says the consumer pins one client per Agent ID. The Agent Gateway owns registration and heartbeats, not fencing, so `runtime-views.md` drops "and fencing". The QA row expects the message to be stored once after the check.
```

## SPEC-0023

```
severity: minor
category: defect
status: resolved
**Resolution:** Resolved in the working tree on `dev`, not yet committed. `COMMAND_REJECTED` is named as a slot-releasing message in `entity-model.md`, `interface-contracts.md`, `runtime-views.md`, and the DSL. The DSL names the lock order Task Instance, Attempt, `OUTBOX`.
```

## SPEC-0024

```
severity: minor
category: defect
status: resolved
**Resolution:** Resolved in the working tree on `dev`, not yet committed. `OUTBOX.agent_id` is a copy of the Attempt's `agent_id` for Commands.
```

## SPEC-0025

```
severity: minor
category: defect
status: resolved
**Resolution:** Resolved in the working tree on `dev`, not yet committed. The Attempt glossary entry links to `entity-model.md#attempt`. EPIC 3 has one Dispatch Engine row that names both tasks.
```

## SPEC-0026

```
severity: minor
category: defect
status: resolved
**Resolution:** Resolved in the working tree on `dev`, not yet committed. `DISPATCH_TARGET_UNKNOWN` has one meaning in both rows: the dispatch target resolves to no Agent.
```
