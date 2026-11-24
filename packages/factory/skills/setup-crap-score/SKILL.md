---
name: setup-crap-score
description: Set up the CRAP gate in a project once — try tools on real files, propose measures, exclusions, a threshold and a time limit, check them with gate-setup-proof, and enable the gate only after the User confirms each value.
category: quality
---

# Set up the CRAP gate

Read [factory-voice.md](../../rulebooks/conventions/factory-voice.md) now and hold every rule as a writing constraint. No prose reaches terminal output or a file until it passes all four gates and clears the final pass.

The CRAP gate `crap-score` judges the functions that a story changed. It needs the entry `gates.crap-score` in `docs/testing.yaml` and one measuring command per part of the code. This skill writes both, once per project. The test-strategy agent runs it, and a person can also call it directly (BR-139).

At each step, the agent brings a proposal that it has tried, and the User decides: the tools, the exclusions, the threshold, and the time limit. The skill names no default threshold and no default time limit. Setup is finished when the User enables the gate.

[crap-score/SKILL.md](../crap-score/SKILL.md) describes the gate: the settings, the measurement format, the formula, the exit codes, the exceptions register, and where the gate runs. Read it before step 1. This skill refers to it and does not repeat it (DEC-01).

## What the setup writes

| File                                                                     | Written in                       | Committed |
| ------------------------------------------------------------------------ | -------------------------------- | --------- |
| The entry `gates.crap-score` in `docs/testing.yaml`                      | step 4, changed in steps 6 and 7 | step 7    |
| One measuring command per measure, such as `scripts/crap-measure-python` | step 4                           | step 7    |
| A `ready` command for a measure that tests against a running service     | step 4                           | step 7    |
| The plant under `.current-work/gate-setup-proof/plant/<name>/`           | step 5                           | never     |

The setup writes no row of the exceptions register `docs/findings/exceptions.md`, because only the stakeholder writes it (BR-092). The setup writes no commit hook for the gate. A CRAP run starts the test suite, so the gate runs in the gate-check step and at the merge, never in a commit hook (DEC-05). The setup also proposes no test hook, because test hooks belong to the project (BR-029).

The setup proposes the test commands of the measuring commands, and the project owns them once the User confirms (BR-023). No measuring command, `ready` command, or tool configuration that the setup writes names a path under the Factory's install folder. So a person can run each command without the Factory by setting `GATE_OUTPUT`.

Run the Factory scripts `.agent-factory/factory/scripts/gate-setup-proof` and `.agent-factory/factory/scripts/crap-score` from the root of the project.

## Step 1 — Read the project

Read the languages, the test commands, and the suites from `docs/testing.yaml`, which `detect-test-regime` writes. When the file is missing, run `detect-test-regime` first.

Plan one measure per language, such as `python` for the suite `python` and `typescript` for the suite `typescript`. A language whose code has two parts with different test commands, such as a backend and a command-line tool, gets one measure per part. Each measure gets a `name`, a `files` pattern, and later a `command`.

## Step 2 — Choose a tool for each language

The table names the tools that the Factory has tried for each language:

| Language              | Complexity                    | Coverage                                                           |
| --------------------- | ----------------------------- | ------------------------------------------------------------------ |
| Python                | `radon`, `lizard`             | coverage.py                                                        |
| TypeScript/JavaScript | ESLint `complexity`, `lizard` | Vitest or Jest with v8; `node --test --experimental-test-coverage` |

Take the first candidate of the row and run it on a real file of the project before you propose it. Show the User what the tool reported: the functions, their complexity, their line ranges, and the coverage. When the tool fails on the file or misses functions, try the next candidate. A project that runs its TypeScript tests with `node:test` and has no `package.json` takes `node --test --experimental-test-coverage`.

For a language outside the candidate table, the agent looks up tools that report per-function complexity with line ranges and per-line or per-function coverage. It tries each proposed tool on a real file of the project in the same way, and it names in the proposal where it found the tool.

For Python, the Factory template `crap-measure-python` next to this file holds the `radon` and coverage.py code. When the project has scripts that start through `uv run --script`, check on one of them that coverage reaches it. Such scripts get no exclusion (DEC-04).

