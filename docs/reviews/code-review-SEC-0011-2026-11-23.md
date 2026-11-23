---
type: code-review
title: Code review of SEC-0011, premerge-check reads whether the CRAP gate runs from dev
date: 2026-11-23
status: pass
reviewer: code-review-agent
findings_filed: 0
story: SEC-0011
run:
branch: story/SEC-0011
branch_base: 65d6e61b2b9e6c8676ca27a10af1a9089a265d5c
branch_head: 9b1938c41bc707a834a19df0d7453a6560f1fa76
---

# Code review of SEC-0011, premerge-check reads whether the CRAP gate runs from dev

## Verdict

SEC-0011 passes the code review, and the review files no new finding. The status of [SEC-0011](../findings/SEC-0011.md) is now `resolved`. A story can no longer switch its CRAP gate off or on through its own `docs/testing.yaml`. The story's `quality-gates` field still adds the gate. The read of `dev` uses `show-ref --verify` and the hardening of SEC-0009. The review records one note and asks the stakeholder one question.

Next, the developer agent commits this report and the changed status of SEC-0011 on `story/SEC-0011`. Then the implementation agent runs the gate-check step. The orchestrator records DEC-82 in the Appendix and answers the question below.

## Scope

The review covers the diff `65d6e61b..9b1938c4`, the one commit `9b1938c4`. It changes four files:

- `packages/factory/scripts/premerge-check`:
  - `trusted_crap_entry` reads `gates.crap-score` of `docs/testing.yaml` at the tip of `refs/heads/dev`.
  - `resolve_gates` takes `enabled` and the existence of the entry from that read.
  - `crap_cannot_measure` gives exit `3` without `dev` when the head holds an entry.
  - `_parse_testing_yaml` and `_entries_of` split the old readers, so both the head and `dev` use one parser.
- `tests/factory/test_crap_gate_premerge.py`: five new tests `test_sec_0011_*`, and `dev_testing` for the fixture `_build_repo`.
- `tests/factory/test_premerge_check.py`: the fixtures commit a `dev`.
- `docs/spec/work/spec-feedback-SEC-0011.md`: four drift rows.

The review read SEC-0011, DEC-80 and DEC-81 in the Appendix of `docs/proposals/crap-gate-setup.md`, BR-066, BR-136 and BR-137, and the callers of the gate entries in `premerge-check` and `dispatch`.

## Checks

### The read of dev

`trusted_crap_entry` resolves the tip with `git show-ref --verify --hash refs/heads/dev`, so no tag, remote ref or revision expression stands in for the branch (DEC-78). It reads the file with `git show <tip>:docs/testing.yaml`. Both calls go through `_hardened_git_text`, which runs `git -c core.useReplaceRefs=false --no-replace-objects`, the same argv as `git_argv` of `crap-score`. The old keys such as `crap_score` count on `dev` too, because `_entries_of` maps them.

### The probe

QA's probe `probe-enabled.py` calls `resolve_gates` in a folder without git. With the fix, such a folder has no `dev`, so the probe no longer separates the cases. The review wrote its own probe, `/tmp/claude-1000/-home-matthiasdaues-Documents-datenschoenheit-agent-factory/89fd1670-49e4-4a59-97db-e1035150aa04/scratchpad/sec0011/probe_gates.py`. Each case builds a git repository with `dev` and a checked-out story branch, then calls `resolve_gates` and `crap_cannot_measure`. "Before" is `premerge-check` at `65d6e61b`, and "after" is `premerge-check` at `9b1938c4`.

| Case                                                                     | Before       | After                             |
| ------------------------------------------------------------------------ | ------------ | --------------------------------- |
| `dev` enabled, head `enabled: false`                                     | no gate      | `crap-score`                      |
| `dev` enabled, head without the entry                                    | no gate      | `crap-score`                      |
| `dev` enabled, head enabled                                              | `crap-score` | `crap-score`                      |
| `dev` `enabled: false`, head enabled                                     | `crap-score` | no gate                           |
| `dev` and head `enabled: false`, `quality-gates: [crap-score]`           | `crap-score` | `crap-score`                      |
| `dev` without the entry, head enabled                                    | `crap-score` | no gate                           |
| `dev` enabled, a replace ref turns `dev` off, `core.useReplaceRefs true` | no gate      | `crap-score`                      |
| no `dev`, head enabled                                                   | `crap-score` | no gate, cannot measure, exit `3` |
| no `dev`, head `enabled: false`                                          | no gate      | no gate, cannot measure, exit `3` |
| no `dev`, head without the entry                                         | no gate      | no gate                           |
| no `dev`, a tag `dev` at the head with `enabled: false`                  | no gate      | no gate, cannot measure, exit `3` |

The first two rows are the attack of SEC-0011, and the gate now runs. The fourth and sixth rows are the accepted limit: a gate that only the head adds runs only once `dev` holds it. The fifth row shows that `quality-gates` still forces the gate (BR-066). In the seventh row, a replace ref on the file of `dev` does not turn the gate off, and the tag in the last row does not stand in for the branch.

End to end, `test_sec_0011_dev_enabled_gate_runs_when_the_story_disables_it` runs the real `premerge-check` and sees `crap-score` start. `test_sec_0011_dev_enabled_gate_runs_when_the_story_removes_its_entry` sees exit `1` with "no entry gates.crap-score", the accepted refusal. `test_sec_0011_no_dev_with_a_head_entry_cannot_measure` sees exit `3`.

