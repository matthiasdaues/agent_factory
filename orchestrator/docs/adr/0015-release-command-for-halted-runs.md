# 0015. Release command for halted runs

**Status**: Accepted

A halted run is a terminal state with no recovery path — the operator must abort and re-run from scratch, losing all completed phases. This is wasteful when the halt cause is transient (auth failure, gate timeout, misconfigured model). The `release` command restores a halted phase to its pre-halt status so the operator can `resume`.

`PhaseRecord` gains a `halted_from: PhaseStatus | None` field, set by `_halt()` before writing `HALTED`. `release` reads `halted_from`, restores that status, resets the iteration counter, and sets `mode: paused`. The operator then runs `resume` to continue. If `halted_from` is absent (legacy or manual halt), `release` refuses.

## Considered Options

- **A**: Auto-retry on transient failures. Dangerous — the orchestrator cannot reliably distinguish transient from permanent without operator judgment.
- **B**: `abort` + re-run. Safe but wasteful — completed phases are discarded.
- **C**: `release` with `halted_from` breadcrumb. Safe (operator decides), efficient (preserves completed work), auditable (the field records what happened).

Option C chosen. `release` is gated by VR-029: `halted_from` must be present, and `mode` must be `halted`.
