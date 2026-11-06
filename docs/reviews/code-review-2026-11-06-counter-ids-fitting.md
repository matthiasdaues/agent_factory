---
type: code-review
title: Code review of the counter-ids-fitting implementation
date: 2026-11-06
status: defects
reviewer: code-review-agent
findings_filed: 3
branch: feature/counter-ids-fitting
branch_base: 8c358125090f6764f123e56d092c43f8d1c53731
branch_head: bda10b05d4ccb75109e49ee0ae44731c4ce828b8
---

# Code review of the counter-ids-fitting implementation

## Result

The review found three major defects. None of them is in use, so none is critical.

1. The move pushes from the project's own repository, so the project's pre-push hooks decide whether it succeeds.
2. A resumed move can put C back on the local counter after `origin` has gained a counter that grew from C. Two counters then hand out the same number.
3. The session-start check shows VIRGIL the `origin` URL with its token.

The seed plan, the local counter, `init-factory`, and the ID producer texts hold. The fix of BUG-0118 holds, so BUG-0118 is `resolved`.

Next, the Implementation Agent fixes IMPL-0008, IMPL-0009, and IMPL-0010 and submits the branch for review again. The branch is not ready for reconciliation.

## Scope

The review covers `git diff dev...feature/counter-ids-fitting` at `bda10b05`. That diff holds ST-0376 to ST-0385 and the fix of BUG-0118. The review read the code and the text that agents execute:

- `packages/factory/scripts/next-id` with `--plan-seed`, the local counter, and `--move-to-origin`
- `check_counter`, `record_counter_seeded`, and the six-key status in `init-factory`, and `housekeeping-about`
- `virgil.md` § Fitting, the four `AGENTS.*.md` files, `session-menu.md`, `id-prefixes.md`, `rules.md`, `branching-policy.md`, `finding-format.md`, and every ID producer file that ST-0384 and ST-0385 changed
- the new and changed tests in `tests/factory/`

The review checked them against the stories `backlog/ST-0376.md` to `ST-0385.md`, `interface-contracts.md` § Counter IDs Contracts, BR-096 to BR-108, the Move Lifecycle, and ADR-0033. The Decisions DEC-01 to DEC-15, ADR-0031 to ADR-0033, and CIFP-C01 to C18 count as settled. The changed spec and backlog files are out of scope, because the reconciliation run covers them.

The classification follows the accepted proposal `finding-classification.md`, code class. The review did not run the suite. It ran four reproductions with the `next-id` of the branch head in temporary repositories, and two revert checks of the story tests in a temporary copy of the tree. No reproduction used a real remote or a real token.

## Findings

| Finding                                                                                                                                                                                                                                                        | Artifact                                     | Category | Type          | Severity |
| -------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- | -------------------------------------------- | -------- | ------------- | -------- |
| [IMPL-0008](../findings/IMPL-0008.md): the move runs `git -C <local> push`, so the project's pre-push hook runs. For the root commit C, the pre-commit framework runs every hook on all files. A slow hook cuts off every move, and a failing hook refuses it. | `packages/factory/scripts/next-id:725`       | defect   | interface     | major    |
| [IMPL-0009](../findings/IMPL-0009.md): a resumed move that finds `origin` empty and then meets a refused push restores C. ADR-0033 keeps the marker for a resume collision. A reproduction handed out `ST-0013` twice.                                         | `packages/factory/scripts/next-id:869`       | defect   | algorithm     | major    |
| [IMPL-0010](../findings/IMPL-0010.md): check 2 of § Counter check runs `git remote get-url origin`, which prints the URL with its token to VIRGIL. BR-077 and the boundary of ST-0382 forbid that.                                                             | `packages/factory/config/session-menu.md:12` | defect   | checking      | major    |
| IMPL-0011 (register `docs/findings/register/code.jsonl`): step 4 names the parent of `git rev-parse --git-common-dir` without "absolute". In the main worktree, the command prints `.git`. Name `--path-format=absolute`.                                      | `packages/factory/agents/virgil.md:304-306`  | defect   | documentation | minor    |

## Points the dispatcher asked about

