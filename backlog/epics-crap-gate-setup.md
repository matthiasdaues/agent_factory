---
scope: global
---

# EPICs — CRAP Gate Setup

Proposal trace: [crap-gate-setup.md](../docs/proposals/crap-gate-setup.md), accepted, with DEC-01 to DEC-49 in its Appendix
Specification trace: [crap-gate-setup.feature](../docs/spec/features/crap-gate-setup.feature) (Rules CG-01 to CG-13), [gaps report](../docs/spec/work/crap-gate-setup-gaps.md), [validation-rules.md § CRAP gate](../docs/spec/validation-rules.md#crap-gate-crap-score-br-127br-139) (BR-127 to BR-139, and the changed BR-027, BR-055, BR-066, BR-092, BR-116, BR-124), [interface-contracts.md](../docs/spec/interface-contracts.md), [state-machines.md § Ledger Entry Lifecycle](../docs/spec/state-machines.md#ledger-entry-lifecycle), [entity-model.md § CRAP Gate Entities](../docs/spec/entity-model.md#crap-gate-entities), the schemas in [docs/spec/schemas/](../docs/spec/schemas/)
Architecture trace: the fourth amendment of [ADR-0003](../docs/adr/0003-test-execution-via-hooks.md), [arc42 § 5](../docs/arc42/05_building_block_view.md), § 6, § 8, and QS-31 in [§ 10](../docs/arc42/10_quality_requirements.md)
QA strategy trace: [crap-gate-setup-qa-strategy.md](../docs/spec/work/crap-gate-setup-qa-strategy.md), one owner row per contract

Dependency order: E1 has no dependency and goes first, because the new `crap-score` exits 2 without a gate entry, and the built default would run it in every project without one (DEC-48). E2 builds the new verdict. E3, E4 and E5 then run in parallel. E6 runs last and outside the run of `feature/crap-gate-setup`: it starts after that branch merges into `dev` and `update-factory` installs the new scripts (DEC-49).

Phase 4 numbered the stories ST-0433 to ST-0449 with `next-id ST`. [§ Story waves](#story-waves) shows the expected order.

## Story waves

`dispatch plan` sets the waves from the dependencies and the file overlap. This table is the expected result. Each story names its file overlaps in its section File Overlap, so `dispatch plan` may split a wave further.

| Wave | Stories                            | Reason for the order                                                                                                                                                |
| ---- | ---------------------------------- | ------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| W1   | ST-0433, ST-0435, ST-0436, ST-0441 | No dependency. ST-0433 and ST-0436 change different classes of `tests/factory/test_premerge_check.py`                                                               |
| W2   | ST-0434, ST-0437, ST-0442          | ST-0434 needs ST-0433; ST-0437 and ST-0442 need ST-0436                                                                                                             |
| W3   | ST-0438, ST-0446                   | ST-0438 needs ST-0436 and shares `crap-score` with ST-0437; ST-0446 needs ST-0435 and ST-0436                                                                       |
| W4   | ST-0439, ST-0440, ST-0445, ST-0447 | ST-0439 shares `premerge-check` and `implementation-agent.md` with ST-0434 and ST-0442; ST-0440 shares `crap-score` with ST-0437 and ST-0438; ST-0445 needs ST-0438 |
| W5   | ST-0443, ST-0448                   | ST-0443 needs ST-0438, ST-0439 and ST-0442; ST-0448 needs ST-0446 and ST-0447                                                                                       |
| W6   | ST-0444                            | ST-0444 needs ST-0442 and ST-0443                                                                                                                                   |
| W7   | ST-0449                            | alone, after `feature/crap-gate-setup` merges into `dev` and `update-factory` installs it (DEC-49)                                                                  |

## Terms used in every EPIC

The feature file's description and the [glossary](../docs/spec/glossary.md) define each term. A short reminder:

- **Measure.** One entry under `gates.crap-score.measures` in `docs/testing.yaml`. It names a `files` pattern, optional `exclude` patterns, a measuring command, and an optional `ready` command.
- **Measuring command.** A project-owned script that writes the complexity and the coverage of each function as JSON rows to the path in `GATE_OUTPUT`.
- **Ready command.** A project-owned script that exits 0 when the measuring command can run now, for example when a Compose stack is up.
- **Gate cannot measure.** `crap-score` exits 2. Nobody judged the code, so the story stops as `blocked` with the reason `gate cannot measure: crap-score` and costs no attempt.
- **Exceptions register.** `docs/findings/exceptions.md`. Its section `## CRAP score` lists the functions a person accepts above the threshold.
- **Gate-check step.** The implementation agent runs the gates on a story branch, and a fresh developer agent fixes each failure.
- **Orchestrated run and run by hand.** The two ways of driving the story workflow. An orchestrated run starts stories in worktrees under `.current-work/`; a run by hand works in the primary checkout after the User's go.
- **Installed copy.** `.agent-factory/factory/`, the copy of `packages/factory/` that `dispatch` and the agent tools run.

## Rules that hold for every EPIC

- The stories change the built `crap-score`, `premerge-check`, `dispatch` and `dispatch_lib.py` in place. No story rebuilds a script.
- Source edits go to `packages/factory/`, never to `.agent-factory/factory/`.
- No story edits the specification, the architecture, the proposal, or the QA strategy. A story that finds a conflict writes a spec-feedback row.
- `docs/testing.yaml` of this repository keeps its current content until E6. Only the setup run of E6 changes it, through the test-strategy agent, which owns the file.
- Each story owns the QA strategy rows that its EPIC's Ownership Resolution assigns to it. A pytest test carries `@pytest.mark.spec("CG-NN-XX-NN")` with the Test ID of its row.
- Every git test builds its own repository in `tmp_path`, as [§ Test setup on temporary git repositories](../docs/spec/work/crap-gate-setup-qa-strategy.md#test-setup-on-temporary-git-repositories) defines. No test starts a real measuring command against this repository's root.
- A story that makes an existing test wrong changes or deletes that test in the same commit, as [§ Run-lifecycle tests that change](../docs/spec/work/crap-gate-setup-qa-strategy.md#run-lifecycle-tests-that-change) lists.
- Agents do not run `uv run pytest` by hand, because the guardrail blocks it. The tests run through the commit hooks and the gate-check step.
- A story that changes an agent or a skill regenerates `packages/factory/INDEX.yaml` in the same commit, and `index-lint --check` passes.
- Every story carries `quality-gates: []`, because `docs/testing.yaml` disables both gates until E6.
- No story plans deferred scope: a general check before a run, the mutation gate, gates in CI, a commit hook for the gate, gate evidence beyond the report, tried tools for other languages, or the migration of Gigacron.

## Governance and risk

The proposal declares `assurance: elevated` and two risk domains:

| Risk domain   | What goes wrong                                                                                                                                          | EPICs that guard it |
| ------------- | -------------------------------------------------------------------------------------------------------------------------------------------------------- | ------------------- |
| `reliability` | The gate passes code it should fail: it judges the wrong lines, reads the register from the wrong branch, or the proof accepts a lying measuring command | E2, E3, E5          |
| `operations`  | A fault in the setup costs a story an attempt, or a run starts while a service it needs is stopped                                                       | E4                  |

The stories of E2, E3 (register part), E4 and E5 (proof) get `risk_level: high`.

## E1: Merge stories without a CRAP gate until a person sets it up

### Why this EPIC exists

Today `premerge-check` runs `crap-score` by default when a project has no `gates` section. No project can pass that default, because no step writes coverage data. The new `crap-score` exits 2 without a gate entry, so the default would block every merge in a project that has not set the gate up. This EPIC removes the default and tells the User which gate is not set up and which skill sets it up.

### Actor Goals

- User merges stories without a CRAP gate until a person sets it up

### Demo

1. In a temporary project whose `docs/testing.yaml` has no `gates` section, the User runs `dispatch merge-story ST-0350`.
2. The merge passes. `premerge-check` prints one line that names `crap-score` with the skill `setup-crap-score` and `mutation-testing` with the skill `mutation-testing`. No `crap-score` runs.
3. The User sets `quality-gates: [crap-score]` in ST-0351 and runs `dispatch merge-story ST-0351`.
4. `premerge-check` exits 1, and its refusal names `crap-score` and `setup-crap-score`. `dispatch status` shows ST-0351 still `dispatched`.

### Scope

**In:**

- `premerge-check` drops `DEFAULT_GATES`. Without an entry for a built-in gate, it prints one line that names each such gate with the skill that sets it up, and the merge continues (BR-066, DEC-20, DEC-33).
- `premerge-check` refuses a story whose `quality-gates` field names `crap-score` while `docs/testing.yaml` has no entry, with exit 1, and names `setup-crap-score` (DEC-21). This refusal is no case of "gate cannot measure".
- `implementation-agent.md` refuses the same story in the gate-check step and loses the precedence rule that runs `crap-score` alone. The comment on `quality-gates` in `packages/factory/rulebooks/templates/story.md` loses the same default.
- `packages/factory/rulebooks/templates/charter-testing.yaml` loses its entry `crap_score` with `threshold: 8` and keeps `mutation_testing` (DEC-41, BR-055).
- The `spec` marker in `pyproject.toml` gains the prefix CG ([QA gap 3](../docs/spec/work/crap-gate-setup-qa-strategy.md#gap-findings)).

**Out:**

- The new call of `crap-score` at the merge (E2).
- Exit 3 of `premerge-check` (E4).

### Dependencies

None.

### Boundaries

- Code: `packages/factory/scripts/premerge-check`
- Documents: `packages/factory/agents/implementation-agent.md`, `packages/factory/rulebooks/templates/story.md`, `packages/factory/rulebooks/templates/charter-testing.yaml`, `pyproject.toml`
- Contracts: [§ premerge-check](../docs/spec/interface-contracts.md#agent-factoryfactoryscriptspremerge-check), the `quality-gates` row of [interface-contracts.md](../docs/spec/interface-contracts.md), BR-066
- Tests: `tests/factory/test_premerge_check.py` (the gate-list rows of `test_st_0359_gate_list`, `TestSt0359DemoFixtures.test_st_0359_no_gates_requires_crap_and_skips_dependency_without_rules`, `test_st_0415_the_merge_is_refused_and_names_the_gate`), new `test_crap_gate_*` files

### Domain Rules

- A gate runs at the merge only when `docs/testing.yaml` has an entry for it or the story names it. No gate has a default.
- A story that names `crap-score` without an entry is refused with exit 1, so it costs an attempt like any other refused check.
- The not-set-up line is a notice. It never refuses a merge.

### Size

2 stories.

### Building-Block Inventory

| Story   | Capability                                                   | Tier     | Spawns | Goal                                                                                                                                                         | Basis                                                                                                                                                                                                |
| ------- | ------------------------------------------------------------ | -------- | ------ | ------------------------------------------------------------------------------------------------------------------------------------------------------------ | ---------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| ST-0433 | Merge a story in a project without a CRAP gate entry         | standard | 2–3    | A merge in a project without a gate entry runs no `crap-score` and prints one line that names each gate that is not set up with its skill.                   | `premerge-check` has `DEFAULT_GATES = ["crap-score"]`; the charter template has `crap_score` with `threshold: 8`. Removes the default, adds the line, edits the template, adds the CG marker prefix. |
| ST-0434 | See a story that names `crap-score` before the setup refused | standard | 2      | A story with `quality-gates: [crap-score]` and no entry is refused in the gate-check step and by `premerge-check`, and the refusal names `setup-crap-score`. | `premerge-check` refuses a named gate it cannot run, but names no skill; the agent text and the story template name the default gate. Adds the refusal text and edits both documents.                |

### Testability Assessment

Both goals produce observable outcomes at the exit code and the output of `premerge-check`, run as a subprocess on a temporary repository, and at the ledger state that `dispatch status` shows. The template and the agent text are checked by text checks. The refusal in the gate-check step has one red flag: no script shows that the agent follows its text. CG-11-LN-01 checks the text, and CG-11-IT-03 checks that `premerge-check` refuses the same story at the merge.

### Ownership Resolution

| Contract                                                                                        | .feature Rule                                                                                     | Owner   | Rationale                                                                                   |
| ----------------------------------------------------------------------------------------------- | ------------------------------------------------------------------------------------------------- | ------- | ------------------------------------------------------------------------------------------- |
| CG-11-IT-01: without a `gates` section, no `crap-score` runs and the line names the setup skill | crap-gate-setup.feature#User merges stories without a CRAP gate until a person sets it up         | ST-0433 | removes the default gate                                                                    |
| CG-11-IT-02: the line names every built-in gate without an entry                                | crap-gate-setup.feature#User merges stories without a CRAP gate until a person sets it up         | ST-0433 | introduces the not-set-up line                                                              |
| CG-11-IT-04, CG-11-LN-02: a project from the charter template has no CRAP gate                  | crap-gate-setup.feature#User merges stories without a CRAP gate until a person sets it up         | ST-0433 | edits the charter template                                                                  |
| CG-12-LN-05: BR-066, BR-027, BR-092, BR-116 and BR-124 state the gate's behaviour               | crap-gate-setup.feature#Factory maintainer reads one CRAP gate contract in every Factory document | ST-0433 | first story; the rule texts exist from the spec phase, and BR-066 is this story's behaviour |
| CG-11-IT-03: a story that names `crap-score` without an entry is refused at the merge           | crap-gate-setup.feature#User merges stories without a CRAP gate until a person sets it up         | ST-0434 | introduces the refusal that names the setup skill                                           |
| CG-11-LN-01: the gate-check step refuses the same story; no document names a default gate       | crap-gate-setup.feature#User merges stories without a CRAP gate until a person sets it up         | ST-0434 | edits the agent text and the story template                                                 |

## E2: Get one CRAP verdict for the functions a story changed, in any language

### Why this EPIC exists

The built `crap-score` reads only Python files that end in `.py`, through `radon` and the JSON report of coverage.py. So it skips 55 scripts in `packages/factory/scripts/` that have no ending, and it judges every function in the named files. This EPIC makes the project measure and the Factory judge: `crap-score` runs the project's measuring commands, scores the rows, and judges only the functions whose lines changed against `--base`. The same verdict then comes from the gate-check step and from the merge.

### Actor Goals

- User measures each part of the code with a measuring command the project owns
- Implementation agent gets one verdict for the functions a story changed
- Implementation agent merges a story only when crap-score measures and passes at its branch head (the Scenarios of the call, the folder, the report, and the feature merge)

### Demo

1. A temporary project has `feature/login`, `story/ST-0350`, and a committed `docs/testing.yaml` with `gates.crap-score`: `threshold: 8`, `timeout_minutes: 10`, and a measure `python` whose command is the Python template.
2. On `story/ST-0350`, the developer changes `tree_severity` in `packages/factory/scripts/finding-lint`, a script without an ending, so that it scores 9.
3. The implementation agent runs `crap-score --base feature/login --story-id ST-0350 --report-dir .current-work/crap-score/` as a background job. It exits 1, and the output names the file, `tree_severity` and `9.00`. An unchanged function that also scores 9 is not named.
4. `.current-work/crap-score/ST-0350.json` holds one row per judged function with `crap_score` and `pass_fail`.
5. The User runs `dispatch merge-story ST-0350`. `premerge-check` calls `crap-score --base feature/login` in its temporary worktree and refuses the merge. The report stays under `.current-work/crap-score/` of the primary checkout.

### Scope

**In:**

- The Python measuring-command template under `packages/factory/skills/setup-crap-score/`. It holds the `radon` and coverage.py code of the built `crap-score`, declares both in its `uv run --script` header, reports qualified names such as `Parser.parse` (DEC-12), measures scripts without an ending, reports a file it cannot parse as a row with `parse_error` (DEC-34), and exits non-zero for a case it cannot measure (BR-130). Its header names that duty. It refers to nothing under `.agent-factory/`.
- `crap-score` with the call `(--base <revision> | --all) [--story-id <id>] [--report-dir <folder>]` (BR-127). It loses `--source-root`, `--coverage-json`, `--threshold` and the file list, and holds no language-specific import or file pattern.
- The reader of `gates.crap-score`: `threshold`, `timeout_minutes` and `measures` are required, and a missing value, a measure without `name`, `files` or `command`, an empty list, or two measures with one name make it exit 2 and name the cause (BR-128). It reads `docs/testing.yaml` of the folder it runs in.
- The run of the measures in list order, each `ready` command before its measuring command, one time limit over all commands, and a lock per measure with a `ready` command, so two runs of such a measure never overlap (BR-129, DEC-43, DEC-47).
- The shape check of the rows against `measure-output-rows.json` (BR-130), the `files` and `exclude` filter with one glob dialect (BR-131, DEC-35), the two duplicate checks, and the judging of changed lines against the merge base of `--base`, with deletions counted for both neighbours (DEC-37, DEC-42).
- The formula, the rounding to two decimals half up (DEC-36), the exit codes 0, 1 and 2 (BR-133), and the report `<report-dir>/<story-id>.json` that replaces an earlier one and stays unchanged on exit 2. The report name comes from `--story-id`, `STORY_ID`, the branch ID of a story or a finding, or `adhoc` (DEC-27).
- `premerge-check` calls `crap-score --base <target> --story-id <id> --report-dir <primary>/.current-work/crap-score/` in its temporary worktree, drops the `.py` filter and its notice, and runs no `crap-score` at the feature merge (BR-136, call part).
- `implementation-agent.md` starts `crap-score` in the gate-check step as a background job, passes `--base <feature-branch>` and `--report-dir`, and reads only the exit code (BR-134).
- `packages/factory/skills/crap-score/SKILL.md` is rewritten to describe the gate, with no default threshold and no tool (DEC-01). BR-027 holds the exception for the report.
- `tests/conftest.py` clears every `COVERAGE_*` variable for subprocesses ([QA gap 13](../docs/spec/work/crap-gate-setup-qa-strategy.md#gap-findings)).
- The tests that this EPIC makes wrong: the `crap-score` tests in `test_quality_metrics.py` with the fixture `packages/factory/fixtures/quality-gates/high-crap/`, the tests of `read_threshold_from_testing_yaml` and of named files in `test_crap_score.py`, the class `TestSt0415CrapScoreScoresTheDiff` and the built-call tests in `test_premerge_check.py`, and the fixture `GATES_CRAP_ONLY`.

**Out:**

- The exceptions register (E3).
- Exit 3 of `premerge-check`, `ready` commands before the test suite, and `blocked` (E4).
- The setup skill text and `gate-setup-proof` (E5). E2 adds only the template file under the skill's folder.
- Measuring commands of this repository (E6).

### Dependencies

E1, for ST-0439 only: the new `crap-score` exits 2 without an entry, so the default gate must be gone before `premerge-check` calls it.

### Boundaries

- Code: `packages/factory/scripts/crap-score`, `packages/factory/scripts/premerge-check`, `packages/factory/skills/setup-crap-score/` (template only)
- Documents: `packages/factory/skills/crap-score/SKILL.md`, `packages/factory/agents/implementation-agent.md`
- Contracts: [§ crap-score](../docs/spec/interface-contracts.md#agent-factoryfactoryscriptscrap-score), [§ `gates` section schema](../docs/spec/interface-contracts.md#docstestingyaml--gates-section-schema), `measure-output-rows.json`, `crap-score-report-rows.json`, `crap-score-entry-measures.json`, ADR-0003 amendment, [ADR-0038](../docs/adr/0038-premerge-check-reruns-the-gates-in-a-temporary-worktree.md)
- Tests: `tests/conftest.py`, `tests/factory/test_crap_score.py`, `test_quality_metrics.py`, `test_premerge_check.py`, new `test_crap_gate_judging.py`, `test_crap_gate_score.py`, `test_crap_gate_lock.py`, `test_crap_gate_template.py`, `test_crap_gate_premerge.py`, `test_crap_gate_text.py`

### Domain Rules

- Only changed code can fail. A function counts as changed when its line range holds a changed or deleted line against the merge base of `--base`.
- One commit and one state of the exceptions register always get the same verdict.
- The threshold and the time limit come only from `docs/testing.yaml`. The gate has no built-in value.
- `crap-score` never imports a measuring tool and never matches a language's file ending.
- A run that cannot measure writes no report and leaves an earlier report unchanged.
- The verdict is the exit code. No step reads the report to decide a merge.

§§E2SIZE§§ | Tier | Spawns | Goal | Basis |
| \----- | ------------------------------------------------------------------------------ | -------- | ------ | ---------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- | --------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| ST-0435 | Measure Python code, also scripts without an ending, with the Factory template | standard | 3 | A person runs the Python template in a project without `.agent-factory/` and gets the six-field rows in `GATE_OUTPUT`, or a non-zero exit that names what it cannot measure. | The `radon` and coverage.py code lives inside `crap-score`; no template exists. Adds the template and its tests, and the `COVERAGE_*` clearing in `tests/conftest.py`. |
| ST-0436 | Get a verdict on the changed functions of a story | strong | 3 | `crap-score --base feature/login` exits 1 and names each changed function above the threshold, passes unchanged ones, and exits 2 when its settings are missing or a measuring command fails. | `crap-score` walks `*.py`, reads `coverage.json`, takes a file list and a default threshold. Rewrites it around the measures and rewrites `crap-score/SKILL.md`; deletes the tests of the old code. |
| ST-0437 | Refuse a measuring-command report in the wrong shape | standard | 2 | When a report is not an array of valid rows or names one function twice, `crap-score` judges nothing, exits 2, and names the measure and the fault. | ST-0436 reads the rows. Adds the shape check and the two duplicate checks. |
| ST-0438 | Run a measure that needs a running service, within one time limit | standard | 3 | A measure with a `ready` command runs its `ready` command first, never overlaps a second run of the same measure, and stops with exit 2 when the time limit runs out. | ST-0436 runs the measuring commands. Adds the `ready` commands, the time limit over all commands, and the lock per measure. |
| ST-0439 | Get the same verdict in the gate-check step and at the merge | standard | 3 | The gate-check step and `premerge-check` call `crap-score --base`, so a story that changes only scripts without an ending is scored at the merge and its report stays in the primary checkout. | `premerge-check` passes the `.py` files of the diff and a threshold; the agent text runs `crap-score` in the foreground. Changes the call, the report folder, and the agent text. |

### Testability Assessment

All goals produce observable outcomes: the exit code and the output of `crap-score`, the report file, the rows in `GATE_OUTPUT`, and the exit code of `premerge-check`. Contract tests call the judging functions through `load_script` with planted rows, so a test can set a score of 8.004 or 9.006 exactly. Integration tests run `crap-score` and `premerge-check` as subprocesses on temporary repositories with stub measuring commands, and run the real template on a small temporary project. The background job of the implementation agent has one red flag, because no script sees how an agent starts a command. CG-04-LN-01 checks the text, and CG-08-IT-01 checks the call of the real scripts at the merge.

### Ownership Resolution

| Contract                                                                                                                                                               | .feature Rule                                                                                                           | Owner   | Rationale                                                 |
| ---------------------------------------------------------------------------------------------------------------------------------------------------------------------- | ----------------------------------------------------------------------------------------------------------------------- | ------- | --------------------------------------------------------- |
| CG-03-IT-01 to CG-03-IT-05: the template's rows, qualified names, scripts without an ending, non-zero exit, `parse_error`                                              | crap-gate-setup.feature#User measures each part of the code with a measuring command the project owns                   | ST-0435 | introduces the template                                   |
| CG-03-LN-01, CG-03-LN-02: the template holds the tool code and names no `.agent-factory/` path                                                                         | crap-gate-setup.feature#User measures each part of the code with a measuring command the project owns                   | ST-0435 | introduces the template                                   |
| CG-03-LN-03: `crap-score` holds no language-specific code                                                                                                              | crap-gate-setup.feature#User measures each part of the code with a measuring command the project owns                   | ST-0436 | removes the tool code from `crap-score`                   |
| CG-04-CT-01 to CG-04-CT-03, CG-04-CT-05, CG-04-CT-06, CG-04-CT-08, CG-04-CT-09: formula, rounding, judged lines, filter, settings, call, report name, glob             | crap-gate-setup.feature#Implementation agent gets one verdict for the functions a story changed                         | ST-0436 | introduces the new judging and the settings reader        |
| CG-04-CT-04, CG-04-CT-07: duplicate rows and rows in the wrong shape                                                                                                   | crap-gate-setup.feature#Implementation agent gets one verdict for the functions a story changed                         | ST-0437 | introduces the checks of the report                       |
| CG-04-IT-01 to CG-04-IT-05, CG-04-IT-07, CG-04-IT-09 to CG-04-IT-12: the verdict on real diffs, `--all`, repeat runs, exit 2, report, folder, `parse_error`, revisions | crap-gate-setup.feature#Implementation agent gets one verdict for the functions a story changed                         | ST-0436 | introduces the new `crap-score`                           |
| CG-12-LN-01: `crap-score/SKILL.md` names no tool and no threshold                                                                                                      | crap-gate-setup.feature#Factory maintainer reads one CRAP gate contract in every Factory document                       | ST-0436 | rewrites the skill                                        |
| CG-12-LN-04: ADR-0003 and arc42 § 5 name exit 2 of `crap-score`                                                                                                        | crap-gate-setup.feature#Factory maintainer reads one CRAP gate contract in every Factory document                       | ST-0436 | first to ship exit 2; the text exists from the spec phase |
| CG-04-IT-06: the measures run in list order, `ready` first, also for a disabled gate that a story names                                                                | crap-gate-setup.feature#Implementation agent gets one verdict for the functions a story changed                         | ST-0438 | introduces the `ready` commands                           |
| CG-04-IT-08: the time limit covers the whole gate run                                                                                                                  | crap-gate-setup.feature#Implementation agent gets one verdict for the functions a story changed                         | ST-0438 | introduces the time limit                                 |
| CG-04-IT-13 to CG-04-IT-16: the lock per measure with a `ready` command                                                                                                | crap-gate-setup.feature#Implementation agent gets one verdict for the functions a story changed                         | ST-0438 | introduces the lock                                       |
| CG-04-LN-01: the gate-check step runs `crap-score` as a background job with `--base` and `--report-dir`                                                                | crap-gate-setup.feature#Implementation agent gets one verdict for the functions a story changed                         | ST-0439 | rewrites the gate-check text                              |
| CG-08-CT-01, CG-08-IT-01, CG-08-IT-02: `premerge-check` passes `--base`, scores scripts without an ending, measures the branch head                                    | crap-gate-setup.feature#Implementation agent merges a story only when crap-score measures and passes at its branch head | ST-0439 | changes the built call                                    |
| CG-08-IT-06, CG-08-IT-07: the report of a refused merge stays in the primary checkout; the feature merge runs no `crap-score`                                          | crap-gate-setup.feature#Implementation agent merges a story only when crap-score measures and passes at its branch head | ST-0439 | changes the report folder and the feature merge           |

## E3: Accept a function above the threshold, and keep agents out of the register

### Why this EPIC exists

Some old functions score above the threshold at full coverage. Take a legacy function of complexity 9 and a threshold of 8: a one-line fix inside it fails, and no test can change that. This EPIC lets a person accept such a function in the exceptions register, and it keeps every agent from writing that file. A later change that raises the score fails again, so an exception never hides new risk.

### Actor Goals

- User accepts a function above the threshold in the exceptions register
- User keeps agents from writing the exceptions register

### Demo

1. On `story/ST-0350`, the changed function `tree_severity` scores 9 at the threshold 8, and `crap-score --base feature/login` exits 1.
2. The User adds a row for `packages/factory/scripts/finding-lint`, `tree_severity`, accepted score 9, with a reason, to `docs/findings/exceptions.md` and commits it on `dev`.
3. The User runs `crap-score --base feature/login` again. It exits 0, and the output names `tree_severity` as `accepted` with `9.00` and the reason.
4. An agent tries `tee docs/findings/exceptions.md`. `guard-human-fields` refuses the call, and the file stays unchanged.
5. `finding-lint` passes on `docs/findings/` with the register present.

### Scope

**In:**

- `crap-score` reads the register from `dev` through git, also from a linked worktree. It reads only the table of `## CRAP score`. A row on a story branch has no effect, and a repository without the file or without `dev` has no exceptions (BR-132).
- The accept rule: a judged function above the threshold gets `accepted` when a row names its file and qualified name and its rounded score is at or below the accepted score. The output prints every accepted function with its score and reason.
- A row with an empty cell or a non-numeric score, and two rows for one function, make `crap-score` exit 2 and name the rows (DEC-38).
- `guard-human-fields` refuses a write, an edit, and a shell redirect into the register in the payload format of each supported CLI, and lets an agent read it (BR-092).
- `finding-lint` and the stop notice skip `docs/findings/exceptions.md` by name.

**Out:**

- Any row in the register. The setup writes none, and no story writes one.
- A section for the mutation gate.

### Dependencies

E2, for ST-0440. ST-0441 has no dependency and can start with E1.

### Boundaries

- Code: `packages/factory/scripts/crap-score`, `packages/factory/config/hooks/guard-human-fields`, `packages/factory/scripts/finding-lint`, `stop_notice` in `packages/factory/scripts/dispatch_lib.py`
- Contracts: BR-092, BR-132, [entity-model.md § CRAP Gate Entities](../docs/spec/entity-model.md#crap-gate-entities) (`EXCEPTIONS_REGISTER`, `EXCEPTION_ROW`)
- Tests: `tests/factory/test_guard_human_fields.py`, `test_finding_lint.py`, `test_finding_stop.py`, `test_crap_gate_judging.py`, `test_crap_gate_score.py`

### Domain Rules

- Only a person writes the exceptions register. The Factory refuses an agent's write through any tool.
- A row counts only once a person has committed it on `dev`.
- The accepted score is the score the person saw. The gate compares the score rounded to two decimals, half up.
- `crap-score` ignores every section of the register except `## CRAP score`.

### Size

2 stories.

### Building-Block Inventory

| Story   | Capability                                       | Tier     | Spawns | Goal                                                                                                                                                                   | Basis                                                                                                                                                        |
| ------- | ------------------------------------------------ | -------- | ------ | ---------------------------------------------------------------------------------------------------------------------------------------------------------------------- | ------------------------------------------------------------------------------------------------------------------------------------------------------------ |
| ST-0440 | Accept a function above the threshold on `dev`   | standard | 3      | A changed function above the threshold passes as `accepted` when a row on `dev` names it at or above its rounded score, and the output shows the score and the reason. | ST-0436 judges without a register. Adds the reader from `dev`, the parser, the accept rule, and exit 2 for broken rows.                                      |
| ST-0441 | Keep agents from writing the exceptions register | standard | 2–3    | An agent's write, edit or shell redirect into `docs/findings/exceptions.md` is refused in every supported CLI, and `finding-lint` and the stop notice ignore the file. | `guard-human-fields` guards the human fields of findings; `finding-lint` treats every file in `docs/findings/` as a finding. Adds the register path to both. |

### Testability Assessment

All goals produce observable outcomes: the exit code and the output of `crap-score`, the refusal of `guard-human-fields` with the file unchanged, and the exit code of `finding-lint`. Contract tests call the parser and the accept rule with planted rows. Integration tests commit the register on `dev`, on the story branch, or on both, and run `crap-score` from a linked worktree. `guard-human-fields` runs with the tool payloads of each supported CLI. No red flag.

### Ownership Resolution

| Contract                                                                              | .feature Rule                                                                                  | Owner   | Rationale                            |
| ------------------------------------------------------------------------------------- | ---------------------------------------------------------------------------------------------- | ------- | ------------------------------------ |
| CG-05-CT-01: the parser reads only `## CRAP score` and names broken or duplicate rows | crap-gate-setup.feature#User accepts a function above the threshold in the exceptions register | ST-0440 | introduces the parser                |
| CG-05-CT-02: the accept rule with rounding half up                                    | crap-gate-setup.feature#User accepts a function above the threshold in the exceptions register | ST-0440 | introduces the accept rule           |
| CG-05-IT-01: the register is read from `dev`; a row on the story branch has no effect | crap-gate-setup.feature#User accepts a function above the threshold in the exceptions register | ST-0440 | introduces the read from `dev`       |
| CG-06-IT-01, CG-06-IT-02: the guard refuses writes and allows reads                   | crap-gate-setup.feature#User keeps agents from writing the exceptions register                 | ST-0441 | adds the register to the guard       |
| CG-06-CT-01, CG-06-CT-02: `finding-lint` and the stop notice skip the register        | crap-gate-setup.feature#User keeps agents from writing the exceptions register                 | ST-0441 | adds the register to both skip lists |

## E4: Stop a story when the gate cannot measure, and resume it without new code

### Why this EPIC exists

When the gate cannot measure, for example because a Compose stack is stopped, nobody has judged the code. A developer agent then has nothing to fix, and a counted attempt would punish the story for a fault in the setup. This EPIC stops the story as `blocked` without an attempt, on both ways and at both run points. After a person fixes the setup, `dispatch resume-gates` returns the story to the gate-check step with its code unchanged. `dispatch init` also refuses to start a run while a `ready` command fails.

### Actor Goals

- Implementation agent stops a story without a counted attempt when the gate cannot measure
- Implementation agent merges a story only when crap-score measures and passes at its branch head (the Scenarios of exit 3 and of `ready` commands before the test suite)
- User resumes a story blocked by a gate that cannot measure without new code
- User starts a run only when every ready command of an enabled gate passes

### Demo

1. In a temporary project, the measure `backend` has the `ready` command `scripts/crap-ready-backend`. The User runs `dispatch init --mode by-hand --feature-branch feature/login --stories ST-0350` while the stub exits 1. `dispatch init` refuses and names `backend` and the command. No branch and no ledger exist.
2. The stub exits 0, and the run starts. ST-0350 has one counted attempt.
3. The stub exits 1 again. In the gate-check step, `crap-score` exits 2. The implementation agent runs `dispatch mark-blocked ST-0350 --reason "gate cannot measure: crap-score"`. `dispatch status` shows ST-0350 `blocked` with one attempt.
4. The User fixes the stub and says to continue. The agent runs `dispatch resume-gates ST-0350`. `dispatch status` shows ST-0350 `dispatched` with one attempt, and no developer agent starts.
5. The gate-check step passes. `dispatch merge-story ST-0350` merges the story.
6. In a second case, the stub fails during `dispatch merge-story`. `premerge-check` exits 3 before the test suite, its refusal starts with `GATE CANNOT MEASURE: crap-score`, and `merge-story` sets the story `blocked`.

### Scope

**In:**

- `implementation-agent.md`: on exit 2 in the gate-check step, the agent spawns no developer agent, counts no attempt, runs `dispatch mark-blocked <id> --reason "gate cannot measure: crap-score"`, and names the gate, the measure and the message in the stop (BR-116, DEC-03). `mark-blocked --reason` exists in `dispatch` today.
- `premerge-check` runs the `ready` command of every measure of an enabled gate, and of a disabled gate that the story names, before the test suite. A failure makes it exit 3 at once (BR-136, DEC-39).
- `premerge-check` exits 3 when `crap-score` exits 2 and every other check passes, and its refusal starts with `GATE CANNOT MEASURE: crap-score`. With another failed check, it exits 1.
- `dispatch merge-story` turns exit 3 into `blocked` with the reason `gate cannot measure: crap-score`, on both ways (BR-124).
- `dispatch resume-gates <id>`: the ledger edge ResumeGates from `blocked` to `dispatched` in `dispatch_lib.py`. It accepts only the exact reason, keeps the attempts, `attempt_grants`, the branch and the worktree, writes no manifest and no brief, and is refused while a stop holds (BR-135, DEC-07, DEC-22).
- `implementation-agent.md`: after the User's go, the agent runs `resume-gates` and then the gate-check step; it uses `re-dispatch` when the code must change.
- `dispatch init` runs the `ready` command of every measure of an enabled gate once, from the primary checkout, before it cuts the branch or writes the ledger. A failure makes it exit 1 and leaves nothing behind (BR-137, DEC-23).
- The tests that this EPIC changes: `LIFECYCLE_EDGES` in `test_run_lifecycle_ledger.py` gains ResumeGates (RL-06-CT-01), and the stop causes of RL-06-IT-01 gain their rows.

**Out:**

- A general check that all pieces are in place before a run.
- Any change to the rule that exit 1 costs an attempt.

### Dependencies

E2: exit 2, the `ready` commands, and the report come from ST-0436 and ST-0438.

### Boundaries

- Code: `packages/factory/scripts/dispatch`, `packages/factory/scripts/dispatch_lib.py`, `packages/factory/scripts/premerge-check`
- Documents: `packages/factory/agents/implementation-agent.md`, `packages/factory/rulebooks/conventions/dispatch-contract.md` where it lists the subcommands
- Contracts: [§ dispatch](../docs/spec/interface-contracts.md#agent-factoryfactoryscriptsdispatch), [§ premerge-check](../docs/spec/interface-contracts.md#agent-factoryfactoryscriptspremerge-check), [§ Ledger Entry Lifecycle](../docs/spec/state-machines.md#ledger-entry-lifecycle) (event ResumeGates), QS-31
- Tests: `tests/factory/test_run_lifecycle_ledger.py`, `test_run_lifecycle_dispatch.py`, `test_finding_stop.py`, new `test_crap_gate_dispatch.py`, `test_crap_gate_premerge.py`, `test_crap_gate_journey.py`, `test_crap_gate_text.py`

### Domain Rules

- A gate that cannot measure never costs an attempt (QS-31).
- `blocked` has four causes: a merge conflict, a refresh conflict, a red test suite after the merge, and a gate that cannot measure.
- The ledger `reason` of the fourth cause is the fixed text `gate cannot measure: crap-score`.
- `resume-gates` never changes code and never starts a developer agent. `re-dispatch` stays the way back for a story whose code must change.
- When a `ready` command fails at the merge, neither the test suite nor a gate runs.

### Size

4 stories.

### Building-Block Inventory

| Story   | Capability                                                       | Tier     | Spawns | Goal                                                                                                                                                                         | Basis                                                                                                                                                    |
| ------- | ---------------------------------------------------------------- | -------- | ------ | ---------------------------------------------------------------------------------------------------------------------------------------------------------------------------- | -------------------------------------------------------------------------------------------------------------------------------------------------------- |
| ST-0442 | Stop a story in the gate-check step when the gate cannot measure | economy  | 2      | On exit 2 in the gate-check step, the story becomes `blocked` with the reason `gate cannot measure: crap-score`, its attempts stay unchanged, and no developer agent starts. | `mark-blocked --reason` exists; the agent text treats every gate failure as a fix for a developer agent. Adds the exit-2 rule to the text and its tests. |
| ST-0443 | Block a story at the merge when the gate cannot measure          | strong   | 3–4    | `premerge-check` exits 3 when the gate cannot measure or a `ready` command fails before the suite, and `merge-story` sets the story `blocked` on both ways.                  | `premerge-check` exits 1 or 2, and `merge-story` keeps the story `dispatched` on any refusal. Adds the `ready` run, exit 3, and its handling.            |
| ST-0444 | Resume a blocked story with `dispatch resume-gates`              | standard | 3      | After the setup is fixed, `dispatch resume-gates ST-0350` sets the story `dispatched` with its attempts and branch, and the next step is the gate-check step.                | `dispatch` has `re-dispatch` and no edge from `blocked` to `dispatched`. Adds the subcommand, the edge, its guard, and the agent text.                   |
| ST-0445 | Refuse to start a run while a `ready` command fails              | standard | 2–3    | `dispatch init` runs each `ready` command of an enabled gate once and refuses to start, naming the measure and the command, when one fails.                                  | `dispatch init` runs no `ready` command. Adds the run before the branch and the ledger are written.                                                      |

### Testability Assessment

All goals produce observable outcomes: the ledger state and the attempt count that `dispatch status` shows, the exit codes of `premerge-check` and `dispatch`, the refusal text, and the absence of a branch or a ledger after a refused `init`. Integration tests run `dispatch` and `premerge-check` as subprocesses with `ready` stubs that exit 0 or 1. One end-to-end test runs the whole journey by hand on a temporary repository. The agent's choice not to spawn a developer agent has one red flag; CG-07-LN-01 checks the text, and CG-08-IT-03 shows that `premerge-check` and `merge-story` set `blocked` by themselves when the agent misses it.

### Ownership Resolution

| Contract                                                                                            | .feature Rule                                                                                                           | Owner   | Rationale                                        |
| --------------------------------------------------------------------------------------------------- | ----------------------------------------------------------------------------------------------------------------------- | ------- | ------------------------------------------------ |
| CG-07-LN-01: the agent text marks exit 2 `blocked` and spawns no developer agent                    | crap-gate-setup.feature#Implementation agent stops a story without a counted attempt when the gate cannot measure       | ST-0442 | introduces the exit-2 rule                       |
| CG-07-IT-01: `mark-blocked` with the reason keeps the attempts and the branch on both ways          | crap-gate-setup.feature#Implementation agent stops a story without a counted attempt when the gate cannot measure       | ST-0442 | first to exercise the fourth cause               |
| CG-08-IT-03, CG-08-IT-04: exit 3 and `blocked`, or exit 1 beside another failed check               | crap-gate-setup.feature#Implementation agent merges a story only when crap-score measures and passes at its branch head | ST-0443 | introduces exit 3                                |
| CG-08-IT-05, CG-08-IT-08: a failed `ready` command stops `premerge-check` before the suite          | crap-gate-setup.feature#Implementation agent merges a story only when crap-score measures and passes at its branch head | ST-0443 | introduces the `ready` run at the merge          |
| CG-09-CT-01, CG-09-IT-01 to CG-09-IT-03: the ResumeGates guard, the return, `re-dispatch`, the stop | crap-gate-setup.feature#User resumes a story blocked by a gate that cannot measure without new code                     | ST-0444 | introduces `resume-gates`                        |
| CG-09-LN-01: the agent text runs `resume-gates` and then the gate-check step                        | crap-gate-setup.feature#User resumes a story blocked by a gate that cannot measure without new code                     | ST-0444 | introduces the text                              |
| CG-08-E2-01: one run by hand from a failing gate through `blocked` and `resume-gates` to the merge  | crap-gate-setup.feature#Implementation agent merges a story only when crap-score measures and passes at its branch head | ST-0444 | completes the journey; needs ST-0442 and ST-0443 |
| CG-10-IT-01 to CG-10-IT-03: `dispatch init` runs the `ready` commands of an enabled gate            | crap-gate-setup.feature#User starts a run only when every ready command of an enabled gate passes                       | ST-0445 | introduces the `ready` run of `init`             |

## E5: Set up the CRAP gate in a project through the test-strategy agent

### Why this EPIC exists

The gate is only as good as the numbers it reads. A measuring command that reports false coverage, or that measures another folder's code, passes every story. This EPIC gives the test-strategy agent a setup skill that tries tools on real files and proposes exclusions, and a proof script that plants an untested and a tested function. The gate must catch the first and pass the second before a person enables it. The person decides every value.

### Actor Goals

- User sets up the CRAP gate through the test-strategy agent and decides every value
- Test-strategy agent checks with gate-setup-proof that the measuring command reports true coverage
- Factory maintainer reads one CRAP gate contract in every Factory document (the index entry and `test-strategy-agent.md`)

### Demo

1. In a small temporary Python project, the User asks the test-strategy agent to set up the CRAP gate. The agent runs the skill `setup-crap-score`.
2. The agent proposes a measure `python` from the template, tried on one real file, with a threshold of 8 and a time limit. After the User confirms, it writes the entry with `enabled: false`.
3. The agent runs `gate-setup-proof --measure python --plant <folder>`. The output names the checks "Repeatable", "Catches CRAP", "Sees the folder" and "Reports a gap", all passing, and the proof exits 0.
4. The agent runs `crap-score --all` and reports the number of failing functions and the run time. The User confirms the threshold 8 and a `timeout_minutes` at least the run time.
5. The agent sets `enabled: true` and commits the setup once.

### Scope

**In:**

- `gate-setup-proof --measure <name> --plant <folder>`: a temporary worktree at `.current-work/gate-setup-proof/worktree`, a first commit with the working tree's setup files and `base/`, a second commit with `gap/`, the four checks, exit 0, 1 or 2, and no trace on the project's branches (BR-138, DEC-06, DEC-30, DEC-32, DEC-46). The check of the planted complexities runs before the checks are judged (DEC-31).
- The skill `packages/factory/skills/setup-crap-score/SKILL.md` with its seven steps, the candidate table for Python and TypeScript/JavaScript, the duty to try a tool on a real file, the exclusions with reasons, the planted code, the pause points, and one commit at the end. It refers to `crap-score/SKILL.md` and does not repeat it (BR-139, DEC-01, DEC-08).
- `test-strategy-agent.md` calls the skill, runs the proof and `crap-score --all` during setup, and runs no gate on a story. Its completion criteria lose the claim that no gate ran.
- The generated index lists `setup-crap-score`.
- The test that this EPIC changes: `test_st_0357_never_runs_a_gate` in `test_core_artifact_ownership_text.py`.

**Out:**

- The setup of this repository (E6).
- Tried tools for languages other than Python and TypeScript.

### Dependencies

E2: the proof runs the new `crap-score`, and CG-02-IT-08 runs the template of ST-0435. E5 needs neither E3 nor E4.

### Boundaries

- Code: new script in `packages/factory/scripts/` (`gate-setup-proof`)
- Documents: `packages/factory/skills/setup-crap-score/`, `packages/factory/agents/test-strategy-agent.md`, `packages/factory/INDEX.yaml`
- Contracts: [§ gate-setup-proof](../docs/spec/interface-contracts.md#agent-factoryfactoryscriptsgate-setup-proof), BR-138, BR-139, BR-023, BR-029
- Tests: `tests/factory/test_core_artifact_ownership_text.py`, new `test_crap_gate_proof.py`, `test_crap_gate_text.py`

### Domain Rules

- An agent may set a gate up, but only a script may say whether a story's code passes it.
- The gate has no default. The agent proposes and tries, and the person chooses tools, exclusions, threshold and time limit.
- The planted functions have the same complexity, at or below the threshold, so only coverage decides them.
- The proof leaves the project's branches and worktree list as they were.
- The setup writes no register row and no commit hook, and commits once, after the person confirms the start of the gate.

### Size

3 stories. Phase 3 split the proof into its four checks and its refusals, so no story needs more than three spawns.

### Building-Block Inventory

| Story   | Capability                                                              | Tier     | Spawns | Goal                                                                                                                                                         | Basis                                                                                                                          |
| ------- | ----------------------------------------------------------------------- | -------- | ------ | ------------------------------------------------------------------------------------------------------------------------------------------------------------ | ------------------------------------------------------------------------------------------------------------------------------ |
| ST-0446 | Check a measuring command with the four checks of `gate-setup-proof`    | strong   | 3      | `gate-setup-proof` passes an honest measuring command and fails each lying one in exactly the check it breaks, and leaves the branches as they were.         | No proof script exists; E2 ships the new `crap-score` and the template. Adds the script and its tests.                         |
| ST-0447 | Refuse a wrong call or wrong planted code in `gate-setup-proof`         | standard | 2      | `gate-setup-proof` exits 2, names the cause, and runs no check for a wrong call or planted code that coverage alone cannot decide.                           | ST-0446 runs the checks. Adds the refusals.                                                                                    |
| ST-0448 | Set up the gate with `setup-crap-score` through the test-strategy agent | standard | 3      | The test-strategy agent runs `setup-crap-score`, writes the entry only after confirmation, runs the proof and `crap-score --all`, and enables the gate last. | The test-strategy agent proposes a threshold by hand and runs no gate. Adds the skill, edits the agent, regenerates the index. |

### Testability Assessment

The proof's goal produces observable outcomes: its exit code, the named checks in its output, the branch tips and `git worktree list` afterwards. Integration tests run the real proof and the real `crap-score` with an honest stub, four faulty stubs and six cases of wrong planted code. The setup skill's goal has a red flag, because it describes what an agent does: no script sees whether the agent tried a tool or waited for confirmation. Text checks own those Scenarios, and the proof stands behind them (QA strategy § Behaviour that needs a real agent session).

### Ownership Resolution

| Contract                                                                                                                    | .feature Rule                                                                                                             | Owner   | Rationale                     |
| --------------------------------------------------------------------------------------------------------------------------- | ------------------------------------------------------------------------------------------------------------------------- | ------- | ----------------------------- |
| CG-02-IT-01, CG-02-IT-03, CG-02-IT-05 to CG-02-IT-08, CG-02-IT-10, CG-02-IT-11: the four checks, the worktree, the branches | crap-gate-setup.feature#Test-strategy agent checks with gate-setup-proof that the measuring command reports true coverage | ST-0446 | introduces `gate-setup-proof` |
| CG-02-IT-02, CG-02-IT-04, CG-02-IT-09: the threshold from `docs/testing.yaml`, a wrong call, wrong planted code             | crap-gate-setup.feature#Test-strategy agent checks with gate-setup-proof that the measuring command reports true coverage | ST-0447 | introduces the refusals       |
| CG-02-CT-01: the check of the planted complexities                                                                          | crap-gate-setup.feature#Test-strategy agent checks with gate-setup-proof that the measuring command reports true coverage | ST-0447 | introduces the check          |
| CG-02-LN-01: the skill writes planted functions that coverage alone decides                                                 | crap-gate-setup.feature#Test-strategy agent checks with gate-setup-proof that the measuring command reports true coverage | ST-0448 | writes the skill text         |
| CG-01-LN-01 to CG-01-LN-05: tools, candidate table, pause points, no register row or hook, one commit                       | crap-gate-setup.feature#User sets up the CRAP gate through the test-strategy agent and decides every value                | ST-0448 | introduces the skill          |
| CG-12-LN-02: the generated index lists `setup-crap-score`                                                                   | crap-gate-setup.feature#Factory maintainer reads one CRAP gate contract in every Factory document                         | ST-0448 | adds the skill to the index   |
| CG-12-LN-03: `test-strategy-agent.md` runs the setup and no gate on a story                                                 | crap-gate-setup.feature#Factory maintainer reads one CRAP gate contract in every Factory document                         | ST-0448 | edits the agent text          |

## E6: Run the CRAP gate on this repository for Python and TypeScript

### Why this EPIC exists

The setup in this repository is the acceptance test that the gate works in any language. This repository has Python scripts without an ending, 21 scripts that start with `uv run`, and TypeScript tests that run with `node:test` and no `package.json`. This EPIC runs after `feature/crap-gate-setup` merges into `dev` and `update-factory` installs the new scripts (DEC-49). During implementation, `dispatch` and `premerge-check` run from the installed copy, so a gate entry in the new form would meet the old scripts.

### Actor Goals

- Factory maintainer runs the CRAP gate on this repository for Python and TypeScript

### Demo

1. After `update-factory`, the test-strategy agent runs the installed `setup-crap-score` on this repository.
2. The installed `gate-setup-proof` passes for the measure `python` and for the measure `typescript`. `crap-score --all` reports the failing functions and the run time. Step 6 writes the run time as `measured_minutes` into `docs/testing.yaml` (DEC-19).
3. `docs/testing.yaml` shows `gates.crap-score` with `enabled: true`, a threshold, `measured_minutes`, a `timeout_minutes` at least `measured_minutes`, and the two measures.
4. In the next run, a story that changes `packages/factory/scripts/finding-lint` gets its changed function scored at the merge.

### Scope

**In:**

- The setup run of the installed `setup-crap-score` on this repository, with the values the User confirms.
- This repository's Python measuring command, from the template, covering the scripts without an ending. Coverage reaches the `uv run` scripts, and none of them gets an exclusion (DEC-04).
- This repository's TypeScript measuring command with `node --test --experimental-test-coverage`.
- The entry `gates.crap-score` in `docs/testing.yaml` with `enabled: true`. The entry `mutation-testing`, the `dispatch` section and every suite stay.
- T-0402 in `docs/spec/work/todo.md` names `docs/proposals/crap-gate-setup.md` for the CRAP part and `docs/proposals/mutation-gate.md` for the mutation part.

**Out:**

- A `ready` command: this repository's tests start no service.
- Rows in the exceptions register. A person adds them later, when a change to an old function fails.

### Dependencies

E1 to E5, merged into `dev` through `feature/crap-gate-setup`, and an `update-factory` run that installs them (DEC-49). So E6 runs in its own run on `feature/crap-gate-self-host`, cut from `dev` after that install, outside the run of `feature/crap-gate-setup`.

### Boundaries

- Code: this repository's measuring commands (a project folder outside `packages/factory/` and `.agent-factory/`)
- Documents: `docs/testing.yaml`, `docs/spec/work/todo.md` (T-0402)
- Contracts: QS-31, DEC-04, the `gates` section schema
- Tests: new `tests/factory/test_crap_gate_repository.py`, `test_crap_gate_text.py`

### Domain Rules

- This repository's measuring commands refer to nothing under `.agent-factory/`.
- No script that starts with `uv run` is excluded.
- `timeout_minutes` is at least the run time of `crap-score --all` from setup step 6.
- No retained test runs a real measuring command against this repository's root.

### Size

1 story.

### Building-Block Inventory

| Story   | Capability                                                        | Tier     | Spawns | Goal                                                                                                                                                            | Basis                                                                                                                                                                          |
| ------- | ----------------------------------------------------------------- | -------- | ------ | --------------------------------------------------------------------------------------------------------------------------------------------------------------- | ------------------------------------------------------------------------------------------------------------------------------------------------------------------------------ |
| ST-0449 | Enable the CRAP gate on this repository for Python and TypeScript | standard | 3      | This repository's `docs/testing.yaml` enables `crap-score` with a measure `python` and a measure `typescript`, both proved, and every merge then runs the gate. | `gates.crap-score` has `enabled: false`, `threshold: 8`, and no measures; no measuring command exists; T-0402 names neither proposal. Runs the setup and writes both commands. |

### Testability Assessment

The goal produces observable outcomes: the entry in `docs/testing.yaml`, the exit code of the proof for each measure, and the rows the two measuring commands write on small temporary projects. Text checks read the entry and T-0402. Integration tests run the two commands on a planted `uv run --script` script and a planted `.ts` file. The run on the whole repository is a one-time check with no retained test, because a retained test would start the suite inside the suite. Its run time lives in `measured_minutes` in `docs/testing.yaml` (DEC-19).

### Ownership Resolution

| Contract                                                                                | .feature Rule                                                                                              | Owner   | Rationale              |
| --------------------------------------------------------------------------------------- | ---------------------------------------------------------------------------------------------------------- | ------- | ---------------------- |
| CG-13-LN-01: the entry, both measures, `measured_minutes` and `timeout_minutes`         | crap-gate-setup.feature#Factory maintainer runs the CRAP gate on this repository for Python and TypeScript | ST-0449 | writes the entry       |
| CG-13-IT-01: the Python command measures a `uv run --script` script                     | crap-gate-setup.feature#Factory maintainer runs the CRAP gate on this repository for Python and TypeScript | ST-0449 | introduces the command |
| CG-13-IT-02: the TypeScript command reports rows from `node:test`                       | crap-gate-setup.feature#Factory maintainer runs the CRAP gate on this repository for Python and TypeScript | ST-0449 | introduces the command |
| CG-13-IT-03: the proof passes for both measures on this repository (one-time setup run) | crap-gate-setup.feature#Factory maintainer runs the CRAP gate on this repository for Python and TypeScript | ST-0449 | runs the setup         |
| CG-12-LN-06: T-0402 names both proposals                                                | crap-gate-setup.feature#Factory maintainer reads one CRAP gate contract in every Factory document          | ST-0449 | edits T-0402           |
