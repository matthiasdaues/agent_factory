---
title: Use the factory in an existing repository
type: how-to
status: implemented
order: 10
description: Install the factory into a repository that already has its own history, .gitignore, and pre-commit configuration.
---

# Use the factory in an existing repository

`init-factory` works the same way in a repository that already has its own history, `.gitignore`, and `.pre-commit-config.yaml`. It does not disturb what the project already owns, and you can remove everything it adds without a trace.

1. Run `init-factory` from inside the repository:

   ```bash
   cd /path/to/existing-project
   /path/to/agent_factory/packages/factory/scripts/init-factory
   ```

   To start the installation from a conversation instead of a shell, ask for the `init-factory` skill (`.agent-factory/factory/skills/init-factory/SKILL.md`). It confirms the target with you, runs the script, and relays its output.

2. Check what it changed. Against an existing repository, it changes only these files:

   - **`.gitignore`:** a single block between markers, headed `agent_factory related`, that lists exactly the files and folders the factory adds. It never rewrites or duplicates existing lines, and it keeps your file's exact bytes, down to a missing final newline. Under `.github/` it ignores each entry it adds, one by one, never the whole folder, so your `.github/workflows/` stay tracked.
   - **`.pre-commit-config.yaml`:** the one tracked change. Without the file, `init-factory` creates it with only the factory block. With the file, `init-factory` hands over to `.agent-factory/factory/scripts/merge-precommit-config`, which inserts the `- repo: local` block at the top of your `repos:` list and leaves your own hooks untouched. Every hook id of the block starts with `agent_factory_hook-`. A `.pre-commit-config.yml` stays untouched, because pre-commit reads only `.yaml` on its own.
   - **Orientation files:** when you already have `.github/copilot-instructions.md`, `.claude/CLAUDE.md`, or a root `AGENTS.md`, `init-factory` puts an orientation block between markers at the top of the file. For Claude Code the block is a single `@`-include line. For Copilot CLI, Pi, and Codex the block holds the full orientation text. Your own content stays below the block, and `remove-factory` removes the block on uninstall.

   Your `docs/`, your scripts, and your configuration stay as they are. `init-factory` never touches a file or folder it did not create.

3. Run it again whenever you like. The script is idempotent: it skips whatever is already in place. It records what it did in `.agent-factory/install.json`, and a second run reads that manifest, so it never loses track of what it owns.

4. When the script stops, read the path it names. When it finds something it cannot safely work around, it stops at once and names the exact path. It may stop after earlier changes of the run, such as the copy of the factory. Resolve the reported collision and run `init-factory` again: the rerun skips what is already in place. [Fix a known setup failure](../troubleshooting/fix-setup-failures.md) lists the known stops.

5. Onboard the existing code with the `brownfield-onboarding` playbook. [Kinds of playbooks](../playbooks/playbook-kinds.md#onboarding-playbooks) describes its two stages.

[Update the factory](update-the-factory.md) and [Remove the factory](remove-the-factory.md) cover the rest of the factory's life in the repository.
