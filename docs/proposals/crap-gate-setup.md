---
schema_version: 2
scope: global
title: CRAP Gate Setup
status: open
owner: agent-factory
created: 2026-11-09
updated: 2026-11-09
supersedes:

impact:
  scope: cross_component
  architecture_change: false
  external_contract_change: true
  boundaries:
    - packages/factory/scripts/crap-score
    - packages/factory/scripts/premerge-check
    - packages/factory/scripts/dispatch
    - packages/factory/scripts/dispatch_lib.py
    - packages/factory/config/pre-commit-config.yaml
    - packages/factory/config/hook-metadata.yaml
    - packages/factory/config/hooks/guard-human-fields
    - docs/proposals/run-lifecycle.md
    - packages/factory/skills
    - packages/factory/agents/test-strategy-agent.md
    - packages/factory/agents/implementation-agent.md
    - packages/factory/agents/developer-agent.md
    - docs/spec/validation-rules.md
    - docs/spec/interface-contracts.md
    - docs/testing.yaml

governance:
  assurance: elevated
  risk_domains:
    - reliability
    - operations

estimate:
  as_of: 2026-11-09
  basis: judgment
  confidence: low
  human_review_hours: unknown
  normalized_tokens: unknown
  estimated_consumption: unknown
---

# Feature Request: CRAP Gate Setup

## Primer

A team uses Agent Factory, a set of agents and scripts that carry out a project's planned work. Each item of work is called a story. The team wants a check that stops a commit when a changed function is complicated and poorly tested. The Factory calls such a check a gate, and this one is the CRAP gate. CRAP stands for Change Risk Anti-Patterns, a score for one function. The score rises with the function's complexity and falls as tests cover more of the function.

The gate is installed, but it cannot run. Its script reads only Python, and no step produces the coverage report it needs. So the Gigacron project, which uses the Factory, wrote its own script for its frontend. Every project would have to solve the same problems alone.

The work has two parts. An agent does the setup once per project, following a written procedure called a skill. After that, only scripts decide, at commits and merges. This proposal covers only the CRAP gate.

Suppose the Gigacron team runs the setup for its Python backend. The agent that plans testing picks a complexity tool and a coverage tool and tries them on a real file. It proposes to exclude code whose coverage depends on a local database. Then it writes a measuring command into the project. That command reports complexity and coverage per function in one fixed format, so the gate stays the same in every language. A person confirms each choice. Gigacron's trial run used a threshold of 8, and 4 of 140 backend functions failed. Numbers like these help the person set the threshold.

A newcomer might expect a ready-made gate with a built-in threshold. The proposal has none, because no default can run without the project's own tools and coverage data.

Only a function that a commit changes can fail, so Gigacron's 4 failing functions stop no commit that leaves them alone. A gate that cannot measure blocks and names the cause. Gigacron's test database was once ahead of the code, and all 233 backend tests failed. The gate reports such a case apart from bad code, so the person knows the code was not judged.

Before a person enables the gate, a script runs three checks, called the proof, so the agent cannot declare success by itself. Two runs on one commit must agree, a planted untested function must fail, and a broken measuring command must block. A commit hook runs the gate on every commit, and it runs once more before a story's final commit. Then an agent merges the story in an orchestrated run, or a person reviews the branch and merges it.

The project keeps its measuring commands, tool settings, exclusions, and its commit hook for this gate. If the Factory is removed, that hook prints the measurements and says that no verdict script is installed.

## Summary

The Factory ships one skill, `setup-crap-score`, and one script, `gate-setup-proof`. A project in any language can then check whether a changed function exceeds its threshold. The first release covers CRAP only. Python and TypeScript in this repository are the acceptance test of language neutrality. Mutation testing is left to [mutation-gate.md](mutation-gate.md), which starts with a measured trial.

## Motivation

The CRAP gate is installed in the Factory but cannot run. It is `enabled: false` in this repository's `docs/testing.yaml`, as [T-0402](../spec/work/todo.md) records. The faults go beyond a missing setting:

- The `crap-score` script reads Python only, through `radon` and the JSON format of coverage.py.
- It finds files by the ending `.py`, so it passes over 52 Python scripts in `packages/factory/scripts/` that have no ending, among them `finding-lint`.
- The implementation agent, which runs the backlog stories, is told to call `crap-score <source-files>`. The script accepts no file arguments, so that call fails.
- No step produces the coverage report. Without one, every function counts as 0 % covered.
- `premerge-check`, which `dispatch merge-story` calls before a merge, accepts any result file that says it passed. An agent runs the gate that writes the file.
- `premerge-check` requires `crap-score` by default, which no project can run without coverage data.

