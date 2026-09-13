# Structurizr Behavior Checklist

Eleven-point checklist for modeling behavior in dynamic views, plus DSL
examples. Used by
[model-structurizr-slice](../../skills/model-structurizr-slice/SKILL.md).

## Behavior flow checks

Check each dynamic view flow for:

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

## Durable command delivery

For durable command delivery, show:

- Stable `command_id`.
- Agent persistence and fsync before `COMMAND_ACK`.
- Duplicate handling.
- Acknowledgement ingestion.
- Redelivery after a lost acknowledgement.
- Return persistence before `RETURN_ACK`.

Broker publish success is not Agent acceptance.

## DSL examples

### Tagging elements

```dsl
component "Attempt Builder" "..." "Application service" {
    tags "MVP,Increment 1,Runtime:worker"
}
```

### Grouping components within a container

```dsl
group "Increment 1 — worker" {
    queueClaimer = component "Queue Claimer" "..." "Application service" "MVP,Increment 1,Runtime:worker"
    attemptBuilder = component "Attempt Builder" "..." "Application service" "MVP,Increment 1,Runtime:worker"
}
```

### Deployment environment

```dsl
increment1 = deploymentEnvironment "Increment 1" {
    deploymentNode "worker" "Background execution loop." "Process" {
        containerInstance planning
        containerInstance dispatch
    }
}
```

### Filtered view styles

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
