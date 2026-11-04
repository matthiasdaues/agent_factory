---
title: Finding Filing
category: review
enforcement: orchestrator findings-ingest loop (reads docs/findings/*.md with status open)
version: 1.0.0
---

# Finding Filing

Shared rules for filing review findings as local markdown files. Findings are project artifacts, not entries in an external tracker — one file per finding, with strict frontmatter, under `docs/findings/`.

## When to file

Canonical statement: [rules.md § Findings](../rules.md#findings).

For most reviews the blocking severity is **Critical** or **Major** (see [report-format.md](report-format.md)); the security and ATAM reviews file at **Medium or higher**. Minor findings and Suggestions stay in the review report only, unless the user asks to track them.

## File location and name

- Directory: `docs/findings/`
- Filename: `<TAG>-<NNNN>.md`, zero-padded, sequential per tag (e.g. `SPEC-0001.md`).
- Allocate the next `NNNN` by scanning existing files with the same tag.

| Review                          | TAG     |
| ------------------------------- | ------- |
| Spec review                     | `SPEC`  |
| ATAM architecture review        | `ATAM`  |
| Architecture agent's read check | `ARCH`  |
| Implementation code review      | `IMPL`  |
| Fagan code inspection           | `FAGAN` |
| Security review                 | `SEC`   |
| Unresolved mutant               | `QA`    |
| Bug hunt / exploratory testing  | `BUG`   |

## Format

Frontmatter and body skeleton: [finding.md template](../templates/finding.md).

Canonical statement: [rules.md § Findings](../rules.md#findings) — no "this looks off" without a fix direction.

## Owner

`owner:` in the frontmatter names the agent that acts on the finding next. The filer is not the owner. By default the owner is the producer of the artifact the finding is about. A `BUG` finding names the developer agent. A `QA` finding for a missing test names the planning agent.

## Status lifecycle

- `open` — the finding stands; the owner must address it.
- `resolved` — on a repeat pass, the reviewer verified the owner's fix and set the status. Keep the file as the durable record; do not delete it.

## How the orchestrator reads findings

The finding files are the contract. When run under the orchestrator, the review loop reads every `docs/findings/*.md` whose `status` is `open`. Those are the findings the phase must still address. The orchestrator sends each open finding to the agent in `owner:`, not to the author of the reviewed phase. It sends an open finding without `owner:` to the producer of the artifact it names, read from the output declarations (`outputs:` in the agent definitions). The loop repeats until no open finding remains. You do not emit any machine-readable block; filing the files, and setting `status: resolved` on a repeat pass once a fix is verified, is all the loop needs. This works the same whether the review ran headless or in an interactive session.

## Pause point

Present the findings to the user before writing any files. The user decides which findings warrant a filed finding. Then write the files and save the review report.

## Referenced from

- [rules.md § Findings](../rules.md#findings)
- [report-format.md § Findings drive the loop](report-format.md#findings-drive-the-loop)
- [reconciliation-agent.md § Workflow](../../agents/reconciliation-agent.md#workflow)
- [spec-review-agent.md § Workflow](../../agents/spec-review-agent.md#workflow)
- [architecture-review-agent.md § Workflow](../../agents/architecture-review-agent.md#workflow)
- [code-review-agent.md § Workflow](../../agents/code-review-agent.md#workflow)
- [qa-agent.md § Workflow](../../agents/qa-agent.md#workflow)
- [security-review § Report](../../skills/security-review/SKILL.md#report)
- [reconcile-spec § Step 2 — Update](../../skills/reconcile-spec/SKILL.md#step-2--update)
- [bug-hunt § Phase: Hunt](../../skills/bug-hunt/SKILL.md#phase-hunt)
- [inspect-spec § Step 3 — Write the review report](../../skills/inspect-spec/SKILL.md#step-3--write-the-review-report)
- [atam-review § Step 4 — Write the review report](../../skills/atam-review/SKILL.md#step-4--write-the-review-report)
- [fagan-review § Step 3 — Write the review report](../../skills/fagan-review/SKILL.md#step-3--write-the-review-report)
