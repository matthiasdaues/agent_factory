---
schema_version: 2
title: Git Guard and Merge Gates
status: draft
owner: Matthias Daues
created: 2026-10-27
updated: 2026-10-27
supersedes:

impact:
  scope: cross_component
  architecture_change: true
  external_contract_change: true
  boundaries:
    - packages/factory/config/hooks/block-dangerous-git.sh
    - packages/factory/config/extensions/block-dangerous-git.ts
    - packages/factory/scripts/verify-base
    - packages/factory/scripts/premerge-check
    - packages/factory/scripts/commit-safe
    - packages/factory/scripts/dispatch
    - packages/factory/rulebooks/conventions/branching-policy.md

governance:
  assurance: high
  risk_domains:
    - data_integrity
    - reliability
    - operations

estimate:
  as_of: 2026-10-27
  basis: judgment
  confidence: low
  human_review_hours: unknown
  normalized_tokens: unknown
  estimated_consumption: unknown
---

# Feature Request: Git Guard and Merge Gates

## Primer

<!-- Written last by the write-primer skill, once the design is settled. -->

## Summary

The git guard reads each shell command the way git and the shell read it,
instead of matching text. The commit and merge gates check what can go wrong
at that moment: a commit checks that the branch descends from its recorded
base in the right worktree, and a merge checks by a trial merge that the
branch merges cleanly. A conflict in a file a tool regenerates, such as
`INDEX.yaml`, is resolved by running the tool. The first release covers the
shell hook that Claude Code, Codex, and Copilot run, the Pi extension,
`verify-base`, `premerge-check`,
`commit-safe`, and the `dispatch` commands `refresh-story` and
`merge-story`.

## Motivation

The guard is a list of regular expressions in
`packages/factory/config/hooks/block-dangerous-git.sh`, which Claude Code,
Codex, and Copilot run, with a second copy in TypeScript for Pi. It sees a command as one line of text. So it fails in
both directions:

- **It lets dangerous commands through.** In the bug-hunt review, a commit
  without a `verify-base` marker passed as `git -C . commit`,
  `command git commit`, `GIT_X=1 git commit`, or `cd . && git commit`. Hook
  bypasses passed as `git commit -nm x` and
  `git -c core.hookspath=/dev/null commit`. Destructive commands passed as
  `git reset -q --hard` or `git clean -xdf` (G-2, G-3 in
  [bug-hunt-2026-10-15.md](../reviews/bug-hunt-2026-10-15.md)). On
  2026-10-27, `git -C <path> push` and `git -C <path> merge` passed while
  `git push` was blocked. The test-command patterns are anchored at the
  start of the line, so `cd <worktree> && uv run pytest <file>` passes
  while `uv run pytest` is blocked.
- **It blocks harmless commands.** A commit message that mentions
  `git push`, a `grep` for `reset --hard`, and a `git log --grep` were
  denied. In `git merge --no-ff -m "merge msg" story/ST-0001`, the guard
  read the message as the branch name (G-5).

The gates check the wrong thing at the wrong time:

- **A running story stops when its target moves.** The guard accepts a
  commit while the `verify-base-ok` marker's head is an ancestor of HEAD.
  But `tests/factory/test_characterization_safety.py` runs `verify-base` in
  the real checkout, and that run deletes the marker. The `run-tests` hook
  runs the test on every commit that touches scripts or tests, so the next
  commit needs a new `verify-base`. That run demands that the branch holds
  every commit of its target, and fails once another story has merged. In
  the bug-hunt run, the back-merge and the refresh of ST-0308 needed the
  stakeholder to run commands with the `!` prefix.
- **`premerge-check` checks ancestry, not mergeability.** It fails a branch
  that does not contain its target, although the branch may merge cleanly.
  It passes nothing about conflicts.
- **A regenerated file blocks a merge.** ST-0308 was blocked by a conflict
  in `INDEX.yaml` alone. `index-lint` writes that file from the sources, so
  the conflict had one right answer, and a person still had to reopen the
  story by hand.
- **Markers do not say whom they authorize.** The `premerge-check-ok`
  marker records the branch and its head, not the target, and a failed run
  leaves it in place. After a pass against `dev` and a block against `main`,
  a merge into `main` was allowed (G-6). The `verify-base-ok` marker
  survives a branch switch in the same worktree (G-7). In the brownfield
  run, an agent ran `verify-base` in the invocation worktree instead of its
  own and left a marker there that would let an unchecked commit through.

