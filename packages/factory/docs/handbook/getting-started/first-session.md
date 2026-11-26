---
title: Run your first session
type: tutorial
status: implemented
order: 10
description: Set up the factory, meet VIRGIL, and run one poc-spike from start to finish.
---

# Run your first session

This tutorial takes you through your first session with Agent Factory. You need an idea for something to build and an AI coding assistant, a tool such as Claude Code or GitHub Copilot CLI that reads and writes files and runs commands in a terminal. You do not need to be a professional software engineer. You need to read what the assistant proposes and say yes or no to each step.

Agent Factory gives the assistant a way of working that produces code you can trust in production. The assistant does the work, and you approve each step. The factory never builds the whole thing while you look away. It works in small, visible moves and stops to show you each one. When a move looks wrong, you say so, and the assistant tries again. An AI works fast but makes mistakes, so frequent and cheap checks catch them: a tool, a test, or you.

## Step 1: Set up the factory

Follow [`.agent-factory/factory/README.md`](../../../README.md) once. It lists the tools you need and the one script that wires everything up.

**Checkpoint:** the script finished without an error. [Files that init-factory creates](../reference/local-configuration.md) lists what it put on your disk. You do not need to touch these files now.

## Step 2: Say hello

Open your AI assistant in your project folder and say hello. The assistant may first summarize what `init-factory` found and offer to walk you through the fitting, which tunes the factory to your project. Answer that you want to skip to the menu. You can run the fitting later from K — Housekeeping.

The menu shows four options:

- **H — Help: I'm new here or need orientation.** The assistant walks you through the basics, section by section, and answers your questions.
- **K — Housekeeping: project setup and maintenance.** Check the factory state, fit the project again, update the factory, or refresh the agent context.
- **P — Project Work: start or continue a workstream.** A menu of situations opens: spike, new project, feature, bug fix, or research. The assistant picks the playbook for it, or continues where you left off.
- **O — Open Stage: let's just talk.** An open conversation with no structure and no artifacts, until the idea finds its shape.

The voice behind the menu is VIRGIL. Once you choose a direction, VIRGIL hands you to the right playbook or stays with you for an open conversation. [Agents](../concepts/agents.md) explains who VIRGIL is.

**Checkpoint:** you see the four options. If you worked in this project before, the assistant names the signs of earlier work it found, such as a finished spike, a charter, or earlier playbook outputs, and offers to skip ahead.

## Step 3: Run a poc-spike

Ask the assistant to run `poc-spike`. This playbook has no specification, no architecture, and no formal checks. It turns one idea into one small thing you can run, in minutes. You watch the assistant work before you commit to anything real, and what you throw away costs almost nothing.

Watch the loop:

1. The assistant reads the playbook and tells you the steps it plans.
2. It writes a small amount of code and shows it to you.
3. It runs the code, and you see the result.
4. You react: "Yes, keep going," or "No, that is not what I meant."

This loop is how Agent Factory works. Larger work runs the same loop with more checks.

**Checkpoint:** you have run the spike and seen its result. At any point you can ask the assistant "where am I?" or "what do I do next?", and it shows you where you are.

## Step 4: Keep three habits

1. **Read before you approve.** The assistant always shows you its move. Read it. Your "yes" is the last check, and it matters most.
2. **Let the gates do their job.** A check that blocks a commit or a failing test is the system working: it found a mistake while the mistake is still cheap to fix.
3. **Take one small step at a time.** Ask for one small step, not the whole thing at once. Small, checked steps correct mistakes before they add up, and they avoid a day-long detour.

> Rule summary: **MUST NOT** bypass a failing pre-commit hook (`--no-verify`, `core.hooksPath`); fix the hook.
> Source: [rules.md § Git workflow](../../../rulebooks/rules.md#git-workflow)

## Step 5: Get ready for your first real playbook

After a spike or two, you can run a full playbook: `greenfield-development`, `brownfield-onboarding`, or `feature-addition`. [Choose a playbook](../playbooks/choose-a-playbook.md) helps you pick. Three things appear in such a run, and each has its own page:

- **Agent context.** The first real playbook run asks you to set up `docs/agent-context.md`. The assistant interviews you, and you confirm or correct each concern. [What the agent context does](../agent-context/what-agent-context-does.md) explains the file.
- **The model matrix.** `.agent-factory/config/model.conf` maps the tiers economy, standard, and strong to AI models, one set per CLI. The fitting walk-through configures it. If you skipped the fitting, the installer wrote a `CONFIGURE-ME` row for each tier of each selected CLI that routes models. OpenCode gets no rows. Before model-routed work, fix each `CONFIGURE-ME` row in one of two ways. Replace it with a model ID your account can access. Or delete the row of a tier that should use the CLI's own default, and set `on_missing = auto`. That setting applies to every tier and CLI without a row, not only to the tier you deleted. A matrix with no model rows left fails `matrix-lint` with `MX-EMPTY`. A row left as `CONFIGURE-ME` is sent to the CLI as a model name. [Model matrix](../reference/model-matrix.md) describes both settings and the error.
- **The dependency chain.** A full playbook runs through five kinds of work, each with its own agent. Run `intent select` to see which agents can run with the artifacts that exist. [Five kinds of work](../concepts/kinds-of-work.md) explains the chain.

**Checkpoint:** you know where these three pages are. You need nothing else to start. Run one `poc-spike`, watch the loop, and come back to the rest of the handbook when you need it.
