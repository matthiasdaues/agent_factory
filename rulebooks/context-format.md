---
title: CONTEXT.md Format
category: domain-modeling
enforcement: domain-modeling skill (written by), most other skills (read by) — not mechanically gate-checked
version: 1.0.0
---

# CONTEXT.md Format

## Structure

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

## Rules

- **Be opinionated.** When multiple words exist for the same concept, pick the best one and list the others under `_Avoid_`.
- **Keep definitions tight.** One or two sentences max. Define what it IS, not what it does.
- **Only project-specific terms.** General programming concepts (timeouts, error types, utility patterns) don't belong even if heavily used. Ask: unique to this context, or general programming? Only the former belongs.
- **Group under subheadings** when natural clusters emerge; a flat list is fine otherwise.

## Single vs multi-context repos

**Single context (most repos):** one `CONTEXT.md` at the repo root.

**Multiple contexts:** a `CONTEXT-MAP.md` at the repo root lists the contexts, where they live, and how they relate:

```md
# Context Map

## Contexts

- [Ordering](./src/ordering/CONTEXT.md) — receives and tracks customer orders
- [Billing](./src/billing/CONTEXT.md) — generates invoices and processes payments
- [Fulfillment](./src/fulfillment/CONTEXT.md) — manages warehouse picking and shipping

## Relationships

- **Ordering → Fulfillment**: Ordering emits `OrderPlaced` events; Fulfillment consumes them to start picking
- **Fulfillment → Billing**: Fulfillment emits `ShipmentDispatched` events; Billing consumes them to generate invoices
- **Ordering ↔ Billing**: Shared types for `CustomerId` and `Money`
```

Infer the structure: `CONTEXT-MAP.md` exists → read it for contexts; only a root `CONTEXT.md` exists → single context; neither exists → create a root `CONTEXT.md` lazily when the first term is resolved.

When multiple contexts exist, infer which one the current topic relates to; ask if unclear.
