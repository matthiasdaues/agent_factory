---
type: plan
title: Fix run for the bug hunt of 2026-10-15
date: 2026-10-15
status: draft
---

# Fix run for the bug hunt of 2026-10-15

This plan fixes 33 findings of the
[bug-hunt report](bug-hunt-2026-10-15.md) in parallel. The findings are
filed as BUG-0049 to BUG-0081. The implementation agent runs the fix in
automated mode: each cluster becomes one backlog story, and one developer
agent works on each story. No two clusters change the same file, so the
stories cannot conflict. The rest of the report stays serial or waits for a
decision; see [Not in this run](#not-in-this-run).

Three dispatch defects would hit this run: BUG-0082 (D-4), BUG-0083 (D-5),
and BUG-0084 (D-6). The main session fixes them first.

## Branches

- **Integration branch:** `feature/bug-hunt-fixes`, cut from `dev`. It is
  the dispatch's feature branch.
- **Story branches:** `dispatch` creates one branch and worktree per story.
- A story merges into the integration branch only after its review passes.
  The integration branch merges into `dev` once, at the end.

## Clusters

| #   | Cluster               | Findings                                                                               | Files                                                                                                                    |
| --- | --------------------- | -------------------------------------------------------------------------------------- | ------------------------------------------------------------------------------------------------------------------------ |
| 1   | `conjecture-mermaid`  | BUG-0049 (L-2), BUG-0050 (L-14), BUG-0051 (L-9)                                        | `conjecture-lint`, `mermaid-lint`                                                                                        |
| 2   | `structure-gates`     | BUG-0052 (L-3), BUG-0053 (L-4), BUG-0054 (L-10)                                        | `statemachine-lint`, `backlog-lint`, `concern-lint`, `arch-lint`, `voice-anchor-lint`                                    |
| 3   | `contract-checks`     | BUG-0055 (L-5), BUG-0056 (L-11)                                                        | `module-graph-check`, `schema-validate`                                                                                  |
| 4   | `index-handoff`       | BUG-0057 (L-6), BUG-0058 (L-12)                                                        | `index-lint`, `handoff-lint`                                                                                             |
| 5   | `validate-links`      | BUG-0059 (L-7), BUG-0060 (R-8), BUG-0061 (L-8)                                         | `skills/validate/SKILL.md`, `link-check`                                                                                 |
| 6   | `context-test-design` | BUG-0062 (L-13), BUG-0063 (U-10)                                                       | `context-lint`, `test-design-verify`                                                                                     |
| 7   | `usage-capture`       | BUG-0064 (U-5), BUG-0065 (U-6), BUG-0066 (U-7), BUG-0067                               | `usage-capture`, `packages/usage/src/usage/accounting.py`, the `records/` line in `init-factory`                         |
| 8   | `usage-tools`         | BUG-0068 (U-3), BUG-0069 (U-11), BUG-0070 (U-12)                                       | `pi-capture-bootstrap.mjs`, `usage-explore`, `housekeeping-about`                                                        |
| 9   | `quality-metrics`     | BUG-0071 (U-8), BUG-0072 (U-9)                                                         | `dependency-check`, `crap-score`                                                                                         |
| 10  | `build-release`       | BUG-0073 (I-1)                                                                         | `build-release`                                                                                                          |
| 11  | `remove-factory`      | BUG-0074 (I-2), BUG-0075 (I-5), BUG-0076 (U-4), the `remove-factory` items of BUG-0079 | `remove-factory`                                                                                                         |
| 12  | `bootstrap-installer` | BUG-0077 (I-3), BUG-0078 (I-4)                                                         | `install-agent-factory`                                                                                                  |
| 13  | `small-scripts`       | the other items of BUG-0079, BUG-0080 (G-8), BUG-0081 (G-11)                           | `init-factory` (Codex hooks save), `update-factory` (receipt), `migrate-layout`, `commit-safe`, `merge-precommit-config` |

All scripts sit in `packages/factory/scripts/` unless the table names a
different folder. Cluster 7 and cluster 13 both touch `init-factory`, but
in different functions; cluster 13 merges after cluster 7 and resolves any
overlap.

The stories are ST-0295 to ST-0308, in the order of the table, with story
14 as ST-0308. `dispatch plan` puts them into three waves:

- **Wave 1:** ST-0295 to ST-0306. No two of them share a file.
- **Wave 2:** ST-0307, after ST-0301, because both change `init-factory`.
- **Wave 3:** ST-0308.

Each wave starts when every story of the wave before has merged into the
integration branch. Wave 1 holds twelve stories, so the implementation
agent starts at most six developer agents at a time within it.

## Story 14: YAML files begin with `---`

The stakeholder decided on 2026-10-15 that every YAML file begins with the
document marker `---`. In this repository `yamllint` already enforces it.
The gap lies in what the factory writes into other projects: `init-factory`
writes `docs/testing.yaml` without the marker, and the format example in
`skills/detect-test-regime/SKILL.md` lacks it, so agents copy the gap.

The story does three things:

1. It states the rule in the conventions: every YAML file the factory
   creates, and every YAML example it gives agents, begins with `---`.
2. It adds a test that runs every factory writer that produces YAML and
   extracts every YAML example from skills and templates. The first line
   that is not a comment must be `---`.
3. It fixes each gap the test finds. A file that belongs to the developer,
   such as an existing `.pre-commit-config.yaml`, stays untouched.

The story may touch writers that other clusters change, so it runs alone in
wave 3. The factory does not yet enforce the marker inside consumer
projects, and the two legacy fixtures under `tests/fixtures/concern-lint/`
keep their old form.

## Stories

Each cluster becomes one story file `backlog/ST-NNNN.md`. Its `touches:`
lists the cluster's files, and its body lists the findings with links. The
story for cluster 13 declares `deps:` on the story for cluster 7. Every
story names the steps below as its acceptance criteria.

Every story sets `quality-gates: []`. Without that entry the factory
default applies, and it runs `crap-score` and `dependency-check`, which
this run fixes (BUG-0071, BUG-0072).

## The work of one developer agent

1. Work in the worktree that `dispatch` prepared.
2. For each finding: write a regression test that fails on the old code,
   then fix the code. Put new tests in a new file per cluster, named
   `tests/factory/test_<cluster>.py`, unless a test file for that script
   already exists.
3. Run the full suite with `pre-commit run run-tests --all-files`. Bare
   `pytest` is blocked by a hook.
4. Commit once per finding, as `fix: <what changed> (BUG-NNNN)`.
5. Change no file outside the cluster's row, except tests and the
   documentation of the changed script. Never edit `.agent-factory/`.
6. Report each fix in one or two sentences, the test that proves it, and
   any finding that turned out wrong or needs a decision.

A fresh code-review agent then reviews the story's diff. Defects go back
to a developer agent, and the review repeats until it passes. Then
`dispatch merge-story` merges the story into the integration branch.

Automated mode has no code-review step of its own; only manual mode reviews
each story. The brief to the implementation agent adds the review for this
run. Whether automated mode should always review each story is an open
question for the factory.

## Work in the main session

These stay serial, because their findings share files:

- **Dispatch, before the run:** BUG-0082 to BUG-0084 (D-4 to D-6) in
  `dispatch` and `dispatch_lib.py`.
- **Dispatch, after the run:** D-7 to D-12 in `dispatch`, `dispatch_lib.py`,
  `resolve-model`, `trigger`, and `session-reconcile`. They hit only a
  misused command, so the run can go ahead without them.
- **Instructions:** R-3, R-4, R-6, R-7, R-9, and R-10 meet in `rules.md`.
  One pass fixes them together.

## Not in this run

These need a decision or a proposal first:

- **Guardrail rewrite (G-2 to G-7, D-14).** The pattern matching in
  `block-dangerous-git.sh` and its Pi twin becomes a command parser. This
  needs its own proposal.
- **R-5, step manifests.** It waits on the open questions of the
  [step-guard proposal](../proposals/step-guard-enforcement.md).
- **BUG-0086, chain predecessors in the ledger.** `prepare-story` reads
  the ledger's `deps` as the serial-chain predecessor. This run has no
  chains, because no two stories share a file.
- **D-13, duplicate story IDs across sessions.** Allocation needs a design:
  a lock, or a namespace per session.
- **Offline token counting.** `usage-capture` downloads its encoding on
  first use. Whether the installer should seed the cache is a question,
  not a defect.

## Finish

1. The full suite runs on the integration branch.
2. `premerge-check dev feature/bug-hunt-fixes`, with `--max-files` raised
   to the branch's real size, then one merge into `dev`.
3. The full suite runs on `dev`.
4. Each finding gets its resolution with the full SHAs of its commits and
   of the merge.

## Cost

Thirteen developer agents and at least thirteen review agents, plus a
second review for every cluster whose first review finds defects. Earlier
batches in this session needed a second review about half the time.
