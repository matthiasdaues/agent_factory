---
title: Run your first session
type: tutorial
status: implemented
order: 10
description: Set up the factory, meet VIRGIL, and run one poc-spike from start to finish.
---

# Run your first session

Try Agent Factory on a small idea and see the result run. Use a project where you can make a temporary change. You need an AI coding assistant that can edit files and run terminal commands, such as Codex or Claude Code.

## 1. Install Agent Factory

Follow the [installation instructions](../../../README.md#install). When the installer finishes, open your AI coding assistant from your project folder.

## 2. Open Project Work

Start by saying “hello” to your assistant. If it offers to configure the Factory for your project, ask to skip to the menu. You can return to setup later under **K — Housekeeping**.

When the menu appears, choose **P — Project Work**. Choose **Create something new** and then **poc-spike**. A spike is a small experiment you can run to see whether an idea works. If asked to choose a workstream, create one named “Greeting script” for the example below. A workstream gives the assistant a way to find this work again.

## 3. Run a small experiment

Use your own idea or paste this prompt:

> Create a small Python script that takes a name and prints a greeting. Run it with the name Ada and show me the output.

Read the proposed change before approving it. If the assistant proposes work beyond the experiment, ask it to keep the change small.

**Checkpoint.** You see output from a run. For the greeting script, expect something like `Hello, Ada!`. If the assistant only shows you the code, ask it to run the script and show the output.

You have completed your first session. When you have a task in mind, [choose a playbook](../playbooks/choose-a-playbook.md). If the playbook needs you to configure models, follow the [model setup instructions](../reference/model-matrix.md#modelconf).