The project has reached the point where agents meet these gates every day,
and each false block costs a stakeholder round trip.

## Core Principles

- **One parser, every CLI.** One program decides for every CLI. Each CLI's
  hook passes the command to it and relays the answer.
- **Parse, then decide.** A rule names a git subcommand and its options, not
  a text pattern.
- **Fail closed on what the parser cannot read.** A command that holds git
  and cannot be parsed is denied, with a message that names the reason.
- **Check what can go wrong now.** Freshness is checked when work starts and
  before a merge. A commit checks only where the work belongs.
- **A marker names whom it authorizes.** Every marker records the worktree,
  the branch, and the heads it was written for.

## Design

The design has five parts. Part 1 is the parser that the guard uses. Parts
2 to 5 change the gates the guard enforces.

### 1. The command parser

`packages/factory/scripts/git-guard` is a standard-library Python program.
It reads one shell command line on standard input and the hook's working
directory as an argument. It prints a decision as JSON: `allow` or `deny`,
with the reason.

The parser works in four steps:

1. **Split the line into simple commands** at `;`, `&&`, `||`, `|`, and
   subshell parentheses, with shell quoting applied. A `cd <path>` before a
   command changes the working directory of the commands after it.
2. **Strip the prefixes** that do not change the program: variable
   assignments such as `GIT_X=1`, and `command`, `exec`, `env`.
3. **Parse git's global options**: `-C <path>`, `-c <key>=<value>`,
   `--git-dir`, `--work-tree`, `--no-pager`. `-C` and `cd` together give the
   directory the command acts in. Configuration keys compare without regard
   to letter case.
4. **Parse the subcommand and its options**: bundled short flags such as
   `-nm`, unique abbreviations of long options such as `--no-verif`, and
   option values such as the text after `-m`, which the rules never read as
   a branch or a path.

The rules then read the parsed commands. A rule table in the same program
holds every rule of the current guard:

| Rule                    | Denies                                                                                                         |
| ----------------------- | -------------------------------------------------------------------------------------------------------------- |
| Destructive commands    | `reset --hard`, `clean -f`, `branch -D`, forced `push`, `checkout` or `restore` of a whole tree, `stash clear` |
| Hook bypass             | `--no-verify`, `-n` on `commit`, `core.hooksPath` in any case, `pre-commit uninstall`, `SKIP=` on a commit     |
| Push                    | every `push`; the stakeholder pushes                                                                           |
| Branch without worktree | `branch <new>`, `switch -c`, `checkout -b`, `checkout --orphan`                                                |
| Worktree path           | `worktree add` to a path that does not resolve under `.current-work/`                                          |
| Commit gate             | `commit` in a linked worktree without a valid commit marker (part 3)                                           |
| Merge gate              | `merge` and `pull` without a valid premerge marker (part 4)                                                    |
| Test command            | a test runner outside the hooks, with any prefix, such as `uv run pytest`, `python -m pytest`, `npm test`      |

Text inside quotes is an argument, never a command. So
`grep -rn "reset --hard" docs` and `git commit -m "explain git push"` pass.
A command that runs other text as a command, such as `bash -c '<text>'` or
`sh -c`, is parsed one level deep. A second level that holds git, as in
`bash -c "sh -c 'git push'"`, is denied as too deep to check (DEC-06). `eval`
with git in its arguments is denied.

The shell hook `block-dangerous-git.sh` and the Pi extension
`block-dangerous-git.ts` shrink to a call of `git-guard` and the relay of its
answer. The Pi extension starts `git-guard` as a Python process for each
Bash call, like the shell hook does (DEC-05). All four CLIs then share one
rule table and one test table.

### 2. The commit marker

`verify-base` writes `.current-work/verify-base-ok` with five fields:
`worktree` (the absolute path of the worktree root), `branch`, `base` (the
SHA the branch was cut from), `target`, and `head` (HEAD at the check).

A commit marker is valid for a commit when all three hold:

- `worktree` equals the root of the worktree the commit acts in, as the
  parser resolved it from `cd` and `-C`.
- `branch` equals that worktree's current branch.
- HEAD descends from `base`.

