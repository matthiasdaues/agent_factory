---
name: handoff
description: Create and validate a dense phase-boundary restart contract before ending the outgoing session.
category: utility
---

# Handoff

Create one CLI-neutral phase handoff when the next action crosses a Factory
phase boundary. Work that remains in the same phase is exempt. This skill ends
the outgoing phase; it never performs in-place transcript compaction and never
starts the incoming phase.

Read [handoff-format.md](../../rulebooks/conventions/handoff-format.md) before
writing the handoff.

## 1. Confirm the boundary

Identify the outgoing and incoming phases. If the next work stays within the
same phase, stop this skill and continue the current session. Otherwise, the
handoff, independent semantic review, hard stop, and fresh-session restart are
mandatory.

## 2. Gather durable evidence

Read Git directly for the checkout, branch, exact lowercase 40-character HEAD
SHA, configured upstream and exact upstream SHA (or `none`), ahead/behind
counts, working-tree paths, and intentionally retained worktrees or branches.
Gather every artifact path, decision and its origin, open item, gate result,
verification result, and the one next action. Do not infer Git state from prior
prose or omit a zero/none result.

## 3. Write the restart contract

Write the exact required headings and fields from `handoff-format.md`. Use dense,
unambiguous prose: compression removes wording, never decisions, open items,
artifact paths, branch/upstream state, gate or verification evidence, the next
action, or any exact 40-character SHA. Do not replay the transcript or copy
historical narration that does not constrain the incoming phase.

The next action tells a fresh session to read the handoff first, verify Git
state, then read only the named artifacts in bounded chunks.

## 4. Validate structure

Run:

```bash
factory/scripts/handoff-lint <handoff-path> --repo-root <repository-root>
```

If any structural finding is reported, correct every finding and rerun the
command. A clean result establishes only mechanically observable structure,
field syntax, repository state, and referenced-path existence. It does not
establish semantic completeness or losslessness.

## 5. Require semantic review

Give the lint-clean handoff and all outgoing durable evidence to a designated
independent semantic reviewer. The reviewer compares decisions, open items,
artifact paths, branch/upstream facts, gate results, verification evidence, and
next action for omission or distortion. Record the reviewer and status in the
handoff. A failed or pending review blocks closure; after a correction, repeat
both `handoff-lint` and semantic review.

## 6. Stop at the boundary

After structural lint and semantic review pass, report the handoff path and
stop the outgoing session. Do not enter the next phase. The incoming participant
must use a fresh session and begin from the handoff and canonical artifacts,
not from the prior transcript.
