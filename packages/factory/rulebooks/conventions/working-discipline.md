---
title: Working Discipline
category: implementation
enforcement: none — agent and human discipline, not mechanically gate-checked
version: 1.0.0
---

# Working Discipline

Canonical statements: [rules.md § Working discipline](../rules.md#working-discipline).

The [factory voice](factory-voice.md) sets how a text reads. This convention sets how the work behind the text is done: how an agent handles its own errors, checks a premise, and decides whether to build something. A text can pass every voice gate and still rest on a wrong premise. These rules catch that case.

## Check the premise before the explanation

An agent meets an unexpected input: a test passes that should fail, a file is missing, or a user's claim contradicts the code. The quick move is to build an explanation that makes the input fit. The explanation then becomes the foundation for the next step, and nobody has checked it.

So the agent checks the premise first. It reads the file, runs the command, or asks the user. Only then does it explain.

Some signs that a premise is wrong:

- The result is unexpected.
- The agent needs a long justification to make the parts fit.
- The simplest explanation is "something is wrong here".

Each sign is a reason to stop and check, not a conclusion. When a sign appears, the agent investigates before it goes on.

## Admit, analyse, adapt

Errors happen. An agent that finds one, or is told about one, works through three steps:

1. **Admit.** The agent states the error plainly. It does not shrink the error, blame the tool, or bury the error in a longer message.
2. **Analyse.** The agent traces how the error came about: which assumption, input, or step produced it. "I misread the file" is a cause. "There was an error" is not.
3. **Adapt.** The agent changes the process so the same error does not happen again. The change is concrete: a check to run, a file to read first, or a question to ask.

**Two attempts, then change course.** An agent may hit the same class of error twice. The class is what matters, not the exact symptom. After the second time, the agent stops repairing the step. It reports that the approach does not work and proposes one of two paths:

- Drop the approach and take another one.
- Go back to an earlier decision. The repeated error may show that the framing or an assumption is wrong, not the step itself.

The agent never hides an error. A status report, a handoff, or a commit message names what failed and what was skipped, in the same plain words as what succeeded.

## Claims about tools

Tools change their flags, defaults, and output from one version to the next. An agent's knowledge of a tool comes from training data and may be out of date.

So a statement about how a tool, a service, or an external product behaves is either checked or marked. "Checked" means the agent ran the command or read the documentation for the installed version in this session. "Marked" means the text says the statement is unchecked and names what would check it: "I believe `uv init` creates `main.py`. Run it once to confirm."

An unchecked claim never goes into a document, a story, or a specification as fact.

## Invented examples

Agents invent material all the time: Gherkin personas, test fixtures, demo data, and sample scenarios. Invented material comes from the same statistical habits that produce the text, so it can contradict itself without the agent noticing. A developer who moved from Pune and is named "Stefan Berger" is one such contradiction.

Before an invented example goes out, the agent checks three things:

- Names fit the backgrounds the example states.
- Dates and durations agree with each other.
- No stated fact contradicts another fact in the example or in the project's material.

An agent that finds a contradiction afterwards treats it as an error and works through admit, analyse, adapt.

## When a document and reality disagree

A document claims something that does not exist: a file, a script, a step, or a behavior. There are two ways to resolve the conflict. The agent can create the thing, or it can remove the claim.

**Remove the claim first.** Removing a claim is usually smaller than building what the claim describes, and it adds no new surface to maintain. Building is the exception and needs a reason.

**The Breakage Test.** Before the agent creates something to match a document, it states one sentence: "If X does not exist, Y breaks." Then it checks the sentence:

- **What is Y?** The agent names the system, process, or function.
- **How does Y break?** The agent describes what fails.
- **Can the agent check it?** "The README is inconsistent" is not a break. It is a documentation error, and the fix is in the documentation.

When the agent cannot name a concrete Y, or the only damage is an inconsistent text, it does not create X. It removes or corrects the claim.

**Scope.** This rule covers descriptive claims: statements about how things are. A requirement in an `accepted` proposal or a specification describes how things must become. When the code lacks an accepted requirement, the code is wrong, and the agent files a finding instead of deleting the requirement.

## Referenced from

- [rules.md § Working discipline](../rules.md#working-discipline)
- [factory-voice.md § The speaker](factory-voice.md#the-speaker)
- [reconciliation-agent.md § Workflow](../../agents/reconciliation-agent.md#workflow)
- [retrospective § Step 1 — Gather evidence](../../skills/retrospective/SKILL.md#step-1--gather-evidence)
