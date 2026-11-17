---
title: Working Discipline
category: implementation
enforcement: none — agent and human discipline, not mechanically gate-checked
version: 1.0.0
---

# Working Discipline

The main statements of these rules are in [rules.md § Working discipline](../rules.md#working-discipline).

[factory-voice.md](factory-voice.md) sets how a text reads. This file sets how the work behind the text is done. A text can pass every writing check and still be based on a wrong premise, and these rules catch that case. They cover how an agent checks a premise, handles its own errors, and decides whether to build something.

## Check the premise before you explain

An agent gets an input it did not expect: a test passes that should fail, a file is missing, or a user's claim contradicts the code. It is easy to make up an explanation that makes the input fit. The next step then builds on that explanation, and nobody has checked it.

So the agent checks the premise first. It reads the file, runs the command, or asks the user. Then it explains.

These signs suggest that a premise is wrong:

- The result is unexpected.
- The agent needs a long justification to make the parts fit.
- The simplest explanation is "something is wrong here".
- The user's words can mean two things. The agent asks which one is meant before it offers options.

A sign is not a conclusion. When one appears, the agent stops and checks the premise before it goes on.

## Handle an error in three steps

An agent that finds an error, or is told about one, goes through three steps:

1. **Say it.** The agent states the error plainly. It does not make the error look smaller, blame the tool, or hide the error in a longer message.
2. **Find the cause.** The agent traces the cause of the error: the assumption, input, or step that produced it. "I misread the file" is a cause. "There was an error" is not.
3. **Change the process.** The agent changes the process so the same error does not happen again. The change is concrete: a check to run, a file to read first, or a question to ask.

**After two tries, change the approach.** An agent may hit the same kind of error twice, with the same or a different symptom. After the second time, the agent stops fixing the step. It reports that the approach does not work and proposes one of two paths:

- Drop the approach and use another one.
- Go back to an earlier decision. The repeated error may show that the way the problem was set up, or an assumption, is wrong, not the step itself.

The agent never hides an error. [factory-voice.md § Meaningful text](factory-voice.md#meaningful-text) sets how a report names what failed.

## Claims about tools

Tools change their flags, defaults, and output from one version to the next. What an agent knows about a tool comes from training data and may be out of date.

So a statement about how a tool, a service, or an external product behaves is either checked or marked. "Checked" means the agent ran the command or read the documentation for the installed version in this session. "Marked" means the text says the statement is unchecked and names what would check it: "I believe `uv init` creates `main.py`. Run it once to confirm."

An unchecked claim never goes into a document, a story, or a specification as a fact.

## Invented examples

Agents often make up material: Gherkin personas, test fixtures, demo data, and sample scenarios. Made-up material comes from the same statistical patterns that produce the text, so it can contradict itself without the agent noticing. A developer who moved from Pune and is named "Stefan Berger" is one such contradiction.

Before an invented example goes out, the agent checks three things:

- Names fit the backgrounds the example states.
- Dates and durations agree with each other.
- No stated fact contradicts another fact in the example or in the project's material.

An agent that finds a contradiction afterwards treats it as an error and goes through the [three steps for an error](#handle-an-error-in-three-steps).

## When a document and reality disagree

A document claims that something exists when it does not: a file, a script, a step, or a behavior. The agent can fix the conflict in two ways: build the thing, or remove the claim.

**Remove the claim first.** Removing a claim is usually less work than building what the claim describes, and it adds nothing new to maintain. Building is the exception and needs a reason.

**Name what breaks.** Before the agent builds something to match a document, it writes one sentence: "If X does not exist, Y breaks." Then it checks the sentence:

- **What is Y?** The agent names the system, process, or function.
- **How does Y break?** The agent describes what fails.
- **Can the agent check it?** "The README is inconsistent" is not a break. It is a mistake in the documentation, and the fix is in the documentation.

When the agent cannot name a concrete Y, or the only damage is a text that contradicts itself, it does not build X. It removes or corrects the claim.

**What this covers.** This rule covers claims that describe how things are. A requirement in an `accepted` proposal or a specification states how things must be. When the code does not meet an accepted requirement, the code is wrong, and the agent files a finding instead of deleting the requirement.

## Referenced from

- [rules.md § Working discipline](../rules.md#working-discipline)
- [factory-voice.md § The writer](factory-voice.md#the-writer)
- [reconciliation-agent.md § Workflow](../../agents/reconciliation-agent.md#workflow)
- [write-primer § How it should sound](../../skills/write-primer/SKILL.md#how-it-should-sound)
- [retrospective § Step 1 — Gather evidence](../../skills/retrospective/SKILL.md#step-1--gather-evidence)
