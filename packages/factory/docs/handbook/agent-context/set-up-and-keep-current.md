---
title: Set up and keep the agent context current
type: how-to
status: implemented
order: 20
description: Create docs/agent-context.md with VIRGIL, edit it as the project changes, and check it with concern-lint.
---

# Set up and keep the agent context current

## Set it up

1. Start a greenfield or brownfield playbook. VIRGIL runs the `capture-context` skill and interviews you one concern at a time.
2. Check the six cross-cutting concerns that the factory seeds on its own.
3. Check the technical concerns. VIRGIL proposes them from the stack it detected: languages, frameworks, and infrastructure.
4. Check the domain concerns. VIRGIL takes them from the scope map when one exists.
5. For each concern, confirm it, change its description, add or remove `Read:` paths, or skip it. VIRGIL creates only the concerns you confirm, so the file fits your project.

## Keep it current

`docs/agent-context.md` is a plain Markdown file, so you edit it directly with no special tool.

- When a source document moves, change its `Read:` path.

- When a new concern appears, add a `###` section under the right category.

- Run `concern-lint` to check the structure: the required headings, that each `Read:` path resolves, and that each concern a story names exists. The pre-commit hook and the `validate` skill run it too.

  ```bash
  .agent-factory/factory/scripts/concern-lint
  ```

The reconciliation agent also reports structural drift during its regular passes. Its reports are suggestions, not errors.
