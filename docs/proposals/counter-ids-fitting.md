---
schema_version: 2
title: Seed the ID counter in the fitting, and name each requestor's prefix
status: draft
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

The primer is written last, by the `write-primer` skill, once the design is
settled.

## Summary

The fitting gets a sixth step that seeds the ID counter of
[counter-ids](counter-ids.md) on the project's `origin`. A new mode of
`next-id` reads the highest ID of each prefix from the project's branches and
prints the seed command, with one pair per prefix, so each sequence continues
without a jump. VIRGIL shows that command and runs it once the human confirms.
Every file that tells an agent to create an indexed artifact also names the one
prefix that artifact takes, so no agent claims an ID with a wrong or borrowed
prefix.

## Motivation

`next-id` hands out every ID from `refs/ids/counters` on `origin`. Until that
ref exists, every claim fails with "counter missing", and every producer stops.
Today the counter comes into being only when a human runs `next-id --seed` by
hand. `init-factory` prints a hint (ST-0375), but nothing in the fitting asks
for the seed, and nothing finds the highest IDs in use. In this project the
human seeded with `--seed 400 ADR=32`, so `ST`, `BUG`, and every other prefix
jumped to 0401, and only `ADR` continued its sequence.

The second gap lies in the producers. `finding-format.md` tells a reviewer to
claim "`next-id <TAG>`" and lists the tags in a table. Fourteen agents and
skills file findings, and none of them names its own tag or `next-id`. The table
also lacks `RECON`, although the reconciliation agent files `RECON` findings,
and the list in its first bullet lacks `ST`, `T`, and `ADR` (IMPL-0007). An
agent that has to work out its prefix from a table can pick the wrong one. A
wrong prefix does not fail: `next-id BUG` hands out a valid `BUG` number for a
finding that should have been `FAGAN`, and that number is gone.

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

The fitting in `virgil.md` § Fitting gets a sixth step, "Seed the ID counter",
after step 3, "Decide on hooks". It flips the key `fitting.counter_seeded` in
`.agent-factory/config/project-context.json`. `fitting.status` becomes
`"fitted"` only when all six keys are `true`.

In the step, VIRGIL:

1. runs `next-id --plan-seed`, which prints the seed command, or a message why
   no seed is needed or possible;
2. shows the command to the human and says what it does: it creates
   `refs/ids/counters` on `origin` once, and every later ID continues from it;
3. runs the command when the human confirms, and sets the key;
4. stops the step without setting the key when the human declines, or when
   `origin` is unreachable. VIRGIL names the reason, and the session start
   lists the step as open until it is done.

Without `origin`, the project's own repository holds the counter: the ref
`refs/ids/counters` in its `.git`. All worktrees share that `.git`, and a local
clone has the project as its `origin`, so all of them claim from one counter.
Once a remote exists, `next-id --move-to-origin` moves the counter there, and
every sequence continues. The move is create-only, so a counter that someone
else already seeded on that remote refuses it, and the collision shows
(DEC-05). This replaces the rule of counter-ids that `next-id` fails without a
remote (counter-ids DEC-20).

`next-id` finds the local counter through the git setting
`agent-factory.counterRemote`, which holds the path of the project's
repository. The fitting step sets it when the project has no `origin`, and
removes it once the counter has moved to `origin`. `.git/config` is shared by
all worktrees, so all of them see it. `next-id` resolves its remote in this
order: `--remote`, then `agent-factory.counterRemote`, then `origin`. A clone
that lost its `origin` by mistake has no such setting, so its claim still fails
and names `origin` and `--remote` (DEC-08).

### Moving a local counter to `origin`

At the session start, VIRGIL checks whether `agent-factory.counterRemote` is
set and `origin` exists. When both hold, it offers the move and runs
`next-id --move-to-origin` after the human confirms (DEC-09). That mode:

1. reads the claim commit of the local counter;
2. pushes it to `refs/ids/counters` on `origin` with the create-only lease
   `--force-with-lease=refs/ids/counters:`;
