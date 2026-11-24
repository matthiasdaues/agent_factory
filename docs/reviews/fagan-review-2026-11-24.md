---
type: fagan-review
title: Fagan inspection of feature/crap-gate-self-host
date: 2026-11-24
status: pass
reviewer: qa-agent
findings_filed: 0
story:
run: feature/crap-gate-self-host
branch: feature/crap-gate-self-host
branch_base: 634135fefd07cbbadd33acdfbc4e17de1e771706
branch_head: 94079fc1766d28a7bd11f3507a63771df71a880e
---

# Fagan inspection of feature/crap-gate-self-host

## Verdict

The feature passes the Fagan inspection. No code finding blocks, and the inspection filed no register file. Four notes stay in this report. The known minors IMPL-0102, IMPL-0104 and IMPL-0113, and the copy that a Ctrl-C leaves behind in `update-factory`, are not filed again.

The security review filed one blocking finding, SEC-0013, in `docs/reviews/security-review-2026-11-24.md`. So the feature goes back to the Implementation Agent before the merge into `dev`.

## Scope

The inspection covers `git diff dev...feature/crap-gate-self-host` from the merge base `634135fe` to `94079fc1`. It leaves out the 1.14 usage work that came in from `dev`. The units are ST-0451, BUG-0141, ST-0449 and BUG-0147.

The inspection read DEC-84 to DEC-87 and DEC-75 in `docs/proposals/crap-gate-setup.md`, BR-130 and BR-131 in `docs/spec/validation-rules.md`, the QA strategy `docs/spec/work/crap-gate-setup-qa-strategy.md`, the added Scenarios of `docs/spec/features/crap-gate-setup.feature`, and the four story reviews under `docs/reviews/`.

Inspected code files: `packages/factory/scripts/crap-score`, `packages/factory/skills/setup-crap-score/crap-measure-python`, `scripts/crap-measure-python`, `scripts/crap-measure-typescript`, `docs/testing.yaml`, `packages/factory/scripts/init-factory`, `packages/factory/scripts/update-factory`, `packages/factory/scripts/trigger`, `packages/factory/scripts/validate`, and `tests/select_tests.py` as the command that `SELECT_COMMAND` starts. The test files of the diff were read for the contract check below.

## Test run

Each test file of the feature ran in the guardrail form `uv run --directory <worktree> pytest -q -n auto tests/factory/<file>.py`. All eight exit 0: `test_crap_gate_score`, `test_crap_gate_template`, `test_crap_gate_repository`, `test_crap_gate_text`, `test_update_factory`, `test_usage_capture_paths`, `test_trigger` and `test_validate`.

## Focus areas

**Correctness.** `crap-score` sets `GATE_SCOPE` and `GATE_CHANGED_FILES` as DEC-84 says, from its own diff, and refuses a path with a line break. The paths come from the same `parse_diff` that judges the rows, so the measure and the judging see one set of paths. The template measures and traces only the changed files that `GATE_FILES` and `GATE_EXCLUDE` keep, and runs `SELECT_COMMAND` with every changed path appended (DEC-85). The update path keeps the runtime and its marker through a failed build, and a rollback puts the copy back (BUG-0147). One message gap of the narrow trace is filed by the bug hunt as BUG-0149.

**Clean Architecture.** `crap-score` still holds no language-specific code; it only hands over two variables. The measuring commands name no path under `.agent-factory/`, as CG-13-LN-01 checks.

**SOLID.** No violation with a concrete cost. `provision_usage_runtime` returns a state and a cause, and `_report_usage_state` prints them, so the two callers share one report rule.

**Maintainability.** The new functions are small. `scripts/crap-measure-python` equals the template apart from `TEST_COMMAND` and `SELECT_COMMAND`, so a later change of the template must be copied by hand. ST-0449 states this choice, and the code review of ST-0449 accepted it.

**Consistency.** See the notes N-2 and N-3.

**YAGNI.** No unused abstraction found. `include_pattern` escapes `,` and `]` for paths that this repository does not hold, but the code review of ST-0451 asked for it, and it costs eight lines.

## Contract-to-test check

ST-0449 and ST-0451 are governed by `crap-gate-setup.feature`, so the `test-design-pass` field does not apply. Every traced contract of both stories has a test with its `spec` marker: CG-03-IT-04, CG-03-IT-06 to CG-03-IT-10, CG-04-IT-18, CG-13-LN-01 to CG-13-LN-03, CG-13-IT-01 and CG-13-IT-02. CG-13-IT-03 has no retained test, and the QA strategy justifies that: it is the one-time setup run behind `measured_minutes`. The testability probe of the epic named no red flag that stays open.

## Findings

| Finding                                                                                                                                                                                                                                                                                                                                                                                                                      | Artifact                                                               | Category   | Severity | Filed as    |
| ---------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- | ---------------------------------------------------------------------- | ---------- | -------- | ----------- |
| N-1: `SELECT_COMMAND` puts the changed paths after `--run` without `--`. A changed file at the root named like an option, such as `-h`, makes `select_tests.py` print its help and run no test. The measure then exits 1 because coverage recorded no data, so the gate fails closed. Put `--` before the paths, if a project with such names needs it.                                                                      | `packages/factory/skills/setup-crap-score/crap-measure-python:335-339` | suggestion | note     | report only |
| N-2: `SELECT_COMMAND` of this repository starts `python3`, the system Python 3.10 that DEC-86 names as unfit for the coverage hook. Each run with `GATE_SCOPE=changed` prints `Error in sitecustomize ... No module named 'tomllib'` before the tests start. The run is not harmed, because `select_tests.py` itself is not measured. Starting the selector with `uv run python` would remove the line from the gate output. | `scripts/crap-measure-python:137`                                      | suggestion | note     | report only |
| N-3: The header of `tests/select_tests.py` names the run-tests hook and `test_changed_command` as the users of `--run`, but not `SELECT_COMMAND` of the measure. A reader who changes the selector does not learn that the CRAP gate depends on it. Add the measure to that sentence.                                                                                                                                        | `tests/select_tests.py:22-24`                                          | suggestion | note     | report only |
| N-4: A story can change `scripts/crap-measure-python`, `scripts/crap-measure-typescript` or `tests/select_tests.py`, and the gate runs them from the story head. DEC-75 accepts this and leaves the guard to the code review and the scope check. The measure files of this repository are ordinary files that stories touch, so a code review should treat a change to them as a change to the gate.                        | `docs/testing.yaml:105-111`                                            | suggestion | note     | report only |

## Next step

The Implementation Agent fixes SEC-0013 and resubmits the feature for QA. The notes need no change before the merge.
