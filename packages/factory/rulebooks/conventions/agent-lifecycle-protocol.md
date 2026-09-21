# Agent Lifecycle Protocol

Three mandatory boundaries every phase agent observes.

## Phase entry

When a playbook crosses a phase boundary, the receiving phase agent begins in
a fresh session. Direct interactive selection from the session menu may adopt
the role in the current session unless that session contains work from which
the selected agent must remain independent. Read the handoff first and verify
its Git claims. Read referenced artifacts through initial bounded chunks,
expanding further only on demand for the current task. Do not replay the prior
transcript. Use no in-place transcript compaction and no prose-only
cache-restabilisation turn.

## Child return

When this agent runs as a child, persist its complete result in canonical
tracked artifacts before returning. The parent-facing envelope contains only
disposition, severity counts, and every artifact path. Include a
one-to-three-sentence next action. Do not include verbatim finding detail or
full reasoning.

## Phase exit

If the next action crosses a workflow phase boundary, invoke `handoff`. Require
a clean `handoff-lint` result and independent semantic review, then stop the
outgoing session without entering the next phase. Work remaining in the same
phase is exempt and may continue in the current session.
