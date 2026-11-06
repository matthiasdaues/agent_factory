---
schema_version: 2
title: Seed the ID counter in the fitting, and name each requestor's prefix
status: accepted
owner: matthiasdaues
created: 2026-11-06
updated: 2026-11-06
supersedes:

impact:
  scope: cross_component
  architecture_change: false
  external_contract_change: true
  boundaries:
    - packages/factory/agents/virgil.md
    - packages/factory/scripts/init-factory
    - packages/factory/scripts/next-id
    - packages/factory/config/AGENTS.claude.md
    - packages/factory/config/AGENTS.codex.md
    - packages/factory/config/AGENTS.copilot.md
    - packages/factory/config/AGENTS.pi.md
    - packages/factory/rulebooks/conventions/finding-format.md
    - packages/factory/rulebooks/conventions/id-prefixes.md
    - docs/spec/interface-contracts.md

governance:
  assurance: elevated
  risk_domains:
    - data_integrity
    - operations

estimate:
  as_of: 2026-11-06
  basis: judgment
  confidence: low
  human_review_hours:
    min: 1.5
    max: 3.0
  normalized_tokens:
    min: 25000
    max: 50000
  estimated_consumption:
    min: 375000
    max: 750000
    overhead_multiplier: 15
    playbook: feature-addition
---

# Feature Request: Seed the ID counter in the fitting, and name each requestor's prefix

## Primer

The Factory is a set of agents, skills, and rules that help people build software in a git repository. Before it can work in a project, a guided setup called the fitting walks the human through a few choices, such as the hooks that run at commit. VIRGIL, the Factory's session agent, leads that walk.

The Factory writes many small documents that refer to each other: stories, bug reports, review findings, architecture decisions, and todo entries. Each is an indexed artifact. Its name is a prefix plus a number. The prefix names the kind, so ST-0375 is a story and ADR-0032 is an architecture decision record. Each prefix has its own sequence of numbers.

Two sessions on different branches used to pick the same next number, because each saw only its own files. The earlier proposal, counter-ids, fixed this with an ID counter, which is a git ref on the project's shared remote, called origin. A script named next-id claims a number there, and the remote refuses a second claim of the same number.

The counter leaves two gaps. First, until someone creates it, every claim fails. The human seeded it by hand in this project with one start of 400 for every prefix, so stories and bugs jumped to 0401.

So the fitting gets a new step that seeds the counter and sets a sixth fitting key. A read-only mode of next-id finds the highest number of each prefix on the local and remote-tracking branches. It reads only file names, register id fields, and todo headings, never body text, and prints one seed command with a start per prefix. VIRGIL shows the command and runs it after the human confirms.

A project without origin keeps the counter in its own .git, which all its worktrees share. A git setting named agent-factory.counterRemote tells next-id where to find it. Once origin exists, VIRGIL offers to move the counter there. The move is refused if origin already has a counter, so a collision shows.

The second gap is the prefix. Today a reviewer picks its prefix from a table, and a wrong pick does not fail. A fagan finding claimed under the bug prefix takes a valid bug number, and that number is gone. So every file that tells an agent to create an artifact names the claim with its literal prefix. One convention file, id-prefixes.md, holds a table of all twelve prefixes, and a text test checks that each requestor names its own.

## Summary

The fitting gets a new step that seeds the ID counter of
[counter-ids](counter-ids.md) on the project's `origin`. A new mode of
`next-id` reads the highest ID of each prefix from the project's branches and
prints the seed command with one pair per prefix. Each sequence then continues
without a jump. VIRGIL shows that command and runs it once the human confirms.
Every file that tells an agent to create an indexed artifact also names the one
prefix that artifact takes, so no agent claims an ID with a wrong prefix.

## Motivation

`next-id` hands out every ID from `refs/ids/counters` on `origin`. Until that
ref exists, every claim fails with "counter missing", and every producer stops.
Today the counter comes into being only when a human runs `next-id --seed` by
hand. `init-factory` prints a hint (ST-0375), but nothing in the fitting asks
for the seed, and nothing finds the highest IDs in use. In this project the
human seeded with `--seed 400 ADR=32`, so `ST`, `BUG`, and every other prefix
jumped to 0401. Only `ADR` continued its sequence.

The second gap lies in the producers. `finding-format.md` tells a reviewer to
claim "`next-id <TAG>`" and lists the tags in a table. Fourteen agents and
skills file findings, and none of them names its own tag or `next-id`. The table
also lacks `RECON`, although the reconciliation agent files `RECON` findings.
The list of `next-id` prefixes in that file lacks `ST`, `T`, and `ADR`. An agent that has to
work out its prefix from a table can pick the wrong one. A wrong prefix does not
fail: `next-id BUG` hands out a valid `BUG` number for a finding that should
have been `FAGAN`, and that number is gone.

## Core Principles

- The counter exists before the first claim. Seeding is part of setting up a
  project, like the model matrix or the hooks.
- A sequence continues where the project left it. The seed takes the highest
  number in use per prefix, not one number for all.
