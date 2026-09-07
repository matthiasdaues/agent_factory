# Session Menu

Presented by VIRGIL at the start of a session when no fitting is pending.

> **What do you want to do?**
>
> **A** — I'm new here — show me around\
> **B** — I want to start something new (prove an idea, research a topic, build a system)\
> **C** — I want to run an agent or playbook directly\
> **D** — I just want to talk something through\
> **?** — Where am I? What can I do next?
>
> At any point, ask 'what is [concept]?' for a plain-language explanation.

______________________________________________________________________

## A — Guided tour (newcomer path)

Load the `newcomer-tour` skill. Walk the user through the Getting Started section of `factory/docs/factory-guide.md` conversationally.

______________________________________________________________________

## B — Intention-based (ask what they want to achieve)

Present this expanded tree only after B is chosen:

> **1. Create something new**\
> `a` — `poc-spike`: build the smallest thing that proves the idea, then throw it away\
> `b` — `technical-poc`: validate a technical risk with a decision-grade prototype\
> `c` — `greenfield-development`: build a real production system from requirements through deployment
>
> **2. Onboard an existing project**\
> → `brownfield-onboarding`: understand an inherited codebase well enough to change it safely
>
> **3. Change existing code**\
> `a` — `feature-addition`: add a feature to an existing system\
> `b` — `bug-fix`: fix a defect in production or development\
> `c` — `refactoring`: improve code structure without changing behavior
>
> **4. Sync docs with code**\
> → `documentation-update`: sync documentation with code when they have drifted
>
> **5. Review what's there**\
> `a` — `architecture-review`: evaluate existing architecture without implementing changes\
> `b` — QA / exploratory bug hunt → `qa-agent`
>
> **6. Research a topic**\
> `a` — `research-survey`: source-grounded survey research\
> `b` — `research-topic`: test a hypothesis with falsification-driven research
>
> **7. Talk it through / explore an idea**\
> → stay in open conversation (VIRGIL's resting state)
>
> **8. Back to the main menu**
>
> At any point, ask 'what is [concept]?' for a plain-language explanation.

When the user picks a leaf (a playbook or agent), run that playbook's operational procedure or spawn that agent with the user's stated goal as the task.

______________________________________________________________________

## C — Factory-content-based (user knows what they want to run)

**Playbook or Agent?**

> `P` — Run a playbook\
> `A` — Run an agent\
> `M` — Back to the Main Menu

On selection, list the full set and let the user pick by name or number, then run that playbook/agent with the user's stated goal as the task.
If `P` → list all playbooks in the local `.*/playbooks` directory. Append an option to go back to the main menu. If the user picks a playbook, initiate that playbook's operational procedure.
If `A` → list all agents in the local `.*/agents` directory. Append an option to go back to the main menu. If the user picks an agent, assume that agent's role and ask the user for the intended task.

______________________________________________________________________

## D — Let's talk

Open with "What's on your mind?" and follow the conversation wherever it leads — no menu, no documents to produce. This is VIRGIL's resting state. When the idea finds its shape, route to the right next step: a proposal, a spike, a research brief, or a clean ending.

______________________________________________________________________

## ? — Guided tour (reorientation)

Load the `guided-tour` skill. Walk the user through a conversational reorientation of what they can do, where they are in the factory, and what the session menu offers.

______________________________________________________________________

When a playbook is selected, read the playbook's markdown file and follow its operational procedure — running agents, enforcing gates, and producing its documented outputs. When an agent is selected directly: if the agent runs in the current session (coaching-agent), adopt its role per the adopt pattern; otherwise, spawn it via the correct mechanism for this CLI (see rules).
