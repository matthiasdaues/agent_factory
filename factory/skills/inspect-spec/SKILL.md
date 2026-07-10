---
name: inspect-spec
description: Two-pass specification review — deterministic spec-lint then LLM semantic inspection. Files findings as local markdown files.
category: requirements
disable-model-invocation: true
---

# Inspect Specification

Review the Phase-1 specification for defects **before** architecture consumes it. Two passes, strict division of labour:

- **Pass 1 — `spec-lint` (deterministic).** Catches provable defects — broken cross-references, missing Cockburn sections, undefined `BR-###`, unreachable states. Zero false-positive by design.
- **Pass 2 — semantic inspection (this LLM).** Only what a parser *cannot* decide: contradictions, ambiguity, testability, hidden assumptions, terminology drift.

Never re-check what Pass 1 already proved. Read `docs/CONTEXT.md` first.

## Step 1 — Run the deterministic linter

```bash
factory/scripts/spec-lint --spec-dir docs/spec --graph docs/spec/traceability.json
```

`error` findings → Defect without debate. `warning`/`info` → confirm or dismiss during Pass 2.

## Step 2 — Semantic inspection

Read the full spec (`docs/spec/`), then evaluate against the Wiegers/INCOSE requirements-quality characteristics — assess only what Pass 1 could not:

1. **Consistent** — contradicting requirements, preconditions no use case establishes, prose ≠ diagram.
2. **Unambiguous** — vague terms ("fast", "user-friendly"), hidden actors, unclear pronouns.
3. **Verifiable** — postconditions and Gherkin scenarios concrete enough to assert in a test.
4. **Complete** — extensions cover real failure modes, not just the happy path; no PRD goal missing from use cases.
5. **Feasible** — no conflicting non-functional requirements.
6. **Necessary** — nothing specified that no actor goal justifies (gold-plating).
7. **Terminology** — terms conflict with `docs/CONTEXT.md`, or two terms for one concept.

## Step 3 — Write the review report

Save as `docs/reviews/spec-review-YYYY-MM-DD.md` per [report-format.md](../../factory/rulebooks/conventions/report-format.md), adding:

1. **Reviewed specification** — artifacts read, `spec-lint` summary line.
2. **Deterministic findings** — Pass-1 table, each row Confirmed or Dismissed.
3. **Semantic findings** — finding table with Characteristic column added.
4. **Traceability summary** — orphans and gaps from `traceability.json`.

File findings per [finding-format.md](../../factory/rulebooks/conventions/finding-format.md) with tag `SPEC`.

Format both the report and any finding files via `factory/scripts/mdformat --number` per [markdown-formatting.md](../../factory/rulebooks/conventions/markdown-formatting.md).

## Step 4 — Verify prior findings (repeat passes only)

Per [review-loop-discipline.md](../../factory/rulebooks/conventions/review-loop-discipline.md): resolve or annotate each open `SPEC` finding, **and** re-run Steps 1-2 fresh against the full spec — not just the prior findings list — to catch new defects.
