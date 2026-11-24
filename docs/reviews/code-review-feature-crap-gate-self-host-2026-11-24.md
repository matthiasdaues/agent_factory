---
type: code-review
title: Code review of the whole feature crap-gate-self-host
date: 2026-11-24
status: pass
reviewer: code-review-agent
findings_filed: 2
story:
run: feature/crap-gate-self-host
branch: feature/crap-gate-self-host
branch_base: 634135fefd07cbbadd33acdfbc4e17de1e771706
branch_head: 94079fc1766d28a7bd11f3507a63771df71a880e
---

# Code review of the whole feature crap-gate-self-host

## Verdict

The feature passes the code review. No finding blocks. The review files two register files of severity `minor`, [IMPL-0116](../findings/register/code/IMPL-0116.json) and [IMPL-0117](../findings/register/code/IMPL-0117.json), and records four notes. Both minors are about the first stories after the merge, when the gate is on for this repository.

- IMPL-0116: the installed `crap-score` 1.14.1 sets no `GATE_SCOPE`. Until a release that holds ST-0451 is installed, every story runs the full Python suite under coverage, twice.
- IMPL-0117: three functions that BUG-0147 changed fail the gate. No gate judged them, so the next story that touches them inherits the failure.

The template, the copy of this repository and `crap-score` agree. The 57 test files that the feature diff selects pass, 3,127 tests in two runs. One scoped gate run on the feature diff judged 14 functions and failed 3.

Next, the orchestrator commits this report and the two register files on the feature branch. The QA agent then runs QA on the feature branch. The handoff of the merge into `dev` names the release and `update-factory` as the step before the next run (IMPL-0116).

## Scope

The review covers `git diff dev...feature/crap-gate-self-host`, merge base `634135fe`, head `94079fc1`, 67 files. It leaves out what the merges from `dev` brought in. The four story reviews went through each unit, so this review does not repeat them: [ST-0451](code-review-ST-0451-2026-11-23.md), [BUG-0141](code-review-BUG-0141-2026-11-23.md), [ST-0449](code-review-ST-0449-2026-11-24.md) and [BUG-0147](code-review-BUG-0147-2026-11-24.md). It looked at three questions that a story review cannot answer:

- Do the template, the copy of this repository and the variables of `crap-score` fit together?
- What does the gate on this repository mean for the gate-check step and `premerge-check` of the next story?
- Do code, skills, specification and architecture still agree across the units, and did a merge from `dev` break the code of the feature?

The review read ST-0449 and ST-0451, DEC-84 to DEC-87 in the Appendix of `docs/proposals/crap-gate-setup.md`, BR-129 and BR-130, § crap-score and § crap-measure-python of `docs/spec/interface-contracts.md`, the new Scenarios of `docs/spec/features/crap-gate-setup.feature`, arc42 § 5 and § 6, the measuring commands in `docs/spec/architecture.dsl`, both skills of the gate, `docs/testing.yaml`, and the gate code of `premerge-check` and `implementation-agent.md`.

## Template, copy and variables

| Part                                               | Result                                                                                                                                                                                                            |
| -------------------------------------------------- | ----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| `scripts/crap-measure-python` against the template | `diff` shows only `TEST_COMMAND` and `SELECT_COMMAND`. The fix of BUG-0141 is in both.                                                                                                                            |
| `crap-score` and the Python command                | `crap-score` sets `GATE_SCOPE=changed` and the paths of the diff with `--base`, and the command reads both. Without a changed path that the measure keeps, the command runs no test and writes `[]`.              |
| `crap-score` and the TypeScript command            | The command ignores both variables and runs the whole TypeScript suite on every call. The contract allows this.                                                                                                   |
| `SELECT_COMMAND` and `test_changed_command`        | Both are `python3 tests/select_tests.py --run`. The selector uses the words of `TEST_COMMAND`, so it runs a subset.                                                                                               |
| The selector and the measure `python`              | Both take only files directly below `packages/factory/scripts/`. Each of the 53 measured scripts selects at least three test files.                                                                               |
| The installed copy                                 | The gate-check step and `premerge-check` run `.agent-factory/factory/scripts/crap-score`. In this repository that is 1.14.1, which sets neither variable ([IMPL-0116](../findings/register/code/IMPL-0116.json)). |