`commit-safe` runs the same check through `git-guard`, so a commit through
`commit-safe` meets the same gate as a direct `git commit` (G-2).

`verify-base` takes `--expect-branch <branch>` and refuses to write a marker
in a worktree on another branch. Dispatch briefs pass it. So an agent that
runs `verify-base` in the wrong worktree gets an error instead of a stray
marker.

### 3. When `verify-base` checks freshness

`verify-base` has two modes:

| Mode                        | When                                  | Checks                                                                                   |
| --------------------------- | ------------------------------------- | ---------------------------------------------------------------------------------------- |
| `--at-dispatch` (default)   | first tool call of a dispatched agent | not behind target; cut from the declared base; on the expected branch; writes the marker |
| commit check (in the guard) | every commit                          | the marker is valid (part 2); freshness is not checked                                   |

A story whose target moves on keeps committing (DEC-07). Freshness returns
at the merge: `merge-story` brings the target into the story branch, runs
the trial merge (part 4), merges, and runs the suite. A conflict in the
refresh blocks the story, and its next iteration starts with
`refresh-story`.

The marker lasts while it is valid. No test runs `verify-base` or
`premerge-check` in the real checkout; each test that runs them works in a
repository of its own under `tmp_path`.

### 4. The merge gate by trial merge

`premerge-check <target> <branch>` replaces the ancestry check with a trial
merge: `git merge-tree --write-tree <target> <branch>`. This writes no
working tree and no ref.

- **No conflict:** the check passes. The file-count and scope checks still
  read the diff `<target>...<branch>`.
- **Conflicts only in regenerable files** (part 5): the check passes and
  lists the files the merge regenerates.
- **Any other conflict:** the check fails and lists the conflicting paths.

The same trial merge runs in every direction the factory merges: a story
into the invocation branch (`merge-story`), the invocation branch into a
story (`refresh-story`), and the invocation branch into `dev`.

The marker `.current-work/premerge-check-ok` records `branch`,
`branch_head`, `target`, and `target_head`. `premerge-check` deletes the
marker at the start of every run. The merge gate allows a merge only when
all four fields match the merge the parser read (G-6).

### 5. Regenerable files

`packages/factory/config/regenerable-files.yaml` lists the files a tool
writes from other sources, with the command that writes each:

```yaml
---
regenerable:
  - path: packages/factory/INDEX.yaml
    command: packages/factory/scripts/index-lint
```

When `refresh-story` or `merge-story` meets a conflict whose paths are all
in this list, it takes the target's side of each file, runs the command,
stages the result, and concludes the merge. A conflict in any other path
stops the command as today.

## Scope

**In the first release:**

- `git-guard` with the four parsing steps and the rule table of part 1.
- The shell hook, which Claude Code, Codex, and Copilot run, and the Pi
  extension call `git-guard`.
- The commit marker with five fields, `--expect-branch`, and the commit
  check in the guard and in `commit-safe` (part 2).
- The two `verify-base` modes (part 3).
- `test_characterization_safety.py` runs `verify-base` in a repository
  under `tmp_path`, not in the real checkout (part 3).
- `premerge-check` by trial merge, the four-field premerge marker, and its
  deletion at the start of each run (part 4).
- `regenerable-files.yaml` with `INDEX.yaml`, and its use in
  `refresh-story` and `merge-story` (part 5).
- One test table of commands and expected decisions, run against
  `git-guard`: every reproduction in G-2 to G-7, the commands from
  2026-10-27, and the harmless commands of G-5.

**Explicitly deferred (do NOT plan stories for these):**

- **The `merge-story` file limit.** It scales with the number of `touches`
  entries, so one folder entry lowers the limit for many files. It is a
  scoping rule, not a git gate, and needs its own finding.
- **Diagram SVGs as regenerable files.** The `arch-lint` hook re-renders
  every SVG for a new timestamp. The fix belongs in `arch-lint`: write an
  SVG only when its drawing changes. Listing the SVGs as regenerable would
  hide that fault.
- **Hooks that run a stale installed copy.** In this repository, a hook ran
  `.agent-factory/factory/scripts/arch-lint`, older than the source, and
  blocked a correct commit. That is an install problem, not a gate problem.

## Design Details

