---
name: update-context
description: >-
  Deprecated. docs/agent-context.md (the concern-based routing interface)
  is edited directly — there is no field-write skill for it. Retained only
  so an invocation surfaces a deprecation notice instead of an error.
category: utility
version: 3.0.0
---

# Update Context

**Deprecated.** update-context is deprecated. Edit `docs/agent-context.md`
directly.

The YAML agent-context model (`stack.yaml`, `workflow.yaml`,
`governance.yaml`, `reading-guides.yaml`) that this skill used to maintain
has been retired in favor of the concern-based `docs/agent-context.md`. See
[Agent Context Composition](../../rulebooks/conventions/agent-context-composition.md)
for the current structure, and `capture-context` (bare invocation) for
migrating a project still on the YAML model.

Invoking this skill produces no error and takes no action beyond showing
this notice.
