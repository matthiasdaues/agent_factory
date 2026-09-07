---
name: fagan-review
description: Structured code review following the Fagan Inspection method — correctness, Clean Architecture, SOLID, maintainability.
category: quality
disable-model-invocation: true
---

# Fagan Review

A structured code review following the **Fagan Inspection** method. The review checks correctness against the specification, architectural compliance, and maintainability. Every finding is categorised and actionable.

Read `docs/CONTEXT.md` if it exists — flag terminology drift between code and domain vocabulary.

## Step 1 — Identify the review scope

Identify the code to review using this three-tier fallback:

1. **Explicit commits (highest priority)**: if base and head commit SHAs are provided, use `git diff <base>..<head>` to scope the review.
2. **Pull request**: if a PR number is provided, use `gh pr diff <PR>` to scope the review.
3. **Main branch (fallback only)**: if neither explicit commits nor a PR number is given, fall back to `git diff $(git merge-base HEAD main)..HEAD`.

Read the relevant Use Case(s) and supplementary specs for the code under review.

**Completion**: scope identified via the appropriate method, relevant spec files read.

## Step 2 — Inspect against five focus areas

For every changed file, check:

1. **Correctness** — does the code implement the spec? Check each Use Case scenario and Business Rule referenced by the issue. Flag behaviour that contradicts the spec or is absent from it.
2. **Clean Architecture** — layer boundaries and dependency direction respected.
3. **SOLID** — flag violations, naming the specific principle.
4. **Maintainability** — naming clarity, cyclomatic complexity, test coverage for changed code, duplication.
5. **Consistency** — does the code follow patterns established in the existing codebase? Flag deviations.

**Completion**: every changed file inspected against all five areas.

## Step 3 — Write the review report

Save as `docs/reviews/fagan-review-YYYY-MM-DD.md` per [report-format.md](../../rulebooks/conventions/report-format.md). File findings per [finding-format.md](../../rulebooks/conventions/finding-format.md) with tag `FAGAN`.

Format both the report and any finding files via `scripts/mdformat --number` per [markdown-formatting.md](../../rulebooks/conventions/markdown-formatting.md).

## Step 4 — Done-check

- [ ] Review covers all changed files
- [ ] Findings are categorised (Defect / Suggestion / Question)
- [ ] Defects are actionable — each describes what's wrong and what to do
- [ ] Spec compliance has been explicitly checked
