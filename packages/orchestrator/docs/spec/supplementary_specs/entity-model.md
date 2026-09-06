# Entity Model — Orchestrator

The orchestrator reads three external entities and calls three external scripts. It owns no persistent state of its own — the marker is the single source of truth for execution position, and only `phase` writes it.

```mermaid
erDiagram
    ORCHESTRATOR ||--|| PLAYBOOK_STATE_MARKER : "reads (never writes)"
    ORCHESTRATOR ||--|| FSM_DEFINITION : "reads track layout"
    ORCHESTRATOR ||--|| AUDIT_LOG : "appends entries"
    ORCHESTRATOR }o--|| PHASE_ADVANCE : "delegates gate checks"
    ORCHESTRATOR }o--|| PHASE_RETRY : "delegates iteration cap"
    ORCHESTRATOR }o--|| TRIGGER : "delegates agent dispatch"

    PLAYBOOK_STATE_MARKER {
        string playbook "FSM name"
        string state "current position on the track"
        int iteration "retry count for current state"
        string recorded_at "timestamp of last advance"
        string recorded_by "who wrote the marker"
    }
    FSM_DEFINITION {
        string playbook "name"
        map states "state definitions with agent and conditions"
        map gate_conditions "condition library"
        list halt_conditions "circuit breakers"
    }
    AUDIT_LOG {
        string timestamp "ISO 8601"
        string playbook "active playbook"
        string state "state being processed"
        string agent "dispatched agent or null"
        string action "dispatch | advance | retry | halt | human-gate | done"
        int trigger_exit "exit code from trigger"
        int phase_advance_exit "exit code from phase advance"
        float duration_seconds "wall clock for agent session"
    }
    PHASE_ADVANCE {
        string mode "real or dry-run"
        int exit_code "0 pass, 1 fail"
    }
    PHASE_RETRY {
        int exit_code "0 cap not hit, 1 cap hit"
    }
    TRIGGER {
        string agent "agent name"
        string cli "claude or copilot"
        string mode "background"
        int exit_code "0 success, 1 agent fail, 2 resolution error"
    }
```

## Entity responsibilities

| Entity                | Single responsibility                                                   |
| --------------------- | ----------------------------------------------------------------------- |
| Playbook state marker | Where the run currently is (position on the track)                      |
| FSM definition        | What the track looks like (states, transitions, conditions, halts)      |
| Audit log             | What happened during this run (append-only event stream)                |
| phase advance         | Whether a transition is allowed (gate evaluation + marker write)        |
| phase retry           | Whether a retry is allowed (iteration cap enforcement)                  |
| trigger               | How to dispatch an agent (resolution + prompt composition + CLI launch) |

## What the orchestrator does NOT own

- Sequencing logic (owned by `phase advance` via FSM transitions)
- Gate evaluation (owned by `phase advance` via `gate_conditions`)
- Agent resolution and prompt composition (owned by `trigger`)
- The marker file format and writes (owned by `phase`)
- Condition types and their evaluation (owned by `phase`'s `evaluate_condition`)
