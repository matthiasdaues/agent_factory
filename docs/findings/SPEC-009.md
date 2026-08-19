---
id: SPEC-009
source: spec-review
severity: major
category: defect
artifact: docs/proposals/mechanize-dispatch-orchestration.md#dispatch-verify-story-story-id-sha-commit-sha
status: resolved
traces: []
---

# verify-story omits the mandated premerge-check --scope argument

**What is wrong:** The current workflow runs `factory/scripts/premerge-check <target> <feature-branch> --scope <story's declared outputs>` ([implementation-agent.md § Workflow, Step 4b](../../factory/agents/implementation-agent.md#workflow)); the `--scope` check is the check that catches out-of-scope paths — the direct mechanical detector for the proposal's own failure mode #1 (branch contamination). The proposal's `verify-story` step 3 says only "premerge-check on the story's branch against the invocation branch", with no `--scope`, and the ledger schema it references carries no `outputs` field for the script to derive scopes from. As written, the mechanized replacement silently regresses a check the current contract mandates, weakening exactly the failure mode the proposal exists to close.

**Fix:** Specify that `verify-story` (or `merge-story`, per SPEC-007) reads the story file's `outputs:` globs and passes them as repeated `--scope` arguments to `premerge-check`, and add this to the completion criteria.

**Resolution (2026-08-18, repeat pass):** Fixed in commit c1507a1. `merge-story` step 1 now reads the story file's `outputs:` globs and passes them as repeated `--scope` arguments, states that omitting `--scope` would silently skip the check, and commits to never calling `premerge-check` without scopes. A matching completion criterion was added. (The check moved from `verify-story` into `merge-story` per SPEC-007, which the fix honours.) Verified against the current proposal text.
