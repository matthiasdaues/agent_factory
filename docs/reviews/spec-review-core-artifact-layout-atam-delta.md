---
type: inspect-spec
title: "Specification review of the ATAM changes — core artifact layout"
date: 2026-11-02
status: findings
reviewer: spec-review-agent
findings_filed: 2
scope: git diff ed472748 6f1a45a6 -- docs/spec/, checked against ADR-0026, planning baseline 307979af90fedc6a7b0d9208ca9b3b0d41295f01
---

# Specification Review of the ATAM Changes — Core Artifact Layout

## Summary

The changes from commit `6f1a45a6` are consistent with each other and mostly agree with ADR-0026. Two major gaps remain. First, `git rm` refuses a tracked file with uncommitted changes in the removal set, and the specification does not say what the script does then (SPEC-0028). Second, the specification does not hold the version comparison rule of ADR-0026, including the stakeholder decision that a value that is not a semantic version counts as older (SPEC-0029). Three minor items stay in this report. No finding requires a change to the proposal's design or to a settled decision. SPEC-0028 needs a new stakeholder decision.

## Reviewed Specification

Artifacts read:

- `git diff ed472748 6f1a45a6 -- docs/spec/`: the feature file, the gaps report, the QA strategy, `interface-contracts.md`, and `entity-model.md`
- [ADR-0026](../adr/0026-layout-migration-runs-inside-the-factory-update.md)
- `packages/factory/scripts/update-factory` at `v1.0.0`, `v1.1.0-rc`, and the working tree, for the rollback and version-record claims
- A scratch git repository, to check how `git rm` and `git mv` treat a tracked file with uncommitted changes

`spec-lint` summary: `spec-lint: 0 error(s), 0 warning(s), 25 info across 26 spec file(s).`

## Deterministic Findings

| Check    | Location                                                                    | Disposition                                                         |
| -------- | --------------------------------------------------------------------------- | ------------------------------------------------------------------- |
| TODO001  | `docs/spec/todo.md`, `docs/spec/todos.md`                                   | Dismissed: open todo items, not in this feature's scope.            |
| TRACE003 | 23 business rules (BR-011 to BR-055) defined but never referenced elsewhere | Dismissed: none belongs to this feature, which defines no `BR-###`. |
| TRACE004 | `entity-model.md`: `EPIC_BUILDING_BLOCK` has no attribute block             | Dismissed: an existing entity, not touched by this change.          |

The output matches the repeat review of `ed472748`. The change added no `spec-lint` finding.

## Semantic Findings

| ID        | Finding                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                           | Artifact                                                                                                              | Characteristic | Category | Severity |
| --------- | --------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- | --------------------------------------------------------------------------------------------------------------------- | -------------- | -------- | -------- |
| SPEC-0028 | The Removes row removes the use-case files with `git rm`. `git rm` refuses a tracked file with uncommitted changes (checked: exit 1, "has local modifications"). The migration then fails on every update until the developer commits or discards the change. `git rm -f` would lose the change. ADR-0026 claims that `git rm` works in this case. CAL-G17 settled only untracked and ignored files.                                                                                                                              | `interface-contracts.md:152`; ADR-0026 § What the script changes                                                      | Complete       | Gap      | Major    |
| SPEC-0029 | ADR-0026 compares versions by Semantic Versioning precedence and counts a value that is not a semantic version as older. The Layout migration row names only "older", no `factory_version`, and `unknown`. A value such as `dev` falls into no case. No Scenario pairs `1.10.0` with a `1.4.0` release or tests a prerelease, so CAL-07-CT-01 passes with a string comparison.                                                                                                                                                    | `interface-contracts.md:133`; `core-artifact-layout.feature:266-274`                                                  | Verifiable     | Gap      | Major    |
| M-07      | The failure-mode row "Untracked file in the removal set; merge or rebase in progress; locked index" still cites `Gap: CAL-G17` and `Gap: CAL-G18` and expects "Behaviour open until the story decides". Both gaps are closed, and the Scenarios at feature lines 96 and 103 hold the behaviour, owned by CAL-03-IT-06. Cite the two Scenarios and write the expected result: the file stays and is listed, and the script refuses to start.                                                                                       | `core-artifact-layout-qa-strategy.md:132`                                                                             | Consistent     | Defect   | Minor    |
| M-08      | The Removes row keeps an untracked or an ignored file in the removal set. `Scenario: An untracked file that the path table removes stays and is listed` tests only the untracked case. An ignored file takes a different path through git. Turn the Scenario into an outline with both states, as the move outline at line 84 does.                                                                                                                                                                                               | `core-artifact-layout.feature:96-101`                                                                                 | Verifiable     | Gap      | Minor    |
| M-09      | The specification splits the behaviour at `update-factory` 1.1.0. Under the precedence rule of ADR-0026, the tag `v1.1.0-rc` is older than 1.1.0. Its `update-factory` already has `_rollback_update`, so it restores the factory tree. The QA failure-mode row "New factory on the old layout" is then wrong for `v1.1.0-rc`. The Scenarios still pass, because neither asserts that the tree stays new. Name the boundary as "the first release with `_rollback_update`" or state that `v1.1.0-rc` counts with 1.1.0 and later. | `interface-contracts.md:134-135`, update-factory Layout move row; `core-artifact-layout-qa-strategy.md` failure modes | Unambiguous    | Defect   | Minor    |