### The other callers

- `dispatch init` runs the `ready` commands through `_ready_refusal` and `ready_commands` of `dispatch_lib`. It reads `docs/testing.yaml` of the primary checkout before a story exists (BR-137). It does not call `resolve_gates`, and the commit does not change it.
- In `premerge-check`, `not_set_up_notice`, `check_story_gates` and the run of the `ready` commands still read the head entries. They take `command`, `ready` and the measures from the head, as DEC-75 keeps them. Only the list of gates comes from `dev`.
- `resolve_gates` has one caller, `main`.

### The changed fixtures

In `test_premerge_check.py`, `_dev_holds` commits the files of the folder as `dev` before `resolve_gates` runs. `_build_repo` does the same with the given `docs/testing.yaml`. So the head and `dev` hold the same file. Each changed test still checks what it checked before: the gate list from enabled entries, the old keys, the `quality-gates` field, the conditional gates, and the warning for both keys. These tests do not separate the head from `dev`, and the five `test_sec_0011_*` tests do. In `test_crap_gate_premerge.py`, the fixtures that expect a CRAP run now pass the same file as `dev_testing`, so their result is the same as before.

### Tests

The six files of the merge path passed 262 tests. Eleven more files that run `premerge-check` or `dispatch merge-story` passed 372 tests.

## Findings

| Finding                                                                                                                                                                                                                                                                                               | Artifact                                      | Category   | Type          | Severity | Basis                                                                                    | Filed as    |
| ----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- | --------------------------------------------- | ---------- | ------------- | -------- | ---------------------------------------------------------------------------------------- | ----------- |
| The docstring of `crap_cannot_measure` and two rows of `spec-feedback-SEC-0011.md` cite DEC-82, but the Appendix of `docs/proposals/crap-gate-setup.md` ends at DEC-81 on this branch and on the feature branch. A reader who follows the reference finds no decision. Record DEC-82 in the Appendix. | `packages/factory/scripts/premerge-check:922` | suggestion | documentation | note     | `in_use: false`, `harms_downstream: false`, `fails_purpose: false`, `raises_cost: false` | report only |

## Question for the stakeholder

DEC-80 says that `premerge-check` reads `enabled` "from `docs/testing.yaml` on the integration branch". The code reads the fixed `dev`, as DEC-68 keeps it for `premerge-check`. The Fix line of SEC-0011 asked for the branch that `crap-score` reads through `integration_branch`. The two choices differ for a project that sets `integration_branch: main` and has no branch `dev`.

Take such a project, where `main` holds `gates.crap-score` with `enabled: true`:

- **With the fixed `dev`, as built:** a story that removes the entry from its `docs/testing.yaml` merges with no CRAP gate and exit `0`. The probe row "no `dev`, head without the entry" shows the same outcome. A story that keeps the entry always gets exit `3`, also when the entry is disabled.
- **With the branch that `integration_branch` names:** `premerge-check` reads the key from the target revision and the entry from `main`. The story that removes the entry would then get the gate and exit `1`, as on a project with `dev`. The review did not build this option.

The review recommends the second option. It closes SEC-0011 for every project that the key exists for, and `crap-score` already holds the reader. The answer changes `trusted_crap_entry`, DEC-80 or DEC-68, and BR-136.

## Focus areas

| Focus area         | Result                                                                                                                                                                                              |
| ------------------ | --------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| Correctness        | The code matches DEC-80 as the coordinator stated it (the fixed `dev`), BR-066 for `quality-gates`, and the exit `3` of DEC-82. The question names the gap between the text of DEC-80 and the code. |
| Clean Architecture | The decision of which gates run stays in `resolve_gates`. The commands of the gates still come from the head.                                                                                       |
| SOLID              | `trusted_crap_entry` reads, and `crap_cannot_measure` decides. Each does one thing.                                                                                                                 |
| Maintainability    | `_hardened_git_text` repeats the argv of `git_argv` of `crap-score`, because the two scripts share no git module. A later change of the hardening must change both.                                 |
| Consistency        | The messages follow the pattern of the existing refusals. The new tests use the fixtures of the file.                                                                                               |

## Verification

```bash
uv run --directory /home/matthiasdaues/Documents/datenschoenheit/agent_factory/.current-work/feature/crap-gate-trusted-source/story/SEC-0011 pytest -q -n auto tests/factory/test_crap_gate_premerge.py tests/factory/test_premerge_check.py tests/factory/test_run_lifecycle_premerge.py tests/factory/test_crap_gate_trusted_source.py tests/factory/test_crap_gate_journey.py tests/factory/test_crap_gate_dispatch.py
uv run --directory /home/matthiasdaues/Documents/datenschoenheit/agent_factory/.current-work/feature/crap-gate-trusted-source/story/SEC-0011 python /tmp/claude-1000/-home-matthiasdaues-Documents-datenschoenheit-agent-factory/89fd1670-49e4-4a59-97db-e1035150aa04/scratchpad/sec0011/probe_gates.py /home/matthiasdaues/Documents/datenschoenheit/agent_factory/.current-work/feature/crap-gate-trusted-source/story/SEC-0011/packages/factory/scripts/premerge-check
```

The first command passed 262 tests on `9b1938c4`. The second prints the rows of [The probe](#the-probe). The copy of `premerge-check` at `65d6e61b` lies next to the probe as `premerge-check-old`.