The Gigacron project, which uses the Factory, wrote its own CRAP script for its Vue frontend. It also planned a wrapper around the Factory script for its Python backend. Its baseline run at threshold 8 was workable, with 5 of 189 frontend functions and 4 of 140 backend functions failing. That run also showed two cases a setup must handle. Coverage of some code depends on the state of a local database. A test database was ahead of the code, which made all 233 backend tests fail during setup.

Every project that wants this gate has to solve the same problems alone.

## Core Principles

- An agent sets a gate up once, and no language model takes part between a commit and its verdict.
- One commit and one state of the exceptions register always get the same verdict, because the gate reads fixed inputs and applies a fixed rule.
- Only changed code can fail.
- Only a person can accept a function above the threshold.
- A gate that cannot measure blocks and names the cause.
- The threshold comes only from `docs/testing.yaml`.
- The agent proposes and tries, and a person decides, so a gate has no default.
- The gate is the same in every language, and only the measuring command differs.
- The measuring commands, tool configuration, exclusions, and commit hook belong to the project.

## Design

### Two parts

| Part         | Who runs it     | How often             | What it does                                                              |
| ------------ | --------------- | --------------------- | ------------------------------------------------------------------------- |
| Setup skill  | an agent        | once per project      | Choose tools, write the commands into `docs/testing.yaml`, run the proof. |
| Gate scripts | `dispatch`, Git | at commits and merges | Run the commands, apply the rule, write the verdict.                      |

`dispatch` is the Factory script that carries a run from its start to its close, as [run-lifecycle.md](run-lifecycle.md) describes. In an orchestrated run the implementation agent runs its commands. In a run by hand the human runs the commands that need a person, such as the merge of a story.

### Setup skill

`setup-crap-score` is a skill and not a playbook, because it is one bounded job and a Factory playbook is a whole workflow. The test-strategy agent, which plans testing, calls it, and a person can call it directly. It has these steps:

