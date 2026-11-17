I read every source in the brief, plus the code and the live repository state. Line numbers are for the tracked files under `packages/factory/` and `docs/`. "dc" means dispatch-contract.md, "bp" branching-policy.md, "ia" implementation-agent.md, "md" mechanized-dispatch.md.

## 1. Lifecycle as implemented

**Mode choice.** The mode comes from a flag, then `docs/agent-context.md`, then `implementation.default_mode`. If none of these settles it, the agent asks the user (ia:95-105).

**Orchestrated mode**

01. **Init.** `dispatch init --base --stories [--feature-branch]` (ia:115, dispatch:579-756).

    - It creates `feature/<x>` plus a worktree at `.current-work/<fb>/invocation`. A branch that already exists is adopted without a new worktree.
    - Without `--feature-branch`, it creates `impl/<ids>` with its worktree at `.current-work/<branch>`.
    - It writes the ledger to `<git toplevel of cwd>/.current-work/<branch>/dispatch-ledger.yaml` with `branch_root` = `branch_head` = the invocation branch tip, and every story `pending`.
    - It refuses while any ledger anywhere has a non-terminal story (`_active_ledger`, :733-746). It also refuses when there is no `test_command` in `docs/testing.yaml`.

02. **Wave planning.** `dispatch plan --backlog-dir` writes wave numbers and deps into the ledger unless `--dry-run` is given (:759-802).

03. **Story start.**

    - `prepare-wave N` first refuses if a prior-wave story is non-terminal. For each eligible `pending` story it then:
      - creates `story/<id>` with a worktree at `<main>/.current-work/<invocation-branch>/story/<id>`;
      - checks the worktree registration;
      - runs `verify-base`, which writes `<worktree>/.current-work/verify-base-ok`;
      - records `branch`, `worktree`, and `base_sha`;
      - writes the step manifest to `<worktree>/.current-work/<fb>/story/<id>/current-step.yml` (dispatch_lib:1114-1117);
      - sets the story to `prepared` (:941-1088).
    - `prepare-story` does the same for a serial link, from the predecessor's `commit_sha`.
    - `mark-dispatching` and `mark-dispatched` surround the spawn (ia:126).

04. **Per-story work.** The developer agent runs TDD and commits `feat: … (ST-NNNN)`, setting `status: done` itself (developer-agent:82). It writes `docs/spec/work/spec-feedback-<id>.md` only when it finds drift (:83).

05. **Gates.**

    - `verify-story --sha` checks the commit exists, sits on the story branch and is ahead of its base. It sets `verify_base: pass` and `commit_sha` (:1576-1641).
    - The dispatcher then runs the gates from the story worktree with `--report-dir <invocation-worktree>/.current-work/<gate>`. Each gate writes `<gate>/<id>.json` (ia:241-256).
    - The fix loop allows 3 iterations per tier, then `mark-failed --class acceptance_unmet` and `escalate`, for at most 6 spawns (ia:258-278).
    - Each fix starts with `refresh-story`, which merges the invocation branch into the story branch. On a conflict the story becomes `blocked` with reason "refresh conflict" (:1678-1771).

06. **Story merge.** `merge-story` must run on the invocation branch (:1774-1985). In order, it:

    - refreshes the story branch;
    - runs `premerge-check` with the outputs and touches, the story file, the drift report, INDEX.yaml and a scaled `--max-files`;
    - runs `git merge --no-ff`, then rewrites `status: done` into the story file and amends the merge commit;
    - copies `packages/factory` over `.agent-factory/factory`;
    - runs the test command;
    - removes the worktree and deletes the branch with `git branch -d`, with return codes ignored;
    - sets `commit_sha` to the merge SHA, the story to `done`, and `branch_head`.

    On a conflict it aborts and blocks the story. On red tests it runs `git reset --hard` back to the pre-merge commit and blocks the story.

    `premerge-check` writes `<toplevel>/.current-work/premerge-check-ok` with `branch=` and `head=` (premerge-check:87-96). It reads gate results only for branches named `story/ST-\d+` (:170, :420-438).

