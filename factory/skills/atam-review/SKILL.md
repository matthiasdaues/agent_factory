---
name: atam-review
description: Two-pass architecture review — deterministic arch-lint (structure, DSL consistency, diagram references) then ATAM evaluation against quality attribute scenarios. Files findings as local markdown files.
category: architecture
disable-model-invocation: true
---

# ATAM Review

Review the Phase-2 architecture for structural defects and quality-attribute risks **before** implementation consumes it. The review runs in two passes with a strict division of labour:

- **Pass 1 — `arch-lint` (deterministic).** A parser catches the boring, provable defects — arc42 chapters missing, Structurizr DSL referencing undefined containers, ADR index out of sync, diagram files not matching view keys. Cheap, reproducible, zero false-positive by design.
- **Pass 2 — ATAM evaluation (this LLM).** Spend judgement only on what a parser *cannot* decide: sensitivity points, tradeoff points, risks versus non-risks for each quality scenario.

Never re-check by hand what Pass 1 already proved. Read `docs/CONTEXT.md` first — the architecture's vocabulary is the yardstick for the terminology checks.

## Step 1 — Run the deterministic linter

Run the linter and capture its report:

```bash
factory/scripts/arch-lint --docs-dir docs/
```

Read every finding. `error`-severity findings are hard defects — they go into the report as **Defect** without further debate. `warning`/`info` findings are candidates: confirm or dismiss each during Pass 2 (a heuristic finding may be a false positive; say so explicitly).

**Completion**: linter run, exit code and all findings recorded.

## Step 2 — Collect quality scenarios

Read `docs/10_quality_requirements.md`. Extract every quality attribute scenario. If the chapter doesn't exist yet, ask the user to define the top 5 quality goals before proceeding.

**Completion**: a numbered list of quality scenarios to evaluate.

## Step 3 — Analyse each scenario

For each quality scenario, read the relevant arc42 chapters and identify the **architectural approach**, **sensitivity points**, **tradeoff points**, and **risk / non-risk** classification, evaluated against the architecture as documented, not as imagined.

**Completion**: every scenario from step 2 has all four assessments.

## Step 4 — Write the review report

Save as `docs/reviews/atam-review.md` per [report-format.md](../../factory/rulebooks/conventions/report-format.md), adding:

1. **Reviewed architecture** — chapters and DSL examined; `arch-lint` summary (error/warning/info counts + exit code).
2. **Deterministic findings** — Pass-1 table, each row Confirmed or Dismissed.
3. **Quality scenarios** — the list from step 2.
4. **Findings** — one subsection per scenario with the four assessments.
5. **Risk summary** — table of risks with severity and proposed mitigation.
6. **Tradeoff summary** — table of identified tradeoffs.

File findings per [finding-format.md](../../factory/rulebooks/conventions/finding-format.md) with tag `ATAM` for risks rated Medium or higher.

Format both the report and any finding files via `factory/scripts/mdformat --number` per [markdown-formatting.md](../../factory/rulebooks/conventions/markdown-formatting.md).

## Step 5 — Verify prior findings (repeat passes only)

Per [review-loop-discipline.md](../../factory/rulebooks/conventions/review-loop-discipline.md): resolve or annotate each open `ATAM` finding, **and** re-run Steps 1-3 fresh against the full architecture — not just the prior findings list — to catch new defects.
