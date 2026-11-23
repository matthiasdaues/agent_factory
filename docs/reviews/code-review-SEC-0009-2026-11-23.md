---
type: code-review
title: Code review of SEC-0009, crap-score ignores replace refs
date: 2026-11-23
status: pass
reviewer: code-review-agent
findings_filed: 0
story: SEC-0009
run:
branch: story/SEC-0009
branch_base: 4e3917dfe4b86d51ac2cecbc8fd5c5fe98272f55
branch_head: a023c2c66977d0124ddab3d406eb94b89c51c0d9
---

# Code review of SEC-0009, crap-score ignores replace refs

## Verdict

SEC-0009 does not pass the code review, and the finding stays `open`. The fix closes the route that QA reported. A second route reopens it: one call of `git config core.useReplaceRefs true` in the shared repository. On git 2.34.1, this config key overrides `--no-replace-objects`. With the key set, the forged threshold 30 of `dev` again gives exit `0`. A scratch repository reproduces this.

The review files no new finding, because the gap is the same defect as SEC-0009 and its fix lies on the same line. The review added the reproduction and the corrected fix to [SEC-0009](../findings/SEC-0009.md).

Next, the developer agent changes `git_argv` to `["git", "-c", "core.useReplaceRefs=false", "--no-replace-objects", *args]` and adds a test with the config key set. Then the code review of SEC-0009 runs again.

## Scope

The review covers the diff `4e3917df..eee1ed20`, one commit `eee1ed20`. It changes three files:

- `packages/factory/scripts/crap-score`: the new function `git_argv`, and five git calls that now use it.
- `tests/factory/test_crap_gate_trusted_source.py`: two new tests. One puts a replace ref on the `docs/testing.yaml` blob of `dev`, and the other puts one on its `docs` tree with a forged register row.
- `docs/spec/work/spec-feedback-SEC-0009.md`: one drift row for § Trusted gate source.

The review read [SEC-0009](../findings/SEC-0009.md) and [security-review-2026-11-23.md](security-review-2026-11-23.md). QA's probes `probe-replace.sh` and `probe-replace-worktree.sh` were no longer in the scratchpad folder, so the review wrote its own probe. It covers both QA cases and the settings that the coordinator asked about.

## Every git call goes through git_argv

`crap-score` runs git in five places: the helper `git`, `_is_branch_name`, `_resolve`, `_branch_tip` and `current_branch`. Each now builds its argument vector with `git_argv`. The helper `git` carries every other call, also the merge base, the diff, `ls-tree`, `show` and `--git-common-dir`. The one other process start in the script, the `Popen` in the measuring code, runs the project's command and not git. From `dispatch_lib`, `crap-score` imports only `glob_match`, which starts no process.

## The probes

The probe is `/tmp/claude-1000/-home-matthiasdaues-Documents-datenschoenheit-agent-factory/89fd1670-49e4-4a59-97db-e1035150aa04/scratchpad/sec0009/probe.sh`. It takes the path of `crap-score` and the name of a case. In its repository, `dev` holds the threshold 8 and an empty register. The story changes `f`, which scores 12, so the true verdict is exit `1`. "Before" is `crap-score` at `4e3917df`, and "after" is `crap-score` at `eee1ed20`.

| Case          | What the story agent does                                                                                                         | Before                        | After                          |
| ------------- | --------------------------------------------------------------------------------------------------------------------------------- | ----------------------------- | ------------------------------ |
| `blob`        | `git replace` of the `docs/testing.yaml` blob of `dev` with threshold 30                                                          | `PASS`, exit `0`              | `FAIL`, exit `1`               |
| `tree`        | `git replace` of the `docs` tree of `dev` with a register row for `f`, run in a detached linked worktree as `premerge-check` uses | `ACCEPTED … forged`, exit `0` | `FAIL`, exit `1`               |
| `blob-config` | the `blob` case, plus `git config core.useReplaceRefs true`                                                                       | `PASS`, exit `0`              | `PASS`, threshold 30, exit `0` |
| `blob-base`   | the replace ref under `refs/replace-x/`, and `GIT_REPLACE_REF_BASE=refs/replace-x/` in the environment                            | `PASS`, exit `0`              | `FAIL`, exit `1`               |
| `alt-env`     | the `blob` case with an empty `GIT_NO_REPLACE_OBJECTS` in the environment                                                         | `FAIL`, exit `1`              | `FAIL`, exit `1`               |
| `graft`       | a `.git/info/grafts` file that makes the story head a commit without a parent                                                     | exit `2`, merge base fails    | exit `2`, merge base fails     |

