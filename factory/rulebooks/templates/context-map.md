---
title: CONTEXT-MAP.md Template
version: 1.0.0
---

# CONTEXT-MAP.md Template

Skeleton for `docs/arc42/CONTEXT-MAP.md` in a multi-context repo. Governed by [context-format.md](../conventions/context-format.md).

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

## Referenced from

- [context-format.md § Single vs multi-context repos](../conventions/context-format.md#single-vs-multi-context-repos)
