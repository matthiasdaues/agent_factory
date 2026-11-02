---
type: atam-review
title: ATAM review of the core artifact layout architecture
date: 2026-11-02
status: defects
reviewer: architecture-review-agent
findings_filed: 2
story: core-artifact-layout
scope: Architecture commit 251bf91b on dev (planning baseline 307979af90fedc6a7b0d9208ca9b3b0d41295f01) — migrate-spec-layout in architecture.dsl, ADR-0025, ADR-0026, the amendment of ADR-0023, and arc42 chapters 5, 6, 8, 9, and 12 — checked against core-artifact-layout.feature, interface-contracts.md, update-factory, and init-factory
---

# ATAM review of the core artifact layout architecture

The architecture carries out DEC-01 to DEC-18, the CAL-G01 anchor pair, and the SPEC-0024 decision consistently. Two Medium risks remain, and both sit on the update path:

- An update from a factory before 1.1.0 does not roll back a failed migration (ATAM-0003).
- The migration does not define what happens to files git does not track (ATAM-0004).

Both can be fixed inside the architecture without changing the proposal's design. Next, the Architecture Agent addresses the two open findings.

## Reviewed architecture

- `docs/arc42/architecture.dsl`: the component `migrate-spec-layout`, its relationships, step 10 of `UpdateTransaction`, and the dynamic views `UpdateLayoutMigration` and `UpdateLayoutMigrationRollback`.
- `docs/adr/0025-core-artifact-layout-under-docs-spec.md`, `docs/adr/0026-layout-migration-runs-inside-the-factory-update.md`, and the amendment of ADR-0023.
- Chapters 5, 6, 8, 9, and 12 as changed in `251bf91b`.
- Reference material: `docs/spec/core-artifact-layout.feature`, `docs/spec/core-artifact-layout-gaps.md`, `docs/spec/supplementary_specs/interface-contracts.md`, `packages/factory/scripts/update-factory`, `packages/factory/scripts/init-factory`, and `update-factory` at the release tags `v0.5.0` to `v1.3.3`.

`packages/factory/scripts/arch-lint --docs-dir docs/arc42` found 0 errors, 1 warning, and 0 info, and exited 0. `packages/factory/scripts/structurizr validate` exited 0.

## Deterministic findings

| Finding                                                             | Disposition                                                                                                                |
| ------------------------------------------------------------------- | -------------------------------------------------------------------------------------------------------------------------- |
| `ARCH-PARSE` warning: could not extract ports from DSL or chapter 5 | Dismissed for this review. The brief records that the warning already exists at HEAD, and commit `251bf91b` adds no ports. |

## Quality scenarios

Chapter 10 has no scenario for the update path. The proposal names the risk domains compatibility and operations. So this review evaluates the four scenarios from the brief:

1. **S1 (compatibility):** A project in the old layout updates to the layout release, and the update moves it into the new layout.
2. **S2 (operations):** The migration fails partway. The project keeps its old layout and its old factory version.
3. **S3 (compatibility):** A first install into a project that has old-layout paths moves no file.
4. **S4 (operations):** A later run on a project that is already migrated moves nothing.

## Findings

### S1: An update from an old version moves the layout

- **Approach:** The installed, old `update-factory` runs the new version's `init-factory`. `init-factory` reads the prior `factory_version` from `install.json` and runs `migrate-spec-layout` as its last step (ADR-0026, view `UpdateLayoutMigration`).
- **Sensitivity points:**
  - The installed `update-factory` must run `init-factory` and leave the prior `install.json` in place. The code meets both conditions in every tagged release from `v0.5.0` to `v1.3.3`. Up to `v1.2.0-rc`, `update-factory` does not touch `install.json` before it runs `init-factory`. From 1.3.0 on, it writes the old record back before that run.
  - The version test needs a defined comparison. CAL-G02 sets the release constant. The comparison must follow semantic versioning, because a string comparison sorts `1.10.0` before `1.4.0`, and it must define how a suffix such as `-rc` sorts.
  - `migrate-spec-layout` must run on the target directory of `init-factory`, not on the current directory, because `update-factory --target` exists. CAL-G10 tracks the argument.
  - The working tree must let `git mv` run (ATAM-0004).
- **Tradeoff point:** The old `update-factory` shows the preview, so the preview cannot mention the move. DEC-17 accepts this: the developer approves the update, not the move.
- **Risk:** ATAM-0004. Untracked or ignored files at old paths make the migration fail. This blocks every update with a generic message.
- **Non-risk:** After `migrate-spec-layout` sets the `files:` values, `refresh_precommit_hooks` in the old `update-factory` compares the factory hook block with the new template. It finds no `files:` difference, so the developer is not asked about hooks a second time.

