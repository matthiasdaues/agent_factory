---
id: FAGAN-0049
status: open
severity: minor
category: contract
artifact: orchestrator/src/orchestrator/phase_runner.py
pass: 3-review
---

# Resume from REVIEWING can still duplicate findings in the pre-ingest crash window

Follow-up to \[[FAGAN-0043]\] (resolved). The 0043 fix closes the common case: on resume it skips re-invoking the reviewer when `open_count(phase, iteration + 1) > 0`. But the `open_count == 0` window remains open. If the reviewer files its `docs/findings/*.md` and the process is killed before `ingest_open_findings` runs, resume re-invokes the reviewer; a non-idempotent reviewer files new tags rather than overwriting, and the subsequent ingest reads both sets, yielding duplicated semantic findings. A secondary variant: a crash mid-ingest leaves a partial set, the resume skip fires, and the un-ingested findings are silently lost.

Root cause: the fix relies on reviewer-file idempotency and store-level de-duplication that the code does not provide.

**Suggested fix**: make ingestion idempotent — key stored findings by content (code/artifact/message) and dedup on ingest, and/or clear or mark the filed `docs/findings/*.md` after a successful ingest so a re-invoked reviewer cannot double-file.

Severity is minor: the trigger is a narrow crash window combined with non-idempotent reviewer file naming, and the 0043 fix is already a strict improvement over the pre-fix behaviour, which duplicated on every resume.
