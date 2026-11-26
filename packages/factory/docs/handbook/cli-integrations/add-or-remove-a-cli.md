---
title: Add or remove a CLI
type: how-to
status: implemented
order: 40
description: Wire a CLI into an existing installation, or remove one, without running the full installer again.
---

# Add or remove a CLI

You do not need to run the full installer again to wire in a new CLI or remove one you no longer use. Run `init-factory` from the project root with `--add` or `--remove`.

## Add a CLI

```bash
# Add Copilot CLI to an existing installation
.agent-factory/factory/scripts/init-factory --add copilot

# Add several CLIs at once
.agent-factory/factory/scripts/init-factory --add copilot codex

# Choose from a menu
.agent-factory/factory/scripts/init-factory --add
```

`--add` creates the CLI's dot folder and links the factory content into it. It installs the guardrails, the step guards, the usage capture, and the freshness hooks for the CLI. It generates the adapter agents again where the CLI has them (Copilot, Codex), and it updates the `.gitignore` block.

## Remove a CLI

```bash
# Remove the Pi wiring
.agent-factory/factory/scripts/init-factory --remove pi

# Choose from a menu
.agent-factory/factory/scripts/init-factory --remove
```

`--remove` reverses everything `--add` did for the named CLI. It also removes the CLI's orientation block from an existing orientation file and deletes dot folders that are left empty.

Both options update the installation manifest `.agent-factory/install.json`, so `remove-factory` stays accurate.
