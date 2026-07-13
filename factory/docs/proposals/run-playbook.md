# Proposal: `run-playbook` — step-at-a-time playbook execution along FSM rails

## The mental model

A playbook is a set of rails. The FSM is the track layout — states are stations,
gate conditions are the signals. An agent does the work at each station. What's
missing is the train: something that pulls into a station, does the work, checks
the outbound signal, and rolls forward to the next station — or stops if the
signal is red.

Today a human is the train. They read the marker, pick the agent, open a CLI
session, wait, check gates, call `phase advance`, and pick the next agent. The
human isn't doing creative work here — they're doing mechanical dispatch. That's
what `run-playbook` replaces.

## One step per invocation

`run-playbook` is not a loop. It executes **one step**:

01. Read the marker to find the current state.
02. Check entry conditions for that state (already done by `phase advance`
    when we arrived here).
03. Resolve the state's agent from the FSM.
04. Dispatch that agent via `trigger --background`.
05. Wait for the agent to finish.
06. Check the state's exit conditions (the out-gate).
07. If out-gate passes → call `phase advance` to move the marker → invoke
    itself for the next step.
08. If out-gate fails → call `phase retry` to check the iteration cap →
    invoke itself for the same step (retry).
09. If retry cap hit → stop. Print the halt message. Exit non-zero.
10. If `agent: null` (human gate) → stop. Print what the human needs to do.
    Exit zero. Human re-invokes when ready.
11. If state is `final: true` → stop. Print done. Exit zero.

The "loop" is emergent: step 7 calls itself. But each invocation is
self-contained — it reads all state from disk (the marker, the FSM, the
filesystem), decides one thing, does one thing, and either chains to the next
or stops.

This means:

- **Crash recovery is free.** Kill the process at any point. Re-run
  `run-playbook`. It reads the marker, sees where it is, and picks up. No
  run-state to corrupt — the marker is the only truth, and `phase advance`
  writes it atomically.

- **Human intervention is natural.** At any `agent: null` state, `run-playbook`
  stops. The human does their thing (reviews the backlog, approves, rejects).
  Then re-invokes `run-playbook`. It reads the marker, checks conditions, and
  continues.

- **The existing gate mechanism is the only sequencing logic.** `run-playbook`
  doesn't re-implement condition evaluation. It calls `phase advance` — the
  same script a human calls. If `phase advance` refuses, `run-playbook`
  refuses. If `phase advance` succeeds, `run-playbook` moves on.

## What's human-initiated vs. what's automatable

Not every state is automatable.

**Requirements (Phase 1)** is always human-initiated and human-driven. The
requirements agent interviews the human; specs exist because a human
participated. `run-playbook` doesn't drive Phase 1.

**Approval gates** (`PHASE_3_APPROVAL` in greenfield, any `agent: null` state)
are human checkpoints. `run-playbook` stops at these and returns control. The
human approves or rejects, then re-invokes.

**Everything else** — Architecture, Architecture Review, Planning,
Implementation, Reconciliation, QA, QA Fix loops — is agent-driven and
gate-checked. These are the states `run-playbook` drives automatically, one
after another, along the rails.

Entry point for greenfield: the marker is at `PHASE_2_ARCHITECTURE` (Phase 1
complete, specs exist, findings resolved). For bug-fix: marker at
`IMPLEMENT_FIX` (bug filed).

## What already exists

| Component                           | What it does for run-playbook                                                                                                                                                                                               |
| ----------------------------------- | --------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| `phase advance`                     | The outbound signal check. Evaluates entry conditions for the target state. Writes the marker forward. Refuses if conditions unmet. **This is the gate mechanism — run-playbook delegates all sequencing decisions to it.** |
| `phase retry`                       | The iteration cap. Increments the per-state counter, refuses when the halt condition fires. **This is the circuit breaker — run-playbook delegates all "should I try again" decisions to it.**                              |
| `trigger agent <name> --background` | The dispatch mechanism. Resolves agent → tier → model, composes prompt, launches CLI, blocks until done, returns exit code. **This is the agent invocation — run-playbook delegates all AI interaction to it.**             |
| `.agent-factory/playbook-state.yml` | The track position. Written by `phase`, read by everyone. **This is the single source of truth for where the train is.**                                                                                                    |
| The `.fsm.yml` files                | The track layout. States, transitions, gate conditions, halt conditions. **run-playbook reads these but never writes them.**                                                                                                |

