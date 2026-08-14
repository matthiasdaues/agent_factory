---
name: model-structurizr-slice
description: Model an increment, MVP, or release in a canonical Structurizr DSL workspace. Use to tag and style a component subset, map runtime deployment, create static and dynamic slice views, separate data models from C4 views, or fix diagrams that mix structure, deployment, behavior, and data.
category: architecture
---

# Model a Structurizr Slice

Project a delivery slice from the canonical model. Do not create a second model.

## Read first

Read:

1. Local project instructions and index.
2. The canonical `architecture.dsl`. Find its path; do not assume it.
3. Slice scope, contracts, and acceptance criteria.
4. Existing component, runtime, and deployment docs.

Define:

- Slice tag, such as `Increment 1`.
- Optional scope tag, such as `MVP`.
- Included and excluded elements.
- Runtime nodes and their contents.
- Behaviors and failure paths to show.

Report conflicts between slice documents and the canonical model. Do not merge
conflicting transports or runtime designs.

## Use the right construct

| Concern                     | Structurizr construct                     |
| --------------------------- | ----------------------------------------- |
| Slice membership and style  | `tags`                                    |
| Boundary within one parent  | `group`                                   |
| Processes and co-deployment | `deploymentEnvironment`, `deploymentNode` |
| Static slice                | `filtered` view                           |
| Ordered behavior            | `dynamic` view                            |
| Tables, keys, cardinalities | Separate data model                       |

Use groups only for same-level elements under one parent. Use deployment nodes
for elements that run together.

## 1. Trace the slice

Map each capability to canonical elements and relationships. Classify each box
in source diagrams as one of:

- C4 element
- Runtime unit
- Adapter or layer
- Behavior
- Data structure

Tag canonical elements, not composite labels such as “Dispatch Loop.” Mark
uncertain elements. Do not include a whole container by default.

## 2. Tag elements

Use independent tag dimensions:

- Scope: `MVP`, `Post-MVP`
- Sequence: `Increment 1`, `Increment 2`
- Runtime: `Runtime:control-plane`, `Runtime:worker`

```dsl
component "Attempt Builder" "..." "Application service" {
    tags "MVP,Increment 1,Runtime:worker"
}
```

Keep canonical identifiers, names, owners, and relationships.

## 3. Group components

Group a slice only within its owning container:

```dsl
group "Increment 1 — worker" {
    queueClaimer = component "Queue Claimer" "..." "Application service" "MVP,Increment 1,Runtime:worker"
    attemptBuilder = component "Attempt Builder" "..." "Application service" "MVP,Increment 1,Runtime:worker"
}
```

Repeat the label in other containers when useful. Define the real runtime mapping
with deployment nodes.

## 4. Model deployment

Create one deployment environment for the slice:

```dsl
increment1 = deploymentEnvironment "Increment 1" {
    deploymentNode "worker" "Background execution loop." "Process" {
        containerInstance planning
        containerInstance dispatch
    }
}
```

Place each container on its runtime node. Describe shared code in prose. Do not
duplicate instances to show shared code.

State any gap from the target deployment, especially lost failure isolation.

## 5. Complete relationships

Add every static relationship needed by a dynamic view. Set its direction to the
actual flow of control or evidence.

Avoid relationships already supplied by implied relationships. Validate after
each batch.

## 6. Model behavior

Create one dynamic view per behavior or failure case. Keep component detail
inside the scoped container. Use a neighboring container at scope boundaries.

Check each flow for:

01. Trigger and preconditions.
02. Authoritative read.
03. Transaction and committed state.
04. Outbound handoff.
05. Receiver persistence and required flush or fsync.
06. Acknowledgement after persistence.
07. Sender persistence and outbox completion.
08. Deduplication identity.
09. Retry after each lossy boundary.
10. Terminal evidence persistence before acknowledgement.
11. Timeout, reconnect, and reconciliation.

For durable command delivery, show:

- Stable `command_id`.
- Agent persistence and fsync before `COMMAND_ACK`.
- Duplicate handling.
- Acknowledgement ingestion.
- Redelivery after a lost acknowledgement.
- Return persistence before `RETURN_ACK`.

Broker publish success is not Agent acceptance.

Decompose a critical container when its internal durability boundary matters.
Otherwise, label the view as container-level.

## 7. Filter and style

Create filtered views for static slices. If the full base view must remain in the
diagram list, add a filtered copy that includes `Element,Relationship`.

Order styles from general to specific:

```dsl
styles {
    element "MVP" {
        background #2e7d32
        color #ffffff
    }
    element "Runtime:worker" {
        stroke #ef6c00
        strokeWidth 4
    }
}
```

Use separate visual properties for separate tag dimensions. Inspect the legend.

## 8. Update docs

- Embed the generated deployment diagram. Remove duplicate Mermaid topology.
- Derive Mermaid sequences from DSL dynamic views when they need `alt`, `loop`,
  return arrows, or notes.
- Match DSL participants and step order.
- Keep the data model separate.
- Mark obsolete mixed diagrams as historical or remove them.

## 9. Validate

Run local project commands for:

1. Structurizr validation.
2. Architecture lint.
3. Markdown formatting.
4. `git diff --check`.
5. PNG and SVG export.

Inspect every new diagram. Check tags, groups, styles, legends, scope, and step
order.

If a wrapper points to the wrong DSL path, use its path override or report the
bug. Do not copy the DSL.

## Report

State:

- Tagged elements.
- Groups and deployment nodes.
- Views added.
- Invariants shown.
- Data-model work excluded.
- Checks run.
- Open conflicts and gaps.