- A script finds the highest numbers, not an agent. Counting files by reading
  them is the scan that counter-ids removed.
- A requestor names its prefix literally. No file asks an agent to choose a
  prefix from a list.

## Design

### The fitting step

The fitting in `virgil.md` § Fitting gets a new step 4, "Seed the ID counter",
after step 3, "Decide on hooks". The step runs after the hooks because a seed
is a push, and the human should decide on the hooks before the first push the
Factory makes. It flips a sixth key, `fitting.counter_seeded`, in
`.agent-factory/config/project-context.json`. `fitting.status` becomes
`"fitted"` only when all six keys are `true`.

In the step, VIRGIL:

1. checks for `origin`. Without it, VIRGIL first sets
   `agent-factory.counterRemote` to the absolute path of the project's main
   repository, the parent of `git rev-parse --git-common-dir`, so the seed
   goes to the local counter below;
2. runs `next-id --plan-seed`, which prints the seed command, or a message why
   no seed is needed or possible;
3. shows the command to the human and says what it does: it creates
   `refs/ids/counters` on the counter's remote once, and every later ID
   continues from it;
4. runs the command when the human confirms, and sets the key. ADR-0032
   already lets an agent push the claim ref through `next-id` (DEC-03);
5. stops the step without setting the key when the human declines, or when
   `origin` is unreachable. VIRGIL names the reason, and the session start
   lists the step as open until it is done.

When `refs/ids/counters` already exists on `origin`, the step sets the key and
reports that the counter is in use, without a seed.

Greenfield projects (`fitting.status == "greenfield"`) walk step 0 and this
step, so a newcomer's first backlog never fails at a missing counter (DEC-06).
A greenfield project has no indexed artifacts, so `--plan-seed` prints
`next-id --seed 0`, and the first story is `ST-0001`.

### `next-id --plan-seed`

`next-id --plan-seed [--remote <url>]` is a read-only mode of `next-id`, so
the prefix list, the remote checks, and the redaction exist once (DEC-07). The
mode changes nothing. It:

1. checks the remote as a claim does. When `refs/ids/counters` exists, it
   prints "the counter is in use on <remote>" and exits `0`. When the remote is
   missing or unreachable, it fails with the same messages as a claim;

2. collects the IDs in use on every local branch and every remote-tracking
   branch, from the artifacts themselves and never from body text, because
   text holds examples such as `ST-9999`:

   - file names: `backlog/ST-NNNN.md`, `docs/findings/<PREFIX>-NNNN.md`, and
     `docs/adr/NNNN-*.md` for `ADR`;
   - the `id` field of each line in `docs/findings/register/*.jsonl`;
   - the headings `## T-NNNN` in `docs/spec/work/todo.md`;

   A file name counts when it starts with a prefix of the list, a hyphen, and
   digits. `ST-0375A.md`, a split story, counts as 375. Older names such as
   `SPEC-001-title.md` or `ATAM-0001-title.md` count by their number. A name
   without a number, such as `BUG-HUNT.md`, does not count. The mode prints each
   counted name that breaks `<PREFIX>-NNNN.md` or `<PREFIX>-NNNN<letter>.md` as
   a warning and goes on, so an old name never blocks the seed and never lowers
   it unnoticed. A new file carries the prefix and the number only, never a
   title (DEC-12);

3. prints one command:
   `next-id --seed <start> <PREFIX>=<highest> …`, with one pair for each
   prefix that has an ID in use. `<start>` is `0`, so a prefix without IDs
   starts at `0001`, and every sequence begins at one (DEC-04).

Each pair holds the highest number, not the count, so a gap in a sequence does
not lower the seed. A prefix with IDs only in a register line, such as a
`minor` finding, counts like one with a file.

`next-id` prints the remote redacted, as BR-077 requires for every line it
writes.

### The local counter without `origin`

Without `origin`, the project's own repository holds the counter: the ref
`refs/ids/counters` in its `.git`. All worktrees share that `.git`, and a local
clone has the project as its `origin`, so all of them claim from one counter
(DEC-05). This replaces the rule of counter-ids that `next-id` fails without a
remote (counter-ids DEC-20).

`next-id` finds the local counter through the git setting
`agent-factory.counterRemote`, which holds the path of the project's
repository. The fitting step sets it when the project has no `origin`.
`next-id --move-to-origin` removes it once the counter is on `origin`.
`.git/config` is shared by all worktrees, so all of them see it. `next-id` resolves its remote in this
order: `--remote`, then `agent-factory.counterRemote`, then `origin`. A clone
that lost its `origin` by mistake has no such setting, so its claim still fails
and names `origin` and `--remote` (DEC-08).

### Moving a local counter to `origin`

Once a remote exists, the counter moves there and every sequence continues. At
the session start, VIRGIL checks whether `agent-factory.counterRemote` is set
and `origin` exists. When both hold, it offers the move and runs
`next-id --move-to-origin` after the human confirms (DEC-09). That mode:

