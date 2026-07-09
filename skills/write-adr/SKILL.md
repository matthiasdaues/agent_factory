---
name: write-adr
description: Document an architecture decision as an ADR (Nygard format). The sole owner of ADR format in this project — every ADR, from any caller, is written by this skill.
category: architecture
disable-model-invocation: true
---

# Write ADR

Document a single architecture decision following **ADR according to Nygard**. Apply **Clean Architecture** and **SOLID** as evaluation criteria where relevant.

Read `CONTEXT.md` if it exists — use the project's domain vocabulary.

**Offer an ADR only when all three hold** (cite this rule when offering): hard to reverse, surprising without context, the result of a real trade-off. Skip otherwise.

## Step 1 — Check for conflicts

Read existing ADRs in `docs/adr/`. Identify any that this decision might conflict with or supersede.

**Completion**: conflicts identified, or confirmed none exist.

## Step 2 — Evaluate alternatives, if there are genuine ones

If this decision has multiple real alternatives worth formally comparing, invoke `pugh-matrix` and get its confirmed result before continuing. If there's no genuine alternative to weigh (the obvious path was taken, or there was only ever one option), skip this step entirely — do not fabricate a matrix to fill the section.

**Completion**: either a confirmed Pugh Matrix in hand, or a deliberate decision that none applies.

## Step 3 — Write the ADR

Save as `docs/adr/NNNN-short-title.md` (next available number — scan `docs/adr/` for the highest existing and increment). Every ADR, matrix or not, carries this frontmatter:

```yaml
---
id: NNNN
status: proposed | accepted | deprecated | superseded by ADR-NNNN
evaluation: pugh-matrix | none
---
```

`evaluation` is never omitted — `none` is a real, valid, common value, not an absence. Body follows full **Nygard format**:

```markdown
# {Short title of the decision}

## Context
{what prompted this — the situation as it stood before deciding}

## Decision
{what was decided. If Step 2 produced a matrix, embed it here verbatim.}

## Consequences
{what this makes easier or harder going forward}
```

If this decision supersedes an earlier ADR, update that ADR's `status` to `superseded by ADR-NNNN`. If `docs/09_architecture_decisions.md` exists (arc42 chapter-9 index), update it to link the new ADR; if it doesn't exist, skip — not every project using this skill has arc42 documentation.

Format the new ADR (and the chapter-9 index, if updated) via `scripts/mdformat --number <path>` per [markdown-formatting.md](../../rulebooks/markdown-formatting.md).

**Completion**: ADR has `status` and `evaluation` in frontmatter, full Nygard body, matrix embedded iff `evaluation: pugh-matrix`, no unresolved conflicts, index updated where one exists.

## What qualifies for an ADR

- **Architectural shape** — e.g. "monorepo," "event-sourced write model, projected read model."
- **Integration patterns between contexts** — e.g. "Ordering and Billing talk via domain events, not synchronous HTTP."
- **Technology choices that carry lock-in** — database, message bus, auth provider, deployment target. Not every library, just the ones that would take a quarter to swap.
- **Boundary and scope decisions** — e.g. "Customer data is owned by the Customer context; others reference it by ID only." The explicit no's are as valuable as the yes's.
- **Deliberate deviations from the obvious path** — e.g. "manual SQL instead of an ORM, because X." Anything a reasonable reader would assume was done differently — these stop the next engineer "fixing" something deliberate.
- **Constraints not visible in the code** — e.g. "can't use AWS, compliance." "Response times under 200ms, partner API contract."
- **Rejected alternatives when non-obvious** — if GraphQL was considered and REST picked for subtle reasons, record it, or someone will suggest GraphQL again in six months.
