---
id: RECON-0011
source: reconcile-spec
severity: major
category: defect
artifact: orchestrator/tests/test_usage_capture_copilot_e2e.py
status: open
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