1. reads the claim commit `C` of the local counter;
2. replaces the local `refs/ids/counters` with a marker commit whose message
   holds one line, `moved=<remote>`, with the remote redacted. The update uses
   a lease on `C`. A claim that raised the counter meanwhile makes the move
   start again at step 1, and no claim lands on the local counter after this
   step;
3. pushes `C` to `refs/ids/counters` on `origin` with the create-only lease
   `--force-with-lease=refs/ids/counters:`;
4. removes `agent-factory.counterRemote` when the push succeeds. When the push
   fails, it puts `C` back on the local `refs/ids/counters`, with a lease on
   the marker, and names the cause.

A claim or a `--plan-seed` that reads the marker fails and names the remote
that holds the counter now, and it never advises a seed. A local clone whose
`origin` is the project's path learns from this where to point its `origin`,
and the fitting step offers it no second seed that would split the counter.

A claim that runs during the move either lands before step 2, and the move
carries its number to `origin`, or it reads the marker and fails. No number
goes out twice.

When `origin` already holds a counter, the push is refused. `next-id` then
names both counters and changes nothing, and VIRGIL reports the collision, so
a counter that someone else seeded never goes unnoticed (DEC-05). The move
is a push of the claim ref through `next-id`, so it is allowed; a plain
`git push` by an agent stays blocked.

### Fitting keys and orientation files

`init-factory` derives the fitting keys from the project's state on every run.
It derives `counter_seeded` from the counter's remote, resolved in the order
`next-id` uses: `agent-factory.counterRemote`, then `origin`. The key is `true`
when that remote holds `refs/ids/counters`, checked with `git ls-remote`, and
`false` when it does not or when neither remote exists. So a local counter and
a greenfield project follow the same rule, and the key never flips between
the two remotes. An unreachable remote leaves the key as it is, so a run
without network never resets a seeded project.

The orientation files `AGENTS.claude.md`, `AGENTS.codex.md`,
`AGENTS.copilot.md`, and `AGENTS.pi.md` list the fitting keys in a table and
count the steps. Each gets the row for the sixth key and the count "six".

### Each requestor names its prefix

Every file that tells an agent to create an indexed artifact names the claim
with its literal prefix, at the step that creates the artifact, for example
"Claim the ID with `.agent-factory/factory/scripts/next-id FAGAN`". The kind of
artifact decides the prefix, not the file, so a file that creates two kinds
names one prefix at each of the two steps (DEC-10).

Every file that tells an agent to add an entry to
`docs/spec/work/todo.md`, such as a review that records an open question, is a
requestor of `T`: at that step it names `next-id T` and points to
`todo-format.md` for the form of the entry. The text test finds these files by
that pointer, so a file that only links to `todo.md` is no requestor. A requestor
missing from the table below fails the test.

The table lists the requestors:

| File                                                                 | Prefix                               |
| -------------------------------------------------------------------- | ------------------------------------ |
| `skills/create-backlog/SKILL.md`                                     | `ST`                                 |
| `skills/create-backlog-stories/SKILL.md`                             | `ST`                                 |
| `skills/retrospective/SKILL.md`                                      | `T`, and `ST` for a backlog story    |
| `skills/write-adr/SKILL.md`                                          | `ADR`                                |
| `rulebooks/conventions/todo-format.md`                               | `T`                                  |
| `playbooks/bug-fix.md`                                               | `BUG`                                |
| `skills/inspect-spec/SKILL.md`, `agents/spec-review-agent.md`        | `SPEC`                               |
| `skills/atam-review/SKILL.md`, `agents/architecture-review-agent.md` | `ATAM`                               |
| `skills/maintain-architecture/SKILL.md`                              | `ARCH`                               |
| `agents/code-review-agent.md`                                        | `IMPL`                               |
| `skills/fagan-review/SKILL.md`                                       | `FAGAN`                              |
| `skills/security-review/SKILL.md`                                    | `SEC`                                |
| `skills/mutation-testing/SKILL.md`                                   | `QA`                                 |
| `skills/bug-hunt/SKILL.md`, `agents/qa-agent.md`                     | `BUG`                                |
| `skills/reconcile-spec/SKILL.md`, `agents/reconciliation-agent.md`   | `RECON`, and `BUG` for a code defect |

The new convention `rulebooks/conventions/id-prefixes.md` holds one table of
all twelve prefixes: the prefix, the kind of artifact, and the requestor files
(DEC-11). `rules.md`, `branching-policy.md`, and `finding-format.md` point to
it, and `finding-format.md` keeps only the review that files each tag, with the
row for `RECON` added. A thirteenth prefix means two changes: the list in
`next-id` and this table. A text test guards both.

## Scope

**In the first release:**

- the fitting step, its key, and its rows in the four orientation files;
- `next-id --plan-seed`;
- the local counter without `origin`: the setting
  `agent-factory.counterRemote`, the remote order in `next-id`, and
  `next-id --move-to-origin`;
- the derivation of `counter_seeded` in `init-factory`;
- the prefix named in each requestor of the table, the convention
  `id-prefixes.md`, and the pointers to it;