Only SPEC-0028 and SPEC-0029 have finding files. The minor items need no finding file. The author can fix them in the same pass.

## Agreement With ADR-0026

- **Version record.** The `init-factory` Version record row, the entity-model note, and three Scenarios state that `init-factory` writes the new `factory_version` only after `migrate-spec-layout` succeeds. This agrees with ADR-0026 § Self-undo and rollback. `update-factory` at `v1.0.0` writes no `factory_version` itself, so the claim holds for the older updater.
- **Old install record.** The Reads row, the Layout migration row, and `Scenario: An install record from release v0.12.0 or earlier counts as older` treat `.agent-factory/factory-install.json` as an older install. The first-install Scenario now requires both records to be absent. This agrees with ADR-0026 § Version test.
- **Rollback by updater version.** `v1.0.0` restores the old tree only when no new tree exists, as ADR-0026 states. The narrowed rollback Scenario and the two new Scenarios follow that split.
- **Git state of moved files.** The Moves row, the Exit code row, and two Scenarios agree with ADR-0026. A check confirms that `git mv` moves a tracked file with uncommitted changes and keeps the changes.
- **Removals and repository state.** The Removes and Preconditions rows agree with ADR-0026 for untracked files, ignored files, merges, rebases, and a held index lock. The case of a tracked file with uncommitted changes disagrees in substance, see SPEC-0028.
- **Version comparison.** The specification has no counterpart, see SPEC-0029.

## Traceability Summary

- **New Scenarios to QA owners.** Each of the seven new Scenarios has an owner: CAL-03-IT-05, CAL-03-IT-06, CAL-07-CT-01, and CAL-07-IT-05. The narrowed rollback Scenario stays with CAL-07-IT-03.
- **Closed gaps.** CAL-G17 and CAL-G18 name the contract row and the Scenario that hold each decision. Both exist. The QA failure-mode table still cites them as open, see M-07.
- **Decisions.** The stakeholder decisions on ATAM-0003 and ATAM-0004 are recorded in the gaps report and match ADR-0026. The rule for a version that does not parse is recorded only in ADR-0026, see SPEC-0029. DEC-01 to DEC-18, the CAL-G01 anchor pair, and the SPEC-0024 decision are not touched by the change.
- **Parts that passed in `ed472748`.** The change edited the path-table outline Given step ("tracked file") and the first-install Given step. Neither edit broke a prior check.

## Overlap With the Parallel ATAM Review

The parallel ATAM review filed ATAM-0006 on the same `git rm` defect as SPEC-0028, from the architecture side. One stakeholder decision settles both. The ATAM review also filed ATAM-0005: the retry after a failure under `update-factory` `v1.0.0` stops at the check for user modifications, or at a missing `install.json`. `Scenario: The next update after a failed migration moves the files` states the outcome that ADR-0026 promises. The Scenario stays right, but its Given steps must name the state that the fix of ATAM-0005 leaves behind, such as the checksums and the install record.

## Next Step

Run the Requirements Agent on SPEC-0028 and SPEC-0029, and let it fix M-07 to M-09 in the same pass. SPEC-0028 needs a stakeholder decision before the author edits the Removes row. The false sentence in ADR-0026 about `git rm` goes to the Architecture Agent.
