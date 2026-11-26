---
title: Choose a playbook
type: how-to
status: implemented
order: 10
description: Find the playbook that fits your situation and see which agents can run next.
---

# Choose a playbook

Pick a playbook once your first spike feels comfortable. When a smaller playbook fits your situation, it saves you the full dependency chain.

1. Find your situation in the table and note its playbook:

   | You want to                                          | Start with               |
   | ---------------------------------------------------- | ------------------------ |
   | See whether a rough idea works at all                | `poc-spike`              |
   | Check a technical risk before you commit to it       | `technical-poc`          |
   | Fix one reported bug                                 | `bug-fix`                |
   | Bring the documentation back in line with the code   | `documentation-update`   |
   | Build a new project properly, from start to finish   | `greenfield-development` |
   | Add Agent Factory to code that already exists        | `brownfield-onboarding`  |
   | Add a feature to a project that the factory manages  | `feature-addition`       |
   | Restructure code without changing its behaviour      | `refactoring`            |
   | Check an existing architecture against quality goals | `architecture-review`    |
   | Survey a topic with sourced citations                | `research-survey`        |
   | Test a specific claim by trying to refute it         | `research-topic`         |

2. Ask the assistant to start that playbook. The playbook describes a typical path through its steps.

3. At each step, run `intent select` to see which agents can run with the artifacts that exist:

   ```bash
   .agent-factory/factory/scripts/intent select
   ```

   You choose what to do next from that list.

[Kinds of playbooks](playbook-kinds.md) describes each playbook in one sentence.
