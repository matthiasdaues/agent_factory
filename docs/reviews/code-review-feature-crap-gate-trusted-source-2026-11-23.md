---
type: code-review
title: Code review of the whole feature crap-gate-trusted-source
date: 2026-11-23
status: defects
reviewer: code-review-agent
findings_filed: 2
story:
run: feature/crap-gate-trusted-source
branch: feature/crap-gate-trusted-source
branch_base: 334f5a2e8e3a812954ca244442a432525606eefa
branch_head: 83ff431982f16c67e39a7db390c3594c8ce3a212
---

# Code review of the whole feature crap-gate-trusted-source

## Verdict

The feature does not pass the code review. One finding blocks. With [IMPL-0098](../findings/IMPL-0098.md), `crap-score --all` exits `2` when the checkout is on the integration branch that `integration_branch` names. So setup step 6 fails for every project that sets the key. A scratch repository reproduces this. The review also files one register file of severity `minor`, [IMPL-0099](../findings/register/code/IMPL-0099.json), records four notes, and asks one question.

Code, tests and the updated specification agree everywhere else. Every caller of `crap-score` on the merge path matches the contract. The 586 tests of the fifteen related test files pass on `83ff4319`.

Next, the developer agent fixes IMPL-0098 on the feature branch, and the code review of the whole feature runs again. IMPL-0099 does not block.

## Scope

The review covers the diff `334f5a2e..83ff4319`, 15 commits and 35 files. The story review in [code-review-ST-0450-2026-11-22.md](code-review-ST-0450-2026-11-22.md) went through the trust boundary in three passes, so this review does not repeat it. It looked at three questions that a story review cannot answer:

- Do code, tests and the specification agree as a whole? The wave close edited the specification after the code.
- Do the callers of `crap-score` still match it?
- Is anything in the diff dead, duplicated or untested?

The review read Rule CG-14 and the CG-01, CG-02 and CG-04 Scenarios of `docs/spec/features/crap-gate-setup.feature`, BR-127 to BR-132 and BR-138, § crap-score, § Trusted gate source, § gate-setup-proof and § `docs/factory-settings.yaml` of `docs/spec/interface-contracts.md`, ADR-0041, arc42 § 5, the relations of `crapScore` in `docs/spec/architecture.dsl`, and DEC-67 to DEC-78 in the Appendix of `docs/proposals/crap-gate-setup.md`.

## Callers of crap-score

| Caller                                                             | Call                                                                     | Result                                                                                                                                                                                               |
| ------------------------------------------------------------------ | ------------------------------------------------------------------------ | ---------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| `premerge-check`, `gate_command`                                   | `--base <target> --story-id <id> --report-dir <primary>/...`             | Matches BR-136. It passes no `--settings-from-folder`, and the key comes from the tree of the target. The script is unchanged.                                                                       |
| `dispatch`                                                         | none                                                                     | `dispatch` starts `crap-score` only through `premerge-check`. It keeps its fixed `dev` (DEC-68).                                                                                                     |
| `gate-setup-proof`, `run_gate`                                     | `--base <start> ... --settings-from-folder`                              | Matches DEC-71 and DEC-73. The first commit holds the working-tree copy of `docs/factory-settings.yaml`. The proof `HEAD` is its own planted commit, so the `HEAD` check of DEC-76 does not stop it. |
| Gate-check step, `packages/factory/agents/implementation-agent.md` | `--base <feature-branch> --story-id <id> --report-dir <gate-folder>/...` | Matches BR-134, without the option. CG-14-LN-01 reads it.                                                                                                                                            |
| `packages/factory/skills/crap-score/SKILL.md`                      | the call line and § Trusted gate source                                  | Matches BR-127 and BR-128. The `--base` bullet does not name DEC-78; see the notes.                                                                                                                  |
| Setup step 6, `packages/factory/skills/setup-crap-score/SKILL.md`  | `--all --story-id setup --report-dir .current-work/crap-score/`          | Exits `2` on a named integration branch. [IMPL-0098](../findings/IMPL-0098.md).                                                                                                                      |
| arc42 § 5, `architecture.dsl`, ADR-0041                            | text                                                                     | Each states DEC-77 and DEC-78 as the code does. arc42 § 5 also names the run of step 6, which IMPL-0098 breaks for a named branch.                                                                   |

