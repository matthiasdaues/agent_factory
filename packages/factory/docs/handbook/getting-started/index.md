---
title: Getting started
type: concept
status: implemented
order: 10
description: Install the factory, run a first session, and get ready for a first playbook.
---

# Getting started

Start in a project where you can make a temporary change. By the end of your first session, you should have seen the assistant propose a change, run it, and show you the result.

## Before you open the assistant

You need Git, Python 3.10 or later, `uv`, and a [supported AI coding CLI](../cli-integrations/index.md). Follow the [installation instructions](../../../README.md#install) and select the CLI you plan to use. If your repository already has pre-commit hooks, see [Install into an existing repository](../installation-and-updates/existing-repository.md).

Open the CLI from your project folder. If VIRGIL, the Factory's session guide, offers to fit the project, you can do that now or skip to the menu for the tutorial. [Fitting](fitting.md) connects the Factory to your project's models, tests, and guidance. You can return to it through **K — Housekeeping**.

```text
Install Factory -> Open CLI in project -> VIRGIL
                                            |
                                 If fitting is offered
                                            |
                    +-----------------------+-------------------+
                    v                                           v
              Fit the project                              Skip for now
                    |                                           |
                    +----------------------> Menu <-------------+
                                               |
                                               v
                                    Project Work -> Spike
```

## Try one small task

In **P — Project Work**, a spike lets you try an idea and see it run. The tutorial gives you a sample prompt, shows which menu choices to make, and tells you what output to expect.

<!-- handbook-index:start -->

## Tutorials

- [Run your first session](first-session.md): Set up the factory, meet VIRGIL, and run one poc-spike from start to finish.

## Concepts

- [Fit the Factory to your project](fitting.md): See what discovery finds, what you confirm, and how the project gets its own configuration and gates.

<!-- handbook-index:end -->

## After your first session

If you want to understand what happened, read [How the Factory works](../concepts/how-the-factory-works.md). It follows a feature through the decisions, checks, and review you would meet on a larger task.

If you already have work in mind, [choose a playbook](../playbooks/choose-a-playbook.md) for it. Before work that needs model routing, check the [model matrix](../reference/model-matrix.md). When a larger run needs to discover your project conventions, [set up agent context](../agent-context/set-up-and-keep-current.md).

If you cannot reach the menu or finish setup, find the error or symptom in [Fix a known setup failure](../troubleshooting/fix-setup-failures.md).
