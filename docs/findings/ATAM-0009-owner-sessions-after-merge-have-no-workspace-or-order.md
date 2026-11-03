---
id: ATAM-0009
source: atam-review
severity: medium
category: defect
artifact: docs/arc42/06_runtime_view.md#612-spec-feedback-and-wave-close
status: resolved
resolution_summary: ADR-0029, section 6.12, and the SpecFeedbackWaveClose view now run owner and reviewer sessions one at a time on the invocation branch, each committing change and status, before the next merge-story.
traces: [ADR-0029, QS-17, DEC-27, DEC-28]
---

# The owner and reviewer sessions after a merge have no defined branch and no order

**What is wrong:** Section 6.12 says that the implementation agent dispatches each row's owner after a story merges, and then the owner's reviewer. It does not say where these sessions work or whether they may run at the same time. Take wave 2 with ST-0318 and ST-0319. Both reports have an `open` row on `validation-rules.md`, owned by the domain-modeling agent. If the implementation agent dispatches the owner after each merge, two domain-modeling sessions can edit `validation-rules.md` and change rows in two reports at once. The dispatch contract forbids two concurrent assignments that can write the same artifact (`dispatch-contract.md`, lines 28 and 29). The architecture also does not say whether an owner session commits on the invocation branch in the primary checkout or in its own worktree, or whether the next story merge waits for it. A story for the implementation agent has to guess, and a wrong guess loses one of the two edits or merges a story onto a half-changed core file.

**Fix:** Keep the dispatch after each merge, as CAO-G02 decides, and state the workspace and the order in section 6.12 and ADR-0029. One rule that fits the wave model: owner and reviewer sessions run one at a time on the invocation branch, each commits its core change and its row status together, and the next `merge-story` waits until the sessions of the merged story have committed. Show the commit and the wait in the `SpecFeedbackWaveClose` view or its key points.
