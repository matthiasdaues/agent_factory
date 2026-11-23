---
type: fagan-review
title: Fagan inspection of feature/crap-gate-trusted-source
date: 2026-11-23
status: pass
reviewer: qa-agent
findings_filed: 1
story:
run: feature/crap-gate-trusted-source
branch: feature/crap-gate-trusted-source
branch_base: 334f5a2e8e3a812954ca244442a432525606eefa
branch_head: b24253262df2322a27b87c2cb83982e352fc3e2f
---

# Fagan inspection of feature/crap-gate-trusted-source

## Result

The inspection files no `FAGAN` finding of its own. The code does what CG-14, BR-128 and DEC-67 to DEC-79 say, and the five focus areas hold. Two blocking findings of the other QA steps fall in the code under inspection, and their files hold the detail:

- [QA-0403](../findings/QA-0403.md), `major`: two Examples rows of CG-14 have no test. The contract-to-test check below found it, and the bug-hunt report owns it.
- [SEC-0009](../findings/SEC-0009.md), `major`: the reader follows replace refs. The security report owns it.

The inspection records five notes. Next, the implementation agent adds QA-0403 and SEC-0009 as units of work.

## Scope

The inspection covers `git diff 334f5a2e..a3c7b47e` of `feature/crap-gate-trusted-source`, 40 files. The code is in two files. It read the section `# --- trusted gate source` of `packages/factory/scripts/crap-score` in full, together with `main`, `parse_register`, the changed docstring, and the diff of `packages/factory/scripts/gate-setup-proof`. It read `tests/factory/test_crap_gate_trusted_source.py` and `tests/factory/test_crap_gate_trusted_proof.py` in the parts that the spec markers point to.

The governing sources are Rule CG-14 and the CG-02 and CG-04 Scenarios of `docs/spec/features/crap-gate-setup.feature`, BR-127, BR-128, BR-129, BR-131, BR-132 and BR-138, § `crap-score` and § Trusted gate source of `docs/spec/interface-contracts.md`, ADR-0041, DEC-67 to DEC-79 of `docs/proposals/crap-gate-setup.md`, and `docs/spec/work/crap-gate-setup-qa-strategy.md`. The decisions count as settled.

The inspection does not file again the open minors IMPL-0095, IMPL-0097, IMPL-0099 and T-0430. It leaves the four stale sentences about the `HEAD` check to the reconciliation step: `crap-score/SKILL.md`, ADR-0041, arc42 § 5.2.3 and the DSL.

## Acceptance test

The project declares no Gherkin runner, so each Scenario traces to a pytest test through the `spec` marker. The inspection ran the two test files of the feature and the ten other test files of the CRAP gate:

```bash
uv run --directory /home/matthiasdaues/Documents/datenschoenheit/agent_factory/.current-work/feature/crap-gate-trusted-source/invocation pytest -q -x tests/factory/test_crap_gate_trusted_source.py tests/factory/test_crap_gate_trusted_proof.py
uv run --directory /home/matthiasdaues/Documents/datenschoenheit/agent_factory/.current-work/feature/crap-gate-trusted-source/invocation pytest -q tests/factory/test_crap_gate_dispatch.py tests/factory/test_crap_gate_journey.py tests/factory/test_crap_gate_judging.py tests/factory/test_crap_gate_lock.py tests/factory/test_crap_gate_premerge.py tests/factory/test_crap_gate_proof.py tests/factory/test_crap_gate_score.py tests/factory/test_crap_gate_template.py tests/factory/test_crap_gate_text.py tests/factory/test_crap_score.py
```

The runs printed `57 passed in 17.12s` and `324 passed in 109.72s`. No Scenario with a test fails.

## Story checks

