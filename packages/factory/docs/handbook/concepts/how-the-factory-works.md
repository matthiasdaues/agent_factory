---
title: How the factory works
type: concept
status: implemented
order: 5
description: The chain of agents from an idea to checked code, and the four ideas the factory is built on.
---

# How the factory works

Agent Factory drives an AI coding assistant from an idea to code you can trust in production. The work runs through a chain of agents, and four ideas hold the chain together.

## The phase chain

The work runs through five kinds of work, from idea to code:

1. **Requirements.** An interview, a product requirements document (PRD), Cockburn use cases, a feature file in Gherkin, and the specifications around it.
2. **Architecture.** arc42 documentation, a Structurizr C4 model, architecture decision records, and an ATAM review.
3. **Planning.** A backlog of INVEST stories with MoSCoW priorities and dependency links.
4. **Implementation.** Test-driven development per story, with feedback to the specification and a reconciliation of the specification against the code.
5. **Quality.** A Fagan inspection, an OWASP security review, and an exploratory bug hunt.

Each kind of work has an author agent and a reviewer agent. The author writes an artifact. The reviewer checks it in a separate session until the review finds nothing that blocks. It is the same principle as not reviewing your own pull request. [Author and reviewer](author-and-reviewer.md) explains why.

```
requirements ↔ spec-review → architecture ↔ architecture-review → planning → implementation → reconciliation ↔ qa
```

Not every task needs the whole chain. [Kinds of playbooks](../playbooks/playbook-kinds.md) describes the shorter paths.

Research runs beside the chain, not as a step in it. The `research-topic` playbook takes an approved brief to a checked report, with its own agents and its own validation. A claim reaches the report only after it survives a serious attempt to refute it. [Survey research and falsification research](../research/survey-and-falsification.md) describes the workflow.

The factory itself keeps the chain in order, so the order does not depend on each agent's discipline. Three parts of `.agent-factory/factory/` enforce it. The state-machine harness lets a phase start only after the phase before it has finished. The `dispatch` script prepares, checks, and merges each story branch, as [Dispatch runs](../branches-and-dispatch/dispatch-runs.md) shows. The generated catalog, `INDEX.yaml`, lists every agent, skill, playbook, and rulebook, so each session finds the right one by name. The harness also caps the review loops. When one activity needs too many rounds of review and fix, the run stops and hands the decision to you. [Halt conditions](../../../playbooks/greenfield-development.md#halt-conditions) names the cap.

## Key ideas

- **Semantic anchors.** Well-known engineering methods steer the assistant, such as Cockburn use cases, EARS, ATAM, Fagan inspection, and TDD. The factory builds on [Semantic Anchors — Spec Driven Development](https://llm-coding.github.io/Semantic-Anchors/spec-driven-development) by Ralf D. Müller, adapted for [arc42](https://arc42.org/) and the [Structurizr](https://structurizr.com/) DSL.
- **Deterministic gates.** A script catches a provable defect before an agent spends judgement on it. A gate is cheap, gives the same result every time, and reports no false positives. [Gates](../quality-and-review/gates.md) explains them.
- **Session isolation.** Each agent runs in its own session. A reviewer never sees the author's reasoning, only the artifact.
- **Eichhorst's Principle.** An LLM is a noisy channel. Short transmissions with error correction, such as a compiler, tests, and a review, work better than one long prompt nobody checks. Each skill is one short transmission.