07. **Drift rows.** After each merge, the dispatcher sends out each row's owner, then that owner's reviewer. Those sessions commit on the invocation branch (ia:133, dc:225-236, ADR-0029:57-61).

08. **Wave close.** `close-wave N` refuses while a story is non-terminal or a drift row is `open`, or `fixed` on a core-list artifact. It reads the reports at the invocation branch head and appends a `waves:` record that sets `branch_head` (:2064-2097, dispatch_lib:362-427). Then the dispatcher routes the open QA findings (ia:137-141).

09. **Feature merge to dev.** Only bp:48 states it: "the invocation branch merges back to `dev`". `suggest-merge-args` prints a `--max-files` value (:2009-2030). No agent step owns this merge. A raw `git merge` by an agent needs the `premerge-check-ok` marker (hook:116-145), and the semantic gates are skipped for a non-story branch.

10. **End and cleanup.** The rules are written in dc:304-327 (Completed Close and Abandoned Close) and rules.md:126. No command does it (todo.md:186-205, T-0014). The ledger field `closed` is never set to true (dispatch_lib:334, 437, 456).

**By hand (manual mode)**

1. The human creates `feature/<name>` from `dev` with `git checkout -b` or adopts the current branch. There are no story branches, worktrees, ledger, or scripts (bp:35-37, ia:157-158).
2. The human confirms the next ready story (ia:160).
3. The developer agent runs with `--no-stage --no-commit` and runs the gates itself, with `--report-dir .current-work/<gate>` (developer-agent:81, ia:163-167).
4. The human commits and sets `done` unless a drift report exists (ia:169-173).
5. A code-review agent reviews the commit, writes `docs/reviews/code-review-*.md` and files `IMPL-*` findings. A fresh developer agent fixes them and the human commits (ia:175-183).
6. Drift rows are handled per story. The story closes only when its rows pass the BR-062 check, and the QA findings are routed then (ia:185-192, dc:242, BR-064).
7. The human pushes (ia:194). The by-hand mode has no merge step and no cleanup.

## 2. State inventory

| State                                                           | Created by                                               | Read by                                                             | Removed by                                                                                                  |
| --------------------------------------------------------------- | -------------------------------------------------------- | ------------------------------------------------------------------- | ----------------------------------------------------------------------------------------------------------- |
| Ledger `.current-work/<branch>/dispatch-ledger.yaml`            | `init`, then every mutating subcommand                   | all subcommands; `_default_ledger`; hook:68-79 (any ledger present) | nobody                                                                                                      |
| `waves:` closeout records                                       | `close-wave`                                             | nobody in code                                                      | nobody                                                                                                      |
| Invocation worktree (`…/invocation` or `.current-work/impl-…`)  | `init`                                                   | `merge-story` (must run there)                                      | nobody                                                                                                      |
| Story branch and worktree                                       | `prepare-*`, `re-dispatch`                               | the developer agent, `refresh-story`, gates                         | `merge-story` on success; `re-dispatch`                                                                     |
| Blocked or failed story branch and worktree                     | —                                                        | —                                                                   | nobody (dc:316 says keep them)                                                                              |
| `verify-base-ok` (per worktree)                                 | `verify-base`                                            | hook, on `git commit` in a linked worktree                          | `verify-base` clears it before each run; otherwise it goes with the worktree                                |
| `premerge-check-ok` (one slot per checkout)                     | `premerge-check` on PASS                                 | hook, on `git merge`                                                | overwritten by the next check (bp:78); never deleted                                                        |
| Gate results `.current-work/<gate>/<id>.json`                   | gate scripts                                             | `premerge-check`, the dispatcher                                    | nobody                                                                                                      |
| Step manifest `current-step.yml`                                | `prepare-*`                                              | step-guard                                                          | `mark-done` and `clear-manifest`. Neither is cited in ia or dc. `merge-story` removes the worktree instead. |
| Ledger `gate_results`                                           | nobody: always `{}` (dispatch_lib:217)                   | —                                                                   | —                                                                                                           |
| Story file `status`                                             | developer agent; `merge-story` (`done`); human (manual)  | `plan`, ia                                                          | —                                                                                                           |
| Drift report `docs/spec/work/spec-feedback-<id>.md` (committed) | developer agent; owners and reviewers set the row status | `close-wave`; the human (manual)                                    | nobody                                                                                                      |
| Briefs and scratch under `.current-work/<branch>/`              | parent agents (dc:94-99)                                 | children                                                            | nobody                                                                                                      |

