---
type: code-review
title: Code review of the core artifact layout implementation
date: 2026-11-03
status: defects
reviewer: code-review-agent
findings_filed: 3
branch: feature/core-artifact-layout
branch_base: 4040854f2f7cfc62d69ff85761780ed503aec479
branch_head: c8724ac0e597890b01443715f87c0786c5adf903
---

# Code review of the core artifact layout implementation

## Result

The review found two major defects in `migrate-spec-layout`. One loses a file and still exits 0. The other blocks every factory update for a project whose `CONTEXT.md` follows the old format rules. The version test in `init-factory`, the self-undo of the migration, and the gates hold. Next, the Implementation Agent fixes IMPL-0001 and IMPL-0002 and submits the branch for review again.

## Scope

The review covers the code of `git diff 4040854f..c8724ac0`: `packages/factory/scripts/`, `packages/factory/config/`, and `tests/`. It checks the code against `docs/spec/features/core-artifact-layout.feature`, `docs/spec/interface-contracts.md`, ADR-0025, and ADR-0026. Documentation changes are out of scope, because a reconciliation run covers them.

The review ran these suites at the head: `test_migrate_spec_layout.py`, `test_core_layout_gates.py`, `test_core_layout_references.py`, `test_spec_lint.py`, `test_arch_lint.py`, `test_docs_assemble.py`, `test_init_factory.py`, and `test_update_factory.py`. 623 tests passed, and 7 were skipped. Each defect below was reproduced in a scratch repository.

## Findings

| Finding                                                                                                                                                                                                                                                                                                                                                            | Artifact                                                     | Category | Severity |
| ------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------ | ------------------------------------------------------------ | -------- | -------- |
| [IMPL-0001](../findings/IMPL-0001.md): Two old files with one new path, `docs/spec/<name>-qa-strategy.md` and `supplementary_specs/<name>-qa-strategy.md`, both start their move. When the second file is untracked, `Path.rename` overwrites the first file, and the script exits 0. Refuse with exit 2 in `refuse_reason` when two moves share a destination.    | `packages/factory/scripts/migrate-spec-layout:1142`, `:1049` | Defect   | Major    |
| [IMPL-0002](../findings/IMPL-0002.md): `convert_context` refuses a `###` subheading and a `- **Term**:` bullet under `## Language`. The old `context-format.md` and the old `spec-lint` allowed both forms. The update then fails every time, and `init-factory` names a fix that does not help. Accept both forms, or document the refusal and name the real fix. | `packages/factory/scripts/migrate-spec-layout:473`           | Defect   | Major    |

## Checks without a finding

**Version test.** `load_prior_manifest` reads `factory_version` before `write_manifest` runs. During a migration, `write_manifest` keeps the prior version. Only `record_factory_version` writes the new version, and only after the script exits 0. `update-factory` writes the candidate version after `init-factory` returns, and so did every updater from `v1.1.0-rc` to `v1.3.3`. `older_than` follows Semantic Versioning 2.0.0 precedence for the seven cases of the Scenario Outline. `ran_layout_migration` reads the same record value as `init-factory`.

**Self-undo.** Every content edit, staging step, removal, and move adds its undo before or right after the change. The undo runs in reverse order and removes the folders the run created. The undo of `git rm` restores the index from `HEAD` and then the working tree. `git rm` is used only for a tracked file without changes. The script never calls `git rm -f`. The busy-state check resolves `MERGE_HEAD`, `rebase-merge`, `rebase-apply`, and `index.lock` with `git rev-parse --git-path`, so it works in a linked worktree.

**Gates.** `arch-lint`, `structurizr`, `scope-lint`, `spec-lint`, `dependency-check`, `module-graph-check`, `test-design-verify`, `intent`, and `publish-docs` read only the new paths. No factory script outside `migrate-spec-layout` names an old path. `arch-lint` reports `ARCH-MISSING` when chapter 5 exists without `docs/spec/architecture.dsl`. Each gate skips a missing file only where it did so before this change, or where DEC-11 requires it. `spec-lint` reports `TRACE002` as an error without a `use_cases/` folder, as the feature requires.

**Hook block.** `rewrite_factory_hooks` changes only the `files:` key of `agent_factory_hook-*` entries. Comments, other keys, and the project's own hooks stay unchanged. The template pattern matches `docs/spec/architecture.dsl`, `docs/spec/dependency-rules.dsl`, and chapter 5.

## Re-review

The re-review of fix commit `dde5796e` at head `ae7ce7ca` resolves IMPL-0001 and IMPL-0002 and files one new major defect, IMPL-0003. Next, the Implementation Agent fixes IMPL-0003 and submits the branch for review again.

The review ran `test_migrate_spec_layout.py` at the head, and all 143 tests passed. It ran the 13 new tests against the script before `dde5796e` in a scratch copy, and all 13 failed. Each case below ran in a scratch repository.

| Finding                                                                                                                                                                                                                                                              | Verdict  | Evidence                                                                                                                                                                                                                        |
| -------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- | -------- | ------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| [IMPL-0001](../findings/IMPL-0001.md): two old files with one new path                                                                                                                                                                                               | Resolved | Both original cases exit 0, and both contents survive under `billing-qa-strategy.md` and `billing-area-qa-strategy.md`. A forced failure after the moves restores both files. Links to the old path point at the `-area-` path. |
| [IMPL-0002](../findings/IMPL-0002.md): old `CONTEXT.md` forms block the update                                                                                                                                                                                       | Resolved | The original `### Orders` case exits 0 and writes the section `Orders`. Bullet terms become rows. No form of `## Language` refuses.                                                                                             |
| [IMPL-0003](../findings/IMPL-0003.md): two `CONTEXT.md` files with the same `###` subheading give two glossary sections with one heading. `duplicate_terms` keys sections by heading, so it lists no duplicate term and no cleanup step. Count sections by position. | Open     | `### Orders` with `Order` in both `docs/CONTEXT.md` and `docs/arc42/CONTEXT.md` exits 0 with no `duplicate term:` line. The same files without subheadings list `duplicate term: Order in Billing, Shop`.                       |

A line under `## Language` that fits no form, such as `#### Notes`, joins the current definition. No text is lost, so the review files no finding for it.
