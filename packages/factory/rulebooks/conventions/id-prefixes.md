---
title: ID Prefixes
category: process
enforcement: tests/factory/test_counter_ids_text.py (the table and the list in next-id must match)
version: 1.0.0
---

# ID Prefixes

`next-id` hands out the number of every indexed artifact. This table lists the twelve prefixes it serves, the kind of artifact each one numbers, and the files that tell an agent to claim the ID. Claim an ID with `.agent-factory/factory/scripts/next-id <PREFIX>`.

| Prefix  | Artifact                                | ID producer                                                                                                                                  |
| ------- | --------------------------------------- | -------------------------------------------------------------------------------------------------------------------------------------------- |
| `ST`    | Backlog story                           | `skills/create-backlog/SKILL.md`, `skills/create-backlog-stories/SKILL.md`, `skills/retrospective/SKILL.md`                                  |
| `BUG`   | Bug finding                             | `playbooks/bug-fix.md`, `skills/bug-hunt/SKILL.md`, `agents/qa-agent.md`, `skills/reconcile-spec/SKILL.md`, `agents/reconciliation-agent.md` |
| `SPEC`  | Spec review finding                     | `skills/inspect-spec/SKILL.md`, `agents/spec-review-agent.md`                                                                                |
| `FAGAN` | Fagan code inspection finding           | `skills/fagan-review/SKILL.md`                                                                                                               |
| `SEC`   | Security review finding                 | `skills/security-review/SKILL.md`                                                                                                            |
| `RECON` | Drift finding of the reconciliation     | `skills/reconcile-spec/SKILL.md`, `agents/reconciliation-agent.md`                                                                           |
| `ATAM`  | ATAM architecture review finding        | `skills/atam-review/SKILL.md`, `agents/architecture-review-agent.md`                                                                         |
| `IMPL`  | Implementation code review finding      | `agents/code-review-agent.md`                                                                                                                |
| `T`     | Todo entry                              | `rulebooks/conventions/todo-format.md`, `skills/retrospective/SKILL.md`                                                                      |
| `ADR`   | Architecture decision record            | `skills/write-adr/SKILL.md`                                                                                                                  |
| `ARCH`  | Architecture agent's read-check finding | `skills/maintain-architecture/SKILL.md`                                                                                                      |
| `QA`    | Unresolved mutant finding               | `skills/mutation-testing/SKILL.md`, `agents/reconciliation-agent.md`                                                                         |

The producer paths lie under `packages/factory/`. A thirteenth prefix means two changes: the list in `scripts/next-id` and this table. A text test fails when they differ.

`PROP` rows in a proposal, the split letters of a story, and other IDs keep their own numbering rule and stay outside the counter.

## Referenced from

- [rules.md § Branching](../rules.md#branching)
- [branching-policy.md](branching-policy.md)
- [finding-format.md § File location and name](finding-format.md#file-location-and-name)