Ledger story statuses are pending, prepared, dispatching, dispatched, done, failed and blocked (dispatch_lib:37-44). Story files in `backlog/` hold only `done` (374), `pending` (21) and `rejected` (3).

The repository today holds:

- 6 ledgers, all `closed: false` and all terminal. One is nested at `.current-work/feature/counter-ids-fitting/.current-work/feature/counter-ids-fitting/dispatch-ledger.yaml`, because `init` used the worktree's toplevel.
- 13 extra worktrees and 36,109 files under `.current-work/`.
- 6 `story/dsl-poc-*` branches, which `premerge-check` would not gate.
- ST-0344, `blocked` in the core-artifact-layout ledger, whose branch and worktree no longer exist.
- A stray `feature/my-work` branch. That is the name used in the spec scenario at md:238.

## 3. Contradictions

- **Ledger schema.**
  - dc:254-273 lists `declared_base`, `premerge_check` and `merge_sha`, with `stories` as a list.
  - The code uses `base_sha`, has no `premerge_check` field, keeps no `merge_sha` (it overwrites `commit_sha`), and stores `stories` as a map. `verify_base: pass` is set by `verify-story`, not by `verify-base` (:1633).
  - rules.md:127 requires "gate results … merge SHA" in the ledger. Neither is recorded.
- **Who sets `done`.**
  - dc:215 and :221 say "same commit that delivers the implementation". developer-agent:82 says "set `status: done`".
  - ia:131 says merge-story "owns … the `status: done` update", and the code amends it into the merge commit.
- **Failed stories.** ia:132 says "Failed stories stay `pending`". The ledger state machine records `failed` as terminal (md:86-89, dispatch_lib:353-358).
- **Gate cap.** ADR-0012:50 and :92 say "three fix iterations before the story is marked blocked". ia:273-278 says `mark-failed`, then escalate, up to 6 spawns.
- **Who runs the gates.** ADR-0012:25 and :98 say "The developer agent never runs validation scripts." developer-agent:81 has the developer run them in manual mode. rules.md:114 says that in manual mode "the human owns all … gate decisions".
- **Wave gate.** ADR-0029:66-68 says `prepare-wave N` "refuses while the ledger does not record wave N-1 as closed". The code checks only that prior-wave stories are terminal (:950-965).
- **Merge waits for drift sessions.** ADR-0029:59 says "The next `dispatch merge-story` waits until the sessions … have committed". `merge-story` has no such check.
- **Installed-copy sync.** dc:335 says "This is a manual step; no automated hook exists yet". `merge-story` copies `packages/factory` into `.agent-factory/factory` (:1926-1932).
- **Test command source.** md:185 and :219 and interface-contracts:23 say `config/project.json`. The code reads `docs/testing.yaml` (:600-606).
- **Plan has side effects.** md:125 says plan makes "No state changes". `plan` writes wave numbers into the ledger.
- **Init uniqueness.** md:192-196 and PROP-0021 refuse init per target branch. The code refuses while any non-terminal ledger exists anywhere (:733-746).
- **Branch root.**
  - bp:101 says "the SHA on `main`/trunk the invocation branch was cut from".
  - bp:52 and rules.md:102 say the invocation branch comes from `dev`.
  - The code records the invocation branch tip at init, which for an adopted branch is not its base.
  - rules.md:103 also calls the story branch's origin "the branch root".
