---
title: Finding Filing
category: review
enforcement: orchestrator findings-ingest loop (reads docs/findings/*.md with status open)
version: 1.0.0
---

# Finding Filing

Shared rules for filing review findings as local markdown files. Findings are project artifacts, not entries in an external tracker — one file per finding, with strict frontmatter, under `docs/findings/`.

## When to file

File every **Defect** and every finding at or above the review's blocking severity — for most reviews that is **Critical** or **Major** (see [report-format.md](report-format.md)); the security and ATAM reviews file at **Medium or higher**. Minor findings and Suggestions stay in the review report only, unless the user asks to track them.

## File location and name

- Directory: `docs/findings/`
- Filename: `<TAG>-<NNNN>.md`, zero-padded, sequential per tag (e.g. `SPEC-0001.md`).
- Allocate the next `NNNN` by scanning existing files with the same tag.

| Review                         | TAG     |
| ------------------------------ | ------- |
| Spec review                    | `SPEC`  |
| ATAM architecture review       | `ATAM`  |
| Fagan code inspection          | `FAGAN` |
| Security review                | `SEC`   |
| Spec reconciliation            | `RECON` |
| Bug hunt / exploratory testing | `BUG`   |

## Frontmatter schema

```markdown
---
id: SPEC-0001
source: spec-review          # the review that produced it (spec-review, atam-review, fagan-review, security-review, reconcile, bug-hunt)
severity: major              # critical | major | minor  (or the review's own scale, e.g. high|medium|low)
category: defect             # defect | suggestion | question
artifact: docs/spec/prd.md#NFR-01   # file#anchor or path:line the finding is about
status: open                 # open | resolved
traces: [NFR-01]             # requirement / use-case / ADR IDs the finding relates to (optional)
---
```

## Body

```markdown
# <one-line finding title>

**What is wrong:** <the defect, stated concretely>

**Fix:** <the concrete remediation>
```

Every finding must state **what is wrong** and **what to do** — no "this looks off" without a fix direction.

## Status lifecycle

- `open` — the finding stands; the author must address it.
- `resolved` — on a repeat pass, the reviewer verified the author's fix and set the status. Keep the file as the durable record; do not delete it.

## How the orchestrator reads findings

The finding files are the contract. When run under the orchestrator, the review loop reads every `docs/findings/*.md` whose `status` is `open` — those are the findings the phase must still address — and loops back to the author until none remain. You do not emit any machine-readable block; filing the files, and setting `status: resolved` on a repeat pass once a fix is verified, is all the loop needs. This works the same whether the review ran headless or in an interactive session.

## Pause point

Present the findings to the user before writing any files. The user decides which findings warrant a filed finding. Then write the files and save the review report.
