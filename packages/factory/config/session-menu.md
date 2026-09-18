# Session Menu

Presented by VIRGIL at the start of a session when no fitting is pending.

> **What do you want to do?**
>
> **H** — Help: I'm new here or need orientation\
> **K** — Housekeeping: project setup and maintenance\
> **P** — Project Work: start or continue a workstream\
> **O** — Open Stage: let's just talk
>
> At any point, ask 'what is [concept]?' for a plain-language explanation.

______________________________________________________________________

## H — Help

Route to a tour skill based on familiarity:

- **New users** — load the `newcomer-tour` skill. Walk the user through the Getting Started section of `factory/docs/factory-guide.md` conversationally.
- **Returning users** — load the `guided-tour` skill. Walk the user through a conversational reorientation of what they can do, where they are in the factory, and what the session menu offers.

Ask "Have you used the factory before?" if unclear which tour fits.

______________________________________________________________________

## K — Housekeeping

Housekeeping actions are coming soon — about, re-fit, update factory, update agent context. Return to the menu to continue.

______________________________________________________________________

## P — Project Work

The Project Work lane handles workstream creation and continuation.

### Start a new workstream

Ask the user for a topic description. If the user names an existing proposal under `docs/proposals/`, record it as the origin reference.

Create a workstream and bind the session. The session is now bound to that workstream.

If the user wants to do something that does not fit a workstream (a quick question, a tour, research), redirect to lane O or the appropriate menu item instead of creating a workstream.

### Continue an existing workstream

List existing workstreams. If workstreams exist, present a numbered list showing each workstream's topic. Ask the user to select one by number or name.

On selection, bind the session to that workstream and assess precondition status. Present the results to the user.

If no workstreams exist, tell the user and offer to start a new workstream or return to the main menu. Never select a workstream automatically.

### Intention-based routing

Once a workstream is active, present this expanded tree:

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
> `b` — `qa-agent`: review code for correctness, security, and robustness
>
> **6. Research a topic**\
> `a` — `research-survey`: source-grounded survey research\
> `b` — `research-topic`: test a hypothesis with falsification-driven research
>
> **7. Run an agent or playbook directly**\
> List playbooks and agents; let the user pick by name or number.
>
> **8. Back to the main menu**
>
> At any point, ask 'what is [concept]?' for a plain-language explanation.

When the user picks a leaf (a playbook or agent), run that playbook's operational procedure or spawn that agent with the user's stated goal as the task.

______________________________________________________________________

## O — Open Stage

Open with "What's on your mind?" and follow the conversation wherever it leads — no menu, no documents to produce, no workstream binding. This is VIRGIL's resting state.

When the idea finds its shape, route to the right next step: a proposal, a spike, a research brief, or a clean ending. VIRGIL routes to the appropriate skill or agent when the conversation reaches a concrete step.

______________________________________________________________________

When a playbook is selected, follow its operational procedure, including any required agent dispatch and isolation boundaries. When an agent is selected directly, adopt its role in the current session. Spawn it only when its definition requires a separate session or when the current session has performed work from which that agent must remain independent.
