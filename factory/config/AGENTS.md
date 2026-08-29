# Agent Factory — CLI Orientation

Canonical orientation content for any AI coding CLI working in a project that uses Agent Factory. Symlinked to each CLI's expected root filename at project-init time.

## Rules

- **MUST — TOP-LEVEL SESSION INSTRUCTION**: At the start of every session, before answering the first prompt or taking any project action, read and ingest [`factory/rulebooks/rules.md`](../rulebooks/rules.md) in full. Treat every `MUST` and `MUST NOT` there as binding for the entire session. If the file is missing or unreadable, stop and tell the user; do not continue with partial Factory guidance.

- **MUST** use `rg` with an explicit hidden-file search, or `bash` ( `find`, `fd`, etc.), when the target may live under a hidden directory or file.

- **MUST** resolve skill invocations through the INDEX.yaml first, and only fall back to the global skill/agent directory if the local INDEX.yaml does not list the skill. If the local INDEX.yaml is missing or unreadable, stop and tell the user; do not continue with partial Factory guidance. Local skill directory, by CLI:

  - Claude Code: `.claude/skills/<name>/SKILL.md`, `.claude/agents/<name>.md`
  - GitHub Copilot CLI: `.github/skills/<name>/SKILL.md`, `.github/agents/<name>.md`
  - Pi: `.pi/skills/<name>/SKILL.md`, `.pi/agents/<name>.md`
  - Codex: `.agents/skills/<name>/SKILL.md`, `.codex/agents/<name>.toml`

- **MUST (Pi only)**: Pi has no native subagent. To run a factory *agent* — not a skill — invoke the `run_agent` tool (registered by the `run-agent` extension), passing the agent name and the task. Do not read `.pi/agents/<name>.md` and act it out in the current session: `run_agent` spawns the agent in a separate Pi session, and that separation is what preserves author/reviewer independence. To run several file-disjoint agents in parallel, invoke `dispatch_wave` (registered by the `dispatch-wave` extension), which isolates each in its own git worktree and merges through `premerge-check`. Claude Code, Codex and GitHub Copilot CLI spawn subagents natively and need no such tools.

- **MUST (Codex only)**: Factory agents are generated native custom agents. Spawn `.codex/agents/<name>.toml` through Codex's subagent mechanism; do not read the canonical Markdown and act it out in the parent session. Separate native threads preserve author/reviewer independence. Use `.codex/playbooks`, `.codex/rulebooks`, and `.codex/scripts` for the Factory aliases.

- **MUST**: Read the local `INDEX.yaml` first (`.claude/INDEX.yaml` for Claude Code, `.github/INDEX.yaml` for GitHub Copilot CLI, `.pi/INDEX.yaml` for Pi, `.codex/INDEX.yaml` for Codex). All locally available agents, skills, and playbooks are referenced there. **Codex**: resolve `path:` entries from INDEX.yaml to their generated equivalents under `.codex/` (e.g. `agents/chat-agent.md` → `.codex/agents/chat-agent.toml`, `skills/grilling/SKILL.md` → `.codex/skills/grilling/SKILL.md`).

- **MUST**: Machine-consumed gates, markers, dispatch records, and handoffs use full 40-character Git SHAs. Abbreviated SHAs are display-only.

- **MUST**: Before you answer the first prompt, present the session entrypoint (see below), then act on the user's choice.

## Session Entrypoint

At the start of every session, greet the user warmly, then present four choices:

> **What do you want to do?**
>
> **A** — I'm new here — show me around\
> **B** — I want to start something new (prove an idea, research a topic, build a system)\
> **C** — I want to run an agent or playbook directly\
> **D** — I just want to talk something through
>
> Then act on the user's selection:

______________________________________________________________________

### A — Guided tour (newcomer path)

Read `docs/arc42/beginner-intro.md` and walk the user through it conversationally, one section at a time, pausing for questions after each section. Before starting, check for signs of prior work (a completed poc-spike, a charter, prior playbook outputs). If found, acknowledge what the user has done and offer to skip ahead or start fresh. At the end, offer to run `poc-spike`.

If the user asks "where am I?", "what do I do next?", or requests reorientation at any point during the tour or afterward, invoke the `guided-tour` skill.

______________________________________________________________________

### B — Intention-based (ask what they want to achieve)

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
> → `chat-agent` (adopted in current session)
>
> **8. Back to the main menu**

When the user picks a leaf (a playbook or agent), run that playbook's operational procedure or spawn that agent with the user's stated goal as the task.

______________________________________________________________________

### C — Factory-content-based (user knows what they want to run)

**Playbook or Agent?**

> `P` — Run a playbook
> `A` — Run an agent
> `M` — Back to the Main Menu

On selection, list the full set and let the user pick by name or number, then run that playbook/agent with the user's stated goal as the task.
If `P` -> list all playbooks in the local `.*/playbooks` directory. Append an option to go back to the main menu. If the user picks a playbook, initiate that playbook's operational procedure.
If `A` -> list all agents in the local `.*/agents` directory. Append an option to go back to the main menu. If the user picks an agent, assume that agent's role and ask the user for the intended task.

______________________________________________________________________

### D — Let's talk

Read the `chat-agent` definition (resolve path from INDEX.yaml) and adopt its role, boundaries, and workflow as your own for the rest of this session. Do not delegate to a subagent — you are the chat-agent now. Open with "What's on your mind?" and follow the conversation wherever it leads — no menu, no documents to produce. When the idea finds its shape, route to the right next step: a proposal, a spike, a research brief, or a clean ending.

______________________________________________________________________

When a playbook is selected, read the playbook's markdown file and follow its operational procedure — running agents, enforcing gates, and producing its documented outputs. When an agent is selected directly: if the agent runs in the current session (chat-agent, kit-manager, coaching-agent), adopt its role per the adopt pattern; otherwise, spawn it via the correct mechanism for this CLI (see Pi/Codex/Claude Code/Copilot CLI notes above).
