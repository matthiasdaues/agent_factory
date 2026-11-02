# Handoff: bug-hunt fix run, closed 2026-10-16

The run is done. All fourteen stories, ST-0295 to ST-0308, merged into
`dev` as `3921e522cc31f7fd454d9c908c9e8e42ceb201fe`; the full suite passed
there with 2017 tests. Commit `d0a67097` resolves 31 findings with their fix
commits. BUG-0076 and BUG-0079 are partly fixed and stay open; BUG-0065 and
BUG-0067 stay open as design decisions.

## What is left in place

- `.current-work/feature/bug-hunt-fixes/` keeps the ledger, the briefs, and
  the review probes the follow-ups below refer to. It is ignored by git.
  Close or move the ledger before the next `dispatch init`, which otherwise
  reports an active run.
- Worktrees, story branches and the integration branch are removed.

## Next work

1. **Gate proposal** (item 23b): write it with the `draft-proposal` skill.
2. **Brownfield onboarding run** (item 24): BUG-0092 to BUG-0096; for
   BUG-0093 reorder the brownfield playbook so the scope map comes before
   the DSL, if possible.
3. **Brief storage rule** (item 18).
4. The other follow-ups below, filed as findings.

## Exceptions granted in this run

- ST-0296 got a fourth iteration for one regression (M-1).
- ST-0303 was reopened by a hand edit of the ledger, past the
  one-escalation-per-wave guard.
- ST-0308 was reopened by a hand edit after a refresh conflict in the
  generated `INDEX.yaml` alone.
- The stakeholder ran three back-merges of `dev` into the integration
  branch and one manual story refresh by hand, outside the guard.

## Rules learned in this run

- Never merge while a fix agent is running: every merge moves the tip, and
  the agent's `verify-base` fails. Refresh a story only when its worktree
  is clean; set staged work aside with a tagged stash and apply it by SHA.
- Brief agents to run `verify-base` on its own, from their own worktree,
  before each commit, never in the same batch as the commit.
- Set `mark-dispatched` after every `mark-dispatching`.
- Three developer iterations per story per tier; one tier escalation per
  wave. `re-dispatch` refuses a blocked story without escalation.
- The classifier protects hook configurations; a story scope that names
  them needs the stakeholder's own edit.
- Keep `dev` still during the final merge: each new commit there makes the
  integration branch stale again and needs another back-merge.
- Keep briefs and probes under `.current-work/<branch>/`, not in `/tmp`.

## Follow-ups to file as findings

01. `merge-story` gives no warning when a merge breaks running fix agents.
02. Guardrail: a commit in the same batch as a failing `verify-base` got
    through (ST-0303, `46b7e86a`).
03. Guardrail: `verify-base` in the wrong worktree satisfied the commit guard
    (ST-0306) and left a marker in the invocation worktree.
04. `mark-dispatched` forgotten for ST-0304; `merge-story` caught it.
05. `premerge-check` semantic gates read `data.get("passed")`, which fails on
    list-shaped gate reports such as crap-score's.
06. `init-factory:213` writes `@../../.agent-factory/...` into
    `.claude/CLAUDE.md`, which resolves outside the project.
07. BUG-0065 (stable capture ID per run) and BUG-0067 (`records/` folder vs
    spec): design decisions.
08. `remove-factory`: `.committing.json` expiry; restoring `active`;
    byte-for-byte `settings.json` restore; pre-existing `.claude/`,
    `.github/`, `.pi/` deleted on removal; `os.link` fails on filesystems
    without hard links; without `fcntl` a stale owner file blocks until
    deleted by hand.
09. Pi bootstrap: a second bootstrap with the same paths and a wrong launcher
    can delete a running capture's files.
10. `index-lint`: a skill without `name` only warns, unseen.
11. `module-graph-check` (medium, needs a decision): rows under a `###`
    heading count toward the previous `##` contract, so this repository's
    `interface-contracts.md` loses `intent select`, `intent assess` and
    `usage-query`. Low: fenced `` ## `path`  `` read as a contract; indented
    rows unmatched.
12. `conjecture-lint:54`: the leading-negation regex still ends in `\b`.
13. `link-check`: a heading with U+E000/U+E001 crashes `slugify`; padded code
    spans keep their spaces.
14. `build-release`: a rename failing after an earlier one leaves mixed
    output.
15. `install-agent-factory`: no test pins "a real file wins over a link".
16. `dependency-check` skill: usage example points to `factory/fixtures/...`.
17. `refresh-story`: a deleted worktree shows as a detached HEAD.
18. Brief storage rule (stakeholder approved 2026-10-16): the scratchpad in
    `/tmp` was emptied overnight and the briefs were lost. Change
    `dispatch-contract.md` § Brief File so every CLI writes briefs to
    `.current-work/<branch>/briefs/<task>.md` in the main checkout (absolute
    path in the prompt) and agents' scratch files to
    `.current-work/<branch>/scratch/<agent-or-story>/`. Add a test that pins
    the path. A hook that enforces it is a separate story. This run already
    follows the rule: briefs in `.current-work/feature/bug-hunt-fixes/briefs/`.
