---
name: fagan-review
description: Structured code review following the Fagan Inspection method — correctness, Clean Architecture, SOLID, maintainability.
category: quality
disable-model-invocation: true
---

# Fagan Review

A structured code review following the **Fagan Inspection** method. The review checks correctness against the specification, architectural compliance, and maintainability. Every finding is categorised and actionable.

Read `CONTEXT.md` if it exists — flag terminology drift between code and domain vocabulary.

## Step 1 — Identify the review scope

Determine what to review: a branch diff, a PR, or a set of files. Read the relevant Use Case(s) and supplementary specs for the code under review.

**Completion**: scope identified, relevant spec files read.

## Step 2 — Inspect against five focus areas

For every changed file, check:

1. **Correctness** — does the code implement the spec? Check each Use Case scenario and Business Rule referenced by the issue. Flag behaviour that contradicts the spec or is absent from it.
2. **Clean Architecture** — layer boundaries and dependency direction respected.
3. **SOLID** — flag violations, naming the specific principle.
4. **Maintainability** — naming clarity, cyclomatic complexity, test coverage for changed code, duplication.
5. **Consistency** — does the code follow patterns established in the existing codebase? Flag deviations.

**Completion**: every changed file inspected against all five areas.

## Step 3 — Write the review report

Save as `docs/reviews/fagan-review-YYYY-MM-DD.md` per [report-format.md](../../rulebooks/report-format.md). File findings per [finding-format.md](../../rulebooks/finding-format.md) with tag `FAGAN`.

Format both the report and any finding files via `scripts/mdformat --number` per [markdown-formatting.md](../../rulebooks/markdown-formatting.md).

## Step 4 — Done-check

- [ ] Review covers all changed files
- [ ] Findings are categorised (Defect / Suggestion / Question)
- [ ] Defects are actionable — each describes what's wrong and what to do
- [ ] Spec compliance has been explicitly checked
