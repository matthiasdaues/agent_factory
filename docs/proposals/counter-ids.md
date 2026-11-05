---
schema_version: 2
scope: global
title: Counter IDs
status: open
owner: Matthias Daues
created: 2026-11-03
updated: 2026-11-04
supersedes:

impact:
  scope: cross_component
  architecture_change: false
  external_contract_change: true
  boundaries:
    - packages/factory/rulebooks/rules.md
    - packages/factory/rulebooks/conventions/branching-policy.md
    - packages/factory/rulebooks/conventions/finding-format.md
    - packages/factory/rulebooks/conventions/todo-format.md
    - packages/factory/scripts/init-factory
    - packages/factory/agents/planning-agent.md
    - packages/factory/skills/create-backlog-stories/SKILL.md
    - docs/proposals/manual-mode-gates.md

governance:
  assurance: elevated
  risk_domains:
    - data_integrity
    - operations
    - security

estimate:
  as_of: 2026-11-03
  basis: judgment
  confidence: low
  human_review_hours: unknown
  normalized_tokens: unknown
  estimated_consumption: unknown
---

# Feature Request: Counter IDs

## Primer

The primer is written last, by the `write-primer` skill, once the design is settled.

## Summary

Every new story, finding, and todo entry claims its number as a git ref on the project's remote, with one sequence per ID prefix. The remote accepts only one claim per number. So any branch in any session can create an indexed artifact, and no two artifacts get the same ID. The script `next-id` makes the claim and prints the ID. Existing IDs keep their names. The first release covers the prefixes that the Factory creates today.

## Motivation