Propose the tools of each measure and wait for the User's choice.

## Step 3 — Find what must be excluded

Look for code whose measurement depends on local state, and for code that the tests cannot reach. Propose exclusions, each with a reason. Database migrations are one example: the coverage of `packages/server/backend/src/db/alembic/versions/` depends on the state of a local database, so the agent proposes the pattern `"**/db/alembic/versions/**"` with that reason.

An exclusion is a glob pattern in the `exclude` list of its measure. Propose no exclusion without a reason, and never exclude a file only because its score is high. A function that stays above the threshold for a good reason belongs in the exceptions register, which a person writes.

## Step 4 — Write the configuration

Write the measuring command of each measure:

- **Python:** copy the template `crap-measure-python` into the project, such as `scripts/crap-measure-python`, and keep it executable. Fill its constant `TEST_COMMAND` with the project's test command from step 1, one list item per argument, such as `["uv", "run", "pytest", "--quiet"]`. The template measures only the files that the measure keeps: it reads the `files` and `exclude` patterns from `GATE_FILES` and `GATE_EXCLUDE`, which `crap-score` sets, one pattern per line. So an exclusion from step 3 also keeps an untested script from stopping the measure (DEC-65). With `GATE_SCOPE` `changed`, the template measures only the paths of `GATE_CHANGED_FILES` that the measure keeps. When the project has a command that runs only the tests of given paths, fill the constant `SELECT_COMMAND` with it, such as `["python3", "tests/select_tests.py", "--run"]`. With `changed`, the template then runs it with the changed paths appended; with an empty `SELECT_COMMAND`, or with `all`, it runs `TEST_COMMAND`. The template hands pytest a `--basetemp` in its own work folder and `-p no:cacheprovider` through `PYTEST_ADDOPTS`, so a run leaves no pytest temp folder behind (DEC-84, DEC-85).
- **Another language:** write a command that writes the rows of [crap-score/SKILL.md § Measurement format](../crap-score/SKILL.md#measurement-format) to the path in `GATE_OUTPUT`, with the tools from step 2. It may read `GATE_FILES` and `GATE_EXCLUDE` to leave out the files the measure drops, and `GATE_SCOPE` and `GATE_CHANGED_FILES` to measure only the changed files. A tool that comes from a package registry, such as ESLint from npm, comes from a lock file that the project commits, which pins every dependency with its hash. The command installs it without install scripts, such as `npm ci --ignore-scripts`, into a cache outside the repository, and never through a call that resolves versions at run time, such as `npx --yes`. Otherwise every gate run may execute code that was published after the setup (SEC-0013).

The header of each measuring command names its duty: when the command cannot measure a case, it exits non-zero and names the cause, and it never reports such a file as 0 % covered (BR-130). The Python template already holds that header.

A measure whose tests need a running service, such as a Compose stack, gets a `ready` command. It exits `0` when the measuring command can run now and any other code when it cannot, and it measures nothing. A project whose tests need no running service has no `ready` line.

Propose a threshold and a time limit, each with its reason. The time limit `timeout_minutes` covers every `ready` command and every measuring command of one run together. Base the first proposal on the run time of the project's test commands, because each measuring command runs the tests. Step 6 measures the real run time.

The agent shows the change to `docs/testing.yaml` as a diff, with the measures, the exclusions, the threshold, and the time limit, and it writes the file only after the User confirms. It writes the entry `gates.crap-score` with `enabled: false`, so the gate runs for no story while the setup is open (BR-066, DEC-18). When the User declines, `docs/testing.yaml` keeps its earlier content.

Commit nothing. The proof reads the files from the working tree (BR-138, DEC-32).

## Step 5 — Run the proof

Write the plant of each measure, then run the proof for it. The plant is the planted code and the planted tests for the language of the measure, in the folder `.current-work/gate-setup-proof/plant/<name>/`. The folder `plant/` keeps every measure name away from the proof's own worktree at `.current-work/gate-setup-proof/worktree`. It holds two subfolders, and each mirrors the layout of the project: the path of a file below the subfolder is its path in the proof worktree (DEC-28, DEC-30).

- `base/` holds one code file with the functions `proof_untested` and `proof_tested`, and a test file that covers `proof_tested` fully and does not call `proof_untested`. The code file must match the `files` pattern of the measure, and the test command must find the test file.
- `gap/` holds one test file with a failing test. It tests the duty of the measuring command to exit non-zero after a failed test run.

Coverage alone must decide the two planted functions (DEC-31). So give `proof_untested` and `proof_tested` the same complexity, at or below the threshold. `proof_untested` must score above the threshold at 0 % coverage: at complexity `c`, its score is `c × c + c`. For example, a function of complexity 3 scores 12 at 0 % coverage and 3 at full coverage, so with the threshold 8, `proof_untested` fails and `proof_tested` passes. A Python function with two `if` statements has the complexity 3:

```python
def proof_untested(value):
    if value > 10:
        return "large"
    if value > 0:
        return "small"
    return "none"
```

`proof_tested` has the same body, and its test calls it with `11`, `1`, and `0`.

Run the proof for each measure:

```bash
.agent-factory/factory/scripts/gate-setup-proof --measure <name> --plant .current-work/gate-setup-proof/plant/<name>/
```

The proof runs four checks in its own worktree: "Repeatable", "Catches CRAP", "Sees the folder", and "Reports a gap". It exits `0` when all four pass, `1` when one fails, and `2` when the call or the plant is wrong, such as a planted complexity above the threshold. Show the User the output of the proof.

A failed proof keeps `enabled: false`. Fix the measuring command or the plant with the User and run the proof again. Go to step 6 only when the proof of every measure passes.

## Step 6 — Measure the whole project

Run `crap-score --all` on the whole project:

```bash
.agent-factory/factory/scripts/crap-score --all --story-id setup --report-dir .current-work/crap-score/
```

Start it as a background job and wait for its exit, because a foreground command call of an agent CLI can end before `timeout_minutes` runs out (BR-134). Take the time from the start to the exit.

Exit `1` is the normal result of this step. It means that some functions lie above the threshold, and the report lists them with their scores. Exit `0` means that no function lies above the threshold. Both exits write the report `.current-work/crap-score/setup.json`.

Exit `2` means that the gate could not measure, and it writes no report (BR-133). Show the User the message of `crap-score`, then go back to the step whose setting failed. When the time limit ran out, propose a higher `timeout_minutes`, write it after the User confirms, and run step 6 again. For any other cause, such as a failed measuring command, fix the setup with the User in step 4 and run the proof of step 5 again.

Report the number of functions that would fail, the run time, and the path of the report. From these numbers, the User confirms the final threshold and sets `timeout_minutes` from the run time. `timeout_minutes` must be at least the measured run time.

Write `measured_minutes` next to `timeout_minutes` in the entry `gates.crap-score`, with the measured run time in minutes (DEC-19). With a run time of 7 minutes and a time limit of 10 minutes, the entry holds `measured_minutes: 7` and `timeout_minutes: 10`. `crap-score` does not read `measured_minutes`. Show the change and write it only after the User confirms. Commit nothing.

## Step 7 — Enable the gate

When the User changed the threshold in step 6, the agent writes the new threshold into `docs/testing.yaml` and runs `gate-setup-proof` again for every measure, because the planted functions depend on the threshold (DEC-08). When the planted complexity no longer fits the new threshold, the agent changes the plant first. The proof reads the threshold from the working tree (DEC-32).

The gate gets `enabled: true` only after the proof passes with the final threshold and the User confirms. Show the change and wait for the confirmation. A failed proof keeps `enabled: false`.

After the User confirms, make one commit with `docs/testing.yaml`, the measuring commands, and the `ready` commands. Name each file in `git add`, so the plant and the reports stay out of the commit:

```bash
git add docs/testing.yaml scripts/crap-measure-python
git commit -m "chore: set up the CRAP gate"
```

No earlier step commits. When the User stops the setup before step 7, nothing is committed, and the working tree holds the entry with `enabled: false`.
