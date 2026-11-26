---
title: Remove the factory
type: how-to
status: implemented
order: 30
description: Reverse the whole installation and get a clean git status back.
---

# Remove the factory

1. Run `remove-factory` from the project root:

   ```bash
   .agent-factory/factory/scripts/remove-factory
   ```

   It reverses the whole installation from the manifest `.agent-factory/install.json`. It deletes the git-ignored files and folders, removes the `agent_factory related` block from `.gitignore`, removes the orientation blocks from your orientation files, and removes the `agent_factory_hook-` block from `.pre-commit-config.yaml`. Your own hooks stay in place.

2. Check `git status`. It is clean. A repository that had its own `.gitignore`, pre-commit configuration, orientation file, or workflows gets each of them back byte for byte.

`remove-factory` also waits for pending usage captures before it deletes anything. [How usage capture works](../usage-capture/usage-capture.md#removal-and-pending-captures) explains the options `--pending-usage` and `--pending-timeout`.
