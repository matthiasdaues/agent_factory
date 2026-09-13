---
name: security-review
description: Security-focused code review against OWASP Top 10 with minimised false positives.
category: quality
disable-model-invocation: true
---

# Security Review

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
[report-format.md](../../rulebooks/conventions/report-format.md). File
findings per
[finding-format.md](../../rulebooks/conventions/finding-format.md) with
tag `SEC` for findings rated Medium or higher.

Format via `scripts/mdformat --number` per
[markdown-formatting.md](../../rulebooks/conventions/markdown-formatting.md).
