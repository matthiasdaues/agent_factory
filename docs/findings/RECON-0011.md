---
id: RECON-0011
source: reconcile-spec
severity: major
category: defect
artifact: orchestrator/tests/test_usage_capture_copilot_e2e.py
status: resolved
traces: [ST-0042, ADR-0007]
---

# Copilot latest-root conservation lacks repeated-turn coverage

**What is wrong:** The canonical usage contract says each Copilot `agentStop`
appends a cumulative root snapshot and total-spend aggregation must select only
the latest root for the session, never sum earlier root snapshots or child
attribution records. The Copilot installed-path suite exercises one root and one
child event, while the generic repeated-session test uses the Claude capture
path. No executable Copilot test proves the repeated-turn conservation rule
that the proposal explicitly requires. A future reader or aggregator can
therefore double count cumulative Copilot turns without breaking the suite.

**Fix:** Add an installed Copilot regression that invokes at least two
`agentStop` events with cumulative transcripts for one session, retains their
sequenced canonical records, and applies the documented aggregation fixture to
prove that only the latest root snapshot contributes to total spend. Include a
supported `subagentStop` record and prove it remains attribution-only rather
than being added to the root total.

**Resolution:** The installed-path regression now sends two sequential
`agentStop` payloads for one session through the real Copilot hook. The second
synthetic transcript retains the first turn's per-call usage and adds the
second turn, producing ordered records `-0001` and `-0002`, distinct persisted
transcripts, and cumulative provider totals of 12/4 then 30/10.

A supported `subagentStop` payload produces a separate non-null-agent
attribution record. A test-local fixture applies the deferred reader contract
to the emitted canonical records: it validates the record sequence for the
target root session, selects only `-0002`, and excludes both `-0001` and the
child for normalized and reported totals. No production reader API was added
because aggregation remains explicitly deferred by ADR-0007.