| Check                         | Result                                                                                                                                                                                                                                                                                                                                                                              |
| ----------------------------- | ----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| `test-design-pass` field      | Not applicable. ST-0450 traces three Rules of `crap-gate-setup.feature`, and IMPL-0098 is a finding fixed inside CG-14, so both units are `.feature`-governed.                                                                                                                                                                                                                      |
| Contract-to-test cross-check  | Every test ID that ST-0450 traces has a test with its `spec` marker: CG-14-CT-01 to CG-14-CT-03, CG-14-IT-01 to CG-14-IT-10, CG-14-LN-01, CG-04-IT-17 and CG-02-IT-12 to CG-02-IT-14. Within CG-14-IT-07, the Examples rows `v1.10.0` and `origin/main` of "Broken gate settings on the integration branch cannot measure" have no case. That is [QA-0403](../findings/QA-0403.md). |
| Testability flags of the EPIC | `backlog/epics-crap-gate-setup.md` gives E3 no red flag, so nothing needs follow-up.                                                                                                                                                                                                                                                                                                |

## Spec compliance

| Source                                             | Code                                                                                                                                                                                                                                  | Result |
| -------------------------------------------------- | ------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- | ------ |
| DEC-67, DEC-72: one reader for every trusted value | `main` reaches the threshold, the patterns and the register only through `TrustedGateSource.gate_values` and `exceptions`. `apply_trusted` replaces `files`, `exclude` and `threshold` and keeps `command` and `ready`.               | holds  |
| DEC-68, DEC-77: the key from the `--base` revision | `open_source` passes the resolved commit to `integration_branch`, and `_settings_text` reads the file with `git show <commit>:docs/factory-settings.yaml`. The folder is read only without `--base` or with `--settings-from-folder`. | holds  |
| DEC-69, DEC-70, DEC-75: the join by measure name   | `join_values` takes the branch patterns for a named measure, the folder patterns with a notice for a new one, and exits 2 for a dropped one.                                                                                          | holds  |
| DEC-74, DEC-76, DEC-77: broken values exit 2       | Each case raises `GateError` before `measure_all`, so no command starts. The scratch runs of the bug hunt show the messages for a tag, a remote ref, `refs/heads/dev`, `--help` and an empty value.                                   | holds  |
| DEC-78: `--base` resolved once, branch before tag  | `resolve_base` tries `refs/heads/<base>` through `show-ref --verify`, and the commit feeds both the diff and the key.                                                                                                                 | holds  |
| DEC-79: the `HEAD` check only with `--base`        | `open_source` sets `refuse_head_tip=base is not None`.                                                                                                                                                                                | holds  |
| DEC-71, DEC-73: the proof                          | `run_gate` adds `--settings-from-folder`, and `run_gates` copies `docs/factory-settings.yaml` of the working tree into the first commit when it exists.                                                                               | holds  |
| BR-132: the register                               | `GitRefSource.exceptions` reads the register from the tip of the integration branch and names the branch in every message of `parse_register`.                                                                                        | holds  |

## Notes

| Finding                                                                                                                                                                                                                                                                                                                        | Artifact                                                | Category   | Type          | Severity | Filed as      |
| ------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------ | ------------------------------------------------------- | ---------- | ------------- | -------- | ------------- |
| YAGNI check: `TrustedGateSource` is an abstract class with one production backend. DEC-72 asks for exactly this seam, and `TestBackend` of CG-14-CT-02 uses it to check that the gate logic reaches no other source. It is no speculative generality.                                                                          | `packages/factory/scripts/crap-score:899-913`           | suggestion | structure     | note     | `report only` |
| `apply_trusted` raises `GateError` when the source returns no pattern for a measure of the folder. `GitRefSource` never does that, because `join_values` maps every folder measure. The check guards the interface for a second backend, so it stays.                                                                          | `packages/factory/scripts/crap-score:1048-1056`         | suggestion | checking      | note     | `report only` |
| `main` reads every trusted value before `measure_all` starts the first measuring command. So story code in a command cannot change the values of the same run. It can change them for a later run through a replace ref, which SEC-0009 covers.                                                                                | `packages/factory/scripts/crap-score:1300-1309`         | suggestion | timing        | note     | `report only` |
| `_branch_tip`, `_resolve` and `_is_branch_name` call `subprocess.run` directly, next to the `git` helper, because they need the exit code. The fix of SEC-0009 must touch the helper and the calls of `_branch_tip` and `_resolve`, which read refs and objects, or move them behind one helper with a flag for the exit code. | `packages/factory/scripts/crap-score:937-948,1059-1078` | suggestion | structure     | note     | `report only` |
| Three lines that the feature added to the module docstring run past 79 characters: lines 16, 25 and 62, such as "that git does not accept as a branch name exits 2 (DEC-77). enabled, timeout_minutes, and the". The rest of the new text wraps at 76.                                                                         | `packages/factory/scripts/crap-score:16,25,62`          | suggestion | documentation | note     | `report only` |