19. `arch-lint` chapter-5 tables (low): a table without outer pipes is not
    recognised; a body row made only of dashes turns the row above into a
    header. L-3: `dsl_core_components()` (arch-lint ~line 152) misses
    components declared without a name (`component "API"`), so such a model
    with an empty chapter 5 passes; allow `(?:=\s*)?\bcomponent\s+"..."`.
    ST-0296 got one approved exception beyond its iteration cap, for
    the container-only regression (M-1) alone.
20. Todo file name: the factory's name is `todo.md` (`rules.md` MUST,
    conventions, templates). `todos.md` remains in `INDEX.yaml`,
    `coaching-agent`, `spec-review-agent`, `requirements-agent`,
    `brownfield-onboarding`, `architecture-review`, `test_spec_lint.py`,
    `docs/spec/work/prd.md`, `validation-rules.md`; this repository has both
    `docs/spec/work/todo.md` and `docs/spec/work/todos.md`. Clean up after the run.
21. `merge-precommit-config` (low): after BUG-0081 a plain merge is a no-op
    once any factory id exists; only `--update` adds missing hooks, and
    VIRGIL's fitting never passes it. `init-factory` re-run (e.g. adding
    Codex) resets `version` to 1 and drops `resolved_source` and
    `archive_sha256`; carry them over in `load_prior_manifest`.
    `install-agent-factory` prints an unquoted uninstall path and `cd`
    (lines ~852, ~1101).
22. Guardrail false positive: `block-dangerous-git.sh` blocks any Bash
    command whose text contains `git commit` or `core.hooksPath`, even in a
    heredoc, a grep pattern, or a `cat` of a file. Agents fall back to
    scratch-file scripts to edit `commit-safe` or its tests.
23. Ledger override (stakeholder approved 2026-10-16): ST-0303 was set by
    hand from `blocked` to `dispatched` for one more fix iteration, past the
    one-escalation-per-wave guard. Backup of the ledger before the edit:
    `.current-work/feature/bug-hunt-fixes/scratch/dispatch-ledger.before-st0303-edit.yaml`.
    This replaces the earlier plan (b') to finish ST-0303 after the run.
    Also an exception: ST-0296 got a fourth iteration for M-1 alone.
    23a. `crap-score` `load_coverage` fallback (medium, accepted at merge): when
    a coverage key names a file under no base (e.g. deleted after the run),
    the old per-key order runs and a same-named file can take the wrong
    coverage silently. Fix: choose the base under which most keys exist,
    skip keys with no file, warn on stderr. Probe:
    `.current-work/feature/bug-hunt-fixes/scratch/review-ST-0303/probe.py`.
    23b. Gate rethink (stakeholder approved 2026-10-16): write a proposal with
    the `draft-proposal` skill right after this run. It folds in G-2 to G-7
    and D-14 and covers: (1) `premerge-check` by trial merge
    (`git merge-tree`) instead of ancestry, in every direction; (2) a list of
    regenerable files (`INDEX.yaml` via `index-lint`) whose conflicts are
    resolved by regeneration in refresh and merge; (3) `verify-base` checks
    freshness only at dispatch, before commits only descent from the
    recorded base and the right worktree; (4) markers bound to worktree path
    and HEAD, checked for the committing worktree, and `commit-safe` runs
    the same check; (5) the guard parses git commands instead of matching
    text. Evidence from this run: the back-merge and the ST-0308 refresh
    needed the stakeholder's `!`; a manual refresh cannot be committed inside
    the guard; ST-0308 was blocked by a conflict in `INDEX.yaml` alone and
    reopened by hand. In the brownfield run an agent ran
    `uv run pytest <file>`; the hook blocks bare `pytest` but not this form.
    (ledger backup
    `.current-work/feature/bug-hunt-fixes/scratch/dispatch-ledger.before-st0308-edit.yaml`).
    23c. `tests/factory/test_yaml_document_start.py` (low): the
    `<!-- yaml-excerpt -->` exemption has no upper bound; one comment line
    exempts any block. Compare the set of marked blocks against a fixed
    allow-list keyed by path and first key (`concerns`, `waves`).
24. Brownfield onboarding run after this one (BUG-0092 to BUG-0096).
    Stakeholder decision for BUG-0093: reorder the brownfield playbook so the
    scope map comes before the DSL, if possible.
25. Also open: BUG-0086, BUG-0088, BUG-0092 to BUG-0097, D-7 to D-13, the
    instructions pass (R-3, R-4, R-6, R-7, R-9, R-10), the guardrail
    proposal (G-2 to G-7, D-14), R-5, tiktoken.