- **Decision output.** `git-guard` prints
  `{"decision": "deny", "rule": "<rule name>", "reason": "<text>"}` and
  exits 0 on allow, 2 on deny. The shell hook passes exit code 2 on as a
  block, as it does today; the Pi extension reads the JSON.
- **Messages.** Each denial names the rule and the command that clears it,
  for example the exact `verify-base` call with the worktree's branch.
- **Speed.** The guard runs before every Bash tool call. `git-guard` reads
  git state only for commands that need it, such as a commit or a merge.
- **Markers and old installs.** A marker without the new fields is invalid.
  The first commit after the update asks for one new `verify-base` run.
- **Pull.** `git pull` counts as a merge of the pulled ref and needs the
  premerge marker for it.

## Open Questions

No question is open. The parser language for Pi and the depth of nested
shells are settled in part 1 (DEC-05, DEC-06).

## Completion Criteria

- Every command in G-2, G-3, and G-4 of
  [bug-hunt-2026-10-15.md](../reviews/bug-hunt-2026-10-15.md) is denied by
  `git-guard`, and every command in G-5 is allowed.
- `git -C <path> push`, `git -C <path> merge <branch>`,
  `cd <worktree> && uv run pytest <file>`, and `bash -c "sh -c 'git push'"`
  are denied.
- The shell hook and the Pi extension return the same decision for every
  row of the test table.
- In a story worktree whose target has moved ahead, a commit passes when
  HEAD descends from the recorded base and the marker names that worktree
  and branch.
- A commit is denied when the marker names another worktree path or
  another branch, both through `git commit` and through `commit-safe`.
- After `pre-commit run run-tests --all-files` in a story worktree, its
  `verify-base-ok` marker still exists and is unchanged.
- `verify-base --expect-branch story/ST-0001` run in a worktree on another
  branch exits non-zero and writes no marker.
- `premerge-check` passes a branch that is behind its target and merges
  cleanly, and fails a branch with a conflict, listing the paths.
- After a `premerge-check` pass for target `dev`, a merge of the same
  branch into `main` is denied.
- `merge-story` and `refresh-story` resolve a conflict in `INDEX.yaml` alone
  by running `index-lint`, without a person.

## Guiding Rule

A gate stops a command for what the command does, and lets it through for
nothing else.

# Appendix

## Decisions

| ID     | Date       | Kind     | Decided by  | Decision                                                                                                                            | Raised by                                                    |
| ------ | ---------- | -------- | ----------- | ----------------------------------------------------------------------------------------------------------------------------------- | ------------------------------------------------------------ |
| DEC-01 | 2026-10-16 | decision | stakeholder | Rethink the gates as one proposal covering trial merge, regenerable files, the two verify-base checks, bound markers, and a parser. | Bug-hunt fix run handoff, item 23b                           |
| DEC-02 | 2026-10-27 | decision | stakeholder | The Pi worktree path (D-14) is out of scope; BUG-0102 fixed it in 1.3.3.                                                            | Brief-storage run                                            |
| DEC-03 | 2026-10-27 | decision | stakeholder | `push` stays denied for agents on every CLI; the stakeholder pushes.                                                                | Guard behaviour on 2026-10-27                                |
| DEC-04 | 2026-10-27 | decision | stakeholder | Defer the `merge-story` file limit, the SVG timestamps, and stale installed hooks: none is a git gate.                              | Brownfield handoff, section "Evidence for the gate proposal" |
| DEC-05 | 2026-10-27 | decision | stakeholder | The Pi extension calls the Python `git-guard` per Bash call, so every CLI uses one rule table.                                      | Open question on the parser language for Pi                  |
| DEC-06 | 2026-10-27 | decision | stakeholder | A second level of nested shell that holds git is denied as too deep to check.                                                       | Open question on nested shells                               |
| DEC-07 | 2026-10-27 | decision | stakeholder | A commit does not check freshness; dispatch start and `merge-story` do.                                                             | Grilling, point 1                                            |

## Review findings

| ID  | Pass | Severity | Check | Status | Finding | Resolution |
| --- | ---- | -------- | ----- | ------ | ------- | ---------- |

## Review passes

| Pass | Date | Reviewed commit | Disposition | Failed checks | Summary |
| ---- | ---- | --------------- | ----------- | ------------- | ------- |
