---
id: RECON-0003
source: reconcile-spec
severity: minor
category: defect
artifact: factory/rulebooks/conventions/branching-policy.md#L26
status: resolved
traces: []
---

# ST-0005's new Worktree Isolation section violates cross-reference-format.md

**What is wrong:** The new "Worktree Isolation" section (added by ST-0005, this range) reads: "See `agents/implementation-agent.md` Step 3 ("Dispatch: one feature branch per story") for the enforcing workflow step." This is a bare code span, not a markdown link — a direct violation of this repo's own MUST rule in `factory/rulebooks/conventions/cross-reference-format.md` ("Every reference from one artifact to another ... is a full markdown link ... Never a bare ID ... or a code span"). Even taken as a plain path, `agents/implementation-agent.md` is wrong from this file's location (`factory/rulebooks/conventions/`) — it would need to be `../../agents/implementation-agent.md`.

**Fix:** Replace the bare code span with a proper cross-reference-format.md-compliant link, anchored to the section: `[implementation-agent.md § Dispatch: one feature branch per story](../../agents/implementation-agent.md#3-dispatch-one-feature-branch-per-story)` (adjust the anchor slug to match the actual rendered heading id).