Today each session takes the next free number by looking at the files it can see. Two sessions on different branches see the same highest number, so both create ST-0346. The rule "Indexed Artifacts On Dev" in [branching-policy.md](../../packages/factory/rulebooks/conventions/branching-policy.md#indexed-artifacts-on-dev) works around this: every indexed artifact must be committed to dev. That rule breaks the manual-mode story flow of [manual-mode-gates.md](manual-mode-gates.md), where a code review files findings on the story branch.

A claim on the shared remote removes the cause. Every clone pushes to the same remote, and the remote refuses a second claim of the same number. So a branch does not need to see the other branches to pick a free one.

## Core Principles

- **One source per number.** A number for a prefix comes only from a claim on the project's remote.
- **Agents never claim a number directly.** Every caller uses `next-id`, so the claim has one home.
- **A failed claim stops, it is never guessed.** When `next-id` cannot claim a number, it fails and names the reason.

## Design

### The counter port

`next-id` reaches the counter through a port with two operations (DEC-11):

| Operation                | Result                                                                       |
| ------------------------ | ---------------------------------------------------------------------------- |
| `claim <prefix>`         | Returns the next number of the prefix that no other caller holds.            |
| `seed <prefix> <number>` | Marks every number up to `<number>` as taken, so the next claim is above it. |

A counter adapter implements both operations for one backend. The config file names the adapter, so a project changes its backend without a change to any producer. The first release ships the git-ref adapter (DEC-12).

Each prefix of a project has its own sequence (DEC-02). The prefixes are the ones the Factory creates today: `ST`, `BUG`, `SPEC`, `FAGAN`, `SEC`, `RECON`, `ATAM`, `IMPL`, `RETRO`, and `T`. Review findings inside a proposal, such as `PROP-01`, get no sequence, because they are numbered within that proposal and cannot collide with another (DEC-09). A reference from outside names the proposal, as in "counter-ids PROP-01".

### The git-ref adapter

One ref on the project's remote, `refs/ids/counters`, holds every sequence of the project (DEC-14). It points at a claim commit: a commit with no parent on the empty tree, made with `git commit-tree`. The message of the claim commit holds one line per prefix with the highest number claimed so far, and a random token:

```text
ST=0348
FAGAN=0012
BUG=0007
token=9f3a61c0d2e4b871
```

The token makes every claim commit unique, so no two claims share a SHA. That matters because the remote does not reject a push that leaves a ref at the SHA it already has (DEC-13).

`claim <prefix>` runs these steps:

1. Fetch `refs/ids/counters` from the remote and read the message of its claim commit. A missing ref fails the claim, because only `seed` creates it.
2. Raise the line of the prefix by one. Keep every other line, and write a new token.
3. Create the new claim commit and push it to `refs/ids/counters` with the lease `--force-with-lease=refs/ids/counters:<old sha>`. The remote accepts the push only while the ref still holds the old SHA. So when another caller claimed first, for any prefix, the remote rejects the push.
4. If the remote rejects the push, wait a random time between 0.1 and 1 second, and start again at step 1. After ten rejections in a row, fail (DEC-15).

`seed <prefix> <number>` runs the same steps, but sets the line of the prefix to `<number>` instead of raising it. When `refs/ids/counters` does not exist yet, `seed` creates it with the create-only lease `--force-with-lease=refs/ids/counters:`.

The claim ref lives outside `refs/heads/` and `refs/tags/`, so it shows up in no branch list, and a default clone does not fetch it. An old claim commit has no ref once a newer one replaces it, so git's garbage collection removes it. Only a person or token with write access to the repository can change or delete the claim ref.

### The config file

`.agent-factory/config/id-counters.yaml` names the adapter, the remote, and the prefixes:

```yaml
---
adapter: git-ref
remote: origin
prefixes: [ST, BUG, SPEC, FAGAN, SEC, RECON, ATAM, IMPL, RETRO, T]
```

The file is tracked, so every clone and every session of the project claims on the same remote. A different project has a different remote, so its numbers never mix with this one.

### The script `next-id`

`packages/factory/scripts/next-id <PREFIX>` is the only caller of the counter port (DEC-05). It runs these steps:

1. Read the config file. A prefix that the file does not list exits non-zero.
2. Call `claim` for the prefix through the adapter that the config file names, and read the number.
3. Print the ID, such as `ST-0348`, on standard output, and exit `0`.

The ID on standard output is the only result. An agent reads it from the output and uses it in its next commands, because a shell variable does not survive from one agent command to the next (DEC-08). The variable `FACTORY_COUNTER_URL` replaces the remote from the config file, so tests claim on a local bare repository and never touch the real remote.

`next-id` exits non-zero and prints no ID in these cases:

| Case                           | Message names                        |
| ------------------------------ | ------------------------------------ |
| remote unreachable             | the remote and the git error message |
| `refs/ids/counters` missing    | the remote and `next-id --seed`      |
| ten rejected claims in a row   | the prefix and the last number tried |
| prefix missing from the config | the prefix and the config file       |

### Seeding

`next-id --seed <PREFIX>` finds the highest number of that prefix on every local and remote-tracking branch and calls `seed` with it. So the next `claim` returns the next free number. Existing IDs keep their names (DEC-03). ST-0327 stays ST-0327, and every commit subject and link that names it stays valid.

`init-factory` writes the config file when it is missing, and seeds each prefix that has no line in the claim commit.

### Producers

Every Factory step that creates an indexed artifact calls `next-id` instead of looking for the highest number:

- `create-backlog-stories` for stories.
- Every reviewer and the QA agent for findings.
- Every step that adds an entry to `docs/spec/work/todo.md`.
- The ticket adapters of [project-agent-flows.md](project-agent-flows.md#ticket-port), when they create an item.

### Indexed artifacts on any branch

An indexed artifact may be created and committed on any branch. [rules.md § Branching](../../packages/factory/rulebooks/rules.md#branching) and [branching-policy.md](../../packages/factory/rulebooks/conventions/branching-policy.md#indexed-artifacts-on-dev) state this instead of the dev-only rule.

### Claim pushes by agents

An agent that creates an indexed artifact runs `next-id`, and `next-id` pushes the claim ref. Agents may do this in manual and in automated mode (DEC-16). A claim push changes no branch and carries no code, and the lease refuses every stale update.

[rules.md § Dispatch](../../packages/factory/rulebooks/rules.md#dispatch) gives the human every push in manual mode. It states the claim push by `next-id` as the one exception. [rules.md § Git workflow](../../packages/factory/rulebooks/rules.md#git-workflow) states the same exception for both modes.

The guardrail hook `packages/factory/config/hooks/block-dangerous-git.sh` stays as it is. It checks the text of each shell command, so an agent's `next-id ST` passes, and a push that an agent types itself stays blocked. So the hook also keeps agents from claiming a number without `next-id`.

### The ID format

The ID format stays `<PREFIX>-<NNNN>`, so the scripts that parse IDs today need no change. These are `backlog-lint`, `premerge-check`, `crap-score`, `dependency-check`, `test-design-verify`, `module-graph-check`, and `migrate-story-schema`.

## Scope

**In the first release:**

- The counter port and the git-ref adapter.
- The script `next-id`, with `--seed`.
- The config file, and its creation and seeding in `init-factory`.
- The producers listed above call `next-id`.
- The branching rules allow indexed artifacts on any branch.
- Tests that claim on a local bare repository.

**Explicitly deferred (do NOT plan stories for these):**

- **Counter adapters for other backends.** A project whose remote refuses custom refs needs one. No project has asked for one yet.
- **Renaming existing IDs.** Old IDs keep their names (DEC-03).
- **Numbers above 9999.** No prefix is near that limit.

## Design Details

- **Security.** Only a person or token with write access can change or delete the claim ref. A writer who deletes it stops every claim until someone runs `next-id --seed`, which starts each sequence above the highest existing number again. Nothing in the Factory deletes the claim ref.
- **Availability.** Without the remote, no session can create an indexed artifact. Every session works online (DEC-07).
- **Gaps.** A number taken by a branch that is later abandoned is never used again. Gaps in a sequence are allowed.

## Open Questions

No open questions remain.

## Completion Criteria

- `next-id ST` prints the next story ID and exits `0`, and the claim commit on the remote then holds that number in its `ST` line.
- Two `next-id` calls from two clones at the same moment, for the same prefix or for two prefixes, print two different IDs, and both succeed after retries.
- `next-id ST` exits non-zero and names `next-id --seed` when `refs/ids/counters` is missing on the remote.
- `next-id ST` exits non-zero and names the remote when the remote is unreachable.
- With `FACTORY_COUNTER_URL` set, `next-id` claims on that remote and not on the one in the config file.
- `next-id --seed ST` sets the `ST` line to the highest existing story number on every local and remote-tracking branch, and keeps every other line.
- `init-factory` on a project without a config file writes one and seeds each prefix.
- Parallel claims from two clones against a GitHub repository hand out no number twice.
- `index-lint --check` passes.

# Appendix

## Decisions

| ID     | Date       | Kind       | Decided by  | Decision                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                 | Raised by                                                                |
| ------ | ---------- | ---------- | ----------- | -------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- | ------------------------------------------------------------------------ |
| DEC-01 | 2026-11-03 | decision   | stakeholder | IDs come from the counter service at countapi.mileshilliard.com. A random suffix per ID was considered and dropped in its favour. Replaced by DEC-12.                                                                                                                                                                                                                                                                                                                                                    | [manual-mode-gates.md](manual-mode-gates.md), indexed-artifacts question |
| DEC-02 | 2026-11-03 | decision   | stakeholder | Each ID prefix has its own counter, so today's sequences continue.                                                                                                                                                                                                                                                                                                                                                                                                                                       | counter scope question                                                   |
| DEC-03 | 2026-11-03 | decision   | stakeholder | Existing IDs keep their names. Each counter starts above the highest number in use.                                                                                                                                                                                                                                                                                                                                                                                                                      | migration question                                                       |
| DEC-04 | 2026-11-03 | decision   | stakeholder | The change gets its own proposal, because it touches every producer of indexed artifacts, not only manual mode.                                                                                                                                                                                                                                                                                                                                                                                          | home question                                                            |
| DEC-05 | 2026-11-03 | decision   | stakeholder | A script wraps the call to the counter service. Agents never call the service directly.                                                                                                                                                                                                                                                                                                                                                                                                                  | home question                                                            |
| DEC-06 | 2026-11-03 | assumption | author      | `next-id` checks every number against the branches before it hands it out, because the service lets anyone set a counter back. Replaced by DEC-12.                                                                                                                                                                                                                                                                                                                                                       | service has no authentication                                            |
| DEC-07 | 2026-11-03 | decision   | stakeholder | Every session works online, so the dependency on the service is accepted.                                                                                                                                                                                                                                                                                                                                                                                                                                | ID source question                                                       |
| DEC-08 | 2026-11-03 | decision   | stakeholder | `next-id` returns the ID on standard output. The variable `FACTORY_COUNTER_URL` replaces the service URL for tests.                                                                                                                                                                                                                                                                                                                                                                                      | caller interface question                                                |
| DEC-09 | 2026-11-03 | decision   | stakeholder | PROP findings inside a proposal get no counter. Legacy PROP-0001 to PROP-0024 files keep their names.                                                                                                                                                                                                                                                                                                                                                                                                    | PROP question                                                            |
| DEC-10 | 2026-11-03 | decision   | stakeholder | `next-id` fetches before its collision check, so a number pushed from another clone is seen. Replaced by DEC-12.                                                                                                                                                                                                                                                                                                                                                                                         | fetch question                                                           |
| DEC-11 | 2026-11-04 | decision   | stakeholder | `next-id` reaches the counter through a port with the operations `claim` and `seed`. A counter adapter per backend implements them.                                                                                                                                                                                                                                                                                                                                                                      | ID source question in [project-agent-flows.md](project-agent-flows.md)   |
| DEC-12 | 2026-11-04 | decision   | stakeholder | The first release ships the git-ref adapter. A number is claimed as `refs/ids/<PREFIX>/<NNNN>` on the project's remote with a create-only push. The claim replaces the countapi service, its keys, and the branch check.                                                                                                                                                                                                                                                                                 | countapi lets anyone who knows a key reset a counter                     |
| DEC-13 | 2026-11-04 | decision   | stakeholder | Each claim ref points at its own parentless commit on the empty tree, because a push that leaves a ref at the same SHA exits `0` and two claims would both win. With unique claim commits, `poc/counters/ref-claim-race.sh` reports "rounds without exactly one winner: 0 of 50" and "re-claim of an existing ref: rejected" on a local bare remote.                                                                                                                                                     | `poc/counters/ref-claim-race.sh`: "same-SHA re-claim: SUCCEEDED"         |
| DEC-14 | 2026-11-04 | decision   | stakeholder | One ref, `refs/ids/counters`, holds every sequence of the project. A claim replaces its claim commit with a lease on the old SHA. This replaces one ref per ID from DEC-12, so the ref list stays at one entry. `poc/counters/ref-claim-race.sh` with 20 rounds handed out 40 IDs with no duplicate and no gap, on a local bare remote, on the personal GitHub repository `matthiasdaues/agent_factory`, and on the enterprise repository `VFDE-GIGA-X/agent_factory`. Each claim took one or two tries. | one ref per ID litters `git log --all` and `git ls-remote`               |
| DEC-15 | 2026-11-04 | decision   | stakeholder | A rejected claim waits a random 0.1 to 1 second before it retries, and fails after ten rejections in a row.                                                                                                                                                                                                                                                                                                                                                                                              | one ref for all prefixes makes claims of different prefixes collide      |
| DEC-16 | 2026-11-04 | decision   | stakeholder | Agents may push the claim ref through `next-id` in manual and in automated mode. `rules.md` states it as an exception to the human's ownership of pushes. The guardrail hook stays unchanged.                                                                                                                                                                                                                                                                                                            | the guardrail hook blocks every push from an agent's shell               |

## Review findings

No review has run yet.

| ID  | Pass | Severity | Check | Status | Finding | Resolution |
| --- | ---- | -------- | ----- | ------ | ------- | ---------- |

## Review passes

No review has run yet.

| Pass | Date | Reviewed commit | Disposition | Failed checks | Summary |
| ---- | ---- | --------------- | ----------- | ------------- | ------- |
