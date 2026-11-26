---
title: Decide where your change belongs
type: concept
status: implemented
order: 5
description: Decide whether to configure your project, write an extension, or contribute to the Factory.
---

# Decide where your change belongs

Suppose your team wants billing changes reviewed for currency handling. Last week a CSV export labeled a EUR invoice as USD. This week you want the reviewer to catch the same mistake before merge.

Start with the rule your team already follows. Write it in your project guidance and link to it from `docs/agent-context.md`. The agent context tells the assistant where to read the policy. It gives the policy a route into a review that already exists.

If reviewers need a repeatable procedure, write a **skill** that says what evidence to inspect and what result to report. If you need a separate reviewer with a distinct responsibility, give that job to an **agent**. If your team needs to coordinate the review with other steps and a release decision, put that sequence in a **playbook**.

Some parts of the review can be expressed as rules that code can check. A fixture with an invoice in EUR and a CSV row labeled USD gives you a concrete test. Put the test with the project code. A **gate** can run a defined check on demand, and a **hook** can call a command when a specific event occurs. The reviewer can still assess questions that rely on interpretation, such as whether a report makes its currency clear to the reader.

## Choose who will maintain it

| Who needs the change?           | Where should it live?                                                                                     |
| ------------------------------- | --------------------------------------------------------------------------------------------------------- |
| You, while you try an idea      | Keep a working copy you can revise and install into a disposable project.                                 |
| Everyone working in one project | Keep the maintained copy in that project's Git repository. Document how teammates install or invoke it.   |
| Factory users across projects   | Keep the proposed change in a Factory source checkout and bring a representative case to upstream review. |

The billing rule stays with the team that owns it. If several projects need the same way to register a review procedure or route its results, that mechanism is a candidate for upstream. Try it with one project first so you can show where the current workflow needs help.

Continue with [Add a project playbook](add-a-project-playbook.md) or [Bring a change upstream](bring-a-change-upstream.md).
