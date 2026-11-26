---
title: How the Factory works
type: concept
status: implemented
order: 5
description: Follow a feature from the first request through decisions, checks, and a merge.
---

# How the Factory works

Agent Factory gives your AI coding assistant a way to carry work through a Git repository. It supplies instructions for common tasks and commands that check and coordinate the work. You bring the goal and make decisions about what to build and what to accept.

Suppose you maintain an invoicing application. Someone asks for a CSV export of the invoices on screen. You open your coding assistant in the project and ask for the export. There is a decision to make before anyone writes code. Does “on screen” mean the current page, or every invoice that matches the filters? Both are plausible. The answer changes which rows the customer receives.

## The first conversation

In a Factory session, VIRGIL is the guide who helps you find a starting point. In this case you can choose **Project Work** and ask to add a feature. The Factory uses a **playbook**, a workflow for a recurring situation. The feature-addition playbook starts by turning your request into a proposal someone can decide on.

The Factory gives different parts of the work to **agents**. An agent is a role with instructions for a job, such as writing requirements or reviewing code. A **skill** gives the agent a procedure it can follow for a task. A **rulebook** tells it which shared rules apply. The proposal, and later the tests and review reports, are **artifacts**. They give each participant something concrete to read, check, or change.

```text
Playbook --guides--> Agent --produces--> Artifact
                       |                    |
                       | follows            +--> Gate checks rules
                       v                    +--> Reviewer reads for meaning
                     Skill
```

If a teammate wants to see the Factory in action before committing to this feature, they can try a [first session](../getting-started/first-session.md). The small experiment in that tutorial has a result they can run and inspect.

## What setup gives the assistant

Installation wires the Factory into the coding CLIs you select. When you open a CLI in the project, its project instructions tell it where to find the installed Factory. The generated `INDEX.yaml` is a catalog of its agents, skills, playbooks, and rulebooks.

During [fitting](../getting-started/fitting.md), the Factory helps you connect its tools to the way your project already works. For the invoicing application, [agent context](../agent-context/what-agent-context-does.md) can point an agent to the team's billing conventions and test guidance. The test configuration tells the Factory which commands to run. The model matrix maps roles' model tiers to models, and hook settings determine which checks run at events such as a commit. The [installation and update guides](../installation-and-updates/index.md) cover those choices in detail.

## The phase chain

The invoicing example follows this path when the proposal calls for both specification and design work. A finding can send work back to the owner of an earlier decision.

```text
Proposal -> Specification -> Design -> Stories -> Code and tests
                ^               ^                       |
                |               |                       v
                +---------------+ <-- findings -- Review, QA, reconciliation
```

### Agree on the behavior

You decide the CSV should include every matching invoice, regardless of pagination. The proposal records that decision. If the change needs new acceptance criteria, the requirements agent can turn it into a scenario. For example, a filter finds 25 invoices, the screen shows 20, and the export contains all 25.

A [gate](../quality-and-review/gates.md) is a script that checks defined rules. At specification review, `spec-lint` checks the structure of the specification. A reviewer in a separate session can ask whether the examples distinguish a filtered export from an export of all invoices. A file can pass the script and still leave that behavioral question open. A [review finding](author-and-reviewer.md) gives the author a specific issue to resolve.

### Decide how to build it

The next question is where the export gets its data. The feature might use the existing invoice query with pagination turned off. If the proposal calls for an architecture change, the design work records the choice and the reviewer checks it against the project's quality goals. For this example, a concern might be what happens when a filter matches thousands of invoices. An explanation of that choice gives the planner a boundary for the work.

The planner turns the agreed behavior and applicable design into backlog stories. Each story gives a developer a result to deliver, the dependencies it relies on, and checks for success. You review the backlog before implementation. The story for filtered export now has a specific expectation the developer can test.

### Build, check, and merge

The implementation agent coordinates the stories. A developer writes a test for the export, implements the change, and runs the relevant checks. [Dispatch](../branches-and-dispatch/dispatch-runs.md) manages story branches and merges. Which gates apply depends on the story and project configuration. People can drive the work one story at a time, or an orchestrated run can coordinate independent stories. [Follow the implementation run](../quality-and-review/implementation-run.md) to see how test-first development, independent review, and gates check each story before merge.

Once the stories are together, code review and QA examine the combined feature. Suppose QA discovers that the CSV contains totals in the application's default currency, even when the invoices use different currencies. The team looks at the agreed behavior. If the specification already requires preserving invoice currency, the finding calls for a code fix. If the decision was never made, the owner needs to settle it with you. The finding helps route the work, and the checks run again after the fix.

After the feature passes its pre-merge checks, the stakeholder merges it into `dev`. Reconciliation then compares the merged code with the specification and architecture. If a document drifted, its owner brings it into line. If the code violates an agreed requirement, the issue belongs with the developer. This is how evidence from building and testing can correct decisions or documents written earlier.

## How work picks up again

You might close your session after the specification review. When you return, select the existing **workstream**, the Factory's record of which piece of work the session belongs to. The proposal, specification, and findings supply the details the next session needs. A finding about the export belongs with that work even after the original chat has closed.

The Factory's eligibility command, `intent select`, checks which agents have the required inputs in the repository. It can show why an agent is ready or what is missing. Look at the open finding and the playbook's decision points before starting the next step. In this example, the unresolved question about filtered invoices tells you where to resume.

## Key ideas

The review illustrates how three parts work together. The CLI loads the instructions and gives an agent access to tools. The agent interprets the task and produces or reviews an artifact. Executable commands check rules, report readiness, or coordinate actions such as a merge. Each handover leaves a result the next person or agent can inspect. Keeping the steps small makes it easier to see which decision needs attention when something changes.

A feature can also involve several CLI sessions. [Usage capture](../usage-capture/usage-capture.md) records token counts from supported CLI events under `.agent-factory/usage/`. The optional usage add-on reads those records and applies each CLI's accounting rule. Some root totals already include child sessions. Other totals need the child records added. [Transcript retention](../usage-capture/configure-transcript-retention.md) controls whether capture keeps the transcript text alongside the counts.

A small bug fix can follow a shorter path than this export, and research has its own outputs and checks. [Choose a playbook](../playbooks/choose-a-playbook.md) maps those situations to their workflows. If you are adapting the Factory for one project, start with [agent context](../agent-context/index.md) and the project's test configuration. When you update the installation, follow the [update guide](../installation-and-updates/update-the-factory.md) to handle any local changes the updater reports.