The `blob-config` row is the gap. The review checked it with git directly in the same repository, which holds the replace ref and the config key:

```text
$ git --no-replace-objects show dev:docs/testing.yaml | grep threshold
    threshold: 30
$ GIT_NO_REPLACE_OBJECTS=1 git show dev:docs/testing.yaml | grep threshold
    threshold: 30
$ git -c core.useReplaceRefs=false show dev:docs/testing.yaml | grep threshold
    threshold: 8
```

```text
the story agent runs git replace <blob of dev> <blob with threshold 30>
        ↓
the agent runs git config core.useReplaceRefs true, which the git guard passes
        ↓
both entries land in the shared git directory, so the worktree of premerge-check sees them
        ↓
git 2.34.1 reads the config key after the option and turns replace refs back on
        ↓
GitRefSource reads the forged blob, and crap-score exits 0 with the threshold 30
```

The guard `packages/factory/config/hooks/block-dangerous-git.sh` has no rule for `git config` or `git replace`. A command-line `-c` setting wins over every config file, so `-c core.useReplaceRefs=false` closes the route. The review checked this with a patched copy of `crap-score` whose `git_argv` adds the setting. The cases `blob-config`, `blob` and `tree` then give `FAIL` and exit `1`. The review ran only git 2.34.1 and did not check other versions.

Every other setting that the review tried leaves the fix intact:

- `GIT_REPLACE_REF_BASE` moves only the place where git looks for replace refs, and the option turns that lookup off.
- An empty `GIT_NO_REPLACE_OBJECTS` turns nothing on.
- A grafts file makes `git merge-base` fail, so the gate exits `2` and passes nothing. That holds before and after the fix.

## The new tests

The two new tests replace a blob and a tree of `dev` and assert the true verdict. Both pass. The `blob` and `tree` probes show that the same cases forge the verdict without the option. Neither test sets `core.useReplaceRefs`, so neither catches the gap above. The test of the corrected fix sets the key with `git config core.useReplaceRefs true` before it writes the replace ref.

## Findings

| ID or finding                                                                                                                                                                                             | Artifact                                      | Category   | Severity | Status or filed as | Blocks |
| --------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- | --------------------------------------------- | ---------- | -------- | ------------------ | ------ |
| [SEC-0009](../findings/SEC-0009.md): `core.useReplaceRefs=true` in the shared config reopens the replace route. Fix: add `-c core.useReplaceRefs=false` in `git_argv`, and add one test with the key set. | `packages/factory/scripts/crap-score:646-653` | defect     | major    | `open`, annotated  | yes    |
| The drift row of `docs/spec/work/spec-feedback-SEC-0009.md` says that the reader ignores replace refs through `--no-replace-objects`. After the corrected fix, the row also names the config setting.     | `docs/spec/work/spec-feedback-SEC-0009.md`    | suggestion | note     | report only        | no     |

SEC-0009 keeps its severity and rating from the security review. This review changes only the record of the fix.

## Focus areas

| Focus area         | Result                                                                                                                                                                        |
| ------------------ | ----------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| Correctness        | The fix closes the route of SEC-0009 as QA reported it. The config key reopens it. The corrected fix changes `git_argv` only.                                                 |
| Clean Architecture | One function builds every git call, so the corrected fix changes one line.                                                                                                    |
| SOLID              | `git_argv` does one thing.                                                                                                                                                    |
| Maintainability    | The docstring of `git_argv` names SEC-0009 and says that every git call goes through it. The two tests use the `repo` fixture and a raw git helper for the replace step.      |
| Consistency        | The five call sites keep their `cwd`, `capture_output` and `check` arguments. The error message of the helper `git` still prints the arguments without the prefix, as before. |

## Verification

```bash
uv run --directory /home/matthiasdaues/Documents/datenschoenheit/agent_factory/.current-work/feature/crap-gate-trusted-source/story/SEC-0009 pytest -q -n auto tests/factory/test_crap_gate_trusted_source.py tests/factory/test_crap_gate_score.py tests/factory/test_crap_gate_judging.py tests/factory/test_crap_gate_proof.py tests/factory/test_crap_gate_premerge.py
```

