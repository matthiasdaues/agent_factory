---
id: FAGAN-0003
source: fagan-review
severity: major
category: defect
artifact: factory/scripts/usage-capture:965
status: open
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