### S2: A failed migration rolls the update back

- **Approach:** The script undoes its own changes and exits non-zero. Then `init-factory` fails, and `update-factory` restores the factory tree, the manifest, and the wiring (ADR-0026, view `UpdateLayoutMigrationRollback`).
- **Sensitivity point:** Whether the factory tree and `install.json` are restored depends on the version of `update-factory` that is installed in the project, not on the new release.
- **Tradeoff point:** Splitting the undo between the script and the update keeps each component small. The cost is that the project files are restored by different code than the factory tree.
- **Risk:** ATAM-0003. `update-factory` 1.0.0 and earlier do not restore the tree or the manifest after a failed `init-factory`. The project then keeps the new factory and its new version on the old layout, and later runs never migrate it. A `v0.12.0` project has no `install.json`, so the new `init-factory` treats its update as a first install.
- **Non-risk:** `update-factory` 1.1.0 to 1.3.3 keeps `manifest_backup` and the wiring snapshot, and `_rollback_update` restores both. A failure after `init-factory` exits 0 leaves the new factory and the new layout, and these two agree.

### S3: A first install moves no file

- **Approach:** No `install.json` means a first install. `init-factory` lists the old paths and names `migrate-spec-layout` (PROP-25).
- **Sensitivity point:** `install-agent-factory` writes `install.json` only after `init-factory` returns. So a first install through the bootstrap does not meet the "missing `factory_version` counts as older" branch. The code confirms this order.
- **Tradeoff point:** Until the developer runs the script, the new gates read the new paths of a project whose files are still in the old layout. The proposal settles this in favour of not moving files the project owns.
- **Non-risk:** The scenario is covered by the specification, and the architecture matches it.

### S4: A re-run moves nothing

- **Approach:** At the layout release or later, the version test is false. On a project without old paths, the script prints nothing and exits 0.
- **Sensitivity point:** The version test is the only trigger, so a project that missed the migration is never offered it again (see ATAM-0003, mitigation 3).
- **Non-risk:** Running the script by hand on a migrated project does no harm.

### YAGNI pass

The architecture adds one component, seven relationships, and two dynamic views. Each element serves a scenario in the specification. `--dry-run` is specified. The only addition with no use is a second `cliAgent -> projectFilesystem` relationship next to an existing one. It adds a second line to the diagrams (Minor, not filed).

## Risk summary

| Finding                                                                                                                                                                                                                                  | Artifact                                                    | Category   | Severity |
| ---------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- | ----------------------------------------------------------- | ---------- | -------- |
| ATAM-0003: `update-factory` before 1.1.0 does not roll back a failed migration, so the new factory stays on the old layout. Restore the prior version on failure, state the minimum installed version, and list old paths on every run.  | `docs/adr/0026-…md` § Decision; `06_runtime_view.md` 6.10.7 | Defect     | Medium   |
| ATAM-0004: The behavior for untracked or ignored files and blocked git states is undefined, and `git mv` fails on them. Define the behavior per git state and add a check that runs before the first change and names the blocking file. | `docs/adr/0026-…md` § Decision                              | Defect     | Medium   |
| Chapter 10 has no quality scenario for the update path. Add one for compatibility and one for operations, based on S1 and S2.                                                                                                            | `docs/arc42/10_quality_requirements.md`                     | Suggestion | Low      |
| The version comparison is not defined. Name a semantic-versioning comparison and the order of prerelease suffixes when CAL-G02 sets the constant.                                                                                        | `docs/adr/0026-…md` § Version test                          | Suggestion | Low      |
| The DSL has two relationships from `cliAgent` to `projectFilesystem`. Merge the fold into the existing description, or keep both on purpose.                                                                                             | `docs/arc42/architecture.dsl`                               | Suggestion | Low      |

## Tradeoff summary

| Tradeoff                                                                 | Gains                                                        | Costs                                                                      |
| ------------------------------------------------------------------------ | ------------------------------------------------------------ | -------------------------------------------------------------------------- |
| The approval of the update covers the move (DEC-17)                      | One decision, and no state with new scripts on an old layout | The old preview cannot name the move                                       |
| The script undoes its own changes, and the update rolls back the factory | Each part restores what it owns                              | The rollback depends on the `update-factory` that is installed (ATAM-0003) |
| The version test decides when the migration runs (PROP-25)               | A first install never moves project files                    | A missed migration is not offered again                                    |
| The script commits nothing (SPEC-0024)                                   | The developer reviews the moves with `git status`            | A `git reset --hard` before the commit loses the move silently             |
