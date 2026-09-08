---
created: 2026-09-08
phase: QA (Phase 5)
feature: concern-oriented-context
branch: feature/concern-oriented-context
base_sha: 21aef19
head_sha: 5633824
status: passed
---

# Handoff: Concern-Oriented Agent Context -- QA Complete

## Summary

QA review of the concern-oriented agent context feature (ST-0217 through
ST-0225) is complete. Two defects found, both fixed with regression tests
and committed.

## Findings

### BUG-001: Hook testing.yaml resolution missed by ST-0223 (fixed)

`packages/factory/config/hooks/block-dangerous-git.sh` --
`resolve_testing_yaml` checked only `docs/agent-context/testing.yaml` and
`docs/charter/testing.yaml`. ST-0223 claimed to update "every consumer" of
testing.yaml to the new canonical path `docs/testing.yaml`, but missed this
hook. After YAML-to-concern migration, agents would be blocked from running
any test command.

**Fix**: Added `docs/testing.yaml` as first resolution path, keeping old
paths as migration fallbacks. Two regression tests added.

### FAGAN-001: concern-lint exit code overflow (fixed)

`packages/factory/scripts/concern-lint` line 468 returned raw error count
as the process exit code. Unix exit codes are mod 256, so 256 errors would
exit 0, appearing clean.

**Fix**: Clamped return to `min(counts["error"], 1)`. Regression tests
added for exit-code clamping and the missing-agent-context.md edge case.

### Security Review: Clean

No actionable security findings. The concern-lint script is a local CLI
tool processing project-owned files. Path traversal in `_path_resolves`
only checks existence (never reads or exfiltrates), the hand-rolled YAML
parser avoids deserialization risks, and glob results are used as booleans.

### Fagan Inspection: Clean (beyond above)

All changed files inspected across six target areas: developer-agent,
planning-agent, backlog-lint, context-lint, validate skill, init-factory.
No stale references or logical errors found beyond the two fixed defects.

**Observation (not a defect)**: Two independent flow-mapping parsers exist
in concern-lint and backlog-lint. Behavior is equivalent for the supported
`concerns` field format. Future refactor candidate if a shared YAML-lite
module emerges.

## Test Results

460 tests passed, 7 skipped (456 existing + 4 new regression tests).

## Commit

```
5633824 fix: QA findings -- hook testing.yaml resolution and concern-lint exit code
```

## Files Changed by QA

- `packages/factory/config/hooks/block-dangerous-git.sh` -- added `docs/testing.yaml` to resolution chain
- `packages/factory/scripts/concern-lint` -- clamped exit code
- `tests/factory/test_block_dangerous_git.py` -- 2 regression tests
- `tests/factory/test_concern_lint.py` -- 2 regression tests

Installed copies synced: `factory/config/hooks/block-dangerous-git.sh`,
`factory/scripts/concern-lint`.

## Disposition

**QA passed.** Branch is ready to merge to dev.

## Suggested Skills

- `handoff` -- if continuing to merge phase
- `validate` -- final gate run before merge
