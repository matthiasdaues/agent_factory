---
title: pi-capture-bootstrap.mjs
type: reference
status: implemented
description: Start the Pi usage supervisor and handle a failed startup.
---

# pi-capture-bootstrap.mjs

## Name

`pi-capture-bootstrap.mjs` — Start the Pi usage supervisor and handle a failed startup.

## Synopsis

```text
.agent-factory/factory/scripts/pi-capture-bootstrap.mjs <registration flags> --supervisor-command <command> [<arguments> ...]
```

This command is used by Factory automation. Its caller supplies the runtime context.

The Pi integration supplies the registration and supervisor command. Use the normal Pi capture flow to exercise this helper.

## See also

- [Command source](../../../scripts/pi-capture-bootstrap.mjs)
