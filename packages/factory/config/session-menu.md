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

- **New users** — load the `newcomer-tour` skill. Walk the user through the Getting Started section of `.agent-factory/factory/docs/factory-guide.md` conversationally.
- **Returning users** — load the `guided-tour` skill. Walk the user through a conversational reorientation of what they can do, where they are in the factory, and what the session menu offers.

Ask "Have you used the factory before?" if unclear which tour fits.

______________________________________________________________________

## K — Housekeeping

Present four actions when the developer selects K:

> **1** — About: show factory state\
> **2** — Re-fit: rerun all fitting steps\
> **3** — Update Factory: install latest version\
> **4** — Update agent context: refresh concern registry\
> **5** — Back to the main menu

### About

Run `.agent-factory/factory/scripts/housekeeping-about` and display its output to the developer. The script reads four independent sources and reports:

- **Factory version** and source path — from `.agent-factory/install.json`
- **Fitting status** — from `.agent-factory/config/project-context.json` (X/5 with step names)
- **CLI integrations** — from `.agent-factory/install.json`
- **Usage pipeline health** — from `.agent-factory/usage/` directory existence

Each source is read independently. When a source is unreadable, its line shows `unknown` with the error message.

### Re-fit

Rerun all five fitting steps: model matrix, fingerprint, agent context, test regime, hooks. Call the existing fitting procedure from the virgil agent definition. Report completed and remaining steps after running.

### Update Factory

Run `init-factory --update <project-root> --force`. Relay the command's stdout and exit status to the developer. On success, rerun About to show the refreshed factory state.

### Update agent context

Check if `docs/agent-context.md` exists:

- If yes: invoke the `capture-context` skill with `--update --scan`. The skill scans the repository, compares discovered concerns and Read paths against the existing file, presents differences grouped by category, and writes only confirmed changes.
- If no: tell the developer "docs/agent-context.md does not exist. Run `capture-context --init --scan` to create it." and return to the Housekeeping menu.

______________________________________________________________________

## P — Project Work

The Project Work lane handles workstream creation and continuation. Ask the user whether they want to start a new workstream or continue an existing one.

### Start a new workstream

1. Ask the user for a topic description.
2. Derive the workstream ID by slugifying the topic to lowercase kebab-case (e.g. "activity graph orchestration" → `activity-graph-orchestration`).
3. Ask whether an existing proposal under `docs/proposals/` should be the origin reference. If yes, record its path as `origin_ref`.
4. Create the workstream state file at `.agent-factory/workstreams/<workstream-id>.yaml` using `engine/workstream.py::create_workstream`. The file contains exactly four fields: `schema_version: 2`, `workstream_id`, `topic`, `origin_ref`. No cycle, attempt, delegation, or work fields exist.
5. Create a session binding at `.agent-factory/workstreams/sessions/<session-id>.yaml` using `engine/session_binding.py::create_binding`. The binding records `session_id`, `workstream_id`, and `bound_at`.
6. Confirm the workstream name and binding to the user.
7. Run `.agent-factory/factory/scripts/intent select --workstream <workstream-id>` to present all agents with their precondition evidence. The developer selects an agent from the list.

If the user wants to do something that does not fit a workstream (a quick question, a tour, research), redirect to lane O (Open Stage) instead of creating a workstream.

### Continue an existing workstream

1. List existing workstreams by calling `engine/workstream.py::list_workstreams`, which scans `.agent-factory/workstreams/*.yaml`.
2. If workstreams exist, present a numbered list showing each workstream's topic and ID. Ask the user to select one by number or name. Never select a workstream automatically.
3. On selection, create a session binding for the selected workstream using `engine/session_binding.py::create_binding`.
4. Run `.agent-factory/factory/scripts/intent select --workstream <workstream-id>` to present all agents with their precondition evidence. The developer selects an agent from the list.

If no workstreams exist, tell the user and offer to start a new workstream (go to "Start a new workstream" above) or return to the main menu.

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