The run passed 271 tests on `eee1ed20`. The probe is the script named in [The probes](#the-probes). The copy of `crap-score` at `4e3917df` and the patched copy lie next to it, as `crap-score-old` and `crap-score-patched`.

## Repeat pass, 2026-11-23

The repeat pass finds no open blocking finding, so SEC-0009 now passes the code review. The status of [SEC-0009](../findings/SEC-0009.md) is now `resolved`, and the review files no new finding. The frontmatter now names `a023c2c6` as `branch_head` and `pass` as `status`.

Next, the developer agent commits this report and the changed status of SEC-0009 on `story/SEC-0009`. Then the implementation agent runs the gate-check step.

### Scope of the repeat pass

The pass covers only `eee1ed20..a023c2c6`:

- `c226795a`: the first pass of this report and the annotation of SEC-0009.
- `a023c2c6`: the fix.
  - `git_argv` now returns `["git", "-c", "core.useReplaceRefs=false", "--no-replace-objects", *args]`, and its docstring names the reason.
  - The new test `test_cg_14_a_repository_setting_use_replace_refs_does_not_raise_the_threshold` sets `core.useReplaceRefs true` before it writes the replace ref, and it asserts exit `1` with the threshold 8.
  - The drift row of `docs/spec/work/spec-feedback-SEC-0009.md` now names the config setting, as the note of the first pass asked.

### The probes again

The probe `/tmp/claude-1000/-home-matthiasdaues-Documents-datenschoenheit-agent-factory/89fd1670-49e4-4a59-97db-e1035150aa04/scratchpad/sec0009/probe.sh` now has five more cases. Each case turns replace refs back on from one more config scope that git reads. The column "Option only" uses `crap-score` at `eee1ed20`, which runs git with `--no-replace-objects` alone. The column "Fix" uses `crap-score` at `a023c2c6`. The true verdict is `FAIL` and exit `1`.

| Case          | Where `core.useReplaceRefs=true` or the forgery comes from                                                      | Option only      | Fix                        |
| ------------- | --------------------------------------------------------------------------------------------------------------- | ---------------- | -------------------------- |
| `blob`        | no config; a replace ref on the `docs/testing.yaml` blob of `dev`                                               | `FAIL`, exit `1` | `FAIL`, exit `1`           |
| `tree`        | no config; a replace ref on the `docs` tree of `dev`, run in a detached linked worktree                         | `FAIL`, exit `1` | `FAIL`, exit `1`           |
| `blob-config` | the repository config `.git/config`                                                                             | `PASS`, exit `0` | `FAIL`, exit `1`           |
| `wt-config`   | `extensions.worktreeConfig true` and `git config --worktree` in a detached linked worktree, where the gate runs | `PASS`, exit `0` | `FAIL`, exit `1`           |
| `include`     | `include.path` in `.git/config`, pointing to a file in the git directory that sets the key                      | `PASS`, exit `0` | `FAIL`, exit `1`           |
| `global`      | `GIT_CONFIG_GLOBAL` pointing to a file that sets the key                                                        | `PASS`, exit `0` | `FAIL`, exit `1`           |
| `env-count`   | `GIT_CONFIG_COUNT=1` with `GIT_CONFIG_KEY_0` and `GIT_CONFIG_VALUE_0` in the environment                        | `PASS`, exit `0` | `FAIL`, exit `1`           |
| `env-params`  | `GIT_CONFIG_PARAMETERS` in the environment                                                                      | `PASS`, exit `0` | `FAIL`, exit `1`           |
| `blob-base`   | `GIT_REPLACE_REF_BASE` pointing to another ref folder                                                           | not run          | `FAIL`, exit `1`           |
| `alt-env`     | an empty `GIT_NO_REPLACE_OBJECTS`                                                                               | not run          | `FAIL`, exit `1`           |
| `graft`       | a `.git/info/grafts` file                                                                                       | not run          | exit `2`, merge base fails |

Every scope that reopened the route under the option alone is closed by the `-c` setting. That covers the repository config, the worktree config, an include, the global config, and the two environment forms. So the command-line setting wins over every scope that the review tried. A story agent can write the first three scopes from the shared git directory. The global config and the environment of `premerge-check` come from the person who runs `dispatch`, not from the story. The review ran only git 2.34.1 and did not check other versions.

### Other checks of the new diff

- Every git call still goes through `git_argv`. The commit adds no new process start.
- The message of the helper `git` still prints the arguments without the prefix, so a failure such as "git merge-base … failed" reads as before.
- The new test runs in the `repo` fixture, under `tmp_path`, so its `git config` reaches no other repository.

### Findings of the repeat pass

| ID                                  | Severity | Status     | Blocks |
| ----------------------------------- | -------- | ---------- | ------ |
| [SEC-0009](../findings/SEC-0009.md) | major    | `resolved` | no     |

The verification command of [Verification](#verification) passed 272 tests on `a023c2c6`. That is one more than in the first pass, which is the new test. The copy of `crap-score` at `eee1ed20` lies next to the probe as `crap-score-option-only`.
