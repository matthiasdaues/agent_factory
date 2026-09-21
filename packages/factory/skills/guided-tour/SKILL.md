---
name: guided-tour
description: Mid-session reorientation — show where the user is in the current workflow, what they can do next, and what factory concepts are relevant. Outside an active playbook, present the session entrypoint options with explanations.
category: utility
---

# Guided Tour

Reorient the user at any point in a session. Answer "where am I?", "what do I do next?", and "what are we doing?" without requiring the user to know factory vocabulary first.

## When invoked

### Inside an active workstream

Read workstream state under `.agent-factory/workstreams/` to determine the current context.

Present three things:

1. **Where you are.** Name the playbook and workstream topic in plain language. Example: "You're working on the feature-addition playbook for the search-indexing workstream."
2. **What you can do next.** List the immediate next actions — run `intent select` to see eligible agents, invoke `run-step` to determine the next step, or the decision the user needs to make.
3. **What's relevant.** Name the factory concepts involved (the current agent's role, the skills it uses, the preconditions it must satisfy) with one-sentence plain-language explanations.

### Outside an active playbook

No playbook-state marker exists. Present the session entrypoint options with explanations of what each leads to:

- **H — Help: I'm new here or need orientation.** Adopts VIRGIL and loads the `newcomer-tour` skill, which walks through the Getting Started section of `.agent-factory/factory/docs/factory-guide.md` conversationally.
- **K — Housekeeping: project setup and maintenance.** Check factory state, re-fit, update the factory, or refresh agent context.
- **P — Project Work: start or continue a workstream.** Opens the intention tree: spike, PoC, greenfield, brownfield, feature, bug fix, refactoring, docs sync, review, or research.
- **O — Open Stage: let's just talk.** Adopts VIRGIL for open-ended conversation.

Explain each option in one sentence of plain language — no factory jargon.

## Tone

Plain language throughout. Introduce factory terms only when they are immediately relevant, and define each on first use. A newcomer who has never seen Agent Factory should understand every sentence.

## Boundaries

- This skill reads state and presents information. It does not modify files, create artifacts, or advance playbook state.
- It does not replace the session entrypoint — it supplements it with mid-session access.
