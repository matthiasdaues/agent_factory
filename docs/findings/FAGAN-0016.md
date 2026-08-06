---
id: FAGAN-0016
source: fagan-review
severity: major
category: defect
artifact: factory/config/extensions/run-agent.ts:160
status: resolved
traces: [BUG-0008, UC-10, BR-040]
---

# BUG-0008 commit disclosure is not applied to non-zero-exit, no-message, or cancel paths

**What is wrong:** The BUG-0008 fix captures `headBefore = gitLocalHead(cwd)`
before every dispatch and adds `childCommitsSince(cwd, headBefore)` disclosure
in the `decoded.error` (envelope parse-failure) branch only. The adjacent
failure paths return without disclosing the child's commits:

- `childResult.status !== 0 || !parsed` (child exited non-zero or emitted no
  `message_end`) returns `errorResult` with exit code, stdout bytes, and stderr
  tail — no `freshChildCommits`.
- `childResult.cancelled` returns `cancellationResult` — no `freshChildCommits`.

A child that persists and commits canonical artifacts, then crashes, exits
non-zero, emits no `message_end`, or is cancelled, has its completed work hidden
— the exact failure mode BUG-0008 describes ("do not discard the child's
completion state … when the child persisted canonical artifacts, report them").
The fix therefore closes the parse-failure false-negative but leaves its sibling
false-negatives open; a caller can still blindly re-dispatch and duplicate
committed work, which BUG-0008 explicitly warns against. BR-040 is preserved
on these paths — genuine spawn/status failures still surface as errors — the
gap is that disclosure is not *added* there, not that it is masked.

**Fix:** In the `status !== 0 || !parsed` branch (and, optionally, the cancel
branch), call `childCommitsSince(cwd, headBefore)` and, when non-null, attach
`freshChildCommits` and the "do not blindly re-dispatch" `note` to the error
metadata, exactly as the `decoded.error` branch does. Leave the
`childResult.error` (spawn-failure) branch undisclosed — no child ran. Add
extension-level tests: child commits then exits non-zero → error discloses the
commits; child commits then emits no `message_end` → error discloses the
commits.

## Verification Evidence

- Read `factory/config/extensions/run-agent.ts` at HEAD (477518d): only the
  `decoded.error` branch calls `childCommitsSince`; the
  `status !== 0 || !parsed` and `cancelled` branches do not.
- `git show 477518d -- factory/config/extensions/run-agent.ts` confirms the
  BUG-0008 delta adds disclosure to the `decoded.error` branch only.