1. **Read the project.** Take the languages, test commands, and suites from `docs/testing.yaml`, which `detect-test-regime` writes.
2. **Choose a tool for each language.** The skill holds a table of candidates per language. The agent tries the first candidate on a real file from the project before it adopts the tool.
3. **Find what must be excluded.** The agent looks for code whose measurement depends on local state, such as database migrations, and for code that unit tests cannot reach. It proposes exclusions, each with a reason.
4. **Write the configuration.** The change to `docs/testing.yaml` includes the threshold and the time limit the agent proposes. The agent also proposes any `ready` command and a `crap-score` hook for the project's own pre-commit configuration. The agent shows the change and waits for the person's confirmation, which is the test-strategy agent's existing pause point.
5. **Run the proof.** The agent runs [the proof](#the-proof) with the threshold from step 4 and shows the output.
6. **Measure.** The agent measures the whole project and ignores the changed-function filter. It reports how many functions would fail and the run time. From these numbers, the person confirms the final threshold and the time limit.
7. **Enable.** After the person confirms, the gate gets `enabled: true`.

At each step the agent brings a tried proposal, and the person chooses the tools, the exclusions, the threshold, and the time limit. Setup is finished when the person enables the gate.

The table lists the languages the Factory has tried. For any other language, the agent looks up tools and tries them in the same way:

| Language              | Complexity                    | Coverage               |
| --------------------- | ----------------------------- | ---------------------- |
| Python                | `radon`, `lizard`             | coverage.py            |
| TypeScript/JavaScript | ESLint `complexity`, `lizard` | Vitest or Jest with v8 |

### The CRAP gate

`crap-score` has no language-specific code. It runs the project's measuring commands, reads their rows, applies the formula, and judges the changed functions.

```yaml
gates:
  crap_score:
    enabled: true
    threshold: 8
    timeout_minutes: 10
    measures:
      - name: backend
        files: "packages/server/backend/src/**/*.py"
        exclude:
          - "**/db/alembic/versions/**"   # coverage depends on database state
        command: "scripts/crap-measure-backend"
        ready: "docker compose ps --status running --services | grep -qx app"
```

Each command runs from the root of the story's checkout. That is the story's worktree in an orchestrated run, the primary checkout when a human drives by hand, and the temporary worktree during the proof. In an orchestrated run, `premerge-check` itself runs in the worktree of the feature branch, where the story branch is not checked out, so it starts `crap-score` in the story's worktree. The measuring command prepares whatever else it needs in that folder, such as dependencies.

Each command writes one JSON array to the path in the environment variable `GATE_OUTPUT`:

| Field          | Content                                  |
| -------------- | ---------------------------------------- |
| `file`         | Path relative to the repository root.    |
| `function`     | The function's name.                     |
| `start_line`   | First line of the function.              |
| `end_line`     | Last line of the function.               |
| `complexity`   | Cyclomatic complexity, an integer.       |
| `coverage_pct` | Share of the function covered, 0 to 100. |

The gate computes `CRAP = complexity² × (1 − coverage/100)³ + complexity`. A function counts as changed when its line range contains a changed line. A changed line differs from the merge base with the branch the story merges into, or from `HEAD` for a staged commit. The caller names that branch with `--base`, and `premerge-check` passes its merge target. The measuring command handles files with no ending, so the scripts in this repository are measured like any others.

The optional `ready` command answers one question: can the measuring command run now? It exits 0 for yes and anything else for no, and it measures nothing. `dispatch init` runs every `ready` command once, before any story starts. When one fails, `dispatch init` refuses to start and names the measure and the command. A project whose tests need no running services has no `ready` line.

The setup skill writes the measuring command and any `ready` command into the project. For Python it starts from a template that holds the `radon` and coverage.py code from `crap-score`. After setup, the command refers to nothing under `.agent-factory/`.

### Exit codes

The gate exits 0 on a pass, 1 on a failure of the code, and 2 when it cannot measure. A missing tool, a failed test run, an expired time limit, or a report in the wrong shape all give 2. Exit code 2 blocks the merge and the commit, and its message names the cause. In a project that needs a running stack, a commit without the stack fails with that message.

A measuring command reports a case it cannot measure with a non-zero exit and a message that names the cause. The gate then exits 2. One such case is a test database at a revision that the code does not know. The setup skill names this duty in the command's header. Another case is a file that coverage cannot reach, which the command must not report as 0 % covered. In this repository, 19 scripts start with `uv run --script` and run in their own environment. So the Python setup has to show that coverage reaches them.

### Exceptions register

A function can stay above the threshold for a good reason. A legacy function of complexity 9 scores 9 at full coverage, so with a threshold of 8 a one-line fix inside it fails, and no test can change that. The exceptions register lets a person accept such a function. It is the Markdown file `docs/findings/exceptions.md`. The file has one section per gate, so the mutation gate can later use its own section of the same document. `crap-score` reads only the section `## CRAP score`.

```markdown
# Exceptions

## CRAP score

| File                 | Function  | Accepted score | Reason                                                                   | Accepted by |
| -------------------- | --------- | -------------- | ------------------------------------------------------------------------ | ----------- |
| scripts/import-orders | parse_row | 9              | Each branch handles one supplier format. A split would only move them. | A. Example  |
```

`crap-score` reads the register from `dev`, so a row on a story branch has no effect until a person has committed it on `dev`. A project without this file has no exceptions. A changed function above the threshold gets `accepted` when a row names its file and function and its score is at or below the accepted score. The gate compares the score rounded to two decimals, as it prints it. A row with a missing cell or an accepted score that is not a number makes the gate exit 2 and names the row.

The accepted score holds the function where the person saw it. A later change that adds a branch or loses coverage raises the score above the row, and the gate fails again. The gate prints every accepted function with its score and reason, so an exception stays visible in every run.

Only a person writes the register, in an editor or with a `!` command. `guard-human-fields` refuses an agent's call that writes to this file. The setup skill does not fill the register. A person adds a row when a change to an old function fails and the person decides that the function should stay as it is.

### Where the gates run

Every gate with `enabled: true` in `docs/testing.yaml` applies to every story. A story's `quality-gates` field can add a gate and cannot remove one.

A gate runs only when there is code for it to judge. The gate compares the changed files with its `files` patterns and exclusions. If none remain, it starts nothing: no worktree, no test run, and no tool. It prints one line that says no code matched, and the gate counts as passed.

| Point                                               | What runs    | Scope            | Purpose                                                                                     |
| --------------------------------------------------- | ------------ | ---------------- | ------------------------------------------------------------------------------------------- |
| Pre-commit hook                                     | `crap-score` | staged functions | Fast feedback at the commit.                                                                |
| `premerge-check`, during `dispatch merge-story`     | `crap-score` | branch diff      | The authority for an automated merge.                                                       |
| Gate-check step of the story workflow, on both ways | `crap-score` | branch diff      | Feedback while the story can still be fixed. The implementation agent runs it on both ways. |

`crap-score` is one of the gates of the [story workflow](run-lifecycle.md#the-story-workflow), so it runs at the same point on both ways. The implementation agent runs it in the gate-check step. Every story then merges through `dispatch merge-story`, which runs `premerge-check` and with it `crap-score` again. In an orchestrated run the implementation agent runs `dispatch merge-story`, and in a run by hand the human runs it.

### The verdict and the report

The verdict is the exit code of `crap-score`. No stored result decides the CRAP gate. On a story branch with the gate enabled, `premerge-check` calls `crap-score` in place of reading its result file, so every merge rests on a run against the branch head, and the marker `premerge-check-ok` still means that the gate passed. The other gates follow [run-lifecycle.md](run-lifecycle.md#checks-at-the-merge).

`crap-score` also writes its rows as one JSON array to `.current-work/crap-score/<story-id>.json`, which is not tracked. A person reads this report, and the proof compares two of them. A row holds the [measurement fields](#the-crap-gate) plus `crap_score` and `pass_fail`. The value of `pass_fail` is `pass`, `fail`, or `accepted`, and `accepted` counts as a pass.

### The proof

The setup skill runs the script `gate-setup-proof` before the person enables the gate, so the agent cannot declare success by itself. All three checks run in a temporary worktree on a commit that holds the planted function. That function lies in a file that matches the measure's `files` pattern, so the gate always has changed code to judge and the measuring command always starts. Nothing from the worktree reaches the project's branches.

| Check         | What happens                                                                                                               | Required result                       |
| ------------- | -------------------------------------------------------------------------------------------------------------------------- | ------------------------------------- |
| Repeatable    | The gate runs twice on the planted commit.                                                                                 | Identical verdict and identical rows. |
| Catches CRAP  | The planted function has no tests. Its complexity is at or below the threshold, and its score at 0 % coverage is above it. | The gate fails and names it.          |
| Reports a gap | The measuring command is made to fail on the planted commit.                                                               | The gate exits 2.                     |

The setup skill writes the planted code for the project's language, and the script checks only the results. The planted function stays within the threshold by complexity alone, so only its coverage can make it fail. A command that wrongly reports full coverage then lets it pass, and the proof fails.

## Scope

**In the first release:**

- The skill `setup-crap-score`, with the candidate table.
- The script `gate-setup-proof`.
- `crap-score` reading the measurement format, with changed-function scoping, exclusions, and exit code 2.
- The exceptions register `docs/findings/exceptions.md`, read by `crap-score` from `dev` and closed to agents by `guard-human-fields` under BR-092.
- The measuring-command template for Python that `setup-crap-score` writes into a project.
- The optional `ready` command per measure, run by `dispatch init`.
- `premerge-check` calling `crap-score` on a story branch when the gate is enabled.
- The setup skill's proposal of a `crap-score` hook for the project's own pre-commit configuration.
- The gate set up in this repository for Python and for TypeScript, as the acceptance test of language neutrality.
- Updates to the test-strategy, implementation, and developer agents, and to the business rules BR-066 and BR-027. BR-066 picks the gates a story runs. BR-027 gets an exception for the gate's report.
- Updates to `docs/spec/interface-contracts.md`, which today states a default gate, a 30-minute default limit, and exit code 2 as a usage error.

**Explicitly deferred (do NOT plan stories for these):**

- **A general check that all pieces are in place before a run.** It covers much more than CRAP and needs its own proposal, which can take over the `ready` commands unchanged.
- **The mutation gate.** Nobody has measured survivors, equivalent mutants, or run times on real stories. [mutation-gate.md](mutation-gate.md) starts with that trial. That proposal defines its own section of the exceptions register.
- **Running the gates in CI.** `.agent-factory/config/project-context.json` lists no CI for this repository. Pre-commit and merge come first.
- **Evidence of a gate run that outlives the run.** A merge reruns the gates and reads no stored result. [gate-evidence.md](gate-evidence.md) owns any evidence beyond that.
- **The story workflow and the split of the git guardrail.** [run-lifecycle.md](run-lifecycle.md) owns them, and `crap-score` is one of its gates.
- **Tried tools for languages other than Python and TypeScript.** The agent finds such tools at setup, and the proof checks them.
- **Migrating Gigacron.** The team can run the setup skill there once it exists.
- **Keeping some hooks and gates after the Factory is removed.** It is an idea for later, and the first release keeps only the project's own files.

## Design Details

**Trial of `lizard`, on copies in a scratch folder.** `lizard` gave per-function complexity with line ranges for a Python file and a TypeScript file. It found nothing in a file with no ending.

**No default gates.** A project without the setup has no CRAP gate. `premerge-check` does not require `crap-score` by default. `premerge-check` prints one line that says which gates are not set up and names the setup skill, and the merge goes on. The gate has no built-in threshold or time limit. The setup writes both, and an enabled gate without one exits 2.

**After the Factory is removed.** `crap-score` holds no project knowledge, so it stays in the Factory as one script. The project keeps its measuring commands, tool configuration, exclusions, and hook. When the hook finds no `crap-score`, it prints the measurements, says that no verdict script is installed, and exits 0.

**Factory rules on test commands.** BR-023 says that the Factory does not construct a project's test commands. The setup skill proposes commands and the project owns them once the person confirms, so the skill is an onboarding step under that rule. BR-029 says that test hooks are project-owned and that the Factory does not inject them. So the hook goes into the project's own `.pre-commit-config.yaml` and never into the Factory's hook block. Under BR-027, the contract of the test suite is exit-code only. The gate reads its measuring report, as an exception to BR-027.

## Open Questions

None.

## Completion Criteria

- `setup-crap-score` exists and is listed in the generated index.
- In this repository, the setup skill produces a working gate for Python and for TypeScript, and `gate-setup-proof` passes for each.
- `gate-setup-proof` fails when the gate gives different rows on two runs of one commit.
- `gate-setup-proof` fails when a planted untested function passes the gate, so a measuring command that reports false coverage is caught.
- `gate-setup-proof` runs exactly three checks: repeatable verdict, planted function caught, and exit code 2 for a failing measuring command.
- With no changed code on the current branch, `gate-setup-proof` still starts the measuring command in each of its three checks.
- `crap-score` contains no language-specific import or file pattern.
- No measuring command or tool configuration that the setup skill writes refers to a path under `.agent-factory/`.
- With `.agent-factory/` absent, the project's commit hook prints the measurements, names the missing verdict script, and exits 0.
- A function above the threshold that a commit changes fails the gate, and the output names the file, the function, and the score.
- A function above the threshold that a commit does not change does not fail the gate.
- On a story branch that starts from a feature branch, a function changed only by an earlier story on that feature branch does not fail the gate.
- `premerge-check` starts `crap-score` in the story's worktree, and the measuring command sees the code of the story branch.
- A file that matches an `exclude` pattern never fails the gate.
- A changed function above the threshold passes as `accepted` when a row on `dev` names it and its score is at or below the accepted score. The output shows the score and the reason.
- A changed function whose score is above its accepted score fails the gate.
- A row that exists only on a story branch does not change the verdict.
- `crap-score` ignores every section of the register except `## CRAP score`.
- A row with a missing cell or a non-numeric accepted score makes `crap-score` exit 2 and names the row.
- `guard-human-fields` refuses an agent's call that writes to `docs/findings/exceptions.md`.
- `finding-lint` passes with `docs/findings/exceptions.md` present, and `stop_notice` does not report the file.
- When a measuring command fails, `crap-score` exits 2 and shows the command's message.
- When a `ready` command fails, `dispatch init` refuses to start and names the measure and the command.
- In this repository, a function in a script that starts with `uv run --script` either shows measured coverage or makes the gate exit 2.
- `premerge-check` reads no `crap-score` result file. On a story branch with a failing function, it refuses the merge even when a passing result file exists under `.current-work/`.
- A story with `quality-gates: []` in a project with an enabled gate still runs that gate when it changes code.
- A commit that changes no file matching a gate's `files` patterns starts no worktree, no test run, and no tool for that gate, and the gate counts as passed.
- In a project with no `gates` section, a merge runs no `crap-score`, and `premerge-check` prints which gates are not set up.
- `crap-score` holds no built-in threshold or time limit. An enabled gate without a required value exits 2.
- `dispatch merge-story` runs `crap-score` through `premerge-check`, without an agent calling a gate script.
- `test-strategy-agent.md` calls the setup skill, and its completion criteria do not say that no gate ran.
- `docs/testing.yaml` in this repository has the CRAP gate enabled, with a measured run time.
- [T-0402](../spec/work/todo.md) names this proposal for the CRAP part and [mutation-gate.md](mutation-gate.md) for the mutation part.
- `index-lint --check` passes.

## Guiding Rule

An agent may set a gate up, but only a script may say whether a commit passes it.

# Appendix

## Decisions

| ID     | Date       | Kind     | Decided by  | Decision                                                                                                                                                                                                                                                                            | Raised by |
| ------ | ---------- | -------- | ----------- | ----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- | --------- |
| DEC-01 | 2026-11-20 | decision | stakeholder | The existing `crap-score` skill is part of this work. The setup uses it and changes it where the design requires, so no text of the skill contradicts the gate.                                                                                                                     | PROP-06   |
| DEC-02 | 2026-11-20 | decision | stakeholder | The proposal is an architecture change. It amends decision 5 of ADR-0003, because `crap-score` reads a JSON report from a project-owned command, and it updates arc42 § 5.2.3 and § 8 for exit code 2.                                                                              | PROP-03   |
| DEC-03 | 2026-11-20 | decision | stakeholder | Exit code 2 does not count as an attempt. The story stops as `blocked`, a new cause beside the conflicts and the red suite, and the stop names the setup. The developer agent still commits while the gate cannot measure, and the merge refuses the story until the gate measures. | PROP-04   |
| DEC-04 | 2026-11-20 | decision | stakeholder | Coverage reaches the scripts that start through `uv run --script`. They get no exclusion, because `dispatch` is among them.                                                                                                                                                         | PROP-05   |

## Review findings

| ID      | Pass | Severity | Check | Status | Finding                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                      | Resolution |
| ------- | ---- | -------- | ----- | ------ | ------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------ | ---------- |
| PROP-01 | 1    | major    | 02    | open   | The In list plans work that run-lifecycle has built and merged into `dev`. ST-0414 makes `premerge-check` rerun every gate in a temporary worktree and read no stored `crap-score` result. ST-0415 runs every enabled gate and makes `quality-gates` only add gates, and BR-066 states both. So line 236, the BR-066 half of line 239, the rule at line 196, the first sentences of line 210, and the criteria at lines 293, 294 and 298 already hold at the reviewed commit. The remaining change at the merge is smaller and not stated: `premerge-check` stops filtering the diff to `.py` files (`py_files` in `gate_command`), passes `--base` instead of a file list, and drops `DEFAULT_GATES`, which still runs `crap-score` alone without a `gates` section (line 257). The fix is to remove the delivered items from the In list and to state the remaining change as a change to the built `premerge-check`: the stories correct and extend that code, and no story rebuilds it. Severity: major, because a planner who follows the In list cuts stories for work that is done (`fails_purpose`). |            |
| PROP-02 | 1    | major    | 03    | open   | Line 149 says that `premerge-check` runs in the worktree of the feature branch and starts `crap-score` in the story's worktree, and line 281 makes that a completion criterion. The built design differs. `premerge-check` reruns each gate in a temporary worktree at the branch head, `.current-work/<feature-branch>/premerge/<id>`, on both ways, and removes it afterwards (ADR-0038, the `premerge-check` contract in `docs/spec/interface-contracts.md`). Line 149 also names the primary checkout for a run by hand, where the merge rerun uses the same temporary worktree. The fix is to name the temporary worktree as the folder of the merge run, and to say that the measuring command and its `ready` check must measure that folder's code. The example `ready` line at line 146 checks a running Compose stack, and a stack started from another checkout does not serve the temporary worktree's code. Severity: major, because a planner who follows line 281 cuts a story that contradicts ADR-0038 and the built `premerge-check` (`fails_purpose`).                                    |            |
| PROP-03 | 1    | major    | 04    | open   | `impact.architecture_change` is `false`, but decision 5 of ADR-0003 states that the gate contract is exit-code-only and that the Factory does not parse JSON summaries or structured test output. The Design makes `crap-score` read a JSON array from a project-owned command through `GATE_OUTPUT` (line 151), and line 261 calls this only an exception to BR-027. The design also adds exit code 2 to `crap-score`, while arc42 § 5.2.3 lists 0 and 1. No item in Scope amends ADR-0003 or the arc42 chapters, and with `architecture_change: false` the feature-addition routing skips the architecture agent. The fix is to set `architecture_change: true` and to add the ADR-0003 amendment and the arc42 § 5.2.3 and § 8 updates to the In list and the boundaries. Severity: major, because the planner routes past the architecture step and cuts no story for the amendment (`fails_purpose`).                                                                                                                                                                                                   |            |
| PROP-04 | 1    | major    | 03    | open   | The Design does not say what the gate-check step does with exit code 2. Under run-lifecycle, a failing gate gets a fresh developer agent and counts as an attempt, and a refused `premerge-check` sends the story back to the gate-check step (ST-0416). So a stopped Compose stack makes developer agents retry code that nobody judged, up to six attempts, and then the story stops as `failed`, although the cause was the setup. Line 170 also says that a commit without the stack fails, which stops the developer agent's commit inside the story workflow. The fix is to state whether exit 2 counts as an attempt, which stop state it leads to (`failed`, `blocked`, or a new cause), and how the developer agent commits while the gate cannot measure. Severity: major, because a planner must ask the author before cutting the stories for the implementation and developer agents (`fails_purpose`).                                                                                                                                                                                         |            |
| PROP-05 | 1    | major    | 01    | open   | The criterion at line 292 lets a function in a `uv run --script` script either show measured coverage or make the gate exit 2. The criterion at line 300 requires the gate enabled in this repository. Twenty-one scripts in `packages/factory/scripts/` run through `uv run`, among them `dispatch`, `crap-score`, `next-id` and `step-guard`. If the exit-2 branch is taken, every story that changes one of them is refused at the merge, and no exception row can accept it, because exit 2 has no score. The fix is to pick one target: coverage reaches these scripts, or they get an exclusion with a reason, as line 115 provides for. Severity: major, because the two criteria together let a planner cut a story whose result blocks most Factory work, and the planner must ask which outcome is wanted (`fails_purpose`).                                                                                                                                                                                                                                                                       |            |
| PROP-06 | 1    | major    | 02    | open   | The skill `packages/factory/skills/crap-score/SKILL.md` exists and is named in neither Scope list. It describes `radon`, coverage.py JSON and a default threshold of 30. That contradicts the principles at lines 93, 94 and 95 and the no-default rule at line 257. The test-strategy agent reads this skill for the gate settings (`test-strategy-agent.md`, line 73), and the run-lifecycle epic names it as the place for the key with hyphens. The proposal adds `setup-crap-score` beside it and does not say whether the old skill is extended, merged into the new one, or removed. Severity: major, because a planner must ask the author what happens to the existing skill (`fails_purpose`).                                                                                                                                                                                                                                                                                                                                                                                                     |            |
| PROP-07 | 1    | minor    | 07    | open   | Two Motivation bullets no longer hold at the reviewed commit. `crap-score` accepts files as positional arguments (`parse_args`, the `files` argument), so the call at line 77 does not fail. `premerge-check` reruns the gate and reads no stored `crap-score` result (ST-0414), so line 79 no longer holds. Two counts are off. `packages/factory/scripts/` holds 55 Python scripts without an ending, not 52 (line 76): 34 start with `python3` and 21 with `uv run`. The scripts that start with `uv run` number 21, not 19 (line 172). The other four bullets hold. Severity: minor, because the remaining bullets still justify the work and the planner can act, but a reader takes the stale bullets as faults to fix (`raises_cost`).                                                                                                                                                                                                                                                                                                                                                                |            |
| PROP-08 | 1    | minor    | 01    | open   | The Exit codes section (line 170) names four causes of exit 2: a missing tool, a failed test run, an expired time limit, and a report in the wrong shape. The criteria check a failing command (line 290) and a missing required value (line 297). No criterion checks an expired `timeout_minutes` or a report in the wrong shape. The rounding to two decimals at line 188 also has no criterion, although it decides an `accepted` row at the boundary. Severity: minor, because the planner can add the criteria from the Design without asking, but the test writer must find the cases a second time (`raises_cost`).                                                                                                                                                                                                                                                                                                                                                                                                                                                                                  |            |
| PROP-09 | 1    | minor    | 03    | open   | `timeout_minutes` sits on the gate (line 139), while `measures` holds several commands. The Design does not say whether the limit applies to each measuring command or to all of them together, nor whether the commands run one after another. The `ready` command has no time limit at all. Severity: minor, because an implementer can choose one reading and the gate still blocks with a named cause, but a project that sets the limit from the measured run time at step 6 gets a wrong number (`raises_cost`).                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                       |            |
| PROP-10 | 1    | minor    | 03    | open   | Line 212 writes the report to `.current-work/crap-score/<story-id>.json` and says that a person reads it. At the merge the report lands inside the temporary worktree, which `premerge-check` removes afterwards (`gate_command` sets `report_dir` to the worktree). A staged commit outside a story has no story ID, and the Design names no file for it. Severity: minor, because the verdict is the exit code and the planner can act, but a person who looks for the report of a refused merge finds none (`raises_cost`).                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                               |            |
| PROP-11 | 1    | minor    | 03    | open   | Three sentences contradict run-lifecycle on who merges a story in a run by hand. Line 107 says the human runs the commands that need a person, "such as the merge of a story". Line 206 says that in a run by hand the human runs `dispatch merge-story`. Line 63 says a person "reviews the branch and merges it". Under run-lifecycle the implementation agent runs `merge-story` on the human's go (§ Two ways to drive it). Line 63 also says the hook "runs once more before a story's final commit", which no step of the story workflow does. Severity: minor, because line 248 leaves the story workflow to run-lifecycle and no CRAP story changes who merges, but a reader learns the wrong actor (`raises_cost`).                                                                                                                                                                                                                                                                                                                                                                                 |            |
| PROP-12 | 1    | minor    | 04    | open   | Three things that the proposal changes are missing from the boundaries and the rule updates. Line 289 needs a change to `packages/factory/scripts/finding-lint`, because `docs/findings/exceptions.md` matches the path of a finding file. Line 301 changes `docs/spec/work/todo.md`. Line 233 places the register under BR-092, but BR-092 covers human field values, not whole files, and `guard-human-fields` guards only those values. So BR-092 needs an amendment, and line 239 lists only BR-066 and BR-027. Severity: minor, because the criteria at lines 288 and 289 tell the planner what to build, but a reader who checks the boundaries and the rule list misses three files (`raises_cost`).                                                                                                                                                                                                                                                                                                                                                                                                  |            |
| PROP-13 | 1    | minor    | 03    | open   | The YAML example at line 136 uses the key `crap_score`. Under BR-055 and the `gates` schema, the key of a gate is its name with hyphens, `crap-score`, and the old key with an underscore only still works. `docs/testing.yaml` and the test-strategy agent already use `crap-score`. Severity: minor, because the old key still works and the planner can act, but the setup skill would copy a key that `premerge-check` warns about when both forms exist (`raises_cost`).                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                |            |
| PROP-14 | 1    | minor    | 02    | open   | Line 240 says that `docs/spec/interface-contracts.md` today states a default gate, a 30-minute default limit, and exit code 2 as a usage error. The default gate holds, in the `quality-gates` row. The 30-minute limit belongs to `gates.mutation-testing.timeout_minutes`, and exit 2 as a usage error belongs to `mutation-testing` and `premerge-check`. The contracts hold no section for `crap-score` itself, only the `gates` schema and the result-file table. Severity: minor, because the planner can find the right rows, but on a second reading and against a source that does not hold (`raises_cost`).                                                                                                                                                                                                                                                                                                                                                                                                                                                                                        |            |
| PROP-15 | 1    | minor    | 03    | open   | `test-strategy-agent.md` says "The agent never runs a gate" (line 65) and lists "No gate ran" in its completion criteria. In the setup skill that the agent calls, the agent runs `gate-setup-proof` and measures the whole project (lines 117 and 118). The criterion at line 299 changes only the completion line. Severity: minor, because the planner can act from line 299, but the agent's text would still contradict the setup it runs (`raises_cost`).                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                              |            |
| PROP-16 | 1    | minor    | 01    | open   | Line 270 makes TypeScript in this repository the acceptance test of language neutrality. The candidate table (line 128) names ESLint `complexity` and Vitest or Jest with v8. This repository runs its TypeScript tests with `node:test` and has no `package.json`, according to the `typescript` suite of `docs/testing.yaml`. So the acceptance follows the route for an untried language, not the table. Severity: minor, because the setup skill looks up other tools by design, but a reader who plans from the table expects a tool this repository does not have (`raises_cost`).                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                     |            |

## Review passes

| Pass | Date       | Reviewed commit                          | Disposition | Failed checks      | Summary                                                                                                                                                                                                                                                                                                                                                                                                                                      |
| ---- | ---------- | ---------------------------------------- | ----------- | ------------------ | -------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| 1    | 2026-11-20 | 54b865849f27d7f171097adf0ae6d3c78f72e239 | findings    | 01, 02, 03, 04, 07 | The boundaries resolve, the open questions are honest, and the `unknown` estimate is acceptable. The scope still plans run-lifecycle work that is merged, the merge worktree and the `uv` script criteria contradict built code or each other, and exit code 2 has no defined path through the gate-check step. The proposal must also mark the architecture change against ADR-0003 and decide the fate of the existing `crap-score` skill. |
