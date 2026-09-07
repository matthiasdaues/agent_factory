---
name: run-step
description: Resolve and run the next agent or playbook step, deciding what "resume" means from observable state (the phase-gate marker, gate results, open findings) rather than a separately persisted execution status.
category: utility
disable-model-invocation: false
---

# Run Step

Dispatches one agent invocation via `factory/scripts/trigger`. What makes this a *resume* mechanism rather than a plain dispatcher: it re-derives "what's next" from disk every time it runs, so a crash, a closed terminal, or a fresh session never leaves work stranded behind stale state. There is no run-status file for this skill to trust or distrust — every fact it needs is already checked by an existing gate.

## Step 1 — Find the current playbook and phase

Read `.current-work/playbook-state.yml` if it exists — it names the active playbook and the current FSM state (written by `factory/scripts/phase advance`, checked by `factory/scripts/transition-lint`).

**No marker** → ask the user which playbook to run, then bootstrap one: `factory/scripts/phase advance` with no prior marker creates it at the playbook's root state.

## Step 2 — Resolve the state to an agent

If the playbook has a companion `.fsm.yml` (check `factory/INDEX.yaml`'s `fsm:` field for that playbook — only `greenfield-development` has one today): read the current state's `agent:` field directly from the `.fsm.yml`. That is the exact agent to run — not a position in `INDEX.yaml`'s derived `agents:` list, which is ordered but doesn't carry state names.

**No `.fsm.yml`** → use `INDEX.yaml`'s `agents:` array for that playbook in order; ask the user to confirm which step they're on the first time, since nothing on disk names it.

## Step 3 — Decide: fresh start, resume mid-step, or already done

Check the current state's `outputs:` glob (from the `.fsm.yml`, when one exists) against what's actually on disk, then run that phase's own gate (`spec-lint`, `arch-lint`, `backlog-lint` — whichever applies):

| Observed state                                                    | Action                                                                                                                                                                                                                                                              |
| ----------------------------------------------------------------- | ------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| Outputs don't exist yet                                           | Fresh start — run the author agent from Step 1 of its workflow.                                                                                                                                                                                                     |
| Outputs exist, gate passes clean, no open findings for this phase | Step is done — advance: `factory/scripts/phase advance`, then go to Step 2 for the new state.                                                                                                                                                                       |
| Outputs exist, gate reports open findings                         | Resume, but check the cap first: `factory/scripts/phase retry`. Refuses (non-zero exit) once this loop's iteration cap is hit — stop and escalate, do not re-dispatch. Otherwise run the SAME agent again; its own workflow reads open findings and addresses them. |
| Outputs exist but the gate errors (not just fails)                | Stop. Something is broken beyond "findings to address" — escalate to the user rather than guessing.                                                                                                                                                                 |

No playbook with a `.fsm.yml` → skip the outputs/gate check; ask the user whether the current step is done. `phase retry` also has nothing to check against (no FSM, no halt_conditions) — track loop count yourself and escalate if it doesn't feel like it's converging.

## Step 4 — Dispatch

```bash
factory/scripts/trigger agent <name> --background --cli claude --cwd <project-root>
# or, for one step of a playbook by name (not index — sidesteps any
# state-name/list-position mismatch):
factory/scripts/trigger playbook <playbook-name> --step <agent-name> --background --cli claude --cwd <project-root>
```

Use `--interactive` instead of `--background` when a human should drive the session directly rather than let it run unattended.

## Iteration cap

`factory/scripts/phase retry` is the loop killer: call it before every re-dispatch of a state whose gate found open findings (Step 3's "Resume" row), never after the fact. It increments a per-loop counter on the marker and refuses once a limit is hit — checked in order:

1. The playbook's own `.fsm.yml` — a `halt_conditions` entry of `type: max_iterations` naming the loop's target state, with its own `limit` and human `message` (already declared in `greenfield-development.fsm.yml` for all three review loops; this command is what makes that config do anything — it was previously declared but never enforced).
2. `--default-max-iterations` (default 5) for any state that declares none.

A refusal means: stop, tell the user, do not loop again — the exact scenario this exists to prevent.

## What this deliberately does not do (yet)

**No CLI-failure classification.** `factory/scripts/trigger` returns the invoked CLI's raw exit code; it does not distinguish an auth failure from a config error from a genuine task failure the way `orchestrator`'s `CopilotAdapter` does (regex-matched stderr, ADR-0002). A non-zero exit means: read the output, don't auto-retry.

Known, named gap — not a silent regression from what `orchestrator` did. Fold it in here if it turns out to matter in practice; don't build it ahead of a real case (YAGNI).

## Referenced from

- [factory/scripts/trigger](../../scripts/trigger)