## What's missing

Almost nothing. The three building blocks (`phase`, `trigger`, marker) cover
the mechanics. What's missing is the glue between them — the part where a
human currently sits:

1. **Read state → pick agent → call trigger → check result → call phase
   advance or phase retry → repeat or stop.** This is the module.

2. **A `--dry-run` flag on `phase advance`** — check whether advance would
   succeed without actually writing the marker. `run-playbook` needs this
   to inspect out-gate status before deciding dispatch vs. advance.

Nothing else. No new gate types. No new condition evaluators. No new state
persistence. The rails already exist. The signals already work. The module
just rides them.

## The proposed module: `factory/scripts/run-playbook`

```
Usage:
  run-playbook [--playbook NAME] [--cli claude|copilot] [--from-state STATE]

  --playbook     Which FSM to follow (default: read from marker, or greenfield-development)
  --cli          Which AI CLI to dispatch agents through (default: claude)
  --from-state   Bootstrap the marker at this state (first run only; ignored if marker exists)
```

### Pseudocode for one invocation

```python
def run_one_step(playbook, cli):
    marker = read_marker()  # disk state
    fsm = read_fsm(playbook)  # track layout
    state = marker.current_state  # where are we?

    if fsm.states[state].final:
        print("Done.")
        return EXIT_DONE

    agent = fsm.states[state].agent

    if agent is None:  # human gate
        print(f"Human action needed at {state}: {fsm.states[state].description}")
        print("Re-invoke run-playbook when ready.")
        return EXIT_HUMAN_GATE

    # --- Can we already advance? (outputs from a previous run?) ---
    if phase_advance(dry_run=True) == 0:
        phase_advance()  # write the marker forward
        return run_one_step(playbook, cli)  # next station (self-call)

    # --- Dispatch the agent ---
    exit_code = trigger(agent, background=True, cli=cli)

    if exit_code == 2:  # resolution error (config broken)
        return EXIT_CONFIG_ERROR

    # --- Check the out-gate ---
    if phase_advance(dry_run=True) == 0:
        phase_advance()  # signal is green — advance
        return run_one_step(playbook, cli)  # next station

    # --- Out-gate red — retry? ---
    if phase_retry() != 0:  # cap hit
        print(f"Halt: iteration cap reached at {state}.")
        return EXIT_HALT

    return run_one_step(playbook, cli)  # same station, next attempt
```

That's it. Every `phase_advance()` call is literally
`subprocess.run(["factory/scripts/phase", "advance"])`. Every `trigger()` call
is literally `subprocess.run(["factory/scripts/trigger", "agent", name, ...])`.
No reimplementation. No new logic. Just glue.

### Walk-through: bug-fix playbook

```
$ run-playbook --playbook bug-fix --from-state IMPLEMENT_FIX --cli claude

[1] State: IMPLEMENT_FIX
    Agent: developer-agent
    Dispatching: factory/scripts/trigger agent developer-agent --background --cli claude
    ... (agent runs TDD, commits fix) ...
    Agent exited 0.
    Out-gate: tests_pass → checking factory/scripts/run-tests ... passed ✓
    Advancing: IMPLEMENT_FIX → QA_VALIDATION

[2] State: QA_VALIDATION
    Agent: qa-agent
    Dispatching: factory/scripts/trigger agent qa-agent --background --cli claude
    ... (agent runs Fagan review, security review) ...
    Agent exited 0.
    Out-gate: no_new_qa_findings → checking docs/findings/{FAGAN,SEC,BUG}-*.md ... 0 open ✓
    Advancing: QA_VALIDATION → MARK_RESOLVED

[3] State: MARK_RESOLVED
    Agent: null (human gate)
    → Human action needed: update BUG-NNNN.md status to resolved.
    Re-invoke run-playbook when ready.

$ sed -i 's/status: open/status: resolved/' docs/findings/BUG-0001.md
$ run-playbook --playbook bug-fix --cli claude

[4] State: MARK_RESOLVED
    Out-gate: bug_resolved → checking docs/findings/BUG-*.md ... 0 open ✓
    Advancing: MARK_RESOLVED → DONE

[5] State: DONE (final)
    ✓ Bug-fix playbook complete.
```

