# Session Menu

Presented by VIRGIL at the start of a session when no fitting is pending.

> **What do you want to do?**
>
> **A** — I'm new here — show me around\
> **B** — I want to start something new (prove an idea, research a topic, build a system)\
> **C** — I want to run an agent or playbook directly\
> **D** — I just want to talk something through

______________________________________________________________________

## A — Guided tour (newcomer path)

Load the `newcomer-tour` skill. Walk the user through the Getting Started section of `factory/docs/factory-guide.md` conversationally.

______________________________________________________________________

## B — Intention-based (ask what they want to achieve)

Present this expanded tree only after B is chosen:

> **1. Create something new**\
> `a` — Quick answer, throwaway → `poc-spike`\
> `b` — Validate a technical risk / decision before committing → `technical-poc`\
> `c` — Build a real production system → `greenfield-development`
>
> **2. Onboard an existing project**\
> → `brownfield-onboarding`
>
> **3. Change existing code**\
> `a` — Add a feature → `feature-addition`\
> `b` — Fix a defect / bug → `bug-fix`\
> `c` — Restructure without changing behavior → `refactoring`
>
> **4. Sync docs with code**\
> → `documentation-update`
>
> **5. Review what's there**\
> `a` — Review architecture quality (ATAM) → `architecture-review`\
> `b` — QA / exploratory bug hunt → `qa-agent`
>
> **6. Research a topic**\
> `a` — Survey: what do credible sources say → `research-survey`\
> `b` — Falsification: test a hypothesis with refutation → `research-topic`
>
> **7. Talk it through / explore an idea**\
> → stay in open conversation (VIRGIL's resting state)
>
> **8. Back to the main menu**

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

When a playbook is selected, read the playbook's markdown file and follow its operational procedure — running agents, enforcing gates, and producing its documented outputs. When an agent is selected directly: if the agent runs in the current session (coaching-agent), adopt its role per the adopt pattern; otherwise, spawn it via the correct mechanism for this CLI (see rules).
