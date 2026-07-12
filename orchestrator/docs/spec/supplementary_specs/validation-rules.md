# Supplementary Specification: Validation Rules

## Exit codes

| Code | Meaning      | When                                                                       |
| ---- | ------------ | -------------------------------------------------------------------------- |
| 0    | Success      | Playbook reached final state, or clean stop at human gate                  |
| 1    | Halt         | Iteration cap hit, or out-gate persistently unmet                          |
| 2    | Config error | Resolution failure from trigger (unknown agent, missing model, broken FSM) |

## Audit log format

Each step writes one JSON-lines entry to `.agent-factory/audit.log`:

```json
{
  "timestamp": "2026-07-12T23:00:00Z",
  "playbook": "greenfield-development",
  "state": "PHASE_2_ARCHITECTURE",
  "agent": "architecture-agent",
  "action": "dispatch|advance|retry|halt|human-gate|done",
  "trigger_exit": 0,
  "phase_advance_exit": 0,
  "phase_retry_exit": null,
  "iteration": 1,
  "duration_seconds": 342.5
}
```

## Marker contract

The orchestrator reads `.agent-factory/playbook-state.yml` but never writes it directly. Only `factory/scripts/phase` writes the marker. This invariant ensures the marker's format and content are governed by a single writer.

## Dispatch contract

The orchestrator calls `trigger` with exactly the same arguments a human would type. The composed prompt is the agent definition file — nothing more, nothing less. No context injection, no findings injection, no iteration-aware phrasing. The agent discovers its work context by reading the filesystem, the same way it would in a human-driven session.

## Self-chaining contract

After a successful `phase advance`, the orchestrator immediately processes the next state within the same process invocation (while loop). It does not fork, exec, or spawn a subprocess of itself. A single `run-playbook` invocation drives the entire run from entry to halt/completion.

## Idempotency

Re-invoking `run-playbook` at any point produces correct behavior:

- If the marker state's out-gate is already satisfied (e.g., outputs exist from a prior agent run that was killed before advance): advance immediately, no re-dispatch.
- If the marker state's agent hasn't run yet: dispatch as normal.
- If the process was killed during agent execution: the marker hasn't advanced (phase advance hasn't been called), so re-dispatch the same agent. The agent sees partial work on disk and continues or redoes — that's the agent's responsibility, not the orchestrator's.

## Dependency on `--dry-run`

FR-05 requires a `--dry-run` flag on `factory/scripts/phase advance`:

- Check all entry conditions for the target state.
- Print pass/fail result.
- Do NOT write the marker.
- Exit 0 if advance would succeed, exit 1 if it would fail.

This is the only change required to an existing factory script.
