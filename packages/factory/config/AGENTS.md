# Agent Factory — CLI Orientation

Read and follow [`factory/rulebooks/rules.md`](../rulebooks/rules.md) in full — every MUST and MUST NOT is binding for the entire session. If the file is missing or unreadable, stop and tell the user.

Read the local INDEX.yaml (`.claude/INDEX.yaml`, `.github/INDEX.yaml`, `.pi/INDEX.yaml`, or `.codex/INDEX.yaml`). All available agents, skills, and playbooks are listed there.

## Session start

**BEFORE YOUR FIRST RESPONSE**, follow these two steps in order.

### 1. Check fitting state

Read `config/project-context.json`. If the file exists and `fitting.status` is `"unfitted"`:

Summarize what the scan found (languages, frameworks, CI, linters from the observations). Then ask:

> "I see init-factory scanned this project — [what the scan found]. Want to walk through the fitting, or skip to the main menu?"

**Stop here. Wait for the user's answer. Do not present the session menu. Do not continue to step 2.**

- User accepts → read the `virgil` agent definition (resolve path from INDEX.yaml) and follow its Fitting procedure.
- User declines → continue to step 2.

If the file is missing or `fitting.status` is anything other than `"unfitted"` → continue to step 2.

### 2. Present the session menu

Read and present [`factory/config/session-menu.md`](session-menu.md). It contains the full menu and all option handlers. Follow the instructions there.

## Deeper guidance

For richer session behaviour — fitting details, skill routing, behavioural anchors, and boundaries — read the `virgil` agent definition (resolve path from INDEX.yaml). Strong models benefit from VIRGIL's full definition; it is not a prerequisite for turn 1.
