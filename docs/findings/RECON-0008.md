---
id: RECON-0008
source: reconcile-spec
severity: major
category: defect
artifact: factory/docs/proposals/token-usage-tracking.md#capture-triggers-per-cli
status: open
traces: [ST-0039, ST-0040, ST-0041]
---

# Claude root and child records have no conservation rule

**What is wrong:** The usage contract defines inclusive-root totals and
attribution-only child records for Copilot and Codex and describes Pi's root
stream, but it does not define whether a Claude root record includes the full
normalized and provider-reported spend of `SubagentStop` records. Without that
platform-specific conservation rule, a future aggregator can either omit child
spend or double count it. Existing Claude tests prove separate records are
written, not how they compose into total spend.

**Fix:** Verify Claude Code's actual parent transcript and provider-usage
semantics for a subagent run. Document whether totals use the inclusive root or
root plus non-inclusive child records, and add a conservation test that proves
the documented aggregation rule.
