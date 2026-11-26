---
title: Fix a known setup failure
type: how-to
status: implemented
order: 10
description: Find the message you see and apply its fix.
---

# Fix a known setup failure

Find the message or the symptom you see, and apply the fix under it.

## `init-factory: STOPPED — <path> already exists and is not a symlink to <dest>`

Check the file or directory at `<path>`. If you can move it without disrupting your project, rename it or move it somewhere safe. Run `init-factory` again and check that it finishes without the same error.

## `merge-precommit-config` cannot merge your `.pre-commit-config.yaml`

The file has no top-level `repos:` list in block style, or its hooks are not indented by 2 spaces. Merge the factory hooks by hand: copy the `- repo: local` block from `.agent-factory/factory/config/pre-commit-config.yaml` into the `repos:` list of your file.

## `uvx: command not found`

Install `uv`, as [.agent-factory/factory/README.md § Prerequisites](../../../README.md#prerequisites) describes. Every gate, and `pre-commit` itself, runs through `uvx`.

## `docker info` fails, or the diagram export fails

Start Docker Desktop on macOS or the Docker daemon on Linux. Only `.agent-factory/factory/scripts/structurizr` needs Docker.

## Your first commit fails, or changes files you did not touch

The `mdformat` hook fixes the formatting on commit. When a commit fails with "files were modified by this hook", the formatter changed files that did not match the project style yet. Review the formatter’s changes with `git diff`. Stage only the files you want in this commit, then retry:

```bash
git add -- <file>
git commit -m "<same message>"
```

Replace `<file>` with the path you reviewed. Repeat for any other files you want to stage.

## `.agent-factory/factory/` looks out of date after you update your `agent_factory` checkout

`init-factory` copies `.agent-factory/factory/` in only once. Run `update-factory` instead, as [Update the factory](../installation-and-updates/update-the-factory.md) describes. Run `update-factory --check` first to see whether the update would replace your own changes to `.agent-factory/factory/`.

## `origin/HEAD` points nowhere after a rename of `master` to `main`

`init-factory` finds and repairs a dangling `origin/HEAD` symref on its own. It tries `git remote set-head origin --auto` first, which needs the network. Then it falls back to the remote-tracking branches it knows locally and looks for `main` or `master`. This repair is best effort and never stops the installation.

## Symlinks do not work on Windows

Agent Factory supports only macOS and Linux. It relies on native symlinks that git tracks, and Windows does not handle them the same way.
