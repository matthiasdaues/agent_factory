---
name: fagan-review
description: Structured code review following the Fagan Inspection method — correctness, Clean Architecture, SOLID, maintainability.
category: quality
---

# Fagan Review

A structured code review following the **Fagan Inspection** method. The review checks correctness against the specification, architectural compliance, and maintainability. Every finding is categorised and actionable.

Read [factory-voice.md](../../rulebooks/conventions/factory-voice.md) now and hold every rule as a writing constraint. No prose reaches terminal output or a file until it passes all four gates and clears the final pass.
Read `docs/spec/glossary.md` if it exists — flag terminology drift between code and domain vocabulary.

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

Save as `docs/reviews/fagan-review-YYYY-MM-DD.md` per [report-format.md](../../rulebooks/conventions/report-format.md). This review classifies findings of the review class `code`. Classify each finding by [Class: code](../../rulebooks/conventions/finding-classification.md#class-code): record its basis, and let the rule of the class compute the severity. File each finding by that severity. A `critical` or `major` finding of the category `defect` or `risk` becomes a finding file with tag `FAGAN` from the [finding template](../../rulebooks/templates/finding.md), as [finding-format.md](../../rulebooks/conventions/finding-format.md) describes. A `minor` finding becomes one register file `docs/findings/register/code/<ID>.json` with `status: open` and gets no finding file. The commit that fixes it sets `status` of the register file to `resolved`. A `note` stays a row of the review report, and a `question` becomes an entry of `docs/spec/work/todo.md`. A register file takes its ID from `next-id`, as a finding file does. Run `.agent-factory/factory/scripts/next-id FAGAN` and read the ID from its standard output, because a shell variable does not survive from one agent command to the next. When `next-id` fails, stop and report its message; never pick a number by hand.

Write the What is wrong field of every Defect in this order: the consequence and who receives it, the first layer where information, control, or an assumption is lost or changed, and whether the behavior looks intended, wrong, or undocumented. When the defect crosses layers, add a causal chain of three to six steps in a text block. In Fix, name the smallest change and the layer where it belongs.

Format both the report and any finding files via `scripts/mdformat --number` per [markdown-formatting.md](../../rulebooks/conventions/markdown-formatting.md).

## Step 4 — Done-check

- [ ] Review covers all changed files
- [ ] Findings are categorised (Defect / Suggestion / Question)
- [ ] Defects are actionable — each describes what's wrong and what to do
- [ ] Spec compliance has been explicitly checked
- [ ] Every Defect states the consequence first and names the layer where the problem starts