## Findings

| Finding                                                                                                                                                                                                                                                                                                                                          | Artifact                                         | Category   | Type          | Severity | Basis                                                                                    | Filed as                                              |
| ------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------ | ------------------------------------------------ | ---------- | ------------- | -------- | ---------------------------------------------------------------------------------------- | ----------------------------------------------------- |
| `GitRefSource.__init__` runs the `HEAD` check of DEC-76 for every call. With `--all` on the checked-out integration branch that `integration_branch` names, `HEAD` is that tip, so setup step 6 exits `2`. Run the check only with `--base`, and limit the `HEAD` sentence of DEC-76 in the specification to `--base`.                           | `packages/factory/scripts/crap-score:1118-1134`  | defect     | checking      | major    | `in_use: false`, `harms_downstream: false`, `fails_purpose: true`, `raises_cost: false`  | [IMPL-0098](../findings/IMPL-0098.md)                 |
| Twelve causes of exit `2` that BR-127, BR-128 and § Trusted gate source now name have no test, and no QA strategy row owns them: eight shape checks of `branch_values`, a broken `docs/factory-settings.yaml`, a branch `docs/testing.yaml` that is no mapping, and a `--base` that names no commit. Add contract tests and one QA strategy row. | `packages/factory/scripts/crap-score:950-1092`   | suggestion | test          | minor    | `in_use: false`, `harms_downstream: false`, `fails_purpose: false`, `raises_cost: true`  | [IMPL-0099](../findings/register/code/IMPL-0099.json) |
| The `--base` bullet of `crap-score/SKILL.md` says "The revision is a branch or a commit" and does not say that a local branch wins over a tag of the same name (DEC-78). BR-127 and the contract say it. A reader of the skill learns it only from the specification.                                                                            | `packages/factory/skills/crap-score/SKILL.md:19` | suggestion | documentation | note     | `in_use: false`, `harms_downstream: false`, `fails_purpose: false`, `raises_cost: false` | report only                                           |
| The Domain Rule bullet 2 and the Analysis bullet "Branch" of `backlog/ST-0450.md` say that `crap-score` reads `integration_branch` from the folder. DEC-77 moved the key to the `--base` revision. The story is `done`, and the specification is right, so the story text is only a stale record.                                                | `backlog/ST-0450.md`                             | suggestion | documentation | note     | `in_use: false`, `harms_downstream: false`, `fails_purpose: false`, `raises_cost: false` | report only                                           |
| `_gate_entry` takes the old key `crap_score` on the integration branch without the warning of BR-055. `read_settings` prints that warning for the folder. A branch file that holds both keys therefore warns only when the folder holds both too.                                                                                                | `packages/factory/scripts/crap-score:1094-1105`  | suggestion | function      | note     | `in_use: false`, `harms_downstream: false`, `fails_purpose: false`, `raises_cost: false` | report only                                           |
| The note of the first story pass on the header of `crap-score`, § Exceptions, still holds: "Without a branch dev, the output says that no register was read" is true only for the default `dev`. The review records it again, so it does not get lost at the merge.                                                                              | `packages/factory/scripts/crap-score:73-79`      | suggestion | documentation | note     | `in_use: false`, `harms_downstream: false`, `fails_purpose: false`, `raises_cost: false` | report only                                           |

The developer agent acts on IMPL-0098 and IMPL-0099. IMPL-0098 blocks the feature. IMPL-0099 has a register file with `status: open`, and the commit that fixes it sets `status` to `resolved`. The known minors IMPL-0095 and IMPL-0097 stay `open`, and the review does not file them again.