- the pointers in `create-backlog-stories` (`next-id ST`) and `retrospective`
  (`next-id T`);
- the text test for the requestors.

**Explicitly deferred (do NOT plan stories for these):**

- Re-seeding a counter that exists. A seed stays create-only (BR-069), and a
  re-seed means deleting the ref by hand.
- IDs on branches that are neither local nor fetched. `--plan-seed` reads only
  what the clone has, so a human fetches first.

## Open Questions

- None. Every question is decided; see the Decisions table.

## Completion Criteria

- `virgil.md` § Fitting has the step "Seed the ID counter" with the key
  `fitting.counter_seeded`, and `fitting.status` becomes `"fitted"` only when
  six keys are `true`.
- Each of the four orientation files lists six fitting keys, the sixth being
  `counter_seeded`.
- `next-id --plan-seed` in a clone with `ST-0375.md` and `ADR` up to `0032` on
  one branch and `ST-0380.md` on another prints a seed command with `ST=380`
  and `ADR=32`, and changes no ref.
- `next-id --plan-seed` against a remote that holds `refs/ids/counters` prints
  that the counter is in use and exits `0`.
- `next-id --plan-seed` in a repository without indexed artifacts prints
  `next-id --seed 0`.
- In a repository without `origin`, the fitting step seeds `refs/ids/counters`
  in the repository's own `.git` and sets `agent-factory.counterRemote`; a
  `next-id ST` in a second worktree of that repository then prints the next
  `ST` ID.
- `next-id ST` in a clone without `origin` and without
  `agent-factory.counterRemote` fails and names `origin` and `--remote`.
- `next-id --move-to-origin` copies the local counter to an `origin` without a
  counter and removes `agent-factory.counterRemote`; against an `origin` that
  holds a counter, it changes nothing and names both counters.
- `init-factory` sets `counter_seeded` from the remote that `next-id` would
  use, `agent-factory.counterRemote` before `origin`: `true` when it holds
  `refs/ids/counters`, `false` when it does not or when no remote exists, and
  unchanged when it is unreachable.
- `next-id --plan-seed` in a clone whose story `ST-0214.md` quotes `ST-9999` as
  an example, with `ST-0375.md` the highest story file, prints `ST=375`.
- `next-id --plan-seed` in a clone that holds
  `docs/findings/ATAM-0014-some-title.md`, `backlog/ST-0380A.md`, and
  `docs/findings/BUG-HUNT.md` prints `ATAM=14` and `ST=380`, warns about the
  ATAM name only, and exits `0`.
- After `next-id --move-to-origin`, the local `refs/ids/counters` holds only
  the marker `moved=<remote>`. `next-id ST` and `next-id --plan-seed` in a
  local clone whose `origin` is the project's path fail, name the remote that
  holds the counter, and do not mention `--seed`.
- `create-backlog-stories` names `next-id ST`, `retrospective` names
  `next-id T`, and the text test fails for a file that adds a `todo.md` entry
  without naming `next-id T`.
- Each requestor in the table of § Each requestor names its prefix contains
  `next-id <PREFIX>` with its prefix, and none contains `next-id <TAG>`.
- `rulebooks/conventions/id-prefixes.md` lists all twelve prefixes of
  `next-id` with their kind of artifact and requestors, and `rules.md`,
  `branching-policy.md`, and `finding-format.md` point to it.
- A text test fails when a requestor drops its prefix or a prefix in
  `id-prefixes.md` differs from the list in `next-id`.

## Guiding Rule

A project's IDs continue where they stand, and every agent knows the one
prefix it claims.

# Appendix

## Decisions

