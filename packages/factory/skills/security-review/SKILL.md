---
name: security-review
description: Security-focused code review against OWASP Top 10 with minimised false positives.
category: quality
---

# Security Review

Read [factory-voice.md](../../rulebooks/conventions/factory-voice.md) now and hold every rule as a writing constraint. No prose reaches terminal output or a file until it passes all four gates and clears the final pass.

Review code changes for security vulnerabilities against the OWASP Top 10.
Read `rulebooks/principles/owasp-top-10.md` before proceeding. Skip only
if you can state all ten categories without reading.

Minimise false positives. Report only findings with a plausible attack
vector in this codebase.

## Scope

Identify the review scope using this fallback chain:

1. Explicit base and head SHAs → `git diff <base>..<head>`.
2. PR number → `gh pr diff <PR>`.
3. Fallback → `git diff $(git merge-base HEAD main)..HEAD`.

Read architecture documentation (`docs/03_system_scope_and_context.md`,
`docs/07_deployment_view.md`) to understand trust boundaries.

## Report

Save as `docs/reviews/security-review-YYYY-MM-DD.md` per
[report-format.md](../../rulebooks/conventions/report-format.md). This review classifies findings of the review class `security`. Classify each finding by [Class: security](../../rulebooks/conventions/finding-classification.md#class-security): record its basis, and let the rule of the class compute the severity. File each finding by that severity. A `critical` or `major` finding of the category `defect` or `risk` becomes a finding file with tag `SEC` from the [finding template](../../rulebooks/templates/finding.md), as [finding-format.md](../../rulebooks/conventions/finding-format.md) describes. A `minor` finding becomes one register file `docs/findings/register/security/<ID>.json` with `status: open` and gets no finding file. The commit that fixes it sets `status` of the register file to `resolved`. A `note` stays a row of the review report, and a `question` becomes an entry of `docs/spec/work/todo.md`. A register file takes its ID from `next-id`, as a finding file does. The bug-bar level of a finding goes into its `rating` field, and only the computed severity enters `severity`. Run `.agent-factory/factory/scripts/next-id SEC` and read the ID from its standard output, because a shell variable does not survive from one agent command to the next. When `next-id` fails, stop and report its message; never pick a number by hand.

Format via `scripts/mdformat --number` per
[markdown-formatting.md](../../rulebooks/conventions/markdown-formatting.md).
