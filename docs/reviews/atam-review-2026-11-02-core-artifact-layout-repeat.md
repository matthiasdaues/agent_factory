---
type: atam-review
title: Repeat ATAM review of the core artifact layout architecture
date: 2026-11-02
status: defects
reviewer: architecture-review-agent
findings_filed: 2
story: core-artifact-layout
scope: Fix commit 6f1a45a6 on dev (planning baseline 307979af90fedc6a7b0d9208ca9b3b0d41295f01) — ADR-0026, architecture.dsl, arc42 chapters 5, 6, 9, 10, and 12 — checked against interface-contracts.md, core-artifact-layout.feature, and update-factory at v0.12.0, v1.0.0, and HEAD
---

# Repeat ATAM review of the core artifact layout architecture

The fixes for ATAM-0003 and ATAM-0004 hold, and both findings are resolved. The three Low items of the first review are fixed. Two new Medium risks remain:

- The retry that ADR-0026 names for a failed migration under an old `update-factory` stops before `init-factory` runs (ATAM-0005).
- A tracked file in the removal set with uncommitted changes either blocks the migration or loses its changes (ATAM-0006).

Both can be fixed inside the architecture without changing the proposal or a settled decision. Next, the Architecture Agent addresses the two open findings.

## Reviewed architecture

- `docs/adr/0026-layout-migration-runs-inside-the-factory-update.md` as changed in `6f1a45a6`.
- `docs/arc42/architecture.dsl`: `initFactory`, `migrateSpecLayout`, their relationships, and the dynamic views `UpdateLayoutMigration` and `UpdateLayoutMigrationRollback`.
- Chapters 5, 6 (6.10.6 and 6.10.7), 9, 10 (QS-14 and QS-15), and 12.
- Reference material: `docs/spec/supplementary_specs/interface-contracts.md`, `docs/spec/core-artifact-layout.feature`, and `update-factory` at `v0.12.0`, `v1.0.0`, and HEAD.

`packages/factory/scripts/arch-lint --docs-dir docs/arc42` found 0 errors, 1 warning, and 0 info, and exited 0. `packages/factory/scripts/structurizr validate` exited 0.

## Deterministic findings

| Finding                                                             | Disposition                                                                              |
| ------------------------------------------------------------------- | ---------------------------------------------------------------------------------------- |
| `ARCH-PARSE` warning: could not extract ports from DSL or chapter 5 | Dismissed. The warning exists at HEAD before this feature, and `6f1a45a6` adds no ports. |

## Prior findings

| Finding   | Verdict  | Evidence                                                                                                                                                                                                                                          |
| --------- | -------- | ------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| ATAM-0003 | Resolved | `init-factory` writes the new `factory_version` only after the script exits 0. `factory-install.json` counts as an older install. The old-updater case is a recorded, accepted risk. ADR-0026, chapters 5 and 6, the DSL, and the contract agree. |
| ATAM-0004 | Resolved | ADR-0026 defines the command for tracked, untracked, and ignored files and refuses during a merge, a rebase, or a held index lock. Chapters 5 and 6, the DSL, the glossary, and the contract agree.                                               |

| Low item of the first review              | Verdict | Evidence                                                                                       |
| ----------------------------------------- | ------- | ---------------------------------------------------------------------------------------------- |
| Chapter 10 has no update-path scenario    | Fixed   | QS-14 (compatibility) and QS-15 (operability) exist and appear in the priority table.          |
| The version comparison is not defined     | Fixed   | ADR-0026 names Semantic Versioning 2.0.0 precedence, prerelease order, and unparseable values. |
| Two `cliAgent -> projectFilesystem` lines | Fixed   | The DSL merges the fold into the existing relationship.                                        |

## Quality scenarios

1. **QS-14 (compatibility):** An update from a version before the layout release moves the project into the new layout.
2. **QS-15 (operability):** A failed migration leaves a project that the next update can migrate.
3. **S3 of the first review (compatibility):** A first install moves no file.
4. **S4 of the first review (operations):** A later run on a migrated project moves nothing.

## Findings

### QS-14: An update moves the project into the new layout