The review checked one script that the gate reaches only as a subprocess of `#!/usr/bin/env python3`: `build-release`. Under the scoped measure it got rows with coverage from 66.67 % to 100 %, so the system Python of this machine records coverage too.

## The gate on this repository after the merge

| Caller or case                                                       | What happens                                                                                                                                                                                                                                                                    |
| -------------------------------------------------------------------- | ------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| The merge of the feature into `dev`                                  | `premerge-check` reads `enabled` from `dev` (DEC-80), where the gate is off until the merge. So no gate judges the feature diff.                                                                                                                                                |
| The gate-check step of the next story                                | `crap-score --base <feature-branch>` reads the threshold 30 and both measures from `dev`. With the installed 1.14.1, the Python measure runs the full suite (IMPL-0116).                                                                                                        |
| `premerge-check` of the next story                                   | The same call with `--base <target>`. `timeout_minutes` 20 covers the measured 12 minutes of a full run.                                                                                                                                                                        |
| A story that changes `do_add`, `_install` or `update-factory` `main` | It fails the gate for code that BUG-0147 changed ([IMPL-0117](../findings/register/code/IMPL-0117.json)).                                                                                                                                                                       |
| A story on a feature branch that has not merged `dev`                | Its `docs/testing.yaml` still has `enabled: false` and no measures, so `crap-score` exits `2` with "gates.crap-score in docs/testing.yaml has no timeout_minutes". `premerge-check` then exits `3`, and the story stops as `blocked`. The fix is to merge `dev`; see the notes. |

## Findings

| Finding                                                                                                                                                                                                                                                                                                                        | Artifact                                              | Category   | Type          | Severity | Basis                                                                                    | Filed as                                              |
| ------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------ | ----------------------------------------------------- | ---------- | ------------- | -------- | ---------------------------------------------------------------------------------------- | ----------------------------------------------------- |
| `dev` enables the gate at the merge, but the gate-check step and `premerge-check` run the installed `crap-score` 1.14.1, which sets no `GATE_SCOPE`. So every story runs the full Python suite under coverage twice, until a release with ST-0451 is installed. ST-0449 names that install as an input.                        | `docs/testing.yaml:80-111`                            | suggestion | build         | minor    | `in_use: false`, `harms_downstream: false`, `fails_purpose: false`, `raises_cost: true`  | [IMPL-0116](../findings/register/code/IMPL-0116.json) |
| `do_add` (342.49), `_install` (38.71) and `update-factory` `main` (61.66) fail the gate at threshold 30. BUG-0147 changed them before the gate was on, and no gate judged them. The next story that changes a line of one of them fails for code it did not write.                                                             | `packages/factory/scripts/init-factory:4449-4454`     | suggestion | test          | minor    | `in_use: false`, `harms_downstream: false`, `fails_purpose: false`, `raises_cost: true`  | [IMPL-0117](../findings/register/code/IMPL-0117.json) |
| A story on a feature branch cut before the merge, such as `feature/GB-5609_factory_as_python_package`, gets exit `2` with "has no timeout_minutes". The message does not say that `dev` holds the entry and the branch must merge it. The merge handoff can tell the owners of the open feature branches.                      | `packages/factory/scripts/crap-score`                 | suggestion | documentation | note     | `in_use: false`, `harms_downstream: false`, `fails_purpose: false`, `raises_cost: false` | report only                                           |
| The measuring commands in `architecture.dsl` say "each measuring command reads GATE_SCOPE and GATE_CHANGED_FILES". `scripts/crap-measure-typescript` reads neither, and BR-129 and the skill allow that. "May read" fits both.                                                                                                 | `docs/spec/architecture.dsl:141`                      | suggestion | inconsistent  | note     | `in_use: false`, `harms_downstream: false`, `fails_purpose: false`, `raises_cost: false` | report only                                           |
| Step 4d of `implementation-agent.md` says "`premerge-check` runs the full `crap-score` and the test suite". Since DEC-84, the Python measure of a story is scoped to its changed paths. The sentence is right only about the reason for the background job, the time limit.                                                    | `packages/factory/agents/implementation-agent.md:178` | suggestion | documentation | note     | `in_use: false`, `harms_downstream: false`, `fails_purpose: false`, `raises_cost: false` | report only                                           |
| The Examples of the Scenario Outline "The measure python excludes a script that no test runs" have no header row. A Gherkin reader takes `generate-codex-agents` as the column name, so `<script>` binds to nothing and seven rows remain. Add the row `\| script \|`. No tool of the run parses the file; `spec-lint` passes. | `docs/spec/features/crap-gate-setup.feature:1563`     | defect     | documentation | note     | `in_use: false`, `harms_downstream: false`, `fails_purpose: false`, `raises_cost: false` | report only                                           |

