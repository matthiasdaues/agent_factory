---
title: Author and reviewer
type: concept
status: implemented
order: 20
description: Why the agent that checks a piece of work is never the agent that wrote it, and how you keep them apart.
---

# Author and reviewer

You drive Agent Factory by hand: you run a playbook yourself, one step at a time. Each step ends with defined artifacts, such as a specification, an architecture document, or a slice of code. These artifacts show that the step is done. You read them, decide whether the work is good, and start the next step. Nothing moves without you.

The most important habit the factory builds in is that the worker and the checker are never the same agent. When one agent writes a specification, a different agent reviews it. The reviewer never sees the first agent's reasoning. It sees only the finished document, the way a stranger would. That is why you do not approve your own expense report or review your own pull request: the blind spot that caused a mistake also hides it.

Most activities therefore have two agents. The author produces an artifact: a specification, an architecture document, or code. The reviewer checks it and sees only the artifact.

> Rule summary: When work moves to a different agent, the receiving agent begins in a fresh session and does not replay the prior transcript.
> Source: [agent-lifecycle-protocol.md § Session entry](../../../rulebooks/conventions/agent-lifecycle-protocol.md#session-entry)

A separate session helps the reviewer because it holds none of the author's assumptions. The reviewer meets the artifact the way its reader will. [The story workflow](../branches-and-dispatch/run-dispatch-by-hand.md) shows where the review falls in a run by hand.

[How each CLI runs an agent in its own session](../cli-integrations/separate-sessions.md) explains how each CLI opens that separate session.