- **Manifest path.** md:304 and :612 say `.current-work/<fb>/<story-branch>/current-step.yml`. interface-contracts:41 says `.current-work/current-step.yml`. The code puts it at `<worktree>/.current-work/<fb>/<story-branch>/current-step.yml`.
- **Red suite.** md:418 says "the merge commit is reverted". The code runs `git reset --hard` (:1957).
- **Abandoned close.** dc:326 says `git branch -D`, which the hook denies (hook:154). dc:325 introduces a story status `abandoned` and an `abandonment:` key, and neither exists in the code.
- **Hook message.** The hook suggests `.current-work/<branch>` (hook:91). bp:25 says `.current-work/<feature-branch>/<branch>`.
- **Handoff.** ia:51 sets `handoff-to: code-review-agent`. ia:303 says "Run reconciliation-agent, then QA".
- **Close scope.** dc:310 defines a completed close as "all stories in the wave", although it describes a whole dispatch.

## 4. Gaps

- No source says when a dispatch ends or how a reader tells that a ledger is finished. `closed` is never written. story-workflow.md:176 would define "a dispatch runs while a ledger exists", and this repo's old ledgers would then always count as a running dispatch.
- No command removes the invocation worktree, the gate results, the markers, briefs, scratch, or old ledgers.
- No one owns the feature-to-dev merge or its checks in either mode.
- Blocked branches are to be "left for manual resolution" (dc:316). No source says who resolves them, how, or by when.
- The developer of a failed attempt keeps its branch. No source says what happens to it if nobody re-dispatches.
- Manual mode has no merge and no story branch, so `premerge-check` cannot run there. Nothing mechanical enforces BR-064. The gate results written in manual mode are read by nobody.
- Resuming after interruption is specified per subcommand only. No source covers a dispatcher session that dies between subcommands, beyond "Recover from the ledger" (ia:118).
- A non-ST story branch name skips the semantic gates silently.
- One code-review report per date (`code-review-YYYY-MM-DD.md`, code-review-agent:87) means several story reviews on one day share a single file name.
- Drift-report and QA-finding lifecycles after the feature merges are not defined.

## 5. Terms

- Orchestrated, automated, mechanized dispatch, and dispatch workflow all name the same mode.
- Manual mode, by hand, and human-driven all name the other mode.
- Invocation branch and feature branch (bp:33, ia:71) mean the same thing. But "feature branch" also means the story branch in rules.md:100 and :103, bp:76, and the ia prompt templates (ia:149, :294). The ledger field `feature_branch` holds the invocation branch.
- Gate-check loop (ia:219) and gate-check step (story-workflow:111) are the same thing. ADR-0012 calls it the semantic gate loop. "Gates" also names test guardrails, quality gates and semantic gates.
- Dispatch, run, and invocation are used for the same thing. "Dispatch" also means a single agent spawn (dc:121).
- Declared base and `base_sha` are the same value.
- Merge SHA and `commit_sha` after the merge are the same value.
- Terminal state means done, failed or blocked in the code, and "merged or blocked/failed record" in dc:204.
- Wave closeout record, `waves:`, and "wave recorded as closed" (ADR-0029) are the same record.
- Primary checkout and main checkout are the same thing.
- Drift report and spec-feedback report are the same thing.
- Story close (manual) and story `done` (orchestrated) are not defined as the same event.

**Points of story-workflow.md that touch this process:**

- one workflow for both modes;
- a code review per story before the gates in orchestrated mode;
- the developer commits in manual mode;
- by hand: one story branch per story from `dev`, which replaces today's single feature branch;
- `done` set in the developer's last commit when driven by hand;
- three new `premerge-check` checks: a review exists, no open finding for the story, and a rerun of the gates that ignores stored results;
- a `story` field on findings;
- the guardrail split into checks that always apply and checks that apply while a ledger exists;
- the contents of the handback.

It defers the dispatch close (T-0014) and repeat-review limits (story-workflow.md:197).
