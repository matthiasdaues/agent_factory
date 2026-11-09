---
schema_version: 2
scope: global
title: Mutation Gate
status: draft
owner: agent-factory
created: 2026-11-09
updated: 2026-11-09
supersedes:

impact:
  scope: cross_component
  architecture_change: false
  external_contract_change: true
  boundaries:
    - packages/factory/scripts/mutation-testing
    - packages/factory/skills/mutation-testing
    - packages/factory/rulebooks/references/mutation-testing-methodology.md
    - docs/testing.yaml

governance:
  assurance: elevated
  risk_domains:
    - reliability
    - operations

estimate:
  as_of: 2026-11-09
  basis: judgment
  confidence: low
  human_review_hours: unknown
  normalized_tokens: unknown
  estimated_consumption: unknown
---

# Feature Request: Mutation Gate

## Primer

The primer is written last, by the `write-primer` skill, once the design is settled.

## Summary

This proposal starts with a trial. A person runs Cosmic Ray by hand on five real stories in this repository, without blocking anything, and records what it finds. The design below is provisional until the trial has run. It came out of [crap-gate-setup.md](crap-gate-setup.md), which ships the CRAP gate first.

## Motivation

The `mutation-testing` gate is installed but cannot run, because no project has written its command, as [T-0402](../spec/work/todo.md) records. An agent also classifies every surviving mutant, so the verdict depends on the run.

Nobody has measured what the gate would do. One trial of Cosmic Ray on a copy of `finding-lint` created 1,744 mutants, about one per line. No figure exists for how many mutants survive, how many of those are equivalent mutants that no test can detect, or how long a real story takes. Every equivalent mutant would stop an automated run until a person acts, so that share decides whether the design is workable.

## Design

### The trial

A person picks five merged stories that changed Python code in this repository. For each story, the person runs Cosmic Ray over the changed lines at the story's merge commit, in a temporary worktree. Nothing blocks a merge, and no Factory file changes.

The trial records these figures for each story, in `docs/reviews/`:

| Figure          | Why it matters                                                           |
| --------------- | ------------------------------------------------------------------------ |
| Mutants         | The size of a typical run.                                               |
| Survivors       | How often a run would fail.                                              |
| Equivalents     | How often a person must act, judged by a person for each survivor.       |
| Time per mutant | Whether the time limit is realistic.                                     |
| Tests selected  | Whether per-test coverage finds the right tests, including subprocesses. |

The stakeholder decides from these figures whether the gate goes ahead and in what form.

### Provisional gate design

The sections below record the design as far as it was settled before the split. The trial may change any of it.

#### The mutation gate

The `mutation-testing` script runs the project's command. Like `crap_score`, the gate declares its `files` patterns and exclusions in `docs/testing.yaml`. The command writes one JSON array to `GATE_OUTPUT`, and the variable `GATE_CHANGED_LINES` names a file that lists the changed lines.

| Field      | Content                                                     |
| ---------- | ----------------------------------------------------------- |
| `file`     | Path relative to the repository root.                       |
| `function` | The function's name.                                        |
| `operator` | The mutation, such as `core/ReplaceBinaryOperator_Add_Sub`. |
| `ordinal`  | The position of this mutation within the function, from 0.  |
| `status`   | `killed` or `survived`.                                     |

The stable ID of a mutant is `file:function:operator:ordinal` (DEC-05). A line number is not part of it, because an edit above the function would change every ID below. The job ID of a tool is not part of it either, because Cosmic Ray's job IDs are random.

For each mutant, the command runs only the tests that execute the mutated code (DEC-21). The selection comes from per-test coverage measured on this commit, so nobody keeps a list of tests by hand (DEC-22). A mutant on code that no test executes counts as `survived` without a test run. The gate runs every mutant on a changed line, so partial runs and samples do not occur (DEC-23).

The gate runs in a temporary worktree of the commit, because mutation tools change files in place. Before it mutates anything, the gate runs the project's test command on the unchanged code. If that run fails, the gate exits 2, because a flaky or broken test would report false kills.

#### Surviving mutants

A surviving mutant means that a test is missing or weak, and it fails the gate. The fix is a better test or simpler code.

The one exception is an equivalent mutant, whose change no test can detect because the program behaves the same for every input. A person lists such a mutant by ID in the tracked file `docs/testing/accepted-survivors.yaml`. The row gives a reason why no test can tell the mutant from the original (DEC-18).

