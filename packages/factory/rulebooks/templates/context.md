---
title: CONTEXT.md Template
version: 1.0.0
---

# CONTEXT.md Template

Skeleton for a single-context `docs/CONTEXT.md` (or a per-context `CONTEXT.md` in a multi-context repo). Governed by [context-format.md](../conventions/context-format.md).

```md
# {Context Name}

{One or two sentence description of what this context is and why it exists.}

## Language

**Order**:
{A one or two sentence description of the term}
_Avoid_: Purchase, transaction

**Invoice**:
A request for payment sent to a customer after delivery.
_Avoid_: Bill, payment request

**Customer**:
A person or organization that places orders.
_Avoid_: Client, buyer, account
```

## Referenced from

- [context-format.md § Structure](../conventions/context-format.md#structure)
- [domain-modeling § Update docs/CONTEXT.md inline](../../skills/domain-modeling/SKILL.md#update-docscontextmd-inline)