3. removes `agent-factory.counterRemote` when the push succeeds.

When `origin` already holds a counter, the push is refused. `next-id` then
names both counters and changes nothing, and VIRGIL reports the collision.
The move is a push of the claim ref through `next-id`, which ADR-0032 already
allows an agent; a plain `git push` by an agent stays blocked.

When `refs/ids/counters` already exists on `origin`, the step sets the key and
reports that the counter is in use, without a seed.

Greenfield projects (`fitting.status == "greenfield"`) walk step 0 and this
step, so a newcomer's first backlog never fails at a missing counter (DEC-06).
A greenfield project has no indexed artifacts, so `--plan-seed` prints
`next-id --seed 0`. Without `origin`, the seed goes to the local counter below,
and the first story is `ST-0001`.

ADR-0032 already lets an agent push the claim ref through `next-id`. The seed
is a push of the same ref through the same script, so VIRGIL runs it after
the human's confirmation (DEC-03).

### `next-id --plan-seed`

`next-id --plan-seed [--remote <url>]` is a read-only mode of `next-id`, so
the prefix list, the remote checks, and the redaction exist once (DEC-07). It
changes nothing. It:

1. checks the remote as a claim does. When `refs/ids/counters` exists, it
   prints "the counter is in use on <remote>" and exits `0`. When the remote is
   missing or unreachable, it fails with the same messages as a claim;
2. collects the IDs in use for each prefix of its list from the file names and
   the text of `backlog/`, `docs/findings/` with its registers, `docs/adr/`,
   and `docs/spec/work/todo.md`, on every local branch and every
   remote-tracking branch;
3. prints one command:
   `next-id --seed <start> <PREFIX>=<highest> …`, with one pair for each
   prefix that has an ID in use. `<start>` is `0`, so a prefix without IDs
   starts at `0001`, and every sequence begins at one (DEC-04).

The remote shows redacted, as BR-077 requires for every line `next-id` writes.

### Fitting keys in `init-factory`

`init-factory` derives the fitting keys from the project's state on every run.
It derives `counter_seeded` from `git ls-remote origin refs/ids/counters`, the
check that ST-0375 runs. An unreachable `origin` leaves the key as it is, so a
run without network never resets a seeded project.

The orientation files `AGENTS.claude.md`, `AGENTS.codex.md`,
`AGENTS.copilot.md`, and `AGENTS.pi.md` list the fitting keys in a table and
count the steps. Each gets the sixth row and the count "six".

### Each requestor names its prefix

Every file that tells an agent to create an indexed artifact names the claim
with its literal prefix, at the step that creates the artifact, for example
"Claim the ID with `.agent-factory/factory/scripts/next-id FAGAN`". The kind of
artifact decides the prefix, not the file: a file that creates two kinds names
one prefix at each of the two steps (DEC-10). These are the requestors:

| File                                                                 | Prefix                               |
| -------------------------------------------------------------------- | ------------------------------------ |
| `skills/create-backlog/SKILL.md`                                     | `ST`                                 |
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
row for `RECON` added. A thirteenth prefix means two changes, the list in
`next-id` and this table. A text test checks that each requestor names `next-id`
with each of its prefixes, that no requestor asks for `next-id <TAG>`, and
that the prefixes in `id-prefixes.md` equal the list in `next-id`.

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
- the text test for the requestors.

**Explicitly deferred (do NOT plan stories for these):**

- Re-seeding a counter that exists. A seed stays create-only (BR-069), and a
  re-seed means deleting the ref by hand.
- IDs on branches that are neither local nor fetched. `--plan-seed` reads only
  what the clone has; a human fetches first.

## Design Details

- `--plan-seed` reads the highest number, not the count, so a gap in a
  sequence does not lower the seed.
- A prefix with IDs only in a register line, such as a `minor` finding, counts
  like one with a file.
