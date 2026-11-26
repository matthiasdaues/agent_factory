---
title: Update the factory
type: how-to
status: implemented
order: 20
description: Bring an installed .agent-factory/factory/ up to date with a newer checkout, and keep your own changes.
---

# Update the factory

When your `agent_factory` checkout gets newer, run `update-factory` to bring the installed project up to date. `init-factory` copies `.agent-factory/factory/` in only once, so running it again does not update the copy.

1. Check for your own changes first:

   ```bash
   .agent-factory/factory/scripts/update-factory --check
   ```

   The script compares the per-file SHA-256 checksums it recorded at installation with the installed files. It reports the files you added, such as your own skills, agents, or scripts, and the files you changed, such as edited prompts or rules. `--check` changes nothing.

2. Run the update:

   ```bash
   /path/to/agent_factory/.agent-factory/factory/scripts/update-factory --target /path/to/existing-project \
       --source /path/to/agent_factory
   ```

   Before it changes anything, the update shows a preview: the source, the installed and the new version, and the planned effects. It goes on only after an explicit `yes`.

   `--source` is optional when the installation recorded its source. `init-factory` stores the checkout it copied from as `factory_source` in `.agent-factory/install.json`, and `update-factory` uses it as the default. You can also run the installed copy from inside the project with `--source` when the manifest no longer holds the original checkout path.

3. When the update reports your own changes, it stops with exit code 2. To update anyway, pass `--force`:

   ```bash
   .agent-factory/factory/scripts/update-factory --force
   ```

   With `--force`, the update saves every changed and added file under `.agent-factory/user-changes/<timestamp>/`, so nothing is lost.

The update replaces the installed `.agent-factory/factory/` with a fresh copy of the source. Then it runs the source's `init-factory`, so every derived step is current too: the Codex adapters are generated again, the symlinks are checked again, the guardrail and usage hooks are merged again, and `pre-commit install` runs again.

The update replaces only `.agent-factory/factory/`. It keeps the project's own files, the changes in `.gitignore` and `.pre-commit-config.yaml`, the usage transcripts under `.agent-factory/`, and the lifecycle state.

An installation from before the checksum recording has no baseline to compare against. Its update replaces everything and records the checksums for the next update.

When the source's `init-factory` stops on a collision, `update-factory` rolls the update back. It moves the old `.agent-factory/factory/` aside, never deletes it, and puts it back in place. So the project is never left without a `.agent-factory/factory/` or with broken runtime symlinks. Resolve the reported collision and run `update-factory` again to finish.
