---
type: code-review
title: Code review of the counter-ids implementation
date: 2026-11-06
status: pass
reviewer: code-review-agent
findings_filed: 2
branch: feature/counter-ids
branch_base: b7ce0d2b70d9121cc3b54a313e08ba333d1123b0
branch_head: 585dda18af573c86ce99dc5c3db1e00c6fee880b
---

# Code review of the counter-ids implementation

## Result

The review found two major defects. Neither defect is in use, so neither is critical. First, a claim over SSH ignores the ssh command that the user set in git, so a user whose key comes from `core.sshCommand` gets no ID. Second, `rules.md` and two other texts send every ID to `next-id`, including `PROP` IDs that `next-id` refuses. The claim loop, the leases, the throwaway repository, and the `init-factory` check hold. Next, the Implementation Agent fixes IMPL-0004 and IMPL-0005 and submits the branch for review again. The branch is not ready for reconciliation.

## Scope

The review covers `git diff dev...feature/counter-ids` at `585dda18`. That diff holds ST-0368, ST-0369, ST-0370, ST-0372, ST-0373, ST-0374, ST-0375, and the follow-up commit for DEC-25. The review read the code and the text that agents execute:

- `packages/factory/scripts/next-id` and the new `check_counter` in `init-factory`
- `tests/factory/test_next_id.py`, `test_next_id_race.py`, `next_id_race.py`, `test_init_factory_counter.py`, `test_counter_ids_text.py`, and the new cases in `test_block_dangerous_git.py`
- `rules.md`, `branching-policy.md`, `finding-format.md`, `todo-format.md`, `bug-fix.md`, `planning-agent.md`, `create-backlog/SKILL.md`, and `write-adr/SKILL.md`

The review checked them against the stories `backlog/ST-0368.md` to `ST-0375.md`, `interface-contracts.md` § Counter IDs Contracts, BR-068 to BR-076, `dependency-rules.dsl`, the Decisions table of `counter-ids.md` up to DEC-25, ADR-0031, and ADR-0032. The changed spec and backlog files are out of scope, because the reconciliation run covers them.

The classification follows the accepted proposal `finding-classification.md`, as the brief requires: category, type of the code class, and severity from the three questions. The review did not run the suite, as the brief says. It reproduced IMPL-0004 with a temporary `HOME` and the `next-id` script of the branch head.

## Findings

| Finding                                                                                                                                                                                                                                                                                          | Artifact                                                                                                                | Category   | Type      | Severity |
| ------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------ | ----------------------------------------------------------------------------------------------------------------------- | ---------- | --------- | -------- |
| [IMPL-0004](../findings/IMPL-0004.md): `CLAIM_ENV` sets `GIT_SSH_COMMAND` to `ssh -o BatchMode=yes`. That replaces the user's own `GIT_SSH_COMMAND` and overrides `core.sshCommand`, so a claim fails for a user who picks a key there. Keep the user's ssh command and add `-o BatchMode=yes`.  | `packages/factory/scripts/next-id:68`                                                                                   | defect     | interface | major    |
| [IMPL-0005](../findings/IMPL-0005.md): `rules.md` says to claim every ID through `next-id`, and two texts list `PROP-NN` among the IDs that `next-id` hands out. `next-id` refuses `PROP` (BR-068, DEC-09). Limit the statements to the prefixes of BR-068 and name the IDs outside the counter. | `packages/factory/rulebooks/rules.md:101`, `:158`; `conventions/branching-policy.md:41`; `agents/planning-agent.md:110` | defect     | function  | major    |
| IMPL-0006 (register `docs/findings/register/code.jsonl`): the test name `..._names_the_seven_tags_for_next_id` checks nine tags. Rename it.                                                                                                                                                      | `tests/factory/test_counter_ids_text.py:139`                                                                            | suggestion | test      | minor    |

## Notes

These observations need no change. They stay in this report only.

**Broken sentence on a push over the time limit.** `claim_loop` puts "the claim of ST-1001" in front of every `NextIdError` from `push`. A push over the time limit then reads "the claim of ST-1001 a git call on /r.git ran over the time limit of 30 seconds". The message still names the remote and the limit, as the contract requires.

**Tracebacks on unlikely git failures.** `rev-parse` and `show` in `RemoteCounter.read`, `git init` in `throwaway`, and `_commit` in `seed` raise `CalledProcessError` without a message of `next-id`. A missing `git` binary raises `FileNotFoundError`. Each case prints a traceback to standard error, exits 1, and prints nothing to standard output. Each needs a failure that the fetch just before it did not show.

**`init-factory` can show an ssh passphrase prompt.** `check_counter` sets `GIT_TERMINAL_PROMPT=0` but not `BatchMode`. With a key that needs a passphrase and no agent, ssh asks on the terminal. The 15-second limit then ends the check, and the install finishes.

