---
title: State Machine Pseudocode Template
version: 1.0.0
---

# State Machine Pseudocode Template

Skeleton for the event-driven pseudocode block that is the source of truth for a state machine; Mermaid is derived from it. Governed by [state-machine-notation.md](../conventions/state-machine-notation.md).

```
State: STATE_NAME          — declare a state; all following actions belong to it
On EventName:              — event trigger
  if condition             — guard (plain English or domain predicate)
    ChangeState(TARGET)    — explicit transition to TARGET
  else
    ChangeState(OTHER)

SetHaltedFrom(X)           — record X as a possible RestoreState target
RestoreState(var)          — dynamic transition to any state recorded by SetHaltedFrom
RejectCommand("reason")    — refuse the event with a diagnostic
```

## Referenced from

- [state-machine-notation.md § Required Structure](../conventions/state-machine-notation.md#required-structure)
