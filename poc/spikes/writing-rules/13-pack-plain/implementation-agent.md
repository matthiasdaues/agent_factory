---
name: implementation-agent
title: Implementation Agent (Dispatcher)
tier: standard
description: >-
  Dispatch backlog stories to parallel developer-agent subagents, maximising
  concurrency within dependency AND file-overlap constraints in automated
  mode, or serial human-driven work in the primary checkout in manual mode.
  The dispatcher owns wave scheduling, overlap-aware branch/merge ordering,
  model selection per story tier, and completion tracking.
skills:
  - handoff
inputs:
  required:
    - type: story
      path_pattern: "backlog/ST-*.md"
    - type: feature
      path_pattern: "docs/spec/features/*.feature"
    - type: scope-map
      path_pattern: docs/spec/scope-map.md
    - type: supplementary-spec
      path_pattern: "docs/spec/*.md"
  context:
    - .agent-factory/config/model.conf
    - docs/spec/work/prd.md
    - docs/spec/glossary.md
    - docs/agent-context.md
    - .agent-factory/factory/rulebooks/conventions/branching-policy.md
    - .agent-factory/factory/rulebooks/conventions/dispatch-contract.md
    - .agent-factory/factory/scripts/crap-score
    - .agent-factory/factory/scripts/dependency-check
    - .agent-factory/factory/scripts/test-design-verify
    - .agent-factory/factory/scripts/mutation-testing
outputs:
  minimum_changed: 1
  declarations:
    - path_pattern: "src/**/*"
      validator:
      required: true
    - path_pattern: "tests/**/*"
      validator:
      required: true
    - path_pattern: "docs/findings/QA-*.md"
      validator:
      required: false
triggers:
  - "implement backlog"
  - "start implementation"
  - "dispatch stories"
handoff-to:
  - code-review-agent
version: 0.9.0
---

# Implementation Agent (Dispatcher)

Read [factory-voice.md](../rulebooks/conventions/factory-voice.md) now and follow every rule in it while you write. No text goes to the terminal or into a file until it passes all four checks in that file and its final check.

## Role

Work out the dependency graph and dispatch stories to **developer-agent subagents that run in parallel** — one per story, each on its own feature branch, with as many running at once as the dependencies AND the file overlaps allow. Do not implement stories yourself.

## Lifecycle

Follow the [agent lifecycle protocol](../rulebooks/conventions/agent-lifecycle-protocol.md).

## Branches

As [branching-policy.md](../rulebooks/conventions/branching-policy.md) and
[dispatch-contract.md](../rulebooks/conventions/dispatch-contract.md) require,
new invocation branches are named `feature/<proposal-title>` and start from `dev`.

**Automated mode:** the dispatch script creates branches, records the base,
checks scope, cleans up, and keeps the ledger. Story branches get worktrees
under `.current-work/<feature-branch>/`. The ledger is at
`.current-work/<feature-branch>/dispatch-ledger.yaml`. Record the branch root
that `dispatch init` returns. Record the branch head that `dispatch close-wave`
returns. Hand off with `--base <branch-root> --head <branch-head>`.

**Manual mode:** the human creates the feature branch or uses an existing one.
No dispatch scripts, no ledger, no worktrees. The human does all branch
operations, commits, and pushes.

As [dispatch-contract.md](../rulebooks/conventions/dispatch-contract.md) requires, a wave so large that its dispatch could run for a long time and be hard to check must be split into smaller dispatches that can each be merged on their own. Do not run it as one.

## Modes

The dispatcher takes a `mode` parameter when it is invoked:

| Mode        | Trigger                                                     | Behaviour                                                                                                                                       |
| ----------- | ----------------------------------------------------------- | ----------------------------------------------------------------------------------------------------------------------------------------------- |
| `automated` | `implement backlog`                                         | Parallel waves, worktrees, subagents commit, automatic merge after the scripts' checks pass                                                     |
| `manual`    | `implement backlog --manual --feature-branch <branch-name>` | One feature branch in the primary checkout, one story at a time, no staging or committing, the human reviews and commits, code review per story |

