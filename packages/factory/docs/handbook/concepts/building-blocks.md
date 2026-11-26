---
title: The five building blocks
type: concept
status: implemented
order: 10
description: Agents, skills, playbooks, gates, and context, and the catalogue that lists them.
---

# The five building blocks

When the assistant says "I'll use the requirements agent now", it uses one of five kinds of things that Agent Factory hands it:

| Word     | Plain meaning                                                                                                                  | Everyday comparison                                   |
| -------- | ------------------------------------------------------------------------------------------------------------------------------ | ----------------------------------------------------- |
| Agent    | One job, such as "write the requirements", "review the architecture", or "fix one bug".                                        | A specialist you hire for one task.                   |
| Skill    | One procedure an agent follows to do a job well.                                                                               | The written procedure the specialist works from.      |
| Playbook | A recipe: which agents run, in what order, for a common situation.                                                             | The plan for the whole job, from start to finish.     |
| Gate     | An automatic check that catches mistakes before you spend time reviewing them.                                                 | The quality inspector who does not let bad work pass. |
| Context  | A small set of files where your project declares its stack, its workflow, and its rules. Agents read them instead of guessing. | The project fact sheet on the wall.                   |

You do not learn the full list by heart. The assistant reads the catalogue [`INDEX.yaml`](../../../INDEX.yaml) and picks the agent or skill that fits your request. You only need to know that these things exist, so you understand what the assistant does.

`INDEX.yaml` is useful to you too. It lists every agent, skill, and playbook with a one-line description and its token count. So you can see what is available and estimate how many tokens a playbook run consumes.

The other concept pages of this chapter explain [agents](agents.md), [skills](skills.md), [proposals](proposals.md), and [rulebooks](rulebooks.md). [Playbooks](../playbooks/index.md) and [gates](../quality-and-review/gates.md) have their own chapters, and so does the [agent context](../agent-context/index.md).
