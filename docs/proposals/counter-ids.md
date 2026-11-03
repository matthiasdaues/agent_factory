---
schema_version: 2
scope: global
title: Counter IDs
status: draft
owner: Matthias Daues
created: 2026-11-03
updated: 2026-11-03
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

Every new story, finding, and todo entry gets its number from a central counter, one counter per ID prefix. So any branch in any session can create an indexed artifact, and no two artifacts get the same ID. The script `next-id` wraps the call to the counter and checks the result before it hands out an ID. Existing IDs keep their names. The first release covers the prefixes that the Factory creates today.

## Motivation

Today each session takes the next free number by looking at the files it can see. Two sessions on different branches see the same highest number, so both create ST-0346. The rule "Indexed Artifacts On Dev" in [branching-policy.md](../../packages/factory/rulebooks/conventions/branching-policy.md#indexed-artifacts-on-dev) works around this: every indexed artifact must be committed to dev. That rule breaks the manual-mode story flow of [manual-mode-gates.md](manual-mode-gates.md), where a code review files findings on the story branch.

A central counter removes the cause. A number comes from one place, so a branch does not need to see the other branches to pick a free one.

## Core Principles

- **One source per number.** A number for a prefix comes only from that prefix's counter.
- **Agents never call the counter directly.** Every caller uses `next-id`, so the service, the keys, and the checks have one home.
- **A wrong number stops, it is never used.** When `next-id` cannot prove a number is free, it fails and names the reason.

## Design

### The counter service

The counter is the hosted service at `https://countapi.mileshilliard.com`. `GET /api/v1/hit/{key}` increments a key by one and returns the new value. `GET /api/v1/set/{key}?value=N` sets a key to a value. The service has no authentication, so anyone who knows a key can read, increment, or set it (DEC-01).

Each prefix of a project has its own key (DEC-02). The prefixes are the ones the Factory creates today: `ST`, `BUG`, `SPEC`, `FAGAN`, `SEC`, `RECON`, `ATAM`, `IMPL`, `RETRO`, and `T`. Review findings inside a proposal, such as `PROP-01`, get no counter, because they are numbered within that proposal and cannot collide with another (DEC-09). A reference from outside names the proposal, as in "counter-ids PROP-01".

### The key file

`.agent-factory/config/id-counters.yaml` maps each prefix to its key:

<!-- yaml-excerpt -->

```yaml
service: https://countapi.mileshilliard.com/api/v1
counters:
  ST: 3f9c…     # 40 hexadecimal characters, random per project and prefix
  BUG: a71e…
```

The file is tracked, so every clone and every session of the project uses the same keys. A different project has different keys, so its numbers never mix with this one.

### The script `next-id`

`packages/factory/scripts/next-id <PREFIX>` is the only caller of the service (DEC-05). It runs these steps:

1. Read the key for `<PREFIX>` from the key file. A prefix without a key exits non-zero.
2. Call `hit` for that key and read the number.
3. Run `git fetch --quiet`, so the remote-tracking branches are current (DEC-10). Then check that no file named `<PREFIX>-<NNNN>` exists on any local branch or remote-tracking branch. The check reads `git ls-tree` of each branch tip and needs no checkout (DEC-06).
4. Print the ID, such as `ST-0346`, on standard output, and exit `0`.

The ID on standard output is the only result. An agent reads it from the output and uses it in its next commands, because a shell variable does not survive from one agent command to the next (DEC-08). The variable `FACTORY_COUNTER_URL` replaces the service URL from the key file, so tests run against a local fake and never touch the real counter.

`next-id` exits non-zero and creates no ID in these cases:

| Case                                               | Message names                                 |
| -------------------------------------------------- | --------------------------------------------- |
| service or remote unreachable, or non-number reply | the service URL and the HTTP status           |
| number already used on a branch                    | the existing file and its branch, and a reset |
| prefix missing from the key file                   | the prefix and the key file                   |

A used number means that someone set the counter back. `next-id` does not skip ahead on its own, because a reset can repeat. The human reseeds the counter with `next-id --seed <PREFIX>`.

### Seeding

`next-id --seed <PREFIX>` finds the highest number of that prefix on every local and remote-tracking branch and sets the counter to it with `set`. So the next `hit` returns the next free number. Existing IDs keep their names (DEC-03). ST-0327 stays ST-0327, and every commit subject and link that names it stays valid.

`init-factory` creates a key for each prefix that has none, writes the key file, and seeds each new counter.

### Producers

Every Factory step that creates an indexed artifact calls `next-id` instead of looking for the highest number:

- `create-backlog-stories` for stories.
- Every reviewer and the QA agent for findings.
- Every step that adds an entry to `docs/spec/work/todo.md`.

### Indexed artifacts on any branch

An indexed artifact may be created and committed on any branch. [rules.md § Branching](../../packages/factory/rulebooks/rules.md#branching) and [branching-policy.md](../../packages/factory/rulebooks/conventions/branching-policy.md#indexed-artifacts-on-dev) state this instead of the dev-only rule.

### The ID format

The ID format stays `<PREFIX>-<NNNN>`, so the scripts that parse IDs today need no change. These are `backlog-lint`, `premerge-check`, `crap-score`, `dependency-check`, `test-design-verify`, `module-graph-check`, and `migrate-story-schema`.

## Scope

**In the first release:**

- The script `next-id`, with `--seed`.
- The key file and its creation and seeding in `init-factory`.
- The producers listed above call `next-id`.
- The branching rules allow indexed artifacts on any branch.
- Tests against a local fake of the counter service.

**Explicitly deferred (do NOT plan stories for these):**

- **IDs assigned by a ticket adapter.** [project-agent-flows.md](project-agent-flows.md) gives that job to the ticket adapter (DEC-08 there). When the adapter exists, `next-id` asks it instead of the counter service.
- **Renaming existing IDs.** Old IDs keep their names (DEC-03).
- **Numbers above 9999.** No prefix is near that limit.

## Design Details

- **Security.** The keys are in a tracked file. In a public repository anyone can read them and set a counter. The collision check in `next-id` turns such a reset into a failed call instead of a duplicate ID.
- **Availability.** Without the service, no session can create an indexed artifact. Every session works online (DEC-07).
- **Gaps.** A number taken by a branch that is later abandoned is never used again. Gaps in a sequence are allowed.

## Open Questions

No open questions remain.

## Completion Criteria

- `next-id ST` prints the next story ID and exits `0` when the number is free on every branch.
- `next-id ST` exits non-zero and names the existing file when the counter returns a number that a branch already uses.
- `next-id ST` exits non-zero and names the service URL when the service is unreachable.
- With `FACTORY_COUNTER_URL` set, `next-id` calls that URL and not the one in the key file.
- `next-id --seed ST` sets the counter to the highest existing story number on every local and remote-tracking branch.
- `init-factory` on a project without a key file writes one key per prefix and seeds each counter.
- Two sessions on two branches that each create a story get two different IDs.
- `index-lint --check` passes.

# Appendix

## Decisions

| ID     | Date       | Kind       | Decided by  | Decision                                                                                                                          | Raised by                                                                |
| ------ | ---------- | ---------- | ----------- | --------------------------------------------------------------------------------------------------------------------------------- | ------------------------------------------------------------------------ |
| DEC-01 | 2026-11-03 | decision   | stakeholder | IDs come from the counter service at countapi.mileshilliard.com. A random suffix per ID was considered and dropped in its favour. | [manual-mode-gates.md](manual-mode-gates.md), indexed-artifacts question |
| DEC-02 | 2026-11-03 | decision   | stakeholder | Each ID prefix has its own counter, so today's sequences continue.                                                                | counter scope question                                                   |
| DEC-03 | 2026-11-03 | decision   | stakeholder | Existing IDs keep their names. Each counter starts above the highest number in use.                                               | migration question                                                       |
| DEC-04 | 2026-11-03 | decision   | stakeholder | The change gets its own proposal, because it touches every producer of indexed artifacts, not only manual mode.                   | home question                                                            |
| DEC-05 | 2026-11-03 | decision   | stakeholder | A script wraps the call to the counter service. Agents never call the service directly.                                           | home question                                                            |
| DEC-06 | 2026-11-03 | assumption | author      | `next-id` checks every number against the branches before it hands it out, because the service lets anyone set a counter back.    | service has no authentication                                            |
| DEC-07 | 2026-11-03 | decision   | stakeholder | Every session works online, so the dependency on the service is accepted.                                                         | ID source question                                                       |
| DEC-08 | 2026-11-03 | decision   | stakeholder | `next-id` returns the ID on standard output. The variable `FACTORY_COUNTER_URL` replaces the service URL for tests.               | caller interface question                                                |
| DEC-09 | 2026-11-03 | decision   | stakeholder | PROP findings inside a proposal get no counter. Legacy PROP-0001 to PROP-0024 files keep their names.                             | PROP question                                                            |
| DEC-10 | 2026-11-03 | decision   | stakeholder | `next-id` fetches before its collision check, so a number pushed from another clone is seen.                                      | fetch question                                                           |

## Review findings

No review has run yet.

| ID  | Pass | Severity | Check | Status | Finding | Resolution |
| --- | ---- | -------- | ----- | ------ | ------- | ---------- |

## Review passes

No review has run yet.

| Pass | Date | Reviewed commit | Disposition | Failed checks | Summary |
| ---- | ---- | --------------- | ----------- | ------------- | ------- |