| ID     | Date       | Kind     | Decided by  | Decision                                                                                                                                                                                                                                                                                                                                                                                                                             | Raised by                                          |
| ------ | ---------- | -------- | ----------- | ------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------ | -------------------------------------------------- |
| DEC-01 | 2026-11-06 | decision | stakeholder | Seeding the counter becomes a step of the fitting.                                                                                                                                                                                                                                                                                                                                                                                   | counter-ids session, after the manual seed         |
| DEC-02 | 2026-11-06 | decision | stakeholder | Every ID requestor claims with its own specific prefix.                                                                                                                                                                                                                                                                                                                                                                              | counter-ids session                                |
| DEC-03 | 2026-11-06 | decision | stakeholder | VIRGIL runs the seed command after the human confirms it, because ADR-0032 already lets agents push the claim ref through `next-id`.                                                                                                                                                                                                                                                                                                 | counter-ids session                                |
| DEC-04 | 2026-11-06 | decision | stakeholder | The seed takes one pair per prefix from the highest number in use, so every sequence continues without a jump. `start` is `0`, so a prefix without IDs begins at `0001`.                                                                                                                                                                                                                                                             | stakeholder question on one seed per artifact type |
| DEC-05 | 2026-11-06 | decision | stakeholder | Without `origin`, the project's own repository holds the counter as `refs/ids/counters` in its `.git`, shared by all worktrees and local clones. One `git push origin refs/ids/counters` moves it once a remote exists. This supersedes counter-ids DEC-20. A second person's local counter is refused at that push, so a collision shows instead of staying silent. Refined by DEC-09: the move runs as `next-id --move-to-origin`. | counter-ids session                                |
| DEC-06 | 2026-11-06 | decision | stakeholder | A greenfield project walks the step too and seeds with `next-id --seed 0`.                                                                                                                                                                                                                                                                                                                                                           | counter-ids session                                |
| DEC-07 | 2026-11-06 | decision | stakeholder | `next-id --plan-seed` finds the highest numbers, so no agent counts files by hand. It lives in `next-id`, so the prefix list, the remote checks, and the redaction exist once.                                                                                                                                                                                                                                                       | mechanical-over-prose rule                         |
| DEC-08 | 2026-11-06 | decision | stakeholder | `next-id` finds a local counter through the git setting `agent-factory.counterRemote`, set by the fitting step and removed once the counter is on `origin`. Without the setting, a clone without `origin` fails as before, so no counter starts by accident.                                                                                                                                                                         | grilling on DEC-05                                 |
| DEC-09 | 2026-11-06 | decision | stakeholder | VIRGIL offers to move a local counter to `origin` and runs `next-id --move-to-origin` after the human confirms. The move is a `next-id` mode, because an agent may push the claim ref only through `next-id` (ADR-0032).                                                                                                                                                                                                             | grilling on DEC-05                                 |
| DEC-10 | 2026-11-06 | decision | stakeholder | The kind of artifact decides the prefix. A file that creates several kinds, such as `reconcile-spec` with `RECON` drift and `BUG` code defects, names one prefix at each step that creates one.                                                                                                                                                                                                                                      | grilling on the requestor table                    |
| DEC-11 | 2026-11-06 | decision | stakeholder | One table of all twelve prefixes lives in the new convention `id-prefixes.md`, and `rules.md`, `branching-policy.md`, and `finding-format.md` point to it.                                                                                                                                                                                                                                                                           | IMPL-0007                                          |
| DEC-12 | 2026-11-06 | decision | stakeholder | A finding file is named with its prefix and number only, `<PREFIX>-NNNN.md`. The 13 ATAM files lose their titles. `--plan-seed` fails on a file that starts with a prefix but breaks the pattern. Refined by PROP-12: it counts old names by their number and only warns.                                                                                                                                                            | PROP-02, pass 2                                    |
| DEC-13 | 2026-11-06 | decision | stakeholder | The proposal is accepted after review pass 4, with the minor rows PROP-06 to PROP-09 and PROP-13 open for planning.                                                                                                                                                                                                                                                                                                                  | review pass 4                                      |

## Review findings

