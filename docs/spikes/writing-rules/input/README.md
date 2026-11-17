# Input for the writing-rules spike

Frozen on 2026-11-17. Source session: `9f81748e` (Claude Code), read from `~/.claude/projects/`.

The input holds only what led to the frozen state of the proposal. The thread starts at 2026-11-15T20:04Z, when the session moved from `story-workflow.md` upstream to the dispatch process. It ends at the last write to the proposal, 2026-11-17T19:13:42Z.

- `proposal-working-copy.md`: `docs/proposals/run-lifecycle.md` after that last write (uncommitted). This is the version under test.
- `proposal-opened-bb717678.md`: the same proposal at commit `bb717678` (`status: open`), for reference.
- `conversation-run-lifecycle.md`: user and assistant text in the window. Tool calls, tool output, and the compaction summary of 2026-11-16T22:07Z are left out.
- `handoff-run-lifecycle-decisions-2026-11-16.md`: the handoff the session resumed from.
- `subagent-inventory-dispatch-process.md`: the inventory report of 2026-11-15T20:09Z. The proposal's facts about the current dispatch process come from it.
- `subagent-proposal-review.md`: the proposal review of 2026-11-16. Its findings drove the edits of 2026-11-17.

Left out on purpose: the primer agent's output and the lector's edits. They are writing, and the spike tests writing.
Lost: the grilling scratchpad of 2026-11-15. It was cleared from disk. Its decisions also appear in the conversation.
