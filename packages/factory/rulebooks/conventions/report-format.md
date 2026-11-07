---
title: Review Report Format
category: review
enforcement: none — human-consumed; the findings a report cites are what the orchestrator mechanically ingests, per finding-format.md
version: 1.0.0
---

# Review Report Format

Shared format for all review and inspection skills.

## Report frontmatter

Every review report carries this YAML frontmatter. Keys marked *(branch-scoped)* apply only when the review targets a branch diff (code review, fagan, bug-hunt, security). Keys marked *(doc-scoped)* apply only when the review targets artifacts against a reference (reconciliation, ATAM, spec review).

```yaml
---
type: <review-skill-name>
title: <human-readable report title>
date: <YYYY-MM-DD>
status: pass | defects | block
reviewer: <agent name>
findings_filed: <integer>
story: <story or artifact ID, when applicable>
branch: <branch under review>              # branch-scoped
branch_base: <full 40-char SHA>            # branch-scoped
branch_head: <full 40-char SHA>            # branch-scoped
scope: <what is being reviewed>            # doc-scoped
---
```

- `branch-base` is the merge base commit — where the branch diverged from its target.
- `branch-head` is the branch tip at the time of review.
- Both must be full 40-character SHAs per [rules.md § Git workflow](../rules.md#git-workflow).
- `scope` describes the reviewed artifacts in plain language when no branch diff applies.

## Finding table

Row format: [review-report.md template](../templates/review-report.md).

## Category rules

[finding-classification.md § The values of a finding](finding-classification.md#the-values-of-a-finding) defines the four categories `defect`, `risk`, `suggestion`, and `question`.

- A **question** needs the author to clarify intent. Record it only in `docs/spec/work/todo.md` per [todo-format.md](todo-format.md). Claim the entry's number with `.agent-factory/factory/scripts/next-id T`, and read the ID from standard output. When `next-id` fails, stop and report its message; never pick a number by hand.

Every finding must state **what is wrong** and **what to do** — no "this looks off" without a fix direction.

## Severity

[finding-classification.md](finding-classification.md) holds the shared severity scale, the blocking rule, and the rule of each review class. Classify every finding by the section of its class, and record its basis.

## Findings drive the loop

File each blocking finding as its own `docs/findings/*.md` per [finding-format.md](finding-format.md). Under the orchestrator, the review loop reads those files directly — an `open` finding loops back to the author, a `resolved` one drops out — so the report table is for the reader and the finding files are what the tool acts on.

## Child-result envelope

Before a child agent returns, it writes its complete report and every finding
to canonical Git-tracked artifacts. Its final parent-facing message is one JSON
object with exactly these four fields and no surrounding prose or Markdown
fence:

```json
{
  "disposition": "pass",
  "finding_counts": {"critical": 0, "major": 0, "minor": 0, "note": 0},
  "artifact_paths": ["docs/reviews/review-report.md"],
  "next_action": "Read the complete report before continuing the workflow."
}
```

- `disposition` is `pass`, `fail`, or `block`.
- `finding_counts` holds a whole number of zero or more for each of the four
  severities `critical`, `major`, `minor`, and `note`. A key with zero findings
  stays in the envelope. `adversarial-review` maps its own scale onto the four
  keys, as
  [finding-classification.md § Claim review stays outside](finding-classification.md#claim-review-stays-outside)
  describes.
- `artifact_paths` is the complete, non-empty list of repository-relative,
  canonical paths to the tracked report and finding files. Paths are unique.
- `next_action` is one to three sentences stating the downstream action.

The envelope never contains verbatim finding detail, per-finding remediation,
or full reasoning. Consumers deliberately read complete content from
`artifact_paths`. Runtime metadata such as model, token usage, and exit code is
transport metadata outside this four-field object.

## Referenced from

- [finding-classification.md § Claim review stays outside](finding-classification.md#claim-review-stays-outside)
- [finding-format.md § When to file](finding-format.md#when-to-file)
- [todo-format.md § When to file](todo-format.md#when-to-file)
- [architecture-review-agent.md § Workflow](../../agents/architecture-review-agent.md#workflow)
- [reconciliation-agent.md § Workflow](../../agents/reconciliation-agent.md#workflow)
- [qa-agent.md § Workflow](../../agents/qa-agent.md#workflow)
- [spec-review-agent.md § Workflow](../../agents/spec-review-agent.md#workflow)
- [security-review § Report](../../skills/security-review/SKILL.md#report)
- [reconcile-spec § Step 3 — Write the reconciliation report](../../skills/reconcile-spec/SKILL.md#step-3--write-the-reconciliation-report)
- [inspect-spec § Step 3 — Write the review report](../../skills/inspect-spec/SKILL.md#step-3--write-the-review-report)
- [atam-review § Step 4 — Write the review report](../../skills/atam-review/SKILL.md#step-4--write-the-review-report)
- [fagan-review § Step 3 — Write the review report](../../skills/fagan-review/SKILL.md#step-3--write-the-review-report)
- [interface-contracts.md § Child-result envelope](../../../../docs/spec/interface-contracts.md)