**ST-0383 and the loosened pointer test.** No requirement is left unchecked. `test_impl_0005_file_links_the_prefix_list_and_names_ids_outside_the_counter` now accepts `id-prefixes.md` or `finding-format.md`. BR-108 names three files that point to `id-prefixes.md`: `rules.md`, `branching-policy.md`, and `finding-format.md`. `test_st_0383_file_points_to_id_prefixes` checks exactly those three. `planning-agent.md` is not among them, so the looser test only lets its old link pass. That link at `planning-agent.md:110` still says that the prefixes are "listed in finding-format.md § File location and name". `finding-format.md` now links to `id-prefixes.md`, so the reader finds the full list one link further. The `rules.md` and `branching-policy.md` parts of IMPL-0007 are fixed. The `planning-agent.md` part remains, so the IMPL-0007 line stays in the register.

**ST-0378 and ST-0384: tests written after the code.** Both sets of tests fail without the code they guard. The review copied the branch head with `git archive` into a temporary directory. In one copy, it put back the `init-factory` of the parent of `9eef5941`. All three `test_st_0378_*` tests failed, and two `test_st_0375_*` tests failed on the changed messages. In the other copy, it put back the 17 files that `625ea474` changed outside `tests/` and `backlog/`, as they stood in its parent. Every `test_st_0384_*` claim test failed. The contract test of the checker, `test_st_0384_checker_names_the_file_and_prefix_of_a_dropped_claim`, passed, because it builds its own fixture in `tmp_path`.

**A counter on `origin` during a resume.** Two counters can hand out the same number, so IMPL-0009 is filed. With `origin` at exactly C, git treats the push as up to date. The move then succeeds and removes the setting, and no number goes out twice. The duplicate needs a counter that grew from C, for example after a second move pushed C and a clone claimed one ID. The setting must also stay, which happens when that second move is cut off before it removes the setting. The reproduction forced this order and got `ST-0013` from both counters. In the same case, the message "the move changed nothing" is false, because the local ref changed from the marker back to C.

**BUG-0118.** The fix holds. `FITTING_STEPS` lists `counter_seeded` as "seed the ID counter", and `read_fitting` counts against the length of the list. `TestAllSixFittingSteps` checks `6/6` and the step name. The status is set to `resolved`.

**Security.** No new mode prints a token. Every line of `next-id` passes through `RedactingStream`, and the marker message is redacted before git stores it (BR-097). The new `init-factory` messages use the redacted URL. The one leak is in the text that agents execute, IMPL-0010. Every git call of `--plan-seed` that reaches a remote is guarded. So are all calls of `--move-to-origin`, including `ls-remote --get-url` and the collision read. The local reads of `--plan-seed` (`for-each-ref`, `ls-tree`, `cat-file`) cannot prompt. `next-id --seed` keeps git's prompts, as BR-076 states. VIRGIL runs it in an agent shell, which ATAM-0015 records, so this review files nothing on it.

## Notes

These observations need no change. They stay in this report only.

**A failed move push hides the hook output.** `_git_error` returns only standard error. A pre-push hook writes its reason to standard output, so the message shows only "failed to push some refs". The fix of IMPL-0008 removes the hook from the push, so this note needs no separate change.

**Greenfield projects reach step 4 only through a recommended action.** `virgil.md` walks a greenfield project through step 0 and step 4. The First-session insight never recommends fitting, and the greenfield branch of the AGENTS files shows no fitting prompt. Step 0 has the same entry today, so step 4 follows an existing pattern.

**The `init-factory` check runs without `BatchMode`.** `check_counter` sets `GIT_TERMINAL_PROMPT=0` but not `BatchMode`. The review of counter-ids noted this, and the new remote order does not change it.

**The register of IMPL-0007 names three files.** Only `planning-agent.md:110` still carries the gap. The line stays as written, because the register holds unfixed findings and the remaining part is unfixed.

## Checks without a finding

**`--plan-seed`.** The plan reads the counter first and stops on a claim commit or a marker (BR-098, BR-097). It counts file names of `backlog/`, `docs/findings/`, and `docs/adr/`, register `id` fields, and todo headings on every local and remote-tracking branch and in the working tree (BR-099). It never reads body text. `SPEC-011-title.md` counts as 11 with a warning, `ST-0380A.md` counts as 380 without one, and `BUG-HUNT.md` does not count (BR-100). The pairs follow `PREFIXES` and use the highest number (BR-101).

**Local counter.** `resolve_remote` takes `--remote`, then the setting, then `origin` for a claim, a seed, and the plan (BR-096). A claim on the local counter uses the same throwaway repository and leased push as a claim on a remote (ADR-0033).

