---
name: security-review
description: Security-focused code review based on the OWASP Top 10.
category: quality
disable-model-invocation: true
---

# Security Review

Review code changes for security vulnerabilities based on the **OWASP Top 10**.

## Step 1 — Identify the review scope

Determine what to review: a branch diff, a PR, or a set of files. Read the architecture documentation (`docs/03_system_scope_and_context.md`, `docs/07_deployment_view.md`) to understand trust boundaries and data flows.

**Completion**: scope identified, trust boundaries understood.

## Step 2 — Evaluate against OWASP Top 10

Check every changed file against all ten current OWASP Top 10 categories (A01–A10).

For each finding:

- Identify the OWASP category
- Describe the attack vector — how would an attacker exploit this?
- Assess severity: Critical / High / Medium / Low
- Provide a concrete remediation — what code change fixes this?

Minimise false positives — do not flag a theoretical risk without a plausible attack vector in this codebase.

**Completion**: every changed file evaluated against all 10 categories, only high-confidence findings reported.

## Step 3 — Write the review report

Save as `docs/reviews/security-review-YYYY-MM-DD.md` per [report-format.md](../../rulebooks/report-format.md). File findings per [finding-format.md](../../rulebooks/finding-format.md) with tag `SEC` for findings rated Medium or higher.

Format both the report and any finding files via `scripts/mdformat --number` per [markdown-formatting.md](../../rulebooks/markdown-formatting.md).
