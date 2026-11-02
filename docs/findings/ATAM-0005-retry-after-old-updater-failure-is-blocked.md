---
id: ATAM-0005
source: atam-review
severity: medium
category: defect
artifact: docs/adr/0026-layout-migration-runs-inside-the-factory-update.md#decision
status: resolved
traces: [ADR-0026, ADR-0023, ATAM-0003, QS-15]
---

# The retry after a failed migration under an old update-factory stops before init-factory runs

**What is wrong:** ADR-0026 accepts one risk: an `update-factory` before 1.1.0 restores nothing after a failed migration. The recovery is "the developer runs the update again", and the new `update-factory` then retries the migration (ADR-0026 § Self-undo and rollback; chapter 6.10.7; QS-15). In two cases the new `update-factory` stops before it runs `init-factory`.

**Case 1: a project at `v1.0.0`.** The old `update-factory` writes `.agent-factory/checksums.json` only after `init-factory` exits 0 (`git show v1.0.0:packages/factory/scripts/update-factory`, lines 420-445). After the failure, `checksums.json` still holds the hashes of the old tree, but the tree on disk is the new one. On the retry, the current `update-factory` runs `_detect_modifications` before staging (line 1449). Every factory file that changed between the two versions counts as a user modification. Without `--force`, the script exits 2 with "User modifications detected". `init-factory` named only "run the update again", so the developer does not know that `--force` is safe here.

**Case 2: a project at `v0.12.0` or earlier.** Its record is `.agent-factory/factory-install.json`. The current `update-factory` reads only `.agent-factory/install.json` (`load_manifest`, line 255). If the failed run of the new `init-factory` left no `install.json`, the retry stops with "is not an init-factory'd project". The architecture does not say whether `init-factory` creates `install.json` before the migration. `interface-contracts.md` line 796 says only that "the other writes of `init-factory`" stay in place.

So in both cases the documented fix does not work, and the new factory stays on the old layout.

**Fix:** Keep the accepted risk and make the retry path real. Two options:

1. `init-factory` names the exact command in its failure report: `update-factory --force` for case 1, with the note that the reported modifications are the new release's own files.
2. The new `init-factory` writes `install.json` with the prior `factory_version` before it runs the migration, and the new `update-factory` treats a tree whose checksums match the target release as unmodified.

In both options, state in ADR-0026 whether `install.json` exists after a failed run that started from `factory-install.json`. Add the retry to QS-15 as an explicit response measure.

**Resolution:** Out of scope after the stakeholder dropped support for updaters before v1.1.0-rc (2026-11-02).