- **Approach:** The new `init-factory` reads the prior version from `install.json` or `factory-install.json`, runs `migrate-spec-layout` as its last step, and then writes the new version. The file's git state picks the command.
- **Sensitivity points:**
  - The version test reads the right record. `factory-install.json` is the record of `v0.5.0` to `v0.12.0` (`MANIFEST_PATH` at both tags), so the fallback covers every tagged release.
  - Each git state of a path-table file needs a command that cannot fail. Moves meet this condition. Removals do not (ATAM-0006).
- **Tradeoff point:** A plain move of untracked files keeps the migration going in every working tree. The cost is that the script must keep a copy of each such file until it exits, because git holds none for the undo.
- **Risk:** ATAM-0006. `git rm` refuses a tracked file with uncommitted changes. Plain `git rm` blocks the migration, and `git rm -f` loses the changes.
- **Non-risk:** `git mv` of a tracked file with uncommitted changes records a rename and keeps the changes. Moving it back during the undo keeps them too.

### QS-15: A failed migration leaves a retryable project

- **Approach:** The script undoes its own changes. `init-factory` keeps the prior version, reports the old layout, and exits non-zero. `update-factory` 1.1.0 and later restore the factory tree.
- **Sensitivity point:** The retry depends on the new `update-factory` reaching `init-factory`. It runs `load_manifest` and `_detect_modifications` first.
- **Tradeoff point:** Accepting the old-updater case keeps the update free of a minimum version. The cost is that recovery depends on a second update run (stakeholder decision on ATAM-0003).
- **Risk:** ATAM-0005. After a failure under `v1.0.0`, `checksums.json` still holds the old tree's hashes, so the retry reports every changed factory file as a user modification and exits 2 without `--force`. After a failure under `v0.12.0` or earlier, the retry finds no `install.json` unless the failed run wrote one, and the architecture does not say whether it does.
- **Non-risk:** With `update-factory` 1.1.0 to 1.3.3, `_rollback_update` restores the manifest and `checksums.json`, so the retry starts from a clean baseline.

### S3: A first install moves no file

- **Approach:** No record at all means a first install. `init-factory` lists old paths and names the script.
- **Non-risk:** The fix narrows "first install" to "neither record", so a `v0.12.0` project is no longer mistaken for one. The feature file has a scenario for each case (lines 277 and 284).

### S4: A re-run moves nothing

- **Approach:** At the layout release or later, the version test is false.
- **Non-risk:** The first review's concern about a missed migration is gone, because a failed run never records the new version.

### YAGNI pass

The fix adds one relationship (`initFactory -> humanOperator`) and two scenarios. Both serve the failure path. The fix removes one duplicate relationship. Nothing unused was added.

### Minor observation (not filed)

The response measure of QS-15 says that `git status` shows no change against the state before the run. Under an `update-factory` before 1.1.0, the instruction headers that `init-factory` rewrote stay changed. Scope the measure to the files the script touches.

## Risk summary

| Finding                                                                                                                                                                                          | Artifact                                                          | Category   | Severity |
| ------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------ | ----------------------------------------------------------------- | ---------- | -------- |
| ATAM-0005: The retry after a failure under an old `update-factory` stops at the checksum check (`v1.0.0`) or at the missing `install.json` (`v0.12.0`). Name the command or make the retry pass. | `docs/adr/0026-…md` § Self-undo and rollback; QS-15               | Defect     | Medium   |
| ATAM-0006: A tracked file in the removal set with uncommitted changes blocks the migration or loses the changes. Keep it in place and list it, as for untracked files.                           | `docs/adr/0026-…md` § What the script changes; contract `Removes` | Defect     | Medium   |
| The QS-15 response measure overstates the result under an old `update-factory`.                                                                                                                  | `docs/arc42/10_quality_requirements.md` QS-15                     | Suggestion | Low      |

## Tradeoff summary

| Tradeoff                                                     | Gains                                               | Costs                                                           |
| ------------------------------------------------------------ | --------------------------------------------------- | --------------------------------------------------------------- |
| A plain move for untracked and ignored files                 | No working tree blocks the migration                | The script keeps a copy of each such file until it exits        |
| The new version is written only after the migration succeeds | A failed migration is retried on the next update    | `init-factory` splits its manifest write around the migration   |
| The old-updater case is an accepted risk                     | No minimum installed version                        | Recovery needs a second update run that works (ATAM-0005)       |
| Refusal during a merge, a rebase, or a held index lock       | The script never moves files into a half-done merge | The update stops until the developer finishes the git operation |
