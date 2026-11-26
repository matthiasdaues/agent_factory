---
title: Author and reviewer
type: concept
status: implemented
order: 20
description: Why the agent that checks a piece of work is never the agent that wrote it, and how you keep them apart.
---

# Author and reviewer

You drive Agent Factory by hand: you run a playbook yourself, one step at a time. Each step ends with defined artifacts, such as a specification, an architecture document, or a slice of code. These artifacts show that the step is done. You read them, decide whether the work is good, and start the next step. Nothing moves without you.

The most important habit the factory builds in is that the worker and the checker are never the same agent. When one agent writes a specification, a different agent reviews it, in a fresh session. The reviewer never sees the first agent's reasoning. It sees only the finished document, the way a stranger would. That is why you do not approve your own expense report or review your own pull request: the blind spot that caused a mistake also hides it.

Most activities therefore have two agents. The author produces an artifact: a specification, an architecture document, or code. The reviewer checks it in a separate session and sees only the artifact.

You keep the two apart. When the requirements, architecture, or developer agent hands you its artifacts, you open a second, clean session and start the matching reviewer there. You point the reviewer at those artifacts and nothing else. The blank session is the separation, because the reviewer cannot lean on a conversation it never had. So every step runs as author, then a fresh session, then reviewer.

[How each CLI runs an agent in its own session](../cli-integrations/separate-sessions.md) explains how each CLI opens that separate session.