| ID      | Pass | Severity | Check | Status   | Finding                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                              | Resolution                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                               |
| ------- | ---- | -------- | ----- | -------- | ---------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- | ------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------ |
| PROP-01 | 1    | major    | 03    | resolved | § The fitting step (L135-139), § `next-id --plan-seed` step 1 (L147-149), and § The local counter without `origin` (L174-176): two statements contradict each other. A greenfield project without `origin` is said to get `next-id --seed 0` from `--plan-seed`. But step 1 of `--plan-seed` fails with the claim's "no remote" message when no remote resolves, and `agent-factory.counterRemote` is not yet set at that point. The numbered steps of the fitting do not say when VIRGIL sets the setting, with which command, or which path it holds: the main worktree, the current worktree, or the common `.git` directory. Add the setting as a step before `--plan-seed`, name the command and the value, and say what happens to the setting when the human declines the seed. Class document, defect, type `inconsistent`. Severity: `fails_purpose` is yes, because the VIRGIL story and the `next-id` story must agree on the order and the value, and a planner has to ask.                                                                                                                                                                                                              | Fixed: § The fitting step, item 1 sets `agent-factory.counterRemote` to the main repository's path before `--plan-seed` when there is no `origin`. Pass 2: resolved. Item 1 sets the setting before `--plan-seed`, names the value, and the greenfield case now reaches the local counter.                                                                                                                                                                                                                                                                                                                               |
| PROP-02 | 1    | major    | 03    | resolved | § `next-id --plan-seed` step 2 (L150-153, L159-161) and Completion Criteria (L275-277): the rule "the file names and the text" does not define what counts as an ID in use. At the reviewed commit, the text holds invented examples: `backlog/ST-0214.md:22` names `ST-9999`, and `docs/adr/0032-agents-push-the-claim-ref-through-next-id.md:11` names `FAGAN-1004`. So `--plan-seed` would print `ST=9999` and `FAGAN=1004`. That is a jump for `FAGAN`, and `next-id` refuses `ST=9999` because `MAX_SEED` is 9998 (`next-id:60`). ADR files carry no prefix in their names (`0032-*.md`, `id: 0032`), so a project whose newest ADR nobody cites seeds one too low and hands out that ADR number twice. `SPEC-001` to `SPEC-011` have three digits. Define the match per prefix: which file name patterns count, whether text counts and where, the digit count, and how an ADR file maps to `ADR`. Add a criterion with an invented example in the text. Class document, defect, type `incorrect`. Severity: `fails_purpose` is yes, because a story built from the rule as written seeds this project with a jump and a refused command.                                                      | Fixed in pass 2 by DEC-12: file names carry the prefix and number only; the 13 ATAM files were renamed to `ATAM-NNNN.md`, and `--plan-seed` fails and names any file that starts with a prefix but breaks `<PREFIX>-NNNN.md`. Two criteria check both. Pass 1 fix: only file names, register `id` fields, and `## T-NNNN` headings count, never body text. Pass 3: resolved. DEC-12 names every finding file `<PREFIX>-NNNN.md`, the 13 ATAM files carry no title, and `--plan-seed` fails on a misnamed file instead of seeding low. PROP-12 records what the new stop rule catches beyond ATAM.                        |
| PROP-03 | 1    | major    | 03    | resolved | § Moving a local counter to `origin` (L185-199) and § The local counter without `origin` (L168-172): the move copies the counter but leaves `refs/ids/counters` in the project's `.git` live. A local clone has the project's path as its `origin` and no `agent-factory.counterRemote`, so after the move it still claims from the old local counter. Take a local counter at `ST=0012` that moves to a new `origin`. The project then claims `ST-0013` from `origin`, and the local clone also claims `ST-0013` from the project's `.git`. A claim from a worktree that runs between the push and the removal of the setting lands in the local counter too, and `origin` never sees it. Say what happens to the local ref after the move, how a local clone switches to the new counter, and add a criterion for a claim from a local clone after the move. Class document, defect, type `incomplete`. Severity: `fails_purpose` is yes, because the design hands out the same number twice, which is the failure the counter exists to prevent.                                                                                                                                                  | Fixed: § Moving a local counter, item 3 deletes the local `refs/ids/counters` after the push; a criterion checks that a local clone then fails with "counter missing". Pass 2: resolved. Item 3 deletes the local ref, and a criterion checks the clone. PROP-10 records what the clone's error message then tells a human. Refined by PROP-10: the local ref becomes a `moved=<remote>` marker instead of being deleted.                                                                                                                                                                                                |
| PROP-04 | 1    | major    | 03    | resolved | § Fitting keys and orientation files (L203-206) and Completion Criteria (L291-293): the derivation of `counter_seeded` uses `git ls-remote origin`, but `next-id` resolves `--remote`, then `agent-factory.counterRemote`, then `origin` (L178-179). Take a project with a local counter that has just added `origin`. `init-factory` sets the key to `false`, because `origin` holds no counter. The fitting step then runs `--plan-seed`, which resolves the local counter, reports it in use, and sets the key to `true`. The next `init-factory` run sets it back. Greenfield is undefined as well: `_reconcile_project_context` skips a greenfield cache (`init-factory:2831-2833`), the greenfield dict sets every other key (L2801-2808), and a greenfield session start never lists open steps, so "the session start lists the step as open" (L129-130) does not hold there. Derive the key with the same remote order as `next-id`, and state the greenfield value, its derivation, and where the open step shows. Class document, defect, type `inconsistent`. Severity: `fails_purpose` is yes, because the criterion encodes the flip, and the planner must ask how greenfield behaves. | Fixed: § Fitting keys derives `counter_seeded` from the remote `next-id` would use, setting before `origin`, which also covers greenfield; the criterion follows. Pass 2: resolved. The derivation now uses the remote order of `next-id`, so the key cannot flip, and the rule covers greenfield. Where a greenfield session start shows the open step stays with PROP-09.                                                                                                                                                                                                                                              |
| PROP-05 | 1    | major    | 02    | resolved | § Each requestor names its prefix (L212-234) and Completion Criteria (L294-295): the table misses files that create indexed artifacts. `skills/create-backlog-stories/SKILL.md:20` tells an agent to create `backlog/ST-NNNN.md` and does not name `next-id`. `skills/retrospective/SKILL.md:61` files action items as todos in `docs/spec/work/todo.md`, which take `T`. Under the accepted finding-classification proposal, a `question` from any review becomes a `todo.md` entry, so every review skill in the table also creates `T` entries, and DEC-10 asks for a prefix at each such step. The text test checks only the files in the table, so it does not catch a missing requestor. Add the missing files, or say how the list was built and what the test checks beyond it. Class document, defect, type `incomplete`. Severity: `fails_purpose` is yes, because a planner cuts the requestor stories from the table and leaves these files asking for a number without a prefix.                                                                                                                                                                                                        | Fixed: the table gains `create-backlog-stories` (`ST`) and `retrospective` (`T`, `ST`); every file that adds a `todo.md` entry names `next-id T`, and the text test finds such files by their reference to `todo.md`. Pass 2: resolved. The table gains both files, and every `todo.md` writer names `next-id T`. PROP-11 records the match rule of the text test.                                                                                                                                                                                                                                                       |
| PROP-06 | 1    | minor    | 05    | open     | `impact.boundaries` (L14-24): every path resolves except `rulebooks/conventions/id-prefixes.md`, which the design creates. The list leaves out files the design changes: `rulebooks/rules.md` and `rulebooks/conventions/branching-policy.md` (L238), the seventeen requestor files of the table, and `docs/spec/architecture.dsl`. Two more files become wrong and appear nowhere: `config/session-menu.md:42` shows the fitting as "X/5" and `:50` reruns "all five fitting steps", and `scripts/init-factory:3109` and `:3133` print "add the remote `origin`, then run `next-id --seed <number>`" and "with a number above your highest ID". Those hints contradict the local counter and the per-prefix seed. Add the files to the boundaries and the Scope. Class document, defect, type `incomplete`. Severity: the planner can act, because the Design names most of these files, but the stale hints and menu text stay unless a reader notices them.                                                                                                                                                                                                                                       |                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                          |
| PROP-07 | 1    | minor    | 04    | open     | Frontmatter `impact.architecture_change: false` (L12) and `supersedes:` (L8): the design changes rules that accepted records state. `docs/spec/architecture.dsl:26` places the counter on the "Project Git Remote", and `:120-121` says next-id "finds the remote from --remote or origin" and "leaves no ref and no object in the clone". A local counter puts the ref into the project's own `.git`. `docs/spec/interface-contracts.md` states the same in BR-074 (L1076) and BR-075 (L1078). counter-ids DEC-17 says "The script does no scan", which `--plan-seed` replaces, but the proposal names only DEC-20. Set `architecture_change` to `true` or say why the model stays, name the BR changes in Scope, and record DEC-17 as replaced. Class document, defect, type `inconsistent`. Severity: the planner can act, because the mechanical check in `playbooks/feature-addition.md` Step 1.4 corrects the flag, but the routing and the record read wrong until then.                                                                                                                                                                                                                      |                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                          |
| PROP-08 | 1    | minor    | 02    | open     | § Moving a local counter to `origin` (L195-197): when `origin` already holds a counter, the move changes nothing and VIRGIL reports the collision. The proposal then stops. The setting stays, VIRGIL offers the same move at every session start, and the project claims from its local counter while colleagues claim from `origin`. Neither In nor Deferred names how a human resolves the collision. Add it to Deferred with the manual steps, or to Scope. Class document, defect, type `incomplete`. Severity: the planner can act, because the refusal itself is defined, but a reader who meets the collision finds no next step.                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                            |                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                          |
| PROP-09 | 1    | minor    | 03    | open     | § Moving a local counter to `origin` (L185-188) and Scope (L247): "at the session start, VIRGIL checks" has no home. The session start lives in `AGENTS.*.md` § Session start and `config/session-menu.md`, and the AGENTS files read `virgil.md` only for "richer session behaviour", which is "not a prerequisite for turn 1". Scope lists only the key rows for the orientation files. Name the file that holds the check and add it to Scope. Class document, defect, type `incomplete`. Severity: the planner can act, because the move mode is defined, but the implementer must pick where the offer runs.                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                    |                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                          |
| PROP-10 | 2    | minor    | 03    | resolved | § Moving a local counter to `origin` (L200-204): after the move, a local clone whose `origin` is the project's path fails with "counter missing". The message of `RemoteCounter.read` (`next-id:356-358`) then says "run `next-id --seed <number>` once for the project", and in that clone the fitting step offers the same seed. Following either creates a second counter in the project's `.git`, while the project claims from `origin`. A claim from a worktree between the push and the deletion also lands in the deleted counter, and `origin` hands out its number again. Say what the clone's message tells the human, for example to set its `origin` to the project's new remote, and close or name the window. Class document, defect, type `incomplete`. Severity: the planner can act, because the move and its criterion are defined, but a human who follows the message splits the counter again.                                                                                                                                                                                                                                                                                 | Fixed in pass 3: the move sets the marker first with a lease on the read commit `C`, then pushes `C` to `origin`, and restores `C` with a lease on the marker when the push fails. A claim during the move either lands before the marker and is carried along, or fails on the marker. Pass 4: resolved. The marker now goes in first, with a lease on `C`, so a claim either lands before the marker and moves with `C`, or reads the marker and fails. A failed push puts `C` back. PROP-13 records an interrupted move.                                                                                              |
| PROP-11 | 2    | minor    | 01    | resolved | § Each requestor names its prefix (L255-259): the text test finds `T` requestors "by their reference to `todo.md`". Several files name `todo.md` without adding an entry: `skills/write-prd/SKILL.md:24` links to entries, `rulebooks/conventions/cross-reference-format.md:42-44` shows a link format, and `rulebooks/templates/todo-entry.md:8` is the template. As written, the test fails for these files, or they gain a `next-id T` they do not need. State the match, for example a verb that adds an entry, or an explicit list with exclusions. Class document, defect, type `ambiguous`. Severity: the planner can act, because the test has a criterion, but the implementer must pick the match rule.                                                                                                                                                                                                                                                                                                                                                                                                                                                                                    | Fixed: § Each requestor names its prefix: a `T` requestor names `next-id T` and points to `todo-format.md` at its step, and the text test finds requestors by that pointer, so a mere link to `todo.md` does not count. Pass 3: resolved. A `T` requestor names `next-id T` and points to `todo-format.md`, and the test finds it by that pointer, so `write-prd` and `cross-reference-format.md` are no requestors.                                                                                                                                                                                                     |
| PROP-12 | 3    | major    | 03    | resolved | § `next-id --plan-seed`, item 2 (L162-165), and DEC-12: the stop rule fails on a file "whose name starts with a prefix of the list but does not match `<PREFIX>-NNNN.md`". A split story is such a file: `skills/create-backlog/SKILL.md:44` and `skills/create-backlog-slice-story/SKILL.md:90-91` name splits `ST-NNNNA.md`, `ST-NNNNB.md`. So `--plan-seed` stops in every project that has split a story, and the fitting step cannot seed. At the reviewed commit, `docs/findings/` also holds `BUG-HUNT.md`, `RECON-cycle-retirement.md`, and `SPEC-001-script-exit-zero-inconsistency.md` and `SPEC-002-uc07-missing-test-command-reference.md`, which the rule stops on, while the criteria rename only the ATAM files. "Starts with a prefix" also matches any name that starts with `T` or `ST` without a hyphen. Accept the split letter, match `<PREFIX>-` instead of the bare prefix, and say what happens to the four other files. Class document, defect, type `inconsistent`. Severity: `fails_purpose` is yes, because a story built from the rule contradicts the Factory's own split naming and stops the fitting step.                                                           | Fixed: `--plan-seed` counts every name that starts with a prefix, a hyphen, and digits, by its number, including split stories and old titled or three-digit names; it warns about names that break `<PREFIX>-NNNN[letter].md` and goes on; names without a number do not count. DEC-12 binds new files only. A criterion checks the three cases. Pass 4: resolved. `--plan-seed` counts every `<PREFIX>-<digits>` name by its number, including `ST-0375A.md` and titled old names, and only warns. `BUG-HUNT.md` and `RECON-cycle-retirement.md` carry no number and do not count. A criterion checks all three cases. |
| PROP-13 | 4    | minor    | 03    | open     | § Moving a local counter to `origin`, steps 2 to 4: the design restores `C` only when the push fails. When the move stops between step 2 and the end of step 3, for example because the session ends or the network drops, the local ref holds the marker, `origin` holds no counter, and `agent-factory.counterRemote` is still set. Every claim then fails and names `origin` as the holder of a counter that is not there. Say how a human or a second run of `--move-to-origin` finishes or undoes such a move, for example by reading `C` as the parent or in the message of the marker. Class document, defect, type `incomplete`. Severity: the planner can act, because the normal path and the failed push are defined, but after an interrupted move the human has no next step.                                                                                                                                                                                                                                                                                                                                                                                                           |                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                          |