## Question for the stakeholder

Take a project whose `dev` already holds `gates.crap-score` with threshold 8 and no `exclude`. The test-strategy agent runs `setup-crap-score` again to add the `exclude` pattern `**/db/alembic/versions/**` to the measure `backend`, and the User proposes threshold 10. Step 5 passes `--settings-from-folder`, so the proof judges with 10 and the new pattern. Step 6 passes only `--all`, so the run judges with threshold 8 of `dev` and still judges the Alembic files. The User then reads failure counts for values that the setup does not propose. The review read this from the code and did not run it. A first setup is not affected, because `dev` holds no entry yet and the values come from the folder.

- **Keep step 6 as it is.** The skill sets the gate up once per project. A change of a committed value goes through a story, and the story review guards it.
- **Pass `--settings-from-folder` in step 6 too.** Step 6 then counts the failures with the values the User is about to confirm. BR-127 and DEC-71 then name the setup as a second caller of the option.

The review recommends the first option, because the skill and CG-01 describe one first setup and no Scenario names a second run. The answer changes step 6 of `setup-crap-score/SKILL.md`, BR-127 and DEC-71, or nothing.

## Focus areas

| Focus area         | Result                                                                                                                                                                                                                                                                                                                                                                           |
| ------------------ | -------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| Correctness        | The code matches DEC-67 to DEC-78 as the specification now states them. IMPL-0098 is the one place where a rule of the specification, the `HEAD` check of DEC-76, breaks a caller that the specification also names, setup step 6.                                                                                                                                               |
| Clean Architecture | `main` reaches every trusted value through `TrustedGateSource`. No line outside `DEFAULT_BRANCH` names `dev`. The gate logic does not call `resolve_base` and `changed_lines` through the reader, which matches ADR-0041: the diff is not a trusted value.                                                                                                                       |
| SOLID              | The story review recorded the one place where the backend holds policy, the call of `join_values` inside `GitRefSource`. Nothing in the later commits changes it.                                                                                                                                                                                                                |
| Maintainability    | Nothing in the diff is dead. `read_register`, `REGISTER_BRANCH` and `NO_DEV_NOTICE` are gone, and no test or script names them. `apply_trusted` raises for a measure without patterns, which only a second backend can reach; that is a guard for the seam of DEC-72. IMPL-0095 names the duplication of `branch_values` and `_measures`, and IMPL-0099 names the missing tests. |
| Consistency        | `gate-setup-proof` defines its own `FACTORY_SETTINGS`, as it defines its own `TESTING_YAML`, because each script stands alone. The messages name the file, the branch, the key and the value, as the contract asks. `INDEX.yaml` changes only token counts, and `test_index_lint.py` passes.                                                                                     |

## Verification

```bash
uv run --directory /home/matthiasdaues/Documents/datenschoenheit/agent_factory/.current-work/feature/crap-gate-trusted-source/invocation pytest -q -n auto tests/factory/test_crap_gate_trusted_source.py tests/factory/test_crap_gate_trusted_proof.py tests/factory/test_crap_gate_score.py tests/factory/test_crap_gate_lock.py tests/factory/test_crap_gate_judging.py tests/factory/test_crap_gate_proof.py tests/factory/test_crap_gate_journey.py
uv run --directory /home/matthiasdaues/Documents/datenschoenheit/agent_factory/.current-work/feature/crap-gate-trusted-source/invocation pytest -q -n auto tests/factory/test_crap_gate_dispatch.py tests/factory/test_crap_gate_premerge.py tests/factory/test_crap_gate_template.py tests/factory/test_crap_gate_text.py tests/factory/test_crap_score.py tests/factory/test_premerge_check.py tests/factory/test_run_lifecycle_premerge.py tests/factory/test_index_lint.py
```

The first run passed 261 tests, and the second passed 325. The reproduction of IMPL-0098 is the script that the finding names. It builds its repository under the scratchpad folder and takes the path of `crap-score` as its first argument.
