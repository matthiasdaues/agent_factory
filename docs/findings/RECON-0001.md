---
id: RECON-0001
source: reconcile-spec
severity: major
category: defect
artifact: factory/scripts/merge-precommit-config#L45
status: resolved
traces: [ADR-0001]
---

# merge-precommit-config's no-op marker is hardcoded, breaking the bidirectional splice ADR-0001 documents

**What is wrong:** `docs/adr/0001-precommit-monorepo-scoping.md` (§ "`merge-precommit-config` as the two-way splicing mechanism") documents this script as direction-agnostic: usable both for factory-into-project (its original, documented use in `README.md`) and, per this ADR's own new decision, for subproject-into-root — e.g. `merge-precommit-config --target .pre-commit-config.yaml --template orchestrator/pre-commit-config.yaml`, the pattern `factory_api/` is expected to follow later. The script's already-merged/no-op check is `MARKER_HOOK_ID = "id: index-lint"`, a hardcoded constant unrelated to whichever `--template` is passed. Root `.pre-commit-config.yaml` already contains `id: index-lint` (from the original factory-into-project splice), so invoking the script in the new, second direction against the root file would immediately report "already has Agent Factory's hooks, no change" and silently no-op — it would never actually splice the subproject's template in. The ADR's bidirectional claim is not true of the code as written. Not yet triggering a production bug (ST-0067 did its merge by hand, per that story's own Analysis section, not via this script), but it is the mechanism ADR-0001 tells future subprojects to rely on.

**Fix:** Derive the no-op marker from `--template` instead of hardcoding it — e.g. extract the template's own first top-level hook `id:` (or its first `- id: <name>` line) and check for that string's presence in `--target`, rather than a fixed `"id: index-lint"`. Add a test exercising the subproject-into-root direction (template = a minimal orchestrator-like block, target = a file already containing the factory block) to confirm it actually splices rather than no-ops.