## Review passes

| Pass | Date       | Reviewed commit                          | Disposition | Failed checks   | Summary                                                                                                                                                                                                                                                                                                                                                                                                                  |
| ---- | ---------- | ---------------------------------------- | ----------- | --------------- | ------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------ |
| 1    | 2026-11-06 | 16d41b91a2e112e42fb2d3d0b545615bb197d3e4 | findings    | 02, 03, 04, 05  | Checks 01, 06, 07, and 08 pass: the criteria are concrete, Open Questions hides no decision, the 0401 jump motivates the timing, and the estimate fits the edits. Check 03 fails on the no-origin order, the ID match, the move, and the key derivation, and check 02 on missing requestors (5 major). Checks 02, 03, 04, and 05 add four minor rows on boundaries, records, the collision, and the session-start check. |
| 2    | 2026-11-06 | 55c6b760d2ad029a50bf8db7b6465019e00f4b38 | findings    | 01, 02, 03      | PROP-01, PROP-03, PROP-04, and PROP-05 are resolved. PROP-02 is open again: the finding file pattern misses titled names such as every ATAM file, so `ATAM-0001` would repeat (1 major). Checks 04 to 08 pass unchanged; the fixes add PROP-10 on the clone after the move and PROP-11 on the text test's match (2 minor). PROP-06 to PROP-09 stay open.                                                                 |
| 3    | 2026-11-06 | 80c81d42a8ab5bc67fb29cfc8e7e7d5cde2778b4 | findings    | 03              | PROP-02 and PROP-11 are resolved. PROP-10 stays open: the marker fixes the clone's message, but the window between the copy and the marker is still unnamed (minor). The new stop rule of `--plan-seed` rejects split stories `ST-NNNNA.md`, which the Factory creates, and four other finding files in this repository (PROP-12, 1 major).                                                                              |
| 4    | 2026-11-06 | 134d24baaebbf2f171aa5345da8616f815aa2022 | clean       | 03 (minor only) | PROP-10 and PROP-12 are resolved, so no `major` row is open. The new move order leaves one gap: a move interrupted between the marker and the push has no recovery path (PROP-13, minor). PROP-06 to PROP-09 and PROP-13 stay open and do not block.                                                                                                                                                                     |