### Walk-through: greenfield (Phase 2 onward)

```
$ run-playbook --playbook greenfield-development --from-state PHASE_2_ARCHITECTURE --cli claude

[1] PHASE_2_ARCHITECTURE → architecture-agent dispatched
    Out-gate passes → advance to PHASE_2_GATE

[2] PHASE_2_GATE → architecture-review-agent dispatched
    Out-gate: no_open_atam_findings → 1 open finding (ATAM-0003)
    Retry (iteration 1/5) → re-dispatch architecture-agent at PHASE_2_ARCHITECTURE
    ... (agent addresses finding) ...
    Out-gate passes → advance to PHASE_2_GATE
    Out-gate: no_open_atam_findings → 0 open ✓ → advance to PHASE_3_PLANNING

[3] PHASE_3_PLANNING → planning-agent dispatched
    Out-gate: backlog_valid → passes ✓ → advance to PHASE_3_APPROVAL

[4] PHASE_3_APPROVAL → agent: null
    → Human action needed: review and approve the backlog.
    Re-invoke run-playbook when ready.

$ run-playbook --playbook greenfield-development --cli claude

[5] PHASE_3_APPROVAL
    Out-gate passes (backlog approved) → advance to PHASE_4_IMPLEMENTATION

[6] PHASE_4_IMPLEMENTATION → implementation-agent dispatched
    ... (spawns developer-agent subagents internally) ...
    Out-gate: code_exists + tests_pass → passes ✓ → advance to PHASE_4_GATE

[7] PHASE_4_GATE → reconciliation-agent dispatched
    ... and so on through PHASE_5_QUALITY → DONE
```

## What this deliberately does not do

**No parallel dispatch.** One agent at a time. The implementation-agent
parallelizes internally (developer-agent subagents), but `run-playbook` sees
one trigger call, one exit code. The FSM is a linear track with loops, not a
DAG.

**No failure classification beyond exit codes.** `trigger` returns the CLI's
raw exit code. `run-playbook` treats 0 as success, 2 as config error,
everything else as "agent finished but work may be incomplete — check the
out-gate." The out-gate is the real arbiter, not the exit code.

**No prompt enrichment on retry.** When retrying, the same agent definition is
sent again. The agent discovers open findings by reading the filesystem (that's
how `run-step` works today). A future improvement: inject findings into the
prompt so the agent starts informed. Named gap, not a blocker.

**No Requirements phase automation.** Phase 1 is human-driven. `run-playbook`
starts after specs exist.

## What's needed to build this

| Deliverable                         | Scope                                                                                                                                                                     |
| ----------------------------------- | ------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| `factory/scripts/run-playbook`      | ~120 lines Python. Calls `phase advance`, `phase retry`, and `trigger` as subprocesses. Reads FSM for agent resolution and human-gate detection. Self-calls for chaining. |
| `--dry-run` flag on `phase advance` | ~10 lines in `factory/scripts/phase`. Check conditions, print result, don't write marker.                                                                                 |
| README section                      | "Running a playbook from the command line" in `factory/README.md`                                                                                                         |

No changes to `trigger`, the FSMs, the gate conditions, or the marker format.
The rails are already laid. This lays the train on them.

## Open questions

1. **Self-invocation mechanism.** The pseudocode shows a recursive function
   call. In practice this could be a `while True` loop within a single process
   (simpler), or literal `os.execv` self-replacement (restarts clean, no stack
   growth), or `subprocess.run(sys.argv)` (each step is a separate process,
   maximum isolation). The choice affects crash behavior but not correctness —
   the marker is the truth regardless.

2. **Logging.** The FSM's `audit:` section declares `.agent-factory/audit.log`.
   Should `run-playbook` write to it? It would mean structured audit entries
   (timestamp, state, agent, exit code, duration) without inventing a new log.
   The alternative is stdout-only — simpler, but no post-mortem trail beyond
   terminal scrollback.

3. **Rejection at human gates.** `PHASE_3_APPROVAL` has two events:
   `BacklogApproved` and `BacklogRejected`. The latter transitions back to
   `PHASE_3_PLANNING`. Should `run-playbook` offer a reject option at human
   gates (move marker backward), or only support "continue" (advance)?
   Supporting reject means `run-playbook` needs to know which event to fire —
   currently `phase advance` always fires the forward transition.
