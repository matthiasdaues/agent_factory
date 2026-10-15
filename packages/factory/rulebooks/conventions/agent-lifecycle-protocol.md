# Agent Lifecycle Protocol

Three mandatory boundaries every agent observes.

## Session entry

When work moves to a different agent, the receiving agent begins in a fresh
session. Direct interactive selection from the session menu may adopt the role
in the current session unless that session contains work from which the
selected agent must remain independent. Read the handoff first and verify its
Git claims. Read referenced artifacts through initial bounded chunks, expanding
further only on demand for the current task. Do not replay the prior
transcript. Use no in-place transcript compaction and no prose-only
cache-restabilisation turn.

## Child return

When this agent runs as a child, persist its complete result in canonical
tracked artifacts before returning. The parent-facing envelope contains only
disposition, severity counts, and every artifact path. Include a
one-to-three-sentence next action. Do not include verbatim finding detail or
full reasoning.

## Session exit

If the next action will be performed by a different agent, invoke `handoff`.
Require a clean `handoff-lint` result and independent semantic review, then
stop the outgoing session without starting the incoming agent's work. Work
that continues within the same agent's session is exempt and needs no handoff.
