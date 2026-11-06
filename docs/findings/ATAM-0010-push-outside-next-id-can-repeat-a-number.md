---
id: ATAM-0010
source: atam-review
severity: medium
category: defect
artifact: docs/adr/0032-agents-push-the-claim-ref-through-next-id.md#consequences
status: open
owner: architecture-agent
traces: [ADR-0032, ADR-0031, QS-18, DEC-16, DEC-22, CID-G07]
---

# A push of the counter outside `next-id` can hand out a number twice

**What is wrong:** ADR-0032 says that a push written as `git -C . push` "can leave a gap in a sequence, but no duplicate". That holds only for a push that `next-id` builds. The lease checks that the ref still holds the SHA the pusher read. It does not check what the new claim commit says.

Take an agent whose `next-id ST` failed after ten stale leases. The agent fetches `refs/ids/counters`, which holds `ST=1020`. It writes a claim commit with `ST=1012` by hand and pushes it with `git -C . push --force-with-lease=refs/ids/counters:<current sha> origin <commit>:refs/ids/counters`. The lease matches, so the remote accepts the push. The next `next-id ST` prints `ST-1013`, a number that a branch already uses. A push with plain `--force` needs no lease at all. The guardrail hook lets both pushes through (DEC-22).

So the text tells the reader that the hook gap is harmless for QS-18, when it is a path to the duplicate that QS-18 forbids. The same sentence stands in DEC-22 and in CID-G07 of `docs/spec/work/counter-ids-gaps.md`.

**Fix:** Keep the decision: the hook stays unchanged. Correct the consequence in ADR-0032 and the matching sentence in section 8.18. State that a push outside `next-id` can write any counter value, including a lower one, and then IDs repeat. State what guards the counter instead: the rule that agents claim only through `next-id`, and write access to the remote. Name T-0017 as the place where the hook gap is tracked. Tell Virgil and the requirements agent that DEC-22 and CID-G07 carry the same wrong sentence, so the stakeholder can correct the record.