## Repeat pass at c0ae79bd

The repeat pass covers `git diff a3c7b47e..c0ae79bd`: the fixes of SEC-0009, QA-0403, SEC-0011 and SEC-0012, with DEC-80 to DEC-82. The Fagan inspection files no blocking finding at the new head, so its status is `pass`. The blocking [BUG-0137](../findings/BUG-0137.md) of the bug hunt sits in the new code of `premerge-check`, and the bug-hunt report owns it.

The changed test files pass at the new head:

```bash
uv run --directory /home/matthiasdaues/Documents/datenschoenheit/agent_factory/.current-work/feature/crap-gate-trusted-source/invocation pytest -q tests/factory/test_crap_gate_trusted_source.py tests/factory/test_crap_gate_trusted_proof.py tests/factory/test_crap_gate_premerge.py tests/factory/test_premerge_check.py tests/factory/test_crap_gate_score.py tests/factory/test_crap_score.py
```

The run printed `235 passed in 77.71s`.

| Prior finding                     | Check at the new head                                                                                                                                                                                                                                                                                 | Status                               |
| --------------------------------- | ----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- | ------------------------------------ |
| [QA-0403](../findings/QA-0403.md) | `test_cg_14_broken_settings_on_the_branch_cannot_measure` has the cases of a tag `v1.10.0` and of `refs/remotes/origin/main`. Both values exit 2 in `/tmp/claude-1000/-home-matthiasdaues-Documents-datenschoenheit-agent-factory/89fd1670-49e4-4a59-97db-e1035150aa04/scratchpad/qa/repeat-crap.sh`. | `resolved`, set by the unit's review |

In the cases that the bug hunt ran, the new code holds to DEC-80 to DEC-82. BUG-0137 is the one exception. `crap-score` builds every git call through `git_argv`. `premerge-check` reads `enabled` and the entry from `refs/heads/dev` through `show-ref --verify`, with the same options. The inspection files one register file:

| Finding                                                                                                                                                                                                                                                                                                                                           | Artifact                                          | Category   | Type      | Severity | Filed as                                                |
| ------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- | ------------------------------------------------- | ---------- | --------- | -------- | ------------------------------------------------------- |
| The options `-c core.useReplaceRefs=false --no-replace-objects` exist twice, in `git_argv` of `crap-score` and in `_hardened_git_text` of `premerge-check`, and no test compares them. The review of SEC-0009 already had to change the first copy once. `in_use: false`, `harms_downstream: false`, `fails_purpose: false`, `raises_cost: true`. | `packages/factory/scripts/premerge-check:891-902` | suggestion | structure | minor    | [FAGAN-0035](../findings/register/code/FAGAN-0035.json) |

`premerge-check` reads the fixed `dev`, while DEC-80 says "the integration branch". The code review of SEC-0011 already raised that question, and BR-066 now names `refs/heads/dev`. So the inspection does not file it again.

## Repeat pass at b2425326

The diff `c0ae79bd..b2425326` holds the fix of BUG-0137 in `premerge-check`, its tests, and its confirmed drift rows in DEC-83, the interface contracts and the validation rules. The inspection files no new finding, so its status stays `pass`. The bug hunt found that the fix makes the feature merge crash on a `gates` section that is no mapping. The bug-hunt report owns that finding, [BUG-0138](../findings/BUG-0138.md). FAGAN-0035 stays open in the register.
