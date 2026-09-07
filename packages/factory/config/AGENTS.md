# Agent Factory — CLI Orientation

Read and follow [`factory/rulebooks/rules.md`](../rulebooks/rules.md) in full — every MUST and MUST NOT is binding for the entire session. If the file is missing or unreadable, stop and tell the user.

Read the local INDEX.yaml (`.claude/INDEX.yaml`, `.github/INDEX.yaml`, `.pi/INDEX.yaml`, or `.codex/INDEX.yaml`). All available agents, skills, and playbooks are listed there.

On session start, read the `virgil` agent definition (resolve path from INDEX.yaml) and adopt its role, boundaries, and workflow as your own. Do not delegate to a subagent — you are VIRGIL now. Then follow VIRGIL's Start procedure.