- The step runs after the hooks because a seed is a push, and the human should
  have decided on the hooks before the first push the Factory makes.

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
- `init-factory` sets `counter_seeded` to `true` when `origin` holds
  `refs/ids/counters`, to `false` when it does not, and leaves it unchanged
  when `origin` is unreachable.
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

| ID     | Date       | Kind     | Decided by  | Decision                                                                                                                                                                                                                                                                                                                                                             | Raised by                                          |
| ------ | ---------- | -------- | ----------- | -------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- | -------------------------------------------------- |
| DEC-01 | 2026-11-06 | decision | stakeholder | Seeding the counter becomes a step of the fitting.                                                                                                                                                                                                                                                                                                                   | counter-ids session, after the manual seed         |
| DEC-02 | 2026-11-06 | decision | stakeholder | Every ID requestor claims with its own specific prefix.                                                                                                                                                                                                                                                                                                              | counter-ids session                                |
| DEC-03 | 2026-11-06 | decision | stakeholder | VIRGIL runs the seed command after the human confirms it, because ADR-0032 already lets agents push the claim ref through `next-id`.                                                                                                                                                                                                                                 | counter-ids session                                |
| DEC-04 | 2026-11-06 | decision | stakeholder | The seed takes one pair per prefix from the highest number in use, so every sequence continues without a jump. `start` is `0`, so a prefix without IDs begins at `0001`.                                                                                                                                                                                             | stakeholder question on one seed per artifact type |
| DEC-05 | 2026-11-06 | decision | stakeholder | Without `origin`, the project's own repository holds the counter as `refs/ids/counters` in its `.git`, shared by all worktrees and local clones. One `git push origin refs/ids/counters` moves it once a remote exists. This supersedes counter-ids DEC-20. A second person's local counter is refused at that push, so a collision shows instead of staying silent. | counter-ids session                                |
| DEC-06 | 2026-11-06 | decision | stakeholder | A greenfield project walks the step too and seeds with `next-id --seed 0`.                                                                                                                                                                                                                                                                                           | counter-ids session                                |
| DEC-07 | 2026-11-06 | decision | stakeholder | `next-id --plan-seed` finds the highest numbers, so no agent counts files by hand. It lives in `next-id`, so the prefix list, the remote checks, and the redaction exist once.                                                                                                                                                                                       | mechanical-over-prose rule                         |
| DEC-08 | 2026-11-06 | decision | stakeholder | `next-id` finds a local counter through the git setting `agent-factory.counterRemote`, set by the fitting step and removed once the counter is on `origin`. Without the setting, a clone without `origin` fails as before, so no counter starts by accident.                                                                                                         | grilling on DEC-05                                 |
| DEC-09 | 2026-11-06 | decision | stakeholder | VIRGIL offers to move a local counter to `origin` and runs `next-id --move-to-origin` after the human confirms. The move is a `next-id` mode, because an agent may push the claim ref only through `next-id` (ADR-0032).                                                                                                                                             | grilling on DEC-05                                 |
| DEC-10 | 2026-11-06 | decision | stakeholder | The kind of artifact decides the prefix. A file that creates several kinds, such as `reconcile-spec` with `RECON` drift and `BUG` code defects, names one prefix at each step that creates one.                                                                                                                                                                      | grilling on the requestor table                    |
| DEC-11 | 2026-11-06 | decision | stakeholder | One table of all twelve prefixes lives in the new convention `id-prefixes.md`, and `rules.md`, `branching-policy.md`, and `finding-format.md` point to it.                                                                                                                                                                                                           | IMPL-0007                                          |

## Review findings

| ID  | Pass | Severity | Check | Status | Finding | Resolution |
| --- | ---- | -------- | ----- | ------ | ------- | ---------- |

## Review passes

| Pass | Date | Reviewed commit | Disposition | Failed checks | Summary |
| ---- | ---- | --------------- | ----------- | ------------- | ------- |