The developer agent acts on IMPL-0116 and IMPL-0117 in the follow-up work; neither blocks. The open minors IMPL-0102, IMPL-0104 and IMPL-0113 of the story reviews stay `open`, and this review does not file them again.

## Focus areas

| Focus area         | Result                                                                                                                                                                                                                                                                                                |
| ------------------ | ----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| Correctness        | The code matches DEC-84 to DEC-87 and BR-129 and BR-130 as the specification states them. The gate judges the feature diff correctly; the three failures are real scores, not measuring faults.                                                                                                       |
| Clean Architecture | `crap-score` still holds no code of a language, and both measuring commands name nothing under `.agent-factory/`. The selector is a project script that the template calls, not Factory code.                                                                                                         |
| SOLID              | ST-0451 adds the two variables in one place, `scope_environment`, and the paths in another, `changed_paths`. `measure_all` passes them through a copy of the measure, so `run_measure` keeps one job.                                                                                                 |
| Maintainability    | The deleted scripts `migrate-proposal` and `migrate-story-schema` have no caller left. IMPL-0117 names the three functions above the threshold that the feature changed.                                                                                                                              |
| Consistency        | The skill, the template header, the interface contract and arc42 § 5 describe the variables in the same words. `architecture.dsl` is the one place that says "reads" where the others say "may", which is a note. The tests of the usage runtime that came from `dev` pass with the code of BUG-0147. |

## Verification

```bash
uv run --directory /home/matthiasdaues/Documents/datenschoenheit/agent_factory/.current-work/feature/crap-gate-self-host/invocation pytest -q -n 4 tests/factory/test_crap_gate_template.py tests/factory/test_crap_gate_score.py tests/factory/test_crap_gate_repository.py tests/factory/test_crap_gate_text.py tests/factory/test_trigger.py tests/factory/test_validate.py tests/factory/test_update_factory.py tests/factory/test_usage_capture_paths.py tests/factory/test_select_tests.py
```

The run passed 276 tests on `94079fc1`. A second run of the other 48 files that the selector picks for the feature diff passed 2,851 tests and skipped 2.

The scratch checks lie under `/tmp/claude-1000/-home-matthiasdaues-Documents-datenschoenheit-agent-factory/89fd1670-49e4-4a59-97db-e1035150aa04/scratchpad/feature-review/`:

| Check                                                                                                        | Result                                                                                                                   |
| ------------------------------------------------------------------------------------------------------------ | ------------------------------------------------------------------------------------------------------------------------ |
| `installed-scope.sh <crap-score>`: a stub command records the scope variables                                | Installed 1.14.1: `GATE_SCOPE=<unset>`. Head `94079fc1`: `GATE_SCOPE=changed`, `GATE_CHANGED_FILES=src/a.py` (IMPL-0116) |
| `build-release-scope.sh repo packages/factory/scripts/build-release`: the scoped Python measure              | Exit `0`, 137 tests, 10 rows with measured coverage                                                                      |
| `old-branch.sh oldwt <crap-score>`: a head with the `docs/testing.yaml` of `dev` before the merge            | Exit `2`, "gates.crap-score in docs/testing.yaml has no timeout_minutes"                                                 |
| `crap-score --base dev` in the clone `repo`, with a local `dev` that holds the feature's `docs/testing.yaml` | Exit `1`: 14 functions judged, `do_add`, `_install` and `update-factory` `main` fail (IMPL-0117)                         |

The last check first exited `2` in a fresh clone, because `test_CAL_14_gate_passes_on_the_factory_repository[link-check]` needs the installed `.agent-factory/` of the checkout. The clone has none. The same test passed in the worktree of the feature. With a copy of the installed tree in the clone, the run measured.
