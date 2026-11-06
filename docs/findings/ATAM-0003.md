---
id: ATAM-0003
source: atam-review
severity: medium
category: defect
artifact: docs/adr/0026-layout-migration-runs-inside-the-factory-update.md#decision
status: resolved
traces: [ADR-0026, ADR-0023, DEC-11, DEC-17]
---

# An update from a factory before 1.1.0 does not roll back a failed migration

**What is wrong:** The rollback in ADR-0026 depends on the `update-factory` that is already installed in the project, because the old version runs the update. Only `update-factory` 1.1.0 and later restore the factory tree and `install.json` when `init-factory` fails. ADR-0026 ("Self-undo and rollback", line 75) and chapter 6.10.7 (line 650) state the rollback for every update.

The tags show the gap. In `v0.5.0` to `v1.0.0`, `update-factory` moves the old tree aside and lets `init-factory` copy the new tree (`init-factory::copy_factory`). On a non-zero exit, it restores the old tree only when no new tree exists:

```text
if backup is not None and backup.is_dir() and not target_factory.exists():
```

(`git show v1.0.0:packages/factory/scripts/update-factory`, line 423.) The new tree always exists at that point, so nothing is restored. That version also keeps no copy of `install.json`. Today `init-factory` writes the new `factory_version` in its manifest step. Because the migration is the last step, it runs after that write, unless the implementation changes this order.

So in a project at 1.0.0, a failed migration leaves the new scripts and hooks, the new `factory_version`, and the old layout. That is the state DEC-11 rules out. Every later run of `init-factory` then sees the layout release and moves nothing. Nothing tells the developer to run `migrate-spec-layout` by hand.

A project at `v0.12.0` or earlier has a related gap. Its manifest is `.agent-factory/factory-install.json`. The new `init-factory` finds no `install.json` and treats the update as a first install, so it moves nothing.

**Fix:** Keep DEC-17 and close the gap in the architecture with these three changes:

1. When `migrate-spec-layout` fails, `init-factory` writes the prior `factory_version` back into `install.json` before it exits non-zero. The next update then runs the migration again. The migration stays the last step.
2. ADR-0026 and chapter 6.10.7 state that the factory tree is restored only when the installed `update-factory` is 1.1.0 or later. They also name the minimum installed version for an update to the layout release, or the path for older projects.
3. `init-factory` at the layout release or later lists the old layout paths it still finds on every run, the same way it does on a first install. A project that missed the migration then learns about it.

Add a scenario for an update from a version before 1.1.0 to `core-artifact-layout.feature`, or record why such a scenario is out of scope.

**Resolution:** `init-factory` writes the new `factory_version` into `install.json` only after `migrate-spec-layout` exits 0. After a failure the record keeps the prior version, so the next run retries the migration. `init-factory` reports the old layout and names the fix: run the update again. An `update-factory` before 1.1.0 restores nothing. ADR-0026 records this state as an accepted, temporary risk: the developer runs the update again, and the new `update-factory` and `init-factory` retry the migration. No minimum installed version applies. A project with only `.agent-factory/factory-install.json`, the record up to `v0.12.0`, counts as an older install, so the script runs. ADR-0026 (Decision and Consequences), the dynamic views `UpdateLayoutMigration` and `UpdateLayoutMigrationRollback`, chapter 6.10.6 and 6.10.7, chapter 5, and chapter 9 state this. Scenarios in `core-artifact-layout.feature` belong to the requirements fix pass.

**Verification (repeat ATAM review, 2026-11-02):** The fix holds. ADR-0026, chapter 5, chapter 6.10.6 and 6.10.7, the DSL, and `interface-contracts.md` agree: `init-factory` writes the new `factory_version` only after `migrate-spec-layout` exits 0, `factory-install.json` counts as an older install, and the case of an `update-factory` before 1.1.0 is recorded as an accepted risk. The retry that this risk relies on does not run as documented. ATAM-0005 tracks that gap.
