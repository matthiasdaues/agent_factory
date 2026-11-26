---
title: Agents
type: concept
status: implemented
order: 40
description: What an agent is, which utility agents support the work, and how they lead from an idea to a feature.
---

# Agents

An agent is one job, such as "write the requirements", "review the architecture", or "implement one story". Each agent is one Markdown file in `.agent-factory/factory/agents/`. Your AI CLI reads it at the start of a session.

The delivery agents come in [author and reviewer](author-and-reviewer.md) pairs. Besides them, several utility agents support the work without belonging to one activity:

- **VIRGIL** greets you in [your first session](../getting-started/first-session.md), and every factory session starts with it. It is the guide you meet before the work has a definite shape. The letters stand for *Versatile Interactive Resource: Guide, Instructor, Liaison*, and the name points to Virgil, who guided Dante through Hell and up the mountain of Purgatory. VIRGIL helps an idea find its shape and then hands you to the right playbook. It also sets up the [agent context](../agent-context/what-agent-context-does.md) `docs/agent-context.md` with the `capture-context` skill.
- **coaching-agent** runs retrospectives, extracts action items, and tracks process improvements across sessions.
- **proposal-review-agent** reviews a feature proposal for clarity, feasibility, and readiness for planning. It advises on a draft and attacks an open proposal.

Together these agents lead from an idea to a delivered feature. In a typical flow, VIRGIL explores an idea. The `draft-proposal` skill turns it into a [proposal](proposals.md). The proposal-review-agent tests the proposal under pressure. Then the `feature-addition` playbook delivers the feature through the dependency chain.

The full list is in [`.agent-factory/factory/INDEX.yaml`](../../../INDEX.yaml). Each entry has two token counts, which help you plan the space an agent takes in the context window:

- `tokens` counts the agent's prompt text with the tiktoken `cl100k_base` tokenizer.
- `total_tokens` adds the skills and rulebooks that the agent references.
