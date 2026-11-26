---
title: Pre-commit hooks
type: concept
status: implemented
order: 30
description: How the factory's pre-commit hooks run without installing anything, skip a clone without the factory, and leave your own hooks alone.
---

# Pre-commit hooks

The factory adds pre-commit hooks to `.pre-commit-config.yaml`. This file is the one tracked file the installation changes, besides a block in `.gitignore`. Every hook id starts with `agent_factory_hook-`, so the block is easy to find, check, and remove.

The hooks form two groups. The formatter `mdformat` fixes the style of Markdown files on commit. The gate scripts reject a commit when a deterministic check fails. [Gate scripts](gate-scripts.md) lists both groups.

## Nothing is installed into your project

The formatter needs external tools, but the hooks never install them into your project tree, your virtualenv, or your global Python packages. They run through `uvx`. On the first run, `uvx` downloads a pinned copy into its own cache, `~/.cache/uv/` or `$UV_CACHE_DIR`, and reuses it afterwards. Your `site-packages`, your `node_modules`, and your own tool versions stay untouched.

When you have `mdformat` installed globally, `uvx` ignores it and runs its own pinned version. So the hook gives the same result on every machine. `.agent-factory/factory/scripts/structurizr` follows the same pattern for its Docker dependency.

The gate scripts are stdlib-only Python. They need only the Python interpreter on your PATH: no `pip install`, no requirements file, and no build step.

## Your teammates can commit without the factory

`.pre-commit-config.yaml` is tracked, so everyone who clones the repository gets the hook definitions. `.agent-factory/factory/` is git-ignored. It exists only on machines where `init-factory` ran, so a colleague who never installed the factory does not have it.

Every hook that calls a gate under `.agent-factory/factory/scripts/` therefore starts with a short bash guard:

```bash
bash -c 'AF=.agent-factory; [ -d "$AF" ] || AF="$(cd "$(git rev-parse --git-common-dir 2>/dev/null)/.." 2>/dev/null && pwd)/.agent-factory"; [ -d "$AF" ] || { [ "$(git config --bool agent-factory.installed)" = true ] || exit 0; echo ".agent-factory/ missing. Run update-factory, or set SKIP=<hook id>." >&2; exit 1; }; exec "$AF"/factory/scripts/<gate> "$@"' --
```

The guard looks for `.agent-factory/` in the current checkout first. A linked worktree has no copy of its own, so the guard then looks in the primary checkout. When neither has the factory, the guard asks the clone whether it installed the factory.

`init-factory` answers that question once per clone. It sets the key `agent-factory.installed` in the clone's local `.git/config`, which git never commits or shares. Linked worktrees read the same file. `remove-factory` unsets the key.

- **The key is not set.** The clone belongs to a colleague without the factory. The hook exits 0 in silence, and the colleague commits with no error, no warning, and no trace of Agent Factory.
- **The key is set.** This clone installed the factory, so a missing folder is a fault. The hook fails with the message above. The message mentions a per-hook skip, but the way out is to repair the installation: run `update-factory`, then commit again. When the hook runs in a clone marked as installed, the guard exits with an error if the factory folder is missing.

> Rule summary: **MUST NOT** bypass a failing pre-commit hook (`--no-verify`, `core.hooksPath`); fix the hook.
> Source: [rules.md § Git workflow](../../../rulebooks/rules.md#git-workflow)

The tracked `.pre-commit-config.yaml` survives clones and branch switches. The untracked `.agent-factory/factory/` is local tooling, not project source. The guard connects the two: the hooks run for everyone who installed the factory and stay silent for everyone else.

## Your own hooks stay as they are

When your project already has a `.pre-commit-config.yaml`, `init-factory` inserts the `agent_factory_hook-` block at the top of your `repos:` list. It does not rewrite, reorder, or change your own hooks. `remove-factory` removes exactly that block, so your hooks stay byte for byte as they were. When you have no `.pre-commit-config.yaml`, `init-factory` creates one with only the factory hooks.

The formatter can change files on your first commit after the setup. [Fix a known setup failure](../troubleshooting/fix-setup-failures.md#your-first-commit-fails-or-changes-files-you-did-not-touch) describes what to do.
