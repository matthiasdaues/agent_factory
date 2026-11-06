---
type: fagan-review
title: Fagan review of the BUG-0115 fix
date: 2026-11-06
status: defects
reviewer: qa-agent
findings_filed: 2
story: BUG-0115
branch: feature/bug-0115-dispatch-ledger
branch_base: 279f01a8fc60d7daff9a092a688f2cda6db6a439
branch_head: 80bdb99a1f2edac6ea829393cd619797d772d211
---

# Fagan review of the BUG-0115 fix

Scope: commit `80bdb99a` against `dev`, two files. The review applies the
`finding-classification` proposal.

## Findings

| ID         | Severity | Type      | Where                                    | Title                                                    |
| ---------- | -------- | --------- | ---------------------------------------- | -------------------------------------------------------- |
| BUG-0116   | major    | interface | `packages/factory/scripts/dispatch:2206` | `dispatch init` fails when several ledgers exist         |
| FAGAN-0032 | minor    | checking  | `packages/factory/scripts/dispatch:1588` | A hex-named ref beats an abbreviated SHA (register line) |

BUG-0116 is fixed in `ff6245eb23fcbade7c413410370423c6c41b49b6`. FAGAN-0032
sits in `docs/findings/register/code.jsonl`.

## Notes

- Spec compliance: the three fix points match `BUG-0115.md`. The story-branch
  lookup, the wave check, and the SHA expansion each have a test.
- `verify-base --expect-base` is a separate script and keeps its 40-character
  demand. The widened `_validate_sha_format` serves only `verify-story`.
- Every other subcommand reads `args.ledger`, so the new error reaches them as
  intended, with the ledger list and the `--ledger` hint.
- When two ledgers hold the same story on a story branch, the lookup falls
  through to the error. This is acceptable because story IDs are unique.
- Test-design-pass and contract-to-test checks do not apply: BUG-0115 is a
  finding, not a backlog story.
