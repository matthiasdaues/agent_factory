---
scope: global
---

# EPICs — Run Lifecycle

Proposal trace: [run-lifecycle.md](../docs/proposals/run-lifecycle.md), accepted
Specification trace: [run-lifecycle.feature](../docs/spec/features/run-lifecycle.feature), [gaps report](../docs/spec/work/run-lifecycle-gaps.md), [validation-rules.md § Dispatch ledger](../docs/spec/validation-rules.md#dispatch-ledger-dispatch) (BR-111 to BR-124), [interface-contracts.md](../docs/spec/interface-contracts.md), [state-machines.md § Ledger Entry Lifecycle](../docs/spec/state-machines.md#ledger-entry-lifecycle), [mechanized-dispatch.md](../docs/spec/areas/mechanized-dispatch.md)
Architecture trace: [ADR-0037](../docs/adr/0037-one-lifecycle-for-runs-orchestrated-and-by-hand.md), [ADR-0038](../docs/adr/0038-premerge-check-reruns-the-gates-in-a-temporary-worktree.md), [ADR-0039](../docs/adr/0039-one-git-guardrail-script-for-all-five-agent-tools.md), [ADR-0040](../docs/adr/0040-the-factory-tests-run-against-the-source.md), the amended [ADR-0012](../docs/adr/0012-dispatcher-owned-semantic-gate-loop.md) and [ADR-0029](../docs/adr/0029-per-story-drift-reports-block-the-wave-close.md), [arc42 § 5.13](../docs/arc42/05_building_block_view.md#513-level-2-component-view----run-lifecycle), [arc42 § 6.22 to § 6.25](../docs/arc42/06_runtime_view.md#622-a-run-from-init-to-close), [QS-28 to QS-30](../docs/arc42/10_quality_requirements.md#qs-28-a-failing-gate-merges-on-neither-way-of-driving-a-run)
QA strategy trace: [run-lifecycle-qa-strategy.md](../docs/spec/work/run-lifecycle-qa-strategy.md), one owner row per Scenario

Dependency order: five stories start at once, because they share no file: the source tests (ST-0429), the report and finding names (ST-0412), the rerun of the gates (ST-0414), the `dependency-check` hook (ST-0417), and the guardrail script (ST-0427). ST-0429 goes first among the stories that edit `dispatch`. Until it merges, every `merge-story` copies `packages/factory` over `.agent-factory/factory`, so a later merge would change the `dispatch` that runs the rest of this backlog. The vocabulary story (ST-0430) comes last, because it checks the text that every other story writes.

## Story waves

`dispatch plan` sets the waves from the dependencies and the file overlap. This table is the expected result. Nearly every story edits `dispatch`, `dispatch_lib.py` or `premerge-check`, so `dispatch plan` may split a wave of this table further where two of its stories edit the same file.

| Wave | Stories                                     | Reason for the order                                                                                                                         |
| ---- | ------------------------------------------- | -------------------------------------------------------------------------------------------------------------------------------------------- |
| W1   | ST-0429, ST-0412, ST-0414, ST-0417, ST-0427 | ST-0429 removes the copy into the installed copy before any other story edits `dispatch`; the other four touch other files                   |
| W2   | ST-0408, ST-0413, ST-0428                   | ST-0408 renames the ledger fields that later `dispatch` stories write, and depends on ST-0429; ST-0413 builds on ST-0412; ST-0428 on ST-0427 |
| W3   | ST-0409, ST-0415, ST-0418                   | ST-0415 builds on ST-0414; ST-0409 and ST-0418 build on ST-0408                                                                              |
| W4   | ST-0410, ST-0419                            | ST-0410 needs ST-0409 and the rerun of ST-0414; ST-0419 needs the attempt rule of ST-0418                                                    |
| W5   | ST-0411, ST-0416, ST-0420, ST-0425          | ST-0416 edits `merge-story` after ST-0410; ST-0425 needs `merge-story` by hand and the return                                                |
| W6   | ST-0421, ST-0424, ST-0426                   | ST-0421 needs the return and the rewritten agent text of ST-0411; ST-0424 needs ST-0411 for the same file                                    |
| W7   | ST-0422                                     | ST-0422 needs the finding scope of ST-0413, the return of ST-0419 and the wave record rule of ST-0421                                        |
| W8   | ST-0423                                     | ST-0423 needs `dispatch add` of ST-0422 and the gate list of ST-0415                                                                         |
| W9   | ST-0430                                     | alone, after every other story                                                                                                               |

Every story carries `quality-gates: []`, because `docs/testing.yaml` disables both gates.

## Terms used in every EPIC

The feature file's description and the proposal's [§ Terms](../docs/proposals/run-lifecycle.md#terms) define each term. A short reminder:

- **Run.** Everything the Factory does for one feature branch, from `dispatch init` to `dispatch close`. The glossary calls it a Dispatch Run.
- **Orchestrated run.** The implementation agent starts stories in waves, each story in its own worktree under `.current-work/`.
- **Run by hand.** The implementation agent starts each story after the User's go, one at a time, in the primary checkout (the repository's main folder).
- **Feature branch.** The branch of a run, cut from `dev`. A **story branch** is `story/<id>`, cut from the feature branch.
- **Unit of work.** A story or a blocking finding that runs through the story workflow on `story/<id>`.
- **Gate-check step.** The implementation agent runs the gates on a story branch, and a fresh developer agent fixes each failure.
- **Stopped.** A unit of work waits for the User. The predicate HasStopped of the Ledger Entry Lifecycle decides when a `failed` unit of work has stopped.
- **Drift session.** The spawn of an owner, or of its reviewer, to settle one row of a spec-feedback report.
- **Installed copy.** `.agent-factory/factory/`, the copy of `packages/factory/` that the agent tools run.

## Rules that hold for every EPIC

- Source edits go to `packages/factory/`, never to `.agent-factory/factory/`.
- No story edits the specification, the architecture, the QA strategy, or `docs/testing.yaml`. A story that needs a change there writes a spec-feedback row. The test-strategy agent writes each `docs/testing.yaml` change at the wave close, because it owns that file (`core-artifacts.yaml`).
- Each story owns the QA strategy rows that its EPIC's Ownership Resolution assigns to it. A pytest test carries `@pytest.mark.spec("RL-NN-XX-NN")` with the Test ID of its row. A `node:test` test starts its name with the Test ID.
- Every git test builds its own repository in `tmp_path`, as [§ Test setup on temporary git repositories](../docs/spec/work/run-lifecycle-qa-strategy.md#test-setup-on-temporary-git-repositories) defines. Only the one-time `--orphans` run of ST-0426 reads this repository's ledgers.
- A story that makes an existing test wrong changes or deletes that test in the same commit, as [§ Test Retention Policy](../docs/spec/work/run-lifecycle-qa-strategy.md#test-retention-policy) lists.
- Agents do not run `uv run pytest` by hand, because the guardrail blocks it. The tests run through the commit hooks and the gate-check step.
- A story that changes an agent, skill, convention or playbook regenerates `packages/factory/INDEX.yaml` in the same commit, and `index-lint --check` passes.
- A story that changes an error message of `dispatch` or `premerge-check` uses the terms of [§ Terms](../docs/proposals/run-lifecycle.md#terms).
- No story plans deferred scope: the security scanner, a limit on repeat reviews, trusted gate results, gates for documents, or mutation testing at the merge.

## Governance and risk

The proposal declares `assurance: elevated` and two risk domains:

| Risk domain   | What goes wrong                                                                                                | Stories that guard it                                         |
| ------------- | -------------------------------------------------------------------------------------------------------------- | ------------------------------------------------------------- |
| `reliability` | A merge passes a check it should fail, because `premerge-check` reads the wrong folder or a stored gate result | ST-0410, ST-0413, ST-0414, ST-0415, ST-0416, ST-0423, ST-0424 |
| `operations`  | A command destroys work: `dispatch close` removes a worktree with untracked files, or an agent drops a run     | ST-0419, ST-0425, ST-0426, ST-0427, ST-0428                   |

Each of these stories has `risk_level: high`.

## Follow-up outside this backlog

[mutation-gate.md](../docs/proposals/mutation-gate.md) is a draft proposal. Its DEC-09 says that filing a `QA` finding does not unblock a merge. RL-G25 says that a surviving mutant filed as a `QA` finding counts as resolved for the story merge. The owner of `mutation-gate.md` settles the conflict before that proposal is accepted. No story here changes it.

## E1: Drive a run by hand through the same story workflow

### Why this EPIC exists

Today a run by hand has no story branches, no ledger and no merge step, so `premerge-check` never runs there. A function that fails the CRAP threshold can merge by hand while an orchestrated run blocks it. This EPIC gives the run by hand the same ledger, story branches and `merge-story` as an orchestrated run. The implementation agent drives it and waits for the User's go before each step that needs a person.

### Actor Goals

- User starts a run on a feature branch in either way of driving it
- Implementation agent runs every story through the same story workflow on both ways
- User approves each step that needs a person in a run driven by hand
- Factory maintainer finds in the dispatch contract exactly the fields the ledger holds

### Demo

1. The User asks the implementation agent for a run by hand on `feature/login` with ST-0350. The agent runs `dispatch init --mode by-hand --feature-branch feature/login --stories ST-0350`.
2. `dispatch status` shows `mode: by-hand` and `feature_branch: feature/login`. `git worktree list` shows no worktree for `feature/login`.
3. The agent stops and names `dispatch prepare-story ST-0350`. After the User's go, the primary checkout is on `story/ST-0350`.
4. The developer agent commits, and the code-review agent reviews. The implementation agent runs the gates, then stops and shows the output of `premerge-check`.
5. After the User's go, the agent runs `dispatch merge-story ST-0350`. `dispatch status` shows ST-0350 `done`, and `git show HEAD:backlog/ST-0350.md` reads `status: done`.

### Scope

**In:**

- `dispatch init --mode orchestrated|by-hand`. Without `--mode`, `init` starts an orchestrated run. A run by hand gets no feature worktree. Several runs may be active, but only one run by hand at a time. `init` refuses a story whose dependency outside the run is not `done` in the backlog (BR-111, BR-112).
- The test command comes from `docs/testing.yaml` only. The fallback to `config/project.json` and its two tests go.
- The ledger with `mode` and `feature_branch`, without `gate_results` and `closed`. `dispatch` reads the old names `invocation_branch` and `mode: automated` and writes only the new ones. `dispatch-contract.md` lists exactly the fields the code writes.
- `prepare-story` by hand checks out the story branch in the primary checkout and opens a wave of its own. `mark-dispatching` and `mark-dispatched` work by hand.
- `merge-story` by hand runs `premerge-check` with the story branch checked out, and checks out the feature branch only after exit 0. A refused check leaves the primary checkout on the story branch. A refused checkout stops `merge-story` (BR-124). Today `dispatch` requires the feature branch for `merge-story` (around line 1824).
- `mark-done` goes. Only `merge-story` sets `done`, in the merge commit, and `commit_sha` then holds the merge commit (BR-118).
- The text of the implementation agent: the stops by hand, the three commands of the User, the story workflow order, and the repeat review. The developer agent drops the gate run and the `done` update. `rules.md` and `branching-policy.md` follow the proposal's [§ Documents that change](../docs/proposals/run-lifecycle.md#documents-that-change). The tests `test_st_0365_*` and `test_st_0362_manual_mode_*` change with them.

**Out:**

- The checks that `premerge-check` adds at the branch head (E2).
- The attempts, the stop states and `return-story` (E4).
- `dispatch close` (E7).

### Dependencies

E2, for one story: ST-0410 needs the rerun of ST-0414, so that a changed tracked file in the primary checkout cannot hide a failing gate.

### Boundaries

- Code: `packages/factory/scripts/dispatch`, `packages/factory/scripts/dispatch_lib.py`
- Documents: `packages/factory/agents/implementation-agent.md`, `developer-agent.md`, `packages/factory/rulebooks/rules.md`, `rulebooks/conventions/dispatch-contract.md`, `branching-policy.md`
- Contracts: [§ dispatch](../docs/spec/interface-contracts.md#agent-factoryfactoryscriptsdispatch), [§ Ledger Entry Lifecycle](../docs/spec/state-machines.md#ledger-entry-lifecycle), [arc42 § 6.22.2](../docs/arc42/06_runtime_view.md#6222-sequence-a-run-by-hand)
- Tests: `tests/factory/` (new `test_run_lifecycle_*` files; `test_dispatch_run_blockers.py`, `test_core_artifact_ownership_text.py`)

### Domain Rules

- Both ways share the ledger states, so a story reaches `dispatched` before it merges on either way.
- One ledger exists per feature branch. `init` with the same stories on an existing ledger is a no-op that exits 0.
- Only `merge-story` sets `done`. The developer agent never sets it and never runs a gate script.
- By hand, the implementation agent waits for the User's go before a story starts, before it merges, when it stops, and before the merge into `dev`. It runs `prepare-story`, `add` and `merge-story` itself after the go.

### Size

4 stories.

### Building-Block Inventory

| Story   | Capability                                                             | Tier     | Spawns | Goal                                                                                                                                                                     | Basis                                                                                                                                                                        |
| ------- | ---------------------------------------------------------------------- | -------- | ------ | ------------------------------------------------------------------------------------------------------------------------------------------------------------------------ | ---------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| ST-0408 | Start a run by hand or an orchestrated run with `dispatch init --mode` | standard | 3–4    | The User starts a run in either way, beside other active runs, and `dispatch status` shows the mode and the feature branch under the new ledger names.                   | `init` has no `--mode`, writes `invocation_branch`, `automated`, `gate_results` and `closed`, and falls back to `config/project.json`. Adds the mode and renames the fields. |
| ST-0409 | Prepare a story by hand in the primary checkout                        | standard | 3      | After the User's go, `prepare-story` puts the primary checkout on `story/<id>` in a wave of its own, and the story reaches `dispatched`.                                 | `prepare-story` refuses a non-automated ledger and always adds a worktree. Adds the path without a worktree.                                                                 |
| ST-0410 | Merge a story by hand after `premerge-check` passes                    | strong   | 4      | After the User's go, `merge-story` merges the story into the feature branch only when `premerge-check` passed on the story branch, and sets `done` in the merge commit.  | `merge-story` requires the feature branch checked out; `mark-done` exists. Reorders the steps and removes `mark-done`.                                                       |
| ST-0411 | Lead the User through a run by hand                                    | standard | 3      | The implementation agent's instructions name each stop by hand and the three commands of the User, and the developer agent's instructions run no gate and set no `done`. | The implementation agent has no stops by hand; the developer agent runs the gates by hand. Rewrites both and the two conventions.                                            |

### Testability Assessment

All four goals produce observable outcomes: the ledger file, `git worktree list`, the checked-out branch, the exit codes of `dispatch`, and the story file in the merge commit. Integration tests on temporary repositories instrument `dispatch` as a subprocess. Contract tests call the ledger functions through `load_script`. The stops of the implementation agent have one red flag: no script shows that an agent follows its instructions. Text checks own them, and the mechanical checks of `premerge-check` and the guardrail stand behind them (QA strategy § Behaviour that needs a real agent session).

### Ownership Resolution

| Contract                                                                                     | .feature Rule                                                                                               | Owner   | Rationale                               |
| -------------------------------------------------------------------------------------------- | ----------------------------------------------------------------------------------------------------------- | ------- | --------------------------------------- |
| RL-01-IT-01 to RL-01-IT-06: the start, parallel runs, resume, the dependency outside the run | run-lifecycle.feature#User starts a run on a feature branch in either way of driving it                     | ST-0408 | introduces `--mode` and the start rules |
| RL-01-CT-01: the test command comes from `docs/testing.yaml`                                 | run-lifecycle.feature#User starts a run on a feature branch in either way of driving it                     | ST-0408 | removes the fallback                    |
| RL-17-CT-01, RL-17-CT-02, RL-17-LN-01, RL-17-IT-02: the ledger names and the contract        | run-lifecycle.feature#Factory maintainer finds in the dispatch contract exactly the fields the ledger holds | ST-0408 | first to rewrite the ledger fields      |
| RL-02-IT-01, RL-03-IT-01, RL-03-IT-02: a story reaches `dispatched` by hand                  | run-lifecycle.feature#User approves each step that needs a person in a run driven by hand                   | ST-0409 | introduces `prepare-story` by hand      |
| RL-03-IT-03 to RL-03-IT-05: `merge-story` by hand and BR-124                                 | run-lifecycle.feature#User approves each step that needs a person in a run driven by hand                   | ST-0410 | introduces `merge-story` by hand        |
| RL-02-IT-02, RL-02-CT-01, RL-17-IT-01: only `merge-story` sets `done`; `commit_sha`          | run-lifecycle.feature#Implementation agent runs every story through the same story workflow on both ways    | ST-0410 | removes `mark-done`                     |
| RL-02-LN-01 to RL-02-LN-03, RL-03-LN-01, RL-03-LN-02: the agent instructions                 | run-lifecycle.feature#User approves each step that needs a person in a run driven by hand                   | ST-0411 | introduces the text                     |

## E2: Merge a story only when its review ran, its findings are closed and its gates pass

### Why this EPIC exists

Today `premerge-check` checks the base, the diff size and the scope, and it reads stored gate results. It does not check that a review ran or that its findings are closed. A stored result can belong to older code. This EPIC makes the check read the review report and the finding files at the branch head with git, and rerun every gate in a temporary worktree. A story that skipped its review, left a blocking finding open, or broke a gate then cannot merge.

### Actor Goals

- Reviewer agent files reviews and findings that name their story or run
- Implementation agent merges a unit of work only when premerge-check passes at its branch head
- Test-strategy agent sets the gates of every story in docs/testing.yaml

### Demo

1. In an orchestrated run on `feature/login`, the implementation agent runs `dispatch merge-story ST-0350` on a branch without a review report. `premerge-check` refuses and names the missing report.
2. The code-review agent commits `docs/reviews/code-review-ST-0350-2026-11-24.md` and `docs/findings/BUG-0091.md` with `story: ST-0350` and `status: open`. `merge-story` refuses and names BUG-0091.
3. A fresh developer agent fixes BUG-0091 and sets it `resolved`. `docs/testing.yaml` enables the invented gate `license-check` with a command.
4. `merge-story` passes. Its output lists `license-check` and `dependency-check` as run on the branch head, and the primary checkout is unchanged.

### Scope

**In:**

- The code-review report name `code-review-<story-id>-YYYY-MM-DD.md`, with `-2` and `-3` for later reviews on one day, and the frontmatter fields `story` and `branch_head` (BR-122). The code-review agent commits the report also without findings.
- The finding fields `story` and `run` in `finding-format.md`, the finding template, the code-review agent and the QA agent. `finding-lint` refuses a finding that sets both (BR-121).
- `premerge-check` refuses a story branch without a matching review report, or with an open blocking finding of the story at the head. It reads both with git from the head. The story's review reports, findings and register files belong to its scope and do not count toward the file limit.
- `premerge-check` reruns every gate in a temporary worktree at `.current-work/<feature-branch>/premerge/<id>` and removes it afterwards. It takes the gate scripts from the installed copy of the calling checkout. It reads no stored result, except for `mutation-testing`. It skips `dependency-check` without `docs/spec/dependency-rules.dsl` and names the skip (BR-123).
- The gate list: every entry under `gates` with `enabled: true` and a command runs. `quality-gates` only adds gates. Keys with hyphens and the old keys `crap_score` and `mutation_testing` both work (BR-055, BR-066). The test-strategy agent and the `crap-score` skill name the keys with hyphens.
- In an orchestrated run, a refused `premerge-check` sends the story back to the gate-check step. An uncommitted change in the feature worktree stops `merge-story`, unless `dispatch.refuse_dirty_feature_worktree` is `false` (BR-124).

**Out:**

- The branch pattern `story/<id>` for findings and the scope of a finding's merge (E5, ST-0422).
- The merge rule for a filed surviving mutant (E5, ST-0423).
- The feature merge check (E6).

### Dependencies

None.

### Boundaries

- Code: `packages/factory/scripts/premerge-check`, `finding-lint`, `dispatch` (`merge-story`), `crap-score`, `mutation-testing`
- Documents: `packages/factory/agents/code-review-agent.md`, `qa-agent.md`, `test-strategy-agent.md`, `rulebooks/conventions/report-format.md`, `finding-format.md`, `rulebooks/templates/finding.md`, `skills/crap-score/SKILL.md`
- Contracts: [§ premerge-check](../docs/spec/interface-contracts.md#agent-factoryfactoryscriptspremerge-check), [§ `gates` section schema](../docs/spec/interface-contracts.md#docstestingyaml--gates-section-schema), [§ `dispatch` section schema](../docs/spec/interface-contracts.md#docstestingyaml--dispatch-section-schema), [§ finding-lint](../docs/spec/interface-contracts.md#packagesfactoryscriptsfinding-lint), [ADR-0038](../docs/adr/0038-premerge-check-reruns-the-gates-in-a-temporary-worktree.md), [arc42 § 6.24](../docs/arc42/06_runtime_view.md#624-the-merge-check-of-a-story)
- Tests: `tests/factory/` (new `test_run_lifecycle_*` files; `test_premerge_check.py`, `test_finding_lint.py`, `test_crap_score.py`, `test_core_artifact_ownership_gates.py`)

### Domain Rules

- `premerge-check` checks the result, not the order. It reads the state of the branch head at the merge.
- It reads the review report and the finding files from the branch head, not from the folder it runs in.
- A gate passes only when it passes on the branch head in a fresh worktree. A stored result counts only for `mutation-testing`.
- The gates the project enables always run. A story's `quality-gates` can only add gates.
- Only `story` and `run` say which review filed a finding. `traces` does not count at the merge.

### Size

5 stories.

### Building-Block Inventory

| Story   | Capability                                                              | Tier     | Spawns | Goal                                                                                                                                                                    | Basis                                                                                                                                                    |
| ------- | ----------------------------------------------------------------------- | -------- | ------ | ----------------------------------------------------------------------------------------------------------------------------------------------------------------------- | -------------------------------------------------------------------------------------------------------------------------------------------------------- |
| ST-0412 | File reviews and findings that name their story or run                  | standard | 3      | A review of a story commits a report named with the story ID and findings with `story` set, a feature-level finding names its run, and `finding-lint` refuses both.     | The report name carries only the date; findings have no `story` or `run`. Adds the names, the fields and the lint rule.                                  |
| ST-0413 | Refuse a story merge without a review or with an open blocking finding  | strong   | 4      | `premerge-check` refuses a story branch whose head has no matching review report or holds an open blocking finding of the story, and names the cause.                   | `premerge-check` checks neither. Adds both checks and the story's file scope.                                                                            |
| ST-0414 | Rerun the gates at the branch head in a temporary worktree              | strong   | 4      | `premerge-check` refuses a branch head that fails a gate, although a passing result file exists, and leaves the primary checkout and the story's checkout as they were. | `premerge-check` reads stored results under `.current-work/`. Adds the temporary worktree and the rerun.                                                 |
| ST-0415 | Run every gate that `docs/testing.yaml` enables                         | standard | 3–4    | `premerge-check` runs an enabled gate with a command that the script does not name, and a story's `quality-gates` adds a gate without dropping the project's gates.     | Only `crap-score` and `mutation-testing` are known; `quality-gates` replaces the project's choice. Generalizes the gate list.                            |
| ST-0416 | Send a refused story back to the gate-check step in an orchestrated run | standard | 3      | In an orchestrated run, a refused `premerge-check` sends the story back to the gate-check step, and an uncommitted change in the feature worktree stops `merge-story`.  | `merge-story` does not check the feature worktree. Adds the refusal and records the `dispatch.refuse_dirty_feature_worktree` key as a spec-feedback row. |

### Testability Assessment

All three goals produce observable outcomes: the exit code and the named cause of `premerge-check`, the list of gates it ran, the files of the primary checkout before and after, and the exit code of `finding-lint`. Integration tests on temporary repositories put the passing state in one place and the failing state in the other, so a read from the wrong folder fails the test. Contract tests own the gate list and the key forms. The report name rule for `-2` and `-3` is agent behaviour, so a text check owns it. No red flags.

### Ownership Resolution

| Contract                                                                                          | .feature Rule                                                                                                       | Owner   | Rationale                             |
| ------------------------------------------------------------------------------------------------- | ------------------------------------------------------------------------------------------------------------------- | ------- | ------------------------------------- |
| RL-04-LN-01 to RL-04-LN-04, RL-04-CT-01, RL-04-IT-01: report names and finding fields             | run-lifecycle.feature#Reviewer agent files reviews and findings that name their story or run                        | ST-0412 | introduces the names and fields       |
| RL-08-IT-01 to RL-08-IT-03, RL-08-IT-07, RL-08-IT-08: the review and finding checks and the scope | run-lifecycle.feature#Implementation agent merges a unit of work only when premerge-check passes at its branch head | ST-0413 | introduces both checks                |
| RL-08-IT-04 to RL-08-IT-06, RL-08-IT-10, RL-08-IT-13, RL-08-IT-14: the rerun                      | run-lifecycle.feature#Implementation agent merges a unit of work only when premerge-check passes at its branch head | ST-0414 | introduces the temporary worktree     |
| RL-09-CT-01 to RL-09-CT-07, RL-09-IT-01, RL-09-IT-02, RL-09-LN-01: the gate list and the keys     | run-lifecycle.feature#Test-strategy agent sets the gates of every story in docs/testing.yaml                        | ST-0415 | introduces the generic gate list      |
| RL-08-IT-15, RL-08-IT-16, RL-08-LN-01: the orchestrated `merge-story`                             | run-lifecycle.feature#Implementation agent merges a unit of work only when premerge-check passes at its branch head | ST-0416 | introduces the feature worktree check |

## E3: Learn at commit time that an import breaks a dependency rule

### Why this EPIC exists

Today `dependency-check` runs only at the merge. A developer agent learns about a forbidden import after the whole story is written, and the fix costs a gate-check retry. This EPIC adds a pre-commit hook, so the agent sees the break on the commit that makes it. A project without dependency rules needs neither the script nor `uv`.

### Actor Goals

- Developer agent learns at commit time that its imports break a dependency rule

### Demo

1. In a project with `docs/spec/dependency-rules.dsl`, the developer agent stages a `.py` file under the source root that imports across a forbidden boundary and runs `git commit`. The `dependency-check` hook fails and names the rule.
2. In a project without the rules file, the same commit passes, and the hook prints `dependency-check: no docs/spec/dependency-rules.dsl, skipped`.
3. Fitting a project without the rules file leaves the hook out of the generated `.pre-commit-config.yaml`.

### Scope

**In:**

- The hook `agent_factory_hook-dependency-check` in `packages/factory/config/pre-commit-config.yaml`. It runs on the whole source root when a commit stages a `.py` file there, and it checks for the rules file before it calls the script.
- The entry in `packages/factory/config/hook-metadata.yaml` with `availability: requires-path:docs/spec/dependency-rules.dsl`, so fitting leaves the hook out of a project without the file.
- Called directly without the rules file, `dependency-check` still exits 2.

**Out:**

- The skip of `dependency-check` in `premerge-check` (E2, ST-0414).

### Dependencies

None.

### Boundaries

- Config: `packages/factory/config/pre-commit-config.yaml`, `hook-metadata.yaml`
- Code: `packages/factory/scripts/dependency-check` (unchanged behaviour), `init-factory` (reads the metadata)
- Tests: `tests/factory/` (new `test_run_lifecycle_*` file; `test_precommit_config_contract.py`)

### Domain Rules

- Fast gates run on every commit; slow gates run once per story.
- The hook watches only `.py` files, because `dependency-check` reads Python imports only.
- Without a rules file, the hook passes with a notice, also when `uv` is missing.

### Size

1 story.

### Building-Block Inventory

| Story   | Capability                                     | Tier     | Spawns | Goal                                                                                                                                                     | Basis                                                       |
| ------- | ---------------------------------------------- | -------- | ------ | -------------------------------------------------------------------------------------------------------------------------------------------------------- | ----------------------------------------------------------- |
| ST-0417 | See a dependency-rule break in the commit hook | standard | 3      | A commit that breaks a rule of `dependency-rules.dsl` fails in the `dependency-check` hook, and a project without the file skips the hook with a notice. | No such hook exists. Adds the hook stanza and its metadata. |

### Testability Assessment

The goal produces observable outcomes: the exit code and output of a commit through a pre-commit shell hook, the generated configuration after fitting, and the metadata entry. Integration tests run the hook on temporary repositories, and contract tests read the stanza and the metadata. No red flags.

### Ownership Resolution

| Contract                                             | .feature Rule                                                                                        | Owner   | Rationale           |
| ---------------------------------------------------- | ---------------------------------------------------------------------------------------------------- | ------- | ------------------- |
| RL-10-IT-01 to RL-10-IT-04, RL-10-CT-01, RL-10-CT-02 | run-lifecycle.feature#Developer agent learns at commit time that its imports break a dependency rule | ST-0417 | introduces the hook |

## E4: Decide how a stopped story continues

### Why this EPIC exists

Today a story that fails its gates gets one escalation, and only one story per wave may escalate. ADR-0012 calls the end `blocked`, and the implementation agent calls it `failed`. When the cause cannot be fixed, the User has no command to give the story back to the backlog. This EPIC sets the attempts in `docs/testing.yaml`, names each stop by its cause, and adds `dispatch return-story`. The stories that depend on a returned story then wait.

### Actor Goals

- Implementation agent retries a failing gate within the configured attempts
- User decides how a stopped story continues
- Implementation agent starts a story only when its dependencies inside the run are done

### Demo

1. In an orchestrated run, ST-0350 fails `dependency-check` on each attempt. The implementation agent spawns a fresh developer agent per attempt.
2. After three attempts on its tier, `dispatch escalate ST-0350` grants the stronger tier. After three more, `dispatch status` shows ST-0350 `failed`.
3. The User runs `dispatch return-story ST-0350`. `dispatch status` and `backlog/ST-0350.md` both show `pending`.
4. `dispatch prepare-story ST-0351`, whose story depends on ST-0350, refuses and names the return.

### Scope

**In:**

- `gates.attempts` and `gates.attempts_escalated`, with the default 3 and the first attempt counted. `0` turns escalation off. Only the failure classes `acceptance_unmet` and `contradictory_evidence` count (BR-114).
- `escalate` grants under BR-115 and drops the limit of one escalation per wave. `re-dispatch` refuses when the attempts on the tier are used up and escalation is possible. After the User's fix, `re-dispatch` grants new attempts and records them in `attempt_grants` (BR-116, OI-13).
- The predicate HasStopped decides when a `failed` story has stopped. A failed attempt with a retry left is no decision point.
- `failed` for used-up attempts; `blocked` for a merge conflict, a refresh conflict, or a red suite after the merge. The red suite moves the feature branch back, as the code does today.
- `dispatch return-story` sets a `failed` or `blocked` story to `pending` in the ledger and the backlog, and records `returned`. The ledger schema in `dispatch-contract.md` gains `returned` and `attempt_grants`.
- `prepare-wave` and `prepare-story` check every dependency inside the run in the ledger, so the chain behind a returned story waits (BR-113).
- The implementation agent's text on attempts and fresh developer agents.

**Out:**

- The guardrail refusal of `return-story` to agents (E8).
- The return of a finding (E5, ST-0422).
- `dispatch close --drop` (E7).

### Dependencies

E1, for one story: ST-0418 writes attempts into the ledger under the names of ST-0408.

### Boundaries

- Code: `packages/factory/scripts/dispatch`, `dispatch_lib.py`
- Documents: `packages/factory/agents/implementation-agent.md`, `rulebooks/conventions/dispatch-contract.md`
- Contracts: [§ dispatch](../docs/spec/interface-contracts.md#agent-factoryfactoryscriptsdispatch), [§ Ledger Entry Lifecycle](../docs/spec/state-machines.md#ledger-entry-lifecycle), [mechanized-dispatch.md § Feature: Evidence-Gated Escalation](../docs/spec/areas/mechanized-dispatch.md#feature-evidence-gated-escalation), [ADR-0012](../docs/adr/0012-dispatcher-owned-semantic-gate-loop.md)
- Tests: `tests/factory/` (new `test_run_lifecycle_*` files; `test_dispatch_ledger_default.py`)

### Domain Rules

- `dispatch` enforces the attempt cap and the value `0`; the implementation agent does not count.
- The state names the cause: `failed` for used-up attempts, `blocked` for a conflict or a red suite.
- Both stop states wait for the User. The User fixes the cause and the agent re-dispatches, or the User returns the story.
- The ledger needs no new state for a return. It gains the transitions from `failed` and `blocked` to `pending`.
- A returned story holds back every story that depends on it inside the run, directly or through another story.

### Size

3 stories.

### Building-Block Inventory

| Story   | Capability                                            | Tier     | Spawns | Goal                                                                                                                                                            | Basis                                                                                                             |
| ------- | ----------------------------------------------------- | -------- | ------ | --------------------------------------------------------------------------------------------------------------------------------------------------------------- | ----------------------------------------------------------------------------------------------------------------- |
| ST-0418 | Retry a failing gate within the configured attempts   | strong   | 4      | A failing story gets `gates.attempts` attempts on its tier and as many on the stronger tier, then stops as `failed`, and two stories of one wave both escalate. | `escalate` allows one escalation per wave and reads no attempt settings. Adds the cap, the grants and HasStopped. |
| ST-0419 | Return a stopped story to the backlog                 | strong   | 4      | The User runs `dispatch return-story` on a `failed` or `blocked` story, and the ledger and the backlog both show it `pending`.                                  | No `return-story` and no field `returned` exist. Adds the command, the transitions and the schema field.          |
| ST-0420 | Hold back the stories that depend on a returned story | standard | 3      | `prepare-wave` and `prepare-story` refuse a story that depends on a returned story, directly or through another, and start a story that does not.               | Neither command knows a return. Adds the ledger dependency check.                                                 |

### Testability Assessment

All three goals produce observable outcomes: the ledger entries and their attempts, the exit codes and named reasons of `escalate`, `re-dispatch`, `return-story` and `prepare-story`, and the status in the story file. The attempt cap and HasStopped are pure logic, so contract tests own them. The return and the red suite need git state, so integration tests own them. The fresh developer agent per retry is agent behaviour, so a text check owns it. No red flags.

### Ownership Resolution

| Contract                                                                                | .feature Rule                                                                                                | Owner   | Rationale                   |
| --------------------------------------------------------------------------------------- | ------------------------------------------------------------------------------------------------------------ | ------- | --------------------------- |
| RL-05-CT-01 to RL-05-CT-07, RL-05-LN-01 to RL-05-LN-03: the attempts and the escalation | run-lifecycle.feature#Implementation agent retries a failing gate within the configured attempts             | ST-0418 | introduces the cap          |
| RL-03-CT-01: a failed attempt with a retry left is no decision point                    | run-lifecycle.feature#User approves each step that needs a person in a run driven by hand                    | ST-0418 | introduces HasStopped       |
| RL-06-CT-02: re-dispatch grants new attempts after the User's fix                       | run-lifecycle.feature#User decides how a stopped story continues                                             | ST-0418 | introduces `attempt_grants` |
| RL-06-CT-01, RL-06-IT-01 to RL-06-IT-05: the stop states and `return-story`             | run-lifecycle.feature#User decides how a stopped story continues                                             | ST-0419 | introduces `return-story`   |
| RL-07-CT-01 to RL-07-CT-03, RL-07-IT-01: the chain behind a returned story              | run-lifecycle.feature#Implementation agent starts a story only when its dependencies inside the run are done | ST-0420 | introduces the ledger check |

## E5: Close each wave and run blocking findings as units of work

### Why this EPIC exists

Today the drift sessions run after each merge, so a story merge and a drift fix can commit on the feature branch at the same time. A blocking finding from the feature checks has no way into the run, and the `mutation-testing` skill sends every surviving mutant to the test-strategy agent. This EPIC moves the drift sessions to the wave close and adds `dispatch add`, so a finding runs through the story workflow on its own branch. The owner of a `QA` finding then follows its cause.

### Actor Goals

- Implementation agent starts the next wave only after the wave close
- Implementation agent runs a blocking finding from the feature checks as a unit of work

### Demo

1. After the last story of wave 1 merges, the implementation agent runs `dispatch close-wave 1`. It refuses and lists an `open` row of `docs/spec/work/spec-feedback-ST-0350.md` with its owner.
2. The agent spawns the owner and its reviewer. `close-wave 1` passes and writes the wave record. `prepare-wave 2` now starts.
3. The QA agent files `docs/findings/BUG-0090.md` with `run: feature/login`. The agent runs `dispatch add BUG-0090`, and `dispatch status` shows BUG-0090 in a new wave.
4. After the story workflow on `story/BUG-0090`, `merge-story BUG-0090` passes, and the finding file reads `status: resolved` in the merge commit.

### Scope

**In:**

- `close-wave` refuses while a spec-feedback row of the wave is `open`, or `fixed` on a core-list artifact, and lists each row with its owner. A unit of work lets its wave close in five states (BR-062, BR-064). The implementation agent runs the drift sessions at the wave close without waiting for the User's go. `prepare-wave` and `prepare-story` refuse until the previous wave has a record. By hand, each story is a wave of its own.
- `dispatch-contract.md` moves the drift rows from after each merge to the wave close. The helper `_drift_rows_rule` and the `test_st_0362_*` tests change with the section name.
- `dispatch add` accepts only an open blocking finding, puts it into a new wave, and reuses a `pending` entry with its attempts reset. It refuses an ID in any other state and names it (BR-117). A stop refuses `dispatch add`.
- `premerge-check` accepts `story/<id>` for a story ID or a finding ID and runs the semantic gates on both. `merge-story` declares no file scope for a finding, and the file limit still applies.
- `merge-story` sets `status: resolved` in the finding file. `return-story BUG-0090` changes only the ledger entry and reads no `backlog/BUG-0090.md`.
- The gate-check step files a blocking `QA` finding for a surviving mutant it cannot resolve. The owner follows the cause: `planning-agent` for a test the step could not write, `test-strategy-agent` for a mutant that no test should kill (RL-G24). The `mutation-testing` skill report gains the field `finding`, and `test_st_0358_file_qa_finding_names_path_and_owner` changes with it.
- The mutation gate lets a filed mutant count as resolved for the story merge and keeps an `unresolved` mutant, an empty list, or a missing list failing (RL-G25, BR-066).
- The wave close routes the open `QA` findings by `owner`. A finding with `owner: planning-agent` runs in the next wave through `dispatch add`.

**Out:**

- The feature merge check that reads the findings with `run` (E6).
- DEC-09 of `mutation-gate.md` (follow-up outside this backlog).

### Dependencies

E1 (ST-0421 edits the agent text after ST-0411), E2 (the finding fields, the file scope, the gate list) and E4 (`return-story`, HasStopped).

### Boundaries

- Code: `packages/factory/scripts/dispatch`, `dispatch_lib.py`, `premerge-check`, `mutation-testing`
- Documents: `packages/factory/agents/implementation-agent.md`, `rulebooks/conventions/dispatch-contract.md`, `skills/mutation-testing/SKILL.md`
- Contracts: [§ `dispatch close-wave`](../docs/spec/interface-contracts.md#dispatch-close-wave), [§ premerge-check](../docs/spec/interface-contracts.md#agent-factoryfactoryscriptspremerge-check), [ADR-0029](../docs/adr/0029-per-story-drift-reports-block-the-wave-close.md)
- Tests: `tests/factory/` (new `test_run_lifecycle_*` files; `test_dispatch_close_wave_reports.py`, `test_core_artifact_ownership_text.py`, `test_core_artifact_ownership_gates.py`, `test_premerge_check.py`)

### Domain Rules

- A drift session never commits on the feature branch while a story merges, because drift sessions run only at the wave close.
- A finding has no story file, no dependencies and no model tier. It runs on the default tier, and its `artifact` serves the overlap planning.
- Returning a finding does not change what it found. The finding file stays `open`, and it still blocks the feature merge.
- The owner of a `QA` finding follows the cause of the surviving mutant.

### Size

3 stories.

### Building-Block Inventory

| Story   | Capability                                                                | Tier     | Spawns | Goal                                                                                                                                                                        | Basis                                                                                                                                                      |
| ------- | ------------------------------------------------------------------------- | -------- | ------ | --------------------------------------------------------------------------------------------------------------------------------------------------------------------------- | ---------------------------------------------------------------------------------------------------------------------------------------------------------- |
| ST-0421 | Close a wave after its drift rows are handled                             | standard | 3–4    | `close-wave` refuses while a drift row is not handled or a unit of work can still go on, the agent runs the drift sessions, and the next wave starts only after the record. | `close-wave` and its drift check exist; the documents run the drift sessions after each merge. Moves them and adds the five states.                        |
| ST-0422 | Run a blocking finding from the feature checks as a unit of work          | strong   | 4      | `dispatch add BUG-0090` puts the open finding into a new wave, and after `merge-story` the finding file reads `status: resolved` in the merge commit.                       | No `dispatch add`; `premerge-check` accepts only `story/ST-NNNN`. Adds the command, the wider pattern and the finding merge.                               |
| ST-0423 | File an unresolved mutant as a `QA` finding whose owner follows the cause | standard | 4      | A story merges with its surviving mutant filed as a `QA` finding, that finding names its owner by cause, and the wave close routes it by owner.                             | The skill writes `owner: test-strategy-agent` always and has no field `finding`; any survivor fails the gate. Changes the skill, the gate and the routing. |

### Testability Assessment

All goals produce observable outcomes: the exit code and listed rows of `close-wave`, the wave record, the ledger entry of a finding, the finding file in the merge commit, and the result file of `mutation-testing`. Integration tests on temporary repositories own the git paths, and contract tests own the five states and the acceptance rules of `dispatch add`. The routing by owner and the drift sessions are agent behaviour, so text checks own them. No red flags.

### Ownership Resolution

| Contract                                                                                          | .feature Rule                                                                                                       | Owner   | Rationale                       |
| ------------------------------------------------------------------------------------------------- | ------------------------------------------------------------------------------------------------------------------- | ------- | ------------------------------- |
| RL-11-IT-01 to RL-11-IT-04, RL-11-CT-01 to RL-11-CT-03, RL-11-LN-01: the wave close               | run-lifecycle.feature#Implementation agent starts the next wave only after the wave close                           | ST-0421 | introduces the wave close rules |
| RL-12-IT-01 to RL-12-IT-05, RL-12-CT-01, RL-12-CT-02: `dispatch add` and the finding merge        | run-lifecycle.feature#Implementation agent runs a blocking finding from the feature checks as a unit of work        | ST-0422 | introduces `dispatch add`       |
| RL-08-CT-01, RL-08-IT-09, RL-08-IT-11, RL-08-IT-12: `story/<id>` for a finding                    | run-lifecycle.feature#Implementation agent merges a unit of work only when premerge-check passes at its branch head | ST-0422 | first to run a finding branch   |
| RL-12-LN-01 to RL-12-LN-03, RL-12-IT-06 to RL-12-IT-08, RL-12-CT-03: the mutant as a `QA` finding | run-lifecycle.feature#Implementation agent runs a blocking finding from the feature checks as a unit of work        | ST-0423 | introduces the owner by cause   |

## E6: Merge the feature branch into dev after the feature merge check

### Why this EPIC exists

No step owns the merge of a feature branch into `dev` today. One line of the branching policy says it happens. So a feature can reach `dev` with a failed story, an open wave, or an open finding from QA. This EPIC adds `premerge-check dev <feature-branch>`, which the implementation agent runs and shows before the User merges.

### Actor Goals

- User merges the feature branch into dev only after the feature merge check passes

### Demo

1. After the last wave closes, the code-review agent reviews the whole feature, and the QA agent writes its Fagan, security and bug-hunt reports.
2. The implementation agent runs `premerge-check dev feature/login`. It refuses and names `BUG-0090`, which has `run: feature/login` and `status: open`.
3. After BUG-0090 merges as a unit of work, the check passes, and the agent shows the result.
4. The User merges `feature/login` into `dev`.

### Scope

**In:**

- `premerge-check dev <feature-branch>` refuses while a unit of work is `failed` or `blocked`, a wave is not closed, the end-of-feature review or a Fagan, security or bug-hunt report of the QA agent is missing or older than the head, or a blocking finding of the run is open. It runs the full test suite on the feature branch head in a temporary worktree (BR-123).
- A report or a finding of another run does not count.
- The playbook order: code review of the feature, then QA, then reconciliation on `dev`. The line in the implementation agent that names reconciliation first goes. The implementation agent shows the result and the User merges.

**Out:**

- The merge itself, which stays the User's.
- `dispatch close` (E7).

### Dependencies

E1 (ST-0424 edits the agent text after ST-0411) and E2 (the `run` field, the report frontmatter, the temporary worktree).

### Boundaries

- Code: `packages/factory/scripts/premerge-check`
- Documents: `packages/factory/agents/implementation-agent.md`, `playbooks/feature-addition.md`, `playbooks/greenfield-development.md`, `rulebooks/conventions/branching-policy.md`
- Contracts: [§ premerge-check](../docs/spec/interface-contracts.md#agent-factoryfactoryscriptspremerge-check)
- Tests: `tests/factory/` (new `test_run_lifecycle_*` file)

### Domain Rules

- The feature merge counts only reports and findings whose `run` names the feature branch or whose `story` names a story of the run.
- Every unit of work of the run is `done` or `pending` before the merge into `dev`.
- The User merges; no agent merges a feature branch into `dev`.

### Size

1 story.

### Building-Block Inventory

| Story   | Capability                                                | Tier   | Spawns | Goal                                                                                                                                                      | Basis                                                          |
| ------- | --------------------------------------------------------- | ------ | ------ | --------------------------------------------------------------------------------------------------------------------------------------------------------- | -------------------------------------------------------------- |
| ST-0424 | Check that a feature is ready before the merge into `dev` | strong | 4      | `premerge-check dev feature/login` refuses a run that is not ready and names the cause, and passes once the run is ready, with the suite run on the head. | No feature merge check exists. Adds it and the playbook order. |

### Testability Assessment

The goal produces observable outcomes: the exit code and the named cause of `premerge-check dev`, for each of the ten rows of the Outline. Integration tests on temporary repositories own the rows, and text checks own the playbook order and the agent's step. No red flags.

### Ownership Resolution

| Contract                                             | .feature Rule                                                                                           | Owner   | Rationale                    |
| ---------------------------------------------------- | ------------------------------------------------------------------------------------------------------- | ------- | ---------------------------- |
| RL-13-IT-01 to RL-13-IT-04, RL-13-LN-01, RL-13-LN-02 | run-lifecycle.feature#User merges the feature branch into dev only after the feature merge check passes | ST-0424 | introduces the feature check |

## E7: End a run and clean up the old runs

### Why this EPIC exists

No command removes a ledger today. This repository holds six old ledgers, thirteen worktrees besides the primary checkout, and 36,109 files under `.current-work/`. Every check that asks whether a run is active sees those runs as live. This EPIC adds `dispatch close` for a finished or dropped run and `dispatch close --orphans` for what no active run owns. Untracked files go into named stashes, and unmerged branches are listed for the User.

### Actor Goals

- User ends a run and leaves no run state behind
- User cleans up the runs that no active run owns

### Demo

1. After the User merges `feature/login` into `dev`, the User runs `dispatch close`.
2. The ledger, the worktrees, the gate results, the markers and the briefs of `feature/login` are gone, and `git branch` no longer lists `story/ST-0350`.
3. The output lists the stash `run feature/login ST-0350 2026-11-24` and the unmerged branch `story/ST-0351`.
4. In this repository, the User runs `dispatch close --orphans`. The ledgers of `brownfield-onboarding` and `bug-hunt-fixes` are gone, and the output lists the `core-artifact-layout` ledger with ST-0344 `blocked`.

### Scope

**In:**

- `dispatch close` refuses while a unit of work is `failed` or `blocked`, or the feature branch is not merged into `dev`. It removes the ledger, the worktrees, the gate results, the markers, the briefs and the temporary premerge worktrees, and deletes merged branches with `git branch -d`. It stashes untracked files under a name and lists each stash and each unmerged branch (BR-119).
- `dispatch close --drop` ends a run whose unfinished stories are returned.
- `dispatch close` closes a ledger with the old names.
- The end-to-end run by hand from `init` to `close`, with scripted commits in place of the agents.
- `dispatch close --orphans` removes a worktree whose branch is merged, lists the rest, and removes a ledger without a branch whose stories are all `done`, also when nested inside a worktree (BR-120). It ignores the ledger's `mode`.
- The one-time `--orphans` run in this repository.

**Out:**

- The guardrail refusal of `close --drop` to agents (E8).
- Deleting unmerged branches or stashes. The User decides.

### Dependencies

E1 (the ledger names, `merge-story` by hand) and E4 (`return-story`). ST-0425 also needs the temporary worktrees of ST-0414.

### Boundaries

- Code: `packages/factory/scripts/dispatch`, `dispatch_lib.py`
- Documents: `packages/factory/rulebooks/conventions/dispatch-contract.md`, `packages/factory/agents/implementation-agent.md`
- Contracts: [§ dispatch](../docs/spec/interface-contracts.md#agent-factoryfactoryscriptsdispatch), [arc42 § 6.22](../docs/arc42/06_runtime_view.md#622-a-run-from-init-to-close)
- Tests: `tests/factory/` (new `test_run_lifecycle_*` files)

### Domain Rules

- A run is finished after the merge into `dev`, or dropped by the User. Every unit of work is then `done` or `pending`.
- After the close, the record of the run is the merge commits in `dev` and the `done` status in each story file.
- `dispatch close` never deletes an unmerged branch or a stash. It lists them.
- A ledger that holds an unfinished story is listed, never removed by `--orphans`.

### Size

2 stories.

### Building-Block Inventory

| Story   | Capability                                          | Tier   | Spawns | Goal                                                                                                                                                  | Basis                                                 |
| ------- | --------------------------------------------------- | ------ | ------ | ----------------------------------------------------------------------------------------------------------------------------------------------------- | ----------------------------------------------------- |
| ST-0425 | End a finished or dropped run with `dispatch close` | strong | 4      | After `dispatch close`, the run's state is gone, merged branches are deleted, untracked files are in named stashes, and unmerged branches are listed. | No `close` exists. Adds `close` and `close --drop`.   |
| ST-0426 | Clean up old runs with `dispatch close --orphans`   | strong | 4      | `dispatch close --orphans` removes what is merged and done, lists the rest, and in this repository leaves only the `core-artifact-layout` ledger.     | No `--orphans` exists. Adds it and runs it once here. |

### Testability Assessment

Both goals produce observable outcomes: the files and worktrees before and after, `git branch`, `git stash list`, and the listed leftovers. Integration tests on temporary repositories check what stays after each removal. The run in this repository is a one-time check, not a retained test (QA strategy § One-time checks). No red flags.

### Ownership Resolution

| Contract                                            | .feature Rule                                                                                               | Owner   | Rationale                              |
| --------------------------------------------------- | ----------------------------------------------------------------------------------------------------------- | ------- | -------------------------------------- |
| RL-14-IT-01 to RL-14-IT-08: the close               | run-lifecycle.feature#User ends a run and leaves no run state behind                                        | ST-0425 | introduces `close`                     |
| RL-17-IT-03: close a ledger with the old names      | run-lifecycle.feature#Factory maintainer finds in the dispatch contract exactly the fields the ledger holds | ST-0425 | first to close a ledger                |
| RL-02-E2-01: one run by hand from `init` to `close` | run-lifecycle.feature#Implementation agent runs every story through the same story workflow on both ways    | ST-0425 | first story with every step of the run |
| RL-15-IT-01 to RL-15-IT-05: `--orphans`             | run-lifecycle.feature#User cleans up the runs that no active run owns                                       | ST-0426 | introduces `--orphans`                 |

## E8: Keep agents from destroying work in every agent tool

### Why this EPIC exists

A run by hand relies on the User watching, so the guardrail refuses agents only the commands that destroy work. Today no guardrail refuses `dispatch return-story` or `dispatch close --drop`. The script counts any ledger under `.current-work/`, so a ledger of another branch blocks work on `dev`. pi's TypeScript copy holds its own rules and has drifted, and OpenCode has no git guardrail. This EPIC makes one script decide for all five agent tools.

### Actor Goals

- User keeps agents from destroying work in every agent tool

### Demo

1. In Claude Code, an agent runs `dispatch return-story ST-0350`. The guardrail refuses with exit 2. The same holds after `cd x && dispatch close --drop` and inside `bash -c`.
2. With `dev` checked out and the ledger of `feature/search` under `.current-work/`, an agent's `git commit` passes.
3. In pi, the same refusal comes from `block-dangerous-git.sh`, and `block-dangerous-git.ts` holds no rule of its own.
4. In a real OpenCode session, the User starts `pre-commit run run-opencode-session-test --hook-stage manual`. The session's `dispatch return-story ST-0350` is refused through the `shell` tool and through the `execute` tool.

### Scope

**In:**

- `block-dangerous-git.sh` refuses agents `dispatch return-story` and `dispatch close --drop` through any path to `dispatch`, in a chain after `&&` or `;`, and inside `bash -c`. It refuses no other `dispatch` command.
- The script finds the run of a folder from the folder's branch. A ledger of another branch never counts.
- The checks that stay: a merge needs `premerge-check-ok` for the current head, and the rest of the proposal's [§ The git guardrail](../docs/proposals/run-lifecycle.md#the-git-guardrail) list.
- The payloads of Claude Code, Codex, Copilot and pi reach the script.
- `config/extensions/block-dangerous-git.ts` becomes a thin wrapper that passes each command to the script and returns its answer, as `guard-human-fields.ts` does.
- `config/plugins/agent-factory.ts` gets a git guardrail that calls the same script for the `shell` and the `execute` tool. A fast `node:test` contract test with a stub script covers each path without a real session.
- The real-session test of OpenCode behind the marker `opencode_session`, registered in `pyproject.toml`, and the manual pre-commit hook `run-opencode-session-test` after `run-container-tests` in `.pre-commit-config.yaml`. The story records the marker for `docs/testing.yaml` as a spec-feedback row, and the test-strategy agent writes it at the wave close (OI-12).

**Out:**

- A command built from variables, which still passes (OI-11).
- The human's own `git commit --no-verify`.

### Dependencies

None.

### Boundaries

- Code: `packages/factory/config/hooks/block-dangerous-git.sh`, `block-dangerous-git.json`, `config/extensions/block-dangerous-git.ts`, `config/plugins/agent-factory.ts`
- Config: `pyproject.toml`, `.pre-commit-config.yaml`
- Contracts: [§ block-dangerous-git.sh](../docs/spec/interface-contracts.md#agent-factoryfactoryconfighooksblock-dangerous-gitsh), [ADR-0039](../docs/adr/0039-one-git-guardrail-script-for-all-five-agent-tools.md), [arc42 § 6.25](../docs/arc42/06_runtime_view.md#625-the-git-guardrail-in-every-agent-tool)
- Tests: `tests/factory/test_block_dangerous_git.py`, new `test_run_lifecycle_*` files, `packages/factory/config/extensions/__tests__/block-dangerous-git.test.ts`, `packages/factory/config/plugins/__tests__/agent-factory.test.ts`

### Domain Rules

- One script holds every rule. Each agent tool's entry passes the command and returns the script's answer.
- Agents may never run `dispatch return-story` or `dispatch close --drop`, in either way of driving a run.
- The guardrail relies on refusing a command, which every agent tool supports.
- A ledger counts only for the branch it names or the story branches it lists.

### Size

2 stories.

### Building-Block Inventory

| Story   | Capability                                              | Tier   | Spawns | Goal                                                                                                                                                          | Basis                                                                                            |
| ------- | ------------------------------------------------------- | ------ | ------ | ------------------------------------------------------------------------------------------------------------------------------------------------------------- | ------------------------------------------------------------------------------------------------ |
| ST-0427 | Refuse the two destructive commands in four agent tools | strong | 4      | In Claude Code, Codex, Copilot and pi, the guardrail refuses an agent every form of the two commands, and on `dev` a ledger of another branch blocks nothing. | The script counts any ledger and does not know the two commands; pi's copy has its own rules.    |
| ST-0428 | Give OpenCode the same git guardrail                    | strong | 4      | In a real OpenCode session, the guardrail refuses an agent `dispatch return-story` through the `shell` and the `execute` tool.                                | The plugin guards only human fields. Adds the git guardrail, its tests, the marker and the hook. |

### Testability Assessment

Both goals produce observable outcomes: the exit code 2 and the deny reason of the script for each payload and each command form. Integration tests feed the script each tool's payload. The `node:test` tests with a stub script show that pi and OpenCode hold no rule of their own. One red flag: only a real OpenCode session shows that OpenCode calls the plugin at all. The QA strategy accepts this with an opt-in test behind a marker, started by the User before each release.

### Ownership Resolution

| Contract                                                         | .feature Rule                                                                    | Owner   | Rationale                         |
| ---------------------------------------------------------------- | -------------------------------------------------------------------------------- | ------- | --------------------------------- |
| RL-16-IT-01 to RL-16-IT-07: the script's refusals and run lookup | run-lifecycle.feature#User keeps agents from destroying work in every agent tool | ST-0427 | introduces the rules              |
| RL-16-CT-01: pi's wrapper holds no rule                          | run-lifecycle.feature#User keeps agents from destroying work in every agent tool | ST-0427 | introduces the wrapper            |
| RL-16-CT-02, RL-16-E2-01, RL-16-E2-02: OpenCode                  | run-lifecycle.feature#User keeps agents from destroying work in every agent tool | ST-0428 | introduces the OpenCode guardrail |

## E9: Run the tests against the source and read one vocabulary

### Why this EPIC exists

Today `merge-story` copies `packages/factory` over the installed copy of the checkout where it runs. Every session there then runs code that has not reached `dev`, and this backlog's own run would change the `dispatch` it runs on. Beside that, the documents use several words for one thing: "manual mode", "main checkout" and "invocation branch" name what the run lifecycle calls a run by hand, the primary checkout and the feature branch. This EPIC removes the copy and makes the vocabulary one.

### Actor Goals

- Factory maintainer runs the tests against the source, not the installed copy
- Factory maintainer reads one vocabulary in every Factory document

### Demo

1. The implementation agent runs `dispatch merge-story ST-0350`. `git status --ignored .agent-factory/factory` and the file times show the installed copy unchanged.
2. The maintainer runs the test suite in a linked worktree that holds no `.agent-factory/`, and it passes.
3. The maintainer searches `packages/factory/` and `docs/spec/` for "manual mode" and "main checkout" and finds no living document that uses them. `index-lint --check` passes.

### Scope

**In:**

- `merge-story` copies nothing into `.agent-factory/factory` (ADR-0040). Its comment and lines 1954 to 1962 of `dispatch` go.
- The test suite reads no installed copy of its own. The `.agent-factory` link for `scope-lint` in `test_core_layout_gates.py` does not count (OI-08).
- The `spec` marker description in `pyproject.toml` gains the prefix RL.
- No Markdown file under `packages/factory/` or `docs/spec/` uses the terms automated mode, manual mode, mechanized dispatch, invocation branch, gate-check loop, drift report or main checkout. Accepted ADRs, superseded proposals and file names keep their terms.
- The rows of `counter-ids.feature` and `finding-classification.feature` that quote the old terms, with `test_counter_ids_text.py`.
- No error message of `dispatch` or `premerge-check` says "invocation branch" or "main checkout".

**Out:**

- Renaming files such as `mechanized-dispatch.md`.

### Dependencies

ST-0429: none; it goes into wave 1. ST-0430: every other story of this backlog.

### Boundaries

- Code: `packages/factory/scripts/dispatch`, `premerge-check` (messages only)
- Documents: every living Markdown file under `packages/factory/` and `docs/spec/`
- Contracts: [ADR-0040](../docs/adr/0040-the-factory-tests-run-against-the-source.md)
- Tests: `tests/factory/` (new `test_run_lifecycle_*` files; `test_counter_ids_text.py`)

### Domain Rules

- The Factory repository is a project like any other: its code and tests live in `packages/factory` and `tests/`, and the tests run the code from there.
- Tests that install the Factory into a temporary project keep using that project's `.agent-factory`.
- Each concept has one term, as the proposal's [§ Terms](../docs/proposals/run-lifecycle.md#terms) defines.

### Size

2 stories.

### Building-Block Inventory

| Story   | Capability                                           | Tier     | Spawns | Goal                                                                                                                                      | Basis                                                                                  |
| ------- | ---------------------------------------------------- | -------- | ------ | ----------------------------------------------------------------------------------------------------------------------------------------- | -------------------------------------------------------------------------------------- |
| ST-0429 | Merge a story without touching the installed copy    | standard | 3      | `dispatch merge-story` leaves `.agent-factory/factory` unchanged, and the test suite passes without this repository's installed copy.     | `merge-story` copies `packages/factory` over the installed copy. Removes the copy.     |
| ST-0430 | Read one vocabulary in every living Factory document | standard | 4      | No living document under `packages/factory/` or `docs/spec/` and no error message of `dispatch` or `premerge-check` uses a replaced term. | Many documents and messages use the old terms. Replaces them and adds the text checks. |

### Testability Assessment

Both goals produce observable outcomes: the installed copy before and after a merge, a test run without `.agent-factory/`, and a text search with a fixed term list. Integration tests own the merge, and text checks own the vocabulary and the test reads. A static scan cannot see a runtime read of the installed copy, so ST-0429 runs the suite once in a linked worktree, and every later `premerge-check` repeats that run. No red flags.

### Ownership Resolution

| Contract                              | .feature Rule                                                                                      | Owner   | Rationale                  |
| ------------------------------------- | -------------------------------------------------------------------------------------------------- | ------- | -------------------------- |
| RL-18-IT-01, RL-18-LN-01, RL-18-LN-02 | run-lifecycle.feature#Factory maintainer runs the tests against the source, not the installed copy | ST-0429 | removes the copy           |
| RL-19-LN-01 to RL-19-LN-03            | run-lifecycle.feature#Factory maintainer reads one vocabulary in every Factory document            | ST-0430 | introduces the text checks |