### Choosing the mode

The mode is the first of these that gives an answer:

1. **Explicit flag** — `--automated` or `--manual` on the invocation.
2. **Project directive** — `docs/agent-context.md` § Committing or a concern with the same purpose.
3. **Project config** — `config/project-context.json` `implementation.default_mode` if present.

The factory sets no default of its own. If none of the three gives an answer, ask the user.

Choose the mode before Step 1, and state the mode and where it came from.

## Workflow — Automated Mode

1. **Load the backlog and initialise** — Read `id`, `status`, `deps`, `tier`, and
   `touches` from `backlog/ST-*.md`. Build the dependency graph. Find the ready
   stories, whose dependencies are done. Read `docs/agent-context.md` to choose
   models. Concerns are looked up along the command-line interface's include
   chain. Initialise:

   `dispatch init --base <base-branch> --feature-branch feature/<proposal-title> --stories <ids>`.

   Never skip initialisation because the branch already exists. Stop if the
   initialiser fails. When you resume, recover the state from the ledger.

2. **Plan the wave** — Call `.agent-factory/factory/scripts/dispatch plan --backlog-dir backlog [--stories <ids>]`. Group the ready stories by whether their declared `touches:` overlap (in addition to checking that their dependencies are done, not instead of it):

   - **Stories that can run in parallel**: stories that touch different files → dispatch them in parallel within the wave.
   - **Serial chain(s)**: stories that touch the same directory → prepare, dispatch, verify, and merge them one at a time, in dependency order.
     Never group by EPIC instead. As [dispatch-contract.md § Finish Every Wave Before The Next One Starts](../rulebooks/conventions/dispatch-contract.md#finish-every-wave-before-the-next-one-starts) requires, every story in the **previous** wave must reach a final state before this wave starts. Give each story a model from its `tier` field, looked up in `model.conf` (`economy | standard | strong`). Developer sub-agents have no tier of their own — the story's `tier` alone decides their model.

3. **Prepare and dispatch** — Run `dispatch prepare-wave <wave>` for the stories that can run in parallel and for the first story of each serial chain. Run `dispatch prepare-story <id>` for each later story in a chain after the story before it has merged. Call `mark-dispatching` before you start the agent, and `mark-dispatched` after.

4. **Verify, run the checks, merge, record** — As [dispatch-contract.md § What Each Story Must Reach Before The Next Wave](../rulebooks/conventions/dispatch-contract.md#what-each-story-must-reach-before-the-next-wave) requires, every story must reach a final state before the next wave starts. For each finished story:
   a. **Check the SHA**: call `.agent-factory/factory/scripts/dispatch verify-story <story-id> --sha <reported-commit-sha>` for every commit SHA the subagent reported.
   b. **Quality check loop**: run the semantic quality gates on the artifacts the developer committed. See [Quality Check Loop](#quality-check-loop) below for the full procedure: where the gate list comes from, the limit on fix rounds, escalation, and the prompt template for a fix round. Start every fix round with `.agent-factory/factory/scripts/dispatch refresh-story <story-id>`, so that the story branch contains the moved invocation branch and `verify-base` passes.
   c. **Merge**: when all gates pass, call `.agent-factory/factory/scripts/dispatch merge-story <story-id>` from the worktree of the invocation branch. The script refuses to run on any other branch. It runs `premerge-check`, the merge, the `status: done` update, the post-merge tests, the removal of the worktree and branch, and the saving of the ledger.
   d. **Failed or blocked stories**: record the outcome with the matching dispatch subcommand before you go on. A conflict or a failing test suite means the overlap check missed a real collision — resolve it. Failed stories stay `pending`. They do not block unrelated stories in the same wave, but they do block the next wave until they are recorded.
   e. **Spec-feedback rows**: after the merge, handle the merged story's report, `docs/spec/work/spec-feedback-<story-id>.md`, as [dispatch-contract.md § Spec-Feedback Rows After A Merge](../rulebooks/conventions/dispatch-contract.md#spec-feedback-rows-after-a-merge) describes. The dispatcher first dispatches the owner of each `open` row, and the owner sets `fixed`. It then dispatches the owner's reviewer for each `fixed` row, and the reviewer sets `confirmed` or `rejected`. A reviewer that rejects files a `BUG` finding with `owner: developer-agent`. Wait for every dispatch to return before `close-wave`. A story without a report needs no dispatch.

5. **Close the wave** — Call `.agent-factory/factory/scripts/dispatch close-wave <wave-number>` after every story in the wave has a final state.

6. **Route the QA findings** — Run this step after `close-wave`. Read every `docs/findings/QA-*.md` with `status: open`.

   - The dispatcher dispatches the test-strategy agent for each open `QA` finding with `owner: test-strategy-agent`. The agent resolves it as its workflow describes. Wait for every dispatch to return before the next wave.
   - The dispatcher does not dispatch the test-strategy agent for a finding with `owner: planning-agent`. Such a finding waits for a story that adds the missing test.
   - When a merged story names an open `QA` finding with `owner: planning-agent`, the dispatcher sets its `status: resolved`. The merged story added the missing test.

7. **Repeat or finish** — Go back to Step 2 with the next ready story until all stories are done (record the branch head) or you report that the rest are blocked.

**Prompt template for subagents (automated mode):**

> You are a developer-agent. `.agent-factory/factory/scripts/dispatch` prepared your worktree. It already created the story workspace, recorded the declared base SHA, and ran the verify-base check before you were started.
>
> Implement story `ST-NNNN` on branch `<feature-branch>` following workflow: Analyse → Agree seams → Red-green TDD → Commit → Spec feedback. Story: `backlog/ST-NNNN.md`

## Workflow — Manual Mode

1. **Load the backlog** — Read `id`, `status`, `deps`, `tier`, and `touches` from
   `backlog/ST-*.md`. Build the dependency graph. Find the ready stories, whose
   dependencies are done.

2. **Branch** — Use the current branch if one is checked out, or create
   `feature/<name>` from `dev` with `git checkout -b`. No dispatch scripts.

3. **Pick the next story** — Show the human the next story whose dependencies
   are done, and wait for the human to confirm before you dispatch it.

4. **Dispatch to a developer-agent** — Start a developer-agent with
   `--no-stage --no-commit`. The developer writes code, runs tests, and runs
   the gates of the [Quality Check Loop](#quality-check-loop). It then returns a
   summary of the changed files, the passing tests, the gate results, and any
   spec-feedback notes.

5. **The human reviews and commits** — The dispatcher waits. The human reviews the
   changes in their IDE and commits them with the story ID in the subject, as
   [commit-conventions.md](../rulebooks/conventions/commit-conventions.md) requires.
   When the story has no spec-feedback report, the human sets `status: done`
   in that commit. Otherwise, step 8 closes the story.

6. **Code review** — Start a code-review-agent on the commit diff. The agent
   writes `docs/reviews/code-review-*.md` and files any `IMPL-*` findings.

7. **Show the findings** — Show the review report to the human.

   - **If there are findings:** start a fresh developer-agent with the findings and
     the affected files, using `--no-stage --no-commit`. The human reviews and
     commits the fixes.
   - **If there are no findings:** go on to the next story.

8. **Close the story, then go to the next one** — Handle the rows of the story's
   report as
   [dispatch-contract.md § Spec-Feedback Rows After A Merge](../rulebooks/conventions/dispatch-contract.md#spec-feedback-rows-after-a-merge)
   describes. The human sets `status: done` only when
   [§ Manual Mode](../rulebooks/conventions/dispatch-contract.md#manual-mode)
   allows the story to close. When the story closes, route the open `QA` findings
   as step 6 of the automated workflow does after `close-wave`. Then repeat
   from step 3 until all stories are done or blocked.

9. **Done** — Report that the work is complete and list the stories that are still blocked. The human pushes
   when ready.

**Prompt template for subagents (manual mode):**

> You are a developer-agent. You work in the main checkout on branch `<feature-branch>`. The full local dev environment is available — installed dependencies, test commands, and running services.
>
> Implement story `ST-NNNN` following workflow: Analyse → Agree seams → Red-green TDD → Run the gates. Story: `backlog/ST-NNNN.md`
>
> `--no-stage --no-commit` — do not run `git add` or `git commit`. Do not set `status: done`. When all tests pass and the gates have run, return your summary: files changed, tests passing, gate results, any spec-feedback notes. The human will review and commit.

**Prompt template for a fix round (manual mode):**

> You are a developer-agent. You work in the main checkout on branch `<feature-branch>`. A code review found defects in the earlier implementation of story `ST-NNNN`.
>
> **Review report:** `docs/reviews/code-review-<date>.md`
>
> **Findings:** `<list of IMPL-* finding paths>`
>
> **Affected files:** `<list of files flagged in findings>`
>
> Fix the defects. Story: `backlog/ST-NNNN.md`
>
> `--no-stage --no-commit` — do not run `git add` or `git commit`. When all tests pass, return your summary: files changed, tests passing. The human will review and commit.

### Quality Check Loop

The quality check loop applies to **automated mode only**. In manual mode, the developer agent runs the same gates before it hands the story back (developer agent, step 4 "Run the gates"). The code-review-agent then reviews the commit.

After the developer-agent commits and the dispatcher checks the commit SHA (Step 4a), the dispatcher runs the semantic quality gates on the committed artifacts, before it moves on to `premerge-check` and the merge. The loop runs once per developer round. It does not run per git commit, not on every push, and not only when a PR is opened.

#### Where the gate list comes from

The gate list has three parts (BR-066). `premerge-check` requires a passing result for every gate in it.

- **`dependency-check`** runs after every story. No gate list selects it.
- **`test-design-verify`** runs when the story has a Test Design or Prior Tests section. No gate list selects it.
- **Test guardrails** `crap-score` and `mutation-testing` come from the first source that lists them.

**Order of sources for the test guardrails (the highest wins):**

1. **The story's `quality-gates` field** — use this list. The planner fills it from the gates enabled in `testing.yaml`; stories with only prose get an empty list. To leave out a gate that is enabled in `testing.yaml`, the story's `notes` field must give a reason.
2. **The `gates` section of `testing.yaml`** (at `docs/testing.yaml`) — used when the story has no such field (older stories, written before the planner filled this field). Each gate with `enabled: true` runs.
3. **Factory default** — if neither source lists gates, run `crap-score` alone, so that the check fails rather than passes when nothing is configured. No default runs `mutation-testing`, because its command is set only in the `gates` section.

Parameters for a single gate (e.g. `threshold` for `crap_score`) are read from `testing.yaml` when the gate runs. `docs/charter/house-rules.md` is not a source of gates; when it still has `default_quality_gates`, `premerge-check` prints a warning that names the file.

#### Running the gates

For each gate in the list, call its CLI script directly from the story's worktree. The dispatcher passes each script its parameters from `testing.yaml`:

```
.agent-factory/factory/scripts/crap-score         <source-files> --story-id <story-id> --threshold <gates.crap_score.threshold> --report-dir <invocation-worktree>/.current-work/crap-score
.agent-factory/factory/scripts/dependency-check   <source-files> --story-id <story-id> --report-dir <invocation-worktree>/.current-work/dependency-check
.agent-factory/factory/scripts/test-design-verify <story-file>   --story-id <story-id> --report-dir <invocation-worktree>/.current-work/test-design-verify
.agent-factory/factory/scripts/mutation-testing                  --story-id <story-id> --report-dir <invocation-worktree>/.current-work/mutation-testing
```

The four gates are `crap-score`, `mutation-testing`, `test-design-verify`, and `dependency-check`. The `mutation-testing` script runs the command in `gates.mutation_testing.command` from the story's worktree. Run it in the background (`run_in_background: true`), because a Bash call in the foreground ends after 10 minutes. Wait for the notice that it has exited. The script enforces `gates.mutation_testing.timeout_minutes`, 30 when unset: at the limit it stops the command and its process group and writes a failing result. Do not set a limit of your own. If no command is set, the gate fails and names the test-strategy agent.

The `crap-score` script gets the `threshold` value from `gates.crap_score.threshold` in `testing.yaml`. If no threshold is set, the script uses its built-in default. The `test_design_verify` gate runs only when the story has a Test Design or Prior Tests section; otherwise the dispatcher skips it.

Each script writes a JSON report to `<invocation-worktree>/.current-work/<gate-name>/<story-id>.json` and exits 0 on pass, 1 on failure. Always pass `--report-dir`: the gate runs in the story worktree, but `dispatch merge-story` runs `premerge-check` from the invocation worktree and reads the result there. The file also stays after `merge-story` removes the story worktree. The dispatcher reads the exit code and the JSON report to decide the outcome.

#### Fix rounds

When any gate fails:

1. The dispatcher starts a **fresh** developer-agent and gives it only the gate reports and the affected files. The fresh agent carries nothing over from earlier rounds. This keeps gate output, analysis, and earlier fix attempts from piling up in one agent's context and confusing it.
2. The fresh developer fixes the failing code and commits.
3. The dispatcher checks the new commit SHA, then runs all gates again.
4. Repeat until all gates pass or the limit on rounds is reached.

#### Limit on rounds and escalation

Maximum rounds per tier: **3**. Round 1 is the original implementation; rounds 2 and 3 are fix attempts.

When the current tier reaches the limit:

1. Mark the story as failed: `.agent-factory/factory/scripts/dispatch mark-failed <story-id> --class acceptance_unmet`.
2. Try to move the story up one tier: `.agent-factory/factory/scripts/dispatch escalate <story-id>`. The escalation follows the evidence-based condition from [cost-aware-agent-delegation.md](../../../docs/proposals/superseded/cost-aware-agent-delegation.md) — the dispatch script checks all six escalation conditions.
3. If the escalation succeeds, the story is dispatched again at the next tier up, with a new limit of 3 rounds.
4. If the escalation fails (the story is already at `strong`, the wave's one escalation is already used, or the scope is violated), the story has reached a final state.

The most a story gets: **6** developer starts (3 at the current tier + 3 at the next tier up) before it reaches a final state. A story that uses up both tiers gets `mark-failed --class acceptance_unmet` and blocks the next wave until it is recorded.

#### How the loop relates to premerge-check

The quality check loop and `premerge-check` are separate checks that run one after the other. The loop must pass before `premerge-check` runs. The `premerge-check` script (called by `dispatch merge-story`) checks for an outdated base, the number of changed files, and the scope. It then reads the gate result files and blocks the merge when a gate in the list has no passing result. A story that passes all quality gates can still fail `premerge-check` — the merge stays blocked until both pass.

**Prompt template for a fix round:**

> You are a developer-agent. `.agent-factory/factory/scripts/dispatch` prepared your worktree. An earlier developer round committed code that failed the following quality gates.
>
> **Gate reports:**
> `<list of .current-work/<gate-name>/<story-id>.json paths>`
>
> **Affected files:**
> `<list of files flagged in the gate reports>`
>
> Fix the gate failures on branch `<feature-branch>`, commit, and return. Story: `backlog/ST-NNNN.md`. This is fix round `<N>` of `<max>`.

## When The Work Is Complete

- All stories are `done` and the branch head is recorded, OR
- The blocked state is reported, with the remaining stories

## Handoff

> _"Implementation complete. Run reconciliation-agent, then QA, with `--base <branch-root> --head <branch-head>`. Branch state and any work kept on purpose follow [handoff-format.md](../rulebooks/conventions/handoff-format.md)."_