**Move steps.** The marker has C as its only parent and the one line `moved=<remote>`. The lease on C retries on both stale-lease messages, at most ten times, and the tenth stale lease sets no marker (BR-102, BR-103). The forced race in `test_st_0381_a_claim_between_the_read_and_the_marker_reaches_origin` runs a real claim, so no timing decides the result. The three resume rows match the contract table, apart from IMPL-0009.

**`init-factory`.** `check_counter` asks the setting, then `origin`, and returns `True`, `False`, or `None`. `record_counter_seeded` skips the write on `None`, recomputes the status for a fitted cache, and leaves a greenfield status as it is (BR-105, CIF-G07). `_fitting_status` counts six keys.

**Agent texts.** Step 4 follows step 3, shows the printed seed command, runs it only after confirmation, and names the four endings of BR-104. The four AGENTS files count six keys. `id-prefixes.md` holds twelve rows, and the text test compares it with `PREFIXES`. Every producer file names its literal prefix and its stop rule (BR-107). No file holds `next-id <TAG>`.

**Architecture.** `next-id` still uses only the standard library. The move reaches git through `LocalCounter` and the module-level push, as ST-0380 built it. BUG-0117 covers the gap between the port and the architecture.

## Pass 2

Pass 2 reviews the fix commit `23d1c6e54e596f286eda4cda8ef5354126183a17` on `fix/impl-0008-0010`, diffed against `feature/counter-ids-fitting` at `3e7ca328`. It checks the three blocking findings of pass 1 and looks for new defects in the fix only. The fix holds for all three findings, and it adds no blocking defect. The branch may go to reconciliation once the fix is merged into `feature/counter-ids-fitting`. One question about the first move still needs the stakeholder's answer, and it does not block reconciliation.

| Finding   | Outcome                                                                                                                                                                                                                                        |
| --------- | ---------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| IMPL-0008 | Resolved. `push_to_origin` fetches the local counter into a throwaway repository and pushes C from there. The scratch project with a pre-commit pre-push hook that sleeps 35 seconds now moves the counter at once, and the hook does not run. |
| IMPL-0009 | Resolved for the resume path. The reproduction of pass 1, run against the fix, keeps the marker and the setting, and the next local claim fails by BR-097. The question below covers the first move.                                           |
| IMPL-0010 | Resolved. Check 2 uses `git remote` and a match on the line `origin`. A new text test refuses every command that prints a URL.                                                                                                                 |
| IMPL-0012 | New, `minor`, register line. `test_impl_0009_a_refused_push_finishes_when_origin_holds_c` pushes exactly C, so git accepts the move's push as up to date. No test runs the branch `on_origin == move.sha` in `_after_refusal`.                 |

**Question for the stakeholder: a first move that meets a counter grown from C.** The race of IMPL-0009 also reaches a first move. Take move A, which sets the marker, and move B, which reads that marker and resumes. B pushes C, a clone claims `ST-0013` on `origin`, and B is cut off before it removes the setting. Then A's push is refused. A is a first move, so it restores C, as BR-102 and the contract row "`origin` holds a counter" require. The setting stays, and the next claim in the clone returns `ST-0013` again. A scratch run against the fix showed exactly this. The code follows the specification here, so the review files no code defect. A first move cannot tell an independent seed from a counter that grew from C, because a claim commit has no parent.

- Option 1: a first move also keeps the marker when `origin` holds a counter. No number goes out twice. Claims in the clone then fail until a human resolves the collision (CIF-G03), even when someone else seeded `origin` on their own.
- Option 2: keep the restore. A duplicate then needs two moves at once, a cut-off, and a claim in the window.

The review recommends option 1. QS-22 asks for no duplicate, and a collision needs a human under both options. The answer changes BR-102, the contract row, and the Move Lifecycle. The coordinator should record the question as a todo entry for the domain-modeling agent.

**Notes on the fix.** These need no change.

- A resumed move whose push fails for another reason now keeps the marker, and the message says so. The contract has no row for that case yet. `spec-feedback-IMPL-0008.md` names it for the domain-modeling agent.
- When the second `ls-remote` fails, `_after_refusal` treats `origin` as empty. A first move then restores C, and a resumed move keeps the marker. Both are the safe outcome.
- A hooks path in the user's global git config still applies in the throwaway repository, as it does for a claim. `init-factory` installs its hooks per repository, so no Factory hook runs there.
