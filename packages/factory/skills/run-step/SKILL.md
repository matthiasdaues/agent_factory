---
name: run-step
description: Resolve the next agent from agent eligibility preconditions, then dispatch it. Re-derives state from disk on every invocation.
category: utility
---

# Run Step

Read [factory-voice.md](../../rulebooks/conventions/factory-voice.md) now and hold every rule as a writing constraint. No prose reaches terminal output or a file until it passes all four gates and clears the final pass.

Dispatches one agent invocation via `.agent-factory/factory/scripts/trigger`. Re-derives "what's next" from agent eligibility preconditions on every invocation, so a crash, a closed terminal, or a fresh session never leaves work stranded behind stale state.

## Step 1 — Read the workstream state

Read the session binding (`.agent-factory/workstreams/sessions/<session-id>.yaml`) to find the active workstream, then read its identity file (`.agent-factory/workstreams/<workstream-id>.yaml`).

**No binding or identity file** → list workstreams under `.agent-factory/workstreams/`, or direct the user to start one via the session menu.

## Step 2 — Resolve eligible agents

Read `.claude/INDEX.yaml`. Filter agents whose `inputs.required` preconditions are satisfied by the current repository state.

The declared inputs set the order of the producers. An agent is eligible once its required inputs exist, so a producer runs before the agents that read its output. When two agents are eligible, the operator chooses between them.

| Eligible agents | Action                                                                                          |
| --------------- | ----------------------------------------------------------------------------------------------- |
| None            | Tell the user no agents are eligible given current preconditions. Offer to run `intent select`. |
| One             | Confirm with the user: "Agent X is eligible based on precondition evidence. Dispatch?"          |
| Multiple        | Present the list and ask the user to choose. Never auto-select.                                 |

## Step 3 — Decide: fresh start, resume, or done

Check the agent's declared outputs against what is on disk, then run the applicable gate (`spec-lint`, `arch-lint`, `backlog-lint` — whichever applies):

| Observed state                                     | Action                                                                     |
| -------------------------------------------------- | -------------------------------------------------------------------------- |
| Outputs don't exist yet                            | Fresh start — run the chosen agent from Step 1 of its workflow.            |
| Outputs exist, gate passes clean, no open findings | Step is done — offer `intent select` to see what agents are eligible next. |
| Outputs exist, gate reports open findings          | Resume — run the same agent again; its own workflow reads open findings.   |
| Outputs exist but the gate errors                  | Stop. Escalate to the user.                                                |

A step is done once its outputs exist, the gate passes, and no finding is open. A changed input never restarts a step that is done. The producer of the changed file starts the next pass in its handoff. For example, the domain-modeling agent changes `docs/spec/entity-model.md`, and its handoff starts the architecture agent's component pass.

## Step 4 — Dispatch

The input of this step includes the stop notice. When `dispatch` or `premerge-check` exits `1` and prints `STOP:`, dispatch nothing. In an interactive session, explain each stopping finding with `explain-review-finding` and wait. A headless run ends with the notice in its final summary.

```bash
.agent-factory/factory/scripts/trigger agent <name> --background --cli claude --cwd <project-root>
```

Use `--interactive` instead of `--background` when a human should drive the session directly.

## Referenced from

- [.agent-factory/factory/scripts/trigger](../../scripts/trigger)
- [.agent-factory/factory/scripts/intent](../../scripts/intent)
