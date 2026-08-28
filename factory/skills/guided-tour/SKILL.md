---
name: guided-tour
description: Mid-session reorientation — show where the user is in the current workflow, what they can do next, and what factory concepts are relevant. Outside an active playbook, present the session entrypoint options with explanations.
category: utility
---

# Guided Tour

Reorient the user at any point in a session. Answer "where am I?", "what do I do next?", and "what are we doing?" without requiring the user to know factory vocabulary first.

## When invoked

### Inside an active playbook

Read `.current-work/playbook-state.yml` (if it exists) to determine the current phase and state.

Present three things:

1. **Where you are.** Name the playbook, current phase, and current state in plain language. Example: "You're in the greenfield-development playbook, in the Requirements phase. The requirements-agent has finished and the spec-review-agent is about to run."
2. **What you can do next.** List the immediate next actions — the gate that needs to pass, the agent that runs next, or the decision the user needs to make.
3. **What's relevant.** Name the factory concepts involved (the current agent's role, the skills it uses, the gate it must pass) with one-sentence plain-language explanations.

### Outside an active playbook

No playbook-state marker exists. Present the session entrypoint options with explanations of what each leads to:

- **A — I'm new here — show me around.** Walks through `docs/arc42/beginner-intro.md` conversationally, one section at a time.
- **B — I want to start something.** Opens the intention tree: spike, PoC, greenfield, brownfield, feature, bug fix, refactoring, docs sync, review, or research.
- **C — I want to run an agent or playbook directly.** Lists available agents and playbooks from INDEX.yaml.
- **D — I just want to talk something through.** Adopts the chat-agent role for open-ended conversation.

Explain each option in one sentence of plain language — no factory jargon.

## Tone

Plain language throughout. Introduce factory terms only when they are immediately relevant, and define each on first use. A newcomer who has never seen Agent Factory should understand every sentence.

## Boundaries

- This skill reads state and presents information. It does not modify files, create artifacts, or advance playbook state.
- It does not replace the session entrypoint — it supplements it with mid-session access.