**`RECON` is in the `next-id` list but not in the tag table.** `finding-format.md` names `RECON` for `next-id`, as BR-068 requires. Its tag table has no `RECON` row, which follows `interface-contracts.md`. A reader may wonder which review files `RECON` findings.

**The claim-push exception appears twice in `rules.md`.** § Dispatch and § Git workflow both state it. ST-0374 requires both places, so the repetition is intended.

## Checks without a finding

**Prefix and seed checks.** `check_prefix` and `parse_seed` run before `resolve_remote`, so a wrong argument contacts no remote (BR-068, BR-069). The seed refuses `10000`, `abc`, `ST=x`, an unknown prefix, and a second pair, and names what BR-069 asks for. `number_lines` writes four digits (BR-070).

**Claim loop.** `raise_line` raises the prefix's line, gives a new prefix `start` plus one, keeps every other line, and writes a new token (BR-071). The push carries the lease on the SHA that the read returned. Only the two stale-lease messages retry. The tenth stale lease ends the claim without a tenth wait and names the prefix and the last ID (BR-072). The seed uses the create-only lease and maps both `stale info` and `already exists` to the "already exists" message (BR-073).

**Remote and throwaway repository.** `resolve_remote` uses `git remote get-url origin`, so URL rewrites apply, and names `origin`, `--remote`, and the seed when both are missing (BR-074). Every call runs with `--git-dir` on a bare repository in a new temporary directory, so the clone gains no ref and no object. The fixed identity lets a clone without `user.name` claim (BR-075).

**Time limit.** Every claim call, including `git init`, is guarded. On POSIX, `subprocess.run` kills git at the limit and waits only for git, so the limit holds. The seed calls run unguarded and keep prompts (BR-076, ATAM-0012).

**`init-factory`.** `check_counter` only runs `ls-remote` on `origin`. It never seeds or pushes, and no case stops the install (DEC-17, DEC-23). Each of the three messages matches the Contract of ST-0375. A closed port fails at once, and a silent host ends after 15 seconds.

**Producer texts.** `create-backlog`, `finding-format.md`, `bug-fix.md`, `todo-format.md`, and `write-adr` name the installed path, read the ID from standard output, and stop on a failure (ST-0372). The split rule keeps its letter scan. `finding-format.md` lists `ARCH` and `QA` (DEC-25). The guardrail hook is unchanged, and its tests pass the three command texts of ST-0374.

**Architecture.** `next-id` uses only the standard library and imports nothing from `usage`, so `dependency-rules.dsl` holds. The `Counter` protocol separates the claim loop from git, which lets the unit tests drive the loop without a remote (DEC-11).

## Pass 2

Pass 2 reviews the fix commit `3da01aa8dc31e48f1986b0cfd6e0b1f6516aa6f7` on `fix/impl-0004-0005`, diffed against `feature/counter-ids` at `585dda18`. It checks the three findings of pass 1 and looks for new defects in the fix only. The fix holds for all three findings, and it adds no blocking defect. The branch may go to reconciliation once the fix is merged into `feature/counter-ids`.

| Finding   | Outcome                                                                                                                                                                                                                                             |
| --------- | --------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| IMPL-0004 | Resolved. `ssh_command_with_batch_mode` takes `GIT_SSH_COMMAND`, else `core.sshCommand`, else `ssh`, and adds ` -o BatchMode=yes`. The reproduction of pass 1 now runs the user's script. The spec-feedback row for BR-076 is filed.                |
| IMPL-0005 | Resolved. The four statements name only the prefixes that `next-id` serves. They drop `PROP-NN` and name `PROP` rows and split letters as outside the counter.                                                                                      |
| IMPL-0006 | Resolved. The test is now `test_st_0372_finding_format_names_every_tag_for_next_id`. The register holds unfixed findings only, so its line is removed from `code.jsonl`. This report keeps the record.                                              |
| IMPL-0007 | New, `minor`, register line. The fixed texts say that the prefixes are listed in `finding-format.md`, but that list holds only the nine finding tags. `ST`, `T`, and `ADR` are missing. Each producer file names its own prefix, so no claim fails. |

**Notes on the fix.** These need no change.

- `ssh_command_with_batch_mode` reads `core.sshCommand` in the current directory, so a value in the clone's local config also reaches the claim. Plain `git fetch` in the clone uses that value too. The Credentials row of the contract names only a credential helper as local config that does not reach the claim, so the row stays true.
- A user who sets only the older `GIT_SSH` variable still gets plain `ssh`, because `GIT_SSH_COMMAND` ranks above `GIT_SSH`. Pass 1 behaved the same way.
- Every guarded git call now starts one extra `git config` process. A claim makes at most about twenty guarded calls, so the cost is small.
