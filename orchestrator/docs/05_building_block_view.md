# 5 — Building Block View

## Level 1: run-playbook in context

```mermaid
graph LR
    Human["Human Operator"] -->|invokes| RP["run-playbook"]
    RP -->|reads| Marker[".current-work/playbook-state.yml"]
    RP -->|reads| FSM["factory/playbooks/*.fsm.yml"]
    RP -->|calls| PA["factory/scripts/phase advance"]
    RP -->|calls| PR["factory/scripts/phase retry"]
    RP -->|calls| TR["factory/scripts/trigger"]
    TR -->|launches| CLI["AI CLI (claude / copilot)"]
    PA -->|writes| Marker
    PA -->|reads| FSM
    PR -->|reads/writes| Marker
    RP -->|appends| Audit[".current-work/audit.log"]
```

## Level 2: run-playbook internals

The module has no internal decomposition worth diagramming. It is a single function (`run_one_step`) called in a while loop. Its responsibilities:

| Responsibility                   | Delegated to                                    |
| -------------------------------- | ----------------------------------------------- |
| Read current state               | Marker file (direct read)                       |
| Resolve agent for state          | FSM file (direct read)                          |
| Check if out-gate already passes | `phase advance --dry-run`                       |
| Dispatch agent                   | `trigger agent <name> --background --cli <cli>` |
| Advance marker on gate pass      | `phase advance`                                 |
| Enforce iteration cap            | `phase retry`                                   |
| Write audit entry                | Direct append to `.current-work/audit.log`      |

The orchestrator itself contains no condition evaluation, no prompt composition, no agent resolution, and no marker writing logic.
