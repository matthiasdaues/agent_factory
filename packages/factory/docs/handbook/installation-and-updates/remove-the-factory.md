---
title: Remove the factory
type: how-to
status: implemented
order: 30
description: Remove Agent Factory and check which project files changed.
---

# Remove the factory

Removing Agent Factory deletes its saved usage records and transcripts. Copy any records or transcripts you want to keep from `.agent-factory/usage/` to a location outside the project before you continue.

1. Run `git status --short` from the project root and note any changes already present.

2. Run `remove-factory` from the project root:

   ```bash
   .agent-factory/factory/scripts/remove-factory
   ```

   It reverses the whole installation from the manifest `.agent-factory/install.json`. It deletes the git-ignored files and folders, removes the `agent_factory related` block from `.gitignore`, removes the orientation blocks from your orientation files, and removes the `agent_factory_hook-` block from `.pre-commit-config.yaml`. Your own hooks stay in place.

3. Run `git status --short` again. Compare it with the first output and check the diff for any files the removal touched. Check that the Factory entries are gone and that your project changes are still present.

`remove-factory` also waits for pending usage captures before it deletes anything. [How usage capture works](../usage-capture/usage-capture.md#removal-and-pending-captures) explains the options `--pending-usage` and `--pending-timeout`.