```yaml
- id: "scripts/x:count:core/ReplaceComparisonOperator_Lt_NotEq:0"
  reason: "i starts below n and rises by one, so i < n and i != n stop at the same moment."
  accepted_by: "A. Developer"
```

`story-gates` is the one script that runs a story's gates (see section "Where the gates run"). It reads this file from `dev` and ignores the version on the story branch (DEC-19). So an agent cannot accept a survivor from its own story. A commit on `dev` adds a row, and the story then passes without a rebase. Filing a QA finding does not unblock a merge (DEC-09). The contract-owner classification in the `mutation-testing` skill stays available as analysis and does not affect the verdict.

## Scope

**In the first release:**

- The trial on five stories and its report.

**Explicitly deferred (do NOT plan stories for these):**

- **The gate, the skill `setup-mutation-testing`, and every change to `mutation-testing`.** They wait for the trial's figures.

## Design Details

**Mutation volume.** A trial of Cosmic Ray on one copy of `finding-lint` created 1,744 mutants, about one per line, so the gate tests changed lines only. If a run exceeds `gates.mutation_testing.timeout_minutes`, the gate exits 2, and a person raises the limit or splits the story.

**Test selection per tool.** Some mutation tools select the tests for each mutant themselves. Cosmic Ray runs one fixed test command per mutant, so a Python setup with it needs a project-side selection step. Per-test coverage must also reach tests that start a script as a subprocess, which 55 test files in this repository do. The first Python setup story tries this and may choose another tool (DEC-22).

## Open Questions

- **Can per-test selection work here?** It needs per-test coverage across tests that start subprocesses, which 55 test files do. Cosmic Ray runs one fixed test command per mutant, so another tool may fit better. The trial answers this.
- **Can an automated run bear the cost of equivalent mutants?** Each one stops the run until a person commits on `dev`. The trial gives the share.

## Completion Criteria

- A report in `docs/reviews/` holds the five figures for each of five stories.
- The stakeholder has decided from the report whether the gate goes ahead, and the decision is in the Decisions table.

## Guiding Rule

No gate before the numbers.

# Appendix

## Decisions

These rows were made in [crap-gate-setup.md](crap-gate-setup.md) and keep their IDs.

| ID     | Date       | Kind     | Decided by  | Decision                                                                                                                                         | Raised by                          |
| ------ | ---------- | -------- | ----------- | ------------------------------------------------------------------------------------------------------------------------------------------------ | ---------------------------------- |
| DEC-05 | 2026-11-09 | decision | stakeholder | The stable mutant ID is `file:function:operator:ordinal`, because Cosmic Ray's job IDs are random and line numbers shift.                        | Trial of Cosmic Ray                |
| DEC-06 | 2026-11-09 | decision | stakeholder | A survivor fails the gate unless a tracked file lists its ID with a reason written by a person. This replaces the agent's classification.        | Author's recommendation, confirmed |
| DEC-09 | 2026-11-09 | decision | stakeholder | Filing a QA finding does not unblock a merge. Only a row in the accepted-survivors file does, so that the verdict needs no judgment by an agent. | Consequence of DEC-06              |
| DEC-18 | 2026-11-09 | decision | stakeholder | Every survivor fails. The accepted list holds only equivalent mutants, each with a reason why no test can detect it. Narrows DEC-06.             | Grilling, question 4               |
| DEC-19 | 2026-11-09 | decision | stakeholder | `story-gates` reads the accepted list from `dev`, so an agent cannot accept a survivor from its own story branch.                                | Grilling, question 4               |
| DEC-21 | 2026-11-09 | decision | stakeholder | For each mutant, only the tests that exercise that particular piece of code run.                                                                 | Grilling, question 5               |
| DEC-22 | 2026-11-09 | decision | stakeholder | Per-test coverage on the commit provides that selection. The first Python setup story tries it, including for tests that start subprocesses.     | Consequence of DEC-21              |
| DEC-23 | 2026-11-09 | decision | stakeholder | No partial runs and no samples. A run that exceeds the time limit exits 2.                                                                       | Grilling, question 5               |
| DEC-33 | 2026-11-09 | decision | stakeholder | The mutation gate starts with a hand-run trial on five real stories, with no blocking.                                                           | Independent skeptical review       |

## Review findings

No review has run yet.

| ID  | Pass | Severity | Check | Status | Finding | Resolution |
| --- | ---- | -------- | ----- | ------ | ------- | ---------- |

## Review passes

No review has run yet.

| Pass | Date | Reviewed commit | Disposition | Failed checks | Summary |
| ---- | ---- | --------------- | ----------- | ------------- | ------- |
