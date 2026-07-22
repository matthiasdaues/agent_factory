---
id: FAGAN-0003
source: fagan-review
severity: major
category: defect
artifact: factory/scripts/usage-capture:965
status: resolved
traces: [ST-0036, ST-0038, ST-0042, ST-0043]
---

# Concurrent captures can reuse a record ID and overwrite transcript evidence

**What is wrong:** `_next_record_id()` counts existing lines before the record
append. Two capture processes for the same session can read the same count and
both allocate, for example, `session-0001`. Atomic `O_APPEND` preserves both
record lines, but both records reference the same transcript path and the
second `write_text()` overwrites the first transcript. The existing concurrency
test supplies already-distinct IDs, and the sequencing test invokes processes
serially, so neither exercises allocation under concurrency. This violates the
unique-record and durable audit-link contracts.

**Fix:** Make record-ID allocation inter-process safe, using a lock-protected
counter, an atomic allocation primitive, or collision-resistant IDs. Create
transcript files exclusively so an allocation collision cannot overwrite
evidence. Add a synchronized multi-process regression for two same-session
captures that asserts distinct record IDs, distinct transcript references, and
the correct content in both transcript files.

**Resolution:** Record-ID allocation and transcript creation are now one
lock-free `UsageStoragePaths.reserve_transcript()` operation. It estimates the
next sequence from existing records and probes monotonically with
`O_CREAT | O_EXCL | O_NOFOLLOW`; concurrent processes can share an estimate,
but only one owns each evidence path. Normal failures remove only their own
reservation. A crash may leave an empty, unreferenced reservation, which later
allocators skip as a valid sequence gap. Numeric reservation sequence—not JSONL
append order—defines snapshot order.

A synchronized 12-process regression releases real `usage-capture` processes
against one session and verifies unique IDs, unique references, and the matching
distinct content behind every reference. A separate orphan-reservation test
proves crash gaps do not block later capture.
