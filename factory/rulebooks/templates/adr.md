---
title: ADR Template
version: 1.0.0
---

# Architecture Decision Record Template

Skeleton for a single `docs/adr/NNNN-short-title.md` file. Governed by [write-adr skill](../../skills/write-adr/SKILL.md) and following Nygard format.

## Frontmatter

```yaml
---
id: NNNNNN
status: proposed | accepted | deprecated | superseded by ADR-NNNNNN
evaluation: pugh-matrix | none
---
```

**Notes:**

- `evaluation` is never omitted — `none` is a real, valid, common value (not an absence)
- `pugh-matrix` means a Pugh Matrix table was used to evaluate alternatives
- `none` means no formal alternative evaluation was needed (obvious path, single option)

## Body

```markdown
# {Short title of the decision}

## Context

{what prompted this — the situation as it stood before deciding}

## Decision

{what was decided. If evaluation: pugh-matrix, embed the matrix table here verbatim.}

## Consequences

{what this makes easier or harder going forward}
```

## When a Pugh Matrix is present

If `evaluation: pugh-matrix`, the Decision section includes the confirmed matrix from the `pugh-matrix` skill invocation.

## Referenced from

- [write-adr § Step 3](../../skills/write-adr/SKILL.md#step-3--write-the-adr)
- [arch-lint script](../../scripts/arch-lint) (validates frontmatter)
