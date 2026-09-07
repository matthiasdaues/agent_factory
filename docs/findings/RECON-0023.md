---
id: RECON-0023
source: reconcile-spec
severity: minor
category: suggestion
artifact: docs/spec/scope-map.md
status: open
traces: [UC-09]
---

# Scope-map reconciliation needed post-merge

**What is wrong:** The scope map at `docs/spec/scope-map.md` was committed to dev (commits `627d2d6`, `1ff39b9`) after the `test-gate-presence-over-test-execution` branch diverged. The scope map cannot be edited in this worktree without creating an add-add merge conflict.

Two updates are needed after this branch merges to dev:

1. **UC-09 Feature Link stale**: The existing row for "Run project tests deterministically via mechanically triggered gates" points its Feature Link at `factory/scripts/run-tests`, which was deleted. Update the Feature Link to `docs/charter/testing.yaml`, `factory/config/hooks/block-dangerous-git.sh`, `factory/scripts/phase`.

2. **14 new Rules to add as `implemented`**: The following Rules from `docs/spec/test-gate-presence.feature` need scope-map rows with status `implemented` and Source `test-gate-presence.feature`:

   - User declares project test commands via charter
   - FSM gate conditions resolve test command from charter
   - Guardrail allowlists charter-declared test commands for agents
   - Factory does not inject test hooks into pre-commit config
   - Factory deletes run-tests and mutation-analysis scripts
   - Detect-test-regime skill discovers test entrypoints during onboarding
   - Dispatcher gate sequence reduces from three to two
   - Mutation-analysis skill provides setup guidance
   - Remove-factory leaves project test infrastructure intact
   - Gate contract is exit-code-only
   - Charter declares layer bindings for QA strategy grounding
   - QA strategy grounds contract-owner assignments in charter
   - Developer-agent feeds back test-harness mismatches
   - Mutation-analysis skill classifies survivors by contract ownership

**Fix:** After merge to dev, run scope-map reconciliation: update the UC-09 row and add the 14 new Rules. This is a routine post-merge scope-map update, not a blocking issue.
