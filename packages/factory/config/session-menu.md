# Session Menu

Presented by VIRGIL at the start of a session when no fitting is pending.

> **What do you want to do?**
>
> **A** — I'm new here — show me around\
> **B** — I want to start something new (prove an idea, research a topic, build a system)\
> **C** — I want to run an agent or playbook directly\
> **D** — I just want to talk something through\
> **E** — Where am I? What can I do next?
>
> At any point, ask 'what is [concept]?' for a plain-language explanation.

______________________________________________________________________

## A — Guided tour (newcomer path)

Load the `newcomer-tour` skill. Walk the user through the Getting Started section of `factory/docs/factory-guide.md` conversationally.

______________________________________________________________________

## B — Start something new (create a workstream)

Ask the user for a topic description. If the user names an existing proposal under `docs/proposals/`, record it as the origin reference.

Run `factory/scripts/cycle select --state .current-work/cycles/<workstream-id>.yaml --topic "<topic>" IDEA [--work <proposal-path>]` where `<workstream-id>` is the topic slugified to lowercase kebab-case.

On success, confirm the workstream name, cycle IDEA, and the state file path. The session is now bound to that workstream.

If the user wants to do something that does not fit a workstream (a quick question, a tour, research), redirect to option D or the appropriate menu item instead of creating a workstream.

______________________________________________________________________

## C — Factory-content-based (user knows what they want to run)

**Playbook or Agent?**

> `P` — Run a playbook\
> `A` — Run an agent\
> `M` — Back to the Main Menu

On selection, list the full set and let the user pick by name or number, then run that playbook/agent with the user's stated goal as the task.
If `P` → list all playbooks in the local `.*/playbooks` directory. Append an option to go back to the main menu. If the user picks a playbook, initiate that playbook's operational procedure.
If `A` → list all agents in the local `.*/agents` directory. Append an option to return to the main menu. When the user selects an agent, adopt its role in the current session and ask for the intended task. If that agent explicitly requires isolation from work already performed in the session, spawn it instead.

______________________________________________________________________

## D — Let's talk

Open with "What's on your mind?" and follow the conversation wherever it leads — no menu, no documents to produce. This is VIRGIL's resting state. When the idea finds its shape, route to the right next step: a proposal, a spike, a research brief, or a clean ending.

______________________________________________________________________

## ? — Guided tour (reorientation)

Load the `guided-tour` skill. Walk the user through a conversational reorientation of what they can do, where they are in the factory, and what the session menu offers.

______________________________________________________________________

When a playbook is selected, follow its operational procedure, including any required agent dispatch and isolation boundaries. When an agent is selected directly, adopt its role in the current session. Spawn it only when its definition requires a separate session or when the current session has performed work from which that agent must remain independent.
