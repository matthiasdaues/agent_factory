---
id: RECON-0008
source: reconcile-spec
severity: major
category: defect
artifact: docs/proposals/implemented/token-usage-tracking.md#capture-triggers-per-cli
status: resolved
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

## Analysis

Claude Code stores the main transcript and each subagent transcript separately.
The main transcript contains the `Agent` request and returned summary but not
the child's internal message sequence. Provider usage on the main transcript's
assistant messages covers parent model calls; the child transcript carries its
own per-assistant usage. Observed result-level `toolUseResult.usage` metadata did
not equal the child's cumulative transcript usage and is not a conservation
source.

The current
[Claude hooks reference](https://code.claude.com/docs/en/hooks#subagentstop)
specifies that `SubagentStop.transcript_path` is the main transcript and
`agent_transcript_path` is the child transcript. The existing adapter used
`transcript_path` for both events, so a real child hook duplicated the parent
record and lost the child's normalized and provider usage.

The deterministic fix requires `agent_transcript_path` for `SubagentStop`, with
no fallback to the parent. Tests prove that the child transcript is persisted,
misleading result-level usage is ignored, and the conservation rule is the
latest cumulative root plus each distinct child record once.

## Resolution

The adapter now uses the nested transcript supplied by `SubagentStop` and
conserves Claude usage as the latest cumulative root plus each distinct child
record once. Automated regression tests cover the transcript boundary and the
fieldwise aggregation rule.

On 2026-07-22, a controlled Claude Code session with exactly one foreground
subagent produced one root and one child record in the same session. The child
was emitted through `SubagentStop`, the root through `Stop`, and their distinct
transcript references both resolved to persisted artifacts. Their fieldwise
sum matched the documented conservation rule. The metadata-only acceptance
record is [Claude root-and-child usage conservation smoke
test](../reviews/claude-usage-conservation-smoke-2026-07-22.md).
