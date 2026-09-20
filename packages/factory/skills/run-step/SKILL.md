---
name: run-step
description: Resolve the next agent from the workstream's current cycle and agent eligibility, then dispatch it. Re-derives state from disk on every invocation.
category: utility
---

# Run Step

Dispatches one agent invocation via `.agent-factory/factory/scripts/trigger`. Re-derives "what's next" from the workstream state file and agent eligibility on every invocation, so a crash, a closed terminal, or a fresh session never leaves work stranded behind stale state.

## Step 1 — Read the workstream state

Read the session binding (`.current-work/session-bindings/<session-id>.yaml`) to find the active workstream, then read its state file (`.current-work/cycles/<workstream-id>.yaml`) for the current cycle.

**No binding or state file** → run `.agent-factory/factory/scripts/cycle list --dir .current-work/cycles/` to show available workstreams, or direct the user to start one via the session menu.

## Step 2 — Resolve eligible agents

Read `.claude/INDEX.yaml`. Filter agents whose `inputs.required` preconditions are satisfied by the current repository state.

| Eligible agents | Action                                                                               |
| --------------- | ------------------------------------------------------------------------------------ |
| None            | Tell the user no agents are eligible for this cycle. Offer to list available cycles. |
| One             | Confirm with the user: "Agent X is eligible for cycle Y. Dispatch?"                  |
| Multiple        | Present the list and ask the user to choose. Never auto-select.                      |

## Step 3 — Decide: fresh start, resume, or done

Check the current cycle's expected outputs against what is on disk, then run the applicable gate (`spec-lint`, `arch-lint`, `backlog-lint` — whichever applies):

| Observed state                                     | Action                                                                                           |
| -------------------------------------------------- | ------------------------------------------------------------------------------------------------ |
| Outputs don't exist yet                            | Fresh start — run the chosen agent from Step 1 of its workflow.                                  |
| Outputs exist, gate passes clean, no open findings | Step is done — offer `.agent-factory/factory/scripts/cycle select` to advance to the next cycle. |
| Outputs exist, gate reports open findings          | Resume — run the same agent again; its own workflow reads open findings.                         |
| Outputs exist but the gate errors                  | Stop. Escalate to the user.                                                                      |

## Step 4 — Dispatch

```bash
.agent-factory/factory/scripts/trigger agent <name> --background --cli claude --cwd <project-root>
```

Use `--interactive` instead of `--background` when a human should drive the session directly.

## What this does not read

This skill does **not** read `.current-work/playbook-state.yml`. The workstream state file is the single source of truth for which cycle the workstream is in. The playbook marker is a legacy artifact from the linear FSM; it may still exist on disk but `run-step` ignores it.

## Referenced from

- [.agent-factory/factory/scripts/trigger](../../scripts/trigger)
- [.agent-factory/factory/scripts/cycle](../../scripts/cycle)
